# 015 — Ordenação e Classificação

Prompt do `/speckit-specify`. Revisado em 04/09/2026, depois da avaliação que apontou seis ajustes
e de três lacunas que a avaliação não viu.

**Frase que governa:**

> Dado um conjunto de participantes e uma regra publicada, o sistema produz a ordem entre eles, de
> modo reproduzível e auditável — e essa ordem é constituída por ato, não por consulta.

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- `doc/decisoes-pre-vertical.md` — as quatro decisões que esta spec consome, em especial **D-2**
  (fatos declarados pelo Edital, congelados na submissão)
- `doc/briefing-013-resultado-da-etapa.md` — os seis invariantes; esta feature herda **I-2**
  (proveniência reprodutível), **I-3** (imutabilidade histórica) e **I-5** (autoridade)
- `doc/achados-editais-externos.md` — os Editais são EVIDÊNCIA, nunca especificação
- `specs/013-consolidacao-resultado-etapa/spec.md` §5 — o que a 013 excluiu e por quê
- `specs/004-enderecamento-normativo-estavel/spec.md` — como se aponta para item do conteúdo
  publicado sem depender de posição
- `backend/processo_seletivo/resultados/` — o que existe: `ResultadoEtapa`, progressão,
  compatibilidade, prontidão
- `backend/processo_seletivo/editais/models/perfis.py` — `ModalidadeConcorrencia` e
  `RegraNormativa` **já existem**, e a segunda tem `call_rules` reservado e nunca consumido

## A DISTINÇÃO CENTRAL, QUE A SPEC NÃO PODE PERDER

Ordenação/classificação é **uma única capacidade de domínio**, exercida em **marcos
classificatórios identificáveis** do mesmo certame. Cada emissão declara qual marco realiza e qual
regra publicada a governou.

```
ordem sobre o resultado de UMA Etapa     → insumo do corte da 014
ordem sobre a combinação de N Etapas     → classificação final
```

Não são coisas de naturezas diferentes; são o mesmo ato, com regras de origem distintas. Uma spec
desenhada só para o produto final nascerá sabendo compor duas Etapas e sem saber ordenar dentro de
uma — e a 014 cobrará metade dela depois.

**O marco precisa de identidade estável**, e não de um enum `INTERMEDIARIA`/`FINAL` inventado aqui.
Para o mesmo Processo e Perfil pode haver ordenação pós-títulos, outra pós-entrevista e outra
depois de recurso; sem identidade do marco não há unicidade do ato vigente, não há sucessão entre
emissões, não há obsolescência endereçável e não há sobre o que a 017 publicar ou a 018 recorrer. A
identidade é do marco declarado no conteúdo publicado, endereçado pelo padrão da 004 — nunca por
posição na lista.

Evidência de que os dois marcos são atos plenos, e não um deles um rascunho: há Editais que
publicam a ordem intermediária, recebem recurso sobre ela e a republicam antes de convocar para a
Etapa seguinte.

## CALCULAR NÃO É EMITIR

```
calcular(entradas, regra_versionada)  →  proposta determinística
                                      →  EMITIR (ato autorizado)
                                      →  snapshot oficial imutável
```

A computação é pura e reproduzível. O artefato é histórico, versionado e emitido por quem tem
autoridade — nunca regenerado em silêncio quando a tela abre.

Entrada nova torna o snapshot vigente **OBSOLETO, não inválido**: alguém autorizado emite o
próximo. E a divergência entre o computado e o vigente precisa ser OBSERVÁVEL na interface —
capacidade que o domínio sustenta e nenhuma interface alcança não está entregue (Princípio VI).

## O UNIVERSO CLASSIFICÁVEL, QUE DELIMITA A OBSOLESCÊNCIA

Nem todo `ResultadoEtapa` novo obsoleta toda ordem emitida. O ato declara o **universo** sobre o
qual foi produzido, e só mudança relevante *nesse* universo torna o vigente desatualizado.

O universo é, no mínimo: Processo, Perfil (e o recorte de oferta que a 016 depois refinará), o
marco, os participantes elegíveis àquele marco e os Resultados antecedentes considerados. A spec
precisa dizer, para cada um, o que conta como mudança relevante — e precisa responder à pergunta
que a 013 deixou aberta: quem foi `ELIMINADA` em Etapa anterior **entra ou não entra** na população
ordenada, e se entra, em que posição. Resultado tardio, resultado revisto e múltiplos Perfis no
mesmo Edital são os casos que forçam a resposta.

## DESEMPATE

O desempate não é uma sequência hardcoded nem um único campo da Etapa: é **conteúdo normativo
estruturado**, composto por critérios **ordenados e parametrizados** que o motor interpreta
deterministicamente, aplicados na ordem declarada.

O motor conhece tipos executáveis de critério — não há como executar o que não se sabe interpretar.
O que ele **não** pode é decidir quais critérios existem, em que ordem se aplicam ou qual parâmetro
cada um recebe: isso viaja no snapshot, é retificável e responde pela mesma cadeia de vigência que
peso e nota mínima.

Os critérios consomem pontuação de **Etapa específica** — endereçada por identidade estável do
conteúdo publicado, no padrão da 004, como `ResultadoEtapa.etapa_id` já faz — e fatos do candidato
congelados na inscrição (D-2).

**O empate que sobrevive a todos os critérios declarados precisa ter desfecho explícito.** Esgotada
a lista publicada, o sistema **não inventa ordenação**: nem por UUID, nem por nome, nem por
horário de criação, nem pela ordem que o banco devolveu. O desfecho legítimo é declarar o empate
não resolvido, ou exigir mecanismo normativamente declarado — e a interface precisa mostrar qual
dos dois aconteceu.

## PROVENIÊNCIA

Toda ordem emitida identifica os Resultados de Etapa que entraram nela, a regra normativa vigente
que a governou e os valores usados em cada critério de desempate — de modo que a MESMA ordem seja
reproduzível a partir deles. Registrar o que foi usado e conseguir chegar de novo ao mesmo
resultado são coisas distintas, e a Constituição pede a segunda (I-2).

Disso decorre uma proibição, e não uma máquina de versões: **mudança futura na implementação não
pode alterar silenciosamente a reprodução de classificações históricas.** A spec não versiona
código-fonte por classificação; ela exige que a reprodução de um ato antigo continue chegando ao
mesmo resultado, e que qualquer mudança que a alteraria seja detectável.

## AUTORIDADE

Emitir é ato autorizado e auditável — I-5. A 015 **consome** o contrato institucional que já
existe: registra quem emitiu, sob qual autoria e em que instante, pelo mesmo caminho que
`resultado:consolidar` já percorre. Ela **não** inventa quem é a autoridade competente; a definição
concreta vem das capacidades já constituídas.

## O QUE ESTA SPEC PUBLICA, E O QUE ISSO CUSTA

A regra de classificação e a lista ordenada de critérios de desempate são **conteúdo publicado
novo**. Isso é exatamente o que a 013 excluiu no §5 — *"novo campo normativo para regra de
combinação; isso inclui esquema, elaboração, documento e catálogo de Retificação"* —, e a conta
vem inteira para cá:

- esquema canônico e elevação de `SCHEMA_VERSION` (hoje **6**, em `shared/canonical.py`), com
  caminho de leitura das versões anteriores;
- tela de elaboração própria;
- presença no documento publicado;
- entrada no catálogo de Retificação, endereçada por identidade estável.

**D-2 e D-3 também sobem a mesma versão**, e o documento das decisões recomenda planejá-las na
mesma leva. Feitas juntas, é uma elevação; feitas em specs separadas, são duas ou três, cada uma
com seu caminho de leitura. A spec precisa declarar essa dependência de planejamento, e não
descobri-la no `/plan`.

## O QUE JÁ EXISTE E NÃO DEVE SER REINVENTADO

`ModalidadeConcorrencia` **já existe** como modelo com identidade estável por Perfil, viaja no
conteúdo publicado como `competitionModalities`, é endereçada pela Retificação, restringe Documento
Exigido e é **escolhida pelo candidato na inscrição** (`Inscricao.modality_id`). `reserve_type`
(`LIMITED`/`UNLIMITED`) e `call_rules` também já existem, inertes.

O que não existe é **verificação de elegibilidade** à modalidade e **ocupação/remanejamento**. Logo,
a modalidade que a 015 e a 014 leem é **declarada e não verificada**, e a spec deve dizê-lo com
essas palavras. A 016 estrutura ocupação, concorrência entre modalidades e remanejamento; a
verificação (heteroidentificação) é mecanismo próprio, com comissão, sessão, comparecimento e
instância recursal, e entra como spec separada.

## FORA DE ESCOPO — cada um é feature própria

- corte por alvo e progressão (014)
- vagas, modalidades, cotas, reserva, remanejamento, ocupação (016)
- publicação de resultado, preliminar ou definitivo (017)
- recurso e superação de atos (018)
- convocação, chamadas e suplência (019)
- verificação de elegibilidade a modalidade — heteroidentificação, spec própria
- barema estruturado (D-4: fora do primeiro vertical, por decisão)
- **ordem produzida fora do sistema e importada — o sorteio.** Não por escolha de escopo, mas por
  dependência: o mecanismo sorteio não existe na 013, que hoje só produz `ResultadoEtapa` a partir
  de Avaliação, e D-1 acrescenta apenas a Ocorrência. Não há Resultado de sorteio para ordenar. A
  consequência precisa ficar escrita na spec, e não descoberta depois: **o Edital 57/2026, que é um
  dos dois em vista, não é executável pela 015 enquanto o mecanismo sorteio não existir.** O
  briefing da 013 já reserva a prontidão dele — *"a ordem está importada e homologada"* —, e a
  frase que governa esta feature não pode ser lida como se a 015 já a atendesse.

## DEPENDÊNCIA QUE PRECISA CAIR ANTES OU JUNTO

**D-2 — fatos declarados pelo Edital.** Sem eles não há desempate por idade nem por tempo de
experiência, e a 015 nasce inexecutável para os Editais em vista. A coleta é território da 009; o
congelamento acontece na submissão, contra a `versao_aceita`.

## O TESTE QUE A SPEC PRECISA PASSAR

A frase que governa a feature tem de fazer sentido sem citar Edital nenhum.

- "Põe os participantes em ordem segundo uma regra publicada" — passa.
- "Calcula a média de títulos e entrevista" — reprova.
