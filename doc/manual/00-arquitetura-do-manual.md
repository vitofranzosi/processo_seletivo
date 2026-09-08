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

**Base da descoberta:** `main` @ `a6f25a4`. Fontes lidas: `README.md`, a Constituição, as 18 pastas
de `specs/`, os quatro relatórios de auditoria E2E (`doc/e2e/015`, `017`, `018`, `020-polish`), os
documentos de decisão em `doc/`, e — como fonte de verdade final — o código: `interface/urls.py`,
`portal/urls.py`, `interface/atos.py`, `interface/acoes.py`, `interface/identidade.py`, os 97
templates das duas interfaces e os enums de domínio.

> **Uma advertência sobre as specs.** A numeração não é sequência pedagógica e nem sequência
> histórica confiável: faltam as pastas 014, 016 e 019 (features não construídas), a 012 e a 013
> foram revisadas em conjunto por um terceiro documento, e o `README.md` está **defasado** — ele
> descreve o produto até a spec 004 e afirma que "a interface administrativa e pública é uma
> especificação futura", o que deixou de ser verdade há quinze incrementos. Nenhuma sessão de
> produção do manual deve tomar o README como retrato do sistema.

---

## A. Quem usará o manual

### A.1 Os atores que existem de fato

O sistema reconhece identidade de três maneiras distintas, e essa distinção é a espinha do manual.

**1. Papéis nomeados** (`interface/identidade.py::PAPEIS`) — conjuntos fixos de permissões que, na
implantação institucional, virarão grupos do diretório. São **seis**:

| Papel | O que pode fazer |
|---|---|
| **Elaborador** | Elaborar e submeter Edital; elaborar e submeter Retificação |
| **Homologador** | Homologar e devolver Edital; homologar Retificação; revogar homologação |
| **Publicador** | Publicar Edital, publicar Retificação e **publicar resultado** |
| **Gestor** | Criar/ativar/encerrar/cancelar Processo; criar/encerrar/cancelar Edital; cancelar Retificação; **constituir a comissão**; consultar inscrições recebidas |
| **Julgador de recursos** | Admitir e julgar recursos — e nada mais |
| **Auditor** | Consultar a trilha de auditoria e as telas de leitura |

**2. Capacidades verificadas contra o vínculo** — não são papéis; são conferidas objeto a objeto:

| Capacidade | Como se obtém |
|---|---|
| **Presidência da comissão** (`comissao:presidir`) | Ser designado PRESIDENTE na comissão daquele Processo |
| **Avaliação atribuída** (`avaliacao:atribuida`) | Receber a Atribuição de uma inscrição numa Etapa |

**3. Identidade do candidato** — outra sessão, outro domínio, outro endereço (`/selecoes/`).
Obtida por código enviado por e-mail, sem senha.

**4. Público anônimo** — sem identidade nenhuma. Vê a vitrine, a página da seleção, o PDF do
Edital, os anexos e os resultados divulgados.

### A.2 Agrupamento pedagógico — e o que foi descartado

O manual **não** terá um capítulo por permissão. Terá **oito públicos**:

| Público do manual | Reúne | Por quê |
|---|---|---|
| **Quem organiza o certame** | Gestor | Abre e fecha o Processo, cria o Edital, monta a comissão. É o dono do ciclo |
| **Quem redige o Edital** | Elaborador | Passa 90% do tempo num assistente de nove passos. Merece o capítulo mais denso |
| **Quem aprova** | Homologador | Trabalho curto, decisão pesada, vocabulário próprio (fundamento, devolução, revogação) |
| **Quem assina e publica** | Publicador | Pratica os dois atos irreversíveis do sistema: publicar Edital e divulgar resultado |
| **Quem preside a avaliação** | Presidente da comissão | Distribui, controla impedimento e ocorrência, consolida, emite classificação |
| **Quem avalia** | Membro da comissão / avaliador | Só vê o que lhe foi atribuído. Manual curtíssimo e autossuficiente |
| **Quem julga recursos** | Julgador | Papel deliberadamente isolado — quem julga não pode ter atuado |
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
  *constitui* a comissão mas não pode presidi-la por isso; a presidência é vínculo.

### A.3 · A equipe real — acúmulo de papéis numa operação de duas ou três pessoas

Os seis papéis descrevem **funções**, não pessoas. Uma pessoa pode acumular vários, e a operação
inicial prevista é de **duas a três pessoas**. Isso não invalida a arquitetura — mas obriga o
manual a ensinar *como acumular*, porque o sistema tem regras que olham para **quem foi a pessoa**,
e não só para qual permissão ela tem.

**As três regras de identidade que existem no domínio** (verificadas no código, não inferidas):

| Regra | O que o sistema exige | Mínimo de pessoas |
|---|---|---|
| **Publicar Edital ou Retificação** | Quem publica não pode ser a mesma pessoa que elaborou **e** homologou aquela revisão. Basta que uma das duas etapas anteriores tenha sido de outra pessoa | **2** |
| **Julgar recurso** | Quem julga não pode ter concluído a avaliação que fundamentou o resultado atacado, nem o consolidado, nem emitido o ato de classificação atacado, nem praticado a publicação atacada — nem ter impedimento declarado quanto àquela inscrição | **2**, com divisão rígida |
| **Reavaliação determinada por recurso** | Exige avaliador diferente do que concluiu a original | **2 avaliadores** — mas a espécie está fora do manual (§H.2) |

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

**O que uma equipe de duas pessoas perde**, e o manual deve dizer sem rodeio:

- **não há reavaliação por recurso** — com um avaliador só, não existe o "avaliador diverso" que
  ela exige (a espécie já está fora do manual por outro motivo, §H.2);
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

A sequência do briefing está quase certa. Três correções que o código impõe:

1. **Antes de "planejar" existe um ato próprio:** o **Processo Seletivo** é criado e depois
   **ativado**; o Edital nasce dentro dele. São duas entidades com ciclos de vida separados.
2. **"Revisar" e "homologar" são o mesmo degrau**, praticado por uma pessoa só.
3. **"Corrigir/reavaliar" não vem depois de "julgar" como fase própria** — é *efeito* do
   julgamento, e uma das quatro espécies de decisão **não tem caminho de cumprimento** (§H.2).

### B.2 O mapa

```
┌─ FASE 1 · ABRIR ───────────────────────────────── Gestor
│  Criar Processo Seletivo → Ativar Processo → Criar Edital
│
├─ FASE 2 · ELABORAR ────────────────────────────── Elaborador
│  Assistente de 9 passos:
│  Identificação → Perfis de Vaga → Cronograma → Etapas de Avaliação →
│  Classificação → Inscrição → Anexos → Conteúdo → Revisão
│  ↓  Submeter para revisão            ◆ congela a revisão
│
├─ FASE 3 · APROVAR ─────────────────────────────── Homologador
│  Homologar (com fundamento)   ⟲ Devolver para elaboração
│                               ⟲ Revogar homologação
│  ↓
├─ FASE 4 · PUBLICAR ────────────────────────────── Publicador
│  Publicar (autoridade signatária)     ■ SEM RETORNO
│  → Edital público e imutável, PDF gerado com hash
│  → aparece na vitrine pública
│
├─ FASE 5 · RECEBER INSCRIÇÕES ──────────────────── Candidato
│  Entrar por código → escolher vaga e modalidade → dados →
│  documentos → fatos exigidos → revisar → Enviar inscrição
│  → Comprovante com protocolo   ■ fatos declarados congelam no envio
│
├─ FASE 6 · ORGANIZAR A COMISSÃO ───────────────── Gestor        ∥ paralela à 5
│  Comissão do Processo (presidente + membros) → Alocação por Etapa
│
├─ FASE 7 · DISTRIBUIR ──────────────────────────── Presidente
│  Propor distribuição (rodízio) → Confirmar esta distribuição
│  ⟲ Registrar impedimento    ⟲ Retirar as selecionadas
│
├─ FASE 8 · AVALIAR ─────────────────────────────── Avaliadores
│  Minhas Etapas → Minha Mesa → inscrição a inscrição
│  forma DECISÓRIA (rótulos do Edital + parecer)  ou  PONTUADA (nota)
│  Salvar sem concluir → Concluir avaliação   ■ concluída vira leitura
│  ⟲ Reabertura é ato da presidência (Conclusões preservadas)
│
├─ FASE 9 · CONSOLIDAR ──────────────────────────── Presidente
│  ⟲ Registrar ocorrência (elimina quem não foi avaliado)
│  Prontidão da Etapa → Consolidar resultados
│  → Resultado da Etapa: Habilitada | Eliminada     ■ SEM RETORNO por inscrição
│
├─ FASE 10 · CLASSIFICAR ────────────────────────── Presidente
│  Ordenação do marco: cálculo + desempate → Emitir ordem
│  → Ato de classificação                            ■ imutável
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
│  Recursos recebidos → peça → Admitir | Não admitir → Julgar
│  quatro espécies:
│    · Indeferir                    → nenhum efeito
│    · Deferir fixando a correção   → Resultado sucessor (append-only)
│    · Deferir determinando reavaliação → ⛔ NÃO UTILIZAR nesta versão (§H.2)
│    · Determinar providência a jusante → pendência registrada
│  ■ non reformatio in pejus: a correção não pode piorar quem recorreu
│  ■ julgador que atuou no ato atacado está impedido
│
├─ FASE 14 · REFAZER E REPUBLICAR ───────────────── Presidente + Publicador
│  Resultado superado → classificação fica OBSOLETA →
│  Emitir ato sucessor (com motivo) → nova Publicação sucede a anterior
│  ■ a publicação anterior permanece consultável, dizendo que foi sucedida
│
├─ FASE 15 · DEFINITIVO ─────────────────────────── Publicador
│  Publicar resultado DEFINITIVO — porta de fato, cinco impedimentos:
│  recurso pendente · reingresso pendente · reavaliação pendente ·
│  providência pendente · janela recursal ainda aberta
│
└─ FASE 16 · ENCERRAR ───────────────────────────── Gestor
   Encerrar Edital (motivo)  → Encerrar Processo     ■ SEM RETORNO
   ⟲ Cancelar Edital / Processo — interrupção, não encerramento
```

### B.3 O que corre em paralelo

- **Retificação** — ciclo próprio e completo (elaborar → submeter → homologar → publicar), disponível
  a qualquer momento com o Edital publicado, inclusive com inscrições em andamento e inclusive
  depois de resultados emitidos. Tem **vigência**: uma Retificação pode entrar em vigor no futuro.
- **Composição da comissão** (fase 6) roda em paralelo às inscrições (fase 5).
- **Avaliação de várias Etapas** roda em paralelo; cada Etapa consolida no seu tempo.
- **Recursos** de vários candidatos correm juntos e são julgados um a um.
- **Auditoria** é consultável em qualquer instante, por Processo e por Edital.

### B.4 Pontos sem retorno

O manual precisa marcá-los com o mesmo símbolo, sempre:

| Ato | O que trava |
|---|---|
| **Submeter para revisão** | O formulário fecha; a revisão congela |
| **Publicar Edital** | Imutável; correção só por Retificação |
| **Publicar Retificação** | Idem; a versão consolidada nasce |
| **Enviar inscrição** | Os fatos declarados congelam com o valor do envio |
| **Concluir avaliação** | Vira leitura; só a presidência reabre |
| **Registrar ocorrência** | Elimina, e não se desfaz |
| **Consolidar o Resultado da Etapa** | Não reconsolida; corrigir exige recurso |
| **Emitir ordem** | Ato imutável; corrigir exige ato sucessor |
| **Publicar resultado** | Público; corrigir exige publicação sucessora |
| **Encerrar / Cancelar** | Nenhuma transição posterior |

### B.5 Atos históricos — o que nunca desaparece

Publicações, documentos publicados, versões consolidadas, atos administrativos, conclusões
preservadas, Resultados de Etapa, atos de classificação e suas posições, publicações de resultado
e situações divulgadas, recursos, juízos de admissibilidade e decisões, e a trilha de auditoria.
**Nada é excluído.** Encerrar e cancelar são atos motivados que preservam tudo.

### B.6 De quem é cada ação

- **Do candidato:** entrar, escolher vaga e modalidade, preencher, anexar, declarar, enviar,
  acompanhar, recorrer, gerir os próprios e-mails, vincular participação anterior.
- **Da comissão:** distribuir (presidência), avaliar (membros), impedir, registrar ocorrência,
  consolidar, emitir a ordem classificatória, reabrir avaliação.
- **Da autoridade institucional:** criar e ativar o Processo, criar o Edital, homologar, publicar
  Edital e Retificação, divulgar resultado, julgar recurso, encerrar e cancelar.

---

## C. Arquitetura de capítulos

Nenhum capítulo é numerado por spec. A organização atende às duas entradas do leitor: quem quer
**entender** desce pelas Partes 1 e 2; quem precisa **fazer agora** entra pela Parte 3 (trilha do
seu papel) ou pela Parte 4 (a tarefa pelo nome).

```
PARTE 1 — ENTENDER O SISTEMA          (leitura linear, 5 capítulos curtos)
PARTE 2 — AS FASES DO PROCESSO        (o corpo do manual, 12 capítulos, ordem cronológica)
PARTE 3 — TRILHAS POR PAPEL           (8 páginas-roteiro, sem conteúdo próprio: apontam)
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
| C-05 | Cinco ideias que explicam todo o resto |

### Parte 2 — As fases do processo

| # | Capítulo | Fase |
|---|---|---|
| C-06 | Abrir o Processo Seletivo e criar o Edital | 1 |
| C-07 | Elaborar o Edital I — identificação, perfis, vagas e cronograma | 2 |
| C-08 | Elaborar o Edital II — etapas de avaliação e regra de classificação | 2 |
| C-09 | Elaborar o Edital III — inscrição, anexos, conteúdo e revisão final | 2 |
| C-10 | Submeter, homologar e publicar | 3–4 |
| C-11 | O período de inscrições, visto de dentro | 5 |
| C-12 | Inscrever-se — o manual do candidato | 5 |
| C-13 | Montar a comissão e alocar por Etapa | 6 |
| C-14 | Distribuir o trabalho | 7 |
| C-15 | Avaliar — o manual do avaliador | 8 |
| C-16 | Consolidar o resultado de cada Etapa | 9 |
| C-17 | Classificar | 10 |
| C-18 | Divulgar o resultado | 11 |
| C-19 | Recursos — interpor, admitir e julgar | 12–13 |
| C-20 | Refazer e republicar depois de um recurso | 14–15 |
| C-21 | Encerrar o certame | 16 |

*(São 16 capítulos na Parte 2; a numeração acima já os contempla — C-07 a C-09 são o assistente
dividido em três, que é o trecho mais longo do manual.)*

### Parte 3 — Trilhas por papel

`T-01` Gestor · `T-02` Elaborador · `T-03` Homologador · `T-04` Publicador ·
`T-05` Presidente da comissão · `T-06` Avaliador · `T-07` Julgador de recursos ·
`T-08` Candidato

### Parte 4 — Tarefas frequentes

`R-01` Corrigir algo num Edital já publicado (Retificação) · `R-02` Encerrar as inscrições antes
do prazo · `R-03` Trocar um avaliador no meio da Etapa · `R-04` Reabrir uma avaliação já concluída ·
`R-05` Conferir quantas inscrições chegaram e o que veio · `R-06` Baixar o comprovante ou o PDF
oficial · `R-07` Acrescentar um e-mail à conta do candidato · `R-08` Vincular uma participação
anterior · `R-09` Emitir um ato de classificação sucessor · `R-10` Consultar quem fez o quê
(auditoria)

### Parte 5 — Situações excepcionais

`X-01` O Edital voltou para elaboração (devolução) · `X-02` A homologação foi revogada ·
`X-03` Cancelar em vez de encerrar — e por que não é a mesma coisa · `X-04` Um candidato não pôde
ser avaliado (ocorrência) · `X-05` Um avaliador está impedido · `X-06` Deu empate ·
`X-07` "Este ato está obsoleto" — o que aconteceu e o que fazer · `X-08` A publicação definitiva
está bloqueada · `X-09` O prazo de recurso acabou · `X-10` Um recurso não pode piorar a situação
de quem recorreu

### Parte 6 — Referência

`G-01` Glossário · `G-02` Mapa de todas as telas · `G-03` O que o sistema **não** faz hoje ·
`G-04` Perguntas frequentes · `G-05` Nota para administradores (única seção com vocabulário técnico)

---

## C.bis — Detalhamento de cada capítulo

Formato: **público · objetivo · pré-requisitos · assuntos · telas · screenshots · exemplo ·
alertas · o que NÃO entra.**

### C-01 · O que este sistema faz (e o que ele não faz)

- **Público:** todos, inclusive quem só vai ler uma vez.
- **Objetivo:** o leitor sai sabendo que o sistema conduz um certame do Edital à divulgação do
  resultado, e que **uma publicação realizada não é reescrita** — correções geram atos novos, por
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
- **Alertas:** 💡 quem digita o endereço raiz cai na vitrine pública, não na gestão.
- **NÃO entra:** como entrar (§H.1 — não há login institucional documentável ainda).

### C-03 · O ciclo completo em um mapa

- **Público:** todos.
- **Objetivo:** dar ao leitor a figura que ele vai revisitar o manual inteiro.
- **Assuntos:** as 16 fases, quem pratica cada uma, o que corre em paralelo, os pontos sem retorno.
- **Telas:** nenhuma — este capítulo é **diagrama**, não captura.
- **Screenshots:** nenhum. Ilustração vetorial (§G.4).
- **Alertas:** ✅ um quadro "onde estou" que reaparece no topo de cada capítulo da Parte 2.
- **NÃO entra:** detalhe de qualquer fase.

### C-04 · Quem faz o quê — e por que ninguém faz tudo

- **Público:** todos, sobretudo gestores.
- **Objetivo:** entender a segregação de funções como regra de trabalho, não como burocracia.
- **Assuntos:** os seis papéis; a presidência e a atribuição como vínculos, não papéis; por que quem
  elabora não homologa; por que quem elaborou **e** homologou não publica; por que julgar recurso é
  papel isolado.
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
  pessoas do §A.3, com os nomes do certame-exemplo.
- **Alertas:** ⚠ ação cinzenta com um motivo ao lado não é defeito — é o sistema avisando antes.
  ⚠ acumular papéis é legítimo; acumular **atos do mesmo caso** é o que o sistema recusa.
- **NÃO entra:** nomes de permissões em formato técnico; a lista completa de permissões por papel
  (vai para `G-05`).

### C-05 · Cinco ideias que explicam todo o resto

- **Público:** todos.
- **Objetivo:** entregar de uma vez os cinco conceitos sem os quais todo o resto parece arbitrário.
- **Assuntos:** (1) publicação é imutável; (2) retificação corrige por cima e tem vigência;
  (3) versão vigente ≠ versão histórica; (4) ato emitido é fotografia, não fórmula viva;
  (5) tudo fica registrado.
- **Telas:** detalhe do Edital publicado com a lista de documentos publicados; ato de classificação
  marcado como sucedido.
- **Screenshots:** SS-006, SS-007.
- **Alertas:** 🔎 caixa "O que muda depois?" em cada uma das cinco.
- **NÃO entra:** hash, assinatura, estrutura de dados.

### C-06 · Abrir o Processo Seletivo e criar o Edital

- **Público:** gestor.
- **Objetivo:** sair com um Processo ativo e um Edital em elaboração.
- **Pré-requisitos:** ter o papel de gestor.
- **Assuntos:** Processo × Edital; código institucional; ativar; numeração do Edital única por ano.
  **(S-00)** O Processo **nasce com o primeiro Edital**, numa tela só — o capítulo ensina a tela como
  ela é. Acrescentar um segundo Edital a um Processo existente é capacidade do domínio **sem tela**;
  não se promete aqui, e o fato vai em uma linha para `G-03`.
- **Telas:** lista de Processos; Novo Processo e primeiro Edital; detalhe do Processo.
- **Screenshots:** SS-008, SS-009. **(S-00)** `SS-010` foi removida: a tela não existe.
- **Exemplo:** *Processo Seletivo Simplificado 2026 · Edital 03/2026 — Auxiliar de Biblioteca*.
- **Alertas:** 🕒 ative o Processo antes de publicar o Edital.
- **NÃO entra:** comissão (é a fase 6, e tem capítulo).

### C-07 · Elaborar o Edital I — identificação, perfis, vagas e cronograma

- **Público:** elaborador.
- **Objetivo:** os três primeiros passos do assistente prontos e sem pendências.
- **Pré-requisitos:** Edital em elaboração.
- **Assuntos:** o assistente e seus nove passos; estados dos passos (pendente / pronta para
  revisar / concluída); Perfil de Vaga; modalidades e reserva; vagas imediatas × cadastro de
  reserva; requisitos; Cronograma e Eventos; **qual Evento é o período de inscrições**.
- **Telas:** passo Identificação; passo Perfis (com linha de modalidade); passo Cronograma.
- **Screenshots:** SS-011, SS-012, SS-013, SS-014.
- **Exemplo:** um perfil com ampla concorrência + PPI, 2 vagas + cadastro de reserva.
- **Alertas:** ⚠ sem um Evento marcado como período de inscrições, o Edital publica e **ninguém
  consegue se inscrever**. 💡 o assistente pode ser percorrido fora de ordem, mas cada passo
  depende do anterior para oferecer escolhas — siga a ordem na primeira vez.
- **NÃO entra:** etapas de avaliação e classificação (C-08).

### C-08 · Elaborar o Edital II — etapas de avaliação e regra de classificação

- **Público:** elaborador. **É o capítulo mais difícil do manual.**
- **Objetivo:** compor uma regra de avaliação e de classificação que o sistema consiga executar e
  que um leitor do Edital consiga reconstituir.
- **Pré-requisitos:** perfis e cronograma prontos.
- **Assuntos:** Etapa de Avaliação; **as duas formas** — pontuada (nota, faixa, nota mínima) e
  decisória (dois rótulos escolhidos pelo Edital, p.ex. Deferida/Indeferida); peso; vínculo da
  Etapa a um Evento do cronograma; **Marco Classificatório**; quais Etapas o marco combina;
  normalização, escala e arredondamento; critérios de desempate e o que cada um compara; o que
  acontece quando o dado do desempate falta; **fatos declarados**; **a janela recursal declarada no
  marco**.
- **Telas:** passo Etapas de Avaliação; passo Classificação (marco + critérios).
- **Screenshots:** SS-015, SS-016, SS-017, SS-018.
- **Exemplo:** Etapa 1 decisória (Deferida/Indeferida) + Etapa 2 pontuada (0–100, mínima 60, peso 2);
  marco FINAL combinando as duas, três critérios de desempate, recurso em 5 dias corridos.
- **Alertas:** ⚠ **declare a janela recursal aqui.** Se o marco não disser que admite recurso e por
  quantos dias, o resultado definitivo depois exigirá uma declaração escrita de encerramento de
  prazo — e recurso nenhum terá prazo computável. ⚠ um critério de desempate precisa dizer *o que*
  compara.
- **NÃO entra:** como se calcula a nota final passo a passo (vai para C-17).

### C-09 · Elaborar o Edital III — inscrição, anexos, conteúdo e revisão final

- **Público:** elaborador.
- **Objetivo:** fechar a composição e submeter sem pendências impeditivas.
- **Assuntos:** Documento Exigido (por perfil e por modalidade); vínculo de um documento a um
  **modelo oficial**; Anexo do Edital (rótulo editorial + arquivo); seções textuais do Conteúdo;
  o painel "O que falta para submeter"; "O que será congelado na submissão"; a prévia do documento.
- **Telas:** passo Inscrição; passo Anexos; passo Conteúdo; passo Revisão; Prévia do Edital.
- **Screenshots:** SS-019, SS-020, SS-021, SS-022, SS-023.
- **Exemplo:** três documentos exigidos, um deles só para PPI, com o modelo de autodeclaração
  anexado.
- **Alertas:** ⚠ remover um anexo apaga o arquivo do rascunho — reenviar é o único caminho de volta.
  ✅ ao terminar: nenhuma pendência impeditiva no painel de revisão.
- **NÃO entra:** a submissão em si (C-10).

### C-10 · Submeter, homologar e publicar

- **Público:** elaborador, homologador, publicador — os três, na ordem em que atuam.
- **Objetivo:** levar o Edital de "Em elaboração" a "Publicado" com as três pessoas certas.
- **Pré-requisitos:** composição sem pendências impeditivas.
- **Assuntos:** submeter e o que congela; a trilha de estados do Edital; homologar com fundamento;
  devolver com motivo; revogar homologação; publicar com autoridade signatária; o documento
  publicado; a segregação que impede a mesma pessoa de fechar o ciclo; "Quem atuou".
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
  **não** pode fazer com uma inscrição.
- **Telas:** Inscrições recebidas; detalhe da inscrição recebida.
- **Screenshots:** SS-030, SS-031.
- **Alertas:** ⚠ rascunho não é inscrição; o contador só conta o que foi enviado.
  ⚠ dado pessoal — consulte só o necessário.
- **NÃO entra:** avaliação.

### C-12 · Inscrever-se — o manual do candidato

- **Público:** candidato e público anônimo. **Deve funcionar isolado do resto do manual.**
- **Objetivo:** o candidato encontra a vaga, se inscreve, envia e guarda o comprovante.
- **Pré-requisitos:** nenhum.
- **Assuntos:** a vitrine e a página da seleção; ler o Edital e baixar anexos; entrar por código de
  e-mail (sem senha); escolher vaga e modalidade; preencher; enviar documentos; declarar os fatos
  exigidos; revisar; enviar; o comprovante e o protocolo; retomar um rascunho; o aviso "o Edital foi
  atualizado"; acompanhar; gerir os e-mails da conta; vincular participação anterior.
- **Telas:** vitrine; página da seleção; Entrar; Informe o código; Minhas inscrições; Sua inscrição;
  Revisar e enviar; Comprovante; Acompanhar; Acesso à conta.
- **Screenshots:** SS-032 a SS-042.
- **Exemplo:** Ana concorre à ampla; Carla concorre por PPI e vê aparecer a autodeclaração.
- **Alertas:** ⚠ os dados exigidos pelo Edital **congelam no envio** e não mudam depois.
  ⚠ enquanto não clicar em *Enviar inscrição*, ninguém recebeu nada. 🕒 confira o prazo no cartão.
- **NÃO entra:** recurso (C-19 tem a parte do candidato; aqui só uma remissão).

### C-13 · Montar a comissão e alocar por Etapa

- **Público:** gestor.
- **Objetivo:** deixar cada Etapa com gente designada.
- **Pré-requisitos:** Processo ativo, Edital publicado com Etapas.
- **Assuntos:** a comissão pertence ao **Processo**, não ao Edital; presidente e membros; adicionar
  vários de uma vez; a matriz de alocação por Etapa; inativar membro; alocações órfãs.
- **Telas:** Comissão do Processo; confirmação; Alocação por Etapa.
- **Screenshots:** SS-043, SS-044, SS-045.
- **Alertas:** 👤 designar a presidência não dá poderes de gestão, e ser gestor não dá a presidência.
  ⚠ sem alocação a Etapa não pode ser distribuída.
- **NÃO entra:** distribuir inscrições (C-14).

### C-14 · Distribuir o trabalho

- **Público:** presidente da comissão.
- **Objetivo:** cada inscrição com um avaliador responsável, em cada Etapa.
- **Pré-requisitos:** inscrições recebidas e alocação feita.
- **Assuntos:** onde a presidência encontra a Etapa (**o caminho não é anunciado — ver §H.13**);
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
  leitura; o que fazer se errou.
- **Telas:** Minhas Etapas; Minha Mesa; Inscrição na Mesa (decisória e pontuada).
- **Screenshots:** SS-050, SS-051, SS-052, SS-053.
- **Alertas:** ⛔ **concluir não se desfaz por você** — reabrir é ato da presidência.
  ⚠ você só vê o que lhe foi atribuído; isso é proposital.
- **NÃO entra:** consolidação, classificação, recursos.

### C-16 · Consolidar o resultado de cada Etapa

- **Público:** presidente da comissão.
- **Objetivo:** transformar avaliações concluídas em Resultados oficiais da Etapa.
- **Pré-requisitos:** avaliações concluídas.
- **Assuntos:** prontidão × oficial; registrar ocorrência (quem não pôde ser avaliado); consolidar
  em lote; Habilitada × Eliminada; o que decide a consequência em cada forma; eliminada numa Etapa
  não aparece na Etapa seguinte; Conclusões preservadas e reabertura; a tela de Resultados da Etapa.
- **Telas:** Registrar ocorrência (2 passos); prontidão antes de consolidar; Resultados da Etapa;
  Conclusões preservadas.
- **Screenshots:** SS-054, SS-055, SS-056, SS-057.
- **Alertas:** ⛔ **consolidar não se refaz** — a correção depois disso é matéria de recurso.
  ⚠ ocorrência elimina; leia a revisão antes de "Registrar mesmo assim".
- **NÃO entra:** classificação.

### C-17 · Classificar

- **Público:** presidente da comissão; auditor como leitor.
- **Objetivo:** emitir a ordem classificatória e saber explicá-la.
- **Pré-requisitos:** Etapas do marco consolidadas.
- **Assuntos:** o marco e seu universo; a ordem calculada antes de emitir; como a nota combinada se
  forma; o desempate critério a critério e a proveniência de cada par; empate residual e posição
  compartilhada; participantes sem posição; emitir; o ato como fotografia; obsolescência
  (regra mudou / universo mudou); ato sucessor.
- **Telas:** Ordenação do marco; Ato de classificação (posições + proveniência); ato obsoleto com
  divergências.
- **Screenshots:** SS-058, SS-059, SS-060, SS-061.
- **Exemplo:** 1º Ana 95 · 2º Bruno 88 · 3º Carla 82 · 4º Diego 75, com empate desfeito por fato
  declarado.
- **Alertas:** 🔎 quem foi eliminado em Etapa anterior à última **não aparece** entre "considerados
  sem posição" — essa história é contada pelos Resultados de Etapa. ⚠ emitir com a página velha é
  recusado.
- **NÃO entra:** divulgação.

### C-18 · Divulgar o resultado

- **Público:** publicador; candidato e público como leitores.
- **Objetivo:** publicar um resultado preliminar ou definitivo e saber onde ele aparece depois.
- **Pré-requisitos:** ato de classificação vigente.
- **Assuntos:** a prévia e o que será divulgado; preliminar × definitiva; a revalidação na
  confirmação; a página pública estável; o documento oficial; a situação de cada participante na
  área do candidato; o histórico de publicações do marco; sucessão de publicação.
- **Telas:** Prévia da publicação; Resultado divulgado (público, desktop e celular); Acompanhar
  (candidato); Resultados divulgados (histórico).
- **Screenshots:** SS-062 a SS-067.
- **Alertas:** ⚠ **quem emitiu o ato não é quem o publica.** ⚠ a prévia envelhece: se algo mudar
  entre abrir e confirmar, a confirmação é recusada — e isso é proteção, não erro.
  🔎 nenhum candidato é notificado; a divulgação é passiva (§H.5).
- **NÃO entra:** recursos.

### C-19 · Recursos — interpor, admitir e julgar

- **Público:** candidato (primeira metade), julgador (segunda metade).
- **Objetivo:** o candidato recorre no prazo; o julgador admite e julga com efeito correto.
- **Pré-requisitos:** resultado divulgado, ou Resultado de Etapa visível ao candidato.
- **Assuntos:** o que pode ser atacado (a publicação, ou um Resultado de Etapa); a janela recursal;
  o protocolo do recurso; admissibilidade ≠ mérito; **as três espécies de decisão utilizáveis** e o
  efeito de cada uma; impedimento do julgador; a proibição de agravar a situação de quem recorreu;
  onde o candidato acompanha.
- **Tratamento da quarta espécie:** *Deferir determinando reavaliação* **sai do fluxo principal**.
  Ela não é ensinada como opção disponível, não entra na tabela de espécies e não recebe
  procedimento. Aparece uma única vez, ao fim do capítulo, numa **caixa de limitação conhecida**
  com o texto: *"⛔ Não utilize esta opção nesta versão do sistema."* — seguido de uma frase
  dizendo o que acontece se alguém a usar (o marco fica impedido de chegar a resultado definitivo)
  e da remissão a `G-03`. **(S-00)** Essa caixa usa o componente
  **`Limitação conhecida desta versão`** do §G.3, e **não** o callout `⛔`: o glifo permanece na
  frase, mas o bloco não é do tipo "ato sem retorno" — uma capacidade que não deve ser usada é outra
  coisa, e misturar as duas apagaria a distinção que se pede ao leitor que memorize. O manual não normaliza uma capacidade que não fecha operacionalmente.
- **Telas:** Acompanhar → Recorrer; Recurso (candidato); Recursos recebidos; peça do recurso;
  Admissibilidade; Julgar.
- **Screenshots:** SS-068 a SS-074.
- **Alertas:** ⛔ **Não utilize "Deferir determinando reavaliação" nesta versão.** A decisão fica
  registrada, nada a cumpre, e o marco passa a ficar permanentemente impedido de chegar a
  resultado definitivo — §H.2. Redação categórica e sem contorno sugerido: **não há** contorno.
  ⚠ julgar é papel próprio: quem atuou no ato atacado está impedido.
  ⚠ a espécie escolhida determina o efeito — indeferir não muda nada, corrigir cria um Resultado
  novo, providência a jusante só registra pendência.
- **NÃO entra:** o refazimento do resultado (C-20).

### C-20 · Refazer e republicar depois de um recurso

- **Público:** presidente da comissão e publicador.
- **Objetivo:** cumprir uma decisão recursal até a nova divulgação.
- **Assuntos:** o Resultado sucessor citando o anterior e a decisão; o original permanece;
  reabilitação e progressão retroativa; a classificação fica obsoleta com o motivo certo; emitir o
  ato sucessor; a publicação sucessora; a anterior continua consultável dizendo que foi sucedida;
  **os cinco impedimentos da publicação definitiva**; a declaração de encerramento de prazo quando
  o marco não declarou janela.
- **Telas:** Resultados da Etapa depois dos recursos; ordenação obsoleta; ato sucessor; prévia da
  segunda publicação; publicação anterior preservada; recusa da definitiva.
- **Screenshots:** SS-075 a SS-080.
- **Alertas:** ⚠ a publicação fica bloqueada — inclusive como preliminar — enquanto houver quem
  foi reabilitado e ainda não tem Resultado na Etapa seguinte.
- **NÃO entra:** o julgamento em si.

### C-21 · Encerrar o certame

- **Público:** gestor.
- **Objetivo:** fechar Edital e Processo com o registro correto.
- **Assuntos:** encerrar × cancelar; o motivo; o que permanece consultável; quando encerrar em
  relação ao resultado definitivo (**o sistema não orienta — §H.7**).
- **Telas:** confirmação de encerramento; detalhe encerrado.
- **Screenshots:** SS-081, SS-082.
- **Alertas:** ⚠ depois de encerrado nenhuma Retificação pode ser publicada.
  ⚠ cancelar registra interrupção administrativa — não é a mesma coisa.
- **NÃO entra:** nomeação, convocação, posse — não existem (§H.7).

### G-03 · O que o sistema não faz hoje

Ficha própria porque esta seção passou a carregar peso editorial: ela é o **destino único** das
limitações que não interrompem nenhuma tarefa (§H.0).

- **Público:** gestor e quem decide processo institucional; secundariamente, quem responde dúvida
  de candidato.
- **Objetivo:** que ninguém procure por horas uma função que não existe, e que a instituição saiba
  o que precisa resolver por fora do sistema.
- **Pré-requisitos:** nenhum; é seção de referência, alcançável do menu e por remissão.
- **Assuntos:** consulta pública por data; Resultado de Etapa não público; ausência de comunicação
  ativa; ausência de corte e progressão automática entre Etapas; o ciclo terminar na divulgação;
  múltiplos marcos sem orientação; capacidades sem tela — **(S-00)** entre elas, **acrescentar um
  segundo Edital a um Processo já criado**, que existe no domínio e não tem tela; e — em caixa
  própria e destacada — a espécie de decisão recursal que não deve ser usada.
- **Telas:** nenhuma.
- **Screenshots:** nenhum.
- **Alertas:** nenhum. Esta seção **é** o alerta.
- **Forma:** uma lista de fatos em linguagem neutra, cada um com uma frase de "o que fazer no
  lugar" quando houver alternativa institucional (avisar candidatos por outro canal, publicar o
  intermediário fora do sistema). Sem tom de desculpa e sem prometer data.
- **NÃO entra:** defeitos de UX que o manual já mitiga (§H.8), distinções que são conteúdo e não
  falta (§H.12), nada sobre o repositório ou sobre specs, e nenhum item que já tenha alerta inline
  no capítulo da tarefa — nesse caso `G-03` apenas o repete em uma linha, para quem chegou por aqui.

---

## D. Mapa papel × capítulo

Legenda: ● capítulo obrigatório · ○ leitura recomendada · — não se aplica.

> **Numa equipe pequena, leia pela coluna, não pela linha.** Uma pessoa que acumula elaborador,
> publicador e presidência lê a **união** das três colunas — e é para isso que os capítulos são
> curtos e as trilhas da Parte 3 são páginas de roteamento (§A.3).

| Capítulo | Gestor | Elabor. | Homol. | Public. | Presid. | Avaliad. | Julgad. | Candid. | Auditor |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| C-01 O que o sistema faz | ● | ● | ● | ● | ● | ● | ● | ○ | ● |
| C-02 As duas portas | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| C-03 O ciclo em um mapa | ● | ● | ● | ● | ● | ○ | ○ | ○ | ● |
| C-04 Quem faz o quê | ● | ● | ● | ● | ● | ○ | ● | — | ● |
| C-05 Cinco ideias | ● | ● | ● | ● | ● | ○ | ● | ○ | ● |
| C-06 Abrir o Processo | ● | ○ | — | — | ○ | — | — | — | ○ |
| C-07 Elaborar I | ○ | ● | ● | ○ | — | — | — | — | ○ |
| C-08 Elaborar II | ○ | ● | ● | ○ | ● | ○ | ○ | — | ○ |
| C-09 Elaborar III | ○ | ● | ● | ○ | — | — | — | — | ○ |
| C-10 Submeter/homologar/publicar | ● | ● | ● | ● | — | — | — | — | ● |
| C-11 Inscrições por dentro | ● | — | — | — | ○ | — | — | — | ○ |
| C-12 Inscrever-se | ○ | ○ | — | — | — | — | — | ● | — |
| C-13 Comissão e alocação | ● | — | — | — | ● | ○ | — | — | ○ |
| C-14 Distribuir | ○ | — | — | — | ● | ○ | — | — | ○ |
| C-15 Avaliar | — | — | — | — | ● | ● | ○ | — | ○ |
| C-16 Consolidar | ○ | — | — | — | ● | ○ | ○ | — | ● |
| C-17 Classificar | ○ | ○ | — | ○ | ● | — | ● | — | ● |
| C-18 Divulgar | ○ | — | — | ● | ● | — | ○ | ○ | ● |
| C-19 Recursos | ○ | — | — | ○ | ○ | — | ● | ● | ● |
| C-20 Refazer e republicar | ○ | — | — | ● | ● | ○ | ● | ○ | ● |
| C-21 Encerrar | ● | — | — | ○ | — | — | — | — | ○ |

---

## E. Conceitos que precisam ser ensinados

**Momento de ensino:** `INÍCIO` = Parte 1, antes de qualquer tarefa · `USO` = no capítulo onde
aparece pela primeira vez · `SAIBA MAIS` = caixa lateral, não bloqueia a leitura.

| Conceito | Como dizer ao leitor | Quando |
|---|---|---|
| **Processo Seletivo** | O certame inteiro. Guarda um ou mais Editais e a comissão | INÍCIO |
| **Edital** | O documento normativo que rege a seleção. Nasce em elaboração e termina publicado | INÍCIO |
| **Publicação** | O ato que torna o Edital público e **imutável**. Não se reescreve | INÍCIO |
| **Retificação** | A correção de um Edital já publicado, com aprovação própria e data de vigência | INÍCIO |
| **Versão vigente / versão histórica** | O que vale hoje × o que valia numa data | INÍCIO |
| **Segregação de funções** | Quem elabora não homologa; quem elaborou e homologou não publica | INÍCIO |
| **Perfil de Vaga** | Cada cargo/função ofertado, com seus requisitos e vagas | USO (C-07) |
| **Modalidade** | Como se concorre dentro do perfil: ampla, PPI, PcD… | USO (C-07) |
| **Cadastro de reserva** | Vagas além das imediatas | USO (C-07) |
| **Cronograma / Evento** | As datas do certame; um Evento é o período de inscrições | USO (C-07) |
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
| **Autoridade signatária** | Quem assina institucionalmente a publicação | USO (C-10) |
| **Documento publicado** | O PDF oficial gerado na publicação | USO (C-10) |
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
| **Espécies de decisão** | Indeferir · corrigir · determinar reavaliação · providência | USO (C-19) |
| **Não agravar quem recorreu** | O recurso nunca piora a situação de quem o interpôs | USO (C-19) |
| **Resultado sucessor** | O Resultado corrigido, que nasce ao lado do original | USO (C-20) |
| **Trilha de auditoria** | O registro de quem fez o quê, quando e por quê | SAIBA MAIS (C-05), capítulo em G |
| **Acesso sem senha** | Entrar por código enviado ao e-mail | USO (C-12) |
| **Vincular participação anterior** | Reunir inscrições feitas com outro e-mail | SAIBA MAIS (C-12) |

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
| ⛔ | **Sem retorno** | Os dez atos irreversíveis do §B.4 | exatamente onde eles estão |
| 🔎 | **O que muda depois** | O efeito invisível de um ato | 1 por ato importante |
| ✅ | **Você terminou quando…** | Fecha capítulo e tarefa | 1 no fim de cada procedimento |

`⛔` é distinta de `⚠️` de propósito: hoje o produto trata dez atos como irreversíveis, e misturá-los
com avisos comuns apagaria a única distinção que o leitor precisa memorizar.

### G.3 Componentes

- **Cartão de papel** — bloco com ícone, nome do papel e "o que este papel pode fazer". Abre as
  trilhas da Parte 3.
- **Cartão de tela** — miniatura + nome da tela + endereço + "chega-se aqui por…". Usado no mapa de
  telas (`G-02`) e no topo de cada procedimento.
- **Linha do tempo horizontal** — as 16 fases, com a fase atual em destaque. Repetida, reduzida, no
  topo de cada capítulo da Parte 2 (o quadro "onde estou").
- **Linha do tempo vertical** — dentro de um capítulo, para sequências de ato (submeter → homologar
  → publicar), com o ator ao lado de cada nó.
- **Tabela de decisão** — "se acontecer X, faça Y". É o formato da Parte 5 inteira.
- **Passo numerado com captura** — a unidade do procedimento: número, uma frase imperativa, a
  captura anotada, e o resultado esperado.
- **(S-00) Bloco "Limitação conhecida desta versão"** — moldura própria, barra vermelha à
  esquerda, **sem marcador emoji**, com o veredicto em destaque na primeira frase. Existe para a
  capacidade que o sistema oferece e que não deve ser usada (`§H.2`, em C-19). **Não é um oitavo
  callout**: `⛔` continua reservado aos dez atos irreversíveis do §B.4, e este bloco é da família de
  "por trás disto". Forma fixada e demonstrada em `doc/manual/piloto/index.html`.
- **Bloco "por trás disto"** — recuado, cinza, tipograficamente menor. Só quando explicar o
  mecanismo evita erro: por que a prévia envelhece, por que a conclusão trava, por que a definitiva
  é recusada. Nunca fala de código.

### G.4 Ilustrações vetoriais (não capturas)

Quatro, e são as que carregam o manual: o mapa das 16 fases (C-03); o quadro de papéis e o que cada
um pode (C-04); o diagrama "elaborar × retificar" (C-05); e o diagrama do efeito das espécies de
decisão recursal (C-19) — três caminhos desenhados e o quarto grafado como indisponível, para que
a ilustração não ofereça o que o texto proíbe. Devem ser SVG, legíveis em claro e escuro, e nunca conter texto que só
existe na imagem.

### G.5 Navegação

- **(S-00) O quadro "onde estou"** é uma **faixa de dezesseis traços**, um por fase, com o traço
  atual mais alto e na cor de acento, e acima dela uma linha em texto:
  `Fase 11 de 16 · Divulgar · o trabalho é do publicador`. Entra logo abaixo do resumo e antes do
  primeiro callout, **só nos capítulos da Parte 2** — C-03 é a linha do tempo inteira e não a
  repete. É gerado de um único atributo (`data-fase`), o que garante o mesmo nome de fase em vinte
  capítulos. Dezesseis rótulos legíveis não cabem em 375 px sem rolagem horizontal, e este é o
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
| **Alerta inline + `G-03`** | Afeta a ação em curso: o leitor faria algo errado, ou ficaria esperando algo que não vem | H.1, H.2, H.4, H.5, H.9, H.10, H.11 |
| **Só `G-03`** | Fato relevante do produto que não muda nenhuma tarefa | H.3, H.6, H.7, H.13, H.14, **H.17 (S-00)** |
| **Nem no manual** | Achado interno; o manual o **resolve** escrevendo bem, ou ele é sobre o repositório | H.8, H.12, H.15 |

Detalhando as três exceções da última linha, porque são as que costumam vazar para o texto por
descuido:

- **H.8** (o caminho da presidência não é anunciado) — o manual **é** a mitigação. C-14 abre
  nomeando o caminho e pronto; escrever "o sistema não te leva até aqui" só ensinaria desconfiança.
  Fica no backlog de produto (§H.16), não no manual.
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

**H.2 · A decisão "deferir determinando reavaliação" não tem caminho de cumprimento.**
Achado E2E18-001, **aberto**, P1. A decisão é registrada, a Etapa passa a mostrar a pendência, e
não existe rota, botão ou tela que produza a reavaliação — a reabertura é recusada por regra. Como
reavaliação pendente é um dos fatos que barram a publicação definitiva, o marco fica
**permanentemente impedido** de chegar a resultado definitivo. *No manual:* a espécie **sai do
fluxo principal** — não é ensinada como opção, não entra na tabela de espécies e não recebe
procedimento; aparece uma vez só, em caixa de limitação conhecida ao fim de C-19, com o texto
*"⛔ Não utilize esta opção nesta versão do sistema"*, e repetida em uma linha em `G-03`. Não
inventar procedimento e não sugerir contorno: **não há** contorno. Ver também §H.16.

**H.3 · A consulta pública histórica não tem tela.**
O sistema sabe responder "qual era o conteúdo vigente em tal data" e "quais Retificações houve",
mas **só pela API**. A página pública da seleção mostra apenas o vigente e não lista Retificações.
*No manual:* C-05 ensina o conceito de versão vigente × histórica porque ele governa o
comportamento; e `G-03` registra que a consulta por data não tem interface.

**H.4 · O Resultado de Etapa não é público.**
O candidato vê o próprio ("Eliminada na Análise de requisitos") dentro da sua inscrição; o público
não vê Resultado de Etapa em lugar nenhum. Só o ato de classificação é divulgado. *No manual:*
dito explicitamente em C-16 e C-18.

**H.5 · Não há comunicação ativa.**
Ninguém é notificado de nada. E-mail é usado só para o código de acesso do candidato. Publicação é
passiva: quem não abrir a página não fica sabendo. *No manual:* alerta em C-18 e entrada em `G-03`.

**H.6 · Não há corte nem progressão automática entre Etapas.**
A feature existiria na 014, que não foi construída. Quem passa para a Etapa seguinte é quem tem
Resultado Habilitada; não há "aprovar os N primeiros". *No manual:* `G-03`.

**H.7 · O ciclo termina na publicação definitiva.**
Não existem homologação do resultado final, nomeação, convocação ou posse. E o sistema **não
orienta** quando encerrar o Edital em relação ao resultado. *No manual:* C-21 diz o que o
encerramento faz e declara que o momento é decisão institucional, não do sistema.

**H.8 · O caminho da presidência até distribuir e consolidar não é anunciado.**
Achado E2E15-016, aberto: "Minhas Etapas" do presidente diz que ele não tem Etapas atribuídas, e o
caminho real (Alocação por Etapa → Distribuir → painel da Etapa) só se descobre explorando. *No
manual:* **nada** — C-14 simplesmente abre nomeando o caminho, e a lacuna deixa de existir para
quem lê. Fica no backlog de produto (§H.16).

**H.9 · O rascunho não avisa que o período encerrou.**
Achado E2E15-007, aberto: com as inscrições encerradas, a revisão do rascunho ainda convida a
prosseguir. *No manual:* alerta em C-12 ("confira o prazo na página da seleção; o rascunho não te
avisa").

**H.10 · Um candidato deslogado recebe 404 na própria inscrição.**
Achado E2E15-013, aberto: um link guardado no celular vira beco em vez de convite a entrar. *No
manual:* dica em C-12 — entre primeiro, depois abra o link.

**H.11 · A Mesa aceita concluir avaliação de inscrição que já tem Resultado.**
Achado E2E15-003, aberto, **depende de decisão de governança**. Produz um par contraditório nos
registros. *No manual:* não documentar como comportamento; alerta em C-16 para a presidência
registrar ocorrência **antes** de as avaliações pendentes serem concluídas.

**H.12 · Recursos escolhem o objeto, e o vocabulário do objeto é sutil.**
Um recurso pode atacar a publicação **ou** um Resultado de Etapa, e o efeito de cada escolha é
diferente. Não é defeito; é uma distinção que o manual precisa ensinar com exemplo, em C-19.

**H.13 · Múltiplos marcos por perfil são aceitos e não têm jornada.**
A composição aceita mais de um marco classificatório por perfil; nada no produto sugere quando
usar. *No manual:* C-08 documenta um marco; `G-03` registra a capacidade sem orientação.

**H.14 · Capacidades sem tela.**
A prova de reprodutibilidade do ato de classificação e o teto de inscrições por candidato existem
no domínio e não têm interface (o teto só é configurável fora do assistente). *No manual:*
`G-03`, sem procedimento.

**H.17 · Acrescentar um Edital a um Processo já criado não tem tela. (S-00)**
Encontrado ao montar o certame do piloto. `/gestao/processos/criar` cria o Processo **junto com** o
primeiro Edital, numa tela só (`Criar Processo e Edital`); o detalhe do Processo não oferece a ação,
não há rota, e `add_edital` existe apenas na API. A capacidade é do domínio e a interface não a
alcança. *No manual:* **só `G-03`**, em uma linha, junto do `H.14` — o fato não muda o que o leitor
deve fazer agora, porque a tela o conduz corretamente pelo caminho que existe. C-06 perde a promessa
de ensinar "um Processo com vários Editais", e a captura `SS-010` sai do inventário.

**H.16 · Backlog de produto — o que não é problema de manual.**
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

### I.1 · As fases da produção

**Fase 0 — Piloto editorial.** Acima. Termina com um padrão aprovado e, se for o caso, com o §F
corrigido.

**Fase 1 — Coleta.** O certame do §F.1 percorrido **inteiro** pelo navegador, na ordem da jornada,
capturando as 88 imagens já sob o padrão aprovado. Banco limpo, seletor de identidade ligado,
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
| S-01 | Capturar as fases 1–5 | SS-001 a SS-042 | §F, padrão aprovado em S-00 |
| S-02 | Capturar as fases 6–11 | SS-043 a SS-067 | idem |
| S-03 | Capturar as fases 12–16 e as exceções | SS-068 a SS-087 | idem |
| S-04 | Esqueleto definitivo e sistema visual | Menu, busca, glossário com âncoras | §G, saída de S-00 |
| S-05 | As quatro ilustrações vetoriais | 4 SVG | §B, §G.4 |
| S-06 | C-06, C-07 | Abrir o Processo + Elaborar I | §C.bis, capturas de S-01 |
| S-07 | C-08 | Elaborar II (o capítulo difícil) | §C.bis, §E, o espécime de S-00 |
| S-08 | C-09, C-10 | Elaborar III + aprovar e publicar | §C.bis |
| S-09 | C-11 + revisão de C-12 | Inscrições por dentro; C-12 revisto | §C.bis, saída de S-00 |
| S-10 | C-13, C-14, C-15 | Comissão, distribuição e avaliação | §C.bis |
| S-11 | C-16, C-17 | Consolidação e classificação | §C.bis |
| S-12 | Revisão de C-18 + C-19 | C-18 revisto; recursos | §C.bis, §H.2 |
| S-13 | C-20 | Refazer e republicar | §C.bis |
| S-14 | C-21 + Parte 1 (C-01 a C-05, com C-03 revisto) | Encerramento e visão geral | tudo escrito até aqui |
| S-15 | Parte 3 (8 trilhas) | Páginas-roteiro | §D |
| S-16 | Parte 4 (10 tarefas) | Receitas | §C, capítulos prontos |
| S-17 | Parte 5 (10 situações) | Tabelas de decisão | §B.4, §H |
| S-18 | Parte 6, com `G-03` | Glossário, mapa de telas, limites, FAQ | §E, §H.0, §H |
| S-19 | Revisão final de consistência | Rótulos conferidos contra a interface ao vivo | — |

**Vinte sessões.** S-01 a S-03 exigem o sistema no ar e não podem ser paralelizadas entre si — o
certame é sequencial. Da S-06 em diante, cada sessão depende apenas do acervo de capturas, do
padrão aprovado em S-00 e deste documento; várias podem ser retomadas fora de ordem sem perda.

### I.3 · Duas decisões editoriais a preservar

Registradas aqui porque são exatamente as que uma sessão futura, sob pressão de prazo, tende a
desfazer sem perceber o que está desfazendo.

**Os personagens são um recurso pedagógico, não enfeite.** Gustavo abre o Processo, Elena redige,
Wagner homologa, Paula publica, Paulo preside, Alice e Otávio avaliam, Júlia julga o recurso, Ana e
os demais participam. O fio narrativo é o que torna a segregação de funções compreensível sem
explicá-la em abstrato: o leitor **vê** que são pessoas diferentes. Nenhuma sessão deve trocar
nomes por "o elaborador", "o usuário A".

**O manual é grande porque a jornada é grande.** São 21 capítulos principais porque o certame tem,
de fato, 16 fases e nove públicos. A tentação de comprimir isso num material de quinze páginas
produziria um manual que não serve para operar. A resposta correta ao tamanho já está na
arquitetura — conteúdo modular, capítulos curtos, entrada por papel e por tarefa —, e não em
eliminar complexidade que existe no produto. **Não reduzir escopo por parecer grande.**
