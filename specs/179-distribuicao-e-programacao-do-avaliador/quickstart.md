# Quickstart: validar a 179

Roteiro de validação, um por incremento. Os detalhes estão em [contracts/telas.md](contracts/telas.md),
[contracts/validacao.md](contracts/validacao.md) e [data-model.md](data-model.md).

## Pré-requisitos

- A worktree com `backend/.env`, PostgreSQL local e `DB_NAME` próprio (o `CLAUDE.md`, *Um banco de
  teste por worktree*): `make test-pg DB_NAME=ps_178`, e não `DB_NAME=… make`.
- Para percorrer pela tela: `make preparar`, `INTERFACE_SELETOR_IDENTIDADE=true` e o cenário de
  treinamento C20 (a Entrevista com vinte participantes e a agenda vazia), que exige
  `CENARIOS_DE_TREINAMENTO=true` no ambiente do comando.

## Incremento 1 — distribuição coerente e programação

**Suíte da mudança** (enquanto trabalha, só o que a mudança toca):

```bash
cd backend && make test-pg DB_NAME=ps_178 PYTEST_ADDOPTS="tests/unit/avaliacoes tests/integration/avaliacoes tests/integration/agendamento tests/unit/agendamento tests/interface/test_distribuicao.py tests/interface/test_distribuicao_por_sessao.py tests/interface/test_minha_etapa.py tests/interface/test_programacao_na_mesa.py tests/interface/test_minhas_atividades.py tests/interface/test_agenda_e_avaliadores.py tests/interface/test_coerencia_na_gestao.py tests/interface/test_agenda_da_etapa_publicada.py tests/performance/test_escala_da_mesa.py tests/performance/test_minhas_atividades_em_escala.py"
```

**Percurso pela tela** (C20, como presidência e como dois membros):

1. Configurar a agenda com duas bancas, dois dias; preencher; conferir; publicar.
2. Pela tela Comissão, incluir quatro membros e alocá-los à Etapa (no Incremento 2, o C20 já os traz, research T-020). Na Distribuição, filtrar "dia 1 · Banca 01", selecionar todas,
   marcar dois membros, distribuir. Repetir para a Banca 02 com os outros dois.
3. Tentar atribuir a um membro da Banca 01 uma pessoa da Banca 02 no mesmo horário: a linha volta
   recusada com o nome, o horário e a banca do outro compromisso.
4. Pedir o rodízio para o dia 2: a proposta não tem par simultâneo.
5. Remarcar uma pessoa para um horário em que um avaliador dela está ocupado: a tela diz quem fica em
   conflito antes; confirmar; ver o conflito no cartão da Agenda da Distribuição e na agenda publicada.
6. Entrar como um dos membros: Minhas atividades diz a próxima entrevista; a Mesa abre na
   Programação, com os dois dias, a banca, o botão da sala; "Por inscrição" continua como antes.
7. Abrir a página pública da agenda e o PDF do ato: nenhum nome de avaliador.

**Antes do PR:** `make lint check`, e a suíte inteira **uma vez** (`make test-pg DB_NAME=ps_178`).

## Incremento 2 — aviso aos avaliadores

```bash
cd backend && make test-pg DB_NAME=ps_178 PYTEST_ADDOPTS="tests/unit/avisos tests/integration/avisos tests/integration/avaliacoes tests/unit/avaliacoes tests/test_situacoes_de_mensagem.py tests/interface/test_avisar_os_avaliadores.py tests/interface/test_agenda_da_etapa_publicada.py"
```

1. Com o percurso acima concluído, na agenda publicada, a seção Avaliadores diz "pronta para 4" e
   oferece "Avisar os avaliadores (4)". Abrir: a confirmação mostra quem recebe e a mensagem.
2. Confirmar e rodar `manage.py despachar_avisos` **à mão** (o `CLAUDE.md`: em desenvolvimento,
   ninguém roda por você); as mensagens saem no terminal do comando.
3. Remarcar uma pessoa: os dois avaliadores dela aparecem como "mudou"; "Avisar as mudanças (2)";
   despachar; só dois e-mails.
4. Repetir o gesto sem mudança: nada é criado.
5. Os avaliadores do C20 têm conta com e-mail de exemplo (research T-020): os quatro aparecem
   prontos, e as mensagens saem no terminal do despacho. Para ver "sem e-mail", acrescente à comissão,
   pela tela, um membro com identificador inventado.
