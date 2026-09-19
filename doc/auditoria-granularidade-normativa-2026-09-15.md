# Auditoria exploratória — granularidade normativa, fonte autoritativa e fidelidade do Edital

**Data:** 2026-09-15
**Evidência principal:** os dois PDFs em `~/Downloads` — `EDITAL 140.2025 – SELEÇÃO DE CADASTRO DE
RESERVA DE TUTOR PRESENCIAL .docx.pdf` (27 páginas, o documento real) e
`previa-edital-149-2026.pdf` (22 páginas, gerada pelo sistema às 08h54 de 15/09, com 9 dos 16
códigos). O repositório foi consultado **depois** de cada sintoma, só para achar a causa.
**Código de referência:** `c53e3b4`. Onde um achado já foi corrigido depois da prévia, isso está
dito no próprio achado.

> **Registro, não escopo.** Este documento mede e enumera. Qual achado vira trabalho — e se algum
> vira — é decisão do usuário (Constituição, Princípio VI).

---

## Sumário executivo

**14 achados fortes**, **3 hipóteses** e **7 diferenças sem achado**, com **três experimentos
executados**.

**E-1** elevou o AX-7 de hipótese a fato medido: o sistema publicou **3% e 30% para a mesma lei
federal**, em tabelas vizinhas do mesmo Edital, sem emitir uma única conferência.

**E-2 encontrou o pior achado da rodada — o AX-14.** Declarar os documentos condicionados como o
Edital os declara, uma vez por modalidade, é **aceito pela publicação** e alcança **um único
Perfil**. O PDF afirma *"Dos candidatos concorrentes na modalidade Pessoa com Deficiência"*, sem
qualificar Perfil, enquanto a execução entrega a exigência a 1 de 3 — e a 1 de 16, no Edital real.
É o único achado em que **o documento publicado e o comportamento do sistema se contradizem**, e o
único cuja fração de prejudicados **cresce** com o número de códigos.

**E-3, pela tela, corrigiu a causa do AX-14 e encontrou um achado que nenhuma API alcança.** A
interface **é honesta**: o seletor mostra `LP01 — Tutor Presencial · PcD`, com o Perfil à frente.
Quem apaga a qualificação é o renderizador do PDF (**AX-17**). E a salvaguarda de rascunho não
enviado perde as modalidades, deixa os botões inertes e regrava a perda por cima (**AX-16**).

O achado de 15/09 ([atribuições repetidas por polo](achado-atribuicoes-repetidas-por-polo.md))
descreveu a amplificação `1 → N` no **texto descritivo** do Perfil e previu, como risco, que as N
cópias divergissem. **Esta auditoria encontrou a divergência acontecendo, duas vezes, em objetos
que o achado não olhava** — e num deles a divergência não é textual: ela troca a ordem de
classificação dos candidatos, e o campo que a carrega é **não retificável**.

Os três eixos que o relatório de ontem não alcançou:

1. **A amplificação atinge regra executável, não só prosa.** Critério de desempate, fato
   declarado, modalidade de concorrência e regra normativa de cota são todos `FK → PerfilVaga` ou
   descendentes dele. Com 16 códigos, o item 6.3.2 do Edital — três linhas, declaradas uma vez —
   vira 48 objetos independentes que nada compara.
2. **Existe amplificação no sentido inverso, e ela é pior.** A Ficha de Avaliação varia por
   **curso** (Letras pontua Doutorado em 25; TADS, em 20, e tem dois itens que Letras não tem),
   mas `EtapaAvaliacao` é do **Edital** e "vale para todos os seus Perfis". O sistema colapsou
   `K = 2` baremas em `1`, e o barema em si — os itens, os limites, as notas de rodapé — não
   existe como objeto em lugar nenhum.
3. **O catálogo de Seções é fechado e não tem via de escape.** Oito seções normativas do 140/2025
   — Vagas, Prova de Títulos, Verificação da autodeclaração, Convocação, Mobilidade entre perfis,
   Curso de formação, Vinculação à UAB, Prazo de validade — não têm onde morar. É por isso que a
   prévia tem 11 seções, seis delas com prosa institucional genérica, e o documento real tem 15
   com norma substantiva em todas.

E um achado que corrige uma premissa do registro de ontem: **`LP01` e `LP04` são o mesmo polo**
(Afonso Cláudio) com perfis de formação diferentes. O código **não** é o polo; é o par
`(perfil de formação × polo)`. A matriz é bidimensional e o sistema tem um eixo só.

---

## Mapa da estrutura normativa observada

O 140/2025 declara em **seis** níveis, não em três:

```
EDITAL 140/2025
├── norma do certame .................. inscrição única por candidato (5.7), prova de títulos em
│                                       etapa única (6.1), ordem de desempate (6.3.2),
│                                       reserva legal e tabela de convocação (4.3, 10.5),
│                                       heteroidentificação (8), mobilidade entre perfis (11),
│                                       curso de formação (12), validade de 2 anos (14)
│
├── FUNÇÃO ............................ Tutor Presencial (2.1 + ANEXO I)
│   └── atividades, regime de trabalho, remuneração
│   └── nota: LP05–LP11 têm "Tutor Presencial / Supervisor de Estágio" — duas funções num código
│
├── CURSO + CAMPUS OFERTANTE .......... Lic. em Letras Português (Vitória) · TADS (Alegre)
│   └── ÁREA ........................... Letras · Informática
│   └── FICHA DE AVALIAÇÃO ............. ANEXO IV, uma por curso, com composição diferente
│
├── PERFIL (formação exigida) ......... 3 em Letras, 1 em TADS — 4 no Edital inteiro
│   └── requisito de formação, e o documento que o comprova
│
├── POLO .............................. 10 municípios distintos em Letras, 5 em TADS
│
└── CÓDIGO DE INSCRIÇÃO ............... 16 — o par (perfil × polo)
    └── identidade para inscrever, classificar, ocupar e convocar
```

Cardinalidades medidas no documento real:

| Dimensão | Instâncias | Independente? | Faz variar |
|---|---:|---|---|
| Função | 2 grafias | sim | atividades, regime, remuneração |
| Curso | 2 | sim | ficha de avaliação, campus ofertante, área |
| Campus ofertante | 2 | não — propriedade do Curso | nada |
| Área | 2 | não — propriedade do Curso | nada observável |
| Perfil de formação | 4 | sim | requisito, documento comprobatório |
| Polo | 14 distintos | sim | nada além da localidade |
| Código | 16 | derivado — `perfil × polo` | nada; é chave |
| Modalidade | 4 | sim, e é do **certame** | documentos condicionados, ordem de convocação |
| Etapa | 1 | sim, e é do **certame** | — |
| Marco / desempate | 1 regra | sim, e é do **certame** | — |
| Cronograma | 13 eventos | sim, e é do **certame** | — |

**Nenhuma dimensão do Edital varia por código.** O código é a chave da execução — inscrever,
classificar, ocupar, convocar, e a cota de PcD de 8.2 ("até 3 candidatos por código de inscrição").
Ele não é a granularidade de **nenhuma declaração normativa**.

---

## Matriz de propriedade normativa

`n` = número de códigos (16 no Edital real, 9 no teste). Colunas "sistema" medidas no código em
`c53e3b4`.

| Informação | Escopo real | Card. real | Onde o sistema guarda | Card. sistema | Renderização | Retificação | Risco |
|---|---|---:|---|---:|---|---|---|
| Atividades de tutoria | Função | 1 | `PerfilVaga.duties` | n | n blocos | n endereços | alto |
| Regime de trabalho | Função | 1 | `PerfilVaga.description` | n | n blocos | n endereços | alto |
| Carga horária | Função | 1 | `PerfilVaga.workload` | n | 1 coluna da Tabela 1 | n endereços | médio |
| Remuneração | Edital (13.4) | 1 | `PerfilVaga.compensation` | n | n linhas | n endereços | alto |
| Requisito de formação | Perfil | 4 | `PerfilVaga.requirements` | n | n blocos | n endereços | alto |
| **Idem, como documento** | Perfil | 4 | `DocumentoExigido.instructions` | n | n blocos | n endereços | **alto — já divergiu** |
| Ficha de avaliação (barema) | Curso | 2 | **não existe** | 0 | ausente | inendereçável | alto |
| Pontuação máxima | Curso | 2 | `EtapaAvaliacao.maximum_score` | 1 | 1 linha | 1 endereço | alto |
| Ordem de desempate | Edital (6.3.2) | 1 | `CriterioDesempate` (via marco, via perfil) | 3n | n blocos | 3n, e o **tipo** não se retifica | **alto — já divergiu** |
| Fatos do candidato | Edital | 3 | `FatoDeclarado` | 3n | n blocos | 3n endereços | médio |
| Marco de classificação | Edital | 1 | `MarcoClassificatorio` | n | n blocos | n endereços | médio |
| Modalidades AC/PPIQ/PcD/PTT | Edital (4.4) | 4 | `ModalidadeConcorrencia` | 4n | por perfil | 4n endereços | médio |
| Fundamento e % da reserva | legislação federal | 3 | `RegraNormativa` (1:1 modalidade) | 4n | — | 4n endereços | médio |
| Documento condicionado à modalidade | Edital (5.5 h–m) | 5 | `DocumentoExigido` + FK modalidade-do-perfil | 5n | n blocos | 5n endereços | alto |
| Documento geral (RG, CPF, TSE…) | Edital (5.5 a–e) | 7 | `DocumentoExigido` sem escopo | 7 | 1 bloco | 7 endereços | — correto |
| Tabela de convocação (10.5) | Edital | 1 | `RegraNormativa.call_rules` (opaco) | 4n | ausente | não retificável | alto |
| Teto de inscrições (5.7) | Edital | 1 | `Edital.max_inscricoes_por_candidato` | 1 | **ausente** | 1 endereço | alto |
| Curso / Área / Campus | Edital | 2 | **não existe** | 0 | ausente | inendereçável | alto |
| Cronograma | Edital | 13 | `EventoCronograma` | 13 | 1 tabela | 13 endereços | — correto |
| Anexos | Edital | 11 | `AnexoEdital` | 11 | lista de rótulos | 11 endereços | médio |
| Número do Edital | Edital | 1 | `number`/`year` **e** `title` | 2 | capa usa `title`, rodapé usa `number` | só `title` se retifica | **alto — já divergiu** |

---

## Achados

### AX-1 — Dois dos nove critérios de desempate apontam para o lado oposto, e o campo não é retificável

**Natureza:** MODELAGEM

**Evidência no Edital real:** item 6.3.2, declarado **uma vez** para o certame inteiro:
*"a) Candidato mais idoso […]; b) Maior experiência na tutoria (em mês); c) Candidato que tenha
realizado curso […] Mediação pedagógica no Moodle"*. O terceiro critério premia **ter** o curso.

**Evidência na prévia:** os nove blocos "Marcos classificatórios" repetem os três critérios. Sete
deles imprimem *"3º **maior** valor declarado em Realização do curso…"*. **Dois — `LP01` (p. 5) e
`TADS14` (p. 18) — imprimem "3º menor valor"**, que desempata a favor de quem **não** fez o curso.
Os dois não formam grupo: um é de Letras, outro de TADS; um é o primeiro perfil da lista, outro o
oitavo. Não há dimensão do Edital que explique a diferença.

**Evidência no código:** `editais/models/perfis.py:336` — `CriterioDesempate.marco` é
`FK → MarcoClassificatorio`, que em `:255` é `FK → PerfilVaga`. A escolha é um `<select>` por
critério em `interface/templates/interface/_criterio.html:21-22`. Não existe, em lugar nenhum,
replicação entre Perfis nem conferência de igualdade — o `grep` por "copiar/replicar/todos os
perfis" em `interface/` e `editais/` devolve só o reaproveitamento de Edital anterior.
**E `mutabilidade.py:362` classifica `("tiebreakers", "type")` como não retificável**, com a razão
escrita: *"trocá-lo não corrige o desempate, substitui-o por outro"*.

**Granularidade no documento:** o certame. Um item, uma vez.
**Granularidade no sistema:** `Perfil → Marco → Critério`.
**Cardinalidade:** `1 → 3n`.

**Por que importa:** é a primeira divergência **medida** entre cópias que deveriam ser a mesma
norma, e não é cosmética: ela inverte a ordem de dois candidatos empatados. Publicada, não se
corrige — o tipo é imutável por decisão da `026`, e o caminho restante é remover o critério e
acrescentar outro, o que deixa os empates já resolvidos resolvidos por critério que o Edital não
tem mais.

**Comportamento em escala:** `n=1`, impossível — não há com o que divergir. `n=3`, 9 selects.
`n=16`, **48 selects**, e a taxa observada no teste foi de **2 erros em 9 blocos (22%)**. `n=50`,
150 selects e nenhuma conferência.

**Impacto na Retificação:** corrigir a ordem de desempate no Edital inteiro são `n` Alterações de
`order` mais `3n` pares remoção+acréscimo se algum tipo estiver errado.

**Risco de divergência:** **alto**, e já materializado. Categoria **A** (o modelo admite múltiplas
fontes), não B: os outros sete blocos estão certos, o texto é idêntico, e o autor não tinha como
conferir 48 seletores sem um diff que o sistema não oferece.

**Relação com achados existentes:** **novo objeto, mesmo mecanismo**. O achado de 15/09 previu a
divergência em `duties`/`workload`/`compensation` e disse *"divergem no dia em que uma Retificação
alcançar quinze"*. Aqui ela apareceu **na autoria**, antes de qualquer Retificação, e num campo
que a Retificação não alcança.

**Possíveis famílias de solução:** (a) a regra de classificação como objeto do Edital, referenciada
pelos Perfis; (b) o marco herdado do Edital com sobrescrita explícita por Perfil; (c) manter a
granularidade e acrescentar conferência de publicação que exiba as divergências entre Perfis sem
decidir por elas; (d) declarar uma vez no assistente e materializar por Perfil na gravação — alívio
de digitação que não fecha a divergência posterior.

**Confiança:** alta.

---

### AX-2 — O requisito de formação tem duas fontes no mesmo documento, e as duas já se contradizem

**Natureza:** MODELAGEM

**Evidência no Edital real:** ANEXO III declara o requisito na coluna PERFIL; o item 5.5.f manda
comprová-lo *"de acordo com a função pleiteada e conforme apresentado na coluna Perfil do ANEXO III"*
— ou seja, o documento **remete** ao requisito, não o repete.

**Evidência na prévia:** duas contradições internas, no mesmo PDF.

1. **`LP04`.** A seção 5.4 (p. 9) declara o requisito *"Graduação em Letras OU outra Licenciatura
   COM experiência em Atendimento Educacional Especializado (AEE) - Leitura"* — que é exatamente o
   que o ANEXO III diz. Mas a seção 4 (p. 2) imprime **quatro** blocos de documento para os quatro
   perfis de Letras, e os quatro dizem *"Graduação em Letras/Português COM Pós-graduação Lato sensu
   OU Stricto sensu…"*. **O documento que o `LP04` exige comprova um requisito que o `LP04` não
   tem.**
2. **TADS.** A seção 5.5 (p. 12) traz o requisito íntegro e legível. A seção 4 (p. 2) traz o mesmo
   requisito com o texto embaralhado: *"…OU Sistemas de Tecnologia em Análise e Desenvolvimento de
   Sistemas (TADS) Informação Tecnologia Informática Análise OU em e Desenvolvimento de Sistemas
   OU…"* — resíduo de colagem da tabela de três colunas do ANEXO III. Nas cinco cópias.

**Evidência no código:** `PerfilVaga.requirements` (`editais/models/perfis.py:20`) e
`DocumentoExigido.instructions` (`editais/models/documentos.py:29`) são campos livres
independentes. Não há vínculo entre eles: `DocumentoExigido.anexo` liga o requisito ao **modelo de
formulário**, nunca ao requisito do Perfil. O PDF imprime os dois por caminhos separados —
`pdf.py:1627-1636` para o Perfil, `pdf.py:1892` para o documento.

**Granularidade no documento:** Perfil de formação — 4 no Edital inteiro, e o documento remete.
**Granularidade no sistema:** dois campos de texto em duas tabelas, `n` vezes cada.
**Cardinalidade:** `4 → 2n`.

**Por que importa:** o candidato lê os dois blocos e eles discordam. Com `LP04`, a pessoa que
atende o requisito publicado (AEE) não consegue apresentar o documento publicado (pós em Letras), e
a inscrição dela é indeferível pelo item 5.13. A conferência da banca tem duas respostas para a
mesma pergunta.

**Comportamento em escala:** `n=1` — as duas cópias ficam lado a lado na mesma tela e o autor vê a
diferença. `n=9` — já divergiu, duas vezes. `n=16` — 32 textos. `n=50` — 100.

**Impacto na Retificação:** corrigir o requisito do `LP04` são **duas** Alterações em dois
endereços de coleções diferentes (`/profiles/id=…/requirements` e
`/requiredDocuments/id=…/instructions`), e nada obriga a segunda.

**Risco de divergência:** **alto**, materializado duas vezes em nove perfis. Categoria **A**, com
efeito de **D** no caso TADS (o texto veio de colagem, mas a colagem só precisou existir porque o
requisito não tinha uma fonte só).

**Relação com achados existentes:** **novo**. Vizinho de **P-13** de
[`achados-editais-externos.md:237`](achados-editais-externos.md:237) — *"a ramificação antes do
documento"* —, que descreve a via alternativa de elegibilidade; aqui a questão é anterior: o
requisito e sua prova são dois textos livres sem relação declarada.

**Possíveis famílias de solução:** (a) requisito como objeto com identidade, e o documento aponta
para ele em vez de repeti-lo; (b) `instructions` proibido de repetir o requisito, com o PDF
compondo a remissão como o Edital real faz; (c) manter os dois textos e conferir a divergência na
publicação.

**Confiança:** alta.

---

### AX-3 — O catálogo de Seções é fechado, e oito seções normativas do Edital real não têm onde morar

**Natureza:** MODELAGEM

**Evidência no Edital real:** 15 seções numeradas. Oito delas carregam norma que o sistema não tem
onde guardar: **4 VAGAS** (4.3 a 4.9 — reserva legal, opção única, verificação étnico-racial),
**6 PROVA DE TÍTULOS** (etapa única, autopontuação, desempate), **8 VERIFICAÇÃO DA AUTODECLARAÇÃO**
(12 subitens com rito de videoconferência e as cinco hipóteses de indeferimento), **10 CONVOCAÇÃO**
(tabela de 50 posições e as regras de reversão 10.5.1/10.5.2), **11 MOBILIDADE ENTRE PERFIS**,
**12 CURSO DE FORMAÇÃO** (com desclassificação por não apresentar certificado), **13 VINCULAÇÃO À
UAB** (remuneração, acúmulo de bolsas), **14 PRAZO DE VALIDADE** (2 anos, prorrogável uma vez).

**Evidência na prévia:** 11 seções numeradas, seis delas com a redação institucional padrão
intocada — p.ex. seção 2, *"Poderá participar do processo seletivo quem atender às condições
estabelecidas neste Edital e aos requisitos específicos do Perfil de Vaga pretendido"*, no lugar dos
nove requisitos do item 3. Nenhuma das oito seções acima aparece, em nenhuma forma.

**Evidência no código:** `editais/domain/secoes.py:1-11` — *"O conjunto de seções e a ordem entre
elas são definidos pelo sistema […] É o que separa um documento institucional estruturado de um
construtor de documentos"*. O `CATALOGO` tem 12 entradas fixas, seis textuais e seis geradas, e não
há caminho para acrescentar uma décima terceira: a identidade é `uuid5(edital.id, key)` sobre chave
do catálogo.

**Granularidade no documento:** o Edital.
**Granularidade no sistema:** doze chaves fixas em código.
**Cardinalidade:** `15 → 12`, com as 8 sobrantes descartadas.

**Por que importa:** o documento gerado não é o Edital. Não é questão de redação: as regras que
sumiram decidem quem é eliminado (12.2), quem é convocado e em que ordem (10.5), o que acontece
quando falta candidato numa submodalidade (10.5.1), e por quanto tempo o certame produz efeito
(14.1). Publicar o documento da prévia como Edital 149/2026 publicaria um certame cujas regras de
convocação e de validade não existem.

**Comportamento em escala:** independe de `n`. É defeito de **cobertura de norma**, e nem um Perfil
nem cinquenta o revelam — só um Edital real de tamanho normal revela.

**Impacto na Retificação:** nulo, porque não há o que retificar. É o pior caso do Princípio II: não
há fonte autoritativa nenhuma, nem divergente.

**Risco de divergência:** **alto**, por ausência: a norma sobrevive fora do sistema (no `.docx` que
alguém guardou), e aí divergência é certa.

**Relação com achados existentes:** **novo como diagnóstico**; consequência estrutural do que a
`006` chamou de "elaboração completa". Vizinho da lacuna "Perfil de Vaga" da auditoria de 13/09,
que olhava vocabulário e não cobertura.

**Possíveis famílias de solução:** (a) seções textuais livres acrescentáveis, com ordem declarada —
resolve a publicação e deixa a norma inexecutável; (b) catálogo maior, cobrindo as espécies
recorrentes da amostra (convocação, validade, verificação de autodeclaração), cada uma com forma
própria; (c) distinguir "norma que o sistema executa" de "norma que o sistema apenas publica", e
dar à segunda um lugar declarado — é a P-9 de `achados-editais-externos.md` aplicada ao documento e
não ao requisito; (d) deixar como está e aceitar que o sistema publica um extrato, não o Edital.

**Confiança:** alta.

---

### AX-4 — A Ficha de Avaliação varia por curso, não existe como objeto, e a Etapa que a substitui é do Edital inteiro

**Natureza:** MODELAGEM

**Evidência no Edital real:** ANEXO IV, **duas** fichas, uma por curso, com composição diferente:

| Item | Letras (Vitória) | TADS (Alegre) |
|---|---:|---:|
| Doutorado na área | **25** | **20** |
| Mestrado na área | 15 | 15 |
| Pós lato sensu (2 × 5) | 10 | 10 |
| Curso Moodle / Mediadores | 20 | 20 |
| Tutoria em EaD | **30** | **10** (e "nos últimos 2 anos") |
| Tutoria em ADS/Sistemas para Internet | — | **10** |
| Docência em TADS | — | **15** |
| **Total** | 100 | 100 |

**Evidência na prévia:** a seção 6 (p. 21) declara uma única Etapa: *"6.1 Prova de Títulos ·
Caráter: eliminatória e classificatória · Peso: 1 · Nota mínima: 0 · Pontuação máxima: 100"*. Os
itens, os limites por item e as duas notas de rodapé (*"só serão pontuados os títulos que excederem
aos exigidos no perfil"*) não aparecem em lugar nenhum do documento.

**Evidência no código:** `editais/models/etapas.py:11-20` — *"Pertence ao **Edital** e vale para
todos os seus Perfis"*. Não há modelo de item de barema: `avaliacoes/models.py` tem `Atribuicao`,
`Avaliacao`, `ConclusaoAvaliacao` e `Impedimento`, e nada mais; o `grep` por "barema" no backend
devolve zero. A pontuação é um `DecimalField` livre validado apenas contra `maximum_score`.

**Granularidade no documento:** o Curso — `K = 2`.
**Granularidade no sistema:** o Edital — `1`. E o conteúdo da ficha: `0`.
**Cardinalidade:** `2 → 1`, com achatamento; e `12 linhas de barema → nenhuma`.

**Por que importa:** é **amplificação ao contrário**, e o §3 do briefing pede as duas direções. Um
candidato de Letras com doutorado vale 25 pontos; um de TADS, 20. O sistema não tem como dizer
isso. Pior: **declarar as duas fichas como duas Etapas não resolve**, porque a Etapa "vale para
todos os Perfis" — o candidato de Letras ficaria sujeito também à ficha de TADS. O modelo, como
está, **não consegue representar o 140/2025 fielmente**, e nenhum ajuste de cadastro contorna isso.

E o barema ausente tem consequência de direito: o item 6.2 diz *"Só serão pontuados os documentos
constantes no ANEXO IV"*. Sem o anexo, a pontuação atribuída pela banca não é conferível contra
norma nenhuma, e o recurso do item 7 perde o objeto.

**Comportamento em escala:** `n=1` não revela nada — um Perfil, um curso, uma ficha, e o colapso é
invisível. `n=9`, como no teste, também não revela: os nove blocos herdam a mesma Etapa e ninguém
nota que os dois cursos deveriam divergir. `n=16` é idêntico. **É defeito por número de cursos,
não por número de códigos** — aparece com `K=2` e some com `K=1`.

**Impacto na Retificação:** corrigir "Doutorado: 25" é **inendereçável**. Corrigir a pontuação
máxima é 1 Alteração que atinge os dois cursos ao mesmo tempo.

**Risco de divergência:** **alto**, por ausência de fonte: a ficha real circula como anexo `.docx`
fora do sistema, e o sistema executa contra um teto que não sabe de onde veio.

**Relação com achados existentes:** **novo**. Vizinho de **P-7** de `achados-editais-externos.md`
(*"a expectativa de pontuação declarada pelo candidato limita o que a banca atribui"*) — que
pressupõe um barema que aqui não existe.

**Possíveis famílias de solução:** (a) barema como objeto publicado, com itens, limites e
acumulabilidade, pendurado na Etapa; (b) o Curso como dimensão, e a Etapa referenciada por Curso;
(c) Etapa com aplicabilidade por Perfil, como `DocumentoExigido` já tem; (d) o anexo continua fora
e o sistema declara explicitamente que não conhece a regra de pontuação — o que torna a nota da
banca um ato discricionário publicado, e é decisão, não omissão.

**Confiança:** alta.

---

### AX-5 — Curso, Área e Campus ofertante não existem, e a semântica deles sobrevive apenas dentro do código de inscrição

**Natureza:** MODELAGEM

**Evidência no Edital real:** o ANEXO III é uma matriz com cabeçalho `Curso:` e `Campus ofertante:`
e colunas `CURSO | ÁREA | PERFIL | FUNÇÃO | POLO | CÓDIGO DE INSCRIÇÃO`. Cinco dimensões e uma
chave. O ANEXO IV repete `Curso:` e `Campus ofertante:` como cabeçalho das fichas.

**Evidência na prévia:** as palavras "Licenciatura em Letras Português", "Tecnologia em Análise e
Desenvolvimento de Sistemas", "Letras", "Informática", "Vitória" e "Alegre" **não aparecem uma
única vez** fora do texto de requisito. O que restou da dimensão Curso é o prefixo `LP` / `TADS` no
código.

**Evidência no código:** `grep` por curso/área/campus em `editais/` devolve apenas ocorrências de
"Recurso" e de prosa em comentários. `PerfilVaga` tem `code`, `name`, `locality` — e nada mais que
possa carregar as três dimensões.

**Granularidade no documento:** Curso (2), Área (2), Campus (2) — propriedades do Curso.
**Granularidade no sistema:** inexistente; inferível só por prefixo de string.
**Cardinalidade:** `2 → 0`.

**Por que importa:** o candidato não descobre, pelo documento publicado, **para qual curso** está se
inscrevendo. A ficha de avaliação depende do curso (AX-4). A mobilidade entre perfis do item 11.3
opera por *"aderência por perfil e polo"*. A cota do item 4.3 é *"5% dos convocados para cada
curso/área/polo"* — a **população de apuração** é o trio, e o sistema só conhece o código. E a
única coisa que ainda distingue os dois cursos é o prefixo de uma string livre, que nada valida:
um `LP16` digitado sob TADS não seria recusado por nada.

O briefing pede que isto seja dito explicitamente: **`LP` e `TADS` não são evidência normativa de
Curso.** São convenção editorial do redator do 140/2025, e o 173/2025 usa outra.

**Comportamento em escala:** `n=1` com um curso, invisível. A partir de dois cursos no mesmo Edital
— que é o caso deste — a informação some da publicação. Com 50 códigos em 6 cursos, o documento
publica 50 blocos que o leitor não consegue agrupar.

**Impacto na Retificação:** corrigir o nome de um curso é inendereçável; na prática seria retificar
`name` ou `code` de todos os Perfis daquele curso — e `code` é **estrutural**, não retificável
(`mutabilidade.py:198`).

**Risco de divergência:** **médio** — não há duas cópias divergindo, há uma informação ausente.

**Relação com achados existentes:** **evidência adicional de P-5** (`achados-editais-externos.md:127`),
que já dizia *"não é o Edital, e nem sempre é o curso […] a unidade é a oferta localizada, e a
matriz é bidimensional"*. A evidência nova é que o eixo ausente **não é só o polo**: é o curso, e
com ele o campus, a área e o barema.

**Possíveis famílias de solução:** (a) Curso como objeto do Edital, com campus e área, e o Perfil
referenciando-o; (b) uma dimensão genérica de agrupamento declarada pelo Edital, sem nomear
"curso" — atende também o 28/2026 e o 58/2026 da amostra; (c) manter e aceitar que Editais
multicurso saem sem a estrutura.

**Confiança:** alta.

---

### AX-6 — O código não é o polo: `LP01` e `LP04` são o mesmo município com perfis diferentes

**Natureza:** MODELAGEM (evidência que corrige um registro anterior)

**Evidência no Edital real:** ANEXO III, primeira tabela. `LP01` → Afonso Cláudio, perfil
*"Graduação em Letras/Português COM Pós-graduação…"*. `LP04` → **Afonso Cláudio**, perfil
*"Graduação em Letras OU outra Licenciatura COM experiência em AEE - Leitura"*. Os onze códigos de
Letras cobrem **dez** municípios distintos.

**Evidência na prévia:** Tabela 1, p. 3 — `LP01 — Tutor Presencial · Afonso Cláudio` e
`LP04 — Tutor Presencial · Afonso Cláudio`. Duas linhas com nome e localidade idênticos,
distinguíveis só pelo código.

**Evidência no código:** `uq_perfil_edital_code` (`editais/models/perfis.py:95`) — a identidade é o
código, e `locality` é texto livre sem unicidade.

**Granularidade no documento:** o código é o **par** `(perfil de formação × polo)`.
**Granularidade no sistema:** o código, como átomo.
**Cardinalidade:** `4 perfis × 14 polos → 16 pares`, dos quais o Edital abriu 16.

**Por que importa:** o registro de 15/09 afirma *"Cada código é um polo"* e lista onze municípios
para onze códigos de Letras. **São dez.** A consequência da correção não é aritmética: se o código
fosse o polo, bastaria acrescentar a dimensão polo para resolver. Como ele é o **par**, qualquer
solução que trate "perfil" e "polo" como um eixo só continua errada — e a família de solução 4
daquele registro ("o polo como dimensão própria") precisa, para funcionar, que a formação seja a
**outra** dimensão, não uma propriedade da oferta localizada.

Também explica por que a Tabela 1 fica ambígua: duas linhas iguais na tela, e o que as separa é
justamente a informação que a tabela não mostra.

**Comportamento em escala:** `n=1` invisível. `n=9`, a colisão já aparece (é este caso). `n=16`,
duas colisões. Com 6 cursos × 10 polos × 3 perfis, `n=50+` e a tabela vira uma lista de códigos sem
estrutura legível.

**Impacto na Retificação:** nenhum efeito direto; o efeito é sobre a forma da solução dos demais
achados.

**Risco de divergência:** **baixo** — é imprecisão de diagnóstico, não de dado.

**Relação com achados existentes:** **corrige** uma premissa de
[`achado-atribuicoes-repetidas-por-polo.md`](achado-atribuicoes-repetidas-por-polo.md) e **reforça**
P-5.

**Possíveis famílias de solução:** as do AX-5, com a condição de que a matriz tenha **dois** eixos
declarados e o código seja derivado do par, não sua identidade única.

**Confiança:** alta.

---

### AX-7 — Modalidade, regra de cota e documento condicionado à modalidade amplificam por Perfil

**Natureza:** MODELAGEM

**Evidência no Edital real:** item 4.4 declara as quatro modalidades **uma vez**, para o certame.
Itens 4.3 e 10.4 declaram o fundamento e os percentuais **uma vez** (Lei 15.142/25 e Decreto
12.536/25, 30%; Portaria CAPES 309/2024, 25%; Decreto 9.508/18, 5%). Itens 5.5.h a 5.5.m declaram
**cinco** documentos condicionados a modalidade, uma vez cada.

**Evidência na prévia:** nenhuma modalidade foi cadastrada no teste original. **A lacuna foi
fechada por experimento em 15/09** — ver *Experimento E-1*, adiante: 12 modalidades, 12 regras
normativas, divergência de percentual publicada sem nenhuma conferência.

**Evidência no código:** `ModalidadeConcorrencia.perfil` é `FK → PerfilVaga`
(`editais/models/perfis.py:112`); `RegraNormativa.modalidade` é `OneToOne → ModalidadeConcorrencia`
(`:355`); `DocumentoExigido.modalidade` é `FK → ModalidadeConcorrencia` (`documentos.py:39`), e
`interface/forms.py:1263-1284` confirma que *"a modalidade carrega o Perfil a que pertence porque a
tela precisa recusar a combinação impossível"*. Logo **um documento restrito a PPIQ está restrito
ao Perfil dono daquela modalidade**, mesmo com `perfil = None`.

**Granularidade no documento:** o Edital (modalidades, percentuais, documentos condicionados).
**Granularidade no sistema:** `Perfil → Modalidade → Regra`.
**Cardinalidade:** modalidades `4 → 4n`; regras normativas `3 → 4n`; documentos condicionados
`5 → 5n`, cada um com `key` própria por causa de `uq_documento_edital_key`.

**Por que importa:** com 16 códigos, as quatro modalidades do item 4.4 viram **64 objetos**, as
regras de cota viram **64**, e as cinco autodeclarações viram **80 registros com 80 chaves
inventadas**. O fundamento legal é federal — a informação mais estável do Edital inteiro — e é a que
mais se multiplica. Quando a Lei 15.142/25 for alterada, o Edital publicado tem 64 endereços com o
mesmo texto.

**Comportamento em escala:** `n=1` → 4+4+5 = 13 objetos, razoável. `n=3` → 39. `n=16` → **208**.
`n=50` → 650.

**Impacto na Retificação:** corrigir o fundamento de uma cota são `n` Alterações
(`/profiles/id=…/competitionModalities/id=…/normativeRule/foundation`). O percentual, idem. A
`callRules` — que carregaria a tabela de 50 posições do item 10.5 — é **não retificável e opaca**
(`mutabilidade.py:264`, `OPACOS`): o Edital que mudar a ordem de convocação não tem caminho.

**Risco de divergência:** **alto**, e **medido** (E-1): o sistema publicou 3% e 30% para a mesma
Lei 15.142/25, em tabelas vizinhas do mesmo documento, sem emitir conferência nenhuma.

**Relação com achados existentes:** **conflita parcialmente com decisão anterior**, e isso precisa
ficar escrito: a Constituição determina *"Cotas DEVEM ser definidas por Perfil"*
(citada em `mutabilidade.py:246`). O achado **não** contesta essa regra — contesta que o **Perfil**
seja o código de inscrição. Se o Perfil fosse `(curso × função × formação)` e a oferta localizada
fosse a dimensão abaixo, "cota por Perfil" e "uma declaração por certame" deixariam de estar em
tensão. Consequência prática: **nenhuma solução para este achado pode ser tomada sem tocar o
Princípio ou a granularidade do Perfil**, e essa é decisão do usuário.

**Possíveis famílias de solução:** (a) redefinir o que é Perfil (ver AX-5/AX-6); (b) modalidade e
regra normativa como objetos do Edital, com o quadro de vagas continuando por Perfil — a cota é
"por Perfil" na **apuração**, e "do Edital" na **declaração**, que é a distinção que o §8 do
briefing pede; (c) manter e aceitar `4n`.

**Confiança:** alta — mecanismo e impacto confirmados por E-1.

---

### AX-8 — O número do Edital tem duas fontes, e o documento gerado se identifica com dois números diferentes

**Natureza:** MODELAGEM, com efeito de GERAÇÃO/PUBLICAÇÃO

**Evidência no Edital real:** o número aparece no título do ato e se repete no cabeçalho de todas as
páginas de anexo — mas ali é um documento redigido à mão, com uma fonte só: quem escreve.

**Evidência na prévia:** a capa imprime, em caixa alta e negrito, **"EDITAL 140/2025 – SELEÇÃO DE
CADASTRO DE RESERVA DE TUTORES PRESENCIAIS…"**, e o rodapé de todas as 22 páginas imprime
**"Edital 149/2026"**. O mesmo documento se identifica como dois atos distintos.

**Evidência no código:** `publicacoes/infrastructure/pdf.py:867-875`:

```python
ato = f"EDITAL Nº {snapshot.get('number','')}/{snapshot.get('year','')}"
anuncio = titulo if titulo.upper().startswith("EDITAL") else (f"{ato} — {titulo}" if titulo else ato)
```

O rodapé (`:2145`) usa `number`/`year`. O cabeçalho usa `title` sempre que ele começa por "EDITAL" —
e aí o campo estruturado é **descartado**. A validação de publicação só exige que `title` exista
(`validation.py:1332`); nada confronta os dois. E a mutabilidade é assimétrica:
`(RAIZ, "number")` e `(RAIZ, "year")` são **não retificáveis** (`mutabilidade.py:177,182`);
`(RAIZ, "title")` é **retificável** (`:186`). A fonte que vai para a capa é a mutável e não
conferida.

**Granularidade no documento:** um número por ato.
**Granularidade no sistema:** dois campos, um deles livre.
**Cardinalidade:** `1 → 2`.

**Por que importa:** é o caso exato do §6 do briefing — *"se o dado estruturado mudar, algum texto
antigo pode permanecer válido sintaticamente, mas semanticamente errado"*. Aqui nem foi preciso
mudar: bastou o autor colar o título do Edital de origem. O documento publicado passa a citar o ato
errado na linha que mais importa, e a numeração institucional — protegida por
`uq_edital_scope_number_year` e por irretificabilidade — perde para uma string livre na hora de ir
ao papel.

O mesmo mecanismo alcança tudo que o §6 lista: o texto do item 5.3 do Edital real manda o candidato
nomear o arquivo `[EDITAL 140/2025–CÓDIGO–MODALIDADE–NOME]`. Numa seção textual, esse "140/2025"
ficaria congelado do mesmo jeito.

**Comportamento em escala:** independe de `n`. Aparece em qualquer Edital criado a partir de outro —
que é o caminho que a `023` oferece e que a auditoria de 13/09 já flagrou por outro motivo
(fricção #2).

**Impacto na Retificação:** o número certo é irretificável, e o número errado — dentro do `title` —
é retificável. A correção existe, mas depende de alguém notar.

**Risco de divergência:** **alto**, materializado no primeiro teste real.

**Relação com achados existentes:** **novo**. A fricção #2 de 13/09 tocou o reaproveitamento
(cronograma vencido), não a identidade.

**Possíveis famílias de solução:** (a) o cabeçalho compõe sempre a partir de `number`/`year`, e
`title` é só o objeto; (b) validação de publicação que recuse título contendo número de Edital
diferente do declarado; (c) `title` deixa de admitir o prefixo "Edital" e o assistente explica por
quê; (d) manter, e conferir na leitura.

**Confiança:** alta.

---

### AX-9 — O teto de inscrições por candidato é executado, é retificável e não é publicado em canal nenhum

**Natureza:** GERAÇÃO/PUBLICAÇÃO

**Evidência no Edital real:** item 5.7 — *"Será aceita somente 1 (uma) inscrição por candidato para
este edital. […] cada candidato poderá se inscrever somente para 1 (um) único código de inscrição"*.
É norma que elimina: quem se inscrever duas vezes tem a segunda recusada.

**Evidência na prévia:** a seção 3 ("DA INSCRIÇÃO", p. 1) traz três linhas genéricas e **não diz
nada** sobre teto. Nenhuma outra seção diz.

**Evidência no código:** o campo existe (`processos/models.py:63`), entra no snapshot
(`publicacoes/application/publish_edital.py:285`), é **retificável**
(`mutabilidade.py:195`), tem rótulo de tela (`interface/retificacao.py:118`) e é **executado**:
`inscricoes/application/submissao.py:266-291` recusa a submissão com HTTP 409 e a mensagem *"Este
Edital admite N inscrição(ões) por candidato"*. O `grep` por `maxInscricoesPorCandidato` em
`pdf.py`, nos templates do portal e na consulta pública devolve **zero**.

**Granularidade no documento:** o Edital.
**Granularidade no sistema:** o Edital — **a granularidade está certa**.
**Cardinalidade:** `1 → 1`.

**Por que importa:** é o inverso dos outros achados e por isso vale registrar separado: aqui o dado
está no lugar certo e o defeito é o documento não o dizer. O sistema **elimina uma inscrição com
base em regra que o Edital publicado não declara**. Para o candidato, é uma recusa sem norma
visível; para o recurso do item 7, é ato sem fundamento publicado.

**Comportamento em escala:** independe de `n`. Independe até de o Edital ter Perfis.

**Impacto na Retificação:** 1 endereço, e ele funciona. O problema é que retificar um valor que
ninguém lê no documento não produz efeito visível — a Retificação publicaria uma Alteração cujo
antes/depois não aparece em canal nenhum.

**Risco de divergência:** **médio**: não há duas cópias; há execução sem publicação.

**Relação com achados existentes:** **novo**, e é o mesmo padrão de
[`achado-objeto-normativo-sem-forma.md`](achado-objeto-normativo-sem-forma.md) visto do outro lado.
Lá o campo tem leitor nenhum e forma nenhuma; aqui ele tem **forma, semântica e executor**, e
mesmo assim nenhum canal.

**Possíveis famílias de solução:** (a) o PDF e o portal declaram o teto na seção de inscrição;
(b) varredura de contrato que exija, para todo campo classificado retificável, ao menos um canal de
exibição — transformaria esta classe inteira de achado em teste; (c) manter e aceitar a execução
silenciosa.

**Confiança:** alta.

---

### AX-10 — "Documentos exigidos para a inscrição" funde quatro categorias, e a ficha de pontuação entrou como documento facultativo de todos

**Natureza:** MODELAGEM, com AUTORIA/CADASTRO como efeito

**Evidência no Edital real:** o 140/2025 separa explicitamente:
**(i) documentos obrigatórios de todos** (5.5 a–e: diploma, identidade, CPF, quitação eleitoral,
alistamento militar — este último condicionado a *sexo masculino, maiores de 17*);
**(ii) documento comprobatório de requisito** (5.5.f, que remete à coluna Perfil do ANEXO III);
**(iii) documentos condicionados à modalidade** (5.5.h–m);
**(iv) formulários que o Edital fornece** (5.5.j, 5.5.l — ANEXO VI e VII);
**(v) títulos passíveis de pontuação** (ANEXO IV), que o item 6.2 governa e que o 5.4.3 conta
separadamente no limite de 50 páginas.

**Evidência na prévia:** a seção 4 (p. 2) traz, sob "De todos os candidatos", cinco alíneas — que
são exatamente os cinco itens do barema de Letras — todas marcadas **"(facultativo)"**. Os
obrigatórios de (i) não aparecem. Os de (iii) e (iv) não aparecem. O de (ii) aparece `n` vezes e
com o defeito do AX-2.

**Evidência no código:** `DocumentoExigido` tem `required: BooleanField` e duas dimensões de
aplicabilidade (`perfil`, `modalidade`). A quarta categoria — *título que pontua* — não tem campo:
o autor só pode marcá-la como não obrigatória. E a condição do 5.5.e (*sexo masculino, maiores de
17*) não tem dimensão, o que `achados-editais-externos.md:288` já registrou como *"a condição sobre
a pessoa, terceira dimensão que o requisito documental ainda não tem"*. `pdf.py:1892-1895` imprime
`instructions` e o sufixo "(facultativo)" — sem categoria.

**Granularidade no documento:** cinco naturezas distintas.
**Granularidade no sistema:** uma tabela, um booleano, duas dimensões.
**Cardinalidade:** `5 naturezas → 1`, e a distinção some.

**Por que importa:** o candidato lê "DOCUMENTOS EXIGIDOS PARA A INSCRIÇÃO" e encontra cinco itens
facultativos que na verdade são o barema, sem saber **quanto cada um vale** (AX-4) — e não encontra
o RG. Do lado do sistema, o portal montará a inscrição sobre a mesma lista: o candidato anexará
títulos numa seção chamada "documentos exigidos" e não anexará identidade, porque ninguém a pediu.

**Comportamento em escala:** `n=1` já revela a fusão de categorias (i)/(v) — e a auditoria de 13/09
não a registrou, porque o cenário 1 tinha **um** documento. `n=16` acrescenta a amplificação de
(ii) e (iii) por cima.

**Impacto na Retificação:** mudar o barema é `5` Alterações em documentos, e não uma no anexo.

**Risco de divergência:** **médio**, com efeito alto sobre o candidato.

**Relação com achados existentes:** **novo quanto à fusão de categorias**; **evidência adicional**
para a "condição sobre a pessoa" já registrada em `achados-editais-externos.md`.

**Possíveis famílias de solução:** (a) natureza declarada no Documento Exigido (obrigatório /
comprobatório / condicionado / pontuável / formulário fornecido), com o PDF agrupando por natureza;
(b) o pontuável sai de "documentos" e passa a pertencer ao barema (AX-4); (c) manter o booleano e
tratar como orientação de cadastro.

**Confiança:** alta.

---

### AX-11 — Os fatos declarados pelo candidato são do certame e moram no Perfil

**Natureza:** MODELAGEM

**Evidência no Edital real:** ANEXO VI — REQUERIMENTO DE INSCRIÇÃO pede **os mesmos** dados de todo
mundo: RG, CPF, data de nascimento, naturalidade, endereço, contato, código pretendido e
modalidade. O desempate por idade (6.3.2.a) e por experiência em tutoria (6.3.2.b) valem para o
certame inteiro.

**Evidência na prévia:** os mesmos três fatos — *Realização do curso…*, *Data de nascimento*,
*Experiência em tutoria, em meses* — repetidos nos nove blocos, em bloco próprio "Dados exigidos na
inscrição".

**Evidência no código:** `FatoDeclarado.perfil` é `FK → PerfilVaga`
(`editais/models/perfis.py:214`), com `uq_fato_perfil_code`. E o tipo é **não retificável**
(`mutabilidade.py:276`).

**Granularidade no documento:** o certame — 3 fatos.
**Granularidade no sistema:** o Perfil — `3n`.
**Cardinalidade:** `3 → 3n`.

**Por que importa:** o `factId` que cada critério de desempate aponta é o do Perfil. Com 16 códigos
existem 16 "Data de nascimento" diferentes, e a mesma pergunta feita ao candidato tem 16
identidades. Se uma delas for cadastrada como `INTEIRO` em vez de `DATA`, o tipo é irretificável e
o desempate daquele código passa a comparar outra coisa — o mesmo mecanismo do AX-1, num campo
ainda mais rígido.

**Comportamento em escala:** `n=1`, 3 fatos. `n=16`, **48**. `n=50`, 150.

**Impacto na Retificação:** renomear um fato são `n` Alterações; corrigir o tipo de um é
impossível — remove-se e acrescenta-se, e o que foi congelado sob o anterior fica sob ele
(`015`, FR-058).

**Risco de divergência:** **médio** — não houve divergência medida nos nove, mas os três rótulos são
idênticos por sorte de digitação, não por construção.

**Relação com achados existentes:** **consequência do achado de 15/09**, em objeto que ele não
listou.

**Possíveis famílias de solução:** as mesmas do AX-1 — o fato é o insumo da regra, e os dois
deveriam morar no mesmo nível.

**Confiança:** alta.

---

### AX-12 — Os anexos são publicados como uma lista de rótulos, e a numeração romana que o texto normativo usa não é verificada

**Natureza:** GERAÇÃO/PUBLICAÇÃO

**Evidência no Edital real:** onze anexos, todos com conteúdo, e o corpo do Edital os cita **vinte e
seis vezes** por número romano — *"conforme ANEXO III – QUADRO DE PERFIL"*, *"ANEXO IV – FICHA DE
AVALIAÇÃO"*, *"(ANEXO VIII)"*.

**Evidência na prévia:** a seção 10 (p. 22) lista **dez** rótulos e nada mais. O ANEXO XI –
DECLARAÇÃO DE PERTENCIMENTO QUILOMBOLA não está na lista. Nenhum rótulo é citado no corpo do
documento, porque o corpo do documento não tem as seções que os citariam (AX-3). Os dois anexos que
o sistema **poderia** ter substituído por estrutura — o III (quadro de perfil) e o IV (ficha de
avaliação) — aparecem como rótulo **e** como seção 5, sem que nada diga qual prevalece.

**Evidência no código:** `pdf.py:1834-1858` — *"Lista, e não conteúdo. […] E não imprime endereço"*.
A decisão é deliberada e registrada (`020`, D-002). O que não existe é conferência: nada verifica se
um `ANEXO III` citado em seção textual tem anexo correspondente, nem se dois anexos têm o mesmo
número, nem se a numeração tem buracos — o rótulo é *"reproduzido como o autor o escreveu"*.

**Granularidade no documento:** onze anexos, com remissões cruzadas.
**Granularidade no sistema:** `n` rótulos, sem numeração própria e sem destino verificável.

**Por que importa:** o §10 do briefing pede integridade referencial. Hoje ela não existe em nenhum
sentido: nem do texto para o anexo, nem do anexo para o texto. Um Edital que cite "ANEXO IV" numa
seção textual e não tenha esse anexo publica uma remissão morta, e nada recusa a publicação.

**Comportamento em escala:** cresce com o número de anexos e de remissões, não com `n` de códigos.

**Impacto na Retificação:** nenhum novo.

**Risco de divergência:** **médio**.

**Relação com achados existentes:** **já coberto em parte** por
[`achado-anexo-sem-destinatario.md`](achado-anexo-sem-destinatario.md), que olha o anexo sem
requisito que o cite. A face nova é a **oposta**: a remissão sem anexo, e a ausência de qualquer
verificação de numeração. A falta do ANEXO XI é **fidelidade do teste** (ver abaixo), não defeito.

**Possíveis famílias de solução:** (a) conferência de publicação que case remissões `ANEXO \w+` nas
seções textuais com os rótulos declarados; (b) número do anexo como campo, em vez de prefixo do
rótulo; (c) manter.

**Confiança:** média-alta — a ausência de conferência é certa; o peso depende de as seções textuais
voltarem a citar anexos (AX-3).

---

### AX-13 — O cabeçalho de alcance dizia o nome do Perfil, e os nove nomes eram o mesmo

**Natureza:** GERAÇÃO/PUBLICAÇÃO — **já corrigido**

**Evidência na prévia:** nove cabeçalhos idênticos `Dos candidatos ao perfil Tutor Presencial:`
(p. 2–3).

**Evidência no código:** corrigido em `c0403a9`, *"fix(pdf): o cabeçalho de alcance dizia o nome do
Perfil, e nove Perfis tinham o mesmo"*, às 10h03 de 15/09 — **1h09 depois de a prévia ser gerada**.
`_rotulo_do_perfil` (`pdf.py:1783`) agora compõe `LP01 — Tutor Presencial`.

**Relação com achados existentes:** **já coberto e fechado** — era a seção "Um defeito de documento
cai junto, e é separável" do achado de 15/09. Fica registrado aqui só para que ninguém releia a
prévia e o conte de novo.

**Confiança:** alta.

---

### AX-14 — O documento publicado diz que a exigência vale para toda uma modalidade; a execução a aplica a um Perfil só

**Natureza:** MODELAGEM, com efeito imediato de execução

**Evidência no Edital real:** item 5.5.i — *"Os candidatos que se inscreverem como Pretos, Pardos ou
Indígenas deverão apresentar: I) Autodeclaração Étnico-racial devidamente assinada (ANEXO V)"*.
Declarado **uma vez**, para toda a modalidade, em todos os 16 códigos.

**Evidência de experimento (E-2):** declarei os cinco documentos condicionados **uma vez cada**,
como o Edital os declara, sem restringir Perfil. A publicação foi **aceita sem nenhuma
conferência**. O PDF publicado imprime:

```
Dos candidatos concorrentes na modalidade Pessoa com Deficiência:
     a) Laudo Médico de Especialista — Item 5.5.h.I do Edital.
     b) ANEXO VIII — Autodeclaração para Pessoa com Deficiência — Item 5.5.h.II do Edital.
```

Sem qualificar Perfil: o Edital afirma, por escrito, que **todo** candidato PcD deve apresentar.
Mas a execução entrega:

```
LP01     5 de 5 documentos
LP02     0 de 5     <<< o candidato nunca é solicitado
TADS11   0 de 5     <<< o candidato nunca é solicitado
```

**Evidência no código:** `editais/domain/documentos.py:97` — `aplicaveis()` compara a **identidade**
da modalidade: `str(modalidade) != str(modality_id)`. Como `ModalidadeConcorrencia` é `FK → PerfilVaga`,
a PcD do `LP01` e a PcD do `LP02` são objetos distintos com UUIDs distintos. Um documento que aponte
a primeira não alcança a segunda. A validação de elaboração
(`documentos.py:65-94`) aceita a declaração porque só verifica se a modalidade existe **em algum**
Perfil do Edital — e o PDF, em `pdf.py:1828`, compõe o cabeçalho sem Perfil justamente porque
`profileId` está vazio.

Os três pontos são individualmente coerentes. Juntos, produzem um Edital que promete uma coisa e
executa outra.

**Granularidade no documento:** a modalidade, no certame.
**Granularidade no sistema:** a modalidade **de um Perfil**.
**Cardinalidade:** `5 → 5n`, com o caminho de `5` aceito e silenciosamente incompleto.

**Por que importa:** é o achado mais grave desta rodada, e o único que produz **contradição entre o
que o Edital publica e o que o sistema faz**. Os efeitos concretos:

- o candidato PcD de 15 dos 16 códigos se inscreve **sem** apresentar laudo, e concorre na cota
  reservada sem a prova que o Edital exige;
- a banca, ao conferir, não tem o documento e não tem como saber se a culpa é do candidato — o
  sistema nunca o pediu;
- o item 5.13 manda indeferir inscrição com documentação irregular, e aqui a irregularidade foi
  produzida pelo sistema;
- a inscrição fica **juridicamente frágil nos dois sentidos**: indeferir pune quem cumpriu o que lhe
  foi pedido; deferir dispensa a prova que o Edital exige de todos.

**Comportamento em escala:** `n=1` — **impossível de detectar**: com um Perfil só, a modalidade do
Perfil e a do Edital são a mesma coisa, e o caminho ingênuo funciona perfeitamente. `n=3` — 1 de 3
recebe. `n=16` — **1 de 16 recebe, e 15 não**. `n=50` — 1 de 50. **A fração de candidatos
prejudicados cresce com `n`**, e é o único achado com essa propriedade.

**O caminho correto, medido:** declarar um registro por `(documento × Perfil)` — 15 registros para
3 Perfis, **80 para os 16 do 140/2025**, cada um com chave e ordem únicas no Edital
(`uq_documento_edital_key`, `uq_documento_edital_order`), forçando o autor a inventar
`anexo-v-lp01`, `anexo-v-lp02`, `anexo-v-tads11`… O PDF então imprime 48 cabeçalhos de alcance, e o
documento repete as mesmas cinco exigências dezesseis vezes.

**Impacto na Retificação:** corrigir a instrução de um anexo são **16** Alterações; e a correção do
Edital que caiu no caminho ingênuo não é uma Retificação de valor — é o acréscimo de 75 objetos que
deveriam existir desde a publicação.

**Risco de divergência:** **alto**, e de espécie pior: não é divergência entre cópias, é
divergência entre **a norma publicada e o comportamento do sistema**.

**Relação com achados existentes:** **novo**, e não é derivável do achado de 15/09 — aquele mede
repetição; este mede **ausência silenciosa**. É o caso extremo do mecanismo do AX-7.

**Possíveis famílias de solução:** (a) a modalidade como objeto do Edital, referenciada pelos
Perfis — a aplicabilidade por modalidade volta a significar o que o documento diz; (b) manter a
granularidade e fazer a aplicabilidade por **código** de modalidade em vez de por identidade — casa
por string, que é exatamente o que a `R-006` da `025` recusou por escrito; (c) recusar, na
elaboração, documento com `modalityId` e sem `profileId` quando o Edital tem mais de um Perfil —
fecha a armadilha sem tocar o modelo, ao custo de exigir as `n` declarações explicitamente;
(d) conferência de publicação que compare o alcance declarado com o alcance executável e recuse a
diferença.

**Confiança:** alta — medido de ponta a ponta, com o PDF e a função de aplicabilidade reais.

---

### AX-15 — As submodalidades de PPIQ não existem, e o Edital as trata como listas distintas

**Natureza:** MODELAGEM

**Evidência no Edital real:** o item 10.5 convoca, em posições **diferentes** da mesma tabela,
`PPIQ (Pretos/Pardos)` — nas ordens 3ª, 6ª, 13ª, 16ª, 19ª, 23ª, 29ª, 33ª, 36ª, 43ª, 46ª, 48ª e 49ª
—, `PPIQ (Indígenas)` — 9ª e 39ª — e `PPIQ (Quilombolas)` — 26ª. O item 10.5.1 declara reversão
**entre as submodalidades** antes de ir à ampla concorrência. E o item 5.5 pede documentos
distintos de cada uma: ANEXO V de todos, ANEXO IX e declaração da Funai só de indígenas, ANEXO XI
só de quilombolas. O item 8 submete **só** pretos e pardos à heteroidentificação.

**Evidência de experimento (E-2):** as modalidades que o sistema conhece são
`['AC', 'PCD', 'PPIQ', 'PTT']`. Não há onde declarar "indígena" ou "quilombola" dentro de PPIQ.

**Granularidade no documento:** a submodalidade — 4 dentro de PPIQ.
**Granularidade no sistema:** a modalidade — 1.
**Cardinalidade:** `4 → 1`, achatado.

**Por que importa:** é **achatamento**, não amplificação — o mesmo erro de direção do AX-4. As
consequências são executáveis, não redacionais: a ordem de convocação do item 10.5 não é
representável; a reversão hierárquica do 10.5.1 não tem sobre o que operar; a heteroidentificação
do item 8 não consegue separar quem a ela se submete; e os documentos de cada submodalidade não têm
condição a que se prender — que é por que, no E-2, o ANEXO XI (quilombola) teve de ser pendurado no
PPIQ inteiro, exigindo declaração de pertencimento quilombola de todo candidato preto ou pardo.

**Comportamento em escala:** independe de `n`. Depende de o Edital usar reserva com subdivisão — e
`achados-editais-externos.md` já registra a **reversão hierárquica** como forma observada em mais de
um Edital.

**Impacto na Retificação:** nenhum novo; não há o que endereçar.

**Risco de divergência:** **médio** por ausência; alto se alguém tentar representar as
submodalidades como modalidades irmãs, porque aí a cota de 30% passa a ser repartida por quem
cadastra.

**Relação com achados existentes:** **evidência adicional** para a *"reversão hierárquica"* já
registrada em [`achados-editais-externos.md:280`](achados-editais-externos.md:280) — *"vaga não
preenchida num subgrupo vai para os outros subgrupos da mesma reserva, e só depois para a ampla
concorrência"*. A face nova é que a subdivisão também governa **documentos, convocação e
heteroidentificação**, não só reversão.

**Possíveis famílias de solução:** (a) submodalidade como nível abaixo da Modalidade, com
documentos e ordem próprios; (b) modalidades irmãs com a cota declarada no grupo; (c) manter e
aceitar que Editais com subdivisão de reserva não são representáveis.

**Confiança:** alta.

---

### AX-16 — Restaurar o rascunho não enviado perde as coleções aninhadas e deixa a tela inoperante

**Natureza:** AUTORIA/CADASTRO

**Como foi encontrado:** só pela tela. Os experimentos E-1 e E-2 passaram pela API e não o alcançam.

**Evidência medida (E-3):** com um Perfil e uma Modalidade digitados e **não** enviados ao servidor,
saí da etapa e voltei. A tela oferece *"Há preenchimento não enviado neste navegador […]
Restaurar o que eu havia digitado"*. Clicando:

```
storage_antes_tinha_PPIQ ............... true    (a modalidade ESTAVA guardada)
campos_de_modalidade_restaurados ....... 0       (a restauração não a trouxe)
codigo_restaurado ...................... "LP99"  (o Perfil voltou — parece que deu certo)
botao_acrescentar_modalidade_funciona .. false   (e não dá para recadastrar)
storage_depois_ainda_tem_PPIQ .......... false   (a perda foi regravada por cima)
```

**Evidência no código:** `interface/static/interface/rascunho.js:119-133`. A gravação está
correta — `ler()` captura todos os campos do formulário, e o conteúdo do `localStorage` contém a
modalidade. O defeito é a restauração:

- `restaurar()` faz `lista.replaceChildren()` e recria cada linha buscando `form.dataset.fragmento`
  — **o fragmento do Perfil, que nasce sem modalidade nenhuma**;
- `preencher()` só casa nomes na forma `^[a-z]+-\d+-(\w+)$`, que é a do Perfil; os campos de
  modalidade têm quatro segmentos (`modalidade-<perfil>-<modalidade>-code`) e caíram em `simples`;
- os de `simples` são restaurados por `form.elements[nome]`, que é `undefined` para campos que o
  fragmento recriado não tem — e o valor é **descartado em silêncio**;
- o HTML é inserido com `insertAdjacentHTML` e **nada chama `htmx.process()`** — o `grep` por
  `htmx.process` em `interface/static/interface/*.js` não devolve ocorrência nenhuma. Os botões
  `hx-get` dentro do que foi restaurado ficam inertes.

**Por que importa:** são três defeitos encadeados que se somam num só efeito. A pessoa vê o Perfil
de volta e conclui que a salvaguarda funcionou; as modalidades, os fatos declarados e as linhas do
quadro não voltaram; ela não consegue recadastrá-los, porque os botões não respondem; e o autosave
seguinte **regrava o estado incompleto por cima do bom**, tornando a perda irreversível. Nada disso
emite mensagem.

**Comportamento em escala:** o dano é proporcional ao que havia digitado. Num Edital de 1 Perfil e
nenhuma modalidade, a restauração é perfeita — que é por que o cenário 1 de 13/09 não podia
encontrá-lo. Num Perfil do 140/2025, perde as 4 modalidades, as 4 regras normativas, os 3 fatos e
as linhas do quadro: **24 campos preservados, 27 perdidos**.

**Impacto na Retificação:** nenhum — é anterior à publicação.

**Risco de divergência:** **alto** por outra via: a pessoa que recadastra o que sumiu digita de
novo, e é digitando de novo que as cópias divergem (AX-1).

**Relação com achados existentes:** **novo**. Vizinho de
[`replace_draft apaga o que não for reenviado`](../doc/) na memória do projeto — mesma família
("o que não for reenviado some"), agora do lado do navegador e não do `replace_draft`.

**Possíveis famílias de solução:** (a) a restauração recria as coleções aninhadas buscando os
fragmentos correspondentes, e chama `htmx.process()` no que insere; (b) o autosave não regrava
enquanto a restauração não estiver confirmada como completa; (c) a salvaguarda guarda o HTML do
formulário em vez de um mapa de campos; (d) remover a salvaguarda, que hoje promete mais do que
entrega.

**Confiança:** alta — reproduzido três vezes, com a causa localizada no código.

---

### AX-17 — A tela qualifica a modalidade pelo Perfil; o documento publicado apaga a qualificação

**Natureza:** GERAÇÃO/PUBLICAÇÃO — **e é a correção de rumo do AX-14**

**Evidência na tela (E-3):** o seletor "Exigido apenas da modalidade" **não** oferece "PPIQ"
genérico. Com 2 Perfis, ele lista:

```
Todas as modalidades
LP01 — Tutor Presencial · AC — Ampla Concorrência
LP01 — Tutor Presencial · PPIQ — Pretos, Pardos, Indígenas e Quilombolas
LP02 — Tutor Presencial · AC — Ampla Concorrência
LP02 — Tutor Presencial · PPIQ — Pretos, Pardos, Indígenas e Quilombolas
```

**A interface é honesta**: ela diz, em cada opção, de qual Perfil aquela modalidade é. Quem lê com
atenção percebe que precisa declarar uma vez por Perfil.

**Evidência do que o documento faz (E-2):** escolhida a opção `LP01 · PcD`, o PDF imprime

```
Dos candidatos concorrentes na modalidade Pessoa com Deficiência:
```

— **sem o `LP01`**, porque `pdf.py:1828` compõe o cabeçalho a partir de `profileId`, que está
vazio, e ignora o Perfil que a modalidade carrega consigo.

**Por que isto corrige o AX-14:** a causa primária **não** é a tela induzir ao erro. É a
**publicação** descartar uma qualificação que a autoria tinha. O sistema sabe que aquela PcD é a do
`LP01` — mostra isso na tela, guarda isso no banco, usa isso na execução — e só omite no único
lugar em que a informação vira norma.

**O que a tela ainda não faz:**

- o texto de ajuda diz *"ou só para uma modalidade"*, sem dizer que a modalidade pertence a um
  Perfil — é a frase que ensina a leitura errada;
- a combinação **"Todos os Perfis" + "LP01 · PPIQ"** é aceita **sem aviso nenhum**, e foi assim que
  gravei e salvei ("Rascunho salvo — Inscrição."). É contraditória na face, e nada a assinala;
- com 16 Perfis e 4 modalidades, esse seletor teria **65 opções**, e a escolha certa precisa ser
  feita 80 vezes.

**Impacto na Retificação:** nenhum novo.

**Risco de divergência:** **alto** — é o AX-14, com a causa melhor localizada.

**Relação com achados existentes:** **refina o AX-14**, deslocando a causa primária de
MODELAGEM/autoria para GERAÇÃO/PUBLICAÇÃO. A amplificação `5 → 5n` continua sendo de modelagem; a
**contradição entre documento e execução** é do renderizador.

**Possíveis famílias de solução:** (a) o cabeçalho de alcance nomeia o Perfil da modalidade mesmo
quando `profileId` está vazio — conserto pequeno, e fecha a contradição; (b) a elaboração recusa
`modalityId` sem `profileId`, tornando a declaração explícita; (c) as duas.

**Confiança:** alta.

---

## Experimento E-1 — as 4 modalidades em 3 Perfis

Executado em 15/09, em banco de teste isolado, pela **API real de elaboração** (`PUT
/editais/{id}/rascunho` → submissão → homologação → publicação). O Edital reproduz o recorte do
140/2025: 3 Perfis (`LP01`, `LP02`, `TADS11`), cada um com as 4 Modalidades que o item 4.4 declara
uma vez e as Regras Normativas que os itens 4.3/10.4 fundamentam uma vez. Uma única divergência foi
introduzida de propósito: no `TADS11`, o percentual do PPIQ foi digitado como **3%** em vez de 30%
— o dedo que escorrega num zero.

**O que ele mede e o que não mede.** Não mede taxa de erro humano: quem digitou foi um script, que
não erra. Mede o que o modelo **permite** e o que o sistema **confere**.

### Resultado

```
Perfis .............................  3
Modalidades criadas ................ 12    (o Edital declara 4, uma vez)
Regras normativas criadas .......... 12    (o Edital fundamenta 3, uma vez)
Objetos para 7 declarações ......... 24

PPIQ publicado, cópia por cópia (a Lei 15.142/25 manda 30%):
   LP01     percentage = 30.0000
   LP02     percentage = 30.0000
   TADS11   percentage =  3.0000   <<< DIVERGE

RESULTADO: a publicação foi ACEITA.
Conferências emitidas que mencionam percentual ou divergência: NENHUMA
Endereços de Retificação (6 campos por modalidade × 12): 72
```

A submissão emitiu três avisos — sobre descrição ausente, período de inscrição e linhas do quadro
de vagas. **Nenhum sobre a cota.** O Edital foi homologado e publicado normalmente.

### O que o documento publicado diz

O PDF imprime uma tabela de modalidades **por Perfil**. As três ficam a poucos centímetros uma da
outra:

```
Tabela 3 — Modalidades de concorrência — LP01
  PPIQ — Pretos, Pardos, Indígenas e Quilombolas    30%    Lei 15.142/25 e Decreto 12.536/25

Tabela 5 — Modalidades de concorrência — LP02
  PPIQ — Pretos, Pardos, Indígenas e Quilombolas    30%    Lei 15.142/25 e Decreto 12.536/25

Tabela 7 — Modalidades de concorrência — TADS11
  PPIQ — Pretos, Pardos, Indígenas e Quilombolas     3%    Lei 15.142/25 e Decreto 12.536/25
```

**O fundamento é literalmente o mesmo texto nas três linhas, e o percentual da terceira é a décima
parte.** O Edital publicado afirma, com assinatura de autoridade, três coisas diferentes sobre a
mesma lei federal.

### O que isso confirma

1. **A divergência do AX-1 é do modelo, não azar do autor.** Categoria **A**, sem ambiguidade: o
   sistema aceita e publica declarações independentes e contraditórias da mesma norma. Não existe
   comparação entre Perfis em lugar nenhum do caminho de publicação.
2. **A amplificação é real e composta.** `4 + 3 = 7` declarações normativas viram **24 objetos** com
   3 Perfis. Com os 16 códigos do 140/2025 seriam **128** (64 modalidades + 64 regras), e o
   documento teria **64 linhas de tabela** repetindo as mesmas quatro leis.
3. **O leitor é a única conferência que existe.** A divergência é visível — e só para quem ler as
   16 tabelas em sequência e comparar célula a célula. Com 3 Perfis isso é viável; com 16, é o que
   o Princípio II existe para não depender.
4. **Escala de Retificação:** 72 endereços com 3 Perfis; **384** com 16. Corrigir a cota do PPIQ no
   Edital inteiro seria redigir 16 Alterações idênticas, e nada verifica que ficaram iguais.

### O que ele não cobriu

- O **fundamento** (texto livre) divergente entre cópias: não foi testado, mas o campo é
  `TextField` sem qualquer confronto — o mecanismo é o mesmo.
- Os **documentos condicionados à modalidade** (as 5 autodeclarações): medidos em **E-2**.
- A **tela** de elaboração: medida em **E-3**.

**Limpeza:** o arquivo de teste e o banco `test_exp_modalidades` foram removidos. Nada no
repositório foi alterado além deste documento.

---

## Experimento E-2 — os 5 documentos condicionados à modalidade

Executado em 15/09, mesmo método de E-1: API real, 3 Perfis × 4 Modalidades, e os cinco documentos
que o 140/2025 condiciona à modalidade nos itens 5.5.h a 5.5.m — laudo médico e ANEXO VIII (PcD),
ANEXO V e ANEXO XI (PPIQ), ANEXO X (PTT). Dois caminhos foram medidos.

### Caminho 1 — declarar os cinco uma vez, como o Edital declara

```
registros criados: 5
publicação: ACEITA — conferências sobre documento: NENHUMA

quantos dos 5 cada Perfil efetivamente recebe:
   LP01     5 de 5
   LP02     0 de 5   <<< o candidato nunca é solicitado
   TADS11   0 de 5   <<< o candidato nunca é solicitado
```

E o PDF publicado afirma o contrário do que o sistema faz — ver **AX-14**, que este caminho
produziu.

### Caminho 2 — um registro por (documento × Perfil)

```
registros criados: 15    (o Edital declara 5, uma vez)
chaves distintas a inventar: 15
exemplo: ['anexo-v-lp01', 'anexo-v-lp02', 'anexo-v-tads11']

quantos dos 5 cada Perfil recebe:
   LP01     5 de 5
   LP02     5 de 5
   TADS11   5 de 5
```

Funciona, e o PDF passa a imprimir nove cabeçalhos de alcance — três por Perfil — repetindo as
mesmas cinco exigências. Projeção para os 16 códigos do 140/2025: **80 registros, 80 chaves, 80
ordens, e 48 cabeçalhos no documento**.

### Submodalidades

```
modalidades que o sistema conhece: ['AC', 'PCD', 'PPIQ', 'PTT']
lugar para declarar 'indígena' ou 'quilombola' dentro de PPIQ: nenhum
```

Ver **AX-15**. No experimento, o ANEXO XI — que o Edital exige só de quilombolas — teve de ser
pendurado no PPIQ inteiro, e o PDF passou a exigir declaração de pertencimento quilombola de todo
candidato preto ou pardo.

### O que E-2 acrescenta a E-1

E-1 mostrou que o sistema **aceita cópias divergentes**. E-2 mostrou algo pior: que o caminho
natural — declarar uma vez, como o Edital declara — **é aceito e não funciona**, sem que nada
avise. A falha de E-1 é visível para quem comparar as tabelas; a de E-2 é invisível até o dia da
conferência da banca.

**Limpeza:** arquivo de teste e banco `test_exp_documentos` removidos.

---

## Experimento E-3 — pela tela de elaboração

Executado em 15/09 no navegador, contra um ambiente próprio (`ps_aud_granul`, porta 8040), com o
assistente real: Processo criado do zero, Edital 150/2026, papéis de elaborador, homologador,
publicador e gestor. **É o único dos três experimentos que passa por onde a pessoa passa.**

### O que a tela diz de si mesma

No topo da etapa 2, antes de qualquer campo:

> *"Cada Perfil é uma oportunidade do Edital, com requisitos, vagas e modalidades próprios.
> **Alterar um não afeta os demais.**"*

A frase é verdadeira e é o achado de 15/09 escrito pela própria interface. Ela descreve o
comportamento; não avisa que, quando a norma é uma só, esse comportamento é o problema.

E na ajuda da etapa 6:

> *"Um documento pode valer para todos, ou só para um Perfil, **ou só para uma modalidade**, ou
> para a combinação dos dois."*

É a frase que ensina a leitura que o AX-14 pune — "só para uma modalidade" não existe: toda
modalidade é de um Perfil.

### Custo de autoria, medido

| Objeto | Campos | No 140/2025 (16 códigos) |
|---|---:|---:|
| Perfil, sem modalidades | 16 | 256 |
| Cada Modalidade (+ sua linha no quadro) | 6 | 384 (4 × 16) |
| **Perfil com as 4 modalidades** | **40** | **640** |
| Cada Documento Exigido | 7 | 560 (5 × 16 × 7) |
| Cada Fato declarado | 3 | 144 (3 × 16) |

**Mais de 1.300 campos** para um Edital que o Cefor redige hoje em 27 páginas de texto.

E, confirmado na tela: **não existe botão de copiar, duplicar ou replicar.** A varredura por
`copiar|duplicar|replicar|aplicar a todos` nos botões da página devolve lista vazia. O segundo
Perfil nasce com **16 campos em branco e nenhuma modalidade** — zero herdado do primeiro.

### O que a tela faz melhor do que o documento

O seletor de modalidade qualifica cada opção pelo Perfil — ver **AX-17**. É a peça honesta da
cadeia, e é o que desloca a culpa do AX-14 para a publicação.

### O que só a tela revelou

**AX-16**, a cadeia de perda da salvaguarda de rascunho — três defeitos encadeados que nenhum teste
de API alcança.

### Limpeza

Servidor parado, banco `ps_aud_granul` removido, entrada de preview revertida no
`.claude/launch.json`. O `git status` fica com um arquivo novo: este relatório.

---

## Hipóteses (não confirmadas)

**H-1 — A função pode ser plural dentro de um código.** `LP05`–`LP11` declaram, na coluna FUNÇÃO,
*"Tutor Presencial / Supervisor de Estágio"*. Se forem **duas** funções acumuladas, o sistema teria
de guardar dois conjuntos de atribuições no mesmo `PerfilVaga.duties`; se for **uma** função de nome
composto, não há achado. Os sete códigos não foram cadastrados, e o Edital não esclarece. Só o
autor do 140/2025 responde.

**H-2 — A mobilidade entre perfis (item 11) precisa de adjacência entre polos.** *"Na ausência de
aderência de perfil, será considerado o polo adjacente mais próximo indicado pelo candidato"* — uma
relação entre polos e uma declaração do candidato que hoje não existem. Se a mobilidade for executada
no sistema, ela precisa da dimensão polo (AX-5/AX-6) **e** de um grafo de proximidade. Não há
evidência de que se pretenda executá-la.

**H-3 — A cota de heteroidentificação tem população por código, e a declaração é do certame.**
Item 8.2: *"serão convocados […] até 3 (três) candidatos por código de inscrição"*. É o exemplo
puro do §8 do briefing — regra declarada uma vez, executada particionada por código. Não há hoje
onde declará-la, então não é possível dizer se o sistema a duplicaria. Vira achado no dia em que a
regra tiver lugar.

---

## Divergências de conteúdo que NÃO demonstram problema de arquitetura

1. **Remuneração R$ 1.600,00 na prévia contra R$ 1.100,00 no item 13.4.** Valor divergente, idêntico
   nos nove blocos. É cadastro — a granularidade errada (AX-7/matriz) é achado, o valor não.
2. **Requisito TADS com texto embaralhado na seção 4.** Resíduo de colagem da tabela de três
   colunas. Entra no AX-2 como evidência de que há duas fontes; sozinho, é erro de digitação.
3. **ANEXO XI ausente da lista.** Dos onze anexos, dez foram cadastrados. Fidelidade do teste.
4. **Datas deslocadas de 2025 para 2026** e *"Resultado Final […] 16/12/2026, às 16h"* contra
   *"após as 16 h"*. Adaptação deliberada do teste.
5. **Sete dos dezesseis códigos ausentes.** Fidelidade do teste; ver Lacunas.
6. **22 páginas contra 27.** Não é achado em nenhuma direção: a prévia tem 9 dos 16 códigos e não
   tem oito seções normativas. Com 16 códigos e as seções presentes, o documento passaria de 27 —
   mas "menos páginas" nunca foi objetivo, e o §12 do briefing é explícito.
7. **"Realização: 19/11/2026, às 00h" na Etapa.** O evento do cronograma é de data única sem hora
   declarada; imprimir "00h" é literal e não afirma norma errada. Editorial.

---

## Lacunas de cobertura

Com 9 dos 16 códigos, e sem modalidades cadastradas, **não foi possível verificar**:

| Hipótese | O que faltou | O que a cobriria |
|---|---|---|
| Divergência entre as 64 modalidades e 64 regras normativas (AX-7) | nenhuma modalidade cadastrada | cadastrar AC/PPIQ/PcD/PTT em ≥3 Perfis e comparar `foundation`, `percentage` e `version` |
| Amplificação das 5 autodeclarações condicionadas (AX-7) | nenhum documento de modalidade cadastrado | cadastrar o ANEXO V para PPIQ em 3 Perfis e contar registros e chaves |
| Função plural em `LP05`–`LP11` (H-1) | os 7 códigos não entraram | cadastrar `LP05` e comparar `duties` com `LP01` |
| O terceiro perfil de formação de Letras | idem | cadastrar `LP05`, que tem o requisito com AEE ausente e pós exigida |
| Colisão de polo além de Afonso Cláudio | idem | `LP05`–`LP11` cobrem 7 municípios novos; nenhum repete |
| Comportamento da Tabela 1 com 16 linhas | idem | a tabela já é ambígua com 2 linhas iguais; com 16 o efeito é de leitura |
| Retificação real sobre `n` cópias | nada foi publicado nem retificado | publicar e retificar `duties` — mede o custo do AX-1 e do achado de 15/09 no canal real |
| Quadro de vagas por modalidade | o 140/2025 é cadastro de reserva com 0 vagas | é o `027`, e este Edital não o exercita |

**Os sete códigos ausentes são todos de Letras (`LP05`–`LP11`)**, e são justamente os que carregam
o terceiro perfil de formação e a função composta. O teste cobriu 2 dos 4 perfis de formação e
1 das 2 grafias de função.

---

## Cobertura de caminho e cobertura de cardinalidade

O §15 do briefing pede que isto seja dito explicitamente, e o achado de 15/09 já formulou a frase:
**cobertura de cenário mede caminho, não escala.** Esta auditoria acrescenta uma segunda
constatação: **cobertura de cardinalidade também não é uma coisa só.** Os achados aqui se repartem
em três eixos independentes, e um cenário que cresce num deles continua cego nos outros dois:

| Eixo | Some com | Aparece com | Achados |
|---|---|---|---|
| **número de códigos** (`n`) | `n = 1` | `n ≥ 3`, grave em `n ≥ 16` | AX-1, AX-2, AX-7, AX-11 |
| **número de cursos / agrupamentos** (`K`) | `K = 1`, em qualquer `n` | `K ≥ 2` | AX-4, AX-5 |
| **cobertura de norma** | nunca some | qualquer Edital real completo | AX-3, AX-9, AX-10, AX-12 |

O cenário 1 de 13/09 (1 perfil, 1 curso, 1 documento, 1 marco) era cego nos três. O teste do
140/2025 abriu o primeiro eixo e **tocou** o terceiro. **O segundo eixo continua sem cobertura**:
os dois cursos existem no Edital real, mas como o sistema não tem a dimensão, o teste não pôde
sequer tentar declará-la — e por isso o AX-4 e o AX-5 só apareceram na leitura comparada, nunca na
tela.

---

## Próximos experimentos

Na ordem de poder discriminatório por custo. Nenhum exige código novo.

1. **Cadastrar `LP05` e comparar com `LP01`, campo a campo.** Custo: uma tela. Confirma ou refuta
   H-1 (função composta), fecha o terceiro perfil de formação, e mede a taxa de divergência de
   digitação num décimo bloco — a amostra atual é de 2 erros em 9 e merece um ponto a mais.
2. ~~**Cadastrar as quatro modalidades em três Perfis.**~~ **FEITO — ver E-1.** Resultado:
   24 objetos, divergência publicada, zero conferências.
3. ~~**Cadastrar o ANEXO V como documento condicionado a PPIQ.**~~ **FEITO — ver E-2.** Resultado:
   o caminho natural é aceito e alcança 1 de 3 Perfis (AX-14); o caminho correto custa 80 registros
   nos 16 códigos; e as submodalidades de PPIQ não existem (AX-15).
4. **Publicar o 149/2026 e retificar uma vírgula em `duties`.** Custo: um fluxo de Retificação.
   Mede, no canal real, quantos cartões a tela apresenta e se ela oferece alguma forma de conferir
   que as nove alterações são iguais. É a prova do §7 do briefing, e o achado de 15/09 a deixou
   como previsão.
5. **Tentar declarar as duas fichas de avaliação como duas Etapas.** Custo: dois formulários.
   Confirma o AX-4 por demonstração: as duas Etapas aparecerão aplicáveis a todos os nove Perfis, e
   o documento dirá que o candidato de Letras faz as duas.
6. **Escrever, numa seção textual, uma remissão a "ANEXO XII" que não existe, e publicar.**
   Custo: um campo. Confirma o AX-12: se a publicação passar, não há integridade referencial.
7. **Retificar o `title` para "EDITAL 999/1999 – …" e gerar a prévia.** Custo: um campo. Confirma o
   AX-8 de forma inequívoca e mostra que o número estrutural perde para o texto livre.

---

## Como isto se relaciona com o que já estava escrito

| Achado | Relação |
|---|---|
| AX-1 | mesmo mecanismo do [achado de 15/09](achado-atribuicoes-repetidas-por-polo.md), **objeto novo e divergência medida** |
| AX-2 | **novo**; vizinho de P-13 de [`achados-editais-externos.md`](achados-editais-externos.md) |
| AX-3 | **novo**; consequência estrutural do escopo da `006` |
| AX-4 | **novo**; vizinho de P-7 |
| AX-5 | **evidência adicional de P-5**, ampliando o eixo ausente de "polo" para "curso" |
| AX-6 | **corrige uma premissa** do achado de 15/09; reforça P-5 |
| AX-7 | **novo**, e **conflita parcialmente** com *"Cotas DEVEM ser definidas por Perfil"* — o conflito é sobre o que é Perfil, não sobre a regra |
| AX-8 | **novo** |
| AX-9 | **novo**; mesmo padrão de [`achado-objeto-normativo-sem-forma.md`](achado-objeto-normativo-sem-forma.md), visto do lado oposto |
| AX-10 | **novo** quanto à fusão; **evidência adicional** para "a condição sobre a pessoa" |
| AX-11 | **consequência** do achado de 15/09 |
| AX-12 | **já coberto em parte** por [`achado-anexo-sem-destinatario.md`](achado-anexo-sem-destinatario.md); a face nova é a remissão sem destino |
| AX-13 | **já coberto e corrigido** em `c0403a9` |
| AX-14 | **novo**, e não derivável do achado de 15/09 — aquele mede repetição, este mede ausência silenciosa |
| AX-15 | **evidência adicional** para a *reversão hierárquica* de `achados-editais-externos.md`, ampliada a documentos, convocação e heteroidentificação |
| AX-16 | **novo**, e só encontrável pela tela; mesma família de "o que não for reenviado some" |
| AX-17 | **refina o AX-14** — desloca a causa primária da autoria para a publicação |

Nada aqui propõe solução. O que esta rodada acrescenta ao registro de ontem é que **a amplificação
não é de prosa**: ela alcança a regra que ordena candidatos, o fato que a alimenta e o fundamento
legal da cota — e que existe um segundo eixo, o do curso, em que o sistema erra na direção
contrária, colapsando duas normas numa só.
