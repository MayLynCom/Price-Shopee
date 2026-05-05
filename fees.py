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
    ShopeeFeeTier(0.0,    79.99,  0.20,  4.00,  0.0),
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
