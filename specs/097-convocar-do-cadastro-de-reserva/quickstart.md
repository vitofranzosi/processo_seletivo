# Quickstart: Convocar do cadastro de reserva, na ordem publicada

**Feature**: [spec.md](spec.md) · **Tela**: [contracts/tela.md](contracts/tela.md)

## Verificação automática

```bash
cd backend && make lint check test-pg
```

Os arquivos desta feature, para rodar sozinhos durante o trabalho:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER="$USER" DB_RUNTIME_USER="$USER" DB_NAME=ps_097 uv run pytest -n 4 --dist worksteal tests/unit/ocupacao/test_acrescimo.py tests/unit/ocupacao/test_acrescimo_append_only.py tests/integration/ocupacao/test_acrescimo.py tests/integration/convocacao/test_reserva.py tests/interface/test_acrescimo.py tests/unit/editais/test_reserva_convocada_fora.py
```

O `make test-pg` não aceita lista de arquivos; o par `TEST_DB_ENGINE` e usuário é o que ele monta, e o
`DB_NAME` próprio evita disputar o banco de teste de outra worktree.

Depois da migration, `make preparar` em banco já provisionado: a linha `N de M` passa a dizer **41**.

## O cenário do TMD, pela gestão (`SC-920`)

**Preparação.** Um Edital publicado com um Perfil de **0 vagas imediatas**, **cadastro de reserva sem
limite**, só a linha geral no quadro e um marco por sorteio cuja regra de corte tenha alvo fixo que
alcance a reserva — por exemplo, 20, sem excedente, sem Etapa governada. Relação publicada, ocorrência
observada, sorteio constituído e corte emitido: é o ciclo da `021`, e as telas dele já existem. Numa
demonstração, faça-o numa cópia do banco (`make preparar DB_NAME=ps_097`), nunca no de
desenvolvimento.

**Na Revisão, antes de publicar** (`US2`):

1. O aviso do Perfil diz que a convocação depende de vagas acrescidas depois da publicação, e que a
   convocação poderá alcançar até 20 classificados. **Não** diz que ela é feita fora do sistema.

**Na ocupação do marco** (`US1`):

2. O recorte da ampla mostra *0 vagas publicadas* e, por não ter apuração, *ainda não apurado*. O
   formulário *"Acrescentar vagas"* está no bloco.
3. Quantidade **1**; origem *"Edital Multicampi nº 20/2026, Campus Vitória"*; fundamento *"vaga não
   preenchida no Edital regular"*. **Conferir o acréscimo.**
4. A conferência diz: *0 publicadas; depois deste ato, 1 efetiva*; a ordem alcança **o 1º do sorteio**,
   pelo nome; a apuração seguinte será emitida pelo ato, em seu nome. **Acrescentar 1 vaga.**
5. De volta à ocupação: *1 vaga acrescida depois da publicação*, link para a lista; a apuração vigente
   diz 1 efetiva, 1 ocupada, 0 faltando; a lista mostra o acréscimo com a origem e o seu nome.

**Na convocação do recorte** (o que já existe):

6. *"Convocar os 1"* aparece, com o 1º do sorteio. Convocar por publicação, registrar onde publicou.
7. Registrar o **não atendimento** quando o prazo vencer. A vaga volta a faltar.
8. O 2º do sorteio é chamável como suplente, **sem novo acréscimo**.

**O desfazimento** (`US3`), numa segunda vaga:

9. Acrescentar mais 1, e logo desfazê-la com o motivo *"matrícula efetivada no regular"*: a
   conferência diz que o 3º do sorteio sai da conta, e o ato é aceito — ninguém o chamou.
10. Tentar desfazer a primeira, depois de convocar quem a ocupa: recusado, com a frase de que há pessoa
    chamada para a vaga e o desfecho a registrar antes.

**Quem não pode** (`FR-2465`):

11. Como auditor, a ocupação mostra os acréscimos e não mostra o formulário; diz a quem pedir.

## O que olhar fora da tela

- A trilha do Edital lista *"Acréscimo de vagas"* e a apuração que ele emitiu, com o mesmo autor.
- No portal, a página pública da seleção continua dizendo **0 vagas imediatas e cadastro de reserva**,
  e o convocado vê a convocação com o fundamento que cita a apuração — nem a origem nem o fundamento
  do acréscimo aparecem (`FR-2467`, `FR-2468`).
