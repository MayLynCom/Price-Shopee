"""
Shopee Price Calculator — App principal (Streamlit).

Execução:
    streamlit run app.py
"""

import io
import pandas as pd
import numpy as np
import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter

from pricing import calcular_lote
from styles import (
    CUSTOM_CSS, TITLE_HTML, SIDEBAR_HEADER_HTML,
    section_header, badge_html,
)

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Shopee Price Calculator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Constantes ────────────────────────────────────────────────────────────────
MARGIN_TOLERANCE = 0.02     # ±2 pp tolerância para marcar como "ok"
CURRENCY_FMT = "R$ {:,.2f}"


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def parse_excel(file) -> pd.DataFrame | None:
    """
    Lê o arquivo Excel e normaliza os nomes das colunas.
    Aceita variações comuns de nomes de coluna.
    Retorna None em caso de erro.
    """
    try:
        df = pd.read_excel(file, dtype=str)
        df.columns = [str(c).strip().lower() for c in df.columns]

        col_map = {
            "id": ["id", "id_produto", "sku", "código", "codigo", "cod"],
            "nome": ["nome", "nome_produto", "produto", "descrição", "descricao", "name"],
            "custo": ["custo", "custo_produto", "cost", "costo", "valor_custo", "custo (r$)"],
            "peso_extra_kg": ["peso_extra_kg", "peso_extra", "peso adicional", "extra_kg"],
        }

        rename = {}
        for target, aliases in col_map.items():
            for alias in aliases:
                if alias in df.columns:
                    rename[alias] = target
                    break

        df = df.rename(columns=rename)

        if "id" not in df.columns:
            st.error("❌ Coluna de ID do produto não encontrada. "
                     "Certifique-se de ter uma coluna chamada 'ID', 'SKU' ou 'Código'.")
            return None

        if "custo" not in df.columns:
            st.error("❌ Coluna de Custo não encontrada. "
                     "Certifique-se de ter uma coluna chamada 'Custo' ou 'Cost'.")
            return None

        # Converte custo para float
        df["custo"] = (
            df["custo"]
            .str.replace(r"[R$\s]", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        if "peso_extra_kg" in df.columns:
            df["peso_extra_kg"] = pd.to_numeric(
                df["peso_extra_kg"].str.replace(",", "."), errors="coerce"
            ).fillna(0.0)
        else:
            df["peso_extra_kg"] = 0.0

        if "nome" not in df.columns:
            df["nome"] = df["id"].astype(str)

        df = df[df["custo"] > 0].reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
        return None


def build_results_df(
    df_raw: pd.DataFrame,
    sobretaxa_peso: float,
    margem: float,
    desconto_promo: float,
    aliquota_imposto: float,
) -> pd.DataFrame:
    """Executa o motor de cálculo e retorna um DataFrame formatado."""
    produtos = df_raw.to_dict("records")
    resultados = calcular_lote(
        produtos=produtos,
        sobretaxa_peso=sobretaxa_peso,
        margem_desejada=margem,
        desconto_promo=desconto_promo,
        aliquota_imposto=aliquota_imposto,
    )

    rows = []
    for r in resultados:
        rows.append({
            "ID Produto": r.produto_id,
            "Nome": r.nome_produto,
            "Custo (R$)": r.custo,
            "Preço Alvo (R$)": r.preco_venda,
            "Fake Price (R$)": r.fake_price,
            "Lucro (R$)": r.lucro,
            "Comissão Shopee (R$)": r.comissao_shopee,
            "Viável": r.viavel,
        })

    return pd.DataFrame(rows)


# ── Exportação Excel ──────────────────────────────────────────────────────────
def generate_excel(
    df: pd.DataFrame,
    margem: float,
    desconto_promo: float,
    aliquota: float,
) -> bytes:
    """Gera um Excel com formatação profissional e retorna bytes."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Precificação Shopee"

    # Paleta
    ROXO_ESC = "1a0533"
    ROXO_MED = "2d0a52"
    DOURADO   = "D4AF37"
    BRANCO    = "FFFFFF"
    VERDE     = "1DB954"
    VERMELHO  = "E74C3C"
    CINZA_CL  = "F0E6FF"

    fill_header  = PatternFill("solid", fgColor=ROXO_MED)
    fill_title   = PatternFill("solid", fgColor=ROXO_ESC)
    fill_params  = PatternFill("solid", fgColor="0f0120")
    fill_ok      = PatternFill("solid", fgColor="0a2e1a")
    fill_nok     = PatternFill("solid", fgColor="2e0a0a")
    fill_row_alt = PatternFill("solid", fgColor="1f063b")

    font_title   = Font(name="Calibri", bold=True, size=14, color=DOURADO)
    font_header  = Font(name="Calibri", bold=True, size=10, color=DOURADO)
    font_data    = Font(name="Calibri", size=10, color=BRANCO)
    font_params  = Font(name="Calibri", size=10, color="c8a8e9")
    font_ok      = Font(name="Calibri", size=10, color=VERDE, bold=True)
    font_nok     = Font(name="Calibri", size=10, color=VERMELHO, bold=True)

    thin_gold    = Border(
        left=Side(style="thin", color=DOURADO),
        right=Side(style="thin", color=DOURADO),
        top=Side(style="thin", color=DOURADO),
        bottom=Side(style="thin", color=DOURADO),
    )
    center_align = Alignment(horizontal="center", vertical="center")
    left_align   = Alignment(horizontal="left", vertical="center")

    # ── Linha 1: Título ──
    ws.merge_cells("A1:H1")
    ws["A1"] = "SHOPEE PRICE CALCULATOR"
    ws["A1"].font = font_title
    ws["A1"].fill = fill_title
    ws["A1"].alignment = center_align
    ws.row_dimensions[1].height = 30

    # ── Linhas 2-4: Parâmetros ──
    params = [
        ("Margem Desejada", f"{margem*100:.1f}%"),
        ("Desconto Promocional (Fake Price)", f"{desconto_promo*100:.1f}%"),
        ("Imposto sobre Receita", f"{aliquota*100:.2f}%"),
    ]
    for i, (label, value) in enumerate(params, start=2):
        ws.merge_cells(f"A{i}:E{i}")
        ws.merge_cells(f"F{i}:H{i}")
        ws[f"A{i}"] = label
        ws[f"F{i}"] = value
        ws[f"A{i}"].font = font_params
        ws[f"F{i}"].font = Font(name="Calibri", size=10, color=DOURADO, bold=True)
        ws[f"A{i}"].fill = fill_params
        ws[f"F{i}"].fill = fill_params
        ws[f"A{i}"].alignment = left_align
        ws[f"F{i}"].alignment = left_align
        ws.row_dimensions[i].height = 18

    ws.row_dimensions[5].height = 6   # espaço

    # ── Linha 6: Cabeçalhos da tabela ──
    data_cols = [
        "ID Produto", "Nome", "Custo (R$)", "Preço Alvo (R$)",
        "Fake Price (R$)", "Lucro (R$)",
        "Comissão Shopee (R$)", "Status",
    ]
    for col_idx, col_name in enumerate(data_cols, start=1):
        cell = ws.cell(row=6, column=col_idx, value=col_name)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = center_align
        cell.border = thin_gold
    ws.row_dimensions[6].height = 22

    # ── Linhas de dados ──
    currency_num = '#,##0.00'
    pct_num      = '0.0"%"'

    for row_idx, (_, row) in enumerate(df.iterrows(), start=7):
        viavel = bool(row["Viável"])
        fill_row = fill_ok if viavel else fill_nok
        fill_alt = fill_row_alt if row_idx % 2 == 0 else PatternFill("solid", fgColor="160430")

        values = [
            row["ID Produto"],
            row["Nome"],
            row["Custo (R$)"],
            row["Preço Alvo (R$)"],
            row["Fake Price (R$)"],
            row["Lucro (R$)"],
            row["Comissão Shopee (R$)"],
            "✔ OK" if viavel else "⚠ Revisar",
        ]
        formats = [
            None, None,
            currency_num, currency_num, currency_num,
            currency_num, currency_num, None,
        ]

        for col_idx, (val, fmt) in enumerate(zip(values, formats), start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.fill = fill_alt
            cell.alignment = center_align if col_idx != 2 else left_align
            cell.border = Border(
                left=Side(style="thin", color="3d1562"),
                right=Side(style="thin", color="3d1562"),
                bottom=Side(style="thin", color="3d1562"),
            )
            if col_idx == 8:
                cell.font = font_ok if viavel else font_nok
            else:
                cell.font = font_data
            if fmt:
                cell.number_format = fmt

        ws.row_dimensions[row_idx].height = 18

    # ── Largura das colunas ──
    col_widths = [14, 24, 14, 16, 16, 14, 20, 12]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Freeze panes ──
    ws.freeze_panes = "A7"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── Template Excel para download ──────────────────────────────────────────────
def generate_template_excel() -> bytes:
    """Gera um Excel modelo simples para o usuário preencher e retorna os bytes."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Produtos"

    ws.cell(row=1, column=1, value="ID")
    ws.cell(row=1, column=2, value="Nome")
    ws.cell(row=1, column=3, value="Custo")

    example_rows = [
        ("SKU-001", "Camiseta Básica", 49.90),
        ("SKU-002", "Meia Esportiva", 18.50),
        ("SKU-003", "Tênis Casual", 110.00),
    ]
    for row_idx, (pid, nome, custo) in enumerate(example_rows, start=2):
        ws.cell(row=row_idx, column=1, value=pid)
        ws.cell(row=row_idx, column=2, value=nome)
        ws.cell(row=row_idx, column=3, value=custo)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_HEADER_HTML, unsafe_allow_html=True)

    st.markdown("**Margem de Lucro**")
    margem_pct = st.slider(
        "Margem (%)", min_value=5, max_value=80, value=30, step=1,
        label_visibility="collapsed",
        help="Margem desejada sobre a receita líquida após comissão Shopee",
    )

    st.markdown("**Desconto Fake Price**")
    promo_pct = st.slider(
        "Promo (%)", min_value=0, max_value=50, value=10, step=1,
        label_visibility="collapsed",
        help="Percentual de desconto aparente. O preço riscado será: Preço Alvo ÷ (1 - desconto%)",
    )

    st.divider()

    st.markdown("**Imposto sobre Receita**")
    aliquota_pct = st.slider(
        "Imposto (%)", min_value=0, max_value=50, value=6, step=1,
        label_visibility="collapsed",
        help="Alíquota de imposto sobre a receita bruta (ex: Simples Nacional, Lucro Presumido)",
    )

    st.divider()
    st.markdown(
        "<div style='text-align:center; color:#7B2FBE; font-size:0.75rem;'>"
        "Taxas Shopee conforme tabela oficial<br>Versão 1.0</div>",
        unsafe_allow_html=True,
    )

# ── Parâmetros calculados ─────────────────────────────────────────────────────
margem         = margem_pct / 100
desconto_promo = promo_pct / 100
aliquota       = aliquota_pct / 100

# ── Cabeçalho principal ───────────────────────────────────────────────────────
st.markdown(TITLE_HTML, unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown(
    section_header("Importar Planilha de Produtos", "📂"),
    unsafe_allow_html=True,
)

col_upload, col_hint = st.columns([2, 3])
with col_upload:
    uploaded = st.file_uploader(
        "Selecione o arquivo Excel",
        type=["xlsx", "xls"],
        label_visibility="collapsed",
    )
    st.download_button(
        label="⬇️ Baixar Planilha Modelo",
        data=generate_template_excel(),
        file_name="modelo_shopee.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Baixe o modelo, preencha com seus produtos e faça o upload acima.",
    )
with col_hint:
    st.markdown(
        "<div style='background:#2d0a52; border:1px solid #7B2FBE; border-radius:8px;"
        " padding:12px 16px; color:#c8a8e9; font-size:0.85rem;'>"
        "<b style='color:#D4AF37'>Colunas obrigatórias:</b><br>"
        "• <code style='color:#e8d5ff'>ID</code> / <code style='color:#e8d5ff'>SKU</code> "
        "/ <code style='color:#e8d5ff'>Código</code><br>"
        "• <code style='color:#e8d5ff'>Custo</code> (valor numérico em R$)<br>"
        "<b style='color:#D4AF37'>Colunas opcionais:</b><br>"
        "• <code style='color:#e8d5ff'>Nome</code> &nbsp;"
        "• <code style='color:#e8d5ff'>peso_extra_kg</code>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Processamento ─────────────────────────────────────────────────────────────
if uploaded is not None:
    if "last_file" not in st.session_state or st.session_state.last_file != uploaded.name:
        st.session_state.last_file = uploaded.name
        st.session_state.df_raw = parse_excel(uploaded)

    df_raw = st.session_state.get("df_raw")

    if df_raw is not None and len(df_raw) > 0:

        df_results = build_results_df(
            df_raw=df_raw,
            sobretaxa_peso=0.0,
            margem=margem,
            desconto_promo=desconto_promo,
            aliquota_imposto=aliquota,
        )

        # ── Tabela de resultados ────────────────────────────────────────────
        st.markdown(
            section_header("Tabela de Preços Calculados", "📋"),
            unsafe_allow_html=True,
        )

        # Parâmetros exibidos como badges
        st.markdown(
            f"Parâmetros ativos: "
            + badge_html(f"Margem {margem_pct}%")
            + " &nbsp; "
            + badge_html(f"Promo {promo_pct}%", "#7B2FBE")
            + " &nbsp; "
            + badge_html(f"Imposto {aliquota_pct:.1f}%", "#1a7a4a"),
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Formata o DataFrame para exibição
        display_df = df_results.drop(columns=["Viável"]).copy()

        # Formatação condicional por margem (cor de fundo via Styler)
        def color_rows(row):
            return ["background-color: #1f063b; color: #FFFFFF"] * len(row)

        styled = (
            display_df.style
            .apply(color_rows, axis=1)
            .format({
                "Custo (R$)":          "R$ {:,.2f}",
                "Preço Alvo (R$)":     "R$ {:,.2f}",
                "Fake Price (R$)":     "R$ {:,.2f}",
                "Lucro (R$)":          "R$ {:,.2f}",
                "Comissão Shopee (R$)":"R$ {:,.2f}",
            })
            .set_properties(**{
                "text-align": "center",
                "font-size": "0.88rem",
            })
            .set_properties(subset=["Nome"], **{"text-align": "left"})
        )

        st.dataframe(styled, use_container_width=True, height=420)

        # ── Exportação ─────────────────────────────────────────────────────
        st.markdown(
            section_header("Exportar Resultados", "📥"),
            unsafe_allow_html=True,
        )

        excel_bytes = generate_excel(
            df=df_results,
            margem=margem,
            desconto_promo=desconto_promo,
            aliquota=aliquota,
        )

        col_dl, col_info = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="⬇️  Baixar Excel",
                data=excel_bytes,
                file_name="shopee_precificacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with col_info:
            st.markdown(
                "<div style='color:#c8a8e9; font-size:0.85rem; padding-top:8px;'>"
                "Exporta todos os produtos com os parâmetros atuais.<br>"
                "O arquivo inclui formatação profissional e destaque por status de margem."
                "</div>",
                unsafe_allow_html=True,
            )

    elif df_raw is not None and len(df_raw) == 0:
        st.warning("Planilha lida, mas nenhum produto com custo > 0 foi encontrado.")

else:
    # ── Estado vazio: instruções ────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 48px 24px;
            background: linear-gradient(135deg, #2d0a52 0%, #1f063b 100%);
            border: 1px dashed #7B2FBE;
            border-radius: 12px;
            color: #c8a8e9;
        ">
            <div style="font-size: 3rem; margin-bottom: 12px;">📊</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #D4AF37; margin-bottom: 8px;">
                Importe sua planilha para começar
            </div>
            <div style="font-size: 0.9rem; line-height: 1.7;">
                Faça upload de um Excel com as colunas <b>ID</b> e <b>Custo</b>.<br>
                Ajuste a margem e o desconto no painel lateral —<br>
                os preços serão calculados <b>em tempo real</b>.
            </div>
            <div style="margin-top: 20px; font-size: 0.8rem; color: #7B2FBE;">
                Taxas Shopee aplicadas automaticamente por faixa de preço
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tabela de referência das taxas ──────────────────────────────────────
    st.markdown(
        section_header("Tabela de Taxas Shopee (referência)", "💡"),
        unsafe_allow_html=True,
    )

    df_fees = pd.DataFrame([
        {"Faixa de Preço": "Até R$ 79,99",        "Comissão": "20% + R$ 4,00",  "Subsídio Pix": "—"},
        {"Faixa de Preço": "R$ 80 a R$ 99,99",    "Comissão": "14% + R$ 16,00", "Subsídio Pix": "5%"},
        {"Faixa de Preço": "R$ 100 a R$ 199,99",  "Comissão": "14% + R$ 20,00", "Subsídio Pix": "5%"},
        {"Faixa de Preço": "R$ 200 a R$ 499,99",  "Comissão": "14% + R$ 26,00", "Subsídio Pix": "5%"},
        {"Faixa de Preço": "Acima de R$ 500",      "Comissão": "14% + R$ 26,00", "Subsídio Pix": "8%"},
    ])
    st.dataframe(df_fees, use_container_width=True, hide_index=True)
    st.markdown(
        "<div style='font-size:0.78rem; color:#7B2FBE; margin-top:6px;'>"
        "* O Subsídio Pix é pago pela Shopee ao comprador — não afeta a receita do vendedor."
        "</div>",
        unsafe_allow_html=True,
    )
