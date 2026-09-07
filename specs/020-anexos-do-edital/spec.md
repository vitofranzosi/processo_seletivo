# Feature Specification: Anexos do Edital

**Feature Branch**: `claude/edital-anexos-spec-f9bdf2`

**Created**: 2026-09-07

**Status**: Draft

**Input**: O Edital exige do candidato documentos em forma própria — autodeclaração étnico-racial,
declaração de pertencimento, anuência da chefia imediata, requerimento, procuração — e hoje manda
o candidato a um anexo que o documento publicado não contém. Esta feature entrega a primeira perna
do ciclo: o Edital passa a **carregar** o documento que ele próprio exige, sob a mesma vigência, a
mesma Retificação e a mesma consulta histórica do resto do seu conteúdo.

> Um Edital que exige documento em forma própria precisa publicar essa forma — sob a mesma
> vigência, a mesma Retificação e a mesma consulta histórica do resto do seu conteúdo.

E o corte que a mantém pequena:

> Isto não é uma feature de documentos. É uma feature de **conteúdo normativo binário versionado**.

Prompt de origem: `doc/prompt/020-anexos-do-edital.md`. Evidência: `doc/achados-editais-externos.md`,
`doc/avaliacao-de-capacidade-editais-2026-09-07.md` (L-5) e
`doc/descoberta-escopo-sorteio-e-anexos.md` (§Parte 2).

---

## 1. O que já está fechado, e que a 020 consome

### 1.1 A distinção que define a feature, e que ela não pode perder

```text
anexo como ARQUIVO      o autor sobe o formulário; o candidato baixa, preenche, assina,
                        digitaliza e devolve; a banca lê e defere.
                        O sistema NUNCA lê os campos.          ← ESTA FEATURE

anexo com CAMPOS        o autor declara campos; o candidato preenche dentro do sistema;
que o sistema conhece   o sistema gera o documento preenchido.  ← NÃO É ESTA FEATURE
```

A `009` já escreveu a recusa da segunda forma, e ela vale palavra por palavra: *"não há quinta
forma, não há operador e não há expressão — e é essa recusa que separa isto de um construtor de
formulários"*. O critério positivo também já existe, na docstring de `FatoDeclarado` (`015`): **o
campo existe porque uma regra publicada o consome**. Onde consome, ele já tem casa e não precisa de
anexo estruturado; onde não consome, é tela, e o arquivo basta.

Na amostra dos sete Editais há **um** campo que uma regra consome — a coluna "expectativa de
pontuação pelo candidato" das fichas do 14/2026 e do 173/2025, vinculante no segundo. Ele é do
**barema**, e trazê-lo para cá é como esta feature incha até virar outra.

Metade dos anexos exige assinatura e carimbo. O ciclo passa por imprimir e digitalizar porque a
**norma** exige, não porque o sistema seja pobre: não é limitação a superar.

### 1.2 A evidência que governa as decisões da §2

O Edital 73/2026 publica doze anexos, e a página dele mostra três fatos que não são hipótese:

```text
Edital        publicacoes.ifes.edu.br/cef/Edital-73-2026.pdf     publicado 16.07
Anexo I       drive.google.com/file/d/1Tgs2ip1eo…                RETIFICADO 31.08
Anexo II–XII  publicacoes.ifes.edu.br/cef/Anexo-II-…pdf          nomes sem versão
```

1. **o anexo é retificado sozinho**, quarenta e cinco dias depois, com o Edital permanecendo na
   versão original;
2. **os nomes não comportam duas versões** — caminho estável, sem data e sem revisão, de modo que
   a substituição no mesmo caminho **perde** o artefato anterior;
3. **a retificação vazou do acervo institucional para o Google Drive**, como o Resultado preliminar
   retificado e dois dos três Comunicados — o mesmo Drive que a docstring de `DocumentoSubmetido`
   diz que o sistema veio substituir, reaparecendo do lado do conteúdo normativo.

### 1.3 O que o repositório já entrega, e que esta feature não constrói

- **Anexar e avaliar já existem.** Das quatro etapas do ciclo, duas estão prontas: a inscrição
  recebe um arquivo por `DocumentoExigido`, validado como PDF pelo conteúdo, em armazenamento
  privado, com hash e congelamento no envio (`009`); a Etapa decisória, a mesa de avaliação e o
  `ResultadoEtapa` deferem e indeferem lendo o que voltou (`012`/`013`). **Esta feature não
  acrescenta máquina de avaliação nenhuma.**
- **Identidade estável, nunca posição** (`004`): o seletor de Retificação só aceita `id=<uuid>`, e
  coleção inendereçável é coleção irretificável.
- **Publicação append-only com bytes e hash**: `Publicacao` e `DocumentoPublicado` recusam
  sobrescrita e exclusão, e `document_hash` é integridade, não chave de unicidade.
- **Retificação, versão consolidada e consulta temporal** já existem, e o estado normativo vigente
  em qualquer instante já é reproduzível.
- **Concorrência entre Retificações já está resolvida**: `AlteracaoNormativa.expected_previous_hash`
  cobre duas Retificações sobre o mesmo alvo. Esta spec **herda; não desenha**.
- **A fronteira de regime já foi escrita** antes desta spec existir, na docstring de
  `inscricoes/storage.py`: a coluna binária de `DocumentoPublicado` foi considerada e recusada para
  o arquivo do candidato porque *"lá é um documento por publicação, imutável e pequeno"*, enquanto
  aqui são dez megabytes por requisito, por candidato, substituíveis durante o rascunho.
- **O padrão de identidade sem tabela de versões** é o do `SecaoEdital`: identidade estável,
  conteúdo que muda com a versão do Edital, nenhuma versão própria.

---

## 2. Decisões fechadas antes do planejamento

Não são perguntas para o `/plan`. Reabrir qualquer uma exige evidência nova.

### D-001 — Identidade normativa estável, separada do artefato binário

O Anexo tem identidade própria no conteúdo publicado; cada versão do Edital referencia, para essa
identidade, **um** artefato imutável endereçado por hash.

```text
Anexo VI  ← identidade normativa estável
   │
   ├─ conteúdo canônico da versão 3 → { id, rótulo, ordem, hash A }
   └─ conteúdo canônico da versão 4 → { id, rótulo, ordem, hash B }
```

As versões 3 e 4 são **do Edital**, não do anexo: não existe versão por anexo, pela mesma razão que
não existe por Seção. O que a decisão dispensa é **versionamento autônomo do anexo**, e é só isso —
ela não é de graça. O `DocumentoPublicado` de hoje é **um documento por publicação**, e nenhuma
publicação com nove anexos cabe aí sem mudança. Herdar `DocumentoPublicado` significa
herdar as **garantias** — bytes imutáveis, hash, append-only —, não necessariamente a mesma linha
da mesma tabela. Qual das duas formas é decisão do `/plan`.

### D-002 — Os anexos acompanham a publicação; não se incorporam ao documento principal

A justificativa é a prática observada, não uma limitação técnica: o Anexo I do 73/2026 foi
retificado sozinho. Incorporar faria a correção de um formulário **reescrever o documento normativo
inteiro**, que é o que a instituição demonstradamente não faz. O documento principal lista e
referencia; não carrega os bytes.

### D-003 — Seção estruturada rotulada como "Anexo" continua sendo Seção

A numeração editorial não determina a entidade de domínio. O Cronograma é gerado pelo catálogo, é
retificável por campos estruturados e aparece como "Anexo I" em cinco dos sete Editais lidos — e
continua sendo Seção. O Anexo desta feature é **opaco**: o sistema não conhece seus campos e o
retifica por substituição do artefato. Fundir os dois porque ambos aparecem sob o título "ANEXO" é
confundir forma editorial com natureza de conteúdo.

### D-004 — A versão aceita resolve o que estava **vigente**, e não o que o candidato baixou

Dada a versão consolidada aceita por uma Inscrição, o sistema deve dizer exatamente qual artefato
correspondia a cada anexo referenciado pelos documentos exigidos **naquela versão** — e responde
isso **sem guardar nada novo**: o hash já está no conteúdo canônico daquela versão, e a resolução é
consulta.

O que ele **não** afirma é qual versão do modelo o candidato de fato baixou e preencheu. A `009` já
separa as duas coisas, e a separação vale aqui: a versão reconhecida é o que ele viu enquanto
preenchia (FR-059a da `009`), a versão aceita é aquela sob a qual se inscreveu (FR-058) — nenhuma
das duas é proveniência de arquivo, e nenhuma pode ser: o PDF devolvido tem bytes diferentes do
modelo e o sistema deliberadamente não lê o que há dentro dele. **Conformidade do que voltou é
juízo da banca**, que já existe.

### D-005 — O anexo é PDF

Doze de doze no 73/2026; nenhum Edital lido publica anexo editável. Admitir `.docx` seria construir
para um caso que não existe, contra a disciplina que o próprio projeto escreve em `EtapaAvaliacao`
— *"admitir não é exigir"*. Entra quando aparecer o Edital que o exija, e com ele entram conversão,
visualizador e a pergunta de renderização, todos hoje inexistentes.

Não há dupla política de formato: anexo publicado e documento submetido são ambos PDF. O que separa
os dois não é formato, é **regime** — um é conteúdo público versionado, o outro é documento privado
do candidato.

### D-006 — O rótulo é campo versionado; não existe numeração automática

"ANEXO VI — AUTODECLARAÇÃO ÉTNICO-RACIAL" é **um campo de texto único** do Anexo no conteúdo
canônico daquela versão, escrito inteiro pelo autor e alterado só por Retificação explícita. Não se
parte em designação e título, porque dois campos convidariam a preencher o numeral pela posição —
que é exatamente o que esta decisão proíbe. O que não existe é numeração derivada: o sistema não
renumera nada, não calcula rótulo a partir de posição e não computa sequência atravessando a
coleção de Seções e a de Anexos. Acrescentar, remover ou reordenar não muda o rótulo de nenhum
outro anexo, e remover deixa **lacuna** na sequência.

A razão é a mesma que define a feature: os bytes do PDF podem trazer "ANEXO VI" impresso, e o
sistema não os lê nem os reescreve — rótulo derivado divergiria do artefato em silêncio. Renumerar
de verdade é substituir o artefato, e é ato do autor.

### D-007 — Regime de acesso: conteúdo público versionado

O artefato publicado é público por natureza — é norma. Pode reutilizar infraestrutura física de
armazenamento, mas **não** herda o regime da raiz privada da `009`, que existe para negar acesso a
documento de candidato. A spec não exige dois armazenamentos; exige que a fronteira de autorização
não se perca, nos dois sentidos: artefato de Edital publicado não pode ficar atrás de autenticação,
e artefato de Edital não publicado não pode ter endereço público.

### D-008 — As operações da Retificação sobre a coleção, todas por identidade

Cinco: **acrescentar**, **substituir o artefato**, **alterar o rótulo**, **alterar a ordem
editorial**, **remover da versão futura**. Nunca por posição. "Remover" significa **deixar de
existir na versão consolidada seguinte**, e nunca apagar do histórico. Os **bytes não viajam dentro
da alteração normativa**: o artefato entra antes, e a alteração referencia identidade e hash.

### D-009 — O vínculo não sobrevive ao alvo, e o Documento Exigido sobrevive

O `DocumentoExigido` pode apontar um Anexo como modelo. A cardinalidade não é decisão: uma
referência anulável já é `N:1` por construção. A forma da resposta ao alvo removido já está no
repositório, em `EtapaAvaliacao.evento` — *"remover o Evento não pode remover a Etapa; o que não
pode é o vínculo sobreviver a ele"*. Remover o Anexo não remove o Documento Exigido: desfaz o
vínculo, no mesmo ato, e conteúdo com referência pendurada é erro impeditivo de publicação.

### D-010 — A publicação é atômica

Ou o documento principal e todos os artefatos referenciados por aquela versão entram juntos, ou não
entra nenhum. Publicação com anexo faltando é Edital que manda o candidato a um anexo inexistente —
exatamente o defeito que a feature veio corrigir.

### D-011 — O endereço do anexo é da versão, nunca "o vigente"

Se a consulta de uma publicação histórica devolver o artefato atual, o Edital de então entrega o
conteúdo de agora. Esse é precisamente o defeito da prática observada — e é o que o passo
emblemático do teste de aceitação verifica.

O endereço é do **canal**, e não dos bytes: o documento principal lista os anexos pelo rótulo e não
imprime URL (clarificação de 07/09/2026). Assim a resolução por versão fica onde é verificável — a
publicação e a versão consolidada já são endereçáveis publicamente —, e o PDF imutável não carrega
um domínio que um dia muda.

### D-012 — Substituir o modelo não invalida o que já foi enviado

Se a Retificação substitui o modelo depois de o candidato ter enviado o arquivo preenchido, o
enviado continua valendo. A `009` já avisa e pede reconfirmação quando a versão muda (FR-059,
FR-059a), e o descarte da FR-031 é para requisito que deixou de ser aplicável — modelo substituído
não torna requisito inaplicável. Decidir o contrário exigiria dizer como o sistema saberia, e ele
não lê o arquivo (D-004).

---

## 3. Problema

O catálogo de Seções é declarado e fixo, com onze entradas e nenhuma delas anexo. Os Editais reais
têm de dois a onze anexos, e os do grupo mais agudo são **Documentos Exigidos cujo modelo o próprio
Edital fornece**: o sistema sabe exigir o documento e não sabe publicar a forma que o candidato
precisa preencher para produzi-lo.

O efeito é duplo. Para o candidato, o documento publicado promete um anexo que não existe. Para a
instituição, quando o anexo precisa mudar, a correção sai do acervo — vai para um Drive, ou
substitui o arquivo no mesmo caminho e apaga o artefato anterior, tornando irrespondível a pergunta
"o que estava valendo quando eu me inscrevi?".

---

## Clarifications

### Sessão 2026-09-07

- Q: O que o documento principal publicado carrega sobre cada anexo — só o rótulo, ou também o
  endereço para baixá-lo? → A: **Só o rótulo.** O endereço vive na página pública da seleção e na
  API da publicação, e não nos bytes do PDF.
- Q: Na página pública da seleção, todo visitante vê a coleção inteira de anexos, ou ela é filtrada
  pelo Perfil e pela modalidade? → A: **Coleção inteira**, na ordem editorial. O anexo é conteúdo do
  Edital e não tem Perfil próprio; a filtragem útil acontece no fluxo de inscrição, onde o candidato
  vê o modelo do requisito dele.
- Q: Durante a elaboração, um Anexo pode existir declarado sem artefato? → A: **Não.** Subir o
  arquivo é o que cria o Anexo; não existe anexo vazio, e por isso não existe estado intermediário a
  validar. O rótulo se escreve junto ou depois.
- Q: Trocando o arquivo de um Anexo antes de publicar, o que acontece com o artefato anterior, que
  nunca foi publicado? → A: **É descartado** — substituir sobrescreve, como a `009` decidiu para o
  arquivo do candidato. A imutabilidade vale para o artefato que alguma versão publicou; artefato
  que nenhuma publicação referencia não é histórico de nada.
- Q: O rótulo é um texto só ou dois campos, designação e título? → A: **Um texto só**, escrito
  inteiro pelo autor. Dois campos convidariam a preencher a designação pela posição, que é o que a
  D-006 proíbe.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O autor publica o Edital com os seus anexos (Priority: P1)

Quem elabora o Edital acrescenta ao conteúdo os formulários que o candidato terá de devolver
preenchidos, dá a cada um o rótulo com que o documento os cita, ordena-os, e publica. O documento
principal passa a listá-los; os artefatos vão junto.

**Why this priority**: é a perna que falta. Sem ela o ciclo não fecha, e as outras histórias não
têm objeto.

**Independent Test**: elaborar um Edital com três anexos pela interface administrativa, publicá-lo,
e abrir a página pública da seleção baixando os três — sem shell e sem manipulação de banco.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** o autor acrescenta um PDF com rótulo "ANEXO II —
   REQUERIMENTO DE INSCRIÇÃO", **Then** o anexo passa a integrar o conteúdo do Edital, com
   identidade própria, e aparece na lista de anexos do documento renderizado.
2. **Given** um Edital em elaboração com anexos, **When** o autor pede a publicação, **Then** o
   documento principal e todos os artefatos são publicados no mesmo ato.
3. **Given** um Edital em elaboração cujo artefato de um anexo se tornou indisponível ou não
   corresponde ao resumo registrado, **When** o autor pede a publicação, **Then** a publicação é
   recusada com erro impeditivo que nomeia o anexo, e nada é publicado.
4. **Given** um Edital ainda não publicado, **When** alguém sem autorização de elaboração tenta
   alcançar o artefato, **Then** o acesso é negado.

---

### User Story 2 — O candidato baixa o modelo e devolve preenchido (Priority: P1)

O candidato, na inscrição, encontra ao lado do requisito o modelo que o Edital manda usar, baixa,
preenche, assina, digitaliza e devolve pelo mesmo campo de sempre.

**Why this priority**: é o valor que o candidato recebe, e é o que hoje o manda para fora do
sistema.

**Independent Test**: percorrer a inscrição de um Perfil cujo requisito tem modelo, baixar o
modelo pelo portal e enviar o arquivo preenchido, sem sair do fluxo.

**Acceptance Scenarios**:

1. **Given** um requisito com modelo vinculado, **When** o candidato chega ao campo de envio,
   **Then** o modelo vigente é oferecido para download, identificado pelo rótulo.
2. **Given** um requisito sem modelo, **When** o candidato chega ao campo de envio, **Then** nada é
   oferecido e o campo funciona como hoje.
3. **Given** um modelo baixado e devolvido preenchido, **When** o candidato envia, **Then** o
   arquivo é recebido como `DocumentoSubmetido`, e o sistema não compara nem lê o conteúdo contra o
   modelo.
4. **Given** uma Retificação que substituiu o modelo depois do envio do arquivo no rascunho,
   **When** o candidato retoma o rascunho, **Then** ele é avisado da nova versão pelo mecanismo que
   já existe e **o arquivo enviado é preservado**.

---

### User Story 3 — A Retificação substitui um anexo, e os dois coexistem (Priority: P1)

Uma Retificação troca o formulário do Anexo VI. A partir dela, quem consulta o Edital recebe o
novo; quem abre a publicação anterior continua recebendo o antigo.

**Why this priority**: é o que separa esta feature de um gerenciador de arquivos, e é exatamente o
que a prática atual perde ao substituir o arquivo no mesmo caminho.

**Independent Test**: retificar um Edital publicado substituindo o artefato de um anexo, e
verificar que a publicação anterior e a vigente entregam bytes diferentes, com hashes distintos.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com o Anexo VI, **When** uma Retificação substitui o artefato,
   **Then** a identidade do Anexo VI é a mesma e o conteúdo da nova versão referencia o novo hash.
2. **Given** essa Retificação, **When** alguém abre a publicação anterior, **Then** recebe o
   artefato de então, e não o novo.
3. **Given** a mesma Retificação, **When** a consulta pública é feita por um instante anterior ao
   efeito, **Then** o anexo devolvido é o de então.
4. **Given** duas Retificações concorrentes sobre o mesmo anexo, **When** a segunda é aplicada
   sobre estado que mudou, **Then** ela é recusada pelo controle otimista que já existe.

---

### User Story 4 — A banca abre o modelo que estava valendo (Priority: P2)

Ao avaliar, a banca vê o documento apresentado e, ao lado, o modelo que estava vigente sob a versão
aceita daquela Inscrição.

**Why this priority**: torna o deferimento verificável sem inventar máquina de avaliação; depende
das duas primeiras histórias.

**Independent Test**: abrir a mesa de avaliação de uma Inscrição enviada sob a versão anterior a
uma Retificação e conferir que o modelo mostrado é o daquela versão.

**Acceptance Scenarios**:

1. **Given** uma Inscrição com versão aceita anterior à Retificação, **When** a banca abre o
   requisito, **Then** o modelo apresentado é o vigente **naquela** versão.
2. **Given** a mesma Inscrição, **When** a banca lê a tela, **Then** o sistema não afirma qual
   arquivo o candidato baixou, nem julga conformidade por conta própria.

---

### User Story 5 — O autor corrige a coleção sem quebrar o Edital (Priority: P2)

O autor renomeia um anexo, muda a ordem editorial e remove da versão futura um anexo que deixou de
existir — e o Edital continua íntegro.

**Why this priority**: é a manutenção normal do conteúdo publicado; sem ela a coleção é
inadministrável depois da primeira publicação.

**Independent Test**: aplicar as três operações por Retificação e verificar rótulos, ordem, lacuna
e ausência de referência pendurada.

**Acceptance Scenarios**:

1. **Given** uma coleção com seis anexos, **When** o quarto é removido da versão futura, **Then**
   os rótulos dos demais **não** mudam e a sequência fica com lacuna.
2. **Given** um anexo apontado como modelo por um Documento Exigido, **When** a Retificação o
   remove, **Then** o Documento Exigido continua existindo, sem modelo, e o conteúdo resultante não
   tem referência pendurada.
3. **Given** uma Retificação que deixaria referência pendurada, **When** ela é aplicada, **Then** é
   recusada com erro impeditivo que nomeia o vínculo.
4. **Given** um anexo removido da versão futura, **When** a publicação anterior é consultada,
   **Then** ele continua lá, íntegro.

---

### Edge Cases

- **Arquivo que não é PDF**, ou PDF só na extensão: recusado no envio do artefato, pelo conteúdo.
- **Mesmo artefato em dois anexos**, ou Retificação que reverte outra e reproduz bytes idênticos:
  legítimo. O hash é integridade, não unicidade.
- **Anexo sem nenhum Documento Exigido apontando**: legítimo — conteúdo programático, ficha
  informativa. O vínculo é opcional nos dois sentidos, e o anexo aparece na lista pública como os
  demais.
- **Anexo sem rótulo**: possível durante a elaboração, entre o envio do arquivo e a redação do
  rótulo; erro impeditivo na publicação.
- **Dois anexos com o mesmo rótulo**: o sistema não deduplica rótulo, porque rótulo não é
  identidade; a validação de publicação pode avisar, e não impedir.
- **Retificação que só troca o rótulo**, mantendo o artefato: legítima, e não cria artefato novo.
- **Edital cancelado ou com publicação revogada**: os artefatos seguem o destino do conteúdo, sem
  regra própria.
- **Anexo referenciado por um Perfil que a Retificação removeu**: o vínculo é do Documento Exigido,
  e segue a regra dele.
- **Publicação interrompida no meio**: nada entra (D-010), e o Edital permanece na versão anterior.

---

## Requirements *(mandatory)*

### Functional Requirements

**A coleção de Anexos no conteúdo do Edital**

- **FR-001**: O Edital MUST poder declarar uma coleção de **Anexos**, cada um com identidade
  própria, rótulo, ordem editorial e referência a exatamente um artefato binário.
- **FR-002**: A identidade do Anexo MUST ser estável e sobreviver a Retificação, e MUST NOT ser a
  posição, o rótulo ou o nome do arquivo.
- **FR-003**: A coleção MUST integrar o conteúdo publicado do Edital e MUST obedecer à validação
  das demais coleções publicadas, inclusive a exigência de identificador no formato aceito pelo
  seletor de Retificação.
- **FR-004**: O Anexo MUST NOT ter versão própria: a versão é a do Edital, como na Seção.
- **FR-005**: O rótulo MUST ser **um texto único** — designação e título juntos, como
  "ANEXO VI — AUTODECLARAÇÃO ÉTNICO-RACIAL" —, escrito inteiro pelo autor, e MUST integrar o
  conteúdo daquela versão. O sistema MUST NOT separá-lo em campos, e MUST NOT interpretá-lo.
- **FR-006**: O sistema MUST NOT derivar, calcular ou renumerar rótulo a partir de posição, ordem
  ou contagem, nem atravessando a coleção de Seções.
- **FR-007**: A ordem editorial MUST ser campo próprio, e MUST NOT ser derivada do rótulo.
  Alterá-la MUST NOT alterar o rótulo de nenhum Anexo.
- **FR-008**: Remover um Anexo MUST deixar lacuna na sequência de rótulos, e o sistema MUST NOT
  renumerar os remanescentes.

**O artefato**

- **FR-009**: O artefato MUST ser PDF, verificado pelo conteúdo do arquivo e não pela extensão ou
  pelo nome.
- **FR-010**: O artefato **referenciado por alguma versão publicada** MUST ser imutável, endereçado
  por resumo criptográfico, e MUST NOT ser sobrescrito nem excluído pela aplicação — nem quando uma
  Retificação posterior o substitui.
- **FR-010a**: Trocar o arquivo de um Anexo **antes da primeira publicação que o referencie** MUST
  substituir o artefato corrente, e o anterior MUST NOT ser preservado. Não há histórico de
  elaboração de artefato, e não há desfazer.
- **FR-011**: Artefatos de conteúdo idêntico MUST ser legítimos; o resumo criptográfico MUST ser
  tratado como integridade, e MUST NOT ser chave de unicidade.
- **FR-012**: Cada artefato MUST registrar tamanho, tipo, resumo criptográfico, autoria e instante
  do envio.
- **FR-013**: O limite de tamanho do artefato MUST ser da aplicação, e MUST NOT ser negociado pelo
  Edital.
- **FR-014**: O nome do arquivo enviado MUST ser preservado apenas para exibição, e MUST NOT
  decidir identidade, caminho ou endereço.

**Elaboração, revisão e homologação**

- **FR-015**: O autor MUST poder acrescentar, substituir, rotular, ordenar e remover Anexos de um
  Edital em elaboração, pela interface administrativa.
- **FR-015a**: O Anexo MUST nascer do envio do artefato: não existe Anexo sem artefato, em nenhum
  estado. O rótulo MUST poder ser escrito no envio ou depois, e MUST ser exigido antes da
  publicação.
- **FR-016**: Cada uma dessas operações MUST exigir a autorização de elaboração do Edital,
  verificada no backend.
- **FR-017**: Artefato de Edital ainda não publicado MUST NOT ter endereço público, e MUST ser
  alcançável apenas por quem tem autorização de elaboração, revisão ou homologação.
- **FR-018**: Os bytes examinados na revisão e na homologação MUST ser exatamente os que a
  publicação entregará. Como o resumo do artefato integra o conteúdo daquela versão (FR-029), trocar
  o arquivo depois da homologação MUST invalidá-la pelo mecanismo que já existe, e MUST NOT publicar
  bytes que ninguém homologou.
- **FR-019**: O documento renderizado em elaboração MUST listar os Anexos declarados, com rótulo e
  ordem.

**O vínculo com o Documento Exigido**

- **FR-020**: O `DocumentoExigido` MUST poder apontar no máximo um Anexo como modelo, por
  referência anulável.
- **FR-021**: O vínculo MUST ser feito pela identidade do Anexo, e MUST NOT usar rótulo, posição ou
  nome de arquivo.
- **FR-022**: Remover o Anexo MUST NOT remover o Documento Exigido; o vínculo MUST ser desfeito no
  mesmo ato que remove o alvo.
- **FR-023**: Conteúdo com vínculo apontando Anexo inexistente naquela versão MUST ser erro
  impeditivo de publicação e de Retificação, nomeando o vínculo.
- **FR-024**: O sistema MUST NOT exigir que todo Documento Exigido tenha modelo, nem que todo Anexo
  esteja vinculado.

**Publicação**

- **FR-025**: A publicação MUST ser atômica sobre o documento principal e todos os artefatos
  referenciados por aquela versão.
- **FR-026**: A publicação MUST ser recusada, com erro impeditivo que nomeia o Anexo, quando o
  artefato de algum Anexo estiver indisponível ou não corresponder ao resumo registrado.
- **FR-027**: O documento principal MUST listar os Anexos pelo rótulo e pela ordem editorial, e
  MUST NOT carregar os bytes deles.
- **FR-027a**: O documento principal MUST NOT imprimir endereço de download por anexo. O endereço
  MUST viver no canal — a página pública da seleção e a consulta da publicação —, para que os bytes
  imutáveis não fiquem presos a um domínio nem dependam de identidade alocada antes da renderização.
- **FR-028**: A referência publicada MUST resolver o artefato **daquela** publicação, e MUST NOT
  resolver "o vigente".
- **FR-029**: O conteúdo canônico de cada versão MUST registrar, para cada Anexo, identidade,
  rótulo, ordem e resumo criptográfico do artefato.
- **FR-030**: A inclusão de Anexos MUST NOT quebrar o determinismo do documento principal.

**Retificação**

- **FR-031**: A Retificação MUST admitir exatamente cinco operações sobre a coleção: acrescentar,
  substituir o artefato, alterar o rótulo, alterar a ordem editorial e remover da versão futura.
- **FR-032**: Toda operação MUST endereçar o Anexo por identidade, e MUST NOT aceitar seletor
  posicional.
- **FR-033**: Remover MUST significar deixar de existir na versão consolidada seguinte, e MUST NOT
  apagar artefato, publicação ou histórico.
- **FR-034**: Substituir o artefato MUST preservar a identidade do Anexo, e MUST NOT criar Anexo
  novo silenciosamente.
- **FR-035**: Os bytes do artefato MUST NOT viajar dentro da alteração normativa: o artefato MUST
  entrar antes, e a alteração MUST referenciar identidade e resumo criptográfico.
- **FR-036**: A concorrência entre Retificações sobre o mesmo Anexo MUST usar o controle otimista
  existente, e MUST NOT introduzir mecanismo novo.
- **FR-037**: Substituir, rotular, ordenar, acrescentar e remover Anexo depois da publicação MUST
  exigir a mesma autorização e o mesmo ato de Retificação dos demais conteúdos normativos.
- **FR-038**: Cada Retificação sobre Anexo MUST registrar autoria, motivo, instante e versão, na
  auditoria já existente.

**Consulta pública e histórica**

- **FR-039**: A página pública da seleção MUST oferecer **todos** os Anexos vigentes para download,
  na ordem editorial, identificados pelo rótulo.
- **FR-039a**: A lista pública MUST NOT ser filtrada por Perfil ou modalidade, e MUST NOT derivar
  aplicabilidade dos vínculos: o Anexo é conteúdo do Edital, e anexo que nenhum requisito aponta
  MUST aparecer como os demais.
- **FR-040**: A consulta do conteúdo por um instante MUST devolver os Anexos vigentes naquele
  instante, com os artefatos de então.
- **FR-041**: A consulta de uma publicação histórica MUST continuar entregando o artefato de então,
  e MUST NOT redirecionar para o vigente.
- **FR-042**: Artefatos de versões diferentes MUST coexistir, e MUST ter resumos distintos quando
  os bytes diferem.
- **FR-043**: Baixar anexo de Edital publicado MUST NOT exigir identificação nem autorização, e o
  sistema MUST NOT registrar quem baixou.

**Inscrição**

- **FR-044**: Na inscrição, todo requisito com modelo vinculado MUST oferecer o modelo para
  download junto ao campo de envio.
- **FR-045**: O modelo oferecido MUST ser o vigente, e a divergência entre a versão reconhecida e a
  vigente MUST ser tratada pelo aviso que já existe na `009`.
- **FR-046**: A substituição do modelo por Retificação MUST NOT descartar nem invalidar documento
  já enviado no rascunho.
- **FR-047**: O sistema MUST NOT ler, extrair, comparar ou verificar o conteúdo do arquivo
  devolvido contra o modelo.
- **FR-048**: Dada a versão aceita de uma Inscrição, o sistema MUST resolver qual artefato
  correspondia a cada Anexo referenciado pelos documentos exigidos naquela versão, sem dado novo
  por submissão.
- **FR-049**: O sistema MUST NOT afirmar qual versão do modelo o candidato utilizou.

**Avaliação**

- **FR-050**: A mesa de avaliação MUST poder abrir, a partir do documento apresentado, o modelo
  vigente sob a versão aceita daquela Inscrição.
- **FR-051**: Esta feature MUST NOT acrescentar critério, conferência automática ou qualquer
  máquina de avaliação.

**Regime, integridade e auditoria**

- **FR-052**: O regime de acesso dos artefatos MUST ser o de conteúdo público versionado, e MUST
  NOT herdar o da raiz privada dos documentos de candidato.
- **FR-053**: A cadeia versão histórica → identidade → resumo publicado → bytes MUST ser
  verificável internamente e coberta por teste.
- **FR-054**: A verificação de integridade MUST NOT ser exposta como funcionalidade ao usuário
  final.
- **FR-055**: Envio de artefato, vínculo, desvínculo e Retificação sobre Anexo MUST gerar evento de
  auditoria com ator, ação, entidade, identificador e instante.

### Key Entities

- **Anexo do Edital**: conteúdo normativo binário com identidade estável, rótulo editorial e ordem,
  declarado pelo Edital e publicado com ele. Não tem versão própria; a versão é a do Edital. É
  opaco: o sistema não conhece seus campos.
- **Artefato**: os bytes publicados de um Anexo numa versão, imutáveis, endereçados por resumo
  criptográfico, com tipo, tamanho, autoria e instante. Um Anexo referencia um artefato por versão;
  versões diferentes podem referenciar artefatos diferentes, e os anteriores permanecem.
- **Modelo do Documento Exigido**: a referência anulável do `DocumentoExigido` ao Anexo que serve de
  forma. Não é entidade nova, é campo — e não pode sobreviver ao alvo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quem elabora publica um Edital com anexos e quem consulta os baixa da página pública
  **sem autenticação, sem shell e sem manipulação de banco**, pelos canais de cada ator.
- **SC-002**: Retificado um anexo, a publicação anterior e a vigente entregam bytes diferentes, com
  resumos distintos, em 100% dos casos — nenhum artefato anterior é perdido.
- **SC-003**: A consulta por qualquer instante anterior devolve o anexo de então em 100% das
  verificações, incluindo instantes entre duas Retificações.
- **SC-004**: Nenhum Edital publicado referencia anexo inexistente, e nenhum requisito publicado
  aponta modelo removido: zero ocorrências, garantidas por erro impeditivo.
- **SC-005**: O ciclo do 173/2025 é demonstrável de ponta a ponta com os anexos-formulário —
  publicar, retificar preservando o anterior, baixar o vigente na data da inscrição, devolver
  preenchido, deferir, consultar o instante anterior e ver os dois artefatos coexistirem.
- **SC-006**: Acrescentar, remover ou reordenar anexos não altera o rótulo de nenhum outro anexo em
  nenhum caso.
- **SC-007**: A banca alcança o modelo vigente sob a versão aceita a partir do documento
  apresentado, sem sair da mesa de avaliação.
- **SC-008**: Nenhum artefato de Edital não publicado é alcançável por quem não tem autorização de
  elaboração, revisão ou homologação.

---

## Assumptions

- **O teste de aceitação é sobre os anexos-formulário.** Os anexos do 173/2025 caem nos dois grupos
  que a L-5 separou: formulários que o candidato devolve — autodeclaração étnico-racial, declaração
  de pertencimento quilombola, anuência da chefia imediata — e conteúdo normativo tabular — quadro
  de perfil, ficha de avaliação —, que é L-1 e barema, e está fora de escopo. O Cronograma, rotulado
  como anexo, é Seção (D-003). Cobrar os nove seria o teste contradizendo o escopo do mesmo
  documento.
- **Nenhuma proibição é construída para o conteúdo tabular.** O sistema não lê PDF e não classifica
  o que entra; proibir seria inexequível. Fica registrado o preço já apurado na nota de descoberta:
  conteúdo publicado não se remodela, e o Edital que publicar o quadro como binário fica assim para
  sempre.
- **O ciclo passa por papel.** Imprimir, assinar, carimbar e digitalizar é exigência da norma, não
  limitação do sistema, e não há requisito para superá-la.
- **O armazenamento físico pode ser compartilhado** com o que já existe, desde que o regime de
  autorização não se misture (D-007). Escolher a forma é do `/plan`.
- **A infraestrutura de Retificação, versão consolidada e consulta temporal é reutilizada
  integralmente**, incluindo o controle otimista de concorrência.

---

## Out of Scope

Cada item é feature própria, e nenhum deriva automaticamente desta.

- **Formato que não seja PDF**, e tudo que ele arrasta: conversão, visualizador, pacote ZIP,
  concatenação de documentos.
- **Quadro de vagas estruturado** (L-1) e **barema estruturado com autopontuação vinculante**.
- **Campos legíveis pelo sistema**, de qualquer natureza; **geração de documento preenchido**;
  **preenchimento web**; **editor online de anexo**.
- **Assinatura digital, ICP-Brasil e validação de assinatura.**
- **OCR, extração ou qualquer leitura do conteúdo do que o candidato devolve** — a `009` já recusou.
- **Rastreamento de download** e registro de qual artefato o candidato obteve.
- **Verificação de integridade exposta ao usuário final.**
- **Limite de páginas e limite de arquivo declarados pelo Edital** — pressão registrada contra a
  decisão vigente, feature própria.
- **Comunicados e atos normativos complementares** — publicação posterior que altera o certame sem
  ser Retificação, figura que o sistema não tem.
- **Relação de inscritos publicada.**
- **Sorteio, corte e progressão, ocupação de vagas, convocação.**
