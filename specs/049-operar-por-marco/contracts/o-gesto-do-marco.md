# Contrato — a tela do marco e o gesto

## 1. Rotas

| Rota | Método | Porta | O que faz |
|---|---|---|---|
| `/gestao/editais/<edital>/marcos/<marco>/conducao` (`interface:marco`) | GET | presidência/gestão, auditoria **ou** `resultado:publicar` | indicador completo, gestos que a pessoa pratica, desfecho do último gesto |
| `/gestao/editais/<edital>/marcos/<marco>/conducao/<operacao>` (`interface:gesto-do-marco`) | POST | `ordenar`, `cortar`, `apurar`: gestão da comissão · `publicar`: `resultado:publicar` | sem `confirmar=1`: conferência; com `confirmar=1`: pratica e redireciona |

`<operacao>` fora de `ordenar | cortar | apurar | publicar` é 404. Marco que a norma vigente não
publica é 404.

## 2. Conferência (POST sem `confirmar`)

Entrada: `natureza` e `autoridade` na publicação. Resposta `200` com `marco_conferir.html`:

- três grupos (`UX-092`): **Serão praticados**, **Ficam de fora**, **Impedidos**, cada recorte com
  rótulo, resumo e razão;
- um formulário de confirmação só quando há recorte a praticar (`FR-819`), com:
  - `confirmar=1`, `chave` (nova, desta conferência);
  - um `recorte` e uma `assinatura_<recorte>` por recorte do grupo *Serão praticados* — a ampla é
    `ampla`;
  - na publicação, `natureza`, `autoridade` e, quando exigida, `declaracao_de_encerramento`;
- o botão nomeia a operação e a quantidade: *"Emitir 3 ordens"*, *"Emitir 3 cortes"*,
  *"Apurar 3 recortes"*, *"Publicar 3 resultados"*.

Na publicação sem natureza ou sem autoridade válida, a conferência não é composta: a tela do marco
volta com a recusa.

## 3. Confirmação (POST com `confirmar=1`)

Para cada `recorte` do formulário, na ordem da derivação:

1. o recorte é conferido contra a derivação única de agora: o que não é identidade é 404; o que é
   identidade e não é mais recorte do marco — uma Retificação o retirou depois da conferência —
   volta no desfecho como recusado, sem nada praticado nele, e o gesto segue nos demais;
2. o comando é chamado com a chave `marco:<chave>:<operacao>:<recorte>`, o `correlation_id`
   `gesto-<chave>`, a assinatura do recorte e motivo vazio;
3. `DomainError` vira desfecho `recusado` com `detail`; sucesso vira `feito`.

Um recorte recusado não interrompe os seguintes (`FR-823`). Depois, `302` para `interface:marco`, e
o desfecho aparece uma vez.

## 4. Desfecho (`UX-093`)

Cabeçalho: *"N feitos, M recusados."* Depois os recusados, com a razão e o caminho para a tela do
recorte; depois os feitos, com o caminho para o ato.

## 5. Página do Edital (`UX-090`)

Cada marco do bloco de marcos classificatórios ganha:
- uma linha de resumo: *"Recortes: 4 · com ordem 2 · com corte 1 · apurados 0 · publicados 0"*
  (corte omitido quando o marco não corta);
- o destino *"conduzir o marco"*, para quem abre a tela do marco.

## 6. Recusas nomeadas

| Situação | Onde | Frase |
|---|---|---|
| Processo em estado final (ordenar, cortar, apurar) | conferência | a frase de `ensure_processo_accepts_changes` |
| Alcance vazio | conferência | *"Não há recorte a praticar neste marco."* e os grupos *fora* e *impedidos* |
| Marco de sorteio, `ordenar` | conferência | *"A ordem deste marco nasce do sorteio público…"* (a do domínio) |
| Marco sem regra de corte, `cortar` | conferência | *"Este marco não declara regra de corte."* |
| Recorte mudou desde a conferência | desfecho | a frase do comando (`stale_ordering_calculation`, `ordering_act_already_exists`, `publication_preview_stale`…) ou, na apuração, *"O recorte mudou desde a conferência; confira de novo antes de apurar."* |
