# Data Model: Convocar do cadastro de reserva, na ordem publicada

**Feature**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

## `AcrescimoDeVagas` (nova, app `ocupacao`, append-only)

A quantidade que entra num recorte depois da publicação, por fato de fora do Edital, e o ato contrário
que a devolve. Uma tabela para os dois (`T-001`).

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | gerado **antes** da apuração que o lê, para que ela o cite em `acrescimosLidos` |
| `edital` | FK `processos.Edital`, `PROTECT` | |
| `perfil_id` | UUID | |
| `marco_id` | UUID | |
| `lista_id` | UUID, nulo | o recorte exato em que foi registrado (`T-002`); nulo é a ampla |
| `especie` | texto | `ACRESCIMO` ou `DESFAZIMENTO` |
| `quantidade` | inteiro | `> 0` sempre; o sinal vem da espécie |
| `origem` | texto | obrigatória no acréscimo; vazia no desfazimento |
| `fundamento` | texto | obrigatório nos dois: o porquê do acréscimo, o motivo do desfazimento |
| `referencia` | texto | opcional; o processo administrativo |
| `desfaz` | FK `self`, nulo, `PROTECT` | obrigatória no desfazimento, nula no acréscimo; aponta um `ACRESCIMO` |
| `versao` | FK `publicacoes.VersaoConsolidada`, `PROTECT` | a versão vigente no ato: é ela que declarou o cadastro de reserva que o autorizou (`FR-2463`) |
| `registrado_por` | texto | o `subject` do ator |
| `registrado_em` | instante | o `now` do comando |

**Constraints** (no banco):

- `ck_acrescimo_quantidade_positiva`: `quantidade > 0`
- `ck_acrescimo_especie`: `especie IN ('ACRESCIMO', 'DESFAZIMENTO')`
- `ck_acrescimo_com_origem`: `especie = 'DESFAZIMENTO' OR (origem <> '' AND desfaz IS NULL)`
- `ck_desfazimento_cita_o_acrescimo`: `especie = 'ACRESCIMO' OR (desfaz IS NOT NULL AND origem = '')`
- `ck_acrescimo_com_fundamento`: `fundamento <> ''`
- índice `ix_acrescimo_recorte` em `(edital, perfil_id, marco_id, lista_id)`

**Imutabilidade**, em três camadas, como `MovimentoDeVaga` e `EfeitoDeOcupacao`:
- gatilho `acrescimo_de_vagas_imutavel BEFORE UPDATE OR DELETE`, pela função
  `reject_occupancy_mutation()` que a `ocupacao/0001` criou;
- a tabela em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`), que passa de 40 a 41;
- `save()` recusa quando não está adicionando, e `delete()` sempre, com *"append-only"* na mensagem.

**O que a aplicação garante, e o banco não pode** (`CHECK` não agrega):
- o desfazimento não excede o que resta do acréscimo citado — `quantidade do acréscimo − soma dos
  desfazimentos que o citam` (`FR-2462`);
- o desfazimento cita acréscimo do mesmo recorte, e acréscimo, e não outro desfazimento;
- as duas, sob o `select_for_update` do Processo.

## `ApuracaoDeOcupacao` (existe, `016`) — o que muda

- `universo["acrescimosLidos"]`: lista dos ids de `AcrescimoDeVagas` que a apuração leu, na ordem
  `(registrado_em, id)`. Ausente nas apurações anteriores a esta feature, e lida como lista vazia.
- `efetivas` passa a ser `publicadas + recebidas − cedidas + acrescidas − desfeitas`, com o saldo dos
  acréscimos congelados.
- A constraint `ck_apuracao_ocupadas_no_limite` não muda: `ocupadas <= efetivas` continua valendo, e a
  trava do desfazimento é o que impede um saldo que a violaria por pessoa chamada (`T-005`).

## Causa de obsolescência nova

`acrescimo_posterior` — existe no recorte `AcrescimoDeVagas` cujo id não está em `acrescimosLidos` da
apuração vigente. Descrição na tela: *"Uma vaga acrescida ou desfeita depois desta apuração mudou as
vagas deste recorte."*

## Nenhuma mudança em

`MovimentoDeVaga`, `EfeitoDeOcupacao`, `Convocacao`, `DesfechoDeConvocacao` e o conteúdo publicado do
Edital. A convocação lê a apuração como lê hoje.
