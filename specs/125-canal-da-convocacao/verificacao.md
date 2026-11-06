# Verificação: A convocação segue o canal (125)

**Data**: 2026-11-06, sobre a `main` em `250efe97` com os commits desta branch.

## No navegador

Banco de demonstração próprio (`ps_demo_125`), montado pelos auxiliares dos testes num shell: um
certame por publicação, com documentos, duas vagas, a primeira pessoa convocada e **sem** publicação
registrada. As pessoas são as das fixtures (*"Candidata 601"*, *"Candidata 602"*), sem nome real. O
servidor é a entrada `canal-125` do `.claude/launch.json` (porta 8125). Sem violação no console em
nenhuma tela percorrida.

| Passo | O que se viu | Requisito |
|---|---|---|
| Portal, convocação da 601 sem registro, pelo endereço direto | *"Ainda não há convocação neste Processo Seletivo."* — a tela de quem não tem convocação | FR-3982, FR-3983, FR-3984 |
| Gestão, tela de condução | pastilha *"Publicação não registrada"*; seção *"Publicações a registrar"* com *"O candidato só vê a convocação depois do registro."*; botão *"Registrar a publicação"*; nenhuma de *"Sem comunicação enviada"*, *"Emitir a comunicação"*, *"A comunicação sai no mesmo ato"*, *"contado do envio"* | FR-4000, D-007 |
| Gestão, os campos de texto | *"Este texto será mostrado ao candidato."* ao lado dos complementos; o derivado rotulado *"O candidato lerá este fundamento"* | FR-3991, FR-3992 |
| Gestão, chamar a 602 com complemento | o bloco *"Conferir o texto"* no topo, com o fundamento composto (*"… Complemento: Apresentar-se na secretaria do campus."*), *"Este texto será mostrado a 1 pessoa."*, o texto editável e *"Convocar"*; nada praticado até o clique | FR-3993 a FR-3996 |
| Gestão, confirmar | *"Convocação praticada. … O candidato só vê a convocação depois do registro."* | FR-4000 |
| Gestão, registrar a publicação das duas | *"Publicação registrada para 2 convocações: site do certame, 06/11/2026. O prazo corre a partir deste registro, e os candidatos já veem a convocação no portal."*; cartões com *"Publicação registrada em"* e *"contado do registro da publicação"*; nenhum *"Enviada em"* | FR-4000 |
| Portal, a mesma convocação depois do registro | *"Você foi convocado!"*, o prazo com o dia da semana; em *Sobre esta convocação*, *"Publicada em: site do certame, 06/11/2026"* e *"Vencimento registrado: …, contado da publicação"* | FR-3987, FR-3998 |

## Pendências

- **SC-1209** é validação humana: um operador que nunca viu a tela diz, sem ajuda, que o candidato ainda
  não vê a convocação.
- **O ajuste da D-004 na correção** (FR-3997) aguarda o usuário.
