# Data Model: Prévia interativa da classificação — fatia 1

**Nenhuma tabela, nenhuma migration, nenhuma coluna.** Tudo aqui existe só durante a resposta do
fragmento (FR-2234). As formas abaixo são dicionários Python, como o resto do domínio de
`classificacao`, e as chaves seguem as que `calcular_ordem` já usa para que a função extraída sirva aos
dois caminhos sem tradução.

## Cenário

Constante de domínio em `classificacao/domain/cenarios_da_previa.py`.

| Campo | Tipo | Regra |
|---|---|---|
| `chave` | texto | `sem_empate`, `criterios_sucessivos`, `empate_na_faixa`, `empate_nas_vagas`, `valor_ausente` (FR-2225) |
| `rotulo` | texto | o nome no seletor do painel |
| `descricao` | texto | o que foi construído para mostrar (FR-2226) |
| `ancora` | relativa | a posição em que a situação é plantada: última da faixa, última das vagas, `alvo − 1`, linhas fixas |

**Regras de geração** (R-005): determinística; depende só de `chave`, das Etapas enumeradas (com nota e
decisórias), da Etapa do marco, dos fatos declarados do Perfil e de `alvo`, `suplentes`, `vagas` (D-003,
FR-2205). Nenhum acaso, nenhum relógio.

## Candidato fictício

Gerado pelo cenário; é a forma de **inscrito** que `universo_classificavel.preparar` recebe, e por isso
é a mesma que o caminho oficial monta a partir do banco.

| Campo | Tipo | Regra |
|---|---|---|
| `inscricao_id` | texto | `F000`, `F001`… — nunca um UUID, para que não se confunda com inscrição real |
| `nome` | texto | da lista fixa de nomes fictícios; repetida com sufixo numérico acima de 26 |
| `modalidade_id` | texto ou nulo | **sempre nulo na fatia 1**; a porta da fatia 2 (D-008) |
| `resultados` | lista | um por Etapa enumerada: `{etapa_id, pontuacao, consequencia}`; Etapa com nota sem número quando o cenário a deixa ausente; Etapa decisória com `pontuacao` nula |
| `fatos` | dicionário | `{fato_id: data ou inteiro}`, um valor por fato declarado do Perfil; ausente quando o cenário remove |

**Validação**: nenhuma — é dado gerado. O que se valida é o **marco**, pela mesma aferição que a gravação
usaria; a prévia não acrescenta regra.

## Universo classificável

Saída de `universo_classificavel.preparar(marco, etapas, inscritos, *, recorte=None)`
([contrato](contracts/universo-classificavel.md)).

| Lista | Item | Origem |
|---|---|---|
| `classificaveis` | inscrito + `pontuacao` (Decimal, arredondada uma vez, ou nula em marco só de portas) + `consequencia="HABILITADA"` + `motivo=""` | `combinar` |
| `sem_posicao` | inscrito + `posicao=None`, `pontuacao=None`, `consequencia`, `motivo`, `empate_residual=False`, `separado_por=None` | eliminação mais recente, ou `SEM_PONTUACAO` |

As chaves são exatamente as de hoje em `calcular_ordem`; a equivalência compara as duas listas inteiras
(FR-2232).

## Prévia

Saída de `classificacao/application/previa.simular(...)`; a interface a transforma em painel.

| Campo | Tipo | Conteúdo |
|---|---|---|
| `cenario` | texto | a chave efetivamente usada |
| `ancora` | texto | onde o cenário plantou a situação, para o painel dizer |
| `fronteiras` | `(alvo, suplentes, vagas)` | as que posicionaram o cenário; o painel as devolve no próximo pedido para dizer que reposicionou (FR-2206) |
| `ordem` | lista | `ordenar_com_trajetoria(...)`: posição, `empate_residual`, `separado_por`, `trajetoria`, `grupo_da_pontuacao` |
| `sem_posicao` | lista | do universo classificável |
| `regra` | dicionário ou nulo | o `cutRule` digitado, normalizado por `faixa.normalizar` |
| `alvo`, `origem_do_alvo` | inteiro, texto | `faixa.alvo_apurado`; do quadro, a linha geral |
| `corte` | dicionário | `declarado`; `recusado` com `posicao` e `quantas`; ou `progrediram`, `excedentes`, `ultima`; `alternativo` (o outro desfecho, FR-2217); `sem_desfecho` com as duas consequências (FR-2216) |
| `aviso_das_vagas` | dicionário | `avaliado`, `para`, `posicao`, `quantas`, ou `motivo` de não avaliado |
| `faltas` | lista de texto | o que falta declarar; quando não vazia, nada mais é calculado (FR-2227) |

### Situação de cada linha (FR-2212)

| Situação | Quando |
|---|---|
| sem corte | o marco não declara regra |
| corte não emitido | `faixa.calcular` levantou `EmpateAtravessaOCorte`, ou o desfecho não está declarado e o empate atravessa |
| dentro do alvo | está entre os que progrediram, e a contagem até o grupo dele cabe no alvo |
| empate na fronteira do alvo | o grupo empatado dele começa dentro do alvo e termina fora |
| suplente | progrediu, além do alvo, sem empate na última posição da faixa |
| empate na última posição da faixa | algum membro do grupo está em `excedentes` — **o grupo inteiro** recebe a marca |
| fora da faixa | não progrediu |
| sem posição | está em `sem_posicao` |

A consequência (FR-2213) deriva da situação, da Etapa governada (`faixa.etapa_governada`) e da
continuação (`faixa.admite_continuacao`, mais o caso não declarado).
