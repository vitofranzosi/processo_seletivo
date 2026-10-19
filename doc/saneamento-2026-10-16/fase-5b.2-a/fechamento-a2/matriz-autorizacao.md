# Matriz de autorização por ação

## Contrato comum obrigatório C

Cada linha herda **C**: identidade `5dadcc37-7015-4a5a-b1a1-727dd7e3d901`, projeto
`cefor_homologacao_f4_20261016`, engine local no endpoint aprovado, recursos próprios com
IDs/labels/recibos e hashes exatos. Não usar só nomes como prova de isolamento.
Banco de aplicação: `ps_homologacao_f4_20261016`; rede: `cefor-f4-rede-20261016`; volumes:
`cefor_f4_pg_20261016` e `cefor_f4_midia_20261016`. Nenhum desses recursos foi criado.

Uma autorização futura deve indicar aprovador, referência da deliberação, revisão/hash,
**uma única ação**, efeitos e recursos exatos, responsável, janela, pré-condições comprovadas,
limites, destinos e custódia. Ler configuração sintética/autorizações, validar hashes e consultar
identidade/metadata dos alvos para isolamento são verificações comuns às ações, não permissões
para consultar dados de domínio fora do escopo. A inspeção inicial pode descobrir o ID da engine;
ações posteriores devem compará-lo com ID aprovado. Nenhuma aprovação foi preenchida nesta fase.

**Erro C:** comunicação/permissão/JSON/metadata incompleta, alvo desconhecido ou alterado,
ausência de evidência, dado real, saída externa ou privilégio excessivo → interromper antes da
próxima mutação; preservar e registrar resultado sanitizado. Não reparar, repetir, adotar ou
ampliar escopo automaticamente. Falha parcial exige inventário e nova decisão, nunca limpeza.

**Evidência C:** autoria e referência da aprovação, UTC, ação, commit/hashes, engine/IDs,
estado inicial e final, exit code/resultado sanitizado e destino; ausência de conclusão não é
sucesso. Não registrar senha, token, env completo, conteúdo sensível ou dump integral.
O operador atual ainda não gera toda essa ficha: os campos adicionais são critério de revisão
antes da operação, não evidência já produzida.

## Operações e recursos

| Ação (todas sob C) | Recursos permitidos / privilégio mínimo | Pré-condições próprias e isolamento | Permitido | Proibido / interrupção específica | Evidência própria / implementação |
|---|---|---|---|---|---|
| `inspecionar` | Engine local explícita; leitura da API, sem privilégio SQL | Cliente exclusivo vazio aprovado; dispensa imagem/banco | Ler ID da engine | Não iniciar daemon, alterar contexto, listar bases ou adquirir imagens; erro encerra | ID observado; caminho preparado |
| `adquirir-imagens` | Só referências/digests e plataforma aprovados; cliente público sem credencial institucional | Origem/quota/plataforma e destino aprovados | Camadas/cache e imagens locais explicitamente adquiridos | Sem fallback de tag, imagem auxiliar, build ou container | Digests/IDs/plataforma, bytes e resultado; executor bloqueado |
| `construir-imagens` | Contexto exportado sanitizado e builder aprovado; nenhuma credencial real | Bases, Dockerfile/lock, wheels/rede e arquitetura aprovados | Build temporário/cache/ID final local | Sem push, sdist/Python/apt implícitos na proposta atual, serviços ou dados reais | Hashes, log sanitizado, ID final; Dockerfile proposto, executor bloqueado |
| `criar-recursos` | Dois containers, rede e dois volumes acima; API Docker restrita por procedimento | Inventário livre bem-sucedido e exclusividade declarada; imagens locais aprovadas | Criar parados; povoamento inicial de volume e recibos | Sem start/initdb/banco/seed; colisão ou mount extra para | Recibo/resultado e prova de estado parado; caminho preparado |
| `bootstrap-postgres` | Apenas PG/volume novo; papel bootstrap, nenhum runtime/migration | Volume vazio e imagem correta, nenhum init script/dump; autorização enumera estruturas administrativas | Initdb, templates/postgres/papel inicial, servidor temporário e primeira partida | Sem banco da aplicação/papéis funcionais; cluster existente não autoriza reinit | UUID/identificador do cluster e volume, PG_VERSION, estruturas/contagens; bloqueada |
| `iniciar-postgres` | PG e volume já inicializados; SO/conta PG | Recibo de bootstrap e identidade do cluster; guarda de recusa se vazio | Partida de cluster existente, recuperação/WAL/logs normais | Sem initdb ou banco extra; falta de cluster interrompe | PID/estado/identidade e horário; bloqueada |
| `criar-banco` | Só banco exclusivo; administração do cluster aprovado | Destino correto e banco ausente por consulta positiva | CREATE DATABASE e recibo próprio | Sem adotar banco existente, criar papéis ou migrar | Nome/OID/dono/versionamento do manifesto; bloqueada |
| `papeis` | Papéis exclusivos; tarefa admin só neste gate | Banco correto, política SQL e credenciais segregadas aprovadas | Papéis e concessões anteriores às migrations | Sem superuser runtime, schema/carga ou credencial admin em app | Atributos/grants sanitizados, resultado; bloqueada |
| `migrar` | Banco exclusivo; papel migration sem senha admin | Plano/migrations/commit aprovados; banco novo correto | DDL e escritas internas enumeradas das migrations | Sem seed, DB externo, migration reescrita ou reparo silencioso | Plano aplicado e resultado por migration; bloqueada |
| `proteger-esquema` | Banco, papéis e schema controle; admin só nesta tarefa | Todas as migrations previstas concluídas | Concessões pós-schema/marcador e conferência das proteções | Sem alterar gatilho para passar ou inserir domínio | N de M, referências e política exata revisada; bloqueada |
| `conferir` | Container de tarefa, banco exclusivo e mídia; runtime em transação read-only | Recibos/hash íntegros, política de gatilhos APROVADA e completa | Criar/iniciar tarefa preservada, SELECT/catálogos e evidências | Sem DDL/INSERT no banco, admin/migration ou reparo; política pendente recusa | Resultado read-only e metadata; preparada, não executada |
| `baseline` | Banco/mídia exclusivos; runtime | Manifesto dos dados/contagens/relógio/IDs aprovado; início vazio e proteção verificada | Só carga sintética e atos privados enumerados | Sem demonstrar cenário, importar DB real, duplicar carga ou apagar dado | Inventário e hashes por objeto/arquivo e integridade; bloqueada |
| `iniciar` | App exclusiva, runtime e porta loopback | Protocolo, autenticação/perfis e baseline aprovados | Serviço web local, logs e sessões previstas | Sem migration/carga; não conceder cenários ou papéis | Estado/URL restrita e versão, sem token; bloqueada também no launcher |
| `demonstrar` | Somente atores/dataset/subcasos nomeados; permissões de domínio existentes | Ficha, mecanismo de sessão e tempo aprovados | Operações de leitura/escrita/atos privados do subcaso | Sem outros subcasos, RA, rede real ou alteração funcional | Esperado/observado, trilha, impactos; bloqueada |
| `evidencias` | Recibos e destino novo aprovado; leitura de metadata | Custódia e conteúdo/minimização definidos | Arquivo novo de metadados no caminho atual | Sem dump/env ou inferir resultado de cenário; destino ocupado recusa | Metadata e hash; ampliação de coleta não implementada |
| `preservar` | Só app por ID; API de parada | Identidade positiva do conjunto | Parar app, manter PG/volumes | Sem remoção ou parada de PG por efeito colateral | Registro da contenção a coletar; caminho preparado |
| `encerrar` | Só IDs de containers do recibo; API de parada | Alvos revalidados, tarefas conhecidas | Parar todos os containers registrados | Sem parar engine ou apagar volumes; falha parcial inventariada | Inventário de parados e custódia; caminho preparado |
| `descartar` | Só alvos parados listados; remoção explícita | Encerramento, retenção/custódia decidida e confirmação de IDs | Futuras remoções por alvo com plano de recuperação parcial | Sem prune, down global, força, exclusão de evidência ou dado real | Manifesto antes/depois e resultado por alvo; executor bloqueado |

As permissões técnicas Docker do usuário host podem exceder esta matriz; o operador não é
uma ACL do daemon nem substitui segregação no SO. Controles técnicos implementados: ação única,
escopo exato de recursos/efeitos declarados, revisão/hashes, autorização antes do cliente,
endpoint/cliente fechado, inventário fail-closed e confronto dos recursos existentes com recibos.
Os códigos simbólicos de escopo não são IDs: o recibo e a conferência posterior continuam necessários.

`isolamento/politica_operacional.py:ESCOPOS` é a representação executável somente das seis ações
preparadas. Ações restantes e os aliases antigos são recusados, inclusive se constarem de uma
lista local de aprovação. O grafo não fornece executor, autorização, prova de dependência ou
transição automática. Políticas de trigger e de ação são distintas; a primeira continua pendente.
