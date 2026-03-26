import streamlit as st
import pandas as pd
import os
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Carreteras CV", page_icon="🚔", layout="centered")

# --- LÓGICA DE MENSAJE DE BIENVENIDA ---
if 'visto_anuncio' not in st.session_state:
    st.session_state.visto_anuncio = False

if not st.session_state.visto_anuncio:
    aviso = st.container()
    with aviso:
        st.markdown("""
            <div style="
                background-color: #1a2a4a; 
                padding: 30px; 
                border-radius: 20px; 
                border: 2px solid #b38f00; 
                text-align: center;
                margin-bottom: 25px;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
            ">
                <h1 style="color: #ffffff; font-size: 28px; margin-bottom: 10px; font-family: sans-serif;">📢 ACTUALIZACIÓN DEL SISTEMA</h1>
                <p style="color: #ffd700; font-size: 20px; font-weight: bold; margin-bottom: 20px; font-family: sans-serif;">
                    REV: AÑADIR TRAZADO CON MAPA DE LA VÍA INDICANDO PUNTOS KILOMÉTRICOS Y CORRECCIÓN DE ERRORES MENORES
                </p>
                <p style="color: #cccccc; font-size: 14px; font-family: sans-serif;">Optimización de carga y mejora visual de mapas v2.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ ENTENDIDO / NO MOSTRAR MÁS", use_container_width=True):
            st.session_state.visto_anuncio = True
            st.rerun()
    st.stop()

# --- ESTILOS CSS ---
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
    .map-container {
        border: 2px solid #555; 
        border-radius: 20px; 
        overflow: hidden;
        margin-top: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        position: relative;
    }
    .seccion-final {
        margin-top: 40px;
        padding: 15px;
        border-top: 1px solid #444;
    }
    /* Estilo para que el expander de privacidad no destaque demasiado */
    .stExpander {
        border: none !important;
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛣️ CARRETERAS")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('db_carreteras_pk.csv')
        df['id_vial'] = df['id_vial'].astype(str).str.strip().str.upper()
        return df
    except: return pd.DataFrame()

df_raw = load_data()
geolocator = Nominatim(user_agent="sector_cv_v65", timeout=5)

st.warning("⚠️ APLICACIÓN EN FASE DE PRUEBAS")
prov_sel = st.selectbox("📍 SELECCIONE PROVINCIA:", ["VALENCIA", "ALICANTE", "CASTELLÓN"])

limites = {"VALENCIA": (38.80, 40.00), "ALICANTE": (37.80, 38.79), "CASTELLÓN": (39.40, 40.80)}
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
            li = geolocator.reverse(f"{puntos.iloc[0]['lat']}, {puntos.iloc[0]['lon']}")
            lf = geolocator.reverse(f"{puntos.iloc[-1]['lat']}, {puntos.iloc[-1]['lon']}")
            def obtener_ref(loc):
                if not loc: return "N/A"
                d = loc.raw.get('address', {})
                return d.get('town') or d.get('village') or d.get('city') or "TM"
            st.success(f"📌 **TRAMO:** De {obtener_ref(li)} a {obtener_ref(lf)} ({longitud_total} KM)")
        except:
            st.info(f"🚩 **VÍA {via_input}:** Desde PK {pk_min} hasta PK {pk_max} ({longitud_total} KM)")
        
        intervalo = 1 if longitud_total <= 10 else (2 if longitud_total <= 40 else 5)
        puntos_km = puntos[puntos['pk'] % intervalo == 0].to_dict('records')
        
        pk_val = st.number_input("📍 PK A BUSCAR:", min_value=float(pk_min), max_value=float(pk_max), step=0.1, value=float(pk_min))
        p_c = puntos.iloc[(puntos['pk'] - pk_val).abs().argsort()[:1]].iloc[0]
        
        st.link_button("👉 IR AL PK SELECCIONADO (GPS)", f"https://www.google.com/maps?q={p_c['lat']},{p_c['lon']}", use_container_width=True)
        
        mapa_html = f"""
        <div class="map-container">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <div style="position: absolute; top: 12px; right: 12px; z-index: 1000; background: #ffffff; padding: 6px 14px; border-radius: 8px; font-family: sans-serif; font-weight: bold; font-size: 13px; color: #000000; border: 2px solid #555555; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                📍 Trazado de la vía
            </div>
            <div id="map" style="width: 100%; height: 450px;"></div>
            <script>
                var map = L.map('map');
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                var pts = {puntos_km};
                var group = L.featureGroup();
                pts.forEach(function(p) {{
                    var iconText = L.divIcon({{
                        className: 'custom-km-label',
                        html: "<div style='color:#000; font-weight:900; font-size:13px; text-shadow: 2px 2px 0px #fff, -2px -2px 0px #fff;'>" + p.pk + "</div>",
                        iconSize: [30, 20],
                        iconAnchor: [15, 10]
                    }});
                    L.marker([p.lat, p.lon], {{icon: iconText}}).addTo(group);
                }});
                L.marker([{p_c['lat']}, {p_c['lon']}]).addTo(group).bindPopup("<b>PK: {pk_val}</b>").openPopup();
                group.addTo(map);
                map.fitBounds(group.getBounds(), {{padding: [40, 40]}});
            </script>
        </div>
        """
        components.html(mapa_html, height=480)
    else:
        st.error(f"No hay datos para '{via_input}'.")

# --- PIE DE PÁGINA CON DESPLEGABLE ---
st.markdown('<div class="seccion-final">', unsafe_allow_html=True)
col_escudo, col_info = st.columns([1, 5])

with col_escudo:
    if os.path.exists("assets/escudo.png"): st.image("assets/escudo.png", width=60)
    else: st.write("🚔")

with col_info:
    # Aquí creamos el "botón" desplegable
    with st.expander("🔒 PRIVACIDAD Y SEGURIDAD"):
        st.write("""
            Esta aplicación no utiliza cookies de rastreo ni almacena el historial de búsqueda. 
            No se registra la dirección IP del usuario ni se recopilan datos de ubicación en tiempo real. 
            El procesamiento de los datos de la vía se realiza de forma local y efímera en la sesión actual.
        """)
    st.markdown("**✍️ Gómez Dest B**")
st.markdown('</div>', unsafe_allow_html=True)
