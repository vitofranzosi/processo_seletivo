# Contrato: a tela

**Feature**: [spec.md](../spec.md) · **Atos**: [atos.md](atos.md)

## Rotas (`interface/urls.py`, ao lado das da ocupação)

| Caminho | Nome | Método |
|---|---|---|
| `editais/<edital_id>/marcos/<marco_id>/ocupacao/acrescentar-vagas` | `acrescentar-vagas` | `POST` |
| `editais/<edital_id>/marcos/<marco_id>/ocupacao/desfazer-acrescimo` | `desfazer-acrescimo` | `POST` |

O recorte vai no campo `lista`, como nas rotas da ocupação. As duas views abrem por
`_edital_para_classificar(..., somente_gestao=True)` e não levantam `Http404` por conta própria.

## Na ocupação (`ocupacao.html`), no bloco do recorte da linha geral

**Os números** (`UX-220`): o resumo ganha *"Vagas acrescidas depois da publicação"* entre *publicadas* e
*efetivas*, só quando há acréscimo; o número é link para a lista, logo abaixo, com âncora no recorte.

**A lista dos acréscimos**: uma tabela por recorte — data, espécie (*"Acréscimo"* ou *"Desfazimento"*),
quantidade, origem, fundamento, referência, quem registrou. Cada acréscimo com saldo tem o formulário
de desfazimento: quantidade (`input type="number" min="1"`), motivo (`p.campo` + `textarea rows="3"
required`) e o botão *"Conferir o desfazimento"*.

**O formulário do acréscimo**, só para quem apura e só no Perfil que o aceita: quantidade, origem
(`input type="text" required`), fundamento (`textarea`), referência (opcional) e o botão
*"Conferir o acréscimo"*. A ajuda diz: *"Escreva de onde a vaga veio — o número do Edital e o campus — e
por quê. Não escreva o nome de pessoas do outro Edital."* No Perfil que publicou cadastro de reserva e
reparte vagas entre modalidades, no lugar do formulário, a frase da recusa que o ato daria
(`acrescimo_fora_da_linha_geral`). No Perfil sem reserva — a maioria dos Editais —, nem formulário nem
frase: o acréscimo não é caminho de nada ali, e a recusa em toda tela de ocupação seria ruído
(*alinhado à implementação na convergência, T044*).

**Os botões** novos de `ocupacao.html`, na ordem, entram em `BOTOES` de
`tests/interface/test_telas_de_resultado_e_atos.py`: `("botao", "Conferir o acréscimo")` e
`("botao", "Conferir o desfazimento")`.

## A conferência (`ocupacao_acrescimo.html`, nova)

Renderizada pelo `POST` sem `confirmar`. Trilha no `caminho_do_contexto` como a da ocupação, terminando
em *"Acrescentar vaga"* ou *"Desfazer acréscimo"* com `aria-current="page"`.

| Bloco | O que diz |
|---|---|
| Título | *"Conferir o acréscimo de N vaga(s)"* — por extenso, sem *"(s)"*: *"de 1 vaga"*, *"de 3 vagas"* |
| As vagas | *"O recorte tem 0 vagas publicadas e 1 acrescida. Depois deste ato, terá 2 efetivas."* |
| Quem a ordem alcança (`UX-221`) | lista ordenada com posição e nome; com vagas sem pessoa, *"3 vagas; a ordem alcança só mais 2 pessoas."* |
| Os acréscimos anteriores | a mesma tabela da ocupação, para que a duplicata se veja (caso-limite da spec) |
| A apuração seguinte | *"A apuração seguinte será emitida por este ato, em seu nome, com o motivo: …"*; ou a causa que a impede, e o ato que falta |
| O que é imutável | `p.imutavel`: *"O acréscimo não se apaga. Se estiver errado, desfaça-o por outro ato, com motivo."* |
| O formulário | ocultos `lista`, `chave`, `confirmar=1`, `leitura` (a assinatura) e os campos digitados; botão `("botao", "Acrescentar N vaga")`/`"vagas"` (`UX-222`); link *"Voltar à ocupação"* |

No desfazimento, os mesmos blocos, com *"Desfazer N vaga(s) do acréscimo de dd/mm"* e o botão
*"Desfazer N vaga"*.

**Recusa**: volta à ocupação com `erro_da_ocupacao` e a frase do domínio, como a emissão já faz. A
recusa por leitura mudada (`leitura_do_recorte_mudou`) volta à **conferência** recalculada, com a
frase no topo — nunca à ocupação, onde a pessoa teria de redigitar.

## O que não muda

`convocacao.html`. A convocação lê a apuração, e o gesto *"Convocar os N"* aparece quando há titular
não chamado — inclusive o que a vaga acrescida criou.

## Vocabulário

`ocupacao_acrescimo.html` e `ocupacao/application/acrescimo.py` entram em `DA_016`
(`tests/test_vocabulario_da_ocupacao.py`) e em `TELAS` de `tests/test_vocabulario_da_composicao.py`.
Nenhum texto escrito por esta feature nas duas telas diz convocação, matrícula, aceite ou desistência.
