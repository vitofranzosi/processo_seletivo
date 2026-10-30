# Verificação: Sorteio viável desde a publicação

Demonstração dos cenários do [quickstart](quickstart.md) pela interface real, em 29/10/2026, para a
SC-959 e a T022. Banco próprio `ps_demo_102`, preparado em três passos com `make preparar`, sem
`seed_demo`. Servidor pela entrada `sorteio-viavel-102` do `.claude/launch.json` (porta 8102). Painel
do aplicativo a 1280×900.

## Como o Edital foi levado ao estado

O Edital 72/2026 de demonstração foi publicado por um script de `manage.py shell` com os ajudantes da
suíte (`levar_a_publicacao`, `constituir`, `inscrever`), como já se faz noutras demonstrações. Ele usa
a `Fonte de demonstração (só a data)`, o concurso 6113, as inscrições terminando às 21h00 e a
extração declarada para 30/10 às 20h05, com três inscrições submetidas e a presidência de `maria`.
**A publicação passou**, porque o dia da extração é posterior ao do fim. O banco de demonstração não
tem a autoridade signatária que a fixture da suíte registra, e o script chama `garantir_o_cefor()`
antes de publicar.

A sessão de demonstração foi aberta por `curl` (subject `maria`, papel `elaborador`) e o cookie foi
levado ao painel, como registrado para a `100`.

## Cenário 2, passo a passo

| Hora | Passo | O que se viu |
|---|---|---|
| 20h58 | Retificação pela interface: "Quando a ocorrência acontece" de 30/10 20:05 para 29/10 20:05, "Criar Retificação" | A Retificação nasce em elaboração com a alteração declarada. |
| 20h58 | "Submeter para revisão", página de confirmação | **A advertência da seção 2 do contrato**: "O marco SORTEIO declara a extração de Fonte de demonstração (só a data) em 29/10/2026, e as inscrições terminam em 29/10/2026 às 21:00. […] Se a relação ainda não foi congelada, esta Retificação pode declarar uma extração de dia posterior ao congelamento. […]". O botão "Confirmar" continua: a Retificação não é impedida. |
| 20h59 | Submissão, homologação e publicação pelo ajudante `publish_retification` (são três papéis distintos) | Retificação publicada. |
| 20h59 | Tela do sorteio, com as inscrições ainda correndo | "Ainda não é possível publicar a relação." seguido de **"Congelar a relação depois do fim das inscrições impede o sorteio com a extração declarada."**, com o link "retifique o método" (o papel `elaborador` retifica). O botão de congelar não aparece, porque as inscrições correm. |
| 21h00 | Tela do sorteio, inscrições encerradas | **"Congelar a relação hoje impede o sorteio com a extração declarada."** antes do recorte, com "Congelar não se desfaz." O botão "Publicar e congelar a relação" **está disponível** (D-005). |
| 21h00 | "Publicar e congelar a relação" | Relação congelada às 21h00, 3 participantes. Antes de "Realizar o sorteio", o diagnóstico da seção 4: **"Esta relação não pode ser sorteada com a extração que o método dela declara."**, com a data do congelamento, o dia da extração a partir de 00h00 e os três passos. |
| 21h00 | "Observar a ocorrência 6113 na fonte" | A ocorrência é registrada; o diagnóstico continua, e **o botão "Realizar o sorteio" continua oferecido**: esconder não foi decidido. |
| 21h00 | "Realizar o sorteio" | A recusa `occurrence_precedes_freeze`, no topo da tela, com os acréscimos da seção 5: *"Fonte de demonstração (só a data) publica só a data da extração, sem o horário: a data vale a partir de 00h00. Suceder a relação sem retificar não resolve: a relação nova seria congelada ainda mais tarde. A saída é retificar o método para uma extração de dia posterior, publicar relação nova sucedendo esta, e então observar a ocorrência nova."* |

**A primeira frase da recusa continua em UTC**: ela diz *"a partir de 29/10/2026 03:00"* e *"congelada em
30/10/2026 00:00"*, quando a tela mostra 00h00 e 21h00. É a lacuna 2 do achado de 29/10, fora desta
feature (FR-2668, R-007), e a demonstração a reproduz exatamente.

## Cenário 3, passo a passo

| Hora | Passo | O que se viu |
|---|---|---|
| 21h01 | Retificação da extração para 30/10 às 20h05, pelo ajudante `retify` | Publicada. |
| 21h01 | Tela do sorteio | A variante: **"O método já foi retificado, e esta relação continua comprometida com o anterior."** e *"Falta publicar relação nova, sucedendo esta"*. |
| 21h01 | "Publicar relação nova, sucedendo a atual", com motivo, pela interface | Relação nova congelada às 21h01. O diagnóstico some. O sorteio dela só se constitui amanhã, quando o início do dia for posterior ao congelamento — é a garantia funcionando. |

## Cenário 1

A publicação impedida e a pendência na revisão foram verificadas pelos testes
(`integration/editais/test_edital_72.py` e `interface/test_revisao_extracao_inviavel.py`), pelo mesmo
`_pendencias` que a revisão desenha. Não foram repetidas no navegador.

## O que fica fora desta demonstração

- **A SC-958** é de pessoas, pelo [roteiro de compreensão](roteiro-de-compreensao.md).
- **O botão "Realizar o sorteio" continua oferecido** à relação que não sorteará. A spec não pede
  escondê-lo, e a decisão é do usuário.
