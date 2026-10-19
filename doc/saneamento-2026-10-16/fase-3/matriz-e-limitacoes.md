# Evidências, dependências e decisões restantes — Fase 3

Data: 16/10/2026. Estado de mérito herdado da [Fase 2](../fase-2-consolidacao-dec-15.md),
sem nova ratificação. **O** execução em memória; **L** leitura; **R** recomendação. Procedimentos
e consultas preparados não são execução ou manifestação institucional.

## Matriz das oito pendências

| DEC-15 | Evidência produzida / fontes consultadas | Resultado e limite | Dependência e próxima ação recomendada | Responsável pela próxima decisão / encerramento |
|---|---|---|---|---|
| .01 | Dossiê técnico, JSON e reprodutor; `validation.py`, `retificacoes.py`, `periodo.py`; teste unitário do período cancelado executado | **O:** bloqueio no ato de publicação, ausência desse código na Retificação e troca de evento. Outros erros no snapshot mínimo; nenhuma publicação completa | Autorizar ambiente e persistência para três percursos do dossiê; depois decidir alcance contextual do impeditivo | Produto/Cefor: resultados observados por cenário, impacto em inscrições e aceite explícito. Impeditivo continua não ratificado |
| .06 | Dossiê dos três cenários; `elevacao.py`, `changes.py`, `mutabilidade.py`, `metodo.py`, `relacao.py`, `sorteio.py`; testes de elevação executados, integração de método somente lida | **O:** ausência não inventa método e REPLACE endereça método. **L:** método/hash congelados têm tratamento próprio; sem demonstração completa de conversão | Completar matriz por fase/ato, demonstração autorizada de B/C e manifestação administrativa; .09 não aprova .06 | Produto, comissão e autoridade competente: delimitação por cenário, restrições e nova ratificação |
| .07 | Git `0c3f0135`/`be700cba`; contrato/matriz 026, `changes.py`/`colecoes.py`; execução de correção de fundamento, versão, vigência e troca de ID em memória | **O:** três campos aceitos, ID recusado. **L:** origem técnica encontrada; aprovação humana histórica não encontrada. Sem substituição administrativa demonstrada | Mapear referências reais em ambiente sintético autorizado e pactuar exemplos de correção/substituição; manter ID provisório | Produto e setor normativo se aplicável: origem/limites documentados, cenários e vínculos completos, alternativa ratificada |
| .15 | Inventário de 34 colunas, template, erros e operações; `views.py`, `matriculas.html`, `exportar.py`, `colunas.py`, `lacuna.py`, `models.py`; testes de interface/geração somente lidos | **L:** prévia nominal gera `MATRICULA_PREVER`; geração tem registro próprio; não há confirmação de recebimento/importação. Sem acesso a dado real | Validar inventário com equipe/encarregado; executar GET/POST sintéticos somente com autorização da escrita de auditoria; deliberar política por operação | Produto, com encarregado: superfície/risco/cobertura aprovada e nova decisão sobre condição de auditoria |
| .04 | Consulta I-04 com seis situações; reaproveitamento de contexto da minuta jurídica e decisões R2 | Preparada, não enviada; nenhuma resposta; preservação de aceitas é orientação provisória, não transição ratificada | Usuário encaminhar a Cefor; coordenar com .05 e calendário; decidir vigência/publicidade/prazo | Cefor/autoridade do certame e produto: resposta às seis situações e ratificação posterior |
| .12 | Consulta I-12; minuta Cefor e 060 | Preparada, sem confirmação de competência; permissão técnica não demonstra autoridade administrativa | Usuário encaminhar; distinguir aprovador/operador e habilitar/alterar/revogar; articular DEC-04/02 | Cefor/setor competente: matriz ação/competência/fundamento/escopo/vigência e ratificação |
| .13 | Consulta I-13; minuta encarregado/Cefor, 029 e contexto de coleta/exportação 031 | Preparada por categoria e momento; sem resposta ou ratificação para certame real | Usuário encaminhar consulta conjunta; articular DEC-03/12 e necessidade normativa do edital | Cefor/encarregado, jurídico se remetido, produto: decisão por categoria e momento, bloqueio e condições de uso |
| .16 | Plano DEC-14 e ficha/protocolo propostos; roteiro assistido e critério existente da 072 | Sete dimensões explicitadas; dez minutos referência inicial; sem pactuação ou sessões | Nomear participantes; aprovar protocolo/ambiente/critérios antes de executar; não alterar retroativamente | Produto/observadores/representantes: protocolo prévio aprovado, depois resultados completos e aceite operacional |

## Limitações verificadas e decisões ainda necessárias

1. Os 11 testes executados não usam banco. Não demonstram triggers, privilégios, publicação,
   concorrência, escopo de acesso ou atendimento integral às condições ratificadas.
2. A fixture mínima da .01 gera outros impeditivos. “Sem `registration_period_cancelled`” não é
   “Retificação publicada”. A exceção para Retificação está comprovada no validador e no chamador,
   mas o percurso completo continua pendente.
3. O reprodutor .07 demonstra gramática/contrato, não licitude de corrigir fundamento ou substituir
   norma. Fundamento, identidade, versão e vigência continuam distintos.
4. O levantamento .15 é inspeção de código, sem captura de telas reais ou dados reais. Há inferência
   potencial por protocolo, população e pequenos grupos; registro de geração não comprova download.
5. Históricos Git identificam origem técnica, não aprovação humana não localizada.
6. Consultas são minutas, sem resposta; protocolo é proposta; nenhum responsável nominal foi designado.
7. Cenários persistentes exigem autorização específica e ambiente previamente preparado. Nenhuma
   migration, criação/remoção de banco, seed, alteração de dados ou exclusão autorizada nesta entrega.
8. Havendo lacuna funcional, registrar achado para novo escopo Spec Kit depois de decisão; não
   adaptar implementação, enfraquecer teste ou alterar spec para fazer cenário passar.

## Ordem de resolução proposta, sem início de implementação

| Ordem | Trabalho | Paralelismo/dependências | Aceite |
|---|---|---|---|
| 1 | Revisar e encaminhar I-13/I-12/I-04 pelo responsável humano | Podem tramitar em paralelo; compartilhar respostas DEC-03/04/12 sem duplicidade | Questões completas recebidas pelos setores e resposta competente registrada; envio não realizado pelo agente |
| 2 | Pactuar DEC-14/.16 e confirmar ambiente para demonstrações | Agenda/protocolo em paralelo às consultas; demonstrações aguardam autorização de persistência | Participantes, critérios e ambiente identificados; escopo de escrita aprovado sem atingir desenvolvimento |
| 3 | Executar .01 completo e .07 correção/substituição; .06 por fases; .15 por operação | Cenários isolados podem ser independentes; interpretação de efeitos depende de respostas institucionais | Evidências observadas, versões/atos e limites; nenhuma alteração funcional para obter sucesso |
| 4 | Nova deliberação por pendência | Dossiês + respostas + demonstrações; não ratificar pacote por silêncio | Alternativa e condições expressas por item, com competência e prova |
| 5 | Propor regularização e eventuais incrementos | Somente depois do mérito resolvido e autorização própria | Mapa decisão → spec/plano/tarefas/testes/documentação; execução e merge dependem de autorização futura |

Trilha de preservação GO-09/GO-47 permanece separada: esta instrução da DEC-15 não comprova revogação,
backup de vídeos ou bancos. Não a declarar encerrada por conclusão documental da Fase 3.

## Arquivos e revisão desta execução

Criados nesta pasta: `README.md`, `dossie-tecnico.md`, `dossie-institucional.md`,
`homologacao-e-protocolo.md`, `matriz-e-limitacoes.md`, `reproduzir-em-memoria.py`,
`resultado-em-memoria.json`. Nenhum arquivo funcional ou spec alterado.

Revisão: cobertura dos oito IDs, distinção O/L/H/R/D, resultados de testes e reprodutor, JSON
documental, caminhos de links e espaços finais. Revisão documental não equivale a homologação.

**FASE 3 — EVIDÊNCIAS PREPARADAS; DECISÕES PENDENTES DE RATIFICAÇÃO.**
