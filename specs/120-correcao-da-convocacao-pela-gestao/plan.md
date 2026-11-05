# Implementation Plan: A correção da convocação pela gestão

**Branch**: `claude/beautiful-einstein-dd75ba` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)
**Input**: a spec da `120`, revista no commit seguinte a `4b2bd844` (FR-3837 a FR-3857, SC-1141 a
SC-1149, D-001 a D-010)

## Summary

A correção por sucessão existe no comando de convocar e não existe na tela. O plano a leva ao cartão
de cada chamada em aberto e com vencimento, **pelo mesmo comando e pela mesma view**, com três
acréscimos ao comando, todos sob a trava que ele já toma:

1. **a convocação nomeada** (FR-3843): o formulário diz qual convocação corrige, e o comando recusa
   se ela não for mais a vigente em aberto — sem corrigir a sucessora nem praticar chamada nova;
2. **a assinatura da prévia** (FR-3857, D-010): o formulário leva o resumo do que mostrou —
   convocação, apuração, versão, forma de comunicação e espécie —, e o comando recusa se o resumo
   que ele calcula no ato for outro;
3. **as recusas próprias da correção**: motivo obrigatório, vencimento obrigatório, chamada sem
   vencimento.

A **idempotência** continua a do comando: a repetição de uma chave já concluída devolve o resultado
anterior **antes** de qualquer conferência, de modo que o duplo clique não é recusado como
"convocação já corrigida" (R-002).

A tela ganha um parcial por cartão, montado da leitura do recorte que ela já faz, sem consulta por
cartão (FR-3855). A recusa volta ao cartão, com os campos preservados, por um registro de sessão
próprio da correção (D-009). Um script estático, permitido pela CSP, diz se o vencimento informado
estende, antecipa ou mantém o prazo; sem ele, a prévia diz as três regras (FR-3844).

**Nenhuma migration, rota, papel, tabela, estado, desfecho ou mensagem nova.** O portal não muda; a
jornada até ele é demonstrada no navegador, e a demonstração é condição de conclusão (FR-3854).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)
**Primary Dependencies**: as do projeto; nenhuma nova. Playwright no grupo opcional `navegador`
**Storage**: PostgreSQL; **nenhuma migration**. As tabelas append-only continuam 53
**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME` próprio da worktree);
`node --test` para o script; jornada no navegador com o grupo `navegador`
**Target Platform**: a gestão (desktop) e o portal do candidato (375 px), servidor Django, CSP
`'self'` sem `unsafe-inline`
**Project Type**: monólito web
**Performance Goals**: a tela da condução com o mesmo número de consultas com 1 e com 20 chamadas em
aberto (SC-1147); a correção, uma transação como a chamada individual de hoje
**Constraints**: CSP — estilo em folha, script em arquivo estático; classe citada no template exige
regra na folha; varreduras de vocabulário da convocação; inventário de negativas da `033` (nenhum
`Http404` novo é previsto)
**Scale/Scope**: um comando estendido (`convocar`), um fluxo (`convocar_e_comunicar`), uma view
(`convocar_view`) e a leitura da tela (`convocacao`), dois parciais, um script, códigos de recusa
novos em `nomes.py`

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | o ato se chama *"Corrigir esta convocação"*; "prorrogação" e "reabertura de prazo" não entram (FR-3856), porque não existem | ✅ |
| II — imutabilidade | a sucessora é linha nova; a corrigida, a lista, as apresentações e as conferências não se tocam (FR-272 da `019`, FR-3573 da `115`) | ✅ |
| III — negar por padrão; auditoria com estado anterior e posterior | a mesma base de convocar, conferida na view e de novo sob a trava; a trilha ganha a convocação corrigida e o vencimento anterior ao lado do novo (FR-3851) | ✅ |
| III — LGPD | nenhum dado pessoal novo. O motivo é texto da comissão, guardado onde já se guarda o motivo da sucessão; a sessão o retém só entre a recusa e a tela seguinte, e o consome ao exibir | ✅ |
| IV — regra no domínio; concorrência | as três conferências moram no comando, sob a trava do Processo; a tela as antecipa, mas não é a fronteira. Duplicidade (R-002), uso de dado obsoleto (R-003) e perda de atualização (R-001) tratados | ✅ |
| IV — derivado visível antes do ato | espécie, fundamento, forma de comunicação, efeito sobre o prazo e o que reabre aparecem antes do botão, com a origem (FR-3844); o que se grava é o que se viu (FR-3857) | ✅ |
| V — simplicidade | sem rota nova, sem tela intermediária (D-008), sem tabela; a assinatura segue o molde da assinatura do alcance da `050` | ✅ |
| VI — jornada demonstrável pelo canal do ator | a comissão corrige pela gestão; o convocado complementa e envia pelo portal; nenhum passo de ação por shell ou banco (SC-1141, SC-1142) | ✅ |

Nenhuma entrada em *Complexity Tracking*. Reavaliado depois do desenho: sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/120-correcao-da-convocacao-pela-gestao/
├── spec.md
├── plan.md                ← este arquivo
├── research.md            ← R-001 a R-010
├── data-model.md          ← o que se lê, o que se grava, a assinatura, as recusas
├── contracts/
│   └── correcao-da-convocacao.md
├── quickstart.md          ← o roteiro de demonstração
├── rastreabilidade.md     ← requisito → teste, com cada caso-limite
├── checklists/requirements.md
└── tasks.md               ← /speckit-tasks, depois da aprovação deste plano
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── convocacao/
│   ├── domain/
│   │   ├── nomes.py                      ← os códigos de recusa da correção
│   │   ├── alcance.py                    ← assinatura_da_correcao (pura)
│   │   └── especie.py                    ← especie_da_sucessora (pura), usada pela tela e pelo comando
│   └── application/
│       ├── convocar.py                   ← `correcao=`: convocação nomeada, assinatura, recusas; razão da trilha
│       └── fluxo.py                      ← convocar_e_comunicar repassa `correcao`; vencimento obrigatório;
│                                            previa_das_correcoes (por cartão, em memória)
├── interface/
│   ├── views.py                          ← convocar_view: o ramo da correção e a sessão da recusa;
│   │                                        convocacao: a prévia por cartão e a recusa no cartão
│   ├── templates/interface/
│   │   ├── convocacao.html               ← o resultado "correcao" e o include no cartão
│   │   ├── _correcao_da_convocacao.html  ← novo: a ação, a prévia, o formulário, o impedimento, a recusa
│   │   └── _vencimento_da_convocacao.html← `obrigatorio`, valores preservados, `data-fim` nos Eventos
│   └── static/interface/
│       ├── correcao-da-convocacao.js     ← novo: estende / antecipa / mantém
│       └── gestao/…                      ← regras das classes novas, se houver
└── (portal: nada)

backend/tests/
├── unit/convocacao/test_correcao_pura.py
├── integration/convocacao/test_correcao_da_convocacao.py
├── interface/test_correcao_da_convocacao.py
├── performance/test_convocacao.py        ← o caso de 1 × 20 cartões
├── javascript/correcao-da-convocacao.test.js
└── navegador/test_jornada_da_correcao_da_convocacao.py
```

## Design

### 1. A conferência da convocação nomeada, sob a trava (FR-3843, D-003)

`convocar(...)` ganha um argumento opcional, `correcao`, com dois campos: a convocação nomeada
(`convocacao_id`) e a assinatura da prévia (`assinatura`). Sem ele, o comando é exatamente o de hoje
— a API da `019` e a chamada individual da `050` não mudam.

**A ordem dentro de `comando_de_comissao`, que já toma `select_for_update` sobre o Processo:**

1. **`ctx.repetido` → devolve o resultado anterior.** É o primeiro passo hoje, e continua o primeiro.
   A chave do formulário (`<chave da tela>-corrigir-<convocação>`) nasce no GET; o segundo clique
   espera a trava do primeiro, encontra a reserva concluída e recebe o mesmo resultado — **sem
   passar pela conferência**, que o recusaria como "já corrigida" pelo próprio primeiro clique
   (R-002).
2. Ordem vigente, apuração ausente, apuração superada — como hoje. São os impedimentos do recorte, e
   a mensagem deles ganha a orientação da FR-3839 (R-006).
3. **A convocação nomeada**, quando há `correcao`:
   - procurada entre as convocações do recorte que o contexto já leu; ausente, ou de outra inscrição
     → `nao_encontrado` (404, como toda referência fora do escopo);
   - `anterior = _em_aberto_da_pessoa(...)`, como hoje. Se `anterior` não é a nomeada:
     - a nomeada tem desfecho → `convocacao_corrigida_com_desfecho`, com a espécie do desfecho, quem
       o registrou e quando;
     - a nomeada tem sucessora → `convocacao_corrigida_sucedida`, com quem praticou a sucessão e
       quando;
     - em nenhum dos dois casos o comando segue: **a chamada nova que o caminho de hoje praticaria
       não acontece**;
   - a nomeada sem vencimento → `correcao_sem_vencimento` (D-004);
   - o motivo vazio → `motivo_da_correcao_obrigatorio`, com `campo="motivo"`. Hoje, sem motivo, a
     recusa é `convocacao_vigente_existente`, que manda declarar o motivo; com `correcao` a recusa é
     a do campo, porque quem a recebe já está no formulário certo.
4. Espécie: `especie_da_sucessora(contexto, anterior)`, a função pura que a tela também usa (R-004).
5. **A assinatura da prévia** (seção 2): calculada com a apuração, a versão e a forma lidas **aqui**,
   e comparada com a do formulário → `previa_da_correcao_superada`.
6. As guardas de ordem, regularização e déficit, como hoje com `sucede=anterior`.
7. A gravação e a trilha, como hoje; a razão da trilha ganha *"Sucede a convocação ‹id›, de
   vencimento ‹instante›."* (FR-3851).

**O payload da reserva de idempotência** passa a incluir a convocação nomeada e a assinatura: a
mesma chave com outro conteúdo é `idempotency_conflict`, como em todo comando.

**O vencimento obrigatório** mora em `convocar_e_comunicar`, ao lado de `_recusar_vencimento_passado`,
que já está lá: com `correcao` e sem vencimento resolvido → `vencimento_da_correcao_obrigatorio`,
`campo="vencimento"`. Os dois ficam fora da trava, como hoje; o efeito colateral conhecido é que a
**repetição** de um envio feito depois de o próprio vencimento novo passar seria recusada em vez de
devolver o resultado — o caso exige que alguém repita o envio depois do prazo que acabou de dar, e não
grava nada (R-002).

### 2. A assinatura da prévia (FR-3857, D-010)

`alcance.assinatura_da_correcao(convocacao_id, apuracao_id, versao_id, forma, especie)` →
`canonical_sha256` de um dicionário com o gesto `"correcao"` e os cinco valores. É o molde da
`alcance.assinatura` dos vencidos, que já resume apuração, versão e forma (R-003).

**Por que esses cinco bastam.** O fundamento da sucessora é
`fundamento.com_complemento(fundamento.da_convocacao(especie, rótulo do Edital, rótulo do recorte,
data da apuração), complemento)`. Os rótulos saem da versão; a data, da apuração; o complemento é
digitado e viaja no próprio formulário. Fixados convocação, apuração, versão e espécie, o texto
gravado é o texto mostrado. A forma entra porque a prévia diz o que a comunicação vai fazer.

**Quem calcula, e quando:**

- **a tela**, ao montar cada cartão, com a apuração e a versão que a página já leu e a espécie de
  `especie_da_sucessora` — tudo em memória (FR-3855);
- **o comando**, sob a trava, com a apuração e a versão lidas no ato. Hoje o comando lê a versão
  depois das recusas, para gravar; o plano a lê antes da assinatura, uma vez, e reusa a mesma.

**O que a recusa mostra.** A assinatura não diz o que mudou, e não precisa: a recusa recarrega a
página, que monta a **prévia nova** — com a data da apuração nova, a espécie nova, a forma nova — e
a mensagem diz *"A prévia mudou desde que você abriu este formulário: confira o fundamento e a
espécie antes de confirmar."* Os campos voltam preenchidos (seção 3). O comando registra no detalhe
da recusa quais componentes diferem, para o diagnóstico, comparando com os valores atuais.

**O que a assinatura não cobre, e por quê.** O vencimento resolvido de um Evento: ele é escolhido
pela pessoa, e a FR-3849 diz no resultado o vencimento gravado. Uma Retificação que mude o fim do
Evento muda a versão, e a versão está na assinatura.

### 3. A preservação dos campos e a recusa no cartão (FR-3850, D-009)

**A view.** `convocar_view` ganha um ramo: com `corrige` no POST, monta `correcao` e, na
`DomainError`, grava na sessão `recusa_da_correcao` em vez de `erro_da_convocacao`:

```text
{ "convocacao": <nomeada>, "inscricao": <inscrição>, "codigo": <código>, "detalhe": <frase>,
  "campo": <campo, se houver>, "campos": {motivo, vencimento, evento, complemento},
  "cartaoMudou": <código ∈ {sucedida, com_desfecho}> }
```

403 e 404 não passam por aqui: sobem como hoje, e nada é guardado (FR-3847).

**A tela.** `convocacao` consome `recusa_da_correcao` e a prende à linha **da mesma inscrição** — a
chamada é a mesma, ainda que a convocação vigente agora seja outra. Dois desenhos:

| Situação | O cartão mostra |
|---|---|
| a recusa é do formulário ou do domínio, e a nomeada continua a vigente em aberto (motivo vazio, vencimento ausente ou passado, prévia superada, fora da faixa, sem vaga faltante, impedimento surgido no intervalo) | a ação **aberta**, a recusa junto do campo que ela nomeia, ou no topo do formulário; motivo, vencimento, Evento e complemento **preenchidos**; a prévia é a nova, montada agora |
| o cartão mudou (`cartaoMudou`) | a situação nova do cartão — a sucessora com o vencimento dela, ou o desfecho —; a recusa diz *quem* e *quando*; **o motivo digitado aparece como texto citado**, com a instrução *"Copie, se ainda quiser usá-lo"*; o formulário da sucessora, quando ela está em aberto, **nasce vazio** |

O foco vai para a recusa (`role="alert"`, `tabindex="-1"`), como a recusa de topo de hoje. Se a
inscrição não tiver mais cartão no recorte — o que só aconteceria por um ato que tira a pessoa do
recorte —, a recusa cai no topo da tela, onde a de hoje aparece.

**A sessão como portador.** É o mesmo mecanismo do `erro_da_convocacao` e do `resultado_da_convocacao`
(pop na leitura seguinte). O motivo fica na sessão do próprio operador, por um redirecionamento, e
sai dela ao ser exibido (Constituição, III).

### 4. A prévia por cartão, sem consulta por cartão (FR-3844, FR-3855)

`fluxo.previa_das_correcoes(leitura, versao, forma, fundamentos)` devolve, por convocação em aberto e
com vencimento: a espécie da sucessora e se difere da atual; o fundamento derivado (do dicionário
`fundamentos_por_especie`, já calculado para a chamada individual) e se ele cita outra apuração ou
outra versão que a corrigida; a forma de comunicação e a frase do que ela fará; se a chamada já
venceu (o que reabre); a assinatura. Os insumos já estão na página:

- `leitura` traz `apuracao`, `ocupando`, `alcancados`, `regularizaveis`, `causasDeObsolescencia` e as
  linhas, com convocação, desfecho e estado;
- `versao` e `fundamentos` são lidos uma vez por página; `forma_vigente` é pura sobre a versão.

**O impedimento do recorte** (FR-3839) sai dos mesmos insumos: `apuracao is None`,
`causasDeObsolescencia` não vazio, ou ordem não vigente. A ordem é a única informação que a leitura
não traz pronta; o plano usa `ato_vigente` **uma vez por página** se a leitura não a expuser — a
conferir na T001 —, e nunca por cartão.

A prévia só se monta para quem pode emitir, como as prévias da `050` hoje.

### 5. O formulário

`_correcao_da_convocacao.html`, incluído em cada cartão sob `{% if pode_emitir and not linha.desfecho %}`,
depois de *"Registrar desfecho"*, em `<details class="como-preencher">` — aberto quando há recusa
daquele cartão:

- **chamada sem vencimento**: nada (D-004);
- **recorte impedido**: o resumo *"Corrigir esta convocação"* e, no lugar do formulário, *"A correção
  está impedida: ‹causa, nas palavras do topo da tela›."* e o link *"Emitir a apuração seguinte"*,
  para a ocupação (FR-3839);
- **caso geral**: os campos ocultos (`lista`, `chave`, `inscricao`, `corrige`, `previa`), a prévia
  em `<dl class="dados-da-inscricao">` com a origem ao lado de cada valor (UX-101 da `050`), o
  parágrafo de irreversibilidade (FR-3845), o motivo (`textarea required`), o vencimento pelo parcial
  com `obrigatorio=True` (o texto *"Deixe em branco se o Edital não publica prazo"* troca por
  *"Obrigatório: a correção informa o vencimento novo."*; o `required` não vai no `input`, porque o
  Evento é alternativa a ele — quem confere é o servidor), o complemento, a linha do efeito sobre o
  prazo e o botão *"Corrigir a convocação de ‹protocolo›"*.

**O efeito sobre o prazo.** O formulário leva `data-vencimento-atual` no formato do `datetime-local`;
cada `<option>` de Evento leva `data-fim` no mesmo formato. `correcao-da-convocacao.js` compara o
valor informado — o do campo, ou o fim do Evento escolhido — com o atual e troca o texto de
`<p class="nota" aria-live="polite" data-efeito-do-vencimento>`: *"O prazo é estendido até …"*,
*"O prazo é antecipado para …: um vencimento anterior ao atual encurta um prazo já comunicado."*,
*"O vencimento é mantido."* Sem script — ou antes de informar —, o parágrafo diz as três regras. A
comparação é de texto no mesmo formato e no mesmo fuso, o da instituição, que é o do `datetime-local`
da tela.

**O resultado.** `acao == "correcao"` em `convocacao.html`: *"Convocação de ‹protocolo› corrigida. O
vencimento passou de ‹anterior› para ‹novo›: o prazo foi estendido."* (ou antecipado, ou mantido),
seguido do resultado da comunicação, pelo parcial que a chamada individual já usa. A view lê o
vencimento anterior da própria convocação corrigida, depois do ato — não do formulário.

**O cartão depois do ato.** A linha da sucessora mostra o vencimento novo e o estado recalculado, e
ganha, ao lado do fundamento, *"Corrigida em ‹data› — ver o histórico"*, quando a convocação vigente
tem `convocacao_anterior`. É informação que a linha já traz.

### 6. A trilha e o histórico (FR-3851, FR-3852)

A razão do evento de convocar já tem o recorte, a apuração, a ordem, o fundamento, o motivo da
sucessão e a origem do vencimento. Ganha, quando há anterior, a convocação corrigida e o vencimento
dela. Ator, base, escopo e instante vêm do `auditar` de sempre. O histórico (`convocacao_historico`)
já mostra a sucedida com o motivo da sucessora; o plano só o prende por teste, com duas correções em
cadeia.

### 7. O portal

Nada muda. A sucessora é a convocação vigente da chamada, e o portal a lê pelas regras da `115` e da
`118`; `test_a_correcao_com_vencimento_novo_reabre` já prova, no serviço, que o Requerimento reabre.
O que falta é a prova de ponta a ponta (seção 8). **Se ela falhar por defeito do portal, o defeito é
registrado em `doc/`, a feature não se declara concluída, e a decisão sobre o conserto é do usuário**
(FR-3854).

## Validação planejada

### Por camada

| Camada | Arquivo | O que prende |
|---|---|---|
| unidade | `unit/convocacao/test_correcao_pura.py` | `especie_da_sucessora` (posição, fallback da raiz, regularizar); `assinatura_da_correcao` muda com cada um dos cinco componentes e só com eles |
| serviço | `integration/convocacao/test_correcao_da_convocacao.py` | FR-3843 (sucedida, com desfecho, de outra inscrição, de outro recorte), FR-3857 (apuração seguinte, Retificação, espécie), motivo e vencimento obrigatórios, sem vencimento, nenhuma chamada nova, idempotência nos três resultados da comunicação, trilha, cadeia, regularizar |
| interface | `interface/test_correcao_da_convocacao.py` | a ação nos três estados e a ausência nos cinco casos da FR-3838; o impedimento; a prévia e os textos; o POST com sucesso, o resultado e o cartão; cada recusa no cartão com os campos; o cartão mudou; 403; 404; duplo POST; histórico; vocabulário |
| desempenho | `performance/test_convocacao.py` | a tela com 1 e com 20 chamadas em aberto, o mesmo número de consultas |
| script | `javascript/correcao-da-convocacao.test.js` | estende, antecipa, mantém, sem valor, pelo Evento, valor apagado |
| navegador | `navegador/test_jornada_da_correcao_da_convocacao.py` | a jornada da gestão ao portal (abaixo), sem violação de CSP no console, sem rolagem horizontal a 375 px |

### A jornada no navegador (SC-1141, SC-1142)

No molde de `test_depois_do_prazo_nada_se_envia_e_nada_se_decide_sozinho` da `115`: preparação por
fixtures, ações só no navegador, verificações na tela, no banco e na trilha.

1. **Preparação** — o que o cenário G da `118` (`tests/fixtures/jornada_do_convocado.py`) monta: um
   documento pendente com motivo, o Requerimento declarado na convocação nunca enviado, o vencimento
   decorrido sem desfecho. No navegador o relógio não se adianta: como o teste vencido da `115`, a
   convocação nasce com vencimento de dois segundos, é comunicada, e o teste espera três. A sessão
   do portal do convocado aberta, como depois do código de acesso.
2. **Portal, 375 px, antes** — a convocação diz que o prazo terminou; o reenvio e o Requerimento são
   recusados com a mesma frase.
3. **Gestão, desktop** — a presidência abre a condução, abre *"Corrigir esta convocação"* no cartão
   de G, lê a prévia (*"o que reabre"*), informa o motivo e um vencimento futuro e confirma. Lê o
   resultado (*"estendido"*) e o cartão em *"Prazo em curso"*.
4. **Portal, 375 px, depois** — o prazo novo no formato único da `118`; complementa o documento
   pendente; preenche e envia o Requerimento.
5. **Gestão** — os documentos da convocação: a complementação aguardando conferência, a conferência
   anterior legível; o histórico com a sucedida e o motivo.
6. **Verificações** — uma sucessora, mesmo número de chamada; um evento de trilha com o motivo e os
   dois vencimentos; nenhuma lista, apresentação ou conferência a menos.

Um segundo caso no mesmo arquivo: **apuração superada** — um desfecho em outro cartão do mesmo
recorte deixa a apuração para trás; todos os cartões em aberto mostram a limitação e o link, e
nenhum formulário (SC-1146).

**A demonstração humana** repete os passos 2 a 5 no navegador do app, com capturas, e o registro vai
para `verificacao.md`, como a `118` fez.

## Riscos

| Risco | Mitigação |
|---|---|
| Teste existente prende a razão da trilha de convocar por texto exato | a frase nova só entra quando há anterior; T001 procura `Motivo da sucessão` nos testes antes de mudar |
| A chave de idempotência da tela é uma só por página, com sufixo por formulário | o sufixo da correção leva o id da convocação, que é único por cartão |
| Varredura de vocabulário da convocação (`test_vocabulario_da_convocacao.py`) tem lista literal de templates | o parcial novo entra na lista na mesma tarefa que o cria |
| Classe nova sem regra na folha reprova `test_acessibilidade` | reusar `como-preencher`, `confirmar`, `campo`, `nota`, `dados-da-inscricao`, `erro`; classe nova só com regra |
| Script novo sem teste reprova `test_javascript.py`, ou não carrega por CSP | arquivo estático com `defer`, e teste `node --test` no padrão de `tests/javascript/` |
| O vencido no navegador | o vencimento curto e a espera do teste vencido da `115`, e não `mock` do relógio, que o `live_server` não compartilharia com segurança; nos testes de interface, o relógio adiantado do cenário G |
| Defeito do portal na jornada | registrado em `doc/`, conclusão bloqueada, decisão do usuário (FR-3854) |
| Teste de tempo da ocupação oscila sob carga | conhecido (`CLAUDE.md`); medir isolado antes de atribuir ao diff |
