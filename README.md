# Zela Aí · CitizenTech

**Global Solution 2026.2 · FIAP · Engenharia de Software · Turma 2ESPS**

| Integrante | RM |
|---|---|
| Gabriel Cutrim | RM568059 |
| Guilherme Pereira | RM567487 |
| Gustavo Firmino | RM566903 |

## Ficha da CitizenTech

| Campo | Resposta |
|---|---|
| **Nome da CitizenTech** | Zela Aí |
| **Cidade e bairro** | São Paulo · Aclimação, Cambuci, Liberdade e Vila Mariana |
| **Cidadão beneficiado** | Morador do bairro que convive com buracos, lâmpadas apagadas, entulho e bocas de lobo entupidas |
| **Problema, em uma frase** | O morador vê o problema na rua, mas não sabe se alguém já reclamou, não acompanha o andamento e não entende por que outros pedidos são atendidos antes do dele. |
| **Como funciona** | O morador registra a ocorrência, os vizinhos apoiam ("eu também") e o sistema prioriza o atendimento de forma transparente, mostrando o andamento até a resolução. |
| **Link do repositório** | https://github.com/devguilherme1/zela-ai |
| **Indicador de impacto** | Impacto resolvido por dia de equipe e tempo médio até a resolução das ocorrências |
| **ODS conectados** | ODS 11 (Cidades e comunidades sustentáveis), ODS 9 (Indústria, inovação e infraestrutura), ODS 10 (Redução das desigualdades) |

## Dynamic Programming · priorização com a Mochila 0/1

A equipe de zeladoria tem **8 horas por dia** e muitas ocorrências abertas. O algoritmo escolhe **quais atender hoje para resolver o maior impacto possível** sem passar da jornada. Isso é o **Problema da Mochila 0/1**, resolvido com programação dinâmica em **O(n · W)**.

| Mochila 0/1 | Zela Aí |
|---|---|
| Capacidade | Jornada da equipe: 16 blocos de 30 min (8 h) |
| Item | Ocorrência aberta |
| Peso | Tempo estimado de atendimento |
| Valor | Impacto = 10 × gravidade + 3 × apoios (até 10) + dias em aberto (até 30) |

**Resultado com a base de 40 ocorrências:** o DP resolve **30% mais impacto** que o atendimento por ordem de chegada, com a mesma equipe e as mesmas 8 horas.

### Onde está cada coisa
| Arquivo | Conteúdo |
|---|---|
| [`dynamic-programming/priorizacao.py`](dynamic-programming/priorizacao.py) | Algoritmo principal (`mochila_dp`) |
| [`dynamic-programming/priorizacao_zela_ai.ipynb`](dynamic-programming/priorizacao_zela_ai.ipynb) | Notebook com o cenário, a fonte dos dados, exemplos, comparação e eficiência |
| [`dynamic-programming/test_priorizacao.py`](dynamic-programming/test_priorizacao.py) | 8 testes automatizados |
| [`dynamic-programming/dados/`](dynamic-programming/dados/) | Base de ocorrências simuladas (CSV) |
| [`dynamic-programming/relatorio/`](dynamic-programming/relatorio/) | Relatório em PDF |

### Como executar
```bash
cd dynamic-programming
pip install pandas matplotlib pytest
python -m pytest -v
```

**Fonte dos dados:** base simulada pela equipe, com categorias baseadas nos serviços de zeladoria do SP156 da Prefeitura de São Paulo ([Portal de Dados Abertos](http://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156)). Não há nenhum dado pessoal.
