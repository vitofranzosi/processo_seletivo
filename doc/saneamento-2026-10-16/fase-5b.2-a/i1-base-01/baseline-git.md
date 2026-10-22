# Baseline Git — diagnóstico

Investigação FASE-5B.2-A-I1-BASE-01; executor Codex; 20/10/2026, America/Sao_Paulo (UTC−03:00).
Repositório: D:\projetos\cefor\processo_seletivo. Branch: 001-decisoes-pendentes. HEAD observado: 4ec10ba52636ef54b56dee35970333f5742548df.

I1 bloqueado; I2–I6 não autorizados; G1–G6 bloqueados individualmente. Nenhuma nova baseline aprovada.

## Estado inicial

Raiz e diretório confirmados. Índice sem diff; nenhum diff rastreado no working tree; 15 arquivos não rastreados. Ambos os objetos existem e são commits. Destino documental inexistente antes da escrita. Nenhum checkout, fetch, reset, stage ou commit executado.

Referência anterior: 550f5bb8983bcdbf32eff210622449a0c959d12d. Referência atual: 4ec10ba52636ef54b56dee35970333f5742548df.
Merge-base: 550f5bb8983bcdbf32eff210622449a0c959d12d. Contagem simétrica antigo...atual: 0 à esquerda e 5 à direita; atual não é ancestral do antigo. Há merges no percurso, portanto o histórico não é uma cadeia simples de cinco commits ordinários.

## Commits incorporados

| Commit | Autor registrado | Data de autoria | Descrição |
|---|---|---|---|
| 4ec10ba52636ef54b56dee35970333f5742548df | Vito Rodrigues Franzosi | 2026-10-20T08:42:32-03:00 | Merge main em 001-decisoes-pendentes |
| df85de01815728905566d8f0e0dc19370689d886 | Vito Rodrigues Franzosi | 2026-10-20T08:41:58-03:00 | Merge main remoto em main local |
| e7e22b8947f40926425b6b54fd626bbe7091ff2f | Saymon Castro | 2026-10-20T08:31:46-03:00 | Merge PR 317; committer GitHub |
| 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 | Saymon Castro | 2026-10-19T21:39:38-03:00 | Extração do universo e trajetória |
| 3e65144fb8e0076a9aef8991191768949c330cfd | Saymon Castro | 2026-10-19T21:32:26-03:00 | Tabela de linha de base; commit em 21:38:37-03:00 |

Metadados consultados com log fuller. São declarações Git locais, sem comprovação de identidade civil ou decisão administrativa.

## Alterações completas entre referências

| Caminho | Tipo | Último commit no intervalo / autor / data | Classe | Impacto | Integridade | Relação I1 |
|---|---|---|---|---|---|---|
| backend/processo_seletivo/classificacao/application/calculo.py | M | 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 / Saymon Castro / 2026-10-19T21:39:38-03:00 | Código-fonte | Médio | SHA-256 físico registrado; funcional não verificada | Indireta |
| backend/processo_seletivo/classificacao/domain/desempate.py | M | 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 / Saymon Castro / 2026-10-19T21:39:38-03:00 | Código-fonte | Médio | SHA-256 físico registrado; funcional não verificada | Indireta |
| backend/processo_seletivo/classificacao/domain/universo_classificavel.py | A | 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 / Saymon Castro / 2026-10-19T21:39:38-03:00 | Código-fonte | Médio | SHA-256 físico registrado; funcional não verificada | Indireta |
| backend/tests/integration/classificacao/test_previa_equivale_ao_oficial.py | A | 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 / Saymon Castro / 2026-10-19T21:39:38-03:00 | Código de teste | Baixo | SHA-256 físico registrado; funcional não verificada | Indireta |
| backend/tests/unit/classificacao/test_ordenar_com_trajetoria.py | A | 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 / Saymon Castro / 2026-10-19T21:39:38-03:00 | Código de teste | Baixo | SHA-256 físico registrado; funcional não verificada | Indireta |
| backend/tests/unit/classificacao/test_universo_classificavel.py | A | 1eb61ea58ef4ce1c1e4f23f1779ee59443cc62f5 / Saymon Castro / 2026-10-19T21:39:38-03:00 | Código de teste | Baixo | SHA-256 físico registrado; funcional não verificada | Indireta |

O teste de integração foi inicialmente criado em 3e65144f e teve mudança posterior em 1eb61ea5; a coluna registra o último commit por caminho. O diff total tem 1110 inserções e 103 exclusões; zero remoções ou renomeações de arquivos. As mudanças de produto extraem a montagem do universo para função própria e acrescentam trajetória ao desempate; o wrapper oficial remove as chaves adicionais. Equivalência funcional declarada pelos commits não foi validada nesta investigação.

Classes documentação, configuração, integridade criptográfica, autorização, evidência histórica e controle operacional: nenhum arquivo alterado no diff. Ausência de diff documental não aprova o conteúdo nem explica sozinha a procedência dos arquivos não rastreados.

Impacto A.4/A.5: referências Git históricas continuam antigas e devem ser preservadas; inventários físicos conferem. Impacto I1: a identidade Git exigida mudou e requer decisão humana explícita. Não houve alteração de HEAD nesta execução.

