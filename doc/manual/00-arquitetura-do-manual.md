# Arquitetura do Manual do Sistema de Processo Seletivo

**Sessão de descoberta — 08/09/2026.** Este documento **não é o manual**. Ele estabelece o que o
manual precisa ensinar, em que ordem, para quem, com quais imagens e com qual linguagem.

> **Revisão 2 — 08/09/2026.** Arquitetura aprovada, com quatro ajustes de direção incorporados:
> (1) **um piloto editorial (S-00) precede a coleta de capturas** — validar o formato antes de
> industrializar a produção (§I.0); (2) a espécie de decisão recursal sem caminho de cumprimento
> **sai do fluxo principal** e vira limitação declarada, não alerta (§C.bis · C-19); (3) o manual
> **separa operação de referência** — as limitações se concentram em `G-03` e só há alerta inline
> quando a lacuna muda o que o leitor deve fazer agora (§H.0); (4) o vocabulário passa a dizer
> **imutável**, nunca "definitivo", ao falar do que uma publicação trava — para não colidir com
> *definitiva* como natureza do resultado.
>
> **Revisão 3 — 08/09/2026.** A equipe inicial é de **duas a três pessoas**. Levantei no domínio as
> regras que olham para a identidade da pessoa, e não só para a permissão, e o resultado virou a
> nova **§A.3**: o ciclo inteiro fecha com duas pessoas, mas quem julga recursos precisa ficar fora
> de toda a cadeia de avaliação e divulgação — o que inverte a ordem natural de distribuir papéis.
> C-04 ganhou bloco obrigatório sobre acúmulo, §D ganhou nota de leitura por coluna, e o inventário
> foi a 88 capturas. Ficaram registrados também o **gate de S-00** e as nove perguntas que a sessão
> precisa responder (§I.0).

> **Revisão 4 — 08/09/2026, após S-00.** O piloto editorial foi executado e o padrão está fixado.
> Cinco emendas entraram neste documento, todas marcadas **(S-00)** no ponto em que valem: o acento
> único e o seu uso na anotação (§G.1, §G.6); o componente `Limitação conhecida desta versão`, que
> **não** é um oitavo callout (§G.3); a forma reduzida do quadro "onde estou" (§G.5); a régua de
> densidade (§G.8, nova); e a correção do viewport de captura (§F.2). Duas fichas do §C.bis mudam
> por achado de produto: **C-06** deixa de prometer "um Processo com vários Editais", porque a tela
> para acrescentar o segundo não existe. O inventário do §F foi revisado e passou a 89 capturas —
> a revisão vive em `doc/manual/01-inventario-de-capturas-revisado.md`, e é ela que autoriza S-01.
> As respostas de design estão em `doc/manual/piloto/relatorio-s00.md`.

> **Revisão 5 — 06/10/2026, sobre a `main` @ `4602b04`.** Nenhuma sessão de produção rodou depois do
> piloto, e o produto andou ~790 commits e quarenta features (`019` a `058`) sem que este documento
> acompanhasse. A revisão foi feita por auditoria contra o código e as specs, não contra relatórios,
> e as mudanças estão marcadas **(R5)** no ponto em que valem. As de direção, que uma sessão futura
> precisa conhecer antes de escrever qualquer capítulo:
>
> 1. **O ciclo não termina na divulgação.** Depois da ordem vêm o corte, a apuração de ocupação, a
>    convocação com suplência, o Requerimento de Matrícula e a exportação para o Registro Acadêmico.
>    O mapa passou de 16 para **19 fases** (§B.2), e o quadro "onde estou" do piloto precisa ser
>    regerado.
> 2. **São sete papéis**, e não seis: entrou o **Exportador de matrículas** (§A.1).
> 3. **O Gestor alcança todos os atos da presidência** — distribuir, consolidar, emitir, cortar,
>    sortear, apurar e convocar aceitam as duas bases. Isso muda a orientação para equipe pequena:
>    o Gestor que pratica esses atos perde a elegibilidade para julgar (§A.3).
> 4. **A reavaliação determinada por recurso tem caminho** (§H.2). A caixa "⛔ não utilize" sai de
>    C-19, e a espécie volta à tabela com procedimento.
> 5. **Segunda e terceira correções factuais de peso:** o Processo nasce junto com o primeiro
>    Edital e publicar ativa o Processo — o alerta "ative antes de publicar" era falso; e acrescentar
>    Editais a um Processo **tem tela** desde 16/09 (§H.17).
> 6. **Capítulos novos**, com sufixo de letra para não renumerar referências (§C): C-11a, C-17a,
>    C-17b, C-20a a C-20d, C-21a e C-22.
> 7. **As capturas e as quatro páginas do piloto estão vencidas** — a série de polish (`055` a
>    `058`) mudou a folha e os componentes, e várias telas fotografadas mudaram de conteúdo. O
>    inventário ganhou uma revisão própria (`01-…`, §R5). As páginas do piloto **não** foram
>    reescritas: continuam valendo como padrão editorial, que era a função delas, e são revistas
>    nas sessões que as citam.

**Base da descoberta:** `main` @ `a6f25a4`. Fontes lidas: `README.md`, a Constituição, as 18 pastas
de `specs/`, os quatro relatórios de auditoria E2E (`doc/e2e/015`, `017`, `018`, `020-polish`), os
documentos de decisão em `doc/`, e — como fonte de verdade final — o código: `interface/urls.py`,
`portal/urls.py`, `interface/atos.py`, `interface/acoes.py`, `interface/identidade.py`, os 97
templates das duas interfaces e os enums de domínio.

> **Uma advertência sobre as specs.** A numeração não é sequência pedagógica e nem sequência
> histórica confiável: a 012 e a 013 foram revisadas em conjunto por um terceiro documento, e há
> pasta que registra decisão sem construir nada — a `039` (catálogo de modalidades) entrou na `main`
> como registro, e a Modalidade continua dentro do Perfil. **A `014`, a `016` e a `019`, que esta
> advertência já listou como ausentes, existem e foram construídas. (R5)**
>
> **Sobre o `README.md`, esta advertência envelheceu — corrigida em 10/09/2026.** A defasagem que
> ela registrava era textual: "descreve o produto até a spec 004" e "a interface administrativa e
> pública é uma especificação futura". **Nenhuma das duas frases existe mais**; o arquivo foi
> reescrito, abre dizendo que o sistema tem as duas interfaces e mantém a tabela de incrementos
> atualizada até a `022`.
>
> A conclusão prática, porém, sobrevive **por outro motivo**, e é este que a sessão precisa saber:
> a tabela de módulos do README nomeia **7 dos 17** apps de `backend/processo_seletivo/` — ficam de
> fora `avaliacoes`, `classificacao`, `comissoes`, `divulgacao`, `identidade`, `inscricoes`,
> `interface`, `portal`, `recursos` e `resultados`, isto é, quase tudo o que o manual descreve.
> Continua sendo retrato parcial, e nenhuma sessão de produção do manual deve tomá-lo como retrato
> do sistema. O que mudou é a razão: era conteúdo errado, hoje é conteúdo ausente.

---

## A. Quem usará o manual

### A.1 Os atores que existem de fato

O sistema reconhece identidade de três maneiras distintas, e essa distinção é a espinha do manual.

**1. Papéis nomeados** (`interface/identidade.py::PAPEIS`) — conjuntos fixos de permissões que, na
implantação institucional, virarão grupos do diretório. São **sete (R5)**:

| Papel | O que pode fazer |
|---|---|
| **Elaborador** | Elaborar e submeter Edital; elaborar e submeter Retificação; partir de um Edital anterior num rascunho vazio |
| **Homologador** | Homologar e devolver Edital; homologar Retificação; revogar homologação |
| **Publicador** | Publicar Edital, publicar Retificação e **publicar resultado** |
| **Gestor** | Criar o Processo com o primeiro Edital e **acrescentar Editais** a ele; ativar/encerrar/cancelar Processo; encerrar/cancelar Edital; cancelar Retificação; **constituir a comissão**; consultar inscrições recebidas; **ler a Visão Geral institucional** |
| **Julgador de recursos** | Admitir e julgar recursos — e nada mais |
| **Auditor** | Consultar a trilha de auditoria e as telas de leitura — ordenação, corte, sorteio, convocação, publicações —, sem emitir nada |
| **Exportador de matrículas** **(R5)** | Exportar, de um Edital que coleta Requerimento de Matrícula, o arquivo para o Registro Acadêmico |

**(R5)** O sétimo papel é próprio pela mesma razão do julgador: pendurá-lo no Gestor daria a quem
abre um dossiê por vez um arquivo com CPF, RG, filiação e endereço da população inteira. Nenhum
outro papel o recebe.

**2. Capacidades verificadas contra o vínculo** — não são papéis; são conferidas objeto a objeto:

| Capacidade | Como se obtém |
|---|---|
| **Presidência da comissão** (`comissao:presidir`) | Ser designado PRESIDENTE na comissão daquele Processo |
| **Avaliação atribuída** (`avaliacao:atribuida`) | Receber a Atribuição de uma inscrição numa Etapa |

> **(R5) A presidência não é papel, mas o Gestor alcança tudo o que ela pratica.** Distribuir,
> registrar impedimento, reabrir, consolidar, registrar ocorrência, emitir a ordem, cortar,
> sortear, apurar a ocupação, convocar e instruir recurso aceitam duas bases, e cada uma basta
> sozinha: presidir **este** Processo, ou deter a permissão de gerir comissão, que é do Gestor. A
> segunda existe para a comissão ainda vazia e para a intervenção da administração. Era assim já
> em `a6f25a4` — a omissão é desta descoberta, não do código —, e é o que impede o manual de tratar
> "Gestor" e "Presidente" como trilhas disjuntas. A consequência para equipe pequena está na §A.3.

**3. Identidade do candidato** — outra sessão, outro domínio, outro endereço (`/selecoes/`).
Obtida por código enviado por e-mail, sem senha. **(R5)** Além de inscrever-se e recorrer, o
candidato vê a própria convocação, preenche o Requerimento de Matrícula (e consulta as versões que
ele corrigiu) e baixa o comprovante em PDF.

**4. Público anônimo** — sem identidade nenhuma. Vê a vitrine (com busca e filtros), a página da
seleção, o PDF do Edital e de cada Retificação, os anexos e os resultados divulgados — e, **(R5)**
quando o marco ordena por sorteio, a relação de habilitados, a verificação do sorteio e o
manifesto que permite conferi-lo por conta própria.

### A.2 Agrupamento pedagógico — e o que foi descartado

O manual **não** terá um capítulo por permissão. Terá **nove públicos (R5)**:

| Público do manual | Reúne | Por quê |
|---|---|---|
| **Quem organiza o certame** | Gestor | Abre e fecha o Processo, cria os Editais, monta a comissão, lê a supervisão do Processo e a Visão Geral institucional. É o dono do ciclo |
| **Quem redige o Edital** | Elaborador | Passa 90% do tempo num assistente de nove passos. Merece o capítulo mais denso |
| **Quem aprova** | Homologador | Trabalho curto, decisão pesada, vocabulário próprio (fundamento, devolução, revogação) |
| **Quem assina e publica** | Publicador | Publica Edital, Retificação e resultado — os atos que tornam algo público |
| **Quem conduz a avaliação e o que vem depois** | Presidente da comissão — ou o Gestor, pela mesma porta (§A.1) | Distribui, controla impedimento e ocorrência, consolida, emite a ordem; e, **(R5)** depois dela, corta, sorteia, apura a ocupação, convoca e instrui recurso |
| **Quem avalia** | Membro da comissão / avaliador | Só vê o que lhe foi atribuído. Manual curtíssimo e autossuficiente |
| **Quem julga recursos** | Julgador | Papel deliberadamente isolado — quem julga não pode ter atuado |
| **Quem exporta para matrícula (R5)** | Exportador de matrículas | Tarefa curta e rara, com o maior volume de dado pessoal do sistema num arquivo só |
| **Quem se inscreve e quem consulta** | Candidato + público anônimo | Mesma superfície, o segundo é o primeiro sem sessão |

Mais o **Auditor**, que não é uma jornada e sim uma leitura transversal: ganha um capítulo de
referência, não uma trilha.

**Descartes deliberados** — atores que a lista do briefing sugeria e que **não existem** como
figura separada neste sistema:

- **Revisor** — não existe. Quem revisa é o **homologador**: submeter leva o Edital a "Em revisão",
  e é o homologador que lê essa revisão e decide entre *Homologar* e *Devolver para elaboração*.
  Criar um capítulo de "revisor" inventaria um posto que ninguém ocupa.
- **Membro da comissão** ≠ **avaliador** — são a mesma pessoa em dois momentos. O manual usa
  "avaliador" ao falar do trabalho e "membro da comissão" ao falar da composição.
- **Publicador** ≠ **homologador** — parecem próximos e **não podem ser fundidos**: o sistema recusa
  publicar quando a mesma pessoa elaborou e homologou a revisão. Separá-los é conteúdo, não
  organização.
- **Presidente** ≠ **gestor** — também não podem ser fundidos, e pela razão inversa: o gestor
  *constitui* a comissão mas não pode presidi-la por isso; a presidência é vínculo. **(R5)** A
  distância, porém, é menor do que esta linha sugeria: os atos da presidência aceitam também a
  permissão do Gestor (§A.1), e o Gestor que os pratica passa a ter autoria na cadeia do resultado,
  com o efeito que a §A.3 descreve.

### A.3 · A equipe real — acúmulo de papéis numa operação de duas ou três pessoas

Os sete papéis descrevem **funções**, não pessoas. Uma pessoa pode acumular vários, e a operação
inicial prevista é de **duas a três pessoas**. Isso não invalida a arquitetura — mas obriga o
manual a ensinar *como acumular*, porque o sistema tem regras que olham para **quem foi a pessoa**,
e não só para qual permissão ela tem.

**As três regras de identidade que existem no domínio** (verificadas no código, não inferidas):

| Regra | O que o sistema exige | Mínimo de pessoas |
|---|---|---|
| **Publicar Edital ou Retificação** | Quem publica não pode ser a mesma pessoa que elaborou **e** homologou aquela revisão. Basta que uma das duas etapas anteriores tenha sido de outra pessoa | **2** |
| **Julgar recurso** | Quem julga não pode ter concluído a avaliação que fundamentou o resultado atacado, nem o consolidado, nem emitido o ato de classificação atacado, nem praticado a publicação atacada — nem ter impedimento declarado quanto àquela inscrição. **(R5)** O impedimento olha também a Etapa que a decisão vai alcançar, e **realizar um sorteio conta como emitir** o ato de ordenação que ele constitui | **2**, com divisão rígida |
| **Reavaliação determinada por recurso** | Exige avaliador diferente do que concluiu a original; a distribuição abre uma vaga a mais para isso | **2 avaliadores** — **(R5)** e a espécie tem caminho de cumprimento (§H.2) |

**E uma que não existe, e é bom o manual dizer:** emitir o ato de classificação e publicar o
resultado são permissões distintas e **não** têm checagem de identidade. A mesma pessoa pode fazer
as duas. A separação ali é de autorização, não de pessoa.

**A consequência prática inverte a ordem natural de planejamento.** A restrição que aperta uma
equipe pequena não é a publicação do Edital — essa se resolve com duas pessoas. É o **julgamento
de recurso**, porque ele exclui quem participou de *qualquer* elo da cadeia que produziu o
resultado atacado. Daí a regra que o manual precisa dar antes de qualquer outra:

> **Escolha primeiro quem vai julgar recursos, e mantenha essa pessoa fora de toda a cadeia de
> avaliação e divulgação.** Distribuir os demais papéis depois é fácil; descobrir no meio do prazo
> recursal que ninguém está livre para julgar não tem conserto dentro do sistema.

**Duas configurações que fecham o ciclo inteiro**, ambas conferidas contra as regras acima:

| | Duas pessoas | Três pessoas |
|---|---|---|
| **Pessoa 1** | Elaborador · Publicador · Presidência da comissão · Avaliador | Elaborador · Avaliador |
| **Pessoa 2** | Gestor · Homologador · **Julgador** · Auditor | Gestor · Homologador · Presidência · Publicador |
| **Pessoa 3** | — | **Julgador** · Auditor |

Na configuração de duas pessoas, note o detalhe que parece errado e não é: **quem publica o
resultado é a Pessoa 1**, que também o emitiu. Se a Pessoa 2 publicasse, ela ficaria impedida de
julgar os recursos contra a própria publicação — e a equipe perderia o único julgador possível.

**(R5) Ter o papel não obriga a usá-lo, e numa equipe pequena usar é o problema.** Na
configuração de duas pessoas, quem julga é também Gestor — e o Gestor tem base para consolidar,
emitir a ordem, realizar o sorteio e convocar (§A.1). O sistema **deixa**; se ela o fizer no
caminho do resultado atacado, fica impedida de julgar, e era a única que podia. Na de três pessoas
o risco desaparece, porque a Pessoa 3 não tem papel de Gestor. O manual precisa dizer isso em C-04 e
repetir em uma linha em cada capítulo desses atos. Três notas que completam a tabela:

- **instruir o recurso não impede** — instruir não é julgar, e a presidência pode juntar parecer
  sem perder nada. Instruir um *documento* da inscrição, porém, pede a permissão de consultar
  inscrições, que é do Gestor: na configuração de duas pessoas, só a Pessoa 2 o faz;
- **o Exportador de matrículas não entra em regra de identidade nenhuma**, e por isso não aparece
  na tabela. Onde colocá-lo é decisão sobre dado pessoal, não sobre segregação — a instituição
  precisa tomá-la explicitamente;
- **a convocação é ato da mesma porta da presidência**, e quem convoca não fica impedido por isso:
  a regra de julgamento olha o resultado atacado, não o que veio depois dele.

**O que uma equipe de duas pessoas perde**, e o manual deve dizer sem rodeio:

- **não há reavaliação por recurso** — com um avaliador só, não existe o "avaliador diverso" que
  ela exige. **(R5)** Agora que a espécie tem caminho (§H.2), esta perda deixa de ser teórica:
  uma decisão que determine reavaliação não terá quem a cumpra;
- **não há substituto para o avaliador impedido** — registrar impedimento numa inscrição deixa
  aquela inscrição sem quem a avalie;
- **a pluralidade da comissão é nominal** — presidência e único membro são a mesma pessoa.

Nada disso é defeito do produto: é o que uma banca de uma pessoa significa. Mas é decisão
institucional, e o manual precisa expô-la antes que alguém a descubra no meio de um certame.

**Efeito sobre a arquitetura do manual:** nenhum capítulo muda de lugar, e as trilhas por papel
(Parte 3) ficam **mais** úteis, não menos — numa equipe de duas pessoas cada uma lê três ou quatro
trilhas, e é justamente por isso que elas precisam ser páginas curtas de roteamento e não capítulos
com conteúdo próprio. O que muda é que **C-04 ganha um bloco obrigatório** sobre acúmulo de papéis,
com a tabela acima.

---

## B. Jornada macro do processo

### B.1 O que o sistema realmente suporta hoje

A sequência do briefing está quase certa. Quatro correções que o código impõe **(R5, revistas)**:

1. **O Processo Seletivo nasce junto com o primeiro Edital**, numa tela só; outros Editais se
   acrescentam depois, pela página do Processo. São duas entidades com ciclos de vida separados.
   Ativar o Processo é opcional: **publicar o primeiro Edital o ativa**, e a trilha registra que a
   ativação foi derivada daquela publicação.
2. **"Revisar" e "homologar" são o mesmo degrau**, praticado por uma pessoa só.
3. **"Corrigir/reavaliar" não vem depois de "julgar" como fase própria** — é *efeito* do
   julgamento. As quatro espécies de decisão têm caminho de cumprimento; o da reavaliação passa
   por distribuir a outro avaliador e consolidar (§H.2).
4. **O ciclo não termina na divulgação.** A ordem pode vir de cálculo ou de sorteio; o corte decide
   quem segue para a Etapa seguinte ou quem entra na faixa de vagas; e depois vêm a apuração de
   ocupação, a convocação com suplência, o Requerimento de Matrícula e a exportação. A cadeia é
   imposta: a convocação recusa recorte sem ordem vigente e sem apuração emitida, e a apuração
   recusa recorte sem quadro publicado. O resultado definitivo **não** é pré-condição de convocar —
   o momento é decisão institucional, e o manual precisa dizê-lo.

### B.2 O mapa

**(R5)** O mapa passou de 16 para **19 fases**. As fases 1 a 15 mantêm o número; a 16 antiga
(encerrar) virou a 19, e as três novas entram antes dela. "Presidência" abaixo quer dizer
**presidência ou Gestor** — a mesma porta (§A.1).

```
┌─ FASE 1 · ABRIR ───────────────────────────────── Gestor
│  Criar Processo e primeiro Edital (uma tela) · Novo Edital neste Processo
│  (Ativar é opcional: publicar o primeiro Edital ativa o Processo)
│
├─ FASE 2 · ELABORAR ────────────────────────────── Elaborador
│  [Partir de um Edital anterior — só com o rascunho vazio]
│  Assistente de 9 passos:
│  Identificação → Perfis de Vaga → Cronograma → Etapas de Avaliação →
│  Classificação → Inscrição → Anexos → Conteúdo → Revisão
│  (duplicar Perfil · aplicar a todos os Perfis · quadro de vagas por modalidade ·
│   corte e recurso declarados no marco · Requerimento de Matrícula no passo Inscrição)
│  ↓  Submeter para revisão            ◆ congela a revisão — pendência "Impede" recusa
│
├─ FASE 3 · APROVAR ─────────────────────────────── Homologador
│  Homologar (com fundamento)   ⟲ Devolver para elaboração
│                               ⟲ Revogar homologação
│  ↓
├─ FASE 4 · PUBLICAR ────────────────────────────── Publicador
│  Publicar (autoridade signatária)     ■ SEM RETORNO
│  → Edital público e imutável; o PDF gerado é o ato oficial
│  → aparece na vitrine pública; o primeiro Edital ativa o Processo
│
├─ FASE 5 · RECEBER INSCRIÇÕES ──────────────────── Candidato
│  Entrar por código → Seus dados (nome e CPF, uma vez) → escolher vaga e
│  modalidade → documentos → [Requerimento, se pedido na inscrição] →
│  fatos exigidos → revisar → Enviar inscrição
│  → Comprovante com protocolo (e PDF)  ■ fatos declarados e CPF congelam no envio
│
├─ FASE 6 · ORGANIZAR A COMISSÃO ───────────────── Gestor        ∥ paralela à 5
│  Comissão do Processo (presidente + membros) → Alocação por Etapa
│
├─ FASE 7 · DISTRIBUIR ──────────────────────────── Presidência
│  Propor distribuição (rodízio) → Confirmar esta distribuição
│  ⟲ Registrar impedimento    ⟲ Retirar as selecionadas
│
├─ FASE 8 · AVALIAR ─────────────────────────────── Avaliadores
│  Minhas Etapas → Minha Mesa → inscrição a inscrição
│  forma DECISÓRIA (rótulos do Edital + parecer)  ou  PONTUADA (nota)
│  Salvar sem concluir → Concluir avaliação   ■ concluída vira leitura
│  ⟲ Reabertura é ato da presidência (Conclusões preservadas)
│
├─ FASE 9 · CONSOLIDAR ──────────────────────────── Presidência
│  ⟲ Registrar ocorrência (elimina quem não foi avaliado)
│  Prontidão da Etapa → Consolidar as N prontas
│  → Resultado da Etapa: Habilitada | Eliminada     ■ SEM RETORNO por inscrição
│
├─ FASE 10 · CLASSIFICAR E CORTAR ───────────────── Presidência
│  um recorte por vez (ampla e cada lista reservada), ou o marco inteiro pela tela do marco
│  Marco por pontuação: cálculo + desempate → Emitir ordem
│  Marco por sorteio: Publicar a relação → observar a ocorrência (semente) →
│                     Realizar o sorteio (sem prévia)
│                     ⟲ Anular = Retificar + sorteio sucessor; não desfaz
│  → Ato de classificação                            ■ imutável
│  Corte (quando o marco corta): conferir a faixa → Emitir corte   ■ imutável
│  → a faixa alimenta a Etapa seguinte (volta à fase 7 para ela) ou a ocupação
│
├─ FASE 11 · DIVULGAR ───────────────────────────── Publicador
│  Prévia da publicação → Publicar este resultado    ■ SEM RETORNO
│  natureza: PRELIMINAR ou DEFINITIVA
│  → página pública estável + PDF + situação na área do candidato
│
├─ FASE 12 · RECORRER ───────────────────────────── Candidato
│  Acompanhar → Recorrer → escolher o objeto → fundamentar → Interpor
│  objetos atacáveis: a publicação  ou  um Resultado de Etapa
│  ■ só dentro da janela recursal declarada no marco
│
├─ FASE 13 · JULGAR ─────────────────────────────── Julgador
│  [Instruir — Presidência: juntar parecer ou documento à peça  ■ acrescenta]
│  Recursos aguardando decisão → peça → Admitir | Não admitir → Julgar
│  quatro espécies:
│    · Indeferir                    → nenhum efeito
│    · Deferir fixando a correção   → Resultado sucessor (append-only)
│    · Deferir determinando reavaliação → distribuir a OUTRO avaliador →
│      Mesa → consolidar em cumprimento → Resultado sucessor
│    · Determinar providência a jusante → pendência registrada
│  ■ non reformatio in pejus: a correção não pode piorar quem recorreu
│  ■ julgador que atuou no ato atacado está impedido
│
├─ FASE 14 · REFAZER E REPUBLICAR ───────────────── Presidência + Publicador
│  Resultado superado → classificação fica OBSOLETA →
│  Emitir ato sucessor (com motivo) → nova Publicação sucede a anterior
│  ■ a publicação anterior permanece consultável, dizendo que foi sucedida
│
├─ FASE 15 · DEFINITIVO ─────────────────────────── Publicador
│  Publicar resultado DEFINITIVO — porta de fato, cinco impedimentos:
│  recurso pendente · reingresso pendente · reavaliação pendente ·
│  providência pendente · janela recursal ainda aberta
│  (e mais: corte obsoleto recusa QUALQUER divulgação; definitiva não é
│   sucedida por preliminar; marco sem prazo computável exige declaração
│   expressa de encerramento do prazo — a lista completa está em C-20)
│
├─ FASE 16 · OCUPAR ─────────────────────────────── Presidência         (R5)
│  Apurar a ocupação por recorte: publicadas · efetivas · ocupadas · faltando
│  ■ imutável (sucessão com motivo)   → Faixa seguinte leva o déficit ao corte
│
├─ FASE 17 · CONVOCAR ───────────────────────────── Presidência         (R5)
│  Convocar (a espécie sai da posição: vaga inicial | suplência | regularizar)
│  → comunicação: e-mail individual OU registro da publicação, conforme o Edital
│  → desfecho (aceite, regularização, desistência, não atendimento…)
│  gestos em lote: convocar titulares · não atendimento dos vencidos ·
│  emitir pendentes · atestado de fato externo       ■ cada ato fica
│  Candidato: vê a convocação no portal (hoje só por endereço — §H.18)
│
├─ FASE 18 · MATRICULAR ─────────────── Candidato → Exportador           (R5)
│  Requerimento de Matrícula (se pedido na convocação) → Enviar  ■ imutável
│  Exportador: escolher a população → conferir → Baixar o arquivo
│  ■ a geração fica registrada; o arquivo não é guardado
│
└─ FASE 19 · ENCERRAR ───────────────────────────── Gestor
   Encerrar cada Edital (motivo) → só então Encerrar o Processo   ■ SEM RETORNO
   ⟲ Cancelar Edital / Processo — interrupção, não encerramento
```

### B.3 O que corre em paralelo

- **Retificação** — ciclo próprio e completo (elaborar → submeter → homologar → publicar), disponível
  a qualquer momento com o Edital publicado, inclusive com inscrições em andamento e inclusive
  depois de resultados emitidos. Tem **vigência**: uma Retificação pode entrar em vigor no futuro.
- **Composição da comissão** (fase 6) roda em paralelo às inscrições (fase 5) — **(R5)** mas só
  até a alocação: **distribuir é recusado enquanto o período de inscrições corre**, e a tela diz
  "Ainda não é possível distribuir esta Etapa."
- **Avaliação de várias Etapas** roda em paralelo; cada Etapa consolida no seu tempo — salvo a
  Etapa governada por um corte, que só recebe a faixa depois de o corte ser emitido.
- **Recursos** de vários candidatos correm juntos e são julgados um a um.
- **Auditoria** é consultável em qualquer instante, por Processo e por Edital.
- **(R5) Vários Editais no mesmo Processo**, cada um no seu ponto do ciclo; e, dentro de um marco,
  **cada recorte** (a ampla e cada lista reservada) tem sua ordem, seu corte, sua apuração, seu
  sorteio e sua convocação — a tela do marco mostra os recortes lado a lado e pratica o gesto que
  falta em todos de uma vez.
- **(R5) Rodadas de convocação** sucedem-se enquanto houver vaga e fila: desfechos, vencidos,
  suplentes e faixa seguinte.
- **(R5) Supervisão** — a página do Processo e a Supervisão mostram o pulso das inscrições, os
  próximos marcos e os sinais de "Atenção" a qualquer momento; a Visão Geral faz o mesmo para a
  instituição inteira.

### B.4 Pontos sem retorno

O manual precisa marcá-los com o mesmo símbolo, sempre:

| Ato | O que trava |
|---|---|
| **Submeter para revisão** | O formulário fecha; a revisão congela |
| **Publicar Edital** | Imutável; correção só por Retificação |
| **Publicar Retificação** | Idem; a versão consolidada nasce |
| **Enviar inscrição** | Os fatos declarados congelam com o valor do envio; **(R5)** o CPF passa a só ser corrigido pelo atendimento |
| **Concluir avaliação** | Vira leitura; só a presidência reabre |
| **Registrar ocorrência** | Elimina, e não se desfaz |
| **Consolidar o Resultado da Etapa** | Não reconsolida; corrigir exige recurso |
| **Emitir ordem** | Ato imutável; corrigir exige ato sucessor |
| **(R5) Publicar a relação do sorteio** | Endereço público e estável; substituir exige relação sucessora com motivo |
| **(R5) Realizar o sorteio** | Ordem e ato constituídos de uma vez, **sem prévia**; anular constitui um sucessor, não desfaz |
| **(R5) Emitir corte / faixa seguinte** | A faixa só muda por geração sucessora, com motivo |
| **Publicar resultado** | Público; corrigir exige publicação sucessora; **(R5)** definitiva não é sucedida por preliminar |
| **(R5) Instruir, admitir, julgar recurso** | Cada registro acontece uma vez; instruir de novo acrescenta |
| **(R5) Apurar a ocupação** | Imutável; nova apuração exige motivo |
| **(R5) Convocar · registrar desfecho · atestar fato externo** | Registram e comunicam; nenhum se desfaz |
| **(R5) Enviar o Requerimento de Matrícula** | Imutável; "Conferir e atualizar" só com convocação em aberto, e cria um sucessor |
| **(R5) Gerar o arquivo de matrícula** | A geração fica registrada; o arquivo não é guardado |
| **Encerrar / Cancelar** | Nenhuma transição posterior; **(R5)** o Processo só encerra com todos os Editais encerrados ou cancelados |

**(R5)** Eram dez linhas; são dezoito, e algumas reúnem mais de um ato — hoje são mais de vinte. O `⛔` do §G.2 continua reservado a eles, e a régua "forte,
rara" passa a valer por capítulo, não pelo manual inteiro.

### B.5 Atos históricos — o que nunca desaparece

Publicações, documentos publicados, versões consolidadas, atos administrativos, conclusões
preservadas, Resultados de Etapa, atos de classificação e suas posições, publicações de resultado
e situações divulgadas, recursos, juízos de admissibilidade e decisões, e a trilha de auditoria —
e, **(R5)**, instruções de recurso; cortes e suas gerações; relações, ocorrências e sorteios;
apurações de ocupação e seus movimentos; convocações, desfechos, comunicações e atestados;
Requerimentos de Matrícula e as versões que corrigiram; gerações do arquivo de matrícula.
**Nada é excluído.** Encerrar e cancelar são atos motivados que preservam tudo.

### B.6 De quem é cada ação

- **Do candidato:** entrar, informar nome e CPF uma vez, escolher vaga e modalidade, preencher,
  anexar, declarar, enviar, acompanhar, recorrer, gerir os próprios e-mails, vincular participação
  anterior — e **(R5)** ver a convocação e enviar o Requerimento de Matrícula.
- **Da comissão:** distribuir (presidência), avaliar (membros), impedir, registrar ocorrência,
  consolidar, emitir a ordem classificatória, reabrir avaliação — e **(R5)** sortear, cortar,
  apurar a ocupação, convocar e instruir recurso. Tudo o que é da presidência aceita também o
  Gestor (§A.1).
- **Da autoridade institucional:** criar o Processo e seus Editais, homologar, publicar Edital e
  Retificação, divulgar resultado, julgar recurso, encerrar e cancelar — e **(R5)** exportar para
  matrícula, que é papel à parte.

---

## C. Arquitetura de capítulos

Nenhum capítulo é numerado por spec. A organização atende às duas entradas do leitor: quem quer
**entender** desce pelas Partes 1 e 2; quem precisa **fazer agora** entra pela Parte 3 (trilha do
seu papel) ou pela Parte 4 (a tarefa pelo nome).

```
PARTE 1 — ENTENDER O SISTEMA          (leitura linear, 6 capítulos curtos)
PARTE 2 — AS FASES DO PROCESSO        (o corpo do manual, 25 capítulos, ordem cronológica)
PARTE 3 — TRILHAS POR PAPEL           (9 páginas-roteiro, sem conteúdo próprio: apontam)
PARTE 4 — TAREFAS FREQUENTES          (receitas curtas, entrada por verbo)
PARTE 5 — SITUAÇÕES EXCEPCIONAIS      (o que fazer quando dá errado)
PARTE 6 — REFERÊNCIA                  (glossário, mapa de telas, limites, FAQ)
```

**A decisão editorial central:** as fases são o corpo; as trilhas por papel são **roteiros de
navegação**, não cópias do conteúdo. A trilha do homologador é uma página de meia tela que diz
"seu trabalho é este, ele acontece aqui, comece por C-08" e nada mais. Isso evita a duplicação
que mataria a manutenção do manual — e é o que permite as duas entradas sem escrever tudo duas
vezes.

### Parte 1 — Entender o sistema

| # | Capítulo |
|---|---|
| C-01 | O que este sistema faz (e o que ele não faz) |
| C-02 | As duas portas: a área de gestão e o portal público |
| C-03 | O ciclo completo em um mapa |
| C-04 | Quem faz o quê — e por que ninguém faz tudo |
| C-05 | Seis ideias que explicam todo o resto **(R5: eram cinco)** |
| C-22 | A Visão Geral da instituição **(R5)** |

### Parte 2 — As fases do processo

**(R5) Regra de numeração.** Os códigos C-01 a C-21 não mudam: o §D, o §F, o inventário e o piloto
os citam. Capítulo novo da Parte 2 recebe **sufixo de letra** junto do capítulo da fase vizinha, de
modo que a leitura cronológica se mantém sem renumerar nada; capítulo novo de outra Parte vai para
o fim da numeração (C-22).

| # | Capítulo | Fase |
|---|---|---|
| C-06 | Abrir o Processo Seletivo, criar Editais e partir de um anterior | 1 |
| C-07 | Elaborar o Edital I — identificação, Perfis, quadro de vagas e cronograma | 2 |
| C-08 | Elaborar o Edital II — Etapas, marcos, desempate, sorteio, corte e recurso | 2 |
| C-09 | Elaborar o Edital III — inscrição, Requerimento, anexos, conteúdo e revisão final | 2 |
| C-10 | Submeter, homologar e publicar o ato oficial | 3–4 |
| C-11 | O período de inscrições, visto de dentro | 5 |
| C-11a | **(R5)** Acompanhar o certame: o Processo, a Supervisão e os sinais de Atenção | 5–19 |
| C-12 | Inscrever-se — o manual do candidato | 5 |
| C-13 | Montar a comissão e alocar por Etapa | 6 |
| C-14 | Distribuir o trabalho | 7 |
| C-15 | Avaliar — o manual do avaliador | 8 |
| C-16 | Consolidar o resultado de cada Etapa | 9 |
| C-17 | Classificar — por recorte e pela tela do marco | 10 |
| C-17a | **(R5)** Ordenar por sorteio público | 10 |
| C-17b | **(R5)** Cortar: quem segue para a Etapa seguinte ou para as vagas | 10 |
| C-18 | Divulgar o resultado | 11 |
| C-19 | Recursos — interpor, instruir, admitir e julgar | 12–13 |
| C-20 | Refazer e republicar depois de um recurso | 14–15 |
| C-20a | **(R5)** Apurar a ocupação das vagas | 16 |
| C-20b | **(R5)** Convocar, chamar de novo e suplência | 17 |
| C-20c | **(R5)** O Requerimento de Matrícula | 5, 18 |
| C-20d | **(R5)** Exportar para matrícula | 18 |
| C-21 | Encerrar o certame | 19 |
| C-21a | **(R5)** Retificar um Edital publicado | paralela |

*(São 25 capítulos na Parte 2. C-07 a C-09 continuam sendo o assistente dividido em três. **(R5)**
A Retificação foi promovida de receita a capítulo porque a `048` a fez acrescentar Perfil,
Modalidade, linha do quadro, critério, Evento e Anexo, com "aplicar a todos" — não cabe mais numa
receita. R-01 fica como receita curta que aponta para C-21a.)*

### Parte 3 — Trilhas por papel

`T-01` Gestor · `T-02` Elaborador · `T-03` Homologador · `T-04` Publicador ·
`T-05` Presidente da comissão · `T-06` Avaliador · `T-07` Julgador de recursos ·
`T-08` Candidato · `T-09` Exportador de matrículas **(R5)**

**(R5)** `T-01` (Gestor) aponta também para os capítulos de `T-05`, com a advertência da §A.3: o
Gestor **pode** praticá-los, e numa equipe de duas pessoas não deve.

### Parte 4 — Tarefas frequentes

`R-01` Corrigir algo num Edital já publicado (Retificação — aponta para C-21a) · `R-02` Encerrar as
inscrições antes do prazo · `R-03` Trocar um avaliador no meio da Etapa · `R-04` Reabrir uma
avaliação já concluída · `R-05` Conferir quantas inscrições chegaram e o que veio · `R-06` Baixar o
comprovante ou o PDF oficial · `R-07` Acrescentar um e-mail à conta do candidato · `R-08` Vincular
uma participação anterior · `R-09` Emitir um ato de classificação sucessor · `R-10` Consultar quem
fez o quê (auditoria) · **(R5)** `R-11` Começar um Edital a partir de um anterior · `R-12` Duplicar
um Perfil e aplicar um ajuste a todos · `R-13` Cumprir uma reavaliação determinada por recurso ·
`R-14` Pedir a faixa seguinte quando faltam candidatos

*(R5: `R-02` não foi reconferida contra a tela atual.)*

### Parte 5 — Situações excepcionais

`X-01` O Edital voltou para elaboração (devolução) · `X-02` A homologação foi revogada ·
`X-03` Cancelar em vez de encerrar — e por que não é a mesma coisa · `X-04` Um candidato não pôde
ser avaliado (ocorrência) · `X-05` Um avaliador está impedido · `X-06` Deu empate ·
`X-07` "Este ato está obsoleto" — o que aconteceu e o que fazer · `X-08` A publicação está
bloqueada **(R5: os impedimentos são bem mais que os cinco da definitiva — a lista está em C-20)** · `X-09` O prazo de recurso acabou ·
`X-10` Um recurso não pode piorar a situação de quem recorreu · **(R5)** `X-11` O Processo não
encerra: há Edital pendente · `X-12` O sorteio precisa ser anulado · `X-13` "Você não tem
permissão para isto" — ler a recusa explicada

### Parte 6 — Referência

`G-01` Glossário · `G-02` Mapa de todas as telas · `G-03` O que o sistema **não** faz hoje ·
`G-04` Perguntas frequentes · `G-05` Nota para administradores (única seção com vocabulário técnico)

---

## C.bis — Detalhamento de cada capítulo

Formato: **público · objetivo · pré-requisitos · assuntos · telas · screenshots · exemplo ·
alertas · o que NÃO entra.**

### C-01 · O que este sistema faz (e o que ele não faz)

- **Público:** todos, inclusive quem só vai ler uma vez.
- **Objetivo:** o leitor sai sabendo que o sistema conduz um certame do Edital **(R5)** à
  exportação para matrícula — passando por divulgação, convocação e Requerimento —, que **o PDF
  que o sistema gera é o ato oficial**, e que **uma publicação realizada não é reescrita** — correções geram atos novos, por
  cima, nunca por dentro.
- **Vocabulário — regra para o manual inteiro:** dizer **imutável**, nunca "definitivo", ao falar
  do que uma publicação trava. O sistema usa *definitiva* como **natureza** de um resultado
  (preliminar × definitiva), e as duas leituras colidiriam já no primeiro capítulo. "Definitivo"
  fica reservado para essa natureza; para a imutabilidade, o manual escreve *imutável*,
  *não se reescreve* ou *não tem volta*.
- **Pré-requisitos:** nenhum.
- **Assuntos:** o que é um Processo, o que é um Edital, a diferença entre "editar" e "retificar",
  a promessa de que nada se perde, os limites honestos do produto.
- **Telas:** nenhuma completa — uma tira do mapa.
- **Screenshots:** SS-001.
- **Exemplo:** o certame que atravessa o manual inteiro (§F.1).
- **Alertas:** ⚠ Publicar não tem volta.
- **NÃO entra:** papéis, permissões, nenhum passo a passo.

### C-02 · As duas portas

- **Público:** todos.
- **Objetivo:** o leitor nunca mais procura a tela errada no endereço errado.
- **Assuntos:** `/gestao/` é interna e exige identificação institucional; `/selecoes/` é o portal
  do candidato e do público; o que cada uma mostra; por que uma inscrição não aparece na gestão
  antes de ser enviada.
- **Telas:** vitrine pública; lista de Processos Seletivos.
- **Screenshots:** SS-002, SS-003.
- **(R5) Acrescentar:** o cabeçalho da gestão tem "Minhas Etapas" para qualquer pessoa
  identificada; a lista traz "Novo Processo Seletivo" e, para o Gestor, "Visão Geral". A vitrine
  ganhou busca, filtros e ordenação, e a consulta fica no endereço — pode ser compartilhada.
- **Alertas:** 💡 quem digita o endereço raiz cai na vitrine pública, não na gestão. **(R5)** 💡 a
  vitrine não tem caminho para a gestão; quem opera guarda o endereço `/gestao/`.
- **NÃO entra:** como entrar (§H.1 — não há login institucional documentável ainda).

### C-03 · O ciclo completo em um mapa

- **Público:** todos.
- **Objetivo:** dar ao leitor a figura que ele vai revisitar o manual inteiro.
- **Assuntos:** as **19 fases (R5)**, quem pratica cada uma, o que corre em paralelo, os pontos sem
  retorno. **(R5)** O mapa precisa mostrar as duas origens da ordem (cálculo ou sorteio), o corte
  que devolve à fase 7 para a Etapa seguinte, e a cauda ocupar → convocar → matricular.
- **Telas:** nenhuma — este capítulo é **diagrama**, não captura.
- **Screenshots:** nenhum. Ilustração vetorial (§G.4).
- **Alertas:** ✅ um quadro "onde estou" que reaparece no topo de cada capítulo da Parte 2.
- **NÃO entra:** detalhe de qualquer fase.

### C-04 · Quem faz o quê — e por que ninguém faz tudo

- **Público:** todos, sobretudo gestores.
- **Objetivo:** entender a segregação de funções como regra de trabalho, não como burocracia.
- **Assuntos:** os **sete (R5)** papéis; a presidência e a atribuição como vínculos, não papéis;
  **(R5)** que o Gestor alcança os atos da presidência; por que a mesma pessoa não pode elaborar,
  homologar **e** publicar a mesma revisão — e pode fazer duas das três; por que julgar recurso é
  papel isolado; por que exportar para matrícula também é. **(R5)** O aviso que a tela de
  homologação dá um ato antes ("Depois de homologar, você não poderá publicar esta revisão") e a
  recusa explicada (`033`), que nomeia a permissão que teria servido.
- **Bloco obrigatório — "E se somos duas ou três pessoas?"** Fecha o capítulo e é, para a operação
  inicial prevista, a parte mais útil dele. Traz: papéis são funções e podem ser acumulados; as
  três regras que olham para a pessoa e não para a permissão; a regra de ouro — **escolha primeiro
  quem julga recursos e mantenha essa pessoa fora da cadeia de avaliação e divulgação**; a tabela
  das duas configurações que fecham o ciclo (§A.3); e o que uma equipe de duas pessoas perde. Sai
  como recomendação de organização, nunca como limitação do produto.
- **Telas:** tela de recusa por permissão; cartão "O que fazer agora" com ação desabilitada e motivo;
  peça de recurso com o impedimento nomeado.
- **Screenshots:** SS-004, SS-005, SS-088.
- **Exemplo:** a elaboradora tenta homologar e recebe recusa nominal; e a configuração de duas
  pessoas do §A.3, com os nomes do certame-exemplo. **(R5)** O bloco "duas ou três pessoas" ganha
  a frase da §A.3: *o Gestor pode consolidar, emitir e convocar — e, se for também quem julga, não
  deve*.
- **Alertas:** ⚠ ação cinzenta com um motivo ao lado não é defeito — é o sistema avisando antes.
  ⚠ acumular papéis é legítimo; acumular **atos do mesmo caso** é o que o sistema recusa.
- **NÃO entra:** nomes de permissões em formato técnico; a lista completa de permissões por papel
  (vai para `G-05`).

### C-05 · Seis ideias que explicam todo o resto

- **Público:** todos.
- **Objetivo:** entregar de uma vez os seis conceitos sem os quais todo o resto parece arbitrário.
- **Assuntos:** (1) publicação é imutável; (2) retificação corrige por cima e tem vigência;
  (3) versão vigente ≠ versão histórica; (4) ato emitido é fotografia, não fórmula viva;
  (5) tudo fica registrado; **(R5)** (6) **o documento publicado é o ato oficial** — o PDF que o
  sistema gera é o que vale (`054`), traz no fecho local, data, autoridade e ato de nomeação, e
  não se regenera depois: mudar o sistema não muda o que já foi publicado.
- **Telas:** detalhe do Edital publicado com a lista de documentos publicados; ato de classificação
  marcado como sucedido.
- **Screenshots:** SS-006, SS-007.
- **Alertas:** 🔎 caixa "O que muda depois?" em cada uma das cinco.
- **NÃO entra:** hash, assinatura, estrutura de dados.

### C-06 · Abrir o Processo Seletivo, criar Editais e partir de um anterior

- **Público:** gestor; elaborador para a última seção.
- **Objetivo:** sair com um Processo e um Edital em elaboração — **(R5)** e saber acrescentar outro
  Edital ao mesmo Processo e começar um Edital a partir de outro já publicado.
- **Pré-requisitos:** ter o papel de gestor.
- **Assuntos:** Processo × Edital; código institucional; numeração do Edital única por ano. O
  Processo **nasce com o primeiro Edital**, numa tela só. **(R5)** "Novo Edital neste Processo"
  existe desde 16/09 e o capítulo volta a ensinar um Processo com vários Editais. A página do
  Processo é hoje um painel ("Onde cada Edital está", pulso de inscrições, próximos marcos,
  Atenção) — aqui só a apresentação; a leitura é de C-11a. **(R5)** "Partir de um Edital
  anterior": só com o rascunho vazio, o que vem junto e o que não vem, e o aviso que acompanha
  todos os passos ("datas, vagas e prazos são da oferta anterior"); Cronograma copiado e vencido
  deixa o passo pendente e a Revisão impede publicar.
- **Telas:** lista de Processos; Novo Processo e primeiro Edital; detalhe do Processo; **(R5)** Novo
  Edital; Partir de um Edital anterior e sua confirmação.
- **Screenshots:** SS-008, SS-009, **(R5)** SS-010 volta (Novo Edital), mais as do reaproveitamento
  (`01-…`, §R5).
- **Exemplo:** *Processo Seletivo Simplificado 2026 · Edital 03/2026 — Auxiliar de Biblioteca*.
- **Alertas:** ~~🕒 ative o Processo antes de publicar o Edital.~~ **(R5) Era falso:** publicar o
  primeiro Edital ativa o Processo; ativar à mão é opcional. ⚠ partir de um anterior **substitui**
  o que já estiver composto — a tela pede confirmação.
- **NÃO entra:** comissão (é a fase 6, e tem capítulo).

### C-07 · Elaborar o Edital I — identificação, perfis, vagas e cronograma

- **Público:** elaborador.
- **Objetivo:** os três primeiros passos do assistente prontos e sem pendências.
- **Pré-requisitos:** Edital em elaboração.
- **Assuntos:** o assistente e seus nove passos; estados dos passos (pendente / pronta para
  revisar / concluída) — **(R5)** os estados não bloqueiam nada, quem barra é a Revisão; "Salvar
  rascunho" e o rascunho local do navegador ("Restaurar o que eu havia digitado"); Perfil de Vaga;
  modalidades e reserva; vagas imediatas × cadastro de reserva; requisitos; Cronograma e Eventos.
  **(R5) Novos no passo Perfis:** a visão do conjunto ("Perfis deste Edital (N)", um cartão aberto
  por vez); o **quadro de vagas por modalidade**, que só aparece quando há lista reservada e é
  conferido contra as vagas imediatas; "Duplicar este Perfil"; o bloco "Declarado uma vez para
  todos os Perfis" e "Aplicar aos demais Perfis (N)"; os **fatos exigidos do candidato** (a tela é
  esta, o conceito é de C-08); "Qual delas é a ampla concorrência"; a reversão de vaga reservada
  não preenchida; **"Como a convocação é comunicada"**. **(R5)** A Identificação agora tem título e
  descrição editáveis. O Evento ganhou tipo, término opcional e "Onde acontece".
- **Telas:** passo Identificação; passo Perfis (com linha de modalidade **e quadro de vagas**);
  passo Cronograma.
- **Screenshots:** SS-011, SS-012, SS-013, SS-014 **(R5: SS-013 e SS-014 mudam de conteúdo — ver
  `01-…`, §R5)**.
- **Exemplo:** **(R5, reescrito)** um Perfil com 2 vagas + cadastro de reserva, com a lista
  reservada PPI declarada — a ampla concorrência **não** se declara como Modalidade: é a linha geral
  do quadro ("Nenhuma — a ampla concorrência é só a linha geral do quadro").
- **Alertas:** ~~⚠ sem um Evento marcado como período de inscrições…~~ **(R5)** o período de
  inscrições **não se escolhe mais no Cronograma**: escolhe-se no passo Inscrição (C-09), e a
  ausência é Aviso na Revisão. ⚠ **(R5)** Evento vencido deixa o passo Cronograma pendente; período
  de inscrições já encerrado **impede** publicar. ⚠ **(R5)** Perfil cujo marco corta precisa
  declarar "Como a convocação é comunicada" — sem isso a Revisão **impede** submeter (`051`); e
  só a forma "por mensagem individual" faz o sistema enviar e-mail na convocação. ⚠ **(R5)** o Evento exige hora:
  Evento só com data sai "às 00h" no documento. 💡 o assistente pode ser percorrido fora de ordem,
  mas cada passo depende do anterior para oferecer escolhas — siga a ordem na primeira vez.
- **NÃO entra:** etapas de avaliação e classificação (C-08); **(R5)** o catálogo de modalidades da
  `039` — a spec é registro de decisão, e a Modalidade continua dentro do Perfil.

### C-08 · Elaborar o Edital II — etapas de avaliação e regra de classificação

- **Público:** elaborador. **É o capítulo mais difícil do manual.**
- **Objetivo:** compor uma regra de avaliação e de classificação que o sistema consiga executar e
  que um leitor do Edital consiga reconstituir.
- **Pré-requisitos:** perfis e cronograma prontos.
- **Assuntos:** Etapa de Avaliação; **as duas formas** — pontuada (nota, **(R5)** pontuação
  máxima — o termo "faixa" sai —, nota mínima) e decisória (dois rótulos escolhidos pelo Edital,
  p.ex. Deferida/Indeferida); peso; **(R5)** caráter eliminatório/classificatório; avaliações por
  inscrição; vínculo da Etapa a um Evento do cronograma; **Marco Classificatório**; **(R5)** "Como
  a ordem deste marco é produzida" — pela pontuação combinada **ou por sorteio** (com o método do
  sorteio declarado no Edital); quais Etapas o marco combina — com uma Etapa só, a tela não pergunta
  como as pontuações se combinam; normalização, escala e arredondamento; critérios de desempate e o
  que cada um compara; o que acontece quando o dado do desempate falta; **fatos declarados**; **a
  janela recursal declarada no marco** — **(R5)** três opções: admite, não admite, não declara;
  **(R5) a Regra de corte** (quantos progridem, suplentes, empate na última posição, Etapa que o
  corte alimenta, faixa seguinte); vários marcos por Perfil (o par preliminar/final); a visão do
  conjunto "Classificação dos Perfis deste Edital (N)".
- **Telas:** passo Etapas de Avaliação; passo Classificação (marco + critérios **+ corte +
  recurso**; **(R5)** marco de sorteio).
- **Screenshots:** SS-015, SS-016, SS-017, SS-018 **(R5: as quatro mudam — §R5 do inventário;
  e o espécime de C-08 do piloto precisa ser recapturado na tela da `053`)**.
- **Exemplo:** Etapa 1 decisória (Deferida/Indeferida) + Etapa 2 pontuada (0–100, mínima 60, peso 2);
  marco FINAL combinando as duas, três critérios de desempate, recurso em 5 dias corridos, **(R5)**
  corte "quantas vagas o quadro publicar no recorte".
- **Alertas:** ⚠ **declare a janela recursal aqui.** Se o marco não disser que admite recurso e por
  quantos dias, o resultado definitivo depois exigirá uma declaração escrita de encerramento de
  prazo — e recurso nenhum terá prazo computável. ⚠ um critério de desempate precisa dizer *o que*
  compara. **(R5)** ⚠ sem corte não há faixa, e sem faixa não há convocação: o primeiro marco já
  nasce com o corte "o que o quadro publicar"; Perfil sem nenhum marco que corte **impede**
  publicar. ⚠ **(R5)** duas avaliações por inscrição sem regra de combinação impedem publicar
  quando o fluxo exige o Resultado da Etapa. ⚠ **(R5)** a mesma Etapa tem um peso só, em todos os
  marcos que a enumeram. ⚠ **(R5)** prazos só em dias corridos. ⚠ **(R5)** o prazo de recurso escrito como Evento do Cronograma é
  texto livre e não se liga à janela do marco: confira que as duas datas batem (RC-76).
- **NÃO entra:** como se calcula a nota final passo a passo (vai para C-17); a execução do sorteio
  e do corte (C-17a, C-17b).

### C-09 · Elaborar o Edital III — inscrição, anexos, conteúdo e revisão final

- **Público:** elaborador.
- **Objetivo:** fechar a composição e submeter sem pendências impeditivas.
- **Assuntos:** **(R5)** o **período de inscrições** ("Evento do Cronograma", ou "Este Edital não
  recebe inscrições pelo sistema"); **(R5)** o teto "Inscrições por candidato neste Edital";
  Documento Exigido (por perfil e por modalidade — **(R5)** com o grupo "Em todos os Perfis");
  vínculo de um documento a um **modelo oficial**; **(R5)** o Requerimento de Matrícula ("Quando
  pedir": não pede / no ato da inscrição / quando o candidato for convocado; texto da declaração
  de veracidade); Anexo do Edital (rótulo editorial + arquivo; cada operação grava na hora, o passo
  não tem "Salvar rascunho"); **(R5)** o Conteúdo como **22 seções fixas**, numeradas como sairão no
  documento — 5 compostas automaticamente, nenhuma com redação padrão, seção vazia não sai no
  documento; o painel "O que falta para submeter", com itens **Impede** e **Aviso** — **(R5)** é o
  mesmo exame da publicação, de modo que o que passa aqui é executável; "O que será congelado na
  submissão"; **(R5)** "O que não se corrige depois de publicado (N)"; a prévia do documento, que
  não traz local, data nem autoridade.
- **Telas:** passo Inscrição; passo Anexos; passo Conteúdo; passo Revisão; Prévia do Edital.
- **Screenshots:** SS-019, SS-020, SS-021, SS-022, SS-023 **(R5: SS-019 e SS-021 mudam — §R5 do
  inventário)**.
- **Exemplo:** três documentos exigidos, um deles só para PPI, com o modelo de autodeclaração
  anexado; **(R5)** Requerimento de Matrícula pedido "quando o candidato for convocado".
- **Alertas:** ⚠ remover um anexo apaga o arquivo do rascunho — reenviar é o único caminho de volta.
  **(R5)** ⚠ Apresentação e Disposições Finais vazias geram Aviso na Revisão. ⚠ o momento do
  Requerimento **não** se retifica depois de publicado; a declaração, sim. ✅ ao terminar: nenhuma
  pendência impeditiva no painel de revisão.
- **NÃO entra:** a submissão em si (C-10).

### C-10 · Submeter, homologar e publicar

- **Público:** elaborador, homologador, publicador — os três, na ordem em que atuam.
- **Objetivo:** levar o Edital de "Em elaboração" a "Publicado" com as três pessoas certas.
- **Pré-requisitos:** composição sem pendências impeditivas.
- **Assuntos:** submeter e o que congela; a trilha de estados do Edital; homologar com fundamento;
  devolver com motivo; revogar homologação; publicar com autoridade signatária; o documento
  publicado; a segregação que impede a mesma pessoa de fechar o ciclo; "Quem atuou". **(R5)** O
  aviso de segregação um ato antes, na homologação; os avisos não impeditivos do quadro de vagas
  na confirmação; a conferência da prévia contra o original pelo homologador (processo
  institucional, sem tela própria); o fecho do PDF publicado (local, data, autoridade, ato de
  nomeação); publicar o primeiro Edital ativa o Processo.
- **Telas:** confirmação de submissão; detalhe em revisão; confirmação de homologação; confirmação
  de publicação; detalhe publicado com documentos.
- **Screenshots:** SS-024, SS-025, SS-026, SS-027, SS-028, SS-029.
- **Exemplo:** Elena submete, Wagner homologa, Paula publica.
- **Alertas:** ⛔ **Publicar não tem volta.** ⚠ o fundamento da homologação e o motivo da devolução
  ficam registrados e são lidos por quem vier depois. 👤 três pessoas, sempre.
- **NÃO entra:** retificação (R-01).

### C-11 · O período de inscrições, visto de dentro

- **Público:** gestor.
- **Objetivo:** acompanhar o que está chegando sem interferir.
- **Assuntos:** a lista de inscrições recebidas e o contador; rascunhos "em preenchimento" ×
  inscrições enviadas; abrir uma inscrição recebida; ver os documentos apresentados; o que o gestor
  **não** pode fazer com uma inscrição. **(R5)** A ação no Edital chama-se "Inscrições recebidas
  (N)"; a lista ganhou filtro por Perfil, busca por "Nome, protocolo ou CPF", filtro de
  Concorrência e as colunas Protocolo / Candidato / CPF / Perfil / Concorrência / Documentos /
  Situação. O detalhe mostra "Versão do Edital aceita", "Código de verificação" (para conferir
  contra o comprovante), o Requerimento de Matrícula quando há, e "Não se aplicam a esta
  inscrição" — os documentos que o recorte documental (`044`) tirou da lista dela.
- **Telas:** Inscrições recebidas; detalhe da inscrição recebida.
- **Screenshots:** SS-030, SS-031 **(R5: as duas mudam — §R5 do inventário)**.
- **Alertas:** ⚠ rascunho não é inscrição; o contador só conta o que foi enviado.
  ⚠ dado pessoal — consulte só o necessário. **(R5)** 🔎 a lista de documentos exigidos congela no
  envio, como os fatos declarados.
- **NÃO entra:** avaliação; o pulso das inscrições (C-11a).

### C-11a · Acompanhar o certame: o Processo, a Supervisão e os sinais de Atenção **(R5)**

- **Público:** gestor e presidência; auditor para a parte que lê.
- **Objetivo:** saber, sem abrir Edital por Edital, onde cada um está e o que pede atenção.
- **Pré-requisitos:** um Processo com Edital publicado.
- **Assuntos:** a página do Processo como painel — "Onde cada Edital está", o pulso de inscrições,
  os próximos marcos, "Aguardando quem elabora"; a **Supervisão do Processo** (`022`), só para a
  gestão da comissão e a presidência; os **sinais de Atenção** (`038`/`045`) — ato obsoleto, ato
  não divulgado, ordem sem ocupação apurada, recurso em que todos estão impedidos, Etapa pronta para
  distribuir —, cada um levando à tela que resolve; por que cada pessoa vê só os sinais do que ela
  alcança, e a frase de ausência é relativa a isso; o cartão "O que fazer agora" do Edital, com a
  ação principal, as secundárias e as terminais, e "aguardando quem…".
- **Telas:** detalhe do Processo; Supervisão do Processo; detalhe do Edital com o cartão de ações.
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** 🔎 nenhum sinal pratica nada — todos levam a uma tela onde o ato acontece.
  ⚠ quem não alcança a Supervisão recebe "não encontrado", e não a recusa explicada.
- **NÃO entra:** a Visão Geral institucional (C-22).

### C-12 · Inscrever-se — o manual do candidato

- **Público:** candidato e público anônimo. **Deve funcionar isolado do resto do manual.**
- **Objetivo:** o candidato encontra a vaga, se inscreve, envia e guarda o comprovante.
- **Pré-requisitos:** nenhum.
- **Assuntos:** a vitrine e a página da seleção; ler o Edital e baixar anexos; entrar por código de
  e-mail (sem senha); escolher vaga e modalidade; preencher; enviar documentos; declarar os fatos
  exigidos; revisar; enviar; o comprovante e o protocolo; retomar um rascunho; o aviso "o Edital foi
  atualizado"; acompanhar; gerir os e-mails da conta; vincular participação anterior.
- **(R5) Assuntos novos:** a vitrine com busca, filtros e os quatro grupos (abertas, próximas,
  encerradas, outras); a página da seleção com a situação ("Acontecendo agora", "Próximo, em…"),
  as Retificações com "O que mudou", os resultados divulgados e, quando há, o bloco do sorteio;
  **"Seus dados"** — nome e CPF uma única vez, antes da primeira inscrição; "Encontramos
  participação anterior" logo após o código; a escolha de modalidade gravada na hora, e a
  confirmação quando mudar de modalidade **descarta documentos**; o Requerimento de Matrícula
  quando pedido na inscrição (a inscrição só é enviada depois dele); o e-mail "Inscrição
  recebida"; o comprovante em PDF; "Minha inscrição" (o que foi enviado); o aviso de rascunho
  fechado quando o período termina.
- **Telas:** vitrine; página da seleção; Entrar; Informe o código; **(R5)** Seus dados; Minhas
  inscrições; Sua inscrição; Revisar e enviar; Comprovante; Acompanhar; Acesso à conta.
- **Screenshots:** SS-032 a SS-042 **(R5: várias mudam, e entram as de "Seus dados", rascunho
  fechado e Requerimento — §R5 do inventário)**.
- **Exemplo:** Ana concorre à ampla; Carla concorre por PPI e vê aparecer a autodeclaração.
- **Alertas:** ⚠ os dados exigidos pelo Edital **congelam no envio** e não mudam depois — **(R5)**
  o CPF também, que depois só o atendimento corrige. ⚠ enquanto não clicar em *Enviar inscrição*,
  ninguém recebeu nada. 🕒 confira o prazo no cartão. ~~"o rascunho não te avisa"~~ **(R5)** o
  rascunho avisa: o período encerrado fecha a inscrição com uma frase clara (§H.9). 💡 **(R5)**
  quem abre um link guardado sem estar identificado recebe "não encontrado": entre primeiro, depois
  abra o link (§H.10, aberta).
- **NÃO entra:** recurso (C-19 tem a parte do candidato; aqui só uma remissão).

### C-13 · Montar a comissão e alocar por Etapa

- **Público:** gestor.
- **Objetivo:** deixar cada Etapa com gente designada.
- **Pré-requisitos:** Processo ativo, Edital publicado com Etapas.
- **Assuntos:** a comissão pertence ao **Processo**, não ao Edital; presidente e membros; adicionar
  vários de uma vez; a matriz de alocação por Etapa; inativar membro; alocações órfãs.
- **Telas:** Comissão do Processo; confirmação; Alocação por Etapa.
- **Screenshots:** SS-043, SS-044, SS-045.
- **(R5) Rótulos atuais:** "Adicionar membro" → "Continuar"; "Adicionar vários de uma vez" →
  "Conferir a lista" → "Confirmar inclusão de N"; por membro, "Alterar função" e "Remover da
  comissão" — **"inativar membro" não é rótulo de tela**: remover inativa o membro e as alocações
  dele, sem apagar nada. Na Alocação, o botão diz "Salvar distribuição" embora o ato seja alocar, e
  cada coluna tem o link "Distribuir". A alocação só existe depois de o Edital ser publicado, e a
  matriz fica desabilitada sem presidência.
- **Alertas:** 👤 designar a presidência não dá poderes de gestão, e ser gestor não dá a presidência
  — **(R5)** mas o Gestor pratica os atos dela pela própria permissão (§A.1). ⚠ sem alocação a Etapa
  não pode ser distribuída. ⚠ **(R5)** a comissão alcança todos os Perfis e polos do Processo:
  distribuição e alocação não filtram por Perfil.
- **NÃO entra:** distribuir inscrições (C-14).

### C-14 · Distribuir o trabalho

- **Público:** presidente da comissão.
- **Objetivo:** cada inscrição com um avaliador responsável, em cada Etapa.
- **Pré-requisitos:** inscrições recebidas e alocação feita.
- **Assuntos:** onde a presidência encontra a Etapa (**(R5)** Alocação por Etapa → "Distribuir";
  "Minhas Etapas" de quem preside e não avalia aponta esse caminho, e a Supervisão leva direto à
  distribuição — a remissão antiga a §H.13 estava errada, era §H.8, e H.8 está fechada);
  **(R5)** os números-filtro da Etapa e a seção "Distribuir o que falta"; "Distribuir as
  selecionadas"; o filtro "fora do corte" e as inscrições "aguardando a Etapa anterior";
  **distribuir é recusado enquanto o período de inscrições corre**;
  quem está alocado; propor distribuição por rodízio; conferir a carga antes de gravar; confirmar;
  distribuir uma a uma; retirar atribuições; atribuições órfãs; registrar impedimento.
- **Telas:** Distribuição da Etapa (proposta e confirmada); Impedimentos.
- **Screenshots:** SS-046, SS-047, SS-048, SS-049.
- **Alertas:** 💡 a proposta mostra a carga por avaliador **antes** de gravar. ⚠ impedimento
  registrado retira a pessoa daquele conjunto — e é registrado com motivo.
- **NÃO entra:** avaliar.

### C-15 · Avaliar — o manual do avaliador

- **Público:** membro da comissão. **Deve funcionar isolado.**
- **Objetivo:** o avaliador conclui suas avaliações corretamente na primeira vez.
- **Pré-requisitos:** ter recebido atribuições.
- **Assuntos:** Minhas Etapas; a Mesa; ler os documentos apresentados; **avaliação decisória** (os
  rótulos que o Edital escolheu + parecer obrigatório no sentido desfavorável); **avaliação
  pontuada** (nota dentro da faixa); salvar sem concluir; concluir; por que a conclusão vira
  leitura; o que fazer se errou. **(R5)** Quem já tem Resultado na Etapa não pode ser concluído, e a
  Mesa diz por quê antes do clique (a exceção é a reavaliação determinada por recurso); inscrição
  fora do corte não aparece na Mesa; "Próxima pendente".
- **Telas:** Minhas Etapas; Minha Mesa; Inscrição na Mesa (decisória e pontuada).
- **Screenshots:** SS-050, SS-051, SS-052, SS-053.
- **Alertas:** ⛔ **concluir não se desfaz por você** — reabrir é ato da presidência.
  ⚠ você só vê o que lhe foi atribuído; isso é proposital. ⚠ **(R5)** a Mesa não avisa quando a
  inscrição é uma reavaliação determinada por recurso — a presidência precisa dizer.
- **NÃO entra:** consolidação, classificação, recursos.

### C-16 · Consolidar o resultado de cada Etapa

- **Público:** presidente da comissão.
- **Objetivo:** transformar avaliações concluídas em Resultados oficiais da Etapa.
- **Pré-requisitos:** avaliações concluídas.
- **Assuntos:** prontidão × oficial; registrar ocorrência (quem não pôde ser avaliado); consolidar
  em lote — **(R5)** "Consolidar as N prontas" ou "Consolidar as selecionadas", sempre pela
  conferência "Confira antes de consolidar"; Habilitada × Eliminada; o que decide a consequência em cada forma; eliminada numa Etapa
  não aparece na Etapa seguinte; Conclusões preservadas e reabertura; a tela de Resultados da Etapa.
- **Telas:** Registrar ocorrência (2 passos); prontidão antes de consolidar; Resultados da Etapa;
  Conclusões preservadas.
- **Screenshots:** SS-054, SS-055, SS-056, SS-057.
- **Alertas:** ⛔ **consolidar não se refaz** — a correção depois disso é matéria de recurso.
  ⚠ ocorrência elimina; leia a revisão antes de "Registrar mesmo assim". ~~alerta da §H.11~~
  **(R5)** a Mesa recusa concluir depois do Resultado, e a ordem "ocorrência antes" deixou de ser
  cuidado do operador. ⚠ **(R5)** a reavaliação cumprida **não** entra em "Consolidar as N prontas":
  marque a linha e use "Consolidar as selecionadas" (§H.2).
- **NÃO entra:** classificação.

### C-17 · Classificar — por recorte e pela tela do marco

- **Público:** presidente da comissão (ou Gestor); auditor como leitor.
- **Objetivo:** emitir a ordem classificatória e saber explicá-la.
- **Pré-requisitos:** Etapas do marco consolidadas.
- **Assuntos:** o marco e seu universo; **(R5)** o **recorte** — um marco com lista reservada tem
  uma ordem por lista, navegada pela aba "Recorte: X", com três estados vazios distintos; a ordem
  calculada antes de emitir; como a nota combinada se forma; o desempate critério a critério e a
  proveniência de cada par; empate residual e posição compartilhada; participantes sem posição;
  emitir — **(R5)** em dois passos, "Emitir ordem" → "Confira antes de emitir" → "Emitir a ordem",
  com "Decisões de recurso que este ato executa" quando houver providência a cumprir; o ato como
  fotografia; obsolescência (regra mudou / universo mudou); ato sucessor. **(R5) A tela do marco**
  (`049`): a tabela "Recortes deste marco" com Ordem · Corte · Apuração · Publicação (Feito /
  Obsoleto / Falta / Não se aplica); "Conduzir o marco inteiro" oferece só os gestos que faltam,
  passa por uma conferência que não grava ("Serão praticados", "Ficam de fora", "Impedidos") e
  pratica o primeiro ato de cada recorte — suceder continua na tela do recorte, com motivo.
- **Telas:** Ordenação do marco; **(R5)** confirmação da emissão; Ato de classificação (posições +
  proveniência); ato obsoleto com divergências; **(R5)** tela do marco e sua conferência.
- **Screenshots:** SS-058, SS-059, SS-060, SS-061.
- **Exemplo:** 1º Ana 95 · 2º Bruno 88 · 3º Carla 82 · 4º Diego 75, com empate desfeito por fato
  declarado.
- **Alertas:** 🔎 quem foi eliminado em Etapa anterior à última **não aparece** entre "considerados
  sem posição" — essa história é contada pelos Resultados de Etapa. ⚠ emitir com a página velha é
  recusado. ⚠ **(R5)** "Ninguém concorreu por este recorte" ainda emite a ordem vazia — e é o certo.
- **NÃO entra:** divulgação; sorteio (C-17a); corte (C-17b).

### C-17a · Ordenar por sorteio público **(R5)**

- **Público:** presidência (ou Gestor); publicador para a classificação; público e candidato como
  leitores.
- **Objetivo:** produzir uma ordem por sorteio que qualquer pessoa consiga conferir sem pedir nada.
- **Pré-requisitos:** marco declarado "Por sorteio", com o método no Edital; inscrições encerradas.
- **Assuntos:** o método declarado no Edital (algoritmo, fonte da semente, ocorrência, derivação,
  normalização, substituição) e por que alterá-lo é Retificação; os três atos, recorte a recorte —
  **"Publicar e congelar a relação"** (recusado com inscrições em curso; pode partir das habilitadas
  numa Etapa), **"Observar a ocorrência na fonte"** (ninguém digita a semente; a ocorrência precisa
  ser posterior ao congelamento; "indisponível" fica registrado e aciona a substituição),
  **"Realizar o sorteio"** (um botão, sem prévia, que constitui o ato); publicar a classificação do
  sorteio; **anular** — Retificar declarando a ocorrência nova → relação nova com motivo → observar →
  "Anular e constituir o sucessor"; o lado público: relação de habilitados, "Verificar este
  sorteio", o manifesto e o verificador independente.
- **Telas:** Sorteio — marco; Relação de habilitados (pública); Verificar este sorteio (pública).
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** ⛔ realizar não tem prévia nem volta; anular **não** desfaz, constitui um sucessor.
  👤 **realizar o sorteio conta como emitir o ato de ordenação**: quem sorteia fica impedido de
  julgar recurso contra aquela ordem (§A.3). 🔎 a relação de habilitados é pública e nominal —
  é a única lista de Etapa que o público vê (§H.4).
- **NÃO entra:** o método do sorteio em detalhe matemático (vai para `G-05`); declarar o marco de
  sorteio (C-08).

### C-17b · Cortar: quem segue para a Etapa seguinte ou para as vagas **(R5)**

- **Público:** presidência (ou Gestor); auditor como leitor.
- **Objetivo:** emitir a faixa que o marco declara e saber o que ela faz e o que **não** faz.
- **Pré-requisitos:** ordem vigente no recorte; Regra de corte publicada no marco.
- **Assuntos:** o que o corte é — a faixa que progride, calculada da ordem e da regra (alvo fixo ou
  lido do quadro, suplentes, empate na última posição) — e o que ele não é: não elimina, não grava
  Resultado, não ocupa vaga; os dois usos — **marco intermediário** (a faixa alimenta a Etapa
  seguinte, que só recebe quem está nela; os demais aparecem "fora do corte") e **marco final** (a
  faixa é o universo da ocupação e da convocação); "A faixa calculada" e a tabela Progride / Fora
  da faixa; "Emitir corte"; nova geração com motivo; "Continuar corte" → "Emitir faixa seguinte",
  quando a regra admite continuação; o histórico do corte e a reprodução da faixa; o corte obsoleto.
- **Telas:** Corte e progressão; Corte — histórico.
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** ⛔ emitir corte não tem volta; corrigir é nova geração. ⚠ **corte obsoleto impede
  qualquer publicação** de resultado e trava a Etapa governada — refaça o corte antes de divulgar.
  💡 abrir a tela calcula e não grava nada.
- **NÃO entra:** ocupação (C-20a).

### C-18 · Divulgar o resultado

- **Público:** publicador; candidato e público como leitores.
- **Objetivo:** publicar um resultado preliminar ou definitivo e saber onde ele aparece depois.
- **Pré-requisitos:** ato de classificação vigente.
- **Assuntos:** a prévia e o que será divulgado; preliminar × definitiva; a revalidação na
  confirmação; a página pública estável; o documento oficial; a situação de cada participante na
  área do candidato; o histórico de publicações do marco; sucessão de publicação. **(R5)** As
  portas novas: o destino "divulgar o resultado" no card Classificação do Edital, "Publicar a
  classificação deste sorteio" e o gesto "Publicar o resultado do marco…" na tela do marco; a
  "Declaração de encerramento do prazo recursal" na definitiva sem janela computável; "Um
  resultado definitivo não é sucedido por um preliminar"; **um documento público por marco e por
  lista de concorrência** — não há documento único do marco. Do lado público: "Prazo de recurso
  aberto… até" / "encerrado em…" e "Publicações anteriores deste resultado (N)"; num marco de
  sorteio a coluna de pontuação some e entra "Esta ordem foi produzida por sorteio público".
- **Telas:** Prévia da publicação; Resultado divulgado (público, desktop e celular); Acompanhar
  (candidato); Resultados divulgados (histórico).
- **Screenshots:** SS-062 a SS-067 **(R5: mudam — §R5 do inventário)**.
- **Alertas:** ~~⚠ **quem emitiu o ato não é quem o publica.**~~ **(R5) Era impreciso:** são
  permissões diferentes, mas não há checagem de identidade entre emitir e publicar (§A.3) — a mesma
  pessoa, com as duas bases, pratica as duas. O que a regra protege é o julgador. ⚠ a prévia
  envelhece: se algo mudar entre abrir e confirmar, a confirmação é recusada — e isso é proteção,
  não erro. 🔎 nenhum candidato é notificado de resultado; a divulgação é passiva (§H.5 — o
  sistema avisa por e-mail outras coisas, não esta).
- **NÃO entra:** recursos.

### C-19 · Recursos — interpor, instruir, admitir e julgar

- **Público:** candidato (primeira metade), julgador (segunda metade); **(R5)** presidência ou
  Gestor para a instrução.
- **Objetivo:** o candidato recorre no prazo; o julgador admite e julga com efeito correto.
- **Pré-requisitos:** resultado divulgado. **(R5)** O Resultado de Etapa só fica visível ao
  candidato depois que existe uma publicação vigente de um marco que conta aquela Etapa — não logo
  após a consolidação; e o botão "Recorrer de um resultado" só aparece quando há algo recorrível
  dentro do prazo.
- **Assuntos:** o que pode ser atacado (a publicação, ou um Resultado de Etapa) — **(R5)** e o que
  não pode: a convocação e a relação de habilitados ao sorteio; a janela recursal; o protocolo do
  recurso; admissibilidade ≠ mérito; **(R5) as quatro espécies de decisão**, com os rótulos da tela
  — "Indeferir", "Deferir fixando a correção", "Deferir determinando reavaliação", "Deferir
  determinando providência a jusante" — e o efeito de cada uma; "Etapa alcançada pela decisão";
  impedimento do julgador; a proibição de agravar a situação de quem recorreu; onde o candidato
  acompanha. **(R5) A instrução do recurso** (`036`): não é o julgador quem instrui — é a
  presidência ou o Gestor, que junta à peça o parecer atacado e/ou o documento, com razão escrita
  ("Instruir o recurso"); o julgador lê o que foi instruído enquanto o recurso não é decidido, e o
  acesso acaba com a decisão; quem instrui não fica impedido de nada. A entrada do julgador é a
  ação "Recursos aguardando decisão (N)", que conta só os pendentes.
- **~~Tratamento da quarta espécie~~ — (R5) revogado.** A caixa "⛔ Não utilize" e a exclusão da
  espécie da tabela saem, porque o diagnóstico que as motivava não se confirmou (§H.2). *Deferir
  determinando reavaliação* entra na tabela de espécies como as outras, e o seu cumprimento é a
  receita `R-13`: distribuir a **outro** avaliador (a distribuição abre uma vaga extra), concluir na
  Mesa e consolidar pela seleção. O componente `Limitação conhecida desta versão` do §G.3 fica sem
  caso de uso no manual por ora — e continua definido, para o próximo.
- **Telas:** Acompanhar → Recorrer; Recurso (candidato); Recursos recebidos; peça do recurso
  (**(R5)** com "Conferir o que se contesta" e "Instrução do recurso"); Admissibilidade; Julgar.
- **Screenshots:** SS-068 a SS-074 **(R5: SS-071 muda; SS-073 perde a tarja "não utilizar")**.
- **Alertas:** ⚠ julgar é papel próprio: quem atuou no ato atacado está impedido — **(R5)**
  incluindo quem realizou o sorteio que constituiu a ordem atacada. ⚠ a espécie escolhida determina
  o efeito — indeferir não muda nada, corrigir cria um Resultado novo, reavaliar pede uma nova
  avaliação por outra pessoa, providência a jusante registra pendência que o próximo ato precisa
  citar. ⚠ **(R5)** depois da decisão de reavaliar, a peça diz "Nenhum — este recurso não produziu
  resultado sucessor" e não indica o próximo passo: o manual é quem indica (§H.2).
- **NÃO entra:** o refazimento do resultado (C-20).

### C-20 · Refazer e republicar depois de um recurso

- **Público:** presidente da comissão (ou Gestor) e publicador.
- **Objetivo:** cumprir uma decisão recursal até a nova divulgação.
- **Assuntos:** o Resultado sucessor citando o anterior e a decisão; o original permanece;
  reabilitação e progressão retroativa ("Reabilitada por recurso" na distribuição da Etapa
  seguinte); **(R5)** a reavaliação cumprida; **(R5)** a providência a jusante, citada em "Decisões
  de recurso que este ato executa" ao emitir o ato sucessor; a classificação fica obsoleta com o
  motivo certo; emitir o ato sucessor; **(R5)** o corte sucessor, quando a faixa ficou obsoleta; a
  publicação sucessora; a anterior continua consultável dizendo que foi sucedida; **(R5) os
  impedimentos da publicação**, que são mais que os cinco da definitiva:
  - barram qualquer natureza: marco removido por Retificação · ato sucedido · reingresso pendente ·
    corte obsoleto · ato desatualizado · prévia envelhecida;
  - barram só a definitiva: recurso pendente · reavaliação pendente · providência pendente · janela
    recursal ainda aberta · declaração de encerramento exigida (marco sem janela computável) ·
    declaração recusada (marco que tem janela);
  - e duas regras de forma: definitiva não é sucedida por preliminar; autoridade obrigatória.
- **Telas:** Resultados da Etapa depois dos recursos; ordenação obsoleta; ato sucessor; prévia da
  segunda publicação; publicação anterior preservada; recusa da definitiva — **(R5)** que hoje é
  anunciada antes da escolha ("Este marco ainda não pode ser publicado como definitivo").
- **Screenshots:** SS-075 a SS-080 **(R5: SS-079 muda)**.
- **Alertas:** ⚠ a publicação fica bloqueada — inclusive como preliminar — enquanto houver quem
  foi reabilitado e ainda não tem Resultado na Etapa seguinte. ⚠ **(R5)** um recurso deferido
  depois da convocação torna obsoletos a ordem, o corte e a apuração, e a convocação passa a ser
  recusada até a apuração seguinte.
- **NÃO entra:** o julgamento em si.

### C-20a · Apurar a ocupação das vagas **(R5)**

- **Público:** presidência (ou Gestor); auditor como leitor.
- **Objetivo:** saber, por recorte, quantas vagas existem, quantas estão ocupadas e quantas faltam.
- **Pré-requisitos:** ordem vigente no recorte e quadro de vagas publicado.
- **Assuntos:** os quatro números — publicadas, efetivas, ocupadas, a ocupar —, e os movimentos que
  os explicam (reversão de vaga reservada não preenchida para a ampla, quando o Edital declara);
  "Apurar a ocupação deste recorte"; a apuração obsoleta e "Emitir nova apuração" com motivo; o
  déficit e "Pedir a faixa seguinte com este déficit", que leva ao corte; o histórico do recorte.
- **Telas:** Ocupação de vagas; Histórico da ocupação.
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** ⛔ apurar não tem volta; corrigir é nova apuração com motivo. 🔎 apurar não seleciona
  ninguém: quem escolhe é o corte, quem chama é a convocação. ⚠ sem apuração emitida, a convocação
  é recusada.
- **NÃO entra:** convocar (C-20b).

### C-20b · Convocar, chamar de novo e suplência **(R5)**

- **Público:** presidência (ou Gestor); candidato para a parte do portal.
- **Objetivo:** chamar quem a faixa e a apuração indicam, comunicar, registrar o que cada pessoa
  respondeu e seguir a fila até as vagas fecharem.
- **Pré-requisitos:** apuração emitida no recorte; forma de convocação declarada no Perfil.
- **Assuntos:** as três espécies, **derivadas da posição** e não escolhidas — vaga inicial,
  suplência, para regularizar; "Convocar os titulares num ato só", com o vencimento do prazo
  (Evento do Cronograma ou data e hora) e o fundamento; a comunicação — **e-mail individual** quando
  o Perfil declara "mensagem individual", ou o registro de onde e quando a lista foi publicada,
  quando declara "por publicação" (o sistema registra a publicação, não a faz); "Comunicações que
  ainda não saíram"; "Chamar uma pessoa da fila"; os desfechos (aceite, regularização,
  indeferimento, desistência expressa, não atendimento, cancelamento por inércia, reclassificação);
  "Atestar fato externo" como insumo da inércia; "Registrar o não atendimento das N" vencidas;
  quando a fila esgota, a faixa seguinte; o histórico. Do lado do candidato: a tela "Convocação",
  com espécie, prazo e "O que fazer".
- **Telas:** Convocação; Histórico da convocação; Convocação (portal).
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** ⛔ convocar comunica no mesmo ato; desfecho e atestado não se desfazem. ⚠ falha de
  envio do e-mail não inicia o prazo. ⚠ **o portal não tem link para a tela de convocação** — o
  e-mail leva a "Minhas inscrições", e nem ela nem Acompanhar apontam a convocação (§H.18). Até a
  correção, o manual do candidato e a comunicação precisam dizer o caminho. 🕒 o resultado
  definitivo **não** é pré-condição de convocar; o momento é decisão institucional.
- **NÃO entra:** o Requerimento (C-20c); recurso contra a convocação, que não existe.

### C-20c · O Requerimento de Matrícula **(R5)**

- **Público:** candidato; presidência e Gestor como leitores.
- **Objetivo:** o candidato envia uma vez os dados de matrícula, no momento que o Edital declarou.
- **Pré-requisitos:** Edital que declara o Requerimento — "no ato da inscrição" (a inscrição só é
  enviada depois dele) ou "quando o candidato for convocado" (só com convocação em aberto).
- **Assuntos:** "O que já sabemos" e os links para corrigir na origem; os quatro estados ("Ainda não
  é a hora", "O que falta você informar", "Enviado", não se aplica); o CEP que preenche município e
  UF; a declaração de veracidade; "Guardar e continuar depois" × "Enviar requerimento"; "Conferir e
  atualizar" quando reconvocado, que cria um sucessor; o requerimento anterior consultável.
- **Telas:** Requerimento de Matrícula (portal); Requerimento anterior; o bloco na inscrição
  recebida (gestão).
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** ⛔ enviado não muda; atualizar só com convocação em aberto, e cria um sucessor.
  ⚠ quando pedido na convocação, **nenhuma tela do portal leva ao requerimento** (§H.18).
  💡 sem a base de CEP carregada, o candidato digita o endereço inteiro e o envio conclui.
- **NÃO entra:** a matrícula em si — o sistema não matricula ninguém.

### C-20d · Exportar para matrícula **(R5)**

- **Público:** Exportador de matrículas.
- **Objetivo:** gerar o arquivo que o Registro Acadêmico importa, com a população certa.
- **Pré-requisitos:** papel de Exportador; Edital publicado que declara o Requerimento.
- **Assuntos:** "Quem entra no arquivo" — os convocados de um marco, ou um resultado definitivo
  divulgado e não sucedido; quem não enviou Requerimento é nomeado, e a geração é recusada; "Ver o
  que sairá vazio"; "Baixar o arquivo" (`.xlsx`); a norma de cada pessoa é a do ato que a alcançou,
  não a vigente; o arquivo não é guardado, e a geração fica registrada sem dado de candidato.
- **Telas:** Exportar para matrícula.
- **Screenshots:** novas (`01-…`, §R5).
- **Alertas:** ⚠ o arquivo reúne CPF, RG, filiação e endereço da população inteira — guarde e
  descarte conforme a política de dados da instituição. 🔎 baixar de novo gera outra geração
  registrada.
- **NÃO entra:** a importação no sistema acadêmico, que é fora do sistema.

### C-21 · Encerrar o certame

- **Público:** gestor.
- **Objetivo:** fechar Edital e Processo com o registro correto.
- **Assuntos:** encerrar × cancelar; o motivo; o que permanece consultável; quando encerrar em
  relação ao resultado definitivo e à convocação (**o sistema não orienta — §H.7**); **(R5)** o
  Processo só encerra com **todos os Editais encerrados ou cancelados** — a tela lista os pendentes
  em "O encerramento e o cancelamento do Processo estão impedidos"; o desfecho que a página pública
  da seleção passa a mostrar.
- **Telas:** confirmação de encerramento; detalhe encerrado.
- **Screenshots:** SS-081, SS-082.
- **Alertas:** ⚠ depois de encerrado nenhuma Retificação pode ser publicada.
  ⚠ cancelar registra interrupção administrativa — não é a mesma coisa. 🔎 **(R5)** cancelar o
  Edital não gera Publicação.
- **NÃO entra:** nomeação e posse — não existem (§H.7). ~~convocação~~ **(R5)** a convocação existe
  e tem capítulo (C-20b).

### C-21a · Retificar um Edital publicado **(R5)**

- **Público:** elaborador, homologador e publicador — o mesmo trio do C-10.
- **Objetivo:** corrigir ou acrescentar a um Edital publicado sem reescrevê-lo.
- **Pré-requisitos:** Edital publicado e não encerrado.
- **Assuntos:** o que a Retificação pode mudar e o que não pode — cada campo tem natureza própria
  (`026`), e a Revisão do Edital já mostrou "O que não se corrige depois de publicado"; o que ela
  pode **acrescentar** (`048`): Perfil, Modalidade, linha do quadro, critério de desempate, Evento e
  Anexo, com "aplicar a todos" na conferência; o que ela pode fazer nascer (janela recursal, regra de
  corte, reversão de vaga); o que não acrescenta (Documento Exigido, Seção); "O que vai mudar" em
  português; vigência, inclusive futura; o mesmo ciclo submeter → homologar → publicar; o que o
  candidato com rascunho aberto vê ("O Edital foi atualizado"); a Retificação exigida para anular um
  sorteio.
- **Telas:** Retificar; Detalhe da Retificação.
- **Screenshots:** SS-083, SS-084 **(R5: SS-083 muda)**, mais as de acrescentar.
- **Alertas:** ⛔ publicar a Retificação não tem volta. ⚠ ato histórico continua lendo a norma que
  citou — uma Retificação não muda o que já foi emitido.
- **NÃO entra:** o detalhe de cada campo retificável (vai para `G-01`).

### C-22 · A Visão Geral da instituição **(R5)**

- **Público:** gestor; quem decide processo institucional.
- **Objetivo:** ler o conjunto dos Processos da instituição sem abrir um por um.
- **Pré-requisitos:** papel de Gestor.
- **Assuntos:** o que a Visão Geral mostra (`040`–`042`) e, principalmente, o que ela declara que
  **não mede** — matrícula efetivada, classificados, convocados, ocupação, requerimentos, divisão por
  campus, tipo de Processo e ano de ingresso.
- **Telas:** Visão Geral.
- **Screenshots:** nova (`01-…`, §R5).
- **Alertas:** 🔎 é leitura: nada nela pratica ato.
- **NÃO entra:** a supervisão de um Processo (C-11a).

### G-03 · O que o sistema não faz hoje

Ficha própria porque esta seção passou a carregar peso editorial: ela é o **destino único** das
limitações que não interrompem nenhuma tarefa (§H.0).

- **Público:** gestor e quem decide processo institucional; secundariamente, quem responde dúvida
  de candidato.
- **Objetivo:** que ninguém procure por horas uma função que não existe, e que a instituição saiba
  o que precisa resolver por fora do sistema.
- **Pré-requisitos:** nenhum; é seção de referência, alcançável do menu e por remissão.
- **Assuntos (R5, revistos):** consulta pública do conteúdo vigente numa data passada (§H.3,
  estreitada); Resultado de Etapa não público, salvo a relação do sorteio (§H.4); avisos por
  e-mail só em quatro situações — código, confirmação da inscrição, mudança de credencial e
  convocação por mensagem individual —, nunca de resultado, Retificação ou prazo (§H.5); efetivar a
  matrícula, nomeação e posse, validade e prorrogação do Edital, recurso contra a convocação (§H.7);
  a mesma Etapa com peso único em todos os marcos (§H.13); a prova de reprodutibilidade do ato de
  classificação sem tela e o cancelamento de Evento só pela API (§H.14); prazos só em dias corridos;
  sem carga retroativa de Edital com inscrições encerradas; importação de notas e prova objetiva,
  heteroidentificação como fluxo e segunda instância recursal fora do sistema; cancelamento do
  Edital sem Publicação. **Saíram** (fechadas): corte e progressão, o ciclo terminar na divulgação,
  o segundo Edital sem tela, e a caixa da reavaliação.
- **Telas:** nenhuma.
- **Screenshots:** nenhum.
- **Alertas:** nenhum. Esta seção **é** o alerta.
- **Forma:** uma lista de fatos em linguagem neutra, cada um com uma frase de "o que fazer no
  lugar" quando houver alternativa institucional (avisar candidatos por outro canal, publicar o
  intermediário fora do sistema). Sem tom de desculpa e sem prometer data.
- **NÃO entra:** defeitos de UX que o manual já mitiga, distinções que são conteúdo e não falta
  (§H.12), nada sobre o repositório ou sobre specs, e nenhum item que já tenha alerta inline no
  capítulo da tarefa — nesse caso `G-03` apenas o repete em uma linha, para quem chegou por aqui.

---

## D. Mapa papel × capítulo

Legenda: ● capítulo obrigatório · ○ leitura recomendada · — não se aplica.

> **Numa equipe pequena, leia pela coluna, não pela linha.** Uma pessoa que acumula elaborador,
> publicador e presidência lê a **união** das três colunas — e é para isso que os capítulos são
> curtos e as trilhas da Parte 3 são páginas de roteamento (§A.3).

**(R5)** Coluna nova para o Exportador; linhas novas para os capítulos com sufixo. A coluna do
Gestor sobe em C-14 a C-17b e C-20 a C-20b porque ele alcança esses atos (§A.1) — e lê-los é
também o que o permite **não** praticá-los quando for o julgador.

| Capítulo | Gestor | Elabor. | Homol. | Public. | Presid. | Avaliad. | Julgad. | Export. | Candid. | Auditor |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| C-01 O que o sistema faz | ● | ● | ● | ● | ● | ● | ● | ● | ○ | ● |
| C-02 As duas portas | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| C-03 O ciclo em um mapa | ● | ● | ● | ● | ● | ○ | ○ | ○ | ○ | ● |
| C-04 Quem faz o quê | ● | ● | ● | ● | ● | ○ | ● | ● | — | ● |
| C-05 Seis ideias | ● | ● | ● | ● | ● | ○ | ● | ○ | ○ | ● |
| C-06 Abrir o Processo | ● | ○ | — | — | ○ | — | — | — | — | ○ |
| C-07 Elaborar I | ○ | ● | ● | ○ | — | — | — | — | — | ○ |
| C-08 Elaborar II | ○ | ● | ● | ○ | ● | ○ | ○ | — | — | ○ |
| C-09 Elaborar III | ○ | ● | ● | ○ | — | — | — | ○ | — | ○ |
| C-10 Submeter/homologar/publicar | ● | ● | ● | ● | — | — | — | — | — | ● |
| C-11 Inscrições por dentro | ● | — | — | — | ○ | — | — | — | — | ○ |
| C-11a Acompanhar o certame | ● | — | — | ○ | ● | — | — | — | — | ○ |
| C-12 Inscrever-se | ○ | ○ | — | — | — | — | — | — | ● | — |
| C-13 Comissão e alocação | ● | — | — | — | ● | ○ | — | — | — | ○ |
| C-14 Distribuir | ● | — | — | — | ● | ○ | — | — | — | ○ |
| C-15 Avaliar | — | — | — | — | ● | ● | ○ | — | — | ○ |
| C-16 Consolidar | ● | — | — | — | ● | ○ | ○ | — | — | ● |
| C-17 Classificar | ● | ○ | — | ○ | ● | — | ● | — | — | ● |
| C-17a Sorteio | ● | ○ | — | ● | ● | — | ● | — | ○ | ● |
| C-17b Corte | ● | ○ | — | ○ | ● | — | ○ | — | — | ● |
| C-18 Divulgar | ○ | — | — | ● | ● | — | ○ | — | ○ | ● |
| C-19 Recursos | ○ | — | — | ○ | ● | — | ● | — | ● | ● |
| C-20 Refazer e republicar | ● | — | — | ● | ● | ○ | ● | — | ○ | ● |
| C-20a Ocupação | ● | — | — | — | ● | — | — | ○ | — | ○ |
| C-20b Convocação | ● | — | — | — | ● | — | — | ○ | ● | ○ |
| C-20c Requerimento de Matrícula | ○ | ○ | — | — | ○ | — | — | ● | ● | — |
| C-20d Exportar para matrícula | ○ | — | — | — | — | — | — | ● | — | ○ |
| C-21 Encerrar | ● | — | — | ○ | — | — | — | — | — | ○ |
| C-21a Retificar | ● | ● | ● | ● | ○ | — | — | — | ○ | ○ |
| C-22 Visão Geral | ● | — | — | — | — | — | — | — | — | — |

---

## E. Conceitos que precisam ser ensinados

**Momento de ensino:** `INÍCIO` = Parte 1, antes de qualquer tarefa · `USO` = no capítulo onde
aparece pela primeira vez · `SAIBA MAIS` = caixa lateral, não bloqueia a leitura.

| Conceito | Como dizer ao leitor | Quando |
|---|---|---|
| **Processo Seletivo** | O certame inteiro. Guarda um ou mais Editais — **(R5)** acrescentáveis pela tela — e a comissão | INÍCIO |
| **Edital** | O documento normativo que rege a seleção. Nasce em elaboração e termina publicado | INÍCIO |
| **Publicação** | O ato que torna o Edital público e **imutável**. Não se reescreve | INÍCIO |
| **Retificação** | A correção de um Edital já publicado, com aprovação própria e data de vigência | INÍCIO |
| **Versão vigente / versão histórica** | O que vale hoje × o que valia numa data | INÍCIO |
| **Segregação de funções** | **(R5, corrigido)** Uma pessoa pode fazer dois dos três atos — elaborar, homologar, publicar —, mas não os três na mesma revisão; e quem tocou o resultado atacado não julga o recurso contra ele | INÍCIO |
| **Perfil de Vaga** | Cada cargo/função ofertado, com seus requisitos e vagas | USO (C-07) |
| **Modalidade** | Como se concorre dentro do perfil: PPI, PcD… **(R5)** A ampla concorrência **não** é uma Modalidade a declarar: é a linha geral do quadro | USO (C-07) |
| **Cadastro de reserva** | Vagas além das imediatas | USO (C-07) |
| **Cronograma / Evento** | As datas do certame; um Evento é o período de inscrições — **(R5)** escolhido no passo Inscrição —, e Eventos também datam o sorteio e o vencimento da convocação | USO (C-07) |
| **Etapa de Avaliação** | Cada fase de análise; tem forma, peso e Evento próprios | USO (C-08) |
| **Forma pontuada** | A Etapa produz nota numa faixa, com nota mínima opcional | USO (C-08) |
| **Forma decisória** | A Etapa produz um de dois rótulos escolhidos pelo Edital | USO (C-08) |
| **Marco Classificatório** | Onde as Etapas se combinam numa ordem | USO (C-08) |
| **Critério de desempate** | A regra que separa quem empatou, e o que ela compara | USO (C-08) |
| **Fato declarado** | Dado exigido do candidato e usado no desempate; congela no envio | USO (C-08) |
| **Janela recursal** | O prazo de recurso que o marco declara | USO (C-08) |
| **Documento exigido** | O que o candidato precisa anexar; pode variar por modalidade | USO (C-09) |
| **Anexo do Edital** | Arquivo que o Edital fornece — modelos, formulários | USO (C-09) |
| **Revisão** | O conteúdo congelado na submissão, que será homologado | USO (C-10) |
| **Fundamento / motivo** | O texto que justifica um ato e fica registrado | USO (C-10) |
| **Autoridade signatária** | Quem responde pelo ato, registrada no documento — **(R5)** não é assinatura digital | USO (C-10) |
| **Documento publicado** | O PDF gerado na publicação — **(R5)** é o Edital oficial, não uma cópia dele, e não se regenera | USO (C-10) |
| **Rascunho de inscrição** | Começada e não enviada. Ninguém a recebeu | USO (C-11/C-12) |
| **Protocolo** | O identificador legível da inscrição e do recurso | USO (C-12) |
| **Comissão / presidente / membro** | Quem avalia, e quem organiza quem avalia | USO (C-13) |
| **Alocação por Etapa** | Quem pode atuar em qual Etapa | USO (C-13) |
| **Distribuição / Atribuição** | Quem responde por qual inscrição naquela Etapa | USO (C-14) |
| **Rodízio** | A proposta automática que equilibra a carga | USO (C-14) |
| **Impedimento** | O registro de que alguém não pode atuar num caso | USO (C-14) |
| **Avaliação concluída** | O que você afirmou, e que não muda mais sem a presidência | USO (C-15) |
| **Ocorrência** | O desfecho de quem não pôde ser avaliado. Elimina | USO (C-16) |
| **Resultado da Etapa** | Habilitada ou Eliminada, oficialmente, naquela Etapa | USO (C-16) |
| **Consolidação** | O ato que transforma avaliações em Resultados | USO (C-16) |
| **Conclusão preservada** | O que alguém havia concluído antes de uma reabertura | SAIBA MAIS (C-16) |
| **Universo do ato** | Quem entra na conta da classificação | USO (C-17) |
| **Ato de classificação** | A ordem emitida, congelada no instante da emissão | USO (C-17) |
| **Ato obsoleto** | O ato cuja base mudou depois dele | USO (C-17) |
| **Ato sucessor** | O novo ato que substitui um obsoleto, com motivo | USO (C-17) |
| **Publicação preliminar / definitiva** | Sujeita a recurso × final | USO (C-18) |
| **Sucessão de publicação** | A nova publicação substitui a anterior, que continua legível | USO (C-18) |
| **Recurso / admissibilidade / mérito** | Contestar; ser recebido; ser decidido | USO (C-19) |
| **Espécies de decisão** | Indeferir · corrigir · determinar reavaliação · providência — **(R5)** as quatro ensinadas | USO (C-19) |
| **Não agravar quem recorreu** | O recurso nunca piora a situação de quem o interpôs | USO (C-19) |
| **Resultado sucessor** | O Resultado corrigido, que nasce ao lado do original | USO (C-20) |
| **Trilha de auditoria** | O registro de quem fez o quê, quando e por quê | SAIBA MAIS (C-05), capítulo em G |
| **Acesso sem senha** | Entrar por código enviado ao e-mail | USO (C-12) |
| **Vincular participação anterior** | Reunir inscrições feitas com outro e-mail | SAIBA MAIS (C-12) |
| **(R5) Recorte / lista de concorrência** | A lista em que a pessoa concorre dentro do Perfil: a geral (ampla) ou uma reservada. Cada uma tem sua ordem, corte, apuração e convocação | USO (C-07) |
| **(R5) Quadro de vagas** | Quantas vagas cada lista tem, conferido contra as vagas imediatas | USO (C-07) |
| **(R5) Duplicar / aplicar a todos / partir de um anterior** | Copiar um valor, sem vínculo com a origem | USO (C-06, C-07) |
| **(R5) Pendência que impede** | O que a Revisão recusa porque o certame não teria como ser conduzido | USO (C-09) |
| **(R5) Lista exigida** | Os documentos pedidos àquela inscrição, que congelam no envio | USO (C-11, C-12) |
| **(R5) Origem da ordem** | Calculada pela pontuação ou produzida por sorteio | USO (C-08) |
| **(R5) Sorteio: relação, ocorrência, semente, verificação** | A ordem vem de uma fonte pública sobre uma lista congelada, e qualquer um a confere | USO (C-17a) |
| **(R5) Corte / faixa / geração** | Quem segue adiante; não elimina nem ocupa vaga; corrigir é nova geração | USO (C-17b) |
| **(R5) Apuração de ocupação** | Publicadas, efetivas, ocupadas, a ocupar | USO (C-20a) |
| **(R5) Convocação: espécie, vencimento, desfecho** | Por que a pessoa foi chamada, até quando, e o que ela respondeu | USO (C-20b) |
| **(R5) Atestado de fato externo** | O registro de algo que aconteceu fora do sistema | SAIBA MAIS (C-20b) |
| **(R5) Requerimento de Matrícula** | Dados de matrícula pedidos uma vez; o enviado não muda | USO (C-09, C-20c) |
| **(R5) Instrução do recurso** | Juntar à peça o que o julgador precisa ler; não dá acesso permanente a ninguém | USO (C-19) |
| **(R5) Natureza não regride** | Um resultado definitivo não é sucedido por um preliminar | SAIBA MAIS (C-18) |
| **(R5) Ativação derivada** | Publicar o primeiro Edital ativa o Processo | SAIBA MAIS (C-06) |
| **(R5) Pulso, Atenção, Visão Geral** | Leituras da condução; não praticam nada | SAIBA MAIS (C-11a, C-22) |
| **(R5) Recusa explicada** | A tela diz qual permissão serviria e a quem pedir | INÍCIO (C-04) |

**Conceitos que NÃO entram no manual** (existem no sistema e não são do usuário): identificadores
técnicos e UUIDs, versão de esquema do conteúdo, resumo criptográfico, controle otimista de
concorrência, chave de idempotência, comando, papel de banco, registro append-only, gatilho,
escopo institucional como campo, nomes de módulos, classes e funções. O resumo criptográfico e o
identificador aparecem **na tela** em algumas superfícies de auditoria — o manual os chama de
"detalhe técnico do registro" e não os explica além disso, exceto em `G-05`.

---

## F. Inventário de screenshots

### F.1 O certame-exemplo — um só, do começo ao fim

Todas as capturas saem do **mesmo** certame fictício, para que o leitor reconheça os nomes de
capítulo em capítulo:

> **Processo Seletivo Simplificado 2026** · **Edital 03/2026 — Auxiliar de Biblioteca**
> Perfil único, 2 vagas + cadastro de reserva, modalidades *Ampla concorrência* e *PPI*.
> Etapa 1 — *Análise de requisitos* (decisória, Deferida/Indeferida).
> Etapa 2 — *Avaliação de títulos* (pontuada, 0–100, mínima 60, peso 2).
> Marco *Resultado final*, três critérios de desempate, **recurso em 5 dias corridos**.
> Candidatos: Ana, Bruno, Carla, Diego, Elisa, Helena (+ Hugo, rascunho nunca enviado).
> Atores: Gustavo (gestor), Elena (elaboradora), Wagner (homologador), Paula (publicadora),
> Paulo (presidente), Alice e Otávio (avaliadores), Júlia (julgadora), Aurora (auditora).

**Preparação:** banco limpo. **(S-00, corrige e amplia)** `seed_demo` **não produz este certame em
nenhuma parte**: cria dois perfis que não são o Auxiliar de Biblioteca, três Etapas com outra faixa
de pontuação, e um elenco cujos primeiros nomes **colidem** com os dos candidatos
(`ana.elaboradora` e a candidata Ana; `bruno.homologador` e o candidato Bruno). Num manual que
ensina segregação de funções mostrando que são pessoas diferentes, isso é justamente o que não pode
acontecer. O certame é montado **à mão, pela interface**, com o seletor de identidade digitando os
nomes do elenco — o piloto percorreu a cadeia completa (Elena submete, Wagner homologa, Paula
publica) e confirmou que ela é percorrível sem atalho. De `seed_demo` continua útil o
`--dias-atras`, único jeito de obter no navegador uma janela recursal **já encerrada**. Ele também
**não cria recursos**. As capturas das fases 6 a 15 exigem execução manual pelo navegador, como
as auditorias E2E fizeram. Ver §I.

> ⚠ **Este inventário é provisório até o piloto (S-00).** Ele foi montado a partir das telas, e não
> a partir de páginas diagramadas. O piloto pode mostrar que uma captura carrega informação demais,
> que duas deveriam ser uma, que falta uma tela intermediária, ou que o enquadramento certo é um
> recorte e não a tela inteira. **Revisar este inventário é a última tarefa de S-00**, e só então
> ele autoriza as sessões de coleta.

### F.2 Convenções

- **Estado necessário** descreve o que precisa existir **antes** da captura.
- **Destaque** é anotação a ser aplicada depois (§G.6), não algo a fotografar.
- **(S-00, corrige)** Toda captura de desktop é tirada com viewport de **1 000 px** — não 1 280 —,
  salvo quando marcada `mobile 375`. A 1 280 px a gestão abre calhas laterais vazias que sobram no
  recorte. Enquadramento, anotação, resolução e as demais regras estão em
  `doc/manual/01-inventario-de-capturas-revisado.md`, §1.
- Nenhum dado pessoal real. Nenhum e-mail real. Nenhum CPF válido.

### F.3 O inventário

| ID | Ator | Tela | Estado necessário | O que precisa estar visível | Destacar depois | Capítulo |
|---|---|---|---|---|---|---|
| SS-001 | — | Vitrine pública | 2 seleções publicadas, 1 aberta | Cartões com vaga, prazo e "faltam N dias" | O cartão aberto | C-01 |
| SS-002 | — | Vitrine pública | idem | Cabeçalho e ausência de qualquer menu de gestão | Endereço `/selecoes/` | C-02 |
| SS-003 | Gestor | Processos Seletivos (lista) | 1 processo ativo | Lista e situação | Endereço `/gestao/` | C-02 |
| SS-004 | Elaboradora | Recusa por permissão ao tentar homologar | Edital em revisão | Mensagem nominal de recusa | A frase da recusa | C-04 |
| SS-005 | Publicador | Detalhe do Edital, cartão "O que fazer agora" | Mesma pessoa elaborou e homologou | Ação *Publicar* desabilitada **com o motivo ao lado** | Motivo | C-04 |
| SS-006 | Gestor | Detalhe do Edital publicado | 1 publicação + 1 retificação publicada | "Documentos publicados" e "Quem atuou" | Lista de documentos | C-05 |
| SS-007 | Auditora | Ato de classificação sucedido | Ato 1 sucedido pelo ato 2 | O aviso de sucessão **acima** dos valores | O aviso | C-05 |
| SS-008 | Gestor | Novo Processo | — | Formulário com código institucional | Campo do código | C-06 |
| SS-009 | Gestor | Detalhe do Processo | Processo ativo, 1 Edital | Trilha do Processo e lista de Editais | Trilha | C-06 |
| SS-011 | Elaboradora | Assistente — barra dos 9 passos | Edital novo | Os nove passos e seus três estados | A barra inteira | C-07 |
| SS-012 | Elaboradora | Passo Identificação | Edital novo | Título e descrição | — | C-07 |
| SS-013 | Elaboradora | Passo Perfis de Vaga | 1 perfil, 2 modalidades, 2 fatos | Vagas imediatas, cadastro reserva, modalidades | Bloco de modalidades | C-07 |
| SS-014 | Elaboradora | Passo Cronograma | 5 eventos, 1 é o período de inscrições | A marcação de "período de inscrições" | Essa marcação | C-07 |
| SS-015 | Elaboradora | Passo Etapas — Etapa decisória | Etapa 1 com rótulos preenchidos | Seletor de forma e os dois rótulos | Forma + rótulos | C-08 |
| SS-016 | Elaboradora | Passo Etapas — Etapa pontuada | Etapa 2, faixa 0–100, mínima 60, peso 2 | Faixa, nota mínima e peso | Nota mínima e peso | C-08 |
| SS-017 | Elaboradora | Passo Classificação — marco | Marco enumerando as 2 Etapas | Etapas enumeradas, normalização, arredondamento | Etapas enumeradas | C-08 |
| SS-018 | Elaboradora | Passo Classificação — critérios + janela | 3 critérios com alvo; janela de 5 dias | Cada critério dizendo **o que compara**; a janela | A janela recursal | C-08 |
| SS-019 | Elaboradora | Passo Inscrição | 3 documentos, 1 só para PPI, 1 com modelo | Aplicabilidade por modalidade e o vínculo do modelo | O vínculo do modelo | C-09 |
| SS-020 | Elaboradora | Passo Anexos | 2 anexos com rótulo e arquivo | Cartão "Anexo 1 de 2", rótulo e ações | Rótulo editorial | C-09 |
| SS-021 | Elaboradora | Passo Conteúdo | Seções preenchidas | Lista de seções textuais | — | C-09 |
| SS-022 | Elaboradora | Passo Revisão | 1 pendência impeditiva pendente | "O que falta para submeter" com link | A pendência | C-09 |
| SS-023 | Elaboradora | Prévia do Edital | Composição completa | Documento montado antes de publicar | Aviso de que é prévia | C-09 |
| SS-024 | Elaboradora | Confirmação de submissão | Sem pendências | As consequências listadas | Lista de consequências | C-10 |
| SS-025 | Elaboradora | Detalhe do Edital em revisão | Submetido | Trilha com "Em revisão" em destaque | Trilha | C-10 |
| SS-026 | Homologador | Confirmação de homologação | Edital em revisão | Campo *Fundamento da homologação* | O campo | C-10 |
| SS-027 | Homologador | Confirmação de devolução | Edital em revisão | Campo *Motivo da devolução* | O campo | C-10 / X-01 |
| SS-028 | Publicadora | Confirmação de publicação | Edital homologado | Autoridade signatária + 4 consequências | "torna-se público e imutável" | C-10 |
| SS-029 | Publicadora | Detalhe do Edital publicado | Publicado | "Quem atuou" com as três pessoas | As três linhas | C-10 |
| SS-030 | Gestor | Inscrições recebidas | 6 enviadas + 1 rascunho | Contador e a seção "Em preenchimento" | A separação entre os dois | C-11 |
| SS-031 | Gestor | Detalhe da inscrição recebida | 1 inscrição com 3 documentos | Dados e documentos apresentados | — | C-11 |
| SS-032 | — | Página da seleção | Edital publicado, inscrições abertas | PDF, anexos, perfis, "faltam N dias" | "Ler o Edital completo (PDF)" | C-12 |
| SS-033 | — | Página da seleção — documentos anunciados aberto | idem | A lista do que será pedido | A lista | C-12 |
| SS-034 | Candidata | Entrar (e-mail) | — | Campo de e-mail e *Receber código* | — | C-12 |
| SS-035 | Candidata | Informe o código | Código enviado | Campo do código e reenvio | — | C-12 |
| SS-036 | Candidata | Sua inscrição — escolha da modalidade | Inscrição aberta | Modalidades e o aviso de documento extra do PPI | O documento que aparece com o PPI | C-12 |
| SS-037 | Candidata | Sua inscrição — documentos | 2 de 3 enviados | Cartão do requisito com **modelo oficial** e o arquivo enviado | O modelo oficial | C-12 |
| SS-038 | Candidata | Revisar e enviar — fatos exigidos | Tudo preenchido | Os fatos e o aviso de congelamento | O aviso de congelamento | C-12 |
| SS-039 | Candidata | Comprovante | Inscrição enviada | Protocolo e documentos apresentados | Protocolo | C-12 |
| SS-040 | Candidato | Revisão com o aviso de Edital atualizado | Retificação publicada com rascunho aberto | "Li as alterações e quero continuar" | O gate | C-12 / R-01 |
| SS-041 | Candidata | Minhas inscrições | 1 enviada + 1 rascunho | As duas situações lado a lado | "Continuar inscrição" | C-12 |
| SS-042 | Candidata | Acesso à conta | 2 e-mails, 1 principal | Lista e ações | — | C-12 / R-07 |
| SS-043 | Gestor | Comissão do Processo | Presidente + 2 membros | Funções e "Adicionar vários de uma vez" | A coluna de função | C-13 |
| SS-044 | Gestor | Comissão — confirmação | Lista pronta para gravar | "Conferir a lista" | — | C-13 |
| SS-045 | Gestor | Alocação por Etapa | Matriz com 2 Etapas | A matriz marcada | Uma célula marcada | C-13 |
| SS-046 | Presidente | Distribuição — antes | Inscrições recebidas, ninguém distribuído | "Quem está alocado" e *Propor distribuição* | O botão | C-14 |
| SS-047 | Presidente | Distribuição — proposta por rodízio | Proposta na tela, ainda não gravada | A carga por avaliador | A carga | C-14 |
| SS-048 | Presidente | Distribuição confirmada | Gravada | Atribuições por avaliador | — | C-14 |
| SS-049 | Presidente | Impedimentos | 1 impedimento a registrar | Campo de motivo e "Registrar mesmo assim" | O motivo | C-14 / X-05 |
| SS-050 | Avaliadora | Minhas Etapas | 2 Etapas atribuídas | As Etapas e a contagem | — | C-15 |
| SS-051 | Avaliadora | Minha Mesa | 3 inscrições, 1 concluída | Situação por inscrição | A que está concluída | C-15 |
| SS-052 | Avaliadora | Inscrição na Mesa — decisória | Documentos disponíveis | Os dois rótulos do Edital + parecer | Os rótulos | C-15 |
| SS-053 | Avaliadora | Inscrição na Mesa — pontuada | idem | Campo de nota com a faixa | A faixa | C-15 |
| SS-054 | Presidente | Registrar ocorrência — revisão | 1 inscrição sem avaliação | O passo de revisão e "Registrar mesmo assim" | O aviso de que elimina | C-16 / X-04 |
| SS-055 | Presidente | Prontidão antes de consolidar | Avaliações concluídas | O que está pronto × o que falta | A distinção | C-16 |
| SS-056 | Presidente | Resultados da Etapa | Etapa consolidada | Habilitada/Eliminada por inscrição, com origem | A coluna de origem | C-16 |
| SS-057 | Presidente | Conclusões preservadas | 1 avaliação reaberta | O histórico e a ação *Reabrir* | *Reabrir* | C-16 / R-04 |
| SS-058 | Presidente | Ordenação do marco — antes de emitir | 2 Etapas consolidadas | Ordem calculada com nota combinada | *Emitir ordem* | C-17 |
| SS-059 | Presidente | Ordenação — desempate e sem posição | Empate presente | Coluna de desempate + "considerados sem posição" | O par empatado | C-17 / X-06 |
| SS-060 | Auditora | Ato de classificação | Ato emitido | Posições, valores de desempate e proveniência | A proveniência | C-17 |
| SS-061 | Presidente | Ato obsoleto | Retificação mudou o peso | "Pontuação no ato" × "Pontuação agora" | As duas colunas | C-17 / X-07 |
| SS-062 | Publicadora | Prévia da publicação | Ato vigente | "O que será divulgado" e natureza | Preliminar × definitiva | C-18 |
| SS-063 | Publicadora | Prévia recusada por envelhecimento | Ato mudou depois de abrir a prévia | A recusa e o motivo | A recusa | C-18 |
| SS-064 | — | Resultado divulgado (público) | Publicação preliminar | Ordem, natureza, data e PDF | Natureza | C-18 |
| SS-065 | — | Resultado divulgado — `mobile 375` | idem | Sem rolagem horizontal | — | C-18 |
| SS-066 | Candidata | Acompanhar | Resultado divulgado | "Sua participação", "Resultado das etapas", "Resultado divulgado" | Os três blocos | C-18 |
| SS-067 | Publicadora | Resultados divulgados (histórico do marco) | 2 publicações | P1 sucedida, P2 vigente | O sinal de sucessão | C-18 / C-20 |
| SS-068 | Candidata | Recorrer — escolha do objeto | Janela aberta | Os objetos atacáveis e o prazo | O prazo | C-19 |
| SS-069 | Candidata | Recurso interposto | Recurso criado | Protocolo do recurso | Protocolo | C-19 |
| SS-070 | Julgadora | Recursos recebidos | 4 recursos | Lista com situação de cada um | A coluna de situação | C-19 |
| SS-071 | Julgadora | Peça do recurso | 1 recurso admissível | Fundamentação e o objeto atacado | O objeto atacado | C-19 |
| SS-072 | Julgadora | Admissibilidade | idem | *Admitir* / *Não admitir* com motivo | — | C-19 |
| SS-073 | Julgadora | Julgar — o seletor de espécie | Recurso admitido | O seletor como ele é, com as quatro opções | **As três utilizáveis**; a quarta recebe tarja de "não utilizar" | C-19 |
| SS-074 | Julgadora | Julgamento recusado por agravamento | Correção que piora quem recorreu | A recusa integral | A frase da recusa | C-19 / X-10 |
| SS-075 | Presidente | Resultados da Etapa após recursos | 1 corrigido, 1 reabilitado | O sucessor citando o anterior e a decisão | A citação | C-20 |
| SS-076 | Presidente | Mesa reaberta por reabilitação | Reabilitada na Etapa seguinte | A inscrição de volta como "Não iniciada" | A linha | C-20 |
| SS-077 | Presidente | Ordenação obsoleta por recurso | Resultado superado | O motivo nomeando o recurso | O motivo | C-20 |
| SS-078 | Publicadora | Publicação bloqueada por reingresso | Reabilitada sem Resultado na Etapa seguinte | A recusa nominal | A recusa | C-20 |
| SS-079 | Publicadora | Definitiva recusada | Janela ainda aberta | A recusa com a data de encerramento | A data | C-20 / X-08 |
| SS-080 | — | Publicação anterior preservada | P1 sucedida por P2 | P1 com os valores antigos e o aviso | O aviso | C-20 |
| SS-081 | Gestor | Confirmação de encerramento do Edital | Edital publicado | Motivo e as três consequências | "Nenhuma Retificação poderá ser publicada" | C-21 |
| SS-082 | Gestor | Detalhe do Edital encerrado | Encerrado | Trilha com "Encerrado" | Trilha | C-21 |
| SS-083 | Elaboradora | Retificar — o que vai mudar | Alterações compostas | Resumo em português + o caminho normativo abaixo | O resumo em português | R-01 |
| SS-084 | Homologador | Detalhe da Retificação | Retificação em revisão | Vigência e alterações declaradas | A vigência | R-01 |
| SS-085 | Auditora | Trilha de auditoria do Edital | Ciclo completo | Ator, ato, data e motivo | A coluna do ator | R-10 / G-01 |
| SS-086 | Candidata | Comprovante — `mobile 375` | Inscrição enviada | Sem rolagem horizontal | — | C-12 |
| SS-087 | Presidente | Distribuição — `mobile 375` | Distribuição confirmada | Legibilidade em tela estreita | — | C-14 |
| SS-088 | Julgadora impedida | Peça do recurso com impedimento | Quem abre a peça publicou o resultado atacado | A razão do impedimento nomeada, e a tela **sem ações** | A razão | C-04 / C-19 |

~~**88 capturas.**~~ **89 capturas, depois de S-00.** Cinco são deliberadamente de recusa (SS-004,
SS-063, SS-074, SS-078/079) porque ensinam a regra melhor do que o caminho feliz. Quatro são
`celular 375` e cobrem as superfícies que o usuário mais consulta pelo celular. Nenhuma tela aparece
duas vezes no mesmo estado.

> **(S-00) Esta tabela está superada em dezessete linhas, uma removida e duas acrescentadas.** A
> versão que autoriza a coleta é `doc/manual/01-inventario-de-capturas-revisado.md`: ela mantém as
> colunas *Estado necessário* e *O que precisa estar visível* desta tabela para tudo que não alterou,
> acrescenta as regras de enquadramento e anotação que valem para todas, e registra que `seed_demo`
> **não** produz o certame do §F.1 — nem os perfis, nem as Etapas, nem o elenco, cujos nomes ainda
> colidem com os dos candidatos. **Leia as duas: esta pelo conteúdo, aquela pela forma e pelas
> mudanças.**
>
> **(R5)** E há uma terceira camada: o mesmo `01-…` ganhou a seção **§R5**, com a situação de cada
> captura contra o código de 06/10, a volta da `SS-010` e as telas novas sem captura prevista. O
> certame do §F.1 continua o mesmo; ele só precisa **ir mais longe** — corte, ocupação,
> convocação, Requerimento e exportação — e ganhar um segundo Perfil com marco de sorteio.

---

## G. Estratégia visual do HTML

### G.1 Tom

Institucional e claro. Referência mental: um manual de norma bem diagramado — não um blog, não um
produto SaaS, não material infantil. Serifada no corpo do texto (leitura longa), sem serifa em
títulos, rótulos e interface. Paleta contida: um cinza-azulado institucional, um acento único,
branco generoso. **(S-00)** O acento é **violeta `#5b3a8f`**, e a escolha é funcional, não estética:
ele é também a cor da anotação sobre as capturas, e o produto usa verde, vermelho e âmbar para
estado — um acento nessas faixas seria lido como parte da tela fotografada. Emoji **apenas** como marcador de tipo de caixa, sempre o mesmo símbolo para o
mesmo tipo, nunca no corpo do texto e nunca em títulos.

### G.2 Tipos de callout — sete, e só sete

| Marcador | Nome | Uso | Frequência esperada |
|---|---|---|---|
| 👤 | **Quem faz isto** | Abre toda tarefa que tem dono definido | 1 por procedimento |
| 🕒 | **Quando fazer** | Pré-condição temporal ou de estado | quando houver |
| 💡 | **Dica** | Atalho legítimo, jeito mais rápido | com parcimônia |
| ⚠️ | **Atenção** | Consequência indesejada, erro comum | forte, rara |
| ⛔ | **Sem retorno** | Os atos irreversíveis do §B.4 — **(R5)** eram dez, hoje são mais de vinte | exatamente onde eles estão |
| 🔎 | **O que muda depois** | O efeito invisível de um ato | 1 por ato importante |
| ✅ | **Você terminou quando…** | Fecha capítulo e tarefa | 1 no fim de cada procedimento |

`⛔` é distinta de `⚠️` de propósito: o produto trata como irreversíveis os atos do §B.4, e misturá-los
com avisos comuns apagaria a única distinção que o leitor precisa memorizar. **(R5)** Com mais de vinte
atos, a raridade passa a ser medida por capítulo: num capítulo de operação, `⛔` aparece no ato
que o capítulo ensina, e não em cada remissão a outro.

### G.3 Componentes

- **Cartão de papel** — bloco com ícone, nome do papel e "o que este papel pode fazer". Abre as
  trilhas da Parte 3.
- **Cartão de tela** — miniatura + nome da tela + endereço + "chega-se aqui por…". Usado no mapa de
  telas (`G-02`) e no topo de cada procedimento.
- **Linha do tempo horizontal** — as **19 (R5)** fases, com a fase atual em destaque. Repetida, reduzida, no
  topo de cada capítulo da Parte 2 (o quadro "onde estou").
- **Linha do tempo vertical** — dentro de um capítulo, para sequências de ato (submeter → homologar
  → publicar), com o ator ao lado de cada nó.
- **Tabela de decisão** — "se acontecer X, faça Y". É o formato da Parte 5 inteira.
- **Passo numerado com captura** — a unidade do procedimento: número, uma frase imperativa, a
  captura anotada, e o resultado esperado.
- **(S-00) Bloco "Limitação conhecida desta versão"** — moldura própria, barra vermelha à
  esquerda, **sem marcador emoji**, com o veredicto em destaque na primeira frase. Existe para a
  capacidade que o sistema oferece e que não deve ser usada. **(R5)** O único caso que o motivava
  (`§H.2`, em C-19) caiu; o componente fica definido e sem uso até aparecer outro. **Não é um oitavo
  callout**: `⛔` continua reservado aos atos irreversíveis do §B.4, e este bloco é da família de
  "por trás disto". Forma fixada e demonstrada em `doc/manual/piloto/index.html`.
- **Bloco "por trás disto"** — recuado, cinza, tipograficamente menor. Só quando explicar o
  mecanismo evita erro: por que a prévia envelhece, por que a conclusão trava, por que a definitiva
  é recusada. Nunca fala de código.

### G.4 Ilustrações vetoriais (não capturas)

Quatro, e são as que carregam o manual: o mapa das **19 (R5)** fases (C-03); o quadro de papéis e o que cada
um pode (C-04); o diagrama "elaborar × retificar" (C-05); e o diagrama do efeito das espécies de
decisão recursal (C-19) — **(R5)** os quatro caminhos desenhados, a reavaliação inclusive, que tem
cumprimento. **(R5) Candidata a quinta:** a cadeia ordem → corte → apuração → convocação de um
recorte, que é a parte do certame que o leitor menos consegue reconstituir sozinho. Devem ser SVG, legíveis em claro e escuro, e nunca conter texto que só
existe na imagem.

### G.5 Navegação

- **(S-00) O quadro "onde estou"** é uma **faixa de dezesseis traços** — **(R5) dezenove**: o
  piloto precisa ser regerado a partir do `data-fase`, que é para isso que ele existe —, um por fase, com o traço
  atual mais alto e na cor de acento, e acima dela uma linha em texto:
  `Fase 11 de 19 · Divulgar · o trabalho é do publicador`. Entra logo abaixo do resumo e antes do
  primeiro callout, **só nos capítulos da Parte 2** — C-03 é a linha do tempo inteira e não a
  repete. É gerado de um único atributo (`data-fase`), o que garante o mesmo nome de fase em vinte
  e cinco capítulos. Dezenove rótulos legíveis não cabem em 375 px sem rolagem horizontal, e este é o
  último lugar do manual onde se pode pedir isso ao leitor.
- **Menu lateral** persistente com as seis Partes; a Parte aberta expande; capítulo atual marcado.
- **Breadcrumb**: `Manual › Parte 2 · As fases › C-16 Consolidar o resultado de cada Etapa`.
- **Duas portas na home**, lado a lado e com o mesmo peso visual:
  *"Quero entender o processo"* → C-01 · *"Preciso fazer alguma coisa agora"* → índice de tarefas
  (Parte 4) com busca por verbo.
- **Progressão**: rodapé de cada capítulo com anterior/próximo **dentro da Parte**, mais um bloco
  "Depois disto, normalmente vem…" que aponta para a próxima **fase** (que pode ser de outro papel —
  e dizer isso é conteúdo: "agora o trabalho é do homologador").
- **Índice por papel** e **índice por tela**, ambos alcançáveis do menu.
- **Busca** local sobre títulos, rótulos de botão e termos do glossário.
- **Glossário com âncoras**: todo termo do §E aparece no texto como link discreto para a sua
  entrada, e a entrada lista os capítulos que o usam.

### G.6 Tratamento das capturas

- Moldura fina, canto levemente arredondado, sombra mínima. Nunca *mockup* de navegador.
- **Anotação sobre a imagem, não dentro dela:** retângulo de acento com 2 px e, quando houver mais
  de um alvo, marcadores numerados `①②③` que a legenda explica em texto. Isso mantém a captura
  legível e o texto pesquisável.
- **(S-00) A anotação é CSS sobre a imagem — nunca gravada no PNG**, e suas coordenadas são
  **emitidas pelo roteiro de captura**, em porcentagem da imagem, a partir do mesmo DOM que ele
  recortou. Refazer a captura não obriga a refazer a anotação, e o retângulo acompanha a imagem em
  qualquer largura de tela.
- **(S-00) Os marcadores seguem a ordem de leitura da imagem** — de cima para baixo, da esquerda
  para a direita —, e não a ordem de importância na legenda. A legenda se reescreve; a imagem não.
  O marcador fica **fora** do retângulo, acima do canto superior esquerdo: encostado no canto, ele
  cobre o primeiro caractere do rótulo que quer apontar.
- **(S-00) O recorte começa e termina em fronteira de elemento**, nunca a N pixels: a faixa de
  contexto acima é o elemento anterior inteiro. Margens de 22 px nas laterais e 8 px embaixo.
- **(S-00) Em 375 px, uma captura de tela larga não encolhe: ela se desloca dentro da moldura**, em
  tamanho real, com a legenda dizendo isso. Reduzida a 327 px, uma captura de 1 000 px fica com
  texto de tela abaixo de 5 px — e a legenda passa a ser a única coisa que ensina.
- **Legenda obrigatória**, em uma frase, dizendo o que a imagem prova — não o que ela mostra.
- **Recorte antes de reduzir**: capturar a tela toda e mostrar só a região relevante, com uma faixa
  de contexto acima.
- **Nunca** substituir texto por imagem: todo rótulo de botão citado aparece também no corpo, em
  **negrito** (*Clique em **Publicar resultado***).
- Dados sensíveis borrados na origem, não na diagramação.
- Versão `mobile` com moldura estreita, ao lado do desktop quando a comparação ensina algo.

### G.7 Linguagem

- Imperativo direto: *Clique em **Submeter para revisão***. Nunca "execute o comando".
- Os rótulos citados são **exatamente** os da tela. Se a tela diz *Concluir avaliação*, o manual
  não escreve "finalizar a avaliação".
- Nada de identificador técnico no corpo. Onde a tela mostra um, o manual diz: "o código longo ao
  lado é o registro de auditoria; você não precisa dele".
- Uma seção — e uma só — com vocabulário técnico: `G-05`, para quem instala e opera o serviço.

### G.8 · Régua de densidade **(S-00)**

Medida nas quatro páginas do piloto, e passa a ser critério de revisão de cada capítulo:

- **Entre duas capturas:** mínimo 4 linhas de texto, máximo 20. Abaixo de 4, as duas capturas são a
  mesma e viram uma; acima de 20, ou falta uma captura, ou sobra explicação que pertence ao bloco
  "por trás disto".
- **Dentro de um passo com captura:** uma frase imperativa (1–2 linhas), a captura, a legenda
  (1–3 linhas), o resultado esperado (1–2 linhas). Entre 3 e 8 linhas de texto por captura, fora a
  legenda.
- **Por página da Parte 2:** 850 a 1 150 palavras, 4 a 6 capturas, 5 a 7 caixas.
- **Caixas:** no máximo uma a cada 100 palavras, e **nunca duas seguidas sem texto entre elas**.
- **Prosa antes de procedimento:** um capítulo denso abre explicando o conceito, não listando
  passos. Foi o que fez o bloco de C-08 sobreviver — os passos ficaram curtos porque a explicação
  saiu deles.
- **Onde uma tabela diz melhor, a tabela fica e a captura encolhe.** Se for preciso cortar, corta a
  captura.

---

## H. Lacunas encontradas

Registradas como estão, sem solução inventada.

### H.0 · Onde cada lacuna aparece — e onde **não** aparece

Este inventário é interno. O manual **não** o reproduz. A regra de roteamento é: uma limitação só
interrompe o leitor no meio de uma tarefa quando ela **muda o que ele deve fazer agora**. Todas as
demais ficam concentradas em `G-03 — O que o sistema não faz hoje`, que é a seção de referência, e
o leitor chega lá por vontade própria.

Três destinos, e cada lacuna tem exatamente um:

| Destino | O que vai | Lacunas |
|---|---|---|
| **Alerta inline + `G-03`** | Afeta a ação em curso: o leitor faria algo errado, ou ficaria esperando algo que não vem | H.1, H.2 (orientação), H.4, H.5, H.10, **H.18 (R5)** |
| **Só `G-03`** | Fato relevante do produto que não muda nenhuma tarefa | H.3 e H.14 (estreitadas), H.7 (o que resta), H.13 (peso único), **H.19 (R5)** |
| **Nem no manual** | Achado interno; o manual o **resolve** escrevendo bem, ou ele é sobre o repositório | H.12, H.15 |
| **(R5) Fechadas — saem do roteamento** | O produto resolveu; o assunto vira conteúdo do capítulo | H.6, H.8, H.9, H.11, H.17 |

Detalhando as exceções da terceira linha (**(R5)** H.8 já não está entre elas), porque são as que costumam vazar para o texto por
descuido:

- ~~**H.8**~~ — **(R5)** fechada, e já estava quando este inventário a deu como aberta (§H.8). A
  regra que ela ilustrava continua valendo: o manual não escreve "o sistema não te leva até aqui".
- **H.12** (o recurso escolhe o objeto) — não é lacuna, é conteúdo. Vira exemplo em C-19.
- **H.15** (documentação defasada) — é instrução para quem produz o manual, nunca para quem o lê.

E uma regra de forma para as que **têm** alerta inline: o alerta diz **o que fazer**, não o que
falta. "Confira o prazo na página da seleção — o rascunho não avisa quando ele termina" ensina;
"o rascunho não avisa que o período encerrou (defeito conhecido)" só reclama.

### H.1 a H.17 · O inventário

**H.1 · Não há como documentar a entrada na área de gestão.**
A identificação da gestão vem hoje de um seletor de identidade que **existe apenas fora de
produção** — o ambiente de produção recusa iniciar com ele ligado — e a integração com o diretório
institucional é incremento futuro. *No manual:* C-02 diz que o acesso é institucional e remete à
área de TI; nenhuma captura da tela de seleção de identidade entra no manual do usuário (pode
entrar em `G-05`).

> *(R5) Continua aberta, e mudou de peso.* A preparação para produção de 30/09
> (`doc/implantacao-em-producao-ubuntu.md`, §1) a registra como bloqueador: sem adaptador
> institucional, `/gestao/` responde 503 em produção. O manual institucional não tem como ser usado
> em produção antes dele — o que não impede de escrevê-lo.

**H.2 · A decisão "deferir determinando reavaliação" não tem caminho de cumprimento.**
Achado E2E18-001, **aberto**, P1. A decisão é registrada, a Etapa passa a mostrar a pendência, e
não existe rota, botão ou tela que produza a reavaliação — a reabertura é recusada por regra. Como
reavaliação pendente é um dos fatos que barram a publicação definitiva, o marco fica
**permanentemente impedido** de chegar a resultado definitivo. *No manual:* a espécie **sai do
fluxo principal** — não é ensinada como opção, não entra na tabela de espécies e não recebe
procedimento; aparece uma vez só, em caixa de limitação conhecida ao fim de C-19, com o texto
*"⛔ Não utilize esta opção nesta versão do sistema"*, e repetida em uma linha em `G-03`. Não
inventar procedimento e não sugerir contorno: **não há** contorno. Ver também §H.16.

> *Nota de 28/09/2026 — o diagnóstico acima não se confirmou.* Percorrido pelas telas da gestão
> (RC-63 da auditoria de consolidação de 26/09): julgada a reavaliação, a organização da Etapa
> nomeia a pendência, a distribuição aceita um avaliador **diferente** do que concluiu a original, a
> Mesa conclui, e a consolidação cria o Resultado sucessor citando a decisão — depois disso a
> reavaliação deixa de barrar a publicação definitiva. A reabertura continua recusada por regra, e
> é ela que não é o caminho; a recusa agora diz qual é. O registro, com o que a tela ainda não
> orienta, está em `doc/validacao-de-unidades-pre-piloto-2026-09-28.md`. Quem for escrever C-19
> precisa refazer esta decisão editorial a partir da tela atual.
>
> *(R5) Decisão editorial refeita.* A espécie volta à tabela de C-19 e o cumprimento vira a receita
> `R-13`: distribuir a **outro** avaliador (a vaga extra), concluir na Mesa, e consolidar marcando a
> linha e usando **"Consolidar as selecionadas"** — "Consolidar as N prontas" não a alcança. O que
> resta são **lacunas de orientação**, que vão como alerta inline: a peça do recurso, depois da
> decisão, diz "Nenhum — este recurso não produziu resultado sucessor" sem indicar o próximo passo;
> a faixa de prontidão não filtra as reavaliações; "Reabrir" continua oferecido em Conclusões
> preservadas, e é recusado; a Mesa não diz à avaliadora que é uma reavaliação.

**H.3 · A consulta pública histórica não tem tela.**
O sistema sabe responder "qual era o conteúdo vigente em tal data" e "quais Retificações houve",
mas **só pela API**. A página pública da seleção mostra apenas o vigente e não lista Retificações.
*No manual:* C-05 ensina o conceito de versão vigente × histórica porque ele governa o
comportamento; e `G-03` registra que a consulta por data não tem interface.

> *(R5) Fechada em parte.* A página pública lista o Edital de abertura e cada Retificação, com PDF,
> "vigente desde" e "O que mudou", e avisa quando o Edital foi retificado (`024`); as publicações
> de resultado sucedidas também ficam listadas (`047`). O que segue sem tela é consultar o conteúdo
> vigente numa data passada qualquer — só pela API.

**H.4 · O Resultado de Etapa não é público.**
O candidato vê o próprio ("Eliminada na Análise de requisitos") dentro da sua inscrição; o público
não vê Resultado de Etapa em lugar nenhum. Só o ato de classificação é divulgado. *No manual:*
dito explicitamente em C-16 e C-18.

> *(R5) Continua aberta, com duas precisões.* O candidato só vê o próprio Resultado de Etapa depois
> que existe publicação vigente de um marco que conta aquela Etapa — não logo após a consolidação.
> E há uma exceção pública: num marco de sorteio, a relação de habilitados é publicada, nominal,
> antes do sorteio.

**H.5 · Não há comunicação ativa.**
Ninguém é notificado de nada. E-mail é usado só para o código de acesso do candidato. Publicação é
passiva: quem não abrir a página não fica sabendo. *No manual:* alerta em C-18 e entrada em `G-03`.

> *(R5) Mudou — e já era impreciso em 08/09.* O sistema envia e-mail em quatro situações: o código
> de acesso; a confirmação do envio da inscrição (existia desde 01/09); o aviso de mudança de
> credencial; e a **convocação**, quando o Perfil declara "por mensagem individual". Resultado,
> Retificação e prazos continuam sem aviso. O alerta de C-18 fica, restrito a resultado; C-20b
> ganha o seu.

**H.6 · Não há corte nem progressão automática entre Etapas.**
A feature existiria na 014, que não foi construída. Quem passa para a Etapa seguinte é quem tem
Resultado Habilitada; não há "aprovar os N primeiros". *No manual:* `G-03`.

> *Nota de 28/09/2026 — o código andou depois desta seção.* A `014` foi construída: o corte existe
> e tem tela (`interface:corte`), e a progressão entre Etapas passa por ele. Esta limitação não vale
> mais, e quem for escrever C-14 ou `G-03` precisa partir da tela atual.
>
> *(R5) Fechada.* Sai de `G-03`; o assunto é C-17b.

**H.7 · O ciclo termina na publicação definitiva.**
Não existem homologação do resultado final, nomeação, convocação ou posse. E o sistema **não
orienta** quando encerrar o Edital em relação ao resultado. *No manual:* C-21 diz o que o
encerramento faz e declara que o momento é decisão institucional, não do sistema.

> *Nota de 28/09/2026 — o código andou depois desta seção.* A convocação, a chamada e a suplência
> existem desde a `019` (`interface:convocacao`), e o Requerimento de Matrícula e a exportação para o
> Registro Acadêmico desde a `029` e a `031`. O ciclo não termina mais na publicação definitiva.
>
> *(R5) Fechada quanto à convocação; o resto fica em `G-03`:* efetivar a matrícula no sistema
> acadêmico (o arquivo é entregue, não importado), nomeação e posse, validade e prorrogação do
> Edital, recurso contra a convocação. E o momento de encerrar continua decisão institucional — o
> que mudou é que encerrar o Processo agora **exige** os Editais encerrados ou cancelados.

**H.8 · O caminho da presidência até distribuir e consolidar não é anunciado.**
Achado E2E15-016, aberto: "Minhas Etapas" do presidente diz que ele não tem Etapas atribuídas, e o
caminho real (Alocação por Etapa → Distribuir → painel da Etapa) só se descobre explorando. *No
manual:* **nada** — C-14 simplesmente abre nomeando o caminho, e a lacuna deixa de existir para
quem lê. Fica no backlog de produto (§H.16).

> *Nota de 28/09/2026 — corrigido no produto.* "Minhas Etapas" de quem preside e não avalia agora
> diz que presidir não atribui trabalho de avaliação e aponta **Gerir comissão** e **Alocação por
> Etapa** (`interface/templates/interface/minhas_etapas.html`). O E2E15-016 não está mais aberto.
>
> *(R5) Precisão:* a correção é de 01/09 (`9ed2bf2d`), **anterior** à base desta descoberta. O
> inventário a deu como aberta lendo o relatório E2E sem conferir a tela — que é exatamente o
> risco que a §H.15 descreve.

**H.9 · O rascunho não avisa que o período encerrou.**
Achado E2E15-007, aberto: com as inscrições encerradas, a revisão do rascunho ainda convida a
prosseguir. *No manual:* alerta em C-12 ("confira o prazo na página da seleção; o rascunho não te
avisa").

> *(R5) Fechada em 28/09 (PR #215, RC-49).* O rascunho fechado diz "O período de inscrições terminou
> em… Esta inscrição não foi enviada e não pode mais ser", some o botão de revisar, e "Minhas
> inscrições" oferece "Consultar inscrição". O alerta de C-12 sai; a tela vira captura.

**H.10 · Um candidato deslogado recebe 404 na própria inscrição.**
Achado E2E15-013, aberto: um link guardado no celular vira beco em vez de convite a entrar. *No
manual:* dica em C-12 — entre primeiro, depois abra o link.

> *(R5) Continua aberta*, e o link "Entrar" do cabeçalho não guarda o destino: depois de entrar, a
> pessoa cai em "Minhas inscrições".

**H.11 · A Mesa aceita concluir avaliação de inscrição que já tem Resultado.**
Achado E2E15-003, aberto, **depende de decisão de governança**. Produz um par contraditório nos
registros. *No manual:* não documentar como comportamento; alerta em C-16 para a presidência
registrar ocorrência **antes** de as avaliações pendentes serem concluídas.

> *(R5) Fechada em 28/09 (PR #220, RC-62), por decisão do usuário:* a Mesa recusa concluir avaliação
> de inscrição que já tem Resultado, salvo reavaliação determinada, e avisa antes do clique. O
> alerta de C-16 sai.

**H.12 · Recursos escolhem o objeto, e o vocabulário do objeto é sutil.**
Um recurso pode atacar a publicação **ou** um Resultado de Etapa, e o efeito de cada escolha é
diferente. Não é defeito; é uma distinção que o manual precisa ensinar com exemplo, em C-19.
**(R5)** E C-19 diz também o que não é atacável: a convocação e a relação de habilitados.

**H.13 · Múltiplos marcos por perfil são aceitos e não têm jornada.**
A composição aceita mais de um marco classificatório por perfil; nada no produto sugere quando
usar. *No manual:* C-08 documenta um marco; `G-03` registra a capacidade sem orientação.

> *(R5) Mudou: virou regra, e sobrou outra lacuna.* A `046` exige ao menos um marco que corte por
> Perfil, e o par preliminar sem corte + final com corte é jornada prevista — C-08 o ensina. O que
> vai para `G-03` é outra coisa: a mesma Etapa tem um peso só em todos os marcos que a enumeram.

**H.14 · Capacidades sem tela.**
A prova de reprodutibilidade do ato de classificação e o teto de inscrições por candidato existem
no domínio e não têm interface (o teto só é configurável fora do assistente). *No manual:*
`G-03`, sem procedimento.

> *(R5) Metade fechada.* O teto de inscrições ganhou tela no passo Inscrição (e na Retificação e no
> portal), e a reprodução do **corte** tem tela no histórico do corte. Seguem sem tela a prova de
> reprodutibilidade do ato de **classificação** e o cancelamento de um Evento do Cronograma.

**H.17 · Acrescentar um Edital a um Processo já criado não tem tela. (S-00)**
Encontrado ao montar o certame do piloto. `/gestao/processos/criar` cria o Processo **junto com** o
primeiro Edital, numa tela só (`Criar Processo e Edital`); o detalhe do Processo não oferece a ação,
não há rota, e `add_edital` existe apenas na API. A capacidade é do domínio e a interface não a
alcança. *No manual:* **só `G-03`**, em uma linha, junto do `H.14` — o fato não muda o que o leitor
deve fazer agora, porque a tela o conduz corretamente pelo caminho que existe. C-06 perde a promessa
de ensinar "um Processo com vários Editais", e a captura `SS-010` sai do inventário.

> *(R5) Fechada em 16/09 (`6f0f9887`).* "Novo Edital neste Processo", na página do Processo, para
> quem tem o papel de Gestor. C-06 volta a ensinar um Processo com vários Editais, e a `SS-010`
> volta ao inventário.

**H.16 · Backlog de produto — o que não é problema de manual.**

> *(R5) O quadro abaixo está obsoleto nas quatro linhas:* H.2 não se confirmou, H.11 e H.17 foram
> fechadas, e H.8 já estava fechada. O backlog de hoje, para quem decide produto — **registro, não
> escopo de nenhuma feature**:
>
> | | Lacuna | Natureza |
> |---|---|---|
> | 1 | **H.1** — sem adaptador institucional de identidade | Bloqueador de produção |
> | 2 | **H.18** — o portal não leva à convocação nem ao Requerimento pedido na convocação | Defeito de navegação, com efeito no prazo do candidato |
> | 3 | **H.2** — lacunas de orientação da reavaliação | Polish de UX; o manual mitiga |
> | 4 | **H.10** — link guardado vira "não encontrado" para quem não entrou | Polish de UX; o manual mitiga |
>
> O texto original fica abaixo, como registro do que se decidia em 08/09.
Três das lacunas acima são candidatas a correção no produto, e a distinção entre elas importa:

| | Lacuna | Natureza | Recomendação |
|---|---|---|---|
| 1 | **H.2** — reavaliação determinada sem cumprimento | **Bloqueio funcional** | **Corrigir antes de publicar o manual institucional.** Documentar uma ação disponível dizendo "não use" é aceitável como estado transitório e ruim como estado final: o manual passa a ser o lugar onde a instituição admite, por escrito, que o produto oferece um botão que não funciona |
| 2 | **H.11** — Mesa aceita conclusão sobre inscrição já resolvida | **Decisão de governança** | Decidir a regra primeiro; a implementação é consequência. Não trava o manual |
| 3 | **H.8** — jornada da presidência não é descobrível | **Polish de UX** | Bom candidato futuro. **Não trava o manual** — C-14 o mitiga integralmente |

A produção do manual **não deve esperar** por H.8 nem por H.11. Só H.2 tem peso para justificar
segurar a publicação institucional do material.

**(S-00)** `H.17` entra neste quadro como quarto item, e é o mais brando dos quatro: **capacidade sem
interface**, não bloqueio nem defeito. Um Processo com vários Editais é o que um Processo Seletivo
real tem, e hoje só a API o monta. **Não trava o manual** — C-06 ensina a tela como ela é. Se a
instituição precisar de dois Editais no mesmo Processo pela interface, é decisão de produto, e não
escopo da produção do manual.

**H.15 · A documentação do repositório está defasada.**
O `README.md` descreve o produto até a spec 004. Os relatórios E2E citam achados já corrigidos —
verifiquei dois deles (a lista de anexos ganhou cartão com posição; a Retificação ganhou resumo em
português) que os relatórios ainda descrevem como abertos. **Consequência operacional:** toda
sessão de produção do manual deve **conferir a tela ao vivo** antes de escrever sobre um achado,
e nunca escrever a partir do relatório sozinho.

> *(R5)* O README está em dia desde 28/09 e um teste o mantém assim
> (`tests/test_readme_acompanha_o_codigo.py`), mas a tabela de módulos repete 14 linhas — registro
> para quem cuida do README. O estado reconciliado dos achados E2E está no anexo 1 da auditoria de
> 26/09. A consequência operacional continua de pé, e esta revisão a confirma: H.8 estava fechada
> quando este inventário a deu como aberta.

**H.18 · O portal não leva à convocação nem ao Requerimento pedido na convocação. (R5)**
Nenhum template do portal tem link para a tela "Convocação" do candidato (`portal:convocacao`); o
e-mail de convocação aponta para "Minhas inscrições", e nem ela nem "Acompanhar" mostram a
chamada. Quando o Edital pede o Requerimento de Matrícula "quando o candidato for convocado",
nenhuma tela do portal leva a ele — o cartão só aparece quando o pedido é na inscrição. Na prática,
o candidato só chega pelo endereço digitado. Conferido por busca nos templates em 06/10. *No
manual:* alerta em C-20b e C-20c, e a comunicação de convocação precisa dizer o caminho até a
correção. É o item 2 do backlog da §H.16, e decisão do usuário.

**H.19 · Limitações declaradas pelas features 019–058 que o leitor precisa encontrar. (R5)**
Todas em `G-03`, uma linha cada, com a fonte: prazos só em dias corridos (`019`); sem carga
retroativa de Edital com inscrições encerradas (decisão de 25/09); cancelamento do Edital não gera
Publicação (RC-120); um documento público por marco **e por lista** de concorrência (DP-15); o
sistema registra onde a convocação foi publicada, não a publica (`047`); importação de notas,
heteroidentificação como fluxo, cascata entre recortes e segunda instância recursal estão fora
(`019`, `021`, `047`); a comissão alcança todos os Perfis e polos, sem filtro por Perfil na
distribuição (DP-11, aberta). O prazo de recurso escrito no Cronograma é texto livre e não se liga
à janela do marco — as duas datas podem discordar, e a da tela é a verdadeira (RC-76): esta vai
**também** como alerta inline em C-07 e C-08.

---

## I. Ordem recomendada de produção

Dois princípios, e o segundo veio corrigir o primeiro:

1. **Produzir na ordem em que os dados existem.** O certame-exemplo é construído uma vez, do começo
   ao fim, e cada estado é capturado no instante em que existe — vários são irreversíveis e
   recriá-los custa um banco novo.
2. **Validar o formato antes de industrializar a produção.** O princípio 1, sozinho, levava a
   capturar 88 imagens antes de existir uma única página escrita — e a descobrir depois que faltou
   uma tela, que um enquadramento tinha informação demais, ou que o desenho da página pedia recorte
   e não captura inteira. **O piloto vem primeiro.**

### I.0 · O piloto editorial (S-00)

Um protótipo **vertical**: poucas páginas, mas completas — do layout ao último callout — para que
o padrão seja aprovado com material real e não no abstrato.

**As três páginas do piloto, e por que estas:**

| Página | Natureza que ela põe à prova |
|---|---|
| **C-03 — O ciclo completo em um mapa** | Página **sem nenhuma captura**: testa as ilustrações vetoriais, a linha do tempo das 16 fases e o quadro "onde estou" que se repete no manual inteiro |
| **C-12 — Inscrever-se** | Jornada de **público externo**, muitos passos curtos, forte uso de celular: testa a densidade texto-por-passo e o comportamento *mobile* |
| **C-18 — Divulgar o resultado** | Ato **institucional com consequência**: testa `⛔`, a caixa "o que muda depois", a captura de recusa e a legenda que prova em vez de descrever |

**Um quarto espécime, e não uma quarta página.** As três acima não põem à prova a superfície mais
difícil do manual — a operação administrativa densa do assistente de elaboração, onde cabe o maior
volume de texto por passo. Em vez de escrever C-08 inteiro no piloto, o que anularia o propósito de
ele ser pequeno, o piloto inclui **um único bloco de procedimento extraído de C-08** (compor um
critério de desempate: 3 passos, 2 capturas). É o pior caso de densidade, custa meia página, e sem
ele o padrão seria aprovado sem nunca ter encostado no capítulo mais difícil.

**Capturas do piloto: 8 a 12**, tiradas de um certame reduzido — não é ainda o acervo definitivo.
Reaproveitá-las depois é bem-vindo, mas não é requisito: o piloto existe para ser descartável.

**S-00 é um teste de design instrucional, não o começo informal do manual.** A diferença é
operacional: um começo informal produz três páginas bonitas e nenhuma regra; um teste de design
produz **decisões escritas** que as dezenove sessões seguintes aplicam sem reabrir. Ao terminar, a
sessão precisa responder por escrito, cada uma em um parágrafo curto e com o exemplo real ao lado:

1. **Qual é a anatomia padrão de uma página?** — a ordem fixa dos elementos, do título ao rodapé de
   progressão.
2. **Quanto texto existe entre duas capturas?** — a régua de densidade, em linhas, com o mínimo e o
   máximo.
3. **Quando usar tela inteira e quando usar recorte?** — o critério, não o gosto.
4. **Como indicar exatamente onde clicar sem poluir a imagem?** — espessura, cor, marcador numerado,
   e o que fazer quando há mais de um alvo.
5. **Quais callouts sobrevivem ao uso real?** — dos sete propostos, quais foram usados, quais
   ficaram sem ocasião e quais faltaram.
6. **Como representar "onde estou no processo"?** — a forma reduzida da linha do tempo das 16 fases,
   e onde ela entra na página.
7. **O tom está simples sem ficar infantil?** — com um trecho antes/depois que demonstre o
   julgamento.
8. **Como a página se comporta em desktop e em 375 px?** — o que reflui, o que rola, o que some.
9. **C-08 continua compreensível na configuração mais densa?** — é o que o bloco-espécime existe
   para responder.

**Gate explícito: S-01 não começa enquanto S-00 não aprovar o padrão e revisar o inventário de
capturas do §F.** As duas coisas, não uma. Aprovar o padrão sem revisar o inventário deixaria a
coleta seguir uma lista montada antes de existir uma página diagramada.

**As capturas do piloto são descartáveis — inclusive as que ficarem boas.** Se o certame definitivo
ou o enquadramento mudar, refazer é o comportamento correto; preservá-las por apego ao trabalho
feito contamina o acervo definitivo com decisões que o piloto justamente serviu para revogar. A
função delas é descobrir o padrão, e uma imagem que já cumpriu essa função não tem nenhum direito
adquirido de entrar no manual.

**O que o piloto precisa entregar para ser considerado aprovado:**

- layout provisório navegável (menu, breadcrumb, rodapé de progressão);
- as três páginas escritas de verdade, sem *lorem ipsum*;
- o bloco-espécime de C-08;
- os sete callouts usados ao menos uma vez cada, em contexto real;
- o **padrão de anotação** de captura fixado: espessura, cor, marcadores numerados, legenda;
- a **régua de densidade**: quantas linhas de texto por passo, quando recortar, quando ampliar;
- o comportamento em 375 px das três páginas;
- uma decisão explícita sobre cada dúvida que aparecer — registrada, não deixada para depois.

> **(S-00, executado em 08/09/2026.)** O piloto foi produzido em `doc/manual/piloto/`, as nove
> respostas estão em `doc/manual/piloto/relatorio-s00.md`, e o inventário foi revisado em
> `doc/manual/01-inventario-de-capturas-revisado.md` — de 88 para **89** capturas. As ferramentas de
> captura ficaram em `doc/manual/piloto/ferramentas/`, para que S-01 não as reconstrua.

**Só depois da aprovação do piloto começa a coleta das capturas.** Se o piloto indicar outro
enquadramento, o inventário do §F é revisado antes de qualquer sessão de captura — e é para isso
que ele existe.

### I.0-bis · A reconciliação (S-00R) **(R5)**

**Esta Revisão 5 é a primeira metade de uma sessão que o plano não previa**, e o gate da S-00 não
basta mais para autorizar a coleta: o padrão editorial que o piloto fixou continua valendo
(anatomia, callouts, densidade, anotação), mas o **inventário** e o **espécime de C-08** foram
aprovados sobre telas que mudaram. Antes de S-01, a S-00R entrega:

1. **feito nesta revisão:** §A, §B, §C, §C.bis, §D, §E, §G e §H revistos contra o código de 06/10;
   a situação de cada captura em `01-…`, §R5, com as telas novas sem captura;
2. **a fazer:** o espécime de C-08 recapturado na tela da `053` (a Classificação mostra hoje um
   Perfil por vez, e o bloco do recurso é recolhível);
3. **a fazer:** o quadro "onde estou" do piloto regerado para 19 fases;
4. **a fazer:** o `LEIA-ME.md` das ferramentas corrigido — o exemplo de recorte usa um seletor que
   nenhuma tela do portal tem, e a porta citada não é a de nenhuma entrada com SMTP;
5. **a fazer:** o inventário de `01-…`, §R5, transformado em tabela de coleta com estado necessário
   para cada captura nova, como a §F faz para as antigas.

**As quatro páginas do piloto não são reescritas na S-00R.** Elas cumpriram a função de fixar o
padrão; o conteúdo de C-03, C-12 e C-18 é revisto nas sessões que os escrevem (S-05, S-09, S-12),
e o que está vencido em cada uma está listado em `01-…`, §R5.

### I.1 · As fases da produção

**Fase 0 — Piloto editorial.** Acima. Termina com um padrão aprovado e, se for o caso, com o §F
corrigido.

**Fase 1 — Coleta.** O certame do §F.1 percorrido **inteiro** pelo navegador, na ordem da jornada,
capturando as ~~88~~ **89 (S-00)** imagens já sob o padrão aprovado — **(R5)** mais as telas novas
de `01-…`, §R5, e com o certame indo até a exportação. Banco limpo, seletor de identidade ligado,
entrada própria no `launch.json`, PDFs fictícios dos candidatos.

**Fase 2 — Esqueleto definitivo e sistema visual.** O provisório do piloto vira definitivo: as
quatro ilustrações vetoriais, o glossário com âncoras, a busca.

**Fase 3 — Parte 2 (as fases), em ordem cronológica.** É o corpo; tudo mais aponta para ele. C-03,
C-12 e C-18 já existem desde o piloto e são **revisados**, não reescritos.

**Fase 4 — Parte 1 (visão geral).** Escrita **depois** do corpo, de propósito: só depois de
escrever as fases se sabe o que precisa ser antecipado.

**Fase 5 — Partes 3, 4 e 5.** Trilhas, tarefas e exceções — todas por remissão ao que já existe.

**Fase 6 — Parte 6 e fechamento.** Glossário consolidado, mapa de telas, `G-03`, FAQ e revisão de
consistência de rótulos contra a interface ao vivo.

### I.2 · Divisão em sessões

Cada sessão precisa caber em contexto sem degradar. A regra: **uma sessão = um entregável fechado,
com no máximo três capítulos ou um bloco de capturas.** Cada uma começa relendo este documento e
mais no máximo dois arquivos do repositório.

| # | Sessão | Entrega | Precisa ler |
|---|---|---|---|
| **S-00** | **Piloto editorial** | **Layout provisório, C-03, C-12, C-18, o bloco-espécime de C-08, 8–12 capturas, padrão de anotação e régua de densidade** | **§C.bis, §G, §F.1** |
| **S-00R** | **Reconciliação (R5)** | **§I.0-bis — metade feita nesta revisão** | **§A–§H, `01-…` §R5** |
| S-01 | Capturar as fases 1–5 | SS-001 a SS-042, **(R5)** com a SS-010 de volta e as do reaproveitamento | §F, padrão aprovado em S-00, `01-…` §R5 |
| S-02 | Capturar as fases 6–11 | SS-043 a SS-067, **(R5)** mais sorteio e corte | idem |
| S-03 | Capturar as fases 12–15 e as exceções | SS-068 a ~~SS-087~~ **SS-088** *(a linha voltou a 087 num merge de 12/09; corrigida)* | idem |
| **S-03b** | **(R5) Capturar as fases 16–19** | Ocupação, convocação (gestão e portal), Requerimento, exportação, encerramento com Edital pendente, Supervisão e Visão Geral | idem — sequencial depois da S-03 |
| S-04 | Esqueleto definitivo e sistema visual | Menu, busca, glossário com âncoras | §G, saída de S-00 |
| S-05 | As quatro ilustrações vetoriais | 4 SVG | §B, §G.4 |
| S-06 | C-06, C-07 | Abrir o Processo + Elaborar I | §C.bis, capturas de S-01 |
| S-07 | C-08 | Elaborar II (o capítulo difícil) | §C.bis, §E, o espécime de S-00 |
| S-08 | C-09, C-10 | Elaborar III + aprovar e publicar | §C.bis |
| S-09 | C-11 + revisão de C-12 | Inscrições por dentro; C-12 revisto | §C.bis, saída de S-00 |
| S-10 | C-13, C-14, C-15 | Comissão, distribuição e avaliação | §C.bis |
| S-11 | C-16, C-17 | Consolidação e classificação | §C.bis |
| S-12 | Revisão de C-18 + C-19 | C-18 revisto; recursos — **(R5)** com a reavaliação como espécie normal | §C.bis, §H.2 e `doc/validacao-de-unidades-pre-piloto-2026-09-28.md` |
| S-13 | C-20 | Refazer e republicar | §C.bis |
| **S-13a** | **(R5) C-17a, C-17b, C-20a** | Sorteio, corte, ocupação | §C.bis, capturas de S-02/S-03b |
| **S-13b** | **(R5) C-20b, C-20c, C-20d** | Convocação, Requerimento, exportação | §C.bis, §H.18 |
| **S-13c** | **(R5) C-11a, C-21a, C-22** | Acompanhar, Retificar, Visão Geral | §C.bis |
| S-14 | C-21 + Parte 1 (C-01 a C-05, com C-03 revisto) | Encerramento e visão geral — **(R5)** C-21 com o encerramento que exige Editais finais | tudo escrito até aqui |
| S-15 | Parte 3 (~~8~~ **9** trilhas) | Páginas-roteiro | §D |
| S-16 | Parte 4 (~~10~~ **14** tarefas) | Receitas | §C, capítulos prontos |
| S-17 | Parte 5 (~~10~~ **13** situações) | Tabelas de decisão | §B.4, §H |
| S-18 | Parte 6, com `G-03` | Glossário, mapa de telas, limites, FAQ | §E, §H.0, §H |
| S-19 | Revisão final de consistência | Rótulos conferidos contra a interface ao vivo | — |

**Vinte sessões — (R5) vinte e cinco**, com a S-00R e as quatro novas. S-01 a S-03b exigem o
sistema no ar e não podem ser paralelizadas entre si — o certame é sequencial. Da S-06 em diante, cada sessão depende apenas do acervo de capturas, do
padrão aprovado em S-00 e deste documento; várias podem ser retomadas fora de ordem sem perda.

### I.3 · Duas decisões editoriais a preservar

Registradas aqui porque são exatamente as que uma sessão futura, sob pressão de prazo, tende a
desfazer sem perceber o que está desfazendo.

**Os personagens são um recurso pedagógico, não enfeite.** Gustavo abre o Processo, Elena redige,
Wagner homologa, Paula publica, Paulo preside, Alice e Otávio avaliam, Júlia julga o recurso, Ana e
os demais participam. O fio narrativo é o que torna a segregação de funções compreensível sem
explicá-la em abstrato: o leitor **vê** que são pessoas diferentes. Nenhuma sessão deve trocar
nomes por "o elaborador", "o usuário A".

**O manual é grande porque a jornada é grande.** São ~~21~~ **31 (R5)** capítulos principais porque o
certame tem, de fato, ~~16~~ **19** fases e ~~nove~~ **dez** públicos. A tentação de comprimir isso num material de quinze páginas
produziria um manual que não serve para operar. A resposta correta ao tamanho já está na
arquitetura — conteúdo modular, capítulos curtos, entrada por papel e por tarefa —, e não em
eliminar complexidade que existe no produto. **Não reduzir escopo por parecer grande.**
