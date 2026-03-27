import streamlit as st
import pandas as pd
import os
import time
import base64
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

# ⚠️ PROTOCOLO DE SEGURIDAD EXCLUSIVO PARA FRAN:
# PROHIBIDO MODIFICAR SIN ORDEN EXPLÍCITA: 
# 1. Motor de búsqueda de PK y lógica de titularidad.
# 2. Filtros de frontera (Valencia, Alicante, Castellón).
# 3. Textos de Privacidad y Seguridad.
# 4. Base de datos de denominaciones locales.

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Carreteras", page_icon="🚔", layout="centered")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

ruta_logo_puro = "assets/escudo.png" if os.path.exists("assets/escudo.png") else "escudo.png"
logo_base64 = get_base64_image(ruta_logo_puro)

# --- DICCIONARIO MAESTRO DE CARRETERAS ---
DICCIONARIO_VIAS = {
    "A-3": "A-3 (Madrid - Valencia)", "A-7": "A-7 (Tarragona - Algeciras)", 
    "A-23": "A-23 (Sagunto - Somport)", "A-31": "A-31 (Atalaya del Cañavate - Alicante)",
    "A-33": "A-33 (Blanca - Fuente de la Higuera)", "A-35": "A-35 (Almansa - Xàtiva)",
    "A-38": "A-38 (Silla - Gandía)", "AP-7": "AP-7 (Autopista del Mediterráneo)",
    "V-11": "V-11 (Acceso Aeropuerto Manises)", "V-15": "V-15 (Valencia - CV-500)",
    "V-21": "V-21 (Puzol - Valencia)", "V-23": "V-23 (Puzol - Sagunto)",
    "V-30": "V-30 (Circunvalación Valencia)", "V-31": "V-31 (Silla - Valencia / Pista Silla)",
    "CV-10": "CV-10 (Autovía de la Plana)", "CV-20": "CV-20 (Vila-real - Puebla de Arenoso)",
    "CV-25": "CV-25 (Llíria - Segorbe)", "CV-30": "CV-30 (Ronda Norte Valencia)",
    "CV-31": "CV-31 (Paterna - Godella)", "CV-32": "CV-32 (Carretera Gombalda)",
    "CV-33": "CV-33 (Albal - Torrent)", "CV-35": "CV-35 (Valencia - Ademuz)",
    "CV-36": "CV-36 (Valencia - Torrent)", "CV-40": "CV-40 (Xàtiva - Alcoy)",
    "CV-42": "CV-42 (Alzira - Almussafes)", "CV-50": "CV-50 (Tavernes - Llíria)",
    "CV-60": "CV-60 (Ollería - Gandía)", "CV-80": "CV-80 (Sax - Castalla)",
    "CV-81": "CV-81 (Ontinyent - Villena)", "CV-300": "CV-300 (Meliana - El Puig)",
    "CV-310": "CV-310 (Burjassot - Torres Torres)", "CV-312": "CV-312 (Alboraya - Port Saplaya)",
    "CV-315": "CV-315 (Valencia - Noquera)", "CV-370": "CV-370 (Manises - Riba-roja)",
    "CV-400": "CV-400 (Valencia - Albal)", "CV-401": "CV-401 (Alfafar - El Saler)",
    "CV-403": "CV-403 (Xirivella - Torrent)", "CV-405": "CV-405 (Torrent - Montroy)",
    "CV-410": "CV-410 (Alaquàs - Bonaire)", "CV-500": "CV-500 (Valencia - El Saler - Sueca)",
    "CV-505": "CV-505 (Alzira - Sueca)", "CV-510": "CV-510 (Alzira - Favara)",
    "CV-600": "CV-600 (Xàtiva - Simat)", "CV-700": "CV-700 (Bocairent - El Verger)",
    "CV-715": "CV-715 (Oliva - Pego - Callosa)", "N-332": "N-332 (Cartagena - Valencia)",
    "N-340": "N-340 (Cádiz - Barcelona)", "N-220": "N-220 (Acceso Aeropuerto - Paterna)"
}

st.markdown("""<style>
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 3.5rem !important; background-color: #000000; }
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"], div[data-testid="stSelectbox"] { width: 100% !important; }
    .stProgress > div > div > div > div { background-color: #104A30 !important; }
    .header-left { text-align: left; width: 100%; margin-bottom: 25px; }
    .header-title { color: #ffffff; font-size: 52px; font-weight: 900; line-height: 1.1; margin: 0; border-bottom: 6px solid #104A30; display: inline-block; }
    .header-subtitle { color: #ffffff; font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 4.3px; margin-top: 8px; display: block; }
    .version-box { background-color: #1a1a1a; padding: 20px; border-radius: 15px; border: 3px solid #104A30; margin-top: 10px; margin-bottom: 15px; }
    .antena-animada { font-size: 60px; text-align: center; margin: 10px 0; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.2); opacity: 0.7; } 100% { transform: scale(1); opacity: 1; } }
    .firma-container { display: flex; align-items: center; justify-content: flex-start; gap: 10px; padding-top: 20px; border-top: 1px solid #333; margin-top: 20px; }
</style>""", unsafe_allow_html=True)

# CABECERA A LA IZQUIERDA
st.markdown("""<div class="header-left"><div class="header-title">🛣️ CARRETERAS</div><div class="header-subtitle">RED VIARIA COMUNIDAD VALENCIANA</div></div>""", unsafe_allow_html=True)

# --- BIENVENIDA (SOLO PRUEBAS Y FEEDBACK) ---
if 'bienvenida_activa' not in st.session_state: st.session_state.bienvenida_activa = True
if st.session_state.bienvenida_activa:
    st.markdown("""<div class="version-box">
        <h3 style="color: #ffffff; background-color: #104A30; padding: 10px; border-radius: 5px; text-align: center;">🚨 APLICACIÓN EN PRUEBAS</h3>
        <p style="color: #ffffff; margin-top: 15px; text-align: center; font-size: 18px;">
            Se ruega a los usuarios utilizar esta aplicación para <b>comprobar datos y verificar posibles fallos</b> de trazado, ubicación o denominación de carreteras.<br><br>
            Su uso activo nos ayudará a detectar errores y mejorar la precisión del sistema.
        </p>
    </div>""", unsafe_allow_html=True)
    if st.button("✅ ACCEDER Y COMPROBAR SISTEMA", use_container_width=True):
        st.session_state.bienvenida_activa = False
        st.rerun()

# --- CARGA Y BUSCADOR ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('db_carreteras_pk.csv')
        df['id_vial'] = df['id_vial'].astype(str).str.strip().str.upper()
        return df
    except: return pd.DataFrame()

df_raw = load_data()
geolocator = Nominatim(user_agent="sector_cv_fran_v3", timeout=10)

if not st.session_state.bienvenida_activa:
    st.markdown('<div style="color:#104A30; font-weight:900; font-size:24px; margin-top:15px; margin-bottom:10px;">📍 DATOS DE LA CONSULTA</div>', unsafe_allow_html=True)
    
    prov_sel = st.selectbox("PROVINCIA:", ["VALENCIA", "ALICANTE", "CASTELLÓN"])
    via_raw = st.text_input("CARRETERA:")
    via_input = via_raw.strip().upper()

    if via_input:
        puntos = df_raw[df_raw['id_vial'] == via_input].sort_values('pk')
        
        if not puntos.empty:
            if prov_sel == "VALENCIA":
                if via_input == "AP-7": puntos = puntos[((puntos['pk'] >= 302) & (puntos['pk'] <= 466)) | ((puntos['pk'] >= 526) & (puntos['pk'] <= 601))]
                elif via_input == "N-332": puntos = puntos[puntos['pk'] >= 204.5]
                elif via_input == "A-7": puntos = puntos[(puntos['pk'] >= 292.95) & (puntos['pk'] <= 429)]
                elif via_input == "CV-81": puntos = puntos[puntos['pk'] <= 34] 
                else: puntos = puntos[(puntos['lat'] >= 38.751) & (puntos['lat'] <= 40.051)]
            elif prov_sel == "ALICANTE": puntos = puntos[puntos['lat'] < 38.751]
            elif prov_sel == "CASTELLÓN": puntos = puntos[puntos['lat'] > 40.051]

        if puntos.empty:
            st.error(f"⚠️ LA CARRETERA '{via_input}' NO EXISTE O NO PERTENECE A {prov_sel}.")
        else:
            pk_min, pk_max = puntos['pk'].min(), puntos['pk'].max()
            long_t = round(pk_max - pk_min, 1)
            titular = "ESTADO (MITMS)" if via_input.startswith(('A-', 'AP-', 'N-', 'V-')) else "GENERALITAT (GVA)"

            nombre_final = ""
            if via_input in DICCIONARIO_VIAS: nombre_final = DICCIONARIO_VIAS[via_input]
            else:
                placeholder_carga = st.empty()
                with placeholder_carga.container():
                    st.markdown('<div class="antena-animada">📡</div>', unsafe_allow_html=True)
                    barra = st.progress(0); txt_perc = st.empty()
                    for i in range(100):
                        time.sleep(0.01); progreso = i + 1
                        barra.progress(progreso)
                        txt_perc.markdown(f"<p style='text-align:center; color:#fff;'>CONECTANDO... {progreso}%</p>", unsafe_allow_html=True)
                        if i == 50:
                            try:
                                li = geolocator.reverse(f"{puntos.iloc[0]['lat']}, {puntos.iloc[0]['lon']}")
                                lf = geolocator.reverse(f"{puntos.iloc[-1]['lat']}, {puntos.iloc[-1]['lon']}")
                                def get_ref(loc):
                                    d = loc.raw.get('address', {}) if loc else {}
                                    return d.get('town') or d.get('village') or d.get('city') or "TM"
                                nombre_final = f"VÍA {via_input} ({get_ref(li)} - {get_ref(lf)})"
                            except: nombre_final = f"VÍA {via_input} (PK {pk_min} a PK {pk_max})"
                placeholder_carga.empty()

            st.markdown(f"""<div style="background-color: #1a1a1a; padding: 20px; border-radius: 15px; border: 3px solid #104A30; margin-bottom: 20px;"><h3 style="color: #ffffff; background-color: #104A30; padding: 10px; border-radius: 5px; text-align: center;">{nombre_final}</h3><p style="color: #ffffff;"><b>Titular:</b> {titular}</p><p style="color: #ffffff; font-size: 20px;"><b>Recorrido:</b> PK <span style="color: #AA151B; font-weight: 900;">{pk_min}</span> a PK <span style="color: #AA151B; font-weight: 900;">{pk_max}</span> (<span style="color: #AA151B; font-weight: 900;">{long_t} KM</span>)</p></div>""", unsafe_allow_html=True)
            
            puntos_km = puntos[puntos['pk'] % (1 if long_t <= 40 else 2 if long_t <= 80 else 5) == 0].to_dict('records')
            
            st.markdown("""<div style="background-color: #104A30; color: #fff; padding: 12px; border-radius: 8px; text-align: center; font-weight: 700;">👉 PULSA SOBRE EL PK PARA IR A GOOGLE MAPS</div>""", unsafe_allow_html=True)
            
            # --- MAPA CON HITO DETALLADO RESTAURADO ---
            mapa_html = f"""
            <div style="border-radius: 10px; overflow: hidden; border: 2px solid #104A30;">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <div id="map" style="width: 100%; height: 450px;"></div>
            <script>
            var map = L.map('map', {{center: [{puntos.iloc[0]['lat']}, {puntos.iloc[0]['lon']}], zoom: 12}});
            L.tileLayer('https://{{s}}.google.com/vt/lyrs=m,traffic&x={{x}}&y={{y}}&z={{z}}', {{subdomains:['mt0','mt1','mt2','mt3']}}).addTo(map);
            var pts = {puntos_km};
            var group = L.featureGroup();
            pts.forEach(function(p) {{
                var hitoHtml = "<div style='background: white; border: 2px solid black; border-radius: 4px; padding: 2px 6px; text-align: center; min-width: 35px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); font-family: Arial, sans-serif;'><div style='font-size: 8px; font-weight: bold; border-bottom: 1px solid black; margin-bottom: 1px;'>{via_input}</div><div style='color: black; font-weight: 900; font-size: 16px;'>" + p.pk + "</div></div>";
                var marker = L.marker([p.lat, p.lon], {{
                    icon: L.divIcon({{
                        className: 'custom-hito',
                        html: hitoHtml,
                        iconSize: [45, 40],
                        iconAnchor: [22, 20]
                    }})
                }}).addTo(group);
                marker.on('click', function() {{ 
                    window.open("https://www.google.com/maps/search/?api=1&query=" + p.lat + "," + p.lon, "_blank"); 
                }});
            }});
            group.addTo(map);
            map.fitBounds(group.getBounds());
            </script>
            </div>"""
            components.html(mapa_html, height=470)

    st.markdown("---")
    with st.expander("🛡️ PRIVACIDAD Y SEGURIDAD DE DATOS"):
        st.write("Esta aplicación ha sido desarrollada bajo estrictos estándares de seguridad de la información. No se recopilan datos personales. Las peticiones de geolocalización se procesan de forma efímera para determinar trazados de vías.")
    
    firma_html = f'<div class="firma-container">'
    if logo_base64:
        firma_html += f'<img src="data:image/png;base64,{logo_base64}" style="width:40px; height:auto;">'
    else:
        firma_html += '<span style="font-size:24px;">🚔</span>'
    firma_html += '<b style="color:#E0E0E0; font-size:16px; margin-left:10px;">✍️ Gómez Dest B</b></div>'
    st.markdown(firma_html, unsafe_allow_html=True)
