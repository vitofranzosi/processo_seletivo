# Verificação: Cadastro de unidades administrado pela aplicação (110)

Três seções, uma por incremento (D-019), e uma quarta, separada, para a validação funcional por
pessoas — critério de aceite humano, que nenhum resultado de suíte substitui (SC-1048, T051).

## A — Integridade do escopo (31/10/2026)

**Base**: `main` em `81ce6e94`, com a `108` e a `109` integradas.

| Verificação | Resultado |
|---|---|
| `ruff check` e `ruff format --check` | limpos |
| `make check` (inclui `makemigrations --check`) | sem problema; nenhuma migration pendente |
| Os casos novos e o guardião das migrations, isolados (`test_escopo_imutavel`, `test_isolamento_entre_unidades`, `agenda/test_fonte`, `migrations/test_migrations`) | 31 passando, nenhum pulado |
| `make test-pg`, 4 workers, `DB_NAME=ps_110_escopo` | **13905 passando, 14 pulados**, 0 falhas, 549,9 s |

**Os 14 pulados** são os 12 deliberados do `CLAUDE.md` mais dois de grupo opcional ausente nesta
worktree — o tokenizer (`assistente`) e as jornadas do navegador (`navegador`). Nenhum caso desta
feature foi pulado: os gatilhos só se testam no PostgreSQL, e a suíte rodou nele.

**O que se provou.**

- Os dois gatilhos recusam a mudança do escopo de Processo e de Edital por `update()`, por `save()`
  e por SQL direto, com a conexão superusuária da suíte; o `save()` completo que regrava o mesmo
  escopo passa, e as outras colunas mudam (FR-3333). Os gatilhos da `060` continuam (FR-3334).
- O único teste que mudava o escopo, o da agenda, passou a criar o Edital da Serra pelos atores da
  Serra, e verifica o mesmo que verificava (FR-3335, EC-15).
- As quatro áreas sem segunda unidade (D-014) respondem como inexistente ao ator de `campus-a`, cada
  uma depois de um controle em que o ator do Cefor alcança o objeto, e nada grava — nem evento de
  trilha (FR-3336). **Nenhum vazamento.**

**Achado registrado, sem correção.** A API administrativa valida o corpo antes de conferir o
escopo: um corpo inválido recebe 422 tanto para objeto alheio quanto para inexistente. Não revela
existência — a resposta é a mesma nos dois casos —, e por isso não é vazamento. O teste manda corpos
válidos para chegar à conferência do escopo.

**Migrations.** `processos` passou de 4 para 5 no guardião da `022`, com justificativa; os dois
gatilhos entraram em `TRIGGERS_POR_APP["processos"]`, o que exercita a reversão. Nenhuma tabela
append-only nova: o `M` do provisionamento continua 46.

## B — Entrada de homologação (31/10/2026)

**Base**: o incremento A (PR #350), empilhado — a spec só existe nele. Recomendação de ambiente
aceita pelo usuário em 31/10.

| Verificação | Resultado |
|---|---|
| `ruff check` e `ruff format --check` | limpos |
| `make check` | sem problema; nenhuma migration |
| `tests/homologacao`, `tests/test_configuracao_producao.py` e `tests/seguranca`, isolados | 231 passando |
| `make test-pg`, 4 workers, `DB_NAME=ps_110_escopo` | **13917 passando, 14 pulados**, 0 falhas, 829,6 s |

Os 14 pulados são os mesmos do incremento A.

**O que se provou.**

- O provedor é subclasse do simulado da `106`: a declaração de teste e o bilhete de uso único vêm
  da herança, sem criptografia própria e sem proteção nova (FR-3342).
- Produção o recusa no *boot* pelo pacote e, copiado para fora de `tests.`, pela declaração; sob a
  marca de produção, `provedor_configurado` o apaga em execução, e a entrada responde 503 (FR-3342).
- O caminho do roteiro G funciona de ponta a ponta: a pessoa cadastrada por
  `conceder_administracao_institucional --provedor homologacao` aparece na página, só ela, e
  escolhê-la entra no escopo institucional com a permissão do vínculo (FR-3343).
- O bilhete escolhido não serve de novo, e o retorno sem o estado da ida é recusado, como com
  qualquer adaptador (FR-3343, FR-3023 da `106`).
- **Simplificado depois, no mesmo dia**: saiu o descarte dos bilhetes das outras linhas da página.
  Quem está na página já escolhe qualquer pessoa, e o ambiente é local, sintético e descartável — o
  descarte não protegia nada. Medido de novo só o que essa mudança alcança:
  `tests/homologacao`, `tests/test_configuracao_producao.py`, `tests/seguranca` e os três guardiões
  de documentação, isolados contra PostgreSQL — **1346 passando**. A mudança é só de código de
  teste; a suíte inteira medida acima não foi repetida.
- A suíte de segurança da `106` e da `107` passa sem mudança (`tests/seguranca`).

**A VM de homologação não mudou**: nenhuma settings, nenhum roteiro. O ambiente novo está no §10.3
do guia de produção.

## C — Fonte oficial e administração (31/10/2026)

**Base**: o incremento B (PR #351), empilhado sobre o A (PR #350); a CI dos dois estava verde.

| Verificação | Resultado |
|---|---|
| `ruff check` e `ruff format --check` | limpos |
| `make check` (inclui `makemigrations --check`) | sem problema; **nenhuma migration** nesta parte |
| `make test-pg`, 4 workers, `DB_NAME=ps_110_escopo` | **14178 passando, 13 pulados, 1 falha**, 640,9 s |
| a falha, corrigida e rodada de novo (`tests/homologacao`, isolado) | 7 passando |
| `make test-navegador` (`tests/navegador`, com a jornada nova) | 7 passando |

**A falha** era do teste do provedor de homologação (B), que conferia o rótulo antigo do papel —
"Administrador institucional de acessos" —, que este incremento renomeia. Corrigida a asserção; a
suíte inteira não foi repetida depois dessa linha. **Os 13 pulados** são os 12 deliberados do
`CLAUDE.md` mais o do tokenizer; o do navegador deixou de pular porque o grupo foi instalado para
rodar a jornada.

**O que se provou**, pelos quinze itens do pedido (mapa no [plan](plan.md)):

1. o Cefor continua sem ação (`test_o_cefor_continua_sem_acao`);
2. a segunda unidade pela aplicação (`test_registrar_uma_unidade`, a jornada no navegador);
3. ela permanece no banco sem estar no arquivo (`test_unidade_fora_do_arquivo_e_valores_diferentes_permanecem`);
4. reinicializar não altera nem remove (`test_a_inicializacao_nao_altera_o_registro`);
5. nome e canal editados não voltam no deploy (`test_a_semente_nao_desfaz_a_tela`);
6. sem `unidade:administrar` nada muda — 9 casos de uso × 12 atores, mais o envio forjado pela tela;
7. o código não muda (`test_o_codigo_enviado_na_alteracao_e_ignorado`, e o gatilho da `060`);
8. o escopo de Processo e Edital não muda no banco (incremento A);
9. desativada não recebe Processo nem acesso e conduz o existente;
10. reativada volta a receber;
11. duas unidades não compartilham acesso, autoridade nem Edital (este incremento e o isolamento do A);
12. o publicado não muda, byte a byte, depois de editar a unidade (`test_editar_a_unidade_nao_muda_o_publicado`);
13. a trilha: cada ato no escopo da unidade, com pessoa, permissão, motivo e antes→depois, lido pela
    trilha da `108` sem mudança nela;
14. os modelos iniciais nascem uma vez, com a pessoa como autora;
15. a homologação com o seletor continua, e ele não alcança as unidades.

**A semente e o apelido**: num banco vazio ela semeia e diz `Unidades: N semeadas.`; num banco com
unidade, não lê o arquivo — nem um caminho inexistente a derruba — e diz que não se aplica; duas
sementes simultâneas gravam uma vez; `sincronizar_unidades` faz o mesmo, com o mesmo *stdout* e o
aviso no *stderr*; o `Makefile`, o `entrypoint.sh` e o guia mandam rodar o nome novo.

**A demonstração reproduzível com duas unidades**, sem mudar código:

- automatizada: `PYTEST_ADDOPTS="tests/navegador/test_jornada_de_unidades.py" NAVEGADOR_VISIVEL=1 make test-navegador`
  — o Administrador institucional cadastra o Campus Serra, concede o administrador de acessos dele,
  que concede o Gestor, que cria o primeiro Processo da Serra; `unidades.json` não muda;
- por pessoas: o roteiro G do [quickstart](quickstart.md), no ambiente de homologação funcional.

**O que a implementação encontrou e a spec não previa**: três casos da trilha da `108` e dois da
identificação da `109` usavam a sincronização para alterar unidade; passaram aos casos de uso desta
feature (SC-1047 registra a exceção). E a mensagem da tela de autoridades dizia que as unidades "são
registradas na implantação"; passou a dizer que são cadastradas pelo Administrador institucional.

**Ativação**: o passo 0 da [migração](migracao.md) — quem já tem o papel institucional em cada
ambiente instalado — continua por fazer na VM de homologação, que esta sessão não alcança. Não
bloqueia o merge, e sim a ativação do privilégio ali.

### A revisão de código (31/10/2026)

Feita depois do PR, a pedido do usuário, sobre o diff de `main` até o C: 7 achados, todos corrigidos.

| Achado | Correção |
|---|---|
| o código aceitava quebra de linha no fim (`match` com `$`) | `fullmatch`; o teste da regra cobre `"serra\n"` |
| sigla, nome, local e cabeçalho aceitavam caractere de controle; o canal recusava antes de aparar | todo campo é uma linha só, conferido depois de aparar |
| a previsão da moldura copiava a regra da `109` | a regra saiu de `da_implantacao` para `da_implantacao_entre`, que as duas usam |
| os rótulos da conferência divergiam dos do histórico | a conferência usa `CAMPOS_LEGIVEIS` da trilha |
| a edição lia o histórico inteiro; o cadastro conferia duas vezes | `ler_unidade` para a edição; a confirmação confere só em `registrar` |
| o parâmetro `versao` escondia a função `versao()` | `versao_conferida` |
| o erro de comando da semente malformada ficou sem teste | `test_o_comando_transforma_a_recusa_em_erro_de_comando`, nos dois nomes do comando |

Depois das correções: lint e `make check` limpos; `make test-pg` com 4 workers, **14200 passando,
13 pulados, 0 falhas** (648,8 s).

## Validação funcional (SC-1048, T051) — critério de aceite humano

Não realizada. Depende de B e de C.
