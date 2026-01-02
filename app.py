import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import numpy as np
from datetime import datetime
from fpdf import FPDF
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="InsightCorp Report", layout="wide", page_icon="📄")

# --- CLASE PARA EL REPORTE PDF ---
class PDF(FPDF):
    def header(self):
        # Logo o Título Corporativo
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'InsightCorp | Informe de Inteligencia de Negocios', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def crear_reporte_pdf(df_filtrado, total_venta, tendencia, analisis_texto, recomendaciones_lista):
    pdf = PDF()
    pdf.add_page()
    
    # 1. TÍTULO Y FECHA
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Reporte Ejecutivo de Gestión', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Fecha de Emisión: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
    pdf.ln(10)
    
    # 2. RESUMEN EJECUTIVO (Texto generado por IA)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. Diagnóstico General', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, analisis_texto)
    pdf.ln(5)
    
    # 3. TABLA DE KPIs
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. Métricas Clave (KPIs)', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    # Datos simples para la tabla
    col_width = 60
    th = 10
    
    pdf.cell(col_width, th, 'Total Ventas', 1)
    pdf.cell(col_width, th, f"${total_venta:,.0f}", 1)
    pdf.ln(th)
    
    pdf.cell(col_width, th, 'Tendencia Proyectada', 1)
    pdf.cell(col_width, th, tendencia, 1)
    pdf.ln(th)
    
    pdf.cell(col_width, th, 'Total Operaciones', 1)
    pdf.cell(col_width, th, str(len(df_filtrado)), 1)
    pdf.ln(15)

    # 4. RECOMENDACIONES (Lista)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. Plan de Acción Recomendado', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    for rec in recomendaciones_lista:
        pdf.cell(10, 7, "-", 0, 0)
        pdf.multi_cell(0, 7, rec)
        
    # Salvar en memoria
    return pdf.output(dest='S').encode('latin-1')

# --- MOTORES DE INTELIGENCIA ---
def motor_analisis(df, col_fecha, col_venta):
    # Proyección
    df_reg = df.copy()
    df_reg['fecha_num'] = df_reg[col_fecha].map(pd.Timestamp.toordinal)
    model = LinearRegression()
    model.fit(df_reg[['fecha_num']], df_reg[col_venta])
    pendiente = model.coef_[0]
    
    # KPIs
    total = df[col_venta].sum()
    
    return total, pendiente

# --- INTERFAZ ---
st.title("📄 Generador de Reportes Corporativos")
st.markdown("Transforma tus datos en un informe PDF profesional listo para imprimir.")

uploaded_file = st.sidebar.file_uploader("Cargar Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    # Carga de datos (igual que antes)
    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
    else: df = pd.read_excel(uploaded_file)
    
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_total = next((c for c in df.columns if any(x in c.lower() for x in ['total', 'monto', 'venta'])), None)

    if col_fecha and col_total:
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df = df.sort_values(by=col_fecha)

        # Análisis
        total_venta, pendiente = motor_analisis(df, col_fecha, col_total)
        tendencia_str = "ALCISTA (Crecimiento)" if pendiente > 0 else "BAJISTA (Contracción)"
        color_tendencia = "green" if pendiente > 0 else "red"

        # Generación de "Narrativa IA"
        texto_analisis = (
            f"Durante el periodo analizado, la empresa generó un total de ${total_venta:,.0f}. "
            f"El análisis econométrico de la serie de tiempo detecta una tendencia {tendencia_str}. "
            "Se observa una volatilidad que requiere atención en la gestión de flujo de caja para las próximas semanas."
        )
        
        recomendaciones = []
        if pendiente < 0:
            recomendaciones.append("Revisar estructura de costos fijos inmediatamente.")
            recomendaciones.append("Activar campaña de reactivación de clientes antiguos.")
        else:
            recomendaciones.append("Aumentar inventario para evitar quiebres de stock ante demanda creciente.")
            recomendaciones.append("Evaluar ajuste de precios para mejorar margen.")
        
        recomendaciones.append("Digitalizar el registro de gastos menores para mejorar la precisión del margen.")

        # --- VISTA PREVIA EN PANTALLA ---
        st.divider()
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Vista Previa del Análisis")
            st.markdown(f"**Diagnóstico:** {texto_analisis}")
            st.markdown(f"**Estado:** :{color_tendencia}[{tendencia_str}]")
            
            # Gráfico simple para acompañar
            fig = px.line(df, x=col_fecha, y=col_total, title="Evolución Financiera")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Panel de Descarga")
            st.info("Su reporte está listo para ser generado.")
            
            # BOTÓN MÁGICO
            pdf_bytes = crear_reporte_pdf(df, total_venta, tendencia_str, texto_analisis, recomendaciones)
            
            st.download_button(
                label="📥 DESCARGAR REPORTE PDF OFICIAL",
                data=pdf_bytes,
                file_name="Reporte_Gerencial_InsightCorp.pdf",
                mime="application/pdf",
            )
            
            st.warning("Nota: Este reporte es válido para presentaciones bancarias o reuniones de directorio.")

    else:
        st.error("Formato incorrecto.")
else:
    st.info("Sube el archivo para generar el reporte.")