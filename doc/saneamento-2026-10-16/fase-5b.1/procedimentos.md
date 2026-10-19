# Procedimentos futuros — não executar sob autorização 5B.1

> Revisão vigente: [Fase 5B.2-A.2](../fase-5b.2-a/fechamento-a2/README.md).
> Os comandos originais abaixo são históricos. Metadados públicos foram consultados por HTTPS;
> nenhuma imagem foi adquirida. A aquisição e todas as operações persistentes exigem novo gate.

> **Histórico do desenho 5B.1; substituído para uso operacional pela revisão 5B.2-A.1.**
> Não executar os exemplos abaixo. Ações acopladas, carga, web e descarte estão bloqueadas,
> inclusive quando aparecerem numa autorização antiga. Ver
> [ações e pré-condições vigentes](../fase-5b.2-a/correcao-a1/operacoes-e-metadados.md).

Todas as ações com Docker, banco ou carga exigem deliberação específica 5B.2. Exemplos abaixo
usam Python da venv existente e paths a partir da raiz; não executar agora. PyYAML é dependência
de desenvolvimento já declarada; scripts não instalam dependências por conta própria.

## Antes de qualquer operação

1. Nomear responsável técnico e aprovador; confirmar manifesto, portas/limites, protocolo e guarda.
2. Revisar `integridade.json`/fontes. Escolher imagens imutáveis e registrar procedência. Nenhum
   digest ou imagem local foi obtido nesta fase.
3. Após autorização de arquivos operacionais, copiar **somente** `homologacao.env.example` para
   `homologacao.env` nesta pasta e preencher digests verificados/credenciais exclusivamente sintéticas.
   Não copiar `.env`, cookies, credenciais de Docker registry ou senhas do ambiente existente.
4. Registrar aprovação humana em `autorizacao.json` a partir do exemplo, com ação/subcaso,
   referência da mensagem, aprovador, SHA-256 do Compose, da configuração sintética e do arquivo de integridade. Ações vazias
   recusam tudo. ID da engine deve ser obtido na inspeção local autorizada e aprovado antes de recursos.
5. Nenhum arquivo real de configuração, autorização, recibo ou evidência foi criado aqui.

## Aquisição/build separado, somente se autorizado

Compose tem `pull_policy: never`: não baixa imagens. Em 5B.2, aprovar aquisição por digest e build
com contexto limpo exportado do commit acima, sem arquivos não rastreados. Preferir exportação
Git para diretório novo autorizado, contendo backend, Dockerfile, .dockerignore e entrypoint
versionados; não mandar a working tree inteira como prova de procedência. Verificar que nenhuma
credencial ou mídia entra no contexto. O Dockerfile existente não é modificado nesta fase.

O build futuro precisa de label `org.opencontainers.image.revision` igual ao commit aprovado.
Usar ID local imutável `sha256:...` ou referência `repositorio@sha256:...` após verificação. Labels
declaram procedência, não a provam sozinhas: guardar hash do contexto/lock e registro de build.
Imagem da app deve fornecer `/app/backend`, Python/dependências e usuário 10001; PostgreSQL deve
ser 18 e ter entrypoint oficial de cluster novo. Sem isso, interromper; não adaptar código em runtime.

## Ações do operador preparadas

Prefixo dos exemplos: `backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-5b.1/operar.py`.

| Ação | Operação e recurso afetado | Autorização e interrupção |
|---|---|---|
| `validar` | Lê somente artefatos/configuração independente; verifica hashes, chaves, digests, labels e estrutura | Só executar após fase atual; exemplo de imagem indefinida deve ser recusado. Não comprova runtime |
| `inspecionar` | Consulta contexto local e engine ID, sem iniciar recursos | Aprovar inspeção de metadados; sem segredo/config global. Registrar engine ID antes de aprovar provisão |
| `provisionar` | Recusa nomes ocupados; verifica imagens; cria rede/volumes/containers e recibo; inicia somente PG, que cria cluster/DB novos | Aprovar criação e initdb expressamente; não inclui app/schema/baseline. Se falhar parcialmente, preservar e inventariar; não repetir ou remover automaticamente |
| `esquema` | Container de tarefa explícita, preservado com recibo: exige banco sem tabelas de usuário; provisão, migration, provisão, marcador/controladores do laboratório | Aprovar roles, DDL/migrations e container de tarefa; sem base real. Recusa repetição/“reparo” automático |
| `conferir` | Tarefa com runtime, container preservado: lê identidade do banco, versão 18, marcador, privilégios/triggers e plano de migrations | Aprovar container de tarefa e leitura isolada. Falha não autoriza contorno/elevação |
| `baseline` | Reserva execução em tabela de controle e chama seed sintético com relógio/args fixos; gera atos/trilha/arquivos | Aprovar carga completa e limites depois de revisar seed. Sem repetição; falha parcial permanece preservada |
| `iniciar` | Inicia app pré-criada; guardas recusam banco/papel/marcador/proteções/schema errados | Aprovar serviço web local; não migra, não carrega dados; sem acesso público |
| `demonstrar --cenario P01-A` | Confere identidade/autorização e informa roteiro/URL para execução manual do subcaso autorizado | Aprovar cada subcaso entre P01-A/C, P06-A/C, P07-A/B, P15-A/F; operador registra esperado/observado |
| `evidencias` | Grava arquivo novo com recibo/hashes, sem dump/env/logs integrais | Aprovar destino e custódia; arquivo existente causa recusa. Capturas/XLSX adicionais são manuais e sanitizados |
| `preservar` | Para apenas app isolada; mantém banco/volumes | Aprovar contenção; não encerra engine nem serviços externos ao laboratório |
| `encerrar` | Para somente containers de IDs registrados após revalidação | Aprovar encerramento do banco/app; preserva volumes, recibo e arquivos |
| `descartar` | Exige containers já parados, ação aprovada e confirmação literal com UUID/IDs; revalida labels/engine/volumes; remove só IDs/volumes registrados, sem força | Aprovação de descarte separada com guarda decidida. Sem `down -v`, paths recursivos ou remoção de recursos desconhecidos; erro preserva remanescentes |

Exemplos futuros, não executados:

```powershell
backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-5b.1/operar.py validar
backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-5b.1/operar.py conferir
backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-5b.1/operar.py demonstrar --cenario P15-C
```

Não chamar Compose diretamente para pular guardas. Se transformação de caminhos Windows/Rancher,
metadata de volume ou criação de container variar e gerar recusa, registrar evidência e revisar
artefatos antes de nova autorização; não reduzir validação para “funcionar”.

## Baseline e cenários

[baseline.json](baseline.json) fixa número 31, ano 2026, código exclusivo, janela recursal declarada
e T0 16/10/2026 às 12h -03:00. Seed gera múltiplos Editais derivados do número; não assumir que o
Processo é um ato único. Datas antigas podem limitar navegação quando o ensaio ocorrer depois de
T0: mudar relógio/manifesto exige revisão e nova evidência, não retroagir critérios depois do resultado.

Gerador usa API de comandos existente e registra dados sintéticos. Preserva rascunhos/versões e
recusa carga sobre Processo já presente ou reserva prévia. Não promete uniformidade de todos os
UUIDs/bytes; hashes de saída devem ser coletados após execução. O seed é a base navegável, não
gerador automático de todos os negativos. Roteiros P01/P06/P07/P15 da F4 especificam variantes
manuais; conferir precondições e criar cenários novos autorizados sem mutar/excluir para limpar.

Antes da carga, revisar contagens máximas planejadas contra limites de 20 Editais/100 inscrições/
5000 eventos; eles ainda não foram medidos. Se não puder assegurar o teto, não executar carga
sob essa autorização, apresentar manifesto ajustado ao usuário. As 43 condições continuam vinculadas
a testes/demonstrações/homologação/instituição, não cobertas automaticamente pelo seed.

## Decisões exatamente necessárias na Fase 5B.2

1. Aprovar responsável, engine local e imagens/contexto de build por digest, recursos/volumes e rede.
2. Autorizar `provisionar`, incluindo initdb/criação do banco sintético e escrita de recibo.
3. Autorizar `esquema`, explicitando roles, migrations e marcador; a proibição atual não é revogada
   pelo simples fato de este script existir.
4. Autorizar `conferir`; depois a carga `baseline` com orçamento e tratamento de falha parcial.
5. Autorizar `iniciar` e subcasos `demonstrar` por ID, incluindo GET com auditoria e atos privados;
   pactuar protocolo humano antes de envolver participantes.
6. Definir coleta/guarda, autorizar `evidencias` e capturas adicionais sanitizadas.
7. Autorizar separadamente `preservar`/`encerrar` e, se desejado, `descartar` com confirmação. Não
   há restauração sobre volume existente; futura restauração exige plano de recurso novo.

Não estão implementados nem autorizados aqui: suite persistente/limpeza de banco de teste,
substituição normativa legítima .07, importação RA, envio externo, inferência ou fonte real de
sorteio. Não aumentar permissões ou desabilitar triggers para concluir ensaio.
