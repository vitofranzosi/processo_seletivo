# Quickstart: validar a orientação da verificação

Roteiro de verificação da `168`. As frases estão em [contracts/frases.md](contracts/frases.md); os
dados, em [data-model.md](data-model.md).

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado, e um `DB_NAME` próprio (*As armadilhas caras*, no
  `CLAUDE.md`).
- `make preparar`, que roda o provisionamento três vezes. Ele protege **65** tabelas, como antes, e num
  banco que já existia imprime "Modelos de aviso: 1 criados" por unidade, que é o modelo do passo.

## 1. A suíte da feature

```bash
cd backend && DB_NAME=gps_168 make test-pg PYTEST_ADDOPTS="tests/unit/portal/test_passo_da_etapa.py tests/portal/test_degrau_do_passo.py tests/portal/test_vocabulario_do_passo.py tests/integration/avisos/test_aviso_do_passo.py tests/interface/test_pendencias_da_etapa_restrita.py tests/integration/treinamento/test_cenario_c18.py"
```

Esperado: tudo passa. Depois, os diretórios tocados (`tests/portal`, `tests/integration/avisos`,
`tests/interface`, `tests/unit/interface`, `tests/integration/treinamento`, `tests/performance`), e a
suíte inteira uma vez, sozinha no cluster.

## 2. Cenários de aceitação, pelo teste que os prova

| Cenário | Onde | Esperado |
|---|---|---|
| US1, o degrau | `test_passo_da_etapa.py`, `test_degrau_do_passo.py` | os três rótulos nas condições da data-model; a consequência pelo efeito; o link para o Edital; nada para quem está só na ampla; a convocação com a linha do passo |
| US2, o aviso | `test_aviso_do_passo.py` | universo dos participantes sem Resultado; um Aviso por Perfil; já avisado; CHECK; e-mail sem Modalidade; chave dos avisos |
| US3, o Centro e Minhas atividades | `test_pendencias_da_etapa_restrita.py` | faltam por membro igual à Mesa; AVISAR até o fim do período; período vencido; "até dd/mm" na linha de avaliar |
| US4, o vídeo | `test_degrau_do_passo.py`, `test_pendencias_da_etapa_restrita.py` | estados da `166` no degrau com a chave; nenhuma palavra "vídeo" sem ela; o cartão separado não existe; "Encaminhar N" |
| US5, o cenário | `test_cenario_c18.py` | os quatro estados no Centro e no acompanhamento |
| SC-2414, o custo | `test_degrau_do_passo.py` | o acompanhamento sem Etapa restrita faz as mesmas consultas que antes |

## 3. O percurso no navegador

1. No `backend/.env`, ligue `CENARIOS_DE_TREINAMENTO=true`, `INTERFACE_SELETOR_IDENTIDADE=true` e
   `AVISOS_AOS_CANDIDATOS=true`. Suba o servidor pela entrada da worktree no `.claude/launch.json`.
2. Rode `carregar_cenario_de_treinamento C18 --banco <DB_NAME>`.
3. Como a presidência do cenário, abra o Centro do Edital. Deve aparecer:
   - a Etapa pelo nome;
   - "Avisar 1 inscrição sobre {etapa}";
   - a nota "faltam: …" com o fim do período.
4. Clique em "Avisar". Confira na prévia o universo e o texto sem a Modalidade, e confirme. Depois
   rode `manage.py despachar_avisos` e leia a mensagem no terminal do comando.
5. Como um avaliador do cenário, abra Minhas atividades e confira "Avaliar 1 inscrição · até dd/mm".
6. Como o candidato não avisado, entre no portal com o código. O código sai no terminal do servidor.
   Confira "Falta um passo seu", a consequência e o link para o Edital.
7. Capture o Centro, Minhas atividades e o acompanhamento, a 1280 px e a 375 px. Confira que o console
   não traz violação de CSP.
