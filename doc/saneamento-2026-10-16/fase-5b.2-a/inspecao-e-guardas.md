# Inspeção do Compose e das guardas

Inspeção estática de 16/10/2026; nenhum caso de teste abaixo foi executado.
Referências de linha pertencem aos artefatos preservados da Fase 5B.1.

## Compose — dez verificações

| Controle solicitado | Evidência estática | Limite / conclusão |
|---|---|---|
| Sem `backend/.env` | [Compose](../fase-5b.1/compose.homologacao.yaml): sem `env_file`; operador usa `--env-file` próprio; settings não usam dotenv | Confirmado na fonte. Conteúdo de imagem/mounts reais ainda não inspecionado |
| Volumes não compartilhados | Dois volumes nomeados/rotulados, sem external/driver_opts; bind único `./isolamento`, read-only | Intenção correta; reuso de nomes, mounts reais e identidade dependem do daemon |
| Banco não externo | DB_HOST fixo `banco-homologacao`, rede interna e sem porta PG no host | Nome DNS não comprova por si identidade do servidor; marcador/engine complementam |
| Sem migration/provisão automática da web | Entrypoint web próprio (58); sem depends_on; schema só tarefa explícita | A imagem PG inicializa cluster/DB ao ser iniciada; `provisionar` inclui esse efeito e não é apenas create |
| Identificação exclusiva | Projeto, serviços, containers, rede/volumes e UUID em labels | UUID constante não é segredo/prova de posse; rótulos podem ser copiados por admin |
| Portas mínimas | Apenas app em `127.0.0.1:18084:8000`; tarefa/PG sem porta | Disponibilidade/bind efetivo não comprovados; nenhuma porta consultada agora |
| Sem serviços reais dependentes | Sem fonte externa, assistente desligado e sem serviço remoto no Compose | Rede internal é configuração, não ensaio de egress; imagem confiável e ausência de rede extra ainda por comprovar |
| Correio simulado | Backend console, HOST/USER/PASSWORD SMTP vazios, settings reafirmam console | Sem transporte SMTP declarado; OTP sintético aparece em stdout, exige custódia e minimização |
| Arquivos isolados | Volume dedicado de mídia; root filesystem da app/tarefa read-only; tmpfs privado | UID/permissões/caminhos Windows precisam de teste futuro; não é mídia do desenvolvimento |
| Sem destruição automática | Sem down/prune/rm automático; descarte explícito com confirmação; tarefa sem `--rm` | Script ainda pode ficar em estado parcial no descarte; não declarar recuperação resolvida |

Herança: Compose recebe arquivo explícito e subprocesso com lista permitida; rejeita HOM_* do
shell e alguns DOCKER_*/COMPOSE_FILE. Porém ainda lê contexto/configuração do cliente Docker via
perfil do usuário, e a imagem pode conter ENV/metadata próprios. Settings fixam campos críticos,
mas herança não foi inventariada integralmente em uma imagem real. Não usar Docker config que
contenha autenticação institucional em aquisição futura. Profiles não impedem acionamento direto
de serviço nomeado por um operador com acesso ao daemon; não são ACL.

## Achados que mudam a avaliação pré-operacional

| ID / prioridade | Evidência precisa | Consequência / encaminhamento proposto |
|---|---|---|
| A01 — alta | [operar.py](../fase-5b.1/operar.py), `main`, linhas 203–227: create de dois containers/rede/volumes e start de PG na mesma ação | Autorizar provisionar também permite initdb/banco. Separar gates ou nomear todos os efeitos; não classificar como só criação sem serviço |
| A02 — alta | `operar.py:238–254`: conferir/esquema/baseline usam compose run e gravam recibo de tarefa no finally | Conferir não é inspeção sem escrita: cria container e arquivo. Seus efeitos precisam de autorização explícita; recibo não contém resultado de sucesso da tarefa |
| A03 — alta | `operar.py:257–266`: demonstrar só checa lista/imprime roteiro; iniciar serve toda app | A lista de subcasos não restringe endpoints ou ações de navegador. Iniciar habilita superfície ampla com seletor de identidade. Exigir controle de sessão/procedimento/operador e não prometer enforcement técnico por cenário |
| A04 — alta | Compose:86–87 passa admin/migration a toda tarefa, inclusive conferir e baseline | Excesso de credenciais no container de leitura/runtime. Separar tarefas/ambientes antes de execução com privilégio mínimo; não confundir settings runtime com ausência de credencial admin |
| A05 — alta | `operar.py:99–110`, `ausente=True`: qualquer erro de inspect retorna None | Indisponibilidade/erro de permissão pode ser interpretado como nome livre. Post-check é depois de create. Exigir distinção comprovada de “não encontrado” e erro, abortando antes da mutação |
| A06 — média | `operar.py:184–187`: consulta contexto Docker antes de validar autorização; validar exige env e digests antes de inspecionar | Uma ação recusada ainda invoca o cliente Docker e lê metadados locais de contexto; essa consulta não prova contato com daemon. A inspeção da engine fica dependente de config de imagem ainda não escolhida. Separar preflight autorizado das etapas de estado |
| A07 — alta para build | [Dockerfile](../../../Dockerfile):11/15/20/41/44 usa Python/uv por tags, apt e uv sync | App final por digest/label não torna build reproduzível. Falta congelar bases/plataforma/dependências de sistema/procedência; não inventar digests |
| A08 — média/alta | `contrato.py:verificar_banco`: ausência de UPDATE/DELETE e contagem de qualquer trigger não interna habilitada | Guarda não comprova nome/definição/semântica do gatilho append-only. Complementar confronto com política/migrations e teste apropriado, sem alterar proteção para fazer passar |
| A09 — alta para carga | `tarefas.py:68–82`, baseline.json: reserva, relógio fixo, seed; limites só descritos | Sem prova de teto/cobertura nem medição determinística completa. Falha pode deixar atos parciais; não repetir. Revisar orçamento e protocolos antes de carga |
| A10 — média/alta | `operar.py:123–170`, descarte:278 em diante | Revalidação é pontual, não lock de daemon. Volumes usam nome/CreatedAt/labels, sem ID imutável próprio. Falha parcial remove alvos já processados e pode impedir repetição pelo verificador que exige todos presentes |
| A11 — média | `validar:54–60`: itera apenas entradas do integridade.json; hashes aprovados são âncora externa | Não exige conjunto exato/completo de artefatos, nem imobiliza binds durante sessão. Definir conjunto obrigatório e confiança do host; autorização JSON editável não é assinatura |
| A12 — média | `compose()/docker()` capturam stdout; recibos de tarefa registram propriedade, não status/horário/resultado; evidencias salva metadados/hashes | Diagnóstico e prova da execução são insuficientes para homologação. Planejar relatório sanitizado de resultado sem log integral/segredos; não deduzir êxito de recibo existente |

As consequências de controle de fluxo são constatáveis na fonte; falhas específicas de metadata
Docker/Rancher, caminhos e rede são **hipóteses operacionais**, não incidentes observados. Não há
evidência de vazamento, conexão real ou destruição ocorrida nesta fase.

## Casos positivos e negativos propostos por guarda

| Guarda | Positivo esperado | Negativo esperado | Tipo / evidência futura |
|---|---|---|---|
| Seleção/configuração | ID/seleção/settings e cinco chaves de env corretos | Backend/.env, chave ausente/extra/duplicada, HOM_* herdada, symlink/junção | Unitário com arquivos fictícios + leitura de args/env; sem importar settings reais |
| Autorização por ação | Hashes/engine/ação/subcaso explicitamente aprovados | Ação não listada, lista tipo errado, config mudada, autorização pendente | Teste com subprocesso simulado; garantir **zero chamada** antes de aprovação, cobrindo A06 |
| Banco autorizado | Nome/user/versão/marker exatos e schema pronto | Host/DB/user/marker errado; marker extra; migration pendente | Mocks primeiro; banco sintético só depois de autorização, sem tocar real |
| Proteções normativas | Política de privilégios e gatilhos correspondentes à fonte | UPDATE/DELETE concedidos, trigger desabilitada ou trigger alheia ocupando o lugar | Fixtures isoladas autorizadas; refutar falso positivo A08 sem mexer em base real |
| Rede | Só rede interna e endpoints do recibo | Rede extra, endpoint desconhecido, porta pública, engine diferente | Mock de inspect primeiro; runtime autorizado depois; nenhum contato com provedor real |
| Volumes/mounts | Volumes novos local/options vazias e bind readonly previsto | Volume ocupado, driver remoto, options de bind host, socket, origem substituída | Asserções de estrutura + metadata simulada; verificar erro de inspect não vira ausência |
| Migration automática | Início web chama só guardas e runserver | Plano pendente deve recusar sem chamar migrate/provisão | Inspeção/call graph e subprocesso simulado; integração não executada agora |
| E-mail/integração | Console, fonte demonstrativa, assistente sem serviço | SMTP, endereço/credencial do assistente ou fonte real | Config sintética/mocks; não testar bloqueio enviando e-mail ou chamando API real |
| Tarefa por privilégio | Conferir/baseline recebem só runtime | Admin/migration em tarefa de leitura deve ser recusado na variante corrigida | Teste de configuração/mounts; versão atual tem A04, não marcar esse caso aprovado |
| Descarte | Parados, engine/IDs/labels corretos, confirmação exata | Recurso ativo/alheio/substituído, label/volume divergente, recusa na metade | Mock com **zero remoção** para pré-condição inválida; ensaio destrutivo exige autorização própria |
| Integridade/imutabilidade dos artefatos | Todos os arquivos obrigatórios/hashes presentes | Entrada removida do mapa, arquivo/bind alterado após preflight | Verificação independente e planejamento de snapshot; não chamar checksum de assinatura |
| Receitas/contagem | Entradas aprovadas, relógio declarado, limites conhecidos | Reexecução, baseline parcial, teto excedido, janelas vencidas | Plano de testes puros e depois escrita isolada autorizada; sem gerador agora |

Os casos são propostas de revisão e teste, não resultado positivo. Nesta fase somente parsing,
leitura e comparação de hashes foram realizados. Alterações corretivas dos artefatos requerem
autorização posterior específica; código inspecionado permanece preservado.
