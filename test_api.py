import requests

API_URL = "http://127.0.0.1:8000"

def test_checkup():
    # 1. Get a patient
    print("Getting patients...")
    patients = requests.get(f"{API_URL}/patients/").json()
    if not patients:
        print("No patients found. Creating one...")
        p = requests.post(f"{API_URL}/patients/", json={
            "full_name": "Test Patient",
            "date_of_birth": "1980-01-01",
            "gender": "M"
        }).json()
        patient_id = p['id']
    else:
        patient_id = patients[0]['id']
        
    print(f"Using Patient ID: {patient_id}")
    
    # 2. Create Checkup
    payload = {
        "age_years": 45,
        "gender": 2,
        "bmi": 28.5,
        "map": 110.0,
        "cholesterol": 2,
        "gluc": 1,
        "smoke": 0,
        "alco": 0,
        "active": 1,
        "checked_by_user_id": 1
    }
    
    print("Sending checkup request...")
    res = requests.post(f"{API_URL}/patients/{patient_id}/checkups/", json=payload)
    
    if res.status_code == 200:
        print("Success!")
        print(res.json())
    else:
        print(f"Failed: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    test_checkup()
