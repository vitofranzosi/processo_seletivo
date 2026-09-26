# A cópia de Edital levava, como Etapa que o corte alimenta, a Etapa do Edital anterior

**Data:** 2026-09-25
**Origem:** plano da `043` (Duplicar Perfil). O defeito é da `023`, e o campo é da `014`.
**Natureza:** referência entre entidades que atravessa o remapeamento sem ser trocada — a mesma
classe de [achado-ampla-declarada-nao-remapeada.md](achado-ampla-declarada-nao-remapeada.md).
**Situação:** **corrigido** em 2026-09-25, por decisão do usuário, com guarda própria. Este
documento existe pelo mecanismo, que continua de pé para o próximo campo.

## O defeito

`editais/domain/reaproveitamento.py::remapear` troca todas as referências a Etapa que o marco
classificatório carrega — `stages[]`, `drawMethod.qualifyingStageId` e
`tiebreakers[].parameters.stageId` — e **não** troca `cutRule.governedStage`, que também é
identidade de Etapa. O `cutRule` inteiro atravessa a cópia pelo `**marco`, intocado.

```
origem   stages                  = [E1]
         cutRule.governedStage   = E1
destino  stages                  = [E1']
         cutRule.governedStage   = E1    ← errado; deveria ser E1'
```

O campo tem um valor que **não** é identidade: o sentinela `faixa.SEM_ETAPA_GOVERNADA` (`"NONE"`),
a declaração de que o corte não alimenta Etapa alguma (D-012). Ele precisa atravessar intocado.

## A consequência, confirmada

Medido em 2026-09-25 contra PostgreSQL, com uma sonda de integração descartável sobre a origem rica
de `tests/integration/editais/test_reaproveitamento.py`, acrescida de uma regra de corte que governa
a Etapa dela:

1. A cópia **grava**. `editais/domain/perfis.py::_validar_regra_de_corte` confere a espécie e as
   quantidades do alvo, e nada mais — a Etapa governada não é conferida na gravação.
2. O rascunho do destino guarda, em `regra_de_corte.governedStage`, o identificador da Etapa **do
   Edital de origem**, e o snapshot o reproduz.
3. `validate_for_publication` sobre esse snapshot emite o impeditivo `cut_rule_com_etapa_inexistente`
   (`editais/domain/validation.py`, na conferência da regra de corte).

**Não é defeito silencioso**: nenhum Edital publica com a referência errada. O custo é outro —
quem reaproveita um Edital com regra de corte encontra uma pendência impeditiva que não causou, e
cuja mensagem ("declara governar uma Etapa que este Edital não publica") não aponta a cópia.

Pela leitura do template, e **sem verificar no navegador**: o seletor *Etapa que o corte alimenta*
(`interface/templates/interface/_marco.html`) compara o valor gravado com as Etapas do destino, não
encontra nenhuma e mostra *Escolha a Etapa*. Quem regravar a etapa do assistente troca a pendência
por `cut_rule_sem_etapa_governada`; quem escolher a Etapa de novo a resolve.

## Por que ninguém viu

É o mecanismo do achado anterior, repetido em outra posição. A varredura negativa
`test_nenhuma_identidade_da_origem_sobrevive_em_posicao_alguma` teria pegado — e estava cega pelo
mesmo motivo: **nenhuma fixture de reaproveitamento declarava regra de corte**. Nem a origem de
unidade (`conteudo_publicado()`), nem a de integração (`rascunho_rico()`), nem a de interface
(`tests/interface/test_reaproveitar.py`).

O campo nasceu na `014` (2026-09-11), depois da `023`. O registro anterior já dizia que *"a fixture
é parte do guarda"*, e que um campo novo precisa entrar em três lugares — forma, remapeamento e
fixture. Este entrou no primeiro.

## O que foi feito

- `remapear` passa a trocar `cutRule.governedStage` pelo identificador do destino, **exceto** o
  sentinela `SEM_ETAPA_GOVERNADA` e o campo em branco — que o rascunho aceita, e a publicação cobra
  como `cut_rule_sem_etapa_governada`.
- Em `backend/tests/unit/editais/test_reaproveitamento.py`, a origem `conteudo_publicado()` passa a
  declarar a regra de corte — o que tira a venda da varredura negativa —, e dois testes próprios:
  `test_a_etapa_que_o_corte_alimenta_aponta_a_etapa_do_destino` afirma a troca, e
  `test_o_corte_que_nao_governa_etapa_continua_sem_governar` prende a exceção do sentinela.
- Em `backend/tests/integration/editais/test_reaproveitamento.py`, a origem `rascunho_rico()` passa
  a declarar a regra de corte, e `test_o_corte_governa_etapa_do_destino` prende a consequência
  medida: a cópia não produz mais `cut_rule_com_etapa_inexistente`. Contraprova feita — com a troca
  desligada, ele reprova.

## O que fica registrado, e não vira escopo

A correção não muda nada publicado — só o que a cópia grava daqui em diante. O que ela deixa de
fora é decisão separada:

- **Rascunhos já copiados** de origem com regra de corte carregam a referência errada hoje. A
  pendência impeditiva os protege, e a correção manual pela interface os resolve; migrá-los seria
  outra decisão.
- **A classe continua aberta.** O registro anterior sugeria uma varredura que comparasse os campos
  do conteúdo publicado contra os que a origem do teste declara. Ela teria pegado este campo no dia
  em que ele nasceu. Continua registro, e não prioridade.
- **A `043` (Duplicar Perfil)** copia marcos dentro do **mesmo** Edital, e ali a situação se
  inverte: a Etapa é do Edital, não do Perfil, e `governedStage` — como `stages[]` — deve continuar
  apontando a mesma Etapa. Se a `043` reusar `remapear`, o mapa dela tem de levar cada Etapa a si
  mesma; com a correção, esquecer isso falharia alto em `governedStage`, como já falha em
  `stages[]`.
