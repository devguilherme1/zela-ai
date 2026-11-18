"""Simula uma semana de atendimento para comparar as estratégias de priorização."""

import random
from datetime import date, timedelta

from gerar_dados import gerar_ocorrencias
from priorizacao import JORNADA_BLOCOS, Ocorrencia, resumo


def _para_ocorrencias(linhas: list[dict]) -> list[Ocorrencia]:
    return [Ocorrencia(l["id"], date.fromisoformat(l["data_registro"]), l["categoria"],
                       l["bairro"], l["gravidade"], l["apoios"], l["tempo_blocos"])
            for l in linhas]


def simular_semana(backlog_inicial: list[Ocorrencia], estrategia, inicio: date,
                   dias: int = 5, novas_por_dia: int = 6, semente: int = 7,
                   capacidade: int = JORNADA_BLOCOS) -> dict:
    """Cada dia: chegam novas ocorrências, a estratégia escolhe o que atender
    dentro da jornada e o restante continua aberto (ficando mais antigo)."""
    rng = random.Random(semente)            # mesma chegada para todas as estratégias
    abertas = list(backlog_inicial)
    impacto, atendidas, espera = 0, 0, []
    for d in range(dias):
        hoje = inicio + timedelta(days=d)
        if d > 0:
            novas = gerar_ocorrencias(novas_por_dia, hoje, 0, rng, prefixo=f"D{d}-")
            abertas += _para_ocorrencias(novas)
        _, escolhidas = estrategia(abertas, capacidade, hoje)
        r = resumo(escolhidas, hoje)
        impacto += r["impacto_total"]
        atendidas += r["atendidas"]
        espera += [o.dias_aberta(hoje) for o in escolhidas]
        ids = {o.id for o in escolhidas}
        abertas = [o for o in abertas if o.id not in ids]
    return {
        "impacto_total": impacto,
        "atendidas": atendidas,
        "graves_ainda_abertas": sum(1 for o in abertas if o.gravidade >= 4),
        "espera_media_dias": round(sum(espera) / len(espera), 1) if espera else 0,
    }
