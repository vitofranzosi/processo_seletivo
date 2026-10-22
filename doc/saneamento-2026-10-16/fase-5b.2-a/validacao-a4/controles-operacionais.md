# Controles operacionais — inspeção estática A.4

Referências relativas a `doc/saneamento-2026-10-16/fase-5b.1/`. Classificações descrevem código, não aprovação humana nem teste operacional.

| Controle | Classificação | Evidência objetiva e limite |
|---|---|---|
| 1. Autorização antes de operações externas | Implementado e comprovado estaticamente | operar.py:269–273 verifica integridade e autorizar antes do subprocesso; politica_operacional.py:80–91 exige ação única e escopo exato. Arquivo local não é assinatura humana. |
| 2. Integridade antes de execução | Implementado e comprovado estaticamente | operar.py:62–71 exige conjunto fixo e hashes brutos; :269 precede :273. A guarda está presente e a integridade atual está reprovada; o Python já iniciou quando verifica os arquivos. |
| 3. Cliente Docker isolado | Parcial | operar.py:138–145 exige pasta sem atalhos, apenas config.json vazio e hash; :152–157 recusa variáveis conflitantes e fornece --config. PATH e diretórios de perfil continuam herdados; ambiente externo não observado. |
| 4. Identidade/integridade do binário | Ausente | operar.py:157 chama "docker" por PATH, sem caminho absoluto, hash ou assinatura. Também não atesta intérprete, biblioteca padrão ou runtime anterior ao main. |
| 5. Endpoint explícito | Parcial | operar.py:135–137 exige prefixo npipe:// ou unix:// e :157 passa --host. Prefixo não prova host local, identidade do servidor, atividade ou ausência de ativação por conexão. |
| 6. Escopo docker info | Implementado e comprovado estaticamente | operar.py:273 usa info --format {{.ID}} e :276–278 retorna no ramo inspecionar, antes de criação/parada/tarefas. Não há fallback nesse ramo. |
| 7. Timeout obrigatório | Ausente | subprocess.run em operar.py:157 não possui timeout; campos descritivos do JSON não são lidos como controle temporal. |
| 8. Processos bloqueados | Ausente | Não há política de deadline, kill/wait ou gestão da árvore do cliente; capture_output pode aguardar indefinidamente. |
| 9. Interrupção segura | Parcial | Não há rotina de cancelamento/Job Object/grupo de processos; captura final de Exception (:352–358) não trata KeyboardInterrupt. Ctrl+C não demonstra encerramento de descendentes; nunca parar o daemon como compensação. |
| 10. stdout/stderr controlados | Parcial | :157 captura ambos em memória; :158–159 não anexa stderr bruto em erro; :277 imprime ID/UUID. Não há limite de bytes, validação forte do ID ou sanitização de saída de binário inesperado. |
| 11. Prevenção de exposição de credenciais | Parcial | Config vazio e ambiente reduzido; sem leitura de backend/.env no ramo; falhas finais exibem classe da exceção. PATH/perfis/binário e saída não autenticados deixam risco residual. Não foram acessadas credenciais reais. |
| 12. Evidência e custódia | Ausente | :277 imprime JSON, :278 retorna; não grava recibo, timestamp, exit code, hash do binário ou cadeia de custódia para inspecionar. Procedimento futuro precisa autorização própria para gravar evidência. |
| 13. Ausência de efeitos colaterais não autorizados | Não verificável sem execução | Ramo selecionado não chama criação, parada, SQL ou gravação documental. Comportamento do executável externo, engine e SO não pode ser comprovado estaticamente; a execução permanece proibida. |

Resultado: três controles comprovados estaticamente, cinco parciais, quatro ausentes e um não verificável sem execução. Nenhum resultado significa validação operacional.

## Chamadas indiretas e imports

`operar.py:8–18` importa biblioteca padrão e contrato/política locais; ajusta sys.path. `contrato.py:1–102` define constantes/funções; Django, banco e MigrationExecutor só aparecem dentro de verificar_banco, que não é chamado por inspecionar. `politica_operacional.py` contém dados/funções de validação, sem IO no import. A biblioteca padrão e hooks do intérprete não foram atestados; `-B` impede bytecode Python, não todos os logs/caches do host.

`tarefas.py:8–29` é entrada separada com django.setup e conexão/transação de leitura; não é importado no ramo inspecionar. Sua execução persistente não está autorizada. Outros ramos de operar.py têm capacidades de criação e parada: a limitação depende da ação única efetivamente autorizada, não do nome genérico do operador.

Nenhum script operacional, teste de serviço ou Docker foi executado. A análise de leitura não garante ausência absoluta de escrita indireta pelo SO ou daemon numa consulta futura.

## Controles documentais atuais

`autorizacao.json` e `docker-cliente/config.json` foram preservados e têm hashes no manifesto A.4. O primeiro mantém ações/cenários vazios e campos humanos pendentes; o segundo contém objeto vazio. O campo descritivo `autorizacao_operacional=false` não é consultado pelo operador: a negação efetiva decorre das ações vazias e da guarda de integridade. Não converter campos descritivos em alegação de controle implementado.

## Verificações futuras propostas, não executadas

| Guarda | Positivo planejado | Negativo planejado | Evidência requerida |
|---|---|---|---|
| Autorização | Ação única/escopo/hash/referência completos | Ação extra, referência pendente, revisão errada | Falha antes de subprocesso com stub puramente em memória |
| Integridade | Conjunto e bytes aprovados | Byte ou lista alterados | Recusa sem chamada externa; cópias temporárias só após autorização |
| Cliente | Config vazio exclusivo | Helper, arquivo extra, symlink/junção | Recusa anterior ao cliente |
| Binário/endpoint | Caminho e digest aprovados; endpoint exato | PATH substituído, hash trocado, endpoint remoto | Bloqueio pela futura guarda revisada |
| Tempo/cancelamento | Resposta dentro do prazo | Cliente suspenso ou saída ilimitada | Deadline e encerramento apenas da árvore autorizada |
| Evidência | Registro novo sanitizado e hash | Destino existente, dado sensível ou falta de custodiante | Não sobrescrever; interrupção e recibo sanitizado |

Os três últimos grupos exigem implementação/revisão autorizada de controles hoje ausentes ou parciais. Testar o operador atual com Docker real não é alternativa autorizada.

