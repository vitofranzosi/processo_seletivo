# Isolamento proposto e controles a preparar

Não aplicado. Mantém os identificadores propostos na Fase 4, sem pressupor existência ou disponibilidade.

| Recurso | Destino proposto |
|---|---|
| Projeto Compose independente | `cefor_homologacao_f4_20261016` |
| Aplicação | `cefor-f4-app-20261016`, `http://127.0.0.1:18084` |
| PostgreSQL 18 | `cefor-f4-pg-20261016`, porta interna 5432 sem publicação no host |
| Banco interativo | `ps_homologacao_f4_20261016` |
| Banco da suíte, se aprovado separadamente | `test_ps_homologacao_f4_20261016`, nunca a baseline interativa |
| Rede interna | `cefor-f4-rede-20261016`, sem egress; verificar contenção efetiva antes de dados |
| Volumes exclusivos | `cefor_f4_pg_20261016`, `cefor_f4_midia_20261016` |
| Runtime | `ps_f4_runtime`, sem privilégios de migração/administração |
| Evidências | Pasta nova `doc/saneamento-2026-10-16/fase-5b/evidencias/execucao-01`, somente após autorização |

A pasta de evidências é proposta atual para a futura Fase 5B, substituindo apenas o destino
planejado `fase-4/evidencias-futuras` da F4. Não há evidência existente movida ou apagada.

## Controles existentes versus preparação necessária

| Controle | Já existe no projeto | Necessário preparar/verificar |
|---|---|---|
| Banco e papel separados | Seleção por DB_ROLE e variáveis específicas; PostgreSQL e provisionamento | Cluster/volumes/credenciais novos; checagem de host/DB/user permitidos antes de cada bloco |
| Imutabilidade | Triggers e ausência de privilégio após preparação correta | Verificar esquema/proteções no cluster isolado; não contornar erro com superusuário da aplicação |
| Dados sintéticos | Seed e fixtures | Manifesto revisado, números/IDs sem colisão, marca visível e ausência de importação de dados |
| Arquivos privados | `ARQUIVOS_CANDIDATOS_RAIZ` configurável | Volume exclusivo, sem bind da mídia de desenvolvimento; testar caminhos por dados fictícios |
| Não entrega de e-mail | Backend console e configuração SMTP | Mailpit só local ou console; rede sem saída. Development liga avisos por código, não confiar em env false |
| Sorteio sem rede | Fonte de demonstração no development/test | Confirmar fonte ativa e vedar E2E real; nunca consultar serviço para demonstrar contenção |
| Assistente sem chamada | Chaves/painel configuráveis | `ASSISTENTE_PILOTO=false`, serviço/endereço/credencial/tokenizer vazios, painel desligado, sem montagem de credenciais |
| Identidade local | Seletor development | Habilitar só rede controlada, atores fictícios; não mapear para diretório real |
| Web privada | ALLOWED_HOSTS configurável | Bind exclusivo loopback, rede interna, identificação “HOMOLOGAÇÃO SINTÉTICA” por título/dataset e documentação; sem modificação de UI funcional |
| Dependências | uv.lock, Dockerfile | Imagens por digest, extras aprovados, etapa de aquisição separada; nenhum download em runtime |
| Rastreio | Auditoria/correlação/versões | Ficha de execução e limites de escrita; não logar credenciais/planilha/dados pessoais de participantes |
| Configuração independente | Variáveis explícitas | Arquivo operacional novo fora do `.env` de desenvolvimento; lista permitida sem herança de ambiente pessoal |

## Prevenção de acesso a bases reais

Não resolver host padrão localhost para banco no host; no container usar somente DNS interno
manifestado. Não montar Docker socket, diretórios pessoais, `.env`, backup ou mídia existentes.
Não consultar banco para “ver se é real”. Antes de conectar, conferir configuração sanitizada por
lista fechada: ENGINE, NAME, HOST, PORT e USER; nunca PASSWORD, SECRET_KEY ou lista completa.
Depois de autorizado, consultar apenas o cluster isolado para identidade/versão e esquema.

Compose independente deve sobrescrever/bypassar o entrypoint automático no runtime; não usar
override que inadvertidamente herde volumes/env_file/portas do desenvolvimento. Validar estrutura
sanitizada sem imprimir interpolação de segredos. Não criar arquivo operacional nesta Fase 5A.

Escolha settings: development com env independente e SMTP exclusivamente coletor interno permite
jornada de OTP; test.py pertence à suíte e não substitui ambiente interativo. Nenhuma chave local
é garantia única de isolamento: combinar rede, mounts, configuração e papéis. O servidor local
de demonstração não é implantação de produção nem dispensa parecer institucional.

## Recuperação e destinação

Preservar por padrão. Em falha, parar apenas app isolada após autorização de contenção, manter
volumes/evidências e registrar último estado. Restauração exige recurso **novo**, ferramenta 18 e
backup sintético identificado; não restaurar sobre baseline existente. Descarte demanda aprovação
separada com caminhos/nomes resolvidos, custódia e retenção definidos. Não propor `down -v`, drop,
truncate ou limpeza de branches/worktrees como parte automática do ensaio.
