# Etapa pontuada com mais de um avaliador por candidato não tem como fechar resultado

**Data:** 2026-11-16
**Origem:** a especificação da `179` (distribuição coerente com a agenda), ao responder se o GPS
permite dois avaliadores para o mesmo candidato.
**Natureza:** lacuna de norma publicável, e não defeito de código. O comportamento atual é
deliberado e está escrito.
**Situação:** **registrado, sem escopo.** Por decisão do usuário em 16/11, isto é achado, e não parte
da `179` nem da feature seguinte. Decidir se vira spec é governança do usuário.

## O que acontece hoje

O Edital declara, Etapa por Etapa, quantas avaliações cada inscrição recebe
(`evaluationsPerRegistration`). A distribuição atende a qualquer número: o lote atribui cada
inscrição a cada avaliador selecionado até esse teto, e o rodízio preenche as vagas.

O que não atende é **fechar o resultado**. `resultados/domain/regra.py`, `impedimento_da_regra`,
impede a consolidação da Etapa inteira quando ela prevê mais de uma avaliação e não é colegiada:

> "o Edital prevê 2 avaliações para esta Etapa e não declara como combiná-las"

E desde a `046` (`FR-746`) a recusa vem antes, na publicação: um Edital novo com Etapa pontuada,
eliminatória e com duas avaliações é recusado com essa mesma frase, e só o acervo — Editais
publicados antes da `046` — ainda tem Etapa assim.

| Forma da Etapa | Com 2 ou mais avaliações |
|---|---|
| Decisória **colegiada** (`165`) | Fecha: o Edital publica a regra de deliberação — maioria, unanimidade para o favorável ou unanimidade para o desfavorável —, que combina **sentidos**. |
| **Pontuada** | Não fecha: não existe regra publicável que combine **notas**. |
| Decisória sem regra de deliberação | Não fecha, pela mesma razão. |

## Por que é assim

O docstring de `regra.py` diz o motivo: o sistema não tira média, não soma, não pondera e não
arredonda, porque "consolidar N avaliações exigiria uma regra de combinação que o Edital não
publica, e inventá-la aqui seria aplicar ao candidato uma norma que ninguém escreveu". A `165`
resolveu o caso dos pareceres com uma regra publicada; o das notas ficou como estava.

## Onde isso vai aparecer

- **Entrevista com nota e banca de dois ou três avaliadores.** É o cenário que a `179` torna fácil de
  distribuir (uma dupla por banca e por dia), e é exatamente o que não fecha: a Programação e a
  distribuição funcionam, a consolidação não.
- **Prova didática ou análise de currículo com dupla correção**, comum em Editais de docentes e
  tutores.
- A heteroidentificação **não** é afetada: é decisória e colegiada.

## O que uma solução precisaria decidir

Registrado como perguntas, e não como proposta:

1. Que regras de combinação um Edital pode publicar — média aritmética, média descartando extremos,
   mediana, soma — e qual é o arredondamento.
2. Se há **discrepância máxima** entre as notas, e o que acontece acima dela (terceira avaliação,
   como em algumas bancas de correção).
3. Se cada nota fica visível ao candidato, ou só a combinada; e como isso conversa com o recurso.
4. Se as avaliações de nota também são às cegas entre os pares, como os pareceres da `165`.
5. Se a regra de deliberação da `165` e a regra de combinação de notas são o mesmo campo publicado
   ou dois.

## Referências no código

- `resultados/domain/regra.py` — `impedimento_da_regra`, `REGRA_DE_COMBINACAO_AUSENTE`.
- `resultados/domain/deliberacao.py` — a regra de deliberação da `165`, só sobre sentidos.
- `avaliacoes/domain/previsao.py` — `avaliacoes_previstas`.
- `tests/interface/test_distribuicao_por_sessao.py` — o caso de 43 pessoas da `179` usa um Edital do
  acervo com duas avaliações, porque um Edital novo assim não publica.
