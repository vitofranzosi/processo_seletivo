# Feature Specification: Configurar, verificar e testar o correio e o Ollama na implantação

**Feature Branch**: `claude/auditoria-configuracoes-sistema-cc4664`, a mesma da auditoria que a
originou, sobre a `main` em `6fac8189`.

**Created**: 2026-10-14

**Status**: Draft. Escopo recortado pelo usuário em 14/10/2026 às lacunas que o
[PR #281](https://github.com/vitofranzosi/processo_seletivo/pull/281) deixa. Sem plano nem tarefas.

**Input**: a seção 5 da
[auditoria de configurações](../../doc/auditoria-configuracoes-do-sistema-2026-10-14.md), com o
recorte do usuário: *"aproveitar os comandos existentes e entregar um caminho simples para
configurar → verificar → testar, sem criar uma plataforma de diagnóstico. A entrega deve permitir à
TI configurar e verificar e-mail e Ollama sem consultar código ou juntar instruções de várias
specs. [...] Se a documentação e os comandos existentes já resolverem a necessidade, [...] não crie
código apenas para justificar a 073."*

---

## Por que esta feature existe

### O problema

Configurar o correio e o Ollama é raro, mas errar neles é fácil e caro. O e-mail é o único fator de
autenticação do candidato: um servidor mal configurado tranca todos eles.

O #281 resolveu a dispersão das instruções:

- o roteiro de troca do assistente na máquina da equipe;
- o procedimento de troca do servidor de correio (§16.5 do guia de implantação);
- as referências vencidas e o `.env.example`.

**Restam quatro lacunas**, todas verificadas na auditoria:

- **O Ollama de produção não tem instrução de implantação.** O guia não cita nenhuma `ASSISTENTE_*`,
  e o roteiro do #281 é da máquina da equipe.
- **Nenhum procedimento ensina a ver a configuração em uso.** O comando genérico que a mostraria
  imprime também a chave da aplicação e a senha do correio.
- **Nenhum procedimento separa o teste de conexão da ação real.** O envio de teste sempre envia. A
  verificação do assistente sempre faz uma inferência, que carrega o modelo na GPU.
- **Dois comportamentos enganam quem configura.** O servidor de correio vazio passa na inicialização
  e só falha no primeiro envio. E um nome de serviço desconhecido, como `Ollama` com maiúscula,
  aparece como "nenhum serviço configurado".

**Os comandos que já existem cobrem as três primeiras**, com exemplos completos. A auditoria os
ensaiou (§4.3):

- uma leitura fechada da configuração mostra o que o processo carregou sem revelar a senha;
- a conexão de correio do framework conecta, negocia a segurança e autentica sem enviar;
- duas leituras do Ollama não pedem inferência.

Por isso esta feature **não cria comando novo** (D-002).

### O ator e o canal

O ator é **quem implanta e opera o servidor** — a pessoa da TI. O canal dele é o terminal do
servidor, pelos scripts de operação do guia. Enquanto a gestão não tiver autenticação de produção
(gap B-1 do guia), é também o **único** canal que alcança produção. É por esse canal que a feature
se demonstra (princípio VI).

**A capacidade que ela amplia:** a TI deixa o correio e o Ollama prontos e comprovados seguindo uma
seção só do guia, e não junta instruções nem lê código.

### O que esta feature não cobre, deliberadamente

- **Comando agregador de diagnóstico.** Especifica-se com a página, se ela vier (D-002).
- **A página "Configuração e diagnóstico" da gestão**, que é evolução depois do B-1.
- **Envio de teste pela interface.** Depende de emendar a `FR-084` da `010`.
- **Edição de configuração pela interface**, e qualquer guarda de segredo no banco.
- **Suporte a SSL implícito no correio.** Esta feature ensina a reconhecer a incompatibilidade
  (D-004). Suportá-la depende da resposta do setor de correio.
- **O canal de atendimento por unidade**, registrado em `doc/pendencias-da-060.md`.
- **O OpenRouter em produção**, que a configuração de produção recusa, e a troca de serviço na
  máquina da equipe, que é do #281.
- **O próprio B-1**, o monitoramento contínuo e a instalação da VM.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A TI configura o correio de produção e o comprova em etapas (Priority: P1)

A pessoa da TI recebeu do setor de correio o servidor, a porta, a segurança e a conta. Ela segue a
seção única do guia, nesta ordem:

1. preenche o arquivo de ambiente;
2. roda o pré-voo;
3. vê a configuração em uso;
4. testa a conexão sem enviar nada;
5. reinicia o serviço e confirma que ele adotou o arquivo;
6. envia uma mensagem de teste para uma caixa da equipe.

Em cada falha, uma tabela de sintomas diz a causa provável e a ação.

**Why this priority**: sem correio, nenhum candidato entra. É o primeiro bloqueio de toda
implantação.

**Independent Test**: num servidor de homologação preparado pelo guia, com o correio em branco, a
pessoa chega à mensagem recebida seguindo só a seção.

**Acceptance Scenarios**:

1. **Given** o mecanismo de envio real com o servidor de correio vazio, **When** o serviço inicia ou
   o pré-voo roda, **Then** a inicialização é recusada com a variável e a ação, como as demais
   recusas de produção.
2. **Given** a configuração preenchida, **When** a TI roda o comando de configuração em uso da
   seção, **Then** vê o servidor, a porta, a segurança, o tempo-limite, a conta e o remetente, **and**
   a senha aparece só como "presente" ou "ausente".
3. **Given** a conta com senha errada, **When** a TI roda o teste de conexão da seção, **Then** o
   teste falha na autenticação, e a tabela de sintomas a leva a "credencial recusada", **and**
   nenhuma mensagem é enviada.
4. **Given** um servidor que só aceita SSL implícito, **When** a TI roda o teste de conexão, **Then**
   ele falha depois do tempo-limite configurado, e a tabela de sintomas nomeia a incompatibilidade
   de segurança e a ação — e não "a porta 465".
5. **Given** o arquivo editado, **When** a TI segue o passo de reinício, **Then** ela confirma pelo
   comando da seção que o serviço subiu depois da última mudança do arquivo.
6. **Given** a conexão testada sem falha, **When** a TI envia a mensagem de teste, **Then** a seção
   diz que aceita pelo servidor não é entregue, e que é preciso conferir a caixa de entrada e o spam.

---

### User Story 2 — A TI configura o Ollama de produção e o comprova sem disparar inferência (Priority: P1)

Com o endereço do Ollama, o nome do modelo e a quantização, a pessoa da TI preenche o bloco do
assistente no arquivo de ambiente. Ela vê a configuração em uso e testa a conexão com duas leituras
que não pedem inferência. Só então roda a verificação existente, que faz a conversa sintética.

**Why this priority**: o Ollama é o único serviço que produção aceita para o assistente, e hoje
nenhum documento da implantação o descreve.

**Independent Test**: com um Ollama alcançável e outro inalcançável, a pessoa distingue os dois
casos pela seção, sem consultar código.

**Acceptance Scenarios**:

1. **Given** o serviço escrito `Ollama`, **When** a TI roda a verificação existente, **Then** ela lê
   que o serviço é desconhecido, com o valor escrito e os aceitos, e não que nenhum serviço está
   configurado.
2. **Given** o endereço com o sufixo do caminho da API, **When** a TI testa a conexão, **Then** a
   leitura falha, e a tabela de sintomas mostra a forma certa do endereço.
3. **Given** o Ollama alcançável e o modelo instalado, **When** a TI testa a conexão, **Then** vê a
   versão e o modelo na lista, **and** nenhuma inferência é feita.
4. **Given** a conexão sem falha, **When** a TI roda a verificação existente, **Then** a saída
   termina em "Divergências: nenhuma", ou a seção diz o que fazer com cada divergência.
5. **Given** o bloco do assistente com o piloto desligado, **When** a TI segue a seção, **Then** a
   seção diz que o assistente não atende ninguém até a chave ser ligada, e que ligá-la é decisão do
   piloto, e não da implantação.

---

### Edge Cases

- **O servidor não tem rede de saída para o correio ou o Ollama.** O teste de conexão falha por
  recusa ou por tempo, e a tabela de sintomas distingue os dois.
- **O arquivo foi editado e o serviço não foi reiniciado.** O teste pelo script de operação prova o
  arquivo, e não o serviço em execução. A seção o diz, e confirma o reinício antes do envio de teste.
- **O tempo-limite do assistente está acima do limite do servidor de aplicação**, ou há serviço
  externo em produção. São recusas que já existem, e o pré-voo as mostra.
- **O nome da variável foi digitado errado no arquivo.** O valor some sem aviso, e a aplicação usa
  o padrão. A configuração em uso é o que revela isso.

---

## Requirements *(mandatory)*

Esta feature abre em **FR-1650** e **SC-620**. A `072` vai até FR-1640 e SC-607.

### Functional Requirements

#### A seção do guia

- **FR-1650**: O guia de implantação MUST ter uma seção única "Configurar, verificar e testar", para
  o correio e para o Ollama em produção. A ordem é: preencher → pré-voo → configuração em uso →
  testar a conexão → reiniciar e confirmar → testar o envio ou a inferência. Ela incorpora o §16.5,
  e não o duplica.
- **FR-1651**: A seção MUST trazer exemplos completos do bloco de correio e do bloco do assistente
  do arquivo de ambiente de produção, coerentes com as variáveis que o sistema lê. Os valores a
  substituir vão marcados, e nenhum segredo aparece. No bloco do assistente entram a regra de
  produção — só o Ollama, com tempo-limite de no máximo 110 s — e a forma do endereço.
- **FR-1652**: A seção MUST trazer um comando, feito só com o que existe, que mostra a configuração
  em uso do correio, do atendimento, dos avisos e do assistente. Ele imprime os valores não secretos
  e, de cada segredo, só "presente" ou "ausente". Ele MUST NOT usar comando que imprima segredos.
- **FR-1653**: A seção MUST trazer, como passos distintos e explícitos:
  - o **teste de conexão** do correio: conecta, negocia a segurança configurada e autentica, sem
    enviar;
  - o **envio de teste**;
  - o **teste de conexão** do Ollama: versão e modelo instalado, sem inferência;
  - a **verificação com inferência** que já existe.

  Nenhum passo de conexão dispara o envio ou a inferência.
- **FR-1654**: A seção MUST trazer uma tabela de sintomas → causa provável → ação, para os testes de
  conexão e para as divergências da verificação existente. Ela cobre, no mínimo:
  - conexão recusada;
  - tempo esgotado;
  - segurança não negociada;
  - credencial recusada;
  - Ollama inalcançável;
  - endereço na forma errada;
  - modelo não instalado;
  - quantização divergente;
  - contexto menor que o configurado.
- **FR-1655**: A linha de tempo esgotado no correio MUST nomear a **incompatibilidade de segurança**:
  o sistema só suporta STARTTLS, e o servidor pode exigir SSL implícito. A ação é pedir ao setor de
  correio uma porta com STARTTLS, ou registrar a necessidade de suporte a SSL implícito. A seção MUST
  NOT apresentar a porta 465 como o erro.
- **FR-1656**: A seção MUST dizer que os testes pelo script de operação provam o **arquivo**, e não
  o serviço em execução. E MUST trazer o comando que confirma que o serviço subiu depois da última
  mudança do arquivo, antes do envio de teste.
- **FR-1657**: A seção MUST ser suficiente sozinha. Ela pode remeter a outras seções do próprio
  guia, mas não a código nem a documentos de `specs/`.
- **FR-1658**: O README MUST apontar, para o desenvolvimento, o roteiro de troca do #281 e esta
  seção. E MUST dizer o que difere entre os dois ambientes: o correio de console, o seletor de
  identidade e o OpenRouter, admitido só em desenvolvimento.

#### As duas correções

- **FR-1660**: Com o mecanismo de envio real, a configuração de produção MUST recusar a
  inicialização quando o servidor de correio estiver vazio. A mensagem nomeia a variável e a ação,
  como as demais recusas.
- **FR-1661**: A verificação do serviço de inferência MUST dizer "serviço desconhecido", com o valor
  escrito e os aceitos, quando o serviço configurado não for um dos conhecidos. "Nenhum serviço
  configurado" fica só para o valor vazio.

### LGPD

A seção e as correções não leem dado pessoal. O único dado que entra é o destinatário do envio de
teste, digitado por quem roda, que deve ser uma caixa da equipe e não é gravado. O comando de
configuração em uso não imprime segredo, e o endereço do atendimento é público por natureza.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-620**: Uma pessoa da TI que não participou do desenvolvimento configura e comprova o correio
  e o Ollama num servidor de homologação. Ela segue só a seção, com **zero** consultas a código ou a
  `specs/`. Ponto de partida: até 30 minutos, sem contar a espera pelo setor de correio.
- **SC-621**: Com segredos plantados no arquivo de ambiente, os valores deles aparecem **zero** vezes
  na saída de todos os comandos da seção.
- **SC-622**: Os testes de conexão fazem **zero** envios e **zero** inferências. Verifica-se pelo
  coletor de correio vazio e pelo modelo não carregado no Ollama.
- **SC-623**: Cada sintoma da tabela da FR-1654, provocado em homologação, leva à causa e à ação
  escritas. Meta: todos os sintomas listados.
- **SC-624**: Cada correção tem teste automatizado. O servidor de correio vazio recusa a
  inicialização de produção, e o serviço com maiúscula produz "serviço desconhecido".

---

## Decisões

### D-001 — Linha de comando agora, página depois do B-1

A página não ajuda quem implanta enquanto a gestão responder 503 em produção. O terminal é o canal
que a TI já usa. A página fica registrada como evolução, e não descartada.

### D-002 — Sem comando novo: exemplos completos sobre os comandos que existem

A primeira revisão da auditoria propunha um comando agregador. O ensaio da §4.3 mostrou que os
comandos existentes, com exemplos completos, cobrem os três motivos dela:

- **a configuração em uso**, por uma leitura fechada que não imprime segredo;
- **as recusas uma de cada vez**, que o pré-voo já repete em segundos, sem reiniciar;
- **a conexão sem a ação real**, pela conexão de correio do framework e por duas leituras do Ollama.

O agregador só se paga quando a página existir, porque ela não roda comandos no terminal. Ele se
especifica junto com ela.

### D-003 — Testes externos em dois níveis, e só a pedido

Ver a configuração é ler. Testar a conexão contata o serviço sem efeito: nada é enviado e nada é
inferido. Testar a ação real envia uma mensagem ou carrega o modelo. Cada nível é um passo próprio
da seção.

### D-004 — A porta não é o erro; a incompatibilidade é

O sistema suporta STARTTLS e não SSL implícito. A porta convencional de SSL implícito só sugere a
incompatibilidade, e o teste de conexão a revela. Suportar SSL implícito depende do setor de correio,
e fica fora desta feature.

### D-005 — As duas correções corrigem o que engana, e não acrescentam capacidade

O servidor vazio que sobe e a mensagem "nenhum serviço configurado" para um valor desconhecido
mandam quem configura procurar no lugar errado. Corrigi-los custa uma regra e uma mensagem, e
nenhuma das duas depende da seção.

---

## Assumptions

- A pessoa da TI roda os comandos pelo script de operação do guia, que carrega o arquivo de ambiente
  de produção. O que eles mostram é o que **esse** processo carregou.
- O servidor alcança o servidor de correio e o Ollama pela rede.
- O #281 entra antes. Esta seção parte do §16.5 dele e o incorpora.
- O ponto de partida do SC-620 é ajustável pelo responsável pelo produto antes da sessão conduzida.
- Ligar o piloto do assistente em produção continua decisão do piloto da `071`. Esta feature ensina
  a deixar o serviço pronto e comprovado, e não a ligá-lo.
