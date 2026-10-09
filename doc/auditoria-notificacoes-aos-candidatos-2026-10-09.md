# Auditoria — Notificações aos candidatos vinculadas a publicações

*Auditoria exploratória de 09/10/2026, sobre a `main` em `4ace3722` (depois da `063`). Nada foi
implementado, migrado nem aberto no Spec Kit. Caminhos de código são relativos a
`backend/processo_seletivo/`, salvo quando começam por `specs/`, `doc/` ou `backend/`.*

**A demanda, nas palavras do setor:** *"Toda a convocação/publicação de resultado que publicarmos na
página do PS o sistema poderia permitir que fizéssemos notificação para os candidatos. Seja
convocação de PPI, para entrevista de títulos, chamada de suplentes, etc. O texto da notificação
seria feito pela seleção. Se possível que o sistema permita salvar os modelos de texto."*

## Resumo em cinco linhas

1. **A demanda colide com duas normas escritas do próprio projeto, e não com limitação técnica.** A
   `FR-084` da `010` diz que o sistema envia mensagem em *exatamente três* situações e exclui
   nominalmente "aviso de retificação, de resultado, lembrete e campanha"
   (`specs/010-area-do-candidato/spec.md:548-555`). A `017` põe "comunicação ativa — e-mail, SMS,
   push, WhatsApp" fora do escopo (`specs/017-publicacao-de-resultados/spec.md:659`). Um teste conta os
   módulos que enviam e reprova o quarto (`backend/tests/test_situacoes_de_mensagem.py:27-31`). Abrir
   a feature exige antes **revisar a `FR-084` por escrito**, como a `019` fez para a convocação.
2. **Metade dos exemplos do setor tem destinatário determinístico hoje, e metade não.** O resultado
   publicado (D), a retificação de resultado (E) e a chamada de suplentes (C) apontam a lista exata
   de inscrições. Já a convocação para heteroidentificação (A) não existe como ato no sistema
   (`specs/019-convocacao-chamada-suplencia/spec.md:792`). A entrevista e a avaliação de títulos (B)
   são Etapas, e convocar para uma Etapa não é ato do sistema.
3. **A infraestrutura de e-mail existe e já resolveu quase tudo o que a demanda pede de difícil.**
   A convocação por mensagem individual (`convocacao/application/comunicar.py`) já tem:
   - reserva de idempotência antes do envio;
   - envio fora da transação;
   - registro append-only de `ENVIADA` e `FALHA`, sem a palavra "recebida";
   - contagem do retorno do `send_mail`;
   - detalhe técnico sem dado pessoal.

   O que falta é texto editável, modelos e um envio que suporte centenas de pessoas sem prender a
   requisição.
4. **O gargalo técnico é o volume, e não o modelo de dados.** Não há fila nem worker
   (`doc/implantacao-em-producao-ubuntu.md:99-101`). O SMTP é síncrono e não tem timeout (gap I-4,
   `:1549`), e o gunicorn corta em 120 s. Hoje um envio para algumas centenas de pessoas dentro de
   uma requisição é aposta, não projeto.
5. **Recomendação:** implementar, depois de revisar a `FR-084`, como **aviso complementar ligado a
   um ato existente**, com o texto da seleção, um conjunto pequeno de variáveis e rodapé fixo. A
   primeira entrega cobre D, E e C (por publicação). A e B ficam registrados como lacuna, porque
   dependem de ato que o sistema ainda não pratica.

## Decisões do usuário, de 09/10/2026

*Tomadas sobre a primeira versão deste relatório. Onde divergem do que vem abaixo, prevalecem, e
os trechos afetados estão anotados no lugar.*

| Questão | Decisão |
|---|---|
| Revisão da `FR-084` da `010` e da exclusão da `017` | **Aprovada.** Quarta situação, estritamente o aviso complementar vinculado a ato oficial, sem efeito sobre prazos, classificação, situação da inscrição ou direitos. Histórico preservado |
| Quem envia | Capacidade própria `aviso:enviar`, concedida de início ao **publicador**, ao **gestor** e à **presidência da comissão**, no escopo institucional. Enviar aviso **não** autoriza publicar resultado nem praticar ato |
| Destinatários | Só os do ato. Resultado: **todos os considerados**, inclusive sem posição. **Nem acréscimo nem exclusão manual no MVP**; os casos sem endereço ficam registrados à parte. Deduplicação por inscrição entre as listas do marco |
| Modelos | Por unidade: criar, editar, reutilizar e inativar. Texto editável antes de cada envio, só com variáveis controladas. Rodapé institucional obrigatório |
| Conteúdo | Assunto neutro, sobretudo em procedimento ligado a reserva de vagas. Sem classificação, resultado individual, motivo de eliminação ou dado sensível no corpo |
| Envio | Fora da requisição, com PostgreSQL e systemd, sem Celery ou RabbitMQ. A spec define idempotência, recuperação, concorrência entre execuções, interrupção, timeout SMTP, limites e tentativa indeterminada. **Falha depois da aceitação e antes do registro não pode gerar reenvio automático.** Aceita pelo servidor não é entregue |
| Retificação | Permite um aviso novo, que se declara sobre publicação retificadora, **sem afirmar que a situação individual mudou** e sem reenviar a todos automaticamente |
| Escopo do MVP | Resultado preliminar e definitivo; retificação de resultado; convocação de titulares e suplentes por publicação |
| Fora do MVP, registrado | Convocação PPI, entrevista e avaliação de títulos, como capacidade futura ligada à evolução dos atos. Registro próprio em [`registro-convocacao-para-etapas-2026-10-09.md`](registro-convocacao-para-etapas-2026-10-09.md). O MVP **não encerra** a demanda do setor |
| Agendamento | Fora do MVP |
| LGPD | Validação institucional registrada como pendente, e exigida antes da entrada em produção |
| Achado do prazo | Investigar com teste, separado da feature. **Investigado: não se confirma** (ver o fim deste relatório) |

---

## A. Diagnóstico do estado atual

### A.1 O que o sistema publica, e onde

- **O sistema tem página pública própria, e ela é a "página do PS".** O portal fica em `selecoes/`
  (`backend/config/urls.py:16`):
  - o Edital: `selecoes/<edital_id>/`, em `portal/views.py:395` e `portal/templates/portal/selecao.html`;
  - cada resultado: `selecoes/resultados/<publicacao_id>/`, em `portal/views.py:2519-2600`.

  Desde 28/09 o PDF que o sistema gera é o documento oficial do piloto
  (`specs/054-edital-como-ato-oficial/spec.md:30`).
- **Atos publicados que o sistema pratica:**

  | Ato | Modelo | Natureza |
  |---|---|---|
  | Edital e Retificação | `publicacoes.Publicacao` (`publicacoes/models.py:46-97`), `Retificacao` (`publicacoes/models_retificacao.py:36-66`) | append-only |
  | Resultado (classificação) | `divulgacao.PublicacaoResultado` (`divulgacao/models.py:35-159`) | append-only, `PRELIMINAR` ou `DEFINITIVA` (`:28-32`) |
  | Relação do sorteio | `sorteios.RelacaoDeHabilitados` (`sorteios/models.py:29`) | append-only |

- **O que não é publicado pelo sistema:**
  - o `ResultadoEtapa` (`017`, D-002);
  - o corte (interno, `063` L-2);
  - a homologação (`017`, D-003);
  - **a convocação por publicação.** Nesse caso a equipe publica no site e o sistema só registra
    onde: `ComunicacaoEmitida.referencia_da_publicacao` (`convocacao/models.py:374-382`), exigida em
    `comunicar.py:180-189`.

### A.2 Como cada ato identifica seus destinatários

- **Resultado publicado → `SituacaoDivulgada`** (`divulgacao/models.py:162-211`). É uma linha por
  inscrição do universo do ato, `CLASSIFICADA` ou `SEM_POSICAO`, gravada na mesma transação da
  publicação (`divulgacao/application/publicar.py:258-269`). Ela tem `UNIQUE (publicacao, inscricao)`
  e FK `PROTECT` para `Inscricao`. Isso torna a lista **exata e congelada**.
  - O conjunto é o **universo do ato**, e não "todos os inscritos":
    - inscrições `SUBMETIDA` do Perfil;
    - filtradas pela modalidade, quando a lista é reservada;
    - restritas a quem participa no marco (`classificacao/application/calculo.py:55-74`,
      `resultados/application/prontidao.py:408`).
  - A **lista pública** (`conteudo_publico["posicoes"]`) traz só quem tem posição. A `SituacaoDivulgada`
    traz também os `SEM_POSICAO`, com motivo (`divulgacao/domain/conteudo.py:69-92`). A diferença
    importa para o Cenário D.
- **Convocação → `Convocacao`** (`convocacao/models.py:84`). É uma inscrição chamada para vaga num
  recorte (Edital × Perfil × marco × lista), com `especie` `VAGA_INICIAL`, `SUPLENCIA` ou
  `PARA_REGULARIZAR`. A pessoa é selecionada pela cadeia ordem → corte → apuração, e nunca por
  escolha manual (`convocacao/application/convocar.py:99-127, 295-343, 408-475`).
- **Edital e Retificação → nenhuma ligação com inscrições.** O efeito sobre o candidato é implícito,
  pela versão vigente. O universo natural de um aviso de retificação seria "inscrições enviadas
  neste Edital", que é consulta trivial e determinística, mas não é lista que o ato declare.
- **Participantes de uma Etapa** podem ser derivados pelo panorama de prontidão: submetidas, menos
  eliminadas antes, menos quem aguarda a anterior (`avaliacoes/application/selectors.py:96-150`).
  Quem avança para a Etapa governada sai do corte vigente (`ItemDoCorte.PROGREDIU`,
  `classificacao/models.py:360-374`). **Nenhum dos dois é ato publicado.**

### A.3 Retificação, sucessão e anulação

- **Tudo é sucessão por linha nova, nunca alteração.**
  - `PublicacaoResultado.publicacao_anterior` admite um sucessor por publicação
    (`divulgacao/models.py:58-64, 102-129`). A vigente é a que ninguém sucedeu
    (`divulgacao/application/selectors.py:16-33`).
  - A cadeia se repete na `Convocacao` (`convocacao_anterior` + `motivo_da_sucessao`), no
    `AtoDeOrdenacao`, no `Corte` e no `ResultadoEtapa`.
- **A publicação sucedida continua respondendo na mesma URL** e aponta para a vigente
  (`portal/views.py:2526-2545`). Isso resolve de graça o Cenário E: o link de um e-mail antigo nunca
  quebra e nunca engana.
- **Não existe anulação de publicação de resultado.**

### A.4 E-mail que já existe

| Situação (`FR-084`) | Módulo | Destino |
|---|---|---|
| código de acesso e aviso de mudança de credencial | `identidade/application/mensagem.py` | credencial |
| confirmação do envio da inscrição | `inscricoes/application/mensagem.py` | `Inscricao.email` congelado |
| convocação, quando o Perfil declara `INDIVIDUAL_MESSAGE` | `convocacao/application/comunicar.py` | credencial principal, senão `Inscricao.email` (`:105-122`) |

O que `comunicar.py` já resolve e deve ser **reaproveitado como padrão**, e não reinventado:

- **Autoriza antes de trabalhar**, com `exigir_base_de_comissao` (`:158`).
- **Reserva a chave numa transação curta antes do envio** (`:239-258`). Reserva pendente não
  reenvia; responde `emissao_em_estado_indeterminado` (`:199-206`).
- **Envia fora da transação.** O `comando_de_comissao` trava o Processo, e um SMTP lento paralisaria
  o certame (`:141-150`).
- **Conta o retorno de `send_mail`**: `0` é `FALHA`, e não sucesso silencioso (`:359-378`).
- **Detalhe técnico sem endereço** (`:315-321`).
- **Registro append-only** em `ComunicacaoEmitida`, `ENVIADA` ou `FALHA`, sem campo de entrega ou
  leitura (`convocacao/models.py:349-425`). A tela diz "enviado em", nunca "recebido em" (`019`,
  D-009, FR-288a).
- **Uma mensagem por destinatário**, sem `To` múltiplo e sem `BCC`, o que impede expor um endereço
  a outro.
- **Envio em lote como laço sequencial com chave por pessoa**, em que uma falha não interrompe as
  outras: `comunicar_cada` (`convocacao/application/fluxo.py:348-396`), usado por "Emitir N
  comunicações" (`:669-720`).

O que **não** existe:

- texto editável (`ASSUNTO` e `CORPO` são constantes, `comunicar.py:39-61`);
- modelos de mensagem;
- fila, worker ou agendamento (`doc/implantacao-em-producao-ubuntu.md:99-101, 130`);
- timeout de SMTP (gap I-4, `:1549`);
- marca de endereço inválido, devolução (bounce) ou descadastro;
- canal além do e-mail.

### A.5 Endereço do candidato

- **`CandidateEmail` só guarda credencial verificada.** Ela é provada pelo código de acesso
  (`identidade/models.py:58-94`), e não existe linha "não verificada".
- **`Inscricao.email`** (`inscricoes/models.py:42`) é copiado da credencial e congela no envio.
  Inscrições anteriores ao portal podem trazer endereço digitado e não provado.
- **A ordem já decidida pela `019` — credencial principal, depois endereço da inscrição — serve
  igual aqui** (`comunicar.py:105-122`).
- **Uma pessoa pode ter várias inscrições**: uma por Perfil por Edital
  (`inscricoes/models.py:73-76`), ligadas pelo `identity_subject`.

### A.6 Papéis, escopo e auditoria

- **Papéis** (`interface/identidade.py:20-107`):
  - `publicador` tem `edital:publicar`, `retificacao:publicar` e `resultado:publicar`;
  - `gestor` tem `comissao:gerir`;
  - a presidência da comissão do Processo também dá base de gestão
    (`comissoes/domain/autorizacao.py:65-81`);
  - `auditor` só consulta.
- **Convocar e comunicar não têm permissão nomeada.** Usam a base de comissão
  (`comissoes/application/__init__.py:45-93`).
- **Isolamento institucional por `institution_scope`.**
  - Toda consulta filtra pelo escopo do ator. Objeto de outra unidade e objeto inexistente
    respondem igual, com 404 (`seguranca/application/authorization.py:117-146`).
  - `Unidade.codigo` é o próprio escopo (`unidades/models.py:1-29`).
  - **Não existe papel entre unidades** (`specs/060-unidades-e-autoridades/spec.md:402, 413`;
    `specs/040-visao-institucional-dos-processos/spec.md:673`).
- **Auditoria append-only em duas camadas** (`auditoria/models.py:6-40`):
  - gatilho;
  - privilégio retirado pela lista `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:26-121`).

  O ponto de entrada é `auditar` (`avaliacoes/application/trilha.py:28-68`). O lote se correlaciona
  por `correlation_id` sem entidade própria (`050`, D-011).

### A.7 Componentes de tela reaproveitáveis

- **`previa_de_publicacao.html`**: prévia que "não grava nada" e confirmação assinada. A prévia
  defasada leva 409 (`divulgacao/application/publicar.py:65-91`).
- **`convocacao.html`, seção "Comunicações que ainda não saíram"** (`:193-225`):
  - pessoas alcançadas em `<ol class="consequencias">`;
  - `alcance` assinado e `chave`;
  - parcial `_resultado_da_comunicacao.html`, com enviadas e falhas e nunca "recebidas".
- **`marco_conferir.html`**: "Confira antes de confirmar", com grupos a fazer, já feito e bloqueado.
- **`publicacoes_do_marco.html`**: é a tela para a qual `publicar_resultado` redireciona depois do
  ato (`interface/views.py:8088`). É o lugar natural do botão.

### A.8 O canal que o candidato já tem

- **O portal já mostra convocação e situação sem depender de e-mail** (`059`, `063`):
  - "➜ Convocação aberta" em `portal/templates/portal/inscricoes.html:35-48`;
  - Situação → Por quê → O que fazer em `portal/situacao.py`.
- **A pesquisa de 07/10 recomenda o e-mail como "convite a voltar ao painel, nunca o canal do
  resultado"** (`doc/pesquisa-divulgacao-de-resultados-2026-10-07.md:100`). Ela marca o e-mail por
  publicação como "escopo novo [que] pede decisão do usuário" (`:200`).

---

## B. Matriz de cenários

| | Tipo de publicação | Origem dos destinatários | Identificação automática | Risco de envio incorreto | Recomendação |
|---|---|---|---|---|---|
| **A — Convocação PPI (heteroidentificação)** | Lista divulgada pela equipe (Edital 90/2026, 4.1: *"convocados … por meio de listagem divulgada"*). **Não é ato do sistema** | Nenhuma no sistema. A heteroidentificação é "spec própria" (`019:792`, `014:882`), e a seção do Edital é só textual (`editais/domain/secoes.py:94-97`). Etapa não se restringe a modalidade (`editais/api/serializers.py:215-240`) | **Não.** Aproximá-la por "inscritos na lista PPI" é inferência: o Edital convoca os *deferidos*, e quem decide é a comissão | **Alto**: errar aqui é dizer a alguém que a autodeclaração dela será verificada, ou não chamar quem deveria. Assunto revela dado sensível | **Lacuna funcional.** Fora do MVP. Paliativo, se o ato coincidir com um resultado publicado da lista PPI: usar a origem D, com modelo próprio e assunto neutro |
| **B — Entrevista / avaliação de títulos** | Convocação para Etapa, publicada pela equipe fora do sistema, com data e horário | Derivável: corte vigente (`PROGREDIU` na Etapa governada) ou participantes da Etapa (panorama). A Etapa tem `scheduleEventId`, e o Evento tem `location` (`editais/api/serializers.py:205`): **uma** data e **um** local, não horário por pessoa | **Parcial.** O conjunto sai de atos vigentes, mas não de ato *publicado*, e horário individual não existe | **Médio**: o corte pode ser sucedido depois do envio, e a lista externa pode divergir | **Melhoria posterior.** Exige referência externa declarada, como a convocação por publicação já faz, e conferência da lista pelo operador. Horário individual é fora de escopo |
| **C — Chamada de suplentes** | `Convocacao` com `especie=SUPLENCIA` | `Convocacao` vigente da chamada, mais `ComunicacaoEmitida` | **Sim** | **Baixo**: a chamada já passou pela fila, pelo corte e pelo déficit (`convocar.py:295-343`) | **Duas situações diferentes.** (1) Perfil `INDIVIDUAL_MESSAGE`: o sistema **já envia**, e a mensagem inicia o prazo. Não criar segundo canal. (2) Perfil `PUBLICATION`: aviso complementar aos convocados que têm `ComunicacaoEmitida` com aquela referência. **MVP** |
| **D — Resultado preliminar ou definitivo** | `PublicacaoResultado` | `SituacaoDivulgada` da publicação (ou do conjunto de listas do marco) | **Sim, e congelada** | **Baixo** quanto à lista. **Médio** quanto ao conteúdo, se o texto afirmar situação | **MVP.** Três universos possíveis, todos determinísticos: (i) classificados na lista; (ii) todos os considerados, incluídos os `SEM_POSICAO`; (iii) todos os inscritos do Edital. Recomenda-se (ii) como padrão, porque é quem o ato alcança, e o corpo **sem** o resultado |
| **E — Retificação** | Nova `PublicacaoResultado` que sucede a anterior; ou `Retificacao` do Edital | Resultado: `SituacaoDivulgada` da sucessora. Edital: inscrições `SUBMETIDA` do Edital | **Sim** nos dois | **Baixo**: o aviso antigo fica intacto, e o link dele mostra "substituída por" (`portal/views.py:2526-2545`) | Resultado: **MVP**, como aviso novo ligado à sucessora e ao aviso anterior. Retificação do Edital: **melhoria posterior** (universo amplo, ver H) |
| **F — Várias inscrições da mesma pessoa** | — | `identity_subject`. Uma inscrição por Perfil por Edital (`inscricoes/models.py:73-76`) | **Sim** | **Médio**: a mesma inscrição aparece na lista AC **e** na PPI do mesmo marco | Dentro de um aviso: **uma mensagem por inscrição**, unindo as listas. Entre Perfis: mensagens distintas, porque são fatos distintos. Aviso de Edital inteiro: uma por pessoa |

**O que a matriz mostra:** dos três exemplos do setor ("PPI, entrevista de títulos, chamada de
suplentes"), só o terceiro tem ato no sistema hoje. Os resultados (D e E), que o setor diz em
"publicação de resultado", são o caso mais limpo de todos.

---

## C. Proposta funcional

### C.1 Conceito: *aviso*, e não *comunicação*

O vocabulário já está tomado, e confundir os dois custa prazo de candidato.

- **"Comunicação da convocação"** (`ComunicacaoEmitida`) é **ato com efeito**. Quando o Edital
  comunica por mensagem individual, o prazo corre do envio (`019`, FR-269a, D-009).
- **"Aviso"**, o objeto novo, é **complementar e sem efeito**:
  - não inicia nem altera prazo;
  - não altera situação, classificação ou direito;
  - não substitui a publicação oficial;
  - não toca `ComunicacaoEmitida`.

  Os dois não podem compartilhar tabela, botão nem palavra na tela.

### C.2 Regras essenciais

1. **Todo aviso cita um ato existente.** Pode ser uma `PublicacaoResultado` (ou o conjunto de listas
   de um marco), ou uma chamada de convocação com `ComunicacaoEmitida` por publicação. Sem ato
   citado, não há botão. Isso elimina por construção o **envio antes da publicação**.
2. **Os destinatários vêm do ato, nunca de filtro.** A tela mostra a origem por extenso: *"As 132
   inscrições consideradas no Resultado preliminar do marco 'Análise documental', listas Ampla
   concorrência e Pretos, pardos e indígenas"*. O operador pode **excluir** pessoas com motivo, mas
   não **acrescentar**. *(Superado em 09/10: nem acréscimo nem exclusão manual no MVP. Só a
   ausência de endereço tira alguém do envio, e ela é registrada.)*
3. **A lista é congelada na confirmação.** Uma retificação posterior não muda quem recebeu o aviso
   anterior. Ela pede aviso novo.
4. **O texto é da seleção. O rodapé é do sistema e não se edita.** O rodapé:
   - aponta a publicação oficial;
   - diz que ela é a referência "conforme o Edital";
   - informa o atendimento;
   - informa que a mensagem é automática.
5. **Variáveis fechadas.** As chaves desconhecidas são recusadas na prévia. Não há linguagem de
   template.
6. **Sem dado pessoal além do nome.** Não entram CPF, telefone, pontuação, posição, motivo de
   eliminação nem link que autentica. É a mesma régua da `FR-084a` e da `FR-290`.
7. **Um aviso por ato, salvo reenvio justificado.** Um segundo aviso sobre o mesmo ato exige
   justificativa, que fica gravada e auditada. O duplo clique é absorvido pela chave de
   idempotência, como hoje.
8. **O reenvio de falhas não exige justificativa** e alcança só quem não teve envio aceito.
9. **O que foi enviado não muda.** O assunto, o corpo final, a lista e o resultado de cada tentativa
   são append-only.

### C.3 Jornada do operador

A jornada do item 8 da demanda se confirma, com dois ajustes:

1. **O ponto de partida é a tela para onde o ato já leva.** Depois de publicar, o sistema redireciona
   para `publicacoes_do_marco` (`interface/views.py:8088`). Ali, ao lado da publicação vigente, entra
   "Avisar candidatos". Na convocação por publicação, o botão fica no cartão da chamada, depois de
   registrada a referência.
2. **O aviso é por marco, e não por lista.** Publicar o resultado de um marco produz uma publicação
   por lista. Avisar lista por lista mandaria duas mensagens a quem concorre na AC e na PPI. O aviso
   reúne as publicações vigentes do marco com a mesma natureza e deduplica por inscrição.

Fluxo:

> Publicações do marco → **Avisar candidatos** → (1) quem recebe, e de onde veio → (2) modelo ou
> texto livre → (3) prévia com o assunto, o corpo e o rodapé, preenchidos para uma pessoa real da
> lista → (4) números: com endereço, sem endereço, excluídos, já avisados por este ato →
> **Enviar a 132 pessoas** → histórico do aviso, com aceitas, falhas e sem endereço, e "Tentar de
> novo as falhas".

---

## D. Proposta técnica mínima

*Não implementado. Nomes indicativos.*

### D.1 Dados

Um app novo e pequeno (`avisos`). Fica fora de `divulgacao` porque cita também convocação, e fora
de `convocacao` porque não é ato dela.

| Modelo | Natureza | Campos essenciais |
|---|---|---|
| `ModeloDeAviso` | mutável e auditado; **nunca excluído**, só inativado | `institution_scope`, `nome`, `finalidade` (rótulo livre), `assunto`, `corpo`, `ativo`, `criado_por/em` |
| `Aviso` | append-only | `edital`, `institution_scope`, origem (`RESULTADO` ou `CONVOCACAO_POR_PUBLICACAO`), referência ao ato, `assunto` e `corpo` **finais**, `modelo` (FK nula), `aviso_anterior` e `justificativa`, `solicitado_por/em` |
| `PublicacaoDoAviso` | append-only | `aviso`, `publicacao` (as listas do marco) |
| `DestinatarioDoAviso` | append-only | `aviso`, `inscricao`, `endereco` resolvido, `excluido_com_motivo`; `UNIQUE (aviso, inscricao)` |
| `TentativaDeEnvio` | append-only | `destinatario`, `resultado` (`ACEITA`, `FALHA` ou `SEM_ENDERECO`), `em`, `detalhe_tecnico` |

- **Por que congelar o corpo no `Aviso`, e não renderizar do modelo:** o modelo muda, e o que foi
  enviado não pode mudar. Guardar o texto final, com variáveis do Edital resolvidas e só
  `{nome_do_candidato}` por resolver, torna o histórico do modelo irrelevante. Também evita guardar
  132 cópias do mesmo corpo.
- **Por que "pendente" não é coluna:** pendente é destinatário sem `TentativaDeEnvio` aceita. Assim
  nada é atualizado, e o padrão é o mesmo da vigência por "ninguém sucedeu".
- As quatro tabelas append-only entram em `TABELAS_APPEND_ONLY`. O `M` do `provisionar_papeis` sobe
  de 34 para 38, e o `AGENTS.md` precisa acompanhar.

### D.2 Destinatários: seletores, não lógica nova

- Resultado: `SituacaoDivulgada.objects.filter(publicacao__in=…)`, distinta por inscrição.
- Convocação por publicação: `Convocacao` vigentes com `ComunicacaoEmitida` `PUBLICATION`/`ENVIADA`
  daquela referência.
- Endereço: `destinatario_de` (`comunicar.py:105`), extraído para um ponto comum e não duplicado.

### D.3 Envio: a única decisão técnica de peso

O padrão de `comunicar_cada` (um `send_mail` por pessoa, sequencial, dentro da requisição) não
escala para centenas. **Não está medido** quanto o SMTP institucional leva por mensagem. Mas basta
algumas centenas de milissegundos por mensagem, num aviso de algumas centenas de pessoas, para
encostar nos 120 s do gunicorn, e o gap I-4 deixa um SMTP pendurado prender o worker inteiro.
Duas saídas, nesta ordem de preferência:

1. **Despacho pelo banco, com timer do systemd.**
   - A confirmação grava `Aviso` e `DestinatarioDoAviso` e responde na hora.
   - Um comando `despachar_avisos`, num timer igual aos quatro que já existem
     (`doc/implantacao-em-producao-ubuntu.md:2070-2100`), envia os pendentes em lotes pequenos, com
     uma conexão SMTP reaproveitada e um limite por minuto.
   - Não entra dependência nova. É a forma mínima de "fila" que o Princípio V admite **com
     necessidade demonstrada**, e a necessidade é a conta acima. De quebra, dá reenvio de falha
     temporária sem operador.
2. **Envio em fatias na requisição**, com "Continuar o envio (faltam 80)". Funciona sem processo
   novo, mas põe o operador em laço e deixa o aviso pela metade se ele fechar a aba.

Nas duas saídas, **`EMAIL_TIMEOUT` é pré-requisito** e corrige um gap que já afeta o código de
acesso.

### D.4 Permissão e escopo

- **Uma capacidade nova, `aviso:enviar`, e não reuso de `resultado:publicar`.** Constituição III:
  responsabilidade, não cargo. Quem publica o resultado não é necessariamente quem fala com o
  candidato.
  - Ela entra no papel `publicador`. Talvez entre também no `gestor` (ver H.2).
  - Na convocação por publicação, exige também a base de comissão, como `comunicar` já exige.
- **`aviso:modelo:gerir`** para os modelos.
- O histórico se lê com `aviso:enviar` **ou** `auditoria:consultar`, como as publicações.
- O escopo é o filtro `institution_scope` de sempre. Não há papel entre unidades, e esta feature não
  deve criar um.

### D.5 Auditoria

- `auditar` na confirmação, com origem, número de destinatários e `correlation_id`.
- `auditar` no reenvio, com justificativa.
- `auditar` na criação, edição e inativação de modelo.
- **O que não vai para a trilha:** a lista de endereços. Ela já está em `DestinatarioDoAviso`, e
  duplicá-la na trilha aumenta exposição sem acrescentar prova.

### D.6 O guardião

`backend/tests/test_situacoes_de_mensagem.py` passa a declarar quatro situações, e o módulo
remetente entra em `SITUACOES`. A spec da `010` ganha a revisão datada, com a redação anterior
preservada. É o mecanismo que a própria `FR-084` prevê, e ele funcionou da última vez.

---

## E. Proposta de UI/UX

Integrada às telas existentes. Não há menu "Comunicação" nem tela de campanha.

1. **`publicacoes_do_marco.html`**
   - Na publicação vigente, um botão secundário **Avisar candidatos**, ao lado do link "Página pública"
     (`interface/templates/interface/publicacoes_do_marco.html:62`).
   - Uma linha de estado: *"Nenhum aviso enviado sobre esta publicação"* ou *"Aviso enviado em
     09/10, 14:02 — 128 aceitas pelo servidor, 4 sem endereço"*.
   - Na sucedida, nenhum botão, porque não se avisa sobre ato que não vale mais.
2. **Tela "Avisar candidatos"**, uma página em quatro blocos verticais, sem assistente de passos:
   - **Quem recebe**, com a origem por extenso e o universo escolhido: *considerados* (padrão) ou
     *só os classificados*. A lista fica recolhida. "Excluir" pede motivo. *(Superado em 09/10:
     o universo é sempre o dos considerados, e não há exclusão manual.)*
   - **Mensagem**: um seletor de modelo (ativos da unidade, mais os padrões do sistema), o assunto e
     um corpo em `<textarea>` simples, com a lista de variáveis clicáveis ao lado. Rodapé fixo,
     visível e não editável.
   - **Prévia**: a mensagem como ela sai, para a primeira pessoa da lista, com "ver outra". Variável
     desconhecida aparece em vermelho e bloqueia o envio.
   - **Confirmar**: os números (com endereço, sem endereço, excluídos e, se for o caso, *já
     avisados por este ato em 08/10*); o campo de justificativa, que só aparece no reenvio; e o
     botão **Enviar a 128 pessoas**, com o número no rótulo.
   - A prévia é assinada, como `assinatura_da_previa`. Se a lista mudou entre prévia e confirmação,
     a resposta é 409 e a prévia se refaz.
   - Opção "Salvar este texto como modelo".
3. **Histórico do aviso**, com o padrão de `_resultado_da_comunicacao.html`:
   - os números por resultado, sempre **"aceita pelo servidor"** e nunca "entregue" ou "recebida";
   - "Tentar de novo as 3 falhas";
   - assunto e corpo como foram enviados;
   - autor, instante e ato citado.
4. **Modelos**: uma lista simples por unidade, com criar, editar e ativar/inativar. Não há editor
   rico.

**Prevenção do envio em massa por engano**, nesta ordem de eficácia:

- não há botão sem ato;
- não há destinatário que o ato não traga;
- o número aparece no botão;
- a prévia com pessoa real;
- a assinatura do alcance;
- o segundo aviso exige justificativa.

Não se recomenda digitar o número para confirmar nem aprovação por segunda pessoa no MVP. O dano de
um aviso complementar enviado por engano se corrige com outro aviso. O dano de um ato publicado por
engano não se corrige, e é ali que a segregação já existe.

---

## F. Modelos de mensagem

Variáveis admitidas (lista fechada, todas resolvidas pelo sistema):

| Variável | Valor |
|---|---|
| `{nome_do_candidato}` | nome da identidade, ou o da inscrição |
| `{edital}` | "Edital nº 57/2026" |
| `{processo_seletivo}` | título do Processo |
| `{perfil}` | nome do Perfil de vaga |
| `{etapa}` | Etapa do marco (resultado) |
| `{natureza_do_resultado}` | "preliminar" ou "definitivo" |
| `{data_da_publicacao}` | data e hora do ato, no fuso da instalação |
| `{link_da_publicacao}` | URL pública do ato (`selecoes/resultados/<id>/`) ou a referência declarada |
| `{area_do_candidato}` | URL do portal, **sem token**: a entrada continua por código (P-001) |

O nome da lista ("Pretos, pardos e indígenas") **não** é variável. Ver H.4.

Rodapé fixo, igual em todos:

```
A publicação oficial está em {link_da_publicacao} e é a referência para prazos e
resultados, conforme o {edital}. Este aviso não substitui a publicação.
Em caso de dúvida, fale com {atendimento}.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
```

**1. Divulgação de resultado (Cenário D)**

```
Assunto: {edital} — resultado {natureza_do_resultado} publicado

Olá, {nome_do_candidato}.

Foi publicado em {data_da_publicacao} o resultado {natureza_do_resultado} da etapa
{etapa}, do {perfil}.

Para ver a sua situação, entre na área do candidato:
{area_do_candidato}

Se o Edital prevê recurso contra este resultado, o prazo e a forma estão na
publicação.
```

*Sem a situação no corpo, de propósito.* O e-mail é encaminhado, lido em tela compartilhada e
guardado em caixa que não é só da pessoa. A situação está no portal, que autentica.

**2. Convocação para verificação da autodeclaração — PPI (Cenário A, quando houver ato)**

```
Assunto: {edital} — convocação publicada

Olá, {nome_do_candidato}.

Foi publicada em {data_da_publicacao} uma convocação do {perfil} que inclui a
sua inscrição, para o procedimento de verificação complementar previsto no
Edital.

A data, o horário, a forma de participação e os documentos exigidos estão na
publicação oficial. Leia com antecedência: a ausência pode ter consequência
prevista no Edital.
```

*Assunto neutro, de propósito.* "Heteroidentificação" no assunto revela, na notificação do celular,
que a pessoa se autodeclarou preta, parda ou indígena. A seleção pode nomear o procedimento no
corpo, se decidir (H.4).

**3. Chamada de suplentes (Cenário C, Perfil que convoca por publicação)**

```
Assunto: {edital} — nova chamada publicada

Olá, {nome_do_candidato}.

Foi publicada em {data_da_publicacao} uma nova chamada do {perfil}, e a sua
inscrição está entre as convocadas.

O que fazer e até quando estão na publicação oficial. O prazo corre conforme o
Edital, a partir da publicação, e não do recebimento deste aviso.

Acompanhe também pela área do candidato: {area_do_candidato}
```

*"E não do recebimento deste aviso"* é a frase que impede o e-mail complementar de ser lido como o
ato. No Perfil `INDIVIDUAL_MESSAGE` este modelo não se aplica: ali a mensagem formal já existe e é
ela que conta.

---

## G. Priorização

**Essencial para o MVP**

- Revisão escrita da `FR-084` da `010` e da exclusão da `017`, antes de qualquer código.
- `EMAIL_TIMEOUT` (gap I-4).
- Aviso ligado a resultado publicado (D), com aviso novo em retificação de resultado (E).
- Aviso ligado a chamada comunicada por publicação (C).
- Destinatários do ato, deduplicados por inscrição, sem exclusão manual (decisão de 09/10).
- Texto livre com variáveis fechadas, rodapé fixo e prévia com pessoa real.
- Modelos por unidade, com ativo e inativo, e "salvar como modelo".
- Registro append-only de aviso, destinatários e tentativas.
- Reenvio de falhas, e reenvio intencional com justificativa.
- Despacho fora da requisição (D.3, opção 1).
- Capacidade `aviso:enviar`, escopo por unidade e auditoria.

**Melhoria posterior**

- Aviso de Retificação do Edital às inscrições enviadas.
- Aviso aos participantes de uma Etapa (B), com referência externa declarada.
- Universo "apenas quem teve a situação alterada" na retificação, que é determinístico pela
  diferença entre as duas `SituacaoDivulgada`.
- Modelos padrão do sistema, versionados no código (como o `unidades.json`).
- Envio de teste para o próprio operador.
- Agendamento. Só se a seleção demonstrar um caso. O aviso segue um ato já praticado, e agendá-lo
  abre a janela "ato retificado entre o agendamento e o envio".

**Desnecessário neste momento**

- WhatsApp, SMS e push.
- Editor rico, HTML e anexos.
- Linguagem de template e condicionais.
- Segmentação por filtro livre.
- Rastreio de abertura ou clique (pixel). É vigilância que a LGPD não justifica para aviso
  complementar.
- Processamento de devolução (bounce).
- Descadastro. Aviso de ato administrativo dirigido à pessoa não é campanha, mas ver H.5.
- Modelos institucionais entre unidades. Exigiriam o papel entre unidades que a `060` recusou.
- Horário individual de entrevista.

---

## H. Decisões pendentes

Só as que exigem posição institucional ou do produto. *Em 09/10 o usuário decidiu de 1 a 4 e o 6
(tabela no topo). Do 5, a LGPD, fica a validação institucional, pendente e exigida antes de
produção.*

1. **Revisar a `FR-084` da `010` para admitir a quarta situação, o *aviso complementar ligado a ato
   publicado*.** Isso inverte a frase que hoje exclui "aviso de resultado e de retificação". Sem
   isso, nada do restante se abre.
2. **Quem envia.** As opções são:
   - (a) só o papel `publicador`, coerente com quem praticou o ato;
   - (b) também o `gestor` e a presidência da comissão, coerente com quem conduz a convocação;
   - (c) uma capacidade própria, atribuída caso a caso.

   A recomendação técnica é (c), com `aviso:enviar` atribuída de início ao `publicador`. Com
   equipe de 2–3 pessoas acumulando papéis, a diferença prática é pequena, mas a separação fica
   pronta.
3. **Processo de despacho em segundo plano (D.3).** É um processo novo em produção: um timer a mais
   e um comando. O Princípio V pede que a necessidade fique escrita na spec.
4. **O nome da modalidade no aviso.** Exemplos: "lista PPI" e "verificação da autodeclaração". É a
   mesma questão de governança que a `063` deixou fora (`specs/063-acompanhamento-pela-situacao/spec.md:81-83`)
   e que a pesquisa marcou como aberta. A recomendação é que não seja variável e que o assunto seja
   neutro.
5. **LGPD.** Duas confirmações com o encarregado de dados, que esta auditoria **não** presume:
   - a base legal do tratamento do e-mail para aviso complementar, que é finalidade diferente da
     autenticação para a qual a pessoa o informou;
   - a retenção da lista de destinatários. A política de retenção já é pré-condição pendente do
     piloto (`specs/010-area-do-candidato/spec.md:68-71`).

   Se a base legal exigir oposição, o descadastro sai de "desnecessário".
6. **O universo padrão do aviso de resultado.** São três opções: *considerados* (recomendado),
   *classificados* ou *todos os inscritos do Edital*.

---

## I. Recomendação final

1. **Deve ser implementada?** Sim, com a ressalva do item 1 de H. A demanda é concreta, os Editais
   já tratam o e-mail como canal complementar (77, 9.3: o candidato deve "acompanhar seu e-mail"; 90,
   11.6: acompanhar "as publicações na página do Cefor"), e o sistema já tem a lista exata de quem
   cada resultado alcança.
2. **A menor solução que atende:** um botão "Avisar candidatos" na publicação vigente e na chamada
   comunicada por publicação. Os destinatários saem do ato. O texto da seleção leva variáveis
   fechadas e rodapé fixo, os modelos ficam por unidade e o registro é append-only. O envio é
   despachado fora da requisição.
3. **A melhor integração:** pela tela para onde o ato já redireciona (`publicacoes_do_marco`) e pelo
   cartão da chamada em `convocacao.html`. A prévia e a assinatura copiam `previa_de_publicacao`; o
   lote e o histórico copiam a seção "Comunicações que ainda não saíram".
4. **Atendidos já:** o resultado preliminar e o definitivo (D), a retificação de resultado (E) e a
   chamada de suplentes ou titulares em Perfil que convoca por publicação (C).
5. **Dependem de ajuste anterior:**
   - a convocação para heteroidentificação (A) depende da spec própria que a `019` e a `014`
     registraram;
   - a entrevista e a avaliação de títulos (B) dependem de decidir se convocar para Etapa vira ato,
     ou se basta o corte vigente com referência externa;
   - a Retificação do Edital depende da decisão do universo (todos os inscritos).
6. **Uma feature ou várias?**
   - **Uma governança antes:** a revisão da `FR-084`, sem código.
   - **Depois, uma feature** para o MVP. Separá-la em "modelos" e "envio" entregaria modelos sem
     uso.
   - A, B e Retificação do Edital ficam como incrementos próprios, quando seus atos existirem.
   - O `EMAIL_TIMEOUT` pode ir antes, como correção isolada, porque já protege o código de acesso.
7. **Riscos e mitigação:**

   | Risco | Mitigação |
   |---|---|
   | Aviso lido como o ato, com prazo contado do e-mail | Rodapé fixo; palavra "aviso"; frase de prazo nos modelos; tabela separada de `ComunicacaoEmitida` |
   | Envio antes da publicação | Sem ato citado, não há botão |
   | Destinatário errado | Lista só do ato, sem acréscimo nem exclusão manual; prévia com pessoa real; alcance assinado |
   | Ato muda depois do envio | Aviso antigo intacto; link antigo mostra "substituída por"; aviso novo ligado ao anterior |
   | Duplicidade | Deduplicação por inscrição; idempotência na confirmação; segundo aviso com justificativa |
   | Texto que induz a erro | Variáveis sem situação nem posição; modelos revisados pela seleção; rodapé que remete à publicação |
   | Dado sensível | Modalidade fora das variáveis; assunto neutro; uma mensagem por destinatário, sem CC ou BCC |
   | SMTP lento ou fora | `EMAIL_TIMEOUT`; despacho fora da requisição; tentativa registrada como `FALHA` e reenviável |
   | Limite da conta de envio | Lotes com limite por minuto no despacho. A conta do setor de correio precisa declarar o limite, como a §16.2 do runbook já pede para o dia de pico |
   | Desempenho | Destinatários por um `filter … in` sobre tabela indexada (`SituacaoDivulgada.inscricao`); nada roda na leitura do portal |

---

## Achado à margem — investigado em 09/10, **não confirmado**

**A hipótese era** que o reenvio da comunicação de convocação reiniciasse o prazo. Ela vinha da
leitura de `envio_de`, que toma o **maior** `enviado_em` bem-sucedido
(`convocacao/application/selectors.py:119-126`), e do botão "Emitir a comunicação de novo"
(`interface/templates/interface/convocacao.html:535`).

**Ela não se sustenta, porque o prazo não é contado a partir do envio.**

- O vencimento é uma **data absoluta**, informada ao convocar (`Convocacao.vencimento`). O sistema
  não calcula dias úteis (`convocacao/domain/prazo.py:1-16`; `019`, `R-004`).
- O envio só decide **se** o prazo corre (`prazo_corre`), e não **até quando**.
- O reenvio depois do vencimento é recusado com `vencimento_anterior_ao_envio`
  (`convocacao/application/comunicar.py:298-312`).

**Sonda executada contra PostgreSQL** (`connection.vendor == "postgresql"` conferido no próprio
teste; 3 casos, 3 passaram). Ela ficou fora do repositório, no scratchpad da sessão, e foi copiada
para `tests/integration/convocacao/` só durante a execução. Os três cenários:

1. **Enviar e reenviar dentro do prazo.**
   - Duas `ComunicacaoEmitida` `ENVIADA`.
   - O `vencimento` ficou idêntico.
   - O `envio_de` passou a ser o do segundo envio.
   - Com `agora` um minuto depois do vencimento, o estado é `CONVOCADO_VENCIMENTO_DECORRIDO`.
   - As duas mensagens trazem a mesma data-limite.
2. **Reenviar depois do vencimento.** A emissão foi recusada com `vencimento_anterior_ao_envio`, e
   nada foi enviado. O não atendimento continuou registrável.
3. **Reenviar no último dia, antes do vencimento.** O não atendimento foi aceito cinco minutos depois
   do vencimento original: o reenvio não empurrou a porta para depois.

**Incorporada à suíte** depois da revisão do usuário: a sonda virou
`backend/tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py`, numa alteração isolada
(branch `claude/teste-reenvio-nao-reinicia-prazo`), sem mudar regra. Os resíduos abaixo têm registro
próprio em `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`, na mesma branch.

**Dois resíduos observados**, que não são reinício de prazo. Ficam para decisão do usuário, e
nenhum entra na feature de avisos.

- **A redação do reenvio.** O corpo diz *"Prazo para atender: até 11/10/2026 às 10:19, contado do
  envio desta mensagem"* (`comunicar.py:57`). A data é a original, mas a cláusula "contado do envio
  desta mensagem", lida num reenvio, sugere que o prazo recomeçou. É texto, não regra.
- **O "enviada em" exibido é o do último envio**, na gestão (`convocacao.html:403`) e no portal
  (`portal/templates/portal/_convocacao_da_inscricao.html:22`). Quem consulta o cartão não vê,
  ali, quando a primeira mensagem saiu. O histórico tem todas.

**De passagem, e só por leitura:** o vencimento é informado **ao convocar**, antes do envio. Se o
envio falha e só tem sucesso dias depois, a janela efetiva da pessoa encolhe. A única recusa é a do
vencimento já passado (`FR-269b`). O caminho previsto é suceder a convocação com vencimento novo
(`comunicar.py:309-310`), mas nada avisa o operador de que o envio tardio encurtou o prazo. Não foi
testado.
