# Feature Specification: Gestão da Comissão e Alocação por Etapa

**Feature Branch**: `011-comissao-alocacao`

**Created**: 2026-09-01

**Status**: Draft

**Input**: Redação conceitual da feature, reconciliada com o modelo real de Processo, Edital,
Etapa, identidade e auditoria já presente no repositório antes do planejamento. A reconciliação
produziu as **Decisões fechadas antes do planejamento**, que corrigem requisitos escritos contra
um domínio que o sistema não tem.

## 1. Visão

Permitir que o responsável por um Processo Seletivo constitua sua comissão, defina quais membros
podem atuar em cada Etapa e ofereça a cada participante institucional uma visão objetiva do
trabalho para o qual está autorizado.

A feature responde à pergunta:

> **Quem trabalha neste Processo e em qual Etapa?**

A 011 organiza pessoas, responsabilidades e autorização contextual.

Ela **não executa avaliação**.

---

## 2. Frase que governa

> **O responsável pelo Processo deve conseguir constituir a comissão, determinar quem pode atuar
> em cada Etapa e enxergar como o trabalho está organizado sem manter planilha paralela de
> distribuição.**

Para quem integra a comissão:

> **Cada membro deve enxergar somente os Processos e Etapas em que efetivamente possui
> atribuição.**

---

## 3. Decisões fechadas antes do planejamento

*A primeira redação desta spec foi escrita olhando a jornada, e não o sistema que a sustenta: ela
descreveu a Etapa como se pertencesse ao Processo, amarrou a alocação a uma linha que o sistema
recria a cada gravação, exigiu um diretório institucional que não existe e afirmou uma autoridade
que a Constituição já define de outro modo. As sete decisões abaixo fecham isso em termos de
resultado; a evidência técnica que as motivou está em [research.md](./research.md), e o corpo da
spec já está escrito conforme elas.*

### D-001 — A Etapa pertence ao Edital, não ao Processo

O caminho do domínio é `Processo → Edital → Etapa`, e um Processo tem N Editais.

A comissão continua sendo do **Processo**: substituir o Edital dentro de um mesmo Processo não
refaz a comissão. Mas a coerência da alocação é verificada percorrendo `etapa → edital → processo`;
a visão administrativa é organizada por Edital antes de por Etapa, porque dois Editais do mesmo
Processo podem ter Etapas homônimas; e `Minhas Etapas` sempre identifica o Edital.

### D-002 — A alocação sobrevive à recriação da coleção de Etapas

Gravar o rascunho de um Edital recria toda a sua coleção de Etapas, preservando os identificadores.
A alocação é feita, portanto, pela **identidade estável da Etapa**, e não pela linha que a carrega
naquele momento.

O que a spec fixa é o invariante, e não o mecanismo:

> A alocação nunca concede acesso a Etapa ausente da Versão Consolidada vigente do Edital, e nada
> do que a 011 grava pode impedir a elaboração ou a Retificação de um Edital.

**A fonte é uma só: a Versão Consolidada vigente.** Disso decorre que a alocação existe apenas para
Etapa de Edital publicado. Alocar durante a elaboração seria alocar contra uma coleção que o próprio
elaborador recria a cada salvamento: a alocação nasceria órfã pelas edições legítimas de quem monta o
Edital, e `Minhas Etapas` mostraria o resultado de um acidente. Constituir a comissão continua
possível a qualquer momento; distribuir trabalho pressupõe que o trabalho exista publicamente.

A integridade referencial que a Constituição exige é preservada no command, que verifica existência
e pertinência a cada operação e a cada acesso. O precedente é `Inscricao.profile_id`, adotado pela
009 pela mesma razão. A forma concreta é decisão do `/plan`; qualquer forma que viole o invariante
acima está errada.

### D-003 — Não existe diretório institucional, e a 011 não o cria

A identidade institucional do projeto é um identificador textual, e não há nome, e-mail, lotação
nem estado de conta de servidor em lugar nenhum do domínio.

Logo, na V1:

- o gestor informa o **identificador institucional** da pessoa, e o sistema o trata como a chave;
- um **rótulo de exibição** opcional pode acompanhá-lo, para leitura humana da lista;
- esse rótulo é declarado não-autoritativo na interface: ele não é fonte de identidade, não é
  usado em nenhuma comparação e não afirma que a pessoa existe ou se chama assim;
- não existe busca por nome, sugestão nem desambiguação de homônimos, porque não há dado sobre o
  qual desambiguar. Fingir busca criaria um cadastro paralelo de pessoas — o que a 008 já recusou
  quando decidiu materializar o Edital sem cadastro de pessoas.

O gate de PC-005 permanece explícito e é a condição para produção. Quando o diretório existir, a
mudança é nesta camada e nos requisitos FR-016 a FR-021, e em nada mais.

### D-004 — Isolamento por escopo institucional

A mesma identidade pode integrar comissões de Processos em escopos institucionais distintos, e esses
vínculos são independentes entre si.

O invariante: toda consulta e toda alteração desta feature são limitadas pelo escopo do Processo, e
escopo divergente responde como recurso inexistente, conforme a convenção já vigente no projeto. A
unicidade de vínculo vale dentro do Processo, que já carrega o escopo.

A forma da chave física — `(processo, identity_subject)` ou equivalente — é decisão do `/plan`. A
011 não exige que o escopo seja copiado para cada tabela nova; exige que ninguém o atravesse. Sem
esse isolamento a 011 abriria vazamento entre unidades, que é o que a demonstração de segurança da
seção 49 existe para negar.

### D-005 — Comissão é dado operacional, e nunca conteúdo normativo

Não existe seção de comissão no catálogo normativo do Edital: a questão de "duas fontes
divergentes" não se coloca, porque só há uma. `MembroComissao` é a única representação de comissão
do sistema, e é operacional.

Portanto, como invariante desta feature: nada da 011 entra no conteúdo publicado, na Versão
Consolidada, no cálculo do hash ou no documento materializado; e nenhuma migration da 011 altera
`editais_etapaavaliacao` nem qualquer tabela de `publicacoes`. Esta é a P-001 da 008 reafirmada no
lugar onde ela seria abandonada por conveniência.

### D-006 — Duas portas, e ambas nomeadas

Existem dois caminhos legítimos até a página de uma Etapa, e eles não se misturam:

- **`Minhas Etapas`** é estritamente derivada de alocação ativa, para **qualquer** papel — inclusive
  presidente e inclusive ator com permissão sistêmica. Privilégio administrativo não injeta Etapa
  nessa lista.
- **A visão administrativa** do Processo mostra todas as Etapas e seus membros, e depende de
  permissão de gestão da comissão, não de alocação.

A porta administrativa tem duas bases, e cada uma autoriza sozinha: permissão sistêmica de gerir
comissão, ou vínculo ativo como `PRESIDENTE` daquele Processo (FR-016).

A página da Etapa pode ser alcançada pelas duas portas, e informa por qual atribuição o ator chegou.
Sem esta separação, "todos e somente" (FR-040) seria indemonstrável.

### D-007 — Alocar exige presidente; constituir, não

A Constituição atribui ao Presidente da Comissão a responsabilidade inicial pela gestão operacional.
A 011 não redefine essa autoridade e não cria mandato, sucessão, posse nem workflow de presidência.
Ela a honra com uma regra só:

> Uma comissão sem presidente pode ser constituída, mas não pode alocar.

A ausência de presidente é estado transitório e legítimo enquanto a comissão está sendo montada — é
o que evita exigir que o primeiro membro adicionado seja o presidente. A partir do momento em que
existe trabalho distribuído, existe responsável por ele, e esse responsável não pode desaparecer
enquanto houver alocação ativa.

---

## 4. Posição na jornada do produto

A decomposição funcional permanece:

> **009 coleta.**
> **010 devolve controle ao candidato.**
> **011 organiza o trabalho.**
> **012 executa o trabalho.**
> **013 produz consequência a partir do trabalho.**

Portanto:

### A 011 entrega

- constituição da comissão do Processo;
- definição de funções na comissão;
- alocação dos membros às Etapas;
- remoção e alteração dessas alocações;
- autorização contextual por Processo/Edital/Etapa;
- visão administrativa da organização do trabalho;
- visão pessoal `Minhas Etapas`;
- trilha de auditoria das alterações relevantes.

### A 011 não entrega

- ficha de avaliação;
- acesso a documentos como mesa de avaliação;
- pontuação;
- parecer;
- decisão;
- distribuição de candidatos;
- consolidação de notas;
- resultado de Etapa.

---

## 5. Precondições

**PC-001** — O modelo de Processo Seletivo, Edital e Etapa já deve existir.

**PC-002** — As Etapas utilizadas pela 011 pertencem a um **Edital**, e o Edital a um Processo
(D-001). A 011 não move a Etapa para o Processo, não a duplica e não cria coleção paralela de
Etapas.

**PC-003** — A 011 deve consumir os contratos existentes e não redefinir:

- `ProcessoSeletivo`;
- `Edital`;
- `EtapaAvaliacao`;
- Cronograma;
- estados de publicação;
- autoria/configuração normativa;
- `Inscricao`;
- identidade do candidato.

**PC-004** — A Área do Candidato não é dependência conceitual de autorização institucional.
Identidade de candidato e identidade institucional permanecem eixos distintos.

**PC-005** — As decisões de autorização da 011 valem o que valer a identidade que as sustenta. A
feature pode ser desenvolvida e demonstrada com o mecanismo institucional disponível no ambiente —
hoje, o seletor de identidade fora de produção —, mas subir a 011 em produção com ele permitiria a
qualquer pessoa declarar-se presidente e redistribuir a banca, sem tocar em um único dado de
candidato. Autenticação institucional confiável é gate de produção **desta** feature (D-003).

O gate correlato — abrir dados reais de candidatos a membros de comissão — pertence à 012, que é
onde esses dados aparecem.

**PC-006** — Toda consulta e toda alteração da 011 são limitadas pelo escopo institucional do
Processo (D-004).

---

## 6. Problema

A plataforma consegue estruturar o certame e receber inscrições, mas ainda não existe representação
explícita de:

- quem integra a comissão daquele Processo;
- qual é a função de cada integrante;
- em quais Etapas cada pessoa pode atuar;
- quais Processos/Etapas devem aparecer para cada membro;
- quem possui poder para alterar essa organização.

Sem isso, a operação tende a voltar para mecanismos externos:

- planilhas;
- listas em documentos;
- mensagens;
- pastas compartilhadas;
- combinações informais sobre "quem avalia o quê".

Isso também impede que features posteriores implementem autorização corretamente, pois "ser
avaliador" de forma global não responde:

> **avaliador de qual Processo e de qual Etapa?**

---

## 7. Princípios

### P-001 — Autorização é contextual

Ter uma função institucional capaz de participar de avaliações não significa acesso automático a
todos os Processos Seletivos. A autorização decorre do contexto:

> pessoa → comissão → Processo → Edital → Etapa.

### P-002 — Comissão do Processo e alocação na Etapa são conceitos diferentes

Uma pessoa pode integrar a comissão de um Processo e não estar alocada em todas as suas Etapas.

> **membro da comissão ≠ membro de todas as Etapas.**

### P-003 — Não criar grupos dinâmicos por certame

Não representar Processo, Edital, comissão ou Etapa como papel do sistema.

Concretamente, neste repositório: **a comissão não vira entrada em `PAPEIS`**
(`backend/processo_seletivo/interface/identidade.py`), e `PRESIDENTE` não é papel institucional —
é função dentro de uma comissão. Os papéis existentes continuam representando capacidades
sistêmicas gerais; a 011 representa autorização sobre objetos concretos. A proibição vale
igualmente para `Django Group`, que o projeto não usa como fonte de autorização e não passará a
usar por causa desta feature.

### P-004 — Alocação deve produzir efeito real

Não basta cadastrar nomes. Quando uma pessoa é alocada a uma Etapa, isso altera objetivamente
aquilo que ela consegue acessar.

Exemplo mínimo:

> a Etapa passa a aparecer em **Minhas Etapas**.

Sem alocação:

> aquele objeto não é acessível.

### P-005 — Privilégio mínimo

A pessoa recebe apenas o acesso necessário à sua atribuição. Participar do Processo não implica
administrar o Processo. Participar de uma Etapa não implica alterar sua configuração normativa.

### P-006 — Organização antes da execução

A 011 responde: quem trabalha onde? A 012 responderá: como esse trabalho é executado? Não
antecipar a Mesa de Avaliação.

### P-007 — A fronteira normativa é intransponível

A comissão é dado operacional. Nada da 011 entra no conteúdo publicado nem no hash (D-005).

---

## 8. Conceitos de domínio

Os nomes concretos podem ser reconciliados no `/plan`, mas conceitualmente a feature necessita de
duas entidades distintas.

### 8.1 Membro da Comissão

```text
MembroComissao
- Processo
- identificador institucional da pessoa (subject)
- rótulo de exibição (opcional, não-autoritativo)
- função
- ativo
- criado_em
- criado_por
```

Representa:

> esta pessoa integra a comissão deste Processo.

O escopo institucional não aparece na lista porque o Processo já o carrega (D-004). Onde ele precisa
existir fisicamente para sustentar unicidade e consulta é decisão do `/plan`.

### 8.2 Alocação em Etapa

```text
AlocacaoEtapa
- membro_comissao
- Edital
- identificador estável da Etapa
- ativo
- criado_em
- criado_por
```

Representa:

> este membro da comissão está autorizado a atuar nesta Etapa.

O Edital é referência real; a Etapa é referida pela identidade estável que o snapshot preserva. A
forma concreta é decisão do `/plan`, limitada pelo invariante de D-002.

---

## 9. Invariantes estruturais

**FR-001** — Um `MembroComissao` pertence a exatamente um Processo.

**FR-002** — A pessoa institucional é identificada pelo identificador estável já utilizado pela
camada institucional da aplicação, e nunca por nome ou rótulo.

**FR-003** — A mesma pessoa não pode possuir dois vínculos ativos equivalentes na comissão do mesmo
Processo. Em Processos de escopos institucionais distintos, os vínculos são independentes.

**FR-004** — Uma `AlocacaoEtapa` somente pode referenciar Etapa de um Edital **do mesmo Processo** do
`MembroComissao`. A verificação percorre `etapa → edital → processo`.

Logo é inválido:

```text
MembroComissao(Processo A)
        ↓
AlocacaoEtapa(Etapa de Edital do Processo B)
```

**FR-005** — Não permitir duplicidade ativa da mesma combinação: membro + Etapa.

**FR-006** — Remover uma alocação não remove o membro da comissão.

**FR-007** — Remover o membro da comissão elimina seu acesso às Etapas daquele Processo.

**FR-008** — A existência e a pertinência da Etapa alocada são verificadas no servidor a cada
operação e a cada acesso, porque a referência é pela identidade estável da Etapa (D-002).

A estratégia física de exclusão, inativação ou histórico pertence ao `/plan`, desde que a auditoria
seja preservada.

---

## 10. Funções na comissão

A 011 precisa distinguir pelo menos:

### Presidente/Responsável pela comissão

Pode organizar a composição e as alocações do Processo.

### Membro

Integra a comissão e pode receber alocações em Etapas.

**FR-009** — A função do membro deve ser explicitamente registrada.

**FR-010** — A V1 possui as funções conceituais `PRESIDENTE` e `MEMBRO`. O nome técnico segue as
convenções existentes.

**FR-011** — Não criar, nesta feature, taxonomia aberta de cargos ou funções customizadas por
Processo.

**FR-012** — Não inferir autorização de Etapa a partir da função na comissão. O presidente não
recebe alocação implícita: para aparecer em `Minhas Etapas`, ele precisa estar alocado como
qualquer outro (D-006). O que a função lhe dá é uma das duas bases de autorização para gerir a
composição (FR-016), e a visão administrativa que decorre dela.

---

## 11. Presidente versus ator administrativo superior

A plataforma já possui atores com capacidade sistêmica de administrar Processos. Isso não se
confunde com a presidência da comissão.

**FR-013** — Permissão administrativa global não transforma automaticamente a pessoa em
`MembroComissao`.

**FR-014** — Um ator com autorização sistêmica adequada pode constituir inicialmente a comissão
conforme as regras existentes de gestão do Processo.

**FR-015** — Depois de constituída, a gestão operacional da comissão pode ser exercida pelo
presidente conforme definido nesta spec.

**FR-016** — A gestão da comissão é autorizada por **uma de duas bases, cada uma suficiente
sozinha**:

- **permissão sistêmica nomeada** de gerir comissão — é como a comissão é constituída (FR-014) e
  como a administração superior intervém depois; ou
- **vínculo ativo como `PRESIDENTE`** daquele Processo (FR-015).

O presidente não precisa acumular a permissão sistêmica para gerir a própria comissão, e quem tem a
permissão sistêmica não precisa ser membro (FR-013). Nenhuma das duas cria papel novo: a primeira é
permissão nomeada no papel responsável, a segunda é contextual e vive no vínculo. Nenhuma das duas
injeta Etapa em `Minhas Etapas` (D-006). A base utilizada é registrada na trilha de auditoria.

**FR-017** — Toda autorização privilegiada adicional já existente no sistema continua explícita e não
é reproduzida por atalhos locais da 011.

---

## 12. US1 — Constituir a comissão

**Prioridade: P1**

Como responsável pelo Processo, quero cadastrar quem integra sua comissão para que a
responsabilidade institucional fique registrada dentro do sistema.

Página conceitual:

> **Comissão do Processo**
>
> Maria Silva
> Presidente
>
> João Souza
> Membro
>
> Ana Costa
> Membro
>
> **Adicionar membro**

---

## 13. Adicionar membro

Fluxo conceitual:

```text
Comissão
   ↓
Adicionar membro
   ↓
informar identificador institucional
   ↓
selecionar função
   ↓
confirmar
```

**FR-018** — O sistema identifica a pessoa pelo identificador institucional informado. Enquanto não
houver diretório, não existe busca por nome, sugestão nem lista de pessoas (D-003).

**FR-019** — Não criar cadastro de pessoa dentro da 011. O rótulo de exibição é campo de leitura
humana da própria lista, e não um registro de pessoa: ele não é pesquisável, não participa de
nenhuma comparação e não é usado para identificar ninguém.

**FR-020** — A interface declara explicitamente que o identificador é a chave e que o rótulo não é
verificado pelo sistema.

**FR-021** — Nome ou rótulo exibido isoladamente nunca é chave de identidade.

**FR-022** — Antes de confirmar, a tela mostra o identificador exatamente como será gravado, para
que o erro de digitação apareça antes da gravação e não depois.

**FR-023** — Quando o diretório institucional existir, FR-018 a FR-022 são substituídos por busca e
desambiguação reais. Até lá, não simular essa capacidade.

Não é requisito da 011 criar um diretório institucional.

---

## 14. Resultado da inclusão

**Given** um Processo existente
**And** Maria possui identificador institucional válido no escopo
**When** o responsável adiciona Maria como membro
**Then** Maria passa a constar da comissão daquele Processo
**And** isso, isoladamente, não concede a ela acesso a nenhuma Etapa.

---

## 15. US2 — Gerir composição

**Prioridade: P1**

Como presidente/responsável, quero alterar a composição da comissão quando houver substituições ou
mudanças de responsabilidade.

Ações mínimas: alterar função; remover membro.

### Alteração de função

**FR-024** — Usuário autorizado pode alterar a função de um membro.

**FR-025** — Alteração produz efeito de autorização imediatamente após persistida.

### Remoção

**FR-026** — Usuário autorizado pode remover/inativar membro da comissão.

**FR-027** — Um membro removido não continua acessando as Etapas por vínculos originados naquela
comissão.

**FR-028** — A remoção não modifica dados históricos produzidos por features posteriores.

Exemplo futuro: se João realizou uma avaliação na 012 e depois deixou a comissão, a autoria
histórica daquela avaliação não desaparece. A 011 apenas preserva essa possibilidade arquitetural;
não implementa `Avaliacao`.

---

## 16. Invariante de governança

**FR-029** — Uma comissão sem presidente pode ser constituída. Esse estado é válido apenas enquanto
não há alocação: a visão administrativa o sinaliza e nomeia o que ele impede (D-007).

**FR-030** — Nenhuma alocação de Etapa é criada enquanto a comissão não possuir presidente ativo. E
remover ou rebaixar o último presidente é recusado enquanto houver alocação ativa; a recusa nomeia o
caminho, que é atribuir outro presidente antes.

**FR-031** — Nenhuma operação pode deixar configuração estruturalmente inválida: vínculo ativo
duplicado, alocação para Etapa de outro Processo ou alocação de pessoa que não é membro ativo.

---

## 17. US3 — Alocar membros às Etapas

**Prioridade: P1**

Como presidente/responsável, quero indicar em quais Etapas cada membro atuará para que cada pessoa
receba somente o trabalho correspondente.

A organização é apresentada **por Edital publicado**, porque a Etapa pertence ao Edital, dois
Editais do mesmo Processo podem ter Etapas homônimas (D-001) e só há alocação a partir da publicação
(D-002):

> **Edital 07/2027**
>
> ### Análise documental
> - Maria Silva
> - João Souza
> `Gerenciar membros`
>
> ### Prova didática
> - Maria Silva
> - Ana Costa
> `Gerenciar membros`
>
> ### Entrevista
> Nenhum membro alocado
> `Adicionar membros`

---

## 18. Alocação

**FR-032** — Usuário autorizado pode alocar um membro da comissão a uma ou mais Etapas de Editais
**publicados** do mesmo Processo. Etapa de Edital ainda não publicado não é alocável, porque a fonte
da alocação é a Versão Consolidada vigente (D-002).

**FR-033** — Somente membros ativos de comissão que possua presidente ativo podem receber novas
alocações (FR-030).

**FR-034** — Não permitir alocar pessoa diretamente à Etapa sem que ela seja membro da comissão.

A jornada reflete o modelo:

```text
pessoa
  ↓
comissão
  ↓
Etapa
```

e não:

```text
pessoa
  ↓
Etapa
```

---

## 19. Remover alocação

**FR-035** — Usuário autorizado pode remover uma pessoa de determinada Etapa sem removê-la da
comissão.

**FR-036** — A remoção revoga imediatamente o acesso contextual decorrente daquela alocação.

---

## 20. Uma pessoa em várias Etapas

**FR-037** — O mesmo membro pode ser alocado em múltiplas Etapas do Processo, inclusive em Etapas de
Editais diferentes do mesmo Processo. Isso não exige duplicar o membro da comissão.

---

## 21. US4 — Visualizar organização do trabalho

**Prioridade: P1**

Como presidente/responsável, quero visualizar rapidamente quem está alocado em cada Etapa para
identificar lacunas sem recorrer a planilhas.

A interface responde com pouco esforço cognitivo:

- quais Editais e Etapas existem;
- quantos membros estão alocados;
- quem são;
- quais Etapas ainda não possuem ninguém.

### Visão recomendada

**Edital 07/2027**

| Etapa | Membros alocados | Situação |
|---|---:|---|
| Análise documental | 3 | Com equipe |
| Prova didática | 2 | Com equipe |
| Entrevista | 0 | **Sem membros** |

Uma Etapa sem alocação é visivelmente distinguível.

**FR-038** — A tela permite navegar da Etapa para a gestão de suas alocações.

**FR-039** — Não exigir abrir cada membro individualmente para descobrir a distribuição.

**FR-040** — Também é possível enxergar as Etapas atribuídas a determinado membro, com o Edital de
cada uma:

> **Maria Silva**
>
> Presidente
>
> Atua em:
>
> - Análise documental — Edital 07/2027
> - Prova didática — Edital 07/2027

---

## 22. Nenhuma distribuição automática

A 011 não conhece candidatos como unidades de trabalho. Portanto não criar round-robin,
balanceamento, sorteio, lote, carga máxima, distribuição por perfil, por candidato ou por
modalidade.

**FR-041** — A unidade de alocação da 011 é:

> **membro → Etapa**

e somente isso.

Se futuramente a 012 necessitar `avaliador → inscrições específicas`, isso será decisão daquela
feature.

---

## 23. Não introduzir `avaliadores_exigidos`

A quantidade necessária de avaliações por candidato pode representar regra normativa, configuração
operacional, propriedade da Etapa, regra do resultado ou característica da modalidade de avaliação.
Ainda não existe evidência suficiente para fixá-la na 011.

**FR-042** — Não adicionar `avaliadores_exigidos`, `numero_avaliadores`, `quorum` ou equivalente à
Etapa como consequência desta feature. Isso também é consequência de D-005: acrescentar campo a
`EtapaAvaliacao` alteraria conteúdo normativo publicável a partir de uma necessidade operacional.

A necessidade será classificada na 012/013.

---

## 24. US5 — Minhas Etapas

**Prioridade: P1**

Como membro da comissão, quero entrar no sistema e enxergar diretamente as Etapas em que tenho
atribuição.

> # Minhas Etapas
>
> **Análise de títulos**
> Edital 07/2027
> Processo Seletivo Docente
> **Abrir**
>
> **Prova didática**
> Edital 07/2027
> Processo Seletivo Docente
> **Abrir**

---

## 25. Regra de seleção

**FR-043** — `Minhas Etapas` mostra todos e somente os objetos aos quais a identidade institucional
possui alocação ativa, no escopo institucional do ator. A regra não tem exceção por papel:
privilégio administrativo não injeta Etapa nesta lista (D-006).

**FR-044** — Etapas de outros Processos não aparecem porque o usuário possui papel global.

**FR-045** — Etapa cuja alocação foi removida deixa de aparecer.

**FR-046** — O usuário pode possuir Etapas em vários Processos e Editais simultaneamente.

**FR-047** — Etapa cuja identidade não existe na Versão Consolidada vigente do Edital não é
listada. A condição é derivada na leitura, comparando a alocação com essa versão: não há campo,
sincronizador nem cópia da Etapa (EC-011). Criação, listagem e autorização consultam a mesma fonte,
pelo mesmo caminho.

---

## 26. Estado vazio

Pessoa institucional elegível, mas sem alocação:

> **Você não possui Etapas atribuídas no momento.**

Isso é um estado válido. Não apresentar erro, permissão quebrada ou Processo inexistente.

---

## 27. O que significa "Abrir Etapa" na 011

Esta fronteira é crítica. Abrir uma Etapa na 011 não significa abrir uma Mesa de Avaliação. A
página mostra somente informações necessárias para contextualizar a atribuição.

> # Análise de títulos
>
> **Edital 07/2027**
> Professor de Informática
>
> Você está alocado nesta Etapa.
>
> Período previsto: 05–08/10/2027
>
> A avaliação dos candidatos será disponibilizada quando a etapa correspondente estiver habilitada
> no sistema.

**FR-048** — A página da Etapa mostra metadados institucionais já públicos ou necessários à
identificação do trabalho.

**FR-049** — A página declara por qual atribuição o ator chegou até ela: alocação ou gestão
(D-006).

**FR-050** — A 011 não apresenta documentos dos candidatos como material de avaliação.

**FR-051** — A 011 não apresenta controles para avaliar, pontuar, emitir parecer, marcar candidato
como apto/inapto ou concluir avaliação.

**FR-052** — Não criar UI falsa/desabilitada antecipando a 012.

---

## 28. Autorização contextual

Este é um dos produtos centrais da feature.

```text
Pode acessar Etapa X?
        ↓
identidade institucional, no escopo de X
        ↓
X pertence a Edital de um Processo P?
        ↓
MembroComissao ativo em P?
        ↓
AlocacaoEtapa ativa para X?
        ↓
sim
```

O caminho administrativo é o outro, e é explícito: permissão de gestão da comissão sobre P.

---

## 29. Guards no servidor

**FR-053** — Toda rota protegida da comissão valida autorização no servidor, sobre o objeto pedido.
Que ocultar controle não é segurança e que identificador não confere autorização a Constituição já
diz; a 011 não reenuncia a regra — verifica-a nos casos concretos abaixo, que são os passos da
demonstração da seção 49 mais a convenção de resposta que os torna indistinguíveis de inexistência.

**FR-054** — Pessoa alocada ao Processo A não acessa Etapa do Processo B alterando o identificador
na URL.

**FR-055** — Pessoa alocada à Etapa A não recebe acesso à Etapa B do mesmo Edital ou do mesmo
Processo.

**FR-056** — Escopo institucional divergente responde como recurso inexistente, conforme a
convenção já vigente no projeto.

**FR-057** — Para objetos cuja existência não deva ser enumerável pelo usuário sem acesso, preferir
`404` conforme convenção existente da aplicação.

---

## 30. Papel global versus autorização contextual

Pode existir papel sistêmico semelhante a `AVALIADOR` ou outra capacidade institucional. Esse papel
responde: esta pessoa pertence à classe de usuários que pode exercer determinada capacidade. Ele
não responde: neste Processo?

**FR-058** — Papel global necessário, caso exista, é condição de capacidade e não fonte de
autorização sobre Processo/Etapa:

```text
capacidade institucional válida
        +
alocação contextual válida
        =
acesso
```

A implementação respeita o sistema de autorização já existente — permissões nomeadas verificadas
pelo command, e não grupos por objeto.

---

## 31. Usuários desabilitados/inválidos

**FR-059** — Identidade institucional indisponível, desativada ou sem condição de autenticar não
obtém acesso apenas porque existe registro histórico de comissão.

**FR-060** — A 011 não implementa gestão de ciclo de vida de contas institucionais. Ela respeita o
estado fornecido pelo mecanismo de identidade existente — que hoje não informa estado algum, o que
é exatamente o conteúdo do gate de PC-005 (D-003). Nenhuma verificação de conta é simulada
localmente.

---

## 32. Separação absoluta do candidato

Uma pessoa física pode ser, em contextos distintos, servidor/membro de comissão e candidato em
outro certame. Esses contextos não se contaminam.

**FR-061** — A identidade de candidato usada pela inscrição não concede autorização na 011.

**FR-062** — Identidade institucional da 011 não concede ownership sobre inscrições.

**FR-063** — Não fundir automaticamente os dois eixos porque CPF ou e-mail coincidam.

---

## 33. US6 — Alterações com efeito imediato

**Prioridade: P1**

Como gestor da comissão, quero que mudanças de alocação produzam efeito real no acesso.

### Cenário

**Given** João é membro da comissão
**And** João está alocado à Etapa A
**When** o presidente remove João da Etapa A
**Then** João deixa de vê-la em `Minhas Etapas`
**And** uma tentativa direta de abrir sua URL deixa de ser autorizada.

---

## 34. Concorrência e consistência

**FR-064** — Não permitir duplicidades decorrentes de submissões repetidas. A idempotência reutiliza
o mecanismo existente do projeto, com chave por escopo, ator, operação e chave da requisição; não se
cria mecanismo novo.

**FR-065** — Repetir acidentalmente a ação de adicionar o mesmo membro/alocação não produz registros
ativos duplicados.

**FR-066** — Operações concorrentes não produzem configuração estruturalmente inválida.

---

## 35. Relação com estado do Processo/Edital

A 011 não inventa nova máquina de estados.

**FR-067** — Respeitar as restrições de edição já definidas pelo domínio para o Processo em estado
final.

**FR-068** — Comissão e alocação são operacionais e permanecem alteráveis enquanto o Processo admite
alteração — inclusive, e sobretudo, depois de o Edital estar publicado, que é quando o trabalho
acontece e quando a alocação passa a ser possível (D-002). Alterar comissão nunca exige
Retificação.

**FR-069** — Nenhuma operação da 011 altera revisão, versão normativa, snapshot ou hash de Edital
(D-005).

---

## 36. Comissão normativa versus autorização operacional

Uma Portaria pode dizer formalmente quem compõe uma comissão; o sistema precisa saber quem possui
acesso operacional a determinada Etapa.

**FR-070** — Não existe hoje representação normativa da comissão no conteúdo do Edital: o catálogo
de seções não a contém. `MembroComissao` é a única representação de comissão do sistema, e é
operacional (D-005).

**FR-071** — Se um dia a comissão nominal integrar o conteúdo normativo, a relação entre os dois
registros é decidida naquela feature, e não por efeito colateral desta. A 011 não cria a segunda
fonte.

---

## 37. Auditoria

Alterações de autorização sobre Processos Seletivos são atos relevantes. São auditáveis: inclusão de
membro; remoção de membro; alteração de função; inclusão de alocação; remoção de alocação.

**FR-072** — Reutilizar a trilha de auditoria já existente, com sua permissão nomeada, seu escopo
institucional e sua natureza append-only.

**FR-073** — Não criar subsistema paralelo de logs de negócio.

**FR-074** — A trilha deve responder, sem recorrer a outro subsistema: quem alterou; em que
Processo; qual pessoa foi afetada; qual Etapa, quando aplicável; qual operação; e quando. A consulta
"o que mudou na comissão deste Processo" deve ser respondível.

Como o registrador existente é adaptado para isso é decisão do `/plan`. O que a spec proíbe é o
inverso: **não acrescentar estado, revisão ou ciclo de vida a membro ou alocação apenas para
satisfazer a forma do registrador**. Se a adaptação exigir criar registro paralelo, a decisão volta
à spec.

**FR-075** — Auditoria não registra dados de candidatos, pois esta feature não opera sobre eles, nem
o rótulo de exibição, que não é identidade.

---

## 38. UX — gestor

**UX-001** — A página separa claramente Comissão de Alocação por Etapa.

**UX-002** — Não apresentar formulário único com matriz de permissões técnicas. O usuário pensa em
pessoas e Etapas, não em ACLs.

**UX-003** — Uma ação de remoção deixa explícito se está removendo apenas da Etapa ou da comissão
inteira: **Remover desta Etapa** versus **Remover da comissão**.

**UX-004** — Não usar apenas ícones sem rótulo para ações destrutivas.

**UX-005** — Etapas sem membros são identificáveis rapidamente.

**UX-006** — Alterações bem-sucedidas produzem feedback perceptível.

**UX-007** — Quando o Processo tem mais de um Edital, a organização por Etapa nomeia o Edital antes
da Etapa, e nunca lista Etapas de Editais diferentes sem essa distinção (D-001).

---

## 39. UX — membro da comissão

**UX-008** — Após autenticação, o membro localiza suas atribuições sem navegar pela estrutura
administrativa do Processo.

**UX-009** — `Minhas Etapas` prioriza nome da Etapa; Edital/Processo; Perfil quando necessário para
desambiguação; período relevante; ação principal.

**UX-010** — Não mostrar controles administrativos para quem apenas executará trabalho futuro.

**UX-011** — Não mostrar Etapas não atribuídas como itens bloqueados. Elas não pertencem à área
pessoal daquele usuário.

---

## 40. Acessibilidade

A 011 herda os critérios institucionais de acessibilidade já adotados pelo projeto e não os
reenuncia: teclado, rótulos acessíveis e conformidade eMAG/WCAG são verificados item a item em
[checklist-ux.md](./checklist-ux.md), antes da entrega. Ficam aqui os dois critérios que são desta
feature e que a herança não cobre.

**FR-076** — Estado "sem membros alocados" não depende exclusivamente de cor.

**FR-077** — As duas remoções possuem nome acessível inequívoco que as distingue: remover da Etapa
não pode ser confundido com remover da comissão.

---

## 41. Responsividade

**FR-078** — Fluxos principais funcionam em viewport de 375 px sem rolagem horizontal da página.
Matrizes administrativas largas não são a única interface: em mobile, agrupamento por Etapa ou por
membro é preferível à tabela horizontal inviável.

---

## 42. Segurança de dados

A minimização de dado pessoal, a ausência de identificador sensível em URL e a contenção de log são
critérios institucionais herdados, verificados no [checklist-ux.md](./checklist-ux.md). Fica aqui o
que é desta feature.

**FR-079** — Não expor atributo institucional além do necessário para identificar a pessoa e operar
a comissão. O rótulo de exibição é o limite: ele existe para leitura humana da lista e não é
identidade (D-003).

---

## 43. Notificações

Fora da 011. Adicionar alguém a uma comissão ou Etapa não implica e-mail, SMS, push ou WhatsApp.

**FR-080** — A 011 registra a atribuição no sistema. Comunicação transacional pode ser tratada
posteriormente como capability própria.

---

## 44. Out of Scope

### Avaliação
ficha de avaliação; critérios de pontuação; notas; parecer textual; apto/inapto; assinatura de
avaliação; conclusão de avaliação.

### Candidatos
lista operacional de candidatos para banca; leitura de documentação como mesa de trabalho;
distribuição de inscrições; anonimização; impedimento por candidato.

### Consolidação
quantidade mínima de avaliações; divergência entre avaliadores; média; desempate; consenso;
resultado preliminar; resultado final.

### Recursos
recurso do candidato; resposta da banca; reconsideração.

### Comunicação
aviso de nova alocação; lembrete; cobrança de avaliação pendente.

### IAM
criação de conta institucional; troca de senha; MFA; integração GOV.BR; diretório corporativo
genérico.

### Workforce management
carga horária; produtividade; SLA de avaliador; balanceamento; distribuição automática; substituição
automática.

---

## 45. Invariantes de não regressão

A 011 não altera comportamento das features anteriores relacionado a: configuração do
Processo/Edital; publicação; vitrine pública; inscrição; documentos do candidato; submissão;
comprovante; Área do Candidato; ownership por identidade de candidato; storage privado; versão
normativa aceita.

**FR-081** — Nenhuma autorização institucional é implementada reutilizando ownership de candidato.

**FR-082** — Nenhuma mudança de comissão altera dados de inscrições.

**FR-083** — Nenhuma migration da 011 altera `editais_etapaavaliacao`, o Cronograma ou qualquer
tabela de `publicacoes`; nenhum código da 011 escreve nelas.

**FR-084** — Uma Retificação que remova ou altere Etapa alocada é aplicada normalmente, não falha e
não apaga alocação: a alocação passa a ser órfã, derivada na leitura (EC-011). Este é o teste de
regressão que prova D-002.

---

## 46. Success Criteria funcionais

**SC-001** — Responsável autorizado consegue adicionar pessoa institucional à comissão de um
Processo.

**SC-002** — A mesma pessoa não pode possuir vínculo ativo duplicado na mesma comissão.

**SC-003** — Membro da comissão pode ser alocado a uma ou várias Etapas de Editais publicados do
próprio Processo, e não a Etapa de Edital não publicado.

**SC-004** — Não é possível alocar membro de Processo A em Etapa de Edital do Processo B.

**SC-005** — Pessoa não integrante da comissão não pode receber alocação de Etapa.

**SC-006** — Remover uma alocação preserva o vínculo da pessoa com a comissão.

**SC-007** — Remover membro da comissão revoga os acessos derivados de suas alocações.

**SC-008** — `Minhas Etapas` contém todos e somente os objetos com alocação ativa, para qualquer
papel, dentro do escopo institucional do ator.

**SC-009** — Alterar manualmente o identificador de uma Etapa na URL não permite acesso a Etapa não
autorizada.

**SC-010** — Alocação a uma Etapa não concede acesso às demais Etapas do mesmo Edital ou Processo.

**SC-011** — Papel institucional global não concede isoladamente acesso a todos os Processos.

**SC-012** — Identidade de candidato não concede acesso à comissão.

**SC-013** — Inclusões, remoções e alterações relevantes ficam registradas na trilha de auditoria
existente, sem tabela nova.

**SC-014** — Uma Etapa sem membros é identificável na visão administrativa.

**SC-015** — A 011 não produz `Avaliacao`, nota, parecer ou resultado.

**SC-016** — Ator de outro escopo institucional não enxerga nem alcança comissão, alocação ou Etapa
deste escopo, e recebe a mesma resposta que receberia se o objeto não existisse.

**SC-017** — Gravar o rascunho de um Edital com Etapas alocadas não apaga alocações nem falha.

**SC-018** — Nenhum artefato publicado — snapshot, Versão Consolidada, hash ou documento — muda em
função de qualquer operação da 011.

**SC-019** — Não é possível criar alocação em comissão sem presidente ativo, nem deixar sem
presidente uma comissão que possua alocação ativa.

**SC-020** — O presidente gere a composição da própria comissão sem possuir a permissão sistêmica, e
quem possui a permissão sistêmica gere sem ser membro.

**SC-021** — Criação, listagem e autorização de alocação decidem pela mesma fonte: uma Etapa alocável
é uma Etapa que aparece em `Minhas Etapas` de quem foi alocado.

---

## 47. Success Criteria de UX

**SC-UX-001** — O responsável sabe, em uma única visão, quais Etapas possuem ou não membros
alocados, com o Edital de cada uma.

**SC-UX-002** — O responsável distingue claramente "remover da Etapa" de "remover da comissão".

**SC-UX-003** — Um membro autenticado chega às próprias Etapas sem navegar por telas administrativas
do Processo.

**SC-UX-004** — Usuário sem nenhuma alocação recebe estado vazio compreensível.

**SC-UX-005** — Fluxos principais são concluíveis somente pelo teclado.

**SC-UX-006** — Fluxos principais funcionam em 375 px sem rolagem horizontal da página.

**SC-UX-007** — Nenhuma informação essencial de estado depende somente de cor.

**SC-UX-008** — A interface deixa claro que o rótulo de exibição não é verificado pelo sistema e que
o identificador institucional é a chave.

---

## 48. Cenários de aceitação emblemáticos

### Cenário 1 — constituir comissão

Existe o Processo Seletivo Docente 2027, com o Edital 07/2027. Carlos possui autorização para gerir
o Processo. Carlos abre **Comissão** e adiciona Maria como Presidente, João e Ana como Membros.

Resultado: as três pertencem à comissão. Nenhuma recebeu acesso a Etapa alguma — inclusive Maria.

### Cenário 2 — organizar Etapas

O Edital 07/2027 possui Análise documental, Prova didática e Entrevista. Carlos ou Maria configura:
Análise documental com Maria e João; Prova didática com Maria e Ana; Entrevista com Ana.

O sistema passa a representar exatamente essa distribuição.

### Cenário 3 — experiência de João

João autentica institucionalmente e abre **Minhas Etapas**. Vê apenas Análise documental, do Edital
07/2027. Não vê Prova didática nem Entrevista.

### Cenário 4 — autorização por objeto

João copia a URL da Prova didática recebida de Maria. Mesmo autenticado: acesso recusado,
preferencialmente `404`. A autorização não depende da descoberta da URL.

### Cenário 5 — remoção de alocação

Maria remove João de Análise documental. João permanece membro da comissão, mas a Etapa desaparece
de `Minhas Etapas` e a URL direta deixa de abrir.

### Cenário 6 — remoção da comissão

João é removido da comissão inteira. Nenhuma autorização daquele Processo permanece ativa para João.
Não apagar eventual histórico produzido por features posteriores.

### Cenário 7 — a presidente também depende de alocação

Maria é presidente e não está alocada à Entrevista. `Minhas Etapas` de Maria não traz a Entrevista.
Maria continua vendo a Entrevista na visão administrativa, e a página da Etapa, quando alcançada por
ali, declara que ela chegou por gestão e não por atribuição.

---

## 49. Demonstração de segurança obrigatória

Preparar:

**Processo A** — Edital A, Etapa A1, João alocado em A1.
**Processo B** — Edital B, Etapa B1, João não pertence à comissão.
**Mesmo Processo A** — Etapa A2, João não alocado.
**Outro escopo institucional** — Processo C, Etapa C1.

No navegador de João:

1. A1 abre;
2. A2 retorna acesso negado/404;
3. B1 retorna acesso negado/404;
4. C1 retorna a mesma resposta de recurso inexistente;
5. alterar manualmente UUIDs não muda o resultado;
6. remover João de A1 revoga o acesso sem exigir alteração de papel global.

Essa demonstração comprova o principal contrato arquitetural da 011:

> **autorização por objeto, e não por título genérico de "avaliador".**

---

## 50. Demonstração de fronteira obrigatória

Ao abrir A1 como João, a interface pode mostrar "Você está alocado nesta Etapa". Mas não existe
lista de documentos para avaliar, nota, parecer, botão `Avaliar` nem botão `Concluir avaliação`.

Isso comprova que a 011 não invadiu a 012.

---

## 51. Edge cases mínimos

**EC-001 — usuário adicionado duas vezes.** Segunda tentativa não cria duplicidade.

**EC-002 — alocação repetida.** Não cria duas alocações ativas equivalentes.

**EC-003 — membro removido com várias Etapas.** Todos os acessos derivados daquele vínculo são
revogados de forma consistente.

**EC-004 — Etapa de outro Processo enviada manualmente.** Operação recusada no servidor, pela
verificação `etapa → edital → processo`.

**EC-005 — pessoa não membro enviada manualmente para endpoint de alocação.** Operação recusada.

**EC-006 — comissão sem presidente.** Constituir é permitido; alocar, não. Remover ou rebaixar o
último presidente é recusado enquanto houver alocação ativa, e a recusa nomeia o caminho: atribuir
outro presidente antes (D-007).

**EC-007 — usuário institucional desativado.** Não recebe acesso operacional só por vínculo
histórico. Enquanto o mecanismo de identidade não informar estado de conta, essa recusa depende dele
e não é simulada — é o gate de PC-005.

**EC-008 — Processo com nenhum Edital, ou Edital com nenhuma Etapa.** Comissão pode existir; a visão
de alocação apresenta estado vazio adequado, distinguindo "não há Edital" de "o Edital não tem
Etapas".

**EC-009 — Etapa sem membros.** Estado válido, claramente sinalizado ao responsável.

**EC-010 — membro sem Etapas.** Continua membro; `Minhas Etapas` fica vazia.

**EC-011 — a Etapa alocada desaparece.** Uma Retificação pode remover a Etapa do conteúdo publicado:
a alocação passa a designar identidade ausente da Versão Consolidada vigente. A condição é **derivada
na leitura** — sem flag, sem sincronizador, sem cópia da Etapa. A alocação não concede acesso, não
aparece em `Minhas Etapas` e é exibida ao gestor com a ação de removê-la. Não apagar em silêncio: a
auditoria já registrou que ela existiu.

**EC-014 — Edital ainda não publicado.** A comissão pode ser constituída, mas suas Etapas não são
alocáveis e a tela diz por quê, em vez de listá-las desabilitadas (D-002, FR-032).

**EC-012 — Processo com dois Editais.** A visão administrativa nomeia o Edital de cada Etapa, e
Etapas homônimas de Editais distintos são objetos distintos para alocação e para acesso.

**EC-013 — identificador inválido ou que nunca autentica.** Sem diretório, o sistema não pode
afirmar que uma pessoa não existe. Ele valida o formato mínimo, grava o identificador informado e o
compara exatamente com a identidade autenticada. Um identificador digitado errado produz um membro
que nunca autenticará: o gestor pode removê-lo, e a interface avisa que o identificador não é
verificado (D-003).

---

## 52. Ordem de implementação sugerida

Nenhuma entrega desta feature é um modelo sem tela. P-004 diz que alocação sem efeito observável não
é entrega, e isso vale também para a ordem em que se constrói.

| Slice | Entrega observável |
|---|---|
| **S1** | **A vertical inteira, no caminho feliz**: constituir comissão → designar presidente → alocar à Etapa de Edital publicado → o membro entra e vê a Etapa em `Minhas Etapas` → quem não foi alocado recebe 404 na mesma URL |
| **S2** | Alterar função, remover da Etapa, remover da comissão; visão administrativa com Etapas sem membros; auditoria das cinco operações |
| **S3** | Múltiplos Editais, alocações órfãs, concorrência e idempotência, escopo institucional, acessibilidade e 375 px |

S1 é a demonstração da seção 49 reduzida ao essencial, e é o que prova o contrato arquitetural da
feature. Se ela não couber numa entrega, o corte da spec está errado — não a ordem.

---

## 53. Diretriz para `/speckit-plan`

> ## Diretriz de implementação
>
> A 011 cria a camada operacional de composição da comissão e autorização contextual por Etapa.
>
> As sete Decisões fechadas da seção 3 já reconciliaram a spec com o modelo real, e a evidência que
> as motivou está em [research.md](./research.md). Não as reabra sem evidência nova; se abrir,
> registre lá.
>
> A alocação designa a Etapa pela identidade estável, e a fonte é uma só: a Versão Consolidada
> vigente. Só há alocação para Etapa de Edital publicado, e criação, listagem e autorização passam
> pelo mesmo resolvedor — uma Etapa alocável é exatamente uma Etapa que aparecerá em `Minhas Etapas`.
> Antes de escolher a forma, escreva o teste da Retificação que remove Etapa alocada: ela não pode
> falhar nem apagar alocação. O precedente é `Inscricao.profile_id`.
>
> Gerir a comissão é autorizado por duas bases independentes: permissão sistêmica nomeada, ou vínculo
> ativo como `PRESIDENTE` daquele Processo. Não exija as duas, e não transforme a segunda em papel.
>
> Toda consulta e toda alteração são limitadas pelo escopo do Processo. Não duplique o escopo em cada
> tabela nova por reflexo: o contêiner já o carrega.
>
> Alocar exige presidente ativo; constituir, não. Não implemente mandato, sucessão nem estado de
> presidência para isso — uma validação basta.
>
> A comissão não vira entrada em `PAPEIS`, e `PRESIDENTE` não é papel do sistema. Papel é capacidade
> sistêmica; comissão e alocação são autorização sobre objetos concretos. Isso vale igualmente para
> `Django Group`, que o projeto não usa como fonte de autorização.
>
> A permissão de gerir comissão é nomeada, entra no papel responsável e é a que aparece na trilha de
> auditoria — que é reutilizada como está, sem tabela nem coluna nova.
>
> Não reimplemente diretório institucional, não reimplemente autenticação e não simule busca de
> pessoas enquanto não houver diretório.
>
> Não crie distribuição por candidato. Não introduza `avaliadores_exigidos`, quorum, nota ou regra
> de consolidação. Não exponha documentos do candidato como mesa de trabalho.
>
> Nada da 011 toca conteúdo publicado, snapshot ou hash, nem escreve em tabelas de `editais` e
> `publicacoes`.
>
> Toda autorização é verificada no servidor. Toda alocação produz efeito observável para o ator
> alocado.
>
> A demonstração mínima da feature é:
>
> **gestor constitui comissão → aloca membro à Etapa → membro vê a Etapa → membro não alocado não a
> acessa.**
>
> Quando houver conflito entre construir uma abstração genérica de permissões e implementar a
> autorização contextual estritamente necessária ao Processo/Etapa, prefira a solução estreita
> aderente ao domínio.

---

## 54. Gate para a SPEC 012

A 011 está pronta para liberar a especificação da 012 quando estiver demonstrado que:

1. existe identidade institucional confiável para o ator, ou o gate de PC-005 está explicitamente
   registrado como pendência de produção;
2. existe comissão vinculada ao Processo, com escopo institucional;
3. existe alocação inequívoca por Etapa, resistente à recriação da coleção de Etapas;
4. existe guard reutilizável de autorização contextual;
5. `Minhas Etapas` reflete as alocações reais, para qualquer papel;
6. remoção de alocação revoga acesso;
7. o modelo não depende de papéis dinâmicos por certame;
8. nenhuma decisão sobre pontuação ou consolidação foi antecipada;
9. nenhum artefato publicado mudou por causa desta feature.

A partir daí, a 012 pode assumir como contrato:

> **se o ator chegou à Mesa de Avaliação de uma Etapa, sua autorização para atuar naquela Etapa já
> foi resolvida pela camada entregue na 011.**

E então responder exclusivamente à próxima pergunta:

> **O avaliador consegue executar o trabalho dentro do sistema?**
