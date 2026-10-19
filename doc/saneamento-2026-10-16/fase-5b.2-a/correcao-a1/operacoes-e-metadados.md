# Operações revisadas e proposta de inspeção de metadados

Nenhum comando operacional foi executado. O prefixo dos comandos futuros é
`backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-5b.1/operar.py`.
Autorizações 5B.1 não são aceitas pela revisão `5B.2-A.1`. Lista vazia continua recusando ações.

## Gates vigentes — preparados, não autorizados

| Argumento | Pré-condições | Efeitos e evidência | Interrupção / limite |
|---|---|---|---|
| `validar` | Configuração fictícia independente preenchida e mapa completo | Leitura de arquivos; nenhum Docker. Exemplo com imagens indefinidas deve falhar | Sem prova de imagem ou isolamento; não precisa ser executado para esta revisão |
| `inspecionar` | Autorização específica com hashes/revisão, endpoint local e cliente exclusivo vazio | Apenas `docker info --format {{.ID}}`; saída com ID. Dispensa env do banco e imagens | Daemon inativo/erro/ID vazio: parar, sem iniciar daemon. Não é inspeção de registry |
| `criar-recursos` | Gate próprio, engine aprovada, imagens locais por digest/revisão, configuração aprovada, inventário positivo livre, exclusividade operacional declarada | Somente Compose create dos containers PG/app, rede e volumes; não start. Escreve evento, recibo e resultado | Falha ou identidade incompleta: parar/preservar. Resultado iniciado sem conclusão não é sucesso. Não repetir nem apagar arquivos para desbloquear |
| `conferir` | Gate próprio, banco/esquema/proteções previamente preparados por desenho futuro aprovado, recursos/recibos íntegros | Cria container de tarefa e arquivos de resultado; transação de banco somente leitura, usando runtime; container preservado | Não é inspeção sem escrita de infraestrutura. Sem esquema/política aprovada deve falhar. Falha deixa tarefa para inventário autorizado, sem adoção automática |
| `evidencias` | Aprovação de destino/custódia e recibos íntegros | Arquivo novo de metadados, hora e recibo | Não contém prova de cenários, não inclui dumps/env/stdout; destino ocupado recusa |
| `preservar` | Aprovação específica de contenção e identidade positiva | Para somente app por ID do recibo | Não para PG, não remove recurso; erro interrompe |
| `encerrar` | Aprovação específica de parada e identidade positiva | Para containers registrados por ID; mantém volumes e arquivos | Não desliga engine, não remove recurso; parada parcial exige inventário |

Não existe autorização operacional concedida nesta entrega, nem arquivos `autorizacao.json`,
`homologacao.env` ou `docker-cliente/config.json`. A criação futura desses arquivos exige escopo
explícito. `inspecionar` só aceita cliente com `config.json` igual a `{}`, único arquivo na pasta,
hash aprovado e sem atalhos. O endpoint é passado com `--host`, sem seleção de contexto herdado.
O operador recusa DOCKER_HOST/CONTEXT/TLS_VERIFY/CONFIG e COMPOSE_FILE herdados.

## Separação ainda incompatível — proposta, não implementada

O entrypoint oficial PG inicializa cluster, papéis e banco inicial ao iniciar volume vazio.
Não é possível obter gates independentes apenas renomeando `provisionar`. Portanto o operador
bloqueia `iniciar-postgres`, `criar-banco`, `papeis`, `migrar` e o antigo `esquema`.

Proposta para deliberação técnica antes de nova alteração:

1. **Bootstrap do cluster**: aprovar imagem/volume vazio e operações inevitáveis de initdb
   (templates e banco administrativo), sem banco de aplicação. Credencial admin só nesse contexto.
2. **Partida do servidor já inicializado**: gate separado, sem initdb automático e com identidade
   do volume/cluster verificável. Distinguir restart de bootstrap; não aceitar marker só por nome.
3. **Criação do banco exclusivo**: gate próprio, conexão administrativa local ao cluster aprovado;
   recusar banco preexistente, sem adotar ou sobrescrever. Não executar migrations.
4. **Papéis antes das migrations**: tarefa admin separada; registrar permissões mínimas, autoria
   e destino. Credencial de migration exclusiva dessa etapa, fora do env comum.
5. **Migrations**: tarefa com papel migration apenas; plano aprovado e banco exclusivo; nenhuma
   senha admin. Não misturar com baseline, concessão pós-schema ou criação de banco.
6. **Concessões e marcador**: tarefa admin separada pós-migration, proteção e marcador conferidos;
   sem carregar domínio. Congelar política de gatilhos revisada a partir das migrations.
7. **Carga sintética**: runtime, limite e manifesto próprios; relógio e tratamento de falha aprovados.

Isso exige rever bootstrap/serviços/arquivos de autorização; **não foi implementado**, conforme
restrição humana para alterações incompatíveis. As operações acima precisam de aprovações próprias;
aprovar o desenho não autoriza executá-las. `baseline` e `descartar` também estão bloqueados.

## Sessões web

Barreiras técnicas atuais: rede interna declarada, bind loopback, seleção/settings exclusivos,
credenciais runtime e bloqueio de partida pelo operador e pelo launcher montado. Não há sessão
web executada. Permissões/escopos existentes do sistema permanecem inalterados.

Barreiras procedimentais propostas: operador único, roteiro por subcaso, observador, registro de
atores/horários e interrupção diante de desvio. Elas não impedem tecnicamente URLs ou atos fora
do roteiro. Se a web for reabilitada sem mecanismos adicionais, o seletor de identidade e as
operações permitidas ao ator continuarão acessíveis; a receita não constitui ACL.

Alternativas para decisão posterior: contas sintéticas de menor privilégio provisionadas
explicitamente; desabilitar seletor após definir autenticação de laboratório; proxy de laboratório
com política de rotas/métodos revisada; instância por cenário. Nenhuma foi aplicada, nenhuma altera
permissões nesta fase. Proxy não substitui autorização de domínio e GET também pode produzir trilha.

## Imagens e builds — proposta de fechamento

Continuam pendentes os digests reais de PostgreSQL 18, Python 3.13 Bookworm e uv, a plataforma,
patches e a identidade da engine. Não foram inventados identificadores. Dockerfile de desenvolvimento
permanece intacto. Proposta para Dockerfile específico futuro: FROM/COPY por digest OCI aprovado;
snapshot Debian e versões de pacotes; dependências Python/uv fixadas pelo lock e hashes; sem
download implícito de tokenizer/modelo ou credenciais. Revisar endpoints de build e fechamento
offline antes de afirmar reprodução. Tags servem à descoberta, nunca à execução aprovada.

Registrar índice e manifesto por plataforma, origem, data, digest/config digest, hash do contexto
exportado, revisão Git, lock, Dockerfile, parâmetros, builder, rede permitida, log sanitizado e ID
final. Label de revisão sozinha não comprova procedência. Mudança de qualquer base exige nova
revisão, novos hashes e aprovação; cache não é evidência de integridade/reprodutibilidade.

## Proposta de autorização restrita a metadados

**Texto sugerido para futura deliberação:** autorizar apenas o responsável técnico a consultar
metadados da engine local já ativa e das imagens públicas indicadas abaixo, sem iniciar daemon,
baixar camadas, executar build ou criar recursos. Autorizar somente a configuração cliente vazia
em diretório novo confirmado e evidências sanitizadas no destino confirmado. Identidades dos
responsáveis, endpoint, diretórios e data da consulta ainda devem ser informados pelo aprovador.

Escopos independentes:

- **M1 local**: ID/versão/plataforma da engine e metadados de imagens já presentes. Exigir endpoint
  `unix://` ou `npipe://`, configuração exclusiva `{}` e ambiente sem variáveis conflitantes.
  Nenhuma inicialização automática para conseguir resposta.
- **M2 remoto**: somente manifestos/headers públicos nos namespaces `docker.io/library/postgres`,
  `docker.io/library/python` e `ghcr.io/astral-sh/uv`, incluindo autenticação anônima e endpoints
  oficiais necessários. Não usar login institucional, chave, camada, pacote ou serviço pago.
  Preferir cliente separado de descoberta; qualquer cache local de metadados deve ser explicitado
  no destino aprovado e não reutilizado como cliente runtime vazio.

Comandos-modelo futuros, com parâmetros obrigatórios aprovados; não executados:

```powershell
docker --config <CLIENTE_EXCLUSIVO> --host <ENDPOINT_LOCAL> info --format '{{json .ID}}'
docker --config <CLIENTE_EXCLUSIVO> --host <ENDPOINT_LOCAL> version --format '{{json .Server}}'
docker --config <CLIENTE_EXCLUSIVO> --host <ENDPOINT_LOCAL> image ls --digests --format '{{json .}}'
docker --config <CLIENTE_EXCLUSIVO> --host <ENDPOINT_LOCAL> image inspect --format '{{json .RepoDigests}}' <REFERENCIA_LOCAL_APROVADA>
docker --config <CLIENTE_DESCOBERTA> manifest inspect --verbose docker.io/library/postgres:18
docker --config <CLIENTE_DESCOBERTA> manifest inspect --verbose docker.io/library/python:3.13-slim-bookworm
docker --config <CLIENTE_DESCOBERTA> manifest inspect --verbose ghcr.io/astral-sh/uv:0.9
```

Os `<...>` são decisões obrigatórias, não comandos prontos para copiar. Validar a ferramenta
disponível antes de autorizar a sequência, sem fallback para pull/build. Redirecionamentos de
registry fora da lista, erro de permissão/comunicação, daemon inativo, pedido de credencial real,
digest/plataforma inconclusivo ou saída contendo segredo são critérios de interrupção.

Aceite: tabela com fontes, versões, digests reais e plataformas, distinção de índice/manifesto,
data e aprovador, sem segredo; discrepâncias permanecem pendentes. M1/M2 não autorizam aquisição,
build, Compose ou nenhuma operação do laboratório. Falha não autoriza limpar caches ou recursos.

## Bloqueios para 5B.2-B

Antes de aquisição/build: aprovar M1/M2, plataforma, digests/procedência, dependências/snapshot,
contexto sanitizado, Dockerfile específico, builder, quota e custódia. Não é necessário resolver
todo bootstrap para descobrir metadados; tampouco descobrir metadados autoriza bootstrap.

Antes de provisionamento/demonstrações: desenho segregado acima, exclusividade/concorrência,
política de proteções preenchida e revisada, protocolo web, baseline/cobertura/relógio,
recuperação de falhas parciais e coleta de evidência. Descarte permanece gate futuro separado.
