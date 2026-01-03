import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard Pyme Chile 3.1", layout="wide")

# --- 1. MÓDULO DE CONTEXTO ECONÓMICO (API CHILE) ---
@st.cache_data(ttl=3600) # Guardamos en caché 1 hora para no saturar la API
def obtener_indicadores():
    try:
        url = "https://mindicador.cl/api"
        response = requests.get(url)
        data = response.json()
        return {
            "uf": data['uf']['valor'],
            "dolar": data['dolar']['valor'],
            "utm": data['utm']['valor']
        }
    except:
        return {"uf": 0, "dolar": 0, "utm": 0} # Valores por defecto si falla

indicadores = obtener_indicadores()

# --- 2. MÓDULO DE PERFILAMIENTO (SIDEBAR) ---
st.sidebar.title("🧠 Configuración Estratégica")
st.sidebar.info("Ayuda a la IA a entender tu negocio")

rubro = st.sidebar.selectbox("Rubro de la Empresa", 
    ["Comercio Minorista (Retail)", "Alimentación / Restaurante", "Servicios Profesionales", "Construcción", "Transporte", "Tecnología"])

modelo_negocio = st.sidebar.radio("Modelo de Venta", ["B2C (Vendo a personas)", "B2B (Vendo a empresas)"])

objetivo = st.sidebar.selectbox("Objetivo actual", 
    ["Aumentar Ventas", "Recuperar Clientes", "Optimizar Costos", "Expansión"])

# --- HEADER CON INDICADORES EN VIVO ---
st.title("🇨🇱 Dashboard Pyme Inteligente")
st.markdown(f"**Estrategia para:** {rubro} | **Modelo:** {modelo_negocio}")

col1, col2, col3 = st.columns(3)
col1.metric("Valor UF Hoy", f"${indicadores['uf']:,.2f}")
col2.metric("Dólar Observado", f"${indicadores['dolar']:,.2f}")
col3.metric("UTM (Mes)", f"${indicadores['utm']:,.0f}")

st.markdown("---")

# --- 3. MÓDULO DE DATOS (SIMULACIÓN DE CLIENTES) ---
# En la versión real, esto vendría de un Excel o Base de Datos
data_clientes = {
    'Cliente': ['Empresa A', 'Juan Pérez', 'Comercial B', 'Ana Silva', 'Tech SpA', 'Pedro L.'],
    'Ultima_Compra_Dias': [5, 120, 15, 200, 3, 45], # Días desde la última compra
    'Promedio_Compra': [500000, 120000, 850000, 45000, 2300000, 60000],
    'Frecuencia_Historica': ['Alta', 'Baja', 'Alta', 'Media', 'Muy Alta', 'Baja']
}
df = pd.DataFrame(data_clientes)

# --- 4. ALGORITMO DE DETECCIÓN DE FUGA (Diagnóstico) ---
st.header("🕵️ Diagnóstico de Cartera de Clientes")

# Definimos "Fuga" como clientes que no compran hace más de 90 días
criterio_fuga = 90 
df['Estado'] = df['Ultima_Compra_Dias'].apply(lambda x: '🔴 EN RIESGO' if x > criterio_fuga else '🟢 ACTIVO')

# Métricas de Fuga
clientes_riesgo = df[df['Estado'] == '🔴 EN RIESGO']
dinero_potencial_perdido = clientes_riesgo['Promedio_Compra'].sum()

m1, m2 = st.columns(2)
m1.error(f"Clientes en Riesgo de Fuga: {len(clientes_riesgo)}")
m2.warning(f"Ingreso Potencial en Pausa: ${dinero_potencial_perdido:,.0f}")

st.dataframe(df.style.applymap(lambda v: 'color: red;' if v == '🔴 EN RIESGO' else 'color: green;', subset=['Estado']), use_container_width=True)

# --- 5. SIMULACIÓN DE CEREBRO IA (RECOMENDACIÓN ESTRATÉGICA) ---
st.header("🤖 Asesor Virtual (IA Contextual)")

if st.button("Generar Diagnóstico Estratégico"):
    st.write("Analizando contexto económico y datos de clientes...")
    
    # Aquí construimos el PROMPT (La lógica que la IA usaría)
    recomendacion = ""
    
    if len(clientes_riesgo) > 0:
        recomendacion += f"⚠️ **Alerta Prioritaria:** Tienes {len(clientes_riesgo)} clientes importantes inactivos. "
        if rubro == "Servicios Profesionales" or rubro == "Tecnología":
            recomendacion += "En tu rubro B2B, la relación es clave. **Acción sugerida:** Envía un correo personalizado agendando una reunión de actualización, no de venta directa. "
        elif rubro == "Alimentación / Restaurante" or rubro == "Comercio Minorista (Retail)":
            recomendacion += "En B2C, la emoción vende. **Acción sugerida:** Crea una campaña de 'Te echamos de menos' con un cupón de descuento agresivo (20%) válido por 48 horas. "
    
    if indicadores['dolar'] > 900:
        recomendacion += "\n\n💵 **Factor Mercado:** El dólar está alto. Si importas insumos, revisa tus márgenes ahora. Si exportas servicios, es momento de invertir en publicidad."

    st.success(recomendacion)
    
    # Espacio para mostrar el "Prompt oculto" que se enviaría a una API real (GPT-4)
    with st.expander("Ver lógica interna (Prompt para LLM)"):
        st.code(f"""
        ACTÚA COMO: Consultor de Negocios Senior en Chile.
        CONTEXTO EMPRESA: Rubro {rubro}, Modelo {modelo_negocio}.
        DATOS MERCADO: UF ${indicadores['uf']}, Dólar ${indicadores['dolar']}.
        PROBLEMA DETECTADO: {len(clientes_riesgo)} clientes en fuga con valor de ${dinero_potencial_perdido}.
        TAREA: Generar estrategia de reactivación y protección de flujo de caja.
        """)