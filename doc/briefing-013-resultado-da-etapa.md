# Briefing — 013: Resultado da Etapa

Ponto de partida da próxima sessão. Substitui o briefing anterior, que se chamava *Consolidação e
Resultado* e nascia da pergunta errada.

**Revisto em 03/09/2026**, depois da análise de três Editais reais do Cefor/Ifes — 35/2026 e
57/2026 (sorteio) e 14/2026 (títulos e entrevista). O que eles mostraram é que o roadmap enxergava
avaliação como o centro do Processo Seletivo, e ela é **um mecanismo entre outros**.

> **Corrigido em 03/09/2026, à noite.** Este briefing foi escrito de manhã, numa branch que ainda
> não continha `specs/013-consolidacao-resultado-etapa/` nem o app `processo_seletivo/resultados/`.
> A 013 foi mergeada às 19:29 (PR #26) e este documento às 19:34 (PR #27) — ele descreve, de
> boa-fé, um repositório que deixou de existir cinco minutos antes de ele entrar.
>
> **A 013 existe e está implementada.** O que este briefing chama de "a feature que vem depois" é a
> generalização dela, e não a sua primeira escrita. As três seções marcadas abaixo foram
> substituídas por [`briefing-revisao-012-013-formas-de-conclusao.md`](briefing-revisao-012-013-formas-de-conclusao.md);
> o resto — a fronteira, os seis invariantes e as lacunas — continua valendo.

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

## Dependência que precisa cair antes — **substituída**

*A dependência é real, e o escopo dela era estreito demais: a mesma premissa está na 013 já
implementada. Ver [`briefing-revisao-012-013-formas-de-conclusao.md`](briefing-revisao-012-013-formas-de-conclusao.md).
O texto abaixo fica como registro do que se sabia pela manhã.*

**A revisão do contrato de conclusão da 012** (`doc/decisao-012-conclusao-decisoria.md`). Hoje
concluir uma Avaliação exige nota — em constraint, em coluna não-nulável de tabela append-only e no
domínio. Enquanto isso valer, a análise documental dos Editais 35/57 não tem como ser concluída, e
a 013 ficaria sem uma das entradas que precisa consumir.

Não é dependência conceitual: a 013 não pressupõe `Avaliacao`. É dependência de **saber a forma
exata de uma das entradas** antes de escrever a spec que a consome.

### Duas perguntas que essa revisão terá de fechar — **fechadas em 03/09/2026**

Nasceram aqui como perguntas em aberto e foram respondidas antes de a revisão começar, que era a
condição para o `/plan` não herdar ambiguidade. Ficam registradas com a resposta.

**1 · O campo novo da Etapa cai no ponto cego da E2E-004 — confirmado, e a metade que importa é
barata.**

A forma da conclusão é propriedade publicada da Etapa, e a auditoria já registrava que a tela de
Retificação não alcança `maximumScore` nem `evaluationsPerRegistration`. A verificação confirmou a
causa exata: `interface/retificacao.py` declara

```python
CAMPOS_ETAPA = [
    ("name", ...), ("weight", ...), ("minimumScore", ...),
    ("eliminatory", ...), ("classificatory", ...),
]
```

Cinco campos. `forma`, `rotuloFavoravel` e `rotuloDesfavoravel` cairiam no mesmo buraco.

Mas `publicacoes/domain/colecoes.py` já lista `/stages` — **o domínio alcança; é a lista literal da
tela que está incompleta**. Completá-la são cinco linhas: os três campos novos mais os dois que a
012 deixou para trás. Isso parte a E2E-004 em duas metades desiguais:

| Metade | Estado da tela | Custo |
|---|---|---|
| **Etapa** | `CAMPOS_ETAPA` existe e está incompleta | linhas |
| **`documentRequirements`** | **não existe grupo nenhum** — sem lista de campos, sem renderização | grupo novo no formulário |

**A decisão:** a metade Etapa entra no escopo da revisão da 012. É onde os campos novos caem, custa
quase nada, e deixá-la de fora significaria publicar uma forma que só se corrige pela API. A metade
`documentRequirements` continua sendo a E2E-004 da leva corretiva — é trabalho de outra natureza.

**2 · O rótulo publicado é um par de campos na Etapa.**

```text
FAVORAVEL / DESFAVORAVEL   ← o que o domínio guarda, sempre
rotulo_favoravel           ← publicado pela Etapa
rotulo_desfavoravel        ← publicado pela Etapa
```

Assim os 35/57 publicam Deferido/Indeferido, a elegibilidade publica Apto/Inapto e a verificação
PcD publica Elegível/Não elegível, sobre o mesmo par que o domínio classifica.

**A decisão:** dois campos publicados, e não objeto genérico nem default institucional. É a forma
mais explícita, versionável e retificável, e é o que P-007 pede — o que o Edital publicou é o que
vale. Duas precisões que vão junto:

- **A condicionalidade é a mesma da conclusão.** Exigidos quando `forma = DECISORIA`, vazios quando
  `PONTUADA`. Uma Etapa pontuada não carrega rótulo que ninguém lê.
- **Prefill não é default.** A tela de elaboração pode sugerir "Deferido/Indeferido" como valor
  inicial editável; o que não pode existir é o domínio aplicar rótulo que o Edital não publicou.

### Ordem de execução da revisão da 012 — **substituída**

*O passo 7, `/specify` da 013, partia de um estado que não é o de `main`. A ordem vigente está no
briefing da revisão de compatibilidade.*


Com as duas fechadas, a emenda da spec vem antes do código: implementar contra a
`specs/012-mesa-de-avaliacao/spec.md` vigente, que ainda diz que concluir exige pontuação, criaria
a contradição que o Princípio V proíbe.

```text
1. branch própria
2. emendar specs/012 — D-008 no §5, ajuste do conceito 8.2 e FRs
3. modelo, constraint, snapshot v6, CAMPOS_ETAPA
4. Mesa: dois instrumentos conforme a forma
5. PDF: forma e rótulos no documento publicado
6. testes
7. /specify da 013
```

Além dos testes óbvios de ida e volta das duas formas, quatro que o projeto cobraria pelo padrão
que já pratica: a recusa da constraint verificada por `INSERT` cru, e não só pelo app; a leitura de
um snapshot versão 5 depois do salto para 6; forma e rótulos no PDF, senão a fonte estruturada e o
documento divergem; e a recusa HTTP no canal real, que a E2E-015 registra como faltante nos POSTs
de escrita da Mesa.

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

## Antes de tocar o código: exploração do que já existe — **substituída**

*Escrita como preparação para um `/specify` que já aconteceu. A lista continua útil como roteiro de
leitura, com um acréscimo que ela não podia prever: **ler também o app `resultados` e a
`specs/013-consolidacao-resultado-etapa/`**, que são a implementação da 013.*


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
| ~~**Desfecho de Etapa sem Avaliação**~~ — ausência, eliminação administrativa, não comparecimento | extensão da 013, antes da 014 | **decidido em 04/09** — FK anulável e `origem` declarada (D-1) |
| ~~**Dados estruturados do candidato**~~ | **015** | **decidido em 04/09** — o Edital declara os fatos, a inscrição os congela (D-2 de `doc/decisoes-pre-vertical.md`) |
| ~~**Cardinalidade da inscrição**~~ | execução dos 35/57 e do 14 | **decidido em 04/09** — `maxInscricoesPorCandidato`, anulável, publicado (D-3) |
| **Barema estruturado** | família 14/2026 | **fora do primeiro vertical por decisão** (D-4); spec própria depois |
| **Sorteio auditável** — importar ordem externa com origem, semente, artefato e hash | família 35/57 | mecanismo sobre a 013, depois dela |
| **Verificação de reserva de vaga** — heteroidentificação, indígena, PcD | família 35/57 | mecanismo sobre a 013, depois dela |
| **Notificações** — convocação por e-mail, com prazo contado do recebimento | **019** | E2E-016; a 010 limitou o canal por decisão |
| **Semântica de seleção discente** — curso, oferta, nível; hoje o vocabulário é de vaga de pessoal | antes de um Edital discente em produção | não bloqueia o backbone |
| **Campus como entidade** — hoje `PerfilVaga.locality` é texto livre, e um Edital multi-campus não tem como dizer para quais campi seleciona | qualquer Edital multi-campus, e a faceta de campus de um catálogo | não bloqueia o backbone; anda junto da semântica discente |
| **Autopontuação do candidato** (Anexo IV do Edital 14) | família 14/2026 | junto do barema |
| **Identidade Gov.br** | fidelidade literal aos 35/57 | método de autenticação sobre a mesma identidade estável |

> **De onde vem a lacuna de campus.** Ela não saiu dos três Editais analisados — saiu do catálogo
> público de processos seletivos do IFRN, que lista 682 processos com faceta de campus e mostra
> Editais destinados a mais de vinte campi de uma vez (`+19 campi` no Exame de Seleção). Multi-campus
> é a norma nesse porte de instituição, não a exceção, e `locality` como texto livre por Perfil não
> a expressa. O mesmo catálogo é evidência a favor da semântica discente: o IFRN serve seleção de
> estudante, contratação de pessoal, bolsa e seleção interna de servidor **no mesmo acervo**,
> tipando o processo em vez de bifurcar o sistema.

> **Onde a classificação de um Edital mora, quando ela existir.** O mesmo catálogo do IFRN
> apresenta os processos em nove categorias com contagem — *Estude no IFRN* (695), *Bolsas para
> estudantes* (295), *Servidores* (115), *Gestão IFRN* (10) —, e o sistema hoje não tem campo
> nenhum de tipo, subtipo ou nível: a única forma de saber que um Edital é de Especialização é ler
> o título. Se um dia houver classificação, ela **não é uma coisa só**, e a costura passa entre os
> dois níveis daquela taxonomia:
>
> - **O tipo é editorial.** *Estude* / *Trabalhe* / *Bolsas* muda com a gestão e não afeta direito
>   de ninguém. A própria lista denuncia: *Monitoria e Tutoria* (23) é bolsa e está fora de
>   *Bolsas para estudantes*; *Pesquise no IFRN* (3) convive com *Bolsas > Projetos de Pesquisa*.
>   Três das nove categorias têm menos de 25 processos, que é o que acontece quando se recorta
>   navegação por campanha e não por natureza.
> - **O subtipo é quase normativo.** *Graduação*, *Especialização*, *Concurso público para docente*
>   determinam família, requisitos e quais Etapas fazem sentido. É praticamente o tipo de processo
>   que falta ao domínio, e por isso pertence à semântica discente registrada acima.
>
> **A consequência prática, e a razão de registrar isto antes de alguém implementar:** neste
> sistema, o que é normativo entra no conteúdo publicado e só muda por Retificação — ato com
> homologação e publicação. Classificação editorial que entre por engano nesse caminho faz renomear
> uma categoria virar ato administrativo sobre todos os Editais dela. O tipo editorial é metadado
> fora do snapshot, sem retificação, sem PDF e sem subir `SCHEMA_VERSION`; só a natureza do
> processo é conteúdo publicado.
>
> Vale de passagem que a vitrine atual (`portal/views.py`) materializa todas as seleções vigentes e
> ordena em memória, sem paginação nem filtro no banco. Ela foi feita para dezenas; faceta com
> contagem sobre mais de mil processos é outro desenho de consulta.

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
