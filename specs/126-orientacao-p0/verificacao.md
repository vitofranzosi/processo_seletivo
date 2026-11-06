# Verificação: Correções de orientação e segurança operacional (126)

06/11/2026, na branch `claude/126-orientacao-p0-307906`, depois de sincronizada com a `main` em
`a1d3bf26` (que trouxe o #410, da `124`, e o #412, do estudo).

## Suíte contra PostgreSQL

`cd backend && make lint check test-pg`, com `DB_NAME=ps_spec126`, 4 workers, `worksteal`, com os
grupos `dev` e `navegador` e **sem** o `assistente`.

| Rodada | Base | Resultado | Tempo |
|---|---|---|---|
| 1 | antes do merge, antes da revisão | 16765 passando, 13 pulados, **5 falhando** | 874s |
| 2 | depois do merge e da revisão | **16788 passando, 13 pulados, nenhuma falha** | 2380s (outra suíte, da `127`, dividia o cluster) |

As cinco falhas da primeira rodada eram todas desta branch, e foram corrigidas:

| Falha | Causa | Correção |
|---|---|---|
| `test_citacoes_de_requisito` | UX-223 a UX-227 citados sem definição; a faixa citada no cabeçalho da spec | seção *Experiência* na spec; a faixa escrita por extenso |
| `test_readme_acompanha_o_codigo` | a pasta `126` fora da tabela de incrementos | linha da `126` no README |
| `performance/test_relatorio` (×2) | o relatório passa de 119 para 120 consultas: o `prefetch` das comunicações (FR-4027) | orçamento 120, com a razão no arquivo; não cresce com as inscrições |
| `test_nenhum_botao_muda_de_rotulo_desenho_ou_lugar[corte.html]` | a faixa seguinte tinha subido para antes da sucessão | ordem original restaurada |

Os 13 pulados são os doze da linha de base do CLAUDE.md sem o grupo `assistente`, mais a contagem real do
tokenizer, que pula sem ele. Nenhum é desta feature.

`make check`: sem problema, e `makemigrations --check` diz **nenhuma mudança** (FR-4040).

## Testes alterados, e por quê

| Arquivo | Mudança | Razão |
|---|---|---|
| `interface/test_sorteio_extracao_inviavel.py::test_a_sucessao_de_uma_relacao_que_sorteia_tambem_e_avisada` | o aviso deixa de ser procurado no topo e passa a ser procurado no bloco de sucessão | é a mudança da FR-4031/FR-4032; a regra da `102` continua verificada |
| `fixtures/relatorio.py` | a convocação do cenário passa a ser comunicada | o cenário é o de quem aguarda resposta; sem o envio, o relatório agora diz, com razão, "sem comunicação enviada" |
| `unit/interface/test_relatorio_consolidado.py` | o dicionário de convocações ganha `sem_comunicacao` | forma nova do consolidado |
| `performance/test_relatorio.py` | `ORCAMENTO` 119 → 120 | o `prefetch` das comunicações |
| `fixtures/sorteio.py` | `certame_com_cotas` aceita `modalidades` e `metodo` | cenário da lista sem inscrito; o padrão continua o mesmo |

## No navegador

Clone do dump do usuário de 05/11 (`~/Downloads/processo_seletivo.backup`, PostgreSQL 18, num container
descartável na porta 55436), em dois bancos migrados: `ps_antes`, servido pela `main` em `250efe97`, e
`ps_depois`, servido por esta branch antes do merge com o #410. Gestor pelo seletor de identidade. Nomes e
protocolos mascarados antes de cada captura. Em `capturas/`:

| Captura | Antes | Depois |
|---|---|---|
| `a1-corte-26-depois-de-emitir-*` | "Corte emitido." e o formulário de sucessão aberto, com "Emitir corte" | "Corte emitido para Ampla concorrência…: 7 progridem, até a 7ª posição", e "Suceder este corte (exige motivo)" recolhido |
| `a2-conducao-35-vitoria-*` | *Falta* nas doze células, "Cortar o marco…" e "Apurar…" | *Não se aplica* em todas, "Nenhuma operação se aplica", "Nada a conduzir neste marco", nenhum gesto |
| `a2-convocacao-35-vitoria-*` | "Ir para a apuração" e "pedir a faixa seguinte" juntos | "Não se aplica", sem caminho |
| `a2-ocupacao-35-vitoria-*` | "emita a ordem deste recorte" nos três recortes | "Não se aplica" nos três |
| `a4-encerrar-51-*` | "1 convocação aguardando resposta." | "1 convocação sem comunicação enviada." |
| `a5-sorteio-35-cefor-*` | "Não congele a relação hoje" como primeira frase dos recortes | sem o aviso no topo |
| `a5-sucessao-da-relacao-35-cefor-depois` | — | o aviso dentro de "Suceder esta relação (exige motivo)" |
| `a6-confirmacao-ordem-91-*` | "Participantes sem posição: 4 — protocolos" | "Nenhuma inscrição deste recorte tem resultado…", "Prova de Títulos: 4 sem resultado", "Prova de Desempenho Didático: 4 sem resultado", a consequência, e os sem posição agrupados pelo motivo |

**Duas substituições em relação ao pedido.** O container `ps-sorteio-35` e o banco pseudonimizado
`processo_seletivo_guia` já não existiam; o clone saiu do dump original. Nele, o Edital 35 **não** tem a
convocação de C10 que o guia praticou depois, e o Encerrar do 35 não diz nada de convocação: o caso de
SC-1214 foi capturado no **Edital 51**, que tem uma convocação vigente sem comunicação enviada.

## Revisão independente

Um subagente que não escreveu o código leu o diff, a spec e o plano. Achados e destino:

| Achado | Destino |
|---|---|
| UX- sem definição e faixa citada no cabeçalho (quebra o CI) | corrigido (a suíte também pegou) |
| Orçamento do relatório 119 → 120 | corrigido |
| `acao_do_corte` gravada antes do comando: um 404 na faixa seguinte deixava a marca na sessão, e o corte seguinte se diria "faixa seguinte" | corrigido: gravada só depois do sucesso, e a emissão a limpa; teste `test_a_marca_da_faixa_seguinte_nao_sobra_para_o_corte_seguinte` |
| Quem só lê o sorteio (sem bloco de sucessão) deixava de ver o aviso da `102` com todas as relações congeladas | corrigido: para quem não sucede, o aviso continua no topo; teste `test_quem_so_le_continua_vendo_o_aviso_da_sucessao_no_topo` |
| "Sem inscrito" esconderia ato existente (Edital retificado de pontuação para sorteio) | corrigido: recorte com ordem vigente nunca é sem inscrito |
| O botão dentro do bloco continua `botao` | mantido: o guardião da `058` prende rótulo e desenho; o que tira o peso é estar recolhido. O contrato foi ajustado |
| `role="status"` em seção estática | retirado da confirmação da ordem e do aviso dentro do bloco |
| `summary` sem marcador de aberto/fechado | ▸/▾ na folha |
| Mensagem da relação diferente do contrato | o contrato foi ajustado: o prefixo antigo é lido por outras telas e testes |
| `resumo_dos_marcos` (página do Edital, Supervisão) continua contando a lista sem inscrito | fora, de propósito (FR-4041): é presença de ato, e muda com a Spec B |
| Falta teste do caso `qualifyingStageId` da D-002 | limitação registrada: o código o trata (`habilitadas=None`), sem cenário na suíte |
| A abertura da ordem por decisão de recurso vale para todos os recortes do marco | aceito: as decisões a citar são do marco, e é o que a FR-4011 diz |

## Limitações

- Nenhum teste com pessoas.
- A captura de A5 dentro do bloco foi feita com o bloco aberto por script; a tela o mostra recolhido.
- As capturas são de antes do merge com o #410, que mexeu na tela do sorteio em trechos que elas não
  mostram (as mensagens da ocorrência).
