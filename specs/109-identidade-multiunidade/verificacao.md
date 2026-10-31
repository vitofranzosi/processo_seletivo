# Verificação da 109

Medido em 31/10/2026, na branch `claude/109-identidade-multiunidade` sobre `origin/main` em
`77f35fd3`, contra PostgreSQL 16 local, com `DB_NAME=ps_109_identidade`.

## A suíte

`cd backend && make lint check test-pg`, 4 workers, `--dist worksteal`:

| Passo | Resultado |
|---|---|
| `ruff check` | limpo |
| `ruff format --check` | 1691 arquivos já formatados |
| `manage.py check` | sem problemas |
| `makemigrations --check` | nenhuma mudança pendente |
| `pytest` | **13848 passando, 14 pulados, nenhuma falha**, em 529s |

Os 14 pulados são os 12 da medição de referência (`CLAUDE.md`) mais dois que vêm de grupos opcionais
ausentes nesta worktree: a contagem real do tokenizer (`assistente`, sem `tokenizers`) e as jornadas
pelo navegador da `107` (`navegador`, sem `playwright`). O CI instala os dois.

A primeira rodada, antes dos ajustes abaixo, deu 37 falhas: 24 testes de unidade das mensagens, que
passaram a receber a assinatura, 12 orçamentos de consulta e o README, editado no meio da execução.

## Os testes existentes que mudaram, e por quê

| Arquivo | Mudança | Motivo |
|---|---|---|
| `tests/unit/avisos/test_mensagem.py` | o `_congelar` passa `assinatura="Cefor/Ifes"` | `congelar` recebe a assinatura pronta (D-006) |
| `tests/unit/convocacao/test_mensagem.py` | os três `dados` levam `"assinatura": "Cefor/Ifes"` | a mensagem de convocação recebe a assinatura pronta, sem recaída que consultaria o banco num teste de unidade |
| `tests/interface/test_proveniencia_do_recurso.py` | 8 → 9 consultas | a sigla da unidade na moldura da gestão (D-001) |
| `tests/interface/test_instrucao_na_peca.py` | 13 → 14 | idem |
| `tests/performance/test_comissao_em_escala.py` | teto 20 → 21 | idem |
| `tests/interface/test_limpeza_dos_achados_da_etapa_4.py` | a tabela medida em 18/10 ganha `_MOLDURA` (+1) nas seis telas e, na prévia do aviso, `_UNIDADE_DO_EDITAL` (+1) | a moldura; e a unidade do Edital, que assina o rodapé que o editor mostra |
| `tests/performance/test_resultado_publico.py` | teto 5 → 6 | a identificação da implantação na moldura do portal (D-002) |

Nenhuma asserção de comportamento foi afrouxada: as mudanças de orçamento são de uma consulta
constante por página, e cada propriedade "não cresce com…" continua medida.

## Antes × depois do Cefor (SC-1031)

Uma captura descartável, fora do commit, rodou o mesmo roteiro na `main` em `ca1e53ed` e nesta
branch: o HTML inteiro de oito páginas (lista da gestão com papel e sem papel, minhas etapas sem
papel, recusa, topo sem ator, página de acesso, vitrine, 404), com o token CSRF e os UUIDs
normalizados, os trechos de marca, título e "a quem pedir acesso", as cinco mensagens (código de
acesso, código de vínculo, mudança de credencial, comprovante, convocação) e o rodapé do aviso.

**As dezoito comparações saíram idênticas.** A única diferença foi o código-fonte da frase do envio
acima do limite, em `interface/erros.py`, que deixou de ser literal; o texto que ela exibe para o
Cefor é conferido literalmente por
`tests/unidades/test_identificacao_multiunidade.py::test_8_o_cefor_sozinho_diz_exatamente_o_que_dizia`.

## Os oito cenários (SC-1032, SC-1033)

`tests/unidades/test_identificacao_multiunidade.py`, com o Cefor da fixture e o `campus-a`
registrado só pelo registro:

| Cenário | Casos |
|---|---|
| 1. cada unidade com a sua identificação | `test_1_cada_unidade_aparece_na_gestao_com_a_sua_identificacao`, `test_1_a_recusa_de_envio_grande_diz_a_unidade_de_quem_enviou` |
| 2. o Edital usa a unidade dele | `test_2_3_5_6_…`, `test_4_o_aviso_…`, `test_4_a_convocacao_…` |
| 3. o PDF mostra a unidade certa | `test_2_3_5_6_…` |
| 4. as mensagens com o atendimento correspondente | `test_4_o_aviso_…`, `test_4_a_convocacao_…`, `test_4_a_conta_do_candidato_…` |
| 5. o portal não depende da unidade ativa do operador | `test_2_3_5_6_…` |
| 6. a troca no registro não altera o publicado | `test_2_3_5_6_…`, `test_4_o_aviso_…` (o texto congelado) |
| 7. nada vaza entre unidades | `test_7_a_404_e_a_moldura_nao_dizem_a_unidade_do_objeto_alheio`, e os `Cefor not in` / `Campus A not in` dos demais |
| 8. o Cefor inalterado | `test_8_o_cefor_sozinho_diz_exatamente_o_que_dizia` |

Mais: o resolvedor (quatro casos), o registro com o canal (seis) e o guardião da SC-1035, que lê os
oito templates e os cinco módulos de mensagem — conferido contra as versões da `main`, onde acusa
seis, um e um textos com "Cefor".

## O quickstart, executado

Num banco descartável (`ps_109_ensaio`, apagado depois): `make preparar` (46 de 46 tabelas
protegidas; `Unidades: 1 criadas`), `make seed`, e a leitura das molduras com o cliente de teste do
Django sobre o banco real:

| | Só o Cefor | Com o `campus-a` pelo `--arquivo` |
|---|---|---|
| gestão (seletor, Cefor) | `Processos Seletivos — Cefor/Ifes` | `Processos Seletivos — Cefor/Ifes` |
| vitrine | `Processos seletivos — Cefor/Ifes` | `Processos seletivos — Ifes` |
| seleção do Cefor (Edital 01/2026 do seed) | `… — Cefor/Ifes` | `… — Cefor/Ifes` |
| página de acesso | — | `Acesso à gestão — Gestão de Processos Seletivos · Ifes` |
| 404 | `Página não encontrada — Cefor/Ifes` | `Página não encontrada — Ifes` |

A sincronização pelo `--arquivo` disse `1 criadas, 0 alteradas, 1 sem mudança` e criou os três
modelos de aviso do campus; o `unidades.json` versionado não mudou. Depois disso, o mesmo banco
recusa o arquivo versionado com `unidade_retirada` — anotado no quickstart.

## A revisão de código de 31/10

Sete achados sobre o diff do #349; cinco corrigidos na mesma branch:

- a prévia do aviso lia a unidade do Edital duas vezes (texto e rodapé do editor), além da moldura:
  agora lê uma, e a passa aos dois;
- o assistente de dúvidas e o `do_ato` ganharam teste — a subconsulta do canal com Editais
  publicados de verdade nas duas unidades, e a recaída do ato sem sigla gravada;
- o assistente de dúvidas deixou de montar uma `Identificacao` só para calcular a recaída;
- o comentário de `recusa.html` voltou a citar a frase inteira.

Depois das correções, `make lint check test-pg` deu **13849 passando, 14 pulados**, sem falha (o caso a mais é o do `do_ato`).

Dois ficaram, com o motivo: o `do_ato` não carrega o canal da unidade (carregá-lo voltaria a ler o
registro, e nenhuma chamada usa o canal dele; a docstring manda a `da_unidade`), e a unidade
desativada que ainda tem Edital na vitrine não conta para a moldura — é o comportamento que a spec
declara nos casos-limite, e a pergunta foi acrescentada à P-1. A tela da convocação do candidato
continua sem teste próprio do canal da unidade: montar uma convocação pede o certame inteiro, e o
canal dela sai da mesma `da_unidade(...).canal()` que os cenários 4 cobrem.

## O que não foi executado

- **Conferência visual no navegador.** As molduras foram lidas como HTML; nenhuma folha mudou, e o
  HTML do Cefor é idêntico ao de antes.
- **As jornadas pelo navegador da `107`**, puladas aqui sem o Playwright. A `109` não toca nas telas
  de acesso.
- **O CI**, que roda no PR.
