# Correção estática — Fase 5B.2-A.1

Data: 16/10/2026. Autorização: solicitação humana anexada nesta sessão, restrita aos artefatos
de homologação 5B.1/5B.2-A. Não autoriza operação nem alteração do sistema funcional.

**FASE 5B.2-A.1 — CORREÇÕES ESTÁTICAS CONCLUÍDAS; EXECUÇÃO OPERACIONAL NÃO AUTORIZADA.**

## Resultado e limites

O operador separa a criação de recursos e não possui mais caminho de start, migrations, seed
ou remoção. Ações antigas são recusadas antes de ler configuração ou invocar Docker.
As tarefas comuns não recebem credenciais administrativas. Erros Docker interrompem a execução;
a ausência é verificada por inventário positivo bem-sucedido, não por erro de inspect.
A autorização é validada antes do cliente Docker, com endpoint e configuração exclusiva explícitos.

Isso não completa o ambiente. O desenho oficial de inicialização PG acopla partida/initdb/banco;
sua substituição precisa de nova decisão, conforme cláusula de incompatibilidade da autorização.
Web, esquema, carga e descarte foram bloqueados, em vez de receber correções arquiteturais
não aprovadas. Não há comprovação de isolamento operacional nem ratificação adicional da DEC-15.

- [Matriz A01–A12](matriz-correcao.md): comportamento, correção, evidência, limites e estado.
- [Operações, proposta de separação e metadados](operacoes-e-metadados.md).
- [Validação e testes negativos](validacao-e-negativos.md).
- [Evidência estruturada](evidencia-a1.json): hashes anteriores/atuais, arquivos e resultados.
- [Testes puros](test_guardas_puras.py): somente memória, subprocessos e rede simulados.

## Preservação e arquivos

Validação concluída: **19 testes puros passaram**, seis arquivos Python com AST válido,
onze hashes técnicos conferidos e 15 cópias históricas íntegras. Na matriz há quatro achados
resolvidos estaticamente, cinco mitigados, um pendente e dois bloqueados. Nenhum está
resolvido operacionalmente. O diff de arquivos rastreados permanece vazio.

As 15 fontes anteriores da 5B.1 foram preservadas byte a byte em `historico-5b1/`, com
[manifesto anterior](estado-anterior.json). São evidências históricas, **não executáveis vigentes**;
links relativos internos dessas cópias conservam o contexto original. O relatório da inspeção
anterior e sua evidência não foram reescritos; o README anterior recebeu apenas um adendo.

Arquivos existentes modificados, relativos a `doc/saneamento-2026-10-16/`:

| Arquivo | Justificativa |
|---|---|
| `fase-5b.1/operar.py` | Separar criação, negar operações pendentes, validar autorização antes de Docker, inventário fail-closed, metadata completa, hashes e resultados |
| `fase-5b.1/compose.homologacao.yaml` | Retirar admin/migration da tarefa comum; identificar exclusivamente conferência |
| `fase-5b.1/homologacao.env.example` | Remover credencial de migration do ambiente comum |
| `fase-5b.1/autorizacao.example.json` | Exigir revisão nova, endpoint, cliente exclusivo e declaração de exclusividade; exemplo continua vazio |
| `fase-5b.1/isolamento/contrato.py` | Exigir política completa de gatilhos/funções; não aceitar gatilho alheio |
| `fase-5b.1/isolamento/tarefas.py` | Somente conferência, sem administração ou carga; transação read-only |
| `fase-5b.1/isolamento/iniciar_aplicacao.py` | Impedir início da web também pela entrada montada enquanto sessão não for aprovada |
| `fase-5b.1/baseline.json` | Explicitar bloqueio e localização histórica do gerador, sem mudar dados/regras do domínio |
| `fase-5b.1/integridade.json` | Atualizar hashes e conjunto obrigatório de onze artefatos técnicos |
| `fase-5b.1/README.md` e `fase-5b.1/procedimentos.md` | Identificar procedimentos antigos como históricos e apontar revisão vigente |
| `fase-5b.2-a/README.md` | Vincular este adendo sem modificar os achados originais |

Criados: `fase-5b.1/isolamento/politica-protecoes.json` (pendente, bloqueante) e, nesta pasta,
`README.md`, `matriz-correcao.md`, `operacoes-e-metadados.md`, `validacao-e-negativos.md`,
`test_guardas_puras.py`, `evidencia-a1.json`, `estado-anterior.json` e as 15 cópias históricas.
A evidência estruturada enumera cada caminho, inclusive os preservados sem alteração.

Não criados: configuração operacional, autorização real, Docker config, recibo de recurso,
baseline, imagem ou banco. Código funcional, desenvolvimento, specs e Constituição preservados.

## Próxima decisão sugerida

Autorizar somente inspeção de metadados, depois de confirmar responsável, destino de evidências,
endpoint local já ativo, configuração cliente vazia e registries públicos permitidos. Não inclui
pull/build. Em paralelo, deliberar sobre a proposta de bootstrap PG e as credenciais por etapa.
Aquisição/build continuam dependentes de imagens/digests, plataforma, contexto limpo e dependências
fixadas. Provisionamento e demonstrações dependem ainda dos bloqueios descritos na matriz.
