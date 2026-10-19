# Fase 5B.2-A.2 — dependências técnicas de isolamento

Data: 16/10/2026. Base funcional: `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`.

**FASE 5B.2-A.2 — DEPENDÊNCIAS TÉCNICAS REVISADAS; EXECUÇÃO OPERACIONAL NÃO AUTORIZADA.**

## Resultado

Foram obtidos e verificados digests de três índices públicos e seis manifestos de plataforma,
sem Docker, download de camadas ou build. O operador passou a exigir uma única ação e escopo
exato de efeitos/recursos; o mapa de planejamento não habilita operações bloqueadas.
O Compose deixou de solicitar a criação do banco da aplicação no bootstrap oficial PG.
Um Dockerfile exclusivo, por digest e sem apt/entrada automática, foi preparado como proposta.

**29 testes puros passaram.** Sintaxe, estrutura, grafo, hashes e metadados foram conferidos.
Isso não prova isolamento operacional nem conclui as dependências restantes. Bootstrap/restart,
banco/papéis/migrations/concessões, baseline, web/demonstrações e descarte seguem bloqueados.
Código funcional, configurações de desenvolvimento, banco, specs e Constituição não foram alterados.

## Entregas

1. [Plano de inicialização segregada](plano-inicializacao.md): efeitos, pré-condições e gates.
2. [Inventário de imagens/digests](inventario-imagens.md) e [metadados verificáveis](metadados-publicos.json).
3. [Matriz de autorização por ação](matriz-autorizacao.md), vinculada à política pura do operador.
4. [Baseline: critérios e cobertura](baseline-e-aceite.md), sem geração ou carga.
5. [Controle das sessões web](sessoes-web.md): implementado, proposto, procedimental e residual.
6. [Validação, testes negativos e bloqueios A01–A12](testes-e-bloqueios.md).
7. [Proposta da primeira validação operacional](proposta-primeira-validacao.md): somente leitura do ID
   da engine local já ativa, sem presumir autorização.
8. [Evidência estática e hashes](evidencia-a2.json) e [testes puros](test_guardas_a2.py).

## Limitações e decisões restantes

- Plataforma/engine locais não consultadas; as duas arquiteturas do registry são candidatas.
  Digests observados não autorizam aquisição nem comprovam segurança/compatibilidade das imagens.
- Bootstrap escreve catálogos, templates, banco administrativo, papel inicial e logs; não é operação
  somente leitura. Executores segregados e identidade do cluster precisam de revisão posterior.
- Política SQL de gatilhos/funções permanece pendente e bloqueante; não foram inventados hashes
  de `pg_get_triggerdef/pg_get_functiondef` nem aprovados valores coletados de base real.
- Baseline ainda não tem orçamento/cobertura completos. Há conflito entre T0 fixo e janelas da
  sessão; o seed usa catálogo institucional e preparação ORM. Definir manifesto aprovado antes da carga.
- Web continua bloqueada; autenticação/perfis/estratégia de restrição e protocolo precisam de decisão.
  Há controle de ação do operador, não ACL de cenário no sistema funcional ou no daemon.
- Falha parcial, mutabilidade do host, coleta detalhada e eventual descarte exigem plano próprio.

## Alterações e preservação

Modificados exclusivamente em `fase-5b.1/`:

| Arquivo | Motivo |
|---|---|
| `operar.py` | Incorporar revisão/política de escopo, bloquear ações ainda só planejadas e incluir novo módulo na integridade |
| `compose.homologacao.yaml` | Separar banco administrativo de bootstrap do banco futuro da aplicação |
| `autorizacao.example.json` | Revisão A2 e escopo vazio obrigatório; continua sem autorização |
| `integridade.json` | Doze hashes técnicos atualizados, incluindo política operacional |
| `README.md`, `procedimentos.md` | Adendos com referência vigente, mantendo histórico |

Criado em `fase-5b.1/isolamento/`: `politica_operacional.py`, módulo puro sem I/O, com seis
escopos preparados e grafo de dezoito ações planejadas. O módulo não concede autorização.

Nesta pasta foram criados os oito relatórios Markdown, `Dockerfile.homologacao.proposta`,
`consultar_metadados_publicos.py`, `metadados-publicos.json`, `test_guardas_a2.py`,
`hashes-antes.json`, `evidencia-a2.json` e seis cópias byte a byte em `historico-a1/` dos arquivos
revisados. O manifesto de evidências enumera todos os caminhos, hashes anteriores e atuais.
As cópias históricas são evidências e não artefatos operacionais vigentes; seus links conservam
o contexto original. Documentos/resultados A1 foram preservados sem alteração.

Não foram criados arquivos de autorização/configuração operacional, Docker config, recibos,
containers, imagens, bancos, redes, volumes ou dados de demonstração. Nenhum script operacional,
Compose, migration, carga, demonstração, e-mail, commit, push ou merge foi executado.
O coletor documental HTTPS foi a única operação de rede, além da tentativa do navegador sem acesso
e da consulta inicial de metadata pública Docker Hub; validação e testes ocorreram sem rede.

## Próximo passo proposto

Deliberar sobre P0, responsável, endpoint e custódia. P0 consulta apenas a engine já ativa e
interrompe se ela estiver indisponível. Depois escolher plataforma/referências e decidir aquisição/
build por gates separados. Em paralelo, revisar executores de bootstrap e o manifesto da baseline,
sem antecipar consultas institucionais ou decisões administrativas da DEC-15.
