# O Edital declara as atividades uma vez; o sistema as guarda uma vez por polo

**Data:** 2026-09-15
**Origem:** teste de inclusão do **Edital 140/2025 — Cadastro de Reserva de Tutores Presenciais do
Cefor/Ifes** no sistema, conduzido pelo usuário, e comparação do PDF original com a prévia que o
sistema gerou (numerada `149/2026`). Os dois PDFs estão em `~/Downloads`, e não no repositório.
Nenhuma linha de código foi escrita.
**Natureza:** contradição com o Princípio II — a mesma que a `027` está fechando do lado do
**número** de vagas, aqui do lado do **texto** normativo.

> **Não vira escopo por estar escrito aqui.** Este documento mede o que acontece e enumera saídas.
> Qual delas se toma — e se se toma alguma — é decisão do usuário.

## O que o teste mediu

O 140/2025 abre 16 códigos de inscrição para a **mesma função**: `LP01` a `LP11` (Licenciatura em
Letras Português, onze polos) e `TADS11` a `TADS15` (Tecnologia em ADS, cinco polos). Cada código é
um polo — Afonso Cláudio, Aracruz, Castelo, Alegre, Baixo Guandu, Linhares, Pinheiros, Santa
Leopoldina, Vargem Alta, Vila Velha, Iúna. O teste cadastrou 9 dos 16.

| | Edital 140/2025 (o documento real) | Prévia gerada (9 dos 16 códigos) |
|---|---|---|
| Bloco de atividades de tutoria | **1 vez**, no ANEXO I, item 1 | **9 vezes**, íntegro |
| "Dados exigidos na inscrição" | 1 vez, no ANEXO IV | 9 vezes |
| Regime de trabalho / carga horária | 1 vez | 9 vezes |
| Páginas | 27, com 16 códigos | 22, com 9 |

Os Perfis ocupam as páginas 3 a 20 da prévia — **18 páginas para 9 Perfis, exatamente 2 cada**, e
4 páginas para todo o resto. Com os 16 códigos do Edital real o documento chegaria a **cerca de 36
páginas** para dizer o que o original diz em 27 — e a diferença inteira é texto repetido.

## O Edital declara em três níveis; o sistema tem um

| Nível no 140/2025 | O que carrega | Quantas vezes é dito | Onde o sistema guarda |
|---|---|---|---|
| **Função** — Tutor Presencial | atividades, regime de trabalho, remuneração | **1** (ANEXO I) | `PerfilVaga.duties`, `.workload`, `.compensation` |
| **Perfil** — a formação exigida | requisitos | **3** (`LP01`–`LP03`, `LP04`, `LP05`–`LP11`) | `PerfilVaga.requirements` |
| **Código de inscrição** — o polo | identidade para inscrever, classificar e ocupar | **16** | `PerfilVaga.code`, `.locality` |

Tudo isso mora em `PerfilVaga` (`editais/models/perfis.py:9`), e a identidade do objeto é o **código**
— `uq_perfil_edital_code`. Logo, os dois níveis de cima são copiados para acompanhar o de baixo: 16
cópias de um parágrafo que o Edital escreve uma vez.

E a unidade de baixo está certa. O código é o que a inscrição escolhe, o que a classificação ordena
e o que a ocupação apura; um Perfil por código não é o defeito. O defeito é o texto de cima não ter
onde morar.

## Não é incômodo de digitação — é a Retificação

`duties`, `workload` e `compensation` são classificados **retificáveis**
(`editais/domain/mutabilidade.py:216`), e a `FR-304` da `026` exige que campo retificável seja
alcançável pelo canal do ator. O catálogo da tela cumpre isso aplicando `CAMPOS_PERFIL`
*"a cada Perfil"* (`interface/retificacao.py:60`), com `("duties", "Atribuições", TEXTO_LONGO)` na
linha 80.

A consequência: **corrigir uma vírgula nas atribuições de um Edital publicado com 16 códigos é
redigitar o mesmo texto em 16 cartões**, e a Retificação nasce com 16 Alterações que precisam ser
iguais entre si — sem que nada no sistema verifique que são. A própria tela já registra o sintoma
na prosa dela: *"Num Edital extenso, conferir uma alteração feita no primeiro cartão custava rolar
seis mil pixels até o fim da página e outros seis mil de volta"* (`interface/templates/interface/retificar.html:233`).

O Princípio II não fala de conforto:

> *"Cada informação normativa estruturada DEVE possuir uma única fonte autoritativa. Vagas, perfis,
> cronogramas, cotas, **requisitos**, documentos, etapas, critérios, pesos, pontuações e regras de
> avaliação NÃO DEVEM existir como dados independentes e divergentes."*

Dezesseis cópias do mesmo parágrafo de atribuições são dezesseis dados independentes, e divergem no
dia em que uma Retificação alcançar quinze.

## Um defeito de documento cai junto, e é separável

A seção "Documentos exigidos para a inscrição" da prévia imprime **nove vezes** o cabeçalho
`Dos candidatos ao perfil Tutor Presencial:`, idênticos e indistinguíveis. `_titulo_do_grupo`
compõe a frase com `name` e só cai no `code` quando o nome falta
(`publicacoes/infrastructure/pdf.py:1802`) — e aqui os nove nomes são o mesmo. O candidato de
Aracruz não tem como saber qual bloco é o dele.

O docstring da função diz para que ela existe: *"Sem este cabeçalho, um laudo exigido só de uma
modalidade pareceria exigido de todo mundo"*. Com nomes repetidos, o cabeçalho volta a não
distinguir — que é o erro que ele foi escrito para evitar. **Isto se conserta sozinho**, incluindo o
código no título, em qualquer cenário e sem depender da decisão de fundo.

## A auditoria de 13/09 não podia ter visto isto

A [auditoria exploratória de UX](auditoria-exploratoria-ux-2026-09-13.md) não registra este achado
em lugar nenhum: nem nas 10 fricções, nem nas 13 lacunas conceituais, nem nos 9 itens de
"complexidade desnecessária", nem nas 34 linhas do backlog priorizado.

A razão está no §2 dela. O cenário 1 — o único montado à mão de ponta a ponta — foi *"1 perfil, 2
vagas, 1 Etapa pontuada classificatória, 1 documento, 1 marco"*. **A fricção é O(n) no número de
códigos** e não existe em `n = 1`: com um Perfil só, digitar as atribuições uma vez é o
comportamento correto. Ela só aparece quando o Edital é uma matriz de polos, e nenhum dos quatro
Editais do ambiente auditado é.

É o mesmo limite que aquela auditoria já declarou sobre si em "Sem cobertura", e vale registrar
como método: **cobertura de cenário mede caminho, não escala.**

## O que já está registrado e é vizinho

- **P-5, em [`achados-editais-externos.md:129`](achados-editais-externos.md:129)** — *"Não é o
  Edital, e nem sempre é o curso. […] a unidade é a **oferta localizada**, e a matriz é
  bidimensional."* Aquele achado olha o mesmo eixo pelo lado de **contar, ocupar e reverter** vaga
  por polo (evidência: 28/2026, 280 vagas em 7 polos, reversão dentro do polo). Este olha pelo lado
  de **redigir**. São a mesma estrutura ausente, vista de duas telas diferentes.
- **A `027`, em execução** — unifica a declaração da **quantidade**. Este achado é a declaração do
  **texto**, pelo mesmo Princípio II. Nenhum dos dois reescreve o que já foi publicado.
- **A lacuna conceitual "Perfil de Vaga"** (§5 da auditoria) toca o vocabulário — *"na amostra real
  a família dominante é curso, e o código de vaga é a turma"* — e não a multiplicidade.

Vale notar o que **não** aparece aqui: o achado P0 da `027` não morde neste Edital. O 140/2025 é
cadastro de reserva ilimitado com zero vagas imediatas, e um quadro vazio é a verdade sobre ele.

## Os caminhos, sem escolher nenhum

1. **Declaração compartilhada — a Função como objeto normativo do Edital.** Atividades, carga
   horária e remuneração passam a morar em um objeto que vários Perfis referenciam; o publicado
   deriva dele. Fecha os três custos de uma vez: digitação, tamanho do documento e Retificação em um
   endereço só. **É a saída cara e é a que obedece ao Princípio II**: objeto normativo novo, segmento
   novo na gramática de endereçamento, forma nova no snapshot e no catálogo de Retificação, e uma
   decisão sobre se o Perfil pode sobrescrever o que herdou. Não alcança Edital publicado — o
   acervo continua com o texto que publicou, como a `026` exige.
2. **"Copiar de outro Perfil" no assistente.** Barato, sem tocar o modelo. Resolve a **digitação** e
   nada mais: as cópias seguem independentes, o PDF segue com 16 blocos, a Retificação segue com 16
   cartões. Alívio, e não conserto — e um alívio que aumenta a chance de divergência, porque torna
   barato produzir cópias.
3. **Agrupar na renderização.** O PDF junta blocos de texto igual — *"Perfis LP01 a LP11 — Tutor
   Presencial"*. Encurta o documento e não toca a origem. Agrupar por igualdade de string é
   exatamente o tipo de inferência que a `R-006` da `025` recusou por escrito ao proibir identificar
   a ampla concorrência casando o nome: um espaço a mais em um dos dezesseis desfaz o grupo, sem
   avisar.
4. **O polo como dimensão própria** — a saída que o P-5 descreve. Perfil é curso + função +
   requisitos; a oferta localizada tem código, quadro de vagas e reversão próprios. É o conserto
   mais fundo, atende também o 28/2026, e é maior do que a pergunta que originou este registro.
5. **Deixar como está.** O sistema publica um Edital correto; o que ele produz é longo e caro de
   retificar. Quem confere a igualdade entre as dezesseis cópias é quem lê o documento.

Enquanto não houver decisão, o que é verdade: **um Edital de 16 polos exige 16 declarações do que a
norma declara uma vez, e o sistema não tem como saber que as dezesseis deveriam ser a mesma.**
