# A Lista de Editais e a Condução do marco não cabem em 375 px

**Data:** 2026-09-30
**Origem:** a passada a 375 px da `057` (polish das telas de operação), que a
[auditoria de polish](auditoria-polish-ui-2026-09-30.md) não tinha feito.
**Natureza:** defeito anterior à `057`, medido igual antes e depois dela. Não virou escopo.
**Situação:** **aberto** — decidir se, quando e como corrigir é do usuário.

## O que se mediu

No banco de demonstração (`ps_057_polish`), com o viewport a 375 px:

- **Lista de Editais.** A tabela de cada Processo tem 531 px dentro de um cartão de 325, e o cartão
  (`article.processo`) recorta o que passa (`overflow:hidden`). A coluna "O que posso fazer" fica
  **fora da tela e inalcançável**: os botões começam em x = 354 a 392 e terminam em até 583. A
  página não rola na horizontal — o corte é silencioso.
- **Condução do marco.** A tabela "Recortes deste marco" tem 486 px, e a **página inteira** rola na
  horizontal.

## Por que não é da 057

As duas medidas são as mesmas com a largura da coluna de ações em 24 rem (antes) e em 30 rem
(depois): quem decide a largura mínima a 375 px é o conteúdo que não quebra — o rótulo
"Recursos aguardando decisão (0)", que é `white-space:nowrap`, e as palavras do título —, e não a
largura declarada. A `057` mudou a ordem das ações e a largura em tela larga; não tocou o
comportamento em tela estreita.

## O que resolveria, sem decidir aqui

- **Lista**: a mesma solução da matriz de Alocação — o cartão rola na horizontal abaixo de 60 rem —
  ou empilhar as células da linha.
- **Condução**: uma moldura com rolagem para a tabela do indicador.
