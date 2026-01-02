import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
import numpy as np
from fpdf import FPDF
from datetime import datetime
import re

# --- 1. CONFIGURACIÓN VISUAL CORPORATIVA ---
st.set_page_config(page_title="Navy Strategic Suite Pro", layout="wide", page_icon="⚓")

# CSS Profesional
st.markdown("""
<style>
    :root {
        --primary-navy: #001f3f;
        --secondary-blue: #003366;
        --accent-gold: #D4AF37;
        --bg-light: #f4f7f6;
        --text-dark: #2c3e50;
        --text-light: #ffffff;
    }
    [data-testid="stAppViewContainer"] {background-color: var(--bg-light) !important; color: var(--text-dark) !important;}
    section[data-testid="stSidebar"] {background-color: var(--primary-navy) !important; border-right: 2px solid var(--secondary-blue);}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] p {color: var(--text-light) !important;}
    h1.main-title {color: var(--primary-navy); font-weight: 800; border-bottom: 3px solid var(--accent-gold); padding-bottom: 15px; display: inline-block;}
    div[data-testid="metric-container"] {background-color: #ffffff; border-left: 5px solid var(--primary-navy); box-shadow: 0 4px 6px rgba(0,0,0,0.05); padding: 15px; border-radius: 8px;}
    div[data-testid="stMetricValue"] {color: var(--primary-navy) !important; font-weight: 700; font-size: 28px !important;}
    div.stButton > button {background-color: var(--primary-navy) !important; color: white !important; border-radius: 5px; font-weight: bold; border: none;}
    
    /* Estilos Nuevos para el Simulador */
    .sim-card {background: #e3f2fd; padding: 20px; border-radius: 10px; border: 1px solid #bbdefb; text-align: center;}
    .sim-result {font-size: 2em; font-weight: bold; color: #001f3f;}
    
    /* Estilos para Anomalías */
    .anomaly-alert {background-color: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; border-left: 5px solid #c62828; margin-bottom: 5px;}
</style>
""", unsafe_allow_html=True)

# --- 2. MOTORES DE INTELIGENCIA ---

def clean_text(text):
    if not isinstance(text, str): return text
    return re.sub(r'[^\x00-\x7F]+', '', text).replace('\n', ' ')

def motor_financiero(df, col_fecha, col_total):
    df_reg = df.copy()
    df_reg['fecha_num'] = df_reg[col_fecha].map(pd.Timestamp.toordinal)
    model = LinearRegression().fit(df_reg[['fecha_num']], df_reg[col_total])
    pendiente = model.coef_[0]
    
    tendencia_score = "Crecimiento" if pendiente > 0 else "Contraccion"
    cv = df[col_total].std() / df[col_total].mean() if df[col_total].mean() > 0 else 0
    estabilidad = "Alta" if cv < 0.2 else "Baja (Volatil)"
    return tendencia_score, pendiente, estabilidad

def motor_anomalias(df, col_total):
    """Detecta transacciones sospechosas usando Isolation Forest"""
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(df[[col_total]])
    anomalias = df[df['anomaly'] == -1]
    return anomalias

def motor_simulacion(total_venta_actual, margen_actual_pct, aumento_precio_pct, reduccion_costo_pct):
    """Calcula el nuevo escenario financiero"""
    costo_actual = total_venta_actual * (1 - (margen_actual_pct/100))
    ganancia_actual = total_venta_actual - costo_actual
    
    nueva_venta = total_venta_actual * (1 + (aumento_precio_pct/100))
    factor_elasticidad = 0.2
    volumen_ajustado = 1 - (aumento_precio_pct/100 * factor_elasticidad)
    nueva_venta_real = nueva_venta * volumen_ajustado
    
    nuevo_costo = costo_actual * (1 - (reduccion_costo_pct/100)) * volumen_ajustado
    nueva_ganancia = nueva_venta_real - nuevo_costo
    
    diferencia = nueva_ganancia - ganancia_actual
    return ganancia_actual, nueva_ganancia, diferencia

def motor_estrategico_mkt(industria, presupuesto):
    plan = {}
    if industria == "Transporte / Logística":
        plan['Mix'] = {"Google Ads B2B": 50, "LinkedIn": 30, "Email": 20}
        plan['Foco'] = "Captación B2B Corporativa"
        plan['CPL_Est'] = 15000 
    elif industria == "Retail":
        plan['Mix'] = {"Meta Ads": 60, "Google Shop": 25, "TikTok": 15}
        plan['Foco'] = "Venta Impulsiva Online"
        plan['CPL_Est'] = 3000
    else: 
        plan['Mix'] = {"Google Search": 40, "Social Media": 40, "Referidos": 20}
        plan['Foco'] = "Posicionamiento Local"
        plan['CPL_Est'] = 7000
    plan['Leads_Est'] = int(presupuesto / plan['CPL_Est'])
    return plan

# --- 3. REPORTING PDF ---
class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(0, 31, 63)
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 10)
        self.cell(0, 10, 'INFORME ESTRATEGICO - NAVY SUITE', 0, 1)
        self.set_text_color(0,0,0)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf(metrics, mkt, simulacion_txt):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    pdf.cell(0, 10, f"Resumen Financiero", 0, 1, 'B')
    pdf.multi_cell(0, 7, f"Total Facturado: ${metrics['total']:,.0f}\nTendencia: {metrics['tendencia']}\nEstabilidad: {metrics['estabilidad']}")
    pdf.ln(5)
    
    pdf.cell(0, 10, f"Plan de Marketing ({metrics['industria']})", 0, 1, 'B')
    pdf.multi_cell(0, 7, f"Foco Estrategico: {clean_text(mkt['Foco'])}\nLeads Estimados: {mkt['Leads_Est']} mensuales.")
    pdf.ln(5)
    
    pdf.cell(0, 10, f"Analisis de Simulacion", 0, 1, 'B')
    pdf.multi_cell(0, 7, clean_text(simulacion_txt))
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. INTERFAZ PRINCIPAL ---

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    uploaded_file = st.file_uploader("Cargar Datos", type=["xlsx", "csv"])
    
    st.markdown("---")
    st.markdown("### 🇨🇱 Indicadores Económicos")
    col_uf, col_usd = st.columns(2)
    col_uf.metric("UF", "$38.500")
    col_usd.metric("Dólar", "$945")
    
    st.markdown("---")
    industria = st.selectbox("Industria", ["Transporte / Logística", "Retail", "Servicios"])
    presupuesto = st.slider("Presupuesto MKT", 100000, 2000000, 300000)

st.markdown("<h1 class='main-title'>Navy Strategic Suite | Pro</h1>", unsafe_allow_html=True)

if uploaded_file:
    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
    else: df = pd.read_excel(uploaded_file)
    
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_total = next((c for c in df.columns if any(x in c.lower() for x in ['total', 'monto', 'venta'])), None)

    if col_fecha and col_total:
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df = df.sort_values(by=col_fecha)
        
        # Filtro Global
        min_date, max_date = df[col_fecha].min().date(), df[col_fecha].max().date()
        rango = st.slider("Filtrar Periodo", min_date, max_date, (min_date, max_date))
        df_filt = df[(df[col_fecha].dt.date >= rango[0]) & (df[col_fecha].dt.date <= rango[1])]

        # Cálculos Base
        total = df_filt[col_total].sum()
        tendencia, pend, estab = motor_financiero(df_filt, col_fecha, col_total)
        mkt_plan = motor_estrategico_mkt(industria, presupuesto)

        # Inicializar variable de simulación (Evita error si no se usa el tab simulador)
        simulacion_msg = "No se ejecutaron simulaciones personalizadas."

        # --- TABS DE FUNCIONALIDAD AVANZADA ---
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard Ejecutivo", "🧪 Simulador de Ganancias", "🚨 Auditoría IA", "📄 Reporte"])

        with tab1: # Dashboard
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Facturación", f"${total:,.0f}")
            k2.metric("Operaciones", len(df_filt))
            k3.metric("Tendencia", tendencia, delta=f"{pend:.1f}", delta_color="normal" if pend>0 else "inverse")
            k4.metric("Estabilidad", estab)
            
            st.markdown("### Evolución y Proyección")
            fig = px.area(df_filt, x=col_fecha, y=col_total, title="Flujo de Caja Histórico")
            # --- CORRECCIÓN AQUÍ: 'fillcolor' en lugar de 'fill_color' ---
            fig.update_traces(line_color='#001f3f', fillcolor='rgba(0, 31, 63, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Mix de Marketing
            st.markdown("### Estrategia de Inversión")
            c_a, c_b = st.columns(2)
            with c_a:
                fig_pie = px.pie(values=list(mkt_plan['Mix'].values()), names=list(mkt_plan['Mix'].keys()), title="Mix de Medios Recomendado", hole=0.5)
                fig_pie.update_traces(marker=dict(colors=['#001f3f', '#003366', '#0059b3']))
                st.plotly_chart(fig_pie, use_container_width=True)
            with c_b:
                st.info(f"💡 **Recomendación:** Enfóquese en {mkt_plan['Foco']}. Con su presupuesto actual, esperamos generar **{mkt_plan['Leads_Est']} leads** mensuales.")

        with tab2: # Simulador
            st.subheader("Laboratorio de Escenarios 'What-If'")
            st.markdown("Juegue con las variables para proyectar su futuro financiero.")
            
            col_sim_input, col_sim_output = st.columns([1, 2])
            
            with col_sim_input:
                st.markdown("**Variables de Control**")
                margen_actual = st.slider("Margen Actual Estimado (%)", 5, 50, 20)
                aumento_precio = st.slider("📈 Aumento de Precios (%)", 0, 20, 0)
                reduccion_costo = st.slider("✂️ Reducción de Costos (%)", 0, 20, 0)
            
            gan_act, gan_new, diff = motor_simulacion(total, margen_actual, aumento_precio, reduccion_costo)
            
            with col_sim_output:
                st.markdown("<div class='sim-card'>", unsafe_allow_html=True)
                c_s1, c_s2 = st.columns(2)
                c_s1.metric("Ganancia Actual Est.", f"${gan_act:,.0f}")
                c_s2.metric("Ganancia Proyectada", f"${gan_new:,.0f}", delta=f"${diff:,.0f}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                if diff > 0:
                    st.success(f"🚀 **Impacto:** Con estos cambios, su bolsillo crecería un **{((gan_new-gan_act)/gan_act)*100:.1f}%**.")
                    simulacion_msg = f"Escenario Positivo: Aumentar precios un {aumento_precio}% y reducir costos un {reduccion_costo}% generaria ${diff:,.0f} adicionales."
                else:
                    st.warning("⚠️ Los cambios no generan impacto positivo o son neutros.")
                    simulacion_msg = "Escenario Neutro/Negativo."

        with tab3: # Auditoría
            st.subheader("Detector de Anomalías Financieras")
            anomalias = motor_anomalias(df_filt, col_total)
            
            if not anomalias.empty:
                st.error(f"⚠️ Se detectaron **{len(anomalias)} movimientos sospechosos**.")
                st.dataframe(anomalias[[col_fecha, col_total]].style.format({col_total: "${:,.0f}"}))
            else:
                st.success("✅ Auditoría Limpia: No se encontraron anomalías estadísticas.")

        with tab4: # Reporte
            st.subheader("Entregable Ejecutivo")
            st.write("Descargue el análisis completo para reuniones de directorio.")
            
            metrics = {'total': total, 'tendencia': tendencia, 'estabilidad': estab, 'industria': industria}
            # simulacion_msg ahora está definido siempre
            pdf_bytes = generar_pdf(metrics, mkt_plan, simulacion_msg)
            
            st.download_button("📥 Descargar PDF Oficial", data=pdf_bytes, file_name="Reporte_Navy_Pro.pdf", mime="application/pdf")

    else:
        st.error("Formato irreconocible. Se requieren columnas 'Fecha' y 'Monto'.")
else:
    st.info("👈 Cargue sus datos para iniciar la consultoría estratégica.")