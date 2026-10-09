# Verificação — 067, correções de norma do Edital em PDF

## Ponto de partida (T001, T002)

Medido em 2026-10-09 sobre `17f361b6` (spec, plano e tarefas, sem código), contra PostgreSQL, com
`DB_NAME=ps067` e `pytest` chamado direto (a worktree não tem `.env`):

```text
tests/unit/editais tests/unit/publicacoes tests/unit/interface tests/contract
tests/integration/publicacoes tests/interface/test_compor_quadro.py
2202 passed in 120.39s
```

`test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes` (A e B) verde nesse ponto: o
renderizador da `main` reproduz byte a byte os PDFs da auditoria.

## Os testes da feature, antes do código

Cada fase rodou contra o código da fase anterior e falhou só pelo comportamento que ia mudar:

| Fase | Arquivo | Falha antes do código |
|---|---|---|
| 2 | `test_predicados_da_067.py` | `ImportError: cannot import name 'declara_sorteio'` |
| US1 | `test_frase_de_recurso.py` | `ImportError: cannot import name 'prazo_do_recurso'` |
| US1 | `test_revisao.py` (frase) | asserção — a frase antiga, sem objeto |
| US3 | `test_arredondamento_sob_sorteio.py` | 8 casos: `milestone_rounding_invalid` sob sorteio |
| US3 | `test_documento_sob_sorteio.py` | "Arredondamento" e "Empate no corte" impressos sob sorteio |
| US3 | `test_correcoes_de_norma_na_revisao.py` | 6 casos: Revisão, cartão, ajuda, dica da Retificação |
| US3 | `test_emissao_de_marco_por_sorteio.py` | a submissão recusava o marco sem arredondamento (`blocking_findings`) |
| US4 | `test_perfil_sem_vaga_imediata.py`, Revisão | quadro e reversão impressos; nota ausente |
| US2 | `test_conferencia_do_recurso.py` | `ImportError: cannot import name 'eventos_de_recurso'` |
| US2 | `test_correcoes_de_norma_na_publicacao.py` | o aviso ausente da submissão e da Retificação |

Dois testes de caso-limite foram escritos **depois** do código, como guarda, porque a análise da
rastreabilidade os achou sem teste: dois marcos no mesmo Perfil e o Evento cancelado no aviso.

**Achado na implementação de US1 (`D-012`).** Com o nome do marco dentro da frase, o agrupamento da
Revisão — que junta os marcos de mesma regra de Perfis diferentes — separou cada Perfil num grupo, e
`test_marcos_iguais_em_perfis_diferentes_aparecem_uma_vez` e `test_o_marco_que_diverge_diz_em_que`
caíram. A Revisão passou a dizer "deste marco", com o nome na linha da denominação logo acima; o
documento continua nomeando.

**Testes antigos atualizados de propósito**, cada um no commit que muda o comportamento:
`test_pdf.py` (as duas frases de recurso), `test_documento_da_retificacao_que_acrescenta.py` (a
frase), `test_revisao.py` (a frase; sob sorteio, nem empate nem arredondamento) e
`test_itens_do_documento.py` (o guardião de bytes, renomeado, aponta para `demonstracao/`).

**Regressão das áreas.** Antes de US5: `tests/unit tests/interface tests/contract
tests/integration/publicacoes tests/integration/classificacao tests/acceptance` — 6044 passados, e
as 3 falhas esperadas (o teste da Revisão que ainda exigia o empate sob sorteio, e os dois de bytes
que mudam em US5). Depois de US5, com `tests/integration/editais`: **6200 passed, 1 skipped**,
inclusive `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` — **a fixture de contrato não
mudou** (`SC-505`).

## A diferença de texto contra os PDFs da auditoria (SC-502, D-010)

`test_documento_da_auditoria_depois_da_067.py` compõe os conteúdos congelados de A e B, extrai o
texto (o mesmo extrator dos testes de contrato), neutraliza o rodapé de página, o cabeçalho de tabela
repetido na quebra e o número das "Tabela N", e exige que o texto do PDF da auditoria, transformado
**só** pelas mudanças pretendidas, seja **igual** ao de agora:

| Cenário | Transformação aplicada ao texto da auditoria | Resultado |
|---|---|---|
| A | 4 frases de recurso trocadas pela que nomeia “Classificação por sorteio eletrônico”; 4 "Arredondamento" e 4 "Empate no corte" retirados | igual |
| B | 18 frases trocadas pela que nomeia “Classificação final pela prova de títulos”; 16 quadros zerados com a reversão logo abaixo retirados (TP-01 a TP-16); as 18 linhas de arredondamento, sob pontuação, **ficam** | igual |

**Prova de que a comparação reprova**: com a frase da continuação trocada por um instante
("publicar" → "publicou"), o teste de A falha.

Por `pdftotext -layout`, a diferença de A é a mesma: as 4 frases (2 linhas cada), 4 + 4 linhas
retiradas, e o resto é paginação — o caractere de quebra de página em outra linha e o cabeçalho do
Cronograma repetido numa página nova.

## Os cenários pelo fluxo real (T047, T048)

Roteiros da auditoria copiados para o scratchpad, com os caminhos trocados por variáveis e o conteúdo
dos cenários intacto. Cada um num banco novo copiado de `ps_067_base` (migrado do zero), com dados
fictícios; publicados pelos comandos de aplicação (`create_process_with_first_edital` →
`replace_draft` → `submit_edital` → `homologate_edital` → `publish_edital`). **Antes** com o código
da `main` (`99d32e16`, extraído por `git archive`), **depois** com o desta branch — o caminho do
`pdf.py` em uso foi impresso em cada execução.

O cenário B é o `cenario_b_corrigido.py` da `065`: desde a `065`, o B original é recusado na
submissão pelos conflitos de numeração, na `main` também; a versão corrigida troca só os números de
subitem.

| Cenário | Banco | Achados da submissão | Páginas |
|---|---|---|---|
| A antes (`main`) | `ps_067_a_antes` | 1 aviso (Evento de 2027) | 9 |
| A depois (`067`) | `ps_067_a_depois` | o mesmo + **o aviso de conferência de recurso** | 9 |
| B corrigido antes | `ps_067_b_antes` | 16 avisos de reserva sem vaga imediata | 44 |
| B corrigido depois | `ps_067_b_depois` | os mesmos + **o aviso de conferência**, com os 4 Eventos de recurso | **36** |
| A sem arredondamento, `main` | `ps_067_a_sem_arred_main` | **recusado**: "O arredondamento do marco deve declarar `scale` como inteiro." (×4) — a recusa da auditoria, §3.3 | — |
| A sem arredondamento, `067` | `ps_067_a_sem_arred` | publicado | 9 |

**Diferença de texto, antes × depois do fluxo real**, pela mesma regra do teste (com o resumo de
verificação também neutralizado, porque o conteúdo de cada banco tem identificadores próprios): A —
só o pretendido; B — só o pretendido, com os 16 quadros retirados. E o documento de A **sem**
arredondamento tem o mesmo texto do de A **com** arredondamento: sob sorteio ele nunca é impresso.

## O acervo (US5, SC-506, FR-1325, FR-1326)

No banco `ps_067_a_antes`, o Edital A publicado com o código da `main` foi retificado com o código
desta branch (a Retificação de `cenario_a2.py`: prorrogação e +5 vagas no polo BJN).

- SHA-256 do documento original antes e depois da Retificação: `aa6e8752…c939612b` — **igual**, e
  igual ao do PDF gravado no ato de publicar com a `main`.
- A confirmação da Retificação mostrou `appeal_schedule_review` entre os avisos, e ela publicou.
- O consolidado ("retificado em 9 de outubro de 2026") saiu pelas regras novas: as 4 frases nomeiam
  “Classificação por sorteio eletrônico”, nenhuma linha de arredondamento nem de empate no corte, e
  nenhuma frase "contados da divulgação do resultado" (`pdftotext -raw`).

## Páginas (T049)

Renderizadas por CoreGraphics (`qrender_all.py`, escala 1,4 — o poppler desta máquina desenha o
Helvetica-Bold como Regular) e olhadas, antes e depois. As escolhidas estão em `demonstracao/`:

| Página | O que se vê |
|---|---|
| `pagina-A-antes-03.jpg` / `pagina-A-depois-03.jpg` | o marco por sorteio de INF-BJN: some "Arredondamento" e "Empate no corte"; "Recurso:" nomeia “Classificação por sorteio eletrônico”, com as aspas tipográficas desenhadas; rótulos em negrito |
| `pagina-B-antes-08.jpg` / `pagina-B-depois-08.jpg` | TP-01: some a "Tabela 6 — Quadro de vagas — TP-01" de zeros e a reversão; a de Modalidades sobe para Tabela 6, com percentual e fundamento; o marco FINAL, por pontuação, continua com arredondamento e empate |
| `pagina-B-depois-07.jpg` | TP-01: a forma de convocação continua, logo depois de "Dados exigidos na inscrição" |
| `pagina-B-depois-04.jpg` | TD-ADM, com vaga: o quadro inteiro, inclusive "PTT 0", e a reversão |

## Interface (T050)

Runserver desta worktree na porta 8067 (entrada `correcoes-067` do `.claude/launch.json`), banco
`ps_067_rascunho` com os rascunhos de A e B, identidade de demonstração `ana.elaboradora` /
Elaborador.

| Captura | O que se vê |
|---|---|
| `1-revisao-com-o-aviso-de-recurso.jpg` | a Revisão de A: o aviso "Prazos de recurso a conferir", com "Ir para Cronograma" (`/compor/cronograma#cronograma-titulo`); nenhuma linha de arredondamento ou empate na conferência do marco |
| `2-cartao-por-sorteio-sem-arredondamento.jpg` | o cartão do marco por sorteio sem "Casas decimais" e "Arredondamento" (ocultos com 2 e meio para cima) |
| `3-cartao-de-volta-a-pontuacao.jpg` | a mesma escolha trocada para pontuação: os campos voltam, preenchidos com 2 e "Meio para cima" |
| `4-revisao-reversao-que-nao-sai.jpg` | a Revisão de B: na reversão de TP-01, "não sai no documento: o Perfil não tem vaga imediata" — nos 16 Perfis TP |

Nada foi gravado pela interface; as trocas de forma ficaram sem salvar.

## Achados registrados, não tratados

- **A dica de vazio do desfecho de empate, na Retificação, anuncia impedimento também sob sorteio**
  (`interface/retificacao.py`, `"cutRule/tieOutcome": "Não declarado — a publicação será
  impedida"`). Sob sorteio a validação não exige o desfecho (`FR-928`), e a dica afirma uma recusa
  que não acontece. É a mesma natureza do `FR-1317`, mas sobre outro campo e anterior a esta feature.
- **O Perfil só de cadastro de reserva corta "os 10 primeiros"** (cenário B): a regra de corte
  continua impressa num Perfil sem vaga, e é parte do RC-58 que a `D-003` deixou aberto.
- **Sem o quadro, a forma de convocação do Perfil sem vaga fica logo abaixo de "Dados exigidos", na
  margem zero** — a ED-15 da auditoria (frases do Perfil fora do recuo), que esta feature não trata.

## Suíte completa (T054)

Em 2026-10-09, sobre `2ce6a130`, com `DB_NAME=ps_067_base` (banco de teste `test_ps_067_base`):

```text
cd backend && make lint check test-pg
ruff check: All checks passed! · ruff format --check: 1331 files already formatted
manage.py check: no issues · makemigrations --check: No changes detected
9955 passed, 11 skipped in 1096.75s
```

Os onze pulados são os mesmos onze deliberados do `AGENTS.md` (9 do vocabulário da composição, a
recusa por vendor e o E2E da fonte real). A rodada anterior, sobre `b4ba653d`, tinha dado 9952
passados e **1 falha** — `test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos`: a `067` não
estava na tabela de incrementos do README; corrigido em `2ce6a130`.
