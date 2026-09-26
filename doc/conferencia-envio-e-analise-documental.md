# Conferência — envio e análise do documento condicional

Continuação do [achado do documento condicional no portal](achado-documento-condicional-no-portal.md),
que parou antes do envio. Aqui o percurso vai até a Mesa de quem analisa. É evidência para a decisão
sobre o recorte transversal e o documento obrigatório sob condição; **não é a decisão**.

Conferido em 25/09/2026, pela interface, no banco do estudo.

## Cenário

Edital **903/2026**, publicado antes da #161, com dois Perfis:

| Perfil | Modalidades |
|---|---|
| C1 — Curso de teste | AC, PcD, PPIQ |
| C2 — Segundo curso de teste | AC, PcD |

| Documento | Recorte publicado | Obrigatório |
|---|---|---|
| Documento de identidade | todos | sim |
| Laudo médico (PcD) | "Todos os Perfis" + modalidade "C1 · PcD" — o recorte ambíguo | sim |
| Autodeclaração de deficiência | todos, instrução "Apenas para quem concorre na modalidade PcD." | não |
| Autodeclaração étnico-racial | C1 · PPIQ | sim |

O PDF publicado diz: *"Dos candidatos concorrentes na modalidade Pessoas com Deficiência: a) Laudo
médico (PcD)"* — sem Perfil.

Três inscrições, enviadas pelo portal com PDFs de teste:

| Candidato | Perfil e modalidade | Protocolo | Enviou |
|---|---|---|---|
| Ana Teste Ampla | C1, AC | INS-2026-62W2R3E8 | identidade |
| Bruno Teste PcD | C1, PcD | INS-2026-WA8FYJZE | identidade e laudo |
| Bruno Teste PcD | C2, PcD | INS-2026-WTBAMDBH | identidade |

Para chegar à análise, uma Retificação antecipou o término das inscrições e tornou a Etapa decisória
("Análise documental", Deferida/Indeferida). A comissão teve uma presidente e um analista, com as três
inscrições distribuídas a ele.

## O que se observou

### 1. O que cada candidato vê como obrigatório, facultativo ou inaplicável

| Inscrição | Obrigatórios | Facultativo |
|---|---|---|
| Ana, C1, AC | identidade | autodeclaração de deficiência |
| Bruno, C1, PcD | identidade · laudo | autodeclaração de deficiência |
| Bruno, C2, PcD | identidade | autodeclaração de deficiência |

**"Inaplicável" não é dito a ninguém.** O documento fora do recorte simplesmente não aparece. A Ana
não é informada de que o laudo não se aplica a ela; o Bruno no C2 não é informado de que o laudo não
lhe é pedido. A autodeclaração de deficiência, cuja instrução diz "apenas PcD", aparece como
facultativa para a Ana, de ampla concorrência.

Na tela de documentos, a autodeclaração traz "(facultativo)". **Na Revisão, a marca desaparece:** ela
é listada como "Ainda não enviado.", com a mesma grafia do laudo obrigatório que falta.

### 2. Se a ausência bloqueia o envio

- **No C1, sim.** Com a identidade e sem o laudo, a Revisão lista *"Falta enviar: Laudo médico
  (PcD)."* e não oferece as declarações nem o botão de envio. O servidor também recusa
  (`missing_required_documents`), de modo que o bloqueio não depende da tela.
- **No C2, não.** O PcD envia com a identidade só. O Edital publicado exigia o laudo dele.
- **O facultativo nunca bloqueia**, em nenhum dos três casos.

Como o envio sem documento obrigatório é impedido, **um "PcD sem laudo" no C1 não chega à análise**.
Os únicos PcD sem laudo que a análise recebe são os que o portal dispensou: aqui, o C2.

### 3. Como o documento ausente aparece para quem analisa

Na Mesa, a lista é a dos requisitos **que o portal aplicou** àquela inscrição, sob a versão que ela
aceitou (`avaliacoes/application/mesa.py`, `requisitos_da_inscricao`):

| Inscrição | O que o analista vê |
|---|---|
| Ana, C1, AC | identidade (obrigatório, com arquivo) · autodeclaração de deficiência — "não apresentado" |
| Bruno, C1, PcD | identidade · laudo (os dois obrigatórios, com arquivo) · autodeclaração — "não apresentado" |
| Bruno, C2, PcD | identidade (obrigatório, com arquivo) · autodeclaração — "não apresentado" |

- **O laudo do Bruno no C2 não aparece.** Nem como "não apresentado", nem como inaplicável. O analista
  só sabe que ele faltava se conhecer o Edital e cruzar Perfil e modalidade de cabeça.
- O facultativo ausente sai como "não apresentado", sem marca; o obrigatório presente traz
  "obrigatório". A ausência da marca é o único sinal de que o documento era facultativo.
- **A instrução não chega à Mesa.** "Apenas para quem concorre na modalidade PcD" não aparece: a
  autodeclaração ausente da Ana (AC) e a do Bruno (PcD) se leem iguais.
- A lista da Mesa mostra só protocolo e situação. Perfil, modalidade e completude aparecem só dentro
  de cada inscrição.

A consulta administrativa ("Inscrições recebidas", do Gestor) faz a mesma leitura: o Bruno no C2 sai
como "1 de 1" documento, completo. O filtro de concorrência lista **"Ampla Concorrência" e "Pessoas com
Deficiência" duas vezes**, uma por Perfil, sem dizer de qual.

### 4. Se a análise diferencia "não se aplica", "não enviado" e "pendência"

**Não.** A Mesa tem dois estados por documento: com arquivo, e "não apresentado". "Não apresentado"
cobre o facultativo que o candidato escolheu não mandar e o facultativo que nem se aplicava a ele.
"Não se aplica" não existe como estado: o documento inaplicável some da lista, e com ele o que o
portal dispensou por erro de recorte. "Pendência" também não existe: o obrigatório ausente não
chega à Mesa, porque o envio o impede.

### 5. Se o analista pode registrar a inaplicabilidade, e com qual consequência

**Não há onde.** A conclusão é da inscrição inteira: Deferida ou Indeferida, com parecer em texto
livre. Não há juízo por documento.

- Deferir sem abrir documento é permitido: a Ana foi deferida sem nenhuma leitura registrada. A Mesa
  diz se o analista abriu algo ("1 de 2 abertos por você", marca "aberto"), mas não impede.
- Indeferir exige parecer: *"A conclusão Indeferida exige parecer, porque é ele que responde a um
  recurso."* O Bruno no C2 foi indeferido com o parecer *"Não apresentou o laudo médico exigido no
  item 4 do Edital…"*. **O parecer é o único lugar onde a ausência do laudo ficou registrada**, e
  ficou em prosa.
- Concluída, a avaliação só muda por reabertura da presidência, com motivo registrado.
- "Registrar ocorrência", da presidência, também não serve: ela elimina sem avaliação ("o Resultado
  nasce eliminado"), sem desfazer.

### 6. O que fica congelado após o envio

O comprovante e a inscrição guardam:

- protocolo, código de verificação, Perfil, concorrência;
- a versão do Edital aceita ("vigente desde 25/09/2026 às 14h50");
- os documentos **apresentados**, cada um com nome, tamanho, instante e SHA-256.

**Não fica registrado** o que foi pedido e não enviado, nem o que não se aplicava. O facultativo
ausente não aparece no comprovante. Não há como reconstruir, da inscrição, a lista que o portal
exigiu naquele instante, a não ser recalculando o recorte sobre a versão aceita. É o que a Mesa faz,
e é por isso que ela herda o erro do recorte.

A versão aceita governa o que o analista vê. Isso vem do código (`inscricao_para_avaliar` lê a
`versao_aceita`), e não da tela: neste cenário, a Retificação não mudou a lista de ninguém.

### 7. Os dois Perfis, com modalidades de mesmo nome e código

- O mesmo candidato, PcD nos dois Perfis, recebeu listas diferentes para a mesma modalidade: laudo
  obrigatório no C1, laudo ausente no C2.
- O PDF agrupava pelo nome e dizia "todo PcD"; o portal aplicava pela identidade e dizia "PcD do C1".
  A análise segue o portal. Neste percurso, o analista que leu o PDF indeferiu o candidato do C2
  **por um documento que o sistema nunca lhe pediu** — e nada na Mesa o avisou de que faltava.
- Os filtros da gestão repetem as modalidades por Perfil sem nomeá-lo.

## A Retificação que abriu a análise

- **A #161 impediu a Retificação** enquanto o laudo continuasse ambíguo: *"O Documento Exigido 'Laudo
  médico (PcD)' vale para todos os Perfis, mas está restrito à modalidade 'Pessoas com Deficiência'
  do Perfil 'C1'… Declare o Perfil 'C1' no documento — ou, para exigi-lo também nos outros Perfis,
  repita-o com a modalidade de cada um."* A contenção funciona: a ambiguidade não sobrevive à primeira
  Retificação.
- As duas saídas oferecidas são as do modelo atual. O seletor "Exigido apenas da modalidade" lista
  seis pares Perfil × Modalidade, e nenhum "PcD de todos os Perfis".
- A Retificação declarou o Perfil C1 no laudo. PDF e portal voltaram a concordar, **pela restrição**:
  o laudo deixou de ser exigido do PcD do C2 também no papel.

## Achados fora do escopo

**O resumo público da Retificação omite a mudança de recorte.** A Retificação declarou 7 alterações;
o portal mostra "O que mudou (6)". A que falta é a do laudo, que passou a valer só no C1 — a mais
consequente para o candidato. A causa: `publicacoes/domain/alteracoes.py` só nomeia, do Documento
Exigido, nome, instruções, obrigatoriedade, ordem e modelo; `profileId` e `modalityId` são
descartados em silêncio.

**A tela da Retificação mostra o caminho com UUID** sob o rótulo de cada alteração
(`/schedule/id=…/endAt`). É a família do item 4 do estudo de esforço, em outra tela.

## O que isto muda para a decisão

- **"Não se aplica" precisa de lugar**, ou pelo menos de fala. Hoje o documento inaplicável some na
  inscrição, no comprovante e na Mesa, e o que o portal dispensou por erro some junto. Qualquer
  recorte novo herda essa invisibilidade, a menos que ela seja decidida.
- **A análise recalcula o recorte; não lê o que foi pedido.** Se o recorte mudar de forma, por
  código ou por categoria, a Mesa muda junto, e as inscrições já enviadas passam a ser lidas pela
  regra nova sobre a versão antiga. Guardar na inscrição a lista exigida no envio é uma alternativa
  a pesar.
- **O condicional sobre o candidato não tem por onde passar.** O analista só tem a conclusão da
  inscrição e o parecer. "Informativo com verificação manual" é, na prática, o comportamento de hoje,
  com o custo medido aqui: a verificação fica em prosa, e a condição não aparece na Mesa.
- **O facultativo com instrução é pior do que parecia**: a instrução nem chega a quem analisa.
