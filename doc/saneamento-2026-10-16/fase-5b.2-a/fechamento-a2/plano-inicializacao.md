# Plano de inicialização segregada

Data: 16/10/2026. Artefatos preparados/revisados; **nenhuma etapa operacional autorizada**.
Identidade: `5dadcc37-7015-4a5a-b1a1-727dd7e3d901`, projeto `cefor_homologacao_f4_20261016`.
O grafo puro `isolamento/politica_operacional.py:DEPENDENCIAS` representa planejamento,
não comprovação das pré-condições nem implementação de todas as ações.

## Sequência, estados e efeitos

| Etapa / ação | Pré-condição positiva | Efeitos que exigirão autorização própria | Não inclui | Situação técnica |
|---|---|---|---|---|
| 1a `adquirir-imagens` | Digests/plataforma/procedência e disco aprovados; cliente sem credencial institucional | Contato registry, download de camadas, imagens/cache locais e evidência | Build, criação/start de containers, banco | Sem executor; bloqueada no operador |
| 1b `construir-imagens` | Contexto Git sanitizado, Dockerfile/lock/builder/rede aprovados, bases disponíveis | Etapas temporárias de build, pacotes/cache, imagem local e registro do resultado | Push, app, esquema ou aquisição implícita de imagem extra | Dockerfile específico proposto, não construído; bloqueada |
| 2 `criar-recursos` | Engine/imagens aprovadas, nomes livres por inventário válido, exclusividade, hashes e aprovação de uma ação | Cria rede interna, volumes e containers parados; povoamento inicial de volume pela imagem pode escrever arquivos; evento/recibo/resultado | Start/initdb, banco da aplicação, papéis, migrations ou carga | Caminho preparado, não executado; não aceita autorização antiga |
| 3a `bootstrap-postgres` | Volume novo e vazio, imagem PG aprovada, nenhum dump/script de init, autorização que nomeie todos os efeitos | `initdb`, catálogos, `template0`, `template1`, banco administrativo `postgres`, papel bootstrap, configurações e logs; servidor temporário do entrypoint oficial e primeira partida | Banco `ps_homologacao_f4_20261016`, papéis runtime/migration, migrations, domínio | Plano definido, executor bloqueado; exige guarda prévia do volume e identidade do cluster |
| 3b `iniciar-postgres` | Cluster previamente inicializado, identidade e PG_VERSION esperados, recibo de bootstrap concluído | Partida/repartida, logs, WAL/checkpoint e recuperação normal de PG | Initdb se faltar cluster, criação de banco/papéis ou reparo | Ainda bloqueada; futura entrada deve recusar cluster ausente, não inicializá-lo |
| 4a `criar-banco` | Cluster correto ativo e banco exclusivo ausente | Criação explícita do banco vazio e registro de propriedade | Papéis, tabelas de domínio, migrations | Planejada e bloqueada; não conectar em servidor externo |
| 4b `papeis` | Banco exclusivo correto e política de papéis aprovada | Cria papéis migration/runtime restritos ao laboratório e privilégios prévios | Migration, carga, concessões pós-schema não enumeradas | Planejada e bloqueada; credenciais de tarefa próprias |
| 5a `migrar` | Plano/hash das migrations, banco e papel migration comprovados | DDL e operações inerentes às migrations versionadas no banco novo | Reescrever migration, seed ou alteração de base existente | Planejada e bloqueada; migrations podem criar registros estruturais, não declarar zero escrita de dados |
| 5b `proteger-esquema` | Migrations concluídas e tabela a tabela revisadas | Concessões pós-schema, schema de controle, marcador e política de proteções | Dados de candidato, baseline ou alteração de gatilho para fazer teste passar | Planejada e bloqueada; manter ordem provisionar → migrar → provisionar sem fundir autorizações |
| 5c `conferir` | Esquema/proteções/recibos completos; política aprovada | Cria/inicia container de tarefa preservado, lê banco em transação read-only e grava evidência local | Corrigir schema, executar migration ou seed | Implementada como artefato, não exercitada; política de gatilhos ainda pendente |
| 6 `baseline` | Manifesto/datas/contagens/atores/cobertura e tratamento de falha aprovados | Apenas carga sintética enumerada, documentos e atos privados marcados | Demonstrações e preenchimento dos respectivos resultados | Bloqueada; critérios em documento próprio |
| 7 `iniciar` | Baseline/conferência e protocolo/controle de sessão aprovados | Partida web, conexões e logs; acessos posteriores podem gerar sessões/trilha | Migration, carga, autorização automática de cenários | Bloqueada no operador e no launcher |
| 8 `demonstrar` | Subcaso/ator/dataset/janela explicitamente autorizados, sessão aprovada | GET/POST, atos e auditoria previstos em cada subcaso; geração/download apenas quando enumerados | Outros cenários, RA, serviços pagos ou atos oficiais reais | Bloqueada; receitas continuam manuais |
| 9 `evidencias` | Destino, custódia e conjunto aprovados | Cria arquivos novos sanitizados; metadados, hashes, capturas/XLSX permitidos | Dumps integrais, segredos, alteração dos resultados | Operador atual coleta apenas metadados; outras coletas exigem aprovação própria |
| 10 `descartar` | Custódia/retencão decididas, todos os alvos parados e identidade comprovada | Remoção explícita apenas de alvos enumerados e confirmação de IDs | Parar recursos por efeito oculto, prune/down global, limpeza de outros ambientes | Bloqueada; executor de recuperação parcial ainda pendente |

`preservar` para só app; `encerrar` para IDs registrados; ambos são gates independentes sem
remoção. Coletar evidências em cada etapa é um efeito expressamente enumerado da ação; a
coleta final ampliada é gate próprio. Uma dependência não concede autorização da etapa seguinte.

## Ajuste aplicado ao Compose

O serviço PG passou de `POSTGRES_DB=ps_homologacao_f4_20261016` para `POSTGRES_DB=postgres`.
Assim o entrypoint oficial não recebe ordem de criar o banco da aplicação no bootstrap.
O destino Django permanece o banco exclusivo; antes de sua criação deverá falhar, sem fallback.
A imagem ainda escreve estruturas administrativas e cria o papel bootstrap especificado por
`POSTGRES_USER`. Esse papel faz parte dos efeitos de initdb, não equivale à criação dos papéis
da aplicação. Não chamar bootstrap de operação somente leitura.

O operador ainda não possui caminho de start PG. Preparar executores distintos para bootstrap,
start de cluster existente, banco, papéis e migrations requer revisão posterior. Não liberar
um simples `docker start` como substituto: sem a guarda ele pode disparar initdb em volume vazio.

## Privilégios e recuperação

Bootstrap/admin somente no contexto inicial; banco/papéis e concessões em tarefas administrativas
separadas; migration só no seu gate; runtime para carga/aplicação; conferência runtime dentro de
transação read-only. Esta última é barreira técnica de transação, não um papel de auditoria
independente já criado. Papel de auditoria exclusivo permanece proposta a revisar.

Falha em qualquer gate: interromper, marcar estado iniciado/falha, preservar recursos e registrar
inventário sanitizado. Não repetir seed/initdb, adotar recurso desconhecido, elevar privilégios,
recriar recibo ou apagar evidência. Nova tentativa usa ambiente novo aprovado; nenhum comando
de limpeza/rollback/restauração sobre recurso existente foi preparado ou executado nesta fase.
