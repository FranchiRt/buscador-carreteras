import streamlit as st
import pandas as pd
import os
import time
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Carreteras", page_icon="🚔", layout="centered")

st.markdown("""<style>
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 2rem !important; }
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"], div[data-testid="stSelectbox"] { width: 100% !important; }
    .stProgress > div > div > div > div { background-color: #ffd700 !important; }
    
    .simple-header { text-align: left; margin-bottom: 15px; }
    .header-title { color: #ffffff; font-size: 52px; font-weight: 900; border-bottom: 6px solid #ffd700; display: inline-block; line-height: 1.1; }

    .section-label { color: #ffd700; font-size: 16px; font-weight: 600; margin-top: 15px; margin-bottom: 5px; text-transform: uppercase; }
    .antena-gigante { font-size: 60px; text-align: center; margin: 10px 0; }
</style>""", unsafe_allow_html=True)

# CABECERA
st.markdown('<div class="simple-header"><div class="header-title">🛣️ CARRETERAS</div></div>', unsafe_allow_html=True)

# --- GESTIÓN DEL MENSAJE DE BIENVENIDA (SOLO AL INICIO) ---
if 'bienvenida_activa' not in st.session_state:
    st.session_state.bienvenida_activa = True

if st.session_state.bienvenida_activa:
    with st.container():
        st.markdown("""
            <div style="background-color: #1a1a1a; padding: 20px; border-radius: 15px; border: 2px solid #ffd700; margin-bottom: 15px;">
                <h3 style="color: #ffd700; margin-top: 0px; font-size: 22px;">🚀 BIENVENIDO A LA VERSIÓN 3.0</h3>
                <p style="color: #ffffff; font-size: 15px;">Se han implementado las siguientes mejoras de revisión (Marzo 2026):</p>
                <ul style="color: #cccccc; font-size: 14px; line-height: 1.5;">
                    <li><b>Ficha de Carretera:</b> Nuevo diseño de alto contraste con titularidad.</li>
                    <li><b>Geolocalización:</b> Identificación automática de municipios.</li>
                    <li><b>Tráfico Real:</b> Capa de intensidad circulatoria activa por defecto.</li>
                    <li><b>Precisión Maps:</b> Enlace directo al punto kilométrico exacto.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("✅ LEÍDO, ACCEDER A LA APLICACIÓN", use_container_width=True):
            st.session_state.bienvenida_activa = False
            st.rerun()

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('db_carreteras_pk.csv')
        df['id_vial'] = df['id_vial'].astype(str).str.strip().str.upper()
        return df
    except: return pd.DataFrame()

df_raw = load_data()
geolocator = Nominatim(user_agent="sector_cv_ultra_final_v3", timeout=5)

NOMBRES_OFICIALES = {
    "V-21": "V-21 (Puzol - Valencia)", "V-31": "V-31 (Silla - Valencia)",
    "AP-7": "AP-7 (Autopista del Mediterráneo)", "A-7": "A-7 (Autovía del Mediterráneo)",
    "N-332": "N-332 (Valencia-Alicante)", "A-3": "A-3 (Autovía del Este)",
    "CV-35": "CV-35 (Autovía de Ademuz)", "CV-50": "CV-50 (Llíria - Tavernes)",
    "V-23": "V-23 (Acceso Puerto Sagunto)", "V-30": "V-30 (Circunvalación VLC)"
}

# --- ENTRADA DE DATOS (SUBE CUANDO SE CIERRA LA BIENVENIDA) ---
if not st.session_state.bienvenida_activa:
    st.markdown('<div class="section-label">📍 DATOS DE LA CONSULTA</div>', unsafe_allow_html=True)
    prov_sel = st.selectbox("PROVINCIA:", ["VALENCIA", "ALICANTE", "CASTELLÓN"])
    via_raw = st.text_input("CARRETERA:")
    via_input = via_raw.strip().upper()

    if via_input:
        puntos = df_raw[df_raw['id_vial'] == via_input].sort_values('pk')
        
        if prov_sel == "VALENCIA" and not puntos.empty:
            if via_input == "AP-7":
                puntos = puntos[((puntos['pk'] >= 302) & (puntos['pk'] <= 466)) | 
                                ((puntos['pk'] >= 526) & (puntos['pk'] <= 601))]
            elif via_input == "N-332":
                puntos = puntos[puntos['pk'] >= 204.5]
            elif via_input == "A-7":
                puntos = puntos[(puntos['pk'] >= 292.95) & (puntos['pk'] <= 429)]
            else:
                puntos = puntos[(puntos['lat'] >= 38.751) & (puntos['lat'] <= 40.051)]

        if not puntos.empty:
            pk_min, pk_max = puntos['pk'].min(), puntos['pk'].max()
            long_t = round(pk_max - pk_min, 1)
            titular = "ESTADO (MITMS)" if via_input.startswith(('A-', 'AP-', 'N-', 'V-')) else "GENERALITAT (GVA)"

            placeholder_carga = st.empty()
            with placeholder_carga.container():
                st.markdown('<div class="antena-gigante">📡</div>', unsafe_allow_html=True)
                barra = st.progress(0)
                orig_g, dest_g = "", ""
                try:
                    for i in range(100):
                        time.sleep(0.002)
                        barra.progress(i + 1)
                        if i == 40 and via_input not in NOMBRES_OFICIALES:
                            li = geolocator.reverse(f"{puntos.iloc[0]['lat']}, {puntos.iloc[0]['lon']}")
                            lf = geolocator.reverse(f"{puntos.iloc[-1]['lat']}, {puntos.iloc[-1]['lon']}")
                            def obtener_ref(loc):
                                if not loc: return "N/A"
                                d = loc.raw.get('address', {})
                                return d.get('town') or d.get('village') or d.get('city') or "TM"
                            orig_g, dest_g = obtener_ref(li), obtener_ref(lf)
                except: pass
            placeholder_carga.empty()

            # FICHA VISUAL RESALTADA
            nombre_final = NOMBRES_OFICIALES.get(via_input, f"CARRETERA {via_input} ({orig_g} - {dest_g})")
            st.markdown(f"""
                <div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 2px solid #ffd700; margin-bottom: 20px;">
                    <h3 style="color: #ffd700; margin-top: 0px; margin-bottom: 10px; font-size: 26px;">{nombre_final}</h3>
                    <p style="color: #ffffff; font-size: 18px; margin: 5px 0;"><b>Titular:</b> {titular}</p>
                    <p style="color: #ffffff; font-size: 18px; margin: 5px 0;"><b>Recorrido:</b> PK {pk_min} a PK {pk_max} ({long_t} KM)</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-label">🎯 Selección de Punto Exacto</div>', unsafe_allow_html=True)
            pk_val = st.number_input("PK seleccionado:", min_value=float(pk_min), max_value=float(pk_max), step=0.1)
            p_c = puntos.iloc[(puntos['pk'] - pk_val).abs().argsort()[:1]].iloc[0]
            
            url_maps = f"https://www.google.com/maps?q={p_c['lat']},{p_c['lon']}"
            st.link_button("🌐 VER UBICACIÓN EN GOOGLE MAPS", url_maps, use_container_width=True)

            grandes = ["A-3", "A-7", "AP-7", "V-23", "CV-35", "N-332", "CV-50", "V-21", "V-31", "V-30"]
            intervalo = 5 if (prov_sel == "VALENCIA" and via_input in grandes) else 1
            puntos_km = puntos[puntos['pk'] % intervalo == 0].to_dict('records')

            mapa_html = f"""
            <div style="border-radius: 10px; overflow: hidden; margin-top: 10px; border: 1px solid #444;">
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <div id="map" style="width: 100%; height: 450px;"></div>
                <script>
                    var traf = L.tileLayer('https://{{s}}.google.com/vt/lyrs=m,traffic&x={{x}}&y={{y}}&z={{z}}', {{subdomains:['mt0','mt1','mt2','mt3']}});
                    var map = L.map('map', {{center: [{p_c['lat']}, {p_c['lon']}], zoom: 12, layers: [traf]}});
                    var pts = {puntos_km};
                    var group = L.featureGroup();
                    pts.forEach(function(p) {{
                        var icon = L.divIcon({{
                            className: 'label',
                            html: "<div style='color:#000; font-weight:700; font-size:11px; text-shadow: 1px 1px 0 #fff;'>" + p.pk + "</div>",
                            iconSize: [25, 15]
                        }});
                        L.marker([p.lat, p.lon], {{icon: icon}}).addTo(group);
                    }});
                    L.marker([{p_c['lat']}, {p_c['lon']}]).addTo(group).bindPopup("PK {pk_val}").openPopup();
                    group.addTo(map);
                    map.fitBounds(group.getBounds());
                </script>
            </div>
            """
            components.html(mapa_html, height=470)
        else:
            st.error(f"Vía {via_input} no localizada.")

    # --- SECCIÓN INFERIOR PERMANENTE ---
    st.markdown("---")
    with st.expander("🚀 NOVEDADES DE LA VERSIÓN (v3.0)"):
        st.markdown("""
            <div style="background-color: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 5px solid #ffd700;">
                <p style="color: #ffd700; font-weight: bold; margin-bottom: 8px; font-size: 18px;">Revisión Marzo 2026:</p>
                <ul style="color: #ffffff; font-size: 15px; line-height: 1.6;">
                    <li><b>🗂️ Nueva Ficha Técnica:</b> Datos de titularidad y recorrido en tarjeta.</li>
                    <li><b>📡 Geolocalización:</b> Identificación de municipios automática.</li>
                    <li><b>🚦 Tráfico Real:</b> Visor con flujo circulatorio activo.</li>
                    <li><b>📍 Pin de Precisión:</b> Marcado exacto en Google Maps.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("🔒 PRIVACIDAD Y SEGURIDAD"):
        st.markdown("""
            <div style="padding: 10px;">
                <ul style="color: #cccccc; font-size: 14px;">
                    <li><b>Sin rastreo de IP:</b> No se registra el origen de las conexiones.</li>
                    <li><b>Sin guardado de datos:</b> No se almacenan coordenadas ni consultas.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # FOOTER
    col1, col2 = st.columns([1, 4])
    with col1:
        ruta_img = "assets/escudo.png" if os.path.exists("assets/escudo.png") else "escudo.png"
        try: st.image(ruta_img, width=80)
        except: st.markdown("<h2 style='text-align:right;'>🛡️</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown("<br>**✍️ Gómez Dest B**", unsafe_allow_html=True)
