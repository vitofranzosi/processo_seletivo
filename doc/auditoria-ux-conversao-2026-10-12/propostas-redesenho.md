# Propostas de redesenho — vitrine, seleção e início da inscrição

**Data:** 2026-10-12 · Parte da [auditoria de UX e conversão](../auditoria-ux-conversao-2026-10-12.md).
Os achados `C-NN` estão no [diagnóstico](diagnostico.md); a ordem de execução, na
[priorização](priorizacao.md).

> **Proposta, não especificação.** Nada aqui foi implementado nem deve ser lido como requisito. Os
> wireframes são textuais de propósito: mostram ordem e peso, e não pretendem fixar desenho.

---

## 1. Princípios das duas alternativas

Valem para A e para B, e vêm das decisões já registradas:

1. **A consulta continua sendo o endereço**, sem JavaScript (024, D-002, UX-017).
2. **Um link por cartão**, o cartão inteiro como alvo (L8).
3. **Situação por cor e palavra**, no mesmo lugar em todo cartão (UX-016, UX-019).
4. **Ausência não vira frase** (D-009); **nenhum estado agregado inventado** (047, D-002) — o que a
   vitrine passa a dizer das encerradas são **fatos datados**.
5. **Nada novo no domínio** para o escopo recomendado. Onde uma proposta precisa de dado que não
   existe, ela diz.
6. **375 px sem rolagem lateral**, e o celular desenhado primeiro (009 FR-079, 024 UX-018).
7. **Um processo pode ter vários Editais, e um Edital, vários Perfis.** Nenhuma proposta supõe
   "uma seleção = uma vaga".

## 2. Alternativa A — Evolução conservadora

### 2.1 Conceito

Mesma página, mesmos componentes, mesma folha. Muda a **ordem** (oportunidade antes do filtro), o
**peso** (oportunidade no título, Processo no metadado), o **texto** e três fatos que o sistema já sabe
e o cartão não diz. Impacto arquitetural baixo: templates, CSS, `leitura.py` e um seletor em lote.

### 2.2 Vitrine — estrutura

**Celular (375 px):**

```
┌──────────────────────────────────────┐
│ Cefor/Ifes · Seleções         Entrar │
├──────────────────────────────────────┤
│ Processos seletivos do Cefor/Ifes    │  h1
│ 1 seleção com inscrições abertas.    │  linha de fato, do dado
│ ┌──────────────────────────┐ ┌─────┐ │
│ │ Procurar cargo ou curso  │ │ Ir  │ │  busca sempre visível
│ └──────────────────────────┘ └─────┘ │
│ ▸ Mais filtros e ordenação           │  <details>, fechado sem consulta
│                                      │
│ INSCRIÇÕES ABERTAS                   │
│ ┌──────────────────────────────────┐ │
│ │ ABERTA            Faltam 19 dias │ │
│ │ Professor Substituto e Técnico-  │ │  título do Edital
│ │ Administrativo                   │ │
│ │ Professor de Informática (3) ·   │ │  Perfis com vagas, até 3 + "e mais N"
│ │ Técnico de Laboratório (reserva) │ │
│ │ Campus Serra · Campus Vitória    │ │  localidades
│ │ Até 01/11/2026, 20h47            │ │
│ │ [ Ver vagas e inscrever-se ]     │ │
│ │ Processo Seletivo Simplificado   │ │  metadado, discreto
│ │ 2026 · Edital 01/2026 · Cefor    │ │
│ └──────────────────────────────────┘ │
```

A busca fica — ela é o que serve ao Perfil A na primeira tela. Situação, cargo ou curso e ordenação
vão para um `<details>` que **abre sozinho** quando há consulta ativa nesses campos (o servidor
renderiza `open`), e o botão "Filtrar" vai junto. Sem script.

Estimativa, a partir das alturas medidas: o primeiro cartão subiria de 602 px para ~300 px, e o título
da primeira oportunidade entraria na primeira tela a 375 × 667. **Estimativa, a medir na
implementação.**

**Desktop (1280 px):** a barra de consulta fica como está (uma linha, 100 px — já é o modelo da
gestão), com o formulário inteiro visível. Muda o cartão e o peso dos grupos: cabeçalho de grupo com o
peso de um `h2` de verdade, e as **encerradas em cartão compacto** (sem a linha de vagas), que ocupa
metade da altura.

### 2.3 Cartões

| Campo | Aberta | Em breve | Encerrada | Sem período | Na seleção | Só no Edital |
|---|---|---|---|---|---|---|
| Marca de situação | sim | sim | sim | sim | sim | — |
| Título do Edital | **título** | **título** | **título** | **título** | `h1` | — |
| Perfis, com vagas por Perfil | até 3 + "e mais N" | idem | não | não | completo | — |
| Localidades | sim | sim | não | não | por Perfil | — |
| Prazo e tempo restante | sim | início e fim | data do fim | — | sim | — |
| Fato mais recente (resultado, recurso, sorteio) | — | — | **sim** | sim, se houver | completo | — |
| Requisitos | não | não | não | não | sim | integral |
| Documentos e Requerimento | não | não | não | não | anunciados | integral |
| Atribuições, carga, remuneração | não | não | não | não | sim | integral |
| Processo, número, unidade | metadado | metadado | metadado | metadado | subtítulo | — |
| Modalidades e vagas por modalidade | não | não | não | não | nomes (números: pendente desde 13/09) | integral |

**Por que vagas por Perfil, e não a soma.** "Professor de Informática (3) · Técnico de Laboratório
(reserva)" diz o que a soma esconde, e ocupa o mesmo espaço. Acima de três Perfis, "e mais N" — um
Edital de trinta polos não pode virar trinta nomes no cartão (C-08).

**O fato da encerrada** (C-03) é **um**, o mais recente, em uma linha:

- "Resultado preliminar publicado em 12/10/2026 · recurso até 17/10/2026"
- "Sorteio realizado em 12/10/2026"
- "Resultado definitivo publicado em …"

Sai das mesmas leituras que a página da seleção já usa, feitas **em lote** para os cartões da página.
O convite muda com ele: "Ver resultado" quando há resultado, "Ver a seleção" quando não há.

### 2.4 Página da seleção

```
┌──────────────────────────────────────┐
│ ← Todas as seleções                  │  "Voltar aos resultados" só com consulta
│ ABERTA                               │
│ Edital 01/2026 — Professor Substituto│
│ e Técnico-Administrativo             │
│ Inscrições até 01/11/2026, 20h47.    │
│ Faltam 19 dias.                      │
│ ┌──────────────────────────────────┐ │
│ │ O que esta seleção oferece       │ │  resumo, do dado
│ │ Professor de Informática — 3     │ │  cada linha é âncora #vaga-…
│ │ Técnico de Laboratório — reserva │ │
│ │ [ Ver vagas e inscrever-se ↓ ]   │ │  âncora para #vagas-titulo
│ └──────────────────────────────────┘ │
│ Próximo, em 16/11/2026: Aplicação…   │
│ [ Ler o Edital completo (PDF) ]      │
│ ⚠ Este Edital foi retificado…        │
```

O resumo **não** escolhe Perfil: lista os que existem, com o número de cada um, e cada linha leva à
vaga — o que resolve a ressalva da L4 ("decidir o que fazer quando o Edital tem vários Perfis"). Com um
Perfil só, o resumo é uma linha e o botão leva direto à vaga. A âncora de vaga ganha destaque por
`:target` (borda à esquerda na cor de ação), que serve também à volta da autenticação e à campanha.

No cartão da vaga, quando `requerimento_momento` é "na inscrição", uma linha depois dos documentos:
"Além dos documentos, a inscrição pede o preenchimento do Requerimento de Matrícula." (C-14).

### 2.5 Início da inscrição

| Tela | Hoje | Proposta |
|---|---|---|
| Acesso | "Entrar" / "Sem senha: enviamos um código para o seu e-mail." | Com destino de vaga: **"Confirme seu e-mail para se inscrever"**, e abaixo "Professor de Informática · Edital 01/2026". Sem destino: como está. |
| Código | botão "Entrar" | com destino de vaga: **"Confirmar e continuar"**; acrescentar "Não chegou? Confira a caixa de spam." antes do reenvio |
| Seus dados | "Pedimos uma única vez…" | acrescentar a finalidade e a vaga (texto em §5) |
| Volta à vaga | página rolada, sem nada | mensagem no alto do cartão da vaga: "Você entrou como m@ex.br. Para abrir sua inscrição nesta vaga, toque em Inscrever-se." + destaque `:target` |

O segundo clique **fica** — é a garantia de que um link compartilhado não cria inscrição. O que muda é
que a tela o explica.

A vaga do destino sai da própria rota (`_rota_do_destino` já a resolve); o nome do Perfil sai da
versão vigente. Nada novo no domínio.

### 2.6 Vantagens, desvantagens, riscos, dependências

| | |
|---|---|
| **Vantagens** | Ataca os achados Alto das três tarefas (encontrar, começar, acompanhar); nenhuma decisão é revogada, e a única revisada — o achado da `024` sobre títulos repetidos — não toca conteúdo normativo; reaproveita todo componente; pode sair em lotes pequenos |
| **Desvantagens** | A vitrine continua sendo uma lista de Editais — não de oportunidades; a identidade visual continua anônima; nada passa a ser medido |
| **Riscos** | Testes que afirmam texto e estrutura (`test_vitrine.py`, `test_detalhe_selecao.py`, `test_consulta_da_vitrine.py`, `test_acessibilidade_do_portal.py`, `test_porta_de_entrada.py`, `test_peso_da_vitrine.py`) mudam junto. Eles **localizam** compromissos — cada asserção aponta a decisão que a originou — e não tornam o texto intocável: a spec relê a decisão e diz se a mantém; o fato da encerrada pode estourar o orçamento de consultas se lido por cartão |
| **Dependências** | Seletor em lote para o fato da encerrada; nenhuma migration; nenhuma decisão do produto além das de texto |
| **Complexidade** | **Baixa a média**: texto e template baixa; fato da encerrada média |

## 3. Alternativa B — Evolução substantiva

### 3.1 Conceito

A vitrine deixa de ser lista de Editais e passa a ser **lista de oportunidades agrupadas por Edital**,
numa composição mais editorial: uma introdução curta que diz o que existe, as oportunidades abertas em
primeiro plano, o que está em andamento numa faixa de acompanhamento e o que terminou num arquivo. A
página da seleção ganha um bloco "Como participar" e, no celular, uma barra fixa com o prazo e o
atalho para as vagas. A base pública ganha assinatura institucional.

### 3.2 Vitrine — estrutura

**Desktop (1280 px):**

```
┌───────────────────────────────────────────────────────────────────────────┐
│ [marca Ifes] Cefor · Processos seletivos                  Minhas inscrições│
├───────────────────────────────────────────────────────────────────────────┤
│ Processos seletivos do Cefor/Ifes                                         │
│ Cursos, vagas de trabalho e bolsas com seleção pública. Confira requisitos│
│ e prazos e inscreva-se pelo próprio sistema, sem senha.                   │
│ ┌──────────────────────────────────────────────┐  1 aberta · 1 em breve   │
│ │ Procurar cargo, curso ou número do Edital    │  2 com resultado recente │
│ └──────────────────────────────────────────────┘                          │
├───────────────────────────────────────────────────────────────────────────┤
│ Inscrições abertas                                                        │
│ ┌──────────────────────────────────────────────────────────────────────┐  │
│ │ ABERTA · até 01/11/2026 · faltam 19 dias      Edital 01/2026 · Cefor │  │
│ │ Professor Substituto e Técnico-Administrativo                        │  │
│ │ ├ Professor de Informática    Campus Serra    3 vagas + reserva   →  │  │  linha = link para #vaga
│ │ └ Técnico de Laboratório      Campus Vitória  cadastro reserva    →  │  │
│ └──────────────────────────────────────────────────────────────────────┘  │
│ Próximas                                                                  │
│  (lista compacta: título, início das inscrições)                          │
│ Acompanhe                                                                 │
│  Edital 51/2026 — Resultado preliminar em 12/10 · recurso até 17/10   →   │
│  Edital 26/2026 — Sorteio realizado em 12/10                          →   │
│ Anteriores (2)  ▸                                                         │
├───────────────────────────────────────────────────────────────────────────┤
│ Atendimento: selecao@… · Acessibilidade · Privacidade · Ifes              │
└───────────────────────────────────────────────────────────────────────────┘
```

**O cartão-Edital com linhas de oportunidade.** Mantém o Edital como unidade — é ele que tem prazo,
situação e documento —, e mostra cada Perfil como linha com lugar, vagas e um link para a âncora da
vaga. **Um link por linha**, e não o cartão inteiro: são vários destinos legítimos. Acima de cinco
Perfis, "Ver as N vagas" leva à página.

**"Acompanhe"** é o grupo das encerradas que têm fato recente (resultado, recurso, sorteio, Evento
próximo); **"Anteriores"** recolhe o resto num `<details>`. Os dois nomes descrevem a **lista**, não um
estado da seleção: não é "em andamento" (047, D-002), é "tem novidade publicada". A regra de corte
("recente") é decisão do produto.

**Celular:** mesma ordem, em uma coluna; linha de oportunidade empilhada (nome · lugar · vagas); a
busca visível, os filtros recolhidos como em A.

### 3.3 Página da seleção

- **Barra fixa no rodapé, no celular**, enquanto as inscrições estão abertas: "Até 01/11 · 19 dias ·
  [Ver vagas]". Some quando a seção das vagas está na tela (sem script: `position: sticky` no fim do
  cabeçalho; com script: `IntersectionObserver`).
- **"Como participar"**, derivado do dado, depois das vagas: 1. Confirme seu e-mail (sem senha) ·
  2. Informe nome e CPF, uma vez só · 3. Envie N documentos em PDF · 4. Preencha o Requerimento
  (quando pedido) · 5. Revise e envie até 01/11 — e você recebe o comprovante. Cada passo sai de um
  dado que existe; nenhum é texto livre.
- **Resultados** como hoje (062).

### 3.4 Identidade

- Assinatura do Ifes no topo, conforme manual institucional — **não encontrado no repositório; precisa
  vir do produto**;
- fonte carregada de verdade (hoje declarada e não carregada), servida pelo próprio sistema;
- rodapé institucional; favicon; metas de compartilhamento;
- nenhuma imagem decorativa. Se houver imagem, é a da unidade ou do curso, fornecida pela instituição
  e com texto alternativo que informe.

### 3.5 Vantagens, desvantagens, riscos, dependências

| | |
|---|---|
| **Vantagens** | A oportunidade vira a unidade de leitura sem perder o Edital; quem acompanha ganha um lugar; a página parece institucional; a campanha encontra destino coerente (linha → vaga) |
| **Desvantagens** | Revoga ou reinterpreta decisões da 024 (quatro grupos fixos, FR-146; cartão com um link, L8) e da 024/047 (identidade fora de escopo); muito mais teste a reescrever; mais superfície para manter |
| **Riscos** | "Acompanhe" e "Anteriores" exigem regra de corte que é decisão; a barra fixa compete com o teclado virtual e com o zoom; a identidade depende de material que o repositório não tem; o "Como participar" precisa acompanhar cada mudança da jornada, ou mente |
| **Dependências** | Decisão sobre identidade e manual de marca; decisão sobre o corte de "Acompanhe"; seletor em lote (o mesmo de A); revisão das specs 024 e 047 |
| **Complexidade** | **Média a alta** |

## 4. Comparação

| Critério | A — conservadora | B — substantiva |
|---|---|---|
| Resolve a 1ª tela do celular (C-01) | sim | sim |
| Oportunidade antes do Processo (C-02) | sim, pelo título do Edital | sim, por linha de Perfil |
| Lugar no cartão (C-19) | sim | sim, por Perfil |
| Encerrada com fato (C-03) | sim, uma linha | sim, e grupo próprio |
| Ação no celular (C-11) | resumo com âncora | resumo + barra fixa |
| Contexto na identificação (C-12) | sim | sim |
| Identidade institucional (C-15) | rodapé e favicon | completa, se houver manual |
| Decisões anteriores revogadas ou revistas | revê o achado da `024` sobre títulos repetidos (linha 539 da spec), sem tocar conteúdo | revoga FR-146 (grupos) e L8 (um link); reabre o fora de escopo de identidade |
| Domínio novo | nenhum | nenhum (o tipo da seleção ainda ficaria de fora) |
| Testes a reescrever | dezenas de asserções em ~6 arquivos | a maior parte da cobertura da vitrine |
| Mensurável depois | não, sem decisão de mensuração | não, sem decisão de mensuração |
| Complexidade | baixa a média | média a alta |

## 5. Microcopy proposta

| Componente | Hoje | Proposta | Por quê |
|---|---|---|---|
| `<title>` da vitrine | "Seleções abertas" | "Processos seletivos" | A lista inclui encerradas; título e aba dizem o mesmo |
| `h1` da vitrine | "Processos seletivos" | "Processos seletivos do Cefor/Ifes" | Termo que quem procura reconhece e digita; a unidade sai do registro (060), e muda sozinha quando houver outras |
| Linha de fato | — | "1 seleção com inscrições abertas." / "Nenhuma seleção com inscrições abertas agora." | Responde "tem algo?" antes de tudo, sem adjetivo |
| Subtítulo | "Seleções publicadas pelo Cefor/Ifes. Cada uma abre a lista de vagas, os requisitos e o Edital completo." | "Confira vagas, requisitos e prazos e faça sua inscrição pelo próprio sistema, sem senha." | Diz o que a pessoa pode fazer, e tira uma objeção ("preciso de conta?") |
| Campo de busca | rótulo "Procurar", placeholder "cargo, curso ou edital…" | rótulo "Procurar cargo, curso ou Edital"; sem placeholder | O rótulo passa a dizer o alcance; placeholder cortado a 375 px já foi motivo de retirada |
| Recolhido dos filtros | — | "Mais filtros e ordenação" | |
| Convite — aberta | "Ver vagas e inscrever-se" | **manter** | Já é orientado à tarefa e diz o que acontece |
| Convite — em breve | "Ver a seleção" | "Ver vagas e datas" | |
| Convite — encerrada com resultado | "Ver a seleção" | "Ver resultado" | |
| Convite — encerrada sem resultado | "Ver a seleção" | "Ver Edital e cronograma" | |
| Grupo "Outras seleções publicadas" | | **manter** (024, FR-149) | Não é "encerrada", e a diferença é normativa |
| Estado vazio da busca | duas frases | "Nenhuma seleção encontrada para “enfermagem”. Confira a grafia, procure por outro termo ou veja as seleções com inscrições abertas." (link) | Uma frase, e um caminho |
| Catálogo vazio | "Nenhuma seleção publicada no momento. Quando houver, ela aparece aqui — não é preciso se cadastrar para acompanhar." | **manter** | Já é bom |
| Volta, sem consulta | "← Voltar aos resultados" | "← Todas as seleções" | Quem chegou direto não tem resultados |
| Volta, com consulta | "← Voltar aos resultados" | **manter** | |
| Resumo de vagas | — | "O que esta seleção oferece" + uma linha por Perfil com o número de vagas + "Ver vagas e inscrever-se" | "2 vagas nesta seleção" contaria Perfis e diria 2 onde há 3 vagas imediatas — "vaga" no portal nomeia o Perfil e também a quantidade; ver a questão Q6 da [priorização](priorizacao.md#5-questões-para-o-responsável-pelo-produto) |
| Requerimento na inscrição | — | "Além dos documentos, a inscrição pede o preenchimento do Requerimento de Matrícula." | É a mesma frase que o rascunho já diz, antecipada |
| Acesso, com vaga | "Entrar" | "Confirme seu e-mail para se inscrever" + "Professor de Informática · Edital 01/2026" | A pessoa sabe onde está |
| Acesso, sem vaga | "Entrar" | **manter** | |
| Código | "Se este endereço puder ser utilizado, enviaremos um código de acesso." | "Se o endereço estiver certo, o código chega em instantes. Ele vale por 10 minutos." | Mantém a neutralidade da FR-020 sem soar como dúvida; o prazo de 10 minutos já está no e-mail |
| Código, botão | "Entrar" | com vaga: "Confirmar e continuar" | |
| Código, ajuda | — | "Não chegou? Confira a caixa de spam ou de promoções." | O risco que a auditoria de 02/09 nomeou |
| Seus dados | "Pedimos uma única vez. Nas próximas inscrições, não perguntamos de novo." | "Para se inscrever em Professor de Informática, informe seu nome completo e CPF. Eles identificam você nas inscrições e nos resultados, e pedimos uma única vez." | Finalidade e contexto no ponto da coleta — **texto a validar com quem responde por LGPD** |
| Volta à vaga | — | "Você entrou como m@ex.br. Para abrir sua inscrição nesta vaga, toque em Inscrever-se." | Explica o segundo clique |
| Cartão de curso | "Atribuições" / "Remuneração" | depende do tipo da seleção (questão Q4 da [priorização](priorizacao.md#5-questões-para-o-responsável-pelo-produto)) | O exemplo é do seed; a resposta — rótulo, campo ou nada — sai do estudo de Editais reais, e não desta auditoria |

**Linguagem administrativa × orientada à tarefa.** Onde o texto **leva a uma ação**, a orientada à
tarefa vence ("Ver vagas e inscrever-se", "Ver resultado"). Onde ele **nomeia o ato**, a administrativa
fica, porque é o termo do Edital e o que a pessoa vai reencontrar nele ("Edital 01/2026", "Retificação",
"cadastro reserva", "Outras seleções publicadas"). "Processos seletivos" no `h1` é termo administrativo
**e** o que a pessoa digita no buscador — fica.

**Sobre "Encontre sua próxima oportunidade no Ifes".** Acolhedor, mas: (a) promete oportunidade a quem
pode não ter nenhuma aberta; (b) "Ifes" quando o sistema hoje publica só o Cefor anuncia mais do que
há; (c) não é o termo que a pessoa procura. Serve melhor como **linha de campanha** do que como `h1`.

| Alternativa de título | Clareza | Adequação institucional | Precisão | Orienta? |
|---|---|---|---|---|
| "Processos seletivos" (hoje) | alta | alta | alta | pouco |
| "Seleções abertas" (hoje, na aba) | alta | alta | **baixa** — inclui encerradas | sim |
| "Encontre sua próxima oportunidade no Ifes" | média | média | baixa | sim |
| **"Processos seletivos do Cefor/Ifes" + linha de fato** | alta | alta | alta | **sim, pela linha** |

## 6. Comportamento responsivo

| Largura | Vitrine | Seleção |
|---|---|---|
| 320–479 | uma coluna; busca visível, filtros recolhidos; cartão sem metadado longo | resumo de vagas antes do PDF; Cronograma depois das vagas (como hoje) |
| 480–959 | uma coluna larga; filtros ainda recolhidos | idem |
| ≥ 960 | barra de consulta inteira (como hoje); abertas em duas colunas **só quando há duas ou mais**; uma aberta ocupa a linha inteira com Perfis lado a lado | duas colunas (como hoje); resumo de vagas no cabeçalho |
| ≥ 1440 | grade até `--pagina`, e não 76 rem, para não sobrar faixa | idem |

Critérios WCAG 2.2 a manter nas duas alternativas: 1.4.3 (texto, já folgado), **1.4.11** (contorno de
campo — hoje 1,48:1, C-17), 1.4.10 (refluxo a 320 px — hoje sem rolagem lateral), 2.4.7 (foco visível
— já há contorno de 3 px), 2.4.11 (foco não encoberto — atenção à barra fixa da alternativa B), 2.5.8
(alvo mínimo — já atendido), 1.3.1 (o `<details>` dos filtros precisa manter rótulos ligados).

## 7. Recomendação

**Alternativa A, com foco na jornada — as três tarefas, e não só a conversão.** O escopo mínimo é:

1. **hierarquia dos cartões** — o Edital no título, o Processo como metadado, vagas por Perfil, lugar;
2. **filtros recolhidos no celular, com a busca visível e acessível** — rótulo próprio, sem
   placeholder como rótulo, o `<details>` aberto quando há consulta;
3. **contexto durante o acesso** — a vaga nomeada no acesso e no código, a finalidade em "Seus dados";
4. **retorno explicado à vaga** — destaque `:target` e a mensagem que explica o segundo clique, que fica;
5. **informação acionável sobre resultados e recursos** — o fato datado da encerrada na vitrine,
   com "recurso até…" quando o prazo corre, e o convite "Ver resultado";
6. **atalho para as vagas** no alto da página da seleção, e o Requerimento anunciado antes.

**Rodapé, favicon e prévia de compartilhamento entram depois**, conforme contribuição demonstrável:
nenhum deles tem efeito comprovado sobre encontrar, começar ou acompanhar, e o item 5 — um prazo para
exercer um direito — tem prioridade sobre todos eles.

**Por quê A, e não B.** Os achados de severidade Alta (C-01, C-02, C-03, C-11, C-12) são resolvidos por
A, **com o item 5 dentro** — sem ele, C-03 ficaria de fora e a promessa não se sustentaria. O que B
acrescenta — a oportunidade como linha, a faixa de acompanhamento, a identidade — depende de decisões
ainda não tomadas (manual de marca, corte de "recente") e revoga escolhas da 024 feitas com evidência.
Fazer A primeiro e validar por percurso conduzido ([jornada](jornada-publica.md), §7.1) é também a
forma de saber se B é necessária.

**Direção visual.** A página parece administrativa porque o que domina cada tela é **estrutura**
(formulário, código do Processo, cabeçalho de grupo em cinza) e não **conteúdo** (o que se oferece,
onde, até quando, o que mudou). A modernização que importa é de hierarquia e de composição. Imagem,
ilustração ou animação não entram sem função.

**O que esta proposta não demonstra.** Que a conversão aumente, e que a jornada de uma candidata nova
funcione de ponta a ponta — a auditoria não a percorreu inteira. A proposta é sustentada por
evidência de interface; o efeito, só o percurso com pessoas reais vai mostrar.
