# Research: A experiência da convocação, incremento 1

**Plano**: [plan.md](plan.md) · **Spec**: [spec.md](spec.md) · **Data**: 2026-11-05

Cada item registra a decisão de desenho, por que ela e o que se descartou. Os dois primeiros
respondem ao que o usuário pediu ao aceitar a spec: a prova da D-009 e os cenários da D-008.

## R-001 — A versão exata do modelo não se prova pelo histórico de implantação

**Pergunta.** A D-009 foi aceita sob uma condição: o plano precisa provar que, a partir do que já se
grava, é possível identificar em cada envio **a variante** e **a versão exata do modelo**. Se o
histórico de implantação não oferecer essa evidência, a gravação da versão volta ao usuário antes das
tarefas.

**Resposta curta.** A variante se reconstrói, e o plano a prova com um teste (R-002). **A versão exata
do modelo, não:** o histórico de implantação a data com uma janela de incerteza a cada ativação,
mora fora do banco e da trilha, e nenhum teste da suíte o alcança. **A gravação da versão voltou ao
usuário**, que escolheu a opção A em 2026-11-05 (R-009; *A decisão da D-009*, no
[plan.md](plan.md)).

### O que já se grava, e o que reconstrói

| Pergunta da auditoria | De onde sai hoje | Basta? |
|---|---|---|
| Quando a mensagem saiu | `ComunicacaoEmitida.enviado_em`, append-only (`seguranca/papeis.py`, linha `convocacao_comunicacaoemitida`), com `resultado` `ENVIADA` ou `FALHA` | sim |
| Se é a inicial ou a da correção | a cadeia `Convocacao.convocacao_anterior` e as comunicações de cada elo, todas append-only: existe na cadeia uma `ComunicacaoEmitida` `ENVIADA` anterior a esta? | sim |
| Qual mensagem a da correção cita | a última `ComunicacaoEmitida` `ENVIADA` da cadeia anterior a esta, e o `vencimento` da convocação dela | sim |
| A variante de obrigação | `ItemDaListaDaConvocacao` da chamada (append-only, `gravada_em`), e `momento_declarado` sobre o conteúdo da **versão citada** pela convocação (`Convocacao.versao`, imutável) | sim |
| **O texto do modelo** | **o código que estava em produção no instante `enviado_em`** | **não** (abaixo) |

### O histórico de implantação, lido

O manual de produção (`doc/implantacao-em-producao-ubuntu.md`, §8.3) define o único caminho de troca
de código: `ps-construir` monta uma release imutável por SHA da `main`, com o arquivo `REVISION`
(`commit=`, `construida_em=`); `ps-ativar` troca o symlink `current`, reinicia o serviço, espera o
`/readiness` e **só então** acrescenta uma linha a `/var/lib/processoseletivo/implantacoes.log`:

```text
<data ISO>  <ativada|FALHOU>  <commit>  <release>  anterior=<release>  <quem>
```

Dado um `enviado_em`, a versão seria a da última linha *ativada* anterior a ele. O texto exato sairia
do Git, no SHA dessa linha. Isso **quase** funciona, e falha em quatro pontos:

1. **A janela de cada ativação.** O symlink troca no instante T0; a linha é gravada em T1, depois do
   `restart` e do *readiness*. Entre os dois cabem o `graceful_timeout` de 30 s (`TimeoutStopSec=40`),
   a subida do novo master e até 30 tentativas de 2 s do *readiness* — **cerca de dois minutos** em
   que um envio pode ter saído de qualquer das duas versões. O log não grava T0, e nada no envio diz
   qual worker o atendeu.
2. **A linha `FALHOU` não diz o que serviu.** O symlink já trocou antes do *readiness*, o `restart`
   termina em `|| true`, e o `Restart=on-failure` do systemd pode subir a release nova depois. Uma
   linha `FALHOU` seguida de envios não diz se eles saíram da release nova ou de nenhuma.
3. **O log está fora das garantias da auditoria.** É um arquivo de texto, de root, modo 0644, fora do
   banco. A Constituição (Princípio III) exige que eventos de auditoria não possam ser
   **silenciosamente** alterados, e as tabelas append-only têm duas camadas para isso. O log não tem
   nenhuma: corrigi-lo à mão não deixa rastro, e restaurá-lo depende do backup (§18).
4. **Nenhum teste o alcança.** A suíte não lê a VM. A FR-3889 diz que a versão MUST ser identificável,
   e o Princípio V pede teste automatizado para regra crítica. Uma garantia que só se confere à mão,
   em produção, não é a prova que a D-009 pediu. Além disso, a homologação e o ambiente de
   demonstração não usam `ps-ativar`, e ali o histórico não existe.

**Por que não se resolve com uma mudança no script.** Gravar T0 antes do symlink estreitaria a
janela, mas não a fecharia: requisições em curso no worker antigo terminam depois de T0. Os pontos 3
e 4 continuariam. Corrigir o script é operação, e não atende à condição da D-009.

### O que a gravação precisava guardar

O mínimo que fecha os quatro pontos é **uma coluna em `ComunicacaoEmitida`**, gravada na mesma linha
e na mesma transação do envio: o **nome do modelo** (`inicial` ou `correcao`) e o **resumo SHA-256 do
conteúdo dos dois arquivos de modelo**, o HTML e o texto, calculado do arquivo que o processo
carregou. O resumo se confere contra o Git: em qualquer commit, o resumo dos dois arquivos é
reproduzível, e o commit que produz aquele resumo é o texto que saiu. Ele não depende da implantação,
vale em todo ambiente e se testa na suíte.

As alternativas estão na seção *A decisão da D-009* do plano, com o custo de cada uma. O usuário
escolheu esta, e o desenho dela está na R-009.

## R-002 — A variante e a mensagem citada saem de uma função pura, chamada no envio e na reconstrução

**Decisão.** Uma função pura, `escolha_da_mensagem`, recebe o que já está gravado e devolve o modelo
(`inicial` ou `correcao`), a variante de obrigação (FR-3884) e, na correção, a comunicação citada.
As entradas são quatro:

- os itens da lista da chamada com `gravada_em` até o instante do envio;
- o momento do Requerimento lido da versão citada;
- a cadeia de convocações anteriores;
- as comunicações de cada elo da cadeia.

O envio a chama para montar a mensagem. O teste de reconstrução a chama de novo, depois, só com os
registros do banco, e compara o resultado com o que o envio usou.

**Por quê.** A FR-3889 exige que a escolha seja **função só de dados já gravados**. Se a função é a
mesma no envio e na reconstrução, o teste prova a afirmação. Com duas funções, um teste só provaria
que as duas concordam naquele caso.

**A regra da D-008, na função.** Percorre-se a cadeia a partir da convocação imediatamente anterior,
em direção à raiz, e pega-se a primeira comunicação `ENVIADA`. Se houver, o modelo é `correcao`, e
ela é a citada. Se não houver, o modelo é `inicial`. Uma comunicação `FALHA` não conta. Comunicações
por publicação não contam, porque não são mensagem enviada à pessoa.

**Os cenários que o teste cobre** (SC-1160):

| Cadeia | Comunicações | Mensagem de C | Dados do ato de C |
|---|---|---|---|
| A → C | A `ENVIADA` | correção, cita A | substituída: A |
| A → B → C | A `ENVIADA`, B `FALHA` | correção, **cita A** | substituída: **B**, *"Não comunicada"* |
| A → B → C | A `ENVIADA`, B `ENVIADA` | correção, cita B | substituída: B |
| A → B → C | A `FALHA`, B `FALHA` | **inicial** | substituída: B, *"Não comunicada"* |
| A → C | A sem comunicação | inicial | substituída: A, *"Não comunicada"* |
| A → C | A por publicação | inicial | substituída: A, *"Publicada em…"* |
| A → B → C | A `ENVIADA`, B `FALHA` e depois `ENVIADA` | correção, cita o envio de B | substituída: B |

Na última linha, B tem duas comunicações, e a citada é a `ENVIADA` mais recente. O quadro cita o
`enviado_em` dela e o `vencimento` da convocação a que ela pertence, e nunca o da convocação
imediatamente anterior, quando forem diferentes.

**Descartado.** Ler `ComunicacaoEmitida` só da `convocacao_anterior`, como a redação anterior da D-008
fazia: C sairia como inicial na segunda linha, e a pessoa, que recebeu A, leria uma convocação nova
sem aviso de que A deixou de valer.

## R-003 — Uma função de prazo, no domínio da convocação, lendo o fuso das settings

**Decisão.** A função nova fica em `convocacao/domain/prazo_apresentado.py`, e é pura:
`apresentar(vencimento, agora, fuso)`. O fuso sai de `ZoneInfo(settings.TIME_ZONE)`, passado por quem
chama. Ela devolve o valor descrito no [data-model.md](data-model.md). `portal/obrigacoes.py`
(`data`, `hora`, `ate`) e o envio passam a delegar a ela, e os chamadores delas não mudam. O
dia da semana vem de uma tabela própria, em português.

**Por quê.** Hoje há três formatos de hora: *"às HHhMM"* no portal, *"às HH:MM"* no e-mail e
*"HH:MM"* na gestão. Também há quatro funções `data` duplicadas (`obrigacoes.py:128`,
`situacao.py:619`, `fluxo.py:159`, `ficha.py:106`). A FR-3873 pede uma só para o portal e o e-mail.
Delegar pelas funções de `obrigacoes.py` cobre o portal sem tocar nos chamadores. O domínio da
convocação é o lugar porque o e-mail (`convocacao/application`) não pode importar o `portal`.

**O que não muda.** A gestão continua com *"HH:MM"*: a FR-3875 vale para as superfícies do candidato.
`shared/tempo.py` tem o fuso fixo de propósito, para a ficha em PDF, e continua assim. A contagem do
período de inscrições (`views.py:474`, `_dias_ate`, que conta blocos de 24 horas) não é da
convocação, e fica registrada como achado.

**Descartado.** Usar o `locale` do sistema para o dia da semana: depende do servidor, e o
SC-1154 fixa o fuso e troca o do servidor para provar que o resultado não muda. Reaproveitar
`interface/agenda.py:100`, `DIAS_DA_SEMANA`: o domínio passaria a importar a interface.

## R-004 — O redirecionamento sem sessão acontece antes de `_inscricao_do_titular`

**Decisão.** A primeira linha da view `convocacao` pergunta a `identidade_da_sessao(request)`. Ela não
consulta o banco quando falta a chave da identidade (`portal/identidade.py:69`). Sem identidade, a
view redireciona a `portal:acesso?destino=<request.path>` com `urlencode`, sem ler a inscrição. A
rota de escrita (`apresentar_documento_da_convocacao`) e a do arquivo (`documento_da_convocacao`)
continuam como hoje.

**Por quê.** Hoje a resposta sem sessão é 404, mas só **depois** de
`Inscricao.objects.filter(pk=…).first()` (`views.py:2704`). O tempo de resposta e a consulta
dependem de o identificador existir. A FR-3876 e a SC-1157 pedem a mesma resposta e zero consultas
antes dela. Como a pergunta só lê a sessão, a resposta não tem como depender do identificador.

**Os testes que mudam.** O caso `test_convocacao_alheia.py:148`, *sem sessão → 404*, passa a esperar
o redirecionamento idêntico para o identificador existente e o inexistente. O caso de sessão
alheia (`:125`) continua 404.

## R-005 — O destino da convocação entra na lista fechada pela rota, e se reconstrói

**Decisão.** `_de_volta_a_vaga` (`views.py:1087`) ganha o ramo `portal:convocacao`, que devolve
`reverse("portal:convocacao", args=[inscricao_id])`, com o identificador vindo de `resolve()`, e sem
consulta nem fragmento. Os outros dois ramos continuam. Qualquer outra rota cai em
`portal:inscricoes`. O nome da função fica, porque três chamadores e dois testes o usam. A docstring
diz que a lista agora tem três rotas. `_entrar` não passa a convocação por `meus-dados`: o atalho do
núcleo é só da vaga (`_destino_e_vaga`).

As telas de acesso recebem `destino_e_convocacao`, decidido **só** pelo nome da rota resolvida
(FR-3880). A decisão não lê o identificador, e o texto é um só.

**Por quê.** `_destino_seguro` só confere host e esquema, e deixa passar consulta e fragmento. As
camadas 2 a 4 da FR-3878 são o que já se faz para a vaga, estendido à convocação. Reconstruir pela
rota descarta, por construção, tudo o que veio de fora.

## R-006 — A confirmação do envio vive na sessão, com o item, e a tela a monta da projeção

**Decisão.** No sucesso, `apresentar_documento_da_convocacao` grava na sessão um registro próprio,
`confirmacao_da_convocacao`, com o `item_id`, o `apresentacao_id` e `ja_recebido`, e redireciona para
`#confirmacao`. A tela consome o registro ao exibir. O nome do documento, a data e a próxima tarefa
saem da projeção de obrigações que a tela já monta, e não do registro. Na recusa, o registro é
`recusa_da_convocacao`, com o `item_id` e a frase. O destino é `#item-<id>`, e o cartão o mostra com
`data-recusa`, para o `recusa.js` dar o foco.

**Por quê.** Hoje `_avisar` e `_recusar` põem a mensagem no topo, sem âncora (`views.py:2592`). A
FR-3870 pede a confirmação como primeiro elemento da chamada, com foco sem script. Isso se faz com
`id="confirmacao" tabindex="-1"`: o navegador foca o alvo do fragmento quando ele é focável. A
FR-3871 pede a recusa no cartão. O registro guarda identificadores, e não texto do documento,
para que a próxima tarefa seja a do estado depois do envio.

**Verificação.** O foco sem script só se prova num navegador real. A jornada da `115` ganha o caso
da SC-1162, com o script desligado.

## R-007 — `envio.js` passa a valer também para formulário sem htmx

**Decisão.** `envio.js` ganha um ramo: no `submit` de um `form[data-envio]` **sem** `hx-post`, ele
mostra o `.progresso` do formulário e desabilita o botão. O ramo do htmx, que mostra o percentual na
inscrição, continua igual. A convocação passa a carregar `arquivo.js`, `envio.js` e `recusa.js` no
fim do `convocacao.html`.

**Por quê.** O formulário da convocação é POST comum (`_cartao_do_documento_da_convocacao.html:38`),
e `envio.js` só escuta eventos do htmx: carregado como está, o progresso nunca aparece. A spec proíbe
script novo e admite generalizar os três (Assumptions). Passar o formulário para o htmx levaria a
resposta a ser trocada por fragmento, e o retorno a `#confirmacao` com foco sem script se perderia.

**Testes.** Nenhum dos três scripts tem teste em `javascript/`. Entram `envio.test.js`, com os dois
ramos, e `arquivo.test.js`, sobre o *shim* de DOM do repositório.

## R-008 — A linha "Convocação substituída" lê a anterior com a vigente, sem consulta por item

**Decisão.** `vigentes_por_inscricao` (`convocacao/application/selectors.py:90`) passa a carregar
`convocacao_anterior` e as comunicações dela no mesmo *prefetch*. A linha da FR-3869 se monta disso,
com a comunicação `ENVIADA` mais recente da anterior, a publicação ou nenhuma.

**Por quê.** A linha não existe hoje. A `118` mede a mesma contagem de consultas com 1 e com 6 itens
(`test_portal_jornada_consolidada.py:679`), e a anterior lida por item quebraria a medição.

**Distinção.** A linha dos dados do ato descreve a **imediatamente anterior**, e a mensagem cita a
última **enviada** da cadeia (R-002). As duas leituras são diferentes por decisão do usuário (D-008),
e não devem ser unificadas.

## R-009 — O resumo sai das fontes que o carregador entregou para o envio

> **Revista em 2026-11-13, na auditoria dos e-mails** (`doc/auditoria-dos-emails-2026-11-13.md`,
> achado 6). O HTML da convocação passou a ter estilo em linha, aplicado depois da renderização a
> partir de um mapa de classes, e mudar uma cor mudava a mensagem sem mudar o resumo. O mapa saiu do
> código para um arquivo versionado, `backend/processo_seletivo/shared/templates/correio/estilos.json`,
> e entrou no resumo como terceira fonte, com rótulo de regra próprio:
>
> ```text
> <nome>:sha256-com-estilos:<hex de sha256( b"html\0" + fonte_html_utf8 + b"\0texto\0"
>                                           + fonte_texto_utf8 + b"\0estilos\0" + estilos_utf8 )>
> ```
>
> O mapa é lido uma vez pelo processo (`correio.FONTE_DOS_ESTILOS`), e é **a mesma leitura** que
> estiliza o HTML e que entra no resumo — o equivalente, para o mapa, da fonte compilada dos modelos.
> **O rótulo diz a regra**: um valor `<nome>:sha256:` foi gravado antes desta revisão e se confere pela
> regra das duas fontes, abaixo, preservada; um valor `<nome>:sha256-com-estilos:`, pela das três. Na
> conferência pelo Git, o passo 1 lista também os commits que mudaram o `estilos.json`.

**Decisão** *(redação anterior à revisão de 2026-11-13, preservada — é a regra dos valores
`<nome>:sha256:`)*. `identificacao_do_modelo(nome, html, texto)`, em `convocacao/domain/mensagem.py`,
recebe os dois objetos de modelo que o envio acabou de usar para renderizar. Ela devolve:

```text
<nome>:sha256:<hex de sha256( b"html\0" + fonte_html_utf8 + b"\0texto\0" + fonte_texto_utf8 )>
```

A fonte é a que o motor compilou (`template.template.source`), e não um arquivo relido do disco.
Em produção, o carregador com cache entrega a mesma fonte enquanto o processo vive, e é essa fonte que
renderizou o envio. O envio grava o valor em `ComunicacaoEmitida.modelo_da_mensagem`, na mesma linha
do resultado. O nome é `inicial` ou `correcao`, da escolha da R-002.

**Por quê.** O usuário pediu o resumo **dos arquivos efetivamente usados na renderização**. Reler o
arquivo do disco no instante da gravação abriria uma janela: um arquivo trocado entre a renderização
e a gravação produziria um resumo de um texto que não saiu. Tirar o resumo da fonte compilada fecha
essa janela. Os rótulos `html` e `texto` no conteúdo resumido impedem que um texto movido de um
arquivo para o outro produza o mesmo resumo.

**A composição é determinística.** A regra fixa a ordem dos arquivos (HTML, depois texto), os rótulos
e o separador. Fixa também a codificação UTF-8 da fonte como o motor a leu, sem normalizar fim de
linha nem espaço. O mesmo par de arquivos dá sempre o mesmo resumo, em qualquer máquina.

**Como se confere depois, pelo Git.** Os quatro arquivos de modelo são versionados no repositório, sob
`backend/`, e por isso entram em toda release (`ps-construir` arquiva `backend/` do commit). Dado um
resumo gravado:

1. `git log --format=%H -- <os dois arquivos do modelo>` lista os commits que os mudaram;
2. em cada um, `git show <commit>:<arquivo>` devolve o conteúdo histórico, que se resume pela mesma
   regra;
3. o commit cujo resumo for igual ao gravado tem o texto que saiu. Se ninguém mexeu nos arquivos
   desde então, o commit atual também tem.

A regra está escrita aqui para que a conferência não dependa do código de produção. Duas condições a
mantêm possível:

- **os arquivos não saem do Git**: nem gerados no *build*, nem ignorados. Um teste confere isso;
- **um arquivo renomeado continua rastreável**, com `git log --follow`. O caminho de cada modelo é
  fixado no código, e mudá-lo é mudança de código, revisada como as demais.

**Na tentativa falhada.** A renderização passa a vir antes da conferência do destinatário (plano,
seção 5). Assim, toda `FALHA` individual tem modelo, e a identificação diz que texto se tentou enviar.

**Sem retroatividade.** A migration só acrescenta a coluna, com `default ""`. Nenhuma linha anterior
recebe valor, e nenhuma função tenta deduzir a versão delas. Para essas linhas, o que vale continua
sendo o histórico de implantação, com as limitações da R-001.

**Descartado.**

- **Um número de versão escrito à mão**, como o `VERSAO_DO_COMPROVANTE` da `118`: depende de alguém
  lembrar de mudá-lo, e um texto alterado sem mudar o número sairia com a identificação de outro.
- **O resumo da mensagem renderizada**: muda a cada pessoa, e não identifica o modelo. E, por levar
  o link com o identificador da inscrição, viraria dado ligado à pessoa.
