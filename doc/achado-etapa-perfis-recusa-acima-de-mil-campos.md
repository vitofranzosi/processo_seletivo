# Achado — a etapa Perfis deixa de gravar acima de mil campos

Encontrado em 29/09/2026, medindo a escala da etapa Perfis para a
[análise das coleções repetidas](analise-ux-colecoes-repetidas-2026-09-29.md), na branch da `051`
(PR 226, mergeado no mesmo dia — os números valem para a `main`).

> **Situação: aberto.**
>
> **Não vira escopo por estar escrito aqui.** O que se registra é um teto que a composição tem e
> que nenhuma spec declara, onde ele fica, e o que cada correção custaria. Escolher é do usuário.

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
