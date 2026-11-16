# Estudo: a programação de entrevistas chega a quem avalia

**Data:** 16/11/2026, sobre a `main` em `619a4ae0`. **Natureza:** estudo, sem implementação, sem
spec e sem mudança de modelo. **Pedido:** fazer com que quem avalia receba a programação das
entrevistas pelas quais responde, sem planilha e com o mínimo de trabalho a mais para a comissão.

> **Segunda rodada.** A primeira rodada deste estudo, no mesmo dia, partiu da banca e recomendou um
> campo "E-mail da banca". O usuário questionou a premissa: a Etapa já organiza os avaliadores e a
> agenda, e o ponto de partida deveria ser ela. Esta rodada refez a investigação a partir da Etapa,
> **e a premissa do usuário se confirmou**, com uma correção: quem liga o avaliador ao candidato não
> é a alocação à Etapa, e sim a **Atribuição** da Distribuição. A recomendação mudou, e o campo
> "E-mail da banca" saiu da proposta. A primeira rodada não foi commitada; o que dela continua de pé
— a FR-084 como limite do e-mail, a FR-7229 sobre a sala, o recorte da Etapa por Modalidade — está
retomado abaixo.

> **Terceira rodada — a direção final, do usuário.** A investigação desta rodada fica como está; a
> recomendação muda em dois pontos, e a especificação é a
> [`179`](../specs/179-distribuicao-e-programacao-do-avaliador/spec.md):
>
> 1. **O e-mail não sai do escopo.** Ele foi a necessidade original, e não se pode presumir que todo
>    avaliador entre no GPS por conta própria. Fica como **segundo incremento**: um aviso individual,
>    sem lista, com o link para a Mesa, e a revisão da FR-084 como parte explícita dele.
> 2. **O conflito é integridade, e não aviso.** A distribuição recusa a atribuição que põe alguém em
>    dois lugares; a agenda pode criá-lo, mas nunca em silêncio, e ele impede o aviso a quem está
>    nele. A composição de quem avalia fica só na visão interna da comissão.
>
> Ordem: **Incremento 1** (distribuição coerente + programação na Mesa e em Minhas atividades),
> depois **Incremento 2** (aviso por e-mail). O esforço do primeiro deixou de ser "baixo": a recusa
> no lote e no rodízio e a revisão da FR-107 da `012` o fazem médio
> ([contracts/validacao.md](../specs/179-distribuicao-e-programacao-do-avaliador/contracts/validacao.md), §5).

## A resposta curta

**Não é preciso cadastrar e-mail nas bancas.** O GPS já sabe, por vínculos que existem e estão em
uso, **quais candidatos cada avaliador avalia** (a Atribuição) e **quando e onde cada candidato é
atendido** (o horário publicado). A programação de cada avaliador é o cruzamento dos dois, e não
pede dado novo. O e-mail de quem avalia também já existe, na pessoa institucional.

**O que falta não é dado: é coerência.** A Distribuição ignora a agenda. Simulei o caso do pedido —
43 candidatos, 6 avaliadores, 3 bancas, dupla avaliação — com o próprio código do rodízio: ele forma
três duplas fixas, mas as reparte na ordem do protocolo, e **a mesma dupla fica com dois candidatos
no mesmo horário em 8 a 14 dos 15 horários**. Uma programação individual montada sobre isso seria
fiel ao sistema e impossível de cumprir.

**A recomendação:** a programação aparece **dentro do GPS**, na Mesa de quem avalia e em Minhas
atividades (alternativa C). Antes, duas pequenas evoluções na Distribuição tornam o vínculo
confiável: **filtrar as inscrições por banca e dia**, para atribuir "as da Banca 01 em 25/11" a uma
dupla num gesto só, e **acusar o avaliador com dois candidatos no mesmo horário**. O e-mail vem
depois, como aviso curto com link, e só se a FR-084 for revista — decisão sua.

---

## 1. O mapa real

```text
ProcessoSeletivo ──< MembroComissao ──────────────┐  identity_subject (texto)
     │                 │                           │       ║ igualdade de texto, sem FK
     │                 └──< AlocacaoEtapa          │       ▼
     │                        (edital, etapa_id)   │  auth.User.username = "pessoa-<uuid>"
     │                        "pode atuar"          │  auth.User.email (copiado do provedor)
     │                                              │
Edital ─┬─< Atribuicao (membro, etapa_id, inscricao)┘   "avalia ESTA inscrição"   ← o vínculo
        │                      │
        │                      └─────────── Inscricao ───┐
        │                                                 │
        └─< AgendaDaEtapa (edital, etapa_id) ──< BancaDaAgenda (nome, acesso)
                  │                                       │
                  └─< AtoDaAgenda ──< HorarioPublicado (inscricao, banca, inicio, fim)
                                       vigente = não substituído e AGENDADO
```

**A Etapa é o eixo, como o usuário supôs**: a alocação, a Atribuição e a agenda se referem à mesma
`etapa_id` (sem chave estrangeira, porque a Etapa vive na Versão Consolidada e pode nascer por
Retificação — o mesmo motivo nos três apps). **A banca não tem pessoas**, e nada aponta de pessoa
para banca.

### 1.1 As respostas, com a evidência

| Pergunta | Resposta | Onde |
|---|---|---|
| Como o avaliador se vincula à Etapa? | `MembroComissao` do Processo + `AlocacaoEtapa` (membro × Edital × Etapa). A alocação diz **quem pode atuar** na Etapa, e não o que avalia. | [comissoes/models.py](../backend/processo_seletivo/comissoes/models.py) |
| O vínculo identifica a pessoa e o e-mail? | **Sim, em produção; indiretamente.** O `identity_subject` do membro é comparado, como texto, ao `subject` do ator (`membro_ativo`); na pessoa institucional, esse `subject` é o `username` (`pessoa-<uuid>`) do `auth.User`, que guarda o e-mail copiado do provedor a cada entrada (`_atualizar`). Não há chave estrangeira; o elo é a igualdade do texto. | [comissoes/domain/autorizacao.py](../backend/processo_seletivo/comissoes/domain/autorizacao.py), [seguranca/autenticacao.py](../backend/processo_seletivo/seguranca/autenticacao.py) |
| A agenda está ligada à Etapa? | **Sim**: `AgendaDaEtapa(edital, etapa_id)`, uma por Etapa. | [agendamento/models.py](../backend/processo_seletivo/agendamento/models.py) |
| Como a agenda organiza os candidatos? | Horários derivados da configuração; `Agendamento` (rascunho) e, depois de publicada, `HorarioPublicado` por inscrição, com banca, início e fim. A vigente sai de `leitura.vigentes_da_agenda`. | idem, `application/leitura.py` |
| A Distribuição tem relação aproveitável com a agenda? | **O vínculo sim, a coerência não.** A `Atribuicao` é por **inscrição**, e a inscrição tem horário; mas a Distribuição não lê a agenda: o rodízio segue o protocolo, e o filtro da tela é só por cobertura e por avaliador. | [avaliacoes/domain/rodizio.py](../backend/processo_seletivo/avaliacoes/domain/rodizio.py), [interface/templates/interface/distribuicao.html](../backend/processo_seletivo/interface/templates/interface/distribuicao.html) |
| O GPS sabe quais candidatos uma pessoa avaliará? | **Sim**: é exatamente o que a Mesa lista — "todas e somente" as Atribuições ativas da pessoa na Etapa. | `avaliacoes/application/selectors.py`, `mesa()` |
| O que a Mesa oferece? | As inscrições atribuídas, **por protocolo**, paginadas, com filtros de andamento (pendente, rascunho, concluída). **Nenhum horário.** | idem |
| O que Minhas atividades oferece? | Uma linha por Etapa com avaliação pendente: quantas faltam, o fim do período e o link para a Mesa. **Nenhum horário.** | [interface/atividades.py](../backend/processo_seletivo/interface/atividades.py), `linhas_de_avaliacao` |

### 1.2 Vínculos que existem e vínculos que faltam

**Existem, e bastam para a programação individual:**

- avaliador → inscrições: `Atribuicao`;
- inscrição → dia, hora, banca: `HorarioPublicado` vigente;
- banca → local ou sala: `BancaDaAgenda.acesso`;
- avaliador → pessoa → e-mail: `identity_subject` = `User.username` → `User.email`.

**Faltam, e não são cadastro novo:**

1. **Coerência entre Distribuição e agenda.** Nada impede um avaliador com dois candidatos no mesmo
   horário, e nada ajuda a atribuir "a Banca 01" a uma dupla.
2. **Horário na Mesa e em Minhas atividades.** O dado existe; as telas não o leem.
3. **Elo forte entre membro da comissão e pessoa.** É texto contra texto. O registro de ativação do
   SSO já o lista como pendência: "O `identity_subject` da comissão continua texto livre; com o
   identificador opaco, incluir um membro por ele é impraticável. Falta a busca da pessoa"
   ([doc/ativacao-do-sso-institucional.md](ativacao-do-sso-institucional.md)). Para a programação na
   tela, não importa: quem entra na Mesa já casou o texto. **Para o e-mail, importa**: um membro
   digitado errado não recebe nada, e em silêncio.

**Falta, e não precisa existir: a composição da banca.** Não há "integrantes da Banca 01", e a
análise abaixo mostra que a Atribuição já responde à pergunta, com mais flexibilidade.

---

## 2. O caso das múltiplas bancas: 43 candidatos, 6 avaliadores, 3 bancas

### 2.1 O sistema sabe quais dois avaliadores estão em cada banca?

**Não diretamente, e não precisa.** Ele sabe quem avalia **cada candidato**. "Quem está na Banca 01
às 08:00" é o conjunto de quem tem a Atribuição do candidato daquele horário daquela banca. Isso
**já varia por dia, janela ou sessão** sem entidade nenhuma: se a Banca 01 tem a dupla A-B no dia 25
e C-D no dia 26, basta que as Atribuições digam isso. Uma composição fixa de banca seria menos
flexível que o que já existe.

### 2.2 O que acontece hoje, medido

Simulação com `rodizio.propor`, a função de produção, sem alteração: 43 inscrições, 6 membros,
`evaluationsPerRegistration = 2`, agenda preenchida como a `167` preenche (por nome, horário do mais
cedo ao mais tarde, bancas lado a lado — 15 horários), protocolo sem relação com o nome. Cinco
sorteios da ordem dos protocolos:

| Ordem das inscrições no rodízio | Horários em que alguém está em dois lugares | Duplas distintas |
|---|---|---|
| **Protocolo (a de hoje)** | **8, 10, 10, 13 e 14 de 15** | 3 |
| Horário e banca da agenda | **0 de 15**, nos três sorteios testados | 3 |

**O rodízio já forma bancas sem saber**: ele cicla as pessoas e produz três duplas fixas. O que
quebra é a ordem. Na ordem da agenda, cada dupla cai numa banca e fica nela. Mas isso é coincidência
aritmética, e não garantia: um impedimento (comum na heteroidentificação), uma carga anterior ou sete
avaliadores em vez de seis desfazem o ciclo. **Por isso a recomendação não é mudar a ordem do
rodízio, e sim deixar a comissão atribuir por banca e o sistema acusar o conflito.**

### 2.3 Os seis devem receber a agenda completa da Etapa?

**Não.** Cada um recebe o que avalia. A agenda completa da Etapa é **pública** (a página pública da
`167` a mostra por dia, com nome e protocolo, ou só o protocolo na Etapa por Modalidade), e quem
quiser vê-la abre a página; mas a programação que orienta o trabalho é a individual. Mandar a Etapa
inteira a seis caixas é seis cópias de uma lista que muda, e na heteroidentificação seria levar os
nomes de quem concorre pela reserva para fora do GPS sem necessidade.

### 2.4 A menor evolução que torna a relação confiável

Duas peças, ambas na tela da Distribuição, **sem tabela nova e sem campo novo**:

1. **Filtro por banca e dia** na lista "Inscrições, uma a uma". O lote da Distribuição já é
   uniforme — "cada inscrição selecionada vai para cada avaliador selecionado"
   (`avaliacoes/application/distribuicao.py`) —; com o filtro, "Banca 01, 25/11" × {A, B} é **uma**
   submissão. Três bancas em dois dias, seis submissões. Hoje são 43 inscrições marcadas à mão.
2. **A acusação de simultaneidade**: "Ana Lima tem duas entrevistas às 08:15 de 25/11 (Banca 01 e
   Banca 02)". É derivada de Atribuição × horário vigente, numa consulta; aparece na Distribuição,
   na agenda publicada e na remarcação. **Avisa, não impede**: a Distribuição pode vir antes da
   agenda, e uma atribuição não fica errada porque a agenda ainda não existe.

---

## 3. As três alternativas

| | **A — Etapa a todos** | **B — Individual por e-mail** | **C — Na área do avaliador** |
|---|---|---|---|
| O que chega | a agenda inteira da Etapa a cada avaliador alocado | os candidatos e horários de cada um, no e-mail | a programação de cada um na Mesa e em Minhas atividades |
| Dado novo | nenhum | nenhum | nenhum |
| Depende da coerência da §2.4 | não | **sim** | **sim** |
| Acesso mínimo | ruim: cada um vê todos | bom | bom: mostra o que a Mesa já mostra, mais hora e lugar |
| Etapa por Modalidade | leva os nomes de todos para fora do GPS | leva os nomes dele para fora do GPS | **nada sai do GPS** |
| FR-084 (situações de e-mail) | revisão | revisão | **nenhuma** |
| FR-7229 (sala só à pessoa) | revisão, se levar a sala | revisão, se levar a sala | esclarecimento (abaixo) |
| Remarcação | outra cópia da lista inteira a seis pessoas | outra mensagem por pessoa afetada; cópias velhas nas caixas | **a tela já mostra a vigente** |
| Fonte da verdade | a última mensagem | a última mensagem | o GPS |
| Planilha da comissão | some | some | some |

**A** é a mais simples e a pior em privacidade, e não responde "o que eu faço às 08:15".
**B** é a que o pedido imaginou, e herda os dois problemas do e-mail: a cópia que envelhece e o nome
fora do GPS. **C** resolve o problema maior que o usuário apontou — o avaliador deixa de depender de
planilha e de mensagem —, não toca a FR-084 e não expõe nada que a Mesa já não exponha.

**FR-7229 em C.** A regra diz que a sala "MUST chegar só à própria pessoa". As telas da gestão já
mostram a sala a quem gere a comissão, que a cadastrou; então a leitura em vigor é "nada de público,
nada a outro candidato". O avaliador atribuído àquele candidato é quem vai entrar na sala; mostrar-lhe
a sala da banca em que ele atende é a mesma leitura. **Na spec, isso vira uma frase de esclarecimento
da FR-7229**, para não depender de interpretação.

---

## 4. A recomendação

**C, precedida pelas duas peças da §2.4, com o e-mail como aviso opcional depois.** Combinar C com B
seria duplicar a lista; combinar C com um aviso curto não duplica nada.

### 4.1 A experiência da comissão

1. **Distribuição** (tela que existe): filtra "Banca 01 · 25/11", seleciona as inscrições e a dupla,
   distribui. Repete por banca e dia. Se usar o rodízio, a tela acusa o que ficou simultâneo, com o
   nome da pessoa, o horário e as duas bancas, e o filtro leva às linhas para corrigir.
2. **Agenda publicada** (tela que existe): cada linha ganha "Avaliam: Ana Lima, Bruno Reis". Uma
   linha de aviso, só quando houver: "2 entrevistas sem avaliador · 1 avaliador em dois lugares às
   08:15 de 25/11". Nenhum botão novo.
3. **Remarcar** (tela que existe): ao escolher o horário novo, a tela diz quem avalia a pessoa e se
   eles estão livres naquele horário. Ninguém é redistribuído automaticamente: a comissão decide.

### 4.2 A experiência do avaliador

1. **Minhas atividades**: a linha da Etapa ganha a próxima entrevista — "Entrevista · 14 pendentes ·
   próxima: 25/11 às 08:00, Banca 01".
2. **A Mesa** ganha a visão "Programação", que vira a padrão quando a Etapa tem agenda publicada:
   um bloco por dia, em ordem de horário, com hora, candidato (como a Mesa já o mostra), banca, e o
   local ou o botão da sala; o estado da avaliação continua na linha, e o link para a ficha também.
   A lista por protocolo continua lá, como hoje. Na remarcação, a linha diz "remarcado em 21/11".

```text
Minhas atividades                                Mesa · Entrevista · Edital 28/2026
┌──────────────────────────────────────────┐     ┌──────────────────────────────────────────────┐
│ Entrevista — Edital 28/2026              │     │ [Programação]  Por inscrição                 │
│ 14 pendentes · próxima 25/11, 08:00,     │     │ Terça, 25/11 — 7 entrevistas · Banca 01      │
│ Banca 01                       [Abrir]   │     │  08:00  Maria Silva   INS-0412   Pendente    │
└──────────────────────────────────────────┘     │  08:15  João Souza    INS-0388   Rascunho    │
                                                 │  08:30  Ana Oliveira  INS-0501   remarcada   │
                                                 │  …                                           │
                                                 │ Sala da Banca 01  [Entrar na sala]           │
                                                 └──────────────────────────────────────────────┘
```

O avaliador não recebe lista nenhuma para guardar: abre o GPS e vê a vigente.

### 4.3 O e-mail, quando vier

Um **aviso curto, sem lista e sem nome**: "Sua programação na Entrevista do Edital 28/2026 está
disponível: 14 entrevistas entre 25 e 26/11, na Banca 01. Veja no GPS: <link para a Mesa>". Na
remarcação que afeta a pessoa: "Sua programação mudou em 21/11. Veja no GPS: <link>". O link leva à
Mesa, que exige entrar; quem não é o avaliador recebe a recusa da Mesa.

Mesmo curto, é uma oitava situação de envio, e a FR-084 da `010` exige revisá-la — decisão sua. O
destinatário é o `User.email` da pessoa institucional cujo `username` é o `identity_subject` do
membro; quem não casar (membro de demonstração, identificador digitado errado, pessoa que nunca
entrou) aparece para a comissão como "sem e-mail", e não é pulado em silêncio. **Antes do e-mail,
convém resolver a pendência "comissão apontando para pessoa"**, porque o e-mail é o único lugar em que
um identificador errado falha sem que ninguém perceba.

---

## 5. O menor escopo seguro

**Primeiro incremento — sem e-mail, sem tabela nova, sem revisão de norma:**

1. Distribuição: filtro por banca e dia nas inscrições (lê `vigentes_da_agenda`, ou o `Agendamento`
   antes da publicação).
2. Acusação de simultaneidade (Atribuição × horário), na Distribuição e na agenda publicada.
3. Mesa: a visão "Programação", por dia e horário, com banca e local ou sala.
4. Minhas atividades: a próxima entrevista na linha da Etapa.
5. Agenda publicada: "Avaliam:" em cada linha.
6. O esclarecimento da FR-7229 na `167`.

Reaproveita: `leitura.vigentes_da_agenda`, `horarios_na_ocorrencia` (que já cruza inscrição com
horário publicado), a `mesa()` e o lote uniforme da Distribuição. Testes no padrão do orçamento de
consulta da Mesa, que é cobrado desde a `012`: a programação não pode custar uma consulta por linha.

**Segundo incremento — se o primeiro não bastar:** o aviso curto por e-mail, com a revisão da FR-084
e, antes dele, a busca da pessoa na inclusão do membro da comissão.

**Fora:** "E-mail da banca"; composição fixa de banca; a agenda completa por e-mail; anexo;
redistribuição automática na remarcação; mudar a ordem do rodízio por padrão.

**Esforço do primeiro incremento:** nesta rodada, estimado como baixo, por ser só leitura. A terceira
rodada o revê para médio, porque a coerência passou a ser recusa no lote e no rodízio, e não só
aviso (ver o quadro do topo).

---

## 6. O que fica para validar com o usuário

1. **A Distribuição por banca é como a comissão trabalha?** A proposta supõe que, numa Etapa com
   bancas simultâneas, a comissão quer duplas por banca e dia. Se a prática for outra — o mesmo
   avaliador circulando entre salas, ou a banca inteira avaliando todos —, a acusação de
   simultaneidade continua valendo, mas o filtro perde importância.
2. **O e-mail entra?** Se sim, revisar a FR-084 e resolver antes a busca da pessoa na comissão.
3. **A sala na Mesa.** Confirmar a leitura da FR-7229 da §3.

## Pergunta central

> Se o GPS já conhece as pessoas alocadas à Etapa e a agenda pertence à Etapa, por que
> precisaríamos criar um cadastro de e-mails nas bancas?

**Não precisamos.** A pessoa, o e-mail, os candidatos de cada avaliador e o horário de cada
candidato já estão no GPS. O que falta é a Distribuição respeitar a agenda, e as telas do avaliador
mostrarem o horário. Feito isso, a programação de cada avaliador é uma leitura, e o e-mail, quando
vier, só precisa dizer "está lá".
