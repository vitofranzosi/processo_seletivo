# Pesquisa — 084

As decisões de governança — o que se escolheu e o que não se muda — estão na spec (D-001 a D-004).
Aqui ficam as questões de desenho e de teste, e os achados.

## R-001 — A trilha das onze telas

**Decisão**: cada template sobrescreve o bloco `caminho_do_contexto` com a mesma
`nav aria-label="Trilha de navegação" class="caminho-da-secao"` da `077` à `080`, o produto pelo
parcial `_produto_na_trilha.html`, e os três níveis do Edital no começo; a `nav class="trilha"` sai do
`main`. Os níveis que vinham depois do Edital, e o rótulo da página atual, são os de antes, com os
mesmos destinos.

| Tela | Trilha antes, no conteúdo | Trilha agora, no cabeçalho |
|---|---|---|
| Classificação | Processos Seletivos › Edital › marco | GPS › Processos Seletivos › código › Edital › marco |
| Conferir emissão | Processos Seletivos › Edital › marco › Conferir | … › Edital › marco › Conferir |
| Ato de classificação | Processos Seletivos › Classificação › Ato *id* | … › Edital › Classificação › Ato *id* |
| Sorteio | Processos Seletivos › Edital › Sorteio — marco | … › Edital › Sorteio — marco |
| Corte | Processos Seletivos › Edital › Corte | … › Edital › Corte |
| Corte histórico | Processos Seletivos › Edital › Corte de *data* | … › Edital › Corte de *data* |
| Ocupação de vagas | Processos Seletivos › Edital › Ocupação de vagas | … › Edital › Ocupação de vagas |
| Histórico da ocupação | Processos Seletivos › Edital › Ocupação de vagas › Histórico | … › Edital › Ocupação de vagas › Histórico |
| Convocação | Processos Seletivos › Edital › Convocação | … › Edital › Convocação |
| Histórico da convocação | Processos Seletivos › Edital › Convocação › Histórico | … › Edital › Convocação › Histórico |
| Exportar para matrícula | Processos Seletivos › Edital › Exportar para matrícula | … › Edital › Exportar para matrícula |

**Antes, contado nos templates em `cf6d7372`**: nenhuma das onze levava ao Processo, e dez levavam ao
Edital — o Ato de classificação saltava dele (SC-743).

**Por quê**: é o desenho da `077` à `080`, e a trilha do Edital no cabeçalho é a da `078`. As telas
moram sob `/gestao/editais/`, e a seção delas, pelo endereço, já é Processos Seletivos: a barra e o
começo da trilha concordam sem declaração nenhuma da view.

**O recorte.** A conferência da emissão volta ao recorte que se confere pela `url_do_recorte` que a
view já entrega (`FR-497` da `034`), e o histórico da convocação volta à Convocação com o mesmo
`?lista=`. O comentário da `034` que explicava isso dentro da trilha sobe com ela, para fora do bloco.
`test_navegacao_entre_recortes.py::test_a_confirmacao_volta_para_o_recorte_que_se_esta_confirmando`
conta os dois links ao recorte — a trilha e "Cancelar e voltar" — na página inteira, e continua
passando sem mudança.

**Nenhuma consulta a mais.** As onze views já passam `processo` ao contexto; o Processo vem do
`select_related` da porta.

**Alternativas**:
- *O marco como nível entre o Edital e a tela* — D-001.
- *Trocar o rótulo do Ato pelo nome do marco* — D-002.

## R-002 — O que não se mexe

- **As mensagens do último envio** já vêm logo depois do título, do contexto e dos termos recolhidos
  da tela, antes de qualquer formulário. Subir acima dos termos poria o primeiro uso de *recorte* e
  *faixa* antes da definição (D-003).
- **A navegação entre recortes** continua no conteúdo: é a escolha do recorte, com `aria-current`
  próprio, e não o caminho até a tela.
- **Os botões de envio**: 24 nas onze telas — 20 com o desenho de ação principal, 2 com o de perigo,
  2 secundários —, congelados pelo teste novo (D-004).
- **Nenhuma regra na folha comum.** O bloco e a classe `caminho-da-secao` existem desde a `077`.

## R-003 — Os testes

Novos em `tests/interface/test_telas_de_resultado_e_atos.py`:

| Teste | Prova |
|---|---|
| `test_a_trilha_mora_no_bloco_do_cabecalho` | nas onze, pela fonte: o bloco com o produto e os três níveis do Edital, uma página atual, nenhuma trilha no conteúdo, o conteúdo pelo `h1` |
| `test_nenhum_botao_muda_de_rotulo_desenho_ou_lugar`, `test_nenhuma_acao_que_nao_se_desfaz_ganhou_peso` | os 24 botões de envio, na ordem, com o desenho de antes |
| `test_nas_telas_do_marco_a_trilha_e_a_do_edital_com_a_tela` | Classificação, Corte, Ocupação e Convocação renderizadas |
| `test_nos_historicos_a_trilha_passa_pela_tela_de_origem_no_mesmo_recorte` | os dois históricos num recorte reservado |
| `test_na_conferencia_da_emissao_o_marco_volta_ao_recorte` | a conferência, pelo POST, num recorte reservado |
| `test_o_ato_de_classificacao_ganha_o_edital_na_trilha` | o Ato, pelo link que a Classificação oferece |
| `test_quem_audita_le_a_mesma_trilha_de_quem_conduz` | a mesma trilha para gestão e auditoria |
| `test_no_corte_historico_a_trilha_termina_na_emissao` | o corte histórico depois de emitido pela tela |
| `test_no_sorteio_a_trilha_e_a_do_edital`, `test_na_exportacao_a_trilha_e_a_do_edital` | o Sorteio pela presidência, e a exportação por quem só exporta |

**Contraprova**: com `ocupacao.html` e `ato_ordenacao.html` de `cf6d7372` no lugar, cinco desses casos
reprovam.

Nenhum guardião existente muda. A varredura dos 53 arquivos de teste que citam estas telas, a trilha
ou o cabeçalho de contexto passou sem emenda — nenhum deles fixava a trilha no conteúdo destas
telas, nem o cabeçalho da `076` nelas.

## Achados registrados, fora do escopo

- **Atos que não se desfazem saem de botão de ação principal.** Das onze telas, só a emissão da
  ordem (pela conferência) e a anulação do sorteio têm o desenho de perigo. Realizar o sorteio,
  publicar e congelar a relação, emitir o corte e a faixa seguinte, apurar a ocupação, convocar,
  registrar o desfecho e emitir a comunicação têm o de ação principal, com que as features que os
  criaram os desenharam. Na `080`, os atos equivalentes da presidência ("Registrar mesmo assim",
  "Retirar N atribuições") têm o de perigo. Rever o peso é governança (D-004): fica registrado, e o
  guardião novo faz qualquer mudança passar por um arquivo à vista.
- **O Ato de classificação se identifica, na trilha, pelo identificador do ato.** São 36 caracteres
  no cabeçalho, e a página atual repete o que o subtítulo diz por extenso (Edital, Perfil, marco,
  quem emitiu e quando). Não mudou aqui (D-002); se o rótulo mudar, muda em outra feature, com quem
  cita o ato por ele.
- **Telas ainda com a trilha no conteúdo**, fora deste escopo e do da `083`, e que não parecem ser
  das inscrições e dos recursos, da `085`: os avisos (`aviso*.html`, `avisos_do_edital.html`,
  `modelo*_de_aviso.html`), as dúvidas, o assistente, a supervisão, a consolidação e as confirmações
  de Processo. Contadas por `grep -l 'class="trilha"'` em 18/10, antes do merge das outras duas.
