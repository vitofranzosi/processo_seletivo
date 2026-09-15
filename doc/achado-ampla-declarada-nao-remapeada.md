# A cópia de Edital levava, como ampla concorrência, a Modalidade do Edital anterior

**Data:** 2026-09-15
**Origem:** implementação da `027`, Fase 2. O defeito é da `023`, e o campo é da `014`.
**Natureza:** referência entre entidades que atravessava o remapeamento sem ser trocada.
**Situação:** **corrigido**, com guarda própria. Este documento existe pelo mecanismo, que continua
de pé para o próximo campo.

## O defeito

`editais/domain/reaproveitamento.py` troca, uma a uma, todas as identidades que a cópia carrega: o
Perfil, a Modalidade, a Regra Normativa, o fato declarado, o marco, o critério, o Evento, a Etapa,
o Documento Exigido e — desde a `025` — a linha do quadro de vagas e a `modalityId` dela.

`generalCompetitionModalityId` não estava na lista. Ele nasceu na `014` e diz **qual das Modalidades
do Perfil é a da ampla concorrência**. Copiado sem troca, o Edital novo apontava uma Modalidade que
pertence ao Edital de origem: um identificador de outro Edital dentro do conteúdo canônico deste.

```
origem   generalCompetitionModalityId = M1   (Modalidade do Edital de origem)
destino  generalCompetitionModalityId = M1   ← errado; deveria ser M1'
         competitionModalities        = [M1', …]
```

## Por que ninguém viu

**O guarda certo já existia.** `test_nenhuma_identidade_da_origem_sobrevive_em_posicao_alguma`
varre o conteúdo copiado inteiro procurando identificadores da origem, e teria pegado. Ele estava
cego por um motivo simples: **nenhuma fixture declarava o campo**. Um guarda que varre só encontra
o que a fixture põe lá.

É a mesma classe de defeito que o próprio arquivo de teste descreve na abertura — *"um identificador
da origem que escape do remapeamento continua consistente com os seus vizinhos, atravessa a
validação da gravação e só falha na publicação — ou nunca"* —, e desta vez era o "ou nunca": o
conteúdo copiado é internamente coerente para tudo o que o sistema conferia, porque nada conferia
esta referência.

O campo só apareceu quando a `027` passou a exigir a declaração da ampla concorrência para derivar
a linha geral do quadro. Aí a fixture passou a declará-la, e o guarda enxergou.

## O que foi feito

- `reaproveitamento.py` passa a remapear `generalCompetitionModalityId`, ao lado das demais
  referências do Perfil. `None` atravessa intocado: significa "este Perfil não declara nenhuma".
- Dois testes de unidade próprios, em `tests/unit/editais/test_reaproveitamento.py`: um afirma que
  a declaração aponta a Modalidade **do destino**, o outro que a ausência não vira declaração.
- A origem rica do teste de integração passa a declarar o campo, que é o que tira a venda do guarda
  que já existia.

## O que fica registrado, e não vira escopo

**A fixture é parte do guarda.** Um campo novo no conteúdo publicado precisa entrar em três lugares
para ficar coberto: a forma, o remapeamento e **a fixture que o exercita**. O terceiro não tem
teste que o cobre, e é por onde este defeito passou.

Uma varredura que comparasse o conjunto de campos do conteúdo publicado contra o conjunto que a
origem do teste declara fecharia a classe — do mesmo modo que a `026` fechou a classe do contrato
de mutabilidade, e pela mesma razão: transformar "alguém precisa lembrar" em "o teste reprova".

Isso é **registro**, e não prioridade. O Princípio VI proíbe derivar dele automaticamente o escopo
da spec seguinte.
