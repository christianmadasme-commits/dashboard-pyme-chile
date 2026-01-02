import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import numpy as np

# --- 1. CONFIGURACIÓN VISUAL BLINDADA (CSS) ---
st.set_page_config(page_title="Growth AI | Partner", layout="wide", page_icon="✨")

st.markdown("""
<style>
    /* 1. FORZAR VARIABLES DE COLOR GLOBALES (Gana al Modo Oscuro) */
    :root {
        --primary-color: #1A2980;
        --background-color: #f0f2f5;
        --secondary-background-color: #ffffff;
        --text-color: #1f1f1f;
        --font: 'Inter', sans-serif;
    }

    /* 2. FONDO GENERAL */
    [data-testid="stAppViewContainer"] {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 3. SIDEBAR (Barra Lateral) */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        border-right: 1px solid #e0e0e0;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #333333 !important; /* Texto oscuro forzado en sidebar */
    }

    /* 4. TARJETAS DE MÉTRICAS (Glassmorphism) */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #666666 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #1A2980 !important;
        font-size: 28px !important;
    }

    /* 5. BOTONES VIBRANTES (Gradiente) */
    div.stButton > button {
        background: linear-gradient(90deg, #1A2980 0%, #26D0CE 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(26, 41, 128, 0.2) !important;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.03);
    }

    /* 6. PESTAÑAS Y TEXTOS */
    h1, h2, h3 { color: #1f1f1f !important; }
    p, li { color: #4a4a4a !important; }
    
    .custom-card {
        background-color: white !important;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        color: #333 !important;
    }
    
    /* Arreglo para el texto del File Uploader */
    [data-testid="stFileUploader"] label {
        color: #333 !important;
    }
    [data-testid="stFileUploader"] {
        background-color: white !important;
        padding: 20px; 
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)

# --- 2. MOTORES (Lógica igual, solo limpieza interna) ---

def motor_marketing(industria, ticket_promedio):
    plan = {}
    if industria == "Transporte / Logística":
        plan['Canales'] = ["Google Ads (B2B)", "Email Directo", "LinkedIn"]
        plan['Mensaje'] = "Seguridad y Puntualidad Certificada."
        plan['Costo_Lead_Est'] = 15000 
        plan['Conversion_Est'] = 0.10  
    elif industria == "Retail / Comercio":
        plan['Canales'] = ["Instagram Ads", "TikTok", "Google Shopping"]
        plan['Mensaje'] = "Ofertas Flash 24h."
        plan['Costo_Lead_Est'] = 3000
        plan['Conversion_Est'] = 0.05
    elif industria == "Agro / Alimentos":
        plan['Canales'] = ["Facebook Local", "WhatsApp", "Radio"]
        plan['Mensaje'] = "Directo del Productor."
        plan['Costo_Lead_Est'] = 5000
        plan['Conversion_Est'] = 0.20
    else: 
        plan['Canales'] = ["Google SEO", "Referidos", "Blog"]
        plan['Mensaje'] = "Experiencia Garantizada."
        plan['Costo_Lead_Est'] = 8000
        plan['Conversion_Est'] = 0.15
    return plan

def generar_pdf_premium(df, industria, marketing_plan, total_venta, tendencia_texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(26, 41, 128) 
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.set_xy(10, 15)
    pdf.cell(0, 10, 'PLAN ESTRATEGICO DE CRECIMIENTO', 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'1. Diagnostico Financiero ({industria})', 0, 1) 
    pdf.set_font('Arial', '', 11)
    texto_limpio = f"Facturacion Total: ${total_venta:,.0f}. Tendencia: {tendencia_texto}."
    texto_limpio = texto_limpio.replace("ó", "o").replace("ñ", "n").replace("í", "i")
    pdf.multi_cell(0, 7, texto_limpio)
    pdf.ln(5)
    
    # Tabla simple
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 10, 'Inversion (CLP)', 1, 0, 'C', 1)
    pdf.cell(60, 10, 'Leads', 1, 0, 'C', 1)
    pdf.cell(60, 10, 'Ventas Est.', 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 10)
    inversion = 100000
    leads = int(inversion / marketing_plan['Costo_Lead_Est'])
    ventas = int(leads * marketing_plan['Conversion_Est'])
    pdf.cell(60, 10, f"${inversion:,.0f}", 1, 0, 'C')
    pdf.cell(60, 10, str(leads), 1, 0, 'C')
    pdf.cell(60, 10, str(ventas), 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. INTERFAZ ---

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1067/1067357.png", width=70)
    st.markdown("### Configuración")
    uploaded_file = st.file_uploader("Subir Datos", type=["xlsx", "csv"])
    st.markdown("---")
    industria = st.selectbox("Industria", ["Transporte / Logística", "Retail / Comercio", "Agro / Alimentos", "Servicios Profesionales"])
    presupuesto = st.slider("Presupuesto (CLP)", 50000, 2000000, 250000, step=50000)

st.title("Growth AI Partner 🚀")
st.markdown("##### Inteligencia de Negocios y Marketing")

if uploaded_file:
    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
    else: df = pd.read_excel(uploaded_file)
    
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_total = next((c for c in df.columns if any(x in c.lower() for x in ['total', 'monto', 'venta'])), None)

    if col_fecha and col_total:
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df = df.sort_values(by=col_fecha)
        total_venta = df[col_total].sum()
        
        # Proyección
        df['fecha_num'] = df[col_fecha].map(pd.Timestamp.toordinal)
        reg = LinearRegression().fit(df[['fecha_num']], df[col_total])
        tendencia_txt = "ALCISTA" if reg.coef_[0] > 0 else "BAJISTA"
        tendencia_icon = "↗️ CRECIENDO" if reg.coef_[0] > 0 else "↘️ CAYENDO"

        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas Totales", f"${total_venta:,.0f}")
        c2.metric("Tendencia", tendencia_icon)
        c3.metric("Industria", industria.split("/")[0])
        st.markdown("---")
        
        # Pestañas
        tab1, tab2 = st.tabs(["📢 Estrategia", "📄 Reporte PDF"])
        
        plan = motor_marketing(industria, df[col_total].mean())
        
        with tab1:
            col_a, col_b = st.columns([1.5, 1])
            with col_a:
                st.markdown(f"""
                <div class="custom-card">
                    <h3 style="margin-top:0; color:#1A2980">Estrategia Recomendada</h3>
                    <p><b>Canales:</b> {', '.join(plan['Canales'])}</p>
                    <p><b>Mensaje Clave:</b> <i>"{plan['Mensaje']}"</i></p>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                # Simulador rápido
                leads = int(presupuesto / plan['Costo_Lead_Est'])
                st.markdown(f"""
                <div class="custom-card" style="text-align:center; background:#e8f5e9 !important;">
                    <h2 style="color:#2e7d32; margin:0;">{leads}</h2>
                    <p>Clientes Potenciales con tu presupuesto</p>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.write("Descarga el plan formal:")
            pdf_bytes = generar_pdf_premium(df, industria, plan, total_venta, tendencia_txt)
            st.download_button("📥 Descargar PDF", data=pdf_bytes, file_name="Plan.pdf", mime="application/pdf")
            
    else:
        st.error("El archivo debe tener columnas 'Fecha' y 'Monto'.")
else:
    st.info("👈 Sube tu archivo para ver la magia.")