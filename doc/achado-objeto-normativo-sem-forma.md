# Objeto normativo sem forma, sem semântica e sem leitor

**Encontrado em**: 13/09/2026, ao desenhar a spec 026 (contrato de mutabilidade normativa).

**Estado**: registro. **Não é prioridade**, e não deve ser derivado automaticamente em spec
seguinte — o princípio VI da Constituição é explícito: *"Limites registrados são insumo de
priorização, nunca a priorização em si."*

---

## O que é

Dois campos do conteúdo canônico publicado — `/profiles/…/classificationInformation` e
`/profiles/…/callInformation` — são `JSONField` livre no modelo
(`editais/models/perfis.py:36-37`), entram no snapshot publicado
(`publicacoes/application/publish_edital.py:215-216`), e:

- **nenhum canal os exibe** — nem o PDF, nem o portal, nem a consulta pública;
- **nenhum cálculo os lê** — a busca por leitores devolve apenas o ida-e-volta da autoria
  (`interface/forms.py:868-869`) e a emissão;
- **o domínio não declara forma para eles** — não há `Campo` em `validation.py`, não há esquema no
  `openapi.yaml`, e o conteúdo de dentro é o que cada Edital resolveu escrever.

Na amostra do `seed_demo` são objetos de uma chave de prosa — `{"criterio": "…"}`,
`{"forma": "…"}` — mas nada no sistema garante isso: o campo aceita lista, número e booleano.

## Por que virou achado

A spec 026 precisou classificar a mutabilidade de todo campo publicado, e estes dois não couberam
em nenhuma das quatro naturezas por uma razão que a classificação expôs: **não se pode dizer se um
campo é corrigível quando não se sabe o que ele afirma.**

A decisão registrada foi classificá-los como **não retificáveis**, com esta razão:

> O domínio não reconhece forma nem semântica para este objeto; portanto, não consegue determinar o
> que seria uma correção administrativa válida. Atribuir-lhe significado normativo exige decisão e
> especificação próprias, não uma Retificação.

**A ausência de consumidores é evidência do problema, não a justificativa.** Não é por faltar tela
que eles são irretificáveis — isso seria razão técnica, que a D-002 da 026 proíbe. É por não haver
o que se corrija: correção pressupõe saber o que seria o certo.

## A correção de uma afirmação anterior

[`doc/auditoria-exploratoria-ux-2026-09-13.md`](auditoria-exploratoria-ux-2026-09-13.md) afirmava,
sobre estes dois campos, que *"o candidato lê no Edital publicado"*. **É falso**, e a linha foi
corrigida. A afirmação foi inferida do nome do campo e do conteúdo do `seed_demo`, e não de
observação — o PDF não os compõe, e a única citação deles numa suíte de teste os passa vazios.

## A decisão que fica aberta

Uma das duas, e é decisão de produto:

1. **Declarar forma e destino observável.** Se o que eles carregam é norma que o candidato precisa
   ler, alguém precisa declarar a forma (como `callForm` tem: valor de lista fechada) e exibi-la. A
   partir daí a natureza volta a ser discutível, e provavelmente é **retificável** — a razão acima
   expira no dia em que o domínio souber o que o objeto afirma.
2. **Deixar de emiti-los no conteúdo canônico.** Se não são norma, estar no conteúdo publicado é o
   erro, e a correção é pararem de entrar nele — respeitados os degraus da versão canônica, que não
   admitem duas grafias para a ausência.

Enquanto nenhuma das duas acontecer, eles permanecem publicados, não lidos e não retificáveis — que
é o estado honesto, declarado por contrato e protegido por teste.

**Conferido ao fim da implementação da `026`, em 13/09/2026.** Os dois estão no contrato como não
retificáveis, com a razão acima; a tela de Retificação os declara entre o que não se corrige, no
bloco da seção de Perfis; e nenhum canal passou a exibi-los. O estado descrito aqui continua sendo
o estado real.

## Precedente relacionado

É o mesmo gênero do que o código já registra para `callForm`: *"o primeiro Edital publicado com a
forma declarada nasceria irretificável nela"*. Ali o problema era a ordem — decidir a mutabilidade
depois de publicar. Aqui é anterior: **publicar sem decidir o que o campo significa**.
