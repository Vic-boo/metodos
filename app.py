"""
app.py
─────────────────────────────────────────────
Interpolación por Splines Cúbicos — Aplicación Web
PrograMex | Métodos Numéricos

Interfaz web interactiva (Streamlit) que reproduce TODO lo que el
programa de consola original calcula e imprime, además de:
  • Gráfica interactiva (Plotly) con los puntos óptimos marcados.
  • Interpretación automática en lenguaje natural de los resultados.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import spline_engine as se

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PrograMex | Splines Cúbicos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  ESTILOS (colores llamativos, tema oscuro moderno)
# ─────────────────────────────────────────────
PALETTE = {
    "bg": "#0f0f1a",
    "bg_card": "#1a1a2e",
    "bg_card_alt": "#16213e",
    "primary": "#7c3aed",      # violeta
    "primary_light": "#a78bfa",
    "accent_cyan": "#06d6d6",
    "accent_pink": "#f43f9e",
    "accent_green": "#22e0a0",
    "accent_yellow": "#fbbf24",
    "text": "#e8e8f5",
    "text_muted": "#9999b3",
    "border": "#2d2d4d",
}

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(160deg, {PALETTE['bg']} 0%, #161629 100%);
        color: {PALETTE['text']};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {PALETTE['bg_card']};
        border-right: 1px solid {PALETTE['border']};
    }}

    /* Headers */
    h1, h2, h3 {{
        color: {PALETTE['text']} !important;
        font-weight: 800 !important;
    }}

    /* Hero title gradient */
    .hero-title {{
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, {PALETTE['accent_cyan']}, {PALETTE['primary']} 50%, {PALETTE['accent_pink']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        line-height: 1.1;
    }}
    .hero-subtitle {{
        color: {PALETTE['text_muted']};
        font-size: 1.05rem;
        margin-top: 0.3rem;
        margin-bottom: 1.5rem;
    }}

    /* Cards */
    .card {{
        background: {PALETTE['bg_card']};
        border: 1px solid {PALETTE['border']};
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
    }}
    .card-title {{
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    /* Stat callouts */
    .stat-box {{
        background: {PALETTE['bg_card_alt']};
        border-radius: 14px;
        padding: 1rem 1.2rem;
        text-align: center;
        border: 1px solid {PALETTE['border']};
    }}
    .stat-value {{
        font-size: 1.8rem;
        font-weight: 800;
    }}
    .stat-label {{
        color: {PALETTE['text_muted']};
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Badge pills */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .badge-max {{ background: rgba(251, 191, 36, 0.18); color: {PALETTE['accent_yellow']}; border: 1px solid {PALETTE['accent_yellow']}; }}
    .badge-min {{ background: rgba(34, 224, 160, 0.18); color: {PALETTE['accent_green']}; border: 1px solid {PALETTE['accent_green']}; }}
    .badge-inf {{ background: rgba(124, 58, 237, 0.18); color: {PALETTE['primary_light']}; border: 1px solid {PALETTE['primary_light']}; }}

    /* Segment block (mono font for polynomials) */
    .poly-block {{
        background: {PALETTE['bg_card_alt']};
        border-left: 3px solid {PALETTE['accent_cyan']};
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
        font-family: 'Courier New', monospace;
        font-size: 0.88rem;
        white-space: pre-wrap;
        color: {PALETTE['text']};
    }}

    /* Interpretation paragraph */
    .interp-p {{
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 0.7rem;
        color: {PALETTE['text']};
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(90deg, {PALETTE['primary']}, {PALETTE['accent_pink']});
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        transition: transform 0.15s ease;
    }}
    .stButton > button:hover {{
        transform: scale(1.02);
        color: white;
    }}

    /* Dataframe / editor */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
        border-radius: 12px;
        overflow: hidden;
    }}

    footer {{visibility: hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  HERO / HEADER
# ─────────────────────────────────────────────
col_logo, col_title = st.columns([0.07, 0.93])
with col_logo:
    st.markdown(
        f"<div style='font-size:2.8rem; margin-top:-0.3rem;'>📈</div>",
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown('<p class="hero-title">Interpolación por Splines Cúbicos</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">PrograMex · Calcula, interpreta y visualiza tu curva en tiempo real</p>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  SIDEBAR — ENTRADA DE DATOS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")

    n_puntos = st.number_input(
        "Número de puntos (mínimo 3)", min_value=3, max_value=30, value=6, step=1
    )

    st.markdown("#### 📋 Tabla de datos (x, y)")
    st.caption("Edita los valores directamente en la tabla. Los valores de x deben ser distintos.")

    # Datos por defecto: ejemplo coherente, genérico
    default_x = list(np.round(np.linspace(0, 10, n_puntos), 2))
    default_y = list(np.round(np.linspace(10, 70, n_puntos) + np.sin(np.linspace(0, 6, n_puntos)) * 8, 2))

    if "df_puntos" not in st.session_state or len(st.session_state["df_puntos"]) != n_puntos:
        st.session_state["df_puntos"] = pd.DataFrame({"x": default_x, "y": default_y})

    df_editado = st.data_editor(
        st.session_state["df_puntos"],
        num_rows="fixed",
        width='stretch',
        hide_index=True,
        column_config={
            "x": st.column_config.NumberColumn("x", format="%.4f"),
            "y": st.column_config.NumberColumn("y", format="%.4f"),
        },
        key="editor_puntos",
    )

    st.markdown("#### 🔧 Condición de frontera")
    frontera_label = st.radio(
        "Tipo de spline",
        options=["Natural  (S'' = 0 en extremos)", "Sujeto  (se especifican las pendientes)"],
        index=0,
        label_visibility="collapsed",
    )
    frontera = "natural" if frontera_label.startswith("Natural") else "sujeto"

    fp0, fpn = 0.0, 0.0
    if frontera == "sujeto":
        c1, c2 = st.columns(2)
        with c1:
            fp0 = st.number_input("f'(x₀)", value=0.0, format="%.4f")
        with c2:
            fpn = st.number_input("f'(xₙ)", value=0.0, format="%.4f")

    calcular = st.button("🚀 Calcular Spline", width='stretch')

    st.markdown("---")
    st.caption("PrograMex · </ Desarrollamos el Futuro >")

# ─────────────────────────────────────────────
#  VALIDACIÓN Y CÁLCULO
# ─────────────────────────────────────────────
xs_raw = df_editado["x"].to_numpy(dtype=float)
ys_raw = df_editado["y"].to_numpy(dtype=float)

errores = []
if len(set(xs_raw)) != len(xs_raw):
    errores.append("Hay valores de **x repetidos**. Cada x debe ser único para construir el spline.")
if np.any(np.isnan(xs_raw)) or np.any(np.isnan(ys_raw)):
    errores.append("Hay celdas vacías o inválidas en la tabla de datos.")

if errores:
    for e in errores:
        st.error(e)
    st.stop()

# Ordenar por x (igual que el programa original)
orden = np.argsort(xs_raw)
x = xs_raw[orden]
y = ys_raw[orden]

# Mantener resultados en sesión para no perderlos al interactuar con la gráfica
if calcular or "resultados" not in st.session_state:
    coefs, M = se.calcular_splines(x, y, frontera, fp0, fpn)
    optimos = se.encontrar_optimos(x, coefs)
    st.session_state["resultados"] = {
        "x": x, "y": y, "coefs": coefs, "M": M, "optimos": optimos,
        "frontera": frontera, "fp0": fp0, "fpn": fpn,
    }

res = st.session_state["resultados"]
x, y, coefs, M, optimos = res["x"], res["y"], res["coefs"], res["M"], res["optimos"]
frontera, fp0, fpn = res["frontera"], res["fp0"], res["fpn"]

# ─────────────────────────────────────────────
#  STAT CALLOUTS
# ─────────────────────────────────────────────
n_max = sum(1 for _, _, t in optimos if t == "máximo")
n_min = sum(1 for _, _, t in optimos if t == "mínimo")

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(
        f'<div class="stat-box"><div class="stat-value" style="color:{PALETTE["accent_cyan"]}">{len(x)}</div>'
        f'<div class="stat-label">Puntos ingresados</div></div>',
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        f'<div class="stat-box"><div class="stat-value" style="color:{PALETTE["primary_light"]}">{len(coefs)}</div>'
        f'<div class="stat-label">Segmentos cúbicos</div></div>',
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        f'<div class="stat-box"><div class="stat-value" style="color:{PALETTE["accent_yellow"]}">{n_max}</div>'
        f'<div class="stat-label">Máximos locales</div></div>',
        unsafe_allow_html=True,
    )
with s4:
    st.markdown(
        f'<div class="stat-box"><div class="stat-value" style="color:{PALETTE["accent_green"]}">{n_min}</div>'
        f'<div class="stat-label">Mínimos locales</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GRÁFICA INTERACTIVA (PLOTLY)
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="card-title">📊 Curva del spline cúbico</div>',
    unsafe_allow_html=True,
)

xs_plot = np.linspace(x[0], x[-1], 600)
ys_plot = np.array([se.evaluar(xi, x, coefs) for xi in xs_plot])

fig = go.Figure()

# Líneas verticales en cada nodo
for xi in x:
    fig.add_vline(x=xi, line_width=1, line_dash="dot", line_color="#2d2d4d")

# Curva del spline
fig.add_trace(go.Scatter(
    x=xs_plot, y=ys_plot, mode="lines", name="Spline cúbico",
    line=dict(color=PALETTE["accent_cyan"], width=3.5),
    hovertemplate="x=%{x:.4f}<br>S(x)=%{y:.4f}<extra></extra>",
))

# Puntos originales
fig.add_trace(go.Scatter(
    x=x, y=y, mode="markers", name="Puntos de datos",
    marker=dict(color=PALETTE["accent_pink"], size=11, line=dict(color="white", width=1.5)),
    hovertemplate="Nodo<br>x=%{x:.4f}<br>y=%{y:.4f}<extra></extra>",
))

# Óptimos
for x_opt, y_opt, tipo in optimos:
    if tipo == "máximo":
        color_pt, symbol, name = PALETTE["accent_yellow"], "triangle-up", "Máximo"
    elif tipo == "mínimo":
        color_pt, symbol, name = PALETTE["accent_green"], "triangle-down", "Mínimo"
    else:
        color_pt, symbol, name = PALETTE["primary_light"], "diamond", "Inflexión"
    fig.add_trace(go.Scatter(
        x=[x_opt], y=[y_opt], mode="markers+text", name=name,
        showlegend=False,
        marker=dict(color=color_pt, size=16, symbol=symbol, line=dict(color="white", width=1.5)),
        text=[f"{name}"], textposition="top center",
        textfont=dict(color=color_pt, size=11),
        hovertemplate=f"{name}<br>x=%{{x:.4f}}<br>S(x)=%{{y:.4f}}<extra></extra>",
    ))

fig.update_layout(
    plot_bgcolor=PALETTE["bg_card"],
    paper_bgcolor=PALETTE["bg_card"],
    font=dict(color=PALETTE["text"]),
    xaxis=dict(title="x", gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
    yaxis=dict(title="S(x)", gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
    legend=dict(
        bgcolor=PALETTE["bg_card_alt"], bordercolor=PALETTE["border"], borderwidth=1,
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11),
    ),
    margin=dict(l=10, r=10, t=10, b=10),
    height=520,
    hovermode="closest",
)

st.plotly_chart(fig, width='stretch')

# ─────────────────────────────────────────────
#  EVALUAR PUNTO ADICIONAL
# ─────────────────────────────────────────────
st.markdown('<div class="card-title">🎯 Evaluar un punto específico</div>', unsafe_allow_html=True)
ec1, ec2 = st.columns([0.7, 0.3])
with ec1:
    x_eval = st.slider(
        "Selecciona x*", float(x[0]), float(x[-1]), float((x[0] + x[-1]) / 2),
        step=float((x[-1] - x[0]) / 200) if x[-1] > x[0] else 0.01,
    )
with ec2:
    y_eval = se.evaluar(x_eval, x, coefs)
    st.markdown(
        f'<div class="stat-box"><div class="stat-value" style="color:{PALETTE["accent_cyan"]}">{y_eval:.4f}</div>'
        f'<div class="stat-label">S({x_eval:.4f})</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INTERPRETACIÓN AUTOMÁTICA ("LA PROBLEMÁTICA")
# ─────────────────────────────────────────────
st.markdown('<div class="card-title">🧠 Interpretación automática de resultados</div>', unsafe_allow_html=True)
parrafos = se.interpretar_resultados(x, y, M, optimos, frontera, fp0, fpn)
interp_html = "".join(f'<p class="interp-p">{p}</p>' for p in parrafos)
st.markdown(f'<div class="card">{interp_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  RESULTADOS DETALLADOS (tabs: igual que la consola)
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Tabla de datos", "📐 Segundas derivadas (M)", "🧮 Polinomios por tramo", "⭐ Puntos óptimos"
])

with tab1:
    df_show = pd.DataFrame({"i": range(len(x)), "x": x, "y": y})
    st.dataframe(df_show, width='stretch', hide_index=True)
    st.caption(f"Condición de frontera: **{frontera.upper()}**" + (
        f"  ·  f'(x₀) = {fp0:.4f}, f'(xₙ) = {fpn:.4f}" if frontera == "sujeto" else ""
    ))

with tab2:
    st.caption("M[i] = S''(xᵢ) — curvatura de la curva en cada nodo")
    df_m = pd.DataFrame({"i": range(len(M)), "x_i": x, "M[i] = S''(x_i)": M})
    st.dataframe(df_m, width='stretch', hide_index=True)

with tab3:
    st.caption("S_i(x) = a + b(x − x_i) + c(x − x_i)² + d(x − x_i)³,  válido en x ∈ [x_i, x_{i+1}]")
    for i, (a, b, c, d) in enumerate(coefs):
        signo_b = "+" if b >= 0 else "-"
        signo_c = "+" if c >= 0 else "-"
        signo_d = "+" if d >= 0 else "-"
        texto = (
            f"Segmento {i+1}:  x ∈ [{x[i]:.4f}, {x[i+1]:.4f}]\n\n"
            f"S_{i+1}(x) = {a:.6f}\n"
            f"        {signo_b} {abs(b):.6f}·(x - {x[i]:.4f})\n"
            f"        {signo_c} {abs(c):.6f}·(x - {x[i]:.4f})²\n"
            f"        {signo_d} {abs(d):.6f}·(x - {x[i]:.4f})³"
        )
        st.markdown(f'<div class="poly-block">{texto}</div>', unsafe_allow_html=True)

with tab4:
    if not optimos:
        st.info("No se encontraron máximos ni mínimos locales dentro del dominio. La función es monótona.")
    else:
        for x_opt, y_opt, tipo in optimos:
            if tipo == "máximo":
                badge = '<span class="badge badge-max">Máximo</span>'
            elif tipo == "mínimo":
                badge = '<span class="badge badge-min">Mínimo</span>'
            else:
                badge = '<span class="badge badge-inf">Inflexión</span>'
            st.markdown(
                f'<div class="card">{badge}&nbsp;&nbsp;'
                f'<b>x = {x_opt:.6f}</b> &nbsp;→&nbsp; <b>S(x) = {y_opt:.6f}</b></div>',
                unsafe_allow_html=True,
            )

st.markdown(
    f'<p style="text-align:center; color:{PALETTE["text_muted"]}; font-size:0.8rem; margin-top:2rem;">'
    f'PrograMex &nbsp;|&nbsp; &lt; / Desarrollamos el Futuro &gt;</p>',
    unsafe_allow_html=True,
)
