# Contrato: o fragmento da prévia, com recortes

Extensão do contrato da `094` (`specs/094-previa-da-classificacao/contracts/fragmento-da-previa.md`,
no PR #316). A rota, as negativas e as garantias de lá valem sem mudança; aqui fica só o que muda.

## Rota

A mesma: `interface:fragmento-previa-da-classificacao`. Nenhuma rota nova (D-001, D-007).

## Parâmetro novo

| Origem | Parâmetro | Regra |
|---|---|---|
| Painel, só na vista `detalhe` | `recorte` — vazio para a ampla, o id da Modalidade para uma reservada | Valor que não é recorte do Perfil cai na ampla, e o painel diz que o recorte pedido não existe mais no rascunho (R-007). A jornada (`vista=processo`) ignora o parâmetro e mostra todos |

`candidatos`, `populacao` e `anterior` continuam sendo do painel. `populacao` passa a levar também as
fronteiras de cada reservada na montagem, para que a atribuição de Modalidade seja reproduzível sem
remontar (R-005).

Nenhum parâmetro de Modalidade, quadro ou reversão: vêm do rascunho gravado pelo `edital_snapshot`, como
pesos, fatos e linha geral na fatia 1 (spec, Assumptions).

## Respostas — o que muda em cada estado

| Estado | Acréscimo |
|---|---|
| Jornada | no marco simulado, um resumo por recorte (FR-2310); na Etapa alimentada, a união por pessoa e quantos as reservadas acrescentam (FR-2311); depois do marco, fora da sequência, o bloco da ocupação com uma linha por recorte e a reversão (FR-2312) |
| Detalhe | o seletor de recorte (`<select>` nativo com `<label>`, dentro do formulário do painel, `hx-get` no `change`); a manchete e o fluxo do recorte escolhido; na reservada, a coluna da posição na ampla e a marca "ocuparia pela ampla" (FR-2314); a frase da faixa tomada pela ampla (FR-2319); o bloco da ocupação completo, com hipóteses, recortes e reversão |
| Perfil sem reservada | nenhum seletor; o bloco da ocupação só da ampla (FR-2304) |
| Recortes acima do limite | a frase do limite, sem cálculo (FR-2343) |

O anúncio fora de banda passa a ter uma oração por recorte, uma vez (FR-2344).

## Garantias acrescentadas

- **Nenhuma escrita** também em `ApuracaoDeOcupacao`, `MovimentoDeVaga` e efeitos de ocupação
  (FR-2341), verificado pela mesma captura de consultas da `094`.
- **Nenhum dado de inscrição real**: nenhuma consulta a `Inscricao` nem a documentos durante o pedido
  (FR-2342).
