"""
Motor de precificação para Shopee.

Lógica: regra de três sobre o preço total ("Forma A").

O preço de venda é uma "pizza de 100%" dividida em fatias percentuais
que somam exatamente 100%:

    100% = Comissão% + Imposto% + Margem% + TACOS% + Afiliado%
           + (Custo + Taxa Fixa)%

Resolvendo para P:

    P = (C + f) / (1 - t - i - m - tacos - afil)

Onde:
    P     = preço de venda alvo
    C     = custo total (produto + sobretaxa de peso)
    t     = comissão percentual da Shopee (ex: 0.14)
    f     = taxa fixa da Shopee (ex: R$26) — agrupada com o custo na pizza
    i     = imposto sobre receita bruta (inclui Spike Day se ativo)
    m     = margem desejada sobre o preço total (ex: 0.10 para 10% do preço)
    tacos = custo de anúncios (TACOS) sobre a receita (ex: 0.05)
    afil  = comissão de afiliado sobre a receita (ex: 0.03)

O lucro líquido é exatamente m × P (uma fatia limpa de m% do preço final).

O break-even REAL é o preço onde despesa = preço (lucro = 0):
    P_be = (C + f) / (1 − t − i − tacos − afil)
É um valor único: vender abaixo disso = prejuízo.

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
    preco_break_even: float     # preço onde lucro = 0 (despesa = preço)
    taxa_fixa_shopee: float     # parte fixa da comissão (R$, ex: R$ 26)
    fake_price: float
    comissao_shopee: float
    imposto_valor: float
    lucro: float
    margem_real: float          # percentual 0-1 (lucro sobre o preço total)
    pix_subsidy_pct: float
    tier: ShopeeFeeTier
    viavel: bool                # False se não há solução válida
    tacos_valor: float = 0.0    # valor de TACOS em R$
    afiliado_valor: float = 0.0  # valor de comissão de afiliado em R$


def calcular_preco(
    produto_id: str,
    nome_produto: str,
    custo_produto: float,
    sobretaxa_peso: float,
    margem_desejada: float,     # 0 a 1
    desconto_promo: float,      # 0 a 1  — para calcular fake_price
    aliquota_imposto: float,    # 0 a 1
    tacos_pct: float = 0.0,     # 0 a 1  — custo de anúncios (TACOS)
    afiliado_pct: float = 0.0,  # 0 a 1  — comissão de afiliado
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
    tacos = tacos_pct
    afil = afiliado_pct

    best: Optional[PricingResult] = None

    for tier in SHOPEE_FEE_TIERS:
        t = tier.commission_pct
        f = tier.fixed_fee

        denominador = 1 - t - i - m - tacos - afil

        if denominador <= 1e-9:
            continue

        P = (C + f) / denominador

        if P < 0:
            continue

        dentro_da_faixa = tier.price_min <= P <= tier.price_max

        if dentro_da_faixa:
            return _build_result(
                produto_id, nome_produto, C, P, m, i, t, f,
                desconto_promo, tier, viavel=True,
                tacos=tacos, afil=afil,
            )

        # Guarda o melhor candidato fora da faixa para fallback
        if best is None and P > 0:
            best = _build_result(
                produto_id, nome_produto, C, P, m, i, t, f,
                desconto_promo, tier, viavel=False,
                tacos=tacos, afil=afil,
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
        preco_break_even=0.0,
        taxa_fixa_shopee=0.0,
        fake_price=0.0,
        comissao_shopee=0.0,
        imposto_valor=0.0,
        lucro=0.0,
        margem_real=0.0,
        pix_subsidy_pct=0.0,
        tier=SHOPEE_FEE_TIERS[0],
        viavel=False,
        tacos_valor=0.0,
        afiliado_valor=0.0,
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
    tacos: float = 0.0,
    afil: float = 0.0,
) -> PricingResult:
    comissao = P * t + f
    imposto_valor = P * i
    lucro = P * m
    margem_real = m
    tacos_valor = P * tacos
    afiliado_valor = P * afil

    # Break-even REAL: preço onde lucro = 0 (despesa = preço).
    # P_be = (C + f) / (1 - t - i - tacos - afil)
    denom_be = 1 - t - i - tacos - afil
    preco_break_even = (C + f) / denom_be if denom_be > 1e-9 else 0.0

    fake_price = P / (1 - desconto_promo) if desconto_promo < 1.0 else P

    return PricingResult(
        produto_id=produto_id,
        nome_produto=nome_produto,
        custo=C,
        preco_venda=round(P, 2),
        preco_break_even=round(preco_break_even, 2),
        taxa_fixa_shopee=round(f, 2),
        fake_price=round(fake_price, 2),
        comissao_shopee=round(comissao, 2),
        imposto_valor=round(imposto_valor, 2),
        lucro=round(lucro, 2),
        margem_real=round(margem_real, 4),
        pix_subsidy_pct=tier.pix_subsidy_pct,
        tier=tier,
        viavel=viavel,
        tacos_valor=round(tacos_valor, 2),
        afiliado_valor=round(afiliado_valor, 2),
    )


def calcular_lote(
    produtos: list[dict],
    sobretaxa_peso: float,
    margem_desejada: float,
    desconto_promo: float,
    aliquota_imposto: float,
    tacos_pct: float = 0.0,
    afiliado_pct: float = 0.0,
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
            tacos_pct=tacos_pct,
            afiliado_pct=afiliado_pct,
        )
        resultados.append(r)
    return resultados
