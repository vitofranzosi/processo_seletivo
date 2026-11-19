# Contexto para análise: identidade do candidato, CPF coincidente, histórico fragmentado e vantagem em sorteio

**Data:** 2026-11-17
**Natureza:** contexto para análise; não constitui decisão de produto, especificação ou autorização
de implementação.

## Objetivo

Precisamos revisar o modelo de identidade do candidato do Sistema de Processos Seletivos do
Cefor/Ifes.

A solução atual foi desenhada para reduzir a fricção antes da inscrição:

- a pessoa entra apenas com um código enviado ao e-mail;
- não cria senha;
- um endereço novo produz uma sessão válida e uma área vazia;
- nome e CPF são pedidos somente quando a pessoa inicia a primeira inscrição;
- ninguém é impedido de se inscrever porque outra identidade declarou o mesmo CPF.

Essa abordagem resolveu riscos de bloqueio e abandono no onboarding, mas introduziu dois problemas
relacionados:

1. uma mesma pessoa pode criar identidades distintas com e-mails diferentes e obter mais de uma
   participação no mesmo sorteio;
2. as inscrições e o histórico ficam fragmentados entre identidades, de modo que a pessoa não vê
   toda a sua trajetória ao entrar por apenas um dos e-mails.

Precisamos avaliar alternativas que mantenham uma jornada simples sem transformar CPF declarado em
prova indevida de identidade.

## Contexto do produto

O sistema gerencia Processos Seletivos e Editais, incluindo:

- inscrição;
- envio de documentos;
- avaliação;
- habilitação;
- sorteio;
- classificação;
- recursos;
- convocação;
- matrícula.

As decisões podem produzir efeitos administrativos e jurídicos. Portanto:

- Publicações são imutáveis;
- correções ocorrem por sucessão ou Retificação;
- dados normativos não são apagados;
- toda operação sensível precisa de autorização, motivo e auditoria;
- identificadores públicos não concedem acesso;
- dados pessoais devem obedecer à LGPD e à minimização.

## Motivação original do modelo atual

O sistema não queria exigir cadastro tradicional com senha antes de a pessoa poder se inscrever.

A jornada escolhida foi:

```text
informar e-mail
    ↓
receber código
    ↓
provar controle do e-mail
    ↓
entrar na área do candidato
    ↓
informar nome e CPF somente ao iniciar a primeira inscrição
```

Isso evita:

- criação e recuperação de senha;
- coleta antecipada de CPF de quem deseja apenas consultar Editais;
- dependência de um provedor institucional ainda inexistente;
- becos sem saída quando o endereço não tem participação anterior;
- bloqueio da pessoa legítima por alguém que tenha informado seu CPF primeiro.

O CPF é declarado pelo candidato e validado formalmente, mas não é consultado em uma fonte oficial.
Portanto, o sistema sabe apenas que os dígitos formam um CPF possível — não que o endereço de e-mail
pertence ao titular desse CPF.

## Modelo atual

### Identidade

`CandidateIdentity` possui:

- `subject`: identificador opaco, estável e único;
- nome;
- CPF normalizado;
- uma ou mais credenciais de e-mail verificadas.

O CPF não é único. Duas identidades podem declarar o mesmo número.

A propriedade de uma inscrição é determinada exclusivamente por `identity_subject`, nunca por CPF
ou e-mail.

Referência: `backend/processo_seletivo/identidade/models.py`.

### Credencial de e-mail

Cada e-mail verificado pode pertencer a apenas uma identidade.

Uma identidade pode ter vários e-mails e escolher um deles como principal. Esse é o caminho adequado
quando a pessoa ainda tem acesso à conta original: entra nela e adiciona o novo e-mail.

O problema ocorre quando ela entra diretamente com um e-mail novo e não relaciona esse endereço à
identidade anterior.

### Inscrição

A unicidade atual é:

```text
identity_subject + Edital + Perfil
```

Assim:

- a mesma identidade não abre duas inscrições para o mesmo Edital e Perfil;
- identidades diferentes podem abrir inscrições para o mesmo Edital e Perfil;
- essas identidades podem declarar o mesmo CPF.

Referência: `backend/processo_seletivo/inscricoes/models.py`, constraint
`uq_inscricao_identidade_edital_perfil`.

## Reconciliação existente

Quando alguém prova o controle de um e-mail:

1. se o endereço já é credencial, entra na identidade correspondente;
2. se o endereço aparece em inscrições históricas, o sistema oferece uma reconciliação;
3. o CPF pode desempatar entre identidades históricas associadas àquele mesmo endereço;
4. se o endereço não possui correspondência histórica, nasce uma identidade nova sem pedir CPF;
5. recusar o convite, errar o CPF ou esgotar tentativas também produz uma identidade própria e
   utilizável.

Ponto importante: a busca inicial é pelo e-mail. O sistema não procura globalmente uma identidade
pelo CPF informado, pois isso permitiria vinculação ou enumeração baseada em um dado que não prova
titularidade.

Consequentemente:

```text
E-mail A → identidade X → CPF 123 → inscrições antigas
E-mail B → identidade Y → CPF 123 → inscrições novas
```

Nada une automaticamente X e Y.

## Requisitos vigentes sobre CPF coincidente

A especificação `010-area-do-candidato` determina:

- `FR-062`: uma inscrição por identidade, Edital e Perfil;
- `FR-063`: inscrição enviada precisa de CPF normalizado com onze dígitos;
- `FR-064`: duas inscrições de identidades diferentes com o mesmo CPF e Perfil devem ser aceitas;
- `FR-065`: a consulta administrativa deve assinalar a coincidência;
- `FR-066`: o sistema não decide qual inscrição vale; a decisão é institucional e deveria pertencer
  a uma futura feature de avaliação.

Essas regras foram deliberadas para evitar um ataque do tipo “primeiro a enviar vence”: se CPF fosse
único no envio, alguém que conhecesse o CPF de outra pessoa poderia se inscrever primeiro e impedir a
inscrição legítima enquanto o prazo corre.

## Comportamento atual da coincidência

Quando duas identidades enviam inscrições com o mesmo CPF para o mesmo Edital e Perfil:

- as duas inscrições são aceitas;
- nenhuma é automaticamente invalidada;
- a gestão vê a marca de CPF coincidente;
- não existe workflow para analisar, justificar ou resolver a coincidência;
- nenhuma delas é suspensa enquanto aguarda análise;
- a marca não é consumida pelas etapas posteriores.

A especificação diz que a decisão é institucional, mas essa decisão ainda não foi modelada.

## Efeito no sorteio

O sorteio opera por inscrição.

Ao publicar a relação de habilitados, o sistema:

1. seleciona todas as inscrições submetidas e habilitadas daquele Perfil/lista;
2. cria um `ParticipanteHabilitado` para cada inscrição;
3. atribui um número público para cada participante;
4. dá posição a todos os participantes.

Não existe deduplicação por CPF, identidade civil ou pessoa. A marca `cpf_coincidente` não interfere
na relação.

Portanto, se duas inscrições coincidentes permanecerem habilitadas no mesmo recorte:

```text
Inscrição 1 → número público 17
Inscrição 2 → número público 42
```

A mesma pessoa passa a ter duas posições e, materialmente, mais chances.

Esse efeito ocorre antes mesmo de discutir classificação ou convocação: a vantagem nasce quando a
relação de habilitados é congelada.

Se a relação já tiver sido publicada, ela é imutável. Uma correção precisa produzir uma relação
sucessora, nunca editar ou apagar a anterior.

## Efeito no histórico do candidato

A tela “Minhas inscrições” consulta:

```text
Inscricao.objects.filter(identity_subject=identidade.subject)
```

Logo, ela mostra apenas as inscrições daquela identidade técnica.

Uma pessoa com duas identidades não vê um histórico consolidado:

```text
Identidade X → processos de 2024 e 2025
Identidade Y → processo de 2026
```

Entrando pelo e-mail ligado a Y, ela não vê as inscrições de X.

Isso afeta:

- consulta de inscrições antigas;
- comprovantes;
- resultados individuais;
- recursos;
- convocações;
- requerimentos;
- documentos e demais atos vinculados à inscrição.

O histórico não está perdido, mas fica inacessível por aquela sessão porque a titularidade continua
associada ao `subject` anterior.

## Problemas que precisam ser resolvidos

Há pelo menos três problemas distintos. Eles não devem ser tratados necessariamente pela mesma
regra.

### 1. Prevenção de vantagem indevida

Impedir que duas inscrições da mesma pessoa participem do mesmo Perfil/lista ou produzam duas
chances no sorteio.

### 2. Resolução institucional de coincidências

Permitir que uma autoridade analise a coincidência antes de atos posteriores, distinguindo:

- mesma pessoa com duas contas;
- CPF digitado incorretamente;
- uso indevido do CPF de terceiro;
- homonímia sem relevância;
- duplicidade acidental;
- possível fraude.

### 3. Consolidação do histórico e recuperação da conta

Permitir que a pessoa prove que duas identidades são suas e passe a acessar todo o histórico por
qualquer credencial válida, sem reescrever silenciosamente inscrições ou atos antigos.

## Restrições que uma solução deve preservar

### Não bloquear pelo CPF declarado

CPF informado num formulário não prova titularidade. Uma constraint global de unicidade pode criar
negação de serviço contra o titular legítimo.

### Não unir identidades apenas por igualdade de CPF

Fazer merge automático por CPF pode entregar inscrições, documentos e dados sensíveis a quem apenas
conhece o número de outra pessoa.

### Não reescrever silenciosamente a história

Inscrições enviadas têm titularidade e autoria registradas. Uma consolidação precisa preservar:

- identidade original;
- inscrição original;
- atos praticados;
- instante e fundamento da vinculação posterior;
- trilha completa.

Pode ser mais adequado criar uma associação ou ato de consolidação do que substituir diretamente
todos os `identity_subject`.

### Não usar e-mail como identidade civil permanente

E-mail muda, pode ser perdido, reciclado ou compartilhado. Ele é uma credencial de acesso, não
necessariamente a pessoa.

### Não criar beco sem saída

Mesmo uma pessoa com coincidência precisa conseguir:

- concluir uma inscrição dentro do prazo;
- receber uma resposta compreensível;
- saber como regularizar;
- não ficar bloqueada indefinidamente por ação de terceiro.

### Resolver antes do efeito irreversível

Aceitar a inscrição e resolver depois pode ser adequado, mas a pendência não pode atravessar
silenciosamente um ato como:

- relação de habilitados;
- sorteio;
- classificação;
- convocação.

## Questões de domínio que precisam de resposta

Peço que a análise determine:

1. A norma permite apenas uma inscrição da mesma pessoa por Perfil, por Edital ou por Processo
   Seletivo?
2. Um Processo pode possuir vários Editais; o limite deve atravessar esses Editais?
3. Inscrições em Perfis diferentes são sempre legítimas?
4. O que caracteriza que duas inscrições pertencem à mesma pessoa?
5. Quem pode declarar isso institucionalmente?
6. Quais evidências podem ser usadas?
7. O CPF coincidente deve criar:
   - apenas alerta;
   - pendência;
   - suspensão de habilitação;
   - impedimento de publicar a relação;
   - outro estado?
8. Qual inscrição deve prevalecer quando ambas são da mesma pessoa?
9. A escolha é do candidato, da comissão ou decorre de uma regra objetiva?
10. É permitido corrigir CPF antes ou depois do envio?
11. O candidato deve poder contestar ou recorrer da decisão?
12. Como tratar inscrição feita com CPF de terceiro?
13. O que acontece se a coincidência só for descoberta depois do sorteio?
14. Como consolidar o histórico sem alterar atos anteriores?
15. Como recuperar a identidade quando a pessoa perdeu acesso ao e-mail antigo?
16. Existe ou haverá provedor confiável, como autenticação institucional ou gov.br?
17. Há candidatos estrangeiros, menores, pessoas sem CPF ou situações de representação?
18. Um e-mail pode legitimamente ser compartilhado entre familiares ou responsáveis?
19. Qual é a política institucional de retenção das identidades e credenciais?

## Alternativas a comparar

Estas são famílias de solução para análise, não decisões já tomadas.

### A. Identidade externa forte desde o início

Exemplo conceitual: autenticação por provedor que entregue CPF verificado.

Vantagens:

- uma pessoa civil tende a ter uma identidade única;
- simplifica histórico e duplicidade;
- reduz análise manual.

Riscos:

- aumenta dependência externa;
- pode elevar a fricção;
- exige política para indisponibilidade e pessoas sem acesso ao provedor;
- migração das identidades atuais continua necessária.

### B. E-mail primeiro, prova forte somente antes de produzir direito

Manter o onboarding atual, mas exigir verificação mais forte antes de:

- habilitação;
- sorteio;
- classificação;
- convocação.

Vantagens:

- mantém baixa fricção inicial;
- posiciona a prova de identidade no momento de maior risco.

Riscos:

- cria etapa adicional depois da inscrição;
- precisa de prazo e tratamento de falhas;
- pode excluir pessoas que não conseguem completar a verificação.

### C. Aceitar duplicidades e criar um gate institucional

A inscrição continua aceita, mas coincidências ficam pendentes e impedem publicar a relação daquele
recorte até decisão.

Vantagens:

- preserva a proteção contra “primeiro a enviar vence”;
- mantém a decisão humana e motivada;
- resolve o risco antes do sorteio.

Riscos:

- carga operacional;
- necessidade de SLA;
- risco de atrasar o certame;
- exige interface, papéis, auditoria, comunicação e possível recurso.

### D. Consolidação voluntária de contas

A pessoa autenticada solicita unir identidades, provando controle das credenciais ou passando por
recuperação institucional.

Em vez de reescrever inscrições, pode existir um ato append-only que declare que duas identidades
passam a representar a mesma pessoa consolidada.

Vantagens:

- resolve histórico fragmentado;
- preserva proveniência;
- pode permitir múltiplos e-mails por uma pessoa.

Riscos:

- desenho de autorização delicado;
- precisa de reversão ou contestação para consolidação equivocada;
- não resolve sozinho fraude anterior ao merge.

### E. Separar “conta de acesso” de “pessoa candidata”

Criar dois conceitos:

```text
Conta/Credencial → autentica
Pessoa candidata → representa o participante
Inscrição → pertence à pessoa candidata
```

Uma pessoa candidata poderia ter várias credenciais de acesso, e uma nova conta poderia pedir
associação segura à pessoa existente.

Vantagens:

- modela explicitamente o problema;
- histórico deixa de depender de um e-mail ou conta;
- permite diversos níveis de prova.

Riscos:

- mudança estrutural relevante;
- migração e compatibilidade complexas;
- é necessário definir como uma conta prova vínculo com a pessoa.

### F. Deduplicação apenas no universo do sorteio

Manter inscrições duplicadas, mas permitir somente uma participação por pessoa no mesmo recorte.

Vantagens:

- limita diretamente a vantagem.

Riscos:

- exige definir “mesma pessoa”;
- pode mascarar o problema em avaliação, classificação e convocação;
- CPF declarado continua não sendo prova suficiente;
- duas inscrições podem ter modalidades ou documentos divergentes, exigindo decidir qual vale.

## Hipótese inicial para avaliação

Uma direção potencialmente equilibrada — ainda não aprovada — seria combinar:

1. onboarding por e-mail sem senha;
2. múltiplas credenciais por identidade;
3. mecanismo seguro de recuperação/consolidação de histórico;
4. coincidência como pendência institucional, nunca como rejeição automática no envio;
5. bloqueio da publicação da relação de habilitados enquanto houver coincidência relevante sem
   decisão;
6. ato append-only e motivado que determine:
   - inscrições distintas de pessoas distintas; ou
   - inscrições da mesma pessoa e qual delas segue;
7. comunicação e possibilidade de contestação;
8. futura integração com provedor de identidade forte para reduzir análise manual.

Essa direção preserva a baixa fricção e evita que a duplicidade chegue ao sorteio, mas depende de
confirmar as regras institucionais.

## Entrega solicitada ao agente

Peço que produza:

1. análise do problema sob as perspectivas de produto, domínio, segurança, LGPD e operação;
2. como sistemas públicos, educacionais e de seleção normalmente equilibram e-mail simples, CPF,
   recuperação de conta e prevenção de duplicidade;
3. comparação das alternativas acima, incluindo vantagens, riscos e complexidade;
4. recomendação principal e alternativa de contingência;
5. modelo de identidade recomendado:
   - conta;
   - credencial;
   - pessoa;
   - inscrição;
   - vínculo ou consolidação;
6. momento adequado para prova forte ou decisão institucional;
7. workflow completo para CPF coincidente;
8. efeitos sobre sorteio, avaliação, classificação, recursos e convocação;
9. estratégia para consolidar o histórico existente sem perder autoria ou trilha;
10. tratamento das inscrições e identidades já existentes;
11. ameaças e casos de abuso;
12. decisões que precisam ser tomadas pelo usuário antes de especificar;
13. proposta de divisão em incrementos entregáveis;
14. cenários de aceitação indispensáveis.

Não assumir que tornar CPF único é a resposta. O objetivo é preservar a facilidade de entrada,
impedir vantagem indevida e permitir que a pessoa recupere todo o próprio histórico com segurança.
