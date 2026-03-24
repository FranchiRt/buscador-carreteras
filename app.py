import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Buscador de Carreteras P.K.", layout="centered")

st.markdown("<h2 style='text-align: center; color: #1E88E5;'>🔍 BUSCADOR DE CARRETERAS (P.K.)</h2>", unsafe_allow_html=True)
st.warning("⚠️ APLICACIÓN EN FASE DE PRUEBAS")

# Cargar la base de datos
@st.cache_data
def cargar_datos():
    try:
        # Cargamos el CSV y limpiamos nombres de columnas
        df = pd.read_csv("db_carreteras_pk.csv", sep=None, engine='python')
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

df = cargar_datos()

if df is not None:
    # Selectores
    provincia = st.selectbox("1. Selecciona la Provincia:", ["ALICANTE", "CASTELLON", "VALENCIA"])
    carretera_input = st.text_input("2. Introduce la Carretera (ej: A-7, CV-10):").strip().upper()

    if st.button("Buscar Puntos Kilométricos"):
        if carretera_input:
            # Filtrar por provincia y carretera
            resultado = df[(df['PROVINCIA'] == provincia) & (df['CARRETERA'] == carretera_input)]

            if not resultado.empty:
                st.success(f"Resultados para {carretera_input} en {provincia}:")
                
                for _, fila in resultado.iterrows():
                    with st.container():
                        st.markdown(f"### 📍 Tramo")
                        col1, col2 = st.columns(2)
                        
                        # Mostramos PK Inicial y su Origen si existe
                        with col1:
                            st.metric("P.K. INICIAL", f"{fila['PK_INICIAL']}")
                            if 'ORIGEN' in fila and pd.notna(fila['ORIGEN']):
                                st.write(f"**📍 Origen:** {fila['ORIGEN']}")
                        
                        # Mostramos PK Final y su Destino si existe
                        with col2:
                            st.metric("P.K. FINAL", f"{fila['PK_FINAL']}")
                            if 'DESTINO' in fila and pd.notna(fila['DESTINO']):
                                st.write(f"**🏁 Destino:** {fila['DESTINO']}")
                        
                        st.divider()
            else:
                st.error(f"No se ha encontrado '{carretera_input}' en {provincia}. Revisa el nombre.")
        else:
            st.info("Escribe el nombre de la carretera para buscar.")

st.info("Nota: Datos del inventario oficial.")
