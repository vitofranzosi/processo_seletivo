# Contrato: o fragmento da prévia, para marco por sorteio

**Rota**: `GET fragmentos/perfil/<indice>/marco/<sub>/previa` — a mesma da `094` (R-007).

**Autorização, Edital ausente e marco ausente**: os da `094`, sem mudança. Edital fora do escopo → 404
pelo `_edital_do_fragmento`; sem `edital` na query → 204; Perfil ou marco que o formulário não tem →
o painel "sem marco".

## Despacho

| `orderProduction` do marco, como está digitado | Resposta |
|---|---|
| `POR_PONTUACAO` | a prévia da `094`/`095`, sem mudança |
| `POR_SORTEIO` | **a prévia do sorteio**, em `_previa_do_sorteio.html` |
| ausente | o painel da `094` para marco sem forma, sem mudança |

## Parâmetros que a prévia do sorteio lê

| Parâmetro | Forma | Efeito |
|---|---|---|
| `edital`, cartão do Perfil (`hx-include`) | os da `094` | o marco, as vagas e os recortes, como estão digitados e gravados |
| `semente` | token assinado (R-004) | ausente: semente nova; válido: a mesma; inválido ou de outro marco: **recusa** |
| `sortear` | `1` | semente nova, ignorando `semente` |
| `inscritos-ampla` | inteiro ≥ 0 | os só da ampla; ausente ou inválido: a sugestão |
| `inscritos-<lista_id>` | inteiro ≥ 0, um por recorte reservado | os autodeclarados daquela lista; idem |
| `vista` | `processo` ou `detalhe` | a da `094` |
| `recorte` | `lista_id` ou vazio | o recorte em vista no detalhe, como na `095` |

**Nenhum parâmetro informa semente, material ou resumo da relação** (FR-2483). Um `material=` ou `seed=`
na query é ignorado, e o teste da SC-931 o envia de propósito.

## Estados da resposta

| Estado | Quando | O que o painel diz |
|---|---|---|
| `calculada` | caso comum | faixa da semente, população, jornada ou detalhe, ocupação da rodada, resumo das rodadas, o que não simula |
| `semente_recusada` | token inválido ou de outro marco | "A semente desta prévia não foi reconhecida. Sorteie de novo." — com o botão, sem nenhuma ordem |
| `acima_do_limite` | `total > 600` ou mais de seis reservadas | o limite, e os campos para corrigir (FR-2491, FR-2343 da `095`) |
| `regra_desconhecida` | o método declara regra de normalização fora do vocabulário | a recusa de `normalizar`, nomeando o campo; sem ordem |

**Sem regra de corte** não é estado à parte: a prévia calcula as ordens e o bloco da ocupação diz que
não há faixa (FR-2500).

## O que a resposta carrega no formulário do painel

- `semente`: o token da semente em uso — o que permite ao próximo recálculo mantê-la (D-006).
- `inscritos-*`: as quantidades em uso, sugeridas ou digitadas.
- O botão "Sortear de novo", que envia `sortear=1`.

## Anúncio (região `aria-live`)

Uma frase por recálculo, na ordem: se a semente **mudou** ou **foi mantida**; o resumo por recorte
("Ampla: 10 avançariam. PPI: 3 avançariam…"); e a frase de maior consequência do resumo das rodadas
(FR-2511).

## Garantias

- Zero escritas, zero eventos de trilha, em qualquer estado (FR-2509, SC-930).
- O mesmo `token` e as mesmas quantidades produzem a mesma resposta, byte a byte no bloco do
  resultado (FR-2502).
- O HTML não tem `style=`, `<style>`, `<script>` nem `on*=` (FR-2512).
