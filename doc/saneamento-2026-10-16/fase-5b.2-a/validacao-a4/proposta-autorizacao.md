# Proposta futura — uma única consulta inspecionar

**Não autorizada; não executável nas condições atuais.** A recomendação imediata é autorizar uma revisão nova dos controles, antes de considerar a consulta. Não se solicita contornar a integridade atual.

## Comando de referência e executáveis

Comando exato da proposta anterior, explicitado com caminhos absolutos e preservado apenas para revisão:

```powershell
& 'D:\projetos\cefor\processo_seletivo\backend\.venv\Scripts\python.exe' -B 'D:\projetos\cefor\processo_seletivo\doc\saneamento-2026-10-16\fase-5b.1\operar.py' inspecionar
```

Diretório de trabalho: `D:\projetos\cefor\processo_seletivo`. Não executar: o par de hashes diverge, a autorização está vazia e faltam controles obrigatórios. Se a alternativa B for aprovada, o caminho do novo operador e o comando final deverão ser novamente apresentados, sem substituir este comando por suposição.

A chamada interna atual é `docker --config <pasta exclusiva> --host <endpoint aprovado> info --format {{.ID}}`; é explicação, não autorização para comando direto. O operador atual resolve Docker pelo PATH. Caminho absoluto de docker.exe: **PENDENTE**; identidade/versão/procedência/assinatura/SHA-256: **PENDENTES**. A revisão deve fixar esse caminho e validar os bytes antes do lançamento. Identidade/procedência/SHA-256 do intérprete no caminho acima e integridade do runtime: **PENDENTES**. Existência de um arquivo não demonstra sua confiabilidade.

## Campos e condições de autorização

| Campo | Situação / condição necessária |
|---|---|
| Operação | Somente uma tentativa de inspecionar; sem retry, fallback, mudança de endpoint ou elevação |
| Revisão e comando final | PENDENTES de saneamento autorizado e nova revisão estática |
| Endpoint exato | PENDENTE de confirmação humana de localidade, engine já ativa e ausência de ativação por conexão; nenhum endpoint presumido |
| ID de engine anterior | Desconhecido; finalidade é identificar, não inventar ID ou aprovar recursos |
| Executor e supervisor | PENDENTES de designação nominal e aceitação da responsabilidade |
| Aprovador e referência | PENDENTES de deliberação expressa específica; não inferir de fases passadas |
| Janela/fuso | PENDENTES; fixar início/fim e America/Sao_Paulo antes da autorização |
| Timeout | PENDENTE de valor aprovado e mecanismo automático efetivo; operador atual não implementa |
| Interrupção | PENDENTE de mecanismo testado que encerre só cliente/descendentes autorizados; proposta de grupo/Job Object precisa revisão própria |
| Destino novo das evidências | PENDENTE de caminho absoluto confirmado, sem sobrescrita e com acesso restrito |
| Custodiante e retenção | PENDENTES de definição humana; registrar identidade, acesso e prazo |
| Credenciais | Nenhuma institucional; não pedir login/registry; cliente exclusivo vazio e sem helpers |
| Recursos | Apenas leitura de ID da engine no endpoint aprovado; nenhum container/rede/volume/banco ou aplicação |
| Gravação | Somente novo recibo sanitizado no destino expressamente aprovado; nenhum arquivo de controle alterado implicitamente |
| Efeitos indiretos | Processos Python/cliente, leitura de arquivos, IPC local; possíveis logs/métricas do SO/engine. Não prometer escrita zero no host |

## Pré-condições, cancelamento e evidências

Antes da tentativa: aprovar revisão e comando finais, conferir branch/HEAD e todos os hashes brutos; fixar executáveis confiáveis e endpoint; provar controles de tempo/cancelamento e autorização única; impedir modificações concorrentes. Configuração vazia e ações vazias atuais não devem ser editadas nesta fase. Uma futura preparação desses controles exige autorização separada enumerando arquivos e escopo.

Cancelar sem consultar quando qualquer campo obrigatório permanecer pendente, hash divergir, binário/endpoint não forem confirmados, houver herança conflitante, pedido de credencial, risco de ativar serviço ou ausência de destino/custódia. Durante eventual execução: interromper no deadline, saída fora do contrato, pedido humano ou ação inesperada. Sem parar engine, iniciar Docker Desktop, tentar reparos, repetir ou ampliar privilégio.

Evidência futura: autorização, executor/supervisor, janela/instantes, HEAD, comando completo, hashes de entrada/binários, endpoint sanitizado, stdout limitado ao ID/UUID, categoria de falha sanitizada, código de saída, duração, cancelamento e hash/custódia do recibo. Não anexar stderr bruto, ambiente, perfil Docker ou segredos.

Pós-verificação: confirmar término do processo autorizado e de seus descendentes; comparar arquivos preexistentes com inventário anterior; validar recibo e sua custódia. Não acrescentar comandos Docker de inventário/parada sem autorização própria. Esses limites impedem comprovar independentemente todo o estado da engine apenas com esta consulta; registrar a limitação. Sucesso é somente ID não vazio/UUID correto/exit code zero dentro do prazo; não aprova isolamento, imagens ou provisionamento.

## Próximas autorizações separadas

1. Deliberar alternativa de saneamento e autorizar novos artefatos de controle/testes puros, preservando históricos.
2. Rever o resultado, preencher campos humanos e aprovar a preparação dos controles exatos.
3. Autorizar expressamente uma consulta e seu recibo documental após resolver todos os bloqueios.

Nenhuma dessas autorizações foi concedida pela A.4. Aquisição/build, criação/início de recursos, PostgreSQL/papéis/migrations/carga, aplicação, demonstrações e descarte continuam proibidos.

