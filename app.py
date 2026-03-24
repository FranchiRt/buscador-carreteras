import streamlit as st
import pandas as pd
import os
from geopy.geocoders import Nominatim

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Carreteras CV", page_icon="🚔", layout="centered")

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
    .seccion-final {
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #444;
    }
    .privacidad-firma {
        font-size: 1rem;
        color: #ffffff; /* BLANCO PURO para que se vea en pantallas oscuras */
        line-height: 1.5;
        text-shadow: 1px 1px 2px #000000; /* Sombra para que se lea en cualquier fondo */
    }
    .firma-destacada {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.title("🛣️ CARRETERAS")

# 2. FUNCIONES (Intactas)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('db_carreteras_pk.csv')
        df['id_vial'] = df['id_vial'].astype(str).str.strip().str.upper()
        return df
    except: return pd.DataFrame()

# 3. LÓGICA PRINCIPAL (Intacta)
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

via_raw = st.text_input("ESCRIBA CARRETERA (Ej: A-7, CV-310):", placeholder="Escriba aquí...")
via_input = via_raw.strip().upper() 

if via_input:
    puntos = df_prov[df_prov['id_vial'] == via_input].sort_values('pk')
    
    if not puntos.empty:
        pk_min, pk_max = puntos['pk'].min(), puntos['pk'].max()
        longitud_total = round(pk_max - pk_min, 1)
        
        try:
            li = geolocator.reverse(f"{puntos.iloc[0]['lat']}, {puntos.iloc[0]['lon']}", timeout=3)
            lf = geolocator.reverse(f"{puntos.iloc[-1]['lat']}, {puntos.iloc[-1]['lon']}", timeout=3)
            def obtener_ref(loc):
                if not loc: return "N/A"
                d = loc.raw.get('address', {})
                return d.get('town') or d.get('village') or d.get('city') or d.get('municipality') or "TM"
            
            st.success(f"📌 **TRAMO:** De {obtener_ref(li)} a {obtener_ref(lf)} (Longitud: {longitud_total} KM)")
            
        except:
            st.info(f"🚩 **RANGO:** {via_input} ({longitud_total} KM totales)")
        
        pk_val = st.number_input("📍 PK A BUSCAR:", min_value=float(pk_min), max_value=float(pk_max), step=0.1, value=float(pk_min))
        
        p_c = puntos.iloc[(puntos['pk'] - pk_val).abs().argsort()[:1]].iloc[0]
        st.link_button("👉 IR AL MAPA", f"https://www.google.com/maps?q={p_c['lat']},{p_c['lon']}", use_container_width=True)
    else:
        if via_input != "":
            st.error(f"No hay datos para '{via_input}' en {prov_sel}.")

# --- SECCIÓN FINAL: BLANCO SOBRE NEGRO ---
st.markdown('<div class="seccion-final">', unsafe_allow_html=True)
col_escudo, col_texto = st.columns([1, 5])

with col_escudo:
    if os.path.exists("assets/escudo.png"):
        st.image("assets/escudo.png", width=65)
    else:
        st.write("🚔")

with col_texto:
    st.markdown("""
        <div class="privacidad-firma">
            🔒 <b>Privacidad garantizada:</b> Esta aplicación no recopila datos personales ni información técnica del usuario. 
            <br><span class="firma-destacada">✍️ Gómez Dest B</span>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
