# Briefing — 013: Resultado da Etapa

Ponto de partida da próxima sessão. Substitui o briefing anterior, que se chamava *Consolidação e
Resultado* e nascia da pergunta errada.

**Revisto em 03/09/2026**, depois da análise de três Editais reais do Cefor/Ifes — 35/2026 e
57/2026 (sorteio) e 14/2026 (títulos e entrevista). O que eles mostraram é que o roadmap enxergava
avaliação como o centro do Processo Seletivo, e ela é **um mecanismo entre outros**.

## A frase que governa

> Toda Etapa que produz consequência no Processo deve poder resultar em um Resultado da Etapa
> oficial, determinável e auditável, **independentemente do mecanismo que produziu sua evidência de
> origem**.

E o norte do arco inteiro, que esta feature abre:

> 012 conclui avaliações; 013 oficializa resultados de Etapa; 014 determina progressão; 015 ordena;
> 016 ocupa vagas. Nenhuma dessas capacidades deve depender de a origem ser títulos, entrevista,
> análise documental ou sorteio.

## Fronteira

```text
Mecanismo da Etapa
├── avaliação humana ......... 012 (pontuada ou decisória)
├── sorteio .................. ordem produzida e homologada
├── verificação de condição .. decisão de comissão
└── outro mecanismo normativamente definido
          │
          ▼
   evidência concluída
          │
          ▼
        013
          │
          ▼
  ResultadoEtapa oficial
```

A 013 **não** é onde alguém registra o deferimento documental — isso continua sendo trabalho da
Mesa. A 013 transforma trabalho concluído em consequência oficial da Etapa. É essa fronteira que
permite duas análises documentais divergentes, regra de maioria ou desempate entre pareceres sem
mexer no conceito de resultado oficial.

Nada que dependa de combinar Etapas entre si, classificar globalmente candidatos, ocupar vaga ou
tratar recurso pertence a esta feature.

## Dependência que precisa cair antes

**A revisão do contrato de conclusão da 012** (`doc/decisao-012-conclusao-decisoria.md`). Hoje
concluir uma Avaliação exige nota — em constraint, em coluna não-nulável de tabela append-only e no
domínio. Enquanto isso valer, a análise documental dos Editais 35/57 não tem como ser concluída, e
a 013 ficaria sem uma das entradas que precisa consumir.

Não é dependência conceitual: a 013 não pressupõe `Avaliacao`. É dependência de **saber a forma
exata de uma das entradas** antes de escrever a spec que a consome.

### Duas perguntas em aberto que essa revisão terá de fechar

Ficam registradas aqui, e não no documento de decisão, porque decisão é registro fechado e estas
ainda são perguntas. As duas atrasam a 013 se chegarem ao `/plan` sem resposta.

**1 · O campo novo da Etapa cai no ponto cego da E2E-004.** A forma da conclusão é propriedade
publicada da Etapa. A auditoria registra que a tela de Retificação alcança Etapas mas **não**
alcança `maximumScore` nem `evaluationsPerRegistration` — exatamente os campos que a 012
acrescentou à Etapa. É de esperar que `forma` caia no mesmo buraco, e isso precisa ser verificado,
não presumido.

```text
forma publicada errada → só se corrige pela API
```

Ou a revisão assume esse limite explicitamente, ou é o momento natural de fechar a E2E-004 — que já
era P0 antes do primeiro certame real, e cuja causa é a interface parar onde o domínio alcança
(`publicacoes/domain/colecoes.py`).

**2 · O rótulo publicado é mais de um campo.** A decisão diz que `Deferido/Indeferido` vem da
Etapa. Na prática isso é um **par** por Etapa decisória — o rótulo do sentido favorável e o do
desfavorável —, e o Edital 14 usaria outro par, e o Napne outro:

```text
FAVORAVEL / DESFAVORAVEL   ← o que o domínio guarda
Deferido / Indeferido      ← análise documental dos 35/57
Apto / Inapto              ← elegibilidade
Elegível / Não elegível    ← verificação PcD
```

A spec precisa resolver se são dois campos, um par estruturado, ou um default institucional que o
Edital sobrescreve. Não é grande, mas é ambiguidade que trava o planejamento — e, seja qual for a
forma, ela é conteúdo publicado e passa pelo mesmo caminho canônico do item 1.

## Os seis invariantes

**I-1 · Independência do mecanismo.** `ResultadoEtapa` não pressupõe `Avaliacao`. Avaliações,
ordem de sorteio e decisão de verificação são entradas de mesma dignidade.

**I-2 · Proveniência reprodutível.** Todo resultado identifica as entradas e a regra normativa
vigente que o produziram, **de modo que o mesmo resultado seja reproduzível a partir delas**.
Registrar o que foi usado e conseguir chegar de novo ao mesmo valor são coisas distintas, e a
Constituição pede a segunda: o estado normativo vigente em qualquer instante relevante deve ser
reproduzível.

**I-3 · Imutabilidade histórica.** Uma entrada já consumida por resultado oficial não é reescrita
retroativamente. Correção produz nova versão e consequência administrativa, nunca reescrita.

**I-4 · Prontidão delegada ao mecanismo.** Um resultado só pode ser oficializado quando o mecanismo
da Etapa declarar suas entradas completas e válidas. **A regra é do mecanismo, não do
`ResultadoEtapa`** — e é isso que mantém a 013 determinística sem amarrá-la a avaliações.

**I-5 · Autoridade.** Oficializar resultado é operação explícita, autorizada e auditável — nunca
efeito colateral de concluir a última avaliação. O Princípio III lista divulgação de resultado
entre os atos que exigem autorização específica, e o projeto inteiro separa quem elabora de quem
homologa e de quem publica.

**I-6 · Vigência não ambígua.** Para uma mesma Inscrição × Etapa existe **no máximo um**
`ResultadoEtapa` oficial vigente. Não "exatamente um": há momentos legítimos de vazio — antes da
conclusão da Etapa, e entre uma invalidação formal e sua substituição. Os resultados anteriores são
preservados.

## O que a D-1 anterior vira

O briefing antigo dizia: *"uma Inscrição só está pronta para consolidação quando possuir todas as
avaliações exigidas e elegíveis"*. A regra não desaparece — ela **deixa de ser regra do
`ResultadoEtapa` e passa a ser a regra de prontidão do mecanismo avaliação** (I-4). Cada mecanismo
declara a sua:

```text
avaliação   → todas as avaliações exigidas e elegíveis estão concluídas
sorteio     → a ordem está importada e homologada
verificação → a comissão competente decidiu
```

Continua não existindo, na V1: consolidação parcial, nota assumida, quórum reduzido nem
autorização excepcional da presidência. O déficit é estado operacional, não decisão de ninguém.

A D-2 anterior — avaliação consumida por resultado válido não pode ser reaberta — foi **preservada
e generalizada** em I-3: vale para a ordem sorteada importada e para a decisão de verificação pelo
mesmo motivo. O que ela impede continua sendo isto:

```text
resultado = 73 → reabre entrada → troca 72 por 52 → resultado continua 73
```

Anulação e reconsolidação, se vierem, são **ato explícito** — nunca efeito colateral da reabertura.

## Antes do `/specify`: exploração do código real

Ler a implementação da 012 — spec, research, models, guards, testes e contratos — e não preservar
nomes ou estruturas imaginadas se a 012 tiver implementado contratos diferentes. O §27 da 012 diz
o que ela se comprometeu a entregar como contrato; confira item a item.

Verificar especialmente:

- **quais formas de conclusão existem depois da revisão do contrato** (pontuada e decisória) e como
  a forma publicada da Etapa é lida;
- como a 012 determina `avaliacoes_elegiveis`, e onde vive a quantidade exigida (D-007: teto que a
  012 aplica, piso que a 013 cobra);
- como conclusão e reabertura funcionam, e como `ConclusaoAvaliacao` preserva o que havia antes;
- como a versão normativa que governou cada ato é preservada (FR-071) e como reproduzi-la;
- quais permissões existem hoje e qual é o padrão de segregação a seguir para I-5;
- como concorrência, idempotência e revisão são tratadas nos agregados existentes;
- se Etapa ou Perfil introduz restrição — a Etapa hoje pertence ao Edital, e a Constituição admite
  que o Perfil tenha as suas;
- que caminho o conteúdo canônico usa para campos novos, e o custo de subir `SCHEMA_VERSION`.

## Fora de escopo

Progressão entre Etapas, classificação global, desempate, ocupação de vaga, recurso, publicação de
resultado, convocação e notificação. Cada uma é feature própria no arco 014–019.

## Lacunas registradas — não entram nesta feature

As duas primeiras vêm da auditoria E2E de 02/09/2026; as demais foram identificadas na análise dos
três Editais reais e estão registradas **sem spec aberta e sem numeração**, porque ainda não há
justificativa para transformar ordem em compromisso de execução.

| Lacuna | Bloqueia | Quando |
|---|---|---|
| **E2E-004** — Retificação não alcança documentos exigidos pela interface | primeiro certame real | P0 antes da primeira seleção; não é pré-requisito da 013 |
| **E2E-021** — cancelamento de Retificação (decisão fechada, falta implementar) | — | próxima leva corretiva |
| **Dados estruturados do candidato** — a inscrição coleta nome, CPF, e-mail e telefone; o Edital 14 desempata por idade e não há data de nascimento | **015** | decidir antes da classificação; não é construtor genérico de formulários |
| **Cardinalidade da inscrição** — a restrição é `(identidade, edital, perfil)`; os Editais 14 e 57 exigem uma inscrição por Edital | execução dos 35/57 e do 14 | campo do Edital, sobe `SCHEMA_VERSION` |
| **Barema estruturado** | família 14/2026 | spec própria; §21 da 012 segue valendo |
| **Sorteio auditável** — importar ordem externa com origem, semente, artefato e hash | família 35/57 | mecanismo sobre a 013, depois dela |
| **Verificação de reserva de vaga** — heteroidentificação, indígena, PcD | família 35/57 | mecanismo sobre a 013, depois dela |
| **Notificações** — convocação por e-mail, com prazo contado do recebimento | **019** | E2E-016; a 010 limitou o canal por decisão |
| **Semântica de seleção discente** — curso, oferta, nível; hoje o vocabulário é de vaga de pessoal | antes de um Edital discente em produção | não bloqueia o backbone |
| **Autopontuação do candidato** (Anexo IV do Edital 14) | família 14/2026 | junto do barema |
| **Identidade Gov.br** | fidelidade literal aos 35/57 | método de autenticação sobre a mesma identidade estável |

## Uma observação de arquitetura para 015 e 016, registrada aqui para não se perder

O processo real **não é um pipeline**. A cascata dos Editais 35/57 — indeferiu, analisa o próximo,
até preencher as vagas — faz a progressão depender da contagem de vagas, e a verificação da
autodeclaração devolve o candidato à lista de ampla concorrência, mudando a alocação depois de ela
já existir.

A saída, quando 015 e 016 forem escritas: **classificação e alocação são computação determinística
sobre entradas versionadas, e o artefato que elas produzem é emitido por ato administrativo.**

```text
calcular(...) → proposta determinística → EMITIR/HOMOLOGAR → snapshot oficial imutável
```

Entrada nova torna o snapshot vigente **obsoleto**, e não inválido: alguém autorizado precisa
emitir o próximo. E a divergência entre o estado computado e o oficialmente vigente **precisa ser
observável na interface** — pelo Princípio VI, capacidade que o domínio sustenta e nenhuma
interface alcança não está entregue.
