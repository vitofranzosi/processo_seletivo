# DEC-15 — pauta de ratificação individual

Proposta de 16/10/2026. Nenhuma linha está aprovada. Fonte principal:
[ED-47](../auditoria-de-consolidacao-2026-10-15/matriz-pendencias.md#ed-47) e
[rastreabilidade histórica](../auditoria-de-consolidacao-2026-10-15/rastreabilidade-historica.md).
A frase histórica de que merge implica aceitação tácita não atende ao critério de aprovação
expressa desta fase. Não se pede ratificação em bloco.

As evidências abaixo são localizadores documentais: algumas derivam de digestos de sessões,
com confiança média indicada pela auditoria. Não são transcrições primárias reabertas nesta fase.
Quando a autoridade ou o contexto não bastarem, escolher **solicitar evidência**, sem presumir aceite.

Opções por linha: **manter e ratificar**, **rever mediante escopo futuro**, **solicitar evidência**
ou **adiar expressamente**. Rever não autoriza apagar atos históricos nem mudar código nesta fase.

| Item da pauta | Escolha atribuída ao agente / pergunta para deliberação | Evidência e ressalva | Impacto / interlocutor | Estado |
|---|---|---|---|---|
| DEC-15.01 | Período CANCELADO impedir publicação (`registration_period_cancelled`), além de fechar recebimento | ED-47; L08-58, sessão `628c5ea1`, 28/09; #221. Auditoria distingue decisão do usuário de escolha do impeditivo | Validação de publicação; produto e setor de seleção | Aguardando decisão |
| DEC-15.02 | Reclassificação de `operation` na matriz da 026 | ED-47; L05-67, `ae3ad7c8`, 13/09; `doc/decisao-mutabilidade-normativa.md`, seção sobre revisão do #114 | Mutabilidade da regra classificatória; produto | Aguardando decisão |
| DEC-15.03 | Reclassificação de `normalization` | Mesmas fontes; conferir decisão anterior escrita e testada antes de ratificar leitura da revisão | Método e normalização do sorteio; produto/comissão | Aguardando decisão |
| DEC-15.04 | Reclassificação de `maxInscricoesPorCandidato` | Mesmas fontes; alteração descrita como restauração de decisão anterior, sem ratificação nova explícita | Limite de inscrições; produto | Aguardando decisão |
| DEC-15.05 | Reclassificação de `isRegistrationPeriod` | Mesmas fontes; distinguir decisão anterior e mudança de contrato | Evento de inscrições; produto | Aguardando decisão |
| DEC-15.06 | Nascimento de `drawMethod` por Retificação | Mesmas fontes; documento de mutabilidade explica acervo anterior ao degrau 10 | Método do sorteio e efeitos temporais; produto/comissão | Aguardando decisão |
| DEC-15.07 | Reclassificação de `normativeRule/id` | ED-47 inclui esta sexta linha; documento de mutabilidade menciona cinco. Há diferença de contagem/escopo a esclarecer, sem concluir erro de produto | Identidade normativa; produto; solicitar contexto do PR #114 | Aguardando decisão/evidência |
| DEC-15.08 | Restringir “mesmo código, mesma denominação” da D-001 da 044 aos códigos transversais | ED-47; L08-01, `6fefec8a`, 25/09; pergunta registrada duas vezes | Documento exigido e recorte; produto | Aguardando decisão |
| DEC-15.09 | Linha “Habilitação” do sorteio no PDF sem requisito funcional específico | ED-47; L08-51, `233e8b36`, 28/09; 054 | Documento oficial; produto e setor de publicação | Aguardando decisão |
| DEC-15.10 | `key` de documento exigido não editável | ED-47; lote 03 §4, E2E-004; auditoria não traz aprovação expressa | Identidade documental e retificação; produto | Aguardando decisão/evidência |
| DEC-15.11 | D-002 da 060: unidades mantidas pela implantação, sem tela de gestão | Spec 060, D-002 e texto “Quem mantém”; ED-47, lote 09 §4 | Administração de unidades; produto/TI | Aguardando decisão |
| DEC-15.12 | D-003 da 060: autoridade como habilitação na unidade, e limites desse registro | Spec 060, D-003; ED-47. Não confundir com a clarificação expressa que atribui ao Gestor a manutenção das autoridades | Competência e dados da autoridade; Cefor/produto | Aguardando decisão |
| DEC-15.13 | FR-372 da 029: Requerimento “na inscrição” bloquear envio | Spec 029, FR-372; rastreabilidade histórica linha 36, sessões `de544cbf`/`8f427c86`; CA-07 e DEC-12 | Coleta de dados e inscrição; produto/Cefor/encarregado | Aguardando decisão |

## Condução

1. Conferir a regra atual e a evidência anterior de cada linha, sem editar o sistema.
2. Separar mérito normativo, forma de tela e escolha técnica. Encaminhar ao setor competente quando
   a decisão não couber ao produto.
3. Registrar opção, fundamento, autor, competência, data e evidência por linha.
4. Se houver revisão, preparar incremento rastreável apenas após autorização específica.
5. Encerrar DEC-15 quando todas as linhas tiverem destino explícito; itens adiados permanecem
   pendências próprias, com responsável e condição de retomada.

## Fora desta ratificação

Não reabrir automaticamente decisões expressas já existentes, como a manutenção de autoridades
pelo Gestor da unidade (clarificação de 06/10 da 060), oficialidade do PDF e escolhas da 072.
Não incluir ideias exploratórias (Ifes Ads, Libras) como funcionalidades aprovadas.
