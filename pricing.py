"""
Motor de precificação para Shopee.

Fórmula fechada por faixa de taxa:
    P = [f × (1 - m) + C] / [(1 - t - i) - m × (1 - t)]

Onde:
    P = preço de venda alvo
    C = custo total (produto + sobretaxa de peso)
    t = comissão percentual da Shopee (ex: 0.14)
    f = taxa fixa da Shopee (ex: R$26)
    i = imposto sobre receita bruta
    m = margem desejada (ex: 0.30 para 30%)

Como a faixa de taxa depende do preço, resolve-se P para cada faixa
e verifica se o resultado cai dentro daquele intervalo.
"""

import math
from dataclasses import dataclass
from typing import Optional

from fees import SHOPEE_FEE_TIERS, ShopeeFeeTier


TAX_RATES = {
    "MEI": 0.0,
    "Simples Nacional": None,   # alíquota definida pelo usuário
    "Lucro Presumido": 0.0673,
}


@dataclass
class PricingResult:
    produto_id: str
    nome_produto: str
    custo: float
    preco_venda: float
    fake_price: float
    comissao_shopee: float
    imposto_valor: float
    lucro: float
    margem_real: float          # percentual 0-1
    pix_subsidy_pct: float
    tier: ShopeeFeeTier
    viavel: bool                # False se não há solução válida


def calcular_preco(
    produto_id: str,
    nome_produto: str,
    custo_produto: float,
    sobretaxa_peso: float,
    margem_desejada: float,     # 0 a 1
    desconto_promo: float,      # 0 a 1  — para calcular fake_price
    aliquota_imposto: float,    # 0 a 1
) -> PricingResult:
    """
    Calcula o preço de venda ideal para atingir a margem desejada após
    todas as taxas da Shopee e impostos.

    Tenta cada faixa de taxa em ordem. Usa o resultado da primeira faixa
    cujo P calculado cai dentro do intervalo da faixa.
    """
    C = custo_produto + sobretaxa_peso
    m = margem_desejada
    i = aliquota_imposto

    best: Optional[PricingResult] = None

    for tier in SHOPEE_FEE_TIERS:
        t = tier.commission_pct
        f = tier.fixed_fee

        denominador = (1 - t - i) - m * (1 - t)

        if abs(denominador) < 1e-9:
            continue

        P = (f * (1 - m) + C) / denominador

        if P < 0:
            continue

        dentro_da_faixa = tier.price_min <= P <= tier.price_max

        if dentro_da_faixa:
            return _build_result(
                produto_id, nome_produto, C, P, m, i, t, f,
                desconto_promo, tier, viavel=True,
            )

        # Guarda o melhor candidato fora da faixa para fallback
        if best is None and P > 0:
            best = _build_result(
                produto_id, nome_produto, C, P, m, i, t, f,
                desconto_promo, tier, viavel=False,
            )

    # Nenhuma faixa se encaixou — retorna o fallback com viavel=False
    if best:
        return best

    # Caso extremo: custo zero ou parâmetros impossíveis
    return PricingResult(
        produto_id=produto_id,
        nome_produto=nome_produto,
        custo=C,
        preco_venda=0.0,
        fake_price=0.0,
        comissao_shopee=0.0,
        imposto_valor=0.0,
        lucro=0.0,
        margem_real=0.0,
        pix_subsidy_pct=0.0,
        tier=SHOPEE_FEE_TIERS[0],
        viavel=False,
    )


def _build_result(
    produto_id: str,
    nome_produto: str,
    C: float,
    P: float,
    m: float,
    i: float,
    t: float,
    f: float,
    desconto_promo: float,
    tier: ShopeeFeeTier,
    viavel: bool,
) -> PricingResult:
    comissao = P * t + f
    imposto_valor = P * i
    receita_liquida = P - comissao
    lucro = receita_liquida - C - imposto_valor
    margem_real = lucro / receita_liquida if receita_liquida > 0 else 0.0

    fake_price = P / (1 - desconto_promo) if desconto_promo < 1.0 else P

    return PricingResult(
        produto_id=produto_id,
        nome_produto=nome_produto,
        custo=C,
        preco_venda=round(P, 2),
        fake_price=round(fake_price, 2),
        comissao_shopee=round(comissao, 2),
        imposto_valor=round(imposto_valor, 2),
        lucro=round(lucro, 2),
        margem_real=round(margem_real, 4),
        pix_subsidy_pct=tier.pix_subsidy_pct,
        tier=tier,
        viavel=viavel,
    )


def calcular_lote(
    produtos: list[dict],
    sobretaxa_peso: float,
    margem_desejada: float,
    desconto_promo: float,
    aliquota_imposto: float,
) -> list[PricingResult]:
    """
    Processa uma lista de dicts com chaves: id, nome, custo, peso_extra_kg (opt).
    """
    resultados = []
    for p in produtos:
        sobretaxa = sobretaxa_peso * p.get("peso_extra_kg", 0.0)
        r = calcular_preco(
            produto_id=str(p.get("id", "")),
            nome_produto=str(p.get("nome", "")),
            custo_produto=float(p.get("custo", 0.0)),
            sobretaxa_peso=sobretaxa,
            margem_desejada=margem_desejada,
            desconto_promo=desconto_promo,
            aliquota_imposto=aliquota_imposto,
        )
        resultados.append(r)
    return resultados
