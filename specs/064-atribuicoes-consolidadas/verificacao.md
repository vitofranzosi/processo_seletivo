# Verificação: As atribuições idênticas saem uma vez no documento do Edital

**Feature**: [spec.md](spec.md) · **Tarefas**: [tasks.md](tasks.md)

## Ponto de partida (T001, T002) — 2026-10-08

Sobre a `main` `d7d3fe0b`, na branch `claude/064-atribuicoes-consolidadas`, antes de qualquer
alteração de código.

- `manage.py migrate --check` contra o banco de desenvolvimento local (`processo_seletivo`): **sai com
  1** — há migrations pendentes (85 aplicadas em `django_migrations`). A primeira versão desta linha
  dizia "nada pendente", lendo o código de saída do `tail` e não o do `manage.py`; corrigido na T033,
  quando a cópia do banco acusou o mesmo. Não alcança a suíte, que cria o banco de teste do zero, e
  não é desta feature.
- `tests/unit/publicacoes` e `tests/contract`, contra PostgreSQL, banco `test_ps_064`:
  **932 passed** em 30 s.

## Regra de identidade (T003 a T009)

- Contra a `main`: o arquivo novo não importa — `ImportError: cannot import name
  'grupos_de_atribuicoes'` —, e nenhuma outra falha.
- Depois de `grupos_de_atribuicoes`: **23 passed**.

## Documento (T010 a T020)

- Contra o renderizador de antes: **21 failed, 29 passed**. Falham os testes de forma, pelo motivo
  esperado (sem subseção comum; o texto repetido em cada Perfil). Passam os que descrevem o que não
  pode mudar: texto próprio, texto vazio, demais blocos, Edital de um Perfil.
- Depois de `_perfis`: **50 passed**.
- **Prova de mutação do FR-1193**: com a subseção comum aberta em `bloco(coeso=False)`, nove das
  catorze posições de partida de
  `test_a_subsecao_comum_que_cabe_numa_pagina_sai_inteira_e_o_titulo_nunca_fica_sozinho` reprovam —
  a variação de enchimento de fato alcança o rodapé. Restaurado o bloco coeso, verde.
- `tests/unit/publicacoes` e `tests/contract`, contra PostgreSQL: **982 passed** (os 932 do ponto de
  partida mais os 50 novos). `test_a_medicao_de_um_bloco_atravessa_os_quadros_que_ele_contem`
  passou **sem edição**; `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` passou e a
  fixture `documento_publicado_v1.pdf` **não** foi regerada.

## Integridade (T021 a T024)

- **61 passed**.
- **Prova de mutação do FR-1191**, uma de cada vez sobre `_atribuicoes_comuns`/`_perfis`: omitir o
  último parágrafo, desviar a remissão para o item seguinte, inverter a ordem dos parágrafos. Nas
  três, `test_cada_perfil_tem_no_documento_exatamente_as_atribuicoes_da_versao` reprova **sete dos
  nove** cenários; os dois que passam são os sem grupo ("diferentes" e "subconjunto"), onde não há
  o que a mutação alcance. Restaurado, verde.

## Retificação (T025 a T028)

- `test_a_retificacao_reagrupa_as_atribuicoes_e_o_documento_original_nao_muda`, contra PostgreSQL,
  passou: o original com subseção comum de P1, P2 e P3 guarda os mesmos bytes; o documento da
  Retificação agrupa P1 e P2 e traz o texto novo do P3; a alteração legível diz "Atribuições" no
  Perfil "Tutor Polo C", e nada de "comuns".
- O arquivo de Retificações inteiro e o arquivo novo, contra PostgreSQL: **110 passed**.

## Prévia × publicado (T029)

- `tests/contract/test_documento_publicado.py`: **27 passed**, com os dois testes de paginação
  parametrizados também no cenário `atribuicoes-comuns`.

## Lint (T031)

- `ruff check .`: *All checks passed!* · `ruff format --check .`: 1303 arquivos formatados.
- `make check`: nenhum problema; `makemigrations --check`: *No changes detected*.

## A amostra olhada

Um Edital de dez Perfis de Tutor com o mesmo texto e um Mediador de texto próprio, em prévia:
sete páginas; os dez Perfis trazem "Atribuições: as descritas no item 5.12."; o Mediador traz o
próprio bloco; a 5.12 *Atribuições comuns aos Perfis …* imprime o texto uma vez, depois do último
Perfil; as seções 6 em diante e as tabelas seguem numeradas como antes.

**Um detalhe de leitura, não de norma**: o título da subseção comum, com dez códigos, ocupa duas
linhas, e a quebra pode cair dentro de um código que tem espaço — "ADS" no fim de uma linha e
"- P06" no começo da seguinte. É a quebra por palavra de sempre do documento (`_quebrar`), e o
mesmo acontece hoje com qualquer texto que contenha esses códigos.

## Suíte completa (T032)

`make test-pg DB_NAME=ps_064`, sem outra suíte no cluster e sem arquivo editado durante a execução:
**9427 passed, 11 skipped** em 924 s (15 min 24 s). Os onze pulados são o mesmo número que as
instruções do repositório registram como deliberado. Diante dos 9348 medidos ali em 07/10, a
diferença é a soma dos 68 casos desta feature (64 no arquivo novo, 3 no contrato, 1 na integração da
Retificação) com o que a `main` ganhou depois daquela medição.

## Pela interface (T033)

Numa **cópia** do banco de desenvolvimento (`ps_demo_064`, criada com `createdb -T` e preparada com
`make preparar DB_NAME=ps_demo_064`), para não tocar os dados de quem desenvolve. Servidor da
worktree na porta 8064, com o seletor de identidade, como `ana.elaboradora` (Elaborador).

1. No rascunho do Edital 002/2027, etapa Perfis, o Perfil `TEC-EAD` recebeu três atribuições, uma
   por linha.
2. **Duplicar este Perfil** duas vezes, pela tela: `TEC-EAD-2` e `TEC-EAD-3` nasceram com o mesmo
   texto — a cópia da `043` leva as atribuições.
3. O texto do `TEC-EAD-3` foi trocado por outro, e o rascunho foi salvo ("Rascunho salvo — Perfis
   de Vaga").
4. `GET …/previa/documento`, o endpoint que a tela "Ver o Edital" embute: 200, `application/pdf`,
   22.882 bytes. Nele, `TEC-EAD` e `TEC-EAD-2` trazem "Atribuições: as descritas no item 3.4."; o
   `TEC-EAD-3` traz o próprio bloco; a **3.4 Atribuições comuns aos Perfis TEC-EAD e TEC-EAD-2**
   imprime as três atribuições uma vez, logo antes de "4. DA INSCRIÇÃO", que manteve o número.
5. O mesmo documento, composto no shell pelo caminho da view (`edital_snapshot` + modo prévia),
   saiu com os mesmos 22.882 bytes, e a página 3 foi olhada como imagem.

O painel do navegador não exibe PDF embutido ("Seu navegador não exibe PDF nesta tela"), e por isso
a leitura do passo 4 foi pelo conteúdo do arquivo, e a imagem pelo passo 5.

A entrada temporária `atribuicoes-064` do `.claude/launch.json` foi desfeita depois; o banco
`ps_demo_064` ficou, com o rascunho de três Perfis, para quem quiser olhar.

## Revisão de código (08/10/2026)

Nove achados, todos corrigidos:

1. **Título partia código** ("ADS" / "- P06") — o título passou a ser montado em linhas que quebram
   entre códigos (`_linhas_sem_partir`).
2. **Código com ", " ou " e " tornava o título ambíguo** — todos os códigos do grupo entre aspas
   tipográficas quando algum tem o separador (`_codigos_enumerados`).
3. **Numeração das subseções calculada duas vezes** — uma lista `comuns` só, usada pela remissão e
   pela subseção.
4. **Docstring de `grupos_de_atribuicoes` contradizia a regra do texto registrado** — reescrita.
5. **Remissão com espaço de linha, e o cabeçalho vizinho com espaço de sub-bloco** — `_pares` ganhou
   `antes`, e a remissão usa `ANTES_DE_BLOCO`; o Edital de um Perfil continua com o padrão.
6. **Posição e negrito da remissão sem teste** — teste novo.
7. **Legenda de modalidades sem contagem fixada** — `== 3`.
8. **Teste de integridade conferia o conteúdo antes do alvo da remissão** — a ordem foi invertida.
9. **`_numeros` repetia a expressão e a leitura do PDF** — uma de cada.

Os quatro testes novos (título sem partir código, aspas em dois casos, posição e espaço da
remissão) reprovam com o código de antes das correções e passam com o de depois. O arquivo novo
fechou em **69 passed**.

Suíte completa depois das correções, `make test-pg DB_NAME=ps_064`, sem outra suíte no cluster:
**9432 passed, 11 skipped** em 936 s — os 9427 de antes mais os cinco casos novos da revisão.

## Integração com a correção do "?" (#265) — 08/10/2026

O CI do #264 ficou verde às 17:38Z; o #265 entrou na `main` às 18:59Z, mexendo no mesmo renderizador.
Integrada a `main` (merge `5d635ddf`, sem conflito textual), os testes das duas features passaram —
1092 em `tests/unit/publicacoes`, `tests/contract` e nos dois arquivos do #265 —, mas o documento e a
função de agrupamento passaram a divergir, porque o #265 normaliza o snapshot antes de compor:

| Dois Perfis que só diferem em | função | documento |
|---|---|---|
| `●` × `•` | não agrupava | agrupava |
| `●` + largura zero × `●` | não agrupava | agrupava |
| NFC × NFD | não agrupava | agrupava |

O responsável pelo produto escolheu a comparação normalizada. A chave passou a aplicar
`grafia.normalizar`; o FR-1187, dois casos-limite, a D-002 e a rastreabilidade foram emendados; e
os testes passaram a provar a regra na função **e** na prévia, com o par `≥` × `≤` confirmando que o
que a grafia não resolve continua distinto. O arquivo novo fechou em **71 passed**.

Suíte completa sobre a branch integrada e com a emenda, `make test-pg DB_NAME=ps_064`, sem outra
suíte no cluster: **9526 passed, 11 skipped** em 976 s.
