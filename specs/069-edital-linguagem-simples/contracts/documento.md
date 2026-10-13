# Contrato: a forma do documento do Edital

O que o documento composto depois desta feature tem, em cada uma das duas apresentações (R-001). As
frases estão em [`redacao.md`](redacao.md).

## 1. As duas apresentações

| | Por perguntas | Plana |
|---|---|---|
| Quando | a assinatura do catálogo do snapshot é a da `069` (Editais submetidos depois) | qualquer outra (Editais publicados antes, e os consolidados deles) |
| Ordem e títulos | os do *Catálogo apresentado* da spec | os do snapshot original, como hoje |
| Caixa do título de seção | mista, como no catálogo | alta, como hoje |
| Seções reunidas como subseções N.k | sim (FR-1368) | não |
| Regras geradas na seção que trata delas (FR-1369) | sim | não: marcos, recurso e convocação ficam na seção de Perfis |
| Resumo | sim | não |
| Sumário, marcadores, links, título, idioma | sim | sim |
| Redação 2, fonte embutida, hierarquia, paginação | sim | sim |
| Numeração e remissões | as calculadas pela apresentação | as do original, intocadas (FR-1399) |
| Rótulos gerados com "Marcos classificatórios" | não existem (a regra está em "Como será a seleção?") | trocados por "Regras de classificação" (G1–G3 da redação), **com o mesmo número e o mesmo destino** |
| Termos internos da FR-1366 | zero na redação gerada | zero na redação gerada; o texto livre continua literal |

## 2. Abertura (as duas apresentações)

1. Brasão; órgão; linhas da Unidade.
2. Anúncio do ato em caixa alta, com as siglas preservadas (FR-1377).
3. Marca de consolidação, no consolidado.
4. Preâmbulo, sem número.
5. **Resumo** (só na apresentação por perguntas), em bloco destacado:

   | Linha | Fonte | Quando sai |
   |---|---|---|
   | Vagas | `immediateVacancies`, `locality` | sempre |
   | Cadastro de reserva | `reserveType`, `reserveLimit` | quando é igual em todos os Perfis |
   | Inscrições | Evento com `isRegistrationPeriod` | quando existe |
   | Por candidato | `maxInscricoesPorCandidato` | quando declarado |
   | Seleção | forma da ordem dos marcos e Etapas governadas (R-010) | quando todos os marcos têm a mesma forma |
   | Datas | a seção do Cronograma | quando existe |

   Cada linha termina com "(item N)". A última linha diz: "Este resumo repete informações do Edital. As
   regras completas estão nos itens indicados."
6. **Sumário**: as seções numeradas, com pontilhado e página; coeso.

**Descrição administrativa** do Edital: não sai (FR-1378).

## 3. A seção de vagas (FR-1373, FR-1374)

- **Todo Perfil com vaga imediata:** uma tabela "Vagas por Perfil e lista de concorrência":
  - colunas: Código · [Perfil, se os nomes diferem] · Localidade · Ampla concorrência · uma coluna por
    lista reservada, na ordem do quadro · Total;
  - linha Total.
- **Senão:**
  - uma frase com o total de vagas imediatas e os códigos que as têm;
  - a tabela "Perfis" dos Perfis de nome único (Código · Perfil · Localidade · Vagas imediatas);
  - uma tabela por grupo de mesmo nome ("«nome» — Perfis «códigos»": Código · Localidade · Vagas
    imediatas);
  - a tabela "Vagas imediatas por lista de concorrência" dos Perfis com vaga.
- **"Em todos os Perfis: …"** com os atributos iguais (P1 do contrato de redação).
- **"Reserva de vagas":** Lista · Percentual · Fundamento, só as listas reservadas, "—" sem percentual.
- **Reversão** logo abaixo, no mesmo bloco.
- **"N.1 Atribuições"**, quando houver, por grupo de atribuições idênticas.

Na apresentação plana, a seção de Perfis é a da `068`, com a redação 2.

## 4. A seleção (por perguntas)

- **Texto do Elaborador** de `classificacao`.
- **N.1 «Sorteio | Classificação»:** C1; "Para todos os Perfis:", quando há mais de um grupo; o comum;
  depois, "Para o(s) Perfil(is) «…»:" e o próprio de cada grupo, com as unidades da R-009 inteiras.
- **N.2 Dados para conferir o sorteio:** bloco destacado (S1 a S7), uma vez por método.
- **N.k Etapas**, uma por Etapa (E1 a E3).
- **N.k Verificação da autodeclaração**, se houver texto.

## 5. Recurso, convocação, matrícula (por perguntas)

- **Como recorrer?** R1 a R6, por grupo, e depois o texto do Elaborador.
- **Como será a convocação?** V4 ou V5, quando é igual em todos os Perfis; depois, o texto do
  Elaborador.
- **Como será a matrícula?** O texto de `matricula`; as subseções `acesso-ao-curso` e
  `homologacao-matricula` com texto; V11 ou V12 e a declaração em bloco destacado, preso à frase que a
  anuncia.

## 6. Tipografia (FR-1380 a FR-1382)

| Elemento | Forma |
|---|---|
| Fonte | Liberation Sans Regular e Bold, embutidas em subconjunto WinAnsi; recursos `F1` e `F2` |
| Título de seção | 12,5 pt, negrito, fio fino abaixo |
| Subseção N.k | 11 pt, negrito |
| Rótulo de grupo | corpo do texto, negrito |
| Texto | 10,5 pt, justificado, entrelinha de hoje |
| Lista | marcador na margem; as linhas de continuação alinhadas à primeira palavra do item (recuo pendente igual à largura do marcador e do espaço, medida pela fonte embutida). A amostra usava 14 pt fixos, que desalinhavam marcadores de larguras diferentes ("•", "a)", "1º") |
| Bloco destacado | fundo cinza 0,95 com contorno; resumo, dados do sorteio, declaração |
| Tabela | a de hoje (grade, cabeçalho cinza 0,85, legenda "Tabela N — …") |
| Cor | nenhuma informação depende de cor |

## 7. Paginação (FR-1389 a FR-1392)

As regras e os parâmetros estão na R-011. O teste da forma varre A, B, a variante e os casos sintéticos,
procurando:

- título no pé sem a linha seguinte;
- linha de tabela partida;
- continuação de tabela sem cabeçalho;
- tabela que cabia inteira deixando uma linha só na página seguinte;
- página só com o fecho;
- página, exceto a última, com mais de 50% da área útil em branco quando o bloco seguinte podia ser
  dividido.

## 8. O arquivo (FR-1384 a FR-1388)

- `PDF-1.4`, sem `/ID` e sem data em `/Info`: os mesmos bytes para o mesmo snapshot.
- `/Info`: `/Title`, com o anúncio em caixa mista, e `/Author`, "Ifes — «sigla da Unidade»".
- Catálogo: `/Lang (pt-BR)`, `/Outlines`, `/PageMode /UseOutlines` e
  `/ViewerPreferences << /DisplayDocTitle true >>`.
- Anotações `/Link`: do sumário para a seção; e `/URI` para o e-mail e os endereços `http(s)` que o
  texto impresso contém.
- Streams de página sem compactação, com dicionário `<< /Length N >>`. Só o arquivo da fonte é
  compactado, com `/Filter` e `/Length1` (R-006).
- Download: `Content-Disposition: inline; filename="edital-«n»-«ano».pdf"`. No consolidado,
  `edital-«n»-«ano»-retificado-«AAAA-MM-DD».pdf`.
- **Sem marcação** (`/StructTreeRoot`): limitação declarada (FR-1388).

## 9. O que não muda

- O comprovante de inscrição e o documento de divulgação: bytes idênticos (FR-1383), presos por fixture
  antes da mudança (R-005).
- O snapshot e o hash do conteúdo já submetido, homologado ou publicado (FR-1393).
- Os documentos publicados (FR-1394).
- O texto livre do Elaborador (FR-1395).
