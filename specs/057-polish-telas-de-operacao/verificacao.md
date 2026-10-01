# Verificação — 057 · Polish das telas de operação

## Protocolo

| Item | Valor |
|---|---|
| Commit "antes" | `94cb4914` (a `main` com a `055`, a `056` e a conversão dos comentários da folha) |
| Banco | `ps_057_polish`, cópia de `ps_polish_audit` (o banco da auditoria), `migrate --check` limpo |
| Servidor | `runserver` 8057, entrada `polish-057` acrescentada ao `.claude/launch.json` e revertida antes do commit; cookies de sessão próprios da porta |
| Janela | 1280 × 900 |
| Identidades | `ana.gestora` com os sete papéis; `joana.avaliadora` sem papel (avaliadora pela comissão); candidata `MARIA` do fixture |
| Método das medidas | página servida pelo `runserver`, renderizada num `iframe` `srcdoc` de 1280 × 900 dentro do painel do navegador (a folha é inline, a página é a mesma), com `getBoundingClientRect`; o portal e a Minha etapa, renderizados pelo cliente de teste do Django contra o mesmo banco e medidos no Chrome sem janela |
| Método das ações | o cliente de teste do Django, com as duas identidades, lendo o HTML servido (D-017): `href` de todo link no `main`, `action` de todo formulário, `hx-post`, `formaction` e `name=value` de todo botão. Arquivos: [acoes-antes.json](acoes-antes.json) e [acoes-depois.json](acoes-depois.json) |

## Antes

### As medidas das decisões recebidas

| # | Medida | Antes |
|---|---|---:|
| 1 | Detalhe do 01/2026: ações preenchidas | 1 — **Cancelar** (vermelho cheio) |
| 2 | Detalhe do 01/2026: disposição das ações | 7, uma por linha (topos 462 a 759) |
| 3 | Detalhe do 01/2026: "Quem atuou" | 495 px, para 236 de conteúdo |
| 4 | Condução do marco 1 do 01/2026: gestos preenchidos | 4 de 4, empilhados (topos 738, 794, 850, 1.083) |
| 5 | Lista: altura da linha de Edital publicado | 118 px (a auditoria mediu 125, antes da `055`) |
| 6 | Lista: largura da coluna "O que posso fazer" | 384 px |
| 7 | Glossário: altura do bloco | 63 a 84 px |
| 8 | Glossário: topo do primeiro controle ou tabela | Condução 406 · ordem 304 · corte 307 · histórico do corte 344 · ocupação 434 · convocação 307 · sorteio 344 · matrículas 434 |
| 9 | Atenção do Processo: sinais, altura de cada, faixa | 6 cartões com borda dentro do cartão, 74 a 102 px, faixa **verde** (`rgb(21,128,61)`) |
| 10 | Atenção da Supervisão | idem, 6 cartões |
| 11 | Auditoria do 51/2026: altura média por evento | 105,2 px (12 eventos, 1.262 px; a auditoria mediu 97 sem a margem) |
| 12 | Detalhe da inscrição: documentos | 2 cartões de 1.232 × 114 px |
| 13 | Distribuição: ficha | 1.232 × 74 px, 2 dados |
| 14 | Minha etapa (`joana.avaliadora`): ficha | 1.232 × 74 px, 3 dados |
| 15 | Revisão do 76/2027 | "Peso: 2.0000", "Nota mínima: 6.0000", "Peso: 1.0000", "20.0000%", "versão 2014-06-09", "2 vaga(s) imediata(s)", "1 vaga(s)", "0 vaga(s) imediata(s)" |
| 16 | Alocação (9 Etapas): largura da página | 1.398 px |
| 17 | Alocação: altura do `thead` | 174 px; colunas de 108 a 123 px; "01/2026" repetido três vezes |
| 18 | Portal, "Sua inscrição" de MARIA (01/2026): seletor × "Enviar" | duas linhas: seletor em y = 1.157, "Enviar" em y = 1.201; bloco de 88 px |
| 19 | HTML da distribuição (`test_escala_da_mesa`) | **83.294** caracteres |

### A tabela "antes" da auditoria, no que este lote toca

| Medida | Auditoria (30/09, `c0f5ad3d`) | Hoje, antes deste lote (`94cb4914`) |
|---|---:|---:|
| Altura de linha da Lista de Editais | 125 px | 118 px |
| Largura da página da Alocação por Etapa | 1.398 px | 1.398 px |
| Altura do cabeçalho da Alocação | 174 px | 174 px |
| Auditoria, por evento | ~97 px | 105,2 px com a margem |
| "Quem atuou" | 515 px | 495 px |

As demais linhas da tabela da auditoria (Inscrições, Perfis, Conteúdo, Revisão, Retificar) são dos
lotes 1 e 2.

## Depois

Medido no mesmo banco, com o mesmo método, sobre a árvore do PR.

| # | Medida | Antes | Depois | Meta | |
|---|---|---:|---:|---|---|
| 1 | Detalhe do 01/2026: ações preenchidas | Cancelar (vermelho cheio) | **Inscrições recebidas (0)**, a única | uma, nunca a destrutiva | ✓ |
| 2 | Detalhe do 01/2026: disposição | 7, uma por linha | 5 em três linhas; Encerrar e Cancelar depois de um filete, **contornados** em vermelho, com "IRREVERSÍVEL" | secundárias em linha; destrutivas por último | ✓ |
| 3 | "Quem atuou" | 495 px (236 de conteúdo) | **237 px** | altura do conteúdo | ✓ |
| 4 | Condução do marco 1 do 01/2026 | 4 cheios, empilhados | **1 cheio** (Ordenar), 3 secundários; os três primeiros na mesma linha, "Publicar" com os dois campos dele na seguinte | um primário | ✓ |
| 5 | Lista: altura da linha (Edital publicado) | 118 px | **82 px** | ≤ 90 | ✓ |
| 6 | Lista: ordem das ações | Retificar, Inscrições, Recursos, Exportar, Encerrar, Cancelar | **Inscrições, Recursos**, Retificar, Exportar · \| Encerrar, Cancelar; "(0)" esmaecido | frequentes primeiro, destrutivas no fim | ✓ |
| 7 | Glossário | aberto, 63 a 84 px | **fechado**, `summary` de 31 px; a faixa "não pratica nada" à vista | fechado; faixa visível | ✓ |
| 8 | Glossário: topo do primeiro controle ou tabela | 406 · 304 · 307 · 344 · 434 · 307 · 344 · 434 | 374 · 251 · 275 · 291 · 402 · 275 · 291 · 381 (sobe **32 a 53 px**) | sobe ≥ 120 | **fora de alcance** (D-020) |
| 9 | Atenção do Processo | 6 cartões com borda no cartão, faixa verde | **lista com filete**, faixa **âmbar** (`rgb(138,83,0)`) única; zero caixas com borda dentro de outra | lista, âmbar | ✓ |
| 10 | Atenção da Supervisão | 6 cartões | idem, a mesma regra | idem | ✓ |
| 11 | Auditoria do 51/2026: média por evento | 105,2 px | **60,3 px** (1.262 → 723 px para 12 eventos) | ≤ 70 | ✓ |
| 12 | Detalhe da inscrição: documentos | 2 cartões de 1.232 × 114 | `ul.documentos`, uma linha por requisito (~69 px), zero caixas dentro de caixa | desenho da mesa | ✓ |
| 13 | Distribuição: ficha | 1.232 px | **433 px** | largura do conteúdo | ✓ |
| 14 | Minha etapa: ficha | 1.232 px | **582 px** | largura do conteúdo | ✓ |
| 15 | Revisão do 76/2027 | "Peso: 2.0000", "20.0000%", "versão 2014-06-09", "vaga(s)" | **"Peso: 2"**, **"Nota mínima: 6"**, **"Peso: 1"**, **"20%"**, **"versão 09/06/2014"**, **"2 vagas imediatas"**, "1 vaga", "0 vagas"; nenhum "(s)", nenhuma data aaaa-mm-dd | como o critério | ✓ |
| 16 | Alocação: largura da página | 1.398 px | **1.280 px** (a matriz termina em x = 1.256, a borda do conteúdo) | ≤ 1.280 | ✓ |
| 17 | Alocação: altura do `thead` | 174 px | **127 px**; "Edital 01/2026" uma vez, sobre as três Etapas dele | ≤ 130 | ✓ |
| 18 | Portal: seletor × "Enviar" | duas linhas (y 1.157 e 1.201) | **uma linha** (y 1.157 e 1.157), a dica logo abaixo | uma linha a 1.280 | ✓ |
| 19 | HTML da distribuição | 83.294 | **83.444** (+150) | < 120.000 | ✓ |

### As listas de ações (2ª decisão recebida)

Capturadas com o cliente de teste do Django, lendo o HTML servido, em 62 telas com `ana.gestora` e
49 com `joana.avaliadora` (as que recusam com 403 ou 404 entram com o status, e o status também é
comparado): 416 e 101 destinos. A chave de idempotência dos formulários, aleatória a cada carga, é
normalizada nas duas capturas.

```
telas: {'ana.gestora': 62, 'joana.avaliadora': 49} destinos: {'ana.gestora': 416, 'joana.avaliadora': 101} diferenças: 0
```

O portal ("Sua inscrição" de MARIA), à parte: 4 destinos antes, os mesmos 4 depois.

### A 375 px

| Tela | Resultado |
|---|---|
| Detalhe do Edital (01/2026 e 76/2027) | página de 375 px; nenhum controle fora da tela |
| Alocação | página de 375 px; a matriz rola dentro da moldura (`overflow-x:auto` abaixo de 60 rem, a decisão registrada), e os controles do cabeçalho se alcançam por ela |
| Portal, envio de documento | página de 375 px; seletor e nome numa linha, "Enviar" na seguinte, a dica embaixo — a 9ª decisão admite a quebra |
| Lista de Editais | a coluna de ações fica **recortada** pelo cartão — igual antes e depois, com 24 ou 30 rem: defeito anterior, [registrado](../../doc/achado-lista-e-conducao-a-375px.md) |
| Condução do marco | a página rola na horizontal (486 px) pela tabela do indicador — igual antes e depois, registrado no mesmo documento |

### A suíte

`cd backend && make lint check test-pg DB_NAME=ps057t`, sobre a árvore do PR: `ruff check` e
`ruff format --check` limpos, `manage.py check` sem problemas, e **9.099 passando e 11 pulados** em
869 s — os mesmos onze pulados deliberados de antes. Os testes de JavaScript vêm junto, por
`tests/test_javascript.py`.

### Comentários da folha

A conversão dos comentários documentais da folha da gestão para `{% comment %}` já estava na `main`
(`1c4ae6c4`, da `056`). O único `/* */` restante na folha da gestão está dentro de uma frase de
comentário do template, e não é regra desativada. Toda prosa nova desta feature nasceu em
`{% comment %}`.

### Capturas

`capturas/`: `detalhe`, `lista`, `auditoria` e `alocacao`, antes e depois, e `processo-depois`
(a Atenção no fim da página). Renderizadas pelo cliente de teste do Django contra o mesmo banco e
fotografadas no Chrome sem janela, a 1.280 px.
