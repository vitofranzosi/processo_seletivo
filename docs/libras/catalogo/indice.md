# Catálogo de unidades semânticas

**Versão 3 — 2026-10-11 (rodada 3).** 316 identificadores: **304 unidades ativas** e
12 desdobradas na rodada 2, a partir de três editais **simulados** (91/2026, 92/2026 e 01/2026)
e das suas quatro Retificações, e de dois editais **reais** do Cefor (28/2026 e 59/2026, na versão consolidada
que o Cefor publicou). Nenhuma unidade tem tradução produzida, validada ou vídeo associado.

> **O que mudou da versão 2 para a 3.** Entraram os dois editais reais, com os anexos que estão dentro do PDF.
> 162 unidades novas (a partir de LIB-0155) e uma família nova, **ANX** (formulários, declarações e
> termos). 21 unidades anteriores ganharam ocorrência real com outra redação e
> passaram a `SEMELHANTE` ou `PARAMETRIZÁVEL`, com a equivalência a confirmar — o texto do sistema e o texto do
> Cefor dizem, à primeira análise, a mesma coisa de outra maneira. Nenhuma unidade foi desdobrada nesta rodada.

> **O que mudou da versão 1 para a 2.** A rodada 1 tinha 126 unidades. A revisão crítica mostrou dois erros
> de método, e eles foram corrigidos em todo o catálogo: regras diferentes agrupadas por ocuparem a mesma
> posição no documento (12 unidades desdobradas; 3 regras embutidas em descrições de Evento ganharam unidade
> própria) e diferenças só de redação tratadas como diferença de sentido (6 unidades passaram a registrar
> equivalência a confirmar). Também foram retiradas orientações que decidiam a solução linguística para
> favorecer o reuso. Cada correção está no *Histórico* da unidade; o registro da versão 1 está em
> [`../ferramentas/referencia/catalogo-v1.json`](../ferramentas/referencia/catalogo-v1.json).

## O que é uma unidade

Uma informação ou comunicação completa o bastante para ser traduzida com sentido dentro de um contexto
documentado: uma regra, um requisito, um documento pedido, um Evento do Cronograma, uma tabela. Nem uma
palavra, nem uma seção inteira. Termos isolados não são unidades: estão em [`terminologia.md`](terminologia.md).

A unidade é **documental**: serve para controlar cobertura e rastrear origem. Ela não define o limite de um
vídeo, nem a organização da tradução — para isso existe a camada comunicativa
([`../camada-comunicativa.md`](../camada-comunicativa.md)), que reúne unidades de várias seções numa situação
do candidato.

## Quando é a mesma unidade e quando é outra

**É outra unidade** quando muda o destinatário, a modalidade normativa (obrigação, possibilidade, proibição),
a condição ou a consequência — ainda que a diferença de letra seja pequena. Ex.: experiência “no magistério”,
“no magistério superior” e “no ensino básico ou superior, ou vinculação a pós-graduação” (LIB-0139, LIB-0141,
LIB-0142).

**É a mesma unidade, `SEMELHANTE`,** quando a função e, à primeira análise, o efeito são os mesmos, e a
redação difere. A equivalência fica **a confirmar** com a área responsável pelas regras e com o profissional
de Libras. Ex.: “pela internet, no endereço do certame” e “pelo sistema de inscrições” (LIB-0031).

## Identificador

`LIB-NNNN`, atribuído na ordem de descoberta e **nunca reaproveitado nem renumerado** (os mapas estão em
[`../ferramentas/ids.py`](../ferramentas/ids.py)). Unidade desdobrada fica no catálogo, riscada, com as
ocorrências que tinha e o apontamento para as sucessoras.

## Classificação documental

| Classificação | Quer dizer | Unidades ativas |
|---|---|---|
| **EXATA** | texto e contexto equivalentes em todas as ocorrências: texto fixo do sistema, nos simulados, e cláusulas que o Cefor repete literalmente entre 28 e 59 | 33 |
| **PARAMETRIZÁVEL** | estrutura recorrente com variáveis; as variáveis são **de valor** (o dado) ou **de condição** (a regra) | 61 |
| **SEMELHANTE** | mesma função e, provavelmente, mesmo efeito, com redação diferente; equivalência a confirmar | 48 |
| **INÉDITA** | uma ocorrência só no corpus (ou repetida só no mesmo edital) | 158 |
| **ESPECIALIZADA** | conteúdo próprio de cada edital, que pede tradução individual | 4 |

**A classificação é documental, não audiovisual.** Ela não diz se um roteiro, uma solução tradutória ou uma
gravação podem ser reaproveitados: são três perguntas diferentes, avaliadas em
[`../viabilidade.md`](../viabilidade.md), §6.

**Situação na rodada** (nas matrizes de cobertura) é a relação de cada ocorrência com o catálogo no momento
em que foi processada, na ordem 91 → 92 → 01 → 28 → 59: `INÉDITA` se a unidade nasce ali; `EXATA` se o texto é igual
ao de uma ocorrência anterior (numeração de item e alínea não contam); nos demais casos, a classificação da
unidade.

## Origem

Conforme a auditoria do PDF de 08/10/2026, §3.2: **A** gerada automaticamente · **B** campo estruturado ·
**C** frase escrita pelo sistema a partir de regra · **D** redação livre do gestor · **E** outra entidade.
Nas unidades criadas a partir dos editais reais, a origem é **D**: texto do documento oficial, escrito fora do
sistema. Nas matrizes de cobertura dos editais reais, toda linha tem origem **R** (documento real).

## Complexidade linguística preliminar

`baixa`, `média` ou `alta`: estimativa **documental** do esforço de tradução, para escolher o piloto. Não é
avaliação linguística, e deve ser revista pelo profissional.

## Famílias e unidades

Colunas 91, 92 e 01: ocorrências em cada edital simulado (versão original); 28 e 59: nos editais reais (versão
consolidada). Para a marca de consolidação, entre parênteses, o número de Retificações em que aparece.

### ATO — Abertura, estrutura e fecho do ato

A identidade do ato e a navegação no documento.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0001](unidades/LIB-0001.md) | Identificação do órgão emissor | EXATA | A+E | baixa | 1 | 1 | 1 | 1 | 2 |
| [LIB-0002](unidades/LIB-0002.md) | Anúncio do ato: número, ano e objeto do Edital | PARAMETRIZÁVEL | A+D | média | 1 | 1 | 1 | 1 | 1 |
| [LIB-0003](unidades/LIB-0003.md) | Descrição resumida do Edital | ESPECIALIZADA | D | baixa | 1 | 1 | 1 | 0 | 0 |
| [LIB-0004](unidades/LIB-0004.md) | Preâmbulo: a autoridade torna pública a abertura | SEMELHANTE | D | média | 1 | 1 | 0 | 1 | 1 |
| [LIB-0005](unidades/LIB-0005.md) | Abertura de seção numerada | PARAMETRIZÁVEL | A | baixa | 17 | 15 | 7 | 15 | 10 |
| [LIB-0069](unidades/LIB-0069.md) | Local e data do ato | PARAMETRIZÁVEL | A+E | baixa | 1 | 1 | 1 | 1 | 1 |
| [LIB-0070](unidades/LIB-0070.md) | Autoridade responsável pelo ato | PARAMETRIZÁVEL | A+E | baixa | 1 | 1 | 1 | 1 | 1 |
| [LIB-0071](unidades/LIB-0071.md) | Verificação de integridade do documento | PARAMETRIZÁVEL | A | alta | 1 | 1 | 1 | 0 | 0 |
| [LIB-0072](unidades/LIB-0072.md) | Rodapé de página (Edital, verificação e paginação) | PARAMETRIZÁVEL | A | baixa | 1 | 1 | 1 | 0 | 0 |
| [LIB-0126](unidades/LIB-0126.md) | Marca de versão consolidada | PARAMETRIZÁVEL | A | média | (1) | (1) | (2) | — | — |
| [LIB-0214](unidades/LIB-0214.md) | Título de subseção do texto livre | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 2 | 0 |
| [LIB-0294](unidades/LIB-0294.md) | Identificação do edital no alto do anexo | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |

### GER — Disposições gerais

Regras de condução, canais e efeitos gerais do certame, em texto livre.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0006](unidades/LIB-0006.md) | Condução do certame por comissão designada | SEMELHANTE | D | baixa | 1 | 1 | 0 | 1 | 0 |
| [LIB-0007](unidades/LIB-0007.md) | ~~Canal de atendimento a dúvidas~~ — desdobrada em LIB-0127, LIB-0151 | — | — | — | — | — | — | — | — |
| [LIB-0008](unidades/LIB-0008.md) | Local oficial das publicações do certame | SEMELHANTE | D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0068](unidades/LIB-0068.md) | Casos omissos | PARAMETRIZÁVEL | D | baixa | 1 | 1 | 0 | 1 | 1 |
| [LIB-0073](unidades/LIB-0073.md) | Finalidade de cadastro de reserva e convocação conforme a necessidade | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0074](unidades/LIB-0074.md) | Ausência de vínculo empregatício do bolsista | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0075](unidades/LIB-0075.md) | ~~Vedação de acúmulo de bolsas~~ — desdobrada em LIB-0136, LIB-0137 | — | — | — | — | — | — | — | — |
| [LIB-0120](unidades/LIB-0120.md) | Prazo de validade do processo seletivo | PARAMETRIZÁVEL | D | baixa | 0 | 1 | 0 | 0 | 1 |
| [LIB-0121](unidades/LIB-0121.md) | Aceitação das normas pela inscrição | SEMELHANTE | D | baixa | 0 | 1 | 0 | 1 | 1 |
| [LIB-0127](unidades/LIB-0127.md) | Canal exclusivo de esclarecimento de dúvidas, com horário | PARAMETRIZÁVEL | D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0136](unidades/LIB-0136.md) | Vedação de acúmulo de bolsas CAPES e FNDE | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0151](unidades/LIB-0151.md) | Canal facultativo para envio de dúvidas | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0279](unidades/LIB-0279.md) | Inexatidão de informação elimina e anula os atos | EXATA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0280](unidades/LIB-0280.md) | Convocação para verificação em caso de denúncia de fraude | EXATA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0281](unidades/LIB-0281.md) | Fraude implica perda da vaga e penalidades | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0282](unidades/LIB-0282.md) | Sem mensalidades | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0283](unidades/LIB-0283.md) | Vigência do edital a partir da publicação | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 2 |
| [LIB-0284](unidades/LIB-0284.md) | Conhecer as normas e os anexos antes de se inscrever | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0285](unidades/LIB-0285.md) | Prazos do Cronograma, sob pena de desclassificação | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0286](unidades/LIB-0286.md) | Cessão de imagem e voz ao se inscrever | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0287](unidades/LIB-0287.md) | Cessão de imagem e voz do aluno matriculado | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0288](unidades/LIB-0288.md) | Prazo indeterminado da cessão, salvo notificação | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |

### OFE — Oferta, público e certificação

O que é ofertado e para quem; texto livre.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0009](unidades/LIB-0009.md) | Caracterização da oferta do curso | SEMELHANTE | D | média | 1 | 0 | 0 | 1 | 0 |
| [LIB-0010](unidades/LIB-0010.md) | Carga horária e duração do curso | PARAMETRIZÁVEL | D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0011](unidades/LIB-0011.md) | Público-alvo | SEMELHANTE | D | baixa | 1 | 0 | 0 | 1 | 0 |
| [LIB-0066](unidades/LIB-0066.md) | Condição para o certificado | INÉDITA | D | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0155](unidades/LIB-0155.md) | Matriz curricular do curso (quadro) | PARAMETRIZÁVEL | D | alta | 0 | 0 | 0 | 1 | 1 |
| [LIB-0156](unidades/LIB-0156.md) | Objetivo e fundamentos do curso | ESPECIALIZADA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0157](unidades/LIB-0157.md) | Metodologia das aulas | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0158](unidades/LIB-0158.md) | Início do curso indicado no Cronograma | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0159](unidades/LIB-0159.md) | Condição para o certificado: aprovação com nota mínima | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0160](unidades/LIB-0160.md) | Envio do certificado por e-mail em até 60 dias | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0161](unidades/LIB-0161.md) | Confecção do certificado em até 180 dias | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0162](unidades/LIB-0162.md) | Dúvidas e segunda via do certificado | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0163](unidades/LIB-0163.md) | Reprovação em componente: desligamento sem dependência | EXATA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0169](unidades/LIB-0169.md) | Público-alvo: quem tem ensino médio completo | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |

### REQ — Requisitos de participação

Condições que a pessoa precisa cumprir para concorrer.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0012](unidades/LIB-0012.md) | Remissão aos requisitos específicos do Perfil | SEMELHANTE | D | baixa | 1 | 1 | 0 | 0 | 0 |
| [LIB-0021](unidades/LIB-0021.md) | Requisito: diploma de graduação reconhecido pelo MEC | SEMELHANTE | D | baixa | 1 | 1 | 0 | 1 | 0 |
| [LIB-0022](unidades/LIB-0022.md) | Requisito: acesso a computador com internet | SEMELHANTE | D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0076](unidades/LIB-0076.md) | Requisito geral: nacionalidade | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0077](unidades/LIB-0077.md) | Requisito geral: quitação eleitoral e militar | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0082](unidades/LIB-0082.md) | Requisito: graduação em áreas específicas | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0083](unidades/LIB-0083.md) | ~~Requisito: experiência mínima no magistério~~ — desdobrada em LIB-0139, LIB-0141, LIB-0142 | — | — | — | — | — | — | — | — |
| [LIB-0085](unidades/LIB-0085.md) | Requisito: mestrado em qualquer área com graduação em Computação | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0087](unidades/LIB-0087.md) | Requisito: residência no município do polo | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0088](unidades/LIB-0088.md) | Requisito: disponibilidade de horas semanais | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0089](unidades/LIB-0089.md) | Requisito: habilidade com computador e ambiente virtual | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0122](unidades/LIB-0122.md) | Requisito: mestrado na área ou em área afim | INÉDITA | D | baixa | 0 | 0 | 1 | 0 | 0 |
| [LIB-0125](unidades/LIB-0125.md) | Requisito: curso técnico na área | INÉDITA | D | baixa | 0 | 0 | 1 | 0 | 0 |
| [LIB-0137](unidades/LIB-0137.md) | Requisito geral: não ter outra bolsa CAPES ou FNDE no período de atuação | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0139](unidades/LIB-0139.md) | Requisito: experiência mínima no magistério (sem nível de ensino) | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0141](unidades/LIB-0141.md) | Requisito: experiência mínima no magistério superior | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0142](unidades/LIB-0142.md) | Requisito: experiência no magistério básico ou superior, ou vínculo a pós-graduação, comprovada por declaração | INÉDITA | D | alta | 0 | 1 | 0 | 0 | 0 |
| [LIB-0164](unidades/LIB-0164.md) | Requisito: ler atentamente o edital | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0165](unidades/LIB-0165.md) | Requisito: conhecimentos intermediários de Informática | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0166](unidades/LIB-0166.md) | Requisito: ensino médio completo | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0167](unidades/LIB-0167.md) | Requisito: disponibilidade para aulas presenciais semanais | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0168](unidades/LIB-0168.md) | Requisito: habilidade no uso do computador | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |

### PER — Perfis, vagas e modalidades

A oferta estruturada: Perfis, quantidades e listas de concorrência.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0013](unidades/LIB-0013.md) | Quadro de Perfis de vaga (tabela) | PARAMETRIZÁVEL | A+B+D | alta | 1 | 1 | 1 | 0 | 1 |
| [LIB-0014](unidades/LIB-0014.md) | Vagas por lista de concorrência (matriz) | PARAMETRIZÁVEL | A+B | alta | 1 | 1 | 1 | 1 | 0 |
| [LIB-0015](unidades/LIB-0015.md) | Reversão de vagas: ausência de aprovados na reserva | SEMELHANTE | C | média | 1 | 0 | 0 | 1 | 0 |
| [LIB-0016](unidades/LIB-0016.md) | Modalidades de concorrência (tabela) | PARAMETRIZÁVEL | A+B+D | alta | 1 | 1 | 2 | 1 | 0 |
| [LIB-0017](unidades/LIB-0017.md) | Forma de convocação: publicação no endereço eletrônico | EXATA | C | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0018](unidades/LIB-0018.md) | Identificação do Perfil (código, nome e descrição) | PARAMETRIZÁVEL | A+B+D | média | 4 | 18 | 2 | 0 | 0 |
| [LIB-0019](unidades/LIB-0019.md) | Remissão a bloco comum de Perfis | PARAMETRIZÁVEL | C | baixa | 8 | 50 | 0 | 0 | 0 |
| [LIB-0020](unidades/LIB-0020.md) | Título de subseção comum aos Perfis | PARAMETRIZÁVEL | C | média | 2 | 3 | 0 | 0 | 0 |
| [LIB-0078](unidades/LIB-0078.md) | Reversão de vagas: não preenchimento total das reservadas | EXATA | C | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0079](unidades/LIB-0079.md) | Forma de convocação: mensagem individual | EXATA | C | baixa | 0 | 1 | 1 | 0 | 0 |
| [LIB-0080](unidades/LIB-0080.md) | ~~Atribuições da tutoria a distância~~ — desdobrada em LIB-0138, LIB-0140 | — | — | — | — | — | — | — | — |
| [LIB-0081](unidades/LIB-0081.md) | Remuneração do Perfil | EXATA | B+D | baixa | 0 | 18 | 0 | 0 | 0 |
| [LIB-0084](unidades/LIB-0084.md) | Dados exigidos na inscrição | PARAMETRIZÁVEL | A+D | média | 0 | 18 | 1 | 0 | 0 |
| [LIB-0086](unidades/LIB-0086.md) | Atribuições da tutoria presencial (comuns aos polos) | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0138](unidades/LIB-0138.md) | Atribuições da tutoria a distância (três atribuições) | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0140](unidades/LIB-0140.md) | Atribuições da tutoria a distância com orientação de TFC (quatro atribuições) | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0170](unidades/LIB-0170.md) | Total de vagas e onde está a distribuição | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 1 |

### CLA — Classificação

Como a ordem é produzida, cortada, desempatada e contestada.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0023](unidades/LIB-0023.md) | Marcos aplicados a cada Perfil separadamente | EXATA | C | média | 1 | 1 | 0 | 0 | 0 |
| [LIB-0024](unidades/LIB-0024.md) | Identificação do marco classificatório | PARAMETRIZÁVEL | A+B+D | média | 1 | 1 | 2 | 0 | 0 |
| [LIB-0025](unidades/LIB-0025.md) | Forma da ordem: por sorteio | SEMELHANTE | C | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0026](unidades/LIB-0026.md) | Método do sorteio público | PARAMETRIZÁVEL | A+B+D | alta | 1 | 0 | 0 | 0 | 0 |
| [LIB-0027](unidades/LIB-0027.md) | Habilitação ao sorteio: todas as inscrições submetidas | EXATA | C | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0028](unidades/LIB-0028.md) | Prazo de recurso contra o resultado do marco | PARAMETRIZÁVEL | C | média | 1 | 1 | 1 | 0 | 0 |
| [LIB-0029](unidades/LIB-0029.md) | Corte pelo quadro de vagas, com suplentes | PARAMETRIZÁVEL | C | alta | 1 | 0 | 0 | 0 | 0 |
| [LIB-0030](unidades/LIB-0030.md) | Continuação admitida além do corte | EXATA | C | média | 1 | 1 | 0 | 0 | 0 |
| [LIB-0047](unidades/LIB-0047.md) | Classificação por sorteio quando inscritos excedem vagas (texto livre) | SEMELHANTE | D | média | 1 | 0 | 0 | 1 | 1 |
| [LIB-0048](unidades/LIB-0048.md) | Análise documental dos sorteados até as vagas (texto livre) | INÉDITA | D | média | 1 | 0 | 0 | 0 | 0 |
| [LIB-0090](unidades/LIB-0090.md) | Forma da ordem: pela pontuação combinada das Etapas | EXATA | C | baixa | 0 | 1 | 2 | 0 | 0 |
| [LIB-0091](unidades/LIB-0091.md) | Regra de cálculo da nota classificatória | PARAMETRIZÁVEL | C+D | alta | 0 | 1 | 2 | 0 | 0 |
| [LIB-0092](unidades/LIB-0092.md) | Corte com quantidade fixa | PARAMETRIZÁVEL | C | média | 0 | 1 | 2 | 0 | 0 |
| [LIB-0093](unidades/LIB-0093.md) | Empate no corte: todos os empatados progridem | EXATA | C | média | 0 | 1 | 1 | 0 | 0 |
| [LIB-0094](unidades/LIB-0094.md) | Critérios de desempate | PARAMETRIZÁVEL | C+D | alta | 0 | 1 | 0 | 0 | 0 |
| [LIB-0109](unidades/LIB-0109.md) | Nota final pela prova de títulos (texto livre) | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0123](unidades/LIB-0123.md) | Empate no corte: a quantidade não é excedida | EXATA | C | média | 0 | 0 | 1 | 0 | 0 |
| [LIB-0124](unidades/LIB-0124.md) | Continuação não admitida | EXATA | C | baixa | 0 | 0 | 2 | 0 | 0 |
| [LIB-0236](unidades/LIB-0236.md) | A presença no sorteio não é obrigatória | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 2 |
| [LIB-0237](unidades/LIB-0237.md) | Software do sorteio e campo “Semente utilizada” | SEMELHANTE | D | alta | 0 | 0 | 0 | 1 | 1 |
| [LIB-0238](unidades/LIB-0238.md) | Análise dos sorteados até as vagas, com substituição do indeferido pelo próximo | EXATA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0239](unidades/LIB-0239.md) | Lista de habilitados ao sorteio dois dias antes | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0240](unidades/LIB-0240.md) | Sorteio on-line, transmitido e gravado | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0241](unidades/LIB-0241.md) | Sorteio no salão de reuniões do Cefor, gravado | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0242](unidades/LIB-0242.md) | Homologação após a análise; documento irregular impede a matrícula | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0243](unidades/LIB-0243.md) | Homologação após a análise; documento irregular indefere a inscrição | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0244](unidades/LIB-0244.md) | Sorteio da ampla primeiro, com todos; depois o das reservas | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0245](unidades/LIB-0245.md) | Sorteado nas duas listas fica na ampla | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0246](unidades/LIB-0246.md) | Vaga reservada de desistente vai ao próximo autodeclarado | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0247](unidades/LIB-0247.md) | Autodeclarados sorteados na ampla não contam nas reservadas | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0248](unidades/LIB-0248.md) | Análise dos documentos dos suplentes, por código de vaga | PARAMETRIZÁVEL | D | média | 0 | 0 | 0 | 1 | 1 |

### INS — Inscrição

Como, quando e quantas vezes se inscrever.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0031](unidades/LIB-0031.md) | Canal e período de inscrição | SEMELHANTE | D | baixa | 1 | 1 | 0 | 1 | 1 |
| [LIB-0032](unidades/LIB-0032.md) | Indicação do Perfil e da lista na inscrição | SEMELHANTE | D | baixa | 1 | 0 | 0 | 2 | 0 |
| [LIB-0033](unidades/LIB-0033.md) | Concorrência simultânea às vagas reservadas e à ampla | SEMELHANTE | D | média | 1 | 0 | 0 | 1 | 0 |
| [LIB-0034](unidades/LIB-0034.md) | Limite de inscrições por candidato | EXATA | C | baixa | 1 | 1 | 1 | 0 | 0 |
| [LIB-0095](unidades/LIB-0095.md) | Formato e limite do arquivo de documentos | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0096](unidades/LIB-0096.md) | Ausência de conferência na inscrição e responsabilidade do candidato | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0097](unidades/LIB-0097.md) | Indeferimento por excesso de páginas | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0110](unidades/LIB-0110.md) | Concorrência a um único código de inscrição (texto livre) | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0152](unidades/LIB-0152.md) | Isenção de taxa de inscrição até o 5º dia (regra na descrição de Evento) | INÉDITA | D | média | 0 | 0 | 1 | 0 | 0 |
| [LIB-0175](unidades/LIB-0175.md) | Inscrição pressupõe acordo com o edital | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0176](unidades/LIB-0176.md) | Cadastro no Gov.br para a inscrição | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0177](unidades/LIB-0177.md) | E-mail do Gov.br em letras minúsculas | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0178](unidades/LIB-0178.md) | Envio dos documentos: PDF de até 7 MB por campo, legível e sem cortes | EXATA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0179](unidades/LIB-0179.md) | Confirmar a inscrição no formulário | SEMELHANTE | D | baixa | 0 | 0 | 0 | 2 | 1 |
| [LIB-0180](unidades/LIB-0180.md) | Imprimir e salvar o comprovante de inscrição | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0181](unidades/LIB-0181.md) | Responsabilidade do candidato pelo preenchimento e pelo envio | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0182](unidades/LIB-0182.md) | Informações de inteira responsabilidade do candidato, sob as penas da lei | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0183](unidades/LIB-0183.md) | O Cefor não responde por erro de preenchimento ou falha técnica | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0184](unidades/LIB-0184.md) | Indeferimento por dados incompletos ou arquivo com problema, sem recurso | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0185](unidades/LIB-0185.md) | Documentos cortados ou ilegíveis não são aceitos | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0186](unidades/LIB-0186.md) | Indeferimento por documento fora do formato ou inválido | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0187](unidades/LIB-0187.md) | Não se aceita inscrição nem documento por e-mail | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0188](unidades/LIB-0188.md) | Ler o termo de consentimento de dados e marcar a opção | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0189](unidades/LIB-0189.md) | Inscrição com declaração de colação de grau futura | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0190](unidades/LIB-0190.md) | Comprovar o término da graduação em até 30 dias do início | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |

### DOC — Documentos e anexos

O que entregar, quem entrega e onde estão os modelos.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0035](unidades/LIB-0035.md) | Documentos exigidos de todos os candidatos (cabeçalho) | EXATA | C | baixa | 1 | 1 | 1 | 0 | 0 |
| [LIB-0036](unidades/LIB-0036.md) | ~~Documento: identificação com foto~~ — desdobrada em LIB-0128, LIB-0143 | — | — | — | — | — | — | — | — |
| [LIB-0037](unidades/LIB-0037.md) | Documento: comprovante de CPF | SEMELHANTE | D | baixa | 1 | 1 | 0 | 1 | 1 |
| [LIB-0038](unidades/LIB-0038.md) | ~~Documento: diploma de graduação~~ — desdobrada em LIB-0129, LIB-0144 | — | — | — | — | — | — | — | — |
| [LIB-0039](unidades/LIB-0039.md) | Documento: certidão de quitação eleitoral | INÉDITA | D | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0040](unidades/LIB-0040.md) | Documento facultativo: requerimento de nome social | INÉDITA | D+C | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0041](unidades/LIB-0041.md) | Documentos exigidos dos candidatos de uma modalidade (cabeçalho) | PARAMETRIZÁVEL | C+D | baixa | 2 | 3 | 1 | 0 | 0 |
| [LIB-0042](unidades/LIB-0042.md) | Documento: autodeclaração étnico-racial conforme modelo | PARAMETRIZÁVEL | D | baixa | 1 | 1 | 1 | 1 | 0 |
| [LIB-0043](unidades/LIB-0043.md) | ~~Documento: laudo médico~~ — desdobrada em LIB-0130, LIB-0145 | — | — | — | — | — | — | — | — |
| [LIB-0067](unidades/LIB-0067.md) | Relação de anexos do Edital | PARAMETRIZÁVEL | A+D | média | 1 | 1 | 1 | 0 | 0 |
| [LIB-0098](unidades/LIB-0098.md) | Documento: comprovante de experiência no magistério | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0099](unidades/LIB-0099.md) | Documentos passíveis de pontuação (facultativo) | INÉDITA | D+C | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0100](unidades/LIB-0100.md) | Documento: declaração de disponibilidade conforme modelo | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0101](unidades/LIB-0101.md) | Documentos exigidos dos candidatos a um Perfil (cabeçalho) | PARAMETRIZÁVEL | C+B+D | baixa | 0 | 2 | 1 | 0 | 0 |
| [LIB-0102](unidades/LIB-0102.md) | Documento: comprovante de residência no município do polo | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0103](unidades/LIB-0103.md) | Documento: diploma de mestrado | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0104](unidades/LIB-0104.md) | Documento: autodeclaração de identidade de gênero conforme modelo | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0128](unidades/LIB-0128.md) | Documento: identificação com foto (forma de envio) | SEMELHANTE | D | baixa | 1 | 0 | 1 | 0 | 0 |
| [LIB-0129](unidades/LIB-0129.md) | Documento: diploma de graduação ou documento de conclusão com histórico | SEMELHANTE | D | baixa | 1 | 0 | 1 | 0 | 0 |
| [LIB-0130](unidades/LIB-0130.md) | Documento: laudo médico recente com CID | INÉDITA | D | média | 1 | 0 | 0 | 0 | 0 |
| [LIB-0143](unidades/LIB-0143.md) | Documento: identificação com foto, entre os documentos enumerados | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0144](unidades/LIB-0144.md) | Documento: diploma de graduação, sem substituto | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0145](unidades/LIB-0145.md) | Documento: laudo de especialista com CID e limitações funcionais | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0191](unidades/LIB-0191.md) | Diplomas estrangeiros revalidados e traduzidos | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0192](unidades/LIB-0192.md) | Documentos estrangeiros com tradução juramentada | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0193](unidades/LIB-0193.md) | Documento: identificação entre os documentos enumerados pelo Cefor | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0194](unidades/LIB-0194.md) | Documento: comprovante de votação ou certidão de quitação eleitoral | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0195](unidades/LIB-0195.md) | Documento: certidão de nascimento ou casamento | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0196](unidades/LIB-0196.md) | Documento: certidão de nascimento, casamento ou averbação; união estável exige nascimento | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0197](unidades/LIB-0197.md) | Documento: comprovação do ensino médio completo | INÉDITA | D | baixa | 0 | 0 | 0 | 0 | 1 |
| [LIB-0198](unidades/LIB-0198.md) | Documento: situação militar, para candidatos do sexo masculino | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0199](unidades/LIB-0199.md) | Documento: diploma, declaração de conclusão com histórico, ou declaração da data de colação | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0200](unidades/LIB-0200.md) | Documento: Requerimento de Matrícula (anexo) preenchido, com a declaração marcada | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0201](unidades/LIB-0201.md) | Documento: Requerimento de Matrícula; preenchimento incorreto indefere sem recurso | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0202](unidades/LIB-0202.md) | Documento: declaração de pertencimento da comunidade indígena | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0203](unidades/LIB-0203.md) | Documento: declaração da Funai ou comprovante de residência em comunidade indígena | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0204](unidades/LIB-0204.md) | Documento: laudo de especialista com espécie, grau, CID, causa e dados do médico | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0205](unidades/LIB-0205.md) | Documento: autodeclaração de pessoa com deficiência (anexo) | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |

### AFI — Ações afirmativas e acessibilidade

Verificação da autodeclaração e atendimento à pessoa com deficiência.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0044](unidades/LIB-0044.md) | ~~Convocação para verificação da autodeclaração (heteroidentificação)~~ — desdobrada em LIB-0131, LIB-0146 | — | — | — | — | — | — | — | — |
| [LIB-0045](unidades/LIB-0045.md) | Efeito do indeferimento da autodeclaração | SEMELHANTE | D | média | 1 | 0 | 0 | 1 | 0 |
| [LIB-0105](unidades/LIB-0105.md) | Critério fenotípico exclusivo da verificação | SEMELHANTE | D | alta | 0 | 1 | 0 | 1 | 0 |
| [LIB-0106](unidades/LIB-0106.md) | Efeito do não comparecimento à verificação | SEMELHANTE | D | média | 0 | 1 | 0 | 1 | 0 |
| [LIB-0107](unidades/LIB-0107.md) | Atendimento especializado à pessoa com deficiência | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0131](unidades/LIB-0131.md) | Verificação da autodeclaração: só os sorteados para vagas reservadas | INÉDITA | D | alta | 1 | 0 | 0 | 0 | 0 |
| [LIB-0146](unidades/LIB-0146.md) | Heteroidentificação de todos os autodeclarados pretos ou pardos | SEMELHANTE | D | alta | 0 | 1 | 0 | 1 | 0 |
| [LIB-0147](unidades/LIB-0147.md) | Convocação para a heteroidentificação com 48 horas de antecedência (regra na descrição de Evento) | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0171](unidades/LIB-0171.md) | Definição de PPI pelas categorias do IBGE | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0172](unidades/LIB-0172.md) | Definição de pessoa com deficiência pela LBI | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0173](unidades/LIB-0173.md) | Normas que definem quem é pessoa com deficiência no certame | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0174](unidades/LIB-0174.md) | Categorias de deficiência elegíveis à reserva (definições legais) | ESPECIALIZADA | D | alta | 0 | 0 | 0 | 2 | 0 |
| [LIB-0206](unidades/LIB-0206.md) | Verificação da autodeclaração como etapa obrigatória para PPI | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0207](unidades/LIB-0207.md) | Competência da comissão local e meios da verificação | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0208](unidades/LIB-0208.md) | Comunicações da comissão por listagem de deferidos e indeferidos | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0210](unidades/LIB-0210.md) | Videoconferência justificada pela pandemia | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0211](unidades/LIB-0211.md) | Protocolos de segurança na verificação | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0212](unidades/LIB-0212.md) | Heteroidentificação conforme a Resolução CS 61/2019 | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0213](unidades/LIB-0213.md) | Nova verificação a qualquer tempo, com perda do vínculo | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0215](unidades/LIB-0215.md) | Heteroidentificação de menor: responsável presente | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0216](unidades/LIB-0216.md) | Acompanhamento por servidor na falta do responsável | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0217](unidades/LIB-0217.md) | Documento original com foto na entrevista | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0218](unidades/LIB-0218.md) | Requisitos técnicos para a entrevista por videoconferência | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0219](unidades/LIB-0219.md) | Iluminação adequada na entrevista | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0220](unidades/LIB-0220.md) | Roupas sem estampa e sem acessórios na entrevista | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0221](unidades/LIB-0221.md) | Sem maquiagem na entrevista | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0222](unidades/LIB-0222.md) | Acessar a sala até 5 minutos antes | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0223](unidades/LIB-0223.md) | Passos para entrar e configurar a sala de videoconferência | ESPECIALIZADA | D | alta | 0 | 0 | 0 | 2 | 0 |
| [LIB-0224](unidades/LIB-0224.md) | Falha de conexão do candidato: três tentativas e entrevista pendente | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0225](unidades/LIB-0225.md) | Queda de conexão de mais de 10 minutos: entrevista cancelada | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0226](unidades/LIB-0226.md) | Justificar a ausência em até 24 horas, com o print | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0227](unidades/LIB-0227.md) | Nova convocação só com justificativa | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0228](unidades/LIB-0228.md) | Entrevista gravada em áudio e vídeo | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0229](unidades/LIB-0229.md) | Hipóteses de indeferimento da autodeclaração de preto ou pardo | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0230](unidades/LIB-0230.md) | Indeferido pela ausência de características fenotípicas permanece na ampla | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0231](unidades/LIB-0231.md) | Verificação do candidato indígena por análise documental | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0232](unidades/LIB-0232.md) | Documentação do indígena entregue na inscrição | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0233](unidades/LIB-0233.md) | Resultado da verificação do indígena em listagem | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0234](unidades/LIB-0234.md) | Hipóteses de indeferimento da autodeclaração indígena | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0235](unidades/LIB-0235.md) | Verificação da pessoa com deficiência por equipe multiprofissional | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0277](unidades/LIB-0277.md) | Entrevista com o Napne para o candidato PcD classificado | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0278](unidades/LIB-0278.md) | Procurar o Napne se não houver contato | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |

### ETA — Etapas de avaliação

Fichas das Etapas: caráter, peso, nota, resultado e datas.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0046](unidades/LIB-0046.md) | Etapa decisória (ficha) | PARAMETRIZÁVEL | A+B+D | média | 1 | 1 | 1 | 0 | 0 |
| [LIB-0108](unidades/LIB-0108.md) | Etapa pontuada (ficha) | PARAMETRIZÁVEL | A+B+D | média | 0 | 1 | 2 | 0 | 0 |

### CRO — Cronograma

A tabela de Eventos e cada tipo de Evento.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0049](unidades/LIB-0049.md) | Cronograma: abertura da tabela | PARAMETRIZÁVEL | A | média | 1 | 1 | 1 | 1 | 1 |
| [LIB-0050](unidades/LIB-0050.md) | Evento: período de inscrições | PARAMETRIZÁVEL | B+D | baixa | 1 | 1 | 1 | 1 | 1 |
| [LIB-0051](unidades/LIB-0051.md) | Evento: divulgação da relação de participantes do sorteio | PARAMETRIZÁVEL | B+D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0052](unidades/LIB-0052.md) | Evento: sorteio público | PARAMETRIZÁVEL | B+D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0053](unidades/LIB-0053.md) | Evento: divulgação da ordem do sorteio | PARAMETRIZÁVEL | B+D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0054](unidades/LIB-0054.md) | Evento: análise documental | PARAMETRIZÁVEL | B+D | baixa | 1 | 1 | 0 | 0 | 0 |
| [LIB-0055](unidades/LIB-0055.md) | Evento: resultado preliminar | PARAMETRIZÁVEL | B+D | baixa | 1 | 3 | 0 | 2 | 1 |
| [LIB-0056](unidades/LIB-0056.md) | Evento: prazo de recurso | PARAMETRIZÁVEL | B+D | baixa | 1 | 4 | 0 | 2 | 1 |
| [LIB-0057](unidades/LIB-0057.md) | Evento: resultado final | PARAMETRIZÁVEL | B+D | baixa | 1 | 1 | 1 | 1 | 1 |
| [LIB-0058](unidades/LIB-0058.md) | Evento: divulgação das matrículas homologadas | PARAMETRIZÁVEL | B+D | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0059](unidades/LIB-0059.md) | Evento: início das aulas | PARAMETRIZÁVEL | B+D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0111](unidades/LIB-0111.md) | Evento: publicação do Edital | PARAMETRIZÁVEL | B+D | baixa | 0 | 1 | 0 | 1 | 1 |
| [LIB-0112](unidades/LIB-0112.md) | Evento: prazo para impugnação do Edital | PARAMETRIZÁVEL | B+D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0113](unidades/LIB-0113.md) | Evento: homologação das inscrições | PARAMETRIZÁVEL | B+D | baixa | 0 | 2 | 0 | 0 | 0 |
| [LIB-0114](unidades/LIB-0114.md) | Evento: realização de avaliação | PARAMETRIZÁVEL | B+D | baixa | 0 | 1 | 1 | 0 | 0 |
| [LIB-0115](unidades/LIB-0115.md) | Evento: verificação da autodeclaração | PARAMETRIZÁVEL | B+D | baixa | 0 | 1 | 0 | 1 | 0 |
| [LIB-0116](unidades/LIB-0116.md) | Evento: curso de formação dos convocados | PARAMETRIZÁVEL | B+D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0117](unidades/LIB-0117.md) | Evento: início das convocações | PARAMETRIZÁVEL | B+D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0289](unidades/LIB-0289.md) | Evento: publicação da situação das inscrições | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0290](unidades/LIB-0290.md) | Evento: link da transmissão ou da gravação do sorteio | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0291](unidades/LIB-0291.md) | Evento: resultado dos recursos | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 2 | 1 |
| [LIB-0292](unidades/LIB-0292.md) | Evento: publicação da convocação para a verificação | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0293](unidades/LIB-0293.md) | Evento: aula inaugural | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 0 |

### REC — Recursos

Como recorrer, contra o quê e o que não se admite; texto livre.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0060](unidades/LIB-0060.md) | ~~Recurso: objeto, prazo e canal (texto livre)~~ — desdobrada em LIB-0132, LIB-0148 | — | — | — | — | — | — | — | — |
| [LIB-0061](unidades/LIB-0061.md) | ~~Recurso: vedação de outros canais e de recurso fora do prazo~~ — desdobrada em LIB-0133, LIB-0149 | — | — | — | — | — | — | — | — |
| [LIB-0118](unidades/LIB-0118.md) | Vedação de envio de documentos na fase recursal | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0132](unidades/LIB-0132.md) | Recurso contra o resultado preliminar da análise documental: prazo e canal | INÉDITA | D | média | 1 | 0 | 0 | 0 | 0 |
| [LIB-0133](unidades/LIB-0133.md) | Recurso: não se aceitam por e-mail nem fora do prazo | INÉDITA | D | baixa | 1 | 0 | 0 | 0 | 0 |
| [LIB-0148](unidades/LIB-0148.md) | Canal e prazos de todos os recursos (formulário eletrônico) | SEMELHANTE | D | média | 0 | 1 | 0 | 1 | 1 |
| [LIB-0149](unidades/LIB-0149.md) | Recurso: não se aceita forma diferente da prevista | SEMELHANTE | D | baixa | 0 | 1 | 0 | 1 | 1 |
| [LIB-0153](unidades/LIB-0153.md) | Abertura de prazo recursal anunciada na descrição de Evento | INÉDITA | D | média | 0 | 0 | 1 | 0 | 0 |
| [LIB-0209](unidades/LIB-0209.md) | Recurso contra a comissão local, julgado pela comissão permanente | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0249](unidades/LIB-0249.md) | Recurso do suplente com documentação indeferida | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0251](unidades/LIB-0251.md) | Recurso somente contra o resultado preliminar | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0252](unidades/LIB-0252.md) | Recurso somente contra a verificação da autodeclaração e o resultado preliminar da documentação | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0253](unidades/LIB-0253.md) | O recurso não garante alteração do resultado | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0254](unidades/LIB-0254.md) | Recurso sem fundamentação é indeferido | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0255](unidades/LIB-0255.md) | Recurso fora do prazo não é aceito | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0256](unidades/LIB-0256.md) | Onde sai o resultado do recurso | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |

### CON — Convocação e matrícula

Chamada, suplência, matrícula e o Requerimento de Matrícula.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0062](unidades/LIB-0062.md) | ~~Convocação de suplentes em caso de desistência~~ — desdobrada em LIB-0134, LIB-0150 | — | — | — | — | — | — | — | — |
| [LIB-0063](unidades/LIB-0063.md) | Matrícula a partir da documentação da inscrição | SEMELHANTE | D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0064](unidades/LIB-0064.md) | Momento de envio do Requerimento de Matrícula | EXATA | C | baixa | 1 | 0 | 1 | 0 | 0 |
| [LIB-0065](unidades/LIB-0065.md) | ~~Declaração de veracidade do Requerimento de Matrícula~~ — desdobrada em LIB-0135, LIB-0154 | — | — | — | — | — | — | — | — |
| [LIB-0119](unidades/LIB-0119.md) | Convocação por mensagem e prazo de manifestação | INÉDITA | D | baixa | 0 | 1 | 0 | 0 | 0 |
| [LIB-0134](unidades/LIB-0134.md) | Convocação de suplentes quando há desistência | SEMELHANTE | D | baixa | 1 | 0 | 0 | 1 | 1 |
| [LIB-0135](unidades/LIB-0135.md) | Declaração de veracidade do Requerimento: cancelamento por falsidade | INÉDITA | C+D | média | 1 | 0 | 0 | 0 | 0 |
| [LIB-0150](unidades/LIB-0150.md) | Não manifestação no prazo: desistência presumida e substituição | INÉDITA | D | média | 0 | 1 | 0 | 0 | 0 |
| [LIB-0154](unidades/LIB-0154.md) | Declaração de veracidade do Requerimento: cancelamento por inexatidão ou falsidade | INÉDITA | C+D | média | 0 | 0 | 1 | 0 | 0 |
| [LIB-0250](unidades/LIB-0250.md) | Suplentes podem ser chamados para nova turma na validade | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0257](unidades/LIB-0257.md) | Só se efetiva a matrícula homologada | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0258](unidades/LIB-0258.md) | Cancelamento por documentação falsa, com responsabilização | EXATA | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0259](unidades/LIB-0259.md) | Cancelamento de quem não participa da verificação | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0260](unidades/LIB-0260.md) | Matrículas não aceitas são canceladas | SEMELHANTE | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0261](unidades/LIB-0261.md) | Vedação de matrícula simultânea em mais de dois cursos de especialização | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0262](unidades/LIB-0262.md) | Vedação de matrícula simultânea no Ifes por nível de curso | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0263](unidades/LIB-0263.md) | Matrícula simultânea: limite de dois cursos e exceções | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0264](unidades/LIB-0264.md) | Quem já está matriculado deve optar | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0265](unidades/LIB-0265.md) | Desligamento automático de outro lato sensu ao optar | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0266](unidades/LIB-0266.md) | Convocação de indeferidos para regularizar, se sobrarem vagas | EXATA | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0267](unidades/LIB-0267.md) | Prazo de 2 dias úteis para regularizar, a partir do e-mail | SEMELHANTE | D | média | 0 | 0 | 0 | 1 | 1 |
| [LIB-0268](unidades/LIB-0268.md) | Falta na primeira semana sem justificativa: desistência | INÉDITA | D | média | 0 | 0 | 0 | 0 | 1 |
| [LIB-0269](unidades/LIB-0269.md) | Sem acesso ao AVA em 5 dias: desistência | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0270](unidades/LIB-0270.md) | Login e senha por e-mail até um dia antes do curso | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0271](unidades/LIB-0271.md) | Contato se o login não chegar | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0272](unidades/LIB-0272.md) | Responsabilidade de acompanhar o e-mail, inclusive o spam | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0273](unidades/LIB-0273.md) | Depois da homologação, a pessoa é aluna e muda de atendimento | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0274](unidades/LIB-0274.md) | Assuntos acadêmicos com a coordenação ou a secretaria | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0275](unidades/LIB-0275.md) | Declarações de matrícula, frequência ou conclusão | SEMELHANTE | D | baixa | 0 | 0 | 0 | 2 | 0 |
| [LIB-0276](unidades/LIB-0276.md) | Fim da atuação da equipe de seleção | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |

### ANX — Anexos: formulários, declarações e termos

Os modelos que o candidato preenche e assina; nos editais reais, dentro do PDF.

| ID | Unidade | Classificação | Origem | Complex. | 91 | 92 | 01 | 28 | 59 |
|---|---|---|---|---|---|---|---|---|---|
| [LIB-0295](unidades/LIB-0295.md) | Cabeçalho ou rodapé institucional de anexo | SEMELHANTE | D | baixa | 0 | 0 | 0 | 2 | 0 |
| [LIB-0296](unidades/LIB-0296.md) | Requerimento de Matrícula: campos do formulário | EXATA | D | alta | 0 | 0 | 0 | 1 | 1 |
| [LIB-0297](unidades/LIB-0297.md) | Requerimento: o pedido de matrícula no curso | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 1 | 1 |
| [LIB-0298](unidades/LIB-0298.md) | Declaração de veracidade do Requerimento (anexo), com autorização de averiguação | EXATA | D | alta | 0 | 0 | 0 | 1 | 1 |
| [LIB-0299](unidades/LIB-0299.md) | Autodeclaração étnico-racial: identificação e opção | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0300](unidades/LIB-0300.md) | Autodeclaração: ciência das consequências da falsidade | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0301](unidades/LIB-0301.md) | Autodeclaração: ciência de convocação a qualquer tempo | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0302](unidades/LIB-0302.md) | Autodeclaração PcD: identificação e CID | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0303](unidades/LIB-0303.md) | Autodeclaração PcD: o laudo atesta espécie e grau | INÉDITA | D | baixa | 0 | 0 | 0 | 1 | 0 |
| [LIB-0304](unidades/LIB-0304.md) | Declaração de pertencimento étnico (formulário da comunidade) | INÉDITA | D | alta | 0 | 0 | 0 | 1 | 0 |
| [LIB-0305](unidades/LIB-0305.md) | Termo de dados: o que o documento registra | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0306](unidades/LIB-0306.md) | Termo de dados: a opção de consentir | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0307](unidades/LIB-0307.md) | Termo de dados: a opção de não consentir | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0308](unidades/LIB-0308.md) | Termo de dados: quais dados | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0309](unidades/LIB-0309.md) | Termo de dados: para quê | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0310](unidades/LIB-0310.md) | Termo de dados: compartilhamento | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0311](unidades/LIB-0311.md) | Termo de dados: segurança e incidentes | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0312](unidades/LIB-0312.md) | Termo de dados: término e eliminação | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0313](unidades/LIB-0313.md) | Termo de dados: direitos do titular | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0314](unidades/LIB-0314.md) | Termo de dados: revogação do consentimento | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0315](unidades/LIB-0315.md) | Termo de dados: recusar não anula o direito à matrícula | INÉDITA | D | média | 0 | 0 | 0 | 1 | 0 |
| [LIB-0316](unidades/LIB-0316.md) | Local, data e assinatura do formulário | PARAMETRIZÁVEL | D | baixa | 0 | 0 | 0 | 2 | 1 |

## Variantes previstas no código e não observadas

O compositor pode escrever frases que o corpus não exercitou. Não viraram unidade, mas uma rodada futura
que as encontre sabe de onde vêm (`backend/processo_seletivo/publicacoes/infrastructure/pdf.py`,
`publicacoes/domain/vocabulario_da_regra.py`).

| Variante | Par de | Fonte |
|---|---|---|
| “Não caberá recurso contra o resultado de …” — **negativa expressa** | LIB-0028 | `_janela_recursal` |
| “Caberá recurso no prazo de …, contados da divulgação do resultado.” (marco sem nome) | LIB-0028 | `_janela_recursal` |
| “participam apenas as inscrições habilitadas na Etapa …” | LIB-0027 | `_habilitacao_ao_sorteio` |
| “Método: próprio deste marco” / “— diverge do comum deste Edital” / “o comum a este Edital, descrito no item N.” | LIB-0026 | `_origem_do_metodo`, `_marcos` |
| “média ponderada”, “pela soma dos pesos”, “meio para par”, “truncamento”, “sem casas decimais”, “(não pontua)” | LIB-0091 | `_combinacao`, `_arredondamento` |
| “Progride … o 1 (um) primeiro” | LIB-0092 | `_regra_de_corte` |
| “Cada candidato poderá ter no máximo N inscrições enviadas neste Edital.” | LIB-0034 | `teto_de_inscricoes` |
| “O Requerimento de Matrícula será enviado quando o candidato for convocado.” | LIB-0064 | `MOMENTO_DO_REQUERIMENTO` |
| “Dos candidatos ao perfil X concorrentes na modalidade Y:” | LIB-0101, LIB-0041 | `_titulo_do_grupo` |
| “No Perfil X, …” / “Nos Perfis X e Y, …” antes de reversão e convocação | LIB-0015, LIB-0078, LIB-0017, LIB-0079 | `_frases_consolidadas` |
| “maior pontuação na Etapa …” com “sem o valor, o critério não se aplica” | LIB-0094 | `vocabulario_da_regra.py` |

Duas seções do catálogo nunca saíram no corpus — Do Acesso ao Curso e Da Homologação da Matrícula. Os
títulos ficam cobertos por LIB-0005; o conteúdo, que é texto livre, pedirá unidades novas.

## Arquivos

- [`terminologia.md`](terminologia.md) — termos que pedem decisão de sinal antes de qualquer gravação.
- [`unidades/`](unidades/) — um arquivo por identificador, inclusive os desdobrados.
