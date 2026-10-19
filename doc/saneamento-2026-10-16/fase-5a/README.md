# Fase 5A — viabilidade do ambiente isolado

Data: 16/10/2026. Base: `001-decisoes-pendentes` @ `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`.

**FASE 5A — VIABILIDADE ANALISADA; PROVISIONAMENTO E DEMONSTRAÇÕES NÃO AUTORIZADOS.**

## Resultado da inspeção

Há código, dependências locais, Docker CLI/Compose e geradores sintéticos suficientes para
**viabilidade técnica condicionada**. Não há evidência nesta etapa de daemon disponível, imagens
fixadas, recursos livres, baseline pronta, isolamento aplicado ou aprovação institucional.
O ambiente não está aprovado nem preparado.

Principal incompatibilidade: `compose.yaml` é desenvolvimento e importa `backend/.env`; seu
entrypoint provisiona papéis, executa migrations e sincroniza unidades automaticamente. O Dockerfile
também instala dependências em build. Portanto `up`, `run` ou `exec` não são intercambiáveis com
inspeção; não usar a pilha atual como homologação sem planejamento operacional separado.

## Entregáveis

- [Inventário técnico](inventario-tecnico.md).
- [Isolamento proposto](isolamento.md).
- [Baseline sintética planejada](baseline-planejada.md).
- [Responsabilidades e aprovações](responsabilidades.md).
- [Plano 5B e autorização granular](plano-5b-e-autorizacao.md).
- [43 condições e tipos de evidência](evidencias-43-condicoes.md).

Fontes obrigatórias consultadas: [índice Fase 4](../fase-4/README.md),
[demonstrações](../fase-4/plano-demonstracoes.md),
[autorização proposta](../fase-4/proposta-autorizacao.md),
[protocolo](../fase-4/protocolo-para-aprovacao.md),
[matriz](../fase-4/matriz-conformidade.md),
[Constituição](../../../.specify/memory/constitution.md), configurações e specs vinculadas no inventário.

## Impedimentos e decisões necessárias

| Impedimento / desconhecido | Decisão ou evidência exigida |
|---|---|
| Ambiente isolado não provisionado nem confirmado | Aprovar manifesto, responsável, nomes, portas, limites e recursos antes de criação |
| Baseline previamente preparada não demonstrada | Escolher preparação nova com autorização explícita de migrations/papéis ou artefato sintético verificado; não tratar baseline ausente como existente |
| Compose atual lê configuração de desenvolvimento e inicializa banco | Autorizar artefatos operacionais independentes antes do provisionamento, sem modificar a pilha de desenvolvimento |
| Tags de imagens mutáveis e build com rede | Fixar digests/dependências e aprovar aquisição/build separado; runtime sem egress |
| Cliente PostgreSQL local 17, alvo do projeto 18 | Planejar ferramentas 18 no ambiente isolado; não presumir compatibilidade do `pg_dump` 17 com servidor 18 |
| Testes Django podem criar/migrar/truncar/apagar banco de teste | Autorização separada e banco de teste distinto; não usar o banco de homologação interativa como banco da suíte |
| Corpus/seed não comprovam todas as condições e cenários | Aprovar manifesto sintético, casos negativos e complementos sem criar regra nova |
| Participantes/autoridades/protocolo não aprovados | Cefor/produto designar pessoas e pactuar critérios; encarregado orientar registros pessoais da participação |
| Condições institucionais fora do alcance técnico | Respostas .04/.12/.13, validação de concessão/editorial e nova deliberação das pendências |
| Descarte não autorizado | Preservação por padrão; autorizar alvo e destinação separadamente |

## Inspeções efetivamente executadas

Leitura de arquivos versionados, nomes de variáveis do `.env.example` (sem seus valores), `git status`,
resolução de executáveis e comandos de versão; leitura de metadados de pacotes sem importar Django
settings. Sem leitura de `.env`, credenciais ou configurações carregadas de banco. Sem conexão
PostgreSQL ou daemon Docker, container/serviço iniciado, teste ou geração de dados.

Somente os sete documentos desta pasta foram criados. Fases anteriores, código, specs, Constituição
e refs preservados. Nenhum commit, push, merge, migration ou envio externo. Links locais, cobertura
dos 43 itens e consistência de gates revisados; não há nova declaração de conformidade.
