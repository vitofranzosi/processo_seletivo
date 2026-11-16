# Contrato: as telas tocadas

Nenhuma tela nova. Cada seção abaixo parte da tela real, com o arquivo dela, e diz o que entra, onde
e quando aparece. As frases são as que a tela mostra; o plano pode ajustá-las, sem mudar o sentido.

| Tela | Arquivo de hoje | Quem abre | Incremento |
|---|---|---|---|
| Distribuição da Etapa | `interface/templates/interface/distribuicao.html` | gestão da comissão | 1 |
| Remarcar / Agendar | `interface/templates/interface/agenda_remarcar.html` | gestão da comissão | 1 |
| Conferir a agenda | `interface/templates/interface/agenda_conferir.html` | gestão da comissão | 1 |
| Agenda publicada | `interface/templates/interface/agenda_publicada.html` | gestão da comissão | 1 e 2 |
| Mesa (Minha Etapa) | `interface/templates/interface/minha_etapa.html` | avaliador | 1 |
| Minhas atividades | `interface/templates/interface/_atividade.html` | avaliador | 1 |
| Mensagem ao avaliador | moldura `shared/templates/correio/aviso.html` | avaliador | 2 |

---

## 1. Distribuição da Etapa

Hoje a tela tem, em ordem: o cartão **Agenda**, as contagens de cobertura, **Quem está alocado**,
**Atribuições órfãs**, **Distribuir o que falta** (o rodízio) e **Inscrições, uma a uma**, com o
filtro por cobertura e por avaliador e o lote (inscrições × avaliadores).

### 1.1 O filtro (FR-8204, UX-970)

No formulário de filtros de "Inscrições, uma a uma", ao lado de Cobertura e Avaliador, só numa
Etapa com agenda:

```text
Cobertura [Todas ▾]   Avaliador [________]   Dia [25/11 ▾]   Banca [Banca 01 ▾]   [Filtrar]
```

- **Dia** lista os dias da agenda; **Banca**, as bancas que têm alguém naquele dia.
- Antes da publicação, uma linha acima da lista: "Horários da agenda em montagem: ainda podem mudar."
- A sessão filtrada cabe numa página (UX-970), para "selecionar todas desta página" pegar a sessão.

### 1.2 A lista (FR-8204)

Cada linha ganha a coluna **Horário**, antes da cobertura, e a lista passa a vir em ordem de horário
quando o filtro de dia está ativo:

```text
☐  08:00–08:15  Banca 01   INS-2026-0412   Ana Lima, Bruno Reis        2 de 2
☐  08:15–08:30  Banca 01   INS-2026-0388   —                           0 de 2
☐  08:30–08:45  Banca 01   INS-2026-0501   Ana Lima ⚠ 08:30 Banca 02    1 de 2
```

O ⚠ é texto, e não só cor: "Ana Lima tem outra entrevista às 08:30 (Banca 02)".

### 1.3 O resultado do lote (FR-8205, UX-971)

O resultado declarado de hoje ganha a recusa por conflito, com o mesmo formato das recusas por
impedimento:

> **12 atribuições criadas.** 2 recusadas:
> INS-2026-0501 para Ana Lima — ela já tem entrevista das 08:30 às 08:45 de 25/11, na Banca 02.
> Escolha outro avaliador para esta inscrição, ou distribua-a noutro gesto.

### 1.4 O resumo da coerência (FR-8208, UX-974)

No cartão **Agenda** que já existe no topo, uma linha:

- em ordem: "43 de 43 pessoas com avaliadores · nenhum conflito";
- com o que resolver: "**3 sem avaliador suficiente** · **1 conflito**: Ana Lima às 08:30 de 25/11
  (Banca 01 e Banca 02)", cada parte um link que filtra a lista abaixo.

Em **Quem está alocado**, a pessoa em conflito leva a mesma frase ao lado da carga.

### 1.5 O rodízio (FR-8207)

"Distribuir o que falta" não muda de forma. A proposta passa a dizer, quando a Etapa tem horários:
"As inscrições são percorridas na ordem da agenda: dia, horário, banca." E o que fica de fora por
conflito vem com o motivo: "Todas as pessoas selecionadas têm entrevista neste horário."

---

## 2. Remarcar e Agendar (FR-8209)

Hoje: o seletor de horários livres por banca (`fieldset.horarios-livres`), o motivo, e o painel
**Ao confirmar** com os efeitos.

- Acima do seletor, uma linha: "Avaliam esta pessoa: Ana Lima e Bruno Reis."
- Cada horário livre em que um deles já tem entrevista leva a marca textual "Ana ocupada" dentro do
  rótulo do horário, e não desaparece (`D-003`).
- **Ao confirmar** ganha um item, só quando o horário escolhido cria conflito: "Ana Lima passa a ter
  duas entrevistas às 09:30 de 25/11. Resolva na Distribuição; enquanto isso, a pendência fica na
  agenda publicada." No Incremento 2, a frase acrescenta: "e ela não recebe o aviso de programação."
- Sem avaliadores atribuídos, nada muda na tela.

## 3. Conferir a agenda (FR-8208)

No bloco que hoje lista o que impede a publicação, uma seção de **aviso**, e não de impedimento,
quando houver conflito com atribuições que já existem: "A agenda, como está, põe 2 avaliadores em
dois lugares ao mesmo tempo. Isso não impede a publicação; resolva na Distribuição."

---

## 4. Agenda publicada

Hoje: o resumo da publicação, os documentos, **Avisos** (aos candidatos), **Passou a participar
depois**, **Tem horário e não participa mais** e **Horários publicados** (Quando · Pessoa · Remarcar).

### 4.1 Quem avalia (FR-8215, `D-007`)

A tabela **Horários publicados** ganha a coluna **Avaliam**, entre Pessoa e a ação: "Ana Lima e Bruno
Reis", ou "Ninguém ainda" com link para a Distribuição filtrada naquele dia. A tela é da gestão;
a página pública, que tem template próprio (`portal/agenda_da_etapa.html`), não recebe o dado.

### 4.2 A seção "Quem avalia" (Incremento 1: coerência; Incremento 2: aviso)

Depois de **Avisos**, uma seção nova **Quem avalia**, numa linha quando tudo está em ordem
(UX-974). As telas da agenda não dizem "avaliador": a varredura de vocabulário da `167` o proíbe
nelas, para que a banca não seja lida como grupo de pessoas — e a `179` preserva essa decisão.

```text
Incremento 1, em ordem:
  Avaliadores · 6 com programação · 43 de 43 pessoas com avaliadores · nenhum conflito

Incremento 1, com o que resolver:
  Avaliadores · 3 sem avaliador suficiente · 1 conflito (Ana Lima, 09:30 de 25/11)   → Distribuição

Incremento 2, pronto e não avisado:
  Avaliadores · programação pronta para 6 avaliadores        [ Avisar os avaliadores (6) ]

Incremento 2, depois do aviso, com mudança:
  Avaliadores · 4 avisados em 20/11 · 2 com programação mudada   [ Avisar as mudanças (2) ]
  ▸ Ver por avaliador
```

"Ver por avaliador" (`<details>`) abre a lista, uma pessoa por linha, com o estado da FR-8228:

```text
Ana Lima      Mudou depois do aviso de 20/11
Bruno Reis    Avisado em 20/11, 14:02
Carla Souza   Não entregue em 20/11 — o servidor recusou o endereço     [Reenviar]
Davi Rocha    Sem e-mail: o identificador na comissão não corresponde a pessoa institucional
Elisa Prado   Com conflito: 09:30 de 25/11 — fora do aviso até ser resolvido
```

"Mudou" é comparação de estado (FR-8224), e não histórico: a tela não diz qual ato mudou, e a
mensagem também não.

### 4.3 A confirmação do aviso (FR-8222)

O botão leva a uma confirmação na mesma moldura da conferência da agenda (não é tela nova de
fluxo: é o passo de alcance que o Princípio IV pede antes de um ato sobre vários objetos):

```text
Avisar os avaliadores
  5 recebem: Ana Lima, Bruno Reis, Carla Souza, Felipe Dias, Gabriela Melo.
  Fora: Davi Rocha (sem e-mail) · Elisa Prado (conflito às 09:30 de 25/11).

  Assunto: Sua programação de entrevistas — Entrevista — Edital 28/2026
  [texto exato da mensagem de Ana Lima]

  [ Confirmar e avisar 5 ]   Voltar à agenda publicada
```

Com a habilitação dos avisos desligada, a seção diz "Os avisos por e-mail estão desligados nesta
instalação" no lugar do botão (FR-8227).

---

## 5. Mesa (Minha Etapa)

Hoje: a seção **Minha Mesa**, com os filtros-contagem (total, não iniciadas, em rascunho,
concluídas) e a tabela Inscrição · Situação, por protocolo, paginada de 25 em 25.

### 5.1 As duas visões (FR-8211, FR-8212, `D-005`)

Numa Etapa com agenda publicada, a seção ganha, acima dos filtros, a escolha entre **Programação**
(primeira, padrão) e **Por inscrição** (a de hoje, intacta). Os filtros-contagem valem para as duas.
Sem agenda, a Mesa é a de hoje, sem a escolha.

### 5.2 A Programação

```text
Minha Mesa                                   [Programação]  Por inscrição
14 no total · 11 não iniciadas · 1 em rascunho · 2 concluídas

Terça-feira, 25 de novembro — 7 entrevistas
┌──────────────────────────────────────────────────────────────┐
│ 08:00–08:15  Maria Silva · INS-2026-0412                     │
│ Banca 01 · Videoconferência              [Entrar na sala]     │
│ Não iniciada                                    Abrir ficha › │
├──────────────────────────────────────────────────────────────┤
│ 08:15–08:30  João Souza · INS-2026-0388   remarcada em 21/11 │
│ Banca 01 · Videoconferência              [Entrar na sala]     │
│ Em rascunho                                     Abrir ficha › │
└──────────────────────────────────────────────────────────────┘
Quarta-feira, 26 de novembro — 7 entrevistas
…
Sem horário publicado — 0
```

- Cada entrevista é um item de lista, não linha de tabela: cabe a 375 px (UX-972).
- **Entrar na sala** é botão, com o endereço no `href` e não no texto (UX-973); no presencial, o
  local por extenso no lugar do botão.
- O dia de hoje vem aberto e marcado "Hoje"; dias passados, recolhidos no fim, para o próximo
  compromisso ser a primeira coisa da tela.
- A resposta é privada e sem cache, como a Mesa (FR-8231).

### 5.3 Antes da publicação (FR-8212)

A visão Programação mostra só: "A agenda desta Etapa ainda não foi publicada. Quando for, as suas
entrevistas aparecem aqui, por dia e horário." A visão Por inscrição continua funcionando.

---

## 6. Minhas atividades (FR-8214)

Hoje, a linha de avaliação de uma Etapa diz: ato ("Avaliar 14 inscrições"), Edital, lugar, fase e
"até" o fim do período. Ela ganha, só quando há entrevista futura, um trecho a mais na mesma linha
`onde-da-atividade`:

```text
Avaliar 14 inscrições
Edital 28/2026 · Entrevista · Avaliação · próxima entrevista 25/11 às 08:00, Banca 01 · até 26/11/2026
```

O link da linha continua sendo a Mesa, que abre na Programação.

---

## 7. A mensagem ao avaliador (Incremento 2, FR-8223)

Na moldura comum, texto puro primeiro, sem imagem e sem recurso externo:

```text
Assunto: Sua programação de entrevistas — Entrevista — Edital 28/2026

Olá, Ana Lima.

Sua programação de entrevistas está disponível no GPS:
14 entrevistas, de 25/11/2026 a 26/11/2026, na Banca 01.

Veja os horários, os candidatos e o acesso à sala:
https://gps…/gestao/minhas-etapas/<edital>/<etapa>   (a Mesa de hoje, rota `minha-etapa`)

A programação que vale é a do GPS: se algo mudar, ela já estará atualizada lá.

—
Mensagem automática do GPS. Quem organiza as entrevistas é a comissão do Edital 28/2026.
Cefor/Ifes
```

Na atualização, o assunto vira "Sua programação de entrevistas mudou — …", e a primeira frase,
"Sua programação de entrevistas mudou em 21/11/2026." O resto é igual. O nome no "Olá" é o do
avaliador, e não de candidato.

---

## 8. Rotas e parâmetros

Nenhuma rota nova no Incremento 1; uma no Incremento 2. Toda rota tocada continua com a guarda que
tem hoje: a da Distribuição e da agenda (`_etapa_para_distribuir`: Edital fora do escopo → 404; sem a
base da gestão da comissão → recusa da gramática das portas) e a da Mesa (alocação ∧ Atribuição, a
FR-020 da `012`).

| Rota (nome) | Método | O que muda | Incremento |
|---|---|---|---|
| `interface:distribuicao` | GET | parâmetros `dia` (AAAA-MM-DD) e `banca` (id da banca); com os dois, ordem de horário e sem paginação até 200 linhas | 1 |
| `interface:distribuicao` | POST (lote) | o resultado declarado ganha a recusa `conflito_de_horario` | 1 |
| `interface:distribuicao` | POST (rodízio) | a proposta segue a agenda e não propõe par em conflito | 1 |
| `interface:agenda-remarcar` | GET | "Avaliam esta pessoa", e a marca de ocupado em cada horário livre | 1 |
| `interface:agenda-remarcar` | POST | campo `assinatura_dos_conflitos`; recusa `conflitos_mudaram` (409) se o que a tela anunciou mudou | 1 |
| `interface:agenda-conferir` | GET | seção de aviso com os conflitos | 1 |
| `interface:agenda-publicada` | GET | coluna Avaliam; seção Avaliadores | 1 e 2 |
| `interface:minha-etapa` | GET | parâmetro `visao` (`programacao` \| `inscricoes`) | 1 |
| `interface:minhas-atividades` | GET | "próxima entrevista" na linha da Etapa | 1 |
| `interface:agenda-avisar-avaliadores` (nova) | GET | a confirmação: alcance, quem fica fora, a mensagem; não grava | 2 |
| `interface:agenda-avisar-avaliadores` (nova) | POST | `assinatura`, `chave_idempotencia`; recusas `alcance_mudou` (409) e avisos desligados | 2 |
| `interface:agenda-reenviar` | POST | passa a aceitar também o aviso de programação que não foi entregue | 2 |

## 9. As frases das recusas e dos avisos

| Código | Onde | Frase |
|---|---|---|
| `conflito_de_horario` | lote | «Nome» já tem entrevista das «HH:MM» às «HH:MM» de «dd/mm», na «Banca». Escolha outro avaliador para esta inscrição, ou distribua-a noutro gesto. |
| `conflito_no_rodizio` | proposta do rodízio | Todas as pessoas selecionadas têm entrevista neste horário. |
| `conflitos_mudaram` | remarcação | A distribuição mudou enquanto você remarcava: confira quem fica em conflito no horário escolhido e confirme de novo. |
| (aviso) | remarcação, antes da confirmação | «Nome» passa a ter duas entrevistas às «HH:MM» de «dd/mm». Resolva na Distribuição; enquanto isso, a pendência fica na agenda publicada. |
| (aviso) | conferência da agenda | A agenda, como está, põe «N» avaliador(es) em dois lugares ao mesmo tempo. Isso não impede a publicação; resolva na Distribuição. |
| `alcance_mudou` | aviso aos avaliadores | Quem recebe o aviso mudou desde que você abriu esta tela. Confira de novo antes de confirmar. |
| (estado) | seção Avaliadores | Sem e-mail: o identificador na comissão não corresponde a pessoa institucional com e-mail. |
