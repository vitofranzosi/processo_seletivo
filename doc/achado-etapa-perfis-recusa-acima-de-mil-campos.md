# Achado — a etapa Perfis deixa de gravar acima de mil campos

Encontrado em 29/09/2026, medindo a escala da etapa Perfis para a
[análise das coleções repetidas](analise-ux-colecoes-repetidas-2026-09-29.md), na branch da `051`
(PR 226, mergeado no mesmo dia — os números valem para a `main`).

> **Situação: resolvido em 29/09/2026 pelo caminho 1**, escolhido pelo usuário (DP-21, opção A):
> `DATA_UPLOAD_MAX_NUMBER_FIELDS` subiu para 13.000, com a conta no comentário de
> `config/settings/base.py`, um guardião em `tests/interface/test_limite_de_campos_da_composicao.py`
> e uma recusa legível no lugar do 400. Ver *Conferência contra a `main` e o que foi feito*, no fim.
> Continuam abertos os dois pontos listados ali.

## O que se observou

A etapa Perfis grava a coleção inteira num POST só: todo Perfil, com as Modalidades, as linhas do
quadro e os fatos, vai em cada *Salvar*, cada *Avançar*, cada *Aplicar aos demais Perfis* e cada
*Preencher pelo percentual*. O Django recusa, **antes de a view rodar**, qualquer envio com mais de
`DATA_UPLOAD_MAX_NUMBER_FIELDS` campos — mil, o padrão, que o projeto não altera.

Medido com o Edital em elaboração do `seed_demo`, multiplicado pelo mesmo POST da tela (Perfis com
2 Modalidades, sem lista reservada, sem fato):

| Perfis | Campos enviados | Resultado |
|---:|---:|---|
| 1 | 39 | grava |
| 7 | 261 | grava |
| 16 | 594 | grava |
| 26 | 964 | grava |
| **27** | **1.001** | **400**, `TooManyFieldsSent` |

A conta é `2 + 37·N`, e cada Perfil custa mais conforme declara:

| O que o Perfil declara | Campos a mais |
|---|---:|
| cada Modalidade (id, id da regra, código, nome, percentual, fundamento, versão, arredondamento) | 8 |
| cada linha do quadro, com lista reservada (id, Modalidade, quantidade) | 3 |
| cada fato exigido (id, código, rótulo, tipo) | 4 |

Com três Modalidades e quadro repartido — o formato do 140/2025 —, o teto cai para **perto de 18
Perfis**. O 140/2025 tem 16. O multicampi que a `051` projeta (`spec.md`, *Por que esta feature
existe*) tem 66.

**A Classificação tem o mesmo teto, mais baixo por item.** Cada marco envia ~28 campos, mais 5 por
critério de desempate (contado no navegador sobre um marco novo). Dezesseis Perfis com um marco de
três critérios ficam em ~700; dois marcos por Perfil passam de mil.

## O que a pessoa vê

A página de erro 400 do servidor, sem a tela da etapa, sem mensagem de domínio e sem dizer o que
fazer. Nada é gravado.

O que foi digitado sobrevive **na etapa Perfis** pelo rascunho local (`rascunho.js`), que a etapa
declara em `data-rascunho`. **A Classificação não o declara**: ali, o que foi digitado depois da
última gravação fica só no que o botão *Voltar* do navegador conseguir restaurar.

## Por que nenhum guardião viu

O teto não é de domínio, e nenhuma validação o conhece. O maior volume que a suíte compõe, até onde se
procurou, são os 16 Perfis do orçamento de consultas de `test_duplicar_perfil.py`; o `seed_demo`
semeia dois. O teto só aparece
com o volume de um Edital multicampi, que ainda não passou pela interface.

**O mesmo teto já custou uma vez.** A confirmação da distribuição morria com mil inscrições, medido
em 27/09; a correção de lá foi fazer as identidades viajarem num campo só (`views.py`, no comentário
*"As identidades viajam num campo só"*). A composição não foi revista na ocasião.

## O que corrigir exigiria

Três caminhos, em ordem de custo. Nenhum é de interface, e esconder cartões na tela — a proposta da
análise — **não reduz o envio**: os Perfis escondidos continuam no formulário, e precisam continuar.

1. **Subir o limite.** Uma linha em `config/settings`. O limite existe contra negação de serviço por
   envio gigante; a composição exige identidade com `edital:elaborar`, mas o limite é global, e
   subi-lo vale para toda rota, inclusive as do portal. Pede decidir o valor, e se ele vale para
   todos ou só para a gestão.
2. **Serializar a coleção num campo.** O caminho da distribuição. Aqui é bem mais caro: a etapa é
   lida por `forms.ler_perfis`, pela recusa que reexibe o digitado, pelo rascunho local e pelos
   fragmentos do htmx, todos por nome de campo; e a etapa deixaria de funcionar sem JavaScript.
3. **Gravar por Perfil.** Resolve o teto e reabre três decisões: a `UX-020` da `027`, a `FR-638` da
   `043` e a `D-001` da `051`, todas escritas porque o `replace_draft` apaga o que não é reenviado.

O caminho 1 também não resolve para sempre — ele move o teto. Mas o volume real mais alto conhecido
é de dezenas de Perfis, e não de milhares de itens, que foi o que tornou o caminho 2 necessário na
distribuição.

## Conferência contra a `main` e o que foi feito (29/09)

Os números acima foram medidos na branch da `051`. Conferidos contra a `main` em `f00f7214`, depois da
`052` e da `053`, lendo o formulário que a tela devolve — e não somando campos à mão:

| Envio | Campos, com o botão | O antigo teto de mil caía em |
|---|---|---|
| Perfis — 2 Modalidades, quadro de 2 linhas, sem fato | `4 + 37·N` | 27º Perfil (1.003) — **confirmado** |
| Perfis — 3 Modalidades, quadro de 3 linhas (a forma do 140/2025) | `4 + 48·N` | 21º Perfil (1.012); o "perto de 18" acima era estimativa |
| Classificação — 1 marco de 3 critérios por Perfil | `12 + 45·N` | 22º Perfil; 16 Perfis ficam em 732 |
| Classificação — 2 marcos de 3 critérios por Perfil | `12 + 89·N` | 12º Perfil |
| Retificação — 3 Modalidades, 1 marco de 2 critérios | `41 + 56·N` | 18º Perfil; 16 Perfis ficam em 937 |

A conta por Perfil na etapa Perfis é `15 + 8·M + 3·L + 4·F` (Modalidades, linhas do quadro, fatos), e
na Classificação cada marco envia `29 + 5·C` (critérios). A `052` não mudou o envio, como a FR-950 dela
promete. O que difere da fórmula `2 + 37·N` de cima são os dois controles do Edital que a `051`
acrescentou, e que só aparecem a partir do segundo Perfil — a medição de cima valia para N = 1.

**A Retificação não tinha sido medida, e é o maior envio da gestão.** Ela envia o Edital publicado
inteiro. No maior Edital previsto — 66 Perfis, 4 Modalidades, quadro repartido em 4 linhas, 2 fatos,
2 marcos de 3 critérios, sobre 2 Etapas —, os três envios ficam em 4.425 (Perfis), 5.885
(Classificação) e **6.113** (Retificação, `41 + 92·N`). Com o teto antigo, a Retificação desse Edital
morreria a partir do 11º Perfil.

**O que foi feito.** O limite subiu para o dobro do maior dos três, arredondado ao milhar acima:
13.000. É global — o Django lê o valor ao interpretar o corpo, antes de rota e view, e não oferece
limite por caminho. O guardião recompõe o maior Edital previsto, lê o formulário das três telas como
o navegador o enviaria e reprova se algum passar do limite configurado: com o limite de mil, os três
casos reprovam; com o de agora, Perfis e Classificação gravam o envio de volta, e a Retificação chega
à view. E o envio que ainda passar do limite volta como página da gestão — status 413, o que
aconteceu, o número do limite e o que fazer —, também com `DEBUG` ligado (`interface/erros.py`).

**O que a pessoa vê, corrigido.** A seção de cima diz que a Classificação não declara o rascunho
local. Deixou de ser verdade com a `053` (FR-979, D-007), mergeada no mesmo dia: todas as etapas da
composição que gravam coleção o declaram. A Retificação não tem rascunho local.

**Continuam abertos**, fora deste escopo:

- **O rascunho local guarda, mas não devolve, enquanto o limite estiver passado.** Restaurá-lo é
  reenviar o formulário inteiro (`rascunho.js`, `restaurar`), e o reenvio passa do mesmo limite. O
  guardado sobrevive — só a gravação o apaga — e volta a servir quando o limite for ampliado, dentro
  do dia em que vale. A recusa diz exatamente isso.
- **O corpo em bytes, depois da aplicação.** A Classificação do maior Edital envia ~472 KB, dentro
  dos 2,5 MB de `DATA_UPLOAD_MAX_MEMORY_SIZE`, que o guardião também confere. Um proxy à frente da
  aplicação tem limite próprio — o do nginx, por padrão, é 1 MB —, e o repositório não declara
  servidor de produção onde conferi-lo.
