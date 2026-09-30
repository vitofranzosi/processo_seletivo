# Quickstart — 053 · verificação no navegador

O que o shim de `tests/javascript/dom.js` não reproduz — foco, `hidden`, `details`, validação nativa,
fragmento do endereço — se verifica aqui, no preview, a 1280×900.

## Preparar

Um banco próprio (`ps_053_demo`), criado com `createdb`, migrado com o superusuário como runtime, e
`seed_demo`. O Edital em elaboração (76/2027, 2 Perfis) é multiplicado para 7 pelo mesmo POST da etapa
Perfis, e o marco do primeiro Perfil, com 2 critérios de desempate, é aplicado aos demais pelo
*"Aplicar aos demais Perfis"* da `051` — prévia e confirmação, pelo POST da etapa. Uma cópia do banco
nesse estado (`createdb -T`) permite recomeçar. Servidor com `INTERFACE_SELETOR_IDENTIDADE=true`;
identidade `ana.elaboradora`, papéis elaborador e gestor.

## Roteiro

1. **Conjunto** (US1, `SC-354`): abrir a etapa; a tabela começa na primeira tela; nenhum cartão à
   vista; medir a altura da página com zero e com um cartão aberto, contra os 12,5 mil px de hoje.
2. **Editar e passar** (US1): *Editar* no 2º; título *"Editando …"*, foco nele; mudar o prazo do
   recurso — a linha acompanha; trocar a forma da ordem para sorteio — o cartão se reconstrói e a linha
   acompanha; *Próximo*; a linha deixada diz *"alterado — não salvo"*; *Voltar à lista* — foco no
   *Editar* do 3º; *Salvar*; nenhum aberto, *"Rascunho salvo"*, nenhuma linha alterada.
3. **Aplicar a todos** (US2, `SC-355`): *Editar* no 1º, mudar o corte, *Aplicar aos demais Perfis* →
   prévia no alto, o 1º aberto abaixo dela; confirmar → tabela, nenhum aberto, as 7 linhas com o mesmo
   corte e a origem nas 6 alcançadas; editar e salvar uma delas → a origem sai só dela.
4. **Inválido escondido** (US3, `SC-356`): esvaziar o código do marco do 1º, abrir o 3º, *Salvar* → o
   1º abre, foco no campo, balão do navegador. Repetir com um critério (o alvo), e com o prazo do
   recurso negativo dentro do bloco fechado — o bloco abre.
5. **Recusa do servidor** (US3, `SC-357`): provocar recusa num critério de um Perfil fora de vista
   (duas ordens iguais, que só o servidor recusa) → a tela volta com aquele Perfil aberto e o link do
   resumo leva ao campo.
6. **Envio que volta sem gravar** (`FR-971`): com o 4º aberto, pedir e cancelar uma prévia → o 4º
   volta aberto, a notícia no alto; as linhas devolvidas sem mudança não dizem *"alterado"*.
7. **Pendências** (US4): um Perfil com pendência de marco — o bloco no alto a diz, e a linha dele diz
   *"1 pendência"*.
8. **Rascunho local** (US5): alterar dois Perfis, recarregar sem salvar → o aviso; restaurar → os dois
   de volta, *"alterado — não salvo"* nas duas linhas.
9. **Dois Perfis e um** (`FR-961`): no Edital de dois, a tabela; num Edital de um, o cartão aberto e sem
   tabela.
10. **Dois marcos por Perfil** (`D-002`): acrescentar um segundo marco a um Perfil → a linha continua
    uma, com dois blocos por coluna.
11. **Acessibilidade** (`SC-359`): `read_page` — `th` de linha e de coluna, *Editar* com o código,
    `aria-current` na linha em edição.
12. **Estreito** (`UX-128`): 375 px — sem rolagem horizontal da página.
13. **Perfis** (`SC-360`): a etapa Perfis da `052` continua a mesma — tabela, editar, inválido
    escondido —, agora pelo script comum.
