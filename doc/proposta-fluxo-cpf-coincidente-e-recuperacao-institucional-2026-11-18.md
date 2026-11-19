# Proposta de fluxo para CPF coincidente e recuperação institucional

**Data:** 2026-11-18
**Natureza:** material para discussão; não constitui decisão de produto, especificação ou
autorização de implementação.

## Objetivo

Detalhar como a proposta para tratar inscrições com CPF coincidente pode se transformar em uma
jornada completa, incluindo:

- tela para a comissão visualizar e resolver os casos;
- comunicação com os candidatos envolvidos;
- contestação;
- travas para impedir que pendências produzam vantagem;
- união voluntária de contas;
- recuperação institucional quando a pessoa perdeu acesso ao e-mail antigo.

## Situação atual

Hoje o sistema apenas assinala `cpf_coincidente` na listagem administrativa de inscrições.

Ainda não existem:

- fila de pendências;
- item em “Minhas atividades”;
- tela de análise;
- ato institucional de decisão;
- comunicação específica;
- contestação;
- bloqueio do sorteio ou de atos posteriores;
- união de contas que já possuam inscrições;
- recuperação institucional do histórico.

Portanto, tudo o que segue é uma proposta a ser decidida e especificada.

## Capacidades previstas

| Capacidade | Prevista na proposta | Situação atual |
|---|---:|---|
| Tela para visualizar coincidências | Sim | Não existe |
| Pendência em “Minhas atividades” | Sim | Não existe |
| Comparação das inscrições lado a lado | Sim | Não existe |
| Decisão motivada da comissão | Sim | Não existe |
| Aviso aos candidatos envolvidos | Sim | Não existe |
| Contestação da decisão | Sim, ainda requer detalhamento | Não existe |
| Bloqueio da relação de habilitados | Sim | Não existe |
| Bloqueio antes de classificação e convocação | Sim | Não existe |
| União voluntária das contas | Sim | Não existe para contas com inscrições |
| Recuperação sem acesso ao e-mail antigo | Sim, conceitualmente | Não existe |

## Tela da comissão

A comissão deve ter uma fila própria de coincidências, organizada por Processo, Edital e recorte.

Exemplo:

```text
Coincidências de CPF

3 pendentes
├── Edital 12/2027 · Perfil Letras
│   ├── Inscrição ABC123 — enviada em 10/01
│   └── Inscrição DEF456 — enviada em 12/01
└── Edital 12/2027 · Perfis Letras e História
    └── Excede o limite de uma inscrição no Edital
```

Ao abrir um caso, a autoridade deve visualizar, conforme sua permissão:

- Edital e Perfis envolvidos;
- protocolos;
- datas dos envios;
- dados declarados;
- documentos pertinentes;
- se as contas foram voluntariamente vinculadas;
- telefone ou outros indícios já existentes, quando necessários;
- alcance da decisão;
- atos posteriores atualmente bloqueados.

A tela deve oferecer desfechos explícitos:

- `MESMA_PESSOA`;
- `PESSOAS_DISTINTAS`;
- `CPF_INCORRETO`;
- `USO_INDEVIDO`.

Não deve existir um botão genérico “resolver”, pois cada desfecho produz efeitos diferentes.

## Fluxo de decisão

### Mesma pessoa

O sistema aplica a regra previamente publicada no Edital, recomendando-se que siga a última
inscrição enviada dentro do prazo.

- uma inscrição segue;
- a outra fica sem efeito;
- nenhuma é apagada;
- a comissão informa o motivo;
- as contas envolvidas são notificadas;
- existe prazo para contestação.

A regra da última inscrição não deve ser universal ou oculta. Ela precisa constar no Edital ou em
outro fundamento normativo aplicável ao certame.

### Pessoas distintas

As duas inscrições seguem. O ato registra que a coincidência do CPF declarado não representa a
mesma pessoa.

### CPF incorreto

A instituição registra, por ato, o CPF conferido. O valor originalmente enviado deve permanecer
preservado; não pode haver reescrita silenciosa da inscrição.

### Uso indevido

A inscrição indevida fica sem efeito por decisão motivada. Eventual sanção adicional depende do
Edital e da política institucional.

## Travas previstas

O gate deve bloquear somente o recorte afetado, e não o Processo inteiro.

Enquanto houver coincidência relevante sem decisão, o sistema deve impedir:

- publicar ou congelar a relação de habilitados daquele recorte;
- executar o sorteio daquele recorte;
- publicar a primeira classificação ou resultado que consuma as inscrições;
- convocar duas inscrições coincidentes sem decisão;
- ultrapassar o teto por candidato declarado pelo Edital.

Recortes vizinhos sem pendência continuam normalmente.

A recusa deve ser acionável. Exemplo:

> Não é possível publicar a relação da ampla concorrência. Existem 2 coincidências de CPF sem
> decisão. Resolver coincidências.

Não basta mostrar uma advertência escondida ou permitir que a pendência seja ignorada.

## Comunicação prevista

Há pelo menos quatro comunicações diferentes.

### 1. Nascimento da coincidência

Informa às contas que há outra inscrição com o mesmo CPF, sem revelar dados da outra pessoa.

A mensagem não deve:

- acusar fraude;
- revelar o outro e-mail;
- revelar protocolo da outra inscrição;
- expor documentos ou outros dados pessoais.

### 2. Decisão institucional

Comunica:

- desfecho;
- motivo;
- efeitos sobre a inscrição;
- prazo;
- caminho de contestação.

### 3. União voluntária

Avisa todas as credenciais das contas associadas, descrevendo o efeito e o caminho para contestar
ou desfazer o vínculo.

### 4. Recuperação institucional

Avisa o endereço antigo e o atual sobre:

- o pedido;
- o prazo de segurança;
- a decisão final;
- o caminho para contestar.

## Contestação

O fluxo que torna uma inscrição sem efeito precisa oferecer contestação pelo canal do candidato.

O detalhamento ainda depende de decisão, mas deve assegurar:

- prazo explícito;
- envio pelo portal;
- confirmação de recebimento;
- análise por autoridade competente;
- decisão motivada;
- sucessão do ato anterior, sem edição ou exclusão;
- comunicação do resultado.

Comunicação e contestação devem entrar no mesmo incremento que introduzir o gate e o ato de
decisão. Não devem ser adiadas para uma entrega posterior.

## União voluntária de contas

Quando a pessoa ainda controla os dois e-mails, a recuperação institucional não é necessária.

O fluxo recomendado é:

1. entrar em uma das contas;
2. escolher “Tenho outra conta”;
3. informar o e-mail da outra conta;
4. receber um código nesse endereço;
5. provar o controle das duas credenciais;
6. visualizar antecipadamente os efeitos;
7. confirmar o vínculo.

O sistema grava um ato append-only associando as contas. Ele não altera o `identity_subject` das
inscrições.

Depois do vínculo:

- qualquer credencial válida mostra o histórico consolidado;
- uma inscrição por Perfil é contada entre todas as contas vinculadas;
- o teto do Edital é contado por pessoa;
- a autoria original de cada inscrição permanece intacta;
- a união pode ser desfeita somente por ato sucessor.

## Recuperação institucional

A recuperação institucional é usada quando a pessoa afirma possuir inscrições antigas, mas não
controla mais o e-mail vinculado à conta anterior.

Ela é a operação de maior risco do desenho, porque pode conceder acesso a documentos e a todo o
histórico de outra conta. Por isso, deve ser implementada depois da união voluntária.

### 1. Solicitação

Na conta atual, a pessoa escolhe:

> Recuperar inscrições de uma conta antiga

Ela pode informar elementos para localizar o histórico, como:

- e-mail antigo, caso se recorde;
- Edital ou Processo;
- protocolo de inscrição;
- outros identificadores permitidos pela instituição.

A resposta não pode confirmar imediatamente que a conta ou a inscrição existe.

### 2. Evidências

A pessoa apresenta a prova definida institucionalmente. Uma proposta inicial inclui:

- documento de identificação;
- documento de CPF;
- protocolos ou comprovantes disponíveis;
- dados que possam ser confrontados com documentos já enviados.

Perguntas de conhecimento, como data de nascimento, telefone ou endereço, não devem ser usadas como
prova principal, pois terceiros podem conhecer esses dados.

### 3. Registro do pedido

O pedido nasce com:

- conta solicitante;
- contas e inscrições possivelmente relacionadas;
- instante;
- evidências apresentadas;
- situação;
- prazo;
- trilha de todas as ações.

Os documentos da recuperação devem ter acesso restrito e política de retenção definida.

### 4. Aviso preventivo

O sistema envia aviso para:

- e-mail antigo;
- e-mail atual;
- demais credenciais das contas envolvidas, se houver.

O aviso informa que alguém solicitou a associação do histórico e oferece um caminho de
contestação. Ele não entrega documentos nem dados completos da outra conta.

### 5. Prazo de segurança

A associação não acontece imediatamente. Deve existir um prazo institucional para:

- o endereço antigo contestar;
- a equipe examinar as evidências;
- detectar pedido fraudulento.

A duração ainda precisa ser decidida.

A contestação pelo endereço antigo também não cancela automaticamente o pedido, pois o endereço
pode ter sido reciclado ou comprometido. Ela leva o caso para análise reforçada.

### 6. Análise institucional

Uma pessoa com capacidade explícita — por exemplo, `identidade:recuperar` — compara:

- documentos da solicitação;
- dados congelados nas inscrições;
- documentos anteriormente apresentados;
- histórico das credenciais;
- eventuais contestações.

Essa permissão deve ser diferente da capacidade de decidir coincidências do certame. Recuperar uma
conta concede acesso a dados pessoais históricos e exige segregação maior.

### 7. Decisão

A autoridade pode:

- aprovar;
- recusar;
- solicitar complementação;
- encerrar por desistência;
- encaminhar para análise de possível uso indevido.

Toda decisão exige motivo.

### 8. Efeito da aprovação

A aprovação cria um vínculo append-only com fundamento `DECISAO_INSTITUCIONAL`.

Ela não:

- altera o `identity_subject` das inscrições;
- transfere documentos;
- reescreve auditoria;
- apaga a conta antiga;
- move credenciais silenciosamente.

Depois do vínculo, as contas passam a compor a mesma pessoa derivada. A conta atual pode visualizar
o histórico das contas vinculadas, preservando qual conta praticou cada ato.

### 9. Notificação e reversão

Todas as credenciais recebem o resultado.

Se a decisão estiver errada, ela não é editada nem apagada. Outro ato sucede o primeiro, desfazendo
o vínculo e preservando o período em que esteve vigente.

## Decisões ainda necessárias para a recuperação

Antes de especificar, ainda é necessário definir:

- quem pode decidir;
- quais documentos constituem prova suficiente;
- prazo de espera;
- prazo e canal de contestação;
- como lidar com e-mail antigo reciclado;
- quando pedir complementação;
- retenção dos documentos da recuperação;
- SLA para não prejudicar prazo de inscrição ou recurso;
- se o vínculo aprovado permite imediatamente abrir documentos sensíveis;
- se determinadas recuperações exigem dupla conferência por dois agentes.

## Capacidades e segregação de responsabilidades

As permissões não devem ficar rigidamente associadas a cargos. A proposta deve definir capacidades
explícitas e negadas por padrão, por exemplo:

- `coincidencia:consultar`;
- `coincidencia:decidir`;
- `coincidencia:revisar`;
- `identidade:recuperar`.

A presidência da comissão pode receber a capacidade de decisão por padrão, mas o domínio deve
representar a responsabilidade, não o cargo.

A recuperação institucional deve ser segregada da decisão sobre a inscrição porque concede acesso
a um conjunto maior de dados pessoais.

## Sequência de implementação recomendada

### Incremento 1 — Proteção do certame

Entregar de ponta a ponta:

```text
detectar
→ mostrar à comissão
→ decidir com motivo
→ comunicar ao candidato
→ permitir contestação
→ impedir avanço enquanto pendente
```

Inclui:

- detecção das coincidências relevantes;
- fila e tela da comissão;
- item em “Minhas atividades”;
- ato append-only;
- comunicação;
- contestação;
- gates no sorteio e nos atos posteriores;
- efeitos nas leituras de avaliação, classificação e convocação.

### Incremento 2 — Substituição da própria inscrição

Permitir que uma nova inscrição enviada dentro do prazo suceda a anterior:

```text
inscrição anterior → histórica, sem efeito
inscrição mais recente → vigente
```

Nada é apagado. A regra precisa estar previamente publicada no Edital.

### Incremento 3 — União voluntária

Permitir a associação das contas mediante prova de controle das duas credenciais, com histórico
consolidado e autoria preservada.

### Incremento 4 — Recuperação institucional

Permitir a recuperação sem acesso ao e-mail antigo, com prova, prazo, análise, notificação e decisão
motivada.

## Princípios da proposta

- CPF declarado continua sendo sinal, não prova de titularidade.
- Ninguém é impedido de enviar porque outra conta declarou o mesmo CPF.
- Coincidência não resolvida não pode produzir vantagem.
- Nenhuma inscrição ou ato histórico é apagado ou reescrito.
- Toda decisão que afeta direito é motivada, comunicada e contestável.
- O candidato acessa o próprio histórico por vínculo comprovado, não pela mera igualdade do CPF.
- A recuperação sem o e-mail antigo é institucional e proporcional ao risco.
- As permissões são explícitas, escopadas e negadas por padrão.

## Síntese para decisão

A proposta já contempla tela da comissão, comunicação e travas, mas esses elementos ainda precisam
ser especificados e implementados. O primeiro incremento deve ser completo: detectar, decidir,
comunicar, permitir contestação e impedir avanço.

A recuperação institucional deve vir depois da união voluntária. Ela associa contas por ato
append-only, sem alterar inscrições antigas, e exige evidência, aviso ao endereço anterior, prazo de
segurança, autoridade específica e possibilidade de reversão por ato sucessor.
