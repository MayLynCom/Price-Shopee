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


def render_cost_breakdown(row: pd.Series) -> None:
    """
    Renderiza um gráfico de pizza (donut) mostrando como o preço do produto
    se decompõe em 4 fatias limpas:
      • Custo + Taxa Fixa Shopee  (a taxa fixa é agrupada com o custo
                                    porque é um valor fixo, não percentual)
      • Comissão Shopee %         (apenas a parte percentual)
      • Imposto + Spike Day
      • Lucro Líquido (% do preço)
    """
    preco       = float(row["Preço Alvo (R$)"])
    custo       = float(row["Custo (R$)"])
    comissao    = float(row["Comissão Shopee (R$)"])
    taxa_fixa   = float(row["Taxa Fixa Shopee (R$)"])
    lucro       = float(row["Lucro (R$)"])
    break_even  = float(row["Break-Even (R$)"])
    margem_real = float(row["Margem Real"])

    if preco <= 0:
        return

    # Comissão Shopee % (só a parte percentual, sem a taxa fixa)
    comissao_pct = max(0.0, comissao - taxa_fixa)
    # Custo do produto + taxa fixa Shopee (agrupados na pizza)
    custo_e_taxa = custo + taxa_fixa
    # Imposto + Spike Day = o que sobra do preço após o resto.
    # Garante que os componentes somem exatamente 100%.
    imposto_spike = max(0.0, preco - comissao_pct - custo_e_taxa - lucro)

    pct_comissao = comissao_pct  / preco * 100
    pct_imposto  = imposto_spike / preco * 100
    pct_custo    = custo_e_taxa  / preco * 100
    pct_lucro    = lucro         / preco * 100

    nome = str(row["Nome"])

    componentes = [
        ("Comissão Shopee (%)",       comissao_pct,  pct_comissao, "#E67E22"),
        ("Imposto + Spike Day",       imposto_spike, pct_imposto,  "#C0392B"),
        ("Custo + Taxa Fixa Shopee",  custo_e_taxa,  pct_custo,    "#7B2FBE"),
        ("Lucro Líquido",             lucro,         pct_lucro,    "#1DB954"),
    ]

    # Monta as fatias da pizza usando conic-gradient (CSS puro)
    cumul = 0.0
    slices = []
    for _, _, pct, cor in componentes:
        start = cumul
        end = cumul + pct
        slices.append(f"{cor} {start:.4f}% {end:.4f}%")
        cumul = end
    conic = ", ".join(slices)

    # Legenda à direita do donut
    legenda_html = ""
    for label, valor, pct, cor in componentes:
        legenda_html += (
            f"<div style=\"display:flex; align-items:center; gap:10px; "
            f"margin:8px 0; padding:8px 12px; background:#0f0120; "
            f"border-left:3px solid {cor}; border-radius:4px;\">"
            f"<span style=\"display:inline-block; width:14px; height:14px; "
            f"background:{cor}; border-radius:3px; flex-shrink:0;\"></span>"
            f"<span style=\"flex:1; color:#e8d5ff; font-size:0.9rem;\">{label}</span>"
            f"<span style=\"color:{cor}; font-weight:700; font-size:0.92rem; "
            f"min-width:90px; text-align:right;\">{fmt_brl(valor)}</span>"
            f"<span style=\"color:#c8a8e9; font-size:0.85rem; "
            f"min-width:55px; text-align:right;\">{pct:.1f}%</span>"
            f"</div>"
        )

    html = (
        "<div style=\"background:#1f063b; border:1px solid #7B2FBE; "
        "border-radius:10px; padding:18px 20px; margin:18px 0;\">"
        "<div style=\"color:#D4AF37; font-weight:700; font-size:1rem; "
        "margin-bottom:4px;\">"
        f"🥧 Como o preço de {fmt_brl(preco)} é composto"
        "</div>"
        "<div style=\"color:#c8a8e9; font-size:0.82rem; margin-bottom:18px;\">"
        f"Primeiro produto da tabela: <b style=\"color:#e8d5ff\">{nome}</b>"
        " &nbsp;·&nbsp; Total <b style=\"color:#D4AF37\">100%</b>"
        "</div>"
        "<div style=\"display:flex; gap:32px; align-items:center; "
        "flex-wrap:wrap; justify-content:center;\">"
        f"<div style=\"width:230px; height:230px; border-radius:50%; "
        f"background:conic-gradient({conic}); position:relative; "
        "flex-shrink:0; box-shadow:0 4px 24px rgba(212, 175, 55, 0.25); "
        "border:2px solid #D4AF37;\">"
        "<div style=\"position:absolute; top:50%; left:50%; "
        "transform:translate(-50%, -50%); width:120px; height:120px; "
        "border-radius:50%; background:#1f063b; "
        "display:flex; flex-direction:column; align-items:center; "
        "justify-content:center; border:1px solid #3d1562; "
        "box-shadow:inset 0 2px 10px rgba(0, 0, 0, 0.4);\">"
        "<div style=\"font-size:0.7rem; color:#c8a8e9; "
        "text-transform:uppercase; letter-spacing:0.5px;\">Preço Alvo</div>"
        f"<div style=\"font-size:1.05rem; font-weight:700; color:#D4AF37; "
        f"margin-top:2px;\">{fmt_brl(preco)}</div>"
        "</div>"
        "</div>"
        f"<div style=\"flex:1; min-width:300px;\">{legenda_html}</div>"
        "</div>"
        # ── Caixa "Como funciona" ────────────────────────────────────────
        "<div style=\"margin-top:18px; padding:14px 16px; background:#0f0120; "
        "border-left:3px solid #1DB954; border-radius:6px; color:#c8a8e9; "
        "font-size:0.82rem; line-height:1.6;\">"
        "<div style=\"color:#1DB954; font-weight:700; font-size:0.95rem; "
        "margin-bottom:8px;\">ℹ️ Como funciona o cálculo</div>"
        # Linha 1: explicação da lógica
        "<div style=\"margin-bottom:10px;\">"
        "O cálculo é uma <b style=\"color:#D4AF37;\">regra de três</b> simples: "
        "o preço de venda é uma pizza de <b>100%</b> dividida em 4 fatias. "
        f"O <b style=\"color:#1DB954;\">Lucro Líquido</b> é "
        f"<b style=\"color:#1DB954;\">{margem_real * 100:.1f}% do preço total</b> "
        f"= <b style=\"color:#1DB954;\">{fmt_brl(lucro)}</b>, garantido por construção "
        "(é uma fatia limpa da pizza)."
        "</div>"
        # Linha 2: break-even REAL (preço onde lucro = 0)
        "<div style=\"padding:8px 10px; background:#1f063b; border-radius:4px;\">"
        "<b style=\"color:#E67E22;\">⚖️ Break-Even (preço de equilíbrio):</b> "
        f"<b style=\"color:#D4AF37;\">{fmt_brl(break_even)}</b>. "
        "Esse é o <b>preço mínimo</b> que você teria que cobrar para cobrir "
        "exatamente todas as despesas (custo do produto + comissão Shopee + "
        "imposto), <b>sem ganhar e nem perder nada</b>."
        "<div style=\"margin-top:6px; font-size:0.78rem; color:#a98ec9;\">"
        "Vender <b style=\"color:#E74C3C;\">abaixo</b> disso = prejuízo. "
        f"Vender <b style=\"color:#1DB954;\">acima</b> disso = lucro positivo. "
        f"No preço atual de <b>{fmt_brl(preco)}</b>, seu lucro líquido é "
        f"<b style=\"color:#1DB954;\">{fmt_brl(lucro)}</b> "
        f"({margem_real * 100:.1f}% do preço)."
        "</div>"
        "</div>"
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


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
            "Break-Even (R$)": r.preco_break_even,
            "Fake Price (R$)": r.fake_price,
            "Lucro (R$)": r.lucro,
            "Comissão Shopee (R$)": r.comissao_shopee,
            "Taxa Fixa Shopee (R$)": r.taxa_fixa_shopee,
            "Imposto (R$)": r.imposto_valor,
            "Margem Real": r.margem_real,
            "Viável": r.viavel,
        })

    return pd.DataFrame(rows)


# ── Exportação Excel ──────────────────────────────────────────────────────────
def generate_excel(
    df: pd.DataFrame,
    margem: float,
    desconto_promo: float,
    aliquota: float,
    spike_day: bool = False,
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

    # ── Linhas 2-5: Parâmetros ──
    params = [
        ("Margem Desejada", f"{margem*100:.1f}%"),
        ("Desconto Promocional (Fake Price)", f"{desconto_promo*100:.1f}%"),
        ("Imposto sobre Receita", f"{aliquota*100:.2f}%"),
        ("Spike Day", "Ativo" if spike_day else "—"),
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

    ws.row_dimensions[6].height = 6   # espaço

    # ── Linha 7: Cabeçalhos da tabela ──
    data_cols = [
        "ID Produto", "Nome", "Custo (R$)", "Preço Alvo (R$)",
        "Fake Price (R$)", "Lucro (R$)",
        "Comissão Shopee (R$)", "Status",
    ]
    for col_idx, col_name in enumerate(data_cols, start=1):
        cell = ws.cell(row=7, column=col_idx, value=col_name)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = center_align
        cell.border = thin_gold
    ws.row_dimensions[7].height = 22

    # ── Linhas de dados ──
    currency_num = '#,##0.00'
    pct_num      = '0.0"%"'

    for row_idx, (_, row) in enumerate(df.iterrows(), start=8):
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
    ws.freeze_panes = "A8"

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
        "Margem (%)", min_value=5, max_value=80, value=10, step=1,
        label_visibility="collapsed",
        help="Margem sobre o preço total de venda. Ex: 10% = o lucro será 10% do preço cobrado (uma fatia limpa da pizza).",
    )

    st.markdown("**Desconto Fake Price**")
    promo_pct = st.slider(
        "Promo (%)", min_value=0, max_value=50, value=10, step=1,
        label_visibility="collapsed",
        help="Percentual de desconto aparente. O preço riscado será: Preço Alvo ÷ (1 - desconto%)",
    )

    st.markdown("**Imposto sobre Receita**")
    aliquota_pct = st.slider(
        "Imposto (%)", min_value=0, max_value=50, value=10, step=1,
        label_visibility="collapsed",
        help="Alíquota de imposto sobre a receita bruta (ex: Simples Nacional, Lucro Presumido)",
    )

    st.divider()
    st.markdown("**Taxa Spike Day**")
    spike_day = st.toggle(
        "Spike Day (+3,5%)",
        value=False,
        help="Taxa adicional cobrada pela Shopee em produtos participantes do Spike Day. Adiciona 3,5% sobre a receita bruta.",
    )
    spike_day_rate = 0.035 if spike_day else 0.0

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
        "• <code style='color:#e8d5ff'>ID</code><br>"
        "• <code style='color:#e8d5ff'>Custo</code> (valor numérico em R$)<br>"
        "<b style='color:#D4AF37'>Colunas opcionais:</b><br>"
        "• <code style='color:#e8d5ff'>Nome</code>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Aviso de privacidade ──────────────────────────────────────────────────────
st.markdown(
    "<div style='background:#1f063b; border-left: 4px solid #D4AF37; "
    "border-radius:6px; padding:10px 14px; color:#c8a8e9; font-size:0.82rem; "
    "margin-top: 12px;'>"
    "🔒 <b style='color:#D4AF37'>Privacidade:</b> "
    "seus dados de custo <b>não são armazenados</b>. "
    "Eles são usados apenas para o cálculo e descartados ao atualizar a página."
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
            aliquota_imposto=aliquota + spike_day_rate,
        )

        # ── Tabela de resultados ────────────────────────────────────────────
        st.markdown(
            section_header("Tabela de Preços Calculados", "📋"),
            unsafe_allow_html=True,
        )

        # Parâmetros exibidos como badges
        badges_html = (
            f"Parâmetros ativos: "
            + badge_html(f"Margem {margem_pct}%")
            + " &nbsp; "
            + badge_html(f"Promo {promo_pct}%", "#7B2FBE")
            + " &nbsp; "
            + badge_html(f"Imposto {aliquota_pct:.1f}%", "#1a7a4a")
        )
        if spike_day:
            badges_html += " &nbsp; " + badge_html("Spike Day +3,5%", "#E67E22")
        st.markdown(badges_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Formata o DataFrame para exibição
        display_df = df_results.drop(
            columns=[
                "Viável", "Break-Even (R$)", "Taxa Fixa Shopee (R$)",
                "Imposto (R$)", "Margem Real",
            ]
        ).copy()

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

        # ── Breakdown de custos do primeiro produto ────────────────────────
        if len(df_results) > 0:
            render_cost_breakdown(df_results.iloc[0])

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
            spike_day=spike_day,
        )

        col_dl, col_info = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="⬇️ Baixar Excel",
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
