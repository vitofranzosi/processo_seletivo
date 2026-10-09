# Achado — O reenvio da convocação sugere um prazo novo que não existe

*Registrado em 09/10/2026, na investigação que descartou o reinício de prazo por reenvio. É
oportunidade de melhoria de texto, e não defeito de regra. Não é escopo de nenhuma feature aberta, e
fica para decisão do usuário.*

## O que foi descartado

A suspeita era que reenviar a comunicação reiniciasse o prazo, porque `envio_de` toma o envio
bem-sucedido mais recente (`backend/processo_seletivo/convocacao/application/selectors.py:119-126`).
Não reinicia, e por três razões:

- o vencimento é **data absoluta**, informada ao convocar;
- o envio só decide **se** o prazo corre;
- o reenvio depois do vencimento é recusado.

Isso está provado contra PostgreSQL em
`backend/tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py`.

## As duas oportunidades

**1. A mensagem do reenvio diz "contado do envio desta mensagem".**

- O texto é `COM_PRAZO`, em `backend/processo_seletivo/convocacao/application/comunicar.py:57`: *"Prazo
  para atender: até {vencimento}, contado do envio desta mensagem."*
- A data é a original, e está certa.
- A cláusula, porém, lida numa segunda mensagem, diz que o prazo se conta desta, e não da primeira.
  Quem recebe as duas pode concluir que ganhou prazo novo.
- A cláusula só faz sentido na primeira emissão, e nem ali é exata: o prazo **é** a data informada,
  e o envio só o põe em curso.

**2. O "enviada em" mostra só o último envio.**

- Ele aparece na gestão (`backend/processo_seletivo/interface/templates/interface/convocacao.html:403`)
  e no portal (`backend/processo_seletivo/portal/templates/portal/_convocacao_da_inscricao.html:22`).
- Depois de um reenvio, o cartão esconde quando a primeira mensagem saiu. É a informação que importa
  quando o Edital conta o prazo "a partir do recebimento do e-mail" (77, 58 e 59, item 8.3).
- O histórico da convocação tem todos os envios. O que falta é o cartão dizer que houve mais de um.

## Por que não é defeito de regra

Nenhuma das duas muda prazo, estado ou desfecho. As duas mudam o que a pessoa, ou quem conduz, **lê**
sobre o prazo. Num ato cujo efeito é perder ou não perder a vaga, isso é o suficiente para corrigir.
Mas a correção é de redação e apresentação, e cabe numa alteração pequena, quando o usuário decidir.

## De passagem, e não verificado

O vencimento é informado **ao convocar**, antes do envio. Se o primeiro envio falha e só tem sucesso
dias depois, a janela efetiva da pessoa encolhe. A única recusa é a do vencimento já passado
(`FR-269b`). O caminho previsto é suceder a convocação com vencimento novo, mas nada avisa o operador
de que o envio tardio encurtou o prazo. Não foi testado.
