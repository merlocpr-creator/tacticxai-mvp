import streamlit as st

# tactisenseai_mvp_refactor.py
# TactisenseAI - Plataforma de análisis táctico de fútbol con IA
# Autor: Pedro Rafael Merlo Campos
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
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

# =========================
# CONFIGURACIÓN VISUAL & THEME (TACTISENSE OBSIDIAN)
# =========================
st.set_page_config(
    page_title="Tactisense AI",
    page_icon="assets/Tactic_AI_logo-removebg-preview (1).png",
    layout="wide"
)

# Google Fonts and Design System Tokens
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Space+Grotesk:wght@300;400;500;700&family=Outfit:wght@300;500;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Theme State Management
if "theme" not in st.session_state:
    st.session_state.theme = "TACTICAL DARK"

# Official Design System Tokens — Tactisense Brand Palette
if st.session_state.theme == "TACTICAL DARK":
    bg_color = "#040404"
    surface_base = "#080f1a"
    surface_card = "#0d1f35"
    surface_overlay = "#143252"
    text_primary = "#FFFFFF"
    text_secondary = "#B3B2B3"
    brand_blue = "#005595"
    accent_blue = "#3a8fd4"
    dark_navy = "#003B65"
    ghost_border = "rgba(0, 85, 149, 0.22)"
    card_shadow = "0 20px 48px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,85,149,0.12)"
    logo_filter = "brightness(0) invert(1)"        # logo oscuro → blanco
    logo_bg = "transparent"
    logo_padding = "0"
else:
    bg_color = "#F8FAFC"
    surface_base = "#EEF2F7"
    surface_card = "#FFFFFF"
    surface_overlay = "#DDE8F4"
    text_primary = "#040404"
    text_secondary = "#535354"
    brand_blue = "#005595"
    accent_blue = "#003B65"
    dark_navy = "#003B65"
    ghost_border = "rgba(0, 85, 149, 0.15)"
    card_shadow = "0 8px 32px rgba(0,85,149,0.10)"
    logo_filter = "none"
    logo_bg = "transparent"
    logo_padding = "0"

st.markdown(f"""
    <style>
    /* =========================================================
       TACTISENSE AI — DESIGN SYSTEM v2.0
       Palette: #005595 · #003B65 · #B3B2B3 · #040404 · #FFFFFF
    ========================================================= */

    /* BASE */
    .stApp {{
        background: {bg_color};
        font-family: 'Inter', sans-serif;
    }}
    .block-container {{
        padding: 2.5rem 3rem 4rem !important;
        max-width: 1400px !important;
    }}

    /* SCROLLBAR */
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: {bg_color}; }}
    ::-webkit-scrollbar-thumb {{ background: {brand_blue}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {accent_blue}; }}

    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: linear-gradient(175deg, {dark_navy} 0%, {bg_color} 100%) !important;
        border-right: 1px solid {ghost_border} !important;
    }}
    [data-testid="stSidebar"] .block-container {{
        padding: 1.5rem 0.75rem !important;
    }}

    /* TYPOGRAPHY */
    h1, h2, h3, h4 {{
        font-family: 'Outfit', sans-serif !important;
        color: {text_primary} !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        line-height: 1.15 !important;
    }}
    h1 {{ font-size: 2.8rem !important; }}
    h2 {{ font-size: 2rem !important; }}
    h3 {{ font-size: 1.3rem !important; font-weight: 700 !important; }}
    p, li {{ color: {text_primary}; font-family: 'Inter', sans-serif; }}

    /* HERO BLOCK */
    .hero-container {{
        background: linear-gradient(140deg, rgba(0,59,101,0.92) 0%, rgba(0,85,149,0.28) 55%, rgba(4,4,4,0.96) 100%);
        border: 1px solid {ghost_border};
        border-radius: 20px;
        padding: 56px 52px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    }}
    .hero-container::before {{
        content: '';
        position: absolute;
        top: -80px; right: -60px;
        width: 420px; height: 420px;
        background: radial-gradient(circle, rgba(0,85,149,0.28) 0%, transparent 65%);
        pointer-events: none;
    }}
    .hero-container::after {{
        content: '';
        position: absolute;
        bottom: -60px; left: -40px;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(0,59,101,0.18) 0%, transparent 70%);
        pointer-events: none;
    }}

    /* GRADIENT TEXT */
    .gradient-text {{
        background: linear-gradient(125deg, {brand_blue} 0%, {text_secondary} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* SECTION BADGE */
    .section-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, {brand_blue} 0%, {dark_navy} 100%);
        color: #fff;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        padding: 5px 16px;
        border-radius: 100px;
        margin-bottom: 18px;
        font-family: 'Space Grotesk', sans-serif;
    }}

    /* METRIC CARD */
    .metric-card {{
        background: linear-gradient(145deg, {surface_card} 0%, {surface_base} 100%);
        border: 1px solid {ghost_border};
        border-radius: 16px;
        padding: 28px 20px;
        text-align: center;
        transition: transform 0.32s cubic-bezier(0.34,1.56,0.64,1), border-color 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }}
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, {brand_blue}, {accent_blue});
    }}
    .metric-card:hover {{
        transform: translateY(-7px);
        border-color: {brand_blue};
        box-shadow: {card_shadow};
    }}
    .metric-number {{
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        color: {brand_blue};
        line-height: 1;
        letter-spacing: -0.04em;
    }}
    .metric-label {{
        color: {text_secondary};
        font-size: 10px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-top: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }}

    /* FEATURE CARD */
    .feature-card {{
        background: {surface_card};
        border: 1px solid {ghost_border};
        border-radius: 14px;
        padding: 28px 24px;
        transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
        position: relative;
    }}
    .feature-card:hover {{
        background: {surface_overlay};
        border-color: {brand_blue};
        transform: translateY(-5px);
        box-shadow: {card_shadow};
    }}
    .feature-icon {{ font-size: 2rem; margin-bottom: 12px; display: block; }}
    .feature-title {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: {text_primary} !important;
        margin-bottom: 8px !important;
        letter-spacing: -0.01em !important;
    }}
    .feature-desc {{
        color: {text_secondary};
        font-size: 0.875rem;
        line-height: 1.65;
        font-family: 'Inter', sans-serif;
    }}

    /* DATA MODULE */
    .module {{
        background: {surface_card};
        border: 1px solid {ghost_border};
        border-left: 3px solid transparent;
        border-radius: 12px;
        padding: 26px 24px;
        margin-bottom: 14px;
        transition: all 0.28s ease;
    }}
    .module:hover {{
        border-left-color: {brand_blue};
        transform: translateX(5px);
        background: {surface_overlay};
        box-shadow: {card_shadow};
    }}

    /* STAT NUMBER */
    .stat {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: {brand_blue};
        line-height: 1;
        letter-spacing: -0.04em;
    }}

    /* TOKEN / CHIP */
    .token {{
        display: inline-flex;
        align-items: center;
        padding: 5px 13px;
        background: rgba(0,85,149,0.12);
        color: {text_secondary};
        border: 1px solid {ghost_border};
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        border-radius: 100px;
        margin-right: 8px;
        margin-bottom: 6px;
        font-weight: 600;
        font-family: 'Space Grotesk', sans-serif;
    }}

    /* GLOW DIVIDER */
    .glow-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, {brand_blue} 50%, transparent 100%);
        margin: 36px 0;
        opacity: 0.45;
    }}

    /* HERO METRIC (Simulator) */
    .hero-metric {{
        font-family: 'Outfit', sans-serif;
        font-size: 5.5rem;
        font-weight: 900;
        color: {brand_blue};
        line-height: 0.9;
        letter-spacing: -0.05em;
    }}
    .hero-label {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        color: {text_secondary};
        font-weight: 700;
    }}

    /* BUTTONS */
    .stButton > button {{
        background: linear-gradient(135deg, {brand_blue} 0%, {dark_navy} 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        padding: 11px 28px !important;
        letter-spacing: 0.08em !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 18px rgba(0,85,149,0.38) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(0,85,149,0.55) !important;
    }}

    /* INPUTS */
    .stSelectbox [data-baseweb="select"] > div {{
        background: {surface_card} !important;
        border: 1px solid {ghost_border} !important;
        border-radius: 8px !important;
        color: {text_primary} !important;
    }}
    .stSelectbox label, .stSlider label,
    .stColorPicker label, .stFileUploader label,
    .stMultiSelect label {{
        color: {text_secondary} !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 10px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }}

    /* FORMATION BADGE */
    .formation-badge {{
        background: {surface_card};
        border: 1px solid {ghost_border};
        border-top: 2px solid {brand_blue};
        border-radius: 12px;
        padding: 22px 16px;
        text-align: center;
        transition: all 0.28s ease;
    }}
    .formation-badge:hover {{
        transform: translateY(-4px);
        border-top-color: {accent_blue};
        box-shadow: {card_shadow};
    }}
    .formation-badge .title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.7rem;
        font-weight: 900;
        color: {text_primary};
        letter-spacing: -0.03em;
    }}
    .formation-badge .subtitle {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 9px;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: {text_secondary};
        margin: 4px 0;
    }}

    /* CARD GRID CONTAINER */
    .card-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 16px;
    }}

    /* CHAT */
    [data-testid="stChatMessage"] {{
        background: {surface_card} !important;
        border: 1px solid {ghost_border} !important;
        border-radius: 12px !important;
    }}

    /* INVESTOR CALLOUT */
    .investor-block {{
        background: {surface_card};
        border: 1px solid {ghost_border};
        border-left: 3px solid {brand_blue};
        border-radius: 16px;
        padding: 36px 40px;
    }}

    /* MARKDOWN HORIZONTAL RULE */
    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, {ghost_border}, transparent) !important;
        margin: 32px 0 !important;
    }}

    /* MAIN HEADER LOGO */
    .logo-area [data-testid="stImage"] img {{
        filter: {logo_filter} drop-shadow(0 4px 28px rgba(0,85,149,0.50));
        background: {logo_bg};
        padding: {logo_padding};
        display: block;
        margin: 0 auto;
        transition: filter 0.3s ease;
    }}

    /* SIDEBAR LOGO */
    .sidebar-logo [data-testid="stImage"] img {{
        filter: {logo_filter};
        background: transparent;
        padding: 0;
        display: block;
        margin: 0 auto;
    }}

    /* FOOTER LOGO — fondo blanco pequeño */
    .footer-logo [data-testid="stImage"] img {{
        background: rgba(255,255,255,0.88);
        border-radius: 8px;
        padding: 6px 14px;
        filter: drop-shadow(0 2px 10px rgba(0,85,149,0.28));
    }}

    /* ── SIDEBAR PREMIUM OVERRIDES ───────────────────────────── */

    /* Quitar padding extra del bloque de sidebar */
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0 !important;
    }}

    /* Nav items: fuente y transición suave */
    [data-testid="stSidebar"] nav a {{
        transition: background 0.2s ease, color 0.2s ease,
                    box-shadow 0.2s ease !important;
    }}

    /* Hover state con borde izquierdo azul sutil */
    [data-testid="stSidebar"] nav a:hover {{
        border-left: 2px solid {brand_blue} !important;
        padding-left: 14px !important;
    }}

    /* Íconos del menú: tamaño y alineación */
    [data-testid="stSidebar"] nav a svg,
    [data-testid="stSidebar"] nav a i {{
        opacity: 0.85;
        transition: opacity 0.2s ease;
    }}
    [data-testid="stSidebar"] nav a:hover svg,
    [data-testid="stSidebar"] nav a:hover i {{
        opacity: 1;
    }}

    /* Separador decorativo sobre la firma */
    [data-testid="stSidebar"] hr {{
        border-color: {ghost_border} !important;
    }}
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
    brand_palette = ["#005595", "#1a6aaa", "#2d7fbf", "#3a8fd4", "#4da0e0",
                     "#003B65", "#004f88", "#00639b", "#0077ae", "#008bc1"]
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#0d1f35")
    ax.set_facecolor("#0d1f35")
    bars = ax.barh(xg_jugadores.index[::-1], xg_jugadores.values[::-1],
                   color=brand_palette[:len(xg_jugadores)], height=0.6)
    for bar, val in zip(bars, xg_jugadores.values[::-1]):
        ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", color="#B3B2B3",
                fontsize=10, fontweight="bold")
    ax.set_xlabel("xG acumulado", color="#B3B2B3", fontsize=11)
    ax.set_title("Top 10 Jugadores por xG", color="#FFFFFF",
                 fontsize=14, fontweight="bold", pad=16)
    ax.tick_params(colors="#B3B2B3", labelsize=10)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.xaxis.grid(True, color=(0, 0.333, 0.584, 0.2), linewidth=0.8)
    ax.set_axisbelow(True)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

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
# SCOUT REPORT — RADAR
# =========================
def calcular_metricas_jugador(df, jugador):
    """Calcula 6 métricas normalizadas (0-100) para el radar."""
    metricas = {
        "xG":           0.0,
        "Tiros":        0.0,
        "Pases":        0.0,
        "Presión":      0.0,
        "Duelos":       0.0,
        "Regates":      0.0,
    }
    df_j = df[df['player'] == jugador]
    if df_j.empty:
        return metricas

    if 'type_name' in df.columns:
        metricas["Tiros"]   = (df_j['type_name'] == 'Shot').sum()
        metricas["Pases"]   = (df_j['type_name'] == 'Pass').sum()
        metricas["Presión"] = (df_j['type_name'] == 'Pressure').sum()
        metricas["Duelos"]  = (df_j['type_name'] == 'Duel').sum()
        metricas["Regates"] = (df_j['type_name'].isin(['Dribble', 'Carry'])).sum()

    if 'xg' in df_j.columns:
        metricas["xG"] = df_j['xg'].sum() if df_j['xg'].notna().any() else 0.0

    # Normalizar respecto al máximo de todos los jugadores del dataset
    todos = {}
    for jugador_i in df['player'].dropna().unique():
        df_i = df[df['player'] == jugador_i]
        todos[jugador_i] = {
            "xG":      df_i['xg'].sum() if 'xg' in df_i.columns and df_i['xg'].notna().any() else 0,
            "Tiros":   (df_i['type_name'] == 'Shot').sum()    if 'type_name' in df_i.columns else 0,
            "Pases":   (df_i['type_name'] == 'Pass').sum()    if 'type_name' in df_i.columns else 0,
            "Presión": (df_i['type_name'] == 'Pressure').sum() if 'type_name' in df_i.columns else 0,
            "Duelos":  (df_i['type_name'] == 'Duel').sum()    if 'type_name' in df_i.columns else 0,
            "Regates": (df_i['type_name'].isin(['Dribble','Carry'])).sum() if 'type_name' in df_i.columns else 0,
        }

    normalizadas = {}
    for k, v in metricas.items():
        maximo = max((todos[j][k] for j in todos), default=1)
        normalizadas[k] = round(100 * v / maximo, 1) if maximo > 0 else 0.0
    return normalizadas


def graficar_radar(metricas: dict, jugador: str):
    labels  = list(metricas.keys())
    valores = list(metricas.values())
    N = len(labels)
    angulos = [n / float(N) * 2 * np.pi for n in range(N)]
    angulos += angulos[:1]
    valores += valores[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0d1f35")
    ax.set_facecolor("#0d1f35")

    # Grid y spines
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.spines['polar'].set_visible(False)
    ax.yaxis.set_tick_params(labelsize=0)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels([])
    ax.yaxis.grid(True, color=(0, 0.333, 0.584, 0.18), linewidth=0.7)
    ax.xaxis.grid(True, color=(0, 0.333, 0.584, 0.25), linewidth=0.8)

    # Etiquetas de categorías
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(labels, color="#B3B2B3", fontsize=11,
                       fontfamily="sans-serif", fontweight="600")

    # Área rellena
    ax.plot(angulos, valores, color="#005595", linewidth=2.2, linestyle="solid")
    ax.fill(angulos, valores, color="#005595", alpha=0.30)

    # Puntos en cada vértice
    ax.scatter(angulos[:-1], valores[:-1], color="#3a8fd4", s=55, zorder=5)

    # Valores sobre cada punto
    for ang, val, lbl in zip(angulos[:-1], valores[:-1], labels):
        ax.text(ang, val + 8, f"{val:.0f}", ha="center", va="center",
                color="#FFFFFF", fontsize=9, fontweight="bold")

    ax.set_title(jugador, color="#FFFFFF", fontsize=13,
                 fontweight="900", pad=22, fontfamily="sans-serif")

    plt.tight_layout()
    return fig


# =========================
# MAIN
# =========================

# Pantalla de carga branded
_loading_placeholder = st.empty()
_loading_placeholder.markdown(f"""
<div style='position:fixed; inset:0; z-index:99999; display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            background:linear-gradient(135deg, #040404 0%, #0a1628 100%);'>
    <img src="data:image/png;base64,{__import__('base64').b64encode(open('assets/Tactic_AI_logo-removebg-preview (1).png','rb').read()).decode()}"
         style="width:220px; filter:brightness(0) invert(1); margin-bottom:40px;" />
    <div style='font-family:Space Grotesk,sans-serif; font-size:11px; letter-spacing:0.3em;
                text-transform:uppercase; color:#B3B2B3; margin-bottom:28px;'>
        Cargando inteligencia táctica...
    </div>
    <div style='width:180px; height:2px; background:rgba(0,85,149,0.2); border-radius:2px; overflow:hidden;'>
        <div style='width:60%; height:100%;
                    background:linear-gradient(90deg,#003B65,#005595,#3a8fd4);
                    animation:slide 1.4s ease-in-out infinite;'></div>
    </div>
    <style>
        @keyframes slide {{
            0%   {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(280%); }}
        }}
    </style>
</div>
""", unsafe_allow_html=True)

# Cargar competiciones
comps = cargar_competiciones()
_loading_placeholder.empty()  # Oculta la pantalla de carga al terminar

# Lista ligas disponibles
ligas = comps['competition_name'].unique().tolist() if not comps.empty else ["(No disponible)"]

# Cargar logos
logo = Image.open("assets/Tactic_AI_logo-removebg-preview (1).png")
logo_sidebar = Image.open("assets/Tactic_AI_logo-removebg-preview (1).png")

# Centrar logo principal con filtro blanco en dark mode
st.markdown('<div class="logo-area">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=340)
st.markdown('</div>', unsafe_allow_html=True)
# Menú lateral
with st.sidebar:
    # Logo en sidebar
    st.markdown('<div class="sidebar-logo" style="padding:16px 12px 4px;">', unsafe_allow_html=True)
    st.image(logo_sidebar, width=200)
    st.markdown('</div>', unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Análisis Rival", "Análisis Propio", "Scout Report", "Mapa de Calor", "Pizarra", "Comparativa", "Simulador", "Subir CSV", "Chat Tactisense AI"],
        icons=["house", "trophy", "shield", "person-lines-fill", "fire", "pencil", "graph-up", "play", "upload", "robot"],
        default_index=0,
        styles={
            "container": {
                "padding": "6px 8px !important",
                "background-color": "transparent",
            },
            "icon": {
                "color": "#3a8fd4",
                "font-size": "15px",
                "margin-right": "2px",
            },
            "nav-link": {
                "font-size": "13.5px",
                "font-family": "Space Grotesk, sans-serif",
                "font-weight": "500",
                "text-align": "left",
                "margin": "3px 0",
                "padding": "11px 18px",
                "border-radius": "10px",
                "color": "#B3B2B3",
                "letter-spacing": "0.02em",
                "--hover-color": "#143252",
                "transition": "all 0.2s ease",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #005595 0%, #003B65 100%)",
                "border-radius": "10px",
                "font-weight": "700",
                "color": "#FFFFFF",
                "box-shadow": "0 4px 16px rgba(0,85,149,0.45)",
            },
        }
    )

    # Firma al pie del sidebar
    st.markdown(f"""
    <div style='position:fixed; bottom:0; left:0; width:238px; padding:14px 20px;
                background:linear-gradient(0deg, {bg_color} 80%, transparent 100%);'>
        <div style='height:1px; background:linear-gradient(90deg,transparent,rgba(0,85,149,0.3),transparent);
                    margin-bottom:12px;'></div>
        <div style='display:flex; align-items:center; gap:8px;'>
            <div style='width:6px; height:6px; border-radius:50%; background:#005595;
                        box-shadow:0 0 8px rgba(0,85,149,0.8);'></div>
            <span style='font-family:Space Grotesk,sans-serif; font-size:10px;
                         letter-spacing:0.12em; text-transform:uppercase; color:{text_secondary};'>
                Tactisense AI
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    # ── HERO ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-container">
        <h1 style='font-size:3.6rem; font-weight:900; line-height:1.08;
                   margin-bottom:20px; color:{text_primary};
                   font-family:Outfit,sans-serif; letter-spacing:-0.04em;'>
            INTELIGENCIA<br>
            <span class="gradient-text">TÁCTICA TOTAL</span>
        </h1>
        <p style='font-size:1.05rem; color:{text_secondary}; max-width:640px;
                  line-height:1.78; margin-bottom:32px; font-family:Inter,sans-serif;'>
            La plataforma de análisis táctico de fútbol impulsada por IA que transforma
            datos históricos en ventaja competitiva real para entrenadores y cuerpos
            técnicos de cualquier nivel.
        </p>
        <div style='display:flex; gap:8px; flex-wrap:wrap;'>
            <span class="token">⚽ 20+ Ligas Globales</span>
            <span class="token">📊 StatsBomb Open Data</span>
            <span class="token">🤖 IA Táctica LLM</span>
            <span class="token">📡 Análisis en Tiempo Real</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ROW ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:32px;'>
        <div class="metric-card">
            <div class="metric-number">20+</div>
            <div class="metric-label">Ligas Analizadas</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">500K+</div>
            <div class="metric-label">Tiros Procesados</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">15K+</div>
            <div class="metric-label">Partidos en Base</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">9</div>
            <div class="metric-label">Módulos Tácticos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── FEATURE GRID ──────────────────────────────────────────────────
    st.markdown(f'<div class="section-badge">Funcionalidades</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:36px;'>
        <div class="feature-card">
            <span class="feature-icon">🛡️</span>
            <div class="feature-title">Análisis de Rival</div>
            <div class="feature-desc">xG por jugador, formaciones detectadas y patrones de presión del adversario con datos reales de partidos.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🔥</span>
            <div class="feature-title">Mapas de Calor</div>
            <div class="feature-desc">Visualización KDE de tiros y zonas de peligro sobre cancha oficial StatsBomb. Profundidad táctica visual.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">DT — Chat Táctico IA</div>
            <div class="feature-desc">Consulta formaciones, estrategias y análisis con nuestra IA especializada, potenciada por LLaMA 3.3-70B.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">✏️</span>
            <div class="feature-title">Pizarra Táctica</div>
            <div class="feature-desc">Canvas interactivo para posicionar jugadores, trazar rutas de desmarque y diseñar jugadas de estrategia.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Simulador xG</div>
            <div class="feature-desc">Probabilidad de victoria calculada con Expected Goals históricos acumulados. Decisiones respaldadas por datos.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <div class="feature-title">Recomendador Táctico</div>
            <div class="feature-desc">Sugerencias de formación adaptadas a las fortalezas propias y las debilidades detectadas en el rival.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── INVESTOR CALLOUT ──────────────────────────────────────────────
    st.markdown(f"""
    <div class="glow-divider"></div>
    <div class="investor-block">
        <div class="section-badge" style="margin-bottom:16px;">Visión del Producto</div>
        <h3 style='color:{text_primary}; font-size:1.45rem; margin-bottom:14px;
                   font-family:Outfit,sans-serif; font-weight:800; letter-spacing:-0.02em;'>
            El futuro del análisis táctico de fútbol
        </h3>
        <p style='color:{text_secondary}; font-size:0.93rem; line-height:1.82;
                  max-width:800px; font-family:Inter,sans-serif;'>
            Tactisense AI está construida sobre datos de calidad profesional (StatsBomb) e inteligencia
            artificial de última generación. Tactisense AI demuestra la viabilidad técnica de una plataforma
            <strong style="color:{text_primary};">SaaS escalable</strong> que puede servir desde academias
            juveniles hasta equipos de primer nivel, con un modelo de negocio B2B replicable a escala global.
        </p>
        <div style='display:flex; gap:10px; margin-top:22px; flex-wrap:wrap;'>
            <span class="token">B2B SaaS</span>
            <span class="token">Escalable</span>
            <span class="token">Mercado Global</span>
            <span class="token">IA + Datos</span>
            <span class="token">Ventaja Competitiva</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif selected == "Análisis Rival":
    st.markdown(f'<div class="section-badge">Inteligencia Táctica</div>', unsafe_allow_html=True)
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
                    st.markdown("### 🛡️ TACTICAL FORMATIONS")
                    cols = st.columns(len(top_formaciones))
                    for i, (formacion, count) in enumerate(top_formaciones.items()):
                        with cols[i]:
                            st.markdown(f"""
                                <div class="formation-badge">
                                    <div class="subtitle">DETECTED SET</div>
                                    <div class="title">{formacion}</div>
                                    <div class="subtitle">{count} MATCHES ANALYZED</div>
                                </div>
                            """, unsafe_allow_html=True)

            # Visualización top xG promedio por jugador -> TARJETAS EN MOSAICO
            shots = df_r[df_r['type_name'] == 'Shot']
            if not shots.empty and shots['xg'].notna().any():
                xg_prom = shots.groupby('player')['xg'].mean().sort_values(ascending=False).head(12)
                st.subheader("Top xG promedio por jugador")
                st.markdown("<div class='card-container'>", unsafe_allow_html=True)
                for jugador, xg_val in xg_prom.items():
                    st.markdown(f"""
                        <div class="module">
                            <h3>{jugador}</h3>
                            <div style="display:flex; align-items:flex-end; gap:8px;">
                                <div class="stat">{xg_val:.2f}</div>
                                <div class="label" style="margin-bottom:8px;">Expected Goals (xG)</div>
                            </div>
                            <div style="margin-top:12px;">
                                <span class="token">Elite Signal</span>
                                <span class="token">High Impact</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No se detectaron tiros con xG para mostrar.")
    else:
        st.warning("No hay partidos cargados para la liga/equipo seleccionado.")

elif selected == "Análisis Propio":
    st.markdown(f'<div class="section-badge">Tu Rendimiento</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="section-badge">Análisis Espacial</div>', unsafe_allow_html=True)
    st.header("Mapa de Calor de Tiros")
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
                pitch = Pitch(pitch_type='statsbomb', pitch_color=bg_color, line_color=text_secondary)
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
    st.markdown(f'<div class="section-badge">Diseño Táctico</div>', unsafe_allow_html=True)
    st.header("Pizarra Táctica Interactiva")

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
    st.markdown(f'<div class="section-badge">Head to Head</div>', unsafe_allow_html=True)
    st.header("Comparativa de Equipos")
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

        color_prop = accent_blue
        color_rival = brand_blue

        st.markdown(f"""
        <div style='display:flex; gap:2rem;'>
            <div style='flex:1; background:{surface_card}; padding:25px; border-radius:15px; color:{text_primary}; box-shadow: {card_shadow}; border-top: 4px solid {color_prop};'>
                <h3 style='text-align:center; padding-bottom: 6px;'>{equipo_prop}</h3>
                <p style='font-size:24px; margin:15px 0; font-family:Space Grotesk;'><strong style='color:{color_prop};'>{tiros_p}</strong> <span style='font-size:16px; color:{text_secondary};'>Tiros</span></p>
                <p style='font-size:24px; margin:15px 0; font-family:Space Grotesk;'><strong style='color:{color_prop};'>{tarjetas_p}</strong> <span style='font-size:16px; color:{text_secondary};'>Tarjetas</span></p>
            </div>
            <div style='flex:1; background:{surface_card}; padding:25px; border-radius:15px; color:{text_primary}; box-shadow: {card_shadow}; border-top: 4px solid {color_rival};'>
                <h3 style='text-align:center; padding-bottom: 6px;'>{equipo_rival}</h3>
                <p style='font-size:24px; margin:15px 0; font-family:Space Grotesk;'><strong style='color:{color_rival};'>{tiros_r}</strong> <span style='font-size:16px; color:{text_secondary};'>Tiros</span></p>
                <p style='font-size:24px; margin:15px 0; font-family:Space Grotesk;'><strong style='color:{color_rival};'>{tarjetas_r}</strong> <span style='font-size:16px; color:{text_secondary};'>Tarjetas</span></p>
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
    st.markdown(f'<div class="section-badge">Simulation Engine v1.0</div>', unsafe_allow_html=True)
    st.header("Simulador de Probabilidad")
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

    # Elite Simulation: Asymmetry & Scale
    st.markdown(f"""
        <div style="margin-top:60px; border-left: 2px solid {brand_blue}; padding-left: 40px;">
            <div class="hero-label">Tactisense Simulation Engine v.1.0</div>
            <div class="hero-metric">{prob}<span style="font-size:40px; vertical-align:top; margin-left:10px;">%</span></div>
            <div style="font-family:'Space Grotesk'; font-size:32px; color:{text_primary}; font-weight:300;">
                PROBABILIDAD DE VICTORIA PARA <span style="font-weight:700; color:{accent_blue};">{equipo_prop.upper()}</span>
            </div>
            <div style="background:{surface_card}; width:100%; height:4px; margin-top:30px; position:relative; overflow:hidden;">
                <div style="background:{accent_blue}; width:{prob}%; height:100%; box-shadow: 0 0 15px {accent_blue};"></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:12px;">
                <span class="label">Historical xG: {xg_p:.2f}</span>
                <span class="label">Rival Risk: {xg_r:.2f}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif selected == "Scout Report":
    st.markdown(f'<div class="section-badge">Análisis Individual</div>', unsafe_allow_html=True)
    st.header("Scout Report — Radar de Jugador")

    if not matches.empty and equipo_prop and equipo_prop != "(sin datos)":
        df_scout = obtener_datos_eventos_por_nombre(equipo_prop, matches, max_partidos=4)

        if df_scout.empty:
            st.warning("No se encontraron eventos para generar el Scout Report.")
        else:
            jugadores_disp = sorted(df_scout['player'].dropna().unique().tolist())

            col_sel, col_info = st.columns([1, 2])
            with col_sel:
                jugador_sel = st.selectbox("Selecciona un jugador", jugadores_disp)

            if jugador_sel:
                metricas = calcular_metricas_jugador(df_scout, jugador_sel)

                col_radar, col_stats = st.columns([1, 1])

                with col_radar:
                    fig = graficar_radar(metricas, jugador_sel)
                    st.pyplot(fig)
                    plt.close(fig)

                with col_stats:
                    st.markdown(f"""
                    <div style='padding:8px 0 20px;'>
                        <div class='section-badge'>Métricas del jugador</div>
                    </div>
                    """, unsafe_allow_html=True)

                    for metrica, valor in metricas.items():
                        color_bar = "#005595" if valor >= 60 else "#003B65" if valor >= 35 else "#1a2a3a"
                        st.markdown(f"""
                        <div style='margin-bottom:14px;'>
                            <div style='display:flex; justify-content:space-between;
                                        margin-bottom:5px;'>
                                <span style='font-family:Space Grotesk,sans-serif; font-size:12px;
                                             font-weight:600; color:#B3B2B3; letter-spacing:0.08em;
                                             text-transform:uppercase;'>{metrica}</span>
                                <span style='font-family:Outfit,sans-serif; font-size:15px;
                                             font-weight:900; color:#FFFFFF;'>{valor:.0f}<span
                                      style='font-size:10px; color:#B3B2B3;'>/100</span></span>
                            </div>
                            <div style='height:5px; background:rgba(0,85,149,0.15);
                                        border-radius:3px; overflow:hidden;'>
                                <div style='width:{valor}%; height:100%; background:{color_bar};
                                            border-radius:3px; transition:width 0.5s ease;'></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Percentil global
                    percentil_global = round(sum(metricas.values()) / len(metricas), 1)
                    nivel = "Élite" if percentil_global >= 70 else "Alto" if percentil_global >= 45 else "Desarrollo"
                    color_nivel = "#2a9d8f" if percentil_global >= 70 else "#005595" if percentil_global >= 45 else "#B3B2B3"

                    st.markdown(f"""
                    <div class='module' style='margin-top:20px; text-align:center;'>
                        <div style='font-family:Space Grotesk,sans-serif; font-size:10px;
                                    letter-spacing:0.2em; text-transform:uppercase;
                                    color:#B3B2B3; margin-bottom:8px;'>Rendimiento Global</div>
                        <div style='font-family:Outfit,sans-serif; font-size:3rem;
                                    font-weight:900; color:{color_nivel};
                                    line-height:1; letter-spacing:-0.04em;'>{percentil_global:.0f}</div>
                        <div style='font-family:Space Grotesk,sans-serif; font-size:12px;
                                    color:{color_nivel}; font-weight:700;
                                    margin-top:6px;'>{nivel}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("Selecciona una liga y tu equipo para generar el Scout Report.")

elif selected == "Subir CSV":
    st.markdown(f'<div class="section-badge">Datos Propios</div>', unsafe_allow_html=True)
    st.header("Cargar CSV Propio")
    archivo = st.file_uploader("Selecciona CSV con eventos (formato StatsBomb recomendado)", type=["csv"])
    if archivo:
        df_csv = pd.read_csv(archivo)
        st.dataframe(df_csv.head())
        exportar_datos(df_csv, nombre_archivo="datos_subidos.csv")

elif selected == "Chat Tactisense AI":
    st.markdown(f'<div class="section-badge">IA Especializada · LLaMA 3.3-70B</div>', unsafe_allow_html=True)
    st.header("DT — Tu Asistente Táctico")
    
    import os
    from groq import Groq, AuthenticationError, BadRequestError, APIConnectionError, RateLimitError

    # Inicializa historial para Groq (incluye un mensaje system persistente)
    if "messages_groq" not in st.session_state:
        st.session_state.messages_groq = [
            {"role": "system", "content": "Eres un asistente experto en táctica de fútbol llamado DT y formas parte de la plataforma Tactisense AI. Tu misión es ayudar a entrenadores y analistas a tomar decisiones tácticas dentro de Tactisense AI. Siempre responde con claridad y utiliza breves bullets cuando convenga. Solo proporciona información relacionada con tácticas, alineaciones, análisis de rivales, estrategias de juego o rendimiento de jugadores.Información sobre Tactisense AI:Es una herramienta tecnológica enfocada en el análisis táctico de fútbol mediante datos y estadísticas. Su enfoque principal es ayudar a entrenadores y analistas a tomar decisiones estratégicas basadas en datos históricos y patrones de juego. Está en una etapa temprana de desarrollo, con funcionalidades como análisis de rivales, sugerencias tácticas y visualización de alineaciones, pero representa la visión de un sistema completo que escalará para ofrecer predicciones y recomendaciones avanzadas.Como negocio, Tactisense AI apunta a ser escalable ofreciendo servicios a equipos profesionales y formativos, y expandiendo funcionalidades con IA avanzada en el futuro.Instrucciones para tus respuestas:Si te preguntan sobre Tactisense AI o tu rol, explica que eres una inteligencia artificial de Tactisense AI diseñada para apoyar en decisiones tácticas de fútbol.Si te preguntan sobre temas no relacionados con fútbol, responde de manera cortés indicando que solo puedes ayudar en tácticas de fútbol.Responde en el idioma en el que se te haga la pregunta, adaptando tus bullets y explicaciones a ese idioma."}
        ]

    # Renderiza historial en formato chat (sin mostrar el system)
    for m in st.session_state.messages_groq:
        if m["role"] in ("user", "assistant"):
            with st.chat_message("user" if m["role"] == "user" else "assistant"):
                st.markdown(m["content"])

    # Entrada tipo chat (estilo ChatGPT)
    prompt = st.chat_input("Escribe tu pregunta táctica (p. ej., ¿Cómo defender un 4-3-3?)")

    if prompt:
        # Muestra el mensaje del usuario en el chat e insértalo al historial
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages_groq.append({"role": "user", "content": prompt})

        # Cliente Groq
        api_key = os.getenv("GROQ_API_KEY") or getattr(st.secrets, "GROQ_API_KEY", None)
        if not api_key:
            with st.chat_message("assistant"):
                st.error("Falta GROQ_API_KEY en tus Secrets o variables de entorno.")
        else:
            client = Groq(api_key=api_key)
            try:
                # 👇 Modelo correcto y estable
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages_groq,
                    temperature=0.2,
                )
                answer = resp.choices[0].message.content

                # Muestra respuesta y guarda en historial
                with st.chat_message("assistant"):
                    st.markdown(answer)
                st.session_state.messages_groq.append({"role": "assistant", "content": answer})

            except (AuthenticationError, RateLimitError, APIConnectionError, BadRequestError) as e:
                with st.chat_message("assistant"):
                    st.error(f"Error de Groq: {e}")
            except Exception as e:
                with st.chat_message("assistant"):
                    st.error(f"Error inesperado: {e}")




from PIL import Image
import streamlit as st

# Footer
st.markdown(f"""
<div style='margin-top:60px; padding:28px 0 16px; border-top:1px solid {ghost_border};
            display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;'>
    <div>
        <span style='font-family:Outfit,sans-serif; font-size:1rem; font-weight:800;
                     color:{text_primary}; letter-spacing:-0.02em;'>Tactisense AI</span>
        <span style='color:{text_secondary}; font-size:0.8rem; margin-left:12px;
                     font-family:Inter,sans-serif;'>Pedro Rafael Merlo Campos</span>
    </div>
    <div style='display:flex; align-items:center; gap:12px;'>
        <span style='color:{text_secondary}; font-size:0.75rem; font-family:Space Grotesk,sans-serif;
                     letter-spacing:0.08em; text-transform:uppercase;'>Powered by</span>
""", unsafe_allow_html=True)

st.markdown('<div class="footer-logo">', unsafe_allow_html=True)
logo_sb = Image.open("assets/StatsBomb logo.png")
st.image(logo_sb, width=110)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)
