# Pesquisa — 010 Área do Candidato e Acesso sem Senha

**Data**: 2026-09-01 · **Spec**: [spec.md](./spec.md)

Cada decisão abaixo foi verificada contra o repositório em `55caa29`. Nenhuma delas introduz
dependência nova: a lista de dependências de `backend/pyproject.toml` permanece como está.

---

## D-001 — Onde mora a identidade do candidato

**Decisão**: app novo `processo_seletivo.identidade`, com os modelos, os serviços de aplicação e a
migração de reconciliação. O `portal` continua sendo o canal: views, templates e sessão.

**Racional**: é a mesma linha que a `009` já traçou entre `inscricoes` (domínio) e `portal` (canal do
ator externo), declarada no comentário de `INSTALLED_APPS`. O `portal` hoje não tem `models.py`
nenhum, e pôr a identidade lá o transformaria em canal + domínio — exatamente o que a separação
anterior evitou. Há também uma razão mecânica: a reconciliação da `FR-040` é uma migração de dados, e
migração precisa de um app que a hospede.

**Alternativas consideradas**:

- *Modelos dentro de `portal`*: menos um app, mas mistura canal e domínio e amarra o histórico de
  migrações da identidade ao app de telas.
- *Modelos dentro de `inscricoes`*: faria o domínio da Inscrição depender de credencial de acesso,
  invertendo a direção — é a identidade que alimenta a inscrição, não o contrário.

---

## D-002 — Forma do identificador estável de identidades novas

**Decisão**: `cand:` + 32 caracteres hexadecimais de um UUID versão 4, gerado no momento da criação.

**Racional**: a `FR-002` exige opacidade, estabilidade e independência de segredo rotacionável e de
dado pessoal. UUID4 entrega as três. O prefixo cumpre a mesma função que `demo:` cumpria: mantém os
dois conjuntos distinguíveis para sempre, inclusive depois que a identificação por declaração
desaparecer. Cabe folgadamente no `max_length=255` de `Inscricao.identity_subject`.

**Alternativas consideradas**:

- *Manter `HMAC(SECRET_KEY, CPF)`*: é precisamente a dependência que a feature existe para encerrar.
- *`HMAC(chave dedicada, CPF)`*: troca um segredo rotacionável por outro, e mantém o identificador
  derivado de dado pessoal.
- *Chave primária inteira exposta*: enumerável, e identificador público não deve conferir nem sugerir
  nada (Princípio I).

---

## D-003 — Como o código de acesso é guardado

**Decisão**: `django.contrib.auth.hashers.make_password` / `check_password`, com o hasher padrão do
projeto.

**Racional**: é a primitiva já disponível que a plataforma já traz, é salgada, e não exige gerir chave
nova. O custo é pago no máximo cinco vezes por desafio (`FR-029`), o que é irrelevante no percurso.

**Alternativas consideradas**:

- *HMAC-SHA256 com a `SECRET_KEY`*: mais barato, mas amarra os desafios vivos à rotação da chave —
  reintroduzindo, em escala menor, a dependência que a `FR-002` acaba de remover.
- *Guardar o código em claro com expiração curta*: a `FR-027` proíbe, e um vazamento de banco
  entregaria acessos vivos.

---

## D-004 — Consumo atômico e contagem de tentativas

**Decisão**: consumo por atualização condicional em uma instrução — `filter(pk=..., consumido_em
isnull, expira_em > agora).update(consumido_em=agora)` — considerando válido apenas quando a
atualização afeta exatamente uma linha. Tentativas incrementadas por `F("tentativas") + 1` na mesma
forma.

**Racional**: é o idioma que `shared/concurrency.py:compare_and_swap` já usa no projeto para
transição de estado sob concorrência. Ler-verificar-gravar deixaria duas abas consumirem o mesmo
código (`FR-025`, `SC-003`).

**Alternativas consideradas**:

- *`select_for_update` sobre a linha do desafio*: correto, porém mais caro e sem ganho aqui, já que a
  condição inteira cabe no `WHERE`.

---

## D-005 — Onde vivem os limites de tentativa e de reenvio

**Decisão**: no próprio banco, contando linhas de `DesafioDeAcesso` numa janela de tempo — por
endereço canônico e por origem. A origem é guardada como resumo criptográfico, nunca como endereço de
rede em claro.

**Racional**: `CACHES` não está configurado em `config/settings/base.py`; o padrão do Django é o cache
local por processo. Um limite guardado ali seria contornável com mais de um worker, e a `FR-032`
existe exatamente para impedir que a spec prometa uma proteção que a implantação não tem. Guardar
resumo da origem em vez do endereço atende à minimização do Princípio III sem perder a contagem.

**Alternativas consideradas**:

- *Cache compartilhado (Redis/Memcached)*: exigiria serviço novo em produção para uma contagem que a
  tabela já suporta. Complexidade sem necessidade demonstrada (Princípio V).
- *Tabela própria de contadores*: a informação já está nas linhas de desafio; uma segunda tabela seria
  a mesma verdade em dois lugares (Princípio II).

---

## D-006 — Forma canônica do endereço

**Decisão**: função própria em `identidade/domain`, que remove espaços das bordas e baixa a caixa do
endereço inteiro. Nada de remover pontos, cortar sufixos ou aplicar regra de provedor. O endereço
como informado é preservado em campo próprio, para exibição.

**Racional**: a exclusividade da `FR-011` precisa de uma chave estável, e a `FR-012` exige que ela
seja obtida de forma conservadora. Baixar a caixa da parte local é uma suposição — declarada como tal
na spec — e não um fato da norma; assumi-la evita multiplicar identidades por erro de digitação.

**Alternativas consideradas**:

- *`BaseUserManager.normalize_email`*: é a primitiva da plataforma, mas baixa **apenas o domínio** —
  o que faria `Maria@x` e `maria@x` serem credenciais distintas, contrariando a decisão registrada.
- *Canonicalização ao estilo de um provedor específico*: fundiria endereços distintos em outros
  servidores, e fusão indevida de credencial é indistinguível de tomada de identidade.

---

## D-007 — A reconciliação é migração de dados que pode abortar

**Decisão**: migração de dados no app `identidade`, dependente da última migração de `inscricoes`.
Ela materializa as identidades preservando o identificador estável, **interrompe** com mensagem
enumerando as inscrições enviadas sem CPF utilizável (`FR-046`), e **registra em log** os conjuntos
irreconciliáveis sem interromper (`FR-044`) — pelos identificadores estáveis e pelos identificadores
das inscrições, nunca pelo CPF (`FR-009`).

**Racional**: a `FR-040` exige que a reconciliação anteceda qualquer acesso; migração é o único ponto
que roda antes de tudo, uma vez, em toda implantação. Interromper é o comportamento desejado: sem
CPF utilizável, a restrição da `FR-063` não se instala, e prosseguir exigiria escolher um dado por
conta própria.

**Duas migrações, e a ordem entre elas.** A restrição da `FR-063` incide sobre `Inscricao`, e
restrição de modelo mora no app que o define. Logo são duas, e a segunda depende da primeira:

```text
identidade.0002_reconciliacao      cria as identidades, interrompe se precisar
              ↓  (depends_on)
inscricoes.0003_cpf_na_submetida   instala a restrição sobre inscrição enviada
```

A ordem não é preferência: instalar a restrição antes da verificação faria a implantação falhar no
`ALTER TABLE`, com a mensagem do banco em vez do relatório que enumera o que precisa de tratamento.

**Alternativas consideradas**:

- *Comando de gestão executado à parte*: dependeria de alguém lembrar de executá-lo, e a janela entre
  subir e executar é precisamente a janela em que a rotação do segredo destrói o vínculo.
- *Reconciliar sob demanda no primeiro acesso*: é a alternativa que as avaliações da spec rejeitaram,
  pelo mesmo motivo.
- *Comando `--dry-run` acompanhante*: útil, porém escopo a mais; a mensagem de interrupção já enumera
  o que precisa de tratamento.

---

## D-008 — O que a sessão do candidato guarda

**Decisão**: apenas o identificador da identidade. Nome, CPF e endereço principal são lidos do
registro a cada requisição, e o contrato `IdentidadeDoCandidato(subject, nome, cpf, email)` é montado
a partir dele.

**Racional**: a `FR-014` exige que a correção de nome alcance os rascunhos abertos. A `009` guarda os
dados na sessão, o que era correto quando eles eram declarados e efêmeros; guardá-los agora deixaria
a sessão exibir dados obsoletos até o próximo acesso. O custo é uma consulta por requisição do portal,
na mesma ordem das que a página já faz.

**Alternativas consideradas**:

- *Manter a cópia na sessão*: mais barato e errado — a correção só apareceria depois de sair e entrar.

---

## D-009 — Rotação de sessão e separação de eixos

**Decisão**: `request.session.cycle_key()` imediatamente antes de gravar a identidade na sessão. A
chave de sessão do candidato continua sendo a do portal, distinta da chave da interface
administrativa.

**Racional**: `FR-035`. Sem a rotação, quem induzir a vítima a usar uma sessão conhecida antes do
acesso continua dentro dela depois, e o desafio inteiro é contornado sem ser tocado. `cycle_key`
preserva o conteúdo da sessão e troca o identificador, que é exatamente o necessário para não perder
o destino de retorno.

---

## D-010 — A movimentação de credenciais da FR-053

**Decisão**: bloco transacional único que (1) toma bloqueio de linha sobre a identidade de origem,
(2) reconfirma dentro do bloqueio que ela não tem inscrição alguma, (3) move todas as credenciais,
(4) descarta a identidade vazia. A abertura de rascunho toma **o mesmo bloqueio** sobre a identidade
antes de criar a Inscrição.

**Racional**: a `FR-055` exige atomicidade, e o bloqueio só na reconciliação não bastaria: `Inscricao`
não referencia a identidade por chave estrangeira, então nada impediria um rascunho de nascer entre a
verificação e o descarte, deixando inscrição órfã de identidade inexistente. Bloquear a mesma linha
nos dois caminhos serializa os dois, e é barato — a abertura de rascunho já é uma escrita.

**Alternativas consideradas**:

- *Chave estrangeira de `Inscricao` para a identidade*: resolveria por integridade referencial, mas
  reescreveria o modelo da `009` e tocaria o campo que a `FR-042` proíbe mexer.
- *Verificar e mover sem bloqueio*: é o defeito que a `FR-055` nomeia.

---

## D-011 — Aposentadoria da identificação por declaração

**Decisão**: remover a rota, a view e o template de identificação declarada, junto com a derivação do
identificador a partir do CPF. Manter a variável `PORTAL_IDENTIDADE_DEMO` definida e a recusa de
inicialização que ela dispara em `config/settings/production.py`, como armadilha: se alguém
reintroduzir o caminho, produção continua se recusando a subir.

**Racional**: a `FR-048` pede as duas coisas — que a declaração deixe de autenticar e que a recusa
permaneça ativa. Manter a tela "só para desenvolvimento" criaria uma segunda maneira de virar
candidato, sem registro de identidade, e faria conviver dois modelos de identidade no mesmo canal.

**Alternativas consideradas**:

- *Remover também a variável e a guarda*: satisfaz a primeira metade e abandona a segunda; a guarda
  custa as linhas que já existem.

---

## D-012 — Onde ficam os eventos de credencial na auditoria

**Decisão**: `RegistroAuditoria`, a mesma trilha, com `aggregate_type` da identidade,
`aggregate_id` do registro, operação nomeando o ato, e `institution_scope` **vazio**. Sem trilha
paralela e sem escopo inventado.

**E a limitação, declarada**: `auditoria/selectors.py:47` filtra estritamente por
`institution_scope=actor.institution_scope`. Um evento sem escopo, portanto, **não aparece** na
consulta administrativa de auditoria — por construção, porque ele não pertence a Edital algum. Ele é
investigável por inspeção direta da trilha, que é append-only e preserva ator, ato, momento e
correlação. Decidir explicitamente, como a `FR-089` manda, inclui decidir que ele não é visível ali —
e dizer por quê.

**Alternativas consideradas**:

- *Inventar um escopo institucional para atos de candidato*: faria o campo mentir sobre o que
  significa, e o valor apareceria em consultas de quem não tem nada a ver com aquele ato.
- *Alargar o seletor para devolver eventos sem escopo*: mexe numa superfície de autorização existente
  para um ganho que a investigação direta já entrega.
- *Trilha separada para identidade*: proibido pela `FR-089`, e fragmentar a auditoria é o oposto do
  que o Princípio III pede.

---

## D-013 — Como a coincidência de CPF é assinalada

**Decisão**: na consulta administrativa já existente, uma marcação por linha, calculada por subconsulta
de existência — outra inscrição enviada, no mesmo Edital e Perfil, com o mesmo CPF normalizado.

**Racional**: a `FR-065` exige marcação porque a listagem exibe CPF mascarado
(`inscricoes/domain/pessoais.py`), e comparar máscaras a olho não é detecção. Subconsulta de
existência é uma cláusula a mais na consulta que já roda, sem tabela nova e sem varredura própria.

**Alternativas consideradas**:

- *Coluna materializada de duplicidade*: informação derivada persistida, que passa a poder divergir.
- *Relatório separado*: painel novo para um sinal que pertence à linha.

---

## D-014 — Envio da mensagem e recusa de inicialização

**Decisão**: envio pela API de e-mail da própria plataforma, com mecanismo e remetente vindos do
ambiente. Em `production.py`, recusa de inicialização quando o mecanismo estiver no conjunto dos
conhecidos por não entregar — console, memória, arquivo e mudo — ou quando não houver remetente.

**Racional**: a `FR-081` pede a recusa e proíbe alegar mais do que ela prova. É a mesma forma —
conjunto de valores conhecidamente inseguros, verificado na inicialização — que `production.py` já
aplica aos esquemas de autenticação não institucionais, e o próprio módulo já declara que recusa o
que sabe ser inseguro sem provar que o resto está certo.

**Alternativas consideradas**:

- *Verificar conectividade com o servidor de envio na inicialização*: prova pouco, falha por rede e
  transforma indisponibilidade momentânea em recusa de subir.
- *Fila de envio*: infraestrutura nova; a `FR-030` e as suposições da spec já dispensam a
  indistinguibilidade de tempo que a fila serviria.

---

## D-015 — Telas sem tecnologia nova

**Decisão**: formulários com envio por POST, renderizados no servidor, sobre a base visual do portal.
Nenhum componente novo de front-end.

**Racional**: as telas desta feature são três formulários curtos, uma lista e uma página de detalhe. A
`009` já estabeleceu a base, o padrão de acessibilidade e o alvo de 375 px. O campo do código precisa
aceitar colagem integral e digitação natural (`UX-005`), o que um único campo de texto entrega — e
seis campos independentes não entregariam.

---

## D-016 — Onde o contador de tentativas de CPF persiste

**Decisão**: no próprio `DesafioDeAcesso`, em contador separado do de tentativas do código. A linha
**deixa de ser terminal no consumo**: ela passa a portar a reconciliação pendente até que esta seja
decidida ou expire, dez minutos após o consumo. O incremento usa a mesma atualização condicional de
D-004.

**Racional**: o contrato previa esgotamento sem dizer onde ele é contado, e nenhum dos lugares óbvios
serve. A sessão não serve — uma aba nova zera. A identidade alvo não serve, e essa é a parte que
importa: um contador preso ao alvo deixaria um terceiro esgotar as tentativas e **impedir o titular
legítimo de reconciliar**, que é a mesma classe de bloqueio que a `FR-036` e a `FR-064` foram
escritas para evitar. O desafio é o único portador que é, ao mesmo tempo, do lado de quem tenta,
persistente entre requisições, e naturalmente descartável.

**A composição que isso produz** é a proteção real: cinco tentativas por desafio, e desafios limitados
por endereço e por origem (`FR-030`). Quem quiser tentar de novo paga o preço de pedir outro código.

**Alternativas consideradas**:

- *Contador na sessão*: não resiste a aba nova, que é o caminho de quem está tentando adivinhar.
- *Contador na identidade alvo*: cria bloqueio do titular legítimo por ação de terceiro.
- *Tabela própria de tentativas*: a informação já cabe na linha que existe, e uma segunda tabela seria
  a mesma verdade em dois lugares.

**Consequência para a retomada da `FR-053`**: ela também passa por desafio. Quem retoma prova de novo
o endereço que carrega a correspondência, e a contagem vale igual nos dois caminhos — uma regra só. O
custo de experiência é baixo (a retomada é rara) e o ganho é direto: o ato que move credenciais e
descarta uma identidade é reprovado no instante em que acontece.

---

## D-017 — O que a restrição de banco consegue afirmar sobre o CPF

**Decisão**: a restrição sobre inscrição enviada exige `cpf_normalizado` com exatamente onze dígitos.
A conferência dos dígitos verificadores permanece no domínio — na captura (`FR-006`) e na verificação
que a implantação faz antes de instalar a restrição (`FR-046`).

**Racional**: o algoritmo dos dígitos verificadores não cabe numa restrição declarativa. Escrever
"válido, garantido pela persistência" era prometer mais do que o banco entrega, e uma garantia que só
existe no texto é pior que garantia nenhuma, porque ninguém a verifica.

**Alternativas consideradas**:

- *Função em PL/pgSQL chamada pela restrição*: expressa o algoritmo, mas exige função imutável
  mantida fora do código da aplicação, duplica uma regra que já existe no domínio, e torna a migração
  dependente de um objeto de banco que nada mais usa.
- *Deixar a restrição só com "não vazio"*: aceitaria `"1"` numa inscrição enviada, e a `FR-063` existe
  justamente para que a coluna seja utilizável pela reconciliação e pela marcação de coincidência.

---

# Decisões tomadas em revisão

As quinze acima antecederam a implementação. As cinco abaixo nasceram das revisões de código, e
estão aqui pelo mesmo motivo que as outras: comportamento acidental não pode virar regra sem
decisão documentada (Princípio V). Cada uma corrigiu algo que a suíte não pegava.

## D-018 — A topologia de proxy é declarada, não adivinhada

**Decisão**: `PORTAL_ATRAS_DE_PROXY` decide se `X-Forwarded-For` é lido, e `production.py` recusa
iniciar enquanto ela não for declarada como `true` ou `false`.

**Racional**: a primeira versão lia o cabeçalho sempre, e ele é escrito pelo cliente — trocá-lo a
cada requisição fazia cada uma parecer vir de outro lugar, e o teto por origem nunca era alcançado.
Deixar de lê-lo por padrão fechou esse buraco e abriu outro, pior: atrás de um proxy, `REMOTE_ADDR`
é o mesmo para todo mundo, e o teto de trinta por hora passaria a valer para a instituição inteira —
recusando candidato legítimo em bloco no último dia do prazo, com a mensagem neutra de sempre.

Nenhum padrão serve para as duas topologias. Exigir a declaração é o que este projeto já faz com
segredo, host e mecanismo de envio: transformar pressuposto em precondição de inicialização.

**Alternativas consideradas**: *ler o cabeçalho só quando `REMOTE_ADDR` é privado* — heurística que
acerta na maioria das redes e falha em silêncio nas demais, que é o pior desfecho possível para um
limite de segurança.

## D-019 — Sem prova, nada acontece

**Decisão**: só um desafio **consumido**, apontado pela sessão, autoriza seguir na reconciliação. O
endereço guardado na sessão serve para exibição, nunca para decidir a quem uma credencial pertence.

**Racional**: a versão anterior criava identidade a partir do endereço do formulário, gravado antes
de qualquer prova. Informar o e-mail de outra pessoa e abrir a rota entrava em nome dela — e prendia
aquele endereço à identidade do atacante pela restrição de unicidade, impedindo a dona de usá-lo
para sempre. A suíte não pegou porque todo teste seguia o fluxo, e quem ataca pula.

## D-020 — O alvo anotado decide, e sobrevive ao descarte

**Decisão**: `confirmar_cpf` lê `reconciliacao_alvo` quando ele existe, e o campo usa `SET_NULL`.

**Racional**: gravado e nunca lido, ele prometia uma garantia que ninguém impunha — refazer a busca
deixava o conjunto de candidatas mudar sob um convite já aberto. E com `CASCADE`, apagar uma
identidade levaria junto os desafios que a apontam, inclusive o contador de tentativas de CPF, que é
registro de segurança. Anotação não compõe: ela deixa de valer, e o desafio permanece.

## D-021 — O ato e o registro que o explica commitam juntos

**Decisão**: `registrar_ato` é chamado **dentro** da transação de `adicionar` e `remover`.

**Racional**: escrevi `registrar_ato` porque `record_event` lê `status` e `revision`, e a identidade
do candidato não é máquina de estados. Ao sair do auxiliar, larguei junto a garantia que vinha com
ele — a `009` chama `record_event` dentro de `command_context()`. Uma falha entre gravar a credencial
e escrever na trilha deixaria a credencial existindo sem evento que a explicasse (Princípio IV).

## D-022 — Recusa nomeada, e captura estreita

**Decisão**: `remover` devolve três desfechos distintos, e a leitura do conteúdo publicado captura
`DomainError`, não `Exception`.

**Racional**: o booleano fazia a view responder "você não pode remover seu último e-mail" a quem
pedisse a remoção de credencial alheia — resposta que descreve errado o que aconteceu, e que numa
investigação aponta para o lado errado. E a captura larga escondeu um defeito real por uma fase
inteira: a lista lia `.conteudo` num objeto cujo atributo é `content`, e **toda** linha saía sem
Edital e sem Perfil, sem que nada acusasse.

---

# Decisões tomadas depois de percorrer a jornada

Um percurso completo no navegador — do cartaz da vaga ao comprovante, com um candidato novo e duas
participações legadas — encontrou seis defeitos que a suíte não pegava, porque nenhum deles é uma
regra violada: são coisas que o sistema faz corretamente **sem dizer**, ou dizendo o que não é
verdade. As decisões abaixo são a resposta a eles.

## D-023 — A recusa do código nomeia a causa

**Decisão**: `estado_atual` classifica o desafio depois de uma tentativa recusada, e a tela diz qual
dos quatro motivos foi, com o saldo de tentativas quando ele existe (`FR-031a`).

**Racional**: a frase única era a leitura mais larga possível da `FR-031`, e cobrava caro por isso.
Esgotadas as cinco tentativas, o desafio morre — e quem então encontrava o código **certo** na caixa
de entrada e o digitava corretamente lia exatamente "código inválido ou expirado". Do lado do
servidor tudo estava certo; do lado da pessoa o sistema estava mentindo sobre a causa, e a saída que
a frase indicava estava bloqueada pela janela de espera, sem aviso (D-024). Reproduzido no percurso
e depois em teste: `test_o_codigo_certo_depois_do_teto_diz_que_o_codigo_foi_cancelado`.

**O que a FR-031 realmente proíbe** é distinguir código errado de **endereço inexistente** — e nada
disso distingue: `solicitar` cria o desafio de forma idêntica exista ou não identidade, então motivo
e saldo são os mesmos nos dois casos. O que se lê é o estado do desafio que a própria sessão pediu, e
que ela já conhece por ter contado os próprios erros. `test_a_recusa_nao_distingue_quem_existe`
guarda a fronteira.

**Alternativa rejeitada**: manter a frase única e só melhorar o texto. Não resolve — o problema não é
a redação, é a informação ausente.

## D-024 — Reenviar responde por escrito, mesmo quando não envia

**Decisão**: `_noticia_do_envio` produz uma frase para cada desfecho, inclusive "nada foi enviado", e
a contagem ao lado do botão é recalculada a cada renderização (`FR-031b`, `UX-006`).

**Racional**: o botão estava sempre clicável e, dentro da janela de espera, não enviava nada e não
dizia nada. Pior: a recusa que estava na tela sumia junto com o recarregamento, então o clique
**parecia** ter funcionado. Silêncio é a pior resposta possível aqui, porque é indistinguível de
sucesso — a pessoa passava a esperar um e-mail que nunca saiu.

**O botão continua habilitado no servidor**, e é decisão, não descuido: desabilitá-lo na renderização
prenderia quem está sem JavaScript, porque a página não se atualiza sozinha e o botão nunca voltaria.
Quem tem JavaScript vê a contagem correr e o botão liberar; quem não tem clica e recebe a resposta
por escrito. Nenhum dos dois fica sem saber.

**Um número só para a mesma espera.** A primeira versão repetia na notícia o valor apurado no POST, e
a tela mostrava "59 segundos" numa linha e "56 segundos" na outra — dois números para a mesma coisa.
A contagem ao lado do botão é a única fonte.

## D-025 — O envio da inscrição deixa recibo, e é a única exceção

**Decisão**: `inscricoes/application/mensagem.py` envia uma mensagem, depois do commit, e a `FR-084`
passa a nomear essa exceção em vez de proibir tudo.

**Racional**: a proibição original estava certa no princípio — canal existir não torna comunicação
transacional escopo implícito — e errada no caso. A pessoa conclui o ato mais importante do ano dela,
o comprovante aparece na tela, e a caixa de entrada não registra nada; fechada a aba antes de baixar
o PDF, ela fica sem o protocolo que a própria página manda guardar. A exceção é nominal: uma
mensagem, disparada por um ato que a própria pessoa praticou.

**Depois do commit, e fora do domínio.** Enviar de dentro da transação amarraria um ato
administrativo à disponibilidade de um servidor de SMTP: uma falha de rede desfaria uma inscrição
válida, e um rollback posterior deixaria na caixa da pessoa a confirmação de algo que não aconteceu
(Princípio IV, `FR-084b`). `test_falha_no_envio_da_mensagem_nao_custa_a_inscricao` força a falha.

**Sem CPF e sem telefone** (`FR-084a`). Aqui a caixa é credencial provada — não é o caso da `FR-082`,
em que ainda não se sabe de quem ela é —, mas dado que não ajuda quem lê viaja junto quando a
mensagem é encaminhada.

## D-026 — O instante é convertido antes de ser escrito

**Decisão**: `comprovante_pdf.instante` converte para o fuso da instituição antes de chamar
`humano.instante`, e `humano.instante` documenta que escreve o que recebe (`FR-074a`).

**Racional**: o comprovante em HTML passa pelo filtro `date`, que localiza; a tela de conferência e o
PDF liam `comprovante_pdf.instante`, que formatava o valor cru — e o banco devolve UTC. A mesma
inscrição aparecia enviada às 16h03 no comprovante e às 19h03 na conferência, com os documentos
datados às 16h01 três linhas abaixo, na mesma página. `publicacoes/pdf.py` já convertia; este caminho
não, e a assimetria só aparecia olhando as duas telas juntas.

**A conversão fica no chamador**, e não em `humano`: aquele módulo existe para não depender de estado
global do processo, e `localtime` lê `TIME_ZONE`. A docstring passou a dizer isso, para que o próximo
chamador não repita o esquecimento.

## D-027 — A área tem porta, e a porta aparece

**Decisão**: o cabeçalho leva a "Minhas inscrições" quando há sessão e a "Entrar" quando não há, por
bloco de *template* que as telas do próprio acesso esvaziam (`UX-006a`).

**Racional**: a vitrine não oferecia entrada nenhuma. Quem já se inscreveu e volta para conferir
precisava clicar em "Inscrever-se nesta vaga" numa vaga qualquer — a única porta — ou saber o
endereço de cor. E, com sessão aberta, o cabeçalho trazia só o nome e o botão *Sair*.

**Bloco, e não variável de contexto**: as três telas do acesso o esvaziam declarando o bloco vazio, e
nenhuma view precisa lembrar de passar bandeira — que é exatamente o tipo de coisa que se esquece na
quarta tela.

## D-028 — A escolha de modalidade é guardada quando é feita

**Decisão**: o campo submete o formulário que já existe com `acao=guardar`; a view grava e devolve a
página, em vez de avançar para a revisão (`FR-061a`).

**Racional**: a tela promete que "a escolha decide quais documentos serão pedidos a você", e a
promessa não valia no instante da escolha — a lista continuava com dois documentos e o aviso verde
continuava dizendo "todos os obrigatórios foram enviados". O terceiro aparecia na revisão, quando a
pessoa já se considerava pronta; e quem saía e voltava reencontrava o campo em branco, porque a
escolha não era gravada até ali.

**Formulário, e não htmx.** Trocar de modalidade pode descartar documento já enviado, e esse descarte
é confirmado numa tela própria desde a `009`. Um `hx-post` no campo teria de reproduzir aquela
confirmação dentro de um fragmento; submeter o formulário aproveita o caminho que já existe, e o
único acréscimo é para onde voltar depois — que é o que `acao` diz, e o que a confirmação de descarte
carrega adiante.

**Sem JavaScript nada muda**: escolher e clicar em "Revisar inscrição" continua funcionando, e
`test_sem_javascript_nada_muda` guarda isso.

## D-029 — Mexer em quem alcança a conta pergunta antes e avisa depois

**Decisão**: a remoção de credencial passa por uma tela de confirmação (`GET` na mesma rota), e
adicionar e remover avisam a credencial principal por mensagem (`FR-018a`, `FR-018b`).

**Racional**: sem senha, a lista de credenciais **é** a conta. "Remover" ficava ao lado de "Tornar
principal" e apagava no primeiro clique, sem perguntar e sem dizer nada — errar o alvo custava uma
via de acesso, descoberta só na vez seguinte em que a pessoa tentasse entrar por ali. E ninguém era
avisado: quem conseguisse anexar um endereço à conta alheia entraria por ele indefinidamente, e a
titular não teria sinal nenhum disso.

**A confirmação é a mesma forma do descarte de documento** — enunciar o que se perde antes de perder.
Repetir um padrão que já existe é mais barato de manter e mais fácil de reconhecer.

**O aviso da remoção é lido depois do ato**: removida a principal, outra é promovida, e é a que
resta que precisa saber. Ler antes mandaria a mensagem justamente para a caixa que acabou de sair.

## D-030 — O texto do código depende da finalidade

**Decisão**: `enviar_codigo` recebe a finalidade e escolhe o corpo (`FR-082a`).

**Racional**: a mensagem de "adicionar credencial" era idêntica à de entrar, e dizia "se não foi você
que pediu este código, ignore esta mensagem: ninguém entra sem ele". No login isso é verdade e
tranquiliza. Aqui é o contrário do risco: quem obtiver o código não entra na conta de quem recebeu a
mensagem — anexa a caixa de quem recebeu à conta **dele**, e passa a entrar por ela. As duas
finalidades já eram distintas no modelo desde a `FR-028`; só o texto não distinguia.

## D-031 — O atendimento é declarado, e aparece

**Decisão**: `PORTAL_ATENDIMENTO` é exigida em produção e exibida nas duas telas que remetem a ele
(`UX-011`).

**Racional**: "procure o atendimento institucional" aparecia duas vezes sem dizer qual — nem e-mail,
nem telefone, nem link —, e são justamente os dois pontos em que a pessoa já está travada: o CPF
congelado depois da primeira inscrição enviada, e a participação anterior que ela não conseguiu
confirmar. Mandar procurar sem dizer onde é abandonar quem pediu ajuda.

**Exigida em produção**, pela mesma linha da `FR-030a`: é dado que só quem implanta conhece, não tem
padrão que sirva, e a ausência não aparece como erro — aparece como candidato sem saída. Em
desenvolvimento pode faltar, e a frase genérica é o que sobra.

## D-032 — Todo ato responde, e a resposta é lida uma vez

**Decisão**: um par de chaves de sessão para todo o portal (`portal_aviso`, `portal_recusa`), lido
por quem exibe (`UX-012`).

**Racional**: quatro atos mudavam a página sem uma palavra — reconciliar a participação anterior, que
é o momento mais aliviante da jornada; corrigir o nome; adicionar um e-mail; esgotar as tentativas de
CPF. Cada um sozinho é pequeno; juntos formam a impressão de um sistema que não responde.

**Lido nas views, e não num processador de contexto.** O processador roda também para os fragmentos
que o htmx devolve, e a confirmação seria consumida por um envio de arquivo feito logo depois — some
sem nunca ter sido lida. As telas que recebem confirmação são quatro, e nelas a leitura é explícita.

## D-033 — A falha do envio aparece

**Decisão**: `htmx:responseError` e `htmx:sendError` escrevem uma frase junto do documento
(`UX-013`).

**Racional**: o htmx só troca conteúdo em resposta bem-sucedida, o que está certo — e por isso uma
resposta de erro deixava a tela exatamente como estava: o nome do arquivo ali, a contagem igual, nada
acusando. Aconteceu no percurso: a sessão havia caído noutra aba, o envio voltou `404`, e a página
não piscou. A pessoa acredita ter anexado, e descobre na revisão — ou não descobre.

**Não reenvia sozinho**: repetir dez megabytes em rede móvel sem a pessoa pedir é decisão dela. A
mensagem diz o que houve, o que fazer, e que o que já foi enviado continua guardado — sem essa última
frase, quem lê "não foi possível enviar" recomeça tudo.
