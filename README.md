# Desempenho na Copa do Mundo vs. Indicadores Socioeconômicos ⚽📊

Este projeto investiga se fatores estruturais e socioeconômicos de um país — especificamente o desenvolvimento econômico e o nível educacional — possuem correlação direta com o sucesso esportivo de suas seleções na história da Copa do Mundo da FIFA.

O estudo completo detalhando as hipóteses, metodologias e análises qualitativas pode ser encontrado no arquivo `Desempenho na Copa do Mundo versus Indicadores Socioeconômicos.pdf` incluído neste repositório.

## 📌 Problema Analisado
Será que o poder financeiro de uma nação ou o investimento na base educacional de seus jovens conseguem prever ou explicar o aproveitamento de uma seleção de futebol no maior torneio do mundo? 

## 🛠️ Tecnologias e Ferramentas
* **Python 3.x**
* **Pandas:** Para manipulação, limpeza e tratamento dos dados.
* **Matplotlib & Seaborn:** Para visualização de dados e plotagem de gráficos estatísticos.
* **wbgapi (World Bank API):** Para extração automatizada de indicadores macroeconômicos globais em tempo real.
* **adjustText:** Para organização inteligente dos rótulos nos gráficos, evitando sobreposição de textos.

## 📊 Indicadores e Métricas Utilizadas
1. **Aproveitamento (%)**: Calculado como `Pontos Conquistados / (Jogos Disputados * 3)`. Essa métrica padroniza o desempenho, permitindo comparações justas entre seleções com volumes diferentes de jogos.
2. **PIB per capita (`NY.GDP.PCAP.CD`)**: Quantidade média de riqueza produzida por habitante (em USD atual).
3. **Educação (`SE.SEC.ENRR`)**: Taxa bruta de matrícula no ensino médio (%). Valores acima de 100% indicam alta participação e ampla capacidade de atendimento do sistema (incluindo distorções idade-série e educação de adultos).

## 🗂️ Estrutura dos Códigos
O projeto foi segmentado em 4 scripts principais focando em dois recortes temporais e de performance (pós-1960/1990):

1. `pib_campeoes.py`: Analisa estritamente o PIB per capita dos **Campeões Mundiais** no ano do título.
2. `pib_elite.py`: Analisa o PIB per capita de todas as seleções que atingiram a **Elite da Copa** (aproveitamento superior a 60%).
3. `educacao_campeoes.py`: Investiga a taxa de matrícula no ensino médio apenas das seleções **Campeãs Mundiais**.
4. `educacao_elite.py`: Investiga a taxa de matrícula no ensino médio de todas as seleções da **Elite**.

> *Nota: O repositório também conta com um script estruturado para carregar, processar e unificar essa base de dados automaticamente para o **Power BI**, permitindo a criação de dashboards dinâmicos.*

## 💡 Principais Insights obtidos
* **Relação Fraca com o PIB:** O poder econômico isolado mostrou alta dispersão estatística. Países de PIB baixo (como o histórico Brasil de 1962, 1970 e 2002) alcançaram o topo do mundo tanto quanto nações de altíssima renda (Alemanha de 2014).
* **Tendência Consistente na Educação:** O nível educacional apresentou uma convergência muito mais forte. As grandes potências modernas e campanhas de elite concentram-se fortemente no quadrante de países com taxas de escolaridade superiores a 100%.
* **Fatores Multifatoriais (Outliers):** O talento individual e fatores culturais (como as gerações fora da curva do Brasil em 1994 e 2002) são capazes de romper temporariamente a barreira dos indicadores estruturais, embora a tendência contemporânea valorize cada vez mais a organização e a infraestrutura de base.

## 🚀 Como Rodar o Projeto

1. Clone este repositório:
   ```bash
   git clone [https://github.com/tatohi/copaVSeconomia.git](https://github.com/tatohi/copaVSeconomia.git)
   ```

2. Instale as dependências necessárias:

  ```bash
  pip install pandas matplotlib seaborn wbgapi adjustText
  ```

Certifique-se de manter o arquivo WorldCupMatches.csv na mesma pasta dos scripts (ou altere o caminho de leitura no código).

Execute qualquer um dos scripts para gerar os gráficos interativos na tela.
