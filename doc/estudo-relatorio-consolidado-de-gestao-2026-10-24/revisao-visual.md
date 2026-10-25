# Relatório consolidado — revisão visual do PDF (24/10/2026)

**Pedido**: o usuário reprovou o PDF da primeira entrega do PR #331 — números corretos, documento
de outra natureza: indicadores em tabela partida entre páginas, gráfico substituído por duas
linhas, títulos sozinhos no pé, endereços `localhost`. Pediu a correção da apresentação, sem
reimplementar a consolidação, com critérios verificáveis de fidelidade à maquete.

**Comparação lado a lado**: [`comparacao-visual.pdf`](comparacao-visual.pdf) — maquete aprovada ×
PDF anterior × PDF atual, página a página. **PDF atual**, emitido pelo endpoint do GPS:
[`relatorio-consolidado-demonstracao.pdf`](relatorio-consolidado-demonstracao.pdf).

## 1. Matriz de diferenças (antes desta rodada)

| # | Aspecto | Maquete | PDF anterior | Origem da diferença | Agora |
|---|---|---|---|---|---|
| 1 | Cabeçalho e identidade | órgão em três linhas compactas | brasão de 42 pt centralizado, quatro linhas | **composição** | brasão de 30 pt à esquerda das três linhas, com fio |
| 2 | Título e subtítulo | "Relatório Consolidado de Gestão dos Processos Seletivos"; período em azul | "RELATÓRIO CONSOLIDADO DA UNIDADE" em caixa alta | **texto** | o título da maquete, 16,5 pt; período e quantidade de Editais em azul |
| 3 | Hierarquia tipográfica | título, seção com fio, rótulo pequeno cinza, valor em negrito | tudo no corpo de texto, títulos só em negrito | **composição** | quatro níveis (16,5 · 11,5 com fio · 9,8 · 7,8 cinza) |
| 4 | Indicadores | seis cartões, 3 × 2, na primeira página | tabela de três colunas, o sexto na página 2 | **composição** | seis cartões inteiros na primeira página, com "de N apuradas/realizadas" |
| 5 | Gráficos | barras de envio por mês | tabela de dois meses | **composição** (o motor não desenha barra) | barras com o número escrito e texto alternativo; frase com um mês; ausência dita |
| 6 | Tabelas | fio escuro sob o cabeçalho, fios claros | grade completa com cabeçalho cinza | **composição** | sem grade: fio escuro sob o cabeçalho, claro entre linhas |
| 7 | Colunas | oferta × procura; situação × alterações; resultados × vagas | tudo empilhado | **composição** | os três pares lado a lado, sem se partirem |
| 8 | Espaçamentos | ritmo regular, blocos respiram | espaços do texto corrido do Edital | **composição** | espaço próprio por bloco, que some no alto da página |
| 9 | Quebras de página | anexo em página própria; nenhum grupo partido | tabela de indicadores partida; "Anexo técnico" sozinho no pé; tabela por Edital entre páginas | **composição** | grupos atômicos; título leva o começo do conteúdo; tabela continua com cabeçalho repetido; anexo abre página |
| 10 | Seções executivas e anexo | painel; seções; anexo | mesma ordem, sem distinção visual | **composição** | painel com ficha, cartões e faixa âmbar de atenção; anexo com título de nível 1 |
| 11 | Legibilidade | faixa no alto de toda página | rodapé denso | **composição** | faixa no alto (conjunto · dados · emissão) e pé (natureza · página), sem sobreposição |
| 12 | Consistência visual | uma paleta (tinta, azul, âmbar) | preto e um cinza | **composição** | a paleta da maquete |
| — | Links | — | `http://localhost:8100/…` impressos | **ambiente** | emissão local diz que os endereços não estão disponíveis; em host público, o link abre a seleção |
| — | Acessibilidade | PDF estruturado (Chrome) | sem estrutura | **composição** | PDF marcado: títulos, parágrafos, listas, tabelas, figura com texto alternativo; artefatos |

**Diferenças que vêm dos dados, e não são defeito**: 12 Editais fictícios na maquete, seis na
demonstração; a série da demonstração cai em agosto e setembro porque o cenário coerente tem as
datas de inscrição fixas — só a publicação muda de mês. É a nota da série dizendo, de verdade, que
os meses podem passar do período que escolheu os Editais.

## 2. Causa técnica

A maquete foi escrita em HTML/CSS e impressa pelo Chrome. O PDF do GPS foi composto pelo escritor do
Edital (`publicacoes/infrastructure/pdf.py`), que é um **paginador de texto corrido**: empilha
linhas, e só desenha o que esse fluxo pede — grade de tabela, moldura de bloco, um tom de cinza. Não
há posição livre, coluna, cor, cartão nem barra. A primeira entrega aceitou essa limitação para
reaproveitar o escritor; os testes verificavam número, determinismo e privacidade, e nenhum
verificava a composição.

## 3. Alternativas de composição

| | Fidelidade | Paginação | Determinismo | Acessibilidade | Dependência | Manutenção |
|---|---|---|---|---|---|---|
| **A.** aperfeiçoar o escritor do Edital | alta, com muito trabalho | herdada | sim | não marcado | nenhuma | **muda o escritor dos atos oficiais** e os resumos que o comprovante promete |
| **B.** HTML/CSS impresso (Chrome ou WeasyPrint) | máxima | do navegador | **não** no Chrome (`/CreationDate`, `/ID`) | marcado | **nova**: binário de ~300 MB ou Pango/Cairo | duas tecnologias de documento |
| **C.** compositor próprio sobre as peças do escritor | alta (ver comparação) | própria, com grupos | sim | **marcado** | nenhuma | um módulo de ~900 linhas, isolado |

**Escolhida: C** — `interface/diagramacao.py`. B exigiria a decisão do usuário antes, por ser
dependência nova; C chegou ao resultado sem ela. A decisão está na spec (D-010) e na pesquisa (R-013).

## 4. O que mudou

- `interface/diagramacao.py` (novo): blocos, paginação por grupos, arquivo marcado.
- `interface/relatorio_consolidado_pdf.py`: reescrito sobre os blocos, na organização da maquete.
- `interface/relatorio_consolidado.py`: o título; o subconjunto dito por extenso ("conta 4 dos 5
  Editais — fora 1 Edital, com 2 vagas e menos de 5 inscrições"); as vagas fora dele.
- `interface/relatorio.py`: em host local, nenhum endereço no PDF, e a frase que o diz.
- Telas de gestão com o título novo.
- Cenário de teste com título, nomes de Perfil e vagas do segundo Perfil parametrizados; demonstração
  com sete Editais de natureza diferente (tutores, formadores, bolsista, cursistas, designer; 4 a
  362 inscrições; cancelado; só cadastro de reserva; vagas não apuradas; resultado incompleto).
- Requisitos novos: FR-2593 a FR-2600 e SC-946.

**Nada mudou na consolidação**: as regras de vagas, inscrições, razão, resultados, convocações,
cancelados, privacidade e ausência são as da primeira entrega, e os testes delas não mudaram de
afirmação (só de redação, onde a frase do subconjunto mudou).

## 5. Testes de regressão visual

`tests/unit/interface/test_diagramacao_do_consolidado.py`, com conjuntos de 1, 5, 12 e 60 Editais:

| Critério do pedido | Caso |
|---|---|
| 1. Primeira página com os indicadores e a atenção | `test_a_primeira_pagina_e_o_painel_inteiro` |
| 2. Cartão não se parte | `test_cartao_e_grupo_nao_se_partem` |
| 3. Título não fica no rodapé | `test_titulo_nunca_fica_sozinho_no_pe` |
| 4. Gráfico quando há dados | `test_o_grafico_aparece_quando_ha_meses_para_comparar` |
| 5. Tabela longa paginada | `test_tabela_longa_continua_com_o_cabecalho_repetido` |
| 6. Sem sobreposição nem corte | `test_blocos_cabem_na_pagina_e_nao_se_sobrepoem`; `Tela._conferir` recusa texto fora da área útil na própria composição |
| 7. Links adequados ao ambiente | `test_links_so_quando_o_endereco_vale_para_quem_recebe` |
| 8. Identificação e emissão em toda página | `test_toda_pagina_diz_o_conjunto_a_data_e_a_emissao` |
| 9. Poucos e muitos Editais | `test_poucos_e_muitos_editais_mantem_o_painel_e_o_anexo_em_pagina_propria` e a parametrização |
| 10. A4, impressão e leitura digital | `test_a4_marcado_e_deterministico` (A4, marcado, idioma, figura com texto alternativo, mesmos bytes) |

**Inspeção a olho**: as cinco páginas do PDF emitido foram renderizadas (`pdftoppm`) e comparadas com
a maquete — é a comparação visual anexa. A estrutura foi lida por `pdfinfo -struct-text`: a ordem de
leitura é a do documento (cabeçalho, título, ficha, seções, cartões, tabelas, figura).

## 6. Riscos e limitações que restam

- **A marcação é a básica**: títulos, listas, tabelas e figura. Não foi validada por PAC 3 nem por
  leitor de tela real; o próximo passo de acessibilidade é essa validação.
- **A fonte é a do Edital** (Liberation Sans, subconjunto WinAnsi). Texto fora do WinAnsi recusa a
  emissão, como no Edital.
- **A maquete foi feita no navegador**, e a composição própria aproxima, sem reproduzir pixel a pixel:
  o espaçamento e as quebras dos cartões são do compositor.
- **O cenário de demonstração tem a mesma linha do tempo de inscrições** em todos os Editais; a
  série por mês da demonstração fica em dois meses por isso, e não por limitação do relatório.
- **O relatório individual (`099`) continua no escritor do Edital**, e também imprime o endereço do
  host da requisição: o mesmo tratamento de host local cabe lá, e fica registrado aqui, não feito.
