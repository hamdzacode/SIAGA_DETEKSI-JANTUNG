from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal, engine
from ml.cardio_model import CardioRiskModel

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIAGA Jantung API v2")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/model-info")
def get_model_info():
    import json
    from pathlib import Path
    try:
        path = Path(__file__).resolve().parent.parent.parent / "ml" / "model_metadata.json"
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"accuracy": "N/A", "error": str(e)}

# --- Users ---
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# --- Patients ---
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    # Check for duplicate MRN if provided
    if patient.medical_record_number:
        existing = db.query(models.Patient).filter(models.Patient.medical_record_number == patient.medical_record_number).first()
        if existing:
             raise HTTPException(status_code=400, detail="Medical Record Number already exists")
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, name: Optional[str] = None, db: Session = Depends(get_db)):
    patients = crud.get_patients(db, skip=skip, limit=limit, name=name)
    return patients

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

# --- Checkups ---
@app.post("/patients/{patient_id}/checkups/", response_model=schemas.Checkup)
def create_checkup_for_patient(
    patient_id: int, 
    checkup: schemas.CheckupCreate, 
    db: Session = Depends(get_db)
):
    # 1. Validate Patient
    patient = crud.get_patient(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. Calculate Risk
    try:
        model = CardioRiskModel()
        # Prepare data for model
        input_data = checkup.dict()
        
        # Validate Age
        if input_data['age_years'] < 5:
            raise HTTPException(status_code=400, detail="Pasien harus berusia minimal 5 tahun untuk analisis risiko.")
            
        # Model expects specific keys, checkup.dict() has them plus 'notes' and 'checked_by_user_id'
        # The model wrapper _to_feature_array handles extraction by key, so extra keys are fine if we pass the dict.
        # However, we need to ensure the keys match exactly what the model expects.
        # The model expects: age_years, gender, bmi, map, cholesterol, gluc, smoke, alco, active
        
        proba = model.predict_proba(input_data)
        label = model.predict_label(input_data, threshold=0.5)
        
        # Calculate SHAP Values
        shap_dict = model.get_shap_values(input_data)
        import json
        shap_json = json.dumps(shap_dict)
        
        risk_percent = proba * 100
        if risk_percent < 30:
            risk_cat = "Rendah"
        elif risk_percent < 60:
            risk_cat = "Sedang"
        else:
            risk_cat = "Tinggi"
            
        model_version = "xgb_v1.0.0" # Hardcoded for now

        # Generate Recommendations (Clinical Path)
        recs = []
        
        # 1. Risk-Based Path
        if risk_cat == "Tinggi":
            recs.append("⚠️ **PROTOKOL RISIKO TINGGI**: Rujuk segera ke Spesialis Jantung (Cardiologist).")
            recs.append("Lakukan EKG 12-lead dan Panel Lipid Lengkap.")
        elif risk_cat == "Sedang":
            recs.append("⚠️ **PROTOKOL RISIKO SEDANG**: Jadwalkan kontrol ulang dalam 3 bulan.")
            recs.append("Evaluasi gaya hidup ketat dan pertimbangkan terapi statin jika kolesterol tinggi.")
        else:
            recs.append("✅ **PROTOKOL RISIKO RENDAH**: Edukasi gaya hidup sehat (diet & olahraga).")
            recs.append("Kontrol rutin tahunan.")

        # 2. Factor-Based Path (Simplified SHAP-like logic)
        if input_data['smoke'] == 1:
            recs.append("🚭 **STOP MEROKOK**: Program berhenti merokok wajib. (Sumber: WHO Tobacco Free Initiative)")
        if input_data['bmi'] >= 30:
            recs.append("⚖️ **MANAJEMEN BERAT BADAN**: Rujuk ke Ahli Gizi. Target penurunan BB 5-10%. (Sumber: WHO BMI)")
        if input_data['map'] > 105:
            recs.append("🩺 **HIPERTENSI**: Monitoring tekanan darah harian. Pertimbangkan ACE-Inhibitor/ARB. (Sumber: JNC 8)")
        if input_data['cholesterol'] >= 3:
            recs.append("🍔 **KOLESTEROL**: Diet rendah lemak jenuh. Cek ulang profil lipid 1 bulan. (Sumber: ESC/EAS)")
        if input_data['gluc'] >= 3:
            recs.append("🍬 **DIABETES**: Cek HbA1c. Konsul Endokrin jika perlu. (Sumber: ADA Standards)")
        
        recommendations_str = "\n".join(recs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

    # 3. Save to DB
    return crud.create_checkup(
        db=db, 
        checkup=checkup, 
        patient_id=patient_id, 
        probability=proba, 
        risk_label=label, 
        risk_category=risk_cat,
        model_version=model_version,
        recommendations=recommendations_str,
        shap_values=shap_json
    )

@app.get("/patients/{patient_id}/checkups/", response_model=List[schemas.Checkup])
def read_checkups(patient_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    checkups = crud.get_checkups_by_patient(db, patient_id=patient_id, skip=skip, limit=limit)
    return checkups

@app.get("/checkups/", response_model=List[schemas.Checkup])
def read_all_checkups(limit: int = 1000, db: Session = Depends(get_db)):
    return crud.get_all_checkups(db, limit=limit)

@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_checkup_stats(db)
