# Verificação — 065, conflitos de numeração

## Ponto de partida (T002)

Medido em 2026-10-08 sobre `75dd66df` (spec, plano e tarefas, sem código), contra PostgreSQL, com
`DB_NAME=ps065` e `pytest` chamado direto (a worktree não tem `.env`):

```text
tests/unit/editais tests/unit/publicacoes tests/contract
tests/interface/test_caractere_sem_grafia.py tests/integration/publicacoes
1908 passed in 89.39s
```

## Os testes da feature

Seis arquivos novos — `test_numeracao_digitada.py`, `test_conflito_de_numeracao.py`,
`test_remissoes.py`, `test_itens_do_documento.py`, `test_numeracao_na_revisao.py`,
`test_numeracao_na_publicacao.py` — e a fixture de bytes do contrato inalterada. Antes do código,
cada fase falhou só por `ImportError`/`AttributeError` (T008, T017, T025).

**Prova de reprovação de D-006.** Com o código do aviso da Retificação trocado por um instante pelo
da publicação, três testes caem — os dois de Retificação da integração e o de unidade — e voltam a
passar com o código restaurado. É o que garante que o aviso não some da confirmação.

**Regressão.** Depois da US2, `tests/unit/editais tests/unit/publicacoes tests/contract
tests/interface tests/integration/publicacoes tests/integration/editais`: **4755 passed, 1 skipped**
(365s), inclusive os testes de orçamento de consulta da interface (D-015).

## Os cenários da auditoria, pelo fluxo real (T037)

Roteiros em `doc/auditoria-edital-pdf-2026-10-08/cenarios/`, cada um num banco copiado de
`ps_065_base`, publicando pelos comandos de aplicação do sistema.

### B sem correção — submissão recusada (SC-462, SC-469)

`cenario_b.py`: `submit_edital` levanta `blocking_findings` com **5** conflitos e **15** parágrafos —
Da Inscrição (4: 3.1–3.4), Da Verificação da Autodeclaração (6: 4.1–4.3), Dos Recursos (11: 8.1–8.3),
Da Convocação (12: 11.1–11.2), Disposições Finais (15: 14.1–14.3). A primeira mensagem, como saiu:

> Conflito de numeração — comprovado. A seção «Da Inscrição» sai no documento como 4, e 4 parágrafos
> começam por número de outra seção: parágrafo 1, «3.1 A inscrição será realizada exclusivamente pelo
> sistema de inscrições, no…»; parágrafo 2, «3.2 O candidato deverá anexar, em arquivo PDF único de
> até 10 MB, os documentos…»; parágrafo 3, «3.3 Não haverá conferência de documentação no momento da
> inscrição, e a…»; parágrafo 4, «3.4 O candidato que enviar documentação com quantidade de páginas
> superior a 30…». No documento, os subitens desta seção começam por 4. Corrija a numeração no texto
> da seção.

### B corrigido só pelas mensagens — publica, e o documento fecha (SC-465)

`cenario_b_corrigido.py` troca só os números apontados (3.x→4.x, 4.x→6.x, 8.x→11.x e "item 8.1"→
"item 11.1", 11.x→12.x, 14.x→15.x). Resultado (`demonstracao/B-corrigido.pdf`):

- submissão sem nenhum achado da 065;
- **44 parágrafos numerados, todos começando pelo número da própria seção** (conferência por script
  sobre `pdftotext -layout`), e "11.1" um item só;
- **44 páginas**, como o B da auditoria;
- diferença de texto contra `pdf/B-publicado.pdf`, palavra a palavra: só os 15 números de subitem e
  "8.1." → "11.1."; a única outra mudança é a quebra da última página — o parágrafo 15.2 passou inteiro
  para a página 44, onde antes ficava sozinho o "Ifes." de 14.2;
- páginas 39 a 44 renderizadas por CoreGraphics e por `pdftoppm`, e olhadas: "4. DA INSCRIÇÃO" com 4.1
  e 4.2; "11. DOS RECURSOS" com 11.1 a 11.3 e a remissão "item 11.1"; "12." e "15." coerentes.

### Retificação que desloca a numeração — avisa e publica (SC-470, D-002)

Sobre o B corrigido e publicado, a Retificação que esvazia "Do Atendimento à Pessoa com Deficiência"
(7): `advertencias_do_ato` devolve três `typed_numbering_conflict_in_retification` — Dos Recursos (sai
como 10), Da Convocação (11), Disposições Finais (14) — e uma `cross_reference_suspected` ("item 11.1"),
e a Retificação é publicada. No consolidado (`demonstracao/B-corrigido-retificado.pdf`), **8
parágrafos ficam fora da sua seção**: é a consequência aceita e explícita da D-002, que o aviso
anunciou antes da publicação.

### A e A-retificado — nada a acusar (SC-464)

`cenario_a2.py`: publicação e Retificação concluídas, e o único achado da submissão é o aviso antigo
de ano do Evento "Início das aulas". Tamanhos iguais aos da auditoria (45.785 e 45.911 bytes).

### Bytes (SC-466, FR-1219)

`test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes`: os conteúdos congelados de A e de
B, com o contexto do ato de cada cenário, produzem com o código novo exatamente os bytes de
`pdf/A-publicado.pdf` e `pdf/B-publicado.pdf`. A fixture de bytes do contrato passa sem ser refeita.

## Exploratório sobre os Editais reais (T038)

`fp_amostra.py` (versionado sem texto real) lê o texto dos nove Editais da amostra e usa, como número
da seção, o título do próprio original — onde a numeração é coerente por construção, de modo que toda
acusação seria falso positivo.

| Medida | Valor |
|---|---|
| Começos de subitem lidos | 587 |
| Em seção cujo título o roteiro reconheceu | 517 (um dos Editais quebra o título em duas linhas no `pdftotext`, e os 70 dele ficam fora) |
| Acusados | **1** |
| Remissões reconhecidas | 91 |

**O único acusado é artefato de quebra de linha rígida**: uma remissão "…item / 11.2." partida no meio
da frase, em que "11.2." ficou sozinho na linha. No sistema, isso só acontece se o texto for colado
com quebras dentro do parágrafo (o registro das quebras rígidas que a `064` deixou à parte); colado do
Word, o parágrafo é um só. Fica como limitação observada: **um parágrafo que é só um número de subitem
é mais provavelmente o fim de uma remissão partida do que um subitem**, e excluí-lo da forma de
`FR-1199` seria uma emenda à spec — registro para decisão, e não mudança feita aqui.

## Correções da revisão do PR (09/10/2026, D-017)

A revisão reproduziu cinco começos de parágrafo legítimos lidos como subitem — e, numa seção de outro
número, impeditivos: "8.30 às 12.00 – …", "10.10 a 20.10 – …", "1.5 salário mínimo", "1.2 mil
candidatos", "3.5 vezes o valor"; e a remissão "item 10.1.1.1.1" lida como "item 10.1.1.1".

- **Prova de reprovação.** Com o `numeracao_digitada.py` anterior, os 13 casos novos que exigem a
  correção caem (8 do conjunto de prova, 3 de remissão no módulo puro, 1 de conflito, 1 de remissão
  na validação); com o corrigido, os 167 testes de unidade da feature passam. Os 6 casos de forma
  parecida que **continuam** subitem ("1.1 a 1.3", "8.10 a 8.12", "10.10 a 10.12", "4.1 às pessoas…",
  hora 25, mês 13) passam com os dois — a exclusão é da expressão inteira.
- **O conflito real continua impeditivo**: os cinco exemplos e um "3.1" na seção que sai como 4 dão um
  achado só, impeditivo, que cita o parágrafo 6 e nenhum dos cinco.
- **A amostra não mudou.** `fp_amostra.py` sobre os nove Editais, antes e depois: 587 subitens, 91
  remissões e as mesmas acusações — nenhum subitem nem remissão real se perdeu.

## Pelo canal de quem elabora (T039, Princípio VI)

Banco `ps_065_demo` com o rascunho do cenário B; `runserver` na porta 8065 por uma entrada
acrescentada ao `.claude/launch.json` (desfeita no fim); identidade `ana.elaboradora`, papel
Elaborador. Capturas em `demonstracao/`:

1. a Revisão lista os 5 conflitos como **IMPEDE**, cada um com os trechos, e a remissão ambígua logo
   depois do conflito da própria seção «Dos Recursos» (`1-revisao-com-os-conflitos.jpg`);
2. "Ir para Conteúdo" leva a `…/compor/conteudo#titulo-inscricao`, à legenda **"4. DA INSCRIÇÃO"**,
   com o texto "3.1…" logo abaixo (`2-link-leva-a-legenda-da-secao.jpg`);
3. corrigido o campo para 4.x e salvo, a etapa passa a listar 4 conflitos — o de «Da Inscrição» some;
4. a confirmação da submissão mostra os 4 impedimentos restantes, com as mesmas mensagens
   (`3-submissao-barrada.jpg`). O botão de confirmar não foi acionado: a recusa está provada por
   `test_a_submissao_e_recusada_e_corrigir_libera`.

## A suíte inteira (T042)

`make lint check` (com `DB_NAME`, `DB_USER` e `DB_RUNTIME_USER` como variáveis do Make — a worktree
não tem `.env`): `ruff check` e `ruff format --check` limpos, `manage.py check` sem problemas,
nenhuma migration pendente.

`make test-pg DB_NAME=ps065 POSTGRES_USER=saymoncastro`, sobre `6268e16f`:

```text
9692 passed, 11 skipped in 934.23s (0:15:34)
```

Os onze pulados são os deliberados que o `AGENTS.md` reparte. Sem `.env`, `ARQUIVOS_CANDIDATOS_RAIZ`
fica vazio, como no CI.
