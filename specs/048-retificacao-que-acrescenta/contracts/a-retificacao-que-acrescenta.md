# Contrato — a Retificação que acrescenta

**Spec**: [../spec.md](../spec.md) · **Research**: [../research.md](../research.md)

O que a tela oferece, o que o ato emite e o que é recusado. As formas do conteúdo estão em
[../data-model.md](../data-model.md).

## 1. A tela

### 1.1 Seção *Perfis de Vaga*

| Elemento | Hoje | Depois |
|---|---|---|
| Frase *"Modalidades de Concorrência ainda não são definidas por aqui."* | presente | **sai** (`FR-782`) |
| Botão *"Acrescentar Modalidade"* | — | fragmento `fragmento-retificacao-modalidade` (`R-5`) |
| Botão *"Acrescentar critério de desempate"* | — | fragmento `fragmento-retificacao-criterio` (`R-6`) |
| Cartão do Perfil sem reversão | não oferece a espécie | oferece a espécie, com o vazio *"Nenhum — este Edital não reverte vaga reservada"* (`FR-791`) |
| Cartão do marco sem janela | não oferece nada da janela | oferece o prazo em dias corridos, com o vazio que diz que o marco continua sem prever recurso (`FR-786`) |
| Cartão do marco sem corte | não oferece nada do corte | oferece os seis campos da regra (`FR-788`) |
| Cartão do marco **com** corte | três campos e as exclusões com a razão | inalterado (US2, cenário 5) |

### 1.2 O fragmento da Modalidade

| Campo | Tipo | Obrigatório | Conferido contra |
|---|---|---|---|
| Perfil | escolha | sim | Perfis vigentes |
| Código | texto | sim | único no Perfil, vigentes e acrescentadas |
| Denominação | texto | sim | — |
| Descrição | texto | não | — |
| Fundamento, versão, percentual | texto, texto, decimal | não; versão se houver fundamento | `validate_normative_rule` |
| *"É a ampla concorrência deste Perfil"* | caixa de marcação | não | exclusiva com vagas |
| Vagas imediatas | inteiro | não | ≥ 0; em branco não é zero |

### 1.3 O fragmento do critério

| Campo | Tipo | Obrigatório | Conferido contra |
|---|---|---|---|
| Marco | escolha `Perfil · marco` | sim | marcos vigentes |
| O que compara | escolha entre os três tipos | sim | vocabulário de `classificacao/domain/desempate.py` |
| Etapa ou fato comparado | escolha | sim | Etapas **classificatórias do Edital** para o tipo por Etapa, como na composição; fatos **do Perfil** para os tipos por fato |
| Quando o valor não existe | escolha entre os dois | sim | vocabulário |
| Ordem de aplicação | inteiro | sim | única no marco |

### 1.4 A conferência

Cada acréscimo e cada nascimento vira uma linha do resumo, com *antes* igual a *"—"* (`FR-800`):
- a Modalidade: o nome;
- a linha do quadro: *"N vaga(s)"*;
- a declaração da ampla: o nome da Modalidade;
- o objeto que nasce: uma linha por campo declarado, como o método do sorteio já faz;
- o critério: o tipo e o que ele compara.

As advertências do ato sobre o conteúdo resultante vêm abaixo, como hoje.

## 2. O que é recusado, e com que frase

Na gramática das recusas da validação: **o que**, **por quê**, **o que fazer** (`FR-801`). O texto final
é da implementação. O esqueleto é este:

*Conferência* é o POST sem `confirmar`, que só calcula as diferenças; *ato* é a confirmação e a
publicação, onde a aplicação da Retificação valida o conteúdo resultante, por qualquer canal. As recusas
da entidade acrescentada vêm nas **duas**: ao conferir, pela tela, e de novo no ato, para a API.

| Situação | Onde | Esqueleto |
|---|---|---|
| Modalidade com código repetido no Perfil | conferência e ato | *"Modalidade X: o Perfil P já tem uma Modalidade com o código C. Use outro código."* |
| Modalidade sem denominação | conferência e ato | *"Modalidade C: informe a denominação."* |
| Fundamento sem versão | conferência e ato | a frase que `validate_normative_rule` já dá |
| Ampla com vagas próprias | conferência | *"Modalidade C: a ampla concorrência não tem linha própria — as vagas dela são as da linha geral do quadro. Deixe as vagas em branco, ou desmarque a ampla."* |
| Critério com ordem repetida | conferência e ato | a frase de `perfis.py:332-338` |
| Critério com Etapa não classificatória, ou fato de outro Perfil | conferência; e no ato, pela validação de publicação | a frase da publicação (`tiebreaker_stage_missing`, `tiebreaker_fact_missing`) |
| Janela que nasce sem admitir recurso (só pela API) | ato | *"… cria uma janela que não admite recurso onde o Edital não declarava janela. A Retificação concede prazo de recurso onde não havia, e não o retira."* |
| Corte que nasce sobre Etapa com Resultado | ato, na confirmação e na publicação | *"O marco M passaria a cortar, e a Etapa E, que o corte governaria, já tem Resultado registrado: o corte excluiria dela quem já foi avaliado. Declare a regra sem governar Etapa, ou governando uma Etapa ainda sem Resultado."* |

## 3. O que continua exatamente como está

- Os campos de alteração de objetos existentes, e as exclusões com a razão.
- O acréscimo de Perfil, Evento, Anexo e linha do quadro.
- A recusa de nascer regra normativa em Modalidade **já publicada**.
- A segregação: elaborar, submeter, homologar e publicar a Retificação, com as permissões de hoje.
