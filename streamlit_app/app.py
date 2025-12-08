import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

from PIL import Image

# API Configuration
API_URL = "http://127.0.0.1:8000"

try:
    icon = Image.open("assets/heart.png")
except:
    icon = "🫀"

st.set_page_config(
    page_title="SIAGA Jantung Pro",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Medical UI ---
st.markdown("""
<style>
    /* GLOBAL THEME */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    /* BACKGROUND */
    .stApp {
        background-color: #f1f5f9;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 24px rgba(0,0,0,0.02);
    }
    
    /* CARDS */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        border-color: #cbd5e1;
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #3b82f6; /* Default accent */
    }
    
    /* TYPOGRAPHY */
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.02em;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-sub {
        font-size: 12px;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* HEADERS */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        color: #64748b;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* BUTTONS */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None
if "user_id" not in st.session_state:
    st.session_state.user_id = 1
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Helpers ---
def get_patients(name_query=None):
    params = {}
    if name_query:
        params["name"] = name_query
    try:
        response = requests.get(f"{API_URL}/patients/", params=params)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def create_patient(data):
    try:
        response = requests.post(f"{API_URL}/patients/", json=data)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_history(patient_id):
    try:
        response = requests.get(f"{API_URL}/patients/{patient_id}/checkups/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_stats():
    try:
        response = requests.get(f"{API_URL}/stats/")
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_all_data():
    try:
        response = requests.get(f"{API_URL}/checkups/")
        return pd.DataFrame(response.json()) if response.status_code == 200 else pd.DataFrame()
    except:
        return pd.DataFrame()

# --- Visualization Functions ---
def create_gauge_chart(value, title):
    color = "green"
    if value >= 30: color = "orange"
    if value >= 60: color = "red"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 18, 'color': '#2c3e50'}},
        number = {'suffix': "%", 'font': {'color': color}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#333"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#eee",
            'steps': [
                {'range': [0, 30], 'color': "#e8f5e9"},
                {'range': [30, 60], 'color': "#fff3e0"},
                {'range': [60, 100], 'color': "#ffebee"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value}}))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_radar_chart(input_data):
    # Normalize values to 0-1 scale for visualization where 1 is "Bad/High Risk"
    # This is purely for visual representation of risk factors
    
    categories = ['BMI', 'Tekanan Darah (MAP)', 'Kolesterol', 'Glukosa', 'Gaya Hidup (Rokok/Alkohol)']
    
    # Logic normalization (Simplified)
    norm_bmi = min(max((input_data['bmi'] - 18.5) / (35 - 18.5), 0), 1)
    norm_map = min(max((input_data['map'] - 70) / (130 - 70), 0), 1)
    norm_chol = (input_data['cholesterol'] - 1) / 2
    norm_gluc = (input_data['gluc'] - 1) / 2
    
    # Lifestyle score: Smoke(1) + Alco(1) + Inactive(1) -> Max 3
    lifestyle_score = input_data['smoke'] + input_data['alco'] + (1 - input_data['active'])
    norm_lifestyle = min(lifestyle_score / 3, 1)
    
    values = [norm_bmi, norm_map, norm_chol, norm_gluc, norm_lifestyle]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Profil Pasien',
        line_color='#3498db',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=False
            )),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(text="Peta Faktor Risiko", x=0.5, y=0.95, font=dict(size=14))
    )
    return fig

# --- LOGIN PAGE ---
def login_page():
    st.markdown("""
        <style>
            .login-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
        </style>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        try:
            st.image("assets/heart.png", width=100)
        except:
            st.title("🫀")
            
        st.title("Admin Login")
        st.caption("Masuk untuk mengakses Dashboard SIAGA Jantung")
        
        with st.form("login_form"):
            username = st.text_input("Email", placeholder="admin@admin.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Masuk", type="primary", use_container_width=True)
            
            if submit:
                # CREDENTIALS CHECK
                if username.lower().strip() == "admin@admin.com" and password == "ADMIN123":
                    st.session_state.logged_in = True
                    st.toast("Login Berhasil!", icon="🔓")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Email atau Password salah!")

# --- AUTH CHECK ---
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ==========================================
# APP CONTENT (Only runs if logged_in=True)
# ==========================================

from streamlit_option_menu import option_menu

# --- Sidebar ---
with st.sidebar:
    try:
        st.image("assets/heart.png", width=70)
    except:
        st.header("🫀") # Fallback
    st.markdown("### SIAGA Jantung")
    st.caption("v2.1.0 | Professional Edition")
    
    st.divider()
    
    menu = option_menu(
        menu_title=None,
        options=["Dashboard", "Pasien", "Laporan", "Bantuan"],
        icons=["speedometer2", "people-fill", "file-earmark-bar-graph", "info-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "#64748b", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#f1f5f9", "color": "#1e293b"},
            "nav-link-selected": {"background-color": "#eff6ff", "color": "#3b82f6", "font-weight": "600", "border-left": "3px solid #3b82f6"},
        }
    )
    
    if menu == "Pasien":
        st.markdown("#### Cari Pasien")
        search = st.text_input("Nama / MRN", placeholder="Ketik nama pasien...", label_visibility="collapsed")
        if search:
            with st.spinner("Mencari..."):
                patients = get_patients(search)
            if patients:
                for p in patients:
                    if st.button(f"{p['full_name']}", key=p['id'], use_container_width=True):
                        st.session_state.selected_patient = p
                        st.rerun()
            else:
                st.warning("Tidak ditemukan.")
        
        st.markdown("---")
        with st.expander("Daftar Pasien Baru"):
            with st.form("add_patient"):
                new_name = st.text_input("Nama Lengkap")
                new_dob = st.date_input("Tanggal Lahir", min_value=datetime(1900,1,1))
                new_gender = st.selectbox("Jenis Kelamin", ["M", "F"])
                new_mrn = st.text_input("No. Rekam Medis (Opsional)")
                if st.form_submit_button("Simpan Data", type="primary"):
                    with st.spinner("Menyimpan data pasien..."):
                        p = create_patient({
                            "full_name": new_name, 
                            "date_of_birth": str(new_dob), 
                            "gender": new_gender,
                            "medical_record_number": new_mrn if new_mrn else None
                        })
                    if p:
                        st.session_state.selected_patient = p
                        st.toast("Pasien berhasil didaftarkan!", icon="✅")
                        time.sleep(1)
                        st.rerun()
    
    # Logout
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- Main Page ---
if menu == "Dashboard":
    st.title("Dashboard Klinik")
    st.markdown("Ringkasan aktivitas dan performa model hari ini.")
    
    # Fetch Model Info
    try:
        model_info = requests.get(f"{API_URL}/model-info").json()
        acc = model_info.get('accuracy', 0) * 100
        acc_display = f"{acc:.1f}%"
        last_train = model_info.get('trained_at', '-')
    except:
        acc_display = "N/A"
        last_train = "-"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">12</div><div class="metric-label"><i class="fa-solid fa-user-group"></i> Pasien Hari Ini</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label"><i class="fa-solid fa-triangle-exclamation"></i> Risiko Tinggi</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{acc_display}</div><div class="metric-label"><i class="fa-solid fa-bullseye"></i> Akurasi Model</div><div class="metric-sub">Updated: {last_train}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">v2.1</div><div class="metric-label"><i class="fa-solid fa-code-branch"></i> Versi Sistem</div></div>', unsafe_allow_html=True)

    st.markdown("### 📉 Tren Risiko Pasien (Sampel)")
    # Dummy chart for dashboard aesthetic
    chart_data = pd.DataFrame({
        'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
        'Rata-rata Risiko': [0.3, 0.32, 0.28, 0.35, 0.31, 0.29]
    })
    fig = px.area(chart_data, x='Bulan', y='Rata-rata Risiko', line_shape='spline')
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Pasien":
    if not st.session_state.selected_patient:
        st.info("Silakan cari atau pilih pasien dari sidebar untuk memulai pemeriksaan.")
    else:
        p = st.session_state.selected_patient
        
        # --- FETCH HISTORY FIRST ---
        hist = get_history(p['id'])
        df_hist = pd.DataFrame(hist) if hist else pd.DataFrame()
        if not df_hist.empty:
            df_hist['created_at'] = pd.to_datetime(df_hist['created_at'])
            df_hist = df_hist.sort_values('created_at')
            last_checkup = df_hist.iloc[-1]
        else:
            last_checkup = None

        # --- PATIENT HEADER (Medical Record Style) ---
        with st.container():
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; color: #2c3e50;">{p['full_name']}</h2>
                        <div style="color: #7f8c8d; font-size: 14px; margin-top: 5px;">
                            <span style="background-color: #eef2f7; padding: 2px 8px; border-radius: 4px; font-weight: bold;">MRN: {p.get('medical_record_number', '-') or 'N/A'}</span>
                            &nbsp; • &nbsp; {p['gender']} &nbsp; • &nbsp; {p['date_of_birth']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 12px; color: #95a5a6;">Status Pasien</div>
                        <div style="font-weight: bold; color: #27ae60;">AKTIF</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- TABS ---
        tab_dashboard, tab_checkup, tab_history = st.tabs(["📊 Dashboard Pasien", "🩺 Pemeriksaan Baru", "📜 Riwayat Lengkap"])
        
        # --- TAB 1: DASHBOARD PASIEN ---
        with tab_dashboard:
            if last_checkup is not None:
                # 1. Key Metrics Row
                m1, m2, m3, m4 = st.columns(4)
                
                # Risk Card
                risk_val = last_checkup['probability']
                risk_color = "#ef4444" if risk_val >= 0.6 else "#f59e0b" if risk_val >= 0.3 else "#22c55e"
                risk_bg = "#fef2f2" if risk_val >= 0.6 else "#fffbeb" if risk_val >= 0.3 else "#f0fdf4"
                
                with m1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid {risk_color};">
                        <div class="metric-label"><i class="fa-solid fa-heart-pulse"></i> Risiko Kardiovaskular</div>
                        <div class="metric-value" style="color: {risk_color}">{risk_val:.1%}</div>
                        <div class="metric-sub">
                            <span style="background-color: {risk_bg}; color: {risk_color}; padding: 2px 8px; border-radius: 99px; font-weight: 600; font-size: 10px;">
                                {last_checkup['risk_category'].upper()}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # BMI Card
                bmi_val = last_checkup['bmi']
                bmi_color = "#ef4444" if bmi_val >= 30 else "#f59e0b" if bmi_val >= 25 else "#22c55e"
                with m2:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid {bmi_color};">
                        <div class="metric-label"><i class="fa-solid fa-weight-scale"></i> Indeks Massa Tubuh</div>
                        <div class="metric-value">{bmi_val:.1f}</div>
                        <div class="metric-sub">kg/m²</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # MAP Card
                map_val = last_checkup['map']
                map_color = "#ef4444" if map_val > 105 else "#3b82f6"
                with m3:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid {map_color};">
                        <div class="metric-label"><i class="fa-solid fa-stethoscope"></i> Tekanan Darah (MAP)</div>
                        <div class="metric-value">{map_val:.0f}</div>
                        <div class="metric-sub">mmHg</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Visit Card
                with m4:
                    last_date = pd.to_datetime(last_checkup['created_at']).strftime("%d %b %Y")
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid #64748b;">
                        <div class="metric-label"><i class="fa-solid fa-calendar-check"></i> Kunjungan Terakhir</div>
                        <div class="metric-value" style="font-size: 24px; margin: 12px 0;">{last_date}</div>
                        <div class="metric-sub">ID: #{last_checkup['id']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)

                # 2. Charts Row
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("##### <i class='fa-solid fa-chart-line'></i> Tren Risiko", unsafe_allow_html=True)
                    fig_risk = px.area(df_hist, x='created_at', y='probability', markers=True)
                    fig_risk.update_traces(line_color='#ef4444', fillcolor='rgba(239, 68, 68, 0.1)')
                    fig_risk.update_layout(
                        yaxis_range=[0, 1], 
                        height=280, 
                        margin=dict(l=0,r=0,t=0,b=0),
                        xaxis_title=None,
                        yaxis_title=None,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        showlegend=False
                    )
                    fig_risk.update_xaxes(showgrid=False)
                    fig_risk.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
                    st.plotly_chart(fig_risk, use_container_width=True)
                    
                with c2:
                    st.markdown("##### <i class='fa-solid fa-heart-pulse'></i> Tren Tekanan Darah", unsafe_allow_html=True)
                    fig_map = px.line(df_hist, x='created_at', y='map', markers=True)
                    fig_map.update_traces(line_color='#3b82f6', line_width=3)
                    fig_map.update_layout(
                        height=280, 
                        margin=dict(l=0,r=0,t=0,b=0),
                        xaxis_title=None,
                        yaxis_title=None,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        showlegend=False
                    )
                    fig_map.update_xaxes(showgrid=False)
                    fig_map.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
                    st.plotly_chart(fig_map, use_container_width=True)

                # 3. Recommendations (Styled)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### <i class='fa-solid fa-clipboard-list'></i> Rekomendasi Medis & Tindakan", unsafe_allow_html=True)
                if last_checkup.get('recommendations'):
                    for rec in last_checkup['recommendations'].split('\n'):
                        st.markdown(f"""
                        <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 12px 16px; margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 14px;">
                            {rec}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ Tidak ada rekomendasi khusus.")

            else:
                st.info("Belum ada data pemeriksaan untuk pasien ini. Silakan lakukan pemeriksaan baru.")

        # --- TAB 2: PEMERIKSAAN BARU ---
        with tab_checkup:
            col_input, col_viz = st.columns([1.2, 1.8])
            
            with col_input:
                st.subheader("Input Data Klinis")
                with st.form("checkup_form"):
                    # Auto calc age
                    dob = datetime.strptime(p['date_of_birth'], "%Y-%m-%d")
                    age = (datetime.now() - dob).days // 365
                    
                    st.caption("Fisiologis")
                    c_a, c_b = st.columns(2)
                    with c_a:
                        age_years = st.number_input("Usia", value=age, disabled=True)
                        height = st.number_input("Tinggi (cm)", 100, 250, 170)
                        weight = st.number_input("Berat (kg)", 30.0, 200.0, 70.0)
                    with c_b:
                        ap_hi = st.number_input("Sistolik (mmHg)", 80, 250, 120)
                        ap_lo = st.number_input("Diastolik (mmHg)", 40, 150, 80)
                    
                    st.caption("Lab & Gaya Hidup")
                    c_c, c_d = st.columns(2)
                    with c_c:
                        chol = st.selectbox("Kolesterol", ["Normal", "Sedang", "Tinggi"])
                        gluc = st.selectbox("Glukosa", ["Normal", "Sedang", "Tinggi"])
                    with c_d:
                        smoke = st.checkbox("Merokok")
                        alco = st.checkbox("Alkohol")
                        active = st.checkbox("Aktif Fisik")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit = st.form_submit_button("Analisis Risiko", type="primary")
            
            with col_viz:
                if submit:
                    if age < 5:
                        st.error("⚠️ Analisis tidak dapat dilakukan. Pasien harus berusia minimal 5 tahun.")
                    else:
                        # Loading Indicator
                        with st.spinner("Memproses Data..."):
                            time.sleep(0.5) # Simulate work
                            
                            chol_map = {"Normal": 1, "Sedang": 2, "Tinggi": 3}
                            gluc_map = {"Normal": 1, "Sedang": 2, "Tinggi": 3}
                            bmi = weight / ((height/100)**2)
                            map_val = (2*ap_lo + ap_hi)/3
                            
                            payload = {
                                "age_years": age_years,
                                "gender": 1 if p['gender'] == 'F' else 2,
                                "bmi": bmi,
                                "map": map_val,
                                "cholesterol": chol_map[chol],
                                "gluc": gluc_map[gluc],
                                "smoke": int(smoke),
                                "alco": int(alco),
                                "active": int(active),
                                "checked_by_user_id": st.session_state.user_id
                            }
                            
                            try:
                                res = requests.post(f"{API_URL}/patients/{p['id']}/checkups/", json=payload, timeout=30)
                                if res.status_code == 200:
                                    data = res.json()
                                    
                                    # --- RESULTS DISPLAY ---
                                    st.success("Analisis Selesai! Data tersimpan.")
                                    
                                    # Top Row: Gauge & Radar
                                    r1, r2 = st.columns([1, 1])
                                    with r1:
                                        try:
                                            prob = data['probability'] * 100
                                            st.plotly_chart(create_gauge_chart(prob, "Probabilitas Risiko"), use_container_width=True)
                                        except Exception as e:
                                            st.error(f"Gagal menampilkan Gauge Chart: {e}")
                                    with r2:
                                        try:
                                            # Display SHAP if available, otherwise Radar
                                            if data.get('shap_values'):
                                                import json
                                                shap_vals = json.loads(data['shap_values'])
                                                # Create Bar Chart for SHAP
                                                shap_df = pd.DataFrame(list(shap_vals.items()), columns=['Faktor', 'Impact'])
                                                shap_df = shap_df.sort_values(by='Impact', key=abs, ascending=True) # Sort by absolute impact
                                                
                                                fig_shap = px.bar(shap_df, x='Impact', y='Faktor', orientation='h', 
                                                                title="Kontribusi Faktor Risiko (SHAP)",
                                                                color='Impact', color_continuous_scale=['#2ecc71', '#e74c3c'])
                                                fig_shap.update_layout(height=300, margin=dict(l=0,r=0,t=30,b=0), showlegend=False)
                                                st.plotly_chart(fig_shap, use_container_width=True)
                                            else:
                                                st.plotly_chart(create_radar_chart(payload), use_container_width=True)
                                        except Exception as e:
                                            st.error(f"Gagal menampilkan SHAP/Radar Chart: {e}")
                                    
                                    # Recommendations
                                    st.subheader("Rekomendasi Medis")
                                    if data.get('recommendations'):
                                        for rec in data['recommendations'].split('\n'):
                                            st.info(f"{rec}")
                                    else:
                                        st.success("Tidak ada rekomendasi khusus. Kondisi pasien baik.")
                                        
                                else:
                                    st.error(f"Gagal! Server merespon: {res.status_code}")
                            except Exception as e:
                                st.error(f"Tidak dapat terhubung ke server: {e}")
                else:
                    # Placeholder state
                    st.markdown("""
                    <div style="text-align: center; padding: 50px; color: #aaa;">
                        <img src="https://img.icons8.com/ios/100/cccccc/medical-doctor.png"/>
                        <h3>Menunggu Input</h3>
                        <p>Isi data klinis di sebelah kiri dan klik tombol Analisis untuk melihat hasil prediksi AI dan visualisasi risiko.</p>
                    </div>
                    """, unsafe_allow_html=True)

        # --- TAB 3: RIWAYAT LENGKAP ---
        with tab_history:
            if not df_hist.empty:
                # Add Download Button for THIS Patient
                csv_patient = df_hist.to_csv(index=False).encode('utf-8')
                
                # Format Filename: HEARTREPORT_NAMA_RMN_TANGGAL_
                safe_name = p['full_name'].replace(" ", "_").upper()
                safe_mrn = str(p.get('medical_record_number', 'NA')).replace(" ", "")
                date_str = datetime.now().strftime("%d%m%Y")
                filename = f"HEARTREPORT_{safe_name}_{safe_mrn}_{date_str}_.csv"
                
                st.download_button(
                    label="📥 Unduh Riwayat Pasien (.csv)",
                    data=csv_patient,
                    file_name=filename,
                    mime="text/csv",
                    type="primary"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.dataframe(
                    df_hist[['created_at', 'risk_category', 'probability', 'recommendations', 'bmi', 'map', 'smoke', 'alco', 'active']].style.format({
                        'probability': '{:.1%}',
                        'bmi': '{:.1f}',
                        'map': '{:.1f}'
                    }),
                    use_container_width=True
                )
            else:
                st.info("Belum ada riwayat pemeriksaan.")

elif menu == "Laporan":
    st.title("Laporan & Statistik")
    st.markdown("Statistik *real-time* dari seluruh data populasi pasien.")
    
    stats = get_stats()
    
    if stats:
        # --- Top Metrics ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total_patients"]}</div><div class="metric-label">Total Pasien</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total_checkups"]}</div><div class="metric-label">Total Pemeriksaan</div></div>', unsafe_allow_html=True)
        with m3:
            avg_risk = (stats['averages']['risk'] or 0) * 100
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_risk:.1f}%</div><div class="metric-label">Rata-rata Risiko</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["risk_factors"]["Hipertensi"]}</div><div class="metric-label">Kasus Hipertensi</div></div>', unsafe_allow_html=True)
            
        st.divider()

        # --- Visualizations ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Distribusi Risiko Kardiovaskular")
            risk_data = stats['risk_distribution']
            if risk_data:
                labels = list(risk_data.keys())
                values = list(risk_data.values())
                colors = {'Rendah':'#2ecc71', 'Sedang':'#f1c40f', 'Tinggi':'#ef4444'}
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=labels, 
                    values=values, 
                    hole=.5,
                    marker_colors=[colors.get(l, '#ccc') for l in labels],
                    textinfo='label+percent',
                    textfont_size=14
                )])
                fig_pie.update_layout(
                    showlegend=True, 
                    legend=dict(orientation="h", y=-0.1),
                    height=350, 
                    margin=dict(l=0,r=0,t=20,b=0)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Belum ada data risiko.")
            
        with c2:
            st.subheader("Prevalensi Faktor Risiko")
            rf = stats['risk_factors']
            rf_df = pd.DataFrame(list(rf.items()), columns=['Faktor', 'Jumlah'])
            rf_df = rf_df.sort_values('Jumlah', ascending=True)
            
            fig_bar = px.bar(rf_df, x='Jumlah', y='Faktor', orientation='h', 
                             text='Jumlah', color='Jumlah',
                             color_continuous_scale='Blues')
            fig_bar.update_layout(
                yaxis_title=None, 
                xaxis_title="Jumlah Kasus", 
                height=350,
                margin=dict(l=0,r=0,t=20,b=0),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- Actions ---
        st.markdown("### 📥 Ekspor Data")
        
        # FETCH REAL DATA
        df_all = get_all_data()
        
        col_dl, col_info = st.columns([1, 2])
        with col_dl:
            if not df_all.empty:
                csv_data = df_all.to_csv(index=False).encode('utf-8')
                current_date = datetime.now().strftime("%Y%m%d")
                
                # Using emoji in label as a failsafe for icon
                st.download_button(
                    label="📥 Unduh Laporan (.csv)",
                    data=csv_data,
                    file_name=f"laporan_kesehatan_{current_date}.csv",
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.warning("⚠️ Belum ada data untuk diunduh.")
                
        with col_info:
            st.caption("Unduh data lengkap pemeriksaan untuk keperluan audit medis. Data berisi seluruh rekam jejak pemeriksaan pasien.")

    else:
        st.error("Gagal memuat data statistik. Pastikan server backend berjalan.")

    st.markdown("### 📋 Rekomendasi Klinis Populasi")
    st.info("⚠️ Data menunjukkan prevalensi hipertensi yang signifikan. Disarankan untuk mengadakan penyuluhan diet rendah garam bulan ini.")

elif menu == "Bantuan":
    st.markdown("### Panduan Penggunaan")
    st.markdown("""
    1. **Pilih Pasien**: Gunakan menu 'Pasien' di sidebar untuk mencari atau mendaftarkan pasien baru.
    2. **Dashboard Pasien**: Lihat ringkasan kesehatan pasien, tren risiko, dan vital signs.
    3. **Pemeriksaan Baru**: Input data klinis untuk mendapatkan analisis risiko terbaru.
    4. **Interpretasi**:
       - **Gauge Chart**: Menunjukkan tingkat risiko keseluruhan.
       - **Radar Chart**: Menunjukkan faktor risiko dominan.
    5. **Rekomendasi**: Ikuti saran medis yang diberikan (dilengkapi sumber referensi).
    """)
