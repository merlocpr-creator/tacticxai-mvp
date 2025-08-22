import streamlit as st

# tacticai_mvp_refactor.py
# TacticAI - MVP Refactorizado con análisis táctico mejorado y visualizaciones atractivas
# Autor: Pedro Rafael Merlo Campos – 2025
# Requisitos: streamlit, statsbombpy, pandas, numpy, matplotlib, seaborn, mplsoccer, streamlit-option-menu, streamlit-drawable-canvas, pillow

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsbombpy import sb
from streamlit_option_menu import option_menu
from streamlit_drawable_canvas import st_canvas
from mplsoccer import Pitch
from PIL import Image
from io import BytesIO
import random
import subprocess
import sys
import groq

# =========================
# CONFIGURACIÓN VISUAL
# =========================
st.set_page_config(page_title="TacticAI Pro", layout="wide")
st.markdown("""
    <style>
    .block-container { padding: 1rem 2rem; }
    h1 { text-align: center; margin-bottom: 6px; }
    /* Las tarjetas en mosaico responsivo */
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1rem;
        align-items: stretch;
        margin-top: 20px;
    }
    .card {
        background: #222;
        border-radius: 12px;
        padding: 15px 20px;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card h3 {
        margin-top: 0;
        font-size: 18px;
        border-bottom: 2px solid #555;
        padding-bottom: 6px;
    }
    .stat {
        font-size: 18px;
        margin: 10px 0 4px 0;
        font-weight: bold;
    }
    .label {
        font-weight: normal;
        color: #ccc;
        font-size: 14px;
    }
    /* Centrado de la tarjeta del simulador */
    .center-wrap {
        max-width: 720px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# HELPERS ROBUSTOS
# =========================
def extract_name_from_maybe_dict(v):
    if isinstance(v, dict):
        if 'name' in v and isinstance(v['name'], str):
            return v['name']
        for val in v.values():
            if isinstance(val, str):
                return val
        return str(v)
    return v

def safe_type_name(x):
    if isinstance(x, dict):
        return x.get('name') or x.get('type') or None
    return x

def safe_team_name(x):
    return extract_name_from_maybe_dict(x)

# =========================
# CARGA Y EXTRACCIÓN DE DATOS
# =========================
def cargar_competiciones():
    try:
        with st.spinner("Cargando competiciones de StatsBomb..."):
            comps = sb.competitions()
        if comps is None or comps.empty:
            st.error("No se obtuvo información de competencias desde StatsBomb.")
            return pd.DataFrame()
        return comps
    except Exception as e:
        st.error(f"Error al cargar competiciones: {e}")
        return pd.DataFrame()

def obtener_partidos(comp_id, season_id):
    try:
        with st.spinner("Descargando lista de partidos..."):
            return sb.matches(competition_id=comp_id, season_id=season_id)
    except Exception as e:
        st.warning(f"No se pudieron descargar partidos: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=True)
def obtener_datos_eventos_por_nombre(equipo_nombre, matches_df, max_partidos=3):
    if matches_df is None or matches_df.empty:
        return pd.DataFrame()
    partidos_equipo = matches_df[
        (matches_df['home_team_name'] == equipo_nombre) | (matches_df['away_team_name'] == equipo_nombre)
    ].copy()
    if partidos_equipo.empty:
        return pd.DataFrame()
    if 'match_date' in partidos_equipo.columns:
        partidos_equipo = partidos_equipo.sort_values('match_date', ascending=False)
    partidos_ids = partidos_equipo['match_id'].head(max_partidos).tolist()
    eventos = []
    for mid in partidos_ids:
        try:
            with st.spinner(f"Cargando eventos del partido {mid}..."):
                ev = sb.events(match_id=mid)
            if ev is not None and not ev.empty:
                eventos.append(ev)
        except Exception as e:
            st.warning(f"Error descargando eventos para match_id {mid}: {e}")
    if not eventos:
        return pd.DataFrame()
    df = pd.concat(eventos, ignore_index=True)
    # Normalizar columnas
    df['type_name'] = df['type'].apply(safe_type_name) if 'type' in df.columns else None
    df['team_name'] = df['team'].apply(safe_team_name) if 'team' in df.columns else None
    # xG column
    if 'shot_statsbomb_xg' in df.columns:
        df['xg'] = df['shot_statsbomb_xg']
    else:
        if 'shot' in df.columns:
            df['xg'] = df['shot'].apply(lambda s: s.get('statsbomb_xg') if isinstance(s, dict) else None)
        else:
            df['xg'] = None
    # columnas básicas mínimas
    for col in ['player', 'location', 'minute']:
        if col not in df.columns:
            df[col] = None
    return df

# =========================
# ANÁLISIS TÁCTICO SIMPLE
# =========================
def evaluar_rendimiento_xg(df_eventos, jugador, umbral=0.1):
    tiros = df_eventos[(df_eventos['player'] == jugador) & (df_eventos['type_name'] == 'Shot')]
    if tiros.empty:
        return f"No hay tiros registrados para {jugador}."
    xg_promedio = tiros['xg'].mean()
    if xg_promedio >= umbral:
        return f"{jugador} tiene un buen promedio de xG: {xg_promedio:.2f}."
    else:
        return f"{jugador} podría mejorar su rendimiento con xG promedio de {xg_promedio:.2f}."

def sugerir_formacion(fortalezas, debilidades):
    """
    Reglas básicas:
    - Si fortaleza = bandas + debilidad rival = laterales, sugerir 4-3-3 / 3-4-3 y presionar por fuera.
    - Si fortaleza = juego interior + debilidad rival = mediocentro, sugerir 4-2-3-1 / 4-4-2 rombo.
    - Si rival sufre balones a la espalda, sugerir línea de 3 arriba (4-3-3) con extremos rápidos.
    - Si rival domina posesión pero sufre transiciones, sugerir 4-4-2 compacto y contra.
    """
    recomendaciones = []
    sugeridas = set()

    def add(form, motivo):
        if form not in sugeridas:
            sugeridas.add(form)
            recomendaciones.append((form, motivo))

    if ("Bandas fuertes" in fortalezas and "Laterales débiles" in debilidades) or \
       ("Centros precisos" in fortalezas and "Juego aéreo débil" in debilidades):
        add("4-3-3", "Aprovecha amplitud y centros desde las bandas.")
        add("3-4-3", "Carrileros altos para fijar laterales rivales y cargar el área.")

    if ("Juego interior" in fortalezas and "Mediocentro débil" in debilidades) or \
       ("Mediapunta creativo" in fortalezas and "Entre líneas" in debilidades):
        add("4-2-3-1", "Estructura para dominar carril central y activar 10 libre.")
        add("4-4-2 (rombo)", "Superioridad por dentro con 4 carriles interiores.")

    if "Espalda de la defensa" in debilidades:
        add("4-3-3", "Extremos atacando profundidad y diagonales a la espalda.")
        add("4-2-2-2", "Doble punta para atacar rupturas constantes.")

    if "Sufre transiciones" in debilidades:
        add("4-4-2", "Bloque medio-bajo, robo y salida rápida por bandas.")
        add("5-3-2", "Seguridad atrás y dos puntas para correr al espacio.")

    if not recomendaciones:
        add("4-3-3", "Config. base equilibrada si no hay señales claras.")
    return recomendaciones

# =========================
# VISUALIZACIONES
# =========================
def graficar_xg_por_jugador(df_eventos):
    tiros = df_eventos[df_eventos['type_name'] == 'Shot']
    if tiros.empty:
        st.info("No hay tiros para graficar.")
        return
    xg_jugadores = tiros.groupby('player')['xg'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(x=xg_jugadores.values, y=xg_jugadores.index, palette="viridis")
    plt.title("Top 10 jugadores por xG")
    plt.xlabel("xG acumulado")
    plt.ylabel("Jugador")
    st.pyplot(plt)

# =========================
# EXPORTACIÓN
# =========================
def exportar_datos(df, nombre_archivo="datos_exportados.csv"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar datos a CSV",
        data=csv,
        file_name=nombre_archivo,
        mime='text/csv'
    )

# =========================
# UTILIDADES PIZARRA / CANVAS
# =========================
def render_pitch_image(width=900, height=600, theme="green"):
    """Genera una imagen de cancha y la devuelve como PIL.Image para usar en st_canvas."""
    # mplsoccer usa dimensiones proporcionales, convertimos a imagen
    pitch = Pitch(pitch_type='statsbomb',
                  pitch_color='black' if theme == "black" else '#2E7D32',
                  line_color='white')
    fig, ax = pitch.draw(figsize=(width/100, height/100), tight_layout=False)
    ax.set_xlim(0, 120)
    ax.set_ylim(80, 0)
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

def formation_template(name):
    """
    Devuelve posiciones normalizadas (0..1) para 11 jugadores (x,y) en StatsBomb orientation (0-120 x, 0-80 y)
    Normalizamos al lienzo en pixeles multiplicando por canvas width/height.
    """
    # GK + líneas por defecto
    templates = {
        "4-3-3": [(0.07,0.50),
                  (0.20,0.15),(0.20,0.40),(0.20,0.60),(0.20,0.85),
                  (0.40,0.25),(0.40,0.50),(0.40,0.75),
                  (0.65,0.20),(0.75,0.50),(0.65,0.80)],
        "4-2-3-1": [(0.07,0.50),
                    (0.20,0.15),(0.20,0.40),(0.20,0.60),(0.20,0.85),
                    (0.38,0.40),(0.38,0.60),
                    (0.55,0.25),(0.50,0.50),(0.55,0.75),
                    (0.78,0.50)],
        "3-4-3": [(0.07,0.50),
                  (0.20,0.25),(0.20,0.50),(0.20,0.75),
                  (0.40,0.20),(0.40,0.40),(0.40,0.60),(0.40,0.80),
                  (0.65,0.20),(0.75,0.50),(0.65,0.80)],
        "4-4-2": [(0.07,0.50),
                  (0.20,0.15),(0.20,0.40),(0.20,0.60),(0.20,0.85),
                  (0.40,0.25),(0.40,0.45),(0.40,0.55),(0.40,0.75),
                  (0.70,0.40),(0.70,0.60)],
        "5-3-2": [(0.07,0.50),
                  (0.17,0.12),(0.17,0.30),(0.17,0.50),(0.17,0.70),(0.17,0.88),
                  (0.38,0.30),(0.38,0.50),(0.38,0.70),
                  (0.68,0.40),(0.68,0.60)],
        "4-2-2-2": [(0.07,0.50),
                    (0.20,0.15),(0.20,0.40),(0.20,0.60),(0.20,0.85),
                    (0.38,0.35),(0.38,0.65),
                    (0.55,0.35),(0.55,0.65),
                    (0.75,0.45),(0.78,0.55)],
        "4-4-2 (rombo)": [(0.07,0.50),
                          (0.20,0.15),(0.20,0.40),(0.20,0.60),(0.20,0.85),
                          (0.38,0.25),(0.38,0.50),(0.38,0.75),(0.48,0.50),
                          (0.72,0.40),(0.72,0.60)]
    }
    return templates.get(name, templates["4-3-3"])

def make_token(x, y, label, fill="#1976D2", radius=16, selectable=True):
    """Crea un objeto tipo círculo (fabric.js) para st_canvas initial_drawing."""
    return {
        "type": "circle",
        "left": float(x - radius),
        "top": float(y - radius),
        "radius": float(radius),
        "fill": fill,
        "stroke": "#ffffff",
        "strokeWidth": 2,
        "opacity": 0.95,
        "selectable": selectable,
        "hasControls": False,
        "hasBorders": False,
        "lockScalingX": True,
        "lockScalingY": True,
        "lockRotation": True,
        "text": label
    }

def make_label(x, y, text, color="#ffffff", selectable=False):
    return {
        "type": "textbox",
        "left": float(x),
        "top": float(y),
        "text": text,
        "fontSize": 14,
        "fill": color,
        "backgroundColor": "rgba(0,0,0,0.0)",
        "selectable": selectable,
        "editable": False
    }

def make_zone_rect(x, y, w, h, label, stroke="#FF5252", fill="rgba(255,82,82,0.15)"):
    return [
        {
            "type": "rect",
            "left": float(x),
            "top": float(y),
            "width": float(w),
            "height": float(h),
            "fill": fill,
            "stroke": stroke,
            "strokeWidth": 2,
            "rx": 6,
            "ry": 6,
            "selectable": False
        },
        make_label(x + 6, y + 6, label, color=stroke, selectable=False)
    ]

def build_initial_board(width, height, formation_name, color="#1976D2", opponent_color="#E53935",
                        show_weak_left=False, show_weak_right=False, show_halfspace=False):
    objs = []
    # Zonas débiles predefinidas (oponente)
    if show_weak_left:
        objs += make_zone_rect( width*0.55, height*0.05, width*0.40, height*0.20, "Zona débil: Lado Izquierdo", stroke="#FF7043")
    if show_weak_right:
        objs += make_zone_rect( width*0.55, height*0.75, width*0.40, height*0.20, "Zona débil: Lado Derecho", stroke="#FF7043")
    if show_halfspace:
        objs += make_zone_rect( width*0.45, height*0.30, width*0.20, height*0.40, "Entre líneas / Media luna", stroke="#FF5252", fill="rgba(255,82,82,0.12)")

    # Fichas propias
    coords = formation_template(formation_name)
    for i, (nx, ny) in enumerate(coords, start=1):
        x = nx * width
        y = ny * height
        label = "GK" if i == 1 else str(i)
        objs.append(make_token(x, y, label, fill=color, selectable=True))
        objs.append(make_label(x-6, y-32, label, color="#fff"))

    # Fichas rivales (fijas de referencia)
    opp_coords = formation_template("4-4-2")
    for i, (nx, ny) in enumerate(opp_coords, start=1):
        x = (1.0 - nx) * width   # espejo
        y = (1.0 - ny) * height  # espejo vertical para variar
        label = "GK" if i == 1 else str(i)
        objs.append(make_token(x, y, label, fill=opponent_color, selectable=False))

    return {"objects": objs, "background": "transparent"}

# =========================
# MAIN
# =========================
# Cargar competiciones
comps = cargar_competiciones()

# Lista ligas disponibles
ligas = comps['competition_name'].unique().tolist() if not comps.empty else ["(No disponible)"]

# Menú lateral con nueva sección IA táctica (se respeta tal cual)
with st.sidebar:
    selected = option_menu(
        menu_title="TacticAI Pro",
        options=["Inicio", "Análisis Rival", "Análisis Propio", "Mapa de Calor", "Pizarra", "Comparativa", "Simulador", "Subir CSV", "IA táctica"],
        icons=["house", "trophy", "shield", "fire", "pencil", "graph-up", "play", "upload", "robot"],
        default_index=0,
    )

st.markdown("<h1>TacticAI Pro</h1>", unsafe_allow_html=True)

# Selección liga y equipos
col1, col2, col3 = st.columns([1,1,1])
with col1:
    liga_sel = st.selectbox("Selecciona una liga", ligas)
if not comps.empty and liga_sel != "(No disponible)":
    cond = comps['competition_name'] == liga_sel
    try:
        comp_id = comps[cond].iloc[0]['competition_id']
        season_id = comps[cond].iloc[0]['season_id']
    except Exception:
        comp_id = None
        season_id = None
    matches = obtener_partidos(comp_id, season_id) if comp_id and season_id else pd.DataFrame()
else:
    matches = pd.DataFrame()

# Normalizar nombres de equipos
if not matches.empty:
    matches = matches.copy()
    matches['home_team_name'] = matches['home_team'].apply(extract_name_from_maybe_dict) if 'home_team' in matches.columns else None
    matches['away_team_name'] = matches['away_team'].apply(extract_name_from_maybe_dict) if 'away_team' in matches.columns else None
    equipos_home = matches['home_team_name'].dropna().unique().tolist()
    equipos_away = matches['away_team_name'].dropna().unique().tolist()
    equipos = sorted(list(set(equipos_home + equipos_away)))
else:
    equipos = []

with col2:
    equipo_rival = st.selectbox("Equipo Rival", equipos if equipos else ["(sin datos)"])
with col3:
    if equipos:
        default_prop = st.session_state.get("equipo_prop", None)
        opciones_prop = [e for e in equipos if e != (equipo_rival if equipo_rival is not None else "")]
        if default_prop in opciones_prop:
            equipo_prop = st.selectbox("Tu Equipo", opciones_prop, index=opciones_prop.index(default_prop))
        else:
            equipo_prop = st.selectbox("Tu Equipo", opciones_prop)
        st.session_state["equipo_prop"] = equipo_prop
    else:
        equipo_prop = st.selectbox("Tu Equipo", ["(sin datos)"])

# =========================
# SECCIONES DEL DASHBOARD
# =========================
if selected == "Inicio":
    st.markdown("<h2 style='margin-top: 20px;'>Bienvenido a TacticAI Pro</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:16px; line-height:1.6; text-align: justify; padding: 10px 15px; background-color: #1A1A1A; border-radius: 8px;'>
    <strong>TacticAI</strong> es una herramienta innovadora que va a revolucionar la forma en que los equipos de fútbol toman decisiones tácticas. 
    El MVP actual integra datos históricos de más de <strong>20 ligas a nivel mundial</strong>, desde la Premier League hasta la Copa América, 
    y permite a los entrenadores comparar rendimientos, analizar rivales y obtener sugerencias tácticas personalizadas.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown("<h4>¿Qué puedes hacer en TacticAI?</h4>", unsafe_allow_html=True)
    st.markdown("""
    - Analizar a tus rivales con datos reales de partidos.
    - Obtener sugerencias tácticas adaptadas a cada formación.
    - Usar una pizarra visual para diseñar tus propias estrategias.
    - Subir tus datos o simular resultados con base en rendimiento.
    """)

elif selected == "Análisis Rival":
    st.header(f"Análisis Rival: {equipo_rival}")
    if not matches.empty and equipo_rival and equipo_rival != "(sin datos)":
        df_r = obtener_datos_eventos_por_nombre(equipo_rival, matches, max_partidos=4)
        if df_r.empty:
            st.warning("No se encontraron eventos reales para este equipo.")
        else:
            st.write(f"Eventos cargados: {df_r.shape[0]}")

            # Visualización de formaciones (top 5) con estilo tarjeta
            if 'tactics' in df_r.columns:
                formaciones = df_r['tactics'].dropna().apply(lambda t: t.get('formation') if isinstance(t, dict) else None)
                if not formaciones.empty:
                    top_formaciones = formaciones.value_counts().head(5)
                    st.subheader("Formaciones detectadas (top 5)")
                    cols = st.columns(len(top_formaciones))
                    for i, (formacion, count) in enumerate(top_formaciones.items()):
                        with cols[i]:
                            st.markdown(f"""
                                <div style='background:#2a9d8f; padding:15px; border-radius:12px; color:#fff; text-align:center; font-weight:bold;'>
                                {formacion}<br><span style='font-weight:normal; font-size:14px;'>{count} partidos</span>
                                </div>
                            """, unsafe_allow_html=True)

            # Visualización top xG promedio por jugador -> TARJETAS EN MOSAICO
            shots = df_r[df_r['type_name'] == 'Shot']
            if not shots.empty and shots['xg'].notna().any():
                xg_prom = shots.groupby('player')['xg'].mean().sort_values(ascending=False).head(12)
                st.subheader("Top xG promedio por jugador")
                st.markdown("<div class='card-container'>", unsafe_allow_html=True)
                for jugador, xg_val in xg_prom.items():
                    color_xg = "#2a9d8f" if xg_val >= 0.1 else "#f4a261"
                    st.markdown(f"""
                        <div class="card" style="border-top: 4px solid {color_xg};">
                            <h3>{jugador}</h3>
                            <div class="stat" style="color:{color_xg};">{xg_val:.2f}</div>
                            <div class="label">xG promedio</div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No se detectaron tiros con xG para mostrar.")
    else:
        st.warning("No hay partidos cargados para la liga/equipo seleccionado.")

elif selected == "Análisis Propio":
    st.header(f"Tu equipo: {equipo_prop}")
    if not matches.empty and equipo_prop and equipo_prop != "(sin datos)":
        df_p = obtener_datos_eventos_por_nombre(equipo_prop, matches, max_partidos=4)
        if df_p.empty:
            st.warning("No se encontraron eventos reales para tu equipo.")
        else:
            st.write(f"Eventos cargados: {df_p.shape[0]}")
            jugadores_top = df_p['player'].value_counts().head(5).index.tolist()
            for jugador in jugadores_top:
                mensaje = evaluar_rendimiento_xg(df_p, jugador)
                st.write(mensaje)
            graficar_xg_por_jugador(df_p)
            exportar_datos(df_p, nombre_archivo=f"{equipo_prop}_eventos.csv")
    else:
        st.warning("No hay datos disponibles para tu equipo. Comprueba selección de liga y equipo.")

elif selected == "Mapa de Calor":
    st.header("Mapa de calor de tiros")
    if not matches.empty and equipo_prop and equipo_prop != "(sin datos)":
        df_p = obtener_datos_eventos_por_nombre(equipo_prop, matches, max_partidos=6)
        if df_p.empty:
            st.warning("No se encontraron eventos para generar mapa de calor.")
        else:
            shots = df_p[df_p['type_name'] == 'Shot']
            if 'location' in shots.columns and shots['location'].notna().any():
                locs = shots['location'].dropna().tolist()
                x = [p[0] for p in locs if isinstance(p, (list,tuple)) and len(p)==2]
                y = [p[1] for p in locs if isinstance(p, (list,tuple)) and len(p)==2]
                pitch = Pitch(pitch_type='statsbomb', pitch_color='black', line_color='white')
                fig, ax = pitch.draw(figsize=(6,4))
                if x and y:
                    sns.kdeplot(
                        x=x,
                        y=y,
                        ax=ax,
                        fill=True,
                        cmap='magma',
                        alpha=0.8,
                        thresh=0.05,
                        bw_adjust=0.6
                    )
                    st.pyplot(fig)
                else:
                    st.info("No hay datos suficientes para generar el mapa de calor.")
            else:
                st.info("No hay tiros con coordenadas de localización.")
    else:
        st.warning("Selecciona liga/equipo válido.")

elif selected == "Pizarra":
    st.header("Pizarra táctica básica")

    # Selección fondo
    fondo = st.selectbox("Selecciona el fondo de la pizarra:", ["Pizarra táctica (negro)", "Pizarra de campo (verde)"])

    # Parámetros del trazo
    st.markdown("### Configuración del trazo")
    stroke_color = st.color_picker("Color del trazo", "#FF0000")
    stroke_width = st.slider("Grosor del trazo", 1, 10, 3)
    drawing_mode = st.selectbox("Modo de dibujo", ["freedraw", "line", "rect", "circle", "transform"])

    # Definir fondo según selección
    if fondo == "Pizarra táctica (negro)":
        bg_color = "black"
    else:
        bg_color = "#007A33"  # verde cancha

    # Tamaño fijo para canvas
    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",  # transparente para dibujo libre
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=600,
        width=900,
        drawing_mode=drawing_mode,
        key="canvas_pizarra",
    )

    # Botón para descargar imagen dibujada
    if canvas_result.image_data is not None:
        img_bytes = BytesIO()
        plt.imsave(img_bytes, canvas_result.image_data.astype('uint8'))
        img_bytes.seek(0)
        st.download_button(
            "Descargar imagen (PNG)",
            data=img_bytes,
            file_name="pizarra.png",
            mime="image/png"
        )

    st.caption("Tip: Usa 'transform' para arrastrar fichas. Cambia a 'line' o 'freedraw' para rutas de desmarque o flechas.")

elif selected == "Comparativa":
    st.header("Comparativa rápida")
    if not matches.empty and equipo_prop and equipo_rival and equipo_prop != "(sin datos)" and equipo_rival != "(sin datos)":
        df_p = obtener_datos_eventos_por_nombre(equipo_prop, matches, max_partidos=4)
        df_r = obtener_datos_eventos_por_nombre(equipo_rival, matches, max_partidos=4)
        def count_event_type(df, tipo):
            if df.empty: return 0
            return df[df['type_name'] == tipo].shape[0]

        tiros_p = count_event_type(df_p, 'Shot')
        tiros_r = count_event_type(df_r, 'Shot')
        tarjetas_p = count_event_type(df_p, 'Card')
        tarjetas_r = count_event_type(df_r, 'Card')

        color_prop = "#2a9d8f"
        color_rival = "#e76f51"

        st.markdown(f"""
        <div style='display:flex; gap:2rem;'>
            <div style='flex:1; background:#222; padding:15px; border-radius:10px; color:#fff; box-shadow: 0 4px 8px rgba(0,0,0,0.5);'>
                <h3 style='text-align:center; border-bottom: 2px solid {color_prop}; padding-bottom: 6px;'>{equipo_prop}</h3>
                <p style='font-size:20px; margin:10px 0;'><strong style='color:{color_prop};'>{tiros_p}</strong> Tiros</p>
                <p style='font-size:20px; margin:10px 0;'><strong style='color:{color_prop};'>{tarjetas_p}</strong> Tarjetas</p>
            </div>
            <div style='flex:1; background:#222; padding:15px; border-radius:10px; color:#fff; box-shadow: 0 4px 8px rgba(0,0,0,0.5);'>
                <h3 style='text-align:center; border-bottom: 2px solid {color_rival}; padding-bottom: 6px;'>{equipo_rival}</h3>
                <p style='font-size:20px; margin:10px 0;'><strong style='color:{color_rival};'>{tiros_r}</strong> Tiros</p>
                <p style='font-size:20px; margin:10px 0;'><strong style='color:{color_rival};'>{tarjetas_r}</strong> Tarjetas</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Selecciona liga y equipos válidos para comparar.")
# Recomendaciones básicas (reglas)
    st.subheader("Recomendador táctico (reglas básicas)")
    colf, cold = st.columns(2)
    with colf:
        fortalezas = st.multiselect("Fortalezas propias", ["Bandas fuertes","Centros precisos","Juego interior","Mediapunta creativo","Presión alta"])
    with cold:
        debilidades = st.multiselect("Debilidades del rival", ["Laterales débiles","Juego aéreo débil","Mediocentro débil","Entre líneas","Espalda de la defensa","Sufre transiciones"])

    if st.button("Sugerir formaciones"):
        recs = sugerir_formacion(fortalezas, debilidades)
        for f, motivo in recs:
            st.markdown(f"- **{f}** — {motivo}")


elif selected == "Simulador":
    st.header("Simulador sencillo")
    df_p = obtener_datos_eventos_por_nombre(equipo_prop, matches, max_partidos=4) if matches is not None else pd.DataFrame()
    df_r = obtener_datos_eventos_por_nombre(equipo_rival, matches, max_partidos=4) if matches is not None else pd.DataFrame()
    xg_p = df_p['xg'].sum() if not df_p.empty and 'xg' in df_p.columns else 0
    xg_r = df_r['xg'].sum() if not df_r.empty and 'xg' in df_r.columns else 0
    total = xg_p + xg_r
    prob = round(100 * xg_p / total, 1) if total > 0 else 50

    # Definir color según probabilidad
    if prob < 35:
        color = "#e63946"  # rojo
    elif prob <= 65:
        color = "#f4a261"  # amarillo
    else:
        color = "#2a9d8f"  # verde

    # Tarjeta centrada (sin imagen al lado)
    st.markdown(f"""
        <div class="center-wrap">
            <div style="padding:16px; border-radius:12px; background-color:#222; color:{color}; font-size:36px; font-weight:bold; text-align:center;">
                Probabilidad de ganar de <br><span style="color:#fff;">{equipo_prop}</span>
                <div style="margin-top:8px; font-size:48px;">{prob} %</div>
            </div>
            <div style="background:#444; border-radius:10px; height:24px; width:100%; margin-top:15px;">
                <div style="background:{color}; height:100%; width:{prob}%; border-radius:10px;"></div>
            </div>
            <p style="margin-top:10px; font-size:16px; color:#aaa; text-align:center;">Basado en el xG total acumulado</p>
        </div>
    """, unsafe_allow_html=True)

elif selected == "Subir CSV":
    st.header("Cargar CSV propio")
    archivo = st.file_uploader("Selecciona CSV con eventos (formato StatsBomb recomendado)", type=["csv"])
    if archivo:
        df_csv = pd.read_csv(archivo)
        st.dataframe(df_csv.head())
        exportar_datos(df_csv, nombre_archivo="datos_subidos.csv")

elif selected == "IA táctica":
    st.header("IA Táctica - Demo con Chat IA")

    user_input = st.text_input("Escribe tu pregunta táctica (ejemplo: ¿Cómo defender un 4-3-3?)")

    if user_input:
        import os
        from groq import Groq  # ✅ se importa Groq, no GroqClient

        # Crear cliente
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Enviar prompt al chatbot Groq
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # 👈 puedes cambiar a otro modelo de Groq
            messages=[
                {"role": "system", "content": "Eres un asistente experto en táctica de fútbol."},
                {"role": "user", "content": user_input}
            ]
        )

        # Mostrar respuesta
        st.success(response.choices[0].message.content)


from PIL import Image
import streamlit as st

# Pie de página con logo de StatsBomb
st.markdown("---")  # línea separadora

# Cargar logo
logo = Image.open("assets/StatsBomb logo.png")  
# Mostrar logo
st.image(logo, width=150)  # ajusta el tamaño si quieres

# Texto de crédito
st.caption("Pedro Rafael Merlo Campos - TacticAI MVP 2025 | Datos: StatsBomb Open Data")

