# Roteiro de verificação: A data de nascimento entra no cadastro do candidato

## Preparação

Banco próprio da worktree (ver o CLAUDE.md: `DB_NAME` como variável do `make`), migrado:

```bash
cd backend && make preparar DB_NAME=ps_180
```

Um Edital com inscrições abertas (o `seed_demo` serve) e o portal no navegador. O código de acesso
sai no terminal do `runserver`.

## Testes automatizados

```bash
cd backend && make lint check
cd backend && make test-pg DB_NAME=ps_180 PYTEST_ADDOPTS="tests/unit/identidade tests/portal tests/interface/test_conferencia_de_identidade.py tests/integration/inscricoes"
```

Depois, a suíte inteira uma vez (a regra nova alcança as fixtures de toda a suíte):

```bash
cd backend && make test-pg DB_NAME=ps_180
```

## Percurso manual

1. **Candidato novo** (história 1): e-mail novo → vaga → "Seus dados" pede três campos. Deixar a data
   em branco: recusa, e nome e CPF continuam lá. Digitar `31/02/2000`: "Esta data não existe". Digitar
   amanhã: recusa. Digitar `07/03/1998`: volta à vaga.
2. **Cadastro antigo** (história 2): no shell, apagar a data de uma identidade com nome e CPF
   (`CandidateIdentity.objects.filter(...).update(data_nascimento=None)`), entrar com ela e abrir uma
   vaga: "Seus dados" com nome e CPF preenchidos e foco na data.
3. **Envio sem data**: com um rascunho aberto e a data apagada no shell, ir à revisão: a linha "Data de
   nascimento — Falta informar"; tentar enviar: recusa com caminho; informar e voltar: o envio passa.
4. **Congelamento**: depois do envio, "Seus dados" mostra CPF e data somente leitura.
5. **Conferência** (história 3): na gestão, com papel que consulta inscrições, abrir o detalhe da
   enviada; conferir sem motivo: recusa e nada aparece; com motivo: CPF completo e data. Na trilha
   (relatório de auditoria do Edital), o evento com o motivo e sem os valores. Com um papel sem
   consulta: 404.
6. **Requerimento**: convocar a inscrição (C12 dos cenários, ou helper no shell) e abrir o
   requerimento: a data vem preenchida.

## O que conferir no checklist

Os itens 3.03 e 3.04 da planilha do checklist (SC-2905).
