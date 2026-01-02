import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL PREMIUM (CSS) ---
st.set_page_config(page_title="Growth Partner AI", layout="wide", page_icon="🚀")

# Inyección de CSS para diseño moderno
st.markdown("""
<style>
    .stApp {background-color: #f4f6f9;}
    .css-1r6slb0 {background-color: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    div[data-testid="stMetricValue"] {font-size: 28px; color: #004aad; font-weight: bold;}
    div[data-testid="stMetricLabel"] {font-size: 14px; color: #666;}
    h1 {color: #1a202c; font-family: 'Helvetica Neue', sans-serif;}
    h2 {color: #2d3748;}
    h3 {color: #004aad;}
    .stButton>button {
        background-color: #004aad; color: white; border-radius: 8px; border: none; padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {background-color: #003380; transform: scale(1.02);}
</style>
""", unsafe_allow_html=True)

# --- 2. MOTORES DE LÓGICA DE NEGOCIO ---

def motor_marketing(industria, ticket_promedio):
    plan = {}
    if industria == "Transporte / Logística":
        plan['Canales'] = ["Google Ads (Palabras Clave: 'Fletes', 'Carga')", "Email a Jefes de Bodega", "LinkedIn B2B"]
        plan['Mensaje'] = "Seguridad, Puntualidad y Flota Renovada."
        plan['Costo_Lead_Est'] = 15000 
        plan['Conversion_Est'] = 0.10  
    elif industria == "Retail / Comercio":
        plan['Canales'] = ["Instagram Ads (Reels)", "TikTok (Tendencias)", "Email Marketing (Carritos abandonados)"]
        plan['Mensaje'] = "Oferta Flash, Escasez (Solo por hoy) y Envío Gratis."
        plan['Costo_Lead_Est'] = 3000
        plan['Conversion_Est'] = 0.05
    elif industria == "Agro / Alimentos":
        plan['Canales'] = ["Facebook Groups Locales", "WhatsApp Business", "Radio Local"]
        plan['Mensaje'] = "Frescura, Directo del Productor, Precios Mayoristas."
        plan['Costo_Lead_Est'] = 5000
        plan['Conversion_Est'] = 0.20
    else: 
        plan['Canales'] = ["Google Maps (SEO Local)", "Referidos (Boca a Boca digital)"]
        plan['Mensaje'] = "Confianza, Experiencia y Garantía."
        plan['Costo_Lead_Est'] = 8000
        plan['Conversion_Est'] = 0.15
    return plan

def generar_pdf_premium(df, industria, marketing_plan, total_venta, tendencia_texto):
    # NOTA: Recibimos 'tendencia_texto' que NO tiene emojis para evitar el error
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_fill_color(0, 74, 173) 
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.set_xy(10, 15)
    pdf.cell(0, 10, 'PLAN ESTRATEGICO DE CRECIMIENTO', 0, 1, 'C')
    
    # Reset colores
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(50)
    
    # Sección 1: Diagnóstico
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'1. Diagnostico Financiero ({industria})', 0, 1) # Quitamos tilde para seguridad máxima
    pdf.set_font('Arial', '', 11)
    
    # Limpiamos el texto de cualquier caracter extraño antes de escribir
    texto_diagnostico = f"La empresa ha facturado ${total_venta:,.0f}. La tendencia actual es {tendencia_texto}. Se detectan oportunidades de optimizacion."
    # Reemplazamos caracteres problemáticos por seguridad
    texto_diagnostico = texto_diagnostico.replace("ó", "o").replace("ñ", "n").replace("í", "i")
    
    pdf.multi_cell(0, 7, texto_diagnostico)
    pdf.ln(5)
    
    # Sección 2: Plan de Marketing
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Estrategia de Marketing Recomendada', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    canales_str = ', '.join(marketing_plan['Canales']).replace("ñ", "n").replace("ó", "o")
    mensaje_str = marketing_plan['Mensaje'].replace("ñ", "n").replace("ó", "o")
    
    pdf.multi_cell(0, 8, f"Canales Prioritarios: {canales_str}")
    pdf.multi_cell(0, 8, f"Eje de Comunicacion: {mensaje_str}")
    pdf.ln(5)
    
    # Sección 3: Tabla
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Escenario de Inversion Publicitaria', 0, 1)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 10, 'Inversion Mensual (CLP)', 1, 0, 'C', 1)
    pdf.cell(60, 10, 'Leads Estimados', 1, 0, 'C', 1)
    pdf.cell(60, 10, 'Ventas Proyectadas', 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 10)
    inversion = 100000
    costo = marketing_plan['Costo_Lead_Est']
    conv = marketing_plan['Conversion_Est']
    leads = int(inversion / costo)
    ventas = int(leads * conv)
    
    pdf.cell(60, 10, f"${inversion:,.0f}", 1, 0, 'C')
    pdf.cell(60, 10, f"{leads} potenciales", 1, 0, 'C')
    pdf.cell(60, 10, f"{ventas} cierres", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. INTERFAZ PRINCIPAL ---

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.header("Configuración")
    uploaded_file = st.file_uploader("Subir Datos", type=["xlsx", "csv"])
    st.markdown("---")
    st.subheader("Perfil de la Empresa")
    industria = st.selectbox("Industria / Rubro", 
                             ["Transporte / Logística", "Retail / Comercio", "Agro / Alimentos", "Servicios Profesionales"])
    presupuesto = st.slider("Presupuesto Marketing (CLP)", 50000, 1000000, 150000, step=50000)

st.title("🚀 Growth Partner: Inteligencia de Negocios")
st.markdown("Transformamos datos en **acciones reales de venta**.")

if uploaded_file:
    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
    else: df = pd.read_excel(uploaded_file)
    
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_total = next((c for c in df.columns if any(x in c.lower() for x in ['total', 'monto', 'venta'])), None)

    if col_fecha and col_total:
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df = df.sort_values(by=col_fecha)
        
        total_venta = df[col_total].sum()
        ticket_promedio = df[col_total].mean()
        
        df['fecha_num'] = df[col_fecha].map(pd.Timestamp.toordinal)
        reg = LinearRegression().fit(df[['fecha_num']], df[col_total])
        
        # --- AQUÍ ESTÁ EL ARREGLO ---
        # Creamos dos variables: una con emoji para la pantalla, otra limpia para el PDF
        if reg.coef_[0] > 0:
            tendencia_visual = "ALCISTA 🟢"
            tendencia_texto = "ALCISTA" 
        else:
            tendencia_visual = "BAJISTA 🔴"
            tendencia_texto = "BAJISTA"
        
        # --- TABLERO VISUAL ---
        st.markdown("### 📊 Estado Actual")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Venta Total", f"${total_venta:,.0f}")
        c2.metric("Ticket Promedio", f"${ticket_promedio:,.0f}")
        c3.metric("Tendencia", tendencia_visual) # Aquí usamos la visual
        c4.metric("Industria", industria.split("/")[0])
        st.markdown("---")
        
        tab_mkt, tab_adv, tab_rep = st.tabs(["📢 Plan de Marketing", "📈 Proyección de Campañas", "📄 Reporte Final"])
        
        marketing_plan = motor_marketing(industria, ticket_promedio)
        
        with tab_mkt:
            st.subheader(f"Estrategia Recomendada para {industria}")
            col_izq, col_der = st.columns([1, 1])
            with col_izq:
                st.markdown(f"""
                <div class="css-1r6slb0">
                    <h4>🎯 Dónde invertir tu dinero</h4>
                    <ul>{''.join([f'<li>{c}</li>' for c in marketing_plan['Canales']])}</ul>
                    <br><h4>🗣️ Qué decir (Copywriting)</h4>
                    <p><i>"{marketing_plan['Mensaje']}"</i></p>
                </div>""", unsafe_allow_html=True)
            with col_der:
                labels = marketing_plan['Canales']
                values = [50, 30, 20]
                fig = px.pie(values=values, names=labels, title="Distribución de Presupuesto", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

        with tab_adv:
            st.subheader("💡 Simulador de Retorno de Inversión (ROI)")
            st.info("Mueve el deslizador de presupuesto en la barra lateral para recalcular.")
            costo_lead = marketing_plan['Costo_Lead_Est']
            tasa_cierre = marketing_plan['Conversion_Est']
            leads_estimados = int(presupuesto / costo_lead)
            ventas_estimadas = int(leads_estimados * tasa_cierre)
            retorno_estimado = ventas_estimadas * ticket_promedio
            
            c_a, c_b, c_c = st.columns(3)
            c_a.markdown(f"""<div style="text-align:center; padding:10px; border:1px solid #ddd; border-radius:10px;">
                <h3 style="color:#004aad">{leads_estimados}</h3><p>Clientes Potenciales</p></div>""", unsafe_allow_html=True)
            c_b.markdown(f"""<div style="text-align:center; padding:10px; border:1px solid #ddd; border-radius:10px; background-color:#e6f4ea;">
                <h3 style="color:#1e8e3e">{ventas_estimadas}</h3><p>Ventas Cerradas Est.</p></div>""", unsafe_allow_html=True)
            c_c.markdown(f"""<div style="text-align:center; padding:10px; border:1px solid #ddd; border-radius:10px;">
                <h3 style="color:#333">${retorno_estimado:,.0f}</h3><p>Retorno Esperado</p></div>""", unsafe_allow_html=True)

        with tab_rep:
            st.subheader("Descargar Plan Estratégico")
            st.write("Obtén este análisis en un documento formal.")
            
            # Pasamos la variable 'tendencia_texto' (la limpia) al generador de PDF
            pdf_bytes = generar_pdf_premium(df, industria, marketing_plan, total_venta, tendencia_texto)
            
            st.download_button(
                label="📥 Descargar Estrategia en PDF",
                data=pdf_bytes,
                file_name=f"Estrategia_{industria.split()[0]}.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Formato de archivo no reconocido. Asegúrate de tener columnas Fecha y Monto.")
else:
    st.info("👈 Selecciona la industria y sube el archivo para comenzar.")