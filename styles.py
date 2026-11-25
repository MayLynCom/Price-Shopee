"""
Estilos CSS customizados para o app Shopee Price Calculator.
Paleta: roxo escuro (#1a0533) + roxo médio (#2d0a52) + dourado (#D4AF37) + branco (#FFFFFF).
"""

CUSTOM_CSS = """
<style>
    /* ── Fundo e corpo principal ── */
    .stApp {
        background-color: #1a0533;
    }
    .stApp > header {
        background-color: #1a0533;
        border-bottom: 2px solid #D4AF37;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #120226;
        border-right: 2px solid #D4AF37;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label {
        color: #FFFFFF !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #D4AF37 !important;
        border-color: #D4AF37 !important;
    }
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [data-testid="stTickBarMax"] {
        color: #D4AF37 !important;
    }

    /* ── Títulos ── */
    h1 {
        color: #D4AF37 !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }
    h2, h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    h2 {
        border-bottom: 1px solid #D4AF37;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }
    p, span, li {
        color: #e8d5ff !important;
    }

    /* ── Cards de métricas ── */
    [data-testid="metric-container"],
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #2d0a52 0%, #1f063b 100%);
        border: 1px solid #D4AF37;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #c8a8e9 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #D4AF37 !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #a8e6cf !important;
    }

    /* ── Tabela (dataframe) ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #D4AF37 !important;
        border-radius: 8px;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] th {
        background-color: #2d0a52 !important;
        color: #D4AF37 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0.5px;
    }
    [data-testid="stDataFrame"] td {
        color: #FFFFFF !important;
        border-color: #3d1562 !important;
    }

    /* ── Botões ── */
    .stDownloadButton > button,
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #b8920a 100%);
        color: #1a0533 !important;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        box-shadow: 0 3px 12px rgba(212, 175, 55, 0.35);
        transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover,
    .stButton > button:hover {
        box-shadow: 0 5px 20px rgba(212, 175, 55, 0.55);
        transform: translateY(-1px);
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #7B2FBE !important;
        border-radius: 10px;
        background-color: #1f063b;
        padding: 8px;
    }
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p {
        color: #c8a8e9 !important;
    }

    /* ── Select e number input ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] input {
        background-color: #2d0a52 !important;
        color: #FFFFFF !important;
        border-color: #7B2FBE !important;
        border-radius: 6px;
    }

    /* ── Divisor ── */
    hr {
        border-color: #D4AF37 !important;
        opacity: 0.3;
    }

    /* ── Alertas/info ── */
    [data-testid="stAlert"] {
        background-color: #2d0a52;
        border-left: 4px solid #D4AF37;
        color: #FFFFFF !important;
        border-radius: 6px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #1a0533; }
    ::-webkit-scrollbar-thumb { background: #7B2FBE; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #D4AF37; }
</style>
"""


TITLE_HTML = """
<div style="
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 0 20px 0;
    border-bottom: 2px solid #D4AF37;
    margin-bottom: 24px;
">
    <div style="font-size: 2.8rem;">🛍️</div>
    <div>
        <div style="
            font-size: 1.9rem;
            font-weight: 800;
            color: #D4AF37;
            line-height: 1.1;
            letter-spacing: 0.5px;
        ">Shopee Price Calculator</div>
        <div style="
            font-size: 0.88rem;
            color: #c8a8e9;
            margin-top: 2px;
        ">Precificação inteligente com taxas Shopee em tempo real</div>
    </div>
</div>
"""


SIDEBAR_HEADER_HTML = """
<div style="
    text-align: center;
    padding: 8px 0 16px 0;
    border-bottom: 1px solid #D4AF37;
    margin-bottom: 16px;
">
    <div style="font-size: 1.1rem; font-weight: 700; color: #D4AF37;">⚙️ Configurações</div>
    <div style="font-size: 0.78rem; color: #c8a8e9; margin-top: 2px;">
        Ajuste e veja os preços atualizarem
    </div>
</div>
"""


def section_header(title: str, icon: str = "") -> str:
    return f"""
<div style="
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 24px 0 12px 0;
">
    <span style="font-size: 1.1rem;">{icon}</span>
    <span style="
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 3px;
    ">{title}</span>
</div>
"""


def badge_html(text: str, color: str = "#D4AF37") -> str:
    return f"""
<span style="
    background-color: {color}22;
    color: {color};
    border: 1px solid {color};
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 600;
">{text}</span>
"""


# ── Cards de indicadores (KPIs) do diagnóstico ───────────────────────────────
# Obs: o CSS global força a cor de <p>/<span>, então os cards usam só <div>.
KPI_CSS = """
<style>
.kpi-grid {
    display: grid;
    gap: 14px;
    margin: 6px 0 16px 0;
}
.kpi-grid.cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.kpi-grid.cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.kpi-grid.cols-1 { grid-template-columns: minmax(0, 520px); }
@media (max-width: 900px) {
    .kpi-grid.cols-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px) {
    .kpi-grid.cols-2, .kpi-grid.cols-4 { grid-template-columns: minmax(0, 1fr); }
}
.kpi-card {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
    min-height: 118px;
    padding: 16px 18px 14px 18px;
    background: linear-gradient(135deg, #2d0a52 0%, #1f063b 100%);
    border: 1px solid #3d1562;
    border-top: 3px solid var(--kpi-accent, #D4AF37);
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}
.kpi-card.big { min-height: 140px; }
.kpi-head {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #c8a8e9;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.7px;
    text-transform: uppercase;
}
.kpi-icon { font-size: 1rem; line-height: 1; }
.kpi-help {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 17px;
    height: 17px;
    margin-left: auto;
    border: 1px solid #7B2FBE;
    border-radius: 50%;
    color: #c8a8e9;
    font-size: 0.68rem;
    font-weight: 700;
    cursor: help;
    outline: none;
}
.kpi-help:hover, .kpi-help:focus { border-color: #D4AF37; color: #D4AF37; }
.kpi-tip {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: 40px;
    left: 10px;
    right: 10px;
    z-index: 50;
    padding: 10px 12px;
    background: #0f0120;
    border: 1px solid #7B2FBE;
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    color: #e8d5ff;
    font-size: 0.8rem;
    font-weight: 400;
    line-height: 1.5;
    letter-spacing: 0;
    text-transform: none;
    transition: opacity 0.15s ease;
}
.kpi-help:hover + .kpi-tip, .kpi-help:focus + .kpi-tip {
    visibility: visible;
    opacity: 1;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 800;
    line-height: 1.1;
    color: var(--kpi-value, #D4AF37);
    font-variant-numeric: tabular-nums;
}
.kpi-card.big .kpi-value { font-size: 2.1rem; }
.kpi-foot {
    display: flex;
    align-items: center;
    min-height: 24px;
    color: #a98ec9;
    font-size: 0.78rem;
}
.kpi-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--pill-fg, #e8d5ff);
    background: var(--pill-bg, #2d0a52);
}
</style>
"""


def kpi_card(
    titulo: str,
    valor: str,
    ajuda: str = "",
    rodape: str = "",
    icone: str = "",
    cor_valor: str = "#D4AF37",
    cor_destaque: str = "#D4AF37",
    grande: bool = False,
) -> str:
    """HTML de um card de indicador com "?" que mostra a explicação."""
    ajuda_html = (
        f"<div class='kpi-help' tabindex='0'>?</div><div class='kpi-tip'>{ajuda}</div>"
        if ajuda else ""
    )
    icone_html = f"<div class='kpi-icon'>{icone}</div>" if icone else ""
    return (
        f"<div class='kpi-card{' big' if grande else ''}' "
        f"style='--kpi-accent:{cor_destaque}; --kpi-value:{cor_valor};'>"
        f"<div class='kpi-head'>{icone_html}<div>{titulo}</div>{ajuda_html}</div>"
        f"<div class='kpi-value'>{valor}</div>"
        f"<div class='kpi-foot'>{rodape}</div>"
        "</div>"
    )


def kpi_grid(cards: list[str], colunas: int) -> str:
    return f"<div class='kpi-grid cols-{colunas}'>" + "".join(cards) + "</div>"


def kpi_pill(texto: str, fg: str, bg: str) -> str:
    return f"<div class='kpi-pill' style='--pill-fg:{fg}; --pill-bg:{bg};'>{texto}</div>"
