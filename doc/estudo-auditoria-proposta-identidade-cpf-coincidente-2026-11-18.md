# Estudo e auditoria da proposta de identidade e CPF coincidente

**Data original:** 18/11/2026
**Atualização:** 23/11/2026
**Decisão incorporada:** a comissão trata as coincidências no início do fluxo, antes da primeira
publicação das inscrições; o primeiro incremento não integra com o Gov.br
**Situação:** direção apta a virar especificação, ainda sem representar decisão normativa do Edital
**Veredito de segurança:** **SEGURAR A IMPLEMENTAÇÃO** até a spec resolver os achados P1 abertos;
a elaboração da spec é o próximo passo recomendado
**Escopo do primeiro incremento:** detecção, caso de coincidência, análise da comissão, manifestação
dos envolvidos, decisão, comunicação e gates antes da publicação e de qualquer vantagem
**Fora do primeiro incremento:** associação de históricos, recuperação de identidade sem acesso ao
e-mail antigo e integração com Gov.br

## 1. Resumo executivo

A direção escolhida é compatível com o núcleo do sistema: manter o acesso sem senha por e-mail, não
recusar o envio porque outra identidade declarou o mesmo CPF, preservar as inscrições originais e
levar a coincidência para decisão institucional. A comissão passa a analisar o caso cedo, antes da
primeira publicação das inscrições, sem depender de Gov.br.

Essa decisão resolve o principal conflito da redação anterior **desde que o CPF apenas abra um caso**.
A coincidência não pode formar automaticamente uma pessoa, fundir contas, escolher representante ou
retirar efeito. Esses efeitos nascem somente do ato motivado da comissão, depois de manifestação e
evidência suficientes.

A proposta já pode seguir para especificação, mas não para implementação. Permanecem dois pontos P1:

1. definir a base normativa, as evidências, os resultados possíveis, o prazo e a contestação da
   decisão da comissão;
2. compatibilizar o gate com a publicação existente: a relação de recebidas contém todas as
   inscrições enviadas e é opcional, portanto não pode ser o único marco nem pode omitir em silêncio
   a inscrição preservada no histórico.

### Recomendação consolidada

Manter o acesso facilitado por e-mail e separar, no primeiro incremento, três conceitos:

1. **identidade de acesso**, opaca, dona das inscrições e autenticada por e-mails verificados;
2. **coincidência de CPF**, que abre um caso de análise, mas não cria vínculo nem altera titularidade;
3. **decisão sobre participação efetiva**, produzida por ato institucional motivado da comissão,
   com manifestação dos envolvidos, comunicação e revisão.

Associação de histórico e recuperação de identidade ficam para incremento posterior. A comissão
decidir qual inscrição produz efeito no certame **não** concede a uma identidade acesso às inscrições
da outra.

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
- [Spec 148 — Publicação e homologação das inscrições](../specs/148-publicacao-e-homologacao-das-inscricoes/spec.md)
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

A atualização de 23/11/2026 toma a [proposta resumida](proposta-resumida-cpf-coincidente-e-identidade-2026-11-18.md)
como ponto de partida e a complementa com a decisão acima. Nos pontos de conflito, esta atualização
substitui a sugestão anterior de agrupamento automático, “vale a última” ou associação de contas no
primeiro incremento.

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

### 3.5 Publicação das inscrições

A feature 148 já define três atos públicos distintos:

- **relação de inscrições recebidas**;
- **resultado preliminar da análise das inscrições**;
- **homologação das inscrições**.

A relação de recebidas é opcional e deve contemplar **toda inscrição enviada**. Ela prova que o
sistema recebeu a inscrição; não afirma que ela está homologada nem que seguirá como participação
efetiva. O preliminar e a homologação derivam de uma Etapa decisória e têm regras próprias de recurso.

Isso produz duas consequências para a proposta:

1. a comissão pode resolver coincidências antes da primeira publicação, mas uma inscrição enviada
   não pode desaparecer silenciosamente da relação de recebidas; se ficar sem efeito, o ato histórico
   e a decisão permanecem;
2. a publicação não pode ser o único gate, pois hoje ela é opcional e avaliação, classificação,
   sorteio e convocação não dependem dela. A decisão definitiva deve existir antes do **primeiro**
   entre a publicação e qualquer operação que conceda trajetória independente.

## 4. Confronto com a Constituição

| Princípio | Avaliação | Condição para consistência |
|---|---|---|
| I — Linguagem e domínio | **Parcial** | Definir sem ambiguidade `identidade`, `credencial`, `caso de coincidência`, `decisão de participação` e `inscrição representante`. “Conta”, “pessoa”, “candidato” e “participação” não podem alternar como sinônimos. |
| II — Integridade normativa e temporalidade | **Parcial** | A regra de limite e representação deve estar na versão do Edital e não pode reinterpretar silenciosamente inscrições ou resultados históricos. Inscrições originais e atos devem permanecer imutáveis. |
| III — Segurança, dados e auditoria | **Parcial** | A decisão de usar a comissão evita vínculo automático, mas a spec ainda deve definir menor privilégio, evidência proporcional, notificação, contestação, minimização e auditoria append-only. |
| IV — Regras explícitas e consistência | **Parcial** | Coincidência, análise, contestação e decisão precisam de máquina de estados, comandos transacionais e tratamento de concorrência. O gate deve alcançar publicação e todos os consumidores posteriores. |
| V — Rastreabilidade e qualidade | **Parcial** | As specs 010, 015 e 148 precisam ser compatibilizadas explicitamente. Todos os consumidores posteriores precisam de requisitos e testes de regressão. |
| VI — Jornada completa | **Parcial** | A comissão entra no fluxo, mas ainda faltam canal, prazo, ausência de resposta, contestação, erro de CPF e correção posterior de ponta a ponta. |

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
- Registrar decisões e correções reconhecidas como atos históricos, motivados e auditáveis.
- Fazer a comissão decidir, em vez de o sistema concluir pela coincidência.
- Impedir a primeira publicação enquanto houver caso pendente no universo daquele ato.
- Restringir os demais gates ao Perfil, lista ou operação realmente afetados.
- Comunicar os envolvidos sem revelar dados da outra identidade.
- Exigir permissão explícita e escopo para analisar e decidir.

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

**Efeito da decisão de 23/11:** este conflito fica encaminhado. O primeiro incremento deve usar a
coincidência apenas para abrir o caso e colocar a decisão na fila da comissão. Qualquer redação que
diga que o CPF “forma uma única participação” antes da decisão fica superada.

#### Associação de contas e visualização consolidada

A spec 010 proíbe fundir identidades e determina que uma identidade não visualize inscrição de
outra. A proposta de associação append-only é tecnicamente melhor do que reescrever titularidade,
mas ainda muda a autorização: uma credencial passa a alcançar patrimônio que pertence a outro
`subject`.

Isso não é uma extensão neutra. Exige emenda explícita da spec 010, novo modelo de autorização e
prova de que o vínculo foi autorizado. Por isso, associação de contas e visualização consolidada
ficam **fora do primeiro incremento**. A decisão da comissão sobre o certame não concede acesso ao
histórico da outra identidade.

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

#### O que significa “antes da lista de inscritos”

No vocabulário atual, “lista de inscritos” é ambíguo. A spec 148 distingue recebidas, preliminar e
homologação. A futura spec deve adotar uma destas leituras:

- **recomendada:** a relação de recebidas continua provando tudo o que foi enviado; a decisão da
  comissão controla a participação efetiva e as publicações posteriores;
- **alternativa:** criar ou redefinir um ato de inscrições efetivas, com nome e regra próprios.

Não é consistente reutilizar a relação de recebidas e simplesmente omitir a inscrição não
representante: isso violaria o universo completo exigido pela spec 148 e apagaria do ato público o
fato de que a inscrição foi recebida.

Também não basta bloquear apenas a tela de publicação. Como esse ato é opcional, todo comando de
habilitação, distribuição, avaliação, classificação, sorteio, ocupação ou convocação deve recusar
caso pendente no seu recorte, mesmo quando nenhuma lista tiver sido publicada.

## 6. Modelo de ameaças

### 6.1 Ativos

- direito de inscrição e igualdade de oportunidade;
- integridade do teto de inscrições e das relações de participantes;
- histórico, documentos, avaliações, recursos e convocações;
- credenciais, sessões e códigos de acesso;
- dados pessoais e eventuais evidências adicionais pedidas pela comissão;
- autoria, motivação e reprodutibilidade dos atos.

### 6.2 Atores e fronteiras

**Atores:** candidato legítimo, pessoa que errou o CPF, candidato tentando obter vantagem, terceiro
que conhece um CPF, operador da comissão, revisor da decisão, administrador e provedor de e-mail.

**Fronteiras:** navegador, entrega do código por e-mail, sessão Django, backend, PostgreSQL,
armazenamento de documentos, interface institucional e eventual provedor de identidade futuro.

### 6.3 Entradas críticas

- e-mail e código temporário;
- nome e CPF declarados;
- envio de inscrição e documentos;
- escolha de representante ou Perfil;
- contestação de coincidência;
- manifestação e evidências eventualmente pedidas pela comissão;
- decisão, revisão e comunicação institucional.

## 7. Achados de segurança e consistência

A classificação segue: **P0** crítico, **P1** alto/bloqueador, **P2** médio e **P3** baixo. Não foi
identificado P0, pois a proposta ainda não foi implementada.

### P1-01 — CPF declarado produz vínculo e efeito antes da prova — ENCAMINHADO

**Evidência:** a proposta forma participação por CPF e aplica teto e gates ao agrupamento.
**Risco:** alguém que conhece o CPF alheio cria pendência direcionada, interfere no recorte da vítima
e impõe análise ou atraso; além disso, o sistema conclui “uma participação” sem saber se houve erro.
**Controle exigido:** coincidência como sinal; nenhuma associação, acesso, cancelamento ou escolha
automática; decisão somente após prova ou ato institucional contestável.
**Teste necessário:** inscrição maliciosa anterior ou posterior com CPF da vítima não impede envio,
não concede acesso, não escolhe representante e não encerra o direito da vítima.

**Situação em 23/11:** a opção pela análise da comissão fecha o desenho automático, desde que a spec
não transforme a abertura do caso em participação única antes da decisão.

### P1-02 — Associação de histórico contradiz a autorização vigente — FORA DO INCREMENTO

**Evidência:** a spec 010 veda fusão e visualização de inscrição alheia; a proposta oferece histórico
consolidado entre identidades.
**Risco:** uma recuperação ou vínculo incorreto expõe documentos e todo o histórico de outra pessoa.
**Controle exigido:** emendar a spec 010; separar associação de acesso da decisão do certame; exigir
prova forte, propósito próprio, consentimento quando possível, notificações e reversão prospectiva
sem apagar atos.
**Teste necessário:** matriz negativa de IDOR para inscrição, documento, recurso, resultado e
comprovante antes, durante e depois de pedido negado ou contestado.

**Situação em 23/11:** não bloqueia o primeiro incremento porque associação e recuperação de
histórico foram retiradas do escopo. O finding volta a ser bloqueador quando essa fase for iniciada.

### P1-03 — Falta base normativa para a representante e para o gate — ABERTO

**Evidência:** os textos recomendam uma representante e, em versões anteriores, “a última”, mas
deixam a regra para o Edital sem definir transição para Editais já publicados.
**Risco:** retirada de efeito ou atraso sem regra publicada, com tratamento diferente entre
candidatos e possível alteração retroativa.
**Controle exigido:** regra estruturada e versionada no Edital; aplicação prospectiva; ato
institucional explícito; definição dos marcos e do que ocorre na ausência de resposta.
**Teste necessário:** Edital sem regra não recebe comportamento novo; Retificação afeta apenas o
futuro; atos anteriores continuam reproduzíveis.

### P1-04 — Recuperação institucional ainda pode virar tomada de conta — FORA DO INCREMENTO

**Evidência:** prova aceita, prazo, retenção, SLA, segunda revisão e resposta à contestação continuam
como decisões abertas.
**Risco:** fraude documental ou erro interno concede acesso permanente a histórico, documentos e
atos de outra pessoa.
**Controle exigido:** política de evidência proporcional, segregação de responsabilidades, dupla
revisão nos casos de maior risco, prazo de oposição, canal alternativo, retenção mínima e acesso
restrito. A recuperação não pode usar somente CPF e dados facilmente obtidos.
**Teste necessário:** nenhum pedido pendente concede acesso; aprovação concorrente não duplica nem
desvia vínculo; contestação suspende efeitos futuros previstos; todas as leituras respeitam escopo.

**Situação em 23/11:** recuperação sem e-mail antigo foi retirada do primeiro incremento e não pode
ser introduzida como atalho dentro da tela da comissão.

### P1-05 — Documentos da proposta divergem em regras que afetam direitos — ENCAMINHADO

**Evidência:** o resumo admite “última inscrição”; o fluxo afirma que pessoas distintas seguem; a
proposta consolidada exige uma representante antes de qualquer trajetória relevante.
**Risco:** a spec pode escolher acidentalmente uma das versões e criar regras incompatíveis entre
envio, avaliação e convocação.
**Controle exigido:** eleger um documento de decisão, marcar os anteriores como superados e registrar
as decisões abertas antes do `/speckit.specify`.
**Teste necessário:** checklist de rastreabilidade que demonstre uma única regra para cada cenário.

**Situação em 23/11:** para a futura spec, esta atualização prevalece nos conflitos: comissão antes
do primeiro ato, nenhum agrupamento automático, nenhum Gov.br, associação ou recuperação no primeiro
incremento. Os documentos anteriores continuam como histórico de discussão, não como fontes
simultâneas de requisito.

### P1-06 — A publicação não é um marco universal e a relação de recebidas não pode omitir — ABERTO

**Evidência:** a spec 148 torna a publicação opcional, proíbe que os fluxos posteriores a exijam e
manda a relação de recebidas contemplar toda inscrição enviada.
**Risco:** usar somente a publicação como gate deixa avaliação ou sorteio avançar sem decisão; omitir
a inscrição não representante da relação de recebidas contradiz o significado e o universo do ato.
**Controle exigido:** bloquear o primeiro entre publicação e qualquer consumidor de participação;
manter todas as enviadas na relação de recebidas ou criar outro ato normativo para inscrições
efetivas; nunca excluir ou reescrever o ato original.
**Teste necessário:** sem publicação, um caso pendente impede o consumidor afetado; resolvido o caso,
a relação de recebidas ainda reproduz tudo que foi enviado; decisão revista depois de publicação
gera sucessão/correção, não mutação.

### P2-01 — Gate pode virar negação de serviço operacional

Qualquer pessoa pode provocar coincidências em massa usando CPFs conhecidos. Como a publicação das
inscrições é um ato único por Edital e contempla todas as inscrições, uma pendência pode atrasar o
ato inteiro; nos consumidores posteriores, bloquear indefinidamente o Perfil também prejudica
terceiros.

**Controles:** análise contínua desde a detecção; fila priorizada pela data do primeiro ato; SLA entre
o encerramento das inscrições e a publicação; limitação de abuso na origem; alertas de volume;
caminho de decisão em lote que mostre alcance; continuidade dos recortes não afetados quando o ato
permitir. A contingência precisa ser publicada, não improvisada no dia do ato.

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

Documentos adicionais pedidos pela comissão e, futuramente, documentos de recuperação ampliam muito
o impacto de vazamento.

**Controles:** justificar cada dado, definir finalidade, acesso, prazo e descarte; preferir evidência
de controle e consultas verificáveis a armazenar cópias; registrar na auditoria somente resumo e
identificador da evidência, nunca o conteúdo sensível.

### P2-06 — Novas jornadas não podem enfraquecer autenticação e sessão

Manifestação e contestação acrescentam operações sensíveis a uma sessão obtida por e-mail. Criar
links que autentiquem ou reutilizar o código de entrada para autorizar outro propósito contornaria
garantias já entregues pela spec 010.

**Controles:** finalidade separada para cada desafio; código digitado, de uso único, expirável e com
tentativas limitadas; rotação de sessão após autenticação; proteção CSRF em todo comando; cookies e
cabeçalhos conforme o ambiente; nenhuma decisão da comissão muda o `subject` da sessão ou amplia a
autorização para dados da outra identidade.

### P2-07 — Evidências da comissão ampliam a superfície de arquivos

Se a comissão aceitar novos anexos, surge uma segunda jornada de documentos pessoais, com risco de
arquivo ativo, acesso direto, troca de identificador e retenção excessiva.

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
2. **Manifestação do candidato:** confirmação, contestação ou alegação de erro, sem acesso a dados
   alheios e sem produzir decisão automática.
3. **Decisão de participação:** ato append-only que declara efeitos prospectivos, fundamento,
   alcance, representante e inscrições sem efeito para aquele propósito.
4. **Correção reconhecida:** ato que não reescreve o CPF originalmente submetido.
5. **Gate de estabilização:** consulta única que publicação e consumidores posteriores usam para
   recusar caso pendente e ler a decisão vigente.

Não fazem parte deste incremento a associação de identidades para acesso, a recuperação sem e-mail
antigo ou uma identidade civil verificada pelo Gov.br.

### 8.3 Estados mínimos do caso

Uma máquina de estados conduzida pela comissão deve distinguir, pelo menos:

`DETECTADO → NOTIFICADO → EM_ANALISE → AGUARDANDO_MANIFESTACAO → DECIDIDO → EM_REVISAO → DEFINITIVO`

Devem existir saídas próprias para erro corrigido, coincidência sem relação, desistência e
arquivamento motivado. “Uso indevido” não deve ser um atalho para condenação: suspeita e conclusão
são estados diferentes.

### 8.4 Marcos de estabilização

O primeiro marco visível escolhido é a publicação das inscrições. Ele não substitui os demais gates:
para cada modalidade, a spec deve identificar o primeiro ato que publica ou concede trajetória
independente:

- publicação da relação de recebidas, preliminar ou homologação;
- inclusão em relação de habilitados;
- distribuição para análise documental;
- concessão de tentativa de prova, entrevista ou vídeo;
- atribuição para avaliação;
- publicação de resultado/classificação;
- sorteio;
- abertura de recurso dependente de resultado;
- ocupação de vaga e convocação.

A decisão deve ocorrer antes do primeiro desses marcos aplicável ao Edital, tenha ou não ocorrido
publicação. Quando a própria análise documental é necessária para esclarecer a identidade, deve
existir uma análise específica do caso, sem criar duas avaliações competitivas.

### 8.5 Compatibilidade com a cadeia de publicação

A alternativa de menor impacto é:

- manter `RECEBIDAS` como a fotografia de todas as inscrições enviadas;
- registrar separadamente a decisão de participação da comissão;
- fazer preliminar, homologação e consumidores posteriores lerem a decisão quando ela for aplicável;
- recusar a confirmação da publicação se surgiu ou mudou um caso desde a prévia;
- se a decisão for revista depois de um ato público, publicar sucessor/correção com motivo, sem
  alterar o ato anterior.

Se a instituição quiser que a primeira lista pública contenha somente inscrições representantes,
ela não será mais uma simples relação de recebidas. A spec deverá nomear e modelar outro ato, ou
alterar expressamente a spec 148 e suas garantias de universo completo.

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
4. O caso entra imediatamente na fila da comissão; novas inscrições coincidentes atualizam o mesmo
   caso e invalidam qualquer prévia obsoleta.
5. Todas as identidades afetadas recebem aviso neutro e canal autenticado de manifestação.
6. Quem não reconhece a outra inscrição contesta sem receber dados dela; controlar os dois e-mails
   é evidência, mas não funde as identidades.
7. A comissão examina as inscrições e as manifestações, pede evidência adicional somente quando
   necessária e registra a conclusão nos dois eixos: relação entre identidades e situação do CPF.
8. Encerrado o período de inscrições, a comissão estabiliza os casos ainda abertos antes da primeira
   publicação ou operação que gere vantagem, o que ocorrer primeiro.
9. A decisão motivada define efeitos prospectivos, representante quando aplicável e o alcance por
   Edital e Perfil, preservando todas as inscrições originais.
10. Os envolvidos são notificados e têm canal e prazo de revisão; a decisão não concede acesso ao
    histórico da outra identidade.
11. A relação de recebidas, quando publicada, continua reproduzindo todas as inscrições enviadas. A
    decisão da comissão governa a participação efetiva e os atos posteriores.
12. Se a revisão mudar decisão já publicada, o sistema produz sucessor/correção, nunca edição.
13. Associação de histórico, recuperação sem e-mail antigo e Gov.br permanecem em fases futuras.

Esse fluxo mantém baixa fricção no caso comum. A complexidade aparece somente quando já existe um
conflito real, sem transformar CPF em senha ou exigir validação civil de todos os candidatos.

## 11. Matriz mínima de controles e testes para a futura spec

| Risco | Controle de domínio | Evidência automatizada necessária |
|---|---|---|
| CPF alheio usado primeiro | Envio sempre aceito; sem reserva ou vínculo | Teste ponta a ponta com atacante antes da vítima |
| Duas chances no mesmo Perfil | Uma decisão efetiva antes do primeiro marco | Testes em sorteio e em avaliação sem sorteio |
| Teto atravessado em Perfis | Regra versionada e decisão por pessoa comprovada | Concorrência PostgreSQL em Perfis diferentes |
| Acesso cruzado indevido | Decisão do certame não associa identidades | IDOR e matriz de autorização negativa |
| Decisão duplicada | Comando idempotente, lock e unicidade vigente | Duas decisões concorrentes |
| Reescrita histórica | Atos append-only; inscrição intocada | Gatilho, privilégio e reprodução histórica |
| Regra esquecida num módulo | Fonte única de participação efetiva | Contrato para todos os consumidores posteriores |
| Publicação usada como único gate | Guarda também nos consumidores posteriores | avaliação/sorteio sem publicação e com caso pendente |
| Omissão na relação de recebidas | Universo continua sendo todas as enviadas | não representante ainda consta como recebida |
| Decisão alterada após publicação | Sucessor/correção com motivo | ato anterior permanece idêntico e consultável |
| Vazamento por aviso | Conteúdo neutro e respostas equivalentes | Testes de mensagem e enumeração |
| Abuso interno | capacidades separadas e escopo mínimo | matriz de permissões e auditoria completa |
| Evidência excessiva | coleta mínima, acesso restrito e retenção definida | autorização negativa e descarte conforme política |
| Retificação | vigência explícita e não retroatividade | casos antes/depois da nova versão |
| Prazo encerrando | SLA e contingência publicados | caso criado no último dia e ausência de resposta |

## 12. Decisões incorporadas e decisões que a spec deve fechar

### 12.1 Já decidido em 23/11/2026

- a comissão trata as coincidências antes da primeira publicação das inscrições;
- CPF coincidente abre caso, mas não forma automaticamente uma pessoa ou participação;
- o envio continua aceito;
- acesso continua por e-mail;
- Gov.br, associação de históricos e recuperação sem e-mail antigo ficam fora do primeiro incremento;
- a decisão do certame não muda titularidade nem concede acesso cruzado.

### 12.2 A spec ainda deve decidir

1. Qual é o nome e o significado exato do novo agregado, sem confundi-lo com identidade ou
   participante do sorteio?
2. Qual norma autoriza escolher representante e tornar outra inscrição sem efeito?
3. A regra vale apenas para Editais novos ou haverá Retificação expressa dos vigentes?
4. Como o teto publicado é aplicado quando a identidade civil ainda não foi comprovada?
5. Quais evidências permitem concluir mesma pessoa, pessoas distintas, erro ou uso indevido?
6. Qual é a regra na ausência de manifestação, especialmente no último dia e perto da publicação?
7. Qual é o canal, prazo e efeito da revisão da decisão da comissão?
8. A primeira lista continua sendo a relação de todas as recebidas ou a instituição quer um novo ato
   de inscrições efetivas?
9. Qual é o SLA da comissão entre o encerramento das inscrições e a primeira publicação?
10. Qual capacidade autoriza analisar, decidir e revisar, separada da capacidade de publicar?
11. Quais atos posteriores consomem a fonte única de participação efetiva em cada modalidade?
12. Que evidências adicionais podem ser coletadas, com qual acesso, retenção e descarte?

## 13. Ordem recomendada de implementação futura

Depois das decisões anteriores, a solução pode ser dividida sem perder segurança:

1. **Proteção do certame:** caso de coincidência, fila, decisão institucional, comunicação, gates e
   integração com a publicação das inscrições e todos os consumidores posteriores.
2. **Manifestação e revisão:** canal seguro para os envolvidos responderem e pedirem revisão, sem
   ver dados alheios.
3. **Associação voluntária de histórico:** fase futura, com autorização cruzada sem reescrita dos
   `subject`.
4. **Recuperação institucional:** fase futura, somente após política de prova, retenção, SLA e
   segregação.
5. **Identidade civil verificada opcional:** Gov.br ou alternativa futura, sem acoplar o núcleo da
   primeira entrega ao provedor.

## 14. Veredito

### Decisão de produto: APROVAR A IDA PARA A SPEC

A opção pela comissão antes da primeira publicação é coerente com FR-066 e elimina a decisão
automática por CPF, desde que a futura spec preserve o envio, o histórico e o contraditório.

### Gate de segurança: SEGURAR A IMPLEMENTAÇÃO

Permanecem abertos P1-03 e P1-06. O menor próximo passo verificável é a spec definir:

- fundamento e critérios da decisão da comissão;
- manifestação, prazo, ausência de resposta e revisão;
- relação de recebidas como universo completo, ou outro ato expressamente modelado;
- gate no primeiro entre publicação e qualquer consumidor posterior;
- regra prospectiva para Editais novos e tratamento explícito dos já publicados.

Associação de histórico, recuperação sem e-mail antigo e Gov.br não são pré-condições desta entrega e
não devem reaparecer implicitamente no plano.

Com essas condições, **vale a pena manter o acesso facilitado por e-mail**. Ele reduz fricção para a
maioria e a comissão concentra o esforço nos casos excepcionais antes de eles produzirem vantagem ou
ato público. O CPF continua sendo sinal, não credencial nem chave única de conta.
