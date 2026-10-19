# Fase 5B.2-A — inspeção pré-operacional

> Adendo posterior autorizado: [correções estáticas 5B.2-A.1](correcao-a1/README.md).
> As referências de implementação e hashes deste relatório descrevem a versão inspecionada
> antes das correções; as cópias originais e o novo manifesto estão indicados no adendo.

Data: 16/10/2026. Base funcional: `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`.

**FASE 5B.2-A — INSPEÇÃO CONCLUÍDA; AQUISIÇÃO, PROVISIONAMENTO E DEMONSTRAÇÕES NÃO AUTORIZADOS.**

## Conclusão

O Compose foi preparado de forma independente e contém barreiras úteis, mas **não recomendo
autorizar sua execução ampla no estado atual**. Há efeitos além do nome da ação, guardas de
autorização que não limitam a sessão web e lacunas de identidade/procedência/recuperação a resolver.
Não foi detectado carregamento explícito de `backend/.env` ou transporte real de e-mail no
manifesto. Isso não constitui prova de isolamento em execução.

## Relatórios

- [Compose, achados e guardas](inspecao-e-guardas.md): evidências, severidade e casos positivos/negativos propostos.
- [Matriz de ações e baseline](acoes-e-baseline.md): comandos exatos do operador, efeitos, limites e 14 receitas.
- [Imagens, engine e autorização 5B.2-B proposta](imagens-e-autorizacao.md): procedência, dependências, comandos condicionados e proibições.
- `evidencia-estatica.json`: parsing, hashes e preservação dos 15 artefatos anteriores, sem execução deles.

Fontes consultadas: todos os artefatos da [Fase 5B.1](../fase-5b.1/README.md), sua
[revisão](../fase-5b.1/revisao-estatica.md) e [procedimentos](../fase-5b.1/procedimentos.md),
[plano 5A](../fase-5a/plano-5b-e-autorizacao.md),
[Constituição](../../../.specify/memory/constitution.md), Dockerfile/.dockerignore/lock e
specs 003, 015, 026, 044, 060 e 073 pelos registros de rastreabilidade.

## Bloqueios por tipo de execução

| Antes de | Resolver / aprovar |
|---|---|
| Qualquer contato com daemon/registry | Autorização expressa, responsável, endpoint local já ativo e escopo de metadados/rede; não iniciar daemon |
| Aquisição de imagens | Plataforma, referências/digests reais, fonte pública, configuração Docker sem credenciais institucionais e espaço; nenhum digest disponível comprovado nesta inspeção |
| Build | Contexto exportado revisado, Dockerfile de build com bases imutáveis aprovado e rede/dependências delimitadas; atual usa tags/apt mutáveis |
| Criação/start de recursos | Tratar falha de inspect como erro, não ausência; validar pós-criação sem adoção de recurso; distinguir create de start/initdb; estratégia para falhas parciais |
| Esquema/carga/conferência | Credenciais por tarefa, identidade e privilégios mínimos; cobertura/contagens/relógio da baseline; autorizar toda escrita incluindo recibos e containers |
| Sessões/demonstrações | Aceite de protocolo, restrição operacional dos subcasos, isolamento efetivo e responsável; URL não é mecanismo de autorização |
| Descarte | Recuperação de estado parcial, custódia, lista completa e identidade de alvos, concorrência tratada; aprovação própria, nunca consequência da aquisição/build |

Esta etapa apenas **documenta** achados. Nenhum artefato da 5B.1 foi corrigido ou seu hash alterado;
nenhuma nova regra, spec ou Constituição foi modificada. Correções exigem próxima autorização
de artefatos; não são tomadas como automaticamente aprovadas por constarem do relatório.

## Verificações executadas nesta fase

Somente leitura, AST Python sem import dos módulos novos, YAML/JSON, comparação de hashes e
links locais. Não executados: Docker/Compose, operador, gerador, receitas, testes persistentes,
daemon, pull, build, banco, migrations, e-mail, commit, push ou merge. Disponibilidade local de
ferramentas citada da Fase 5A é histórica, não nova observação do daemon.
