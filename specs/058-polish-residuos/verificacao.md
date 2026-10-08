# Verificação — 058 · Polish: os resíduos dos três lotes

## Protocolo

| Item | Valor |
|---|---|
| Commit "antes" | `c4866e19` (a `main` com a reavaliação, sobre a `057`) |
| Banco | `ps_058_polish`, cópia de `ps_polish_audit` (o banco da auditoria), `migrate --check` limpo |
| Servidor | `runserver` 8058, entrada `polish-058` acrescentada ao `.claude/launch.json` e revertida antes do commit |
| Janela | 1280 × 900; a Lista e a Condução também a 375 px |
| Identidades | `ana.gestora` com os sete papéis; `joana.avaliadora` sem papel (avaliadora pela comissão) |
| Método das medidas | a página servida pelo `runserver`, renderizada num `iframe` `srcdoc` da largura da janela (1280 ou 375), com `getBoundingClientRect` e `scrollWidth`; a 375 px, conferido também no viewport emulado do painel, medindo `scrollWidth` **e** `innerWidth` |
| Método das ações | [capturas/acoes.py](capturas/acoes.py), no `manage.py shell`, com o cliente de teste do Django e as duas identidades (D-010): 62 telas, descobertas a partir da Lista e das telas da `057`. Arquivos: [acoes-antes.json](acoes-antes.json) e [acoes-depois.json](acoes-depois.json) |
| Método do envio | `new FormData(form, botão "Salvar rascunho")` na etapa Etapas do 76/2027, sem o token: [envio-etapas-antes.json](envio-etapas-antes.json) e [envio-etapas-depois.json](envio-etapas-depois.json). A Revisão não tem "Salvar rascunho" — não há envio a comparar nela |
| Método do rascunho | [capturas/rascunho.py](capturas/rascunho.py): envia o corpo lido na tela, como `ana.gestora`, e lê as linhas das Etapas e o registro da gravação (D-005): [rascunho-antes.json](rascunho-antes.json) e [rascunho-depois.json](rascunho-depois.json) |

## Antes

| # | Medida | Antes |
|---|---|---|
| 1 | Processo Ativo (PS-DEMO-2026), atos do Processo | **Encerrar** verde cheio (`rgb(21,128,61)`) e **Cancelar** vermelho cheio (`rgb(169,27,27)`), um por linha, os dois acima do aviso de impedimento |
| 1b | Processo em elaboração (2027), atos | "Ativar Processo" `botao secundario`; **Cancelar** vermelho cheio |
| 2 | Lista a 375 px: documento | `scrollWidth` 375, `innerWidth` 375 |
| 3 | Lista a 375 px: tabelas e ações | tabelas de 531 e 570 px dentro de cartões de 325 com `overflow:hidden`; **4 de 4 e 17 de 17 botões fora do cartão**, recortados, sem rolagem (o último termina a 520 e a 559 px da borda do cartão) |
| 4 | Condução do marco 1 do 51/2026 a 375 px | documento com **486** px de rolagem; no viewport emulado, `innerWidth` também 486 (o navegador alarga a janela de layout); a tabela dos recortes tem 462 px |
| 5 | Alocação do PS-DEMO-2026 a 1280 px | página com 1.280 px; `thead` de 127 px; rolada a página 520 px numa janela de 300, o `thead` fica em y = 0 com a tabela começando em y = −48 (fixo) |
| 6 | Matrículas do 51/2026, "O que sairá vazio, e por quê" | `section.resumo`, `display:flex`: `h2` em x = 24, **`p.nota` em x = 268, ao lado do título**; `dl.meta` e `form.confirmar` na linha seguinte |
| 7 | Resultados das Etapas do 51/2026 | tabela sem classe; `td.numero` com `text-align:left` em todas — "8,5" a 12 px da esquerda e 72 da direita; na decisória (Análise documental), "Deferido" também leva `numero` |
| 8 | "(s)" no texto das telas tocadas, no seed | Matrículas: **8** "linha(s)"; Distribuição, Recurso, Ocupação e histórico: 0 no seed (os estados que compõem esses plurais — resultado da consolidação em lote, instrução, reversão de cota, rederivação do quadro — não existem no banco; a prova deles é o teste de renderização) |
| 9 | Etapas do 76/2027: valor dos campos | Peso `2.0000` e `1.0000`, Nota mínima `6.0000`; vazios vazios |
| 10 | Rascunho gravado depois de "Salvar rascunho" | [rascunho-antes.json](rascunho-antes.json): 302 para `?salvo=etapas`; Etapas com `weight` 2.0000 / 1.0000 / None e `minimum_score` 6.0000; registro `ALTERAR_RASCUNHO`, motivo "Etapas de Avaliação" |
| 11 | Revisão do 76/2027: x do primeiro valor dos 29 blocos de pares | **9 x diferentes**: 313 (DOC-INFO), 286 (TEC-LAB), 95, 273, 129, 170, 234, 133 e 229 |
| 12 | Motivo de sucessão | Ordenação e Corte do 51/2026: `textarea rows=3`, 685 × 75 px, em `p.campo`; **Ocupação do 51/2026: `input`, 1.232 × 40 px**, direto no `form.acoes`; **Sorteio do 26/2026: `input`, 685 × 40 px**, em `p.campo` |
| 13 | HTML da distribuição (`test_escala_da_mesa`) | **82.477** caracteres |

Capturas: [processo-antes.png](capturas/processo-antes.png), [lista-375-antes.png](capturas/lista-375-antes.png),
[revisao-antes.png](capturas/revisao-antes.png).

### Os rótulos da Revisão, medidos para a largura da coluna (D-006)

Em 0,875 rem, numa linha: o mais longo é "Reverter vaga reservada não preenchida para a ampla
concorrência:" (439 px), que já quebrava no teto de 16 rem; o seguinte, "Como a convocação é
comunicada:" (229 px); depois "Datas do Evento “Prova objetiva”:" (216). Todos os demais têm até
177 px.

## Depois

Medido no mesmo banco, com o mesmo método, sobre a árvore do PR.

| # | Medida | Antes | Depois | Meta | |
|---|---|---|---|---|---|
| 1 | Processo Ativo: atos do Processo | Encerrar verde cheio, Cancelar vermelho cheio | Encerrar (`botao secundario`) e Cancelar (`botao perigoso`) **contornados** (fundo branco, texto e borda `rgb(169,27,27)`), em linha, cada um com "IRREVERSÍVEL", acima do aviso | nenhum cheio | ✓ |
| 1b | Processo em elaboração | Ativar secundário; Cancelar vermelho cheio | Ativar secundário; Cancelar contornado, depois do filete (borda de 1 px) | idem | ✓ |
| 2 | Lista a 375 px: documento | 375 / `innerWidth` 375 | 375 / `innerWidth` 375 | 375 | ✓ |
| 3 | Lista a 375 px: ações | 21 de 21 botões recortados, sem rolagem | molduras rolam até 531 e 570 px, além do último botão (519 e 558); rolada ao fim, **21 de 21** visíveis | todos alcançáveis | ✓ |
| 3b | Lista a 1280 px | — | molduras com `overflow-x:visible`, sem rolagem (1.230 = 1.230) | sem mudança | ✓ |
| 4 | Condução a 375 px | 486 (`innerWidth` 486) | **375** (`innerWidth` 375); a tabela rola na moldura (462 em 327), que é focável e nomeada "Recortes deste marco" | 375 | ✓ |
| 5 | Alocação a 1280 px | `thead` fixo (y = 0 com a tabela em −48) | idêntico; página 1.280, `thead` 127 | fixo | ✓ |
| 6 | Matrículas: a seção | nota em x = 268, ao lado do título | `display:block`; título em y = 560, nota em y = 600, x = 24 | empilhados | ✓ |
| 7 | Resultados | notas à esquerda (12 px da esquerda, 72 da direita) | notas **à direita** (12 px da direita); "Deferido" à esquerda, sem `numero` | números à direita, texto à esquerda | ✓ |
| 8 | "(s)" nas telas tocadas | Matrículas: 8 | **0**; "1 linha" nas marcas; os demais estados pela renderização do teste | nenhum, salvo o que grava | ✓ |
| 9 | Etapas: valor dos campos | `2.0000`, `1.0000`, `6.0000` | **`2`, `1`, `6`**; vazios vazios | sem zeros | ✓ |
| 10 | Rascunho gravado | [rascunho-antes.json](rascunho-antes.json) | [rascunho-depois.json](rascunho-depois.json): **idêntico** (`diff` vazio) | idêntico | ✓ |
| 11 | Revisão: x do primeiro valor | 9 posições (95 a 313) | **2**: 313 nos 26 blocos da conferência, 335 nos 3 da caixa de irreversíveis (recuo próprio, D-012); a 375 px nenhum bloco transborda, documento 375 | uma posição | parcial |
| 12 | Motivo de sucessão | Ocupação `input` 1.232 × 40; Sorteio `input` 685 × 40 | as quatro telas: `textarea rows=3`, **685 × 75**, em `p.campo`; o botão da Ocupação em linha própria, como no Corte | o mesmo controle e largura | ✓ |
| 13 | Envio de "Salvar rascunho" das Etapas | [envio-etapas-antes.json](envio-etapas-antes.json) | [envio-etapas-depois.json](envio-etapas-depois.json): as mesmas 43 chaves, na mesma ordem; três valores mudam de grafia e designam o mesmo número (`6.0000`→`6`, `2.0000`→`2`, `1.0000`→`1`) | FR-1086 | ✓ |
| 14 | HTML da distribuição | 82.477 | **82.498** (+21: o seletor da moldura na regra da Alocação) | < 120.000 | ✓ |
| 15 | Suíte (`make lint check test-pg`) | — | **9.129 passando, 11 pulados**, em 884 s (`make lint check test-pg`, `DB_NAME=test_ps_058`) | verde | ✓ |

### As provas

- **Destinos por papel**: `diff` de [acoes-antes.json](acoes-antes.json) e
  [acoes-depois.json](acoes-depois.json) **vazio** — 62 telas, `ana.gestora` (594 destinos) e
  `joana.avaliadora`. Recapturado depois de cada item (R1, R2, R3–R5, R6–R8), sempre vazio. A chave
  de idempotência é mascarada (D-011).
- **Envio**: só a exceção de FR-1086 (linha 13).
- **Rascunho gravado**: idêntico (linha 10). O R6 fica no lote.

Capturas: [processo-depois.png](capturas/processo-depois.png),
[lista-375-depois.png](capturas/lista-375-depois.png) (a moldura rolada ao fim),
[revisao-depois.png](capturas/revisao-depois.png).

### Meta parcial

- **Revisão, "o mesmo x em todos os blocos"** (SC-419): de 9 para 2 posições. A que sobra é a da caixa
  de irreversíveis, cujo recuo (borda de 4 px e lista recuada de 1,2 rem) é outro desenho e não
  está na lista. Valor inicial 9, alcançado 2; justificativa na [D-012](research.md).

### A suíte

Duas rodadas completas contra PostgreSQL, sem editar arquivo durante nenhuma:

1. **4 falhas, 9.124 passando, 11 pulados** (903 s). Duas asserções prendiam o valor que o R6 e o R7
   mudam (D-014); os documentos da 058 citavam decisões de outras features no formato que a
   varredura lê como decisão da própria; e a 058 faltava na tabela de incrementos do README. As
   quatro foram corrigidas, junto com os sete pontos da revisão de código (D-015).
2. **9.129 passando, 11 pulados** (884 s), com `ruff check`, `ruff format --check`, `manage.py
   check` e `makemigrations --check` limpos. Os 11 pulados são os da `main` (os nove pares *termo ×
   template* da varredura de vocabulário, a recusa por vendor e o E2E da Caixa); os casos novos de
   `test_polish_da_058.py` são 24. O `AGENTS.md` registrava 9.099 passando, medidos na `057`.
