# Contrato do portal do candidato

## "Seus dados" — `GET|POST portal:meus-dados` (rota existente)

**Entrada do POST**: `nome`, `cpf` (ignorado quando congelado), `data_nascimento` (texto `dd/mm/aaaa` ou
`aaaa-mm-dd`; ignorado quando a data existe e congelou).

**Tela**:
- três campos, nesta ordem: Nome completo, CPF, Data de nascimento;
- o campo da data é `type="text"`, `inputmode="numeric"`, `autocomplete="bday"`, com a dica
  "dia/mês/ano, por exemplo 07/03/1998" (UX-1000);
- a frase de finalidade (FR-8314) entra no parágrafo existente: o nome, o CPF e a data de nascimento
  identificam a pessoa nas inscrições, e a data serve para a instituição confirmar a identidade em
  caso de dúvida;
- data congelada: o campo aparece somente leitura, com a mesma frase de atendimento do CPF congelado;
- cadastro antigo sem data (UX-1001): nome e CPF aparecem preenchidos, e o foco vai para a data.

**Respostas**:
- POST válido → mesmo destino de hoje: de volta à vaga, ou "Seus dados foram guardados." e
  inscrições;
- POST com recusa → 200 com a tela, os três valores como digitados e a recusa ligada ao campo por
  `aria-describedby` (FR-8307). As frases estão na pesquisa (R4).

## Portas que levam a "Seus dados" (sem mudança de código além de `falta_o_nucleo`)

- volta do código de acesso a caminho de uma vaga;
- `POST portal:inscrever`.

Em ambas, a identidade com nome e CPF e sem data é levada a "Seus dados" e volta ao destino (FR-8302).

## Revisão da inscrição — `portal:revisao` (rota existente)

- A lista "dos seus dados" ganha a linha **Data de nascimento**, com o valor `dd/mm/aaaa` ou, se
  faltar, "Falta informar", e o caminho para "Seus dados". Esse caminho leva o destino de volta à
  revisão (FR-8303).
- O envio sem data é recusado pelo comando (`birth_date_required`, 422), e a tela mostra a frase com
  o mesmo caminho.

## Requerimento de matrícula — `portal:requerimento` (rota existente)

- Na primeira abertura, o campo "Data de nascimento" já vem preenchido com a data do cadastro, se o
  requerimento não herdou outra (FR-8313). Alterá-lo ali não muda o cadastro.

## O que não muda

- O comprovante não mostra a data.
- Nenhuma página pública, publicação ou URL contém a data (FR-8311).
- Nenhum caminho de acesso, de retomada ou de credencial pede ou compara a data (FR-8310).
