# Achado — a coluna numérica dos resultados fica à esquerda

Encontrado em 30/09/2026, na `055` (*Polish da folha e dos componentes*), ao tratar o G3 da
[auditoria de polish](auditoria-polish-ui-2026-09-30.md).

> **Não vira escopo por estar escrito aqui.** Priorizar é do usuário.

## O que se observou

`resultados.html` marca a célula de resultado com `class="numero"`, esperando o alinhamento à direita
— mas a regra da folha é `.tabela td.numero`, e a tabela da tela não tem `class="tabela"`. A classe
não faz nada ali: a coluna sai à esquerda, como a pontuação da ordem saía antes da `055`.

## Por que a `055` não resolveu

O caminho mais curto era soltar o prefixo da regra (`td.numero,th.numero`), e ele foi tentado. Mas
`.tabela` não tem outra regra na folha, e a guarda de classe órfã
(`test_nenhuma_classe_citada_deixa_de_existir_na_folha`) reprovou os sete templates que a citam.
Manter a classe viva com uma regra de enfeite seria enganar a guarda. A `055` ficou com
`.tabela td.numero` e pôs `class="tabela"` na tabela da ordem, que era a tela da lista dela (D-011).

## O que resolveria

A mesma coisa na `resultados.html`: `class="tabela"` na tabela. Uma palavra, sem regra nova. Conferir
antes se a coluna mistura número e texto ("favorável", "não avaliada") — à direita, o texto também
vai, e isso pode ser o que se quer ou não.
