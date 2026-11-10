# Contrato da tela: `interface:sorteio` (142)

O que outras partes do sistema — o Centro, o "Próximo nesta lista", os testes da `139` — esperam da
tela. Mudar qualquer item exige mudar quem o lê.

## Destinos (ids)

| id | Onde | Quem leva até ele |
|---|---|---|
| `titulo-recortes` | título do passo 1 | duas listas juntadas na providência da relação |
| `recorte-<lista>` / `recorte-ampla` | o cartão da lista, no passo 1 | a célula da relação (`ancora_do_recorte`) |
| `titulo-ocorrencia` | título do passo 2 | a célula da semente |
| `titulo-execucao` | título do passo 3 | duas listas juntadas na providência do sorteio |
| `sorteio-<lista>` / `sorteio-ampla` | a execução da lista, no passo 3 | a célula do sorteio (`ancora_do_sorteio`) |
| `titulo-resultado` | título do passo 4 | — |
| `titulo-historico-excedente` | os registros fora da operação (`122`) | — |

## Formulários (inalterados)

| Destino | Onde mora | Condição (a de hoje) |
|---|---|---|
| `…/sorteio/relacao` (fixar ou suceder) | o cartão da lista | `pode_emitir and metodo and recorte.projetados and not inscricoes_em_curso` |
| `…/sorteio/ocorrencia` | o passo 2 | `proxima_referencia and pode_emitir and metodo` |
| `…/sorteio/realizar` | a execução da lista | `recorte.congelada and ocorrencia válida and pode_emitir`, sem sorteio |
| `…/sorteio/anular` | a execução da lista, recolhido | `pode_emitir`, com sorteio, com os insumos |

## Classes de situação

`situacao-do-andamento s-<situação>`, as do Centro. A palavra e o sinal vão sempre no texto.
