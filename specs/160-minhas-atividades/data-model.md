# Data Model: Minhas atividades

**Nenhuma entidade persistida nova.** Nenhuma tabela, coluna, migration ou gatilho. Tudo abaixo é
estrutura de leitura, montada na requisição e descartada no fim dela (FR-6884).

## O que se lê (existente)

| Fonte | Para quê | Filtro |
|---|---|---|
| `MembroComissao` | os Processos presididos (R-002) | `identity_subject` do ator, `ativo`, `funcao=PRESIDENTE`, escopo do ator |
| `Edital` | os Editais de condução | dos Processos presididos; `status` em `PUBLICADO`, `ENCERRADO`; Processo fora de `PROCESSO_FINAL` |
| `AlocacaoAConferencia` (`115`) | os Editais e Perfis da conferência | da pessoa, ativa, nos mesmos estados; `perfil_id` nulo é todos |
| `comissao_selectors.minhas_etapas` + `carga_nas_etapas` | a avaliação e os cartões | o que a página já lê hoje |
| `andamento.do_edital` (`127`) | as providências de cada Edital lido | só nos Editais acima |

## Estruturas de leitura (novas, em memória)

### `Linha`

Uma providência da pessoa, ou uma avaliação, com o porquê.

| Campo | De onde | Regra |
|---|---|---|
| `providencia` | o item do nível 1 do Edital, ou a linha de avaliação montada pela carga | é a célula; a página não reescreve o texto (FR-6859) |
| `edital` | o Edital lido | — |
| `base` | o caminho por que o Edital foi lido | `PRESIDENCIA` ou `ALOCACAO`; a avaliação é sempre `ALOCACAO` (FR-6861) |
| `fase` | `centro.fase_da_providencia` | o nome de `conceitos.NOMES` (FR-6867) |
| `indice` | a posição de emissão no Edital | só para ordenar (R-007) |

### `Grupo`

Uma ou mais `Linha` iguais entre Editais (R-006).

| Campo | Regra |
|---|---|
| `linhas` | ordenadas pelo Edital mais antigo; uma só, quando o ato tem número |
| `ato`, `situacao`, `base`, `fase` | os da primeira linha, iguais em todas por construção da chave |
| `quantos_editais` | `len({linha.edital.id for linha in linhas})` |

### `Atividades`

O que a view entrega ao template.

| Campo | Conteúdo |
|---|---|
| `para_fazer` | `[Grupo]` de *Pendente* e *Obsoleto* (FR-6863), ordenados (FR-6866) |
| `em_espera` | `[Grupo]` de *Aguarda* e *Impedido* dos Editais presididos (FR-6868) |
| `nao_lidos` | `[Edital]` cuja leitura falhou (FR-6874) |
| `quantos_atos`, `quantos_editais` | para os títulos das seções (UX-711) |
| `preside`, `gestor` | para a nota de cobertura e os estados vazios (FR-6872, FR-6876) |

## Transições

Nenhuma. Uma linha some quando a célula deixa de ser SUA na derivação, porque o ato foi praticado ou o
estado mudou. Nada é marcado como visto ou feito.
