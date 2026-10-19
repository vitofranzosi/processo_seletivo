# Fase 5B — plano operacional e autorização granular proposta

**NÃO AUTORIZADO. COMANDOS APENAS PREVISTOS, NÃO EXECUTADOS.**
Referências: [isolamento](isolamento.md), [baseline](baseline-planejada.md),
[responsáveis](responsabilidades.md) e planos P01/P06/P07/P15 da Fase 4.

## Sequência e pontos de controle

| Etapa | Gate / comandos ou operações previstos | Recursos afetados / risco | Evidência / critério de interrupção |
|---|---|---|---|
| 1 Confirmar ambiente | G0: inspeção futura do daemon (`docker info` com lista restrita), imagens por digest, nomes/volumes/portas, commit e estado do checkout. Não imprimir env/config com segredos | Somente metadados de recursos aprovados; risco de confundir client instalado com daemon apto | Manifesto sanitizado, capacidade e disponibilidade; parar se recurso existir sem procedência, destino divergente ou dado real |
| 2 Aprovar baseline | G0: revisão do manifesto `f4-sintetico-v1`, opções do seed, cenários/complementos e contagens, protocolo e responsáveis | Planejamento; risco de colisão, cobertura insuficiente ou carga maior que limite | Aprovação humana com variante A/B de preparação e limites; sem aprovação não criar carga |
| 3 Preparar artefatos e recursos | G1: criar arquivos operacionais independentes para revisão; G2: aquisição/build fixados e criação da rede/volumes/containers isolados | Rede, disco e serviços novos; build pode acessar registries. Runtime sem saída. Nunca reaproveitar Compose dev/env | Diff de artefatos, hashes/digests e mounts/ports; parar se herdar `.env`, rede pública, socket ou volume existente |
| 3a Preparar esquema | G3, **autorização distinta**: escolher baseline B restaurada em recurso novo ou A com provisionar → migrar → provisionar. Comando `manage.py migrate --noinput` somente aqui, se aprovado expressamente | Esquema/roles exclusivos; alto risco se alvo incorreto ou privilégios misturados | DB/host/role confirmados, schema/versão, proteção `N de M` após segunda passada; parar se zero protegidas ou qualquer base fora da lista |
| 4 Segurança/conectividade | G4: `pg_isready` no cluster interno; SQL de identidade/versão e verificação de proteções/roles; `manage.py migrate --check` (verifica, não migra), `/readiness`; checar backend local, fonte demonstrativa, assistente e egress | Somente ambiente isolado; readiness/HTTP pode criar metadados/sessão conforme fluxo | Identidade exata, sem migrations pendentes, proteção e isolamento comprovados; não testar egress chamando provedor externo |
| 4a Gerar dados | G5: `sincronizar_unidades`, autoridades e `seed_demo`/helpers/API somente com manifesto aprovado | Dados sintéticos, atos e auditoria, mídia; não confundir com leitura | Contagens e hashes, marca sintética, fonte e datas; parar se ultrapassar orçamento ou faltar cenário sem inventar regra |
| 5 Cenários autorizados | G6: executar subcasos P01/P06/P07/P15 nomeados por browser/API existente. Memória é bloco distinto. G6T: suíte persistente separada, se autorizada | Gravações de Editais/inscrições/versões/trilha e XLSX; teste pode criar/migrar/truncar/remover banco de teste | Ficha por cenário; resultado observado separado de esperado; parar por desvio, rede, dados reais ou alteração funcional necessária |
| 6 Coletar evidências | G7: salvar apenas capturas/JSON/IDs/hashes/XLSX sintéticos autorizados; `Get-FileHash -Algorithm SHA256`; dumps só com autorização específica | Pasta nova e artefatos; risco de token/sessão ou pessoa em captura | Manifesto de evidências sanitizado e custódia; parar se dados fora do escopo, não apagar evidência para ocultar problema |
| 7 Preservar/restaurar/descartar | G8: preservar e parar apenas app isolada. Restauração em volume novo e G9 descarte são decisões separadas, não automatismos | Volumes, recursos e custódia; perda irreversível se alvo errado | Inventário final/retencão e decisão humana; não descartar sem nome/path resolvido, revisão e autorização específica |
| 8 Deliberar | Produto/Cefor/comissão recebem relatório por caso e retornos institucionais | Documentação; risco de converter sucesso técnico em regra | Aceites e decisões por identificador; sem encerramento por silêncio ou aprovação genérica |

Nenhuma etapa da tabela é autorizada pela Fase 5A. A enumeração de migrations em G3 é proposta
de autorização futura explícita, não exceção à proibição vigente. Se o usuário mantiver proibição
em 5B, somente baseline sintética previamente preparada e verificada poderá suprir o esquema;
se não existir, o provisionamento completo fica impedido. Não criar saída alternativa silenciosa.

## Comandos previstos — forma segura e dependências

Arquivos operacionais abaixo **ainda não existem**; serão criados somente se G1 for aprovado e
revisados antes de G2. Não copiar `.env` existente. Variáveis de caminhos representam manifesto
aprovado; não recebem valores de credenciais e não devem ser interpoladas em comandos de exclusão.

```powershell
# Exemplo para futura G1/G2; não executado, depende de arquivos revisados.
$composeHomologacao = 'doc/saneamento-2026-10-16/fase-5b/compose.homologacao.yaml'
# Arquivo independente a definir pelo responsável, fora do repositório, sem exibir conteúdo.
$configuracaoHomologacao = Read-Host 'Caminho aprovado da configuração exclusiva'
docker compose -p cefor_homologacao_f4_20261016 -f $composeHomologacao --env-file $configuracaoHomologacao config --services
```

Depois do gate correspondente, `pull/build/create/up` somente com esse projeto/arquivo e serviços
aprovados, nunca o Compose padrão. Não imprimir `config` completo, `env` ou settings irrestritos.
O arquivo novo precisa impedir entrypoint automático no runtime. Exemplos de **nomes de comandos**
para G3: `manage.py provisionar_papeis`, `manage.py migrate --noinput`, novamente provisionamento.
Argumentos de autenticação por canal seguro devem ser revisados pelo responsável; não incluir
senhas em documento, log, histórico de terminal ou exemplos executáveis.

Após recursos e esquema autorizados, comandos restritos previstos:

```powershell
# Exemplos dependem da confirmação dos nomes e do entrypoint revisado.
docker exec cefor-f4-pg-20261016 pg_isready -d ps_homologacao_f4_20261016
docker exec cefor-f4-app-20261016 python manage.py migrate --check
```

Não confundir readiness de porta com privilégio/imutabilidade. A consulta SQL sanitizada, no cluster
isolado, deve conferir `current_database()`, `current_user`, `version()` e schema; depois comparar
proteções com o inventário versionado `TABELAS_APPEND_ONLY`. Nenhuma consulta dessa natureza foi
executada em 5A. Nenhuma falha de proteção autoriza desabilitar trigger ou elevar runtime.

G5 candidato, somente após revisão das opções/efeitos e orçamento:

```text
python manage.py seed_demo --codigo <codigo-sintetico-aprovado> --numero <numero-numerico-aprovado> --ano <ano-aprovado> --titulo <titulo-sintetico-aprovado>
```

É gabarito, não comando pronto. Não repetir com mesmos IDs/número esperando limpar ambiente;
registrar deslocamento do relógio e atos de seed. Complementos do plano devem estar enumerados
antes; se não cobertos, parar e pedir alteração de escopo sem modificar código funcional.

## Suíte persistente, se escolhida — autorização independente G6T

`pytest`/`make test-pg` podem preparar esquema e usar casos transacionais que truncam tabelas,
além de criar/remover banco de teste. Não estão cobertos por autorização de navegação sintética.
Nome esperado distinto: `test_ps_homologacao_f4_20261016`; confirmar antes de executar. Conta de
teste elevada fica só nesse cluster, nunca no app. Não usar `--reuse-db` como estratégia de
segurança/reprodução nem presumir que evita migrations ou limpeza.

Uma autorização de G6T deve indicar **testes específicos**, permissão de criação/migrations e
limpeza própria da suíte no banco de teste exclusivo, preservando baseline interativa/evidências.
Se limpeza permanecer vedada, não executar esses casos; usar procedimentos de demonstração
autorizados. Não mudar fixtures para fazer teste passar sob privilégio incorreto.

## Autorização granular proposta, ainda sem concessão

O usuário pode aprovar blocos separadamente, indicando manifesto/versão, responsável, alvo,
cenários, limites de dados, janela de execução e evidências. Dependências não são aprovações implícitas.

| Gate | O que aprovar expressamente | Pré-condição |
|---|---|---|
| G0 | Inspeção adicional de metadados e decisão do manifesto/protocolo/baseline | Sem provisionamento ou conexão a banco real |
| G1 | Criar arquivos operacionais exclusivos de homologação para revisão | Sem alterar código funcional ou Compose de desenvolvimento |
| G2 | Aquisição/build e recursos isolados nominados | Artefatos/digests/rede/mounts revisados; sem esquema automático |
| G3-A ou G3-B | Preparação nova com roles/migrations **ou** restauração de baseline sintética verificada | Destino exclusivo; credenciais seguras; manifesto e operação autorizados |
| G4 | Verificar identidade, schema, proteções, backend e conectividade interna | Recursos isolados existentes e autorizados |
| G5 | Gerar baseline/sintéticos e atos privados especificados | Esquema/proteções válidos; aprovação de conteúdo e limites |
| G6 + subcasos | Demonstrações persistentes explicitadas, incluindo GET com auditoria | Dataset/manifesto aprovados; sem uso real ou alteração funcional |
| G6T | Testes persistentes específicos e seu ciclo de banco exclusivo | Permissão de preparação/limpeza **expressa**, distinta do banco interativo |
| G7 | Gravar evidências sanitizadas; dump somente se também explicitado | Pasta nova, custódia e limites pessoais definidos |
| G8 | Parar app isolada e preservar recursos/evidências | Sem remover volumes, atos, arquivos ou refs |
| G9 | Destinação/descarte ou restauração em recurso novo | Novo pedido com alvos resolvidos, inventário, retenção e aprovação humana; não pré-autorizado |

Modelo: “Autorizo **[gates/subcasos]**, manifesto **[versão/hash]**, responsável **[nome/função]**,
recursos **[lista exata]**, operações **[lista]**, limites **[contagens/janela]** e evidências
**[destino/custódia]**. As demais operações permanecem vedadas.” Campos vazios não são autorização.

Recomendação imediata: deliberar **G0/G1**, a estratégia de esquema e as responsabilidades; revisar
os artefatos operacionais antes de aprovar G2 em diante. Não há solicitação para autorização ampla
de “toda a Fase 5B” sem especificar as operações de estado persistente e seus pontos de controle.
