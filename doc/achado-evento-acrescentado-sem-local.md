# O Evento acrescentado pela tela não declara local nem período de inscrições

**Encontrado em**: 26/09/2026, ao confirmar a suspeita que a spec 045 registrou em *Out of Scope*
— *"Evento acrescentado por Retificação nasce sem `location` nem `isRegistrationPeriod`"*.

**Estado**: **corrigido e decidido**. O defeito foi corrigido, e a pergunta de apresentação que ele
levantou foi decidida pelo usuário em 26/09/2026: `location` passa a ser oferecido no Evento
acrescentado; `isRegistrationPeriod` fica fora. A decisão está ao final, e as alternativas que ela
pesou ficam registradas acima dela.

---

## O que era

A suspeita dizia que a Retificação que acrescenta Evento **não publicava**. Era pior: ela **nem
nascia**. `_evento_completo` montava o Evento sem `location` e sem `isRegistrationPeriod`, e
`EVENTO_PUBLICADO` exige os dois. A conferência de forma não espera a publicação — roda já na
elaboração, em `_apply_declared_changes` (`publicacoes/application/retificacoes.py`), sobre o
conteúdo que o ato produziria. Quem acrescentava um Evento pela tela recebia, ao criar o ato:

> O conteúdo que esta Retificação produz possui erros impeditivos: O campo obrigatório não está
> presente em /schedule/id=…/location.; O campo obrigatório não está presente em
> /schedule/id=…/isRegistrationPeriod.

**A elevação de versão não socorria**, como a leitura previa: ela eleva o conteúdo-base antes de
as alterações serem aplicadas, e o Evento acrescentado entra depois. E ela nem teria o que
preencher em `isRegistrationPeriod`, que não tem degrau em `DEGRAUS_DE_EVENTO`.

**Por que nenhum teste via**: os testes de domínio que acrescentam Evento
(`test_retificacoes.py`, `test_reaproveitamento.py`) declaram o Evento inteiro à mão, e o único
teste que passava pela tela (`test_evento_acrescentado_continua_a_ordem_existente`) conferia a
ordem, e não a forma. O guarda de forma que o Perfil tinha — `set(acrescentado) ==
set(vizinho)` — nunca ganhou o gêmeo do Evento.

## O que foi corrigido

`_evento_completo` passou a emitir `location` e `isRegistrationPeriod: False`, que é a forma de
`edital_snapshot` para o Evento — `""` é a grafia de "não declarado" da D-008 da `021`, e `False`
é a ausência de marca da `009`. Dois testes guardam:

- `tests/integration/interface/test_retificacao_estrutural.py` — elabora pela tela, submete,
  homologa e publica, e confere a forma do Evento na versão consolidada;
- `tests/unit/interface/test_retificacao_estrutural.py` — compara o Evento acrescentado com
  `EVENTO_PUBLICADO`, e não com o vizinho da fixture, que já estava completo e não acusou nada.

## A pergunta que a correção levantou

A correção fazia o Evento publicar, mas **com os dois campos fixos**. `NOVO_EVENTO` oferecia tipo,
descrição, início e término — e não oferecia nenhum dos dois. Os dois são **R** na matriz da `026`,
e a tela os oferece no Evento **existente**; a pergunta é se o Evento **novo** também deve
oferecê-los. Não é natureza nova, mas é apresentação nova, e a `026` fez da apresentação uma
decisão (FR-304).

### 1. `location` no Evento acrescentado

- **Oferecer "Onde acontece"**, vazio significando `""`. É o que a elaboração do Edital já faz em
  todo Evento (`_evento.html`), e a D-008 separa as duas coisas: *sugerir é da tela, presumir é do
  conteúdo publicado*. **Custo**: uma linha em `NOVO_EVENTO`, ler o valor em `_evento_completo`, e
  o resumo da conferência passar a mostrar o local — hoje ele mostra só a descrição do acréscimo.
- **Manter fora, com razão escrita.** O local se declara numa **segunda** Retificação, quando o
  Evento já existe e o campo retificável aparece. **Custo**: dois atos, cada um com homologação e
  publicação — e, entre eles, o Edital vigente publica uma prova nova **sem dizer onde** ela
  acontece. O ato não tem como corrigir o próprio acréscimo: a identidade do Evento nasce no
  servidor, e a tela não a vê antes de o ato existir.

### 2. `isRegistrationPeriod` no Evento acrescentado

- **Oferecer a marca.** Um Evento que nasce marcado disputa a designação com o período vigente, e
  `_periodo_de_inscricoes` recusa o ato inteiro com `registration_period_ambiguous` — a menos que o
  mesmo ato desmarque o Evento atual, o que a tela permite pelo campo dele. **Custo**: o movimento
  muda o Evento que o portal obedece para aceitar inscrição (`periodo_de_inscricoes`), e a tela
  precisaria dizer que a marca pede o par.
- **Manter fora, com razão escrita.** Mudar o período de inscrições é, na prática, retificar as
  datas do Evento que já o designa — e esse caminho existe. Designar um Evento novo pede dois atos.
  **Custo**: baixo; é o caso raro.

Nas duas perguntas, as duas saídas eram legítimas. O que não era legítimo era deixar o campo fora
da tela sem que ninguém tivesse decidido.

## O que foi decidido

Decidido pelo usuário em 26/09/2026, cada campo pela alternativa correspondente acima:

- **`location` é oferecido** no Evento acrescentado, com o rótulo "Local" que o Evento existente
  já usa. Vazio publica `""`, "não declarado". Declarado, aparece na conferência em linha própria,
  e não como sufixo da descrição: é o que a pessoa candidata segue para comparecer.
- **`isRegistrationPeriod` fica fora.** O Evento acrescentado nasce sempre com `False`, e o campo
  não é lido do formulário — um POST fabricado com ele é ignorado, porque o formulário não é
  fronteira. Designar um Evento novo como o período de inscrições continua possível em dois atos.

Os testes que guardam a decisão estão em `tests/unit/interface/test_retificacao_estrutural.py`
(`test_evento_acrescentado_declara_o_local_no_mesmo_ato`,
`test_evento_acrescentado_nao_nasce_marcado_como_periodo_de_inscricoes`), e o de integração passou
a declarar o local e a conferi-lo na consulta pública.
