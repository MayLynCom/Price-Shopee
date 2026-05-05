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
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #2d0a52 0%, #1f063b 100%);
        border: 1px solid #D4AF37;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #c8a8e9 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
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
