"""
Tabela de taxas da Shopee Brazil.
Baseado na tabela oficial: comissão percentual + taxa fixa por faixa de preço.
O Subsídio Pix é pago pela Shopee ao comprador — não afeta a receita do vendedor.
"""

from dataclasses import dataclass
from typing import Optional
import math


@dataclass
class ShopeeFeeTier:
    price_min: float
    price_max: float  # math.inf para a última faixa
    commission_pct: float   # ex: 0.14 para 14%
    fixed_fee: float        # em R$
    pix_subsidy_pct: float  # informativo apenas (pago pela Shopee)


SHOPEE_FEE_TIERS: list[ShopeeFeeTier] = [
    ShopeeFeeTier(0.0,    79.99,  0.20,  4.50,  0.0),
    ShopeeFeeTier(80.0,   99.99,  0.14, 16.00,  0.05),
    ShopeeFeeTier(100.0, 199.99,  0.14, 20.00,  0.05),
    ShopeeFeeTier(200.0, 499.99,  0.14, 26.00,  0.05),
    ShopeeFeeTier(500.0, math.inf, 0.14, 26.00, 0.08),
]


def get_fee_tier(price: float) -> Optional[ShopeeFeeTier]:
    """Retorna a faixa de taxa correta para um dado preço."""
    for tier in SHOPEE_FEE_TIERS:
        if tier.price_min <= price <= tier.price_max:
            return tier
    return None


def calculate_commission(price: float) -> tuple[float, float]:
    """
    Retorna (valor_comissao, pix_subsidy_pct) para um dado preço.
    Levanta ValueError se o preço for inválido.
    """
    tier = get_fee_tier(price)
    if tier is None:
        raise ValueError(f"Preço R${price:.2f} fora das faixas suportadas.")
    commission = price * tier.commission_pct + tier.fixed_fee
    return commission, tier.pix_subsidy_pct


# ── TikTok Shop Brasil ────────────────────────────────────────────────────────
# Tabela vigente desde 15/07/2026: comissão percentual + taxa fixa por item,
# calculadas sobre o preço após os descontos dados pelo próprio vendedor.
# Programa de Frete Grátis (opcional): +6% sobre o preço, limitado a R$ 50/item.
TIKTOK_FEE_TIERS: list[ShopeeFeeTier] = [
    ShopeeFeeTier(0.0,  49.99,    0.10, 4.00, 0.0),
    ShopeeFeeTier(50.0, math.inf, 0.06, 6.00, 0.0),
]

TIKTOK_FRETE_GRATIS_PCT = 0.06
TIKTOK_FRETE_GRATIS_TETO = 50.00


# ── Registro de marketplaces ──────────────────────────────────────────────────
@dataclass
class Marketplace:
    chave: str
    nome: str
    emoji: str
    tiers: list[ShopeeFeeTier]
    nome_ads: str                       # nome da ferramenta de anúncios
    tabela_referencia: list[dict]       # linhas da tabela exibida no app
    nota_referencia: str
    tem_spike_day: bool = False
    tem_frete_gratis: bool = False
    tem_diagnostico: bool = False


MARKETPLACES: dict[str, Marketplace] = {
    "shopee": Marketplace(
        chave="shopee",
        nome="Shopee",
        emoji="🛍️",
        tiers=SHOPEE_FEE_TIERS,
        nome_ads="Shopee Ads",
        tabela_referencia=[
            {"Faixa de Preço": "Até R$ 79,99",       "Comissão": "20% + R$ 4,50",  "Subsídio Pix": "—"},
            {"Faixa de Preço": "R$ 80 a R$ 99,99",   "Comissão": "14% + R$ 16,00", "Subsídio Pix": "5%"},
            {"Faixa de Preço": "R$ 100 a R$ 199,99", "Comissão": "14% + R$ 20,00", "Subsídio Pix": "5%"},
            {"Faixa de Preço": "R$ 200 a R$ 499,99", "Comissão": "14% + R$ 26,00", "Subsídio Pix": "5%"},
            {"Faixa de Preço": "Acima de R$ 500",    "Comissão": "14% + R$ 26,00", "Subsídio Pix": "8%"},
        ],
        nota_referencia="* O Subsídio Pix é pago pela Shopee ao comprador — não afeta a receita do vendedor.",
        tem_spike_day=True,
        tem_diagnostico=True,
    ),
    "tiktok": Marketplace(
        chave="tiktok",
        nome="TikTok Shop",
        emoji="🎵",
        tiers=TIKTOK_FEE_TIERS,
        nome_ads="TikTok Ads / GMV Max",
        tabela_referencia=[
            {"Faixa de Preço": "Até R$ 49,99",    "Comissão": "10% + R$ 4,00"},
            {"Faixa de Preço": "A partir de R$ 50", "Comissão": "6% + R$ 6,00"},
            {"Faixa de Preço": "Frete Grátis (opcional)", "Comissão": "+6% (máx. R$ 50 por item)"},
        ],
        nota_referencia="* Taxas vigentes desde 15/07/2026, calculadas sobre o preço após os "
                        "descontos do vendedor. Confira sempre no Seller Center do TikTok Shop.",
        tem_frete_gratis=True,
    ),
}
