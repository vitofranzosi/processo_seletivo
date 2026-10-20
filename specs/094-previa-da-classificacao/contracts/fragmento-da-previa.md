# Contrato: o fragmento da prévia

Interface htmx da gestão. Não é API pública e não atravessa `/api/`.

## Rota

```text
GET /gestao/…/fragmentos/perfil/<indice>/marco/<sub>/previa?edital=<uuid>
name: interface:fragmento-previa-da-classificacao
```

Irmã de `fragmento-marco-recomposto` (mesmo prefixo, mesmos `indice` e `sub`), registrada em
`interface/urls.py`.

## Parâmetros

| Origem | Parâmetros |
|---|---|
| Query da rota | `edital` — o mesmo dos demais fragmentos da composição |
| `hx-include` do cartão | todos os campos `marco-<indice>-<sub>-…` e `criterio-<indice>-<sub>-<n>-…` — lidos por `forms.marco_do_formulario(request.GET, indice, sub)` |
| Painel *(segunda rodada)* | `candidatos` (`estavel`, o padrão, ou `caso:<chave>`); `populacao` (`alvo:faixa:vagas` da montagem, só na população estável); `anterior` (o estado do cálculo anterior, para "O que mudou", R-010) |

Nenhum parâmetro de Etapa, fato ou quadro: esses vêm do rascunho gravado, lidos no servidor pelo
`edital_snapshot(edital)` — a mesma montagem que a etapa Classificação já faz —, e as vagas pela
`linha_do_quadro` sobre ele (spec, Assumptions).

## Respostas

Sempre `200 text/html`, com o conteúdo do painel e, fora de banda, o anúncio:

| Estado | Conteúdo |
|---|---|
| Calculada *(segunda rodada)* | cabeça (título, fechar, Perfil e marco); seletor de candidatos; manchete; "O que mudou", quando comparável; fluxo de três passos e ramo da continuação; apuração das vagas como hipótese; tabela da fronteira; comparação dos empates; `<details>` da classificação completa e da explicação técnica; e, ocultos, `populacao` e `anterior` |
| Incompleta | cabeça e a lista do que falta (FR-2227) |
| Fora da fatia | marco por sorteio ou sem forma: a frase de que a prévia cobre marcos pela pontuação (o botão não aparece nesses casos; a resposta existe para o pedido forjado) |
| Fechar | `GET …/previa/fechar` → corpo vazio, e o anúncio "Prévia fechada" fora de banda |
| Remontar | o mesmo `GET …/previa`, sem `populacao` nem `anterior`: monta a população com a configuração digitada |

O anúncio é sempre `<p id="anuncio-da-previa" role="status" hx-swap-oob="true">` com uma frase.

## Negativas

| Caso | Resposta | Inventário |
|---|---|---|
| Sem sessão | a mesma dos demais fragmentos (`_edital_do_fragmento`) | — |
| Edital fora do escopo do ator | 404, como a tela | linha nova em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, classificada como escopo institucional |
| Marco inexistente no formulário | 200 com "marco não encontrado no formulário" — é pedido de tela, e não recurso | — |

## Garantias

- **Nenhuma escrita**: nenhum `INSERT`, `UPDATE` ou `DELETE` durante o pedido, verificado por
  `CaptureQueriesContext` (FR-2234).
- **Nenhum evento de trilha** e nenhuma alteração de sessão além da que o middleware já faz.
- **CSP**: nenhum `style=`, `<style>`, `<script>` nem `on*=` no HTML devolvido (FR-2237).
- **Sem regra no navegador**: o único script novo é o de foco (FR-2224).
