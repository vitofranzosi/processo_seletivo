# Research — 054 · O Edital do sistema como ato oficial

Cada item diz a decisão, por quê, e o que foi descartado. Conferido contra a `main` em `f00f7214`.

## R-001 — O catálogo de 22 entradas, e as chaves

**Decisão.** As chaves das 12 entradas de hoje ficam; as 10 novas são `informacoes-gerais`,
`publico-alvo`, `verificacao-autodeclaracao`, `atendimento-pcd`, `convocacao`, `matricula`,
`acesso-ao-curso`, `homologacao-matricula`, `certificado` e `prazo-de-validade`. A `order` é a
posição de `FR-980` (1 a 22), e `perfis` sobe para antes de `inscricao`.

**Por quê.** A linha de `SecaoEdital` é endereçada pela chave, e a identidade é `uuid5(edital, chave)`:
manter as chaves é o que faz o texto já escrito num rascunho continuar na mesma seção (`FR-981`). A
ordem nova só muda `order`, que o rascunho não grava — o snapshot a lê do catálogo.

**Descartado.** Renomear `classificacao` para "Do Processo Seletivo", como a amostra: mudaria a
identidade da seção em todo rascunho, e o título atual diz a mesma matéria.

**O mapa do 28/2026** (base da verificação): 1 Informações gerais → `informacoes-gerais`;
2 Público-alvo → `publico-alvo`; 3 Requisitos → `requisitos-gerais`; 4 Vagas → `perfis` (gerada);
5 Inscrições → `inscricao` + `documentos-exigidos` (gerada); 6 e 7 Verificação da autodeclaração →
`verificacao-autodeclaracao`; 8 Processo seletivo → `classificacao` (e `etapas`, gerada, se houver
Etapa); 9 Recurso → `recursos`; 10 Matrícula → `matricula`; 11 Acesso ao curso → `acesso-ao-curso`;
12 Homologação da matrícula → `homologacao-matricula`; 13 Certificado → `certificado`; 14 Entrevista
PcD → `atendimento-pcd`; 15 Disposições finais → `disposicoes-finais`; Anexo I Cronograma →
`cronograma` (gerada). A ordem do documento difere do original em um ponto: a entrevista PcD sai
depois da verificação da autodeclaração, e não depois do certificado — as duas são matéria da reserva
de vagas, e a entrevista acontece antes do início do curso.

## R-002 — A textual vazia

**Decisão.** `Secao.default_text` sai do catálogo. O snapshot continua emitindo **toda** seção do
catálogo, e a textual sem linha sai com `content: ""`. `ler_secoes` grava o texto não vazio, sem
comparar com padrão. `_topologia_das_secoes` exige que o `content` da textual seja texto, e não que
seja não vazio.

**Por quê.** A seção precisa existir no snapshot mesmo vazia: é por ela que a Retificação pode dar
texto a uma seção que o Edital publicou vazia (US4, cenário 3), sem `ADD`, que a topologia recusa. A
chave `content` presente e vazia dá **uma** forma ao fato, como `matriculationRequest: null` dá.

**Descartado.** Omitir a textual vazia do snapshot: a Retificação ficaria sem endereço para ela, e o
conjunto de seções passaria a variar por Edital.

**Sem degrau canônico.** A forma do conteúdo não muda (as chaves são as mesmas), só o que ele admite:
nenhuma elevação de `SCHEMA_VERSION`.

## R-003 — A numeração, de uma regra só

**Decisão.** `pdf.numeracao(snapshot)` devolve, por chave, o número que a seção terá no documento, ou
`None` quando não sai (preâmbulo incluído, que sai sem número). É derivada de `_materializaveis`, que
passa a considerar a textual materializável quando tem texto **ou** quando o sistema lhe acrescenta
norma (`FR-984`). O compositor, a etapa Conteúdo e a Revisão chamam a mesma função.

**Por quê.** Três lugares que numeram por regras próprias divergem — é o RC-26. A regra vive onde o
documento é composto, e as telas a leem.

**Descartado.** Número na tela pela `order` do catálogo (o de hoje): com 22 entradas e textuais vazias,
a tela diria "15" para a seção que o documento imprime como "9".

## R-004 — A topologia de referência na Retificação

**Decisão.** `validate_for_publication` ganha o parâmetro `topologia` — a lista de seções contra a
qual conferir. Omitido, é o catálogo vigente (elaboração, submissão, publicação). Nos três pontos de
`retificacoes.py` que validam com `ATO_DE_RETIFICACAO` (`_assert_well_formed` e `advertencias_do_ato`),
passa-se a topologia do conteúdo **original** do Edital (`_original_version`). A comparação é a de
hoje — chave, título, ordem, espécie e origem —, feita contra a referência.

**Por quê.** A topologia não pode mudar depois da publicação: a do original é a de todas as versões.
Ler a do original, e não a do conteúdo-base da Retificação, dispensa depender de qual versão
consolidada serviu de base.

**Descartado.** (a) Versão de catálogo gravada no conteúdo: pede degrau canônico e elevação do acervo,
por um problema que a referência resolve sem gravar nada. (b) Aceitar "qualquer catálogo histórico":
deixaria uma Retificação pela API converter um Edital de uma forma na outra, somando `ADD` e troca de
título e ordem — que a gramática, sozinha, não recusa (`colecoes.RECUSADOS_EM_OUTRO_LUGAR`).

**A mensagem de "não retificável"** de título, ordem e espécie (`mutabilidade.py`) deixa de afirmar que
são *"os mesmos em todo Edital do Cefor"*.

## R-005 — O fecho como contexto do ato

**Decisão.** `render_edital_pdf` recebe, além da autoridade, `data_do_ato` (`date`) e, na
Retificação, `consolidacao` (as datas das publicações incorporadas e a vigência). A regra de presença
é a da autoridade (`008`, FR-035): em modo publicado a data é obrigatória, e na prévia é recusada. O
fecho é `"<LOCAL>, <data por extenso>."` alinhado à direita, antes da rubrica *"Autoridade responsável
pelo ato"*, no mesmo bloco inseparável da autoridade e da verificação. `LOCAL = "Vitória (ES)"`,
constante ao lado de `ORGAO`.

**Por quê.** A data existe no instante da composição nos dois fluxos (`now`), e chega pelo mesmo
caminho da autoridade: o hash do conteúdo não muda (`FR-990`). Alinhado à direita como nos quinze
Editais, e no bloco inseparável para que a data não fique sozinha no pé de uma página.

## R-006 — A data por extenso

**Decisão.** `humano.data_por_extenso(date) -> "29 de setembro de 2026"`, com os meses em português,
sem zero à esquerda (`D-004`). O `date` vem de `now.astimezone(ZONA).date()`, e não de
`timezone.localtime`, para depender da zona institucional (`shared/tempo.py`), e não da configuração.

## R-007 — O ato de nomeação na Publicação

**Decisão.** `Publicacao.signatory_appointment = CharField(max_length=255, blank=True, default="")`,
migration `publicacoes/0009`. Os dois fluxos gravam `signatory.get("appointment", "")`. A API de
publicação aceita `signatory.appointment` opcional; a consulta pública o devolve, vazio quando não há.
O guardião de contagem de migrations por app sobe com a justificativa escrita.

**Por quê.** `ADD COLUMN ... DEFAULT ''` é só metadado no PostgreSQL moderno: nenhuma linha é
reescrita e o gatilho de `UPDATE` da tabela append-only não dispara. As Publicações existentes ficam
com o ato de nomeação vazio, que é verdade: não o registraram.

**`name` da API continua obrigatório.** Quem publica pela API declara o assinante; o nome vazio é
estado do catálogo da interface, enquanto o Cefor não o fornece. Relaxar o contrato da API por isso
seria abrir um caminho de publicação sem nome para quem tem o nome.

## R-008 — O catálogo de autoridades

**Decisão.** `Autoridade(chave, identificador, cargo, nome="", ato_de_nomeacao="")`. As três entradas
de hoje perdem o nome (que era designação de cargo) e ficam só com o cargo; o `__str__`, usado na
escolha ao publicar, é o nome e o cargo quando há nome, e só o cargo quando não há. O cargo da
Diretora continua o de hoje; conferi-lo com o Cefor é parte da pergunta pendente.

**Por quê.** É o que `D-005` pede: o fecho funciona com o cargo e aceita o nome quando vier, sem
mudança de código fora do catálogo.

## R-009 — Quem assinou, nas telas

**Decisão.** Uma função, `autoridades.quem_assinou(nome, cargo)`, devolve `"nome — cargo"` com nome,
e `"cargo"` sem; `selectors.participantes` e a escolha ao publicar a usam. A consulta pública devolve
os campos separados, como hoje, e quem os lê já os junta.

## R-010 — A marca do consolidado

**Decisão.** Logo abaixo do anúncio do ato, em corpo de texto, centralizada: *"Versão consolidada.
Publicado em 7 de abril de 2026; retificado em 24 de agosto de 2026."* — com cada Retificação
incorporada, em ordem, e *"com vigência a partir de …"* quando a vigência desta começa em outro dia.
As datas incorporadas são as das Retificações publicadas que vigoram na vigência desta
(`_published_retifications` com `effective_at <= effective_at`), mais a publicação original e esta.

**Por quê.** São as mesmas Retificações que `_content_in_force` aplica para compor o conteúdo desta:
a marca lista exatamente o que o documento incorpora. A data de cada uma é a de publicação, porque é
o ato que o leitor procura no Diário.

## R-011 — A declaração do Requerimento

**Decisão.** `_norma_da_secao` ganha o caso `matricula`: com `matriculationRequest.moment`, duas
frases — *"O Requerimento de Matrícula será enviado no ato da inscrição."* ou *"… quando o candidato
for convocado."*, e *"Ao enviá-lo, o candidato declarará:"* —, seguidas do texto integral da
declaração, parágrafo a parágrafo, com recuo. O texto é lido do snapshot, do mesmo campo que o portal
exibe (`requerimentos/application/preencher.py`).

## R-012 — A linha de total

**Decisão.** `_quadro_de_perfis` acrescenta a última linha `["Total", "", soma, "", ""]`, em negrito,
com a soma de `immediateVacancies`. Só existe com mais de um Perfil, porque a tabela só existe assim.

## R-013 — Os avisos da Revisão

**Decisão.** `_secao_com_redacao_padrao` e o código `section_default_text` saem (o rótulo em
`interface_extras` e o destino em `views` também). Entra `_secao_universal_vazia`, código
`section_universal_empty`, só no ato de publicação: uma advertência para `apresentacao` e outra para
`disposicoes-finais` vazias, com destino na etapa Conteúdo.

**Por quê.** São as duas que os quinze têm sem exceção (`FR-986`). Avisar todas as vazias seria avisar
dezesseis vezes por Edital — um ruído que se aprende a ignorar.

## R-014 — A etapa Conteúdo

**Decisão.** `secoes_do_edital` devolve, por seção, o número (R-003) e a norma que o documento
acrescentará (a frase do teto, a declaração). O template mostra `"<n>. <título>"` ou o título seguido de
*"Vazia — não sai no documento"*; a ajuda da textual deixa de falar em redação padrão; a norma
acrescentada aparece como ajuda do campo. Um `conteudo.js` recalcula número e estado quando uma
textual passa de vazia a preenchida ou o contrário, a partir de atributos `data-` que o servidor
escreve (a gerada e a textual com norma têm estado fixo). Sem script, a tela mostra o número do
conteúdo gravado.

**A regra pura** (dada a lista de seções com estado fixo ou dependente do texto, os números) mora numa
função exportável, testada com `node --test`.

## R-015 — A fixture de bytes

**Decisão.** `autoridade_publicada.json` passa a carregar também `ato_de_nomeacao` e ganha, ao lado,
`contexto_publicado.json` com a data do ato; o `snapshot_publicado.json` é refeito pelo catálogo novo
(22 seções, textuais com o texto que já tinham e as novas vazias); o gerador lê os três e o PDF é
refeito no mesmo commit, com a diferença conferida por `pdftotext`.

## R-016 — O banco de demonstração

**Decisão.** O `seed_demo` não grava texto de seção, e passa a produzir Editais com as textuais vazias
— o documento de demonstração sai só com as geradas e o fecho. Para a verificação do 28/2026, o
Edital é composto num banco próprio, pelo helper dos testes, com o texto das seções que o original
tem (quickstart). O documento publicado não se regenera: re-semear é o caminho para ver.

## R-017 — As emendas às specs anteriores

**Decisão.** Nota curta ao pé de cada requisito emendado — `FR-036` e `SC-001` da `008`, `FR-037` e
`FR-041` da `006` —, apontando o requisito da `054` que o emenda. A letra antiga fica, porque é
história do que valeu.
