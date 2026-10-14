# Pesquisa técnica — 072

As decisões de produto estão na [spec](spec.md) (D-001 a D-007, Q1 a Q9 e a clarificação de 12/10).
Aqui ficam as escolhas técnicas, em `T-NNN`, com o que foi lido no código para tomá-las.

## Linha de base medida (12/10/2026, banco `ps_ux_conversao`, `seed_demo`)

| Página | Consultas hoje |
|---|---|
| `/selecoes/` (3 cartões) | 2 |
| `/selecoes/<Edital 01>/` (sem resultado) | 8 |
| `/selecoes/<Edital 51>/` (com resultado) | 10 |

A vitrine não tem teste de orçamento de consultas hoje; a página da seleção tem
(`tests/portal/test_prazo_recursal_publico.py`, `test_a_lista_do_edital_nao_consulta_a_cadeia_degrau_por_degrau`).

## T-001 — O resumo de resultados sai da mesma leitura da página, feita para vários Editais

**Decisão.** `historico_publico_do_edital(edital)` (`divulgacao/application/selectors.py`) ganha a
irmã `historico_publico_dos_editais(editais) -> {edital_id: vigentes}`, com o mesmo corpo aplicado a
`edital__in`, e a função de um Edital passa a ser a consulta de vários com um elemento. O cálculo do
prazo que hoje está dentro de `views.selecao` — `conteudos_citados` + `janela_da_publicacao_divulgada`
\+ "só enquanto `agora <= fim`" — sai da view para `portal/leitura.py`, numa função que as duas páginas
chamam. O resumo do cartão (D-004) é uma função pura sobre a lista que essa função devolve.

**Por quê.** É a exigência de não reproduzir regra de vigência em outro lugar: vigente, cadeia e prazo
continuam calculados por um único caminho. A página da seleção passa a chamar a versão extraída, e os
testes dela continuam valendo como prova de que nada mudou.

**Custo.** Para a vitrine: + 2 consultas fixas (publicações e sucessoras) e + 1 quando há resultado
(versões citadas). O número de consultas não cresce com o número de cartões; o processamento cresce
com as publicações lidas — cada uma decodifica o cabeçalho público, como já acontece na página da
seleção. Nenhum cache, nenhuma persistência.

**Alternativas recusadas.** Chamar `historico_publico_do_edital` por cartão (N+1, a 2 consultas por
Edital); um resumo gravado no banco na publicação do resultado (persistência nova para um dado
derivável, e um segundo lugar onde a vigência seria decidida).

## T-002 — Os filtros recolhidos: `<details>` nativo, aberto por padrão só quando há filtro aplicado

**Decisão.** Em `_consulta.html`, a busca e o botão "Filtrar" ficam fora; unidade, situação, Perfil e
ordenação entram num `<details class="mais-filtros">` com `<summary>Mais filtros e ordenação</summary>`.
O servidor renderiza `open` quando algum desses quatro tem valor aplicado (a ordem padrão não conta,
como já não conta para `consulta.ativa`). Em tela larga, um script pequeno e síncrono
(`portal/consulta.js`, carregado logo depois do `<details>`, sem `defer`) abre o grupo e marca a
classe que esconde o `<summary>`; o CSS faz o miolo do grupo fluir na mesma linha da busca, como hoje.

**Por quê.** O recolhimento funciona sem script em qualquer largura (FR-1603). O script não filtra
nada: só abre, em tela larga, o que no celular fica fechado — e, sendo síncrono e logo depois do
elemento, roda antes da primeira pintura, sem salto de leiaute. Sem script, a tela larga mostra o
grupo fechado com o seu `<summary>` — degradação funcional, não quebra.

**Alternativas recusadas.** `::details-content` sozinho (suporte incompleto em Safari e WebViews
anteriores a 2025); `display: contents` no `<details>` (comportamento divergente entre navegadores);
duplicar os controles em duas marcações por largura (dois `id` para o mesmo campo quebram o `label
for`); caixa de seleção escondida com `:checked` (estado não exposto ao leitor de tela).

## T-003 — A volta da identificação leva uma mensagem de uso único, guardada na sessão

**Decisão.** Uma chave nova de sessão, `portal_volta_a_vaga`, gravada nos dois pontos que hoje
redirecionam para `_de_volta_a_vaga` com destino de vaga — `_entrar` (identidade com núcleo) e
`meus_dados` (depois de gravar nome e CPF) —, com o identificador do Perfil e a marca "dados
guardados". `views.selecao` a lê e a remove **só quando o Perfil pertence ao Edital da página**, e
passa ao template a mensagem para aquele Perfil. Com a mensagem, a resposta é marcada como privada
(`marcar_como_privada`), porque passa a conter o e-mail da pessoa.

**Por quê.** É o mecanismo que o portal já usa para avisos de uso único (`_avisar`/`_mensagens`), sem
o defeito que ele tem aqui: `_mensagens` é consumido pela tela seguinte qualquer que seja ela, e é
assim que "Seus dados foram guardados." aparece hoje fora de contexto, na tela da inscrição (FR-1625).
O `_avisar` de `meus_dados` deixa de existir quando o destino é uma vaga.

**Risco tratado.** A página da seleção é pública e só vira privada quando a pessoa tem inscrição
iniciada. Uma identidade nova não tem; sem a marcação, um cache compartilhado guardaria a página com o
e-mail de alguém.

## T-004 — O contexto da vaga nas telas de acesso deriva do destino já validado

**Decisão.** Uma função `_vaga_do_destino(destino)` em `portal/views.py` reusa `_rota_do_destino` e,
quando a rota é `portal:inscrever`, lê a versão vigente do Edital (`selectors.selecao_publica`) e
devolve nome do Perfil, número, ano e título do Edital — ou `None` se a rota não for de vaga, se o
Edital não for público ou se o Perfil não existir na vigente. `acesso`, `acesso_codigo`,
`acesso_reconciliar` e `meus_dados` leem o destino que já guardam (`CHAVE_DO_DESTINO`, validado por
`_destino_seguro`) e passam o resultado ao template.

**Por quê.** Nenhuma validação nova de destino: o que chega à função já passou pelas de hoje. E nada
depende do e-mail, de modo que a resposta continua equivalente exista ou não identidade (FR-1620).
Custa uma leitura da versão vigente por tela de acesso, e só quando há destino de vaga.

## T-005 — A oferta por Perfil é uma função, usada pelo cartão e pelo resumo da página

**Decisão.** `leitura.quantidade_da_oferta(vagas, tipo_de_reserva)` devolve "3 vagas", "3 vagas e
cadastro reserva", "cadastro reserva" ou "" (FR-1607); `leitura.os_primeiros(itens, teto, termo)`
devolve os itens até o teto e quantos sobram, pondo primeiro os que casam com o termo da busca
(FR-1608 a FR-1610). O cartão e o resumo do cabeçalho da seleção usam as duas.

**Por quê.** Duas telas dizendo a mesma quantidade não podem ter duas redações. O `RESERVA` de
`views.py` continua sendo a tradução do tipo de reserva.

## T-006 — A unidade pela sigla do registro: uma consulta para a página inteira

**Decisão.** A vitrine lê `Unidade.objects.filter(codigo__in=escopos)` uma vez e usa a sigla; sem
registro, cai na chave em caixa alta de hoje. O título da vitrine usa a sigla quando o catálogo tem
uma unidade só (FR-1611).

## T-007 — O destaque da vaga indicada no endereço é CSS (`:target`)

**Decisão.** `.perfil:target` ganha borda esquerda mais grossa e uma etiqueta textual por `::before`
("Vaga indicada"), além do tom de fundo; `scroll-margin-top` evita que o cabeçalho cubra o alto do
cartão. A mensagem de volta (T-003) vem no HTML, com `role="status"`.

**Por quê.** O fragmento do endereço não chega ao servidor — campanha e compartilhamento só podem ser
atendidos no navegador, e `:target` faz isso sem script. Forma (espessura) e texto, além da cor
(FR-1617).

## T-008 — O vocabulário proibido passa a valer para as telas públicas

**Decisão.** Um teste novo renderiza vitrine, seleção (aberta, encerrada com resultado) e as telas de
acesso com destino de vaga, e aplica a elas o dicionário `PROIBIDAS` de
`tests/portal/test_acompanhamento_pela_situacao.py` (importado, não copiado) sobre o texto visível.

## T-009 — Verificação sem script e nas larguras

**Decisão.** A verificação visual usa o script da auditoria (`doc/auditoria-ux-conversao-2026-10-12/medir-primeira-tela.js`),
que renderiza em `iframe` com largura e altura fixas. Para "sem script", o mesmo HTML é renderizado em
`iframe` com `sandbox="allow-same-origin"` (sem `allow-scripts`), que bloqueia a execução de script.
Nos testes, a garantia é estática: nenhum `hx-`/`onclick` na consulta, e o recolhimento funcionando
com o `open` do servidor.

## Achados laterais (registrar, não fazer)

- **A vitrine não tinha teste de orçamento de consultas.** Esta feature acrescenta um, porque passa a
  ler resultados.
- O contraste do contorno de campo (auditoria, C-17) continua fora de escopo.
