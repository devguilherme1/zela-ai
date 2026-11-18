"""
Zela Aí — Priorização de ocorrências de zeladoria com Programação Dinâmica.

Problema: a equipe de zeladoria tem um número limitado de horas por dia.
Cada ocorrência (buraco, lâmpada apagada, entulho...) leva um tempo para ser
resolvida e tem um impacto para os moradores. Quais ocorrências atender hoje
para resolver o MAIOR impacto possível dentro do tempo disponível?

Isso é o Problema da Mochila 0/1 (0/1 Knapsack):
    - mochila  -> jornada da equipe (capacidade em blocos de 30 minutos)
    - item     -> ocorrência (peso = tempo, valor = impacto)
    - 0/1      -> cada ocorrência é atendida inteira ou não é atendida hoje
"""

from __future__ import annotations

import csv
from collections import deque
from dataclasses import dataclass
from datetime import date
from itertools import combinations
from typing import Iterable

BLOCO_MINUTOS = 30          # unidade de tempo do algoritmo
JORNADA_BLOCOS = 16         # 8 horas de equipe = 16 blocos de 30 min
DATA_REFERENCIA = date(2026, 11, 17)


@dataclass
class Ocorrencia:
    id: str
    data_registro: date
    categoria: str
    bairro: str
    gravidade: int        # 1 (incômodo) a 5 (risco à segurança)
    apoios: int           # vizinhos que confirmaram o problema ("eu também")
    tempo_blocos: int     # tempo estimado de atendimento, em blocos de 30 min

    def dias_aberta(self, hoje: date = DATA_REFERENCIA) -> int:
        return max(0, (hoje - self.data_registro).days)

    def impacto(self, hoje: date = DATA_REFERENCIA) -> int:
        return calcular_impacto(self.gravidade, self.apoios, self.dias_aberta(hoje))


def calcular_impacto(gravidade: int, apoios: int, dias_aberta: int) -> int:
    """Pontuação de impacto (inteira, transparente para o cidadão).

    - gravidade pesa mais: 10 pontos por nível (10 a 50)
    - apoios dos vizinhos: 3 pontos cada, limitado a 10 apoios (0 a 30)
    - tempo de espera: 1 ponto por dia aberta, limitado a 30 (0 a 30)
      -> evita que uma ocorrência fique esquecida para sempre
    """
    return 10 * gravidade + 3 * min(apoios, 10) + min(dias_aberta, 30)


def carregar_csv(caminho: str) -> list[Ocorrencia]:
    """Lê o CSV de ocorrências e devolve uma lista (acesso O(1) por índice)."""
    ocorrencias = []
    with open(caminho, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            ocorrencias.append(Ocorrencia(
                id=linha["id"],
                data_registro=date.fromisoformat(linha["data_registro"]),
                categoria=linha["categoria"],
                bairro=linha["bairro"],
                gravidade=int(linha["gravidade"]),
                apoios=int(linha["apoios"]),
                tempo_blocos=int(linha["tempo_blocos"]),
            ))
    return ocorrencias


# ---------------------------------------------------------------------------
# ALGORITMO PRINCIPAL — Mochila 0/1 com Programação Dinâmica (bottom-up)
# ---------------------------------------------------------------------------
def mochila_dp(ocorrencias: list[Ocorrencia], capacidade: int,
               hoje: date = DATA_REFERENCIA, devolver_tabela: bool = False):
    """Escolhe o conjunto de ocorrências de maior impacto total que cabe na jornada.

    Retorna (impacto_total, lista_de_ocorrencias_escolhidas[, tabela]).
    Tempo: O(n · W)   Memória: O(n · W)   (n = ocorrências, W = capacidade em blocos)
    """
    n = len(ocorrencias)
    pesos = [o.tempo_blocos for o in ocorrencias]
    valores = [o.impacto(hoje) for o in ocorrencias]

    # IDEIA CENTRAL (1): subproblemas.
    # dp[i][w] = maior impacto possível usando só as i primeiras ocorrências
    #            com no máximo w blocos de tempo.
    dp = [[0] * (capacidade + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        peso, valor = pesos[i - 1], valores[i - 1]
        for w in range(capacidade + 1):
            # IDEIA CENTRAL (2): escolha ótima em cada passo.
            # Opção A: NÃO atender a ocorrência i -> mesmo resultado de i-1.
            dp[i][w] = dp[i - 1][w]
            # Opção B: atender a ocorrência i (se couber) -> valor dela
            #          + melhor resultado com o tempo que sobra.
            if peso <= w:
                dp[i][w] = max(dp[i][w], valor + dp[i - 1][w - peso])

    # IDEIA CENTRAL (3): reconstrução. Volta pela tabela: se o valor mudou
    # de dp[i-1][w] para dp[i][w], a ocorrência i foi escolhida.
    # Usa uma PILHA porque a volta encontra as escolhas de trás para frente.
    pilha = []
    w = capacidade
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            pilha.append(ocorrencias[i - 1])
            w -= pesos[i - 1]
    escolhidas = []
    while pilha:
        escolhidas.append(pilha.pop())   # desempilha -> volta à ordem original

    if devolver_tabela:
        return dp[n][capacidade], escolhidas, dp
    return dp[n][capacidade], escolhidas


def mochila_dp_valor(ocorrencias: list[Ocorrencia], capacidade: int,
                     hoje: date = DATA_REFERENCIA) -> int:
    """Versão otimizada em memória: só o valor ótimo, com um vetor de W+1 posições.

    Tempo: O(n · W)   Memória: O(W).
    Percorre w de trás para frente para não reutilizar a mesma ocorrência duas vezes.
    """
    dp = [0] * (capacidade + 1)
    for o in ocorrencias:
        peso, valor = o.tempo_blocos, o.impacto(hoje)
        for w in range(capacidade, peso - 1, -1):
            dp[w] = max(dp[w], valor + dp[w - peso])
    return dp[capacidade]


# ---------------------------------------------------------------------------
# Estratégias de comparação
# ---------------------------------------------------------------------------
def fila_fifo(ocorrencias: list[Ocorrencia], capacidade: int,
              hoje: date = DATA_REFERENCIA):
    """Como costuma ser feito: atende por ordem de chegada (fila FIFO).
    Pula quem não cabe no tempo restante. Tempo: O(n log n) pela ordenação."""
    fila = deque(sorted(ocorrencias, key=lambda o: (o.data_registro, o.id)))
    restante, escolhidas = capacidade, []
    while fila:
        o = fila.popleft()
        if o.tempo_blocos <= restante:
            escolhidas.append(o)
            restante -= o.tempo_blocos
    return sum(o.impacto(hoje) for o in escolhidas), escolhidas


def guloso_razao(ocorrencias: list[Ocorrencia], capacidade: int,
                 hoje: date = DATA_REFERENCIA):
    """Heurística gulosa: maior impacto por bloco de tempo primeiro.
    Rápida (O(n log n)), mas NÃO garante o ótimo na mochila 0/1."""
    ordenadas = sorted(ocorrencias,
                       key=lambda o: o.impacto(hoje) / o.tempo_blocos, reverse=True)
    restante, escolhidas = capacidade, []
    for o in ordenadas:
        if o.tempo_blocos <= restante:
            escolhidas.append(o)
            restante -= o.tempo_blocos
    return sum(o.impacto(hoje) for o in escolhidas), escolhidas


def forca_bruta(ocorrencias: list[Ocorrencia], capacidade: int,
                hoje: date = DATA_REFERENCIA):
    """Testa todos os 2^n subconjuntos. Só serve para validar o DP com n pequeno."""
    melhor_valor, melhor = 0, []
    n = len(ocorrencias)
    for k in range(1, n + 1):
        for combo in combinations(ocorrencias, k):
            if sum(o.tempo_blocos for o in combo) <= capacidade:
                valor = sum(o.impacto(hoje) for o in combo)
                if valor > melhor_valor:
                    melhor_valor, melhor = valor, list(combo)
    return melhor_valor, melhor


ESTRATEGIAS = {
    "Fila (ordem de chegada)": fila_fifo,
    "Guloso (impacto/tempo)": guloso_razao,
    "Programação Dinâmica": mochila_dp,
}


def resumo(escolhidas: Iterable[Ocorrencia], hoje: date = DATA_REFERENCIA) -> dict:
    escolhidas = list(escolhidas)
    return {
        "atendidas": len(escolhidas),
        "blocos_usados": sum(o.tempo_blocos for o in escolhidas),
        "impacto_total": sum(o.impacto(hoje) for o in escolhidas),
        "graves_atendidas": sum(1 for o in escolhidas if o.gravidade >= 4),
    }
