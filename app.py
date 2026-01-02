import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Analítica PyME 3.0", layout="wide", page_icon="📊")

# --- ESTILOS CSS (Para que se vea más pro) ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; border-radius: 10px; padding: 15px; text-align: center;}
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE PROYECCIÓN (IA) ---
def proyeccion_ventas(df_input, fecha_col, venta_col, dias_a_proyectar=30):
    if len(df_input) < 2:
        return df_input, 0 # No hay suficientes datos para predecir
        
    df_reg = df_input.copy()
    df_reg['fecha_num'] = df_reg[fecha_col].map(pd.Timestamp.toordinal)
    X = df_reg[['fecha_num']].values
    y = df_reg[venta_col].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    ultima_fecha = df_input[fecha_col].max()
    fechas_futuras = [ultima_fecha + pd.Timedelta(days=x) for x in range(1, dias_a_proyectar+1)]
    fechas_futuras_num = np.array([t.toordinal() for t in fechas_futuras]).reshape(-1, 1)
    
    predicciones = model.predict(fechas_futuras_num)
    
    df_proy = pd.DataFrame({
        fecha_col: fechas_futuras,
        venta_col: predicciones,
        'Tipo': 'Proyección'
    })
    
    df_input['Tipo'] = 'Histórico'
    return pd.concat([df_input, df_proy], ignore_index=True), model.coef_[0]

# --- CABECERA ---
st.title("📊 Monitor de Inteligencia Comercial")
st.markdown("Suba sus datos para detectar ineficiencias y proyectar flujo de caja.")
st.markdown("---")

# --- SIDEBAR: CARGA Y FILTROS ---
with st.sidebar:
    st.header("1. Carga de Datos")
    uploaded_file = st.file_uploader("Archivo Excel/CSV", type=["xlsx", "csv"])
    
    st.markdown("---")
    st.header("2. Filtros Dinámicos")
    # Los filtros aparecerán vacíos hasta que se cargue el archivo

# --- LÓGICA PRINCIPAL ---
if uploaded_file is not None:
    # 1. Carga
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)
    
    # 2. Detección Inteligente de Columnas
    col_fecha = next((c for c in df_raw.columns if 'fecha' in c.lower()), None)
    col_total = next((c for c in df_raw.columns if any(x in c.lower() for x in ['total', 'monto', 'venta'])), None)
    col_cliente = next((c for c in df_raw.columns if any(x in c.lower() for x in ['cliente', 'empresa', 'razon'])), None)

    if col_fecha and col_total:
        df_raw[col_fecha] = pd.to_datetime(df_raw[col_fecha])
        df_raw = df_raw.sort_values(by=col_fecha)

        # --- APLICACIÓN DE FILTROS ---
        df_filtrado = df_raw.copy()
        
        # Filtro de Cliente (Si existe la columna)
        if col_cliente:
            lista_clientes = df_raw[col_cliente].unique().tolist()
            seleccion_cliente = st.sidebar.multiselect("Filtrar por Cliente", lista_clientes)
            
            if seleccion_cliente:
                df_filtrado = df_filtrado[df_filtrado[col_cliente].isin(seleccion_cliente)]
        
        # Filtro de Fechas
        min_date = df_raw[col_fecha].min().date()
        max_date = df_raw[col_fecha].max().date()
        date_range = st.sidebar.date_input("Rango de Fechas", [min_date, max_date])

        # Aplicar filtro de fecha si el usuario seleccionó dos fechas
        if len(date_range) == 2:
            mask = (df_filtrado[col_fecha].dt.date >= date_range[0]) & (df_filtrado[col_fecha].dt.date <= date_range[1])
            df_filtrado = df_filtrado.loc[mask]

        # --- DASHBOARD (Usando df_filtrado) ---
        
        # Métricas (Se recalculan solas)
        total_venta = df_filtrado[col_total].sum()
        promedio_venta = df_filtrado[col_total].mean()
        conteo = len(df_filtrado)

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Ventas (Selección)", f"${total_venta:,.0f}".replace(",", "."))
        c2.metric("📦 Operaciones", conteo)
        c3.metric("📊 Ticket Promedio", f"${promedio_venta:,.0f}".replace(",", "."))
        
        st.divider()

        tab1, tab2 = st.tabs(["📈 Análisis Histórico", "🔮 Proyección IA"])

        with tab1:
            # Gráfico de Línea
            fig_line = px.line(df_filtrado, x=col_fecha, y=col_total, markers=True, title="Evolución de Ventas")
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Gráfico de Barras (Solo si hay cliente)
            if col_cliente:
                st.subheader("Desglose por Cliente")
                ventas_cliente = df_filtrado.groupby(col_cliente)[col_total].sum().sort_values(ascending=False).head(10)
                fig_bar = px.bar(ventas_cliente, orientation='h', color=ventas_cliente.values, color_continuous_scale='Bluyl')
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.subheader("Proyección de Tendencia (Lineal)")
            # Nota: Usamos df_filtrado. ¡La IA predice SOBRE LO QUE FILTRASTE!
            if len(df_filtrado) > 2:
                df_proy, pendiente = proyeccion_ventas(df_filtrado, col_fecha, col_total)
                
                msg_tendencia = "ALZA 🚀" if pendiente > 0 else "BAJA 📉"
                st.success(f"Considerando los datos filtrados, la tendencia es a la **{msg_tendencia}**.")
                
                fig_proy = px.line(df_proy, x=col_fecha, y=col_total, color='Tipo', 
                                   color_discrete_map={"Histórico": "gray", "Proyección": "red"})
                st.plotly_chart(fig_proy, use_container_width=True)
            else:
                st.warning("Necesitas seleccionar más datos para generar una predicción confiable.")

    else:
        st.error("No se encontraron columnas de Fecha o Monto.")
else:
    st.info("👈 Cargue un archivo para comenzar.")
    # Generador de datos (oculto para limpiar visual)