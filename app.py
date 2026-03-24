import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Buscador de Carreteras P.K.", layout="centered")

st.markdown("<h2 style='text-align: center; color: #1E88E5;'>🔍 BUSCADOR DE CARRETERAS (P.K.)</h2>", unsafe__html=True)
st.warning("⚠️ APLICACIÓN EN FASE DE PRUEBAS")

# Cargar la base de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("db_carreteras_pk.csv", sep=None, engine='python')
    # Limpiar espacios en los nombres de las columnas por si acaso
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()

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
                        with col1:
                            st.metric("P.K. INICIAL", f"{fila['PK_INICIAL']}")
                            # Si existe la columna ORIGEN, la mostramos
                            if 'ORIGEN' in fila:
                                st.write(f"**Origen:** {fila['ORIGEN']}")
                        
                        with col2:
                            st.metric("P.K. FINAL", f"{fila['PK_FINAL']}")
                            # Si existe la columna DESTINO, la mostramos
                            if 'DESTINO' in fila:
                                st.write(f"**Destino:** {fila['DESTINO']}")
                        
                        st.divider()
            else:
                st.error(f"No se ha encontrado la carretera '{carretera_input}' en {provincia}. Revisa si lleva guion (ej: CV-10).")
        else:
            st.info("Por favor, introduce el nombre de una carretera.")

except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")

st.info("Nota: Los datos mostrados corresponden al inventario oficial disponible.")
