# Estudo e auditoria da proposta de identidade e CPF coincidente

**Data:** 18/11/2026
**Situação:** análise prévia à especificação; não representa decisão institucional
**Veredito de segurança:** **SEGURAR** a passagem direta para a spec enquanto os achados P1 deste
documento não forem resolvidos
**Escopo:** acesso do candidato por e-mail, coincidência de CPF, limite de inscrições por Edital,
escolha de inscrição representante, associação de identidades e recuperação institucional

## 1. Resumo executivo

A proposta tem uma direção válida: manter o acesso sem senha por e-mail, não recusar o envio porque
outra identidade declarou o mesmo CPF, preservar as inscrições originais, impedir vantagem duplicada
e deixar o Gov.br fora do primeiro incremento. Esses pontos são compatíveis com a Constituição e com
a arquitetura atual.

Ela, porém, **ainda não está consistente o bastante para virar especificação**. O problema principal
é conceitual: os textos afirmam que o CPF é apenas um sinal e, ao mesmo tempo, fazem a simples
coincidência do CPF declarado formar uma única “participação”, limitar Perfis e bloquear atos. Isso
produz um vínculo e um efeito administrativo antes de haver prova ou decisão institucional, em
conflito com as regras vigentes de que CPF não prova titularidade, nenhum vínculo nasce de afirmação
e o sistema não decide qual inscrição coincidente vale.

Há ainda quatro bloqueadores: a associação ampla de contas contradiz a proibição vigente de fundir
identidades; não há base normativa definida para escolher uma inscrição representante; a recuperação
institucional ainda não tem prova, prazo, retenção e segregação suficientemente definidos; e os três
documentos divergem em pontos que afetam direitos.

### Recomendação consolidada

Manter o acesso facilitado por e-mail, mas separar quatro conceitos:

1. **identidade de acesso**, opaca, dona das inscrições e autenticada por e-mails verificados;
2. **coincidência de CPF**, que abre um caso de análise, mas não cria vínculo nem altera titularidade;
3. **decisão sobre participação efetiva**, produzida por autorregularização com prova suficiente ou
   por ato institucional motivado;
4. **associação de histórico**, que concede acesso cruzado somente mediante prova mais forte e em
   fluxo separado da decisão sobre o certame.

O caminho recomendado não é “uma conta por CPF declarado”. Sem verificação independente do CPF,
essa unicidade permitiria que quem conhece o CPF de outra pessoa reservasse ou sequestrasse sua conta.
Uma eventual unicidade por CPF deve ficar para uma fase futura, associada a CPF **verificado**, e não
ao valor apenas informado no formulário.

## 2. Fontes e método

### 2.1 Propostas auditadas

- [Proposta consolidada](proposta-consolidada-cpf-coincidente-2026-11-18.html)
- [Proposta resumida](proposta-resumida-cpf-coincidente-e-identidade-2026-11-18.md)
- [Fluxo e recuperação institucional](proposta-fluxo-cpf-coincidente-e-recuperacao-institucional-2026-11-18.md)

### 2.2 Autoridades e evidências do projeto

- [Constituição](../.specify/memory/constitution.md)
- [Spec 010 — Área do candidato](../specs/010-area-do-candidato/spec.md)
- [Spec 015 — Ordenação e classificação](../specs/015-ordenacao-e-classificacao/spec.md)
- [Modelo de identidade](../backend/processo_seletivo/identidade/models.py)
- [Associação de credenciais](../backend/processo_seletivo/identidade/application/associacao.py)
- [Modelo de inscrição](../backend/processo_seletivo/inscricoes/models.py)
- [Envio da inscrição](../backend/processo_seletivo/inscricoes/application/submissao.py)
- [Consulta administrativa](../backend/processo_seletivo/inscricoes/application/consulta.py)
- [Cálculo da classificação](../backend/processo_seletivo/classificacao/application/calculo.py)
- [Relação do sorteio](../backend/processo_seletivo/sorteios/application/relacao.py)
- [Apuração da ocupação](../backend/processo_seletivo/ocupacao/domain/apuracao.py)

Foi feita inspeção estática das regras e do código. Não foram executados testes, migrations nem
alterações funcionais. Afirmações sobre o comportamento atual são evidências do repositório;
ameaças e efeitos futuros são inferências que a especificação deverá transformar em requisitos e
testes.

### 2.3 Limitações

Esta não é uma análise jurídica do Edital ou da LGPD. A autoridade institucional deverá validar a
base normativa, o contraditório e os prazos. Como não existe implementação da proposta, não foi
possível auditar esquema novo, consultas, interface, configurações, dependências, segredos ou
infraestrutura, nem executar testes dinâmicos. Esses itens precisam de nova revisão de segurança no
plano e na implementação, antes do QA.

## 3. Estado atual confirmado

### 3.1 Identidade, credencial e CPF

O sistema já diferencia corretamente:

- `CandidateIdentity.subject`: identificador opaco e estável que decide a titularidade;
- `CandidateEmail`: credencial cujo controle foi provado, única entre identidades;
- `cpf_normalizado`: dado declarado, não único e não usado como credencial.

Uma identidade pode ter vários e-mails verificados. Um e-mail canônico pertence a no máximo uma
identidade. O CPF não é único porque duas identidades podem declarar o mesmo número.

O fluxo atual permite retomar uma identidade anterior somente quando existe uma correspondência
histórica encontrada por outro caminho e o CPF apenas a confirma. Ele não cria vínculo para alguém
que simplesmente informou um CPF conhecido.

### 3.2 Inscrição e limite do Edital

Existe restrição de banco para uma inscrição por `(identity_subject, Edital, Perfil)`, em qualquer
estado. Ela sustenta a idempotência da abertura de rascunho e deve permanecer.

O teto `maxInscricoesPorCandidato`, quando publicado no Edital, conta hoje as inscrições submetidas
do mesmo `identity_subject` no Edital. Portanto, identidades diferentes que declaram o mesmo CPF
conseguem, atualmente, contornar esse teto.

A Constituição permite inscrições em mais de um Perfil do mesmo Edital, salvo restrição expressa
do próprio Edital. Assim:

- sem teto publicado, múltiplos Perfis são permitidos;
- com teto publicado, o limite é regra normativa versionada do Edital;
- uma solução nova não pode impor universalmente “um Perfil por pessoa”.

### 3.3 CPF coincidente

A regra vigente exige que duas inscrições de identidades diferentes com o mesmo CPF sejam aceitas
no envio, que a gestão veja uma sinalização e que o sistema não decida automaticamente qual vale.

A detecção existente alcança inscrições submetidas do mesmo CPF no mesmo Edital e Perfil. Ela só
assinala a coincidência: ainda não há caso persistente, decisão, contestação, estado pendente nem
gate operacional.

### 3.4 Efeito além do sorteio

Os fluxos posteriores usam a **inscrição** como unidade: avaliação, resultado, classificação,
recurso, relação de sorteio, ocupação e convocação referenciam a inscrição. A chave usada na
ocupação também é o identificador da inscrição, não uma pessoa civil consolidada.

Logo, identidades diferentes com o mesmo CPF podem produzir trajetórias independentes mesmo em
processos sem sorteio. Os riscos incluem duas análises documentais, duas tentativas de avaliação,
aproveitamento do melhor resultado, dois recursos e duas posições ou convocações.

## 4. Confronto com a Constituição

| Princípio | Avaliação | Condição para consistência |
|---|---|---|
| I — Linguagem e domínio | **Parcial** | Definir sem ambiguidade `identidade`, `credencial`, `coincidência`, `participação efetiva`, `inscrição representante` e `associação de histórico`. “Conta”, “pessoa”, “candidato” e “participação” não podem alternar como sinônimos. |
| II — Integridade normativa e temporalidade | **Parcial** | A regra de limite e representação deve estar na versão do Edital e não pode reinterpretar silenciosamente inscrições ou resultados históricos. Inscrições originais e atos devem permanecer imutáveis. |
| III — Segurança, dados e auditoria | **Não atendido ainda** | CPF declarado não pode conceder acesso nem criar vínculo. Recuperação exige menor privilégio, prova proporcional, retenção, notificação, contestação e auditoria append-only. |
| IV — Regras explícitas e consistência | **Não atendido ainda** | Coincidência, análise, contestação e decisão precisam de máquina de estados, comandos transacionais e tratamento de concorrência. Flags dispersas e filtros opcionais nos leitores não bastam. |
| V — Rastreabilidade e qualidade | **Não atendido ainda** | As divergências com a spec 010 devem ser emendadas explicitamente antes da implementação. Todos os consumidores posteriores precisam de requisitos e testes de regressão. |
| VI — Jornada completa | **Parcial** | A proposta contempla candidato e gestão, mas ainda não fecha prazo, ausência de resposta, contestação, erro de CPF e recuperação sem e-mail antigo de ponta a ponta. |

### Invariante de múltiplos Perfis

A agregação por `(Edital, CPF)` só é admissível para aplicar uma restrição **expressamente publicada**.
Ela não pode reduzir múltiplos Perfis por padrão. Se o teto do Edital for dois, por exemplo, duas
participações podem seguir; se não houver teto, a coincidência entre Perfis não representa infração.

O ponto ainda não resolvido é o que significa “por candidato” quando o CPF não é verificado. A regra
publicada precisa declarar o critério administrativo, e a solução precisa preservar contraditório e
correção de erro antes de retirar efeito de uma inscrição.

## 5. Compatibilidade com as regras vigentes

### 5.1 Pontos compatíveis

- Manter autenticação sem senha por código enviado ao e-mail.
- Deixar o Gov.br fora do primeiro incremento.
- Aceitar o envio mesmo quando outra identidade declarou o CPF.
- Não cancelar nem escolher inscrição apenas por coincidência.
- Não reescrever `identity_subject` nem dados de inscrição submetida.
- Preservar a restrição de uma inscrição por identidade, Edital e Perfil.
- Registrar decisões e associações como atos históricos, motivados e auditáveis.
- Restringir gates ao recorte realmente afetado.
- Comunicar os envolvidos sem revelar dados da outra identidade.
- Exigir permissão explícita e escopo para decisão e recuperação.

### 5.2 Conflitos diretos ou potenciais

#### CPF declarado formando automaticamente uma participação

A proposta consolidada diz que `(Edital, Perfil, CPF normalizado declarado)` forma uma única
participação. Embora chame o agrupamento de provisório, ele já limita trajetórias e bloqueia atos.
Isso contradiz:

- P-003 e FR-006/FR-007 da spec 010: CPF declarado não prova titularidade;
- P-007: nenhum vínculo nasce de afirmação;
- FR-066: a decisão sobre qual inscrição vale é institucional;
- a demonstração de segurança da spec 010: terceiro que conhece o CPF não pode reservar ou impedir
  a participação legítima.

**Correção recomendada:** a coincidência deve criar um `CasoDeCoincidencia` ou equivalente, não uma
participação única. A participação efetiva somente nasce ou é limitada depois de:

1. prova de controle das identidades envolvidas e escolha voluntária; ou
2. decisão institucional motivada, com base normativa, comunicação e contestação.

O CPF pode disparar o caso e um gate proporcional; não pode, sozinho, produzir a conclusão de que
as inscrições são da mesma pessoa.

#### Associação de contas e visualização consolidada

A spec 010 proíbe fundir identidades e determina que uma identidade não visualize inscrição de
outra. A proposta de associação append-only é tecnicamente melhor do que reescrever titularidade,
mas ainda muda a autorização: uma credencial passa a alcançar patrimônio que pertence a outro
`subject`.

Isso não é uma extensão neutra. Exige emenda explícita da spec 010, novo modelo de autorização e
prova de que o vínculo foi autorizado. A associação não pode nascer da coincidência de CPF nem da
decisão da comissão sobre qual inscrição participa do certame.

#### Inscrição representante e “vale a última”

Não existe hoje regra geral permitindo substituir inscrição submetida. Ela é imutável e produz ato
administrativo. “Vale a última” só pode existir como novo ato que declara efeito entre inscrições
preservadas, e apenas quando:

- a mesma pessoa foi comprovada;
- a norma do Edital autoriza a escolha ou sucessão;
- o marco temporal e os efeitos estão definidos;
- não há aproveitamento de avaliação, resultado ou informação obtida entre as tentativas.

Ela nunca pode escolher entre identidades apenas porque compartilham CPF. Também não pode ser
aplicada retroativamente a Edital publicado que não contenha a regra.

#### Correção de CPF

O CPF da identidade congela após a primeira inscrição enviada, e a inscrição submetida é imutável.
Portanto, “corrigir CPF” não pode atualizar a inscrição original. A solução compatível é um ato
institucional que registre o valor declarado, o valor reconhecido para efeitos futuros, a evidência,
o responsável, o instante, o alcance e a possibilidade de contestação.

#### Resultados `PESSOAS_DISTINTAS`, `CPF_INCORRETO` e `USO_INDEVIDO`

Esses resultados não são mutuamente exclusivos. Duas pessoas podem ser distintas **e** uma delas
ter informado o CPF incorretamente; uso indevido pode continuar inconclusivo quanto à autoria.

O modelo deve usar ao menos dois eixos:

- **relação entre identidades:** mesma pessoa, pessoas distintas ou inconclusivo;
- **situação do CPF declarado:** confirmado, incorreto, contestado, suspeita de uso indevido ou
  inconclusivo.

“Pessoas distintas” não basta para deixar ambas seguirem com o mesmo CPF: antes é necessário
determinar o identificador correto ou registrar a exceção institucional aplicável.

## 6. Modelo de ameaças

### 6.1 Ativos

- direito de inscrição e igualdade de oportunidade;
- integridade do teto de inscrições e das relações de participantes;
- histórico, documentos, avaliações, recursos e convocações;
- credenciais, sessões e códigos de acesso;
- dados pessoais e documentos usados na recuperação;
- autoria, motivação e reprodutibilidade dos atos.

### 6.2 Atores e fronteiras

**Atores:** candidato legítimo, pessoa que errou o CPF, candidato tentando obter vantagem, terceiro
que conhece um CPF, operador da comissão, agente de recuperação, administrador e provedor de e-mail.

**Fronteiras:** navegador, entrega do código por e-mail, sessão Django, backend, PostgreSQL,
armazenamento de documentos, interface institucional e eventual provedor de identidade futuro.

### 6.3 Entradas críticas

- e-mail e código temporário;
- nome e CPF declarados;
- envio de inscrição e documentos;
- escolha de representante ou Perfil;
- contestação de coincidência;
- pedido e provas de recuperação;
- decisão, revisão e comunicação institucional.

## 7. Achados de segurança e consistência

A classificação segue: **P0** crítico, **P1** alto/bloqueador, **P2** médio e **P3** baixo. Não foi
identificado P0, pois a proposta ainda não foi implementada.

### P1-01 — CPF declarado produz vínculo e efeito antes da prova

**Evidência:** a proposta forma participação por CPF e aplica teto e gates ao agrupamento.
**Risco:** alguém que conhece o CPF alheio cria pendência direcionada, interfere no recorte da vítima
e impõe análise ou atraso; além disso, o sistema conclui “uma participação” sem saber se houve erro.
**Controle exigido:** coincidência como sinal; nenhuma associação, acesso, cancelamento ou escolha
automática; decisão somente após prova ou ato institucional contestável.
**Teste necessário:** inscrição maliciosa anterior ou posterior com CPF da vítima não impede envio,
não concede acesso, não escolhe representante e não encerra o direito da vítima.

### P1-02 — Associação de histórico contradiz a autorização vigente

**Evidência:** a spec 010 veda fusão e visualização de inscrição alheia; a proposta oferece histórico
consolidado entre identidades.
**Risco:** uma recuperação ou vínculo incorreto expõe documentos e todo o histórico de outra pessoa.
**Controle exigido:** emendar a spec 010; separar associação de acesso da decisão do certame; exigir
prova forte, propósito próprio, consentimento quando possível, notificações e reversão prospectiva
sem apagar atos.
**Teste necessário:** matriz negativa de IDOR para inscrição, documento, recurso, resultado e
comprovante antes, durante e depois de pedido negado ou contestado.

### P1-03 — Falta base normativa para a representante e para o gate

**Evidência:** os textos recomendam uma representante e, em versões anteriores, “a última”, mas
deixam a regra para o Edital sem definir transição para Editais já publicados.
**Risco:** retirada de efeito ou atraso sem regra publicada, com tratamento diferente entre
candidatos e possível alteração retroativa.
**Controle exigido:** regra estruturada e versionada no Edital; aplicação prospectiva; ato
institucional explícito; definição dos marcos e do que ocorre na ausência de resposta.
**Teste necessário:** Edital sem regra não recebe comportamento novo; Retificação afeta apenas o
futuro; atos anteriores continuam reproduzíveis.

### P1-04 — Recuperação institucional ainda pode virar tomada de conta

**Evidência:** prova aceita, prazo, retenção, SLA, segunda revisão e resposta à contestação continuam
como decisões abertas.
**Risco:** fraude documental ou erro interno concede acesso permanente a histórico, documentos e
atos de outra pessoa.
**Controle exigido:** política de evidência proporcional, segregação de responsabilidades, dupla
revisão nos casos de maior risco, prazo de oposição, canal alternativo, retenção mínima e acesso
restrito. A recuperação não pode usar somente CPF e dados facilmente obtidos.
**Teste necessário:** nenhum pedido pendente concede acesso; aprovação concorrente não duplica nem
desvia vínculo; contestação suspende efeitos futuros previstos; todas as leituras respeitam escopo.

### P1-05 — Documentos da proposta divergem em regras que afetam direitos

**Evidência:** o resumo admite “última inscrição”; o fluxo afirma que pessoas distintas seguem; a
proposta consolidada exige uma representante antes de qualquer trajetória relevante.
**Risco:** a spec pode escolher acidentalmente uma das versões e criar regras incompatíveis entre
envio, avaliação e convocação.
**Controle exigido:** eleger um documento de decisão, marcar os anteriores como superados e registrar
as decisões abertas antes do `/speckit.specify`.
**Teste necessário:** checklist de rastreabilidade que demonstre uma única regra para cada cenário.

### P2-01 — Gate pode virar negação de serviço operacional

Qualquer pessoa pode provocar coincidências em massa usando CPFs conhecidos. Bloquear o Edital
inteiro seria desproporcional; bloquear indefinidamente o Perfil também prejudica terceiros.

**Controles:** gate apenas do ato que consumiria as inscrições afetadas; fila priorizada por marco;
prazo institucional; limitação de abuso na origem; alertas de volume; caminho de decisão em lote que
mostre alcance; continuidade das partes não afetadas. O comportamento de contingência precisa ser
publicado, não improvisado no dia do ato.

### P2-02 — Enumeração e vazamento por mensagens

Avisos e telas podem revelar que existe outra identidade, Perfil ou inscrição. Respostas, prazos e
erros também podem funcionar como oráculo.

**Controles:** mensagens equivalentes; CPF mascarado apenas onde necessário; nenhum e-mail, nome,
protocolo, documento ou Perfil da outra pessoa; códigos de propósito único, expiráveis, de uso único
e limitados; logs sem CPF completo.

### P2-03 — Corridas de submissão, escolha e decisão

O bloqueio atual serializa por `identity_subject + Edital`; ele não serializa identidades distintas
com o mesmo CPF. Duas submissões, escolhas ou decisões concorrentes podem ultrapassar o teto ou
produzir duas representantes.

**Controles:** chave de concorrência própria para o caso, constraints de unicidade para decisão
vigente, comandos idempotentes, `select_for_update` ou advisory lock e rejeição de versão obsoleta.
O desenho não pode depender apenas de consulta seguida de gravação.

### P2-04 — Consumidores posteriores podem aplicar regras diferentes

Hoje cada módulo consulta inscrições por conta própria. Acrescentar um filtro em sorteio e esquecer
avaliação, recurso ou convocação recria a vantagem em outro ponto.

**Controles:** uma única fonte de leitura da participação efetiva ou guardas obrigatórias em cada
comando; testes contratuais cobrindo habilitação, distribuição, avaliação, resultado, classificação,
sorteio, recurso, ocupação e convocação.

### P2-05 — Retenção e minimização ainda não estão decididas

Documentos de recuperação e cópias de identidade ampliam muito o impacto de vazamento.

**Controles:** justificar cada dado, definir finalidade, acesso, prazo e descarte; preferir evidência
de controle e consultas verificáveis a armazenar cópias; registrar na auditoria somente resumo e
identificador da evidência, nunca o conteúdo sensível.

### P2-06 — Novas jornadas não podem enfraquecer autenticação e sessão

Autorregularização, contestação e recuperação acrescentam operações sensíveis a uma sessão obtida
por e-mail. Criar links que autentiquem, reutilizar o código de entrada para aprovar vínculo ou
aceitar uma sessão antiga após mudança de autorização contornaria garantias já entregues pela spec
010.

**Controles:** finalidade separada para cada desafio; código digitado, de uso único, expirável e com
tentativas limitadas; rotação de sessão após autenticação ou mudança de privilégio; proteção CSRF em
todo comando; cookies e cabeçalhos conforme o ambiente; invalidação ou revalidação das sessões
afetadas por associação, oposição e reversão.

### P2-07 — Evidências de recuperação ampliam a superfície de arquivos

Se a recuperação aceitar novos anexos, surge uma segunda jornada de documentos pessoais, com risco
de arquivo ativo, acesso direto, troca de identificador e retenção excessiva.

**Controles:** reutilizar o armazenamento privado e as validações de documentos existentes quando
forem suficientes; nomes opacos; autorização no download; tipo e tamanho permitidos no backend;
entrega como anexo quando aplicável; nenhuma interpretação ativa pelo navegador; varredura ou
quarentena proporcional ao ambiente; descarte conforme a política aprovada.

### P3-01 — Vocabulário pode criar um segundo conceito de participante

O sistema já possui participante habilitado no sorteio. Usar genericamente “participação” para o
novo agregado pode confundir etapas distintas.

**Controle:** oficina de linguagem antes da spec e glossário com ciclos de vida. Um nome como
`CasoDeCoincidencia` para o sinal e outro conceito explícito para o efeito decidido evita que uma
mera suspeita pareça uma pessoa consolidada.

## 8. Arquitetura de domínio recomendada

Este desenho é orientação para a futura spec, não prescrição de tabelas.

### 8.1 Manter intacto

- `CandidateIdentity.subject` continua sendo a titularidade histórica da inscrição;
- e-mails verificados continuam sendo credenciais;
- CPF declarado continua não único e não autentica;
- inscrição submetida continua imutável;
- unicidade por identidade, Edital e Perfil continua existindo;
- envio não é recusado por coincidência criada por outra identidade.

### 8.2 Acrescentar, se aprovado

1. **Caso de coincidência:** registra o sinal, recorte, inscrições envolvidas e estado do workflow.
2. **Manifestação do candidato:** escolha, contestação ou alegação de erro, sem acesso a dados
   alheios.
3. **Decisão de participação:** ato append-only que declara efeitos prospectivos, fundamento,
   alcance, representante e inscrições sem efeito para aquele propósito.
4. **Associação de identidades para acesso:** ato separado, com prova própria; preserva os
   `subject` originais e amplia autorização apenas após decisão definitiva.
5. **Correção reconhecida:** ato que não reescreve o CPF originalmente submetido.

### 8.3 Estados mínimos do caso

Uma máquina de estados deve distinguir, pelo menos:

`DETECTADO → NOTIFICADO → EM_AUTORREGULARIZACAO → EM_ANALISE → DECIDIDO → EM_CONTESTACAO → DEFINITIVO`

Devem existir saídas próprias para erro corrigido, coincidência sem relação, desistência e
arquivamento motivado. “Uso indevido” não deve ser um atalho para condenação: suspeita e conclusão
são estados diferentes.

### 8.4 Marcos de estabilização

Não basta um gate no sorteio. Para cada modalidade, a spec deve identificar o primeiro ato que
concede trajetória independente:

- inclusão em relação de habilitados;
- distribuição para análise documental;
- concessão de tentativa de prova, entrevista ou vídeo;
- atribuição para avaliação;
- publicação de resultado/classificação;
- sorteio;
- abertura de recurso dependente de resultado;
- ocupação de vaga e convocação.

A decisão deve ocorrer antes do primeiro desses marcos aplicável ao Edital. Quando a própria
análise documental é necessária para esclarecer a identidade, deve existir uma análise específica
do caso, sem criar duas avaliações competitivas.

## 9. Avaliação da alternativa “uma conta por CPF”

### Com CPF apenas declarado: não recomendar

Uma constraint única no CPF da identidade feriria o desenho atual e criaria:

- reserva maliciosa do CPF por quem agir primeiro;
- bloqueio da vítima no prazo de inscrição;
- recuperação baseada em dado público ou vazado;
- impossibilidade de tratar erro de digitação sem intervenção;
- conflito com FR-064 e com a demonstração de segurança da spec 010.

Seria uma falsa simplificação: a complexidade sairia da inscrição e reapareceria como recuperação
urgente de conta.

### Com CPF verificado: opção futura, não consequência automática

Uma identidade civil verificada pode permitir unicidade, mas exige:

- fonte e nível de garantia explícitos;
- recuperação quando o provedor ou documento não estiver disponível;
- tratamento de exceções e indisponibilidade;
- migração dos múltiplos `subject` existentes sem reescrever atos;
- decisão sobre CPF alterado, regularizado ou excepcional;
- revisão de privacidade, contrato e dependência externa.

Isso pode ser feito futuramente com Gov.br ou outra prova institucional, sem bloquear a primeira
entrega. Até lá, “CPF verificado” e “CPF declarado” precisam ser conceitos diferentes.

## 10. Fluxo recomendado sem Gov.br

1. Candidato entra com código enviado ao e-mail.
2. Envia a inscrição normalmente; coincidência nunca recusa o envio.
3. O backend abre um caso de coincidência, sem concluir identidade compartilhada.
4. Todas as identidades afetadas recebem aviso neutro e canal de manifestação.
5. Quem controla os dois e-mails pode provar ambos e pedir associação ou escolher representante.
6. Quem não reconhece a outra inscrição contesta sem receber dados dela.
7. A instituição analisa somente casos não resolvidos antes do marco aplicável.
8. A decisão motivada define efeitos prospectivos e preserva os atos originais.
9. Os envolvidos são notificados e têm canal e prazo de contestação.
10. Apenas a decisão definitiva alimenta a fonte única de participação efetiva.
11. Recuperação de histórico sem e-mail antigo segue processo separado e mais rigoroso.

Esse fluxo mantém baixa fricção no caso comum. A complexidade aparece somente quando já existe um
conflito real, sem transformar CPF em senha ou exigir validação civil de todos os candidatos.

## 11. Matriz mínima de controles e testes para a futura spec

| Risco | Controle de domínio | Evidência automatizada necessária |
|---|---|---|
| CPF alheio usado primeiro | Envio sempre aceito; sem reserva ou vínculo | Teste ponta a ponta com atacante antes da vítima |
| Duas chances no mesmo Perfil | Uma decisão efetiva antes do primeiro marco | Testes em sorteio e em avaliação sem sorteio |
| Teto atravessado em Perfis | Regra versionada e decisão por pessoa comprovada | Concorrência PostgreSQL em Perfis diferentes |
| Tomada de histórico | Associação separada e prova forte | IDOR e matriz de autorização negativa |
| Decisão duplicada | Comando idempotente, lock e unicidade vigente | Duas decisões concorrentes |
| Reescrita histórica | Atos append-only; inscrição intocada | Gatilho, privilégio e reprodução histórica |
| Regra esquecida num módulo | Fonte única de participação efetiva | Contrato para todos os consumidores posteriores |
| Vazamento por aviso | Conteúdo neutro e respostas equivalentes | Testes de mensagem e enumeração |
| Abuso interno | capacidades separadas e escopo mínimo | matriz de permissões e auditoria completa |
| Recuperação fraudulenta | prova, revisão, oposição e retenção | jornadas de aprovar, negar, contestar e expirar |
| Retificação | vigência explícita e não retroatividade | casos antes/depois da nova versão |
| Prazo encerrando | SLA e contingência publicados | caso criado no último dia e ausência de resposta |

## 12. Decisões obrigatórias antes da spec

1. Qual documento passa a ser a fonte da proposta e quais ficam formalmente superados?
2. Qual é o nome e o significado exato do novo agregado, sem confundi-lo com identidade ou
   participante do sorteio?
3. O que o CPF declarado pode produzir sozinho: somente sinalização ou também gate? Por quanto
   tempo e com qual contingência contra abuso?
4. Qual norma autoriza escolher representante e tornar outra inscrição sem efeito?
5. A regra vale apenas para Editais novos ou haverá Retificação expressa dos vigentes?
6. Como o teto publicado é aplicado quando a identidade civil ainda não foi comprovada?
7. Quais provas resolvem “mesma pessoa”, “pessoas distintas”, erro e suspeita de uso indevido?
8. Qual é a regra na ausência de manifestação, especialmente no último dia e perto do primeiro
   marco?
9. Qual é o canal, prazo e efeito da contestação?
10. Associação de acesso fará parte desta feature ou de incremento posterior?
11. Quais provas, permissões, dupla revisão, retenção e SLA regem recuperação sem e-mail antigo?
12. Quais atos posteriores consomem a fonte única de participação efetiva em cada modalidade?

## 13. Ordem recomendada de implementação futura

Depois das decisões anteriores, a solução pode ser dividida sem perder segurança:

1. **Proteção do certame:** caso de coincidência, fila, decisão institucional, comunicação, gates e
   integração com todos os consumidores posteriores.
2. **Autorregularização:** manifestação segura, prova de controle dos dois e-mails, escolha de
   representante e contestação.
3. **Associação voluntária de histórico:** autorização cruzada sem reescrita dos `subject`.
4. **Recuperação institucional:** somente após política de prova, retenção, SLA e segregação.
5. **Identidade civil verificada opcional:** Gov.br ou alternativa futura, sem acoplar o núcleo da
   primeira entrega ao provedor.

## 14. Veredito

### Decisão atual: SEGURAR

Não é recomendável transformar os três documentos diretamente em spec. Permanecem achados P1 que
podem ferir regras vigentes, autorização e direitos do candidato.

### Condição para aprovação da direção

A proposta pode seguir para especificação quando:

- coincidência deixar de equivaler automaticamente a uma pessoa ou participação;
- a base normativa da representante e do teto estiver definida e versionada;
- a associação de histórico for separada da decisão do certame e a spec 010 for emendada;
- a recuperação institucional tiver política de prova, prazo, retenção e segregação;
- os documentos forem consolidados em uma única regra sem contradições;
- todos os fluxos posteriores, com e sem sorteio, estiverem no escopo dos requisitos e testes.

Com essas correções, **vale a pena manter o acesso facilitado por e-mail**. Ele reduz fricção para a
maioria sem impedir a integridade do certame. O preço correto é tratar exceções com um fluxo próprio,
e não transformar o CPF declarado em credencial ou em chave única de conta.
