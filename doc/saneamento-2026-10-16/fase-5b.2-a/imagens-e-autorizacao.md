# Imagens, engine e proposta de autorização granular

Inspeção estática em 16/10/2026. **Proposta, não autorização.** Não foram executados comandos
Docker, consultas de registry, pull ou build. Não foi iniciado daemon.

## Inventário e procedência

| Componente | Versão/referência na fonte | Procedência declarada | Digest verificado | Necessidade |
|---|---|---|---|---|
| PostgreSQL | Major 18 requerido pelo contrato; Compose exige `HOM_POSTGRES_IMAGE` | Proposta: Docker Official Image `docker.io/library/postgres` | Nenhum disponível nesta inspeção | Aquisição por digest; patch/plataforma ainda por aprovar |
| Base Python | `python:3.13-slim-bookworm` no Dockerfile | Docker Official Image `docker.io/library/python` | Não fixado no Dockerfile | Base do build; tag não fixa patch/conteúdo |
| uv | `ghcr.io/astral-sh/uv:0.9` no COPY | Imagem declarada da Astral, GHCR | Não fixado | Ferramenta copiada no build; versão exata ainda por selecionar |
| Aplicação | Build local do commit `6fc3a85a9ce58a973dc0e29bc38085dfd055f171` | Fontes Git locais, Dockerfile e lock versionados | Não existe ID de imagem comprovado | Build local separado; label de revisão exigida |

Hashes em `integridade.json` são de **arquivos**, não digests OCI. Nenhum placeholder é imagem
aprovada. A imagem final precisa de Python/dependências em `/app/backend`, usuário 10001 e da
label de revisão. O entrypoint original da imagem faz preparação automática: somente o manifesto
isolado o substitui. Rodar a imagem diretamente é proibido no escopo proposto.

O Dockerfile da raiz é de desenvolvimento, usa apt sem snapshot e `uv sync --locked` com rede.
O lock restringe dependências Python, mas não fixa bases, pacotes Debian nem a ferramenta uv.
Build com ele não permite afirmar reprodução byte a byte. Não há Dockerfile alternativo aprovado;
esta fase não o cria nem o modifica.

## Engine e dependências

A Fase 5A registrou CLI Docker 29.6.2-rd, Compose 5.3.1 e Rancher Desktop. São dados históricos
do cliente, não identificação atual da engine. ID, versão do servidor, contexto, endpoint,
arquitetura, espaço e imagens locais permanecem **não verificados**. A plataforma proposta é
Linux; `linux/amd64` é candidata e depende da engine/manifestos aprovados. Não presumir que
o daemon esteja ativo nem iniciá-lo para descobrir.

Pull exige rede a registries públicos e seus endpoints de distribuição/autenticação anônima.
Build também pode exigir Debian e índice/distribuição de pacotes Python declarados no lock.
Validar URLs/índices antes de permitir rede; não reutilizar autenticação institucional, SSH,
build secrets, proxy credenciado ou caches de outro ambiente. O driver BuildKit também precisa
ser inventariado: não criar builder nem adquirir imagem auxiliar implicitamente. Build gera
cache e executa etapas temporárias, mesmo sem iniciar o sistema de homologação.

## Comandos futuros de aquisição

Não é possível dar um comando completamente instanciado sem inventar digest, endpoint e
plataforma. O modelo exato abaixo exige referências completas aprovadas como entrada;
**não executar agora**, nem considerar o preenchimento como aprovação. Registrar previamente
aprovador, engine, quota de disco, destino da evidência e referência da autorização.

```powershell
# Somente após aprovação específica de metadados e aquisição.
# Diretório novo, vazio e exclusivo, sem credenciais; criação também deve ser autorizada.
$configDockerHom = Read-Host 'Diretório Docker exclusivo previamente aprovado'
$endpointHom = Read-Host 'Endpoint local aprovado da engine já ativa'
$plataformaHom = Read-Host 'Plataforma aprovada, por exemplo linux/amd64'
$postgresHom = Read-Host 'docker.io/library/postgres@sha256:<digest aprovado>'
$pythonHom = Read-Host 'docker.io/library/python@sha256:<digest aprovado>'
$uvHom = Read-Host 'ghcr.io/astral-sh/uv@sha256:<digest aprovado>'
if ($endpointHom -notmatch '^(npipe:|unix:)') { throw 'Endpoint não local' }
if ($plataformaHom -notin @('linux/amd64','linux/arm64')) { throw 'Plataforma não prevista' }
if ($postgresHom -notmatch '^docker.io/library/postgres@sha256:[a-f0-9]{64}$') { throw 'Referência PG inválida' }
if ($pythonHom -notmatch '^docker.io/library/python@sha256:[a-f0-9]{64}$') { throw 'Referência Python inválida' }
if ($uvHom -notmatch '^ghcr.io/astral-sh/uv@sha256:[a-f0-9]{64}$') { throw 'Referência uv inválida' }
docker --config $configDockerHom --host $endpointHom image pull --platform $plataformaHom $postgresHom
if ($LASTEXITCODE -ne 0) { throw 'Interromper: pull PG falhou' }
docker --config $configDockerHom --host $endpointHom image pull --platform $plataformaHom $pythonHom
if ($LASTEXITCODE -ne 0) { throw 'Interromper: pull Python falhou' }
docker --config $configDockerHom --host $endpointHom image pull --platform $plataformaHom $uvHom
if ($LASTEXITCODE -ne 0) { throw 'Interromper: pull uv falhou' }
docker --config $configDockerHom --host $endpointHom image inspect $postgresHom $pythonHom $uvHom
```

O modelo não é uma guarda completa: o responsável deve validar diretório vazio sem atalhos,
ausência de credenciais/helpers, endpoint e ID da engine e ambiente herdado antes de execução.
Inspeções devem coletar apenas ID, RepoDigests, arquitetura e labels pertinentes, sem publicar
configurações integrais com possíveis segredos. Digest de índice multiplataforma e digest do
manifesto selecionado devem ser distinguidos e registrados.

## Comandos futuros de contexto/build — bloqueados até revisão

Preparar em etapa autorizada diretório novo fora da working tree; revisar a lista de conteúdo
antes de extrair/buildar. Exportação não inclui arquivos não rastreados, mas **não garante** que
o histórico rastreado esteja livre de dados ou segredos: inspecionar o conteúdo aprovado.

```powershell
git archive --format=tar --output=<ARQUIVO_TAR_NOVO_APROVADO> 6fc3a85a9ce58a973dc0e29bc38085dfd055f171 Dockerfile .dockerignore backend scripts/docker/entrypoint.sh
```

Os parâmetros entre `<...>` são lugares obrigatórios de decisão, não argumentos executáveis.
Após autorizar extração, revisar um Dockerfile específico com FROM/COPY por digests aprovados,
fixação da origem apt e política de rede/cache. Qualquer alteração desse artefato exige revisão
e hash próprios. O comando de build proposto, somente após essa revisão, é:

```powershell
docker --config <CONFIG_EXCLUSIVA> --host <ENDPOINT_LOCAL_APROVADO> build --platform <PLATAFORMA_APROVADA> --pull=false --label org.opencontainers.image.revision=6fc3a85a9ce58a973dc0e29bc38085dfd055f171 --iidfile <IIDFILE_NOVO> --tag cefor-homologacao-f4:6fc3a85a-5b2b --file <DOCKERFILE_REVISADO> <CONTEXTO_EXPORTADO_REVISADO>
```

`--pull=false` não impede downloads de bases ausentes nem apt/uv; não é prova de build offline.
Não executar esse comando com o Dockerfile atual como se as bases estivessem fixadas. Se rede
totalmente desabilitada for exigida, primeiro preparar e aprovar fechamento de dependências:
o build atual com apt/uv não está demonstrado como viável offline. Saída local apenas, sem push.

## Proposta 5B.2-B por autorizações separadas

| Parcela | Escopo proposto e recursos afetados | Dependências / aceite | Interrupção |
|---|---|---|---|
| B0 — metadados | Consultar engine já ativa e referências públicas; documentar digests/plataforma/procedência; arquivos de evidência novos | Nomear responsável, endpoint, destino, rede e custódia; comparar ID com aprovação | Daemon inativo, endpoint remoto, credencial institucional, indisponibilidade ou origem não aprovada |
| B1 — aquisição | Pull somente das três referências aprovadas; grava imagem/camadas e cache local | B0 concluída, digests aprovados, quota e configuração exclusiva; IDs/RepoDigests/plataforma conferidos | Digest/plataforma divergente, imagem auxiliar inesperada, disco insuficiente ou rede fora do escopo |
| B2 — contexto | Exportação Git, extração em destino novo e inspeção; proposta separada de Dockerfile imutável | Conteúdo sanitizado e hashes revisados; nenhuma working tree enviada ao daemon | Dado real, segredo, alteração não autorizada ou destino ocupado |
| B3 — build | Executar build local revisado, temporários/cache e iidfile | Bases/dependências/rede/builder aprovados; label, ID, logs sanitizados e contexto registrados | Busca de segredo, fonte inesperada, falha, alteração de contexto ou gasto fora da quota |

Pode-se autorizar apenas B0 e decidir B1 depois. B2/B3 não estão prontos para autorização executável
sem revisão do artefato de build. Nenhuma parcela autoriza remover imagens/cache existentes.
Falha preserva evidências; não autoriza limpeza, fallback para tags ou execução privilegiada.

## Proibições que permanecem

Não iniciar daemon, sistema web, containers da aplicação/PG ou serviços; não criar redes, volumes,
bancos ou esquemas; não executar Compose, migrations, carga, receitas ou testes persistentes.
Etapas temporárias de build são permitidas somente se B3 vier a ser expressamente autorizada.
Não enviar e-mails, acessar bases reais, usar serviços pagos, publicar atos, conceder permissões,
alterar fonte funcional/specs/Constituição ou fazer commit/push/merge. Aquisição/build não aprovam
o ambiente e não encerram pendências. Provisionamento terá proposta e deliberação próprias.
