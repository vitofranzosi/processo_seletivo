# Rastreabilidade — 052 · Perfis de Vaga: a visão do conjunto e um editor por vez

**Frase que governa**: *a etapa mostra o conjunto e um Perfil por vez, e envia exatamente o que enviava.*

Cada linha aponta o lugar do código e o que o prende. **TV** = `tests/interface/test_visao_dos_perfis.py`;
**TJ** = `tests/javascript/perfis.test.js`; **NAV** = verificado no navegador real, no preview, pelo
roteiro de [quickstart.md](quickstart.md) — o que o shim de DOM não reproduz (foco, `hidden`,
validação nativa, fragmento do endereço), medido em 29/09/2026 a 1280×900 e a 375×812, com os
números na seção 3. **Leitura do diff** é promessa negativa, que se confere lendo a mudança.

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-944** | filtro `legenda_do_perfil` (`templatetags/interface_extras.py`); `<legend>` de `_perfil.html` | TV `test_a_legenda_identifica_o_perfil`, `test_a_etapa_identifica_cada_cartao_pela_legenda`, `test_o_perfil_acrescentado_nasce_como_perfil_novo` |
| **FR-945** | `perfis.js`: `montarTabela` (só com mais de um), `mostrar` (um só sempre à vista) | TJ `com um Perfil só, ele é sempre o aberto`; NAV 1, 2 e a passagem 1 ↔ 2 |
| **FR-946** | `perfis.js`: `COLUNAS`, `lerCartao`, `resumo` | TJ `a linha diz o Perfil com as frases da tela`, `o limite só acompanha a reserva limitada`, `Modalidade sem código não entra…`, `o percentual volta sem as casas da gravação…` |
| **FR-947** | `perfis.js`: `aoDigitar` → `atualizar`; `resumo` só ecoa campos (leitura do diff: nenhuma soma, nenhuma regra) | NAV 2 (as vagas mudam na linha ao digitar) |
| **FR-948** | `views._pendencias_por_perfil`, `data-pendencias`; `perfis.js` `situacao` | TV `test_so_a_pendencia_que_nomeia_um_perfil_vai_para_a_linha`, `test_o_cartao_diz_quantas_pendencias_da_etapa_o_tem_por_objeto`; TJ `a situação são dois fatos, em texto` |
| **FR-949** | `forms.perfis_alterados`, `data-nao-salvo`; `perfis.js` `alterado`, `controleAlterado`, `trazCampoDoFormulario` | TV `test_a_devolucao_sem_mudanca_nao_acusa_perfil_nenhum`, `test_a_devolucao_acusa_so_o_perfil_mudado`, `test_perfil_que_so_existe_na_tela_e_alterado`, `test_a_comparacao_ignora_o_que_o_cartao_nao_mostra`, `test_a_etapa_aberta_do_banco_nao_diz_que_devolveu`; TJ `o controle difere…`, `o select que nasce sem opção marcada…`; NAV 5 |
| **FR-950** | `perfis.js` só alterna `hidden` (R-001) | TV `test_o_script_nao_cria_remove_nem_renomeia_campo`; NAV 2 (os sete gravados pelo mesmo envio) |
| **FR-951** | `perfis.js`: `abrir`, título *"Editando …"*, `aria-current` | NAV 2 |
| **FR-952** | `perfis.js`: `vizinho`, `voltarALista` (botões `type=button`) | TV `test_o_script_nao_cria_remove_nem_renomeia_campo` (nenhum envia); NAV 2 |
| **FR-953** | `perfis.js`: `cartaoAAbrir`, `lembrar` (fragmento), `salvo`/`aplicado` o descartam | TJ `a recusa vence o endereço…`, `depois de gravar, o endereço não reabre…`; NAV 4, 5 e o *Salvar* |
| **FR-954** | `perfis.js`: ouvinte de `invalid` em captura, um cartão por rodada | NAV 3 — o Chrome abriu o cartão, focou o campo e não enviou |
| **FR-955** | `#visao-dos-perfis` vazio e oculto; nenhum `hidden` no servidor | TV `test_sem_script_a_etapa_e_a_de_sempre` |
| **FR-956** | `perfis.js`: observador de `#perfis`, `novos`; o foco é do `assistente.js` | NAV 6 |
| **FR-957** | idem; a cópia entra `afterend` da origem, como na `043` | NAV 6 — a cópia logo abaixo da origem, aberta, com o aviso da `043` |
| **FR-958** | `perfis.js`: observador, `posicaoDoRemovido`, `lembrar(null)` | NAV 6 e a passagem 2 → 1 |
| **FR-959** | leitura do diff: nenhuma rota, gravação ou gesto tocado | as suítes da `043`, da `051`, do quadro e do rascunho local, sem mudança (seção 4); NAV 6 (aplicar a todos até a confirmação) |
| **UX-116** | `perfis.js`: `caption` com o número, `th[scope=col]`, `th[scope=row]` | NAV 8 |
| **UX-117** | `perfis.js`: `preencherLinha` — *Editar* + código em `span.oculto` | NAV 8 (nome acessível *"Editar P01"*) |
| **UX-118** | `perfis.js`: *"Em edição"* visível e `aria-current`; situação em texto | TJ `a situação são dois fatos, em texto`; NAV 2 |
| **UX-119** | `perfis.js`: foco no título ao abrir, no *Editar* ao voltar | NAV 2 |
| **UX-120** | ordem de `compor_perfis.html` | TV `test_a_etapa_vem_na_ordem_tabela_conjunto_cartoes` |
| **UX-121** | `.tabela-rolavel` com `position:relative` no `estilo_da_pagina` | TV `test_a_tabela_rola_dentro_do_proprio_conteiner`; NAV 9 |
| **UX-122** | leitura do diff: nada novo dentro do cartão além de atributos | `test_nenhum_cartao_do_assistente_carrega_ajuda_visivel` (`test_medida_dos_campos.py`), sem mudança |

## 2. Critérios de sucesso

| Identificador | Como se mediu | Resultado |
|---|---|---|
| **SC-348** | NAV 1, 7 Perfis a 1280×900 | tabela a 792 px (primeira tela); **3.494 px** com um aberto, contra 14.509 (teto: um quarto, 3.627); **1.542 px** com nenhum (teto: duas telas, 1.800) |
| **SC-349** | NAV 3 | campo obrigatório de Modalidade num cartão fechado: cartão aberto, foco no campo, nada enviado |
| **SC-350** | TV `test_o_script_nao_cria_remove_nem_renomeia_campo`; TV `test_a_devolucao_sem_mudanca_nao_acusa_perfil_nenhum` (o formulário que a tela mostra, devolvido, é o que o servidor aceita) | por construção |
| **SC-351** | NAV 7, Edital de dois Perfis, corrigir as vagas de cada um e salvar | hoje: 1 clique e ~3,9 mil px de rolagem manual; com a vista: 3 cliques (+2) e ~1,6 mil px, **nenhuma rolagem entre um Perfil e outro**. Confirma a `D-002` |
| **SC-352** | NAV 8, árvore de acessibilidade | cabeçalhos de linha e de coluna; *"Editar P01"*; linha em edição com texto visível |
| **SC-353** | seção 4 | nenhum teste da `027`, `043`, `051` ou do rascunho local mudou |

## 3. Casos-limite

| Caso | O que o prende |
|---|---|
| Perfil sem código | TJ `o Perfil sem código ainda aparece, e se edita`; NAV 6 (*"sem código"*, *"Perfil novo"*) |
| Dois Perfis com o mesmo código | FR-954: a marca do `validacao.js` passa pelo mesmo `invalid` (R-002) — NAV 3 cobre a via nativa |
| Pendência de Perfil alterado | TJ `a situação são dois fatos` (*"N pendências · alterado — não salvo"*) |
| Pendência de Perfil removido na tela | leitura do diff: a linha sai com o cartão; o bloco da etapa não muda |
| Restauração do rascunho local | FR-949 no servidor: a restauração é um dos envios que devolvem o digitado (`digitados is not None`) |
| Salvar com um Perfil aberto | TJ `depois de gravar…`; NAV — volta com nenhum aberto e o endereço limpo |
| Envio que volta sem gravar | NAV 5 (o P04 reabriu) e a prévia da `051` (a prévia fica à vista, o cartão reaberto abaixo dela) |
| Endereço que aponta o título da etapa | `cartaoAAbrir` só considera alvo dentro de um cartão (leitura do código) |
| Sem script | TV `test_sem_script_a_etapa_e_a_de_sempre` |
| Tela estreita | TV `test_a_tabela_rola_dentro_do_proprio_conteiner`; NAV 9 (375 px, sem rolagem horizontal) |
| Edital que não está em elaboração | leitura do diff: a vista não depende de `editavel`; os gestos continuam condicionados como antes |

## 4. Verificação

`make lint check` e `make test-pg DB_NAME=ps_052` — números na descrição do PR.
