# A Etapa que prevê duas avaliações publica um ato que não se consolida

**Data:** 2026-09-21
**Contra:** a `main` em `fa4b5b2`, com a `038` mesclada
**Origem:** conferência do [relatório longitudinal de 19/09](relatorio-longitudinal-produto-001-a-037-2026-09-19.md),
que nomeia *"divergência real entre duas avaliações da mesma inscrição"* entre as lacunas de
cobertura da §3. A investigação do achado mostrou que o problema não é o que aquele texto supõe.
**Natureza:** achado registrado, não corrigido. A correção é decisão de escopo, não desta entrega.

> **Este documento corrige uma afirmação minha.** O aviso que versionou o relatório longitudinal
> dizia que *"dois membros atribuídos à mesma inscrição concluem os dois"*. **Está errado:** a
> distribuição respeita o campo e recusa o excesso. O beco é outro, e é pior — ver §4.

## O que acontece

`Avaliações por inscrição` é campo de composição da Etapa — `evaluationsPerRegistration`, oferecido
em `_etapa.html:151` como `<input type="number" min="1">`, sem teto, com o texto de ajuda
*"Vazio: uma avaliação por inscrição."*

Declare **2**. O Edital publica. E a Etapa **nunca** se consolida:

```
o Edital prevê 2 avaliações para esta Etapa e não declara como combiná-las
```

O impedimento é da **Etapa inteira**, não de uma inscrição: `impedimento_da_regra`, em
`resultados/domain/regra.py`, devolve `REGRA_DE_COMBINACAO_AUSENTE`, e toda inscrição submetida
passa a `NAO_CONSOLIDAVEL` com essa frase. `test_etapa_de_leitura_multipla_impede_a_etapa_inteira`,
em `tests/integration/resultados/test_prontidao.py`, o prende: `contagens["prontas"] == 0`.

## Por que a recusa está certa

**Não é defeito de consolidação, e não se conserta lá.** O docstring de `impedimento_da_regra` põe
esse impedimento ao lado de outros dois — a Etapa eliminatória sem nota mínima publicada, e a
decisória sem efeito publicado — e diz o que os três têm em comum:

> *"aceitar 'eliminatória sem critério' ou 'decisória sem efeito' seria deixar a consequência para
> quem implementa decidir."*

Combinar duas avaliações por média, por maior, por menor ou por terceira leitura são **normas
diferentes**, com resultados diferentes para pessoas reais. Escolher uma seria o sistema publicando
regra que o Edital não publicou. A recusa é a Constituição funcionando.

**E a distribuição honra o campo corretamente.** Com `previstas = 2` ela atribui duas pessoas e
recusa a terceira, com a frase de `distribuicao.py:622`: *"Esta inscrição já tem as 2 avaliações que
o Edital declara para esta Etapa."* O trabalho **acontece**: dois avaliadores leem, pontuam e
concluem. É só depois que o sistema diz que não sabe o que fazer com o que produziu.

## O defeito é o momento, e de quem era evitá-lo

**Não existe campo para declarar como combinar.** Procurei: `avaliacoes_previstas` é lida em
`avaliacoes/` (distribuição, seletores) e em `resultados/` (regra, compatibilidade), e a gramática
de combinação que existe — `classificacao/domain/combinacao.py` — é a do **marco classificatório**,
que combina *Etapas entre si*, não *avaliações de uma mesma Etapa*. Não há valor de campo nenhum que
desbloqueie a Etapa. **É beco por construção, não configuração faltando.**

**E a `032` não vê.** A feature existe para antecipar inexequibilidade antes da publicação — é o que
lhe deu a subida de previsibilidade de 5 para 9. Mas `avaliacoes_previstas` **não aparece em
`editais/domain/validation.py`**, e a única verificação do campo na publicação é a faixa:
`Campo("evaluationsPerRegistration", int, admite_nulo=True, minimo=1)` — mínimo 1, **sem máximo**.

De modo que a cadeia é esta, e cada elo está individualmente certo:

| Etapa do percurso | O que faz | Veredito |
|---|---|---|
| composição | oferece o campo, sem teto e **sem aviso** | 🔴 o único texto de ajuda fala do vazio |
| validação da `032` | não conhece o campo | 🔴 é exatamente o que ela existe para pegar |
| publicação | aceita, e **é ato imutável** | 🟡 correto dado o resto |
| distribuição | atribui as 2 e recusa a 3ª, com frase clara | 🟢 |
| avaliação | duas pessoas leem, pontuam, concluem | 🟢 |
| consolidação | recusa a Etapa inteira, e diz por quê | 🟢 a recusa está certa |

**O custo é o da `032` invertida:** o sistema descobre a inexequibilidade depois do ato que não se
desfaz, e depois de gastar o trabalho de dois avaliadores.

## A saída existe, e cai no segundo beco

`("stages", "evaluationsPerRegistration"): retificavel()`, em `editais/domain/mutabilidade.py:452`.
Retificar de 2 para 1 desbloqueia a Etapa — e, se as duas conclusões já existirem, entrega a
inscrição ao outro impedimento, em `prontidao.py:589`:

```
há 2 avaliações concluídas onde o Edital prevê uma, e o sistema não escolhe qual vale
```

O comentário acima dessa linha declara a condição de alcance, e ele **está correto**:

> *"Só alcançável quando a quantidade prevista mudou depois das conclusões. Escolher uma seria o
> sistema decidindo qual nota vale."*

É a mesma recusa, coerente com a primeira. Mas o efeito prático é que a única saída da armadilha
**descarta o trabalho de um avaliador sem dizer qual**, e a inscrição fica parada até alguém reabrir
uma das avaliações pela presidência (`FR-074`) — ato que apaga uma leitura legítima para destravar
um Edital mal composto.

## Quantos Editais isso alcança

**Não medido.** A amostra real está fora do repositório (`~/Downloads`), e não a percorri. O que se
sabe: o Cenário 2 da [reauditoria de 16/09](auditoria-exploratoria-ux-2026-09-16.md) foi montado com
**dois avaliadores**, e o relatório longitudinal registra, na mesma linha, que *"divergência entre
avaliações não foi exercitada"*. Dupla leitura com terceira em caso de divergência é prática comum
em análise de títulos e em avaliação de projeto — **a pergunta de quantos Editais do Cefor a usam é
de governança, e é ela que decide a severidade.**

## Severidade e direção

**S3, e pode ser S4** — um Edital publicado cuja Etapa não pode ser concluída, descoberto depois do
ato imutável. É da mesma família que a
[Retificação que não acrescenta Modalidade](auditoria-de-convergencia-pos-038-2026-09-20.md) (`D-G5`),
que a convergência de 20/09 elegeu como terceiro investimento por ser *"a única coisa na lista que
descreve um Edital publicado sem conserto possível"*. Este descreve outro, e a convergência não o viu.

**Três direções, e a ordem importa.** A decisão é de quem governa o backlog.

1. **A mais barata, e que não decide nada de domínio:** ensinar a `032` o campo. Um Edital com
   `evaluationsPerRegistration > 1` recusa publicação, ou avisa na validação do conteúdo, nomeando
   entidade, falta e etapa de correção — a gramática que a `032` já usa. Fecha o beco sem inventar
   norma. **Enquanto a regra de combinação não existir, publicar 2 é publicar o que não se executa.**
2. **A honesta enquanto isso:** o campo na composição dizer o que seu valor > 1 produz. Hoje a ajuda
   só fala do vazio. Cuidado: a microcópia do cartão é proibida — vai para o `como-preencher` da
   etapa.
3. **A de domínio, se a instituição usa dupla leitura:** declarar a **regra de combinação** como
   norma publicada da Etapa — média, maior, menor, ou terceira leitura com faixa de divergência —, e
   só então consolidar. É spec própria, e precisa do Edital real na mão antes da abstração.

**O que não fazer:** afrouxar a recusa da consolidação. Escolher uma nota entre duas, ou tirar média
por padrão, publicaria norma que nenhum Edital escreveu, num ponto onde o resultado muda a ordem de
classificação de pessoas reais.
