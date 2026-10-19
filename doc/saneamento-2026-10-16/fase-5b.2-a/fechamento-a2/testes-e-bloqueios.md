# Validação e bloqueios remanescentes

## Verificações realizadas

1. Consulta pública de metadados por HTTPS, separada dos testes: três índices e seis manifestos
   amd64/arm64, SHA-256 dos bytes conferido contra headers/descritores; sem blobs/camadas.
2. Validação local: AST Python, JSON/YAML, conjunto de hashes, estrutura Compose, grafo sem ciclos,
   correspondência entre política e ações do operador, autorização de exemplo vazia, 14 receitas
   preservadas, referências e ausência de arquivos operacionais preenchidos.
3. **29 testes puros passaram**, sem rede, banco, Docker ou temporários. São as 19 regressões A1
   com fixture de autorização adaptada à revisão e dez verificações novas de escopo/grafo. Os
   testes originais e documentos de resultado A1 não foram reescritos. Módulos de guarda são
   importados; `main` só é exercitada com dependências simuladas, não como script operacional.

Comando de teste executado:

```powershell
backend/.venv/Scripts/python.exe -B doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/test_guardas_a2.py
```

Os testes bloqueiam subprocessos/rede com mocks. `-B` evita bytecode. O coletor público foi uma
consulta de metadados autorizada separada, não teste de egress nem script operacional.
Detalhes/hashes no [resultado estruturado](evidencia-a2.json). Nenhuma evidência equivale a
comprovação de isolamento em execução, aprovação do ambiente ou encerramento de pendência.

## Positivos e negativos das guardas

| Guarda | Positivo / cobertura atual | Negativo / cobertura atual | Ensaio futuro necessário |
|---|---|---|---|
| Autorização | Uma ação preparada, revisão/hash/escopo correto aceitos em memória | Ações agregadas, alias antigo, cenário anexado, revisão/hash incorretos, recurso/efeito extra ou omitido, duplicata/curinga recusados | Aprovação real sob custódia; sem inicializar recursos |
| Isolamento/config | Inspeção pode dispensar imagem e DB em fixture pura | Docker sem aprovação, endpoint remoto, herança e recibo incompleto recusados | Cliente/engine/caminhos reais após autorização; nenhuma conexão SQL |
| Inventário | Lista bem-sucedida vazia ou com nomes distintos aceita em memória | Erros 1/125/126, JSON truncado/nulo/duplicado e metadata nula recusados | Engine isolada; confirmar distinção de ausência/erro, concorrência e representação Windows |
| Dependências | Grafo atual acíclico e ações preparadas correspondem ao operador | Ciclo, referência ausente e ação só planejada recusados em memória | Pré-condições reais precisam de recibos/evidência, não só presença no grafo |
| Criação | Fluxo simulado faz apenas create e exige estado parado | Start/up não são chamados; bootstrap/banco/migrations/seed bloqueados antes de cliente | Só após autorização de criação: alvos novos, sem start; preservar falha parcial |
| Proteção SQL | Gatilho/função fictícios esperados aceitos em memória | Política pendente/incompleta, gatilho alheio/desabilitado ou função alterada recusados | Mapear política completa pela fonte; ensaio PG sintético em gate posterior |
| Tarefa read-only | AST confirma transação de leitura, sem call_command/admin/carga | Plano: tentar INSERT/DDL, ambiente com credencial privilegiada | Não executado; tentativa SQL exige autorização em banco isolado |
| Rede/mídia | Manifesto interno/loopback/volumes dedicados conferido estaticamente | Plano: rede/mount/socket/volume extra, options remotas, porta pública, bind trocado após preflight | Primeiro mocks de metadata; runtime somente com recursos autorizados |
| Bootstrap | POSTGRES_DB administrativo, app DB distinto | Plano: volume existente em bootstrap, PG_VERSION ausente em restart, scripts/dump de init inesperados | Executores ainda bloqueados; não testar com initdb nesta fase |
| Baseline | Critérios e mapa de 14 casos revisados | Plano: origem real, orçamento excedido, órfão, alias repetido, janelas vencidas, falha parcial | Carga continua bloqueada; comparação em duas instalações novas só com autorização |
| Web/descarte | Bloqueio técnico de ações e launcher | Plano: acesso fora de roteiro, permissão trocada, descarte parcial/concorrrente | Exigem estratégia aprovada e gates próprios; não executar aqui |

## Evolução dos achados A01–A12

| Achado | Avanço nesta revisão | Bloqueio restante / responsável proposto |
|---|---|---|
| A01 | Plano segregado, banco da aplicação retirado do bootstrap automático, ação única/escopo exato | Executores de bootstrap/restart/banco/papéis/migrations/concessões não liberados; responsável técnico e aprovador operacional |
| A02 | Efeitos de container/arquivos e read-only explicitados na matriz | Conferência exige PG/schema/política e ensaio posterior; responsável técnico |
| A03 | Proposta distingue bloqueio, futuras restrições e procedimento | Autenticação/perfis/proxy ou estratégia alternativa e protocolo ainda por decidir; produto/Cefor/homologação |
| A04 | Segregação mantida e privilégios definidos por etapa | Arquivos/serviços administrativos exclusivos ainda por preparar; equipe técnica |
| A05 | Fail-closed mantido e regressões passam | Testar API/caminhos/concorrência local futuramente; equipe técnica |
| A06 | Autorização prévia agora exige ação única e escopo; sem seleção de contexto herdado | ID/endpoint/cliente locais e custódia ainda não confirmados; operador/aprovador |
| A07 | Digests públicos verificados; Dockerfile proposto por digest, sem apt e com wheels somente | Plataforma, builder, contexto/lock e compatibilidade ainda sem aceite; app sem imagem final; responsável técnico/produto |
| A08 | Política exata continua bloqueando, sem hashes de DB inventados | Mapa de tabelas/gatilhos/funções e aprovação técnica da referência; equipe técnica |
| A09 | Critérios de origem/determinismo/tempo/contagem/cobertura e recuperação definidos | Manifesto de carga e complementos não prontos; catálogo e T0 requerem decisão; produto/técnico |
| A10 | Nenhuma remoção reintroduzida | Custódia/retencão, concorrência e recuperação parcial; aprovador e técnico |
| A11 | Nova política incluída no conjunto de integridade; arquivos anteriores preservados | Host/binds ainda mutáveis; decidir snapshot/controle de acesso antes de operação; técnico |
| A12 | Campos exigidos por etapa formalizados, sem inferir sucesso de recibo | Coleta resumida atual não cobre todas as fichas; revisar antes da etapa respectiva; técnico/homologação |

Os achados não são encerrados por esta tabela. A07 avançou de ausência de digests para metadata
verificada e proposta de build; isso não aprova imagem. A01 avançou em segregação documental e
configuração, mas o operador continua recusando as etapas sem implementação revisada.

## Ordem recomendada

1. Confirmar responsável, endpoint/cliente e autorizar somente a inspeção local de metadados proposta.
2. Escolher plataforma/digests/contexto/builder e revisar Dockerfile proposto; decidir aquisição/build
   em autorizações próprias, ainda sem criar o laboratório.
3. Revisar os executores segregados e política SQL; aprovar cada etapa persistente separadamente.
4. Deliberar sobre T0, catálogo fictício e manifesto/cobertura da baseline; pactuar sessão e protocolo.
5. Somente depois propor carga/demonstrações por subcaso, coleta e destinação. Nenhuma etapa
   administrativa pendente da DEC-15 é ratificada por sucesso técnico.
