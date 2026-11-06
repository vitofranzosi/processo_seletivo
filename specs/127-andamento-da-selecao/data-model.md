# Data model: Andamento da seleção (127)

**Nada é persistido.** Nenhuma tabela, coluna, migration nem estado de domínio (FR-4050, FR-4123). Tudo
abaixo é derivado na requisição e descartado depois dela.

## Situação (constante de apresentação)

| Valor | Rótulo | Sinal | Entra no nível 1 |
|---|---|---|---|
| `feito` | Feito | ✓ | não |
| `obsoleto` | Obsoleto | ↺ | sim |
| `pendente` | Pendente | ● | sim |
| `aguarda` | Aguarda | ◷ | sim |
| `impedido` | Impedido | ⊘ | sim |
| `depois` | Depois | · | não |
| `nao_se_aplica` | Não se aplica | — | não |

## Expectativa

`esperada` · `condicional` · `sem_efeito` (D-010). A facultativa não é derivada: ela não entra.

## Responsável (papel)

| Chave | Texto | É "você" quando |
|---|---|---|
| `conduz` | quem conduz a seleção | `pode_gerir_comissao(ator, processo)` |
| `publica` | quem publica resultado | `ator.can("resultado:publicar")` |
| `avalia` | os avaliadores alocados | a carga de Minhas Etapas tem pendente nesta Etapa |
| `julga` | quem julga recursos | `ator.can("recurso:julgar")` |
| `retifica` | quem elabora Retificações | `acoes.pode_retificar(edital, ator)` |
| `confere` | quem conduz ou confere documentos | conduz, ou alocado à conferência do Perfil |
| `retificacao` | o papel que a Retificação espera | `meu_ato` da `103` |
| `` (mundo) | — | nunca: *Aguarda* espera um fato, e não uma pessoa |

## Celula

| Campo | Tipo | Nota |
|---|---|---|
| `situacao` | Situação | |
| `natureza` | texto | relação, semente, sorteio, ordem, corte, apuração, resultado, convocação, conferência, distribuir, avaliar, consolidar, reavaliar |
| `ato` | texto | o verbo da tela ("Congelar a relação") |
| `responsavel` | Responsável | |
| `nota` | texto | "ninguém concorreu", "preliminar", "8 de 12 consolidadas" |
| `razao` | texto | para *Aguarda*, *Impedido*, *Depois*, *Não se aplica*, com a frase da tela |
| `url` | texto | vazio para quem não abre a tela |
| `expectativa` | Expectativa | |
| `ate` | datetime? | prazo (vencimento, fim do período, extração) |
| `contagem` | int? | quantas inscrições/convocações o ato alcança |

Uma Etapa pode ter **várias** células-providência (distribuir, avaliar, consolidar), e por isso a
célula do nível 2 é o resumo delas (a pior situação, com a nota da contagem), e as providências são a
lista completa.

## Ponto

| Campo | Nota |
|---|---|
| `tipo` | `etapa`, `relacao`, `semente`, `sorteio`, `ordem`, `corte`, `apuracao`, `resultado`, `convocacao` |
| `titulo` | o nome da Etapa, ou o do ato |
| `grupo` | "Etapas · valem para o Perfil", "Marco · por sorteio", "Marco · por pontuação", "Etapa governada pela faixa", "Sem efeito no GPS" |
| `marco` | o marco do conteúdo, nos pontos de marco |
| `etapa` | a Etapa do conteúdo, nos pontos de Etapa |
| `celulas` | `{lista_id: Celula}`; a Etapa e a semente têm a mesma célula em todas as listas |

## PerfilNoAndamento

`perfil`, `forma` ("por sorteio", "por pontuação", "por sorteio e por pontuação"), `listas`
(`[(lista_id, rótulo)]` da derivação única), `pontos`, `inscritos` (submetidas no Perfil),
`resumo` (o texto em palavras), `destinos` (os do cartão "Classificação", por marco),
`matricula_fora` (bool, FR-4109).

## Providencia

A forma do `ObjetoDeTrabalho` da `104` mais: `situacao`, `responsavel`, `sua`, `expectativa`,
`razao`, `ate`, `listas` (as listas que a mesma providência cobre, D-016), `onde` ("Cefor ·
Ampla concorrência"), `marco_id`, `lista_id` (a primeira), `perfil_id`.

Chave de agrupamento: `(natureza, marco_id ou etapa_id, situacao, responsavel, ato)`.

## Atencao

`etapa` (nome) e `texto` ("está declarada no Edital, e nenhum ato do GPS depende do resultado dela").

## Andamento

`perfis`, `providencias` (na ordem fixa do nível 1), `atencoes`, `inscricoes` (a linha: aberta até /
encerrada em, enviadas), e as propriedades `total`, `suas`, `de_outros` (por papel), `em_espera`,
`mostradas` (5), `demais`, `nada_em_aberto` (e a frase do porquê).

## As regras, em uma linha cada (a referência do teste)

| Ponto | Ordem de avaliação das condições |
|---|---|
| Etapa | sem efeito → *Não se aplica*/"Atenção" · regra insuficiente → *Impedido* (e a avaliação de quem tem inscrição atribuída continua) · inscrições em curso → *Aguarda* · governada sem corte vigente → *Depois* · corte obsoleto → *Impedido* · sem participante → *Não se aplica* · reavaliação → *Obsoleto* · sem avaliador suficiente, entre as não consolidadas → *Pendente* distribuir · avaliação a concluir → *Pendente* avaliar · pronta → *Pendente* consolidar · todas consolidadas → *Feito* |
| Relação | congelada e diagnóstico → *Obsoleto* · congelada → *Feito* · habilitação não feita → *Depois* · projetados 0 → *Não se aplica* · inscrições em curso → *Aguarda* · congelar inviável → *Impedido* · *Pendente* |
| Semente | nenhuma relação congelada → *Depois* · ocorrência observada → *Feito* · cadeia consumida → *Impedido* · instante futuro → *Aguarda* · *Pendente* |
| Sorteio | relação *Não se aplica* → *Não se aplica* · relação ou semente não feitas → *Depois* · extração anterior ao congelamento → *Impedido* · sem sorteio → *Pendente* · indicador obsoleto → *Obsoleto* · *Feito* |
| Ordem (pontuação) | indicador feito/obsoleto → idem · Etapa lida não feita → *Depois* · *Pendente* |
| Corte | indicador *Não se aplica*/feito/obsoleto → idem · ordem não feita → *Depois* · *Pendente* |
| Etapa governada | (a regra da Etapa; governada sem corte → *Depois*) |
| Apuração | indicador *Não se aplica*/feito/obsoleto → idem · ordem não feita → *Depois* · marco que corta sem corte vigente → *Depois* (D-018) · governada em aberto → *Depois* · *Pendente* |
| Resultado | indicador obsoleto → *Pendente* de quem publica · feito definitivo → *Feito* · feito preliminar → aferição (*Pendente*/*Aguarda*/*Impedido*) · sem ordem → *Depois* · *Pendente* |
| Convocação | apuração ausente/obsoleta → *Depois* · forma não declarada → *Impedido* · pendentes/titulares/vencidos/conferência → *Pendente* · faixa seguinte/próxima da fila → *Pendente* condicional · prazo em curso → *Aguarda* · sem vaga e sem convocação → *Não se aplica* · *Feito* |
