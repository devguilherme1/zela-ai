"""Gera o relatório em PDF (até 4 páginas) da entrega de Dynamic Programming.

EDITE OS DADOS DA CAPA ABAIXO e rode:  python relatorio/gerar_relatorio.py
(requer reportlab: pip install reportlab; rode antes o notebook para gerar img/)
"""

# ======================= DADOS DA CAPA — EDITAR =======================
EQUIPE = "Zela Aí"
INTEGRANTES = [                     # ordem alfabética
    ("Gabriel Cutrim", "RM568059"),
    ("Guilherme Pereira", "RM567487"),
    ("Gustavo Firmino", "RM566903"),
]
TURMA = "2ESPS · Engenharia de Software"
LINK_REPOSITORIO = "https://github.com/devguilherme1/zela-ai"
# ======================================================================

import os
import random
import sys
import time
from datetime import timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)

from reportlab.lib import colors                                   # noqa: E402
from reportlab.lib.enums import TA_CENTER                          # noqa: E402
from reportlab.lib.pagesizes import A4                             # noqa: E402
from reportlab.lib.styles import ParagraphStyle                    # noqa: E402
from reportlab.lib.units import cm                                 # noqa: E402
from reportlab.pdfbase import pdfmetrics                           # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont                       # noqa: E402
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,  # noqa: E402
                                Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

from priorizacao import (DATA_REFERENCIA, JORNADA_BLOCOS, ESTRATEGIAS, Ocorrencia,  # noqa: E402
                         carregar_csv, guloso_razao, mochila_dp, mochila_dp_valor, resumo)
from simulacao import simular_semana                                # noqa: E402

# ---------- fontes (DejaVu tem ≥, ×, ∅; cai para Helvetica se não houver) ----------
FONTES = "/usr/share/fonts/truetype/dejavu/"
try:
    pdfmetrics.registerFont(TTFont("Sans", FONTES + "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("Sans-B", FONTES + "DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Sans-I", FONTES + "DejaVuSans-Oblique.ttf"))
    pdfmetrics.registerFont(TTFont("Mono", FONTES + "DejaVuSansMono.ttf"))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-B")
    SANS, SANS_B, MONO = "Sans", "Sans-B", "Mono"
except Exception:
    SANS, SANS_B, MONO = "Helvetica", "Helvetica-Bold", "Courier"

VINHO = colors.HexColor("#8c1d40")
CINZA = colors.HexColor("#5b6470")
CLARO = colors.HexColor("#f3eef0")

st = {
    "h1": ParagraphStyle("h1", fontName=SANS_B, fontSize=14, leading=18, textColor=VINHO,
                         spaceBefore=4, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName=SANS_B, fontSize=10.5, leading=14, spaceBefore=6, spaceAfter=3),
    "p": ParagraphStyle("p", fontName=SANS, fontSize=9, leading=12.6, spaceAfter=4),
    "cel": ParagraphStyle("cel", fontName=SANS, fontSize=8, leading=10.4),
    "celb": ParagraphStyle("celb", fontName=SANS_B, fontSize=8, leading=10.4, textColor=colors.white),
    "cap": ParagraphStyle("cap", fontName=SANS, fontSize=7.5, leading=10, textColor=CINZA,
                          alignment=TA_CENTER, spaceAfter=4),
    "dest": ParagraphStyle("dest", fontName=SANS_B, fontSize=9.5, leading=13, textColor=VINHO,
                           backColor=CLARO, borderPadding=(6, 8, 6, 8), spaceBefore=6, spaceAfter=10),
    "code": ParagraphStyle("code", fontName=MONO, fontSize=7.3, leading=9.2, backColor=CLARO,
                           borderPadding=6, spaceBefore=2, spaceAfter=8),
}


def P(t, s="p"):
    return Paragraph(t, st[s])


def tabela(linhas, larguras, cab=True):
    dados = [[P(str(c), "celb" if (cab and i == 0) else "cel") for c in l] for i, l in enumerate(linhas)]
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=1 if cab else 0)
    estilo = [("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d5d0d3")),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if cab:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), VINHO))
    t.setStyle(TableStyle(estilo))
    return t


def figura(nome, largura_cm=17):
    caminho = os.path.join(RAIZ, "img", nome)
    return Image(caminho, width=largura_cm * cm, height=largura_cm * cm * 608 / 1760)


# ---------- números calculados ao vivo (mesmos do notebook) ----------
ocorrencias = carregar_csv(os.path.join(RAIZ, "dados", "ocorrencias_simuladas.csv"))
comp = {}
for nome, f in ESTRATEGIAS.items():
    comp[nome] = (resumo(f(ocorrencias, JORNADA_BLOCOS)[1]),
                  simular_semana(ocorrencias, f, DATA_REFERENCIA))
dp_dia = comp["Programação Dinâmica"][0]["impacto_total"]
fifo_dia = comp["Fila (ordem de chegada)"][0]["impacto_total"]


def oc(id_, grav, apoios, dias, tempo, cat="-"):
    return Ocorrencia(id_, DATA_REFERENCIA - timedelta(days=dias), cat, "-", grav, apoios, tempo)


rng = random.Random(1)
perdas = []
for _ in range(2000):
    inst = [oc(f"X{i}", rng.randint(1, 5), rng.randint(0, 15), rng.randint(0, 30), rng.randint(1, 6))
            for i in range(rng.randint(5, 30))]
    otimo = mochila_dp_valor(inst, JORNADA_BLOCOS)
    perdas.append((otimo - guloso_razao(inst, JORNADA_BLOCOS)[0]) / otimo)
erros = [p for p in perdas if p > 0]
pior_guloso = f"{max(erros):.1%}".replace(".", ",")

rng = random.Random(3)
grande = [oc(f"B{i}", rng.randint(1, 5), rng.randint(0, 15), rng.randint(0, 30), rng.randint(1, 6))
          for i in range(2000)]
t0 = time.perf_counter(); mochila_dp(grande, JORNADA_BLOCOS); ms_2000 = (time.perf_counter() - t0) * 1000

# ---------- documento ----------
story = []

# Página 1 — Capa
story += [Spacer(1, 3 * cm),
          P("FIAP · GLOBAL SOLUTION 2026.2 · CITIZENTECH", "cap"),
          Paragraph("Dynamic Programming", ParagraphStyle("t0", fontName=SANS, fontSize=13,
                    textColor=CINZA, alignment=TA_CENTER, leading=18)),
          Spacer(1, 0.4 * cm),
          Paragraph("Zela Aí", ParagraphStyle("t1", fontName=SANS_B, fontSize=34, leading=40,
                    textColor=VINHO, alignment=TA_CENTER)),
          Paragraph("Priorização de ocorrências de zeladoria com o Problema da Mochila 0/1",
                    ParagraphStyle("t2", fontName=SANS, fontSize=12.5, leading=17, alignment=TA_CENTER)),
          Spacer(1, 2 * cm)]
capa = [["Integrante", "RM"]] + [list(i) for i in INTEGRANTES]
t = tabela(capa, [10, 4])
t.hAlign = "CENTER"
story += [P(f"<b>Equipe:</b> {EQUIPE}", "cap"), Spacer(1, 0.2 * cm), t, Spacer(1, 1 * cm),
          P(f"<b>CitizenTech:</b> Zela Aí · {TURMA}", "cap"),
          P(f"<b>Repositório:</b> {LINK_REPOSITORIO} (pasta <i>dynamic-programming/</i>)", "cap"),
          Spacer(1, 4.5 * cm),
          P("São Paulo · novembro de 2026", "cap"),
          PageBreak()]

# Página 2 — Problema
story += [P("1. Problema", "h1"),
          P("O <b>Zela Aí</b> é a CitizenTech da equipe: uma plataforma em que moradores da região central "
            "de São Paulo (Aclimação, Cambuci, Liberdade e Vila Mariana) registram problemas da rua, como "
            "buracos, lâmpadas apagadas, entulho e bocas de lobo entupidas. Os vizinhos apoiam os registros "
            "e todos acompanham o atendimento."),
          P(f"O problema que a CitizenTech enfrenta todos os dias é de <b>escolha sob tempo limitado</b>. A "
            f"base tem {len(ocorrencias)} ocorrências abertas, que somam "
            f"{sum(o.tempo_blocos for o in ocorrencias) / 2:.0f} horas de trabalho, mas a equipe de zeladoria "
            f"tem {JORNADA_BLOCOS / 2:.0f} horas por dia. Quando o atendimento segue a ordem de chegada, um "
            f"buraco perigoso registrado ontem espera atrás de uma poda simples registrada na semana passada."),
          P("Quais ocorrências a equipe deve atender hoje para resolver o maior impacto possível "
            "para os moradores, sem passar da jornada?", "dest"),
          P("Essa pergunta é exatamente o <b>Problema da Mochila 0/1</b>:"),
          tabela([["Mochila 0/1", "Zela Aí"],
                  ["Capacidade da mochila (W)", f"Jornada da equipe: {JORNADA_BLOCOS} blocos de 30 min (8 h)"],
                  ["Item", "Ocorrência aberta"],
                  ["Peso do item", "Tempo estimado de atendimento, em blocos de 30 min"],
                  ["Valor do item", "Pontuação de impacto para os moradores"],
                  ["Decisão 0/1", "A ocorrência é resolvida inteira hoje, ou fica para outro dia"]],
                 [5.5, 11.5]),
          P("Pontuação de impacto", "h2"),
          P("<b>impacto = 10 × gravidade + 3 × min(apoios, 10) + min(dias em aberto, 30)</b>. A gravidade "
            "(1 a 5) pesa mais. Os apoios dos vizinhos mostram quantas pessoas são afetadas. Os dias em "
            "aberto garantem que nenhuma ocorrência fique esquecida, porque quanto mais ela espera, mais "
            "pontos ganha. É uma regra inteira e simples, que o app pode mostrar ao morador para explicar "
            "por que um pedido veio antes do outro."),
          P("Fonte dos dados", "h2"),
          P("A base <i>dados/ocorrencias_simuladas.csv</i> tem 40 ocorrências <b>simuladas</b> pela equipe "
            "(script <i>gerar_dados.py</i>, semente fixa, reprodutível). As categorias reproduzem serviços "
            "de zeladoria do <b>SP156</b>, o canal de solicitações da Prefeitura de São Paulo, cujos "
            "registros são públicos em dados.prefeitura.sp.gov.br/dataset/dados-do-sp156. Gravidade, apoios "
            "e tempo de atendimento são estimativas da equipe, porque são funcionalidades do Zela Aí e não "
            "existem na base pública. Não há nenhum dado pessoal."),
          P("2. Modelagem: estruturas de dados escolhidas e por quê", "h1"),
          tabela([["Estrutura", "Onde é usada", "Por quê"],
                  ["dataclass Ocorrencia", "Cada registro",
                   "Agrupa os campos com nome e concentra o cálculo de impacto() num só lugar."],
                  ["Lista (array)", "Ocorrências, pesos e valores",
                   "O DP acessa o item i por índice em O(1) a cada célula da tabela."],
                  ["Matriz dp[i][w]", "Tabela da programação dinâmica",
                   "Guarda cada subproblema uma única vez. Os (n+1)×(W+1) resultados nunca são recalculados."],
                  ["Vetor dp[w]", "Versão otimizada (só o valor)",
                   "Cada linha só depende da anterior, então a memória cai de O(n·W) para O(W)."],
                  ["Pilha", "Reconstrução da resposta",
                   "A volta pela tabela encontra as escolhas de trás para frente. Desempilhar devolve a ordem original."],
                  ["Fila (deque)", "Estratégia de comparação",
                   "Modela o atendimento atual por ordem de chegada (FIFO), com popleft() em O(1)."]],
                 [3.6, 4.2, 9.2]),
          ]

# Página 3 — Modelagem (DP) + Algoritmo
story += [KeepTogether([P("Por que programação dinâmica", "h2"),
          P("O problema tem as duas propriedades que a técnica exige. Ele tem <b>subestrutura ótima</b>: a "
            "melhor escolha com <i>i</i> ocorrências e <i>w</i> blocos é construída a partir da melhor escolha "
            "com <i>i−1</i> ocorrências. E tem <b>subproblemas sobrepostos</b>: a força bruta testa "
            "2<super>n</super> combinações e recalcula os mesmos pedaços muitas vezes, enquanto o DP resolve "
            "cada par (<i>i</i>, <i>w</i>) uma única vez. A recorrência é:"),
          P("dp[i][w] = dp[i−1][w]    se t<sub>i</sub> &gt; w (a ocorrência i não cabe)<br/>"
            "dp[i][w] = max( dp[i−1][w] ,  v<sub>i</sub> + dp[i−1][w − t<sub>i</sub>] )    caso contrário", "dest")]),
          P("3. Algoritmo: ideia central apontada no código", "h1"),
          P("Trecho resumido da função <i>mochila_dp</i> em <i>priorizacao.py</i>. No repositório, os mesmos "
            "três comentários <b>IDEIA CENTRAL</b> marcam essas partes do código completo. "
            "t<sub>i</sub> é o tempo e v<sub>i</sub> o impacto da ocorrência i."),
          Preformatted(
              "# IDEIA CENTRAL (1): subproblemas.\n"
              "# dp[i][w] = maior impacto usando só as i primeiras ocorrências com no máximo w blocos.\n"
              "dp = [[0] * (capacidade + 1) for _ in range(n + 1)]\n"
              "for i in range(1, n + 1):\n"
              "    peso, valor = pesos[i - 1], valores[i - 1]\n"
              "    for w in range(capacidade + 1):\n"
              "        # IDEIA CENTRAL (2): escolha ótima em cada passo.\n"
              "        dp[i][w] = dp[i - 1][w]                       # Opção A: NÃO atender\n"
              "        if peso <= w:                                 # Opção B: atender, se couber\n"
              "            dp[i][w] = max(dp[i][w], valor + dp[i - 1][w - peso])\n"
              "\n"
              "# IDEIA CENTRAL (3): reconstrução. Se dp[i][w] != dp[i-1][w], a ocorrência i entrou.\n"
              "pilha, w = [], capacidade\n"
              "for i in range(n, 0, -1):\n"
              "    if dp[i][w] != dp[i - 1][w]:\n"
              "        pilha.append(ocorrencias[i - 1]); w -= pesos[i - 1]\n"
              "escolhidas = [pilha.pop() for _ in range(len(pilha))]   # desempilha: ordem original",
              st["code"]),
          P("Exemplo de entrada e saída: por que não basta ser guloso", "h2"),
          P("Com uma jornada de 4 blocos (2 h) e três ocorrências, o guloso escolhe primeiro a de maior "
            "impacto por bloco (A). Ela ocupa 3 blocos e o bloco que sobra não serve para mais nada. "
            "O DP percebe que B e C juntas cabem e valem mais."),
          tabela([["Ocorrência", "Categoria", "Tempo", "Impacto", "Impacto/bloco"],
                  ["A", "Tapa-buraco", "3", "60", "20,0"],
                  ["B", "Limpeza de boca de lobo", "2", "38", "19,0"],
                  ["C", "Iluminação pública", "2", "38", "19,0"],
                  ["<b>Saída</b>", "<b>Guloso: {A} → 60</b>", "", "<b>DP: {B, C} → 76</b>", "<b>+27%</b>"]],
                 [2.4, 5.6, 2, 3.6, 3.4]),
          Spacer(1, 4),
          P("Tabela dp[i][w] desse exemplo. A resposta é a célula final (76). A reconstrução sobe pelas "
            "células destacadas: C entra (76 ≠ 38), depois B entra (38 ≠ 0) e A fica de fora."),
          ]
t = tabela([["", "w=0", "w=1", "w=2", "w=3", "w=4"],
            ["∅", "0", "0", "0", "0", "0"],
            ["+A", "0", "0", "0", "60", "60"],
            ["+B", "0", "0", "<b>38</b>", "60", "60"],
            ["+C", "0", "0", "38", "60", "<b>76</b>"]], [1.6] * 6)
t.setStyle(TableStyle([("BACKGROUND", (3, 3), (3, 3), CLARO), ("BACKGROUND", (5, 4), (5, 4), CLARO)]))
t.hAlign = "LEFT"
story += [t, PageBreak()]

# Página 4 — Resultados, eficiência e conclusões
linhas = [["Estratégia", "Impacto em 1 dia", "Atendidas no dia", "Impacto na semana",
           "Graves abertas após 5 dias", "Espera média (dias)"]]
for nome, (dia, sem) in comp.items():
    linhas.append([nome, dia["impacto_total"], dia["atendidas"], sem["impacto_total"],
                   sem["graves_ainda_abertas"], str(sem["espera_media_dias"]).replace(".", ",")])
story += [P("Resultado com as 40 ocorrências da base", "h2"),
          tabela(linhas, [4.2, 2.5, 2.4, 2.6, 2.8, 2.5]),
          Spacer(1, 4),
          figura("comparacao.png", 16),
          P(f"Com a mesma equipe e as mesmas 8 horas, o DP resolve {dp_dia / fifo_dia - 1:.0%} mais impacto "
            f"que o atendimento por ordem de chegada. Na simulação de uma semana, com 6 novas ocorrências por "
            f"dia, ele deixa menos problemas graves esperando. O guloso chega perto nesta base, mas sem "
            f"garantia: em 2.000 cenários aleatórios ele ficou abaixo do ótimo em "
            f"{len(erros) / len(perdas):.0%} deles, com perda de até {pior_guloso}, e no exemplo da "
            f"página anterior perdeu 21%. O DP nunca perde, como os testes confirmam."),
          P("Eficiência e complexidade", "h2"),
          tabela([["Estratégia", "Tempo", "Memória", "Ótimo garantido?"],
                  ["Força bruta (todas as combinações)", "O(2<super>n</super> · n)", "O(n)", "Sim, mas inviável"],
                  ["Fila por ordem de chegada / Guloso", "O(n log n)", "O(n)", "Não"],
                  ["<b>Programação Dinâmica (tabela + reconstrução)</b>", "<b>O(n · W)</b>", "<b>O(n · W)</b>", "<b>Sim</b>"],
                  ["Programação Dinâmica (vetor, só o valor)", "O(n · W)", "O(W)", "Sim"]],
                 [7.4, 3.2, 3.0, 3.4]),
          Spacer(1, 4),
          figura("eficiencia.png", 16),
          P(f"Com W = 16 fixo, o DP é linear em n na prática: {len(grande)} ocorrências são resolvidas em "
            f"cerca de {ms_2000:.0f} ms, enquanto a força bruta já passa de 100 ms com apenas 18. A complexidade "
            "é <i>pseudo-polinomial</i> porque depende do valor de W. Por isso o tempo foi discretizado em "
            "blocos de 30 minutos: em minutos, W = 480 deixaria a tabela 30 vezes maior sem ganho real."),
          P("<b>Testes</b> (<i>test_priorizacao.py</i>, 8 testes, todos passando): o DP é comparado com a "
            "força bruta em 300 cenários aleatórios, a resposta reconstruída é conferida (cabe na jornada e "
            "soma o ótimo) e são cobertos os casos-limite (lista vazia, jornada zero, ocorrência maior que a "
            "jornada) e o contraexemplo do guloso. <b>Limitações:</b> tempos e gravidades são estimativas, e "
            "o DP é ótimo para cada dia, não para a semana inteira. Próximos passos: usar tempos reais e "
            "estender para várias equipes (mochilas múltiplas)."),
          ]


def rodape(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont(SANS, 7)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.1 * cm, f"Zela Aí · Dynamic Programming · {EQUIPE}")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"{doc.page}")
    canvas.restoreState()


saida = os.path.join(AQUI, "Relatorio_DP_Zela_Ai.pdf")
doc = SimpleDocTemplate(saida, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                        title="Zela Aí · Dynamic Programming", author=EQUIPE)
doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
print("PDF gerado:", saida)
