"""
Gera a base SIMULADA de ocorrências de zeladoria usada pelo Zela Aí.

Fonte dos dados: dados simulados pela equipe (semente fixa = reprodutível).
As categorias reproduzem tipos de serviço de zeladoria do SP156, canal de
solicitações da Prefeitura de São Paulo, cujos registros são publicados em
http://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156
Gravidade, apoios e tempos de atendimento são estimativas da equipe:
a base pública do SP156 não traz essas colunas. Nenhum dado pessoal é usado.

Uso: python gerar_dados.py   -> cria dados/ocorrencias_simuladas.csv
"""

import csv
import os
import random
from datetime import date, timedelta

# categoria: (tempo mínimo, tempo máximo em blocos de 30 min,
#             gravidade mínima, gravidade máxima)
CATEGORIAS = {
    "Tapa-buraco":                         (2, 4, 3, 5),
    "Iluminação pública (lâmpada apagada)": (1, 2, 2, 4),
    "Remoção de entulho / descarte irregular": (2, 5, 2, 4),
    "Limpeza de boca de lobo":             (2, 4, 3, 5),
    "Poda de árvore":                      (3, 6, 1, 4),
    "Reparo de calçada":                   (3, 6, 2, 4),
}
BAIRROS = ["Aclimação", "Cambuci", "Liberdade", "Vila Mariana"]


def gerar_ocorrencias(qtd: int, data_inicial: date, dias_janela: int,
                      rng: random.Random, prefixo: str = "OC") -> list[dict]:
    linhas = []
    for i in range(1, qtd + 1):
        categoria = rng.choice(list(CATEGORIAS))
        t_min, t_max, g_min, g_max = CATEGORIAS[categoria]
        # apoios: a maioria tem poucos, alguns problemas "viralizam" no bairro
        apoios = min(int(rng.expovariate(1 / 4)), 25)
        linhas.append({
            "id": f"{prefixo}{i:03d}",
            "data_registro": (data_inicial + timedelta(days=rng.randint(0, dias_janela))).isoformat(),
            "categoria": categoria,
            "bairro": rng.choice(BAIRROS),
            "gravidade": rng.randint(g_min, g_max),
            "apoios": apoios,
            "tempo_blocos": rng.randint(t_min, t_max),
        })
    return linhas


def salvar_csv(linhas: list[dict], caminho: str) -> None:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)


if __name__ == "__main__":
    rng = random.Random(42)
    # 40 ocorrências abertas, registradas entre 28/10 e 17/11/2026
    linhas = gerar_ocorrencias(40, date(2026, 10, 28), 20, rng)
    linhas.sort(key=lambda l: (l["data_registro"], l["id"]))
    for i, l in enumerate(linhas, 1):           # id segue a ordem de chegada
        l["id"] = f"OC{i:03d}"
    pasta = os.path.dirname(os.path.abspath(__file__))
    salvar_csv(linhas, os.path.join(pasta, "dados", "ocorrencias_simuladas.csv"))
    print(f"{len(linhas)} ocorrências salvas em dados/ocorrencias_simuladas.csv")
