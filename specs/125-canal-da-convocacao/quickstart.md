# Quickstart: verificar a 125

Pré-requisitos: os do README e do `CLAUDE.md` — PostgreSQL, `make preparar`, a suíte por
`make test-pg` com um `DB_NAME` próprio da worktree, e `INTERFACE_SELETOR_IDENTIDADE=true` para a
gestão. Nenhum nome real em banco de demonstração ou captura.

## 0. Antes da implantação: quantas convocações mudam de visibilidade

Num shell Django contra o banco da instalação, conte as convocações vigentes, sem desfecho, cuja forma
citada é a publicação e sem comunicação bem-sucedida na cadeia. Conte também as que já têm arquivo
apresentado. São as que somem do portal até o registro da publicação (R-009). O usuário decide se
registra antes.

## 1. Visibilidade (A)

1. Edital com Perfil *por publicação*. Convoque os titulares de um recorte com documento pedido e o
   Requerimento *na convocação*.
2. Entre no portal como um dos convocados. Nas sete superfícies do
   [contrato](contracts/superficies-do-portal.md), confira a resposta de ausência: o envio de documento
   pelo endereço direto devolve *"Recurso não encontrado."*, e nada é gravado.
3. Como outro inscrito do recorte, não convocado, abra a convocação: a tela não diz que o certame
   chegou a convocar.
4. Na gestão, confira a pastilha *"Publicação não registrada"* e a frase de que o candidato ainda não
   vê. Registre a publicação com uma referência.
5. Recarregue o portal: a convocação aparece nas sete superfícies, com *"Publicada em ‹referência›"*.
6. Repita com um Perfil *por mensagem* e o envio falhando (backend de e-mail recusando): a tela é a de
   hoje, com o prazo não iniciado.
7. Corrija a convocação publicada (`120`): a sucessora continua visível, com *"... a partir da
   publicação da convocação."* (D-001).

## 2. Aviso e prévia (B)

1. Em cada formulário do [contrato](contracts/previa-do-texto.md), confira o aviso ao lado do campo,
   com e sem script.
2. Convoque os titulares com um complemento: o passo *"Conferir o texto"* mostra o fundamento composto
   e *"Este texto será mostrado a N pessoas."* Volte, corrija e confirme.
3. No portal de um dos convocados, depois de registrada a publicação, o fundamento é idêntico ao da
   prévia.
4. Registre um desfecho: o passo aparece sempre, com a linha que o candidato lerá.

## 3. Vocabulário (C)

Percorra as telas do [inventário](contracts/vocabulario-do-canal.md) nas duas formas. A varredura
automatizada faz o mesmo:

```bash
cd backend && make lint check test-pg
```

## 4. Antes de cada PR

- `uv run pytest tests/test_citacoes_de_requisito.py tests/test_readme_acompanha_o_codigo.py`
- a suíte inteira contra PostgreSQL, e `rastreabilidade.md` com uma linha por `FR-`, `SC-` e caso-limite.
