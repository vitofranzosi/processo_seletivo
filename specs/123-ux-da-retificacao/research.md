# Research: o MVP de UX da Retificação (123)

Leitura do código em 06/11/2026, sobre a `main` em `250efe97`. Cada item diz o que foi decidido, por
quê, e o que se descartou. As decisões de produto estão na spec (D-001 a D-009); aqui ficam as de
implementação, R-001 a R-013.

## R-001 — A conferência de conteúdo sai de uma função só, extraída do caminho da criação

**Decisão.** Em `publicacoes/application/retificacoes.py`, extrair de `_apply_declared_changes` uma
função pública e sem escrita, `conferir_conteudo(edital, base_content, changes)`, que:

1. eleva as alterações (`elevar_alteracoes`), como `create_retification` e `edit_retification` fazem
   antes de aplicar;
2. aplica (`apply_changes`) e traduz a recusa de caminho (`_recusa_de_caminho`);
3. roda, **na mesma ordem**, `_recusar_troca_pelo_objeto_inteiro`, `_recusar_o_que_o_ato_acrescenta`
   e `_reject_stale_changes`;
4. calcula os impeditivos com `impeditivos_do_conteudo(content, topologia_publicada(edital))`.

Devolve `(content, recusa, impeditivos)`: `recusa` é o `DomainError` da primeira guarda que recusou
(e então `impeditivos` vem vazio, porque a criação pararia ali), ou `None`.

`_apply_declared_changes` passa a chamá-la e a levantar: a `recusa`, se houver; senão
`_recusa_dos_impeditivos(contexto, impeditivos)`, com a mesma mensagem de hoje ("… possui erros
impeditivos: a; b"); senão segue para o efeito prático. `_assert_well_formed`, que a publicação usa
por fronteira, passa a chamar `impeditivos_do_conteudo` com `situacoes` — a única diferença entre
os dois chamadores, e a que já existe.

**Por quê.** A FR-3940 pede as mesmas funções, ordem e parâmetros. Uma função chamada pelos dois
caminhos é a única forma de isso continuar verdade depois da próxima guarda que alguém acrescentar.

**Descartado.**

- *Chamar `_apply_declared_changes` na conferência e capturar o `DomainError`*: devolve uma frase só,
  com os impeditivos concatenados, e sem a localização de cada um — o link da FR-3942 ficaria sem
  base.
- *Chamar só `validate_for_publication` na view*: pula as guardas e a elevação, e a conferência
  diria "pode criar" para um ato que a guarda recusa.

## R-002 — Os parâmetros da conferência são os da criação, e um teste os prende

**Decisão.** `impeditivos_do_conteudo(content, topologia, situacoes=None)` chama
`validate_for_publication(content, ato=ATO_DE_RETIFICACAO, topologia=topologia, situacoes=situacoes)`
e fica com `blocking_findings`. A conferência e a criação não passam `situacoes` nem
`marcos_sorteados`; `agora` é o padrão (o relógio no instante da chamada).

**Por quê.** É o que `_apply_declared_changes` faz hoje (`retificacoes.py:224`). A consulta à fonte
do sorteio é de rede e é da publicação (FR-3644 da `116`): `None` significa "não rodou", e não há
achado dela na criação.

**Guardião.** Um teste unitário substitui `validate_for_publication` por um espião e confere que a
conferência e a criação a chamam com os mesmos argumentos nomeados, para o mesmo formulário.

## R-003 — Na edição, o conteúdo conferido é o da fusão

**Decisão.** A conferência da edição confere `conteudo_base(item.base_snapshot)` com
`fundir(projecao_da_base, existentes, todas, desfeitas=desfeitas)[0]` — exatamente o par que
`gravar` passa a `edit_retification` (`views.py`, `retificacao_editar`).

**Implementação.** `_compor_retificacao` ganha um terceiro argumento-função, `proposta(todas)`, ao
lado de `gravar`: na criação devolve `todas` sobre `projecao`; na edição, a fusão sobre a projeção
da base. A conferência e a marca «na proposta» (R-005) leem o que ele devolve. A fusão que recusa
(`ValueError`) vira a recusa da conferência, como na gravação.

**Descartado.** *Conferir o proposto mais a diferença*: ignora as remoções desfeitas e confere um
conteúdo que a gravação não grava.

## R-004 — Da localização ao cartão: exato, descendentes, ancestral, seção

**Decisão.** Uma função de `interface/retificacao.py`, `cartao_do_caminho(grupos, caminho, novas={})`,
sem banco, que devolve a referência do cartão (ou da seção) para um caminho normativo de **achado**,
nesta ordem:

1. **exato**: o grupo cujo `caminho` é igual a `caminho`;
2. **linha nova**: se o primeiro segmento por identidade (`/colecao/id=<id>` ou
   `/…/subcolecao/id=<id>`) está em `novas` — o mapa identidade → `novo-<prefixo>-<indice>` que
   `diferencas` monta na mesma requisição (R-006) —, a linha nova;
3. **descendentes**: o primeiro grupo, na ordem da tela, cujo `caminho` começa por `caminho + "/"` —
   o achado da soma do quadro, em `/profiles/id=…/vacancyTable` (`validation.py:3426`), leva à
   primeira linha do quadro daquele Perfil;
4. **ancestral**: o grupo de maior `caminho` que é prefixo de `caminho` em fronteira de segmento
   (`/profiles/id=A` não é prefixo de `/profiles/id=AB/…`). O grupo da raiz (caminho vazio) é o
   ancestral dos caminhos cujo primeiro segmento é campo de `CAMPOS_RAIZ` (`title`, `description`,
   `maxInscricoesPorCandidato`, `matriculationRequest`, `drawMethod`, …), e só deles — o achado em
   `/drawMethod` (`validation.py:1905`) leva à Identificação;
5. **seção**: a seção da tela que contém a coleção do primeiro segmento, pela inversão de
   `COLECAO_DO_TIPO` (`retificacao.py:1647`) até o `tipo` e de `SECOES_DA_TELA` até a seção — **só se
   a seção estiver na página** (Etapas, Documentos e Seções somem quando vazias, `retificacao.py:1630`);
6. senão, nada.

**Por quê.** Os caminhos dos achados são os da gramática da `004` (`_caminho_da_entidade`), por
identidade, e os dos grupos também (`retificacao.py:1333`). O exato vem antes dos descendentes para
que um achado sobre o Perfil não vá para a primeira Modalidade dele. A referência devolvida é a opaca
(`cartao-g12`, `s-cronograma`): o HTML não ganha caminho (FR-3933).

## R-005 — A proposta vira marca, e `ADD`/`REMOVE` só casam a própria entidade

**Decisão.** `referencias_na_proposta(grupos, alteracoes, novas={})` devolve `(referencias,
remocoes_sem_cartao)`, com uma regra por operação:

- **`REPLACE`**: o cartão de R-004 passos 1 e 4 (exato ou ancestral). O `REPLACE` em
  `/profiles/id=X/generalCompetitionModalityId` que a Modalidade nova emite (`retificacao.py:1049`)
  marca o Perfil — o campo «Modalidade que é a ampla concorrência» é dele, e muda.
- **`ADD`** (em `/…/colecao/-`): a identidade do `newValue` dá o caminho da entidade nova. Casa
  **só** o grupo exato (o caso da edição, em que a acrescida já está no proposto) ou a linha nova de
  `novas` (o caso da criação). **Nunca** o ancestral: a linha do quadro, a Modalidade e o critério
  acrescentados (`retificacao.py:2296`, `:1033`, `:1065`, `:1167`) não marcam o Perfil.
- **`REMOVE`**: casa **só** o grupo exato (a criação, em que o cartão marcado para remover existe).
  Sem grupo exato — a edição, em que a entidade removida já não está no proposto —, entra em
  `remocoes_sem_cartao`, e essa contagem MUST ser a mesma de `edicao.remocoes` não desfeitas.

**Onde roda.** Criação: `grupos` da base, `alteracoes = proposta(todas)` (que já inclui as dos gestos:
`todas = alteracoes + …calculado.alteracoes`), `novas` de `diferencas`. Edição: `grupos` do
proposto, `alteracoes` = o ato inteiro (R-003); no GET, `alteracoes_declaradas(item)`.

**Por quê.** FR-3928 proíbe um segundo cálculo de diferença: o conjunto é o mesmo que vai a
`gravar`. Com "maior prefixo" para tudo, o Perfil intocado ganharia «na proposta» por uma linha do
quadro acrescentada, e a edição contaria a remoção de uma Modalidade como alteração do Perfil.

## R-006 — Cada linha do resumo carrega a referência opaca do campo e do cartão

**Decisão.** Cada item do resumo ganha `cartao` e `campo`:

- linhas do laço de grupos de `diferencas` (campo, nascimento, arquivo, lista de texto, remoção): o
  grupo e o campo em mão (`retificacao.py:2135` em diante);
- linhas novas: `_linhas_novas` (`retificacao.py:1933`) passa a devolver o **índice** de cada linha, e
  a referência é `novo-<prefixo>-<indice>`; `diferencas` monta também o mapa `novas` (identidade do
  `newValue` de cada `ADD` → essa referência), válido só nesta requisição, porque as identidades novas
  são `uuid4()` a cada envio (`retificacao.py:1965`, `:2018`, `:2299`);
- linhas montadas fora do laço — as da Modalidade nova (`resumo.extend(linhas)`, `retificacao.py:2256`)
  e o vínculo automático do Documento ao remover um Anexo, no fim de `diferencas` —: a referência sai
  de `cartao_do_caminho` sobre o `targetPath` da Alteração que a linha descreve.

`campo` é `None` quando a linha fala do cartão inteiro (remoção, acréscimo). O template desenha «Ir ao
campo» com `href="#c-<campo>"` ou «Ir ao cartão» com `href="#cartao-<cartao>"`. Os seis fragmentos
de linha nova ganham `id="cartao-novo-<prefixo>-<indice>"`.

**Por quê.** Os gestos já fazem o mesmo («Ir ao cartão de origem», 051).

## R-007 — A marca do servidor é atributo e palavra; a do cliente continua como está

**Decisão.** O template marca o `fieldset.linha` com `data-na-proposta` e acrescenta à legenda o
selo `<span class="na-proposta">na proposta</span>`, renderizado no servidor (sem script). O
`retificacao.js` continua pondo `data-alterado` e o selo «alterada» pelo `default*` do DOM; os dois
selos convivem na legenda.

**Os sinais da barra** são atributos do formulário, **escritos depois** de `data-conferido`, que fica
como está (`retificar.html:146`; `test_aplicar_a_todos_na_retificacao.py:175` afirma o literal
`action="…" data-conferido`):

- `data-modo="edicao"` na edição; ausente na criação;
- `data-enviado` em toda resposta a POST (com ou sem recusa) — é o que distingue "antes da primeira
  conferência" de "depois", e não o `data-conferido`, que falta quando não há resumo;
- `data-proposta` = `nao-conferida` | `recusada` | `conferida`, com `data-proposta-cartoes=N` e, na
  edição, `data-proposta-remocoes=K`.

O script compõe as duas frases de contracts §1.5. A `span.contagem` de hoje continua **o primeiro**
filho que o script põe na barra, com a frase do segundo estado; a frase da proposta vai num
`span.estado-da-proposta` **depois** dela. Assim `barra.filhos[0]` continua sendo a contagem
(`retificacao.test.js:137`, `:143`, `:162`, `:186`, `:199`).

**Por quê.** A marca da proposta precisa existir sem JavaScript, porque é o servidor que a sabe; a
frase da barra já é do script. Um atributo por pergunta mantém um dono por estado.

**CSS.** `.na-proposta`, `[data-na-proposta]` e `.estado-da-proposta` ganham regra em
`interface/static/interface/telas/retificar.css`, distintas de `[data-alterado]`, com contraste AA.

## R-008 — A busca indexa o que a tela desenha, uma vez, no carregamento

**Decisão.** Em `retificacao.js`, `montarFiltro()` monta um índice dos campos dos
`fieldset.linha[data-linha]`: para cada controle editável (os mesmos de `editaveis()`), o texto de
busca normalizado (NFD sem marcas combinantes, minúsculas, espaços colapsados) de: título da seção
(`h2` da `.secao-da-retificacao`), legenda visível (`legend` sem os selos), `data-nome`, o `label`
do campo e o valor elegível (FR-3918: `input[type=text]` e a opção escolhida de `select` cujas
opções não são só Sim/Não). O valor se lê **no momento da busca**, e não no índice, para refletir o
digitado.

`aplicar()` passa a: normalizar o termo; abaixo de 2 caracteres, não filtrar; dividir em palavras;
para cada cartão, separar o **contexto** (seção, legenda, `data-nome`) do **próprio** de cada campo
(rótulo e valor elegível). Um campo dá resultado quando todas as palavras estão em contexto + próprio
e ao menos uma está no próprio; o cartão sem resultado de campo dá **um** resultado de cartão quando
todas as palavras estão no contexto (FR-3917). Um cartão fica visível se deu resultado de qualquer
tipo (ou, sem termo, como hoje); a lista mostra até 25 resultados, na ordem do documento.

**Por que dois tipos.** Com uma regra só, «vagas» casaria com a legenda "Linha do quadro de vagas" e
listaria também a «Lista de concorrência» de cada linha; o nome de um marco listaria os 22 campos
dele. A exigência de uma palavra no próprio campo é o que separa "achei o campo" de "achei o
cartão".

**A lista.** Um `ol.resultados-da-busca` dentro da caixa do filtro, fora do envio (sem `name`), com
um `a.ir-ao-campo` por item, `href="#c-<ref>"` (resultado de campo) ou `href="#cartao-<ref>"`
(resultado de cartão, cujo `irAoCampo` foca o primeiro controle editável do cartão). O clique (e o Enter) chama `irAoCampo(ref)`, que tira
`hidden` do cartão e da seção, faz `scrollIntoView({block: "center"})` e `focus()` no controle.
`aria-label` do link: "Ir ao campo <rótulo> — <cartão>".

**Teclado.** Enter em «Encontrar» já é interceptado (`preventDefault`); passa também a focar o
primeiro `a.ir-ao-campo`, se houver.

**Por quê.** O que a pessoa lê é o que ela digita: a legenda e o rótulo, e não o `data-nome`, que
diverge (`RU-01`). Ler o valor na hora evita índice velho depois da digitação.

**Descartado.** *Indexar no servidor um `data-busca` por cartão*: duplicaria texto de 180 campos no
HTML, não veria o digitado e misturaria os campos do cartão.

## R-009 — A frase da base sai de uma função, e um fragmento a desenha

**Decisão.** Em `interface/views.py`, `_ultima_versao_publicada(edital)` substitui o nome de
`_versao_vigente` (mesma consulta, mesmo resultado: FR-3936). Uma função nova,
`descrever_versao_base(versao, agora)`, em `interface/retificacao.py`, devolve:

- `original_em`: a data de publicação da Publicação original (`_original_version(edital)`);
- `retificacoes`: as de `Publicacao.objects.filter(pk__in=versao.applied_publications,
  revisao__isnull=True)`, ordenadas por `publication_order` — a mesma leitura de `_consolidacao`
  (`retificacoes.py:921`) —, cada uma com **`numero = publication_order`** e a data de `published_at`;
- `situacao`:
  - `VIGORA` se `effective_version(edital_id=…, at=agora)` é esta versão;
  - `SUCEDIDA` se não vigora e (`valid_from <= agora` **ou** existe versão do mesmo Edital com o mesmo
    `valid_from` e `materialized_at` posterior — a rematerialização de `_materialize_affected_versions`,
    `retificacoes.py:868`, que torna a base de uma edição velha mesmo com início futuro);
  - `FUTURA` nos demais casos;
- `inicio`: o `valid_from`, no fuso institucional.

**A numeração é a do detalhe do Edital.** `detalhe.html:182` escreve "Retificação nº
{{ documento.ordem }}" com o `publication_order` cru, e é o que a pessoa vê ao lado: a auditoria
chamou de "nº 3" a terceira publicação. O relatório do Edital (`relatorio_do_edital.py:1312`) numera
por `ordem − 1`. **A divergência entre as duas telas é anterior a esta feature e fica registrada como
achado para o usuário**; esta spec segue o detalhe, que é a tela da jornada.

Um fragmento, `interface/_versao_base.html`, desenha a frase da FR-3935. Ele entra em `retificar.html`
(«Como funciona», acima da tabela e no modo somente leitura), em `retificacao_detalhe.html` e em
`retificacao_confirmar.html` (homologar, devolver, publicar).

**Custo.** Até quatro consultas: a versão original, as publicações aplicadas, a versão em vigor (com o
`prefetch_related` de `effective_version`, `selectors.py:33`) e a existência de rematerialização. Não
variam com o tamanho do Edital.

**Descartado.** *Usar `source_publication`*: ver D-006 da spec.

## R-010 — Os textos que mudam e os testes que os afirmam

Mudam de propósito; os testes que os afirmam são **atualizados para o texto novo**, e não afrouxados:

| Onde | Texto de hoje | Texto novo | Teste que o afirma |
|---|---|---|---|
| barra, depois de conferir | "Nada alterado desde a conferência" | "Nenhuma alteração nova desde a última conferência" | `tests/javascript/retificacao.test.js:162` |
| somente leitura, título | "Conteúdo vigente" | "Conteúdo da versão-base" | `tests/interface/test_acoes.py:154` |
| somente leitura, aviso (`retificar.html:52`) | "Abaixo está o conteúdo vigente do Edital, como referência." | "Abaixo está o conteúdo da versão-base do Edital, como referência." | nenhum |
| criação, «Como funciona» (`retificar.html:41`) | "Abaixo está o conteúdo *vigente* do Edital." | "Abaixo está o conteúdo da versão-base do Edital." | nenhum |
| edição, «Como funciona» (`retificar.html:35-38`) | "o conteúdo *proposto* por esta Retificação: o vigente com o que ela já declara … o campo que voltar ao valor vigente deixa de ser alterado" | "o conteúdo *proposto* por esta Retificação: a versão-base com o que ela já declara … o campo que voltar ao valor da versão-base deixa de ser alterado" | nenhum |
| resumo, coluna | «Vigente hoje» | «Na versão-base» (criação) / «No rascunho» (edição) | nenhum |

"Nenhum campo alterado ainda" continua, como primeira frase da barra antes da primeira conferência.

**Testes que dependem da forma, e não do texto**, e que o desenho preserva em vez de mudar:
`test_aplicar_a_todos_na_retificacao.py:175` (o literal `action="…" data-conferido`: os atributos
novos vêm depois) e os casos de `retificacao.test.js` que leem `barra.filhos[0]` (a contagem continua
o primeiro filho). Se a implementação precisar mexer neles, é sinal de que se afastou de R-007.

## R-011 — Os dois Editais dos testes

**Decisão.** Uma fixture nova, `tests/fixtures/edital_da_auditoria.py`, publica pelos helpers de
`tests/fixtures/publicacao.py`:

- `edital_da_auditoria`: o porte do 01/2026 do `seed_demo` — 2 Perfis (DOC-INFO com 3 vagas e quadro
  AC 2 + PPP 1; TEC-LAB), 3 Eventos com o período de inscrições, 3 Etapas, 3 Documentos, 2 Anexos e
  as Seções do catálogo;
- `edital_extenso`: o mesmo conteúdo ampliado como faz `renderizar-edital-extenso.py` da auditoria —
  4 Perfis (cópias com identidades novas e códigos `CURSO-2`…), 2 Modalidades cada, 11 Eventos —,
  mas **no rascunho, antes de publicar**, e não por troca de `conteudo_base` em memória.

E um helper, `retificacao_publicada(edital, alteracoes, vigencia)`, para os cenários de base futura
e sucedida, pelo caminho da API (criar, submeter, homologar, publicar), como as suítes da `103`.

**Onde viram fixtures.** Os módulos de `tests/fixtures/` são helpers importados por conftest, e não
fixtures registradas. `edital_da_auditoria`, `edital_extenso` e `retificacao_futura` se registram como
fixtures pytest em `backend/tests/conftest.py`, ao lado das que ele já define, para valerem em
`unit/`, `interface/` e `navegador/`.

**Por quê.** O `seed_demo` não roda na suíte; as datas dele são relativas e o elenco colide. O
script da auditoria é de leitura e não serve de fixture.

## R-012 — A jornada de navegador reaproveita a `Tela` da 115

**Decisão.** `tests/navegador/test_jornada_da_retificacao_123.py`, `transaction=True`, com a `Tela`
de `test_jornada_dos_documentos_da_convocacao.py` (seletor de identidade, vigia de CSP, capturas),
como a `122`. Casos:

1. `test_cenario_a_b_c_pela_busca` — demonstração, 1280: «vagas», «remuneração», «prazo»,
   «requisito»; foco no campo; contagem de ações (SC-1173, SC-1174).
2. `test_cenario_b_impeditivo_na_conferencia` — vagas 3→4, conferir, impeditivo com link, corrigir a
   linha, conferir de novo, criar (SC-1179).
3. `test_cenario_d_marca_persistente` — três alterações, conferir, os três selos, as duas frases,
   «Só o que eu alterei», «Ir ao campo» de cada linha, uma alteração nova (SC-1175, SC-1176).
4. `test_edicao_da_devolvida_abre_marcada` — devolvida pela API, aberta pela tela (SC-1177).
5. `test_cenario_g_base_futura` — Retificação de vigência futura publicada; as cinco telas
   (SC-1178).
6. `test_cenario_e_extenso` — ampliado, 1280 e 375: «vagas» no 4º Perfil, Evento 11 pelo nome;
   rolagem lateral zero (SC-1173, SC-1181).
7. `test_so_pelo_teclado` — cenário D inteiro por `keyboard.press`, sem clique (FR-3949).

Cada caso termina com `violacoes == []`.

**A contagem de ações** é a do roteiro da auditoria: cada `fill`, `click` e `press` conta 1; o
`goto` inicial não conta.

## R-013 — A criação recusada mostra a mesma seção

**Decisão.** Quando `gravar` levanta `DomainError` de conteúdo — o `blocking_findings` de
`_apply_declared_changes`, ou o código de uma guarda de conteúdo —, `_compor_retificacao` roda
`conferir_conteudo` sobre a mesma proposta e desenha a seção `#impeditivos`, com os links, **além** da
recusa no alto, que continua com o texto de hoje (nenhum teste de recusa muda). O `data-proposta`
dessa resposta é `conferida`.

As recusas que não são de conteúdo — `ensure_processo_accepts_changes`, Edital fora de `PUBLICADO`,
`stale_revision`, a edição que deixaria o ato vazio — não abrem a seção, nem na conferência nem na
criação: `conferir_conteudo` não as reproduz, e FR-3941 as deixa onde estão.

**Por quê.** US4 é o caminho até a linha. Sem isto, quem clicasse «Criar» sem conferir antes voltaria
à situação de hoje — a frase concatenada no alto, sem link.

