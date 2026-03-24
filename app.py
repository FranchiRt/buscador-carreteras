import streamlit as st
import pandas as pd

# Configuración básica
st.set_page_config(page_title="Buscador Carreteras", layout="centered")

st.title("🔍 BUSCADOR DE CARRETERAS (P.K.)")
st.warning("⚠️ APLICACIÓN EN FASE DE PRUEBAS")

# Cargar datos
@st.cache_data
def cargar_datos():
    try:
        # Carga el CSV detectando el separador automáticamente
        df = pd.read_csv("db_carreteras_pk.csv", sep=None, engine='python')
        # Limpia espacios y pasa cabeceras a mayúsculas
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None

df = cargar_datos()

if df is not None:
    # Selectores de usuario
    provincia = st.selectbox("1. Selecciona la Provincia:", ["ALICANTE", "CASTELLON", "VALENCIA"])
    carretera_input = st.text_input("2. Introduce la Carretera (ej: A-7, CV-10):").strip().upper()

    if st.button("Buscar Puntos Kilométricos"):
        if carretera_input:
            # Filtrar
            resultado = df[(df['PROVINCIA'] == provincia) & (df['CARRETERA'] == carretera_input)]

            if not resultado.empty:
                st.success(f"Resultados para {carretera_input}")
                
                for _, fila in resultado.iterrows():
                    st.subheader(f"📍 Tramo detectado")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("P.K. INICIAL", str(fila['PK_INICIAL']))
                        # Solo muestra el origen si la columna existe y tiene datos
                        if 'ORIGEN' in fila and pd.notna(fila['ORIGEN']):
                            st.info(f"**Origen:** {fila['ORIGEN']}")
                    
                    with col2:
                        st.metric("P.K. FINAL", str(fila['PK_FINAL']))
                        # Solo muestra el destino si la columna existe y tiene datos
                        if 'DESTINO' in fila and pd.notna(fila['DESTINO']):
                            st.info(f"**Destino:** {fila['DESTINO']}")
                    st.divider()
            else:
                st.error(f"No se encuentra '{carretera_input}' en {provincia}.")
        else:
            st.info("Escribe una carretera para empezar.")

st.caption("Datos del inventario oficial de carreteras.")
