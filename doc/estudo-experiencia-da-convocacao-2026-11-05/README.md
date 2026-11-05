# Estudo — a experiência da convocação: portal, e-mail e acesso

**Data**: 05/11/2026 · **Base**: `main` em `337a0d81` · **Natureza**: só estudo. Nada de código,
spec ou requisito mudou. Onde a proposta esbarra num requisito escrito, a justificativa está aqui, e
**a decisão é do usuário** (seção 11).

> **De onde vem.** O usuário percorreu a jornada do convocado na `main` e registrou o achado
> `doc/achado-comunicacao-ao-convocado-2026-11-05.md` (worktree `documentacao-kit-divulgacao`, ainda
> sem commit). Faltam duas coisas: a X3 da `118`, porque a mensagem não diz que há documentos, e a
> QI-7 da `115`, porque a pendência não gera aviso. Este estudo junta as duas com o pedido de mudança
> de perspectiva. A convocação tem de ler como **comunicação institucional importante**, com prazo,
> consequência e uma ação principal, e não como tela de administrar documentos.

## Sumário

1. [Diagnóstico](#1-diagnóstico)
2. [Hierarquia proposta para a página](#2-hierarquia-proposta-para-a-página)
3. [Vocabulário por tipo de seleção](#3-vocabulário-por-tipo-de-seleção)
4. [Modelo de e-mail](#4-modelo-de-e-mail)
5. [Acesso: três alternativas](#5-acesso-três-alternativas)
6. [Percurso no navegador, caso a caso](#6-percurso-no-navegador-caso-a-caso)
7. [Pendências (QI-7): política de avisos complementares](#7-pendências-qi-7-política-de-avisos-complementares)
8. [Maquetes e viabilidade técnica](#8-maquetes-e-viabilidade-técnica)
9. [Plano de teste com pessoas reais](#9-plano-de-teste-com-pessoas-reais)
10. [Impactos nas specs e MVP](#10-impactos-nas-specs-e-mvp)
11. [O que decidir](#11-o-que-decidir)
12. [Como reproduzir](#12-como-reproduzir)

### Como as capturas foram feitas

As capturas são de cinco bancos de demonstração, um por cenário, montados pelas fixtures da `118`:
`tests/fixtures/jornada_do_convocado.py`, com `montar(letra, Montagem(...))`. Os bancos são
`ps_estudo_conv_c1`, `_f`, `_g`, `_i1` e `_corr`, todos copiados de um `ps_estudo_conv_base`
preparado por `make preparar`. Cada um subiu num runserver próprio, das portas 8131 a 8135, e foi
percorrido por um Chromium (Playwright) a 1280 × 900 e a 375 × 812.

| Cenário | O que é |
|---|---|
| C1 | documentos e Requerimento, nada enviado |
| F | um documento pendente e um a enviar, Requerimento enviado |
| G | prazo vencido sem desfecho |
| I1 | vaga aceita |
| corr | cenário A corrigido pela `120`: sucessora com prazo novo e mensagem reenviada |

O acesso foi feito de verdade em C1: o e-mail, o código lido no terminal do servidor, a lista e um
PDF enviado. O roteiro está em [`roteiro/`](roteiro/).

**Artefatos da demonstração, e não defeitos.** Quatro coisas nas capturas vêm da montagem, e não do
produto:

- "Área de gestão" no cabeçalho: o seletor de identidade estava ligado.
- O Perfil chamado "Perfil": é o nome que a fixture dá.
- O fundamento citando o "Edital 77/2026" num Edital 72: é o texto da fixture.
- O canal `selecao@exemplo.test`, que é o `PORTAL_ATENDIMENTO` do `.env`.

---

## 1. Diagnóstico

### 1.1 O e-mail de hoje

Capturado no terminal ao comunicar a convocação de C1. O corpo é o `CORPO` de
`convocacao/application/comunicar.py:48`, enviado por `send_mail` em texto puro.

```text
Subject: Convocação — Edital 72/2026

Você foi convocada(o) no Edital 72/2026.

Prazo para atender: até 10/11/2026 às 10:23, contado do envio desta mensagem.

O que fazer: acesse a sua área e siga as instruções da convocação em
https://‹host›/selecoes/inscricoes/

Em caso de dúvida, fale com selecao@exemplo.test.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
```

| # | Achado | Peso |
|---|---|---|
| E1 | **Não diz que há documentos a enviar** (a X3 da `118`). Quem lê não sabe que precisa juntar certidão, histórico e comprovante antes de o prazo vencer. | alto |
| E2 | **O assunto não diz a ação nem a instituição por extenso.** "Convocação — Edital 72/2026" não traz "Ifes" para quem não conhece o "Cefor", nem diz o que fazer ou até quando. Na lista do celular, ele é a única coisa lida. | médio |
| E3 | **O link leva à lista**, e não à convocação. Sem sessão, a lista manda ao acesso **sem destino**: depois do código, a pessoa cai em "Minhas inscrições" e precisa achar "Ver convocação" (1.3). | médio |
| E4 | **A mensagem da correção é idêntica à original, salvo o prazo.** No banco `corr` saíram duas mensagens, uma com "até 10/11/2026" e outra com "até 12/11/2026", e nenhuma diz qual vale. É o que a própria `120` registra em `_FRASE_DA_COMUNICACAO` (`fluxo.py:405`): *"Ela não diz que corrige a anterior."* | alto |
| E5 | **Não há orientação de segurança.** Uma mensagem institucional que pede ação com prazo e manda clicar num link é exatamente o formato do *phishing*. Nada diz o que o Ifes nunca pede. | médio |
| E6 | **Há formatação a acertar.** "às 10:23" no e-mail contra "às 10h23" no portal: a `118` unificou a tela (FR-3747) e o e-mail ficou de fora. A recaída "a área do candidato, no endereço do certame" aparece quando `endereco_do_portal` vem vazio, como nas fixtures; pela gestão ele vem preenchido. | baixo |

O que **está certo**, e se preserva:

- não traz CPF, telefone, posição na ordem nem link que autentica (FR-290 da `019`; FR-084a da
  `010`);
- não promete a vaga (FR-292c);
- diz que o prazo corre do envio (FR-269a);
- o envio é idempotente, com a chave reservada antes do SMTP, e auditado como "enviada", e nunca
  "recebida" (`comunicar.py`, docstrings de `comunicar` e de `_concluir`).

### 1.2 A página da convocação de hoje

![Convocação em C1, desktop](capturas/hoje/c1-convocacao-desktop.jpg)

| Primeira tela a 375 px (C1) | Página inteira a 375 px (C1) |
|---|---|
| ![](capturas/hoje/c1-convocacao-375-primeira-tela.jpg) | ![](capturas/hoje/c1-convocacao-375.jpg) |

A `118` resolveu bem o que lhe cabia: o "O que fazer agora" vem primeiro, os selos são palavra, e a
ação cabe na primeira tela a 375 px (SC-1119). O que falta é **o significado**.

| # | Achado | Peso |
|---|---|---|
| T1 | **A página não diz o que aconteceu.** O título é só "Convocação", e com documento na chamada não há "Você foi convocada(o)". Essa frase só existe no ramo sem documento, em `convocacao.html:48`. Quem chega pelo e-mail lê "O que fazer agora" sem que nada confirme que foi chamado, para quê, nem que isso é uma boa notícia. | alto |
| T2 | **Nada diz o que a convocação não é.** A pergunta "a vaga está garantida?" não tem resposta na tela aberta. A frase "Este registro não é matrícula, bolsa nem contrato" só aparece **depois** do aceite (I1). | alto |
| T3 | **O prazo é uma linha de texto entre outras**, com o mesmo peso da frase de consequência, e sem o dia da semana nem quanto falta. A 375 px ele fica no fim da primeira tela. | médio |
| T4 | **Não há visão de progresso.** A frase "Você ainda precisa enviar 4 documentos e preencher o Requerimento" diz o que falta, mas não o que já está com a comissão ou conferido, que só se vê descendo. | médio |
| T5 | **O vocabulário do ato aparece cru.** Os dados mostram "Espécie: Para vaga inicial" e "Vencimento registrado"; o rótulo "Espécie" é do modelo de dados (`Convocacao.especie`). | baixo |
| T6 | **A sucessora não diz que substitui** (cenário `corr`). A página mostra "1ª chamada" com o prazo novo, 12/11, e nada diz que havia outra, com outro prazo, na mensagem que a pessoa guardou. | alto |
| T7 | **Depois do envio, a confirmação fica fora da tela** (1.4). | médio |

Os estados encerrados estão corretos e não pedem mudança de regra, só de título:

- **G, prazo vencido**: *"O prazo terminou em 05/11/2026, às 10h24. O fim do prazo não decide nada
  sozinho: quem registra o resultado é a comissão."*
- **I1, vaga aceita**: "Resultado registrado / Vaga aceita", com a ressalva do aceite.

Ver [`g-convocacao-375`](capturas/hoje/g-convocacao-375.jpg) e
[`i1-convocacao-375`](capturas/hoje/i1-convocacao-375.jpg).

### 1.3 O acesso de hoje

| Link direto, sem sessão | Link da mensagem, sem sessão | Código | Depois do código |
|---|---|---|---|
| ![](capturas/hoje/sem-sessao-link-direto-404-375.jpg) | ![](capturas/hoje/sem-sessao-link-da-mensagem-375.jpg) | ![](capturas/hoje/acesso-codigo-375.jpg) | ![](capturas/hoje/depois-do-codigo-375.jpg) |

| # | Achado | Peso |
|---|---|---|
| A1 | **O endereço da convocação, aberto sem sessão, responde 404**: *"Recurso não encontrado"*, com "Voltar às seleções". A causa está em `_inscricao_do_titular` (`views.py:2702`), que confere a titularidade com identidade `None` e recusa como inexistente. É correto contra quem não é titular (FR-1101 da `059`), mas **também alcança o próprio titular com a sessão expirada**. Hoje isso não aparece porque a mensagem aponta para a lista. Qualquer link direto, inclusive um favorito ou a aba que ficou aberta, cai nesse 404. | alto |
| A2 | **O destino existe, mas não alcança a convocação.** `acesso` guarda o `?destino=` na sessão (`views.py:834`), `abrir_sessao` o preserva no `cycle_key`, e `_entrar` (`views.py:1059`) o lê. O problema está em `_de_volta_a_vaga` (`views.py:1087`): ela só devolve a página da vaga ou a do Edital, e manda **qualquer outra rota para a lista**. A restrição é deliberada contra **praticar ato** a partir de endereço compartilhado. A convocação é GET e não pratica ato nenhum, como a página do Edital que a `062` admitiu. | médio |
| A3 | **A tela de acesso não diz para onde se vai.** "Entrar" e "Informe o código" são genéricos. A `072` já faz isso para a vaga (`_vaga_do_destino`), e não para a convocação. | baixo |
| A4 | **A duração da sessão não está declarada.** `config/settings/` não define `SESSION_COOKIE_AGE`, de modo que vale o padrão do Django: **14 dias**, sem expirar ao fechar o navegador. A `010` diz só que a sessão expirada exige novo desafio (FR-036) e que não há "lembrar de mim" (FR-037). Num computador compartilhado de polo, 14 dias é muito; para o convocado que volta no 4º dia, ajuda. **É verificação a fazer, e não defeito.** | verificar |

Hoje, com sessão válida, o caminho é: e-mail → lista → "Ver convocação" → convocação, com um clique
a mais. Sem sessão: e-mail → "Entrar" → e-mail digitado → código → lista → "Ver convocação" →
convocação.

### 1.4 Depois do envio

| Primeira tela depois do envio (375 px) | Página inteira |
|---|---|
| ![](capturas/hoje/depois-do-envio-375-primeira-tela.jpg) | ![](capturas/hoje/depois-do-envio-375.jpg) |

O envio volta a `#item-‹id›` (`views.py:2574`). O cartão enviado **já desceu** para "O que você já
apresentou", e a âncora rola a página até lá, quase no rodapé. A confirmação *"Documento recebido. A
comissão vai conferir."* é renderizada no topo, logo abaixo do título, e fica **fora da tela**. Os
três documentos que ainda faltam ficam **acima** da posição de rolagem. Quem envia o primeiro de
quatro documentos vê o cartão verde com "Aguardando conferência" e os dados do ato, e precisa subir
para continuar. O cartão diz "Recebido em…", e por isso não há perda de informação, mas o próximo
passo some.

---

## 2. Hierarquia proposta para a página

Na mesma página, sem *wizard* e sem página nova, em **cinco blocos**. Maquetes:

- [`convocacao.html`](maquetes/convocacao.html): C1, nada enviado;
- [`convocacao-apos-envio.html`](maquetes/convocacao-apos-envio.html);
- [`convocacao-pendencia.html`](maquetes/convocacao-pendencia.html): F;
- [`convocacao-sucessora.html`](maquetes/convocacao-sucessora.html): a correção.

| Desktop | Primeira tela a 375 px |
|---|---|
| ![](capturas/maquetes/convocacao-desktop.jpg) | ![](capturas/maquetes/convocacao-375-primeira-tela.jpg) |

1. **O significado.** O contexto (Processo, Edital), o título **"Você foi convocado!"** e uma frase:
   *"Esta é a etapa de enviar seus documentos e o Requerimento de Matrícula para a comissão
   conferir. Ela ainda não é a matrícula."* Nunca "aprovado", "vaga garantida", "matriculado" ou
   "bolsa concedida" sem o ato que os registre (FR-3751 da `118`; UX-155 a UX-158 da `063`).
2. **O prazo em destaque.** A data por extenso, com o dia da semana; *"Faltam 5 dias."* (ou *"Termina
   hoje, às 10h23."*); e a frase de consequência **fixa** da FR-1177 da `063`: *"Se você não atender
   no prazo, a comissão poderá registrar o não atendimento desta convocação."*
   - Sem desfecho automático e sem acréscimo. A FR-1177 proíbe qualquer outra frase de
     consequência, e a consequência só vem do Edital quando ele a declarar em forma estruturada
     (L-4). Uma primeira versão desta maquete acrescentava *"com o que o Edital prevê"*, e foi
     retirada por isso.
   - A origem do prazo ("conta a partir do envio da mensagem…") desce para o bloco 5: é verdade que
     a pessoa precisa saber, mas não na primeira tela.
3. **O progresso.** Uma frase e três contagens **em palavra e número**: *a enviar*, *aguardando
   conferência* e *conferidos*, com a ação principal *"Ver os documentos que faltam"*. **Sem barra.**
   Uma barra de 0 a 100 % lê como "quanto falta para ser aprovado", e 100 % seria a "falsa conclusão"
   que a FR-3728 da `118` proíbe. A contagem diz onde cada coisa está, e não promete nada.
4. **Os formulários, logo abaixo.** São os cartões da `118` como estão: selo em palavra, envio com o
   nome do documento no nome acessível, e o Requerimento como último cartão a fazer, com o botão que
   leva ao formulário. Depois vem "O que você já enviou".
5. **Os dados do ato, em segundo plano.** Chamada, comunicação, fundamento e atendimento, menores e
   sem moldura, depois de tudo. "Espécie: Para vaga inicial" vira *"Chamada: 1ª chamada, para vaga
   inicial"*.

**Por que não *wizard*.** Os documentos são independentes, chegam em dias diferentes, e a pessoa
volta várias vezes até o prazo, como no cenário F, em que dois são conferidos antes de os outros
chegarem. Um passo a passo esconderia o que já foi feito, obrigaria a refazer o caminho a cada
volta, e não tem ordem natural a impor. A vantagem que ele daria, uma coisa de cada vez, a contagem
e a ação principal já dão sem tirar a visão do todo.

**A primeira tela a 375 px é apertada.** A SC-1119 da `118` exige a contagem e o primeiro link de
tarefa dentro dos 812 px. A primeira versão da maquete a reprovava, porque o bloco 3 começava no fim
da primeira tela. Ela só coube depois de três ajustes:

- a explicação reduzida a uma frase;
- a origem do prazo descida para o bloco 5;
- as três contagens lado a lado, e não empilhadas.

Medido pelo `getBoundingClientRect` da ação principal, a 375 × 812, no roteiro:

| Maquete | Fim da ação principal | Folga |
|---|---|---|
| C1, nada enviado | 784 px | 28 px |
| F, com pendência | 811 px | 1 px |
| Sucessora | **942 px** | **fora da primeira tela** |
| Depois do envio | 725 px (o link "Próximo") | 87 px |

**A sucessora não cabe.** O aviso *"Esta convocação foi corrigida…"* empurra a ação para a segunda
tela. A SC-1119 não lista esse cenário, mas a pessoa que recebeu a correção é a que mais precisa
saber o que fazer. Há duas saídas, e as duas ficam para a implementação:

- encurtar o aviso para uma linha, *"Convocação corrigida: o prazo que vale é o desta página."*,
  com a data da anterior só no bloco 5;
- ou pôr o aviso dentro do bloco do prazo, que é exatamente o que ele corrige.

Um título de Processo mais longo empurra todas para baixo, e F já está a 1 px. Na implementação,
**a SC-1119 se mede de novo**, nos títulos reais. Se não couber, a explicação do bloco 1 encurta
antes de o prazo perder destaque.

**O título nos demais estados**, com a mesma estrutura e os blocos 3 e 4 trocados pelo que já existe
hoje:

| Estado | Título (h1) | Bloco 2 |
|---|---|---|
| Prazo correndo | Você foi convocado! | prazo e consequência |
| Comunicação não enviada (K) | Você foi convocado! | *"O prazo ainda não começou a correr: ele conta a partir do envio da comunicação."* |
| Prazo vencido sem desfecho (G) | O prazo desta convocação terminou | o núcleo do vencido da FR-3748 |
| Desfecho registrado (I1, I2) | Resultado da sua convocação | o rótulo do desfecho e a frase do aceite |
| Sucessora (`corr`) | Você foi convocado! | prazo novo, com *"Esta convocação foi corrigida. Ela substitui a mensagem enviada em ‹data›. O prazo que vale é o desta página."* acima, e sem o motivo (120, linhas 486–487) |

**O gênero.** O produto escreve hoje "convocada(o)". O título pedido foi "Você foi convocado!", e é o
das maquetes. As alternativas são:

- "Você foi convocada(o)!", que mantém a convenção do produto;
- "Chegou a sua convocação!", que é neutra e não depende de dado de gênero, que o sistema não tem.

A escolha é do usuário (seção 11, D-1).

**O depois do envio.** O envio volta a `#progresso`, e não ao cartão. A confirmação mora no bloco 3,
com `role="status"` e o próximo item como link: *"Recebemos a Certidão de nascimento ou casamento
em 05/11/2026, às 10h25. A comissão vai conferir. Próximo: Histórico escolar do ensino médio."* A
contagem já mostra 1 aguardando conferência. É mudança de template e de destino do `redirect`, sem
regra nova.

| Depois do envio (375 px) | Com pendência (375 px) | Sucessora (375 px) |
|---|---|---|
| ![](capturas/maquetes/convocacao-apos-envio-375-primeira-tela.jpg) | ![](capturas/maquetes/convocacao-pendencia-375-primeira-tela.jpg) | ![](capturas/maquetes/convocacao-sucessora-375-primeira-tela.jpg) |

---

## 3. Vocabulário por tipo de seleção

**O domínio não tem tipo de certame.** A L-6 da `063`, o princípio 6 da mesma spec e a D-010 da
`040` o registram. As famílias da `119` (FIC, Libras, UAB/bolsista, Aperfeiçoamento, TMD, Internos)
existem só na identidade visual da divulgação. A `063` proíbe de propósito `if curso / else
servidor` no texto. Então o vocabulário abaixo **não se implementa adivinhando o tipo**. Ou ele
vem de algo declarado, ou o texto fica no núcleo neutro.

**O núcleo neutro** vale para todo Edital e já é implementável:

- "Você foi convocado!";
- "a comissão confere";
- "o resultado desta convocação";
- "Esta convocação ainda não é ‹o ato final›".

A ressalva já existe no aceite: *"não é matrícula, bolsa nem contrato"*.

**O que varia**, se houver dado declarado para isso:

| Seleção | O ato real da convocação | Diga | Nunca diga antes do ato |
|---|---|---|---|
| Curso técnico (integrado, concomitante, subsequente), FIC, Libras | chamada para **matrícula**: entrega de documentos e Requerimento; a matrícula se efetiva depois, pelo registro acadêmico | "Você foi convocado para a matrícula." · "Envie os documentos e o Requerimento de Matrícula." | "matriculado", "aprovado", "sua vaga" |
| Graduação e pós (lato sensu, Aperfeiçoamento) | o mesmo, com homologação da matrícula conforme o Edital | "Você foi convocado para a matrícula no curso." | "aluno do curso", "matrícula efetivada" |
| Bolsista (UAB, tutor, apoio) | chamada para **cadastramento**: ficha, termo de compromisso, documentos; a bolsa depende de vinculação no programa | "Você foi convocado para o cadastramento como bolsista." · "Envie a Ficha de Cadastramento e o Termo de Compromisso." | "bolsa concedida", "contratado", "vinculado" |
| Professor formador ou colaborador | chamada para **entrega de documentos e assinatura do termo** | "Você foi convocado para apresentar os documentos e assinar o termo." | "contratado", "nomeado", "empossado" |
| Convocação para regularizar (`PARA_REGULARIZAR`) | chamada para **regularizar** o que levou ao indeferimento, quando o Edital o admite | "Você foi chamado para regularizar a sua situação nesta seleção." | "nova chance garantida", "indeferimento revertido" |
| Vaga que vagou (`SUPLENCIA`) | chamada para vaga que ficou disponível | "Uma vaga ficou disponível, e você foi convocado." | "você subiu na lista", "lista de espera" (UX-155 da `063`) |

**De onde viria o dado.** Há duas fontes, e as duas são decisão:

1. **A espécie, que já existe** (`VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR`). Ela decide as duas
   últimas linhas da tabela, e **isso já é implementável**: é ato gravado, e não inferência. Hoje ela
   só aparece crua no bloco 5.
2. **A finalidade da convocação, que não existe**: um campo fechado, declarado no Perfil (*matrícula*,
   *cadastramento de bolsista*, *apresentação de documentos e termo*), que escolhe a frase do bloco 1
   e a do e-mail. É requisito novo, na `019` ou numa spec própria, e cruza com a L-4 da `063`, a
   "ação e consequência estruturadas da convocação". Sem ele, a frase do bloco 1 diz *"enviar seus
   documentos"*, e a palavra "Matrícula" só aparece quando o Requerimento de Matrícula está pedido,
   o que já é dado (`requirement` da `029`).

---

## 4. Modelo de e-mail

[`maquetes/email.html`](maquetes/email.html) e [`maquetes/email.txt`](maquetes/email.txt), a
alternativa completa em texto puro, com as variantes da sucessora e da chamada sem documento.

| 720 px | Celular, 375 px | Modo escuro |
|---|---|---|
| ![](capturas/maquetes/email-desktop.jpg) | ![](capturas/maquetes/email-375.jpg) | ![](capturas/maquetes/email-375-escuro.jpg) |

**Assunto**: `Ifes · Convocação no Edital 72/2026: envie os documentos até 10/11`.

- A instituição, o Edital, a ação e a data estão nos primeiros ~45 caracteres, que é o que a lista do
  celular mostra.
- Sem documento na chamada, o assunto vira `Ifes · Convocação no Edital 72/2026: prazo até 10/11`.
- Na sucessora, vira `Ifes · Convocação corrigida no Edital 72/2026: novo prazo até 12/11`.
- O texto de pré-visualização repete a ação e o prazo.

**O corpo, de cima para baixo**:

- o título e o Processo;
- **a frase dos documentos**, que é a X3: *"Esta convocação pede documentos e o Requerimento de
  Matrícula. Você envia tudo pela sua área do candidato."*;
- o prazo em destaque, *"contado do envio desta mensagem"* (FR-269a);
- o botão **"Acessar minha convocação"**, com o endereço por extenso abaixo;
- como entrar, por e-mail e código, "numa mensagem separada";
- a ressalva *"ainda não é a matrícula"*;
- o canal de atendimento da unidade;
- o quadro "Para a sua segurança";
- o rodapé.

**O que não vai**: CPF, nome do documento, motivo de pendência, modalidade de reserva, número de
inscrição, anexo, imagem, fonte externa, pixel de rastreio e parâmetro de campanha no link.

- **Nem o número de documentos.** "4 documentos" parece inofensivo, mas a lista da chamada pode
  variar com a modalidade (um laudo, uma declaração de renda), e a contagem passaria a dizer algo
  sobre a cota de quem a lê. "Pede documentos" basta para a X3.
- **O nome da pessoa ficou de fora**, e é decisão (D-6). Uma saudação nominal é sinal de mensagem
  legítima contra *phishing*. Mas é dado pessoal, viaja no encaminhamento, e a FR-290 limita a
  mensagem ao "necessário para identificar a chamada".

**Compatibilidade, avaliada no desenho**: nenhuma afirmação abaixo foi testada num cliente real, e o
teste está na seção 10.

| Cliente ou condição | Como o modelo responde | Risco que fica |
|---|---|---|
| Gmail (web e app) | estilo em linha em tudo; o `<style>` é só acréscimo | o app com conta de outro provedor descarta `<style>`: perde o modo escuro próprio e a quebra de largura, e a mensagem continua legível a 600 px com zoom |
| Outlook de mesa (motor do Word) | botão como célula com `bgcolor`, e não fundo em `<a>`; tabelas de largura fixa; sem `max-width` decisivo | cantos retos no botão; o `border-left` do prazo pode sumir, e o texto "Prazo para atender" continua |
| Outlook.com e app | estilo em linha | inversão parcial no modo escuro |
| Celular | uma coluna; o `@media` alarga para 100 %; fonte de 16 px no corpo, 17 px no botão, alvo ≥ 44 px | sem o `@media` (Gmail com outra conta), a mensagem fica em escala reduzida |
| Imagens bloqueadas | não há imagem: a marca é texto | nenhum |
| Modo escuro | `color-scheme` e `@media (prefers-color-scheme: dark)` para Apple Mail e Outlook.com; capturado no Chromium | a inversão **forçada** do Gmail no celular reescreve as cores sem consultar o `<style>`; o verde do botão e o amarelo do prazo foram escolhidos por manterem contraste invertidos, **mas isso não foi verificado** |
| Leitor de tela | `lang="pt-BR"`, tabelas com `role="presentation"`, um `h1`, link com texto próprio ("Acessar minha convocação"), informação nunca só em cor | o endereço por extenso é lido caractere a caractere: fica depois do botão, para quem não precisa dele |
| Texto puro | `email.txt` diz tudo o que o HTML diz, com o endereço completo | nenhum |
| Tamanho | ~6 kB | longe do corte de 102 kB do Gmail |

**SPF, DKIM e DMARC: verificação a fazer, e não premissa.** Nada no repositório os configura, e não
deve: eles moram no DNS do domínio do remetente e no servidor de correio que envia. Antes de produção:

1. Saber de qual domínio sai o `DEFAULT_FROM_EMAIL`.
2. Conferir que o SPF desse domínio inclui o relé SMTP que a aplicação usa.
3. Conferir que o relé assina com DKIM no mesmo domínio do `From:`, que é o alinhamento.
4. Conferir que o DMARC do domínio existe, com `p=quarantine` ou `p=reject`.

Sem os três, um e-mail com botão e prazo é exatamente o que os filtros mandam para o spam. O texto
"Confira a caixa de spam" da tela do código é um remendo para isso. É pergunta para a equipe de TI
do Ifes, e está na seção 11 (D-8).

**O que se preserva na implementação.** `enviar_mensagem_de_convocacao` passa a chamar
`send_mail(..., message=texto, html_message=html)`, com os dois corpos renderizados de templates.
Nada mais muda:

- **auditoria**: a mesma trilha, "enviada em", e nunca "recebida";
- **idempotência**: a reserva da chave antes do SMTP continua igual, e a repetição concluída não envia;
- **prazo**: ele continua correndo do `enviado_em` gravado, e não do texto;
- **situações de mensagem**: nenhuma nova; a FR-084 da `010` continua com quatro, e o guardião
  `tests/test_situacoes_de_mensagem.py` não muda;
- **forma de convocar**: a convocação **por publicação** continua sem e-mail nenhum (D-001 da `066`).
  O modelo é só da mensagem individual, e a página do portal mostra no bloco 5 *"Publicada em
  ‹referência›"* no lugar de "Mensagem enviada em".

Um acréscimo para decidir (D-7): gravar em `ComunicacaoEmitida` **qual versão do modelo** saiu. Hoje
o texto se reconstrói do código mais os dados, e com dois corpos e variantes essa reconstrução fica
mais frágil.

---

## 5. Acesso: três alternativas

O ponto de partida é a P-001 da `010`: *"Não há link que autentica"*. O link viaja no histórico do
navegador, no encaminhamento da mensagem e no cabeçalho de origem, e por isso o código é digitado.

### A — o link aponta para a convocação, e o destino sobrevive ao código

O link da mensagem passa a ser `/selecoes/inscricoes/‹inscrição›/convocacao`. São três mudanças,
todas pequenas:

1. Numa rota do titular aberta **sem sessão**, como a convocação ou o acompanhamento, redirecionar
   para `acesso?destino=‹caminho›` **antes de qualquer leitura do identificador**, em vez do 404 de
   hoje. Fazer isso antes da consulta é o que não abre oráculo de existência: o mesmo redirecionamento
   vale para um identificador real e para um inventado. Para quem tem sessão e não é titular, a
   recusa continua 404 (FR-1101 da `059`).
2. `_de_volta_a_vaga` passa a aceitar a rota da convocação, que é GET e não pratica ato, como a página
   do Edital desde a `062`.
3. As telas de acesso dizem *"Depois do código, você vai direto para a convocação"*, **sem dizer de
   quem nem de qual Edital**. Antes do código, ler o identificador para nomear o Edital revelaria a
   quem tem o link encaminhado que ali existe uma inscrição.

O destino já sobrevive ao `cycle_key` e à reconciliação, que também termina em `_entrar`.

**Variante A′.** O link aponta para `/selecoes/convocacao`, uma rota sem identificador. Depois do
código, ela leva à única convocação em aberto, ou à lista se houver mais de uma. O e-mail fica sem
identificador nenhum, ao custo de uma rota nova e da regra da escolha.

| Acesso, com destino | Código, com destino |
|---|---|
| ![](capturas/maquetes/acesso-1-email-375.jpg) | ![](capturas/maquetes/acesso-2-codigo-375.jpg) |

### B — identificação facilitada, sem redigitar o e-mail

O link leva um identificador opaco e aleatório, de 128 bits, gravado no servidor e apontando para a
credencial. A tela mostra *"Enviar código para c•••••••1@exemplo.br"* e um botão **"Enviar código"**,
sem campo para digitar.

- O identificador sozinho **não dá acesso**: o código continua obrigatório.
- O código só sai num **POST**, e nunca ao abrir a página. Senão, o *scanner* de segurança que abre o
  link dispararia o código e consumiria o limite de pedidos.
- O identificador expira com a convocação e não carrega dado pessoal.

### C — link mágico de uso único e prazo curto

O link da convocação **não pode ser** o link mágico. Um link válido até o vencimento, de cinco dias
ou mais, é uma credencial ao portador circulando numa caixa postal. Por isso C tem duas etapas:

1. A convocação leva à tela de acesso, como em A.
2. A tela oferece *"Receber um link de entrada"*, que manda uma **segunda** mensagem com um link de
   uso único que vale 10 minutos, o mesmo prazo do código.

O link abre uma página com o botão **"Entrar"**, e o consumo acontece no POST, nunca no GET. Depois
do consumo, o token sai do endereço por redirecionamento, com `Referrer-Policy: no-referrer`, e nunca
vai a log. Opcionalmente, o link só vale no navegador que o pediu, amarrado por cookie.

### Modelo de ameaças

| Ameaça | A (destino) | B (identificação facilitada) | C (link mágico) |
|---|---|---|---|
| **E-mail encaminhado** | quem recebe não entra: o código vai para a caixa da titular | quem recebe pode **disparar** códigos para a caixa da titular (incômodo, com limite) e vê o endereço mascarado, que já tinha | se o link mágico for encaminhado dentro dos 10 minutos, **quem recebe entra**; com amarração ao navegador, não |
| **Caixa postal comprometida** | quem a controla pede o código e entra, **como hoje** | igual a hoje | igual a hoje, e mais fácil: um clique |
| **Scanner que abre o link** (Safe Links, Mimecast) | inofensivo: GET sem estado | inofensivo **se** o código só sair no POST | **consome** o token se o consumo for no GET; por isso o POST é obrigatório, mas há *scanners* que submetem formulários |
| **Token em log ou histórico** | não há token: o endereço tem o identificador da Inscrição, que não autoriza nada (princípio do identificador público, constituição) e não é dado pessoal (FR-1102 da `059`; FR-401 da `029`) | o identificador opaco fica no histórico; sozinho, não entra | o token fica no histórico **até ser consumido**; depois, inútil |
| **Reutilização** | nada a reutilizar | o identificador dispara código quantas vezes o limite deixar (FR-030 da `010`) | uso único (como a FR-025 para o código) |
| **Outro dispositivo** | funciona: e-mail e código em qualquer aparelho | funciona | sem amarração, funciona e é o risco do encaminhamento; com amarração, **falha** justamente no caso mais comum: o app do Gmail abre o link num navegador interno, com outro pote de cookies, e não no navegador onde o pedido foi feito |
| **Documentos sensíveis** | o acesso continua pedindo sessão autenticada por código; nada muda | nada muda | a autenticação fica um grau mais fraca (um clique em vez de algo digitado), sobre a mesma área que guarda certidão, comprovante de renda e laudo |

### Custo e ganho

| | Muda requisito | Muda dado | Esforço | Ganho |
|---|---|---|---|---|
| **A** | FR-1104 da `059` (o endereço da mensagem); a US1 da `010` diz "chegar direto ao que é meu", e o destino só estende isso | nenhum | pequeno: um redirecionamento, uma condição em `_de_volta_a_vaga`, uma frase em duas telas | tira o passo da lista e o 404 da sessão expirada; é a maior parte do ganho |
| **B** | P-001 não; FR-020/021 da `010` (resposta neutra) pedem cuidado com o endereço mascarado | tabela nova (identificador → credencial, com expiração) | médio | poupa digitar o e-mail, que o navegador já preenche sozinho (`autocomplete="email"`) |
| **C** | **P-001 da `010`, revista**, e decisão institucional de segurança | tabela nova de token; segunda mensagem, que é uma situação nova da FR-084 ou uma variante da do código | alto | poupa digitar seis dígitos, mas falha entre aplicativos no celular se for amarrado, e enfraquece a autenticação se não for |

**Recomendação: A.** É a menor mudança com ganho real. Ela remove o único passo que não serve a
ninguém, a lista entre o e-mail e a convocação, e o único **erro**, o 404 do titular com a sessão
vencida. Não toca na P-001.

B ganha pouco onde o navegador já preenche o e-mail. C só vale se o teste com pessoas (seção 9)
mostrar que **o código** é onde elas desistem, e não o que vem antes dele. Mesmo então, a amarração
ao navegador precisa ser testada no app do Gmail e do Outlook antes de qualquer decisão.

---

## 6. Percurso no navegador, caso a caso

*Hoje* foi percorrido nos bancos de demonstração; *Com A* é o desenho, sobre o mesmo código.

| Caso | Hoje | Com A e a página proposta |
|---|---|---|
| **Sessão válida** | e-mail → lista ([captura](capturas/hoje/c1-lista-375.jpg)) → "Ver convocação" → convocação | e-mail → convocação |
| **Sessão expirada** (ou outro aparelho) | link da mensagem → "Entrar", sem destino → código → lista → "Ver convocação"; um link direto daria **404** ([captura](capturas/hoje/sem-sessao-link-direto-404-375.jpg)) | link → "Entre para ver a sua convocação" → código → convocação |
| **Primeiro acesso** (convocado que nunca entrou pelo e-mail, ou inscrição antiga a reconciliar) | o mesmo da sessão expirada; a reconciliação termina em `_entrar` e cai na lista | o mesmo, com o destino honrado também depois da reconciliação; a mensagem *"Pronto: sua participação anterior está aqui."* aparece na convocação |
| **Link antigo depois de uma correção** (`corr`) | a lista leva à sucessora, com o prazo novo e **sem dizer** que substitui ([captura](capturas/hoje/corr-convocacao-375.jpg)) | o link da primeira mensagem é o da Inscrição, e abre **a vigente**, com *"Esta convocação foi corrigida… O prazo que vale é o desta página."* |
| **Documento pendente** (F) | o cartão sobe com "Precisa de correção" e o motivo; a pessoa só sabe se voltar | o mesmo cartão, mais a contagem "a corrigir" no bloco 3; o aviso por e-mail fica para a seção 7 |
| **Requerimento e documentos juntos** (C1) | o Requerimento é a 5ª tarefa da lista | o Requerimento é o último cartão a fazer, com o próprio botão; a contagem o inclui |
| **Envio** | âncora no cartão que desceu; confirmação fora da tela (1.4) | volta ao bloco 3, com a confirmação e o próximo item |
| **Confirmação e acompanhamento** | o acompanhamento diz o que falta ([captura](capturas/hoje/c1-acompanhamento-375.jpg)); não muda | não muda; "Voltar ao acompanhamento" fica no bloco 5 |
| **Prazo vencido** (G) | "O prazo terminou", com o resumo do que ficou; nenhum formulário | o mesmo conteúdo, com o título "O prazo desta convocação terminou" |
| **Convocação já decidida** (I1) | "Resultado registrado / Vaga aceita", com a ressalva do aceite | o mesmo, com o título "Resultado da sua convocação" |

---

## 7. Pendências (QI-7): política de avisos complementares

**Proposta à parte. Não se ativa nada.** Ela depende da revisão da FR-084 da `010`, que seria a
quinta situação, e da mesma validação de LGPD que mantém `AVISOS_AOS_CANDIDATOS` desligada em
produção. A recomendação da `118` (linhas 1180–1202) é a base, e este estudo só a fecha em regras:

1. **Por gesto humano, por lote.** Quem confere decide *"Avisar as pessoas com pendência nesta
   chamada"*. O sistema não dispara ao registrar uma pendência, nem por "vencimento próximo": isso
   seria o lembrete que a FR-084 exclui pelo nome.
2. **No máximo um aviso por pessoa por chamada por dia**, e **nenhum**:
   - depois do vencimento;
   - com desfecho registrado;
   - para item que a pessoa já reenviou depois da pendência ("complementado, aguardando
     conferência").
3. **Sem motivo e sem nome de documento.** O texto diz *"Há documento da sua convocação no Edital
   72/2026 que precisa de atenção. O prazo continua sendo até ‹vencimento›."* e aponta a convocação
   pelo mesmo link de A. O motivo fica no portal (FR-3584 da `115`), porque ele pode revelar saúde,
   renda ou cota.
4. **Distinto da convocação.** O assunto é `Ifes · Edital 72/2026: há documento da sua convocação
   para revisar`, que não começa por "Convocação". O rodapé é fixo, no molde da FR-1257 da `066`:
   *"Este aviso não é a convocação e não altera o seu prazo."*
5. **Não reinicia prazo e não substitui o ato.** Nada no aviso cria prazo de complementação. Dar mais
   prazo continua sendo corrigir a convocação por sucessão (FR-3618 da `115`; `120`). O aviso não
   grava `ComunicacaoEmitida`.
6. **O mesmo despacho da `066`**: fila, tentativa registrada antes do envio, resultado indeterminado
   que nunca se reenvia sozinho, e limite por minuto. Não sai no clique, porque a conferência é feita
   em lote e o SMTP síncrono travaria a tela.
7. **Também na convocação por publicação?** Ali não há e-mail de convocação, mas a pendência é
   individual e só se vê no portal. **É decisão própria** (D-5). O argumento a favor é que a pessoa
   não tem outro modo de saber. O argumento contra é que seria o único e-mail individual num certame
   que declarou não mandar nenhum.

Os outros avisos imagináveis ficam **fora**, e o motivo é o seguinte:

- "**documento conferido**" e "**resultado registrado**": resultado se publica, não se avisa;
- "**faltam 2 dias**": é lembrete, que a FR-084 exclui.

---

## 8. Maquetes e viabilidade técnica

| Maquete | O que mostra |
|---|---|
| [`convocacao.html`](maquetes/convocacao.html) | os cinco blocos, nada enviado (C1), em desktop e a 375 px |
| [`convocacao-apos-envio.html`](maquetes/convocacao-apos-envio.html) | a confirmação no bloco 3 e o cartão em "O que você já enviou" |
| [`convocacao-pendencia.html`](maquetes/convocacao-pendencia.html) | a pendência à frente, com o motivo só no portal (F) |
| [`convocacao-sucessora.html`](maquetes/convocacao-sucessora.html) | a correção dita, sem o motivo |
| [`acesso-1-email.html`](maquetes/acesso-1-email.html), [`acesso-2-codigo.html`](maquetes/acesso-2-codigo.html) | o caminho de A, com a frase de destino |
| [`email.html`](maquetes/email.html), [`email.txt`](maquetes/email.txt) | o e-mail e a alternativa em texto |

As capturas estão em [`capturas/maquetes/`](capturas/maquetes/). Nenhuma das telas tem rolagem
horizontal a 375 px, nem erro no console, medido pelo `scrollWidth` no roteiro.

**Viabilidade:**

- **Folha real.** As maquetes do portal carregam `shared/tokens.css` e `portal/portal.css` do
  repositório. [`maquetes/maquetes.css`](maquetes/maquetes.css) traz **só** as classes novas:
  `.significado-da-convocacao`, `.prazo-em-destaque`, `.progresso-das-obrigacoes`,
  `.contagem-das-obrigacoes`, `.confirmacao-do-envio`, `.dados-do-ato` e `.destino-do-acesso`.
  Os cartões, os selos, o envio e `.principal` são os de hoje. `.nota-da-maquete` é do estudo.
- **CSP.** Nenhuma maquete do portal usa `style=""`, `<style>` ou `<script>`, que a política da
  `091`/`092` recusaria. O e-mail usa estilo em linha porque não é tela do portal e porque cliente
  de e-mail não carrega folha externa.
- **Guardiões que vão cobrar.** O de classe sem regra na folha (`test_acessibilidade`) cobra as
  classes novas em `portal.css`. A varredura de vocabulário cobra as frases novas, inclusive contra
  "aprovado" e similares. A SC-1119 a 375 px tem de ser medida de novo (seção 2).
- **Dados.** Tudo o que a página proposta mostra **já é lido hoje**:
  - a contagem sai de `obrigacoes.totais`;
  - o "foi corrigida" sai de `convocacao_anterior` e do envio da anterior;
  - o dia da semana e o "faltam N dias" saem do vencimento, no fuso local;
  - "Pede documentos" no e-mail vem da lista gravada no ato de convocar.

  Nenhuma migration. A exceção é a finalidade da seção 3, que é campo novo e por isso fica fora do MVP.

---

## 9. Plano de teste com pessoas reais

É a X5 da `118`, e a Lei 15.263/2025 (art. 5º, XVIII) prevê o teste com o público. A forma é
**moderada e remota ou presencial**, com protótipo navegável, que pode ser montado a partir das
maquetes. A ordem dos protótipos alterna entre participantes:

- o e-mail e a página de hoje (capturas reais);
- o e-mail e a página propostos.

**Quem participa.** São 6 a 8 pessoas por rodada. Duas rodadas pegam a maior parte dos problemas
graves, e a segunda roda depois dos ajustes. Recrutamento:

- inscritos de curso técnico subsequente (adultos) e de curso técnico integrado, com o responsável;
- um bolsista ou tutor de Edital UAB;
- pelo menos uma pessoa que só usa celular;
- uma de baixa familiaridade digital;
- uma que usa leitor de tela.

**Roteiro.** A pessoa recebe o e-mail numa caixa de teste no próprio celular e é convidada a "fazer
o que faria". Depois responde, sem voltar à tela:

| # | Pergunta | Resposta certa |
|---|---|---|
| P1 | Fui convocado para quê? | enviar documentos e o Requerimento, para a comissão conferir |
| P2 | A vaga está garantida? | não; depende da conferência e do resultado que a comissão registra |
| P3 | O que faço agora? | entrar e enviar os documentos que faltam |
| P4 | Quais documentos faltam? | os da lista, ou "3, e o Requerimento" depois de um envio |
| P5 | Qual é o prazo? | a data e a hora |
| P6 | O que acontece se eu não atender? | a comissão poderá registrar o não atendimento; não é automático |
| P7 | Como sei se foram aceitos? | o selo "Conferido" na página; nada chega por e-mail (ou o aviso da seção 7, se adotado) |
| P8 | Como volto à convocação? | pelo link da mensagem ou por "Minhas inscrições" |

**Métricas:**

- **Entendimento.** É a proporção de respostas certas por pergunta. A meta é ≥ 80 % em todas, e
  **≤ 10 % de "sim" em P2**, que é o erro que mais custa: quem acha que já está matriculado não envia
  nada.
- **Tempo até a ação principal.** Do e-mail aberto até a página da convocação, e até o primeiro
  "Escolher arquivo". As metas são mediana ≤ 60 s para chegar e ≤ 2 min para o primeiro envio, com
  sessão expirada. Ver o código é parte do percurso, e a SC-001 da `010` diz menos de 60 s para
  entrar.
- **Erros.** São quatro: cair na lista e não achar a convocação; enviar arquivo no item errado; não
  ver o Requerimento; e, no caso da sucessora, apontar o prazo antigo como o que vale. A meta é zero
  no último.
- **Desistência no código.** É quantas pessoas pedem o código e não o digitam, e por quê. **É o dado
  que decide se C vale o custo.**
- **Facilidade percebida.** Uma pergunta só no fim (SEQ, de 1 a 7), para comparar hoje e proposta.

A sucessora é tarefa à parte: a pessoa recebe as duas mensagens, a original e a da correção, e
responde P5.

---

## 10. Impactos nas specs e MVP

### Por spec

Legenda: **UX** é melhoria que cabe no requisito como está; **Req.** é revisão de requisito escrito;
**Inst.** é decisão institucional, de segurança, LGPD ou TI.

| Spec | Impacto | Tipo |
|---|---|---|
| `010` | A US1 diz "chegar direto ao que é meu", e o destino da convocação só a estende, como fez a `062`. | UX |
| `010` | A FR-084 não muda em A nem no e-mail novo. | — |
| `010` | A QI-7 é a 5ª situação. | Req. + Inst. |
| `010` | C revê a P-001. | Req. + Inst. |
| `010` | A duração da sessão (14 dias, não declarada) pede uma decisão. | Inst. |
| `019` | A FR-290 ganha "quando a chamada pede documentos, a mensagem o diz" (X3) e a variante da sucessora. | Req. |
| `019` | O HTML com alternativa em texto e o novo assunto cabem no requisito. | UX |
| `019` | A finalidade da convocação (seção 3) seria campo novo. | Req. |
| `029` | Nenhum. O Requerimento vira cartão, com a mesma política e a mesma rota. | UX |
| `059` | **A FR-1104** fixa o endereço da mensagem em "Minhas inscrições" e diz que "o texto da mensagem MUST NOT mudar". A e o e-mail novo a revisam. | Req. |
| `059` | A rota do titular sem sessão deixa de responder 404 e passa a redirecionar ao acesso. A FR-1101 se preserva para quem tem sessão e não é titular. | UX |
| `063` | O título por estado e o prazo em destaque cabem no requisito. A frase de consequência continua a da FR-1177, sem acréscimo. | UX |
| `063` | Consequência declarada pelo Edital, em forma estruturada (L-4). | Req. |
| `066` | Nenhum no MVP. A política da seção 7 reusa o despacho e o rodapé. | Req. (QI-7) |
| `115` | Nenhum no MVP. A QI-7 revê a FR-3614. | Req. (QI-7) |
| `118` | Os cinco blocos da FR-3735 viram outra ordem: significado, prazo, progresso, formulários, dados. "O que fazer agora" passa a ser o bloco 3. **A SC-1119** se reescreve sobre o novo bloco e se mede de novo. A X3 se resolve; a X5 é a seção 9. | Req. (redação da FR-3735 e da SC-1119) |
| `120` | A frase da sucessora no portal e no e-mail, que a `120` deixou registrada sem desenvolver (linhas 81 e 612–614). O motivo continua fora. | Req. |

### MVP em dois incrementos

**Incremento 1 — a comunicação, e a navegação direta.** Uma spec, sem migration. Sequência:

1. **A página** (`convocacao.html`, `obrigacoes.py`, `portal.css`), com os cinco blocos, o título por
   estado, a sucessora dita e o envio voltando a `#progresso`.
   - Aceite: as oito perguntas da seção 9 respondidas pelo texto da primeira tela, nos cenários C1,
     F, G, I1 e `corr`.
   - Aceite: a SC-1119 reescrita passa a 375 × 812.
   - Aceite: nenhum termo da FR-3751.
   - Aceite: a consequência é só a frase da FR-1177.
   - Aceite: a sucessora diz *"foi corrigida"* e *"o prazo que vale é o desta página"*, sem o motivo.
   - Aceite: depois do envio, a confirmação e o próximo item estão na primeira tela.
2. **O acesso A**: o redirecionamento sem sessão, `_de_volta_a_vaga` e a frase nas duas telas.
   - Aceite: o titular com a sessão expirada, pelo link direto, chega à convocação depois do código,
     **sem passar pela lista**, inclusive depois da reconciliação.
   - Aceite: o redirecionamento sem sessão é idêntico para identificador real e inventado.
   - Aceite: com sessão de outra pessoa, continua 404.
   - Aceite: nenhum destino executa ato (POST continua POST).
3. **O e-mail**: os templates `.html` e `.txt`, o assunto, a frase dos documentos, a variante da
   sucessora e o link de A.
   - Aceite: o texto puro contém tudo o que o HTML contém.
   - Aceite: nenhum CPF, nome de documento, motivo, modalidade, imagem ou recurso externo, com teste
     que varre o HTML por `src=`, `http` fora do link do portal e o CPF da fixture.
   - Aceite: a repetição com a mesma chave continua sem enviar.
   - Aceite: `test_situacoes_de_mensagem` inalterado.
   - Aceite: a leitura manual em Gmail (web e Android), Outlook de mesa, Outlook.com e Apple Mail,
     claro e escuro, registrada com captura.
   - Pré-requisito fora do código: SPF, DKIM e DMARC conferidos (D-8).
4. **O teste com pessoas**, sobre o incremento 1 em homologação.

O incremento 1 pede revisar a FR-290 da `019`, a FR-1104 da `059`, a FR-3735 e a SC-1119 da `118` e
o ponto da sucessora da `120`. São quatro redações, nenhuma regra nova de domínio, e é o que a X3
pedia.

**Incremento 2 — só se o teste o justificar.**

- **2a, o aviso de pendência (QI-7)**, se a instituição o admitir, com a política da seção 7. Pede a
  revisão da FR-084, a validação de LGPD e o gesto na tela de conferência.
- **2b, o link mágico (C)**, **somente** se o teste mostrar desistência no código. Pede a revisão da
  P-001, o teste da amarração ao navegador nos apps de e-mail e um parecer de segurança.

As duas são independentes, e 2a é a de maior valor: a pendência no 4º dia de um prazo de 5 é, para
quem não volta ao portal, um prazo perdido.

---

## 11. O que decidir

| # | Decisão | Opções | Recomendação do estudo |
|---|---|---|---|
| D-1 | O título da página | "Você foi convocado!" · "Você foi convocada(o)!" · "Chegou a sua convocação!" | a convenção do produto, "convocada(o)", ou a neutra; o masculino genérico destoa do resto do portal |
| D-2 | O link da mensagem (FR-1104 da `059`) | lista, como hoje · convocação (A) · rota sem identificador (A′) | A |
| D-3 | O acesso | A · B · C | A agora; C só com evidência do teste |
| D-4 | A frase dos documentos e a variante da sucessora (X3; FR-290 da `019`; `120`) | sim · não | sim, no incremento 1 |
| D-5 | O aviso de pendência (QI-7) e, se sim, também na convocação por publicação | não · sim, só na mensagem individual · sim, nas duas | decidir junto com a validação de LGPD |
| D-6 | O nome da pessoa no e-mail | sem nome · primeiro nome | sem nome, até haver avaliação de LGPD |
| D-7 | Gravar a versão do modelo da mensagem em `ComunicacaoEmitida` | não · sim | sim, se o incremento 1 tiver variantes |
| D-8 | SPF, DKIM e DMARC do domínio remetente | conferir com a TI | antes de produção, e independente de tudo o mais |
| D-9 | A duração da sessão do candidato | 14 dias (padrão, hoje) · menor · expirar ao fechar | decidir com a TI; o estudo não recomenda número |
| D-10 | A finalidade da convocação como dado declarado (seção 3) | não · sim, campo fechado no Perfil | registrar; não entra no MVP |

---

## 12. Como reproduzir

Em [`roteiro/`](roteiro/):

- **`montar.py`** monta um cenário num banco já preparado, registra a identidade da candidata e
  imprime a chave de uma sessão aberta. Os parâmetros são `LETRA=C1`, `F`, `G`, `I1` ou `A`, e
  `CORRIGIR=1` aplica a correção da `120`. Roda por `manage.py shell`, com o `.env` do backend
  carregado, `DB_NAME` próprio e `ARQUIVOS_CANDIDATOS_RAIZ` próprio.
- **`capturar.py`** tira as capturas reais. Os identificadores e as chaves de sessão no topo são os
  desta execução, e se trocam pelos que `montar.py` imprimir. O modo `acesso1`/`acesso2` faz o
  acesso de verdade, e o código se lê no terminal do runserver.
- **`variantes.py`** gera as três variantes a partir de `maquetes/convocacao.html`, para que fiquem
  idênticas fora do que muda.
- **`capturar_maquetes.py`** captura as maquetes por `file://`, com a medida de rolagem horizontal; **`medir.py`** mede onde termina a ação principal a 375 × 812.

```bash
createdb ps_estudo_conv_base && make preparar DB_NAME=ps_estudo_conv_base
```

```bash
createdb -T ps_estudo_conv_base ps_estudo_conv_c1
```

Os bancos `ps_estudo_conv_*` desta execução ficaram no cluster local, e podem ser apagados.
