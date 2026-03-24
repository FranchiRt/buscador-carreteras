import streamlit as st
import pandas as pd
import os
from geopy.geocoders import Nominatim

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Buscador Carreteras CV", page_icon="🚔", layout="centered")

st.markdown("""
    <style>
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"], div[data-testid="stSelectbox"] {
        width: 100% !important;
    }
    a[data-testid="stLinkButton"] {
        width: 100% !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 10px !important;
    }
    .privacidad {
        font-size: 0.8rem;
        color: #666;
        text-align: center;
        margin-top: 50px;
        padding: 10px;
        border-top: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# 2. FUNCIONES
def leer_estadisticas():
    archivo = "estadisticas.txt"
    default = {"VALENCIA": 0, "ALICANTE": 0, "CASTELLÓN": 0}
    if not os.path.exists(archivo): return default
    res = {}
    try:
        with open(archivo, "r") as f:
            for l in f.readlines():
                if ":" in l:
                    p, cant = l.strip().split(":")
                    res[p] = int(cant)
        for k in default:
            if k not in res: res[k] = 0
        return res
    except: return default

def registrar_consulta(provincia):
    archivo = "estadisticas.txt"
    stats = leer_estadisticas()
    stats[provincia] = stats.get(provincia, 0) + 1
    with open(archivo, "w") as f:
        for p, cant in stats.items():
            f.write(f"{p}:{cant}\n")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('db_carreteras_pk.csv')
        df['id_vial'] = df['id_vial'].astype(str).str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# 3. LÓGICA PRINCIPAL
df_raw = load_data()
geolocator = Nominatim(user_agent="sector_cv_v62")

st.warning("⚠️ APLICACIÓN EN FASE DE PRUEBAS")

prov_sel = st.selectbox("📍 SELECCIONE PROVINCIA:", ["VALENCIA", "ALICANTE", "CASTELLÓN"])

limites = {
    "VALENCIA": (38.80, 40.00), 
    "ALICANTE": (37.80, 38.79), 
    "CASTELLÓN": (39.40, 40.80)
}
l_min, l_max = limites[prov_sel]
df_prov = df_raw[(df_raw['lat'] >= l_min) & (df_raw['lat'] <= l_max)]

via_raw = st.text_input("🛣️ ESCRIBA CARRETERA (Ej: A-7, CV-310):", placeholder="Escriba aquí...")
via_input = via_raw.strip().upper() 

if via_input:
    puntos = df_prov[df_prov['id_vial'] == via_input].sort_values('pk')
    
    if not puntos.empty:
        pk_min, pk_max = puntos['pk'].min(), puntos['pk'].max()
        
        try:
            li = geolocator.reverse(f"{puntos.iloc[0]['lat']}, {puntos.iloc[0]['lon']}", timeout=3)
            lf = geolocator.reverse(f"{puntos.iloc[-1]['lat']}, {puntos.iloc[-1]['lon']}", timeout=3)
            def obtener_ref(loc):
                if not loc: return "N/A"
                d = loc.raw.get('address', {})
                return d.get('town') or d.get('village') or d.get('city') or d.get('municipality') or "TM"
            
            # Muestra el tramo con el nombre de los pueblos y el rango de KM
            st.success(f"📌 **TRAMO:** De {obtener_ref(li)} a {obtener_ref(lf)} (KM {pk_min}-{pk_max})")
            
        except:
            st.info(f"🚩 **RANGO:** {via_input} (KM {pk_min} a {pk_max})")

        # --- AQUÍ ESTÁ EL CAMBIO QUE PEDÍAS ---
        st.write(f"**Estos son los km que tiene la carretera para elegir: desde el {pk_min} al {pk_max}**")
        
        pk_val = st.number_input("📍 PK A BUSCAR:", min_value=float(pk_min), max_value=float(pk_max), step=0.1, value=float(pk_min))
        
        p_c = puntos.iloc[(puntos['pk'] - pk_val).abs().argsort()[:1]].iloc[0]
        st.link_button("👉 IR AL MAPA", f"https://www.google.com/maps?q={p_c['lat']},{p_c['lon']}", use_container_width=True)

        if 'ultima_v' not in st.session_state or st.session_state.ultima_v != via_input:
            registrar_consulta(prov_sel)
            st.session_state.ultima_v = via_input
    else:
        if via_input != "":
            st.error(f"No hay datos para '{via_input}' en {prov_sel}.")

# --- LEYENDA DE PRIVACIDAD ---
st.markdown("""
    <div class="privacidad">
        🔒 <b>Privacidad garantizada:</b> Esta aplicación no recopila datos personales, 
        geolocalización del dispositivo, ni información técnica del usuario. 
        Las estadísticas de consulta son totalmente anónimas y se utilizan solo para 
        mejorar la base de datos de carreteras.
    </div>
""", unsafe_allow_html=True)

# HISTÓRICO SIDEBAR
with st.sidebar:
    st.header("📊 HISTÓRICO")
    stats = leer_estadisticas()
    st.write(f"Valencia: {stats.get('VALENCIA', 0)}")
    st.write(f"Alicante: {stats.get('ALICANTE', 0)}")
    st.write(f"Castellón: {stats.get('CASTELLÓN', 0)}")
    if st.button("🔄 NUEVA CONSULTA", use_container_width=True):
        st.session_state.clear()
        st.rerun()
