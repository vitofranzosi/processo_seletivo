# SPEC 010 — Área do Candidato e Acesso sem Senha

**Input para `/speckit-specify`.** Redação consolidada após avaliação da proposta original verificada
contra o repositório em `55caa29`, com a `009` já mergeada (`a872b54`).

## 1. Visão

Permitir que o candidato possua uma área pessoal persistente na qual consiga:

> **entrar sem senha → reencontrar suas inscrições → continuar rascunhos → conferir exatamente o que
> submeteu → visualizar/baixar seus documentos e comprovantes → acompanhar o Processo Seletivo**

sem procurar novamente o certame no site e sem criar uma conta convencional com senha.

A autenticação V1 é:

> **e-mail → código de uso único → sessão autenticada**

A feature **substitui o provedor de identidade de demonstração** previsto pela 009. Ela não reabre a
jornada de inscrição já entregue.

---

## 2. A frase que governa esta feature

> **O candidato deve conseguir entrar sem senha, reencontrar tudo o que já submeteu e entender o que
> está acontecendo em suas seleções sem redigitação desnecessária, sem procurar novamente o certame
> fora de sua área pessoal e sem reduzir a proteção dos seus dados e documentos.**

E a contrapartida, que tem o mesmo peso:

> **Nenhuma inscrição já submetida muda de dono porque a 010 foi implantada, e nenhum acesso é
> concedido por afirmação — só por prova.**

---

## 3. Precondições e o que a 010 destrava

**PC-001** — A `009 — Inscrição simples e documentos do candidato` está mergeada, com requisitos,
testes e rastreabilidade pós-demonstração fechados.

**PC-002** — A 010 consome, e não redefine: `Inscricao` e seus estados, titularidade pelo `subject`,
`DocumentoExigido`, `DocumentoSubmetido`, comprovante, versão consolidada aceita, armazenamento
privado e regras de submissão.

**PC-003 — O que a 010 destrava, e que precisa ser dito de frente.** Hoje o portal do candidato
**não sobe em produção**: `config/settings/production.py` recusa a inicialização com
`PORTAL_IDENTIDADE_DEMO` ligado, e sem ele a tela de identificação devolve 404. A 010 é a feature
que remove esse impedimento — e por isso é ela que herda a responsabilidade de não reintroduzir, por
outro caminho, o que aquela guarda proíbe. Toda decisão desta spec que parece rigorosa demais existe
porque, ao fim dela, o portal passa a ser implantável.

**PC-004 — E o que ela não destrava.** A área do candidato não entra em produção com dados reais
enquanto não existir política institucional documentada de retenção e descarte dos dados pessoais
pertinentes. A 010 registra esse gate; não inventa prazo jurídico nem implementa descarte
arbitrário. As duas afirmações convivem: a 010 remove o impedimento **técnico** e mantém o
impedimento **institucional**.

---

## 4. Problema

A 009 permite que uma pessoa se identifique e realize uma inscrição, mas não existe identidade
persistida de candidato. No estado atual:

- o `subject` é produzido pelo provedor de demonstração e deriva do CPF por
  `HMAC(SECRET_KEY, CPF)` (`portal/identidade.py`);
- quem se identifica **declara** nome, CPF e e-mail, e nada verifica a declaração;
- o e-mail está gravado na própria Inscrição, e não existe associação persistente
  `e-mail verificado → candidato`;
- não existe área "Minhas inscrições".

Consequências: ninguém retorna meses depois, ninguém reencontra o que enviou, ninguém troca o e-mail
de contato, e o portal inteiro é indisponível em produção.

**E uma consequência que ainda não doeu.** Como o `subject` histórico deriva da `SECRET_KEY`, a
propriedade de toda inscrição já submetida é hoje refém da rotação de um segredo de aplicação.
Rotacionar a chave hoje tornaria cada inscrição da 009 inalcançável pelo seu titular, em silêncio. A
010 não pode herdar essa dependência — e, como o §7 detalha, é ela que a encerra.

---

## 5. Princípios desta feature

### P-001 — Sem senha
A V1 não tem criação, confirmação, recuperação nem política de complexidade de senha. Controle do
e-mail é provado por código temporário. Também não tem *magic link*: um link que autentica viaja no
histórico do navegador, no encaminhamento do e-mail e no `Referer`. O código é digitado.

### P-002 — E-mail é credencial, não identidade
Trocar de e-mail não cria uma pessoa nova. Uma mesma Identidade de Candidato pode ter vários e-mails
verificados.

### P-003 — CPF não é credencial
Conhecer um CPF não prova nada: ele está em contrato, em crachá, em vazamento. **CPF nunca concede
acesso, nunca cria vínculo por afirmação e nunca é pedido no login recorrente.** Ele é usado em um
único lugar — para confirmar uma correspondência histórica que o sistema já encontrou por outro
caminho.

### P-004 — Segurança não se obtém por burocracia
O fluxo normal é curto. Casos excepcionais podem exigir tratamento diferente, mas não transformam
todo login em "e-mail + CPF + dados pessoais + código".

### P-005 — Dados históricos não são reescritos
Adicionar credencial não altera o e-mail que consta de uma Inscrição submetida. O sistema continua
podendo dizer: *"esta foi a informação efetivamente submetida naquele ato."*

### P-006 — O candidato não é ator institucional
A Identidade do Candidato não entra em `PAPEIS`, comissão, permissão `edital:*` nem Django Group. É
um segundo eixo de identidade, como a 009 já decidiu.

### P-007 — Nenhum vínculo nasce de afirmação
Todo vínculo entre credencial e identidade nasce de prova de controle de e-mail somada, quando há
patrimônio histórico em jogo, a uma confirmação. Um vínculo que se cria só porque alguém digitou um
dado é um vínculo que qualquer pessoa cria.

### P-008 — O contrato da 009 permanece; muda quem o preenche
`IdentidadeDoCandidato(subject, nome, cpf, email)` continua sendo o que a abertura de rascunho
consome (`inscricoes/application/rascunho.py`). A 010 troca **a origem** desses campos — do
formulário declarado para a identidade persistida — e não a jornada que os usa.

---

## 6. Conceitos mínimos

### Identidade do Candidato

```text
CandidateIdentity
- id
- subject            # opaco, estável, próprio da identidade
- nome               # núcleo mínimo exigido pela Inscrição
- cpf_normalizado    # declarado pelo titular; nunca decide propriedade nem acesso
- created_at
```

**FR-001** — `subject` é único e estável, e é o único campo que decide propriedade de Inscrição.

**FR-002** — Para identidades novas, `subject` é um identificador opaco próprio da identidade, que
**não deriva da `SECRET_KEY` nem de qualquer dado pessoal**, e usa prefixo distinto do `demo:`
legado, de modo que os dois conjuntos jamais se confundam.

**FR-003** — CPF não aparece em URL, e não é duplicado em logs ou auditoria.

**FR-004 — O núcleo mínimo, e o motivo dele.** A identidade carrega `nome` e `cpf_normalizado`
porque a Inscrição os exige: hoje `abrir_inscricao` os copia da identidade
(`rascunho.py`), e o `nome` vai no comprovante — é por ele que a comissão confere o documento
apresentado. Trocar o provedor por um que só entrega e-mail, sem isto, quebraria a jornada da 009 na
primeira inscrição de todo candidato novo. Dois campos exigidos por um ato administrativo existente
não são "perfil cadastral": o Out of Scope do §21 continua valendo integralmente.

**FR-005** — `nome` e `cpf_normalizado` são pedidos **uma única vez**, no primeiro rascunho, e
reusados em todas as inscrições seguintes daquela identidade. Quem veio da 009 nunca os informa: a
migração do §7 já os trouxe.

**FR-005a — Uma regra só para os três campos do núcleo.** `nome`, `cpf_normalizado` e o e-mail
principal (FR-008b) alimentam a Inscrição. Enquanto ela for **rascunho**, acompanham a identidade:
corrigir o nome corrige os rascunhos abertos. Na **submissão**, congelam — o que foi submetido é o
que constava naquele ato, e nenhuma correção posterior o alcança (P-005).

Sem esta regra, um campo seguiria a identidade e outro não, e a diferença só apareceria no
comprovante de alguém.

**FR-006** — CPF informado é validado (dígitos verificadores), como a 009 já valida. E a validação
prova apenas que o número é um CPF possível — o próprio domínio já diz isso
(`inscricoes/domain/pessoais.py`). Ela **não** prova titularidade, e nada nesta spec a trata como se
provasse.

**FR-007 — Pedido uma vez não é imutável para sempre.** Erro de digitação, alteração de nome e
correção de cadastro são eventos normais, e a 009 hoje permite redigitar ambos a cada identificação:
uma identidade persistente não pode ser mais rígida do que o estado que ela substitui.

- **Nome** é editável pelo titular a qualquer momento. Ele não decide propriedade — quem decide é o
  `subject` — e o que já foi submetido não muda (P-005).
- **CPF** é corrigível pelo titular enquanto a identidade não tiver nenhuma inscrição **submetida**.
  A partir da primeira submissão ele é peça de ato administrativo e congela; corrigi-lo passa a ser
  ato institucional, fora desta feature.

### E-mails verificados

```text
CandidateEmail
- candidate_identity
- email_canonico      # único no sistema, por constraint de banco
- email_como_informado
- principal           # o que alimenta a Inscrição; um por identidade
- verified_at
- created_at
```

**FR-008** — Uma identidade pode ter vários e-mails verificados, e um endereço canônico pertence a
no máximo uma identidade — **garantido por constraint de banco**, e não por consulta prévia. FR-049
implementada como verificação antes da escrita perde a corrida entre duas confirmações simultâneas,
e o que se perde nessa corrida é a exclusividade de uma credencial.

**FR-008a — Normalização conservadora.** O endereço canônico é o endereço em minúsculas, com o
domínio em forma canônica. **Não** se removem pontos, não se corta sufixo `+alias` e não se aplica
nenhuma regra específica de provedor: essas equivalências valem no Gmail e são falsas em outros
servidores, e fundir dois endereços distintos numa credencial só é indistinguível de takeover depois
que já aconteceu. O endereço como a pessoa informou é preservado para exibição, e nunca decide
identidade.

*A suposição que isto embute, declarada.* A RFC torna a parte anterior ao `@` sensível a caixa, e
baixá-la é, a rigor, uma equivalência que o padrão não garante. A aplicação **assume a parte local
insensível a caixa**, porque nenhum provedor em uso prático distingue `Maria@` de `maria@`, e tratá-
las como credenciais distintas multiplicaria identidades por erro de digitação — um problema
frequente trocado por um problema teórico. Fica registrado como suposição, e não como fato.

**FR-008b — Qual endereço vira `Inscricao.email`.** A identidade tem **um e-mail principal**,
escolhido pelo titular, e é ele que preenche a Inscrição pela regra da FR-005a. O primeiro endereço
verificado é o principal por padrão; adicionar outro não muda essa escolha sozinho.

*Por que explícito, e não derivado.* "O endereço da sessão atual" faria a mesma pessoa constar de
duas inscrições com contatos diferentes conforme a caixa que ela abriu naquele dia; "o mais recente"
mudaria o contato de um certame em andamento por causa de uma credencial adicionada para outro fim.
O campo é o registro de um ato administrativo: quem escolhe é o titular, uma vez, e a escolha fica
visível.

**FR-008c** — Remover o e-mail principal exige que outro assuma o lugar; a identidade nunca fica sem
principal enquanto tiver credencial (FR-051).

**FR-009** — E-mail que consta de uma Inscrição histórica **não** é verificado por ter sido digitado.
Só o desafio da 010 prova controle.

### Desafio de acesso

```text
DesafioDeAcesso
- email_canonico
- finalidade          # entrar | adicionar credencial
- codigo_hash
- expira_em
- tentativas
- consumido_em
- criado_em
```

**FR-010** — O desafio é **persistido em banco**, e não em cache. `CACHES` não está configurado no
projeto: o padrão do Django é `LocMemCache`, por processo — limites de tentativa e de reenvio
guardados ali seriam contornáveis com mais de um worker, e a spec estaria pedindo uma proteção que a
implantação não teria.

## 7. A implantação reconcilia — o primeiro login não

Esta é a decisão estrutural da feature.

A reconciliação com os dados da 009 acontece **por migração de dados, na implantação**, e não sob
demanda no primeiro login.

**FR-011** — A implantação da 010 materializa, a partir das `Inscricao` existentes, uma
`CandidateIdentity` para cada `cpf_normalizado`, com o **mesmo `identity_subject`** que aquelas
inscrições já carregam, e com o `nome` da inscrição mais recente do grupo.

**FR-012** — A migração **não reescreve nenhum `Inscricao.identity_subject`**. Em hipótese alguma.
Ela copia; nunca atribui.

**FR-013** — A migração **não marca e-mail algum como verificado**. Os e-mails históricos ficam
disponíveis apenas como *correspondência histórica* (§9), e a verificação continua sendo o desafio.

**FR-014** — Um `cpf_normalizado` que apareça em inscrições com mais de um `identity_subject`
distinto — situação possível apenas se a `SECRET_KEY` tiver rotacionado durante a vigência da 009 —
**não gera identidade** e é relatado na saída da migração, para tratamento operacional. Falhar aqui é
falhar onde alguém está olhando.

**FR-015 — CPF inválido separa dois destinos, e um deles é parar.**

- **Rascunho** sem `cpf_normalizado`, ou com CPF que não passa na validação de dígitos, é relatado,
  fica **intacto** e não é reconciliado.
- **Inscrição submetida** nessa condição **aborta a migração**, com relatório do que a impediu.

*Por que abortar.* A FR-042 instala uma check constraint que exige CPF válido em toda submetida. Uma
submetida inválida no banco torna a constraint impossível de instalar — e o único jeito de seguir
seria a migração escolher um dado por conta própria, que é exatamente o que a FR-015a proíbe. Parar
com relatório é o que mantém a `SC-010` verdadeira para o banco inteiro, e não só para as linhas que
a migração conseguiu ler.

Pelo caminho normal da 009 isso não existe: a identificação valida os dígitos antes de gravar. Existe
em base de demonstração e em carga manual — e abortar com relatório é mais barato que falhar no
`ALTER TABLE`.

**FR-015a — O que acontece com as inscrições de um grupo não reconciliado: nada.** Elas
mantêm seu `identity_subject`, ninguém muda de dono, nenhum dado é escolhido arbitrariamente
para desempatar, e elas ficam inalcançáveis pela área do candidato até tratamento operacional.
Esse é o estado persistente, e ele não exige coluna nova nem fluxo de revisão: a condição
que o produz — rotação da `SECRET_KEY` durante a vigência da 009 — só é possível onde a 009
rodou, e a guarda do PC-003 impediu que ela rodasse em produção.

**Por que na migração, e não no login.** Enquanto o candidato não voltar, o `subject` dele continua
sendo `HMAC(SECRET_KEY, CPF)`. Se a chave rotacionar antes do primeiro login, aquele CPF passa a
gerar outro `subject`, a reconciliação não encontra mais nada, e o titular perde o acesso ao que
submeteu — permanentemente, porque o §19 põe recuperação fora de escopo. Materializar na implantação
congela o mapeamento no instante em que o segredo ainda é o mesmo. O ganho colateral é maior que o
principal: o "Cenário B" desaparece do fluxo de login, e a ambiguidade passa a ser tratada em lote,
por quem administra, e não na tela de um candidato às 23h.

**FR-016 — Aposentadoria do provedor de demonstração.** Concluída a migração, a identificação por
declaração da 009 deixa de ser um caminho de autenticação. Se ela permanecer no código para
desenvolvimento, a guarda de produção que hoje recusa `PORTAL_IDENTIDADE_DEMO` **permanece** — a 010
não a afrouxa, não a contorna e não abre atalho equivalente.

---

## 8. O canal de e-mail que a 010 inaugura

O projeto **não tem infraestrutura de e-mail**: não há nenhuma configuração `EMAIL_*` em
`config/settings/`, e a 009 pôs comunicação explicitamente fora de escopo. Um OTP por e-mail não é
uma feature que usa um canal existente: é a feature que **inaugura o canal**. Ignorar isso é a
diferença entre uma spec e um relatório de erro em produção.

**FR-017** — O backend de envio e o remetente são configuráveis por ambiente, com console em
desenvolvimento.

**FR-018 — A guarda recusa o que sabe não entregar.** Em produção, a inicialização é recusada — na
mesma forma das guardas já existentes em `production.py` — quando o backend configurado é um dos
**conhecidos por não entregar** (console, dummy, locmem, filebased e o que nascer ao lado deles) ou
quando não há remetente definido.

O alcance dessa guarda é o mesmo que `production.py` já declara sobre a autenticação institucional,
e a redação segue essa honestidade: ela **recusa o que sabe ser inútil**, e **não prova** que um SMTP
configurado entregue mensagem alguma. Nenhuma verificação de inicialização pode provar isso. O que
ela impede é subir imprimindo o código de acesso no log — autenticação sem prova nenhuma, com
aparência de autenticação.

**FR-019** — A mensagem contém o código, o prazo de validade e a orientação de ignorar se não foi a
pessoa que solicitou. Não contém link que autentica (P-001), não contém CPF e não contém dado da
inscrição.

**FR-020** — Falha de envio produz mensagem neutra ao visitante, idêntica à do caminho feliz, e
registro técnico do lado do servidor. O visitante nunca descobre pela falha se o endereço existia.

**FR-021** — Nada além do desafio. A 010 **não** acrescenta comprovante por e-mail, aviso de
Retificação, aviso de resultado, lembrete, campanha ou newsletter. O canal passar a existir não torna
comunicação transacional escopo implícito — e esta frase está aqui exatamente porque, a partir da
010, a objeção "não temos como enviar e-mail" deixa de existir.

## 9. US1 — Entrar sem senha *(P1)*

Como candidato, quero entrar usando um código recebido por e-mail para não precisar criar nem
lembrar uma senha.

```text
Informe seu e-mail
        ↓
Receber código
        ↓
Informe o código
        ↓
Minhas inscrições
```

**Acceptance Scenario** — **Given** um e-mail já verificado e associado a uma identidade **When** o
candidato informa o e-mail e valida corretamente o código **Then** o sistema cria a sessão daquela
identidade e o leva a `Minhas inscrições`, sem passo intermediário.

### O desafio

**FR-022** — A resposta à solicitação é equivalente exista ou não identidade associada ao e-mail:
*"Se este endereço puder ser utilizado, enviaremos um código de acesso."* Nunca "conta não
encontrada".

**FR-023 — A equivalência inclui o reenvio.** A janela de reenvio, a contagem de limite e o texto de
espera são os mesmos para endereço com e sem identidade. Um contador que só avança para endereços
existentes é canal lateral que anula a FR-022 inteira.

*O que a equivalência não alcança, e a spec assume.* Tempo de resposta não é indistinguível: enviar
e-mail tem latência variável, e igualá-la exigiria fila e worker — infraestrutura que esta feature
não tem e que não se justifica pelo ganho. Resposta e janela idênticas bastam para a V1.

**FR-024** — Código numérico e curto, adequado à digitação manual. V1: 6 dígitos.

**FR-024a** — O código é gerado por fonte criptograficamente segura, com distribuição uniforme sobre
todo o intervalo. Seis dígitos só valem 10⁶ tentativas contra quem os adivinha às cegas se forem
mesmo 10⁶: gerador previsível reduz o espaço sem que nada na tela mude.

**FR-025** — Expira em 10 minutos, por instante absoluto gravado no desafio.

**FR-026** — Uso único.

**FR-026a** — O consumo é **atômico**: a mesma linha não pode ser consumida por duas requisições
simultâneas, e a marcação de consumo acontece na mesma operação que reconhece o código como válido.
"Uso único" verificado em leitura e gravado depois é uso único que duas abas quebram.

**FR-027** — Novo código invalida os anteriores ainda utilizáveis daquele endereço.

**FR-028** — Nunca persistido em texto claro; usa primitiva segura já disponível na plataforma.

**FR-028a** — O desafio vale para **um endereço canônico e uma finalidade**. Código pedido para
entrar não confirma a adição de credencial, e vice-versa: um desafio que serve para duas coisas é um
desafio que a pessoa pode ser induzida a resolver para a errada.

**FR-029** — Limite de tentativas de validação por desafio. V1: 5.

**FR-030** — Limite de solicitações repetidas por endereço e por origem. Valores são constantes da
aplicação, não configuração de usuário. **Não** existe limite global de envio: teto global
transforma abuso distribuído em negação de serviço para todos os candidatos, no dia em que ela mais
custa — o último do prazo.

**FR-031** — Esgotado o limite, o desafio morre e a mensagem não distingue "código errado" de
"endereço inexistente".

### Sessão

**FR-032** — Autenticado, não se pede novo código a cada página.

**FR-032a** — O identificador de sessão é **rotacionado no instante da autenticação**. Sem isso,
quem induzir a vítima a usar uma sessão conhecida antes do login continua dentro dela depois — a
fixação de sessão contorna o desafio inteiro sem tocar nele.

**FR-033** — Sessão expirada exige novo desafio.

**FR-034** — Sem "lembrar de mim" permanente nesta versão.

**FR-035** — Sair encerra a sessão do candidato, e apenas a dele.

## 10. US2 — A primeira associação *(P1)*

Depois de validar o código, o sistema decide a qual identidade aquele e-mail pertence. **O CPF não
participa dessa decisão; ele apenas confirma uma correspondência que o sistema já encontrou por
outro caminho.**

```text
e-mail → código válido
   │
   ├─ e-mail já verificado ───────────────────────────────────► entra
   │
   ├─ e-mail consta de inscrições de identidade(s) legada(s)
   │        │
   │        ├─ confirma o CPF agora ───────────────────────────► reconcilia e entra
   │        │
   │        └─ recusa, erra ou esgota ───────────────────────► entra em identidade
   │                                                             própria; retomável
   │                                                             enquanto ela estiver vazia
   │
   └─ nenhuma correspondência histórica ─────────────────────► cria identidade
                                                                sem CPF e entra
                                                                (área vazia)
```

**FR-036 — Candidato novo não informa CPF.** Quando o endereço provado não tem correspondência
histórica alguma, cria-se a identidade **sem CPF**, e a pessoa entra numa área vazia.

*Por quê.* Pedir CPF aqui não localiza nada — por definição não há o que localizar — e cria um
vínculo que qualquer pessoa fabrica: bastaria conhecer o CPF alheio e provar um e-mail próprio para
ocupar aquele CPF antes do titular. Quando o titular chegasse, a recusa o deixaria permanentemente
fora do próprio documento, sem rota de recuperação. A tela que existia para proteger seria a tela que
sequestra. Removê-la elimina o ataque, remove um passo do fluxo e torna a `SC-UX-002` verdadeira
também para quem chega pela primeira vez sem participação anterior.

**FR-037 — Correspondência histórica é indício, e o convite é opcional.** Quando o endereço provado
consta de inscrições de identidade legada, oferece-se a reconciliação: *"encontramos participação
anterior associada a este endereço; confirme seu CPF para acessá-la"*, com **Confirmar agora** e
**Continuar sem isso**. Confirmado o CPF contra o `cpf_normalizado` daquela identidade — que a
migração do §7 já gravou —, o endereço passa a ser credencial verificada dela.

**Acceptance Scenario** — **Given** uma pessoa que se inscreveu pela 009 com `cpf X`, `email A` e
`subject Y` **When** ela prova o controle de `email A` e confirma `cpf X` **Then** `email A` passa a
ser credencial verificada da identidade de `subject Y`, e todas as inscrições que já pertenciam a `Y`
tornam-se imediatamente visíveis — sem que nenhuma delas tenha mudado de dono.

**FR-038** — Se o mesmo endereço constar de inscrições de identidades diferentes, o CPF desempata:
reconcilia com a identidade cujo `cpf_normalizado` confere, e com nenhuma outra.

**FR-039 — A decisão acontece antes de a identidade existir, e provar o e-mail sempre dá sessão.**
O convite é resolvido **entre o código válido e a criação do vínculo**, e não depois dele:

- **Confirmar agora**, com CPF conferido → o endereço vira credencial verificada da identidade
  legada, e a pessoa entra nela;
- **Continuar sem isso**, CPF errado ou tentativas esgotadas → cria-se uma identidade própria, o
  endereço é verificado para ela, e a pessoa entra na sua área vazia.

O limite de tentativas do §9 vale para a confirmação, e a recusa não diz de quem é o quê. Nenhum
caminho termina em beco sem saída.

**FR-040 — A retomada existe, e vale enquanto a identidade nova estiver vazia.** Quem recusou ou
errou pode reconciliar depois, de dentro da área, **enquanto a identidade nova não tiver nenhuma
inscrição — nem rascunho**. Aceita a reconciliação, o endereço migra para a identidade legada e a
identidade nova, que nada contém, é descartada.

*Por que limitada, e por que não é fusão.* Sem limite, a retomada exigiria transferir credencial de
uma identidade que já tem inscrições, abandoná-las ou fundir identidades — e a FR-041 proíbe a
terceira, a FR-012 proíbe reescrever titularidade, e a primeira é um modelo de conta com acesso a
várias identidades, que é outra feature. Com o limite, não há nada a fundir: a origem está vazia por
definição, e o que se move é uma credencial.

*E por que não encerrar de vez.* Porque o caso realista não é o ataque: é a Maria clicando em
"Continuar sem isso" sem ler. Encerrar o convite no clique põe a perda definitiva do que ela
submeteu atrás de um engano de um segundo, e ela é a usuária mais importante deste fluxo. A janela
"enquanto vazia" cobre o engano e fecha sozinha assim que a pessoa começa a usar a identidade nova.

**FR-040a — O indício não vira autoridade.** Um endereço que consta de inscrições da 009 foi apenas
**digitado** — pode ter erro, pode pertencer a terceiro, pode ter sido reciclado pelo provedor anos
depois. Ele nunca impede quem hoje controla aquela caixa de ter a própria identidade (FR-039), e a
identidade legada que ninguém reconciliou permanece intacta, com suas inscrições e seu `subject`.

*O que isto aceita, dito de frente.* Quem controla um endereço que a identidade legada usou **e**
conhece o CPF correspondente alcança aquela identidade. É a consequência direta do P-002 — e-mail é
a credencial — e o preço de não exigir prova de identidade mais forte numa V1 sem provedor
governamental.

**FR-041 — A 010 não funde identidades.** Quem tem identidade e prova um endereço novo, sem
correspondência histórica, ganha uma identidade nova e vazia. A forma de agregar credenciais é o §12,
a partir de dentro. Fusão automática por CPF é o vínculo por afirmação que o P-007 proíbe.

## 11. CPF duplicado: por que a 010 detecta e não bloqueia

Sob o provedor de demonstração, `subject = f(CPF)`. Isso significa que a constraint
`uq_inscricao_identidade_edital_perfil` impede hoje, **sem que ninguém tenha escrito a regra**, que o
mesmo CPF se inscreva duas vezes no mesmo Perfil: o mesmo CPF é sempre o mesmo `subject`.

A FR-002 desacopla identidade de CPF. Com isso o invariante desaparece — duas identidades com o
mesmo CPF produzem dois `subject`, e a constraint existente deixa passar duas inscrições da mesma
pessoa no mesmo Perfil.

**A tentação é repor o invariante como constraint. A 010 não o faz, e o motivo importa.**

Uma constraint `(edital, profile_id, cpf_normalizado)` entre submetidas transforma o certame num
modelo *primeiro a submeter vence*. Como o domínio já reconhece que validar dígitos verificadores
**não prova titularidade** (`inscricoes/domain/pessoais.py`), quem conhece o CPF alheio poderia criar
identidade com e-mail próprio, declarar aquele CPF, submeter primeiro, e fazer a inscrição legítima
colidir — no envio, com todos os documentos já enviados e o prazo correndo. O bloqueio sairia do
rascunho e reapareceria no pior instante possível, sem rota de recuperação, porque o §19 mantém a
recuperação de acesso fora da V1.

E o invariante que se compraria com esse risco **ainda não tem consumidor**: comissão, avaliação,
homologação e classificação estão fora da 009 e da 010. Ninguém hoje lê "uma inscrição por CPF por
Perfil". Pagar um lockout de prazo por uma regra que nenhuma feature consome é inverter a ordem dos
custos.

**FR-042 — Submetida exige CPF.** Uma inscrição no estado `SUBMETIDA` tem `cpf_normalizado` não
vazio e válido, garantido por check constraint, no mesmo bloco que já exige instante, protocolo,
versão aceita e aceite das declarações. Sem isso, qualquer regra condicional sobre CPF passa a
produzir comportamento acidental para o valor vazio.

**FR-043 — Duplicidade não bloqueia o envio.** Duas inscrições submetidas com o mesmo
`cpf_normalizado` no mesmo Perfil são aceitas pelo sistema. Nenhum candidato é recusado no envio por
causa de um CPF que outra identidade declarou.

**FR-044 — Duplicidade é marcada, não apenas "visível".** A consulta administrativa entregue pela
009 **assinala** as inscrições que compartilham `cpf_normalizado` dentro do mesmo Perfil. Um
marcador calculado no servidor, e nada além disso — nem painel, nem relatório, nem fluxo.

*Por que não bastava dizer "é visível".* A listagem exibe o CPF mascarado — `***.456.789-**`, seis
dígitos do meio (`inscricoes/domain/pessoais.py`). Comparar máscaras a olho, numa lista, não é
detecção: duas pessoas podem coincidir nos seis dígitos exibidos, e ninguém varre uma listagem
inteira em busca de repetição. Prometer detectabilidade sem entregar a marcação é prometer nada.

O sistema não decide qual das duas vale — essa decisão é institucional, e a regra pertence à feature
que for avaliar inscrições, junto com o estado, o contraditório e o ato que a acompanham.

**FR-045 — Vincular CPF já declarado por outra identidade não é impedido**, e não concede acesso
algum a nada daquela outra. Uma pessoa que perdeu o e-mail antigo continua podendo participar de
novos certames; o que ela não recupera são os documentos anteriores.

**FR-045a** — A constraint existente `(identity_subject, edital, profile_id)`, em qualquer estado,
**permanece intacta**. Ela é o que sustenta a idempotência de abertura de rascunho, e nada nesta
feature a substitui.

## 12. Adicionar e remover e-mail

**FR-046** — Candidato autenticado pode adicionar e-mail, provando-o por desafio.

**FR-047** — Adicionar e-mail **não** pede CPF.

**FR-048** — E-mail adicionado passa a autenticar diretamente aquela identidade.

**FR-049** — Endereço que já pertence a outra identidade não pode ser adicionado, e a recusa não
revela a quem pertence. A exclusividade é imposta pela constraint da FR-008, e não por consulta
prévia: duas confirmações simultâneas do mesmo endereço não podem produzir dois vínculos.

**FR-050** — Candidato autenticado pode remover e-mail associado.

**FR-051** — O último e-mail verificado não pode ser removido: removê-lo é apagar o próprio acesso.

**FR-052** — Remover credencial não altera Inscrição alguma.

---

## 13. US3 — Minhas inscrições *(P1)*

Depois do login, a entrada padrão é **Minhas inscrições**, mais recente primeiro. Cada item mostra o
Edital, o Perfil, a situação, o protocolo quando houver, e uma ação principal.

> **Professor de Informática**
> Edital 07/2027
> Inscrição não enviada
> **Continuar inscrição**

> **Professor de Informática**
> Edital 07/2027
> ✓ Inscrição enviada
> Protocolo INS-2027-K7M4Q2PX
> **Acompanhar**

**FR-053** — `Continuar inscrição` reutiliza o rascunho e a jornada da 009. Não existe segunda
implementação do formulário.

**FR-054** — A propriedade continua sendo decidida pelo `subject`, pela função de titularidade já
entregue (`inscricoes/domain/titularidade.py`).

**FR-055** — Uma identidade jamais enxerga inscrição de outro `subject`.

**FR-056 — Estado vazio.** Sem inscrições, a área diz *"Você ainda não possui inscrições."* e oferece
**Ver processos seletivos**. Não tem aparência de erro — é o estado normal de todo candidato novo,
inclusive no minuto seguinte ao primeiro login.

---

## 14. US4 — Conferir uma inscrição submetida *(P1)*

Página **Minha inscrição**, mostrando: a oportunidade (Processo/Edital, Perfil, modalidade quando
houver); o envio (situação, protocolo, data e hora, versão normativa aceita); os dados informados; e
os documentos efetivamente submetidos.

> **Diploma de graduação**
> `diploma.pdf` · 1,8 MB
> enviado em 14/09/2027 às 21:42
> **Visualizar** · **Baixar**

**FR-057** — O candidato acessa somente os próprios documentos.

**FR-058** — O arquivo entregue é exatamente o documento vigente na Inscrição submetida.

**FR-059** — Visualizar ou baixar não altera a Inscrição.

**FR-060** — Sem URL pública previsível; reutiliza o armazenamento privado e a autorização da 009.

**FR-061** — Os mecanismos de integridade existentes permanecem intactos: SHA-256 dos anexos, código
de verificação e SHA-256 do comprovante quando já produzido.

**FR-062** — A tela não transforma hashes em protagonista; pode oferecê-los sob **Ver dados de
integridade**.

**FR-063** — `Baixar comprovante` devolve o comprovante já produzido pela 009. Não existe segunda
modalidade de comprovante.

**FR-064** — A 010 não edita inscrição submetida, não substitui nem exclui documento submetido e não
cancela. Ela oferece consulta e acompanhamento; Retificação da inscrição é outra jornada.

---

## 15. US5 — Acompanhar a participação *(P1)*

A página responde *"o que já aconteceu e o que vem agora?"* sem inventar estados que features futuras
ainda não produzem, em duas linhas de informação claramente distintas.

**Sua participação** — fatos da Inscrição:

> ✓ Inscrição enviada — 14/09/2027 às 21:42

**Cronograma do Processo** — derivado da versão consolidada vigente:

> ✓ Período de inscrições — 01–20/09
> **Prova didática — 05/10 às 14h**
> Resultado preliminar — 08/10
> Recursos — 09–10/10

**FR-065** — Evento geral e situação pessoal são visualmente distinguíveis. O sistema não afirma
*"sua análise de títulos foi concluída"* porque o Cronograma institucional chegou à data final da
Etapa.

**FR-066 — Edital atualizado depois da inscrição.** Se a versão vigente difere da versão aceita,
mostra-se *"Este Edital foi atualizado após sua inscrição"*, com acesso ao Edital vigente e à versão
aceita quando o mecanismo atual a disponibiliza.

**FR-067** — A versão aceita não é modificada silenciosamente.

**FR-068** — A Inscrição não é reaberta nem reenviada automaticamente.

---

## 16. Experiência

**UX-001** — Login recorrente exige apenas e-mail + código.

**UX-002** — CPF aparece só no convite de reconciliação histórica (FR-037), que é opcional e
recusável, e nunca no login recorrente.

**UX-003** — Código válido leva a `Minhas inscrições` sem passo intermediário no acesso recorrente
e no primeiro acesso de quem não tem participação anterior (FR-036). Quem **tem** participação
anterior vê um passo, e apenas um: o convite de reconciliação, que é recusável (FR-037).

**UX-004** — Nenhum dado da Inscrição precisa ser redigitado para consultá-la.

**UX-005** — Nome e CPF são pedidos uma vez, e nunca a quem veio da 009. Pedido uma vez não é
irrevogável: o titular corrige o nome sempre, e o CPF enquanto não houver inscrição submetida
(FR-007).

**UX-006** — Mobile 375 px sem rolagem horizontal.

**UX-007** — Todo fluxo principal é concluível apenas pelo teclado.

**UX-008** — O código pode ser colado inteiro.

**UX-009** — O campo do código aceita digitação natural, sem obrigar a navegar entre seis campos
independentes. Um controle lógico único, ainda que a apresentação tenha separadores.

**UX-010** — Reenviar é ação clara e informa quando a próxima tentativa é possível — nos termos da
FR-023.

**UX-011** — Erro no código não apaga o e-mail informado nem obriga a reiniciar o fluxo.

**UX-012** — Mensagens de segurança não expõem detalhe interno de identidade.

---

## 17. Segurança

**FR-069** — Sessão de candidato e sessão de ator institucional são contextos distintos, com chaves
de sessão próprias, como a 009 estabeleceu.

**FR-070** — Sessão de candidato não concede permissão institucional alguma.

**FR-071** — Toda consulta a Inscrição ou Documento verifica titularidade no servidor. Não se confia
em id oculto, botão escondido ou URL difícil de adivinhar.

**FR-072** — Tentativa de acessar objeto de outro candidato responde de forma que não permita
enumerar — 404, conforme a convenção já adotada.

**FR-073** — Nenhum caminho da 010 concede acesso a partir de dado que a pessoa apenas **declara**.

---

## 18. Auditoria

Um código inválido não é ato de negócio e não vira `RegistroAuditoria`. Registram-se, como segurança
técnica: tentativas excessivas, bloqueios e autenticação bem-sucedida quando operacionalmente
necessário — **sem** código, sem CPF completo e sem conteúdo de documento.

**FR-074** — Associação e remoção de e-mail são eventos auditáveis na trilha existente. Não se cria
trilha paralela.

**FR-075 — E o encaixe não é gratuito.** `RegistroAuditoria` exige `permission` e
`institution_scope`, e a 009 preenche os dois nos atos do candidato porque toda inscrição pertence a
um Edital. Associar credencial não pertence a Edital nenhum: o escopo fica vazio, e a consulta
administrativa que filtra por escopo deixa de enxergar o evento. O `/plan` decide como acomodar isso
na trilha existente — e a spec exige que a decisão seja explícita, e não um campo em branco
descoberto depois.

---

## 19. Retenção e recuperação de acesso

**FR-076** — Desafios expirados não são dado permanente de domínio; a implementação permite limpeza
operacional.

**FR-077** — A 010 não decide prazo institucional de retenção e não cria rotina de deleção com prazo
inventado (ver PC-004).

**FR-078 — Recuperação de acesso está fora da V1, e o caminho que existe é institucional.** Quem
perdeu todos os e-mails associados e possui identidade existente precisa de prova mais forte que CPF
conhecido. A 010 **não** cria perguntas secretas, data de nascimento + CPF, envio de documento para
suporte nem GOV.BR improvisado.

O que ela faz é **nomear o caminho que já existe** em vez de fingir que não há nenhum: a equipe
enxerga as inscrições pela consulta administrativa entregue pela 009 e resolve o caso fora da
aplicação, com a conferência documental que o balcão institucional já pratica. A mensagem de recusa
aponta esse procedimento, e não um beco.

Isso é gate operacional registrado — não guarda de inicialização. Bloquear o boot por ausência de
recuperação automatizada impediria a implantação de um sistema que a instituição opera
presencialmente todos os dias, e o gate de produção que realmente incide sobre dados pessoais é o
PC-004.

**FR-079** — GOV.BR está fora da 010. A arquitetura não impede outro provider no futuro, mas a 010
não cria *adapter framework* genérico, interface vazia nem botão falso. O desafio por e-mail é o
provedor real desta versão.

## 20. Invariantes de não regressão da 009

A 010 preserva: vitrine pública, jornada de inscrição, documentos exigidos, upload privado, rascunho,
revisão, submissão, idempotência, protocolo, comprovante, hashes e integridade, consulta
administrativa e titularidade pelo `subject`. A substituição do provedor de identidade é extensão
planejada da 009, não reimplementação da sua jornada.

---

## 21. Out of Scope

Desta feature inteira, e sem exceção:

- **Inscrição** — campos novos, regras documentais novas, alteração de inscrição submetida,
  cancelamento, lógica nova de protocolo.
- **Avaliação** — comissão, banca, notas, documentos para avaliador, resultados, recursos.
- **Comunicação** — qualquer e-mail que não seja o desafio de acesso; SMS, WhatsApp, push.
- **Identidade** — senha, GOV.BR, MFA adicional, recuperação por dados pessoais, diretório
  institucional, candidato como Django Group, fusão automática de identidades.
- **Portal** — perfil cadastral, endereço, avatar, preferências, caixa de mensagens, dashboard
  genérico.

> **"Área do candidato" não autoriza construir um portal genérico**, e o núcleo mínimo da FR-004 —
> dois campos que a Inscrição já exigia — não é a primeira parcela de um cadastro.

---

## 22. Success Criteria funcionais

**SC-001** — Candidato com e-mail associado entra usando apenas e-mail + código.

**SC-002** — Código expirado, reutilizado ou acima do limite de tentativas é recusado.

**SC-002a** — Duas requisições simultâneas com o mesmo código válido consomem-no uma única vez.

**SC-002b** — O identificador de sessão depois da autenticação é diferente do de antes.

**SC-003** — A implantação materializa as identidades legadas preservando o `subject`, e nenhuma
`Inscricao` tem seu `identity_subject` alterado.

**SC-004** — Grupo de CPF com mais de um `subject` histórico é relatado pela migração, não gera
identidade, e suas inscrições permanecem intactas e sem novo dono.

**SC-004a** — Uma inscrição submetida com CPF vazio ou inválido aborta a migração com relatório; um
rascunho na mesma condição é relatado e fica intacto.

**SC-005** — Após a migração, rotacionar a `SECRET_KEY` não altera a propriedade de nenhuma inscrição
existente.

**SC-006** — Candidato novo entra sem informar CPF e chega a uma área vazia.

**SC-007** — Candidato da 009 reconcilia seu e-mail histórico confirmando o CPF, e passa a ver todas
as inscrições daquele `subject`.

**SC-007a** — Recusar o convite ou errar o CPF ainda produz sessão numa identidade própria.

**SC-007b** — A retomada da reconciliação funciona enquanto a identidade nova estiver vazia, move o
endereço, descarta a identidade vazia, e deixa de ser oferecida depois que ela tiver qualquer
inscrição.

**SC-008** — Nenhum `subject` novo depende da `SECRET_KEY`.

**SC-009** — Trocar ou adicionar credencial não altera a propriedade de nenhuma Inscrição.

**SC-010** — Uma inscrição `SUBMETIDA` sem `cpf_normalizado` válido é recusada pelo banco.

**SC-010a** — Duas inscrições submetidas com o mesmo CPF no mesmo Perfil são aceitas e aparecem
**assinaladas** como coincidência na consulta administrativa; nenhuma delas é recusada no envio.

**SC-010b** — Dois pedidos simultâneos de verificação do mesmo endereço canônico resultam em um
único vínculo, recusado pelo banco e não por consulta prévia.

**SC-011** — Nome e CPF são pedidos uma única vez e reusados nas inscrições seguintes; quem veio da
009 nunca os informa.

**SC-011a** — O titular corrige o próprio nome a qualquer momento, e o CPF enquanto não houver
inscrição submetida; o que já foi submetido não muda.

**SC-011b** — Corrigir nome, CPF ou e-mail principal atualiza os rascunhos abertos da identidade e
não altera nenhuma inscrição submetida.

**SC-011c** — `Inscricao.email` recebe o e-mail principal da identidade, e não o endereço que
autenticou a sessão.

**SC-012** — Em produção, a aplicação recusa iniciar com backend de e-mail conhecido por não entregar
ou sem remetente definido.

**SC-013** — A guarda que recusa o provedor de demonstração em produção continua ativa após a 010.

**SC-014** — `Minhas inscrições` mostra todos e somente os objetos do candidato autenticado.

**SC-015** — Rascunho é retomado pela jornada existente da 009.

**SC-016** — Inscrição submetida apresenta protocolo, dados, versão e documentos recebidos.

**SC-017** — Cada documento submetido é visualizável e baixável pelo titular.

**SC-018** — Comprovante e evidências de integridade existentes permanecem disponíveis e inalterados.

**SC-019** — O acompanhamento distingue fato pessoal de evento geral do Cronograma.

**SC-020** — Retificação posterior ao envio não altera a versão aceita pela Inscrição.

**SC-021** — Sessão de candidato não acessa nenhuma ação institucional.

**SC-022** — IDOR entre candidatos é recusado pelo servidor, com resposta que não enumera.

**SC-023** — A abertura de rascunho continua idempotente: a constraint
`(identity_subject, edital, profile_id)` segue impedindo o segundo rascunho da mesma identidade.

## 23. Success Criteria de experiência

**SC-UX-001** — Login recorrente exige no máximo: informar e-mail → informar código.

**SC-UX-002** — Código válido leva a `Minhas inscrições` imediatamente no acesso recorrente e no
primeiro acesso sem participação anterior. Com participação anterior, intercala-se exatamente um
passo — o convite da FR-037.

**SC-UX-003** — CPF não é solicitado no login recorrente, nem no primeiro acesso de candidato novo.

**SC-UX-004** — Nenhum dado ou arquivo submetido precisa ser reenviado para conferência.

**SC-UX-005** — A ação principal de cada inscrição é inequívoca: `Continuar inscrição` ou
`Acompanhar`.

**SC-UX-006** — Todo fluxo principal funciona em 375 px sem rolagem horizontal.

**SC-UX-007** — Todo fluxo principal é concluível apenas pelo teclado.

**SC-UX-008** — Erro no código não apaga o e-mail nem reinicia o fluxo.

**SC-UX-009** — Uma única tela informa quais documentos foram efetivamente submetidos.

---

## 24. Demonstração emblemática

**Preparação, pela 009.** Edital 07/2027, Perfil Professor de Informática. Maria se inscreveu com
`CPF X` e `maria@gmail.com`, e submeteu `diploma.pdf` e `experiencia.pdf`. A 010 é implantada: a
migração cria a identidade de Maria com o `subject Y` que suas inscrições já carregam.

**Primeiro acesso.** Maria abre a **Área do candidato**, informa `maria@gmail.com`, recebe o código e
o confirma. Como o endereço consta de suas inscrições, o sistema pede o CPF **uma vez**. Ela informa,
confere, e o endereço passa a ser sua credencial.

**Área.**

> **Minhas inscrições**
> Professor de Informática · Edital 07/2027
> ✓ Inscrição enviada · INS-2027-K7M4Q2PX
> **Acompanhar**

**Conferência.**

> Diploma de graduação — `diploma.pdf` · 1,8 MB — **Visualizar · Baixar**
> Comprovação de experiência — `experiencia.pdf` · 2,4 MB — **Visualizar · Baixar**
> **Baixar comprovante**

**Acompanhamento.** Separadamente: *Sua participação* — ✓ Inscrição enviada, 14/09 às 21:42. E o
*Cronograma* — ✓ Inscrições; **Prova didática — 05/10**; Resultado preliminar — 08/10.

**No segundo acesso**, Maria informa o e-mail e o código. Nada mais.

Zero senha. Zero nova inscrição. Zero redigitação.

---

## 25. Demonstração de segurança obrigatória

Obrigatória porque o maior risco introduzido pela 010 não é visual: é **account takeover**.

**Caso 1 — IDOR.** Maria tem `subject A`; João, `subject B`. No navegador de Maria, a inscrição A
abre e o documento A abre; trocar o identificador para a inscrição B devolve 404, e para o documento
B também.

**Caso 2 — E-mail arbitrário com CPF conhecido.** Um terceiro controla `atacante@email.com` e conhece
o CPF de Maria. Ele prova o endereço. Como não há correspondência histórica, entra numa **área
vazia**: nenhuma inscrição de Maria aparece, e nenhum vínculo com o CPF dela é criado — porque o CPF
nem chega a ser pedido.

**Caso 3 — Sequestro por precedência.** O mesmo terceiro age **antes** de Maria ter qualquer
identidade. Ele não consegue reservar o CPF dela, porque nenhum caminho da 010 vincula CPF por
afirmação. Quando Maria chega, ela entra normalmente. E se o terceiro chegar a submeter uma inscrição
declarando o CPF dela, **a inscrição de Maria não é recusada** (FR-043): a duplicidade fica visível
para quem conduz o certame (FR-044), e nenhum candidato legítimo é bloqueado no prazo.

**Caso 4 — Endereço reciclado.** Maria digitou `joao@gmail.com` por engano numa inscrição de 2027.
Em 2029, o João real prova aquele endereço. Ele não sabe o CPF de Maria — e **entra normalmente**, na
sua própria identidade vazia, sem ver nada de Maria (FR-039). O endereço não o bloqueia, e a
identidade legada de Maria permanece intacta, com suas inscrições e seu `subject` (FR-040a).

**Caso 4a — Engano no convite.** Maria clica em "Continuar sem isso" sem ler. Ela entra numa
identidade vazia, percebe que suas inscrições não estão ali, e reconcilia de dentro da área: o
endereço migra e a identidade vazia é descartada (FR-040). Depois de abrir qualquer inscrição na
identidade nova, a retomada deixa de ser oferecida.

**Caso 5 — Fixação de sessão.** Uma sessão conhecida antes do login não continua válida depois dele:
o identificador é rotacionado na autenticação (FR-032a).

## 26. Ordem de entrega

Cada linha termina em comportamento observável no navegador — o Princípio VI da Constituição não
admite fatia que só exista no banco. Por isso a identidade persistente **não** é uma entrega
separada: ela chega junto com a porta que a torna visível.

| Entrega | O que se abre no navegador |
|---|---|
| **1** | Migração de reconciliação + desafio por e-mail + sessão: **e-mail → código → Minhas inscrições**, inclusive o estado vazio de quem chega pela primeira vez |
| **2** | Confirmação por CPF da correspondência histórica: quem veio da 009 reencontra suas inscrições |
| **3** | Núcleo mínimo da identidade: nome e CPF pedidos uma vez, e o rascunho da 009 retomado por `Continuar inscrição` |
| **4** | Detalhe da inscrição: dados, versão, documentos submetidos, visualizar, baixar e comprovante |
| **5** | Acompanhamento: participação, Cronograma e aviso de Edital atualizado |
| **6** | Adicionar e remover e-mail, e o *hardening* de limites, auditoria e guardas de produção |

---

## 27. Diretriz para o `/speckit-plan`

> A 010 evolui a identidade do candidato e adiciona uma área pessoal sobre capacidades já entregues
> pela 009.
>
> Não reimplemente Inscrição, upload, comprovante ou armazenamento.
>
> Preserve o contrato `IdentidadeDoCandidato` que a abertura de rascunho consome; troque apenas quem
> o preenche.
>
> Preserve intacta a constraint `(identity_subject, edital, profile_id)`: ela sustenta a idempotência
> de abertura, e nada nesta feature a substitui.
>
> Reconcilie o legado por migração de dados, na implantação, e nunca reescreva
> `Inscricao.identity_subject`.
>
> Não derive identidade nova de segredo rotacionável da aplicação nem de dado pessoal.
>
> Não vincule CPF por afirmação, em nenhum caminho, e não trate CPF como segredo nem como fator de
> autenticação.
>
> Não bloqueie envio por CPF coincidente: detecte e mostre a quem conduz o certame.
>
> Persista desafios e contadores em banco, não em cache, com consumo atômico e rotação de sessão na
> autenticação.
>
> Garanta a exclusividade do endereço canônico por constraint, e normalize de forma conservadora.
>
> Trate a inauguração do canal de e-mail como parte da feature, com guarda de produção no estilo das
> existentes — recusando os backends conhecidos por não entregar, sem alegar provar entrega.
>
> Não transforme `CandidateIdentity` em sistema genérico de IAM, nem o desafio em framework de
> autenticação multicanal.
>
> Não use Django Group para representar candidato.
>
> Nenhum caminho de credencial termina em beco sem saída: provar um endereço sempre produz sessão, e
> a decisão de reconciliar acontece antes de o vínculo existir.
>
> A única movimentação de credencial permitida é a da FR-040, e só a partir de identidade vazia:
> nada mais transfere, funde ou abandona identidade.
>
> Segurança contra IDOR e takeover é requisito funcional, e a demonstração do §25 é condição de
> merge.
>
> Cada fatia termina em comportamento observável no navegador.
>
> Havendo escolha entre uma abstração genérica de contas e uma solução estreita para a Área do
> Candidato, escolha a estreita.
