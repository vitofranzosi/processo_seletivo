# Estudo exploratório — esforço de autoria, reaproveitamento e fidelidade documental

**Data:** 2026-09-21 · **Fuso:** -03 (America/Sao_Paulo) · **Branch:** `claude/edital-registration-ux-study-1291e7`
**Commit base:** `396e75c` · **Diário operacional:** [doc/diario-estudo-esforco-2026-09-21.md](diario-estudo-esforco-2026-09-21.md)
**Ambiente:** execução nativa, PostgreSQL local, banco exclusivo `ps_ux_edital` (`make preparar` → **33 de 33** tabelas append-only protegidas), `runserver` na porta 8043 conectando como a role de runtime.
**Regra do estudo:** todo o cadastro foi feito pela interface web. Nenhum dado entrou por shell, fixture, Admin ou API. O código só foi consultado **depois** de cada comportamento observado.

> **O que este estudo é, e o que não é.** Os cinco Editais são **reais e já encerrados**, e servem
> como **amostra normativa e de complexidade** — não como cenário operacional. Carga retroativa de
> Editais encerrados não é caminho suportado ([decisão de 25/09](decisao-sem-carga-retroativa.md)),
> e para publicá-los foi preciso falsear a data de encerramento das inscrições. O que decorre só
> disso vem marcado como **artefato do método**.
>
> **Medido × estimado.** As interações foram contadas no percurso em **dois** Editais (78/2026 e
> 140/2025). Nos outros três, os números são estimados por custo unitário; o que se afirma sobre
> eles vem do documento publicado, conferido. Interação não é tempo nem taxa de erro: nenhuma
> sessão foi cronometrada com um operador real.
>
> **Complemento, não substituto.** A [auditoria pós-038](auditoria-de-convergencia-pos-038-2026-09-20.md)
> declarou não ter percorrido a composição desde o zero nem uma família multipolo real. Este
> estudo cobre essas duas lacunas — e só elas: não avalia o Processo vivo, avaliação, recurso,
> convocação, matrícula, Retificação nem o portal do candidato.

---

## 1. Sumário executivo

Cadastrei, **pela interface web e só por ela**, os **cinco** Editais da amostra — da criação do
Processo até o PDF publicado, com `Submeter` → `Homologar` → troca de identidade → `Publicar` em
todos. O produto é sólido: a composição em nove passos é bem escrita, a tela de Revisão consolida
impedimentos com link para o campo, o rascunho local é detectado e oferecido de volta quando não
chega ao servidor, o documento gerado tem timbre, numeração, legendas de tabela, lista de
documentos em a)–o) e verificação por SHA-256. A segregação de funções na publicação funciona e se
explica na própria tela. Nada disso é pouco.

Os gargalos, com a integridade normativa antes da eficiência:

1. **Um defeito de uma linha tornava "Cadastro Reserva limitado" inalcançável pela interface** — e
   o PDF publicado passava a declarar o **oposto** do que o Edital diz. Corrigido à parte, no #159.
2. **Documento obrigatório sob condição não tem como ser declarado.** O campo é booleano e o
   recorte só existe por par *(Perfil, Modalidade)*. No 140/2025, **nove documentos obrigatórios
   saíram como `(facultativo)`** — entre eles o laudo médico do candidato PcD.
3. **O reuso copia a prosa normativa inteira e avisa sobre outra coisa.** No 140/2025 vieram 10.900
   caracteres do Edital 14/2026 — com a função e o curso do outro certame — enquanto o banner nomeia
   "datas, vagas e prazos". É também por aí que a cláusula antiga de sorteio atravessaria para a
   oferta nova, que a D-G3 manda declarar fonte pública externa.
4. **O que o Edital declara uma vez, o sistema pede por Perfil.** No 140/2025, 16 Perfis × 4
   Modalidades custaram **~530 interações numa única etapa**, ~80% sem informação nova. O PDF
   herda a repetição: **34 tabelas em 27 páginas**.
5. **Não existe reaproveitamento dentro de um Edital** — nenhum duplicar, aplicar-a-todos ou edição
   em lote, confirmado no código. E como o reuso entre Editais exige origem publicada, **a primeira
   oferta de cada família é sempre composta do zero**.
6. **Citações legais não transcritas passam sem que nada perceba.** Em dois Editais, **nenhum** dos
   sete atos normativos citados no original chegou ao documento — a LGPD entre eles. Não foi o
   sistema que os removeu: fui eu, operador, que não os transcrevi; o sistema nunca conheceu a
   fonte e não tem como notar a falta. Com conferência fato a fato, o último Edital chegou a 11 de 13.
7. **A estrutura documental é fixa.** Oito seções de primeiro nível do 140/2025 viraram parágrafos
   em caixa alta dentro de outras seções.

## 2. Editais analisados

| Edital | Objeto | Perfis / códigos | Eventos | Modalidades | Seleção |
|---|---|---:|---:|---:|---|
| **78/2026** | Vagas remanescentes — Libras Iniciante A1 (presencial) | 2 turmas | 11 | nenhuma | sorteio eletrônico |
| **140/2025** | Cadastro de reserva de Tutores Presenciais (UAB) | 16 (LP01–LP11, TADS11–TADS15) | 13 | 4 (AC, PPIQ, PcD, PTT) | prova de títulos + verificação étnico-racial |
| **28/2026** | Pós-graduação Informática na Educação EaD | 7 polos | 18 | 3 (AC, PPI, PcD) | sorteio + verificação de autodeclaração |
| **149/2024** | mesmo curso, edição anterior (retificado) | 5 polos | 17 | 3 | sorteio |
| **14/2026** | Orientadores de TFC — Gestão EPT (UAB) | 7 (TFC 01–07) | 13 | 4 | análise de títulos + entrevista |

**Os cinco foram percorridos até a publicação.** O 78/2026 e o 140/2025 foram cadastrados do
zero e a partir de reuso, respectivamente; o 28/2026 foi cadastrado por "Partir de um Edital
anterior" sobre o 149/2024 já publicado, e o 140/2025 sobre o 14/2026. Identificadores das
publicações: `0b00691f` (78/2026), `7575ff02` (149/2024), `d4bf0826` (28/2026), `493ad59e`
(14/2026), `6066fb52` (140/2025).

---

## 3. Jornada operacional observada (Edital 78/2026)

```
Identificar-se (Elaborador + Gestor)
  └─ nada na tela diz que são precisos dois papéis
Criar Processo Seletivo  ......................  5 campos, 2 objetos
  └─ o Edital não nomeia nenhum "Processo": duas strings inventadas
1 Identificação  ..............................  1 campo
2 Perfis de Vaga  .............................  2 × 9 campos  ← BLOQUEIO DURO
3 Cronograma  .................................  11 × 1 clique + ~37 campos
4 Etapas de Avaliação  ........................  6 campos
5 Classificação  ..............................  9 + 2 × 8 campos
6 Inscrição  ..................................  7 × 1 clique + ~16 campos
7 Anexos  .....................................  pulado (PDFs teriam de ser recortados fora)
8 Conteúdo  ...................................  7 textos livres
9 Revisão  ....................................  3 IMPEDE + 11 AVISO
  └─ volta ao 4 (rótulos), ao 5 (método do sorteio), ao 3 (data no passado)
Prévia (PDF, 8 páginas)
Submeter  →  trocar de identidade  →  Homologar  →  Publicar
PDF publicado (8 páginas, com SHA-256)
```

---

## 4. Métricas de esforço

Duas colunas são **medidas** contando cada interação no percurso: 78/2026 (o menor) e 140/2025
(o maior). As três do meio foram cadastradas e publicadas, mas as interações não foram contadas na
hora; os números marcados com `~` são derivados dos custos unitários medidos — Perfil sem
modalidade = 1 clique + 9 campos; Perfil com 4 Modalidades = 6 cliques + ~30 campos; Evento =
1 clique + 3–5 campos; Documento = 1 clique + 2–3 campos; marco = 1 clique + 8 a 12 campos.

| Métrica | 78/2026 *(medido)* | 140/2025 *(medido)* | 28/2026 | 14/2026 | 149/2024 |
|---|---:|---:|---:|---:|---:|
| Perfis / Modalidades | 2 / 0 | **16 / 64** | 7 / 21 | 7 / 28 | 5 / 15 |
| Objetos criados | **25** | **118** | ~50 | ~45 | ~42 |
| Campos preenchidos | **~116** | **~730** | ~320 | ~350 | ~260 |
| Cliques em "Acrescentar …" | **23** | **~95** | ~75 | ~70 | ~60 |
| Campos redigitados sem nova informação | ~22 | **~430** | ~120 | ~150 | ~90 |
| Impedimentos / avisos na Revisão | 3 / 11 | **1 / 54** | — | — | — |
| Páginas do PDF original | 11 | 27 | 23 | 17 | 24 |
| Páginas do PDF gerado | 8 | 27 | 16 | 13 | 17 |
| Tabelas no PDF gerado | 4 | **34** | 16 | 16 | 12 |
| Atos normativos citados no original / presentes no gerado | 3 / **0** | 13 / 11 | 7 / **0** | 3 / 1 | 7 / **0** |

**Onde o custo se concentra.** Perfis de Vaga e Classificação juntos respondem por mais de metade
dos campos nos cinco Editais. No 140/2025 a etapa de Perfis sozinha custou **~530 interações**:
9 cliques para criar Perfis, 36 para criar Modalidades, 128 campos de Perfil, 272 de Modalidade,
64 escolhas de radio e `<select>`, 64 linhas de quadro. É exatamente onde a repetição é induzida
pelo sistema, não pelo documento.

**O documento gerado é mais curto que o original em quatro dos cinco casos** — e a causa não é
concisão: **nenhum Anexo foi enviado** (o navegador desta sessão não envia arquivo; ver §14). O
140/2025 empata em 27 páginas *apesar* de sair sem os onze anexos, porque a repetição por Perfil
consome a diferença.

## 5. Principais atritos, com evidência

### 5.1 "Cadastro Reserva limitado" é inalcançável — impasse fechado *(Classe A, alto impacto)*

O §6.10 do Edital 78/2026 publica: *"Para cada código de vaga, haverá a análise dos documentos de
até 30 (trinta) suplentes"*. Tentei declarar isso. Os dois caminhos estão fechados:

- **limite preenchido** → o cliente cancela o envio:
  `"Cadastro Reserva inexistente não admite limite. Apague o valor ou mude o tipo."`
- **limite vazio** → o servidor recusa:
  `"Cadastro Reserva limitado exige limite não negativo."`

Verificado em tela: `form.checkValidity() === false` nos dois Perfis, com
`validationMessage` idêntico.

A causa está em `backend/processo_seletivo/interface/static/interface/validacao.js`:

```js
function campo(linha, sufixo) {
  return linha.querySelector('[name$="-' + sufixo + '"]');   // falta :checked
}
var tipo = texto(campo(linha, "reserveType")) || "NONE";
```

`querySelector` devolve o **primeiro** rádio do grupo — o `NONE` —, e `texto()` lê o `.value` dele.
`tipo` é **sempre** `"NONE"`, qualquer que seja a escolha. Confirmado no console:

```
queryselectorRetorna: {value: "NONE", checked: false}
oQueDeveriaSer:        "LIMITED"
```

O mesmo defeito desliga o ramo oposto: escolher LIMITED e **esquecer** o limite passa pelo cliente
sem aviso. A validação criada para "poupar uma ida ao servidor" hoje impede a ida e não avisa
quando deveria.

**Saída que sobrou ao operador:** declarar "ilimitado". O PDF publicado passou a dizer
`Cadastro reserva: ilimitado` — o oposto do Edital.

### 5.2 Edital encerrado não publica — artefato do método, não achado

```
IMPEDE O período de inscrições encerrou em 03/09/2026 às 23:59. Publicado assim, o Edital
       não receberá inscrição alguma — corrija a data do Evento na etapa Cronograma antes
       de publicar.
```

O comportamento é o correto. Os cinco Editais já tinham corrido, e carga retroativa não é caminho
suportado ([decisão de 25/09](decisao-sem-carga-retroativa.md)). Para chegar ao PDF, falseei a data
de encerramento das inscrições — no 140/2025 ela saiu impressa no documento. Isso é custo do método.

O que sobrevive à decisão, porque vale para qualquer reuso — e todo reuso parte de uma oferta
passada: as datas herdadas estão sempre vencidas, e a etapa Cronograma abre com um paredão de
avisos (25 no 140/2025; §5.12).

### 5.3 O reuso herda a cláusula de sorteio que a D-G3 manda substituir *(Classe B)*

O §6.2 do 78/2026 e o §8.2 do 28/2026 declaram semente **gerada e publicada pelo próprio
sistema**, sem fonte externa. O vocabulário da tela de Classificação não comporta isso — e não
deve: a D-G3 decidiu que, **prospectivamente**, o Cefor declara fonte pública externa. A
incompatibilidade com os Editais antigos é, portanto, artefato do método; para publicá-los declarei
Loteria Federal, e o PDF saiu se contradizendo (§9.A).

O que permanece é de reuso. A cláusula antiga mora em **texto livre**, e o reuso copia o texto livre
inteiro sem marcar nada (diário, Caso E, seção E2 — medido no 140/2025). Uma oferta nova feita a partir do
28/2026 traria a cláusula junto, e só a regra estruturada do sorteio a contradiria — no documento
publicado. A D-G3 já apontava o reuso como o caso que mais facilmente escaparia; o estudo mostra por
onde.

### 5.4 Campo obrigatório que não se anuncia, e impedimento com caminho interno *(Classe A/B)*

```
IMPEDE A Etapa decisória deve publicar os rótulos do resultado em
       /stages/id=3338c19f-7b61-4f99-bd4c-9fef0490721c/rotuloFavoravel
```

UUID e nome de campo em inglês, numa mensagem dirigida ao operador. E os dois campos que ela cobra
— "Rótulo do resultado favorável/desfavorável" — **não têm `*` nem `required`**, enquanto os campos
opcionais do mesmo cartão trazem "(opcional)" no rótulo. Pela convenção do próprio cartão, eles
parecem opcionais.

### 5.5 Seletor de Evento ambíguo, e dois rótulos para a mesma coisa *(Classe A)*

Em **Etapas de Avaliação**, o seletor de Evento rotula as opções como `Tipo · data`. No Edital
78/2026 isso produz **duas opções literalmente idênticas, duas vezes**:

```
Publicação · 04/09/2026 00:00     ← "Publicação da situação de inscrição"
Publicação · 04/09/2026 00:00     ← "Link da gravação do Sorteio Eletrônico"
Resultado · 14/09/2026 00:00      ← "Resultado dos recursos"
Resultado · 14/09/2026 00:00      ← "Publicação do Resultado Final"
```

A `Descrição` — único campo que as distingue — não entra no rótulo. Na etapa **Inscrição**, o mesmo
seletor usa `Tipo · data — Descrição` e não é ambíguo. Dois seletores da mesma coisa, dois
critérios, e o ambíguo é justamente o que amarra Etapa a Evento.

### 5.6 Divulgação progressiva que não cumpre o que promete *(Classe A/B)*

O cartão do marco anuncia: *"A resposta governa o que este cartão pergunta em seguida."* Escolhido
**Por sorteio**, continuam visíveis e **obrigatórios**:

- **Casas decimais \*** e **Arredondamento \*** — com a ajuda "Aplicado uma vez, sobre a pontuação
  combinada", ao lado do texto do próprio sistema dizendo *"não há pontuação a combinar"*.
- **Alvo**, que segue visível mesmo com a regra de corte definida como "Quantas vagas o quadro
  publicar no recorte".

O operador inventa valores para conceitos que o Edital não tem e que o sistema declara inaplicáveis.

### 5.7 O quadro de vagas mente antes de salvar *(Classe A)*

No Edital 140/2025, acabei de digitar as modalidades **AC, PPIQ, PcD, PTT** e o quadro logo abaixo
mostrava quatro linhas todas chamadas **"Modalidade nova"** — indistinguíveis. Só depois de
`Salvar rascunho` os rótulos ficam corretos (`Ampla Concorrência (AC)`, `Pessoas com Deficiência
(PcD)`, …). Quem preenche as quantidades antes de salvar preenche às cegas, e trocar dois números
entre listas de concorrência é erro normativo.

### 5.8 Bloco condicional que não some *(Classe A, baixo impacto)*

Removida a última Modalidade de um Perfil, o bloco **"Quadro de vagas"** permanece na tela com o
texto *"Este Perfil declara lista reservada…"* — que deixou de ser verdade. Os campos ficam
`display:none`; o título e a explicação, não.

### 5.9 Documento obrigatório sob condição não tem forma *(Classe C, alto impacto)*

O item 5.5 do Edital 140/2025 condiciona sete documentos à modalidade de concorrência e dois a
atributos do candidato:

| Condição do Edital | O que o sistema oferece |
|---|---|
| "quem se inscrever como Pessoa com Deficiência" (2 documentos) | `modalityId` — **por par (Perfil, Modalidade)**: 64 opções |
| "quem se inscrever como Preto, Pardo, Indígena ou Quilombola" (3) | idem |
| "quem se inscrever como Pessoa Transgênero e Travesti" (1) | idem |
| "candidato autodeclarado quilombola" | **nada** — Quilombola é submodalidade de PPIQ |
| "candidatos do sexo masculino maiores de 17/18 anos" | **nada** |
| "servidores do Ifes" | **nada** |

Não existe "todos os PcD". Dizer com fidelidade o que o Edital diz em cinco frases custa
**7 × 16 = 112 linhas de documento**. O que o operador faz é deixar "Todas as modalidades" e
escrever a condição na instrução — e aí o campo `required`, que é booleano, não tem resposta
certa: marcado, exige de todo mundo; desmarcado, o gerador publica **`(facultativo)`**.

No 140/2025 publicado, **nove documentos obrigatórios saem marcados como facultativos** — o laudo
médico do candidato PcD entre eles. Um documento sem o qual o candidato perde a reserva legal é
publicado como dispensável. **Não há escolha correta na tela.**

### 5.10 O campo dependente não se limpa quando a regra muda *(Classe A, médio impacto)*

Dois casos idênticos, em telas diferentes:

- **Classificação.** Troquei a regra de corte de "Uma quantidade fixa" para "Este marco não corta".
  O campo **Alvo continuou com `10`** — número herdado de outro Edital.
- **Etapas de Avaliação.** Troquei "Com pontuação" por "Com decisão, sem nota". A **Pontuação
  máxima continuou `100`**, e o rascunho foi aceito sem aviso.

O valor órfão não aparece no documento porque o gerador não o lê. Mas ele fica no formulário, e
quem revisar o cartão lê uma nota máxima numa etapa que não pontua.

### 5.11 O rótulo da Modalidade fica velho até salvar *(Classe A, médio impacto)*

Renomeadas as Modalidades de `G1/G2/G3` para `AC/PPIQ/PcD` na etapa de Perfis, o `<select>` do
Quadro de vagas **logo abaixo, no mesmo formulário**, continua oferecendo os rótulos antigos. O
operador escolhe o recorte da vaga por um nome que já não existe. Depois de salvar, a lista se
corrige. É especialmente perigoso no reuso, porque os rótulos antigos são os **de outro certame**.

### 5.12 A Revisão ordena por objeto, não por severidade *(Classe B, médio impacto)*

No 140/2025 a Revisão apresentou **54 AVISO e 1 IMPEDE**. O único item que impede a publicação fica
soterrado. E 45 dos 54 avisos são a mesma frase repetida por Perfil (16 + 16 + 9) ou por Evento
(13). Antes disso, ao abrir a etapa Cronograma logo após o reuso, foram **25 avisos de uma vez** —
12 de "data já passou" e 13 de "é de 2026, e o Edital é de 2025" —, nenhum deles sobre conteúdo.

A regra do ano merece nota à parte: ela ancora no **ano do Edital**, não no período do certame. No
140/2025 (Edital de 2025 com cronograma de 2025) ela não disparou nenhuma vez depois de corrigidas
as datas; no reuso, disparou **treze vezes seguidas** dizendo a mesma coisa. A regra é útil; a
âncora é que produz o ruído.

---

## 6. Redundâncias

### 6.1 Repetição que já existe no Edital

O Quadro 2 do Edital 28/2026 repete "Ampla Concorrência 28 / PcD 2 / PPI 10 / Total 40" para cada
um dos 7 polos. É repetição do documento, e o sistema apenas a acompanha.

### 6.2 Repetição **criada pelo sistema** — é o que importa

| Informação | Vezes no Edital | Vezes no sistema |
|---|---:|---:|
| Modalidades de concorrência e seu fundamento normativo (§4.3 do 140/2025) | **1** | 16 (uma por Perfil) = 64 linhas × 5 campos |
| Percentuais 25% PPI / 5% PcD (§4.2 do 28/2026) | **1** | 7 (uma por polo) |
| Regra do sorteio (§6 do 78/2026) | **1** | 2 marcos, um por Turma |
| Critérios de desempate (§6.3.2 do 140/2025) | **1** | 16 marcos × 3 critérios |
| Requisitos gerais (§3 do 140/2025, nove itens) | **1** | 16 Perfis |
| Carga horária, remuneração e atribuições do tutor (§2 do 140/2025) | **1** | 16 Perfis |
| Tipo *e* Descrição de cada Evento (Anexo I traz **um** rótulo por linha) | 1 rótulo | 2 campos obrigatórios |

Medido no 140/2025 já cadastrado: entre um Perfil e o seguinte mudam **2 de ~33 campos** — Código e
Localidade. Onze dos dezesseis compartilham até a denominação. Os requisitos são o caso extremo: o
Anexo III original traz **três** blocos para os onze códigos de Letras (LP01–LP03, LP04, LP05–LP11)
e o sistema pede o bloco inteiro dezesseis vezes; **sete das oito linhas** de cada bloco são
idênticas em todos eles. Total: **~430 campos sem informação nova** numa etapa de ~530
interações — quatro em cada cinco.

### 6.3 O que o sistema já acerta

- **Etapas de Avaliação valem para todos os Perfis** — sem repetição.
- **Documentos exigidos têm escopo "Todos os Perfis"** — sem repetição *por Perfil*. O recorte por
  Modalidade, porém, só existe por par *(Perfil, Modalidade)*, e aí a repetição volta: 16 linhas
  para dizer "todos os PcD" (§5.9).
- **Período de inscrições vem do Evento** — *"nada é digitado duas vezes"*, diz a própria tela.
- **Método do sorteio comum ao Edital** — declarado uma vez, herdado pelos marcos.
- **"Obrigatório" já vem marcado** nos documentos.

O padrão é claro: onde existe escopo de Edital, não há repetição. A repetição mora onde o objeto é
por Perfil.

### 6.4 Não existe reaproveitamento dentro do Edital — confirmado no código

Varredura por `duplicar|clonar|copiar|em lote|aplicar a todos|replicar` em
`backend/processo_seletivo/`: as ocorrências de "em lote" são de avaliações, distribuição e
consolidação. **Nenhuma na composição.** As rotas de fragmento
(`fragmentos/perfil`, `.../modalidade`, `.../marco`, `fragmentos/evento`, …) só criam linhas
**vazias**. Não há capacidade escondida que a interface deixe de expor.

---

## 7. Arquitetura de informação

**O que funciona.** A trilha de nove passos com estado por passo, a tela de Revisão consolidando
IMPEDE/AVISO com link para o campo, o "O que fazer agora" no painel do Edital, o "Quem atuou" da
segregação de funções, e o texto explicativo que justifica *por que* o marco é do Perfil e a Etapa
é do Edital — tudo isso o operador entende.

**Onde diverge do modelo mental.**

1. **Processo × Edital.** Quatro dos cinco Editais da amostra são Edital único e **não nomeiam
   nenhum Processo Seletivo**. A criação exige inventar duas strings ("Identificação institucional"
   e "Título" do Processo) que não existem no documento-fonte, e que acabam repetindo o título do
   Edital.

2. **"Perfil de Vaga" colide com o vocabulário do domínio.** O Quadro 2 do Edital 78/2026 tem uma
   coluna chamada **"Perfil da Vaga"** cujo conteúdo é "Público externo"; o Anexo III do 140/2025
   tem uma coluna **"PERFIL"** que traz a formação exigida. Em nenhum dos dois "Perfil" significa o
   que o sistema chama de Perfil — a oportunidade inteira. O termo é do domínio, mas com outro
   referente.

3. **Campos de vínculo de trabalho numa vaga de aluno.** "Remuneração" e "Atribuições" (*"O que a
   pessoa fará"*) ficam vazios nos três Editais de curso. O cartão de Perfil foi claramente
   modelado sobre os Editais de tutor/orientador e reutilizado para os de curso.

4. **A numeração das seções muda entre a tela e o documento.** A tela Conteúdo enumera
   **12** seções (1. APRESENTAÇÃO … 12. DISPOSIÇÕES FINAIS). O PDF traz a apresentação **sem
   número** e vai de "1. DISPOSIÇÕES PRELIMINARES" a "10. DISPOSIÇÕES FINAIS". Quem revisar por
   número não encontra a seção.

5. **Ajuda invisível.** No Cronograma, "Vazio para evento pontual" e "Sala, endereço, canal de
   transmissão ou página" estão em `<span class="oculto">` — só leitor de tela os recebe. E o
   Cronograma é a única etapa **sem** painel "Como preencher estes campos".

---

## 8. Escalabilidade operacional

Custo por Perfil, medido no 140/2025: **5 cliques + ~33 campos** (com 4 Modalidades, quadro e
marco). A curva é **estritamente linear** — não há mecanismo algum que a dobre.

| Perfis | Cliques em "Acrescentar" | Campos | Campos sem informação nova |
|---:|---:|---:|---:|
| 1 | 5 | 33 | 0 |
| 5 | 25 | 165 | ~125 |
| 16 *(140/2025, medido)* | **45** | **~530** | **~430** |
| 50 *(hipótese multicampi)* | 145 | ~1.650 | ~1.400 |

No 140/2025, **oitenta por cento dos campos da etapa de Perfis não carregam informação nova**:
sete das oito linhas de requisito são idênticas nos dezesseis Perfis; carga horária e remuneração
são idênticas nos dezesseis; as quatro Modalidades, com percentual e fundamento, são idênticas nos
dezesseis. O Edital original expressa isso com **três blocos de requisito para onze códigos** e
**dois parágrafos** para as modalidades.

Agravantes observados, agora em escala:

- **"Acrescentar …" sempre anexa ao fim e empurra o botão para baixo.** Em viewport real (~800px),
  cada linha nova exige reencontrar o rodapé. Não há inserir no meio, nem arrastar, nem colar
  tabela. Com dezesseis Perfis o botão "Acrescentar Perfil" fica a dezenas de milhares de pixels do
  topo.
- **Reordenar é `↑`/`↓`, um passo por clique.** Mover um Evento da 11ª para a 2ª posição custa
  nove cliques.
- **Os AVISOs escalam junto, e mais rápido.** No 78/2026 (2 Perfis, 11 Eventos) foram 11 avisos; no
  140/2025 (16 Perfis, 13 Eventos), **54** — três famílias que emitem *um aviso por Perfil*. O
  único IMPEDE fica soterrado.
- **O campo mais caro é um `<select multiple>`.** "Etapas que entram na ordem" existe uma vez por
  marco — dezesseis vezes no 140/2025 — e é o único controle do fluxo que exige conhecer a
  convenção do sistema operacional: clique simples **reinicia** a seleção, `shift+seta` não
  estende, e no macOS só `cmd+clique` acrescenta.

**O teto prático.** Um certame multicampi do Ifes (22 campi) com três funções e quatro modalidades
daria 66 Perfis e 264 Modalidades: da ordem de **2.200 campos** numa única etapa do assistente,
dos quais ~1.900 sem informação nova. Não é um limite do banco; é um limite da interface.

---

## 9. Edital original × PDF gerado (78/2026, 8 páginas)

**Como comparei.** Em duas passagens: o **texto** dos dois PDFs (`pdftotext -layout`), para conteúdo
e ordem; e as **páginas renderizadas** a 110 e 300 dpi (`pdftoppm`), para layout — porque o texto
extraído inventa quebras de coluna e me fez, na primeira leitura, afirmar um defeito que não existe
(ver §9.C). A completude foi conferida fato a fato, não por impressão de leitura.

O gerador é bom: timbre MEC/Ifes/Cefor, numeração, rodapé "Página N de 8", legendas ("Tabela 1 —
Perfis de vaga"), documentos em lista a)–g) igual ao original, seções sem conteúdo desaparecem em
vez de saírem vazias, e o documento publicado traz **verificação por SHA-256 em toda página** e
bloco de **Autoridade Signatária**.

### A. Fidelidade semântica — três problemas

1. **`Cadastro reserva: ilimitado`** para as duas Turmas, contra o "até 30 suplentes por código de
   vaga" do §6.10. Regra invertida.

2. **O documento se contradiz sobre o sorteio.** As seções 5.1 e 5.2 publicam
   *"Fonte: Loteria Federal · Ocorrência: Concurso 5900 · Semente: os dígitos dos cinco prêmios da
   extração"*; a seção 7, transcrita do §6.2 do Edital, publica *"o software usado pelo Cefor…
   observar o campo 'Semente utilizada' ao fim da página do sorteio"*. **Duas normas incompatíveis
   no mesmo ato.** A primeira não existe no documento original. *Artefato do método* quanto à
   origem (Edital antigo, anterior à D-G3); o mecanismo — estrutura e prosa dizendo coisas
   diferentes sem que nada acuse — é o mesmo do §5.3.

3. **Horas inventadas viram norma.** "05/08/2026, **às 00h**" em 9 dos 11 eventos. O Anexo I
   publica só a data; o `datetime-local` obrigatório produziu a hora, e o gerador a imprime como se
   tivesse sido declarada.

### B. Completude — conferência fato a fato

Conferi **33 fatos normativos verificáveis** do Edital original contra o texto do PDF publicado
(quantidades, prazos, valores, endereços, fundamentos legais, assinatura). **24 chegaram, 9 não.**
E a separação entre os dois tipos de perda é o que importa:

**Perdidos por causa do sistema — 4**

| Perdido | Onde estava no original | Por quê |
|---|---|---|
| **Total de 61 vagas** | §4.1 e linha "Total de Vagas" do Quadro 2 | a Tabela 1 não tem linha de total; a soma fica com o leitor |
| **Nome de quem assina** | o nome próprio da diretora, no fecho | a Autoridade Signatária é catálogo de **cargos**; não há campo para a pessoa |
| **Portaria de nomeação** | "Portaria nº 797, de 08 de abril de 2022" | idem |
| **Local e data de expedição** | "Vitória-ES, 05 de agosto de 2026" | o gerador não emite |

**Perdidos por transcrição minha, sem que nada avisasse — 5**

As cinco citações legais do §1.1 — **Leis nº 10.098/2000, 10.436/2002 e 13.146/2015; Decretos nº
5.626/2005 e 9.656/2018** — não estão no documento gerado porque **eu não as transcrevi** ao
escrever a seção APRESENTAÇÃO. É erro de operador, não defeito de produto.

Mas o achado é justamente esse: **nada no fluxo percebeu.** As sete seções de texto livre não têm
conferência contra a fonte, não há checklist, e a Revisão não tem como saber que um parágrafo
normativo inteiro sumiu — o sistema não conhece o documento de origem. Num Edital transcrito à mão
por uma pessoa cansada, **perder o fundamento legal do curso é um erro silencioso e plausível**, e
ele sai publicado e imutável.

- **Anexo III (Termo de Consentimento LGPD)** é citado no §5.14 e segue citado no documento gerado,
  sem existir como anexo — mas isto **não é perda do sistema**: o anexo também não está no PDF
  original que recebi. Vale como observação sobre a etapa Anexos, que aceitaria o arquivo e não
  cobra a citação pendente.

### C. Estrutura documental

- **Ordem de leitura invertida.** O original apresenta as vagas (§4) **antes** da inscrição (§5);
  o gerado põe DA INSCRIÇÃO (3) e DOCUMENTOS (4) **antes** de PERFIS DE VAGA (5). O leitor conhece
  as regras de candidatura antes de saber o que está sendo ofertado.
- **Três seções sem lugar.** Matriz curricular caiu em "Disposições preliminares" (semanticamente
  errado); matrícula e certificado foram empilhados dentro de "Disposições finais", com subtítulos
  em caixa alta improvisados pelo operador no corpo do texto.
- **A Tabela 4 (Cronograma) está quebrada.** Conferido nas páginas renderizadas a 300 dpi, não só
  no texto extraído:
  - A coluna **"Nº" é estreita demais** e o cabeçalho sai **cortado** — o "Nº" fica ilegível,
    mutilado pela borda da célula, nas duas páginas em que a tabela aparece.
  - Os números **10 e 11 quebram em duas linhas**, `1`/`0` e `1`/`1`.
  - A coluna **Início quebra o ano**: cada data ocupa três linhas — `05/08/2` / `026, às` / `00h`.
    O mesmo em Término: `11/09/20` / `26, às` / `23h59`.
  - **As linhas 7 e 8 saem fundidas**: não há filete horizontal entre "Resultado Preliminar" e
    "Período de recurso do resultado preliminar" — dois Eventos distintos do cronograma aparecem
    dentro do mesmo bloco. Abaixo, a linha 9 tem filete normal. É o defeito mais grave da tabela,
    porque compromete a leitura do prazo recursal.

### D. Economia da informação

**O caso mais limpo é o quadro de vagas.** O original resolve as vagas em **uma tabela de quatro
colunas e quatro linhas**, ocupando cerca de um sexto de página:

| Código de vaga | Perfil da Vaga | Quantidade de vagas | Dias e horários das aulas |
|---|---|---:|---|
| Turma 1 | Público externo | 21 | Segundas e quintas-feiras, das 09h às 11h |
| Turma 2 | Público externo | 40 | Segundas e quintas-feiras, das 13h às 15h |
| **Total de Vagas** | | **61** | |

O documento gerado gasta **duas páginas** com a mesma informação, repartida em Tabela 1 (resumo) +
§5.1 com prosa + Tabela 2 (quadro da Turma 1) + frase de convocação + bloco de marcos + §5.2 +
Tabela 3 + frase de convocação + bloco de marcos. E, no caminho:

- **perde** a linha de total (61);
- **dissolve** a coluna "Dias e horários" numa frase solta sob cada Perfil;
- **dissolve** a coluna "Perfil da Vaga" ("Público externo") dentro do nome concatenado
  `Turma 1 — Público externo — Turma 1 (manhã)`;
- **acrescenta** "Cadastro reserva: ilimitado" — que está errado (§5.1).

Uma tabela compacta e autossuficiente virou duas páginas com menos informação.

O bloco do método do sorteio sai **duas vezes**, uma por Turma, com doze linhas cada — e **cada
cópia começa dizendo "Método: comum a este Edital"**. O gerador sabe que é comum e imprime duas
vezes. Junto com isso: os cinco Requisitos saem duas vezes (no original aparecem uma vez, no §3) e
a frase de convocação sai duas vezes.

Com 2 Perfis isso custa cerca de uma página. Com os 7 polos do 28/2026 seriam sete cópias; com os
16 códigos do 140/2025, dezesseis.

Detalhe menor de mesma origem: o Código aparece duplicado no rótulo —
`Turma 1 — Público externo — Turma 1 (manhã)` — porque o operador desambiguou a Denominação sem
saber que o gerador concatena Código + Denominação.

---

## 9-bis. A comparação nos cinco Editais

Com o 140/2025 publicado, a comparação deixa de ser um caso e passa a ser uma série. Cada linha
abaixo foi conferida no PDF publicado.

### A fidelidade semântica erra sempre no mesmo lugar: onde o modelo é binário

| Edital | Regra do Edital | O que o documento publicou |
|---|---|---|
| 78/2026 | "análise de documentos de até **30** suplentes" | "Cadastro reserva: **ilimitado**" |
| 140/2025 | "quem se inscrever como PcD **deverá** apresentar laudo médico" | "Laudo Médico de Especialista (PcD) … **(facultativo)**" |

Os dois têm a mesma forma: **o campo admite menos estados do que a norma**, e o gerador imprime
o estado escolhido como se fosse declarado. Nenhum deles é erro de digitação.

Duas outras divergências saíram nos PDFs e **não entram nesta conta**, porque são artefato do
método: "Fonte: Loteria Federal" no 78/2026 e no 28/2026 (a norma antiga de sorteio, anterior à
D-G3) e as inscrições encerrando em 22/10/2026 no 140/2025 (a data falseada para publicar um
Edital já encerrado).

### A completude erra sempre no mesmo lugar: no texto livre

Conferência mecânica — os atos normativos citados em cada original, procurados no gerado:

| Edital | No original | No gerado | Perdidos |
|---|---:|---:|---|
| 149/2024 | 7 | **0** | Leis 13.709 (LGPD, 7 citações), 14.126, 13.146, 12.764, 7.853; Decretos 3.298, 5.296 |
| 28/2026 | 7 | **0** | os mesmos |
| 78/2026 | 3 | **0** | Leis 10.098, 10.436; Decreto 5.626 |
| 14/2026 | 3 | 1 | Leis 11.273, 11.502 |
| 140/2025 | 13 | **11** | Lei 14.126 e uma outra |

Todos moram nas seções de texto livre. A diferença entre `0 de 7` e `11 de 13` é a diferença entre
transcrever de memória e transcrever com conferência — e **nada no produto sabe qual das duas
aconteceu**. A validação não conhece o documento de origem; a Revisão não tem como perceber que um
parágrafo normativo sumiu; a Publicação congela o que houver.

Perdas de mesma natureza, presentes nos cinco: **nome e portaria da autoridade** (o gerador publica
o cargo, não a pessoa), **local e data de assinatura**, e **as tabelas que não têm objeto** — a de
ordem de convocação em 50 posições do 140/2025 é a maior delas. Pior que perdê-la: o texto que a
cita continua no documento, de modo que **a publicação remete a um item que ela não contém**.

### Os defeitos de renderização são os mesmos, e agora estão caracterizados

Conferidos em páginas renderizadas a 150–300 dpi, não no texto extraído:

1. **Cabeçalho de coluna cortado.** `Nº` não cabe na coluna e o `º` transborda a borda. Aparece na
   Tabela 4 do 78/2026 e na Tabela 34 do 140/2025.
2. **Filete horizontal ausente entre linhas consecutivas.** No 78/2026 são as linhas 7 e 8; no
   140/2025, as 6 e 7. Dois eventos distintos viram um bloco. *Corrigido em 25/09: a causa não é
   "células iguais".* Nos dois casos a primeira das duas é a linha que a quebra de página levou
   para a página seguinte; o gerador perdia o início dela na quebra, e a linha ficava fora da
   grade — com ela, o fio de baixo.
3. **Quebra no meio do número.** `26/11/2` / `025, às` / `00h`; e os números de linha `10` a `13`
   quebram em `1`/`0`, `1`/`1`…
4. **Hora inventada impressa como norma.** "às 00h" em 11 dos 13 eventos do 140/2025 e em 9 dos 11
   do 78/2026. Nenhum dos dois originais publica hora.

Os quatro são do gerador de tabelas, e os três primeiros só aparecem quando a tabela cresce — ou
seja, **exatamente nos Editais grandes**.

### A estrutura documental aperta conforme o Edital tem mais seções

| Edital | Seções numeradas no original | Seções no gerado | Seções sem lugar |
|---|---:|---:|---|
| 78/2026 | 12 | 8 | matriz curricular, matrícula, certificado |
| 140/2025 | 15 | 10 | FUNÇÕES, VAGAS, CLASSIFICAÇÃO FINAL, CONVOCAÇÃO, MOBILIDADE ENTRE PERFIS, CURSO DE FORMAÇÃO, VINCULAÇÃO À UAB, PRAZO DE VALIDADE |

O que não tem lugar vira **parágrafo em caixa alta dentro de outra seção**, na mesma fonte e no
mesmo corpo do texto. Oito títulos de primeiro nível do 140/2025 deixaram de ser títulos.

---

## 10. Rastreamento origem → interface → PDF

**Caso 1 — a regra invertida**

```
§6.10: "análise dos documentos de até 30 suplentes para cada código de vaga"
   ↓
Perfis: rádio "Cadastro reserva limitado" + limite 30
   ↓
validacao.js lê sempre reserveType = NONE  →  setCustomValidity + reportValidity  →  envio cancelado
   ↓  (limite vazio → servidor recusa: "exige limite não negativo")
operador declara "ilimitado" para conseguir prosseguir
   ↓
PDF, Tabela 1: "Cadastro reserva: ilimitado"    ← o oposto do Edital
```

**Caso 2 — a norma que o sistema acrescentou** *(artefato do método: norma anterior à D-G3)*

```
§6.2: semente gerada pelo software, publicada ao fim da página do sorteio
   ↓
Classificação: vocabulário fechado — Algoritmo único, Fonte ∈ {demonstração, Loteria Federal}
   ↓
IMPEDE "ordena por sorteio e não publica método" bloqueia a publicação
   ↓
operador declara Loteria Federal + 8 campos ausentes do Edital
   ↓
PDF §5.1/§5.2: "Fonte: Loteria Federal…"   ✗ contradiz o §7, transcrito do Edital
```

**Caso 3 — a hora que ninguém declarou**

```
Anexo I: "Publicação do Edital — 05/08/2026"   (sem hora)
   ↓
Cronograma: Início é datetime-local obrigatório  →  operador digita 00:00
   ↓
PDF, Tabela 4: "05/08/2026, às 00h"    ← hora publicada como se fosse norma
```

**Caso 4 — a repetição documental**

```
§6: a regra do sorteio, declarada uma vez
   ↓
Classificação: um marco por Perfil, sem "aplicar aos demais"
   ↓
PDF: o bloco do método sai 2×, cada um rotulado "comum a este Edital"
```

**Caso 5 — o documento obrigatório que sai facultativo** *(140/2025)*

```
§5.5.h: "os candidatos que se inscreverem como PcD DEVERÃO apresentar laudo médico"
   ↓
Inscrição: "Modalidade" lista 64 pares (Perfil, Modalidade); não existe "todos os PcD"
   ↓  (a alternativa fiel são 16 linhas de documento, uma por Perfil)
operador deixa "Todas as modalidades" e desmarca "Obrigatório", pondo a condição na instrução
   ↓
PDF §4.j: "Laudo Médico de Especialista (PcD) — Apenas para quem concorre na modalidade
           PcD … (facultativo)"          ← obrigatório sob condição publicado como dispensável
```

**Caso 6 — a data falseada que fica impressa** *(140/2025; artefato do método — ver §5.2)*

```
Anexo II: inscrições de 07/10/2025 a 22/10/2025          (certame encerrado)
   ↓
Revisão: IMPEDE "o período de inscrições encerrou … o Edital não receberá inscrição alguma"
   ↓
não há caminho de registro retroativo → operador move o fim para 22/10/2026
   ↓
PDF, Tabela 34, linha 2: "07/10/2025, às 00h → 22/10/2026, às 23h59"
   ← inscrições que fecham um ano depois de abrir e um mês depois do resultado final
```

**Caso 7 — a prosa de outro certame** *(140/2025)*

```
"Partir de um Edital anterior" (origem: 14/2026 publicado)
   ↓
copia as 7 seções de texto livre — 10.900 caracteres — sem marcar campo algum
   ↓
banner avisa sobre "datas, vagas e prazos"; não menciona o texto
   ↓
se o operador confiar no banner: o PDF publica "Professor Formador/Conteudista" e
"CURSO FORMAÇÃO PARA ORIENTAÇÃO DE TRABALHOS ACADÊMICOS FINAIS NA EAD" sob a capa do 140/2025
```

**Caso 8 — a tabela citada que não existe** *(140/2025)*

```
§10.5: tabela de ordem de convocação, 50 posições, com submodalidades de PPIQ
   ↓
não há objeto para ordem de convocação nem para submodalidade
   ↓
operador escreve, em texto livre, "respeitando a ordem apresentada na tabela do item 10.5"
   ↓
PDF: a frase é publicada; o documento gerado não tem item 10.5 algum
```

---

## 11. Oportunidades, por impacto

### Alto impacto

| # | Achado | Classe |
|---|---|---|
| A1 | `validacao.js` lê o rádio sem `:checked` — "Cadastro Reserva limitado" é inalcançável e a informação some do ato publicado. **Corrigido no #159** | A |
| A2 | Não há reuso dentro do Edital (duplicar Perfil / aplicar Modalidades a todos / edição em lote); o único reuso exige origem **publicada** | A + C |
| A4 | O reuso herda a cláusula de sorteio em texto livre, e nada pede a substituição que a D-G3 exige — estrutura e prosa publicariam normas opostas | B |
| A5 | 12 seções fixas não acomodam matriz curricular, matrícula e certificado | C + D |
| A6 | Bloco do método do sorteio repetido por Perfil no documento, rotulado "comum a este Edital" | D |
| A7 | Documento exigido não sabe dizer "obrigatório para quem concorre como PcD": `required` é booleano e o recorte só existe por par *(Perfil, Modalidade)* — 9 documentos obrigatórios publicados como `(facultativo)` | C |
| A8 | O reuso copia as seções de texto livre inteiras e o aviso nomeia "datas, vagas e prazos" — 10.900 caracteres de prosa de outro certame vieram sem sinalização | B + C |
| A9 | Citações legais não transcritas pelo operador passam sem que nada perceba — 0 de 7 em dois Editais, LGPD entre elas | B + C |
| A10 | Não há objeto para a tabela de ordem de convocação (50 posições, item 10.5 do 140/2025), nem para submodalidade de PPIQ (Pretos/Pardos, Indígenas, Quilombolas) | C |

### Médio impacto

| # | Achado | Classe |
|---|---|---|
| M1 | Seletor de Evento em Etapas usa `Tipo · data` e produz opções idênticas; Inscrição usa rótulo melhor | A |
| M2 | "Rótulo do resultado favorável/desfavorável" impedem a submissão sem `*` nem `required` | A |
| M3 | Impedimento exibe caminho interno com UUID (`/stages/id=…/rotuloFavoravel`) | B |
| M4 | Quadro de vagas mostra "Modalidade nova" até salvar — risco de trocar quantidades entre listas | A |
| M5 | Casas decimais / Arredondamento / Alvo continuam obrigatórios num marco por sorteio | A + B |
| M6 | Total de vagas do Edital ausente no documento gerado | D |
| M7 | Assinatura publica o cargo, não o nome e a portaria; sem local e data de expedição | C + D |
| M8 | Onze AVISOs idênticos de data passada afogam os IMPEDE na Revisão | B |
| M9 | Tipo **e** Descrição obrigatórios por Evento, quando o Anexo I traz um rótulo só; Tipo é texto livre, sem vocabulário | B + C |
| M10 | Ordem de leitura: inscrição e documentos antes dos Perfis de Vaga | D |
| M11 | Campo dependente não se limpa ao mudar a regra: Alvo `10` num marco que não corta; Pontuação máxima `100` numa Etapa decisória | A |
| M12 | Rótulo da Modalidade fica velho no `<select>` do quadro até salvar — no reuso, são os rótulos de outro certame | A |
| M13 | "Fundamento da homologação" é obrigatório e não se anuncia; o envio falha em silêncio | A |
| M14 | A regra do ano ancora no ano do Edital, não no período do certame: 13 avisos idênticos de uma vez logo após o reuso | B |
| M15 | O quadro de vagas de um cadastro de reserva sai degenerado — uma linha "Ampla concorrência \| 0" ao lado de uma tabela que publica 5%, 30% e 25% | C + D |
| M16 | `<select multiple>` de "Etapas que entram na ordem": clique simples reinicia a seleção, sem aviso e sem alternativa na tela | A |

### Baixo impacto

| # | Achado | Classe |
|---|---|---|
| B1 | Tabela 4: cabeçalho "Nº" cortado, números 10/11 e o ano das datas quebrados em duas e três linhas | D |
| B2 | Bloco "Quadro de vagas" permanece visível após remover a última Modalidade | A |
| B3 | Numeração das seções difere entre a tela Conteúdo (12) e o PDF (10 + preâmbulo) | A + D |
| B4 | `Descrição` do Perfil é `<input>` de uma linha e trunca; `Atribuições` é `<textarea>` | A |
| B5 | Cronograma sem painel "Como preencher"; ajudas em `<span class="oculto">` | B |
| B6 | Etapa Anexos sem "Salvar rascunho", ao contrário das demais | A |
| B7 | Papéis listados pela string técnica da capacidade; nada diz que são precisos dois | B |
| B8 | "Cancelar Processo — IRREVERSÍVEL — está impedido", sem dizer por quê | B |
| B9 | Descrição do Edital não é copiada pelo "Partir de um Edital anterior" | A |
| B10 | O botão "Acrescentar …" fica no rodapé da lista e desce a cada inserção; com 16 Perfis, reencontrá-lo é parte do custo | A |
| B11 | O reuso traz `vagas imediatas = 1` e a linha AC do quadro da oferta anterior, sem questionar | A |

---

## 12. Quick wins

1. **Acrescentar `:checked` ao seletor de `reserveType` em `validacao.js`.** Feito no #159. Não
   foi uma linha: os testes do caso existiam e passavam, porque a fixture montava o grupo de rádios
   como um campo único. A correção levou junto a fixture e o shim de DOM.
2. **Usar `Tipo · data — Descrição` no seletor de Evento das Etapas** — o rótulo que a tela de
   Inscrição já usa. Elimina as opções idênticas.
3. **Marcar "Rótulo do resultado favorável/desfavorável" com `*`** quando a Etapa é decisória.
4. **Nomear o campo na mensagem de impedimento**, em vez do caminho com UUID.
5. **Esconder Casas decimais, Arredondamento e Alvo** quando não se aplicam — a divulgação
   progressiva já existe no cartão, só não alcança estes três.
6. **Colapsar os AVISOs de data passada** em uma linha ("11 Eventos com data já passada — ver").
7. **Consertar a Tabela 4 do documento**: alargar as colunas "Nº" e Início (hoje o cabeçalho sai
   cortado e cada data ocupa três linhas) e restaurar o filete entre as linhas 7 e 8, que hoje
   saem fundidas. Feito no #164: com duas colunas longas (Evento e Onde), a regra encolhia todas
   na mesma proporção; agora as curtas recebem o que pedem e as longas repartem o resto. O filete
   é o item 14. Documento já publicado não se regenera — vale para as próximas publicações.
8. **Ocultar o bloco "Quadro de vagas"** quando o Perfil não tem Modalidade.
9. **Copiar a Descrição** no "Partir de um Edital anterior". **Não é quick win**: a FR-007 da
   `023` diz que a identificação — número, ano, título **e descrição** — não deve ser copiada, e o
   `data-model` da `023` repete a decisão. Copiá-la é mudar o requisito — registrado aqui, não
   tomado.
10. **Imprimir o bloco do método do sorteio uma vez**, na seção do Edital, quando for o método
    comum — os marcos passam a remetê-lo. **Não é quick win**: a FR-465/466 da `032` e o contrato
    `marco-no-documento.md` exigem que a seção de cada marco de sorteio imprima o método que o
    governa. Remeter em vez de imprimir é mudar o requisito — registrado aqui, não tomado.
11. **Limpar o campo dependente quando a regra muda** — Alvo ao escolher "não corta", Pontuação
    máxima ao escolher "com decisão, sem nota".
12. **Marcar "Fundamento da homologação" com `*`**, como os demais obrigatórios.
13. **Ancorar a regra do ano no período do certame**, não no ano do Edital, e colapsar os avisos
    de ano divergente como os de data passada.
14. **Restaurar o filete entre linhas consecutivas com células iguais** no gerador de tabelas — o
    colapso atual funde dois eventos distintos num bloco só, no 78/2026 e no 140/2025. Feito no
    #164 — e a causa era outra: a linha levada à página seguinte pela quebra perdia o início e
    saía da grade (§9-bis, item 2).
15. **Nomear o que o reuso copiou** no banner: "…e **as sete seções de texto** são da oferta
    anterior", com link para a etapa Conteúdo. Uma frase.

Nenhum destes altera o domínio. *Conferido em 25/09, ao aplicá-los:* três deles contrariam
requisito escrito — o 9 (FR-007 da `023`), o 10 (FR-465/466 da `032`) e a âncora do 13 (FR-344) —
e o 5 esconderia campo que a publicação exige. Esses ficaram registrados, e não feitos.

---

## 13. Questões estruturais

Estas não se resolvem mudando um botão.

**E1 — Reaproveitamento dentro do Edital.** O produto tem reuso de Edital inteiro (023) e nenhum
reuso de parte. A operação real precisa de "duplicar Perfil", "aplicar estas Modalidades a todos os
Perfis" e "aplicar este marco aos demais". É a única mudança que muda a ordem de grandeza do
esforço em Editais multipolo — que são a maioria da amostra.

**E2 — Onde mora o que é comum a vários Perfis.** Modalidades, critérios de desempate, requisitos
gerais, carga horária e atribuições são declarados **uma vez** no Edital e hoje vivem **no Perfil**.
O padrão que o sistema já usa em três lugares (Etapas do Edital, Documentos com escopo "Todos os
Perfis", método do sorteio comum) resolve o caso. A pergunta aberta é quais destes podem migrar
sem violar a razão pela qual o marco é do Perfil.

Um dado para essa decisão: **na amostra, nenhum Perfil diverge dos irmãos** em Modalidades,
percentuais, carga horária ou remuneração — os 16 do 140/2025, os 7 polos do 28/2026, os 7 códigos
do 14/2026. Exceção por Perfil é plausível, mas não foi observada; o modelo atual, por Perfil, já a
admite, e o que falta para o caso comum é "aplicar a todos" (E1).

**E3 — Editais já encerrados: decidido, fora do produto.** Não haverá carga retroativa
([decisão de 25/09](decisao-sem-carga-retroativa.md)). Uma consequência merece ficar escrita: como o
reuso exige origem publicada, **a primeira oferta de cada família será sempre composta do zero** —
o custo de autoria da §8 é pago ao menos uma vez por família, e o reuso não o amortiza.

**E4 — Sorteio: decidido pela D-G3.** Os próximos Editais declaram fonte pública externa, e o
produto não acomoda a semente própria. O que resta é de reuso, e está no §5.3: a cláusula antiga
viaja em texto livre, e nada pede sua substituição.

**E5 — A forma do documento.** Doze seções fixas não comportam matriz curricular, matrícula e
certificado, que aparecem em Editais de curso. E a ordem de leitura (inscrição antes das vagas)
inverte a do documento original. Revisar o conjunto de seções é mexer em conteúdo normativo.

**E6 — Condição de exigência de documento.** O Edital diz "quem se inscrever como PcD deverá
apresentar"; o sistema tem um booleano `required` e um recorte por par *(Perfil, Modalidade)*.
Expressar as sete condições do 140/2025 com fidelidade custa 112 linhas; não expressá-las publica
nove documentos obrigatórios como facultativos. Falta ou um escopo por Modalidade que valha para
todos os Perfis, ou um estado "obrigatório sob condição" com a condição declarada. E duas condições
do Edital — sexo/idade para o serviço militar, vínculo de servidor para a declaração de chefia —
não são de modalidade nem de perfil: são do candidato, e não há onde declará-las.

São três casos, e não a mesma decisão que E2: **regra comum a todos os Perfis**, **regra comum com
exceção**, e **condição sobre o candidato**. O que a amostra sustenta é menos do que parece:

- o recorte "todos os PcD" cabe no **código** da Modalidade, que já existe e é igual nos 16 Perfis
  — 112 linhas viram 7 sem conceito novo;
- a condição sobre o candidato cabe num estado **"obrigatório sob condição"** com a condição em
  texto. Modelá-la como atributo exigiria **coletar sexo, idade e vínculo de todo candidato** para
  decidir se pede um papel — dado que o sistema não precisa por outro motivo;
- exceção por Perfil não apareceu em nenhum dos cinco Editais (E2).

Antes de desenhar, falta ver o que o candidato PcD de fato encontra no portal como exigido.

**E7 — Submodalidade e ordem de convocação.** O 140/2025 convoca por `PPIQ (Pretos/Pardos)`,
`PPIQ (Indígenas)` e `PPIQ (Quilombolas)`, com cascata de reversão entre elas (item 10.5.1), numa
tabela de **50 posições**. Modalidade de Concorrência é plana e não há objeto para a ordem de
convocação. O texto publicado remete ao item 10.5 — que o documento gerado não contém.

**E8 — Cadastro de reserva sem quantidade.** O sistema amarra convocação a quantidade publicada:
sem linha no quadro não há faixa, sem faixa não há convocação. Um Edital de cadastro de reserva não
publica quantidade alguma. O resultado é um documento que anuncia reservas de 5%, 30% e 25% ao lado
de um quadro com uma única linha valendo zero — e 32 avisos na Revisão dizendo exatamente isso, sem
que exista uma resposta certa a dar.

**E9 — O que o reuso não pode saber.** "Partir de um Edital anterior" acerta o que tem forma
(remapeia `scheduleEventId`, preenche o marco novo com o código e a denominação do Perfil) e erra o
que tem prosa (códigos e denominações de marco, seções de texto, quantidades de vaga). A pergunta
de produto é se o reuso deve **marcar** o que copiou como pendente de revisão, campo a campo, em
vez de avisar em bloco no topo da tela.

**E10 — Redação no sistema ou transcrição?** O estudo mediu um cenário de **transcrição**: um PDF
pronto, redigitado no sistema. É dele que vem a perda das citações legais (§9-bis). Se o Cefor
redigir o Edital no sistema, não existe fonte a que ser fiel, e o risco se desloca para a prosa
herdada no reuso (§5.3, A8). Se continuar redigindo no Word, a fidelidade à fonte é risco real, e
as saídas vão de anexar a fonte a uma conferência estruturada antes da publicação. É decisão de
processo do Cefor, e vem antes de qualquer spec sobre fidelidade.

**E11 — Ficha de avaliação sem forma.** O Anexo IV do 140/2025 e do 14/2026 é uma tabela de títulos
com pontos por item e teto por natureza. A Etapa de Avaliação só tem "Nota mínima", "Pontuação
máxima" e "Peso" — **não há representação para a tabela de pontuação**. Nos dois Editais de
prova de títulos ela teria de virar anexo em PDF ou texto livre, e o sistema não consegue conferir
a pontuação que ele mesmo vai publicar.

---

## 14. Lacunas que merecem investigação adicional

- **Não exercitei Retificação.** Todo Edital da amostra que é pós-graduação veio retificado. O custo
  de retificar — e se ele reabre os mesmos atritos — não foi medido. É hoje a maior lacuna.
- **Não enviei Anexo algum.** O navegador desta sessão não envia arquivo. O que o estudo sustenta é
  outra coisa: os onze Anexos do 140/2025 existem **dentro** do PDF-fonte e o sistema os quer como
  PDFs separados; a extração é trabalho manual que o fluxo não reconhece, e o documento publicado
  cita `ANEXO I` a `ANEXO XI` sem publicar nenhum.
- **Não medi tempo com operador humano.** Os tempos não foram estimados nesta revisão justamente
  por isso; as métricas da §4 contam interações, não minutos.
- **A economia do reuso entre ofertas sucessivas não está sustentada.** O percurso 149/2024 →
  28/2026 foi feito por reuso e a economia chegou a ser contada na sessão, mas o número não foi
  registrado com o método e não é reverificável pelos artefatos. Fica fora deste relatório até ser
  refeito — de preferência entre duas ofertas futuras da mesma família.
- **Não contei as interações dos três Editais do meio** (149/2024, 28/2026, 14/2026) na hora. Os
  números com `~` na §4 são derivados de custo unitário; os que não têm `~` foram conferidos no
  artefato publicado.
- **Não avaliei o portal do candidato** para os Editais cadastrados — se as ambiguidades do cadastro
  reaparecem para quem se inscreve.
- **O Anexo III (LGPD) do 78/2026 não está no PDF recebido.** Pode ser falha da amostra, não do
  Edital.

---

## 15. Recomendações

**Uma correção, já feita à parte:** o `:checked` de `validacao.js` (#159). Era o único achado que
fazia o ato publicado dizer o oposto da norma sem que o operador errasse nada.

**Três decisões, antes de qualquer spec.** Nenhuma é de engenharia:

1. **Redação no sistema ou transcrição** (§13/E10). Define se fidelidade à fonte é problema.
2. **Conteúdo comum e documento condicional, tomadas juntas** (§13/E2 e E6). Têm a mesma raiz — a
   granularidade em que a regra é declarada — mas não são a mesma decisão, e o desenho de uma
   limita o da outra. A evidência da amostra aponta para o menor desenho que cobre os casos (§13/E6).
3. **O conjunto de seções do documento** (§13/E5). É conteúdo normativo: 3 seções sem lugar no
   78/2026, **8** no 140/2025.

**Frentes com evidência para spec, em ordem de risco.** Não as escrevi.

| Ordem | Tema | Evidência |
|---|---|---|
| 1 | **Exigência documental condicional**, incluindo o que o portal pede e o que a análise confere | §5.9: nove obrigatórios publicados como `(facultativo)` |
| 2 | **Conteúdo comum aos Perfis e aplicação em lote** — duplicar, aplicar a todos, sem cópias que divirjam em silêncio | §6.2, §8: ~430 campos redigitados, ~80% da etapa; nenhuma capacidade no código |
| 3 | **Reuso com estado de revisão** — o que veio da oferta anterior fica marcado até alguém revisar, inclusive a cláusula de sorteio | §5.3, A8: 10.900 caracteres de outro certame sem sinal |
| 4 | **Estrutura e economia do documento gerado** — o comum impresso uma vez, total de vagas, autoridade com nome e ato, tabelas legíveis | §9-bis: 34 tabelas em 27 páginas; cabeçalho cortado, filete ausente |

Saíram desta lista, desde a primeira versão: **registro de Edital já executado** (decisão de 25/09)
e **o vocabulário do sorteio** (D-G3).

**Antes da frente 1, um complemento pequeno.** Não repetir os cinco cadastros. Compor com **datas
futuras**: uma oferta N e a N+1 por reuso; uma Retificação; candidatos em AC, PcD e PPIQ no portal;
anexos enviados de verdade. Só o item do portal condiciona a frente 1; o resto informa as outras.

---

## 16. O que o produto faz bem — e que só a escala revelou

Registrado à parte porque um relatório de atritos tende a esconder o que funciona.

- **O rascunho não enviado é detectado e devolvido.** Ao voltar a uma etapa depois de um envio que
  não completou, a tela anuncia *"Há preenchimento não enviado neste navegador de 22/09/2026,
  23:29:26. Ele não chegou ao servidor — o que está na tela é o que foi enviado por último"*, com
  **Restaurar o que eu havia digitado** e **Descartar**; e ao lado do botão de salvar aparece
  *"alterações ainda não enviadas"*. Numa etapa de 530 campos, isso é a diferença entre um
  contratempo e um dia perdido.
- **O marco novo nasce preenchido** com o código e a denominação do Perfil.
- **O reuso remapeia o que pode remapear**: as Etapas herdadas vieram apontando para os eventos
  novos do cronograma, na posição correspondente.
- **A remoção de linha preenchida pede confirmação** e diz quantos campos serão descartados.
- **A etapa Cronograma explica por que fica pendente**, no próprio cartão, e diz que o sistema não
  altera nem sugere datas.
- **A segregação de funções na publicação é por pessoa, e a tela explica**: *"Depois de homologar,
  você não poderá publicar esta revisão. Você a elaborou, e publicar exige que ao menos outra
  pessoa autorizada tenha participado."*
- **A lista de documentos exigidos sai em a)–o)**, com a mesma estrutura do original, e as frases
  derivadas de campo — reversão de vaga, prazo de recurso — são geradas corretamente.
- **O documento publicado carrega SHA-256 por página e bloco de Autoridade Signatária.**
