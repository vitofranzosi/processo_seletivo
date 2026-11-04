# Revisão de UX — a jornada do convocado no portal, depois da `115`

Feita em 04/11/2026 sobre a `main` em `fb0e1ddc`, com a `115` mergeada (#368, #369). Partiu do
achado do PR vitofranzosi/processo_seletivo#374 (`doc/achado-jornada-do-candidato-na-convocacao.md`,
ainda não mergeado). Nenhum código e nenhuma spec foram alterados.

> **Não vira escopo por estar escrito aqui.** Este documento registra o diagnóstico e uma proposta.
> Priorizar, decidir e abrir spec são do usuário. Ninguém de fora do projeto leu estas telas: a
> leitura "pessoa leiga" é de quem revisa, e um teste com candidatos reais diria mais.

## Resumo

1. **Os quatro pontos do achado se confirmam no código e nas capturas.** Três deles são mais graves
   do que o achado registrou.
2. **A falha principal é uma falsa sensação de conclusão.** Quando o Edital pede o Requerimento e
   documentos, o acompanhamento diz *"Seu Requerimento de Matrícula foi enviado."* e tem como botão
   principal *"Conferir o Requerimento de Matrícula enviado"*. Isso acontece com os quatro documentos
   obrigatórios ainda em *"Falta enviar"* (cenário C2, captura `c2-acompanhamento-375.jpg`).
3. **Depois do desfecho, a lista continua pedindo.** O bloco ainda diz *"Envie até…"*, e os itens
   seguem *"aguardando conferência"* e *"Falta enviar"*. Mas a comissão já não pode conferir
   (FR-3588), e o candidato já não pode enviar (cenário I2).
4. **"Atendido pelo documento enviado na inscrição"** aparece enquanto o item ainda espera
   conferência. É a mesma falsa conclusão, num item só (cenário D).
5. **O prazo é um só instante, mas aparece de seis formas diferentes:**
   - três formatos de data e hora;
   - três redações para o prazo vencido;
   - nenhuma menção na tela do Requerimento.
6. **Recomendação: uma spec SDD curta.** O conserto pede uma visão das obrigações *derivada* (sem
   estado gravado) e uma ação principal que leve a ela. Os dois mudam a redação de requisitos já
   escritos: FR-1175 a FR-1178 da `063` e FR-3612 da `115`, presos por teste. Polish solto
   contrariaria FR escrito. Seis ajustes pequenos podem sair já, sem spec (§9).

---

## 1. Como foi medido

- **Doze cenários num Chromium de verdade**, pelo Playwright:
  - os nove pedidos (A–I);
  - I2, o indeferimento com itens não enviados;
  - J, a pendência sobre item que nunca chegou;
  - K, o prazo ainda não iniciado.
- **Montagem pelas *fixtures* da `115` e da `059`**, as mesmas das jornadas de
  `tests/navegador/test_jornada_dos_documentos_da_convocacao.py`.
  - Os dados são fictícios: "Candidata 601", o CPF de teste da fixture e o Edital "Primeiro Edital".
  - Banco de teste próprio, contra PostgreSQL.
- **Captura em duas larguras**, 375 × 812 e 1280 × 900, de "Minhas inscrições", do acompanhamento,
  da convocação e, quando cabia, do Requerimento. Junto, o texto visível de cada tela e as posições
  verticais dos blocos.
- **Teclado**: 40 Tabs na tela da convocação a 375 px (cenários A e F), anotando o elemento focado e
  o contorno do foco.
- **Reprodução**: [`roteiro-de-captura.py`](roteiro-de-captura.py), com instruções no cabeçalho. As
  maquetes estão em [`maquetes/`](maquetes/) e foram renderizadas por
  [`renderizar-maquetes.py`](renderizar-maquetes.py).

**Limites.**

- **As telas foram abertas por GET**, depois de o estado ser preparado por serviço.
  - Fica de fora o aviso de um quadro só que segue um envio pelo portal ("Documento recebido. A
    comissão vai conferir."; "Requerimento de Matrícula enviado.").
  - O texto e a ordem da página são os mesmos.
- **Dois detalhes das capturas vêm do ambiente, e não do produto**:
  - o "Área de gestão" no topo aparece porque o seletor de identidade está ligado;
  - o nome do Perfil, "Perfil", é o da fixture.
- **A gestão não foi percorrida**, salvo onde a pergunta do aviso exigiu.

## 2. Os quatro pontos do achado, conferidos

| # | Ponto do achado | Veredito | Evidência |
|---|---|---|---|
| 1 | Ninguém avisa o candidato | **Confirmado, e mais amplo** | Pendência não dispara mensagem (FR-3614). "Minhas inscrições" mostra o mesmo *"➜ Convocação aberta · Ver convocação"* de A a H (`a-inscricoes-375.jpg`). A mensagem de convocação (`convocacao/application/comunicar.py`, `CORPO`) não diz que há documentos a enviar. No Perfil que convoca por publicação, não há mensagem nenhuma |
| 2 | "Sua situação" não fala de documentos | **Confirmado, e pior** | `_acao_da_convocacao` (`portal/situacao.py:339`) não recebe a leitura documental. Daí três problemas: a falsa conclusão de C2, F e H; o *"Siga as instruções do Edital"* em A, D e E, com a lista pronta logo ali; e o Requerimento não enviado, que some quando o prazo vence (G) |
| 3 | A lista fica escondida na convocação | **Confirmado; a medida corrige a posição** | A 375 px, o título da lista fica em y = 652 e o primeiro item em y = 809 (a tela tem 812). A lista começa no fim da primeira tela, e não "na metade da segunda". Com prazo vencido, o aviso a mais empurra para y = 802. O Requerimento vai para o fim: y ≈ 1930, terceira tela (C1). O *"O que fazer"* manda ao "prazo acima" e não aponta a lista |
| 4 | Palavras que confundem | **Confirmado, e mais um caso** | *"Atendido pelo documento enviado na inscrição"* aparece com o item ainda sem conferência e com o marcador ○ (`d-convocacao-375.jpg`). Com o prazo vencido, o achado contou dois avisos; são **três** redações: duas na convocação e uma no acompanhamento (`g-*.jpg`) |

**O que a `115` acertou e se preserva:**

- o cartão por documento;
- a instrução do Edital;
- o motivo da pendência, visível ao candidato;
- o reenvio já aberto no item pendente;
- o "não se aplica" escondido;
- nenhuma rolagem lateral a 375 px, em nenhum dos 12 cenários;
- o foco visível a 3 px, inclusive no botão de arquivo, que recebe o foco do `input` oculto;
- uma ordem de Tab linear.

Nenhuma tela do portal diz "matriculado", "encaminhado" ou "bolsa".

## 3. Falhas que o achado não registrou

Numeradas para a classificação da §9.

- **F1 — Falsa conclusão no acompanhamento** (C2, F, H).
  - A ação principal é a do Requerimento, porque a FR-1175 da `063` só conhece três ações. Enviado o
    Requerimento, o bloco *"O que fazer"* diz que ele foi enviado, com um botão verde para conferi-lo.
  - Em C2, isso aparece com quatro documentos obrigatórios sem envio. Em F, com uma pendência a
    corrigir.
  - O critério *"nenhuma mensagem dá falsa sensação de conclusão"* falha.

- **F2 — A lista depois do desfecho continua pedindo** (I1, I2; `i2-convocacao-375.jpg`).
  - `_documentos_da_convocacao.html` mostra *"Envie até ‹vencimento›. Cada arquivo é conferido pela
    comissão."* sempre que não há `frase_do_prazo`, e a frase só existe com a chamada em aberto.
  - Os itens repetem *"Recebido…, aguardando conferência"*. Depois do desfecho essa espera não
    termina nunca, porque a conferência é recusada (FR-3588). Repetem também *"Falta enviar"*,
    quando nada mais se envia.

- **F3 — O Requerimento não enviado some depois do vencimento** (G).
  - `_requerimento_da_convocacao` devolve vazio quando o prazo decorreu e o Requerimento não foi
    enviado, para não oferecer um botão que levaria a recusa. É uma decisão certa.
  - Só que nenhuma tela diz que ele **não foi** enviado. O acompanhamento volta a *"Siga as
    instruções do Edital"*.
  - Quem abre o endereço do Requerimento cai na página genérica de recusa, com o título técnico
    *"Operação incompatível com a situação atual"* e o link *"Voltar às seleções"*
    (`g-requerimento-375.jpg`).

- **F4 — O prazo é lido de seis formas.** O instante é o mesmo em toda parte: o `vencimento` da
  chamada vigente, decorrido pela mesma regra (`convocacao/domain/prazo.py`, chamada por
  `estado_de` e por `prazo_decorrido`). A forma de dizê-lo varia:

  | Tela | Texto |
  |---|---|
  | Acompanhamento, topo | *"Prazo desta convocação: até 09/11/2026 às 13h27."* |
  | Acompanhamento, seção, e convocação | *"Prazo para atender: até 09/11/2026 13:27, contado do envio da comunicação"* |
  | Lista de documentos | *"Envie até 09/11/2026, às 13:27."* |
  | Vencido, acompanhamento | *"O prazo desta convocação terminou em 04/11/2026 às 13h28. O resultado da convocação ainda não foi registrado. Se você atendeu e não consta, fale com o atendimento."* |
  | Vencido, convocação | *"O prazo informado nesta convocação já passou. Isso não decide nada sozinho: fale com o atendimento se você atendeu e não consta."* |
  | Vencido, lista e Requerimento | *"O prazo terminou em 04/11/2026, às 13:28. A comissão vai decidir."* |

  A tela do Requerimento não mostra prazo nenhum enquanto ele está aberto.

- **F5 — A pendência não se distingue** (`f-convocacao-desktop.jpg`).
  - O item pendente tem o mesmo cartão neutro e o mesmo marcador ○ de *"Falta enviar"*. Só a
    primeira palavra da linha muda.
  - O ○ cinza, a 375 px, lembra um botão de opção.

- **F6 — "Envie outro arquivo" sem arquivo nenhum** (J).
  - A pendência registrada sobre item que nunca chegou (correção 1 da revisão de código da `115`)
    diz *"Pendente: ‹motivo›. Envie outro arquivo até…"*. Não houve um primeiro.

- **F7 — O facultativo parece obrigação** (lido no código; as fixtures não têm facultativo na
  convocação).
  - O item facultativo sem envio diz *"Falta enviar"*, e só o *"(facultativo)"* em letra menor o
    distingue.
  - Se um resumo de pendências entrar, ele não pode contar o facultativo.

- **F8 — O desfecho tem três rótulos e nenhum próximo passo** (I1).
  - Os rótulos:
    - "Minhas inscrições" diz *"Convocação: Aceite"* (`get_especie_display`);
    - o acompanhamento diz *"Vaga aceita"* (`DESFECHOS`, FR-1172 da `063`);
    - a convocação diz *"Situação registrada: Aceite — …"*.
  - A User Story 2 da `115` (cenário 2) diz que *"o portal mantém a frase atual de que nenhum ato do
    GPS confirma matrícula ou contratação"*. **Essa frase não existe em tela nenhuma do portal.** Ela
    está só no comentário de `situacao.py:59`.
  - Depois do aceite, a pessoa lê *"Vaga aceita · Nada por enquanto"* e mais nada.

- **F9 — O Requerimento enviado não devolve ao resto** (`c2-requerimento-375.jpg`).
  - A página do Requerimento enviado termina em *"Conferir e atualizar"*, sem *"Voltar à
    convocação"* nem *"Voltar ao acompanhamento"*. A ramificação *"ainda não"* tem esse link; a
    ramificação *"enviado"* não tem.
  - A explicação do estado (`requerimentos/application/selectors.py:71`) diz *"Se algo mudar e você
    for convocado, esta página oferece a atualização"*. Ela aparece logo acima de *"Você foi
    convocado e pode conferir o que enviou"*.
  - É o passo "retorno ao acompanhamento depois do envio" da jornada, e ele não existe.

- **F10 — "Minhas inscrições" não diferencia as convocações abertas.** De A a H, é a mesma linha.
  Para a lista distinguir "tem pendência", seria preciso ler os documentos de cada inscrição, e a
  FR-1092 da `059` exige custo constante. A leitura em lote já existe (`leituras_por_chamada`, com
  consultas de número fixo).

- **F11 — Nomes acessíveis repetidos.**
  - Cada cartão tem *"Escolher arquivo PDF"* e *"Enviar"* idênticos. Quem usa leitor de tela, ou
    navega por formulários, ouve quatro "Enviar" sem o nome do documento.
  - O `aria-describedby` aponta só para *"Somente PDF, até 10 MB."*.

- **F12 — O prazo não iniciado contradiz a data** (K).
  - A mesma tela diz três coisas: *"Prazo para atender: até 09/11/2026 13:27, contado do envio da
    comunicação"*; *"A comunicação … ainda não foi enviada. O seu prazo não começou a correr."*; e,
    na lista, *"Envie até 09/11/2026, às 13:27"*.
  - É parente do achado `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`.

## 4. Proposta de hierarquia e navegação

**Sem tela, sem wizard, sem painel e sem estado novos.** Tudo abaixo cabe nas três telas que já
existem e lê o que a `115` já deriva.

### 4.1 A visão consolidada das obrigações, derivada

Uma função pura recebe quatro entradas, todas já calculadas nas views:

- a leitura da chamada (`LeituraDocumental`);
- o estado do Requerimento (`CHAMADO_DO_REQUERIMENTO`, mais "enviado" e "não enviado com prazo
  vencido");
- o estado do prazo (`estado_de`);
- o desfecho.

Ela devolve **três grupos** e um total. É o molde de `situacao.py`: nada gravado e nenhum relógio
lido na função.

| Grupo | Entra | Não entra |
|---|---|---|
| **Você precisa fazer** | obrigatório *a apresentar*; *pendente*; Requerimento disponível ou em preenchimento | facultativo; itens da comissão |
| **Com a comissão** | *recebido*, *complementado* e aproveitado sem conferência | — |
| **Feito** | *conforme*; *não se aplica* por conferência; Requerimento enviado | — |

O facultativo aparece à parte, como *"opcional"*, e nunca no total do que falta.

**A ordem não é a da FR-3591.** A FR-3591 da `115` põe *para conferir* antes de *com pendência*,
porque serve a quem confere. Para o candidato a pendência vem primeiro. A função nova não reaproveita
aquela precedência; reaproveita só os estados de item.

**Nunca "tudo aceito".** Com tudo *conforme* e o Requerimento enviado, mas sem desfecho (cenário H),
a frase é *"Você enviou pelo portal tudo o que esta convocação pede. A comissão ainda vai registrar
o resultado."* Ela não diz que a vaga está garantida, nem que o resultado está decidido.

### 4.2 A tela da convocação, em cinco blocos

Ordem pedida: o que fazer → o que já foi feito ou depende da comissão → prazo → ações → metadados.

1. **"O que falta fazer"**, um painel no topo.
   - A primeira linha é o prazo, em um formato só.
   - Depois, a lista "Você precisa fazer", com âncora para cada cartão.
   - Um botão principal, *"Enviar os N documentos que faltam"*, leva ao primeiro item pendente.
   - Fecham o painel os grupos "Já enviado" e "Com a comissão", e a frase de consequência da
     FR-1177, que não muda.
   - O Requerimento entra **nessa mesma lista**, como uma obrigação a mais, e não como link solto no
     fim.
2. **"Documentos pedidos nesta convocação"**: a lista da `115`, na ordem do Edital.
   - O cartão pendente ganha destaque de aviso (borda e fundo âmbar, selo *"Precisa de
     correção"*).
   - O cartão que só espera a comissão ganha o selo neutro *"Aguardando conferência"*.
3. **"Sobre esta convocação"**: espécie, chamada, comunicação, fundamento e atendimento. Tudo
   visível, sem `details`, porque é o ato que a pessoa tem direito de ler. Só desce de posição.
4. **Prazo vencido**: o painel do topo vira *"O prazo terminou"*, com a frase única e o resumo
   *"Até o prazo, ficou assim"*. O resumo inclui o Requerimento não enviado (F3).
5. **Desfecho registrado**: o painel do topo vira *"Resultado registrado"*. A lista vira *"O que você
   enviou nesta convocação"*, sem *"Envie até"*, com *"Não enviado"* e *"Enviado em…; não foi
   conferido antes do resultado"*.

Maquetes, com a folha real do portal:

| Situação | Antes | Depois |
|---|---|---|
| F, pendente com prazo em curso, 375 px | `capturas/f-convocacao-375.jpg` | `capturas/depois-f-convocacao-375.jpg` |
| F, desktop | `capturas/f-convocacao-desktop.jpg` | `capturas/depois-f-convocacao-desktop.jpg` |
| D/E, só depende da comissão | `capturas/d-convocacao-375.jpg`, `capturas/e-convocacao-375.jpg` | `capturas/depois-de-convocacao-375.jpg` |
| G, prazo vencido | `capturas/g-convocacao-375.jpg` | `capturas/depois-g-convocacao-375.jpg` |
| I2, desfecho registrado | `capturas/i2-convocacao-375.jpg` | `capturas/depois-i2-convocacao-375.jpg` |
| F, acompanhamento | `capturas/f-acompanhamento-desktop.jpg` | `capturas/depois-f-acompanhamento-375.jpg` |

As maquetes não têm rolagem lateral a 375 px. Na de F, o botão principal fica em y ≈ 480, dentro da
primeira tela. Hoje, o primeiro item fica em y = 809.

### 4.3 O acompanhamento: uma ação principal, que leva ao conjunto

A ação do *"O que fazer"* passa a vir da visão consolidada. Vale a primeira linha que se aplicar:

| # | Quando | Ação principal | Link |
|---|---|---|---|
| 1 | desfecho vigente | como hoje (*"Nada por enquanto."*) | Requerimento enviado, como hoje; *"Ver o que você enviou"* |
| 2 | prazo vencido, sem desfecho | *"O prazo terminou em … A comissão vai decidir."* | *"Ver como ficou a convocação"* |
| 3 | há item pendente | *"Corrija N documento(s) da convocação."* | convocação, no painel do topo |
| 4 | há obrigação a fazer, e a chamada tem documentos | *"Envie N documentos[ e o Requerimento de Matrícula]."* | convocação, no painel do topo |
| 5 | o Requerimento é a única obrigação a fazer | *"Preencher o Requerimento de Matrícula."* (hoje) | Requerimento, como hoje (cenário B não muda) |
| 6 | nada a fazer; algo com a comissão | *"Nada por enquanto. A comissão está conferindo N documentos."* | convocação |
| 7 | tudo feito, sem desfecho | *"Nada por enquanto. Você enviou tudo o que esta convocação pede pelo portal."* | convocação |
| 8 | sem documentos e sem Requerimento | *"Siga as instruções do Edital para esta convocação."* (hoje) | convocação |

O Requerimento enviado aparece como linha secundária (*"✓ Requerimento de Matrícula enviado.
Conferir"*), e não como ação principal.

**Uma regra só para o destino:** com documento na chamada, o caminho principal é a convocação, onde
estão todas as obrigações. Sem documento, nada muda. É o que impede o Requerimento de esconder os
documentos.

### 4.4 Lista e Requerimento

- **"Minhas inscrições"** (futuro, §9): a nota ao lado de *"Convocação aberta"* diz *"2 documentos a
  enviar"* ou *"1 documento precisa de correção"*. A leitura é em lote, para manter a FR-1092 da
  `059`. A ação continua *"Ver convocação"*.
- **Requerimento enviado**: ganha *"Voltar à convocação"*, e, com a chamada aberta e algo a fazer, a
  linha *"Ainda faltam N documentos desta convocação."* O texto *"se você for convocado"* sai quando
  ele já foi convocado (F9).

## 5. Textos recomendados

Mesmo sentido jurídico, com a linguagem simples da `069`. A coluna "Restrição" é o que a redação
nova não pode perder.

| Hoje | Proposto | Restrição |
|---|---|---|
| *"Conforme"* | *"Conferido: de acordo com o Edital."* | FR-3589 da `115`: conforme ao exigido, **nunca** autêntico. FR-292c da `019`: não soar como vaga. "Aprovado" continua vetado |
| *"Atendido pelo documento enviado na inscrição em DD/MM"*, sem conferência | *"Você já enviou este documento na inscrição, em DD/MM. Não precisa enviar de novo."* + selo *"Aguardando conferência"* | o mesmo sentido da FR-3576. Não pode dizer "atendido" antes da conferência |
| idem, depois do *conforme* | *"Conferido: de acordo com o Edital (o arquivo da inscrição, de DD/MM)."* | — |
| *"Aproveitado da chamada anterior, enviado em DD/MM. A comissão vai conferir de novo"* | sem mudança, só o ponto final | já diz quem age |
| *"Recebido em DD/MM, às HH:MM, aguardando conferência"* | *"Recebido em DD/MM, às HHhMM. A comissão vai conferir; você não precisa fazer nada agora."* | não inferir prazo da comissão |
| *complementado* (hoje sai como "Recebido…") | *"Novo arquivo recebido em DD/MM, às HHhMM, em resposta à correção pedida. A comissão vai conferir."* | o estado já existe (FR-3590) |
| *"Pendente: ‹motivo›. Envie outro arquivo até ‹data›"* | *"Precisa de correção: ‹motivo›. Envie um novo arquivo até ‹data›, às ‹hora›."* Sem envio anterior: *"… Envie o arquivo até…"* | o motivo continua sendo o de quem conferiu, sem o nome (FR-3584) |
| *"Falta enviar"* (facultativo) | *"Opcional: envie se quiser."* | não contar no total |
| *"Falta enviar"* / *"aguardando conferência"* depois do desfecho | *"Não enviado."* / *"Enviado em DD/MM; não foi conferido antes do resultado."* | FR-3588 |
| *"Envie até … Cada arquivo é conferido pela comissão."* depois do desfecho | (some) | — |
| *"O prazo informado nesta convocação já passou. Isso não decide nada sozinho: …"* + *"O prazo terminou em …, às …. A comissão vai decidir."* + a do acompanhamento | **Uma só**, em todo lugar: *"O prazo terminou em DD/MM/AAAA, às HHhMM. Não é mais possível enviar documentos nem o Requerimento pelo portal. Quem registra o resultado é a comissão. Se você enviou algo que não aparece aqui, fale com o atendimento: ‹canal›."* | FR-1176 da `063` (dizer a data e que não há registro, sem afirmar perda); FR-3622 da `115` (a mesma frase nos documentos e no Requerimento) |
| *"Siga as instruções do Edital para esta convocação dentro do prazo acima."* | só quando não há documento nem Requerimento; com eles, some (o painel o substitui) | FR-1175 da `063` |
| *"Seu Requerimento de Matrícula foi enviado."* como ação | linha secundária *"✓ Requerimento de Matrícula enviado."* | FR-1097 da `059`: o caminho para conferir continua |
| três formatos de prazo | **um**: *"até 09/11/2026, às 13h27"*, a forma do acompanhamento (`HORA = "H\\hi"`). Na convocação, *"contado do envio da comunicação"* fica só com o prazo não iniciado | FR-1176 da `063`; a mensagem da `019` diz *"contado do envio desta mensagem"* |
| prazo não iniciado: data + *"não começou a correr"* | *"O prazo ainda não começou a correr: ele conta a partir do envio da comunicação. Você já pode enviar os documentos."* — e a data não aparece como prazo | FR-3578 da `115`: o envio é aceito antes do prazo correr |
| *"Vaga aceita"* / *"Aceite"* / *"Situação registrada: Aceite"* | o rótulo de `DESFECHOS` nas três telas. Depois do aceite, a frase prometida pela User Story 2 da `115`: *"Este registro não é a matrícula nem o contrato. Os próximos passos são os do Edital, com o setor que ele indica."* | FR-1172 da `063` (o rótulo é decisão dela); o vocabulário da §10 do complemento ("apto para formalização" ≠ "encaminhado" ≠ vínculo) |
| *"Operação incompatível com a situação atual"* (Requerimento depois do prazo) | título *"O prazo terminou"*, com a frase única e *"Voltar à convocação"* | — |

**Sobre "apto para formalização".** O termo é da gestão (FR-3610) e não deve ir ao portal. Para o
candidato, ele seria jargão e soaria como promessa. A frase do aceite acima diz o mesmo sem nomear o
vínculo.

## 6. Matriz de cenários, antes e depois

Para cada cenário, três perguntas: a pessoa leiga entende **o que fazer**, **o que não precisa
fazer** e **o que depende da comissão**? A última coluna diz se alguma tela dá falsa sensação de
conclusão.

| Cenário | Antes | Depois | Falsa conclusão (antes → depois) |
|---|---|---|---|
| **A** documentos sem Requerimento | Fazer: só rolando; o topo diz "Siga as instruções do Edital". Não precisa: —. Comissão: "Cada arquivo é conferido pela comissão" | Painel "Enviar os 4 documentos que faltam" no topo; o acompanhamento diz "Envie 4 documentos" | não → não |
| **B** Requerimento sem documentos | Claro: "Preencher Requerimento" no acompanhamento e na convocação | Igual (linha 5 da §4.3); o prazo aparece também no Requerimento | não → não |
| **C1** ambos, nada enviado | O acompanhamento só fala do Requerimento; na convocação, o Requerimento fica na 3ª tela, depois de 4 cartões | "Envie 4 documentos e o Requerimento", com um caminho só | não → não |
| **C2** ambos, só o Requerimento enviado | **"Seu Requerimento de Matrícula foi enviado."** + botão verde para conferi-lo; 4 obrigatórios sem envio | "Envie 4 documentos"; o Requerimento vira linha "✓ enviado" | **sim → não** |
| **D** aproveitado da inscrição | "Atendido…" lido como pronto; o marcador ○ contradiz | "Você já enviou na inscrição… Não precisa enviar de novo" + "Aguardando conferência"; topo "Você não precisa fazer nada agora" | **sim → não** |
| **E** enviado, aguardando | Acompanhamento: "Siga as instruções do Edital" (sugere que há algo a fazer); convocação: 4 × "aguardando conferência" | "Nada por enquanto. A comissão está conferindo 4 documentos" | não → não (mas antes induzia ação inexistente) |
| **F** pendente, prazo em curso | Acompanhamento: "Requerimento foi enviado"; convocação: pendência sem destaque, no 2º cartão | "Corrija 1 documento e envie 1"; cartão pendente em âmbar, com âncora | **sim → não** |
| **G** pendente, prazo vencido | Três redações do vencimento; Requerimento não enviado invisível; recusa técnica no Requerimento | Uma frase; "Até o prazo, ficou assim", com o Requerimento não enviado | não → não (antes omitia) |
| **H** tudo enviado, sem decisão | Acompanhamento: "Requerimento foi enviado"; convocação: 4 × "Conforme" + ✓, que pode ser lido como aprovado | "Você enviou tudo o que esta convocação pede pelo portal. A comissão ainda vai registrar o resultado." | **risco → não** |
| **I1** aceite | Três rótulos; a lista ainda diz "Envie até…"; nenhum próximo passo | Um rótulo; "O que você enviou"; a frase "não é a matrícula nem o contrato" | não → não |
| **I2** indeferido | Lista: "Envie até…", "aguardando conferência", "Falta enviar" depois da decisão | "Resultado registrado"; "Não enviado"; "não foi conferido antes do resultado" | **convite falso → não** |
| **J** pendência sem envio | "Envie outro arquivo" sem um primeiro | "Envie o arquivo até…" | não → não |
| **K** prazo não iniciado | A data aparece como prazo e, ao mesmo tempo, o texto diz que o prazo não começou | "O prazo ainda não começou… Você já pode enviar" | não → não |

**Teclado e 375 px**, antes e depois:

- nenhuma rolagem lateral;
- foco visível em todos os controles;
- ordem do Tab linear, sem armadilha.

O que muda é o nome acessível. "Enviar" passa a "Enviar a Certidão de nascimento ou casamento", por
texto visualmente oculto (F11).

## 7. Aviso e prazo

As respostas separam **interface** (dá para fazer no portal) de **procedimento ou instituição** (só
com decisão de fora do código).

**Como o candidato fica sabendo de uma pendência, hoje?** Só voltando ao portal por conta própria e
abrindo a convocação. A lista não muda (F10), o acompanhamento não muda (F1), e nenhuma mensagem sai
(FR-3614 da `115`; FR-084 da `010`). No Perfil que convoca por publicação, nem a convocação chega por
e-mail. Com a §4 aplicada, quem volta ao portal vê a pendência na primeira tela. Isso é
**interface**, e não resolve quem não volta.

**Que evento justificaria um aviso complementar?**

- A `066` só admite aviso a partir de **ato oficial publicado**, com destinatários que o ato
  identifica (FR-1241: resultado publicado, ou chamada comunicada por publicação). A conferência não
  é ato publicado, é juízo individual da comissão.
- Avisar pendência é, portanto, a **quinta situação** da FR-084: a QI-7, que a `115` deixou em
  aberto. É decisão **institucional**, e é a mesma da validação de LGPD que mantém
  `AVISOS_AOS_CANDIDATOS` desligada em produção.
- Se for admitida, o evento defensável é um **gesto humano** de quem confere ("Avisar a pessoa das
  pendências desta chamada"). Ele valeria uma vez por lote de conferências, nunca uma por clique,
  nunca automático (FR-084: *"aviso disparado … sem decisão humana continua fora"*; D-007 da `115`).
- Não há evento que justifique aviso **automático** de pendência ou de vencimento próximo: seria o
  lembrete que a FR-084 exclui pelo nome.

**Como evitar dado pessoal ou motivo sensível no e-mail?** Pelo molde da FR-084a e da `066`:

- o e-mail diz só que *"há documento da convocação que precisa de atenção"* e aponta a área do
  candidato (`{area_do_candidato}`);
- o motivo, o nome do documento e a modalidade não vão para o e-mail. O motivo pode revelar
  condição de saúde, renda ou cota; o nome do documento, idem ("laudo", "comprovante de renda");
- o motivo fica no portal, atrás da autenticação, onde já está (FR-3584);
- o assunto segue a orientação da FR-1258 da `066`.

**Como distinguir o aviso da comunicação oficial?**

- Rodapé fixo, como o da FR-1257 da `066`: *"Este aviso não é a convocação nem altera o seu prazo.
  O prazo é o da convocação: até ‹vencimento›. A referência é a sua área do candidato."*
- Assunto que não comece por "Convocação", para não se confundir com o `ASSUNTO` da mensagem da
  `019`, que **é** o ato quando o Perfil convoca por mensagem individual (FR-269a).
- O aviso não grava `ComunicacaoEmitida` (FR-1242 da `066`).

**Pendência registrada perto do vencimento, e depois dele.**

- **Perto do vencimento** (procedimento): a pessoa tem horas, e não dias, para ler e reenviar.
  - O que a **interface** pode fazer é mostrar o prazo restante a quem confere, no cartão da
    conferência, com *"faltam menos de 24 h; para dar mais prazo, corrija a convocação por
    sucessão"*. Hoje a página da gestão não diz isso.
  - Dar mais prazo é decisão da comissão, pelo mecanismo da FR-3618.
- **Depois do vencimento**: a conferência continua aceita (FR-3588). A pendência registrada aí não
  tem como ser respondida, e o portal a mostra sem convite a enviar, o que está certo (G).
  - Para o candidato, a redação da §5 diz *"precisava de correção"* e não oferece envio.
  - Para a comissão, a pendência pós-prazo é, na prática, o fundamento de um indeferimento
    (FR-3594). A tela poderia dizer isso. É decisão de **procedimento**, e não de texto.
- **Não alterar a contagem.** Nada aqui move o vencimento nem cria prazo de complementação próprio
  do item (FR-3618, D-011 da `115`).

**Como funciona a correção formal por sucessão?**

- O comando existe: `convocar` com motivo, sobre convocação vigente sem desfecho, cria a sucessora
  com vencimento novo (FR-272 da `019`). A lista e as apresentações ficam com a chamada (FR-3573). A
  sucessora reabre documentos e Requerimento juntos (FR-3622). O portal passa a mostrar o prazo novo,
  porque lê a vigente.
- **Na interface da gestão, não achei por onde corrigir.**
  - O formulário *"Chamar uma pessoa da fila"* não tem campo de motivo, embora `convocar_view` o leia
    do POST (`interface/views.py`, linha 8830).
  - Encontrar a sucessão só pelo comando é **lacuna da gestão**, a confirmar. Se ela se confirmar, a
    FR-3618 aponta para um mecanismo que a comissão não alcança pela tela.
- **O aviso da sucessão já existe.** No Perfil que convoca por mensagem individual, a sucessora se
  comunica pela terceira situação da FR-084. Mas a mensagem é a mesma *"Você foi convocada(o) no…"*,
  e diz *"contado do envio desta mensagem"*.
  - Uma variante *"A sua convocação foi corrigida: o novo prazo é…"* seria mudança no conteúdo da
    mensagem da `019` (FR-290), e não situação nova.
  - É o mesmo terreno de `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`.

**Uma melhoria que não pede situação nova.** A mensagem de convocação, que já existe, pode dizer que
*"esta convocação pede documentos pelo portal, e a conferência de cada um aparece na sua área"*. Isso
muda o texto da `019` (FR-290) e o teste que o prende, e nada na contagem de situações.

## 8. Impactos nas specs

| Spec | O que muda | Natureza |
|---|---|---|
| `063` | FR-1175: a ação passa a ter também os documentos, pela tabela da §4.3. FR-1178: "Nada por enquanto" ganha a frase de espera da comissão. FR-1176: o formato único do prazo e a frase única do vencido. As frases continuam constantes de `situacao.py` (D-005), e o SC-453 continua lendo os dicionários. A função continua sem relógio (D-001, D-007 da `063`) | **revisão de FR**: redação e tabela |
| `115` | FR-3612: os textos literais da §5. FR-3577: a ordem da tela e o painel do topo. Requisito novo para a visão consolidada derivada, com a regra do facultativo e a do "nunca tudo aceito". FR-3591 fica como está, na gestão. A User Story 2 (cenário 2) deixa de citar uma "frase atual" que não existe | **emenda** |
| `059` | FR-1090 e FR-1096/1097: com documento na chamada, o caminho principal do acompanhamento é a convocação, e não o Requerimento. A lista (FR-1089 a FR-1092) só muda no item futuro da nota, mantendo a FR-1092 | **revisão pontual** |
| `029` | Página do Requerimento enviado: *"Voltar à convocação"*, o prazo visível enquanto aberto, e a explicação *"se você for convocado"* trocada quando já convocado (F9). A recusa depois do prazo ganha título próprio (F3). Nenhuma regra de disponibilidade muda (FR-374, FR-408 e FR-411 continuam como a D-019 da `115` as deixou) | **texto e navegação** |
| `019` | Só se o usuário quiser a frase "esta convocação pede documentos" na mensagem (FR-290) e a variante da sucessora | **opcional** |
| `010` / `066` | Nenhuma mudança nesta proposta. A QI-7 é decisão à parte | **decisão institucional** |

Testes que prendem os textos de hoje e mudariam junto:

- `tests/unit/portal/test_situacao_da_inscricao.py`;
- `tests/portal/test_acompanhamento_pela_situacao.py`;
- `tests/interface/test_portal_documentos_da_convocacao.py`;
- `tests/interface/test_portal_caminho_da_convocacao.py`, com o *"não decide nada sozinho"*;
- `tests/navegador/test_jornada_dos_documentos_da_convocacao.py`;
- `tests/integration/requerimentos/test_prazo_da_chamada.py`;
- `tests/interface/test_portal_requerimento.py`;
- a varredura de vocabulário, que tem lista literal de telas.

## 9. Ajustes classificados

**Bloqueante.** Falsa conclusão ou convite a ato que não existe:

| # | Ajuste | Falha | Pede spec? |
|---|---|---|---|
| B1 | A ação do acompanhamento passa a vir da visão consolidada; o Requerimento enviado deixa de ser a ação principal enquanto falta documento | F1, ponto 2 | sim (FR-1175 da `063`) |
| B2 | Depois do desfecho, a lista vira leitura: sem *"Envie até"*, sem *"aguardando conferência"*, sem *"Falta enviar"* | F2 | sim (FR-3612 da `115`) — mas o *"Envie até"* pode sair já |
| B3 | O aproveitado sem conferência não diz "atendido" | ponto 4 | sim (FR-3612) |
| B4 | O painel "O que falta fazer" no topo da convocação, com o Requerimento dentro dele | ponto 3 | sim (FR-3577) |

**Recomendável.**

| # | Ajuste | Falha | Pede spec? |
|---|---|---|---|
| R1 | Um formato de prazo e uma frase do vencido em todas as telas | F4, ponto 4 | sim (FR-1176 da `063`, FR-3612) |
| R2 | O Requerimento não enviado aparece no resumo depois do prazo; a recusa ganha título próprio | F3 | sim, junto de B1 |
| R3 | Destaque do item pendente, selo de espera, marcador que não pareça botão de opção | F5 | não; é folha de estilo |
| R4 | *"Envie o arquivo"* quando não houve envio anterior | F6 | não; condicional no template |
| R5 | Facultativo dito como opcional | F7 | sim, junto de B3 |
| R6 | Um rótulo de desfecho nas três telas, e a frase pós-aceite | F8 | sim (FR-1172 da `063`, User Story 2 da `115`) |
| R7 | *"Voltar à convocação"* no Requerimento enviado | F9 | não; link |
| R8 | A explicação *"se você for convocado"* não aparece a quem já foi | F9 | não; condicional |
| R9 | Nome acessível com o nome do documento | F11 | não |
| R10 | Prazo não iniciado sem a data lida como prazo | F12 | sim, junto de R1 |
| R11 | O prazo restante na conferência da gestão, perto do vencimento | §7 | sim, pequena |

**Futuro.** Pede decisão de fora ou incremento próprio:

| # | Ajuste | Depende de |
|---|---|---|
| X1 | Nota de pendência em "Minhas inscrições", com leitura em lote | custo da FR-1092 da `059` medido |
| X2 | Aviso de pendência por e-mail, por gesto, sem motivo | QI-7 (quinta situação da FR-084) e LGPD |
| X3 | Frase dos documentos e variante da sucessora na mensagem de convocação | revisão da FR-290 da `019` |
| X4 | Correção por sucessão alcançável pela interface da gestão | confirmar a lacuna da §7 |
| X5 | Teste com candidatos reais da jornada A–I | o produto |

**O que pode sair já como polish, sem spec:** R3, R4, R7, R8, R9 e o *"Envie até"* de B2. Nenhum
deles muda redação de requisito.

## 10. Recomendação

**Uma spec SDD curta**, e não polish:

- **O defeito que pesa é normativo.** B1 a B4 e R1 contrariam requisitos escritos:
  - a FR-1175 da `063` lista as três ações e manda dizer "siga as instruções do Edital";
  - a FR-3612 da `115` fixa *"Conforme"* e *"Atendido pelo documento enviado na inscrição"* como
    textos literais;
  - a FR-1177 e o SC-453 prendem as frases do acompanhamento.

  Polish que os mudasse seria o *quick win* que contraria FR, e a suíte os prende por teste.
- **A spec é pequena**:
  - uma função pura nova, a visão consolidada, no molde de `situacao.py`;
  - uma tabela de ações;
  - a ordem da tela da convocação;
  - os textos da §5;
  - emendas a três specs (`063`, `115`, `059`) e um ajuste de texto na `029`.

  Nenhuma tabela, migration, estado gravado, tela, rota ou envio de mensagem. Nada toca a contagem
  do prazo.
- **Fica fora dela, por decisão de outros:**
  - a QI-7 (aviso de pendência), que é institucional;
  - a mensagem da `019`;
  - a nota em "Minhas inscrições";
  - a correção por sucessão na gestão.

  Misturá-los atrasaria o que não depende de ninguém.
- **Pode sair já, como polish:** os seis itens sem spec listados ao fim da §9. Nenhum deles muda o
  que um requisito diz.

## Arquivos

- [`capturas/`](capturas/): 23 capturas "antes" (a letra é o cenário; `-375` ou `-desktop` é a
  largura) e 6 maquetes "depois" (`depois-*`).
- [`maquetes/`](maquetes/): o HTML das maquetes, com a folha real do portal por caminho relativo.
  Os estilos embutidos ali são só da maquete; a implementação os poria na folha.
- [`roteiro-de-captura.py`](roteiro-de-captura.py): os cenários A–K e as medidas.
- [`renderizar-maquetes.py`](renderizar-maquetes.py): a renderização das maquetes nas duas larguras.
