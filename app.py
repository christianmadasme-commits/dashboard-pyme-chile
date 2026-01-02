import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import numpy as np
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente Virtual PyME", layout="wide", page_icon="🤖")

# Estilos para que parezca una App nativa y amigable
st.markdown("""
<style>
    .big-font {font-size:20px !important; color: #333;}
    .action-card {background-color: #e8f4f8; padding: 15px; border-radius: 10px; border-left: 5px solid #00a8cc; margin-bottom: 10px;}
    .alert-card {background-color: #ffebee; padding: 15px; border-radius: 10px; border-left: 5px solid #ff5252; margin-bottom: 10px;}
    .success-card {background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- MOTORES DE INTELIGENCIA (Backend) ---

def motor_proyeccion(df, fecha_col, venta_col, dias=30):
    if len(df) < 2: return df, 0
    df_reg = df.copy()
    df_reg['fecha_num'] = df_reg[fecha_col].map(pd.Timestamp.toordinal)
    model = LinearRegression()
    model.fit(df_reg[['fecha_num']], df_reg[venta_col])
    futuro = [df[fecha_col].max() + pd.Timedelta(days=x) for x in range(1, dias+1)]
    futuro_num = np.array([t.toordinal() for t in futuro]).reshape(-1, 1)
    prediccion = model.predict(futuro_num)
    df_proy = pd.DataFrame({fecha_col: futuro, venta_col: prediccion, 'Tipo': 'Proyección'})
    df['Tipo'] = 'Histórico'
    return pd.concat([df, df_proy], ignore_index=True), model.coef_[0]

def motor_segmentacion_accionable(df, col_cliente, col_venta, col_fecha):
    # Crear RFM (Recencia, Frecuencia, Monto)
    # Recencia: ¿Hace cuántos días fue su última compra?
    fecha_max = df[col_fecha].max()
    rfm = df.groupby(col_cliente).agg({
        col_fecha: lambda x: (fecha_max - x.max()).days,
        col_venta: ['sum', 'count']
    }).reset_index()
    
    rfm.columns = ['Cliente', 'Dias_sin_venir', 'Total_Venta', 'Frecuencia']
    rfm['Ticket_Promedio'] = rfm['Total_Venta'] / rfm['Frecuencia']
    
    if len(rfm) < 3: return rfm # Protección contra pocos datos
    
    # K-Means para agrupar por VALOR (Venta)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    rfm['Cluster_Valor'] = kmeans.fit_predict(rfm[['Total_Venta']])
    
    # Ordenar clusters para saber cuál es el VIP (el de mayor venta promedio)
    ranking = rfm.groupby('Cluster_Valor')['Total_Venta'].mean().sort_values(ascending=False).index
    mapa = {ranking[0]: 'VIP', ranking[1]: 'Regular', ranking[2]: 'Bajo'}
    rfm['Categoria'] = rfm['Cluster_Valor'].map(mapa)
    
    # Lógica de NEGOCIO (Aquí está el cerebro del consultor)
    # Definimos "Riesgo de Fuga" si no viene hace más de X días (ej: 60 días)
    # Ajustable según el negocio, aquí usamos la media + desv estándar
    limite_fuga = rfm['Dias_sin_venir'].mean() 
    
    rfm['Estado'] = 'Activo'
    rfm.loc[rfm['Dias_sin_venir'] > limite_fuga, 'Estado'] = 'En Riesgo ⚠️'
    rfm.loc[rfm['Dias_sin_venir'] > (limite_fuga * 2), 'Estado'] = 'Perdido ❌'
    
    return rfm

# --- INTERFAZ (Frontend) ---

st.title("🤖 Tu Asistente de Negocios")
st.markdown("Suba sus datos y le diré exactamente **qué hacer esta semana**.")

uploaded_file = st.sidebar.file_uploader("📂 Cargar Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
    else: df = pd.read_excel(uploaded_file)
    
    # Detección de columnas
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_total = next((c for c in df.columns if any(x in c.lower() for x in ['total', 'monto', 'venta'])), None)
    col_cliente = next((c for c in df.columns if any(x in c.lower() for x in ['cliente', 'empresa', 'razon'])), None)

    if col_fecha and col_total and col_cliente:
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        
        # Ejecutar Motores
        rfm_data = motor_segmentacion_accionable(df, col_cliente, col_total, col_fecha)
        df_proy, pendiente = motor_proyeccion(df, col_fecha, col_total)
        
        # --- TABLERO DE ACCIÓN ---
        tab1, tab2, tab3 = st.tabs(["📋 Lista de Tareas", "🚦 Semáforo de Clientes", "🔮 Futuro"])
        
        with tab1:
            st.header("¿Qué debo hacer hoy?")
            st.markdown("Basado en el análisis de sus datos, la Inteligencia Artificial recomienda:")
            
            # 1. Estrategia de Recuperación (Clientes VIP en Riesgo)
            vip_riesgo = rfm_data[(rfm_data['Categoria'] == 'VIP') & (rfm_data['Estado'] != 'Activo')]
            
            if not vip_riesgo.empty:
                st.markdown(f"""<div class="alert-card">
                    <b>🚨 URGENTE: Recuperar Clientes VIP</b><br>
                    Tienes {len(vip_riesgo)} clientes importantes que han dejado de comprar. 
                    Si no los llamas hoy, podrías perder <b>${vip_riesgo['Total_Venta'].sum()*0.2:,.0f}</b> al mes.
                    </div>""", unsafe_allow_html=True)
                
                with st.expander("Ver lista de teléfonos para llamar ahora"):
                    st.table(vip_riesgo[['Cliente', 'Dias_sin_venir', 'Total_Venta']].sort_values('Total_Venta', ascending=False))
            else:
                st.success("✅ ¡Excelente! Tus clientes VIP están todos activos.")

            # 2. Estrategia de Desarrollo (Clientes Regulares que pueden ser VIP)
            potenciales = rfm_data[(rfm_data['Categoria'] == 'Regular') & (rfm_data['Frecuencia'] > rfm_data['Frecuencia'].mean())]
            
            if not potenciales.empty:
                st.markdown(f"""<div class="action-card">
                    <b>💰 OPORTUNIDAD: Convertir a VIP</b><br>
                    Estos {len(potenciales)} clientes compran seguido pero montos medios. 
                    <b>Recomendación:</b> Ofrecerles un descuento por volumen para subir su ticket.
                    </div>""", unsafe_allow_html=True)
                st.dataframe(potenciales[['Cliente', 'Frecuencia', 'Ticket_Promedio']])

        with tab2:
            st.subheader("Estado de tu Cartera")
            c1, c2 = st.columns([3, 1])
            
            with c1:
                # Gráfico interactivo fácil de entender
                fig = px.scatter(rfm_data, x='Dias_sin_venir', y='Total_Venta', 
                                 color='Categoria', size='Ticket_Promedio',
                                 hover_name='Cliente', text='Cliente',
                                 color_discrete_map={'VIP': '#FFD700', 'Regular': '#87CEEB', 'Bajo': '#C0C0C0'},
                                 title="Mapa de Clientes (Arriba=Compran Mucho | Derecha=Hace mucho no vienen)")
                # Añadir líneas de referencia
                fig.add_vline(x=rfm_data['Dias_sin_venir'].mean(), line_dash="dash", annotation_text="Alerta de Fuga")
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.write("**Resumen:**")
                st.write(rfm_data['Categoria'].value_counts())
                st.write("**Estado:**")
                st.write(rfm_data['Estado'].value_counts())

        with tab3:
            st.subheader("Proyección Simple")
            tendencia = "SUBIENDO 🚀" if pendiente > 0 else "BAJANDO 📉"
            color_t = "green" if pendiente > 0 else "red"
            
            st.markdown(f"Tus ventas están: **:{color_t}[{tendencia}]**")
            st.markdown("La línea punteada muestra hacia dónde vas si no haces cambios.")
            
            fig_p = px.line(df_proy, x=col_fecha, y=col_total, color='Tipo',
                            color_discrete_map={"Histórico": "gray", "Proyección": color_t})
            st.plotly_chart(fig_p, use_container_width=True)

    else:
        st.error("Faltan datos. Necesito columnas que digan: Fecha, Cliente y Total.")
else:
    st.info("Sube tu Excel para que el Asistente analice tu negocio.")