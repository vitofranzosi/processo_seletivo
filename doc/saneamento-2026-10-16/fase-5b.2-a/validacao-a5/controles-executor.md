# Especificação técnica proposta para o executor

Documento de planejamento A.5, sem alteração de specs funcionais ou implementação. Estado atual fundamentado em A.4/controles-operacionais.md e no código preservado fase-5b.1/operar.py:119–160,269–278.

## Binário e ambiente

Caminho absoluto docker.exe: **PENDENTE**. Origem/distribuidor, versão declarada, arquitetura, identidade de arquivo, assinatura quando disponível e SHA-256: **PENDENTES**. Não resolver confiança pelo PATH, rodar --version, instalar ou obter imagens para descobrir esses valores. A obtenção posterior de metadados deverá ser separadamente autorizada; distinguir versão declarada em metadados da versão observada por execução.

O futuro contrato deverá fixar caminho absoluto canônico, hash aprovado e referência da origem; recusar arquivo ausente, substituído, atalho/junção, caminho remoto/UNC, permissões incompatíveis ou campo pendente. Identidade inclui caminho, tamanho, SHA-256, distribuição/versão e identidade de arquivo do SO quando disponível; assinatura corroboradora não substitui digest aprovado.

O intérprete Python e o launcher também precisam de caminho absoluto e procedência/hash confirmados antes de iniciar código. Guarda dentro do Python não atesta a inicialização que já ocorreu. Propor lançamento com ambiente mínimo, cwd fixo, shell=False e lista de argumentos imutável, sem herança de contexto Docker, env de aplicação ou hooks Python não aprovados. HOME/perfis não devem fornecer credenciais. Descrever explicitamente o conjunto mínimo de variáveis necessário ao Windows e recusá-lo se incompatível, sem imprimir valores secretos.

Cliente exclusivo: apenas config.json vazio, hashes e ausência de atalhos/junções conferidos; sem helpers/contextos/plugins herdados. Alteração entre conferência e lançamento deve causar bloqueio; reduzir risco com acesso restrito e supervisão. Credenciais e perfis reais não serão lidos.

## Timeout e processos

**Proposta para aprovação:** deadline de 30 segundos monotônicos para a consulta, mais até 5 segundos exclusivos de encerramento/reap. Total planejado de 35 segundos; nunca usar esses números como autorização já concedida. Falha de encerramento pode exceder a capacidade de contenção: registrar falha crítica, manter bloqueio, não declarar processo terminado.

Iniciar relógio antes do lançamento; fazer leitura concorrente limitada de stdout/stderr, sem espera ilimitada ou communicate sem prazo. Ao expirar: registrar categoria TIMEOUT, cancelar o cliente autorizado, encerrar a árvore sob controle e aguardar término confirmado por handles, sem reutilizar PID como prova de identidade. Nenhum retry ou novo comando Docker.

Proposta Windows: processo filho criado suspenso, associado a Job Object exclusivo com kill-on-close e sem breakaway antes de retomar. Se associação ou contenção falhar, não retomar. Identificar limitações de jobs aninhados e privilégios; não elevar nem ampliar permissões para contornar. Falha de criação também deve deixar recibo sanitizado. Não adotar implementação sem testes específicos do SO.

O processo pai supervisiona deadline e cancelamento; fechamento inesperado deve fechar o job e encerrar descendentes. Somente processos criados para a consulta podem integrar esse job. Nunca anexar engine, Docker Desktop, VM ou serviço. POSIX não está aprovado: requer proposta própria de grupo de processos e sinais.

## Interrupção segura

Cancelar por pedido humano, Ctrl+C/sinal de console, deadline, saída excedente, falha de guarda ou comportamento inesperado. O handler deve apenas solicitar cancelamento; fluxo principal encerra cliente/descendentes, faz wait com limite e registra motivo/instante/status. Se houver opção de interrupção cooperativa, seu intervalo conta no limite de encerramento e não pode atrasar o corte obrigatório.

Recusar início se não for possível conter descendentes. Não confiar em Ctrl+C sozinho. Não executar taskkill genérico, parada de engine ou limpeza de recursos. Processo órfão suspeito impede nova tentativa; intervenção adicional exige autorização específica e identidade dos processos. Não afirmar ausência de órfãos sem evidência de término.

## Endpoint e escopo

Endpoint absoluto/exato: **PENDENTE**. Exigir igualdade com valor aprovado, transporte local e confirmação do responsável de engine já ativa sem ativação por conexão. No Windows, rejeitar npipe apontando a host remoto; um prefixo npipe:// não prova localidade. Recusar tcp, ssh, URLs remotas, aliases/contextos e variantes não aprovadas. Unix socket demanda proposta específica, não se aplica automaticamente ao host Windows.

Não procurar endpoint testando serviços. Engine desconhecida/inativa, dúvida de localidade ou falta de acesso: bloquear, sem fallback/inicialização. Comando único futuro: cliente fixado, --config exclusivo, --host exato, info --format {{.ID}}. Sem Compose, listagens adicionais, criação ou consultas SQL. O cliente tem privilégios do daemon; o escopo é imposto pelo executor e procedimento, não reduz a autorização nativa do endpoint.

Autorizar por recibo nominal referenciando revisão/hash do contrato, executáveis, endpoint, ação única, janela, executor e supervisor. Sem ações adicionais, retries ou autorização reutilizável. Mecanismo local de tentativa única deverá usar marcador exclusivo no diretório de evidências aprovado; tentativa iniciada consome autorização mesmo em falha. Essa escrita precisa estar expressamente autorizada, não pode alterar o arquivo histórico de autorização.

## Saída e custódia

Proposta de limites: stdout 4 KiB e stderr 64 KiB em memória; exceder implica cancelamento e categoria sanitizada. Validar uma única linha de ID, até 256 caracteres ASCII alfanuméricos ou :._-, não vazia/não placeholder, sem controles. Schema final restrito a campos aprovados; UUID deve coincidir. Limites e contrato precisam aprovação e testes, não equivalem a comportamento atual.

Não persistir stderr bruto, env, config completo ou mensagens potencialmente secretas. Recibo novo: revisão/HEAD, autorização, executáveis/hashes, endpoint sanitizado, executor/supervisor, início/fim e duração monotônica, argumentos aprovados, exit code, ID/UUID, motivo de cancelamento, término/descendentes e status da preservação. Sem sobrescrita; nomes exclusivos e abertura exclusiva. Em falha do destino, não iniciar consulta; falha posterior de gravação impede encerramento formal.

Custodiante: **PENDENTE**; diretório absoluto autorizado: **PENDENTE**; ACL/perfis de acesso: **PENDENTES**; retenção e revisão: **PENDENTES**. Propor acesso apenas a executor, custodiante e revisor designados; minimizar dados dos participantes. Produzir SHA-256 de cada registro fechado e índice separado com referência da aprovação; registrar entregas e revisão. Hash do índice é atestado fora dele. Nenhuma exclusão automática no fim da retenção: destino de evidências depende de decisão explícita.

## Níveis de prova

| Controle | Inspeção estática futura | Testes sem Docker necessários | Validação supervisionada posterior |
|---|---|---|---|
| Binário/autorizações/hashes | Caminho fixo, digests, ordem de guardas, conjunto exato | Stubs: caminho remoto, hash trocado, autorização vencida/reutilizada; zero chamada externa | Procedência/ACL e arquivo real aprovado no host |
| Timeout e cancelamento | Deadline obrigatório, handlers e job; sem retry | Relógio/transportes simulados; falha de criação, cancelamento em cada transição | Processos sintéticos controlados para job/órfãos, sem Docker; autorização própria |
| Endpoint/cliente | Lista exata e recusa de remotos/herança | Variantes npipe remotas, TCP/SSH, helper e campo pendente | Localidade/atividade sem ativação confirmadas; consulta única só em G5 |
| Saída e custódia | Limites, schema e criação exclusiva | Streams simulados, saída excessiva, segredo fictício, colisão/destino sem acesso | ACL/destino, recibo e término no host autorizado |

Testes de processo/arquivo, ainda que sintéticos e sem Docker, criam estado e precisam de autorização específica. Nesta A.5 nenhum teste do executor foi executado.

