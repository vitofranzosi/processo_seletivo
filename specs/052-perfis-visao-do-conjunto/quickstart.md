# Quickstart — 052 · verificação no navegador

O que o shim de `tests/javascript/dom.js` não reproduz — foco, `hidden`, validação nativa, fragmento
do endereço — se verifica aqui, no preview, a 1280×900.

## Preparar

Um banco próprio (`ps_052_demo`), migrado com o superusuário como runtime, `seed_demo`, e o Edital em
elaboração multiplicado para 7 Perfis pelo mesmo POST da etapa (o script do relatório de 29/09).
Servidor com `INTERFACE_SELETOR_IDENTIDADE=true`; identidade `ana.elaboradora`, papéis elaborador e
gestor.

## Roteiro

1. **Conjunto** (US1, `SC-348`): abrir a etapa; a tabela começa na primeira tela; nenhum cartão à
   vista; medir a altura da página com zero e com um cartão aberto.
2. **Editar e passar** (US1): *Editar* no 2º; título *"Editando …"*, foco nele; mudar as vagas — a
   linha acompanha; *Próximo*; a linha deixada diz *"alterado — não salvo"*; *Voltar à lista* — foco
   no *Editar* do 3º; *Salvar*; nenhum aberto, *"Rascunho salvo"*, nenhuma linha alterada.
3. **Inválido escondido** (US2, `SC-349`): esvaziar o código de uma Modalidade do 1º, abrir o 3º,
   *Salvar* → o 1º abre, foco no campo, balão do navegador. Repetir com o código do Perfil, o rótulo
   de um fato e o limite do cadastro reserva (marca do `validacao.js`).
4. **Recusa do servidor** (US2): provocar recusa num Perfil (duas Modalidades com o mesmo código em
   Perfis distintos não recusa; use o limite de reserva negativo pelo inspetor) → a tela volta com
   aquele aberto.
5. **Envio que volta sem gravar** (R-007): com o 4º aberto, *Preencher pelo percentual* → a tela volta
   com o 4º aberto; as linhas alcançadas dizem *"alterado — não salvo"*.
6. **Gestos** (US3): *Acrescentar Perfil* → cartão novo aberto, foco no Código; duplicar o 1º → a cópia
   aberta, logo depois dele na tabela; remover a cópia → foco no *Editar* seguinte; *Aplicar aos demais
   Perfis* numa Modalidade → prévia no alto; confirmar → tabela com a Modalidade nas 7 linhas.
7. **Dois Perfis** (`SC-351`, `D-002`): num Edital de dois, editar um campo de cada e salvar; contar
   cliques e rolagem.
8. **Acessibilidade** (`SC-352`): `read_page` — `th` de linha e de coluna, *Editar P0N* por nome,
   `aria-current` na linha em edição.
9. **Estreito** (`UX-121`): 375 px — sem rolagem horizontal da página.
10. **Sem script**: desligar JavaScript — a etapa de hoje, com a legenda nova.
