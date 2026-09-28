# Contrato — a prévia e a confirmação na composição

## Pedir a prévia

Envio do formulário da etapa (`classificacao` ou `perfis`) para a mesma URL da etapa, com o conteúdo
inteiro da etapa e **um** dos campos abaixo:

| Campo | Valor | Etapa | Unidade |
|---|---|---|---|
| `aplicar` | `marco:<perfil>:<sub>` | classificacao | o marco `sub` do Perfil |
| `aplicar` | `modalidade:<indice do Perfil>:<indice da Modalidade>` | perfis | a Modalidade, pelo código |
| `aplicar` | `edital:callForm` · `edital:vacancyReversion` | perfis | o valor do controle do Edital |

**Resposta**: 200, a tela da etapa com o digitado reexibido e a seção *"Aplicar aos demais Perfis"* no
alto, com:

- a frase do alcance: *"6 nascem, 1 muda, 1 fica fora"* (`UX-113`);
- uma linha por Perfil destino, na ordem dos Perfis (`UX-111`): código, denominação, efeito em palavras;
  em *substitui*, as mudanças `rótulo: antes → depois`; em *fora do alcance*, o motivo e nenhuma caixa;
- caixa `aplicar_destino=<perfil>` marcada por padrão em *nasce* e *substitui*;
- campo oculto `aplicar_impressao`;
- botão `confirmar_aplicacao=<o mesmo valor de aplicar>` com o número no rótulo;
- botão `cancelar_aplicacao` que reexibe a tela sem a prévia e sem gravar.

**Nada é gravado.**

## Confirmar

Envio com o conteúdo inteiro da etapa, `confirmar_aplicacao`, `aplicar_impressao` e as caixas.

- Impressão igual à recalculada → aplica aos destinos marcados que não estão fora do alcance, grava
  a etapa (`replace_draft`) e o registro do gesto numa transação, e redireciona para a etapa com
  `?salvo=<etapa>&aplicado=<n>`.
- Impressão diferente → 200, a prévia de agora, com a recusa *"O que estava na tela mudou depois da
  prévia. Confira de novo antes de aplicar."*; nada gravado.
- Nenhum destino marcado → 200, a prévia, com a recusa *"Nenhum Perfil marcado."*; nada gravado.
- Recusa do domínio na gravação (a mesma de salvar) → 200, a tela com a recusa, como hoje.

## Preencher o quadro pelo percentual

Envio da etapa `perfis` com `preencher_quadro=1`: 200, a tela com as linhas vazias de lista reservada
preenchidas pela sugestão onde ela é um número só, e a frase *"Preenchidas N linhas em M Perfis"*;
nada gravado — gravar continua sendo *Salvar*.

## Permissão

A de compor (`pode_compor`). Sem ela, o gesto é recusado como a gravação é hoje.
