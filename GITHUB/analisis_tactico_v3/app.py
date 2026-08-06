import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import plotly.graph_objects as go
import json
from pathlib import Path
import matplotlib.patches as mpatches

st.set_page_config(
    page_title="Análisis Táctico · Fútbol de Salón",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BG      = "#F7F8FA"
SURFACE = "#FFFFFF"
SIDEBAR = "#1A1D2E"
ACCENT  = "#E8420A"
TEXT    = "#0F1117"
MUTED   = "#6B7280"
BORDER  = "#E5E7EB"
FIELD   = "#3D6B4F"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #F7F8FA; }
[data-testid="stSidebar"] { background-color: #1A1D2E !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #E5E7EB !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #252840 !important;
    border-color: #4B5563 !important;
    color: white !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * { color: white !important; }
[data-testid="stSidebar"] svg { stroke: #9CA3AF; }
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-bottom: 2px solid #E5E7EB;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: #6B7280;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 12px 24px;
    border-radius: 0;
    border-bottom: 3px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #E8420A !important;
    border-bottom: 3px solid #E8420A !important;
    font-weight: 700;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #6B7280;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    margin: 0;
    font-family: 'DM Mono', monospace;
}
.kpi-sub {
    font-size: 0.65rem;
    color: #6B7280;
    margin-top: 4px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.match-header {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.score {
    font-size: 3.8rem;
    font-weight: 800;
    color: #0F1117;
    font-family: 'DM Mono', monospace;
    letter-spacing: -2px;
    text-align: center;
}
.match-meta { font-size: 0.8rem; color: #6B7280; margin-top: 6px; text-align: center; }
.team-name  { font-size: 1.1rem; font-weight: 700; margin-top: 8px; }
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0F1117;
    letter-spacing: -0.02em;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #E5E7EB;
}
.rot-pill {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 8px 14px;
    margin: 4px 0;
    font-size: 0.85rem;
    color: #0F1117;
}
.sidebar-brand {
    padding: 8px 0 20px 0;
    text-align: center;
    border-bottom: 1px solid #2d3150;
    margin-bottom: 20px;
}
.sidebar-brand-title { font-size: 0.95rem; font-weight: 700; color: white; margin-top: 10px; }
.sidebar-brand-sub   { font-size: 0.7rem; color: #9CA3AF; margin-top: 2px; }
.sidebar-info {
    background: #252840;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 16px;
    font-size: 0.8rem;
    color: #D1D5DB;
    line-height: 1.7;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ruta absoluta para compatibilidad con Streamlit Cloud
BASE = Path(__file__).parent / "datos"

# ── cancha desde JSON ─────────────────────────────────────
CANCHA_JSON = None
try:
    with open(Path(__file__).parent / "cancha_futsal.json", encoding="utf-8") as _f:
        CANCHA_JSON = json.load(_f)["elementos"]
except Exception:
    pass

# ── helpers ───────────────────────────────────────────────
def leer_json(ruta):
    """Lee JSON tolerando BOM y distintos encodings."""
    ruta = Path(ruta)
    raw = ruta.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return json.loads(raw.decode("utf-8"))

@st.cache_data
def cargar_equipos():
    return leer_json(BASE / "equipos.json")["equipos"]

@st.cache_data
def cargar_equipo(equipo_id):
    return leer_json(BASE / equipo_id / "equipo.json")

@st.cache_data
def cargar_partidos(equipo_id):
    carpeta = BASE / equipo_id / "partidos"
    partidos = []
    for p in sorted(carpeta.iterdir(), reverse=True):
        if p.is_dir() and (p / "partido.json").exists():
            data = leer_json(p / "partido.json")
            data["_carpeta"] = str(p)
            partidos.append(data)
    return partidos

@st.cache_data
def cargar_csv(ruta):
    return pd.read_csv(ruta)

@st.cache_data
def cargar_json_app(ruta):
    return leer_json(ruta)

def preparar_df(df):
    conteo = df.groupby(["segmento", "id"])["frame"].count()
    ids_validos = conteo[conteo > 15].index.get_level_values("id").unique()
    df = df[df["id"].isin(ids_validos)].copy()
    equipo_por_id = (df.groupby(["id", "equipo"])
                       .size().reset_index(name="n")
                       .sort_values("n", ascending=False)
                       .drop_duplicates("id")
                       .set_index("id")["equipo"])
    df["equipo_final"] = df["id"].map(equipo_por_id)
    return df

def dibujar_cancha(ax, fontsize=7, alpha_lineas=0.45):
    """Dibuja fondo verde + cancha desde JSON + grilla táctica."""
    ax.set_facecolor(FIELD)

    if CANCHA_JSON:
        for el in CANCHA_JSON:
            lw = el.get("lw", 1.5)
            c  = "white"
            if el["tipo"] == "rectangulo":
                ax.add_patch(mpatches.Rectangle(
                    (el["x"], el["y"]), el["w"], el["h"],
                    linewidth=lw, edgecolor=c, facecolor="none",
                    alpha=alpha_lineas, zorder=1))
            elif el["tipo"] == "linea":
                ax.plot([el["x1"], el["x2"]], [el["y1"], el["y2"]],
                        color=c, lw=lw, alpha=alpha_lineas, zorder=1)
            elif el["tipo"] == "elipse":
                ax.add_patch(mpatches.Ellipse(
                    (el["cx"], el["cy"]), el["rx"]*2, el["ry"]*2,
                    linewidth=lw, edgecolor=c, facecolor="none",
                    alpha=alpha_lineas, zorder=1))
            elif el["tipo"] == "arco":
                ax.add_patch(mpatches.Arc(
                    (el["cx"], el["cy"]), el["rx"]*2, el["ry"]*2,
                    angle=0, theta1=el["angulo_ini"], theta2=el["angulo_fin"],
                    color=c, lw=lw, alpha=alpha_lineas, zorder=1))
            elif el["tipo"] == "punto":
                ax.add_patch(mpatches.Circle(
                    (el["x"], el["y"]), el["radio"],
                    color=c, alpha=alpha_lineas, zorder=1))
            elif el["tipo"] == "tick":
                if el["dir"] == "v":
                    ax.plot([el["x"], el["x"]], [el["y"], el["y"]+el["largo"]],
                            color=c, lw=lw, alpha=alpha_lineas, zorder=1)
                else:
                    ax.plot([el["x"], el["x"]+el["largo"]], [el["y"], el["y"]],
                            color=c, lw=lw, alpha=alpha_lineas, zorder=1)

    for xv in [0.33, 0.66]:
        ax.axvline(x=xv, color="white", lw=1, linestyle="--", alpha=0.5, zorder=3)
    for yh in [0.33, 0.66]:
        ax.axhline(y=yh, color="white", lw=0.7, linestyle="--", alpha=0.4, zorder=3)
    for txt, x in [("DEF", 0.16), ("GEST", 0.50), ("DEFI", 0.84)]:
        ax.text(x, 0.02, txt, color="white", fontsize=fontsize,
                ha="center", transform=ax.transAxes, alpha=0.85, zorder=4)
    for txt, y in [("IZQ", 0.83), ("CEN", 0.50), ("DER", 0.17)]:
        ax.text(0.01, y, txt, color="white", fontsize=fontsize - 1,
                va="center", transform=ax.transAxes, alpha=0.85, zorder=4)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])

def plotly_base():
    return dict(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", color=TEXT),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER),
    )

# ════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    logo_path = Path(__file__).parent / "logo_circular.png"
    st.markdown('<div class="sidebar-brand">', unsafe_allow_html=True)
    if logo_path.exists():
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.image(str(logo_path), width=90)
    st.markdown(
        '<div class="sidebar-brand-title">Análisis Táctico</div>'
        '<div class="sidebar-brand-sub">Fútbol de Salón · IA</div>'
        '</div>',
        unsafe_allow_html=True
    )

    equipos        = cargar_equipos()
    equipo_nombres = {e["id"]: e["nombre"] for e in equipos}
    equipo_sel_id  = st.selectbox(
        "Equipo",
        options=[e["id"] for e in equipos],
        format_func=lambda x: equipo_nombres[x]
    )

    equipo_info = cargar_equipo(equipo_sel_id)
    COLOR_LOCAL = equipo_info["color_principal"]
    COLOR_L     = COLOR_LOCAL if COLOR_LOCAL != "#e8e8e8" else TEXT

    partidos = cargar_partidos(equipo_sel_id)
    if not partidos:
        st.warning("No hay partidos cargados.")
        st.stop()

    partido_opciones = {
        p["id"]: f"{p['fecha']}  ·  vs {p['rival']}  ({p['resultado_local']}-{p['resultado_visitante']})"
        for p in partidos
    }
    partido_sel_id = st.selectbox(
        "Partido",
        options=list(partido_opciones.keys()),
        format_func=lambda x: partido_opciones[x]
    )

    partido     = next(p for p in partidos if p["id"] == partido_sel_id)
    carpeta     = Path(partido["_carpeta"])
    COLOR_RIVAL = partido["rival_color"]

    st.markdown(
        f'<div class="sidebar-info">'
        f'<b style="color:white">{equipo_info["nombre"]}</b> vs '
        f'<b style="color:{COLOR_RIVAL}">{partido["rival"]}</b><br>'
        f'📅 {partido["fecha"]}<br>'
        f'🏆 {partido["torneo"]}<br>'
        f'📍 {partido["sede"]}'
        f'</div>',
        unsafe_allow_html=True
    )

# ════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════
st.markdown('<div class="match-header">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    logo_local = BASE / equipo_sel_id / equipo_info["escudo"]
    ci, ct = st.columns([1, 2])
    with ci:
        if logo_local.exists():
            st.image(str(logo_local), width=80)
    with ct:
        st.markdown(
            f'<div class="team-name" style="color:{COLOR_L}">{equipo_info["nombre"]}</div>'
            f'<div class="match-meta">Local</div>',
            unsafe_allow_html=True
        )

with col2:
    st.markdown(
        f'<div class="score">{partido["resultado_local"]} – {partido["resultado_visitante"]}</div>'
        f'<div class="match-meta">{partido["torneo"]}<br>{partido["sede"]} · {partido["fecha"]}</div>',
        unsafe_allow_html=True
    )

with col3:
    logo_rival = carpeta / partido["rival_escudo"]
    ct2, ci2 = st.columns([2, 1])
    with ct2:
        st.markdown(
            f'<div class="team-name" style="color:{COLOR_RIVAL};text-align:right">{partido["rival"]}</div>'
            f'<div class="match-meta" style="text-align:right">Visitante</div>',
            unsafe_allow_html=True
        )
    with ci2:
        if logo_rival.exists():
            st.image(str(logo_rival), width=80)

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# DATOS
# ════════════════════════════════════════════════════════
csv_path  = carpeta / partido["csv"]
json_path = carpeta / partido["json_app"]
df_raw    = cargar_csv(str(csv_path))
df        = preparar_df(df_raw)

equipos_csv      = df["equipo_final"].dropna().unique()
equipo_local_csv = equipos_csv[0] if len(equipos_csv) > 0 else "local"
equipo_rival_csv = equipos_csv[1] if len(equipos_csv) > 1 else "visitante"

tiene_json = json_path.exists()
if tiene_json:
    datos_app = cargar_json_app(str(json_path))
    jugadores = {j["id"]: f"{j['nombre']} {j['apellido']}"
                 for j in datos_app["jugadores"]}
    dorsales  = {j["id"]: j["dorsal"] for j in datos_app["jugadores"]}
    inc       = datos_app["incidencias"]

# ════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Resumen", "🗺️  Táctico", "📍  Partido completo", "👤  Jugadores"
])

# ─────────────────────────────────────────────────────────
# TAB 1: RESUMEN
# ─────────────────────────────────────────────────────────
with tab1:
    if not tiene_json:
        st.info("No hay datos de la app para este partido.")
    else:
        ataques_nos = [i for i in inc if i["tipo"] == "ataque"    and i.get("equipo") == "nosotros"]
        ataques_riv = [i for i in inc if i["tipo"] == "ataque"    and i.get("equipo") == "rival"]
        tiros_nos   = [i for i in inc if i["tipo"] == "tiro_arco" and i.get("equipo") == "nosotros"]
        tiros_riv   = [i for i in inc if i["tipo"] == "tiro_arco" and i.get("equipo") == "rival"]
        goles_nos   = [i for i in inc if i["tipo"] == "gol"]
        goles_riv   = [i for i in inc if i["tipo"] == "gol_rival"]
        faltas_inc  = [i for i in inc if i["tipo"] == "faltas_acumuladas"]
        rotaciones  = [i for i in inc if i["tipo"] == "rotacion"]
        tarjetas    = [i for i in inc if i["tipo"] == "tarjeta"]

        c1, c2, c3 = st.columns(3)
        for col, label, vl, vr in [
            (c1, "GOLES",         len(goles_nos),   len(goles_riv)),
            (c2, "ATAQUES",       len(ataques_nos), len(ataques_riv)),
            (c3, "TIROS AL ARCO", len(tiros_nos),   len(tiros_riv)),
        ]:
            with col:
                st.markdown(
                    f'<div class="kpi-card">'
                    f'<div class="kpi-label">{label}</div>'
                    f'<div style="display:flex;justify-content:center;gap:24px;align-items:baseline">'
                    f'<div><div class="kpi-value" style="color:{COLOR_L}">{vl}</div>'
                    f'<div class="kpi-sub">{equipo_info["nombre"][:8]}</div></div>'
                    f'<div style="font-size:1.2rem;color:{MUTED}">·</div>'
                    f'<div><div class="kpi-value" style="color:{COLOR_RIVAL}">{vr}</div>'
                    f'<div class="kpi-sub">{partido["rival"][:8]}</div></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

        st.markdown('<div class="section-title">Actividad por minuto</div>', unsafe_allow_html=True)

        def act_minuto(lista):
            c = {}
            for i in lista:
                c[i["minuto"]] = c.get(i["minuto"], 0) + 1
            return c

        act_nos = act_minuto(ataques_nos + tiros_nos)
        act_riv = act_minuto(ataques_riv + tiros_riv)
        minutos = list(range(0, 42))

        fig_act = go.Figure()
        fig_act.add_trace(go.Scatter(
            x=minutos, y=[act_nos.get(m, 0) for m in minutos],
            fill="tozeroy", name=equipo_info["nombre"],
            line=dict(color=ACCENT, width=2),
            fillcolor="rgba(232,66,10,0.15)"
        ))
        fig_act.add_trace(go.Scatter(
            x=minutos, y=[-act_riv.get(m, 0) for m in minutos],
            fill="tozeroy", name=partido["rival"],
            line=dict(color=COLOR_RIVAL, width=2),
            fillcolor="rgba(34,197,94,0.15)"
        ))
        fig_act.add_hline(y=0, line_color=BORDER, line_width=1)
        for g in goles_nos:
            fig_act.add_vline(x=g["minuto"], line_color=ACCENT,
                              line_width=1.5, line_dash="dot",
                              annotation_text="⚽", annotation_font_size=14)
        for g in goles_riv:
            fig_act.add_vline(x=g["minuto"], line_color=COLOR_RIVAL,
                              line_width=1.5, line_dash="dot",
                              annotation_text="⚽", annotation_font_size=14,
                              annotation_position="bottom right")
        layout = plotly_base()
        layout.update(dict(
            height=300,
            xaxis_title="Minuto",
            yaxis_title=f"← {partido['rival']}  |  {equipo_info['nombre']} →",
            legend=dict(orientation="h", y=1.1, x=0),
            xaxis=dict(range=[0, 41], gridcolor=BORDER),
            yaxis=dict(gridcolor=BORDER),
        ))
        fig_act.update_layout(**layout)
        st.plotly_chart(fig_act, use_container_width=True)

        col_f, col_r = st.columns(2)

        with col_f:
            st.markdown('<div class="section-title">Faltas por jugador</div>', unsafe_allow_html=True)
            faltas_max = {}
            for f in faltas_inc:
                jid = f["jugadorId"]
                faltas_max[jid] = max(faltas_max.get(jid, 0), f["faltasAcumuladas"])
            if faltas_max:
                nombres_f = [f"#{dorsales.get(jid,'?')} {jugadores.get(jid,jid).split()[0]}"
                             for jid in faltas_max]
                valores_f = list(faltas_max.values())
                colores_f = ["#DC2626" if v >= 3 else "#EA580C" if v == 2 else "#CA8A04"
                             for v in valores_f]
                fig_f = go.Figure(go.Bar(
                    x=valores_f, y=nombres_f, orientation="h",
                    marker_color=colores_f,
                    text=valores_f, textposition="outside",
                    textfont=dict(color=TEXT, size=12, family="DM Mono")
                ))
                lf = plotly_base()
                lf.update(dict(height=200, xaxis=dict(range=[0, max(valores_f) + 1])))
                fig_f.update_layout(**lf)
                st.plotly_chart(fig_f, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Rotaciones</div>', unsafe_allow_html=True)
            for r in rotaciones:
                sale  = jugadores.get(r["saleId"],  r["saleId"]).split()[0]
                entra = jugadores.get(r["entraId"], r["entraId"]).split()[0]
                st.markdown(
                    f'<div class="rot-pill">'
                    f'<span style="color:{MUTED};font-size:0.75rem;font-weight:600">'
                    f'MIN {r["minuto"]} · T{r["tiempo"]}</span><br>'
                    f'<span style="color:#DC2626">↓ {sale}</span>'
                    f'&nbsp;&nbsp;'
                    f'<span style="color:#16A34A">↑ {entra}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            if tarjetas:
                st.markdown('<div class="section-title">Tarjetas</div>', unsafe_allow_html=True)
                for t in tarjetas:
                    nombre = jugadores.get(t["jugadorId"], t["jugadorId"]).split()[0]
                    emoji  = "🟨" if t["color"] == "amarilla" else "🟥"
                    st.markdown(
                        f'<div class="rot-pill">'
                        f'{emoji} <b>{nombre}</b>'
                        f'<span style="color:{MUTED}"> · min {t["minuto"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

# ─────────────────────────────────────────────────────────
# TAB 2: TÁCTICO
# ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Segmento táctico</div>', unsafe_allow_html=True)

    segmentos_disp = df["segmento"].unique().tolist()
    seg_labels     = {s["id"]: s["label"] for s in partido["segmentos"]
                      if s["id"] in segmentos_disp}

    seg_sel = st.selectbox(
        "Segmento",
        options=list(seg_labels.keys()),
        format_func=lambda x: seg_labels.get(x, x),
        label_visibility="collapsed"
    )
    df_seg = df[df["segmento"] == seg_sel]

    fig_tac, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig_tac.patch.set_facecolor("white")

    for idx, (equipo, color, nombre, cmap) in enumerate([
        (equipo_local_csv, ACCENT,      equipo_info["nombre"], "Oranges"),
        (equipo_rival_csv, COLOR_RIVAL, partido["rival"],      "Greens"),
    ]):
        ax = axes[idx]
        dibujar_cancha(ax)
        sub = df_seg[df_seg["equipo_final"] == equipo]
        if len(sub) > 0:
            ax.hist2d(sub["x_norm"], sub["y_norm"],
                      bins=[10, 7], range=[[0, 1], [0, 1]],
                      cmap=cmap, alpha=0.75, zorder=1)
        ax.set_title(nombre, color=color, fontsize=11, weight="bold", pad=10)
        ax.set_xlabel("← Defensa  |  Definición →", color="#555", fontsize=8)

    ax3 = axes[2]
    dibujar_cancha(ax3)
    for equipo, color in [(equipo_local_csv, ACCENT), (equipo_rival_csv, COLOR_RIVAL)]:
        sub = df_seg[df_seg["equipo_final"] == equipo]
        if len(sub) > 0:
            ax3.scatter(sub["x_norm"], sub["y_norm"],
                        c=color, alpha=0.15, s=14, zorder=1)
    ax3.set_title("Combinado", color=TEXT, fontsize=11, weight="bold", pad=10)
    ax3.set_xlabel("← Defensa  |  Definición →", color="#555", fontsize=8)
    ax3.legend(handles=[
        Patch(color=ACCENT,      label=equipo_info["nombre"]),
        Patch(color=COLOR_RIVAL, label=partido["rival"])
    ], fontsize=8, facecolor="white", edgecolor=BORDER)

    plt.tight_layout(pad=1.5)
    st.pyplot(fig_tac, use_container_width=True)
    plt.close()

    st.markdown('<div class="section-title">Presencia por zona</div>', unsafe_allow_html=True)
    col_z, col_c = st.columns(2)

    for col, col_key, zonas_ids, labels, titulo in [
        (col_z, "zona_v", ["defensa", "gestacion", "definicion"],
         ["DEF", "GEST", "DEFI"], "Zonas verticales"),
        (col_c, "zona_h", ["carril_izquierdo", "carril_central", "carril_derecho"],
         ["IZQ", "CEN", "DER"], "Carriles"),
    ]:
        with col:
            fig_b = go.Figure()
            for equipo, color, nombre in [
                (equipo_local_csv, ACCENT,      equipo_info["nombre"]),
                (equipo_rival_csv, COLOR_RIVAL, partido["rival"])
            ]:
                sub   = df_seg[df_seg["equipo_final"] == equipo]
                total = max(len(sub), 1)
                vals  = [(sub[col_key] == z).sum() / total * 100 for z in zonas_ids]
                fig_b.add_trace(go.Bar(name=nombre, x=labels, y=vals,
                                       marker_color=color, marker_opacity=0.85))
            lb = plotly_base()
            lb.update(dict(
                barmode="group", height=260,
                title=dict(text=titulo, font=dict(size=13, color=TEXT)),
                yaxis_title="% presencia",
                legend=dict(orientation="h", y=1.15)
            ))
            fig_b.update_layout(**lb)
            st.plotly_chart(fig_b, use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 3: PARTIDO COMPLETO
# ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Posicionamiento acumulado — Partido completo</div>',
                unsafe_allow_html=True)

    fig_pc = plt.figure(figsize=(16, 12))
    fig_pc.patch.set_facecolor("white")
    gs = gridspec.GridSpec(2, 2, figure=fig_pc, hspace=0.35, wspace=0.25)

    for subplot, equipo, color, nombre, cmap in [
        (gs[0, 0], equipo_local_csv, ACCENT,      equipo_info["nombre"], "Oranges"),
        (gs[0, 1], equipo_rival_csv, COLOR_RIVAL, partido["rival"],      "Greens"),
    ]:
        ax = fig_pc.add_subplot(subplot)
        dibujar_cancha(ax)
        sub = df[df["equipo_final"] == equipo]
        if len(sub) > 0:
            h = ax.hist2d(sub["x_norm"], sub["y_norm"],
                          bins=[12, 8], range=[[0, 1], [0, 1]],
                          cmap=cmap, alpha=0.75, zorder=1)
            fig_pc.colorbar(h[3], ax=ax, label="Densidad")
        ax.set_title(nombre, color=color, fontsize=12, weight="bold", pad=10)
        ax.set_xlabel("← Defensa  |  Definición →", color="#555", fontsize=8)

    ax3 = fig_pc.add_subplot(gs[1, :])
    dibujar_cancha(ax3, fontsize=9)
    for equipo, color in [(equipo_local_csv, ACCENT), (equipo_rival_csv, COLOR_RIVAL)]:
        sub = df[df["equipo_final"] == equipo]
        if len(sub) > 0:
            ax3.scatter(sub["x_norm"], sub["y_norm"],
                        c=color, alpha=0.08, s=12, zorder=1)
    ax3.set_title("Posiciones combinadas — Partido completo",
                  color=TEXT, fontsize=12, weight="bold", pad=10)
    ax3.set_xlabel("← Defensa  |  Definición →", color="#555", fontsize=9)
    ax3.legend(handles=[
        Patch(color=ACCENT,      label=equipo_info["nombre"]),
        Patch(color=COLOR_RIVAL, label=partido["rival"])
    ], fontsize=9, facecolor="white", edgecolor=BORDER, loc="upper right")

    plt.tight_layout()
    st.pyplot(fig_pc, use_container_width=True)
    plt.close()

# ─────────────────────────────────────────────────────────
# TAB 4: JUGADORES
# ─────────────────────────────────────────────────────────
with tab4:
    if not tiene_json:
        st.info("No hay datos de jugadores para este partido.")
    else:
        st.markdown('<div class="section-title">Estadísticas individuales</div>',
                    unsafe_allow_html=True)

        min_jugados = {str(m[0]): m[1] for m in datos_app["minutosJugados"]}
        faltas_max  = {}
        for f in [i for i in inc if i["tipo"] == "faltas_acumuladas"]:
            jid = f["jugadorId"]
            faltas_max[jid] = max(faltas_max.get(jid, 0), f["faltasAcumuladas"])

        filas = []
        for jid, mins in min_jugados.items():
            filas.append({
                "Dorsal":  f"#{dorsales.get(jid,'?')}",
                "Jugador": jugadores.get(jid, f"ID {jid}"),
                "Minutos": mins,
                "Faltas":  faltas_max.get(jid, 0)
            })

        df_jug = pd.DataFrame(filas).sort_values("Minutos", ascending=False)
        st.dataframe(df_jug, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">Minutos jugados</div>', unsafe_allow_html=True)
        fig_min = go.Figure(go.Bar(
            x=df_jug["Minutos"],
            y=[f"{r['Dorsal']} {r['Jugador'].split()[0]}"
               for _, r in df_jug.iterrows()],
            orientation="h",
            marker_color=[ACCENT if v == 40 else "#3B82F6" if v > 20 else "#9CA3AF"
                          for v in df_jug["Minutos"]],
            text=df_jug["Minutos"].astype(str) + " min",
            textposition="outside",
            textfont=dict(color=TEXT, size=11, family="DM Mono")
        ))
        lm = plotly_base()
        lm.update(dict(height=280, xaxis=dict(range=[0, 48])))
        fig_min.update_layout(**lm)
        st.plotly_chart(fig_min, use_container_width=True)
