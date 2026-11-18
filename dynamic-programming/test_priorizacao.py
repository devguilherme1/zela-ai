"""Testes do algoritmo de priorização. Rodar com:  python -m pytest -v"""

import random
from datetime import date, timedelta

from priorizacao import (DATA_REFERENCIA, Ocorrencia, calcular_impacto, forca_bruta,
                         guloso_razao, mochila_dp, mochila_dp_valor)


def oc(id_, gravidade, apoios, dias, tempo):
    return Ocorrencia(id_, DATA_REFERENCIA - timedelta(days=dias), "Teste", "Teste",
                      gravidade, apoios, tempo)


def aleatorias(rng, n):
    return [oc(f"R{i}", rng.randint(1, 5), rng.randint(0, 15), rng.randint(0, 40),
               rng.randint(1, 6)) for i in range(n)]


def test_impacto_respeita_limites():
    assert calcular_impacto(5, 0, 0) == 50
    assert calcular_impacto(1, 100, 100) == 10 + 30 + 30   # apoios e dias têm teto


def test_lista_vazia_e_capacidade_zero():
    assert mochila_dp([], 16) == (0, [])
    assert mochila_dp([oc("A", 5, 5, 5, 2)], 0) == (0, [])


def test_ocorrencia_maior_que_a_jornada_nao_entra():
    valor, escolhidas = mochila_dp([oc("A", 5, 10, 30, 20)], 16)
    assert valor == 0 and escolhidas == []


def test_contraexemplo_guloso():
    # A rende mais por bloco, mas B + C juntas valem mais e cabem na mesma jornada
    a, b, c = oc("A", 5, 3, 1, 3), oc("B", 3, 2, 2, 2), oc("C", 3, 2, 2, 2)
    assert guloso_razao([a, b, c], 4)[0] == 60
    valor, escolhidas = mochila_dp([a, b, c], 4)
    assert valor == 76 and [o.id for o in escolhidas] == ["B", "C"]


def test_dp_igual_forca_bruta_em_300_casos_aleatorios():
    rng = random.Random(2026)
    for _ in range(300):
        ocorrencias = aleatorias(rng, rng.randint(1, 10))
        capacidade = rng.randint(0, 20)
        valor_dp, escolhidas = mochila_dp(ocorrencias, capacidade)
        assert valor_dp == forca_bruta(ocorrencias, capacidade)[0]
        # a reconstrução é coerente: cabe na jornada e soma o valor ótimo
        assert sum(o.tempo_blocos for o in escolhidas) <= capacidade
        assert sum(o.impacto() for o in escolhidas) == valor_dp
        assert len({o.id for o in escolhidas}) == len(escolhidas)   # sem repetição


def test_versao_otimizada_em_memoria_da_o_mesmo_valor():
    rng = random.Random(7)
    for _ in range(200):
        ocorrencias = aleatorias(rng, rng.randint(0, 40))
        capacidade = rng.randint(0, 32)
        assert mochila_dp_valor(ocorrencias, capacidade) == mochila_dp(ocorrencias, capacidade)[0]


def test_dp_nunca_perde_para_o_guloso():
    rng = random.Random(99)
    for _ in range(300):
        ocorrencias = aleatorias(rng, rng.randint(1, 30))
        assert mochila_dp(ocorrencias, 16)[0] >= guloso_razao(ocorrencias, 16)[0]


def test_ocorrencia_antiga_ganha_prioridade():
    nova, antiga = oc("N", 3, 0, 0, 2), oc("V", 3, 0, 25, 2)
    assert mochila_dp([nova, antiga], 2)[1][0].id == "V"
