# Contrato: a redação 2 das frases geradas

Cada linha é uma **variante** que o compositor conhece hoje (R-008). "Hoje" é a redação 1, que continua
existindo para os atos publicados (R-004). A coluna "Equivalência" diz o que se preserva, ou o que é
novo e precisa de aprovação (SC-517). `«X»` é o nome declarado, impresso como está; `N (ext.)` é o
número com o extenso entre parênteses, pela tabela `POR_EXTENSO` e só quando ela o tem.

Toda variante tem um teste que prende a frase nova. A conferência por enunciado da entrega (FR-1396)
usa esta tabela.

## 1. Classificação (FR-1360, FR-1361)

| # | Variante | Hoje (redação 1) | Redação 2 | Equivalência |
|---|---|---|---|---|
| C1 | Separação por Perfil (marco de grupo) | "Os marcos abaixo se aplicam a cada um desses Perfis separadamente, sobre as inscrições do próprio Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado." | "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado." | alcance por Perfil preservado; "marcos" sai |
| C2 | Ordem por sorteio | "Ordem: por sorteio" | (o título da subseção, "Sorteio", e C4) | a forma da ordem continua dita |
| C3 | Ordem por pontuação | "Ordem: pela pontuação combinada das Etapas" | "A ordem de classificação segue a nota final." | idem |
| C4 | Habilitação: todas | "Habilitação: participam todas as inscrições submetidas" | "Participam do sorteio todas as inscrições enviadas." | "enviada" = submetida (a palavra do teto) |
| C5 | Habilitação por Etapa | "Habilitação: participam apenas as inscrições habilitadas na Etapa «X»" | "Participam do sorteio só as inscrições habilitadas na Etapa «X»." | condição preservada |
| C6 | Nota de uma Etapa, peso 1, sem normalização | "Combinação: soma ponderada da Etapa «X» (peso 1)" + "Normalização: nenhuma" | "A nota final é a pontuação obtida na Etapa «X»." | conta idêntica |
| C7 | Soma ponderada, duas ou mais Etapas | "Combinação: soma ponderada das Etapas «X» (peso a) e «Y» (peso b)" | "A nota final é a soma das pontuações nas Etapas «X» (peso a) e «Y» (peso b), cada uma multiplicada pelo seu peso." | mesma operação, dita |
| C7′ | Soma ponderada de uma Etapa com peso ≠ 1, ou com normalização | "Combinação: soma ponderada da Etapa «X» (peso a)" | "A nota final é a pontuação obtida na Etapa «X» (peso a), multiplicada pelo seu peso." | idem, no singular |
| C8 | Média ponderada | "Combinação: média ponderada das Etapas …" | "A nota final é a média ponderada das pontuações nas Etapas «X» (peso a) e «Y» (peso b)." Com uma Etapa só, a C6 | idem: a média ponderada de um valor é o próprio valor |
| C9 | Normalização pela soma dos pesos | "Normalização: pela soma dos pesos" | "Depois, o resultado é dividido pela soma dos pesos." | idem |
| C10 | Etapa decisória na lista do marco | "«Z» (não pontua)" | "A Etapa «Z» não entra na conta: ela não dá pontos." (no plural, "As Etapas … não entram na conta: elas não dão pontos.") | idem |
| C11 | Arredondamento, meio para cima | "Arredondamento: N casas decimais, meio para cima" | "A nota final é arredondada para N casas decimais; a partir da metade, arredonda-se para cima." | idem (L7) |
| C12 | Arredondamento, meio para par | "…, meio para par" | "A nota final é arredondada para N casas decimais; na metade exata, arredonda-se para o algarismo par mais próximo." | idem |
| C13 | Arredondamento por truncamento | "…, truncamento" | "A nota final é arredondada para N casas decimais, desprezando-se as demais." | idem |
| C14 | Escala 0 / 1 | "sem casas decimais" / "1 casa decimal" | "… para um número inteiro …" / "… para 1 casa decimal …" | idem |
| C15 | Sob sorteio | (067: não imprime arredondamento nem empate) | idem | inalterado |

## 2. Corte (a unidade indivisível da R-009)

| # | Variante | Hoje | Redação 2 | Equivalência |
|---|---|---|---|---|
| K1 | Alvo pelo quadro de vagas | "Corte: Progridem para «Y» os primeiros desta ordem, até o número de vagas ofertadas no recorte[, mais N (ext.) suplentes]." | "Passam para a Etapa «Y» os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista[, mais N (ext.) suplentes]." | "recorte" = Perfil × lista (`faixa.py`) |
| K2 | Alvo fixo | "Corte: Progridem para «Y» os N (ext.) primeiros desta ordem[, mais M (ext.) suplentes]." | "Passam para a Etapa «Y» os N (ext.) primeiros classificados[, mais M (ext.) suplentes]." | idem |
| K3 | Alvo fixo de 1, sem suplentes | "Progride para «Y» o 1 (um) primeiro desta ordem." | "Passa para a Etapa «Y» o 1 (um) primeiro classificado." | idem |
| K4 | Marco terminal (sem Etapa governada) | "Progridem os N (ext.) primeiros desta ordem…" | "Seguem no processo os N (ext.) primeiros classificados…" | idem: a frase não nomeia Etapa, como hoje |
| K5 | Empate admite excedente | "Empate no corte: Havendo empate na última posição, progridem todos os empatados, ainda que excedam essa quantidade." | "Se houver empate na última posição, passam todos os empatados, mesmo que ultrapassem esse número." | idem (L2) |
| K6 | Empate estrito (pontuação) | "Empate no corte: Havendo empate na última posição, essa quantidade não é excedida." | "Se houver empate na última posição, esse número não é ultrapassado." | idem |
| K7 | Suplentes, **sem cadastro de reserva em nenhum Perfil** | — | "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados." | **frase nova** (D-004): descreve a regra de convocação do sistema; aprovação no SC-517 |
| K8 | Suplentes **com** cadastro de reserva | — | (nada) | a relação com o cadastro é a DP-05 |
| K9 | Continuação admitida | "Continuação: Poderá haver chamada, nesta ordem, além dos que este corte publicar." | "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem." | **sem condição acrescentada** (achado 1 da amostra) |
| K10 | Continuação vedada | "Continuação: Não haverá chamada além dos que este corte publicar." | "Não serão chamados candidatos além desses." | idem |

## 3. Desempate

`«F»` é o rótulo do fato declarado. A frase de ausência concorda com o tipo: "a" para data, "o" para
número.

| # | Variante | Hoje | Redação 2 | Equivalência |
|---|---|---|---|---|
| T1 | Menor valor de fato DATA | "menor valor declarado em «F»" | "«f» mais antiga, informada na inscrição" (por exemplo, "data de nascimento mais antiga, informada na inscrição") | menor data = anterior. **Forma genérica sempre**: o sistema não deduz "idade" comparando o rótulo com "Data de nascimento" (D-006) |
| T2 | Maior valor de fato DATA | "maior valor declarado em «F»" | "«f» mais recente, informada na inscrição" | idem |
| T3 | Maior valor de fato INTEIRO | "maior valor declarado em «F»" | "maior número de «f», informado na inscrição" | idem (L5) |
| T4 | Menor valor de fato INTEIRO | "menor valor declarado em «F»" | "menor número de «f», informado na inscrição" | idem |
| T5 | Maior pontuação na Etapa | "maior pontuação na Etapa «X»" | "maior pontuação na Etapa «X»" | inalterado |
| T6 | Ausente: último no critério | "sem o valor, fica por último neste critério" | "quem não a/o informar fica em último lugar neste critério" (Etapa: "quem não a tiver") | idem |
| T7 | Ausente: critério não se aplica | "sem o valor, o critério não se aplica" | "para quem não a/o tiver, o critério não se aplica" | idem |
| T8 | Cabeçalho | "Critérios de desempate:" + "1º …" | "Critérios de desempate, nesta ordem:" + "1º …" | ordem preservada |

**Alcance das frases de desempate:** as mesmas valem para a página do ato de ordenação e para a
proposta de ordenação, que leem o mesmo vocabulário (FR-1364). O ato já publicado lê a redação 1
(FR-1397).

## 4. Recurso (FR-1363) — em "Como recorrer?"

| # | Variante | Hoje | Redação 2 | Equivalência |
|---|---|---|---|---|
| R1 | Admitido, marco com nome | "Recurso: Caberá recurso contra o resultado de “X”, no prazo de N (ext.) dias corridos, contados da divulgação desse resultado." | "Contra o resultado de “X”: no prazo de N (ext.) dias corridos, contados da divulgação desse resultado." | objeto e prazo preservados; nome entre aspas e **sem artigo** (decisão 001 da `067`); sem canal |
| R2 | Prazo de 1 dia | "… 1 (um) dia corrido …" | idem | idem |
| R3 | Vedado | "Não caberá recurso contra o resultado de “X”." | idem | inalterado |
| R4 | Sem nome (só prévia de rascunho) | "Caberá recurso no prazo de …, contados da divulgação do resultado." | "Cabe recurso no prazo de …, contados da divulgação do resultado." | idem |
| R5 | Silêncio | (nada) | (nada) | ausência não vira negativa |
| R6 | Grupos com prazos diferentes | — | "Para os Perfis «códigos» — contra o resultado de “X”: …" | alcance explícito |

## 5. Sorteio (FR-1376) — bloco destacado

| # | Variante | Hoje | Redação 2 |
|---|---|---|---|
| S1 | Abertura | (sem frase) | "A ordem será definida a partir do resultado de “«ocorrência»”, da fonte “«fonte»”, de «quando». Com os dados abaixo, qualquer pessoa pode refazer o sorteio e conferir o resultado." — a ocorrência e a fonte entre aspas e sem artigo, como o nome do marco (decisão 001 da `067`): "do Concurso 6010 da Loteria Federal" adivinharia o gênero de dois textos livres |
| S2 | Método comum | "Método: comum a este Edital" + "Algoritmo: «a»" | "Método: comum a este Edital; algoritmo «a»." |
| S3 | Método próprio | "Método: próprio deste marco" | "Método: próprio deste sorteio; algoritmo «a»." |
| S4 | Próprio divergente | "Método: próprio deste marco — diverge do comum deste Edital" | "Método: próprio deste sorteio, diferente do comum deste Edital; algoritmo «a»." |
| S5 | Derivação | "Derivação: «texto»" | "Qual concurso: «texto»" |
| S6 | Semente | "Semente: «texto»" | "Semente: o número usado no sorteio: «texto»" |
| S7 | Substituição | "Se faltar: «texto»" | "Se faltar: «texto»" |

Os sete campos continuam todos impressos (FR-465): fonte, ocorrência e quando, na abertura; algoritmo,
derivação, semente e substituição, nos pares.

## 6. Vagas, convocação, inscrição, matrícula

| # | Variante | Hoje | Redação 2 |
|---|---|---|---|
| V1 | Reversão por esgotamento | "Havendo ausência de candidatos aprovados na reserva de vagas, o quantitativo será destinado à respectiva ampla concorrência." | "Se não houver candidatos aprovados para as vagas reservadas de um código, essas vagas passam para a ampla concorrência do mesmo código." |
| V2 | Reversão por saldo | "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não preenchido será destinado à respectiva ampla concorrência." | "As vagas reservadas de um código que não forem preenchidas passam para a ampla concorrência do mesmo código." |
| V3 | Reversão com alcance parcial | (frase com os códigos à frente, `068`) | a mesma frase, com "de um código com vagas imediatas («códigos»)" |
| V4 | Convocação por publicação | "A convocação dos classificados será feita por publicação no endereço eletrônico do certame." | "A convocação dos classificados será feita por publicação." |
| V5 | Convocação individual | "A convocação dos classificados será feita por mensagem individual à pessoa convocada." | "A convocação será feita por mensagem individual à pessoa convocada." |
| V6 | Forma não declarada | "forma de convocação não declarada neste Edital" | idem (só em prévia) |
| V7 | Teto 1 | "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital." | "Cada candidato pode enviar apenas 1 (uma) inscrição neste Edital." |
| V8 | Teto N | "Cada candidato poderá ter no máximo N inscrições enviadas neste Edital." | "Cada candidato pode enviar no máximo N (ext.) inscrições neste Edital." |
| V9 | Período de inscrições (novo, gerado) | — | "Período de inscrições: de «início», a «fim» (Cronograma, nº «ordem»)." |
| V10 | Dados declarados (uma vez) | "Dados exigidos na inscrição" + "• «F» (data)" por Perfil | "Na inscrição, informe também:" + "• a «f»;" / "• o número de «f»." + "Esses dados são usados no desempate (item «N»)." quando algum critério os usa |
| V11 | Requerimento na inscrição | "O Requerimento de Matrícula será enviado no ato da inscrição." | "O Requerimento de Matrícula é enviado no ato da inscrição. Ao enviá-lo, o candidato declara:" |
| V12 | Requerimento na convocação | "O Requerimento de Matrícula será enviado quando o candidato for convocado." | "O Requerimento de Matrícula é enviado quando o candidato for convocado. Ao enviá-lo, o candidato declara:" |
| V13 | Lembrete em Documentos e Inscrição (novo) | — | "Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item «N»)." (só AT_ENROLLMENT) |

## 7. Etapas, documentos, atributos, fecho

| # | Variante | Hoje | Redação 2 |
|---|---|---|---|
| E1 | Etapa decisória | "Caráter: eliminatória / Resultado: «F» ou «D» / Realização: «a» a «b»" | "Etapa eliminatória: o resultado é “«F»” ou “«D»”. Será feita de «a», a «b»." — e "Cada inscrição recebe N (ext.) avaliação(ões)." quando declarado, como os pares da redação 1 |
| E2 | Etapa pontuada | "Caráter / Peso / Nota mínima / Pontuação máxima / Avaliações por inscrição / Realização" | "Etapa «classificatória[ e eliminatória]», com pontuação máxima de «m»[ e nota mínima de «n»] e peso «p». Cada inscrição recebe N (ext.) avaliação(ões). Será feita de «a», a «b»." — só o que está declarado |
| E3 | Evento de um instante | "Realização: «a»" | "Será feita em «a»." |
| D1 | Grupo: todos | "De todos os candidatos:" | idem |
| D2 | Grupo: Perfil | "Dos candidatos ao perfil «código — nome»:" | "Também, de quem concorre ao Perfil «código — nome»:" |
| D3 | Grupo: código de modalidade | "Dos candidatos concorrentes na modalidade «nome»:" | "Também, de quem concorre às vagas para «nome» («código»):" |
| D4 | Grupo: Perfil e modalidade | "Dos candidatos ao perfil «p» concorrentes na modalidade «m»:" | "Também, de quem concorre ao Perfil «p» nas vagas para «m»:" |
| D5 | Instrução do documento | "«Nome» — «Instrução»" (e " (facultativo)" no fim) | "«Nome» — «instrução com a inicial minúscula»" (sigla preservada); "«Nome» (facultativo) — «instrução»" |
| P1 | Atributos iguais em todos | (repetidos por Perfil) | "Em todos os Perfis: «nome» — «descrição»; carga horária de «c»; remuneração: «r»; «cadastro»." — só o que é igual |
| P2 | Cadastro de reserva | "não há" / "limitado em N" / "ilimitado" | "não há cadastro de reserva" / "cadastro de reserva de até N (ext.) classificados por Perfil" / "cadastro de reserva sem limite de classificados" |
| F1 | Integridade | "Verificação de integridade — este documento deriva integralmente da versão homologada identificada abaixo." | "Autenticidade — este documento corresponde integralmente à versão homologada do Edital identificada abaixo." |
| F2 | Fecho, autoridade, consolidação, anúncio | (de hoje) | inalterados; o anúncio preserva siglas (FR-1377) |

## 8. Rótulos gerados com "Marcos classificatórios" (FR-1366, FR-1399, D-007) — nas duas apresentações

| # | Onde | Hoje | Redação 2 | Equivalência |
|---|---|---|---|---|
| G1 | Título do bloco no Perfil | "Marcos classificatórios" / "Marcos classificatórios — «código»" | "Regras de classificação" / "Regras de classificação — «código»" | só o rótulo |
| G2 | Remissão no Perfil (068) | "Marcos classificatórios: os descritos no item N." | "Regras de classificação: as descritas no item N." | **o mesmo N e o mesmo destino** |
| G3 | Título da subseção comum (068) | "N.k Marcos classificatórios comuns aos Perfis «códigos»" | "N.k Regras de classificação comuns aos Perfis «códigos»" | o mesmo N.k |

O texto livre do Elaborador não passa por esta tabela: um "marcos classificatórios" escrito por ele sai
literal (FR-1395).

**A hora mantém dois dígitos** ("às 08h"), pela paridade com o portal decidida em `humano.instante`.

## 9. Na apresentação plana

Na plana, as regras do marco continuam no Perfil (D-003). As frases são as mesmas, dispostas assim, na
ordem da redação 1:

- o código e o nome do marco, em negrito;
- C3 a C14 (ou C4/C5 sob sorteio), em itens de lista;
- "Sorteio", em negrito, com S1 e os pares S2 a S7 — ou, se o método comum já saiu noutro item,
  "Método: o comum a este Edital, descrito no item N." (068, FR-1349);
- "Recurso", em negrito, com R1 a R4;
- a unidade do corte (K1 a K10), em itens de lista;
- "Critérios de desempate, nesta ordem:" e os critérios.

**Item de lista** (FR-1382, ED-16): o marcador na margem, e as linhas de continuação alinhadas à
primeira palavra do item — o recuo pendente é a largura do marcador e do espaço que o segue, medida
pela fonte do documento.
