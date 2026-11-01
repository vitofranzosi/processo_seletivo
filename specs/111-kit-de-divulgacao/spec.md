# Feature Specification: Kit de Divulgação do Edital

**Feature Branch**: `claude/gps-kit-divulgacao-viabilidade-63c68e`, sobre a `main` em `4ca16b1d`

**Created**: 2026-10-31

**Status**: Especificada, planejada e revista em 31/10–01/11/2026. A
[revisão crítica independente](revisao-critica.md) encontrou 26 achados, três deles bloqueantes, e
todos foram incorporados. Em 01/11 o usuário aprovou a divisão A → B → C, pediu duas correções de
consistência (feitas) e encaminhou a P-2 a spec própria. **Não implementada.** A sequência
aprovada: o incremento A pode começar; a atribuição do papel espera a spec da P-2; o B e o C vêm
depois, com a verificação do motor antes da integração e os ativos oficiais antes da liberação.

**Input**: o pedido de 31/10/2026, "GPS — Especificação SDD/SpecKit do Kit de Divulgação", que
aprova uma spec **integrada**: ficha estruturada, kit textual e peça visual. A investigação que a
precede está em dois documentos:

- o [estudo de viabilidade](../../doc/estudo-kit-de-divulgacao-2026-10-31.md), eixos A a J;
- a [POC integrada](../../doc/poc-kit-de-divulgacao-2026-10-31/README.md), com 11 cenários publicados
  pelo fluxo real, a galeria das peças e o wireframe.

> **Faixa de identificadores.** Esta spec abre em **FR-3401** e **SC-1051**. O teto medido em
> 31/10/2026 na `main` e em todas as worktrees desta máquina é o requisito três mil trezentos e
> quarenta e três e o critério mil e quarenta e oito, os dois da `110`. A folga até a abertura é
> deliberada, porque pode haver spec paralela ainda sem pasta. **Nenhum `UX-` é aberto aqui.** As
> decisões técnicas reiniciam em `D-001` e moram no [research.md](research.md); as pendências de
> produto são `P-`; os casos-limite são `EC-`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-761 da `047`"). Decisão de outra feature pelo assunto e pela feature, porque `D-` aqui é só
> desta.

---

## Por que esta feature existe

**Hoje a comunicação lê o PDF do Edital para divulgá-lo.** Ela extrai período, opções, vagas e
localidades, monta a arte e escreve a legenda. Isso tem dois custos:

- é trabalho repetido a cada Edital;
- é onde nasce o erro: a data de antes da prorrogação, a soma de vagas lida como de cada polo,
  "inscrições abertas" num Edital cujas inscrições ainda não começaram.

**O GPS já calcula, com regra escrita e testada, quase tudo o que a divulgação precisa afirmar.**
- A página pública da seleção lê só a versão vigente.
- O desfecho vence o período (FR-761 da `047`).
- A oferta é dita por Perfil (FR-1607 da `072`).
- O período de inscrições tem regra própria, que já distingue o cancelado.
- A origem de cada valor já tem regra (FR-1437 da `070`).

O kit **reaproveita essas regras**, e não as reescreve.

**A POC provou a arquitetura.** Uma ficha só, lida do publicado, alimenta os textos e a peça. Uma
conferência automática prova que a peça não diz nada que a ficha não diga. A POC também mostrou o
limite: as conferências provam **coerência**, e não **legibilidade**. Quatro defeitos visuais só
apareceram olhando as imagens. Por isso esta spec exige teste geométrico **e** revisão humana.

### O que existe e é reaproveitado

| Peça | Onde | Nesta spec |
|---|---|---|
| Versão vigente no instante | `publicacoes/application/selectors.py` (`effective_version`) | Usada como está |
| Retificação de vigência futura | `interface/agenda.py` (`retificacoes_a_vigorar`) | **Movida** para `publicacoes/application/selectors.py` (D-002) |
| Original × vigente e a prorrogação | `interface/relatorio_do_edital.py` (`_versoes`, e a regra em linha de `fatos_do_edital`) | **Extraída** como `prorrogacao(original, vigente)` em `publicacoes/application/selectors.py`, usada pelo relatório e pela ficha (D-002) |
| Origem de cada valor | `duvidas/domain/origem.py` (`origens`, `acrescimos`) e `duvidas/application/consultar.py` (`contexto`) | Usadas como estão: o `contexto()` monta atos e registros pela regra da `070`, e o portal já o importa (D-002) |
| Numeração das Retificações publicadas | `interface/relatorio_do_edital.py` (`_retificacoes_publicadas`) | Uma só, compartilhada (FR-3406) |
| Período de inscrições, inclusive o cancelado | `inscricoes/domain/periodo.py` (`periodo_de_inscricoes`) | Usada como está |
| Desfecho do Edital e do Processo | `processos/application/selectors.py` (`desfechos`) | Usada como está |
| Situação pública, quantidade, reserva, teto com "+N" | `portal/leitura.py` (`situacao_publica`, `quantidade_da_oferta`, `TIPOS_COM_RESERVA`, `os_primeiros`) | Usadas como estão |
| Vagas saneadas do conteúdo | `interface/visao_geral.py` (`vagas_do_conteudo`) | Usada como está |
| Unidade do ato, com a recaída de antes da `060` | `unidades/application/identificacao.py` (`do_ato`) | Usada como está |
| Métrica da fonte e quebra por largura | `publicacoes/infrastructure/fonte.py` (`MetricaEmbutida`); `publicacoes/infrastructure/pdf.py` (`_quebrar`) | Apelido público, sem renomear (D-009) |
| Repertório de caracteres | `publicacoes/domain/grafia.py` | Usado como está |
| Hosts que não são endereço público | `interface/relatorio.py` (`HOSTS_LOCAIS`, `_host_local`) | Usado como está (FR-3447) |
| Ação no detalhe, indisponível com motivo | `interface/acoes.py` (padrão do "Relatório do Edital", `099`) | Mesmo padrão |
| Registro na trilha e leitura do `detalhe` | `auditoria/application.py` (`record_event`); `APLICAR_A_TODOS` em `interface/views.py` | Mesmo padrão (D-005) |
| Lista de palavras que as telas públicas não dizem | `tests/portal/test_acompanhamento_pela_situacao.py` (`PROIBIDAS`) | Aplicada às frases do kit (FR-3414) |

### O que esta spec cobre, e o que fica fora

| Cobre | Fora |
|---|---|
| A ficha da versão vigente, os textos e uma peça feed 1080 × 1350 em SVG e PNG | Stories, quadrado, banner do site; mais de um template; temas por campus |
| Inscrições futuras ou em andamento, prorrogação, Edital sem período designado | Material de **resultado** e de **convocação**; material por Evento do cronograma |
| Cópia de cada texto; exportação em PNG, SVG, Markdown, texto simples e ZIP | Publicação em rede social; agendamento; geração automática por evento |
| Registro de cada exportação; aviso de desatualização e de desfecho | Guarda dos arquivos gerados; aprovação peça a peça |
| Uma capacidade própria e um papel restrito | Mudança na política de leitura do rascunho (P-2 decide) |
| Manchete escolhida entre formas fechadas, só quando nenhum título oficial cabe | Texto livre na peça ou nos textos; editor gráfico; IA generativa |
| — | Open Graph, endereço legível, origem de campanha, Ifes Ads (specs próprias, se vierem) |

### A direção de produto que esta spec abre, e não implementa

O nome dessa direção é **Comunicação do Ciclo do Processo Seletivo**. Esta spec é o primeiro
componente dela: o material de **inscrições** de um Edital publicado. Os marcos seguintes têm fontes
de maturidade diferente:

| Marco | Fonte publicada | Situação |
|---|---|---|
| Publicação do Edital; inscrições; prorrogação | `Publicacao`, período, original × vigente | **Esta spec** |
| Aproximação do encerramento | O mesmo período | Coberta como data absoluta. A chamada "últimos dias" é juízo que fica falso, e não entra (FR-3414) |
| Resultado publicado | `PublicacaoResultado`, por Perfil × etapa × lista, preliminar ou definitivo | Possível em spec futura, com regra de agregação própria e sem nomes |
| Convocação | **O GPS não publica convocação** (`convocacao/models.py`) | Exige antes uma feature de publicação de convocação |
| Outro Evento do cronograma | O tipo do Evento é texto livre | Exige tipagem de Evento, recusada até aqui (RC-76 da `047`) |

A arquitetura admite novos **modos** da ficha, um por marco, cada um com os seus campos e as suas
regras. Ela **não** cria agora abstração genérica de marco nem de campanha (D-003).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Conferir e copiar os textos oficiais de um Edital publicado (Priority: P1) 🎯 MVP

Alguém da comunicação abre o Edital publicado e entra em "Kit de divulgação". A tela mostra primeiro
as informações oficiais para conferência: período, opções com localidade e vagas, unidade, de que
publicação veio cada dado e a versão usada. Depois mostra os textos prontos, cada um com "Copiar". A
pessoa copia a legenda e o texto para mensagens, e escreve a arte na própria ferramenta sem abrir o
PDF do Edital.

**Why this priority**: é o produto permanente do kit, útil com ou sem peça visual. Sem esta história
não há kit.

**Independent Test**: com o 91/2026 do corpus publicado e retificado, abrir a tela como alguém do
papel de comunicação e conferir:

- o período é o vigente depois da prorrogação;
- a proveniência do término aponta a Retificação;
- a oferta lista as quatro localidades com as quantidades da página da seleção;
- a legenda não contém "abertas" nem tempo relativo.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com inscrições futuras, **When** a pessoa abre o kit, **Then** os
   textos dizem "Inscrições de DD/MM/AAAA a DD/MM/AAAA, até as HHhMM (horário de Brasília)" e nenhum
   diz que as inscrições estão abertas.
2. **Given** o mesmo Edital no segundo dia do período, **When** a pessoa abre o kit, **Then** os
   textos publicáveis e a peça são os mesmos do cenário 1, porque a norma não mudou com o relógio.
3. **Given** um Edital prorrogado por Retificação, **When** a pessoa abre o kit, **Then** o término é
   o vigente, os textos dizem que o prazo foi prorrogado e de qual data para qual, e a conferência
   mostra que o término veio da Retificação nº N.
4. **Given** a tela aberta, **When** a pessoa aciona "Copiar" na legenda, **Then** o texto vai para a
   área de transferência e a tela anuncia que foi copiado. Sem script, o texto continua selecionável.

---

### User Story 2 — Baixar a peça pronta, coerente com os textos (Priority: P1)

A pessoa confere a prévia da peça 1080 × 1350 na mesma tela, lê o texto alternativo e baixa o PNG
(ou o SVG). A peça diz exatamente o que a ficha diz, em datas absolutas, com o endereço e a busca pelo
número do Edital.

**Why this priority**: é o segundo produto do kit, aprovado junto do primeiro.

**Independent Test**: para cada cenário de referência (§Cenários de referência), gerar a peça e
conferir:

- todo texto da peça é valor da ficha, frase fixa do template ou manchete da lista fechada;
- toda data e quantidade da peça está nos textos;
- nenhum texto sai da área útil nem se sobrepõe a outro;
- duas gerações dão os mesmos bytes.

**Acceptance Scenarios**:

1. **Given** um Edital com quatro opções de mesmo nome em localidades diferentes, **When** a peça é
   gerada, **Then** ela mostra o nome uma vez, as quatro localidades com as quantidades e "N vagas em
   4 opções", e cabe sem colisão.
2. **Given** um Edital com 18 opções e título de 208 caracteres, **When** a peça é gerada, **Then**
   ela mostra a contagem de opções com o convite à página, usa o título do Processo e a tela diz que
   o título do Edital não coube.
3. **Given** um Edital sem período de inscrições designado, **When** a peça é gerada, **Then** ela diz
   "Edital publicado" e nenhuma palavra sobre inscrição.
4. **Given** um título que não cabe nem como título do Edital nem como do Processo, **When** a pessoa
   escolhe uma das manchetes oferecidas, **Then** a peça a usa, os textos mantêm o título oficial e a
   exportação registra a escolha.

---

### User Story 3 — Saber que um material antigo deixou de valer (Priority: P1)

Alguém exportou o kit numa segunda-feira. Na quarta, uma Retificação prorrogou o prazo. Quando
qualquer pessoa volta ao kit, a tela diz, antes de tudo, que o material exportado na segunda está
desatualizado e o que mudou, "término das inscrições: 21/11/2026 → 26/11/2026". Os textos e a peça
já vêm com o novo. Se o Edital for cancelado, a tela diz que o material exportado não deve mais
circular.

**Why this priority**: o risco central do kit é afirmar, numa imagem que circula por semanas, o que
deixou de valer.

**Independent Test**:

- exportar o kit do 91/2026, publicar a Retificação de prorrogação e reabrir: a faixa nomeia o campo,
  com o valor anterior e o novo;
- repetir com o 92/2026 e uma Retificação que só muda uma seção textual: nenhuma faixa;
- exportar e depois cancelar o Edital: a faixa de "não deve mais circular".

**Acceptance Scenarios**:

1. **Given** uma exportação registrada e uma Retificação posterior que muda o término, **When** a
   pessoa reabre o kit, **Then** a faixa diz "Material exportado em DD/MM desatualizado" e lista
   "término das inscrições (antes → agora)".
2. **Given** uma Retificação posterior que não muda nenhum campo do material, **When** a pessoa reabre
   o kit, **Then** nenhuma faixa aparece.
3. **Given** uma Retificação publicada com vigência futura, **When** a pessoa abre o kit antes dessa
   vigência, **Then** a tela e as notas dizem quando a Retificação passa a valer, e o material
   descreve a versão vigente agora. **When** a vigência chega, **Then** a reabertura acusa a
   desatualização como no cenário 1.
4. **Given** duas exportações, a primeira antes e a segunda depois de uma Retificação, **When** a
   pessoa reabre o kit, **Then** a faixa ainda lista a primeira como desatualizada.
5. **Given** uma exportação registrada e o Edital cancelado depois, **When** a pessoa abre o kit,
   **Then** a tela diz o desfecho e que o material exportado em DD/MM não deve mais circular.

---

### User Story 4 — Levar o kit inteiro de uma vez, com a origem dos dados (Priority: P2)

A pessoa baixa o pacote ZIP. Ele traz:

- os textos em Markdown e em texto simples;
- a peça em PNG e em SVG, com o texto alternativo;
- a ficha;
- um manifesto que separa três instantes: quando foi gerado, desde quando vale a versão descrita e
  os próximos marcos já conhecidos.

**Why this priority**: conveniência e rastreabilidade fora do sistema. Os textos e a peça já se
obtêm um a um pelas histórias 1 e 2.

**Independent Test**: baixar o ZIP duas vezes sobre a mesma versão. A peça e os textos publicáveis
são idênticos entre os dois, o manifesto não promete validade e a trilha registra as duas
exportações.

**Acceptance Scenarios**:

1. **Given** um Edital com Retificação publicada a vigorar, **When** a pessoa baixa o ZIP, **Then** o
   manifesto lista a vigência dessa Retificação e o término do período como próximos marcos
   conhecidos, e diz que uma Retificação posterior pode mudar os dados.

---

### User Story 5 — Só quem tem a capacidade gera, e ela não dá mais nada (Priority: P1)

A unidade atribui a alguém da comunicação o papel "Comunicação" (nome provisório, P-1), pela gestão
de acessos da `107`. Essa pessoa vê "Kit de divulgação" nos Editais publicados da unidade e não ganha
nenhuma capacidade de elaborar, homologar, publicar ou retificar.

**Why this priority**: negar por padrão (Princípio III). Quem divulga não é quem pratica o ato.

**Independent Test**:

- uma pessoa sem a capacidade não vê a ação, e a rota a recusa com a frase canônica;
- uma pessoa de outra unidade recebe "não encontrado";
- a pessoa com só esta capacidade não consegue nenhum ato.

**Acceptance Scenarios**:

1. **Given** uma pessoa da unidade sem a capacidade, **When** abre o endereço do kit, **Then** recebe
   a recusa explicada, sem dado do Edital.
2. **Given** uma pessoa com a capacidade em outra unidade, **When** abre o endereço do kit, **Then**
   recebe "não encontrado".

---

### Edge Cases

Cada caso aqui é requisito, e tem linha própria na [matriz](rastreabilidade.md).

- **EC-1 — Edital não publicado.** A ação aparece indisponível com o motivo "disponível depois da
  publicação", decidida só pelo estado. A rota responde 409 com o mesmo motivo, como o
  `INDISPONIVEL` da `099`.
- **EC-2 — Edital cancelado ou encerrado, mesmo dentro do período.** A tela abre e diz o desfecho e a
  data. Nenhum texto nem peça é oferecido (FR-761 da `047`). Se houve exportação, vale a FR-3445.
- **EC-3 — Período de inscrições encerrado ou cancelado.** A tela abre e diz "Inscrições encerradas em
  DD/MM/AAAA" ou "Período cancelado". Material de resultado é escopo futuro. Se houve exportação,
  vale a FR-3445.
- **EC-4 — Processo encerrado com Edital publicado e período aberto.** É caso que só sobrevive de
  antes da decisão de 28/09 (RC-118 da `047`). A página informa; divulgar é outra coisa. Comportamento
  pela P-8. Enquanto não respondida, **sem material**, com o encerramento do Processo dito.
- **EC-5 — Sem período designado.** É o modo neutro: "Edital publicado", nenhuma palavra sobre
  inscrição nas frases do kit (FR-149 da `024`).
- **EC-6 — Período sem término declarado.** "Inscrições a partir de DD/MM/AAAA, às HHhMM". O sistema
  não inventa fechamento.
- **EC-7 — Período que atravessa o ano.** "15/12/2026 a 10/01/2027": o ano aparece nas duas pontas.
- **EC-8 — Retificação com vigência futura já publicada.** É anunciada na tela, nas notas e no
  manifesto. A ficha descreve a versão vigente no instante e **nunca** aplica a futura antes da hora.
- **EC-9 — Retificação que não toca nenhum campo do material.** Nenhuma faixa de desatualização.
- **EC-10 — Retificação que retira, acrescenta ou renomeia Perfil.** A faixa diz "retirada",
  "acrescentada" ou o nome anterior e o novo, casando as opções pela identidade do Perfil. Reordenar
  sem mudar nada não gera faixa.
- **EC-11 — Perfil só com cadastro reserva entre Perfis com vaga.** A quantidade dele é "cadastro
  reserva", e o total de vagas **não** é escrito.
- **EC-12 — Opções que o dado não distingue.** Mesmo nome e localidade ausente ou igual: a peça e a
  legenda contam as opções e mandam à página, em vez de repetir linhas iguais.
- **EC-13 — Título do Edital que repete o número.** O prefixo "Edital nº N/AAAA –" sai só da peça. O
  resto do título não é tocado.
- **EC-14 — Nenhum título oficial cabe na peça.** São oferecidas as manchetes da lista fechada
  (FR-3427). Sem escolha, ou sem manchete que caiba, a peça sai sem título e a tela diz a omissão.
- **EC-15 — Caractere sem grafia na fonte da peça.** A peça é recusada nomeando o caractere; os textos
  continuam disponíveis.
- **EC-16 — Endereço de implantação longo.** O rodapé desce de corpo até o mínimo legível. Se ainda
  não couber, ou se couber só partindo uma palavra, a peça é recusada com o motivo.
- **EC-17 — Conteúdo publicado em esquema antigo, ou Publicação anterior à `060`, sem sigla
  gravada.** A ficha tolera, como a página da seleção, e a unidade sai pela recaída de `do_ato`.
- **EC-18 — Unidade renomeada depois da publicação.** A assinatura é a congelada no ato da versão
  vigente.
- **EC-19 — Vagas acrescidas pela comissão (`097`).** Não entram: não são norma publicada.
- **EC-20 — Nenhuma exportação anterior.** Não há faixa de desatualização.
- **EC-21 — Peça desligada no ambiente** (marca não aprovada, D-010). A seção da peça diz que ela está
  em validação pela comunicação. Os textos e o ZIP sem peça continuam.
- **EC-22 — Script desligado.** As exportações funcionam por formulário; a cópia não, e os textos
  continuam selecionáveis.
- **EC-23 — Edital de 60 ou mais Perfis.** A tela de conferência lista todos; a peça e a legenda
  contam, com "e mais N" na legenda.
- **EC-24 — Mesmo número de Edital em outra unidade.** A busca indicada leva a sigla da unidade
  (FR-3418), e as duas seleções aparecem distinguíveis na vitrine.
- **EC-25 — Prorrogação que só muda a hora.** "Prazo prorrogado: o término passou de 21/11/2026,
  12h00, para 21/11/2026, 23h59". Com a data igual, a hora vai nas duas pontas.
- **EC-26 — Valor oficial com termo da lista proibida.** "Marco", "faixa etária", "São Marcos" no
  título, no nome ou na localidade entram literais. A tela os aponta na conferência, e o material não
  os altera (FR-3414).
- **EC-27 — O Edital mudou entre abrir a tela e exportar.** A exportação é recusada com "o Edital
  mudou desde que você abriu o kit", e a tela reaberta mostra o novo (FR-3446).
- **EC-28 — Gestão aberta por host local ou interno.** Nenhum link absoluto e nenhuma peça. A tela diz
  que o endereço público não é conhecido nesse acesso (FR-3447).

---

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso e porta

- **FR-3401**: O detalhe do Edital MUST oferecer a ação "Kit de divulgação" a quem tem a capacidade
  de gerar material na unidade do Edital. A ação é decidida **só pelo estado do Edital**: disponível
  quando publicado, encerrado ou cancelado; indisponível com o motivo antes da publicação (EC-1), no
  padrão do "Relatório do Edital" da `099`.
- **FR-3402**: A rota do kit MUST responder, nesta ordem:
  - "não encontrado" para Edital inexistente ou de outra unidade, sem distinguir os dois;
  - a recusa explicada da base de permissão para quem é da unidade sem a capacidade;
  - 409 com o motivo para Edital não publicado.
- **FR-3403**: A capacidade de gerar material MUST ser própria, e MUST NOT ser concedida a nenhum papel
  existente por padrão. Um papel restrito, "Comunicação" (nome provisório, P-1), a carrega sozinho. A
  capacidade MUST NOT conceder ato nenhum nem leitura além da tela do kit e das suas exportações.
- **FR-3404**: A tela e toda exportação MUST ler só:
  - a versão vigente no instante da leitura;
  - a unidade do ato dessa versão;
  - o desfecho;
  - o instante de Retificação publicada a vigorar;
  - as exportações anteriores registradas.

  Elas MUST NOT ler tabela de elaboração, Retificação não publicada nem o conteúdo de versão de
  vigência futura.
- **FR-3405**: O kit MUST NOT alterar, condicionar nem acompanhar o fluxo de publicação ou de
  Retificação. Nenhum ato o dispara, nenhum ato depende dele, nenhum comando de publicação muda e
  nenhuma tela de ato oficial muda. As leituras movidas para `publicacoes/application` (D-002) não
  mudam de comportamento.

#### Ficha

- **FR-3406**: Para um Edital e um instante, a ficha MUST reunir, cada item pela regra existente da
  tabela "O que existe":
  - a identificação (número e ano);
  - o título do Edital, e o mesmo título sem o prefixo que repete o número (EC-13);
  - o título do Processo;
  - a unidade, pela regra `do_ato` sobre a publicação da versão vigente;
  - o período (início, término, cancelado);
  - a situação pública, com o desfecho prevalecendo;
  - as ofertas por Perfil, na ordem publicada:
    - identidade, nome e localidade;
    - vagas imediatas saneadas;
    - cadastro reserva por `TIPOS_COM_RESERVA`;
    - a quantidade dita como na página;
  - o total (FR-3425);
  - a prorrogação, por `prorrogacao(original, vigente)`;
  - o instante da Retificação a vigorar;
  - o endereço da página da seleção e a âncora de cada Perfil;
  - a versão: ato, com a numeração única das Retificações; vigente desde; resumo do conteúdo;
  - a impressão (FR-3411).
- **FR-3407**: No mesmo instante, a ficha MUST coincidir em situação, período e oferta por Perfil com
  o cartão da vitrine **e** com o contexto da página da seleção. Um teste MUST comparar os três.
- **FR-3408**: A conferência MUST indicar, para o início e o término do período e para as vagas de
  cada Perfil, o ato ou os atos que deram o valor ("publicação original" ou "Retificação nº N"). A
  regra é a da `070` (`origens` sobre o `contexto()`, que já aplica `acrescimos`), e cobre Perfil
  ou Evento substituído inteiro e Perfil acrescentado. A leitura de `ProvenienciaConteudo` pelo caminho exato MUST NOT ser usada.
- **FR-3409**: A ficha MUST NOT inferir curso, campus, polo, modalidade ou tipo de seleção. Nome e
  localidade são literais. "Em N localidades" só se escreve quando toda opção declara localidade.
- **FR-3410**: O modo do material MUST ser derivado assim:
  - **com período**: período futuro ou aberto, e sem desfecho do Edital;
  - **neutro**: sem período designado, e sem desfecho do Edital;
  - **sem material**: desfecho do Edital, período encerrado ou período cancelado, ou o caso da P-8.
- **FR-3411**: A impressão MUST ser o resumo criptográfico, em serialização canônica, **só dos campos
  que o material afirma**:
  - número, ano e títulos;
  - unidade;
  - período, cancelamento e designação;
  - ofertas, cada uma com a identidade do Perfil, ordenadas pela identidade;
  - o **caminho** da página.

  Ela MUST NOT incluir instante, situação, identificador de versão, host nem a ordem das ofertas.
  Dados iguais MUST dar impressão igual.

#### Kit textual

- **FR-3412**: O kit MUST oferecer, nesta ordem:
  - informações oficiais para conferência, com a proveniência;
  - resumo institucional;
  - legenda para rede social;
  - chamada curta para o site;
  - texto para mensagens;
  - link oficial e link de cada opção;
  - referência à versão, a ressalva da FR-3419;
  - notas para quem divulga (FR-3421).
- **FR-3413**: Cada texto MUST ser composto de forma determinística, por formas fechadas preenchidas
  só com valores da ficha. Não há campo livre nos textos nem modelo de linguagem.
- **FR-3414**: As frases fixas e a composição dos textos e da peça MUST NOT conter:
  - tempo relativo ("faltam", "falta", "hoje", "amanhã", "último dia", "últimos dias");
  - estado do momento ("inscrições abertas", "estão abertas");
  - promessa ("garanta", "garantida", "última oportunidade", "não perca");
  - juízo ("aprovado", "classificado", "resultado final", "resultado disponível");
  - vocabulário interno ("marco", "recorte", "faixa", "apuração", "homologa").

  A lista `PROIBIDAS` das telas públicas também se aplica, e a regra vale também para as manchetes
  da FR-3427. **Valores literais da ficha** (título, nome do Perfil, localidade) não são alterados
  quando contêm um desses termos. A conferência os aponta (EC-26).
- **FR-3415**: Todo prazo MUST ser dito em data e hora absolutas, no fuso institucional, com
  "horário de Brasília". Data e hora vêm uma vez só da ficha, já escritas, para texto e peça.
- **FR-3416**: No modo neutro, as frases do kit, nos textos e na peça, MUST NOT conter palavra sobre
  inscrição.
- **FR-3417**: A prorrogação MUST ser dita só quando comprovada pela comparação do término original
  com o vigente, nomeando as duas pontas. Com a mesma data, a hora vai nas duas (EC-25).
- **FR-3418**: A legenda de rede social MUST trocar o link pelo caminho curto da vitrine e pela busca
  pelo número do Edital com a sigla da unidade ("busque por 01/2026 – Cefor"). O resumo e o texto
  para mensagens MUST trazer o link completo.
- **FR-3419**: Todo texto destinado a publicação MUST trazer a ressalva: "As informações repetem o
  Edital nº N/AAAA, conforme a versão vigente desde DD/MM/AAAA, HHhMM. Em caso de divergência, vale
  o Edital."
- **FR-3420**: Cada texto MUST ter "Copiar". O kit textual inteiro MUST ser exportável em Markdown e
  em texto simples.
- **FR-3421**: As notas para quem divulga MUST dizer:
  - a versão usada e o ato;
  - o instante da conferência e a situação nele;
  - a Retificação a vigorar, quando houver;
  - o término do período publicado;
  - que uma Retificação posterior pode mudar os dados.

  Elas MUST NOT prometer validade futura. As notas são para quem divulga, e não para publicação.

#### Peça visual

- **FR-3422**: O kit MUST compor **um** template, feed 1080 × 1350, entregue em PNG e em SVG da mesma
  composição. O SVG MUST embutir o subconjunto da fonte usada, para desenhar igual fora do GPS.
- **FR-3423**: Todo texto da peça MUST ser valor da ficha, frase fixa do template ou manchete da lista
  fechada da FR-3427. Toda data e quantidade da peça MUST estar também no kit textual. As duas
  conferências MUST ser automáticas.
- **FR-3424**: O período MUST ocupar o destaque principal, em datas absolutas.
  - O selo "prazo prorrogado" aparece quando a prorrogação é comprovada.
  - No modo neutro, o destaque é "Edital publicado".
- **FR-3425**: A oferta MUST obedecer a um teto único de **quatro** opções, na peça e na legenda.
  - Até quatro opções com rótulos distintos são listadas, cada uma com a quantidade.
  - Acima disso, ou com rótulos indistintos, o material diz a contagem e convida à página.
  - O total só aparece quando toda opção tem vaga imediata, e **sempre na forma "N vagas em K
    opções"**, nunca sozinho. É a exceção declarada à FR-1607 da `072`: a soma não pode ser lida
    como de cada opção, porque a mesma frase diz quantas opções a repartem.
- **FR-3426**: O título MUST ser escolhido nesta ordem, cada um só se couber no mínimo legível:
  1. o do Edital sem o prefixo do número;
  2. o do Processo;
  3. a manchete escolhida (FR-3427).

  Se nenhum couber, a peça sai sem título e a tela diz a omissão. O título MUST NOT ser truncado.
- **FR-3427**: A manchete MUST obedecer a estas regras:
  - é oferecida só quando nenhum título oficial cabe;
  - é **escolhida numa lista fechada derivada da ficha**: o nome comum, quando todas as opções têm o
    mesmo nome; o nome de cada opção, quando há até quatro; e a combinação "nome — localidade" da
    opção única;
  - fica só com as que cabem e passam a FR-3414;
  - não há texto livre;
  - é usada **só na peça**, e os textos mantêm o título oficial;
  - é registrada na exportação (FR-3436).
- **FR-3428**: Nenhum texto da peça MUST ter menos de 24 px a 1080 px de largura. O contraste MUST
  atender AA. O conteúdo MUST respeitar a margem de segurança de 80 px.
- **FR-3429**: Nenhum texto da peça MUST sair da área útil nem se sobrepor a outro texto ou à borda
  do bloco que o contém. Composição que não cabe MUST ser recusada com o motivo, e nunca encolhida
  abaixo do mínimo nem truncada. Uma quebra que parta palavra conta como "não cabe". Um teste
  geométrico MUST verificá-lo em todos os cenários de referência e nos casos sintéticos no limite.
- **FR-3430**: Caractere sem grafia na fonte da peça MUST recusar a peça nomeando o caractere. Os
  textos continuam disponíveis. O texto desenhado MUST ser o mesmo que foi medido, já normalizado
  pela grafia.
- **FR-3431**: O rodapé MUST trazer:
  - a chamada à página, com o caminho curto e a busca pelo número com a sigla, medida;
  - o selo da versão, com a data da versão vigente e a referência curta da impressão.

  Os dois respeitam o mínimo da FR-3428.
- **FR-3432**: A marca MUST ser o ativo oficial do Ifes, e da unidade quando o manual o pedir,
  versionado com a sua origem. Sem template aprovado pela comunicação, a peça MUST ficar desligada
  no ambiente (D-010), e o kit textual MUST continuar inteiro.
- **FR-3433**: O texto alternativo MUST ser escrito em frases, com o que a peça mostra e na ordem em
  que mostra. Ele vai embutido no SVG e entregue junto da imagem.
- **FR-3434**: Com pouco conteúdo, o espaço livre entre o fim do corpo e o rodapé MUST ser
  redistribuído: o corpo desce 35% da folga, e o espaço que resta embaixo não passa de 65% dela.
  Nada muda de tamanho nem de ordem.

#### Exportação e rastreabilidade

- **FR-3435**: As exportações MUST ser PNG, SVG, Markdown, texto simples e ZIP. O ZIP leva os textos,
  a peça, o texto alternativo, a ficha e o manifesto. Cada exportação MUST ser um envio que registra.
  Abrir a tela, ver a prévia e copiar MUST NOT registrar (P-5).
- **FR-3436**: Cada exportação MUST gravar um evento na trilha de auditoria do Edital, com o estado e
  a revisão anteriores iguais aos atuais (não é transição) e com:
  - quem e quando;
  - o formato;
  - a versão (identificador, resumo do conteúdo, vigente desde);
  - a versão do template;
  - a impressão, a versão da impressão e os campos que o material afirma, com a identidade de cada
    Perfil;
  - a manchete escolhida, quando houver;
  - o resumo dos bytes entregues.

  O evento MUST ter rótulo legível na trilha e MUST NOT contar como ato no relatório da trilha.
- **FR-3437**: O manifesto MUST separar três instantes, e MUST NOT chamar nenhum deles de validade:
  - o da geração;
  - desde quando vale a versão descrita, com o ato;
  - os próximos marcos já conhecidos (Retificação a vigorar, término do período).

  Ele traz a impressão, o template, o rasterizador e o resumo das fontes.
- **FR-3438**: Determinismo, em dois níveis:
  - a mesma ficha com a mesma versão de template MUST produzir a mesma peça (SVG e, no ambiente de
    implantação, PNG) e os mesmos textos publicáveis, byte a byte, em qualquer instante;
  - o ZIP MUST ser idêntico para a mesma ficha, o mesmo template e o mesmo instante de referência.

  O manifesto e as notas carregam instantes por desenho.
- **FR-3439**: Ao abrir o kit, a tela MUST comparar a ficha de agora com as exportações registradas
  daquele Edital.
  - Para cada impressão exportada diferente da atual, a faixa diz a data da exportação mais recente
    com aquela impressão e os campos que mudaram, com o valor anterior e o atual.
  - São no máximo as cinco mais recentes, com "e mais N".
  - Se toda exportação tem a impressão atual, nenhuma faixa aparece.
  - A faixa não diz quem exportou.
- **FR-3440**: Enquanto houver Retificação publicada a vigorar, a tela, as notas e o manifesto MUST
  dizer quando ela passa a valer. Depois da vigência, a FR-3439 alcança a mudança.
- **FR-3441**: Nenhum arquivo gerado MUST ser guardado, e MUST NOT haver aprovação peça a peça.
- **FR-3442**: Toda resposta do kit MUST ser privada, sem guarda em cache. PNG e SVG MUST sair com o
  tipo certo, como anexo na exportação e com proibição de farejar o tipo. O SVG MUST levar uma
  política de conteúdo restritiva própria, que admita só a fonte embutida.
- **FR-3445**: Quando o modo atual é "sem material" e houve exportação, a tela MUST dizer o motivo
  (desfecho, período encerrado ou cancelado) e que o material exportado em DD/MM não deve mais
  circular.
- **FR-3446**: A tela MUST levar a impressão que a pessoa conferiu para a prévia e para o formulário
  de exportação. Se a ficha mudou nesse meio-tempo, a exportação MUST ser recusada com "o Edital
  mudou desde que você abriu o kit" (EC-27), e a prévia MUST mostrar a mesma recusa.
- **FR-3447**: Quando a requisição chega por host local ou interno (a regra `_host_local` da `099`),
  o kit MUST NOT pôr link absoluto nos textos nem gerar peça, e a tela MUST dizer por quê (EC-28).
- **FR-3448**: A impressão MUST ter versão. Quando a exportação registrada tem versão diferente da
  atual, a comparação MUST ser feita recalculando a impressão a partir dos `campos` gravados. Se isso
  não for possível, a faixa diz "material de versão anterior do kit: confira", sem afirmar mudança.

#### Interface

- **FR-3443**: O kit MUST ser uma tela única com:
  - identificação, situação e versão;
  - as faixas pertinentes (desatualização, desfecho, Retificação a vigorar, modo neutro, título
    omitido, peça recusada ou desligada, host local, termo da lista em valor oficial);
  - a conferência;
  - os textos com "Copiar";
  - a prévia da peça com o texto alternativo;
  - as exportações.
- **FR-3444**: A tela MUST seguir os padrões da gestão:
  - estilo e script só por arquivo (CSP);
  - contraste AA, controles nativos e nome acessível;
  - leitura a 375 px;
  - trilha e moldura;
  - inventário das negativas da `033`.

  "Copiar" MUST funcionar pelo teclado e anunciar o resultado.

### Key Entities

- **Ficha de divulgação**: leitura, sem estado. É o que a comunicação pode afirmar sobre um Edital
  num instante, com a origem de cada valor e a impressão versionada.
- **Material**: os textos e a peça, derivados da ficha e de uma versão de template.
- **Exportação**: o evento na trilha de auditoria (FR-3436). Não guarda arquivo.
- **Template**: a composição da peça, versionada no código e aprovada pela comunicação (D-010).

---

## Cenários de referência

São os 11 da POC e cinco a mais. Viram casos automatizados (SC-1053) e a galeria da revisão humana
(SC-1054):

1. 91/2026 com inscrições futuras;
2. o mesmo 91/2026 em andamento;
3. 91/2026 prorrogado por Retificação;
4. 01/2026 com Retificação a vigorar;
5. 01/2026 depois da vigência;
6. 92/2026 com muitos Perfis;
7. 92/2026 com Retificação que não muda o material;
8. um Perfil;
9. localidade ausente;
10. sem período designado;
11. cancelado depois de exportado;
12. período encerrado;
13. caractere sem grafia;
14. prorrogação só de hora;
15. Perfil substituído inteiro por Retificação (proveniência);
16. mesmo número em duas unidades.

---

## Pendências de produto

Nenhuma bloqueia o **início** da implementação. A P-3 e a P-4 bloqueiam a **liberação da peça** em
produção. A P-1, a P-2 e a P-7 bloqueiam a **atribuição do papel a qualquer pessoa**. A P-2 é
resolvida por spec própria, e não aqui (decisão do usuário de 01/11).

| # | Pergunta | Comportamento enquanto não respondida |
|---|---|---|
| **P-1** | O papel restrito chama-se "Comunicação"? A capacidade também vai para algum papel existente (o `gestor`, o `publicador`)? | Papel próprio, e nenhum papel existente a recebe (FR-3403) |
| **P-2** | **Achado desta spec, ampliado pela revisão.** Qualquer pessoa da unidade, sem capacidade nenhuma, enxerga hoje pela gestão: <ul><li>"Processos Seletivos" e "Agenda" (`navegacao.py`);</li><li>a lista e o detalhe de todo Edital (`views.py`, `lista` e `detalhe`);</li><li>no detalhe, as Retificações **em curso** (`atos_retificacao.em_curso_por_edital`), as pendências e os participantes;</li><li>a prévia do rascunho (`_edital_com_previa`). Os anexos do rascunho, ao contrário, exigem `LEITURA_DO_RASCUNHO`.</li></ul>Uma pessoa só da comunicação saberia de prorrogação, cancelamento ou Retificação antes de publicados. **Encaminhada pelo usuário em 01/11 a spec própria**, separada desta: quem pode ler conteúdo não publicado, com a verificação no backend. Uma entrada própria para a Comunicação melhora a jornada, mas **sozinha não fecha** o acesso direto às outras URLs. | Nenhuma atribuição do papel até a spec da P-2 estar mergeada. O desenvolvimento do incremento A segue. A tela do kit lê só o publicado (FR-3404) |
| **P-3** | Quem fornece os ativos oficiais e o manual? É a marca do Ifes, a da unidade ou as duas? O manual exige fonte própria? | Peça desligada em produção (D-010); marcador declarado em desenvolvimento |
| **P-4** | O `resvg-py` é aprovado depois da verificação da D-007 (licença, Linux, fontes, segurança, reprodutibilidade, lote)? | A peça não entra em produção; se reprovado, a D-007 diz a alternativa |
| **P-5** | "Copiar" também registra, para que a desatualização alcance quem só copiou? | Não registra: só as exportações registram |
| **P-6** | Quem liga a peça em produção depois da aprovação do template? | A operação, pela chave de ambiente, como a dos avisos (`066`) |
| **P-7** | A pessoa da comunicação precisa ver o kit de Editais de **mais de uma** unidade? | Um vínculo por unidade, pela `107`, como os demais papéis |
| **P-8** | Processo encerrado com Edital publicado e período aberto (EC-4): há material ou não? | Sem material, com o encerramento do Processo dito |
| **P-9** | A implantação deve declarar o endereço público, em vez de deduzi-lo da requisição (FR-3447)? | Deduzido da requisição; host local não produz link nem peça |

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1051**: Uma pessoa da comunicação, sem conhecer o sistema, obtém de um Edital real publicado a
  legenda, o texto para mensagens e a peça em menos de três minutos, sem abrir o PDF do Edital.
  Validação humana.
- **SC-1052**: Em 100% dos cenários de referência:
  - as frases do kit não afirmam nada que a ficha não comprove;
  - a peça só contém valores da ficha, frases fixas e manchetes da lista;
  - no modo neutro, as frases do kit não falam de inscrição.

  Verificação automática.
- **SC-1053**: Em 100% dos cenários de referência:
  - toda Retificação que muda campo do material produz a faixa com o valor anterior e o atual;
  - nenhuma Retificação que não muda o material produz faixa;
  - o desfecho depois de uma exportação produz a faixa de "não deve mais circular";
  - nenhuma versão de vigência futura é aplicada antes da hora.
- **SC-1054**: A comunicação institucional aprova o template **com a marca oficial aplicada**, sobre
  a galeria dos cenários de referência, antes da liberação em produção. Validação humana.
- **SC-1055**: Em 100% dos cenários de referência e dos casos sintéticos no limite:
  - nenhum texto da peça sai da área útil, se sobrepõe a outro, fica abaixo do mínimo legível ou tem
    palavra partida;
  - a composição que não cabe é recusada com o motivo.
- **SC-1056**: Para a mesma ficha e o mesmo template, a peça e os textos publicáveis saem idênticos em
  qualquer instante. O PNG sai idêntico no ambiente de implantação.
- **SC-1057**: No ambiente de implantação, a tela do kit com a prévia e o ZIP completo respondem cada
  um em menos de 2 segundos, num lote de 20 gerações seguidas.
- **SC-1058**: A comunicação confere um Edital real montado pela interface e não corrige nenhum dado do
  kit. Validação humana.

---

## Assumptions

- Os Editais divulgados recebem inscrição pelo GPS ou não designam período. Inscrição externa não
  existe como conceito (estudo, §1), e o modo neutro a cobre sem afirmar nada.
- A gestão e o portal respondem pelo mesmo endereço base. Os avisos (`066`) já montam o link da
  página pública a partir da requisição da gestão; o host local é tratado na FR-3447, e a P-9
  pergunta se a implantação deve declarar o endereço.
- A fonte da peça é a Edital Sans, a mesma do Edital (OFL), salvo se o manual exigir outra (P-3).
- O volume é de dezenas de exportações por Edital, e a geração síncrona basta (POC: ~45 ms por peça).
- Nenhum dado pessoal entra no kit. LGPD: o kit lê só conteúdo publicado do ato e grava, na trilha,
  quem exportou. É o mesmo tratamento das emissões do relatório (`099`).
