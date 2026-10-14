# Diagnóstico — a jornada pública, da vitrine ao início da inscrição

**Data:** 2026-10-12 · **Natureza:** auditoria diagnóstica e propositiva — nada foi implementado.

> **Não vira escopo por estar escrito aqui.** É registro e proposta. Decidir se, quando e em que
> recorte isto vira especificação é do responsável pelo produto.

Documentos irmãos: [jornada pública](jornada-publica.md) · [propostas de redesenho](propostas-redesenho.md)
· [priorização](priorizacao.md) · [índice e síntese](../auditoria-ux-conversao-2026-10-12.md).

---

## 1. Resumo executivo

A hipótese de partida era: *a interface pública foi concebida como catálogo administrativo e atende
quem já sabe o que quer, mas não quem chega sem saber*. **Ela se confirma em parte, e a parte que se
confirma tem lugar certo.**

- **A página da seleção já não é catálogo.** Desde a `024` ela é orientada à decisão: o título é o
  do Edital, a situação vem como marca, o requisito vem antes do botão, os documentos são
  anunciados antes da identificação, o cadastro reserva é lido como oferta, o prazo diz quantos
  dias faltam. No desktop, o primeiro "Inscrever-se nesta vaga" aparece na primeira tela.
- **A vitrine ainda é catálogo — sobretudo no celular.** Em todo celular medido o formulário de
  consulta ocupa de 203 a 537 px (a 320 px, até 592) e o primeiro cartão começa em 602 px. Em telas
  baixas (375 × 667, 320 × 568) nem o título da primeira oportunidade aparece antes da rolagem; em
  telas altas (360 × 800, 375 × 812, 390 × 844) ele aparece, mas o convite do cartão não, em nenhuma.
  E o título de cada cartão é o nome do **Processo** — "Processo Seletivo Simplificado 2026",
  idêntico nos três cartões —, com a oportunidade em corpo menor logo abaixo.
- **No celular, a página da seleção esconde a ação.** O primeiro "Inscrever-se nesta vaga" está a
  1.249 px (≈ 1,9 tela); o único botão da primeira dobra é "Ler o Edital completo (PDF)". O registro
  da `009` (L4) já dizia isso a 795 px e chamou a solução de "decisão de produto".
- **O início da inscrição perde o contexto.** Quem toca "Inscrever-se nesta vaga" cai numa tela
  "Entrar" que não diz para qual vaga; depois do código e dos dados volta à vaga sem destaque nem
  mensagem, e precisa tocar o mesmo botão de novo. São seis acionamentos e cinco telas entre o
  cartão e o rascunho, para uma pessoa nova.
- **O cartão de uma seleção encerrada não diz o que está acontecendo nela.** O Edital 51/2026 do
  seed tem resultado preliminar publicado e prazo de recurso aberto até 17/10; o cartão diz só
  "Inscrições encerradas em 02/09/2026". O dado existe e a página da seleção o mostra.

O que **não** está em causa: a correção normativa, a acessibilidade de base (texto com contraste
folgado, estado por cor **e** palavra, consulta sem JavaScript, nenhuma rolagem lateral de 320 a
1.440 px) e a honestidade da comunicação de prazo.

**A vitrine serve a três tarefas, e não a uma:** encontrar uma oportunidade, começar a inscrição e
**acompanhar o certame** de que já se participa — resultado, prazo de recurso, sorteio, convocação.
Otimizar só a conversão deixaria a terceira em segundo plano, e é nela que está o único prazo para
exercer um direito que a vitrine hoje cala (C-03).

A recomendação (ver [propostas](propostas-redesenho.md)) é a **evolução conservadora com foco na
jornada**: hierarquia dos cartões, filtros recolhidos no celular com a busca acessível, contexto
durante o acesso, retorno explicado à vaga e informação acionável sobre resultados e recursos — sem
domínio novo. Rodapé, favicon e prévia de compartilhamento ficam para depois, conforme contribuição
demonstrável.

> **Revisão de 12/10/2026.** Esta versão incorpora uma revisão do texto contra o código e as specs:
> medições reproduzíveis com altura de tela, script e resultado versionados (§3); C-01 corrigido para
> separar telas baixas e altas; o objetivo ampliado para as três tarefas; o escopo mínimo passando a
> incluir C-03; a revisão do achado da `024` sobre títulos repetidos (C-02); a conclusão sobre o tipo
> da seleção rebaixada a questão a estudar (C-09); e a mensuração separada da validação (§6.7).

## 2. Escopo

**Dentro:** a vitrine (`/selecoes/`), a página da seleção (`/selecoes/<edital>/`), a transição até o
primeiro rascunho (`inscrever` → `acesso` → `acesso/codigo` → `meus-dados` → volta à vaga →
`inscricoes/<id>/`), os textos públicos dessas telas, a identidade visual da base do portal, a
compatibilidade com campanhas e o que hoje é mensurável.

**Fora:** o formulário interno da inscrição (dados, documentos, requerimento, revisão, comprovante),
a área do candidato depois do envio, as telas de resultado e de sorteio, a gestão. O que apareceu
dessas telas no percurso está registrado em §7 como **observação lateral**, separado do escopo.

## 3. Metodologia

| Item | Valor |
|---|---|
| Commit auditado | `b4a1abf4` (`main`, merge do PR 275) |
| Branch | `claude/auditoria-processo-seletivo-ux-ef5de7` |
| Execução | `runserver` nativo na porta 8077, `INTERFACE_SELETOR_IDENTIDADE` e `PORTAL_IDENTIDADE_DEMO` ligados, e-mail no console |
| Banco | `ps_ux_conversao`, exclusivo: `make preparar` + `seed_demo` (mantido para a medição de depois) |
| Navegador | painel do aplicativo (Chromium 152), viewport emulado; capturas em 375 × 667, 1280 × 900 e 1440 × 900 |
| Medição | HTML servido, sem sessão, renderizado em `iframe srcdoc` de largura **e altura** fixas — 320 × 568, 360 × 800, 375 × 667, 375 × 812, 390 × 844, 768 × 1024, 1280 × 800 e 1440 × 900 —, posições por `getBoundingClientRect`; script e resultado versionados ([`medir-primeira-tela.js`](medir-primeira-tela.js), [`medicoes.json`](medicoes.json)) |
| Percurso | vitrine → seleção → "Inscrever-se" → e-mail → código → "Seus dados" (identidade nova, parado ali sem digitar CPF) e, com a candidata do fixture (`MARIA`), → volta à vaga → segundo "Inscrever-se" → rascunho |
| Leitura de código | `portal/views.py`, `portal/leitura.py`, `portal/templates/portal/*`, `shared/_tokens.css.html`, `publicacoes/application/selectors.py`, `processos/models.py`, `shared/observability.py`, `seed_demo` |
| Documentos | Constituição v1.2.0; specs `009`, `010`, `024`, `047`, `055`, `060`, `062`, `069`; auditorias de UX de 02/09, 13/09, 16/09 e 30/09; `docs/visao-sistema/` |
| Contraste | razões WCAG calculadas a partir dos tokens de `_tokens.css.html` |

**Como reproduzir as medidas.** "Primeira tela" é sempre o par largura × altura, nunca a largura
sozinha. As posições das tabelas da §6 saem de
[`medir-primeira-tela.js`](medir-primeira-tela.js), e o resultado bruto está em
[`medicoes.json`](medicoes.json), com o navegador (Chromium 152, o painel do aplicativo), o commit e o
Edital medido. Para refazer:

1. `createdb -h localhost ps_ux_conversao`, `make preparar DB_NAME=ps_ux_conversao …` (com os papéis na
   linha de comando, numa worktree sem `.env`) e `manage.py seed_demo`;
2. `runserver` com `INTERFACE_SELETOR_IDENTIDADE=true` e `PORTAL_IDENTIDADE_DEMO=true`;
3. abrir qualquer página do portal, colar o script no console e chamar
   `await medirTudo("<id do Edital 01>")`.

O script busca as páginas **sem** a sessão do navegador e as renderiza em `iframe` de largura e altura
fixas; a folha é inline no `base.html`, e as media queries valem para a largura do `iframe`. O conteúdo
medido é o do seed: os números mudam com o tamanho do título do Edital, com a existência de
Retificação e de "Próximo, em…" — servem para comparar antes e depois no mesmo banco, não como
constante do produto.

**Comprovado × hipótese.** Neste conjunto, **comprovado** é o que foi visto na tela, medido ou lido no
código, com a referência ao lado. **Hipótese** é o que depende de comportamento de pessoas reais —
efeito sobre abandono, clique ou inscrição —, e vem marcado como *impacto esperado, a validar*.
Nenhum número de conversão aparece aqui, porque nenhum foi medido (ver §6.6).

## 4. Estado atual

### 4.1 Rotas públicas

| Rota | View | O que é |
|---|---|---|
| `/` | `IndexView` (`shared/api/operacional.py`) | Navegador vai para a vitrine (302); cliente de API recebe o documento de serviço |
| `/selecoes/` | `portal.views.vitrine` | A vitrine: busca, filtros, quatro grupos por situação |
| `/selecoes/<edital_id>/` | `portal.views.selecao` | A página da seleção; abre também encerrada e cancelada (FR-017) |
| `/selecoes/<edital_id>/vagas/<perfil_id>/inscrever` | `portal.views.inscrever` | **POST** — abre ou retoma o rascunho; sem sessão, manda ao acesso com `?destino=` |
| `/selecoes/acesso`, `/acesso/codigo` | `acesso`, `acesso_codigo` | Acesso sem senha, código de seis dígitos por e-mail (010) |
| `/selecoes/meus-dados` | `meus_dados` | Nome e CPF, uma vez na vida da identidade |
| `/selecoes/resultados/<id>/`, `/sorteio/…` | várias | Divulgações públicas com endereço estável |
| `/api/v1/public/…` | API | Versão vigente, histórico, publicação, documento |

### 4.2 O que a vitrine mostra, e de onde vem

Tudo sai da **versão consolidada vigente** de cada Edital (`selecoes_publicas`, FR-011), sem tabela
de elaboração. Cancelado fica fora da vitrine e continua alcançável pelo endereço. Busca, filtros e
ordenação operam em memória sobre o que já foi carregado (024, D-003) — adequado a dezenas de
seleções; a própria decisão nomeia "algumas centenas" como o sinal de rever.

O cartão (`_cartao_da_selecao.html`) mostra, nesta ordem: marca de situação · título do **Processo**
(o link) · título do **Edital** · código do Processo, número do Edital e unidade · nomes dos Perfis e
soma das vagas imediatas · frase do período com "Faltam N dias" · convite aparente ("Ver vagas e
inscrever-se" ou "Ver a seleção").

### 4.3 Estados que existem no domínio

| Estado | Fonte | Na vitrine | Na seleção |
|---|---|---|---|
| Inscrições abertas | `periodo_de_inscricoes` → `ABERTO` | grupo "Inscrições abertas", marca "Aberta" | marca, frase, "Faltam N dias", botões por vaga |
| Inscrições futuras | `FUTURO` | "Próximas seleções", marca "Em breve" | frase "Inscrições começam em…" |
| Inscrições encerradas | `ENCERRADO` | "Inscrições encerradas", marca "Encerrada" | frase; resultados em destaque se houver |
| Sem período designado | `NAO_DESIGNADO` | "Outras seleções publicadas", marca "Consulta" | nenhuma frase de prazo (FR-149) |
| Período cancelado | `periodo.cancelado` | grupo das encerradas, marca "Período cancelado" | "Período de inscrições cancelado" |
| Edital encerrado / cancelado (ato) | `desfechos()` (047) | encerrado: grupo das encerradas, marca "Edital encerrado"; cancelado: **fora** da vitrine | marca e frase com a data do ato |
| Processo encerrado / cancelado | idem | marca do período; fato dito abaixo | fato dito, recebimento segue o período |
| Resultado publicado, prazo de recurso | `historico_publico_do_edital`, `janela_da_publicacao_divulgada` | **não aparece** | "Resultados divulgados", por Perfil → etapa → lista, com "recurso até" |
| Sorteio (relação congelada, realizado) | `sorteios_do_edital` | **não aparece** | bloco "Sorteio público" |
| Evento em curso / próximo | `agora_e_proximo`, `cronograma` | **não aparece** | "Acontecendo agora", "Próximo, em…" |
| Convocação | área do candidato (019) | não é pública | não é pública |

Não há estado "em andamento", "em análise" ou "concluído" agregado, e isso é **decisão**, não falta:
a `047` (D-002) recusa status agregado que nenhum fato registra. Qualquer proposta de "seleção em
andamento" precisa ser dita como **fato datado** ("resultado preliminar publicado em 12/10"), nunca
como fase inventada.

### 4.4 Processo, Edital, Perfil e vaga

Um **Processo** reúne um ou mais **Editais**; cada Edital publicado tem um ou mais **Perfis**
(o que o portal chama de "vaga": cargo, função ou curso), cada um com vagas imediatas, tipo de
cadastro reserva, localidade, requisitos, modalidades de concorrência e, quando declarados,
atribuições, carga horária e remuneração. **Não existe no domínio** o tipo da seleção (curso, cargo,
bolsa, estágio), taxa, isenção, modalidade presencial/EaD nem duração — a `024` registrou os quatro
últimos como "campos que o domínio não tem". O seed mistura os dois tipos: dois Perfis de trabalho
(Professor, Técnico) e um curso (Técnico em Informática EaD).

## 5. Pontos positivos — o que precisa ser preservado

1. **Consulta no endereço, sem JavaScript** (024, D-002, UX-017): compartilhável, o botão voltar
   funciona, e o link de cada cartão leva a consulta para a seleção e de volta.
2. **Cartão inteiro clicável com um link só** (L8): um alvo para o teclado e o leitor de tela.
3. **Situação por cor e palavra** (UX-019), sempre no mesmo lugar do cartão (UX-016).
4. **Prazo honesto**: data, hora e "Faltam N dias" arredondado **para baixo** (`_dias_ate`), destaque
   âmbar só a menos de três dias. É urgência real, não fabricada.
5. **Cadastro reserva lido como oferta** (D-007): "Cadastro reserva — sem limite declarado, para
   convocação futura", com o zero em posição secundária.
6. **Documentos anunciados antes da identificação**, com contagem ("3 documentos que serão pedidos")
   e a divisão por modalidade.
7. **Teto por candidato antes da escolha** ("Cada candidato pode enviar apenas 1 (uma) inscrição").
8. **Transparência normativa na página**: aviso de Retificação colado ao botão do Edital, lista de
   documentos datada com "O que mudou", Cronograma público, "Próximo, em…".
9. **Ausência nunca vira afirmação** (D-009): nada de "não informado".
10. **Acesso sem senha** com código colável num campo só, espera de reenvio dita em texto.
11. **Nenhuma rolagem lateral** de 320 a 1.440 px (medido: `scrollWidth − clientWidth = 0` nas seis
    larguras, nas duas páginas).
12. **Contraste de texto folgado**: texto fraco 7,0:1 sobre o fundo; marca "Aberta" 7,4:1; "Em breve"
    5,8:1; botão 5,0:1; link 6,5:1; topo 8,4:1.
13. **Nada é coletado sobre a navegação** (024, D-008, SC-047) — o que é um ponto positivo de proteção
    de dados e, ao mesmo tempo, o limite da §6.6.

## 6. Problemas identificados

A numeração `C-NN` é a mesma da [priorização](priorizacao.md). Em cada item: **evidência**, **classe**
(A — já implementado; B — existe no dado, não é apresentado; C — pequena mudança de apresentação;
D — exige funcionalidade ou domínio novo) e, quando houver, o registro anterior.

### 6.1 Vitrine — primeira impressão e hierarquia

**C-01 · No celular, o formulário vem antes da oportunidade, e o convite nunca está na primeira
tela.** *Comprovado.*

| Largura × altura | Formulário (topo → fundo) | Primeiro cartão | Título do Edital visível? | Fundo do 1º convite | Convite visível? |
|---|---|---|---|---|---|
| 320 × 568 | 203 → 592 px | 657 px | não | 1.159 px | não |
| 375 × 667 | 203 → 537 px | 602 px | não | 1.033 px | não |
| 360 × 800 | 203 → 537 px | 602 px | sim | 1.057 px | não |
| 375 × 812 | 203 → 537 px | 602 px | sim | 1.033 px | não |
| 390 × 844 | 203 → 537 px | 602 px | sim | 1.033 px | não |
| 768 × 1024 | 189 → 367 px | 433 px | sim | 771 px | sim |
| 1280 × 800 | 189 → 289 px | 355 px | sim | 717 px | sim |
| 1440 × 900 | 189 → 289 px | 355 px | sim | 717 px | sim |

O formulário ocupa 334 px — **metade de uma tela de 667 px e 40 % de uma de 844** — antes de qualquer
cartão ([captura a 375 × 667](capturas/vitrine-375-primeira-dobra.jpg)). Em telas baixas, a primeira
tela não mostra oportunidade nenhuma; em telas altas, mostra a marca, o título do Processo e o do
Edital da primeira seleção, mas não os Perfis, o prazo nem o convite. Um cartão aberto mede 448 px a 375 px — dois
terços da tela —, de modo que um catálogo de 20 seleções passaria de 8.000 px de rolagem (estimativa
por altura medida, não renderizada). Classe **C**.

**C-02 · O título do cartão é o do Processo, e a oportunidade vem em corpo menor.** *Comprovado.*
Os três cartões do seed têm o mesmo título em verde e negrito — "Processo Seletivo Simplificado 2026"
—, e o que distingue um do outro ("Edital 01/2026 — Professor Substituto e Técnico-Administrativo")
vem abaixo, em 15 px. A página da seleção já fez a inversão contrária (009 FR-014, RC-47, PR #215):
o `h1` é o título do Edital, e o Processo é dito como "a quem o Edital pertence". **A vitrine e a
seleção usam hierarquias opostas para a mesma informação.** O número do Edital ainda aparece duas
vezes no mesmo cartão (no título, quando o elaborador o escreve ali, e na linha de metadados) — a
polish de 30/09 (D3) atribuiu ao seed, mas o título é texto livre e Editais reais costumam
começar por "Edital nº…". Classe **C**.

**Este achado revisa um diagnóstico registrado.** A `024`, em "Achados registrados, e que não são
escopo desta feature" (`spec.md`, linha 539), viu os títulos repetidos e concluiu: *"É conteúdo de
quem elabora, não defeito de tela: a feature garante que número do Edital e unidade continuem
distinguindo os dois, e não renomeia nada."* O conteúdo continua sendo de quem elabora, e nada aqui
propõe renomeá-lo. O que se revisa é a segunda metade: o número e a unidade distinguem, mas em corpo
de metadado, abaixo de um título idêntico — e a própria seleção já resolveu o mesmo problema
destacando o título do Edital, sem tocar conteúdo normativo. A spec que tratar disto precisa dizer
que revisa aquele diagnóstico, e por quê.

**C-05 · Título, subtítulo e `<title>` dizem três coisas diferentes.** *Comprovado.* A aba diz
"Seleções abertas — Cefor/Ifes" (`vitrine.html`, linha 2), o `h1` diz "Processos seletivos", e a lista
inclui encerradas. O subtítulo descreve a mecânica da página ("Cada uma abre a lista de vagas, os
requisitos e o Edital completo") em vez do propósito, e não diz quantas estão abertas. Classe **C**
(texto).

**C-07 · Grupos sem hierarquia entre si, e o desktop com meia linha vazia.** *Comprovado.* O
cabeçalho de grupo ("INSCRIÇÕES ABERTAS") é 16 px, cinza, caixa alta — **mais fraco que o título de
cada cartão**. Encerradas usam o mesmo cartão, do mesmo tamanho, com a mesma linha de vagas, das
abertas: só a marca e o estilo do convite mudam. A 1280 e 1440 px, a única seleção aberta ocupa
metade da linha e deixa a outra metade vazia; a grade para em 76 rem (1.216 px) e a 1440 px sobra uma
faixa à direita ([captura](capturas/vitrine-1440-encerradas.jpg)). Classe **C**.

**C-19 · Metadados administrativos no lugar do "onde".** *Comprovado.* O cartão diz
"PS-DEMO-2026 · Edital 01/2026 · Unidade: CEFOR" — código interno, número e a sigla em caixa alta
(`institution_scope.upper()`). **Onde** a vaga é — "Campus Serra", "Polo Serra", que decide muito para
quem procura — só aparece na página da seleção. A localidade de cada Perfil está no conteúdo
publicado, e o registro de Unidades (060) tem `sigla` ("Cefor"), `nome` e `local`. Classe **B**.

**C-08 · A linha de vagas não tem teto e soma o que não se soma.** *Comprovado no código.* Os nomes
dos Perfis vão por `join:" · "` sem limite: um Edital de 30 polos produz 30 nomes num cartão. E o total
("3 vagas imediatas, com cadastro reserva") soma Perfis diferentes — no seed, 3 do Professor e 0 do
Técnico. Não é falso, mas lido rápido sugere 3 vagas para cada um. Classe **C**.

### 6.2 Vitrine — filtros, descoberta e estados vazios

**C-04 · Filtros com protagonismo desproporcional ao catálogo.** *Comprovado.* Com três seleções e uma
aberta, a página oferece busca, situação, cargo ou curso, ordenação e um botão — cinco controles
antes do primeiro cartão. "Situação" repete o que os grupos já dizem. O formulário é bem feito
(024; modelo da gestão desde a 055), e o problema é **onde** e **quando** ele aparece, não **como**.
O filtro de unidade já some com uma unidade só — o mesmo princípio vale para os demais. Classe **C**.

**C-18 · O estado vazio diz a mesma coisa duas vezes e não sugere caminho.** *Comprovado.*
`?busca=enfermagem` mostra "Nenhuma seleção encontrada para “enfermagem”." e, logo abaixo, "Nenhuma
seleção publicada corresponde a esses filtros hoje. Ver todas as seleções." Nenhuma sugestão de olhar
as abertas, nenhuma indicação do que existe. Um aviso de novas seleções seria a resposta natural, e
está fora de escopo desde a 024 (classe D). Classe **C** para o texto.

**C-09 · Rótulos de vaga de trabalho num Perfil de curso — no exemplo do seed.** *Comprovado no
exemplo; não generalizado.* No Perfil "Técnico em Informática (EaD)" a página diz "ATRIBUIÇÕES — Curso
técnico subsequente" e "REMUNERAÇÃO — Gratuito". Os campos são genéricos (`duties`, `workload`,
`compensation`) e os rótulos, de trabalho. **Mas o conteúdo vem do seed** (`seed_demo.py`, linhas
513–515), escrito para a demonstração: mostra que rótulo e campo podem não casar, e não prova como
Editais reais de curso preenchem esses campos nem qual modelagem resolveria. Antes de falar em
rótulo condicional ou em tipo da seleção como dado (que o domínio não tem; a `009` já adiou o
agrupamento por público), é preciso olhar Editais reais de curso, de cargo e de bolsa e as
diferenças de **comportamento** que cada um exige — não só de rótulo. Fica como questão (Q4 da
[priorização](priorizacao.md#5-questões-para-o-responsável-pelo-produto)), sem classe atribuída.

### 6.3 Estados e sobreposições

**C-03 · A encerrada não diz o que está acontecendo nela.** *Comprovado.* Três fatos públicos que a
página da seleção mostra e o cartão não:

| Seleção | O cartão diz | A página diz |
|---|---|---|
| Edital 51/2026 | "Encerrada · Inscrições encerradas em 02/09/2026." | "Resultado preliminar · publicado em 12/10/2026 · recurso até 17/10/2026 às 23h59" |
| Edital 26/2026 | "Encerrada · Inscrições encerradas em 02/10/2026." | "Sorteio realizado em 12/10/2026 às 20:47. 7 candidatos habilitados." e "Próximo, em 17/10/2026" |

Para quem acompanha — e para quem chega de uma divulgação de resultado —, "Encerrada" é a palavra
que menos informa: soa como fim, quando há prazo correndo. **E o prazo que corre é o de exercer um
direito**: quem não sabe que o recurso está aberto até 17/10 perde a chance de recorrer. Por isso este
achado entra no escopo mínimo com prioridade acima de qualquer item de assinatura visual. A sobreposição de estados que o enunciado
pede para tratar (inscrições encerradas **e** resultado publicado) existe hoje e é resolvida só na
página da seleção. Classe **B**, com uma ressalva de custo: a leitura dos resultados é por Edital, e a
vitrine precisaria fazê-la em lote — o repositório já registrou que leitura por listagem reprova o
orçamento de consulta. É mudança de seletor, não de domínio.

**Sobre "concluída".** O seed chama o Edital 51 de "seleção concluída" no título, mas o domínio não
tem esse estado: há resultado preliminar com recurso aberto. A interface faz bem em não dizê-lo.

### 6.4 Página da seleção

**C-11 · No celular, a ação está a quase duas telas.** *Comprovado.*

| Largura | Fim do cabeçalho | "Vagas" | 1º "Inscrever-se" | Na 1ª tela? |
|---|---|---|---|---|
| 320 × 568 | 758 px | 809 px | 1.350 px | não |
| 360 × 800 | 682 px | 734 px | 1.275 px | não |
| 375 × 667 | 682 px | 734 px | 1.249 px | não |
| 375 × 812 | 682 px | 734 px | 1.249 px | não |
| 390 × 844 | 657 px | 709 px | 1.223 px | não |
| 768 × 1024 | 518 px | 569 px | 783 px | sim |
| 1280 × 800 | 460 px | 512 px | 726 px | sim, rente |

A primeira tela do celular é só cabeçalho: marca, título em três linhas, Processo, período, "Próximo",
descrição, botão do PDF e aviso de Retificação ([captura](capturas/selecao-375-primeira-dobra.jpg)).
Nada diz quantas vagas há nem leva até elas. A `009` (L4) mediu 795 px e deixou a solução como
decisão de produto por causa dos Editais de vários Perfis; o cabeçalho cresceu desde então
(`agora_e_proximo`, aviso de Retificação, teto). A comparação de números não é estrita — o conteúdo
do seed também mudou. Classe **C**: um resumo com âncora não exige escolher Perfil.

**C-10 · "← Voltar aos resultados" para quem não buscou nada.** *Comprovado.* A volta é sempre
renderizada com esse texto (`selecao.html`, linha 10). Quem chega de uma campanha, de um e-mail do
sistema (066) ou de um compartilhamento nunca viu resultado nenhum. Classe **C** (texto condicional).

**C-14 · O Requerimento de Matrícula exigido na inscrição não é anunciado antes.** *Comprovado.* No
Edital 01, a página pública anuncia "3 documentos que serão pedidos" e nada mais. Já dentro do
rascunho: "Este Processo Seletivo pede o Requerimento de Matrícula no ato da inscrição. Você não
consegue enviar a inscrição sem ele." O momento está em `Edital.requerimento_momento`
(`AT_ENROLLMENT`). É o mesmo defeito que a L7 da `009` corrigiu para os documentos — descobrir o que
será pedido só depois de identificar-se. Classe **B**. (Que o seed peça Requerimento de *Matrícula* a
um professor substituto é configuração da demonstração, não defeito de tela.)

### 6.5 Início da inscrição

**C-12 · O caminho perde o contexto, e o segundo clique não é explicado.** *Comprovado no percurso.*

| # | Tela | O que diz da vaga escolhida |
|---|---|---|
| 1 | Seleção → "Inscrever-se nesta vaga" (POST) | — |
| 2 | **Entrar** — "Sem senha: enviamos um código para o seu e-mail." | nada ([captura](capturas/acesso-sem-contexto-1280.jpg)) |
| 3 | **Informe o código** — botão "Entrar" | nada |
| 4 | **Seus dados** — nome e CPF (só identidade nova) | nada |
| 5 | Seleção `#vaga-…`, rolada até a vaga | nenhum destaque, nenhuma mensagem |
| 6 | "Inscrever-se nesta vaga" de novo → **Sua inscrição**, "Etapa 1 de 3" | vaga nomeada |

O segundo clique é deliberado e deve ficar: abrir rascunho é ato auditado, e executar o destino
sozinho faria um endereço compartilhado criar inscrição em nome de quem só se identificou
(`_de_volta_a_vaga`). O defeito é a tela não dizer isso: não há `:target` na folha nem mensagem na
volta, e o aviso "Seus dados foram guardados." gravado em `meus_dados` só é exibido na tela seguinte,
já fora de contexto. O botão "Entrar" na tela do código, para quem queria inscrever-se, também não
ajuda. Classe **C**.

**C-13 · "Seus dados" pede CPF sem dizer para quê.** *Comprovado.* A tela diz "Pedimos uma única vez.
Nas próximas inscrições, não perguntamos de novo." — bom —, mas nem a finalidade nem a vaga a caminho
da qual a pessoa está. Informar finalidade no ponto da coleta é **boa prática** alinhada ao Princípio
III (necessidade, finalidade); se há exigência legal específica de texto aqui, ela **não foi
verificada** nesta auditoria. Classe **C**.

### 6.6 Identidade visual, confiança e campanhas

**C-15 · A base pública não tem assinatura institucional.** *Comprovado.*
- Sem rodapé: nem contato, nem atendimento (o `PORTAL_ATENDIMENTO` existe e só aparece em duas telas
  de bloqueio), nem acessibilidade, nem privacidade;
- sem favicon — `/favicon.ico` responde 404 em toda página;
- sem logotipo ou assinatura do Ifes; a marca é o texto "Cefor/Ifes · Seleções" no topo verde;
- a fonte declarada (`"Open Sans","Segoe UI",system-ui`) **não é carregada** — não há `@font-face`
  nem folha externa —, e a página sai em Segoe UI, San Francisco ou Roboto conforme o aparelho.

A 024 e a 047 puseram "redesenho da identidade visual" **fora de escopo**, e a 060 registrou a marca
na vitrine como pendência. Classe **C** para rodapé e favicon; **decisão do produto** para identidade.
Nenhum destes itens tem contribuição demonstrada para as três tarefas da jornada; o rodapé com o
atendimento é o que mais se aproxima (é o caminho de quem travou). Entram depois do escopo mínimo.

**C-16 · O link compartilhado não tem prévia.** *Comprovado.* Nenhuma `meta name="description"`, nenhuma
tag Open Graph: colado no WhatsApp ou numa rede, o link da seleção sai com o `<title>` cru e sem
descrição. O endereço é estável e público — o que é bom para campanha —, mas é um UUID. Classe **C**
para as metas; endereço legível é decisão (a análise de linguagem simples de 12/10 já registrou).

**C-17 · Contorno de campo abaixo de 3:1.** *Provável não conformidade, a confirmar.* `--borda`
(`#d4d4d4`) dá 1,48:1 sobre branco. Os campos da consulta são brancos sobre o cartão branco, e o
contorno é o que os identifica — o que cai no critério 1.4.11 (contraste não textual) da WCAG 2.1/2.2.
O token é compartilhado com a gestão. Classe **C**, com alcance maior que o portal.

**Alvos de toque (2.5.8).** Abaixo de 24 px de altura só ficaram links em linha de texto e o "Entrar"
do topo (39 × 22 px), que passa pela exceção de espaçamento. Os títulos dos cartões medem 23 px, mas o
alvo real é o cartão inteiro. Sem achado.

### 6.7 Mensuração

| | O que existe | Onde |
|---|---|---|
| Medível hoje, sem dado novo | rascunhos criados e inscrições enviadas, por Edital e Perfil, com horário; anexos e gravações intermediárias | `Inscricao.created_at`, `submitted_at`, `status`; atos `CRIAR`, `GRAVAR`, `ANEXAR`, `SUBMETER` na trilha |
| Medível hoje, sem vínculo com Edital | códigos pedidos e códigos consumidos | `DesafioDeAcesso.criado_em`, `consumido_em` |
| Só em log de servidor, sem estrutura | visualizações da vitrine e da seleção, POST de "Inscrever-se" anônimo | log de acesso do servidor web |
| Não existe | origem da visita, clique em cartão, rolagem, tempo | proibido pela 024 (D-008, SC-047) |

**Contar rascunhos e envios não mede conversão.** Os dois números dizem quantas inscrições
começaram e quantas terminaram — a conclusão do que foi iniciado. Conversão precisa de um denominador
que o sistema não registra (quantas pessoas viram a oportunidade), e esse denominador é justamente o
que a `024` decidiu não coletar. **A falta dele não bloqueia a melhoria**: compreensão e conclusão de
tarefa se validam por percurso conduzido com pessoas reais, sem registrar navegação (ver
[jornada](jornada-publica.md), §7.1). A instrumentação, se vier, é decisão própria — a `024` (D-008)
a vedou naquele incremento e não a proibiu para sempre.

Não há script de analytics, cookie de rastreamento nem tratamento de `utm_*`. Os parâmetros de
campanha não quebram nada — a vitrine ignora o que não reconhece, e a volta (`caminho_de_volta`) só
deixa passar os cinco da consulta —, mas também não sobrevivem ao acesso.

## 7. Observações laterais (fora do escopo principal)

- **Formulário da inscrição:** "Faltam 2 de 2 documentos obrigatórios" convive com "3 documentos que
  serão pedidos" da página pública — a diferença é a modalidade ainda não escolhida, e a página pública
  já a explica ("Se concorrer em…"); não é contradição, mas vale conferir no próximo percurso.
- **Vagas por modalidade** (quantas para ampla, quantas para cada cota) continuam sem número na página
  pública — registrado em 13/09 e ainda aberto.
- **E-mail com o código** é ponto único de falha (E2E-020, 02/09): quem não recebe, desiste. Nenhuma
  tela diz "confira o spam".
- **Página de código:** "Se este endereço puder ser utilizado, enviaremos um código de acesso." seguido
  de "Enviado para m@ex.br" lê-se como contradição. A primeira frase é exigência de não revelar quem
  existe (FR-020), e a segunda confirma o envio; a redação pode servir às duas coisas sem soar insegura.

## 8. Avaliação heurística (Nielsen), na escala 0 a 4 — quanto maior, pior

| Heurística | Vitrine | Seleção | Início da inscrição | Nota |
|---|---|---|---|---|
| Visibilidade do estado | 2 | 0 | 1 | Encerrada sem resultado nem recurso (C-03) |
| Correspondência com o mundo real | 2 | 1 | 1 | Processo antes da oportunidade; "Atribuições" de curso |
| Controle e liberdade | 0 | 1 | 1 | "Voltar aos resultados" sem resultados |
| Consistência e padrões | 2 | 1 | 1 | Hierarquia oposta entre vitrine e seleção; `<title>` × `h1` |
| Prevenção de erro | 0 | 1 | 1 | Requerimento descoberto depois (C-14) |
| Reconhecer em vez de lembrar | 1 | 1 | 2 | Acesso não nomeia a vaga (C-12) |
| Flexibilidade e eficiência | 1 | 2 | 1 | Ação a 1,9 tela no celular (C-11) |
| Estética e minimalismo | 2 | 1 | 0 | Formulário antes do conteúdo; metadados internos |
| Recuperação de erros | 1 | 0 | 1 | Estado vazio sem caminho |
| Ajuda e documentação | 1 | 0 | 1 | Sem rodapé nem atendimento |

## 9. Limitações

- **O seed não cobre todos os estados.** Há três Editais publicados, todos de uma unidade: um aberto e
  dois encerrados. "Em breve", "Consulta" (sem período), período cancelado e desfecho de Edital
  **não foram vistos na tela** — foram avaliados pelo código e pelos testes. O filtro de unidade não
  aparece. Volumes de dezenas de seleções foram **estimados** pela altura medida dos cartões.
- **Ninguém de fora usou a interface.** Todo efeito sobre abandono ou inscrição é hipótese. A
  auditoria sustenta uma proposta de melhoria; **não** demonstra aumento de conversão.
- **A jornada de uma candidata nova não foi validada de ponta a ponta.** A identidade nova parou em
  "Seus dados"; dali em diante o percurso usou a candidata do fixture, que já tinha núcleo — o
  rascunho foi aberto, mas nada foi preenchido nem enviado.
- **Os números de posição dependem do conteúdo.** São do seed, num commit e num navegador
  registrados em [`medicoes.json`](medicoes.json); servem para comparar antes e depois no mesmo banco.
- **Testes citados como dependência localizam compromissos, não os tornam intocáveis.** Cada asserção
  de texto aponta a decisão que a originou; a spec nova relê a decisão e diz se a mantém.
- **Viewport emulado**, no painel do aplicativo; nenhum aparelho real, nenhuma rede lenta.
- **Leitor de tela e teclado** não foram percorridos; a avaliação de acessibilidade vem do código, dos
  testes de acessibilidade do portal e do cálculo de contraste.
- **CPF não foi digitado.** A tela "Seus dados" foi observada com uma identidade nova; o resto do
  percurso usou a candidata do fixture, cujo núcleo já está cadastrado.
- **Nenhuma exigência jurídica foi verificada** além das que a Constituição e as specs já registram.
  Onde o texto fala em LGPD, trata-se de boa prática alinhada ao Princípio III, não de parecer.
- **Nenhuma diretriz formal de identidade visual do Ifes** foi encontrada no repositório; o que se diz
  sobre identidade é avaliação de composição, não conformidade a manual.
