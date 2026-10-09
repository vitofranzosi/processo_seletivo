# Verificação — 068, o que se repete por Perfil sai uma vez no Edital em PDF

Branch `claude/068-consolidacao-por-perfil`, sobre a `main` `2b698592` (a `067` mergeada, PR #268).
Bancos de validação novos, todos com dados fictícios: `ps_068_base` (migrado do zero, molde) e, por
`createdb -T`, `ps_068_a_antes`, `ps_068_a_depois`, `ps_068_b_antes`, `ps_068_b_depois`. Nenhum banco
de desenvolvimento, de demonstração ou de produção foi tocado. Banco de teste da suíte: `ps068`.

## Ponto de partida (T001, T002)

- Subconjunto `tests/unit/publicacoes tests/unit/editais tests/contract tests/integration/publicacoes
  tests/interface/test_compor_quadro.py tests/acceptance/test_us1_declaracao_unica_de_vagas.py`, contra
  PostgreSQL, na `main`: **2225 passados**, em 125 s.
- O guardião de bytes da `067` passava; os PDFs de `specs/067-…/demonstracao/` eram, byte a byte, os
  que a `main` compunha dos snapshots congelados da auditoria.
- **Cota inferior** do ganho (evidência 4 da spec), medida tirando o bloco repetido de todos os Perfis
  menos o primeiro, sem pôr nada no lugar (roteiro `medir.py`, no scratchpad da sessão):

  | Retirado | A: páginas / Perfis | B: páginas / Perfis |
  |---|---|---|
  | nada (a `main`) | 9 / 5 | 36 / 30 |
  | os marcos | 7 / 4 | 21 / 16 |
  | + quadro, modalidades e frases | 6 / 3 | 17 / 11 |
  | + requisitos | 6 / 2 | 13 / 8 |

  As metas da spec (SC-510: A ≤ 7 / ≤ 3; SC-511: B ≤ 18 / ≤ 12) partem daí, com folga para a tabela
  única, as remissões e as subseções comuns.

## Ordem de trabalho — registro honesto

Os testes da fase 2 e da US1 foram escritos antes do código e falharam contra a `main` (29 de 32; os 3
que passavam são de preservação: Edital de um Perfil, compor não muda o snapshot, quebra por pedaços).
O compositor das US1 a US3 foi escrito numa passada só, porque as três leem o mesmo plano; os testes da
US2 e da US3 vieram **logo depois** do código, e não antes. Eles falhariam contra a `main` — usam
`plano_de_consolidacao` e afirmam subseções que ela não compõe —, mas não foram executados contra ela.

## Testes que mudaram de propósito (T014, T021)

A regra: o teste que afirmava o bloco de um Perfil num documento de vários Perfis passa a afirmar a
forma consolidada, com a mesma força; nenhuma asserção foi afrouxada.

| Teste | Antes | Agora |
|---|---|---|
| `test_documento_da_retificacao_que_acrescenta.py::test_o_documento_da_retificacao_mostra_as_seis` | "Egressos da escola pública (EPX)" no quadro do Perfil | a coluna "EPX" na tabela de vagas e a célula do Perfil com o 0 declarado |
| `test_atribuicoes_consolidadas.py::test_os_demais_blocos_…` | requisitos e modalidades 3× | 1×, com ou sem as atribuições agrupadas; a remuneração continua 3× (FR-1197 da `064`, emendado) |
| `test_documento_sob_sorteio.py::test_o_cenario_a_…` | "Ordem: por sorteio" 4× | 1× (os 4 marcos na subseção comum); arredondamento e empate continuam ausentes |
| `test_frase_de_recurso.py` (2 testes) | a frase nomeada 4× | 1× |
| `test_perfil_sem_vaga_imediata.py` (2 testes) | "Quadro de vagas — X" por Perfil; 18 tabelas de modalidades em B | a tabela de vagas só com os Perfis com vaga; 1 tabela de modalidades; a reversão 1× |
| `test_documento_publicado.py::test_as_duas_tabelas_de_vagas_…` | uma tabela "Quadro de vagas — DOC-INFO" | nenhuma legenda repete outra; "Vagas por lista de concorrência" nomeia DOC-INFO e não P2 |
| `test_documento_publicado.py::corpo_normativo` | o rodapé reconhecido por "Edital 0" | pela forma "Edital N/AAAA", para valer nos cenários 91 e 92 que entraram em prévia × publicado |
| `test_itens_do_documento.py` (bytes) | `specs/067-…/demonstracao/` | `specs/068-…/demonstracao/` |
| `test_documento_da_auditoria_depois_da_067.py` | auditoria × compositor de agora | auditoria × os PDFs que a `067` gravou — a evidência dela continua dela |

## Os cenários pelo fluxo real (T034)

Roteiros da auditoria (`cenario_a.py`, `cenario_b_corrigido.py`) copiados para o scratchpad com os
caminhos trocados, conteúdo intacto, publicados pelos comandos de aplicação
(`create_process_with_first_edital` → `replace_draft` → `submit_edital` → `homologate_edital` →
`publish_edital`). **Antes** com o código da `main` `2b698592` extraído por `git archive`; **depois**
com o desta branch. O caminho do `pdf.py` em uso foi impresso em cada execução.

| Cenário | Páginas | Seção de Perfis | Branco no pé das páginas da seção* | Bytes |
|---|---|---|---|---|
| A antes | 9 | pp. 2–6 (**5**) | 161 pt | 45.332 |
| A depois | **6** | pp. 2–4 (**3**) | **61 pt** | 32.188 |
| B antes | 36 | pp. 2–31 (**30**) | 4.162 pt | 156.350 |
| B depois | **14** | pp. 2–10 (**9**) | **173 pt** | 67.438 |

\* Soma do branco entre a última linha e o rodapé nas páginas da seção, menos a última (dividida com a
seção seguinte). A seção conta da página do título dela à do título da seção seguinte.

Metas: SC-510 (A ≤ 7 / ≤ 3) e SC-511 (B ≤ 18 / ≤ 12) **atingidas**; SC-514 **atingido**.

**A primeira versão deixava branco.** No B, o marco de 25 linhas da subseção comum era um bloco coeso
e saltava inteiro para a página seguinte, deixando ⅓ da p. 9 em branco (381 pt de branco na seção). A
correção — o marco da subseção comum quebra entre as suas partes, e nunca dentro de uma (FR-1357,
precisado na spec) — levou o branco a 173 pt sem mudar o número de páginas. No Perfil o marco continua
coeso, e o Edital de um Perfil sai com os mesmos bytes.

## A prova de que nenhuma regra se perdeu (T031, SC-513)

**Pelo fluxo real**, sobre o conteúdo publicado nos bancos `*_depois` (`equivalencia_real.py`):

- **A**: os 4 Perfis — equivalência por Perfil sem diferença; as 24 unidades de texto corrido do
  "antes" estão no PDF real da `main`.
- **B**: os 18 Perfis — sem diferença; 263 unidades de texto do "antes" no PDF real da `main`.

O relatório unidade a unidade — quantos Perfis a tinham, quantos a têm, onde ela está agora — está em
[`demonstracao/equivalencia-A.md`](demonstracao/equivalencia-A.md) (19 unidades distintas) e
[`demonstracao/equivalencia-B.md`](demonstracao/equivalencia-B.md) (52). Em A, por exemplo: as 3 linhas
de vagas, 4 Perfis antes e 4 depois, na Tabela 2; o texto dos marcos, 4 e 4, na subseção 5.6; os 2
requisitos, 4 e 4, na subseção 5.5; as duas frases, 4 e 4, na seção. Nenhuma unidade com contagem
diferente; nenhuma que só exista depois.

**Na suíte**, `test_equivalencia_da_consolidacao.py`: 13 casos (entre eles os snapshots congelados de
A e B) e dois controles negativos — um requisito a menos na subseção comum e uma frase que alcançasse
quem não a declarou — que a prova reprova.

**Fora da seção de Perfis**, o texto é o mesmo palavra por palavra, salvo o número das "Tabela N"
(`test_fora_da_secao_de_perfis_o_texto_e_o_mesmo`).

## Páginas olhadas (T035)

Renderizadas por CoreGraphics (o poppler desta máquina perde o negrito), todas as da seção de Perfis,
antes e depois. Gravadas em `demonstracao/`: `pagina-A-antes-02/03`, `pagina-A-depois-02/03`,
`pagina-B-antes-07/08`, `pagina-B-depois-03/04/09/10`.

- **A p. 2 depois**: tabela de Perfis, tabela de vagas (4 × 3 listas), a frase de reversão, a tabela de
  modalidades na ordem AC, PPI, PcD (a do quadro — ED-11 resolvido), a frase de convocação, e os Perfis
  5.1 e 5.2 com "Requisitos: os descritos no item 5.5." e "Marcos classificatórios: os descritos no item
  5.6.". **A p. 3**: 5.3, 5.4, a subseção 5.5 e a 5.6 com a frase do FR-1347, o marco e o método uma vez.
  A página vai cheia até o pé.
- **B pp. 3–4**: a tabela de vagas só com TD-ADM e TD-INFO-EDU (os 16 TP não têm vaga imediata), as
  quatro listas com o código no cabeçalho, uma tabela de modalidades; os Perfis TP com quatro linhas
  cada. **B pp. 9–10**: as subseções 3.19 (atribuições), 3.20 (requisitos) e 3.21 (marcos), com o
  título de 3.21 em duas linhas que quebram entre códigos; o marco quebra entre "Arredondamento" e
  "Recurso", e a p. 9 vai cheia.
- Hierarquia preservada: o título da subseção comum no nível do título do Perfil; o marco um degrau à
  esquerda do que tinha no Perfil, como as atribuições da `064`.

## Retificação e acervo (T028, T029)

- `test_a_retificacao_reagrupa_os_marcos_e_o_documento_original_nao_muda` (integração, PostgreSQL):
  três Perfis de marcos iguais, publicados; Retificação do prazo de recurso do terceiro; o documento
  original mantém os bytes, o consolidado agrupa P1 e P2 e o P3 imprime os próprios marcos com o prazo
  novo.
- Prévia × publicado com os cenários consolidados A e B: mesmas quebras, mesmo corpo normativo.
- A fixture de contrato de um Perfil (`documento_publicado_v1.pdf`) não mudou.

## Achados do caminho, que não viraram escopo (T040)

1. **Larguras da tabela de vagas.** A folga da linha é repartida em proporção à largura natural, e a
   coluna "Ampla concorrência" sai bem mais larga que as das listas reservadas (A p. 2). É o algoritmo
   de sempre (`_larguras_das_colunas`); não muda o que se lê. Registro.
2. **Remissão sozinha no topo da página.** O Perfil não é coeso (decisão da `008`: a unidade coesa é o
   título com o que ele apresenta), e a última linha de um Perfil — "Marcos classificatórios: os
   descritos no item 3.21." — pode cair sozinha no topo da página seguinte (observado numa composição
   intermediária do B). É o caso de viúva da ED-23, agora com uma linha de remissão. Registro.
3. **"Tabela N" digitada pelo gestor** em Edital publicado antes desta feature e retificado depois pode
   passar a designar outra tabela; a conferência da `065` só acusa a que fica sem destino. Está na spec
   (*Consequências na numeração*), sem tratamento.
4. **A linha "AC — Ampla concorrência | — | —"** continua na tabela de modalidades (ED-05).
5. **A quebra de linha sem recuo pendente** nos requisitos longos (ED-16) aparece também na subseção
   comum.

## Suíte e verificação estática (T039)

Em 2026-10-09, sobre `799f17a8`, com `make lint check test-pg DB_NAME=ps068`:

- `ruff check`: **All checks passed!**; `ruff format --check`: 1335 arquivos já formatados;
- `manage.py check`: nenhum problema;
- **10078 passando, 11 pulados**, em 999 s — os mesmos onze pulados deliberados do `AGENTS.md`. Antes
  desta feature eram 9959 passando: a diferença são os testes novos e os casos parametrizados novos.

**Depois de integrar a `main` com a `066`** (PR #269, mergeado enquanto esta feature terminava; o
único conflito foi a linha do total da suíte no `AGENTS.md`), sobre o merge `f4b97a98`, com o mesmo
comando: `ruff check` e `ruff format --check` limpos (1386 arquivos), `manage.py check` sem problemas,
e **10408 passando, 11 pulados**, em 1095 s — os mesmos onze pulados.

