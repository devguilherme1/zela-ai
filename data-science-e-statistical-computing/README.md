# Zela Aí — Data Science & Statistical Computing

Análise descritiva das solicitações de zeladoria do SP156 (Prefeitura de São Paulo) para a CitizenTech **Zela Aí**. Global Solution 2026.2, Engenharia de Software, FIAP.

## Integrantes

| Nome | RM |
|---|---|
| Gabriel Cutrim | 568059 |
| Guilherme Pereira | 567487 |
| Gustavo Firmino | 566903 |

## Repositório do projeto

https://github.com/devguilherme1/zela-ai

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `zelaai_data_science.ipynb` | Notebook executado: contexto e perguntas, preparação, análise descritiva, gráficos e conclusões |
| `zelaai_sp156_zeladoria_3tri2026.csv` | Base usada: 113.995 solicitações de zeladoria (jul–set/2026) |
| `integrantes.txt` | Nomes, RMs e link do CSV (entrega no Teams) |

## Fonte dos dados

Portal de Dados Abertos da Prefeitura de São Paulo, conjunto **Dados do SP156 - Solicitações**, arquivo *Dados do SP156 - 3° TRI 2026*. A extração da Prefeitura é de 19/10/2026.
https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156

O CSV deste repositório é um recorte do arquivo oficial: só os serviços de zeladoria, agrupados em 6 categorias, sem logradouro, número e CEP. A função `gerar_recorte()` do notebook refaz o recorte a partir do arquivo original. A base é pública e anonimizada pela Prefeitura, e nenhum dado pessoal foi usado.

## Requisitos

- Python **3.10** ou mais recente
- Bibliotecas:
  - `pandas` ≥ 2.0
  - `numpy` ≥ 1.24
  - `matplotlib` ≥ 3.10 (versões mais antigas não aceitam o parâmetro `orientation` do gráfico de caixas)
  - `jupyter` (só para execução local)

O notebook foi testado com Python 3.13, pandas 3.0, numpy 2.5 e matplotlib 3.11.

## Como executar

### Opção A: Google Colab (sem instalar nada)

1. Acesse [colab.research.google.com](https://colab.research.google.com) e entre com uma conta Google.
2. Vá em **Arquivo → Fazer upload de notebook** e escolha `zelaai_data_science.ipynb`.
3. Na barra lateral esquerda, clique no ícone de **pasta** e depois em **Fazer upload para o armazenamento da sessão**. Envie `zelaai_sp156_zeladoria_3tri2026.csv` e espere o upload terminar (26 MB).
4. Vá em **Ambiente de execução → Executar tudo** (Ctrl+F9).

O arquivo enviado no passo 3 é apagado quando a sessão do Colab termina. Ao reabrir o notebook outro dia, envie o CSV de novo.

### Opção B: no computador (Jupyter ou VS Code)

1. Coloque `zelaai_data_science.ipynb` e `zelaai_sp156_zeladoria_3tri2026.csv` na mesma pasta.
2. Abra um terminal nessa pasta e (opcional, mas recomendado) crie um ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS / Linux
   ```
3. Instale as bibliotecas:
   ```bash
   pip install pandas numpy matplotlib jupyter
   ```
4. Abra o notebook:
   ```bash
   jupyter notebook zelaai_data_science.ipynb
   ```
   No VS Code, basta abrir o arquivo `.ipynb`, escolher o interpretador Python do passo 2 como kernel e clicar em **Run All**.
5. Execute todas as células em ordem (**Kernel → Restart & Run All**).

## O que esperar da execução

- A execução completa leva menos de 1 minuto.
- São exibidas as tabelas de estatística descritiva e 8 gráficos, organizados pelas perguntas de negócio P1 a P6.
- Ao final, o notebook gera o arquivo `parametros_categoria.csv` na mesma pasta (tempo de resolução, pendência e repetição por categoria).

### Estrutura do notebook

| Seção | Conteúdo |
|---|---|
| 1. Contexto e perguntas | Problema da CitizenTech e as 6 perguntas de negócio |
| 2. Base de dados | Fonte, recorte e dicionário de colunas |
| 3. Preparação | Tipos, datas, coordenadas, subprefeituras e variáveis derivadas |
| 4. Análise descritiva | P1 a P6: frequências, medidas de tendência central e dispersão, gráficos |
| 5. Da análise para a solução | Parâmetros por categoria exportados para `parametros_categoria.csv` |
| 6. Conclusões | Respostas às perguntas e limitações da análise |

### Refazer o recorte a partir da base oficial (opcional)

O CSV entregue já é o recorte pronto. Para gerá-lo de novo a partir do arquivo original da Prefeitura (cerca de 106 MB), descomente a linha `gerar_recorte()` na primeira célula de código e execute. É preciso ter conexão com a internet.

## Problemas comuns

| Erro | Causa e solução |
|---|---|
| `FileNotFoundError: zelaai_sp156_zeladoria_3tri2026.csv` | O CSV não está na mesma pasta do notebook (ou não foi enviado ao Colab). Confira o nome e a pasta. |
| `TypeError: ... unexpected keyword argument 'orientation'` | Matplotlib antigo. Rode `pip install -U matplotlib` (no Colab: `!pip install -U matplotlib`), reinicie o kernel e execute tudo de novo. |
| `NameError` em alguma célula | As células foram executadas fora de ordem. Use **Restart & Run All**. |
| Acentos estranhos ao abrir o CSV no Excel | Use **Dados → De Texto/CSV** e escolha a codificação UTF-8. No notebook, a leitura já é feita corretamente. |
