> **Registro histórico.** Esta é a análise de viabilidade da **rodada 1** (versão 1 do catálogo, 126
> unidades), preservada sem alterações de conteúdo. Ela foi substituída por [`../viabilidade.md`](../viabilidade.md),
> que corrige o método, recalcula as métricas e separa os três níveis de reaproveitamento. Os links abaixo
> apontam para o estado atual dos arquivos, que mudou: unidades citadas aqui podem estar desdobradas.

# Viabilidade da hipótese: recorrência e reuso de unidades em Libras

**Medição de 2026-10-11 (rodada 1).** Baseada nos três editais **simulados** do corpus e numa sondagem
complementar, fora do corpus, em editais reais do Cefor.

## A decisão em uma frase

**Há recorrência suficiente para justificar um experimento com profissionais de Libras; ainda não há
evidência para justificar o desenvolvimento de uma biblioteca audiovisual integrada ao sistema.** A
recorrência que o corpus demonstra é sobretudo de **função e estrutura**; a de **texto idêntico** é
pequena no corpus e grande na prática — mas a prática foi medida fora do sistema, sobre texto e não
sobre sentido. E a pergunta que decide a hipótese — se uma unidade com variáveis (datas, números,
nomes) pode ser gravada uma vez e recomposta sem perder sentido em Libras — **não se responde por
documento**: depende do experimento descrito no §8.

---

## 1. A amostra, e o que ela não permite dizer

| | Corpus desta rodada | Sondagem complementar |
|---|---|---|
| O quê | 3 editais publicados pelo sistema (91/2026, 92/2026, 01/2026) e 4 Retificações | 18 editais reais do Cefor/Ifes, de 2024 a 2026 |
| Natureza | **simulados**: texto livre redigido pela auditoria do PDF e pelo `seed_demo` | **reais**, mas não produzidos pelo sistema; fora do repositório |
| Inventário | integral, linha a linha, com unidade | nenhum: só comparação automática de frases |
| Serve para | medir o que o sistema escreve sozinho e o que a estrutura repete | estimar se o **texto livre** se repete entre editais de verdade |
| Não serve para | medir a recorrência de texto livre (cada edital foi redigido independentemente) | dizer nada sobre equivalência de sentido, nem sobre outras Unidades além do Cefor |

**Três editais é pouco** (Fato). Os números abaixo descrevem esta amostra; não são estimativas para o
universo de editais do Ifes. A queda de unidades novas de 72 para 49 e para 4 é, em parte, efeito da
ordem de processamento e de o 01/2026 não ter texto livre de seção.

## 2. Métricas do corpus

### 2.1 Unidades e ocorrências

| Medida | Valor |
|---|---|
| Linhas de cobertura | 379 (101 + 224 + 54), inclusive uma de rodapés por edital |
| Ocorrências com unidade | 374 (2 linhas são marcas da simulação, que não se traduzem; 3 são rodapés) |
| Unidades distintas | **126** (124 nos originais, mais o rodapé, mais a marca de consolidação das Retificações) |
| Unidades novas por edital | 91/2026: **72** · 92/2026: **49** · 01/2026: **4** |
| Unidades em 1, 2 e 3 editais | 69 · 31 · **24** |

**Ocorrências por unidade** (originais, sem rodapé):

| Ocorrências | 1 | 2 | 3 | 4 | 5 | 6 | 18 | 19 | 24 | 39 | 58 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Unidades | 63 | 25 | 25 | 3 | 2 | 1 | 1 | 1 | 1 | 1 | 1 |

As cinco unidades com 18 ou mais ocorrências são todas estrutura repetida **dentro** do 92/2026 ou de
navegação: remissão a bloco comum (LIB-0019, 58), abertura de seção (LIB-0005, 39), identificação do
Perfil (LIB-0018, 24), dados exigidos (LIB-0084, 19) e remuneração (LIB-0081, 18).

### 2.2 Proporção do conteúdo coberta por unidades recorrentes

Percentual das palavras do edital (sem rodapés) em cada condição.

| Edital | Palavras | Unidade que reaparece em outro edital | **Texto idêntico** em outro edital | Texto repetido dentro do próprio edital | Unidades sem redação livre |
|---|---|---|---|---|---|
| 91/2026 | 1.436 | 71% | 11% | 4% | 28% |
| 92/2026 | 3.711 | 68% | 5% | **25%** | 19% |
| 01/2026 | 654 | 93% | 17% | 12% | 38% |
| **Corpus** | **5.801** | **72%** | **8%** | — | — |

- **“Unidade que reaparece”** mede recorrência de **função**: a mesma unidade, com qualquer texto.
- **“Texto idêntico”** mede recorrência de **texto**: a mesma redação, em outro edital (numeração de item e
  alínea desconsideradas).
- **“Repetido dentro do edital”** é o que se ganha sem sair do documento — no 92/2026, os 16 blocos de
  tutor presencial.

### 2.3 Palavras por classificação da unidade

| Classificação | Unidades | Ocorrências | Palavras | % |
|---|---|---|---|---|
| EXATA | 17 | 48 | 581 | 10% |
| PARAMETRIZÁVEL | 46 | 240 | 3.510 | **61%** |
| SEMELHANTE | 18 | 39 | 860 | 15% |
| INÉDITA | 44 | 44 | 787 | 14% |
| ESPECIALIZADA | 1 | 3 | 45 | 1% |

**As frases escritas pelo sistema (origem C pura) são 16% das palavras** (910) — o único texto que se
repete por construção. As unidades parametrizáveis concentram quase dois terços do texto, e é delas que
depende a hipótese.

### 2.4 Recorrência de texto idêntico por família

| Família | Palavras com texto idêntico em outro edital |
|---|---|
| ATO — abertura e fecho | 33% (órgão, títulos de seção; o fecho coincide só porque os três foram gerados no mesmo dia) |
| CLA — classificação | 21% (frases do corte, da ordem e dos marcos por Perfil) |
| INS — inscrição | 16% (frase do teto) |
| CON — convocação e matrícula | 11% (frase do Requerimento) |
| DOC — documentos | 6% (cabeçalhos dos grupos) |
| CRO — cronograma | 4% |
| PER — Perfis e vagas | 1% (as tabelas mudam sempre de valor) |
| GER, OFE, REQ, AFI, ETA, REC | **0%** |

## 3. Sondagem complementar: o texto livre se repete entre editais reais?

O corpus não responde a essa pergunta, porque o texto livre dele foi escrito de uma vez por quem montou
a simulação. Os Editais reais da amostra do projeto (em `~/Downloads`, fora do repositório; ver
`doc/avaliacao-de-capacidade-editais-*.md`) respondem em parte.

**Método.** Texto extraído com `pdftotext -layout` de 20 PDFs de editais do Cefor; 2 são digitalizações
sem texto (62/2026 e 73/2026) e ficaram fora. Frases de 6 ou mais palavras, normalizadas (minúsculas,
algarismos trocados por um marcador, pontuação retirada). Uma frase conta como “recorrente” se 80% ou
mais das suas sequências de quatro palavras aparecem em **outro** edital (e como “exata”, se todas
aparecem). Repetida a medição excluindo editais da mesma **família** — 59 e 78/2026 (Libras A1); 89 e
90/2026 (TADS); 28/2026 e 149/2024 (Informática na Educação); 77/2026 e 158/2024 (FIC remanescentes);
58/2026 e 125/2024 (FIC unificado); 69 e 76/2026 (técnico subsequente) —, porque um edital de vagas
remanescentes copia o original.

| Medida (95.768 palavras, 18 editais) | Resultado |
|---|---|
| Palavras em frases com correspondência exata em outro edital | **64%** |
| Palavras em frases recorrentes (≥ 80%) | 78% |
| Palavras em frases recorrentes **em edital de outra família** | **66%** |
| Faixa por edital (outra família) | de 19% (69/2026) a 92% (35/2026) |

**As cláusulas mais difundidas** (presentes em 10 a 18 dos 18 editais) são: a lista de documentos de
identificação aceitos; a isenção de responsabilidade do Cefor por dados incorretos ou inscrição não
efetivada; a explicação do sorteio eletrônico e da semente; o canal e as vedações de recurso; as
cláusulas de fraude; o termo de consentimento de dados pessoais; a tradução juramentada de documentos
estrangeiros; o certificado de alistamento militar.

**Limites da sondagem (Fato).** Mede texto, não sentido: duas frases iguais com “Anexo I” e “Anexo V”
contam como iguais. A correspondência é contra o documento inteiro, e não frase a frase, o que pode
superestimar. Uma Unidade só (Cefor), em dois anos. Nenhuma das frases foi inventariada ou
catalogada — **não há unidades `LIB-` derivadas da sondagem**.

**O que ela permite dizer (Hipótese forte).** Na prática do Cefor, cerca de dois terços do texto de um
edital reaparece, quase literal, em outro edital de outra natureza. Essa recorrência mora no texto
livre — **justamente a parte que o sistema não identifica**, porque não tem redação-padrão desde a
`054` (ver [`auditoria-sistema.md`](../auditoria-sistema.md), §4.1).

## 4. Respostas às perguntas da análise

**1. Quais conteúdos realmente se repetem?** No corpus, com texto idêntico: as frases que o sistema
escreve a partir de regra (teto, cabeçalhos de documentos, formas de convocação, ordem, empate,
continuação, Requerimento, marcos por Perfil) e o cabeçalho do órgão. Com a mesma função e outro texto:
quase tudo o que tem estrutura — tabelas, fichas de Etapa, Eventos, identificação de Perfil, recurso do
marco. Na prática (sondagem), também o texto livre de inscrição, documentos, recurso, fraude e
disposições finais.

**2. Com que frequência?** 24 unidades estão nos três editais; 31 em dois; 69 em um só (§2.1).

**3. Que proporção do conteúdo é coberta por unidades recorrentes?** 72% das palavras por função; 8% por
texto idêntico (§2.2).

**4. Quais diferenças são meramente textuais?** Numeração de item e de alínea; o número da tabela; datas
e quantidades nas unidades parametrizáveis (o 1º Evento de inscrições é o mesmo tipo de informação nos
três editais); o nome do polo na identificação de Perfis do 91/2026; o hash e a data no fecho.

**5. Quais diferenças mudam as condições de tradução?** As que mudam regra ou alcance com pouca mudança
de letra: reversão por ausência × pelo saldo (LIB-0015 × LIB-0078); empate estrito × com excedente
(LIB-0123 × LIB-0093); “exclusivamente” no canal de dúvidas (LIB-0007); experiência “no magistério” ×
“no magistério superior” × “no ensino básico ou superior, ou vinculação…” (LIB-0083); dias corridos ×
dias úteis; a presença ou o **silêncio** de uma frase de recurso; e a numeração, que em vídeo vira
navegação e que uma Retificação desloca.

**6. Quais categorias têm maior potencial de reutilização?** Classificação (CLA), pelas frases fixas;
Inscrição e Matrícula, pelas normas que o sistema acrescenta; os cabeçalhos de Documentos; a abertura e
o fecho do ato; o Cronograma, **se** a data puder ser variável num vídeo gravado; e — pela sondagem —
documentos de identificação, recurso e disposições finais em texto livre.

**7. Quais categorias exigiriam gravação específica quase sempre?** Oferta e público (OFE), requisitos
específicos de Perfil (REQ), atribuições, descrição do Edital, preâmbulo, justificativa de Retificação,
e as tabelas de Perfis e de vagas — cujo conteúdo muda inteiro de edital para edital.

**8. A granularidade proposta é plausível para produção audiovisual?** **Documentalmente, sim; em vídeo,
não está demonstrado.** A unidade média tem 15 palavras; nenhuma é uma palavra solta, e nenhuma é uma
seção inteira. Mas há três famílias de risco: unidades que **dependem** de outra para ter sentido
(empate e continuação só depois do corte; remissões só com o bloco comum), unidades **tabulares** (cuja
tradução é espacial e cuja unidade talvez seja a tabela inteira) e unidades **curtíssimas** de rótulo
(“Ordem: por sorteio”), que talvez só façam sentido dentro do bloco do marco. É exatamente o que o
experimento do §8 precisa testar.

## 5. Categorias por potencial

| Família | Unidades | Ocorr. | Em ≥ 2 editais | Leitura |
|---|---|---|---|---|
| CLA — classificação | 18 | 33 | 8 | **alto**: 8 frases exatas do sistema; mas dependências internas fortes |
| ATO — abertura e fecho | 9* | 59 | 8 | **alto** para órgão, títulos e fecho; baixo para descrição e preâmbulo |
| DOC — documentos | 17 | 36 | 9 | **médio-alto**: cabeçalhos fixos; documentos comuns na prática |
| CON — convocação e matrícula | 5 | 8 | 3 | médio: frase do Requerimento exata; declaração quase igual |
| INS — inscrição | 8 | 11 | 2 | médio: frase do teto exata; o resto, texto livre |
| CRO — cronograma | 18 | 34 | 7 | médio, condicionado a data variável |
| PER — Perfis e vagas | 14 | 142 | 8 | estrutura muito recorrente, conteúdo sempre novo; muita repetição interna |
| ETA — etapas | 2 | 6 | 2 | médio: ficha parametrizável |
| REC — recursos | 3 | 5 | 2 | baixo no corpus, alto na prática |
| GER — disposições gerais | 9 | 13 | 3 | baixo no corpus, alto na prática |
| AFI — ações afirmativas | 5 | 6 | 1 | baixo; sensível, pede tradução cuidadosa |
| REQ — requisitos | 13 | 17 | 2 | baixo: específicos de cada Perfil |
| OFE — oferta | 4 | 4 | 0 | baixo |

\* Inclui a marca de consolidação, vista só nas Retificações, e não inclui o rodapé, que não se traduz.

## 6. Retificações: o que elas mostram sobre a hipótese

As quatro Retificações do corpus (ver os `retificacoes.md` de cada edital) mostram três coisas que uma
biblioteca de vídeos teria de tratar como requisito, e não como exceção:

1. **Mudança pequena, efeito grande.** Esvaziar uma seção renumerou oito seções do 92/2026 e deixou
   subitens digitados e uma remissão apontando para lugar errado — com aviso, sem impedimento.
2. **Texto igual, efeito diferente.** O corte pelo quadro de vagas (91/2026) não muda de texto e passa a
   alcançar mais gente; o corte fixo em 2 (01/2026) não acompanha o aumento de vagas.
3. **Dois documentos válidos.** Com vigência futura (01/2026, v3), há um ato publicado e outro vigente.

## 7. Unidades mais promissoras para validação profissional e piloto

Vinte unidades, escolhidas por: recorrer entre editais ou ser texto fixo do sistema; ter sentido
completo com pouco contexto; ter efeito jurídico claro; e, juntas, exercitar os três tipos de reuso
(texto fixo, parâmetro, composição).

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 1 | [LIB-0034](../catalogo/unidades/LIB-0034.md) Limite de inscrições | EXATA | três editais, texto idêntico, frase autônoma |
| 2 | [LIB-0035](../catalogo/unidades/LIB-0035.md) Documentos de todos (cabeçalho) | EXATA | três editais; testa unidade curta de rótulo |
| 3 | [LIB-0064](../catalogo/unidades/LIB-0064.md) Requerimento no ato da inscrição | EXATA | dois editais, autônoma |
| 4 | [LIB-0017](../catalogo/unidades/LIB-0017.md) Convocação por publicação | EXATA | par com a seguinte: mesma função, regras opostas |
| 5 | [LIB-0079](../catalogo/unidades/LIB-0079.md) Convocação por mensagem individual | EXATA | dois editais |
| 6 | [LIB-0015](../catalogo/unidades/LIB-0015.md) Reversão por ausência de aprovados | EXATA | par com a seguinte: diferença jurídica fina |
| 7 | [LIB-0078](../catalogo/unidades/LIB-0078.md) Reversão pelo saldo não preenchido | EXATA | idem |
| 8 | [LIB-0023](../catalogo/unidades/LIB-0023.md) Marcos por Perfil separadamente | EXATA | frase de alcance; dois editais |
| 9 | [LIB-0092](../catalogo/unidades/LIB-0092.md) Corte com quantidade fixa | PARAMETRIZÁVEL | base do teste de composição (9–13) |
| 10 | [LIB-0093](../catalogo/unidades/LIB-0093.md) Empate com excedente | EXATA | anáfora: só existe depois do corte |
| 11 | [LIB-0123](../catalogo/unidades/LIB-0123.md) Empate estrito | EXATA | idem, regra oposta |
| 12 | [LIB-0030](../catalogo/unidades/LIB-0030.md) Continuação admitida | EXATA | completa o bloco do corte |
| 13 | [LIB-0124](../catalogo/unidades/LIB-0124.md) Continuação não admitida | EXATA | idem, regra oposta |
| 14 | [LIB-0028](../catalogo/unidades/LIB-0028.md) Prazo de recurso do marco | PARAMETRIZÁVEL | três editais, três prazos (2, 3, 5 dias) e três nomes: teste de parâmetro |
| 15 | [LIB-0050](../catalogo/unidades/LIB-0050.md) Evento: período de inscrições | PARAMETRIZÁVEL | três editais; teste de data variável |
| 16 | [LIB-0005](../catalogo/unidades/LIB-0005.md) Abertura de seção | PARAMETRIZÁVEL | 22 títulos fixos; teste de navegação por título |
| 17 | [LIB-0036](../catalogo/unidades/LIB-0036.md) Documento de identificação com foto | SEMELHANTE | três editais; a cláusula mais difundida nos editais reais |
| 18 | [LIB-0061](../catalogo/unidades/LIB-0061.md) Recurso: vedações | SEMELHANTE | frequente nos editais reais |
| 19 | [LIB-0068](../catalogo/unidades/LIB-0068.md) Casos omissos | PARAMETRIZÁVEL | fórmula fixa com uma variável |
| 20 | [LIB-0107](../catalogo/unidades/LIB-0107.md) Atendimento especializado à PcD | INÉDITA | o próprio público surdo é destinatário |

## 8. O experimento mínimo

**Pergunta.** Uma tradução em Libras, validada para uma unidade, pode ser reaproveitada em outro edital
— como está, com uma variável trocada, ou composta com outras unidades — sem perda de sentido nem de
fidelidade jurídica, frente a uma tradução contínua do mesmo trecho?

**Material.** As unidades 9 a 15 da tabela acima, nos três editais do corpus (ou, melhor, em dois
editais reais publicados pelo sistema no piloto), e a [terminologia](../catalogo/terminologia.md) dos
termos que elas usam, decidida antes.

**Desenho.**

1. **Decidir os termos** (corte, suplente, recurso, dias corridos, Perfil, códigos) com o profissional e
   registrá-los na terminologia.
2. **Gravar por unidade**: cada unidade uma vez; as parametrizáveis com a variável tratada como o
   profissional decidir (sinalizada à parte, escrita na tela, ou regravada).
3. **Compor** três trechos a partir das unidades gravadas: o bloco do corte do 92/2026 (corte + empate
   com excedente + continuação admitida), o do 01/2026 DOC-INFO (corte + empate estrito + continuação
   não admitida) e o recurso do marco nos três editais.
4. **Gravar contínuo** os mesmos três trechos, como tradução individual.
5. **Avaliar** as duas versões com pessoas surdas, por perguntas sobre a regra (“quantas pessoas seguem
   para a análise?”, “se houver empate na última posição, o que acontece?”, “até quando se pode
   recorrer, e contra o quê?”), e com revisão jurídica da fidelidade ao ato.

**O que medir.** Acerto nas perguntas, nas duas versões; quantas unidades serviram sem regravação, com
regravação só da variável e com regravação inteira; onde a emenda entre unidades prejudicou o sentido
(apontado pelo profissional e pelos participantes).

**Critério de decisão.** Se a versão composta tiver acerto equivalente à contínua e a maior parte das
unidades servir sem regravação inteira, a hipótese ganha base para uma etapa seguinte (mais unidades,
editais reais, e só então a discussão de integração ao sistema). Se não, o reuso fica restrito ao texto
fixo de maior uso, gravado como trecho autônomo, e a biblioteca integrada não se justifica.

**Fora do experimento.** Estimativa de custo, de tempo de vídeo ou de economia: esta análise não as
produz, porque nada nela as fundamenta.

## 9. O que depende de um profissional de Libras

- Se a unidade, como recortada aqui, é um limite linguístico viável para um vídeo — ou se o limite é o
  bloco (o marco inteiro, a tabela inteira).
- Como tratar variáveis: datas, números, nomes de Etapa, códigos de Perfil, fundamentos legais.
- Como traduzir tabelas e a relação entre colunas.
- Como navegar entre seções em vídeo (por número, por título) e como tratar remissões.
- A terminologia (sinal para “recorte”, “marco classificatório”, “suplente”, “heteroidentificação”…).
- Se paráfrases são admissíveis (“quem nasceu primeiro” por “menor valor declarado em Data de
  nascimento”) — com revisão jurídica.
- A validação de toda tradução, e de todo reaproveitamento em contexto novo.

## 10. Riscos e decisões pendentes

| Risco | Onde | Decisão pendente |
|---|---|---|
| Texto fixo muda com o código | 49 commits no compositor desde 28/08 | gravar a versão do compositor em cada Publicação? |
| Numeração posicional e digitada | 92/2026 v2 | navegação por título nos vídeos? |
| Vocabulário do sistema no ato | auditoria de 08/10, §5 | reescrever as frases **antes** de gravar, para não gravar duas vezes |
| Texto livre sem identidade | sistema, desde a `054` | o setor quer cláusulas institucionais com identidade (que permitiriam reuso reconhecível)? É decisão de produto, não desta análise |
| Anexos e documentos fora do PDF | anexos, resultado, avisos, convocação | entram no escopo de Libras? |
| Declaração com hash do texto em português | Requerimento de Matrícula | qual o estatuto do vídeo frente ao texto aceito? |
| Corpus simulado | esta rodada | repetir a medição com editais reais publicados pelo sistema no piloto |
