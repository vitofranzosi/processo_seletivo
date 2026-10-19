# Fase 2 — relatório de deliberação da DEC-15

> Estado atual após as quatro rodadas: consultar a [consolidação da DEC-15](fase-2-consolidacao-dec-15.md).
> A análise inicial e os avisos de continuidade abaixo são históricos; não substituem o registro
> das deliberações expressas posteriores.

> Atualização de 16/10/2026: a análise inicial abaixo foi preservada. O
> [registro da Rodada 1 e apresentação da Rodada 2](fase-2-rodadas-1-e-2.md) contém o estado
> posterior: DEC-15.14 ratificada somente quanto à separação da permissão; DEC-15.13,
> DEC-15.12 e DEC-15.15 com encaminhamentos aprovados, sem ratificação das regras.
> As declarações de ausência de ratificação abaixo descrevem o momento inicial da análise.

Data: 16/10/2026. Base local: `001-decisoes-pendentes` @ `6fc3a85a`.
**FASE 2 — DEC-15 ANALISADA, AGUARDANDO RATIFICAÇÃO HUMANA.**

Nenhuma decisão ratificada. Este relatório acrescenta análise documental; não altera a pauta da
Fase 1, especificações, funcionalidades ou Constituição. Autorizar a análise não aprova seu mérito.

## 1. Fontes, método e limites

Consultados: [README da Fase 1](README.md), [matriz](matriz-decisoes.md),
[pauta](pauta-dec-15.md), [plano e revisão](plano-e-revisao.md),
[Constituição vigente](../../.specify/memory/constitution.md),
[matriz histórica](../auditoria-de-consolidacao-2026-10-15/matriz-pendencias.md),
[rastreabilidade histórica](../auditoria-de-consolidacao-2026-10-15/rastreabilidade-historica.md),
specs e trechos de implementação relacionados abaixo. Histórico Git lido sem alterar refs.

Princípios aplicados: identidade e integridade do domínio (I); imutabilidade e temporalidade (II);
permissão explícita, minimização e auditoria (III); regras e consequências explícitas (IV);
rastreabilidade (V); demonstração pelo canal do ator (VI). Alternativa que viole essas garantias
não pode ser adotada como mera decisão de produto. Nenhuma emenda constitucional é proposta.

A atribuição histórica de decisão ao agente vem dos registros da auditoria, não da reabertura de
todas as conversas originais. Código e spec comprovam comportamento/contrato, não aprovação humana.
Ausência de aprovação localizada não demonstra que nunca houve manifestação em outro canal.

Foram detalhados os **13 itens da pauta inicial**, mais **duas decisões implementadas da AV-09**
omitidas naquela pauta. Uma **proposta de método de homologação**, GO-31, fica separada como
DEC-15.16: não é regra funcional já implementada. Não se afirma inventário exaustivo de toda escolha
feita desde o início do projeto; este é o conjunto identificado nas fontes obrigatórias e registros
correlatos consultados. Ideias exploratórias e validações em aberto não se tornam regras aprovadas.

## 2. Classificação e ordem proposta

Categorias: **P** ratificação possível pelo produto; **C** manifestação do Cefor;
**J** manifestação jurídica/normativa; **U** validação operacional com usuários;
**T** esclarecimento técnico adicional. Categorias podem coexistir. P não autoriza o produto a
substituir manifestação institucional sobre competência, tratamento de dados ou efeitos normativos.

| Ordem / rodada | Item | Prioridade de deliberação | Classificação | Motivo / dependência | Complexidade de eventual revisão |
|---|---|---|---|---|---|
| 1 / R1 | DEC-15.13 — Requerimento obrigatório | Alta | C, J, U; produto após parecer | Bloqueia inscrição e antecipa coleta; DEC-03/12 | Média/alta: portal, submissão, coleta, specs e testes |
| 2 / R1 | DEC-15.12 — Habilitação de autoridade | Alta | C, J | Competência do ato; DEC-04 | Alta se substituir modelo por hierarquia; menor se apenas formalizar rito |
| 3 / R1 | DEC-15.14 — Papel exportador | Alta | P, C, U | Acesso em lote; concessão institucional ligada à DEC-02 | Baixa/média para mapa; maior para integração institucional |
| 4 / R1 | DEC-15.15 — Auditoria da prévia | Alta | P, T; encarregado se necessário | Acesso nominal e trilha; DEC-03 | Média: eventos, minimização e cobertura |
| 5 / R2 | DEC-15.02 — Operação de pontuação | Alta | P, J, U | Resultado calculado; preservar obsolescência e revisão | Alta para restrições temporais ou sucessão de resultados |
| 6 / R2 | DEC-15.03 — Normalização de pontuação | Alta | P, J, U | Mesma cadeia da operação; deliberar com .02 | Alta pelo efeito nos cálculos |
| 7 / R2 | DEC-15.06 — Método de sorteio ausente | Alta | T, C, J, U | Separar compatibilidade histórica de conversão de método | Média/alta: vigência, relação e sucessores |
| 8 / R2 | DEC-15.04 — Teto de inscrições | Alta | P, J, U | Admissão futura e preservação das anteriores | Média/alta para transição condicional |
| 9 / R3 | DEC-15.05 — Evento de inscrições | Alta | P, C, U; J se efeitos retroativos | Define janela de recebimento | Média: cronograma, recebimento e versões |
| 10 / R3 | DEC-15.01 — Período cancelado impedir publicação | Média | P, C, U | Não confundir bloquear recebimento com impedir publicar | Baixa/média para severidade; validar jornada de retificação |
| 11 / R3 | DEC-15.08 — Coerência do código transversal | Média | P, U | Documentos exigidos e abrangência entre Perfis | Média se ampliar bloqueio; efeito em retificações antigas |
| 12 / R3 | DEC-15.09 — Habilitação no PDF | Média | P, C, U | Explicita universo de sorteio; conferir correspondência | Baixa para redação, alta se mudar universo |
| 13 / R4 | DEC-15.10 — Chave documental estável | Média | P, T | Integridade dos documentos já enviados; DEC-07 não se resolve aqui | Alta para remapeamento; baixa para ratificar estabilidade |
| 14 / R4 | DEC-15.11 — Unidades por implantação | Média | P, C, U | Responsabilidade editorial e operacional | Média/alta para tela e papel central |
| 15 / R4 | DEC-15.07 — Identidade da regra normativa | Média | T, depois P; J se mudar fundamento | Corrigir atribuição histórica antes de deliberar mérito | Alta se tentar trocar identidade em uso |
| 16 / R4 | DEC-15.16 — Ajuda em homologação | Baixa para produto; alta antes do ensaio | P, U | Método de medição, depende de DEC-14 | Baixa documental; pode invalidar comparação se aplicada depois |

A ordem considera risco de inscrição/coleta/competência primeiro, classificação em seguida, depois
cronograma/documentos e governança técnica. Recursos e convocação podem consumir resultados
afetados, mas nenhum item desta lista autoriza mudar seus prazos, decisões ou atos já emitidos.
CA-23 e a reabilitação DEC-08 continuam decisões próprias; não são resolvidas por esta ratificação.
Consultas podem ser preparadas em paralelo; implementação e Fase 3 permanecem fora desta execução.

## 3. Questões detalhadas

### DEC-15.13 — Requerimento enviado como condição da inscrição

**Funcionalidade e regra atual:** inscrição e Requerimento de Matrícula. Quando o Edital declara
Requerimento na inscrição, FR-372 da 029 exige que esteja enviado para submeter a inscrição.
`inscricoes/application/submissao.py` chama a verificação e recusa o envio incompleto.

**Origem/evidência:** [029, FR-372](../../specs/029-requerimento-de-matricula/spec.md), CA-07 e
linha 36 da rastreabilidade; sessões `de544cbf`/`8f427c86`, PR #123. Auditoria registra alternativa
oferecida pelo agente sem resposta. Não confundir decisões expressas sobre campos com este bloqueio.

**Alternativas:** A manter e ratificar bloqueio/coleta; B propor requerimento sem bloquear inscrição;
C manter sem ratificar até manifestação conjunta do Cefor/encarregado, com questões jurídicas
encaminhadas ao setor competente. Desaconselhar coleta na composição é medida adicional, não resolve
por si a necessidade e finalidade de cada campo.

**Impactos:** o candidato preenche mais dados antes de concorrer; em sorteio, inclusive quem não será
convocado. A revisão pode deslocar a conferência para matrícula/convocação e mudar a rotina do setor.
**Risco de manter:** barreira de inscrição e coleta antecipada sem fundamento institucional confirmado.
**Risco de modificar:** admitir inscrição sem documento exigido pelo ato ou deixar matrícula incompleta.
**Recomendação:** C; decidir necessidade/momento com instituição antes de ratificar ou retirar bloqueio.
Fundamento técnico: minimização e correspondência com conteúdo publicado, sem inferir base legal.
**Pergunta:** confirma o encaminhamento conjunto (C), mantendo esta regra sem ratificação até resposta?

### DEC-15.12 — Autoridade como habilitação na unidade

**Funcionalidade e regra atual:** publicação e cadastro de autoridades. D-003 da 060 registra por
quais unidades uma pessoa pode responder, sem inferir competência por lotação ou hierarquia.
Reitor habilitado em várias unidades tem registros por unidade; a delegação é registrada, não interpretada.

**Origem/evidência:** [060, D-003](../../specs/060-unidades-e-autoridades/spec.md), ED-47/lote 09.
O modelo é documentado, mas não há aprovação expressa localizada desta escolha. A clarificação que
atribui manutenção ao Gestor da unidade é decisão distinta e não será reaberta automaticamente.

**Alternativas:** A ratificar modelo explícito, com Cefor confirmando competência e rito; B propor
modelo central/hierárquico após desenho institucional; C aguardar Cefor e orientação normativa antes
da ratificação. **Impactos:** exige manutenção de habilitações e vigências por unidade; evita
deduzir competência pelo cargo. **Risco de manter:** cadastro incorreto pode representar autoridade
indevida se o rito humano não conferir fundamento. **Risco de modificar:** herança automática pode
conceder competência não demonstrada e reinterpretar vínculos históricos.
**Recomendação:** C para ratificação institucional, preservando o modelo explícito enquanto se consulta;
nenhuma inferência automática de competência. **Pergunta:** confirma consultar o Cefor sobre D-003,
com fundamento normativo quando necessário, sem ratificar competência apenas pelo produto?

### DEC-15.14 — Papel próprio de exportador de matrículas

**Funcionalidade e regra atual:** exportação de dados de matrícula em lote. FR-455 exige permissão
`matricula:exportar`; o mapa de identidade local cria papel `exportador` com essa permissão, sem
acrescentá-la automaticamente aos papéis existentes. Permissão e papel são decisões diferentes.

**Origem/evidência:** AV-09; L07-14/L07-17, PRs #125/#127/#130/#155;
[031](../../specs/031-exportacao-de-matriculas/spec.md), FR-455;
`backend/processo_seletivo/interface/identidade.py`, chave `exportador`.
Este item foi omitido da pauta de 13 linhas; não foi ratificado nesta ampliação.

**Alternativas:** A ratificar papel separado e concessão explícita; B atribuir a papel existente,
com autorização e escopo definidos; C pedir definição operacional Cefor/RA antes da escolha.
**Impactos:** distingue leitura individual de retirada de conjunto com dados pessoais. Exige
designar quem exporta; login institucional e concessão real continuam pendentes.
**Risco de manter:** setor pode não conseguir exportar se ninguém receber a permissão; papel local
pode ser confundido com concessão institucional já pronta. **Risco de modificar:** ampliar acesso a
dados em lote por simples acúmulo de funções. **Recomendação:** A para desenho de produto, com Cefor
definindo destinatários e TI realizando concessão futura; não ratifica importação no RA.
**Pergunta:** ratifica papel separado de exportador, sem concessão automática aos demais papéis (A)?

### DEC-15.15 — Auditar prévia de exportação somente quando nomeia pessoas

**Funcionalidade e regra atual:** conferência antes de gerar planilha. Toda geração possui registro;
a prévia registra evento adicional somente se `composicao.nomeia_pessoas` for verdadeiro, calculado
pela existência de pessoas no relatório de lacunas. O evento referencia contexto e não copia os dados.

**Origem/evidência:** AV-09, mesmas sessões e PRs da .14; `matriculas/application/exportar.py`,
propriedade `nomeia_pessoas`; `interface/views.py`, condição antes de `record_event`.
A auditoria identifica esta política como escolha do agente, não aprovação institucional.

**Alternativas:** A ratificar política condicional após confirmar toda a superfície exposta; B propor
auditoria de toda prévia, sem conteúdo pessoal; C esclarecer tecnicamente os dados visíveis em cada
cenário antes de decidir A/B. **Impactos:** rastreabilidade de acesso versus volume de eventos;
não confundir arquivo gerado com consulta anterior. **Risco de manter:** indicador pode não cobrir
todas as formas de exposição nominal ou sensível. **Risco de modificar:** eventos excessivos, custo
operacional e duplicação de informação se desenhados sem minimização.
**Recomendação:** C; o código confirma a condição, mas não comprova por si cobertura de todas as telas.
Depois, submeter a política ao responsável e ao encarregado quando pertinente.
**Pergunta:** confirma esclarecer os dados expostos em cada prévia antes de ratificar a condição (C)?

### DEC-15.02 — Retificar operação de combinação de pontuações

**Funcionalidade e regra atual:** classificação. `classificationMilestones/operation` é retificável;
alteração da regra pode tornar ordem existente obsoleta e recomputável, preservando o ato anterior.
Não significa autorização de recalcular e substituir silenciosamente resultado divulgado.

**Origem/evidência:** ED-47, L05-67, `ae3ad7c8`; [026, matriz](../../specs/026-contrato-de-mutabilidade-normativa/matriz.md),
linha `operation`; comentário do contrato em `editais/domain/mutabilidade.py` aponta a 015 e testes
de cálculo. Commit `1d721b93` restaurou retificabilidade na revisão #114, em vez de criar capacidade
do zero. Não há ratificação humana expressa localizada para essa restauração específica.

**Alternativas:** A ratificar capacidade por Retificação, preservando versões e sucessões; B propor
restrições por fase/ato; C vedar novas alterações, sujeito a revisão constitucional e domínio.
**Impactos:** mudar combinação pode alterar posições, cortes e efeitos subsequentes de recursos e
convocação. **Risco de manter:** operador pode subestimar necessidade de revisar atos dependentes.
**Risco de modificar:** impedir correção normativa legítima ou divergir de capacidades anteriores.
**Recomendação:** A no mérito técnico; casos de aplicação a certame em curso exigem enquadramento
institucional e validação operacional. B precisa de regra temporal própria, não de bloqueio improvisado.
**Pergunta:** ratifica a capacidade técnica de retificar operação com obsolescência explícita (A),
sem aprovar automaticamente sua aplicação a qualquer fase do certame?

### DEC-15.03 — Retificar normalização das pontuações

**Funcionalidade e regra atual:** classificação; `classificationMilestones/normalization` é
retificável. Trata de **pontuações**, não da normalização de números da fonte do sorteio.

**Origem/evidência:** ED-47, L05-67 e `1d721b93`; matriz da 026 e comentário junto de `operation`
em `mutabilidade.py`, que a vincula à regra anterior da 015 e ao tratamento de obsolescência.
**Alternativas:** A ratificar capacidade com versionamento e revisão de dependentes; B restringir
por fases definidas; C suspender ratificação até demonstração conjunta de .02/.03.
**Impactos:** pode mudar pontuações comparáveis e classificação; efeitos chegam a cortes e atos
dependentes. **Risco de manter:** impacto pouco visível ao operador; **risco de modificar:** congelar
erro de cálculo ou retirar capacidade prevista sem rito substituto.
**Recomendação:** A, com demonstração operacional conjunta com .02 e enquadramento normativo quando
afetar atos de certame; não acrescentar restrição temporal por inferência técnica.
**Pergunta:** ratifica retificabilidade da normalização de pontuações com preservação dos atos (A)?

### DEC-15.06 — Declarar método de sorteio por Retificação quando ausente

**Funcionalidade e regra atual:** método do marco; o contrato permite que `drawMethod` passe de
ausente a declarado por Retificação, com método completo e validação de publicação.

**Origem/evidência:** ED-47, L05-67; matriz da 026 e `1d721b93`; contrato de objeto ausente em
`mutabilidade.py` remete à 021 e ao caso de elevação de conteúdo anterior ao degrau 10, que contém
método nulo. Capacidade histórica não prova autorização para transformar qualquer seleção calculada
em sorteada depois de atos praticados.

**Alternativas:** A ratificar permissão geral atual; B ratificar somente o caso de compatibilidade
histórica, após conferir se o sistema consegue distingui-lo; C esclarecer cenários e efeitos antes
da ratificação. **Impactos:** pode definir universo, algoritmo e rito de classificação, afetando
relação e sucessões de sorteio. **Risco de manter:** interpretar compatibilidade como liberdade de
troca de espécie em qualquer fase. **Risco de modificar:** tornar acervo antigo incapaz de declarar
método e criar bloqueio sem migração normativa válida.
**Recomendação:** C; separar ausência histórica e mudança da espécie/rito. Validação com comissão e
manifestação normativa antes de autorizar efeitos em certame real.
**Pergunta:** confirma esclarecer esses dois cenários antes de ratificar alcance da permissão (C)?

### DEC-15.04 — Retificar teto de inscrições por candidato

**Funcionalidade e regra atual:** `maxInscricoesPorCandidato` é retificável; registros e testes
referidos pela matriz preservam inscrições já submetidas quando o teto diminui.
O efeito sobre todos os cenários de candidaturas futuras não foi reensaiado nesta análise.

**Origem/evidência:** ED-47, L05-67; matriz 026, linha restaurada em `1d721b93`, aponta
`test_fatos_congelados`; contrato de raiz em `mutabilidade.py`.
**Alternativas:** A ratificar retificabilidade com preservação das anteriores; B restringir aumento/
redução por fase, após regra institucional; C consultar sobre transição antes de ratificar alcance.
**Impactos:** altera quantas novas inscrições uma pessoa pode enviar; pode mudar oportunidades ao
longo do prazo. **Risco de manter:** regra temporal percebida como desigual ou efeito futuro mal
compreendido. **Risco de modificar:** invalidar indevidamente inscrições aceitas ou impedir correção.
**Recomendação:** C quanto à transição administrativa; preservar obrigatoriamente o histórico.
Não deduzir que inscrição preservada resolve toda questão de tratamento das futuras.
**Pergunta:** confirma consultar a regra de transição, sem ratificar agora redução/aumento irrestritos (C)?

### DEC-15.05 — Retificar qual Evento é o período de inscrições

**Funcionalidade e regra atual:** cronograma e recebimento. `schedule/isRegistrationPeriod` é
retificável; contrato exige conteúdo consistente, sem equivaler a edição livre de inscrições passadas.

**Origem/evidência:** ED-47; matriz 026, restauração `1d721b93`, cita decisão anterior da 009 e
`test_contrato_de_inscricao`; contrato em `mutabilidade.py`.
**Alternativas:** A ratificar designação por Retificação com validações; B limitar por fase após
definir exceções; C esclarecer caso operacional antes. **Impactos:** trocar evento pode alterar
janela que aceita envios e comunicação do calendário. **Risco de manter:** reabertura/fechamento com
efeitos não compreendidos. **Risco de modificar:** sem caminho para corrigir evento mal designado.
**Recomendação:** A para capacidade, validando com setor cenários de reabertura e sem reescrever
instantes ou inscrições anteriores; efeitos normativos específicos dependem de decisão competente.
**Pergunta:** ratifica corrigir designação por Retificação validada, preservando histórico (A)?

### DEC-15.01 — Período CANCELADO impedir publicação

**Funcionalidade e regra atual:** validação da publicação. Se o único evento designado estiver
cancelado, `validation.py` emite impeditivo `registration_period_cancelled`. A decisão de fechar
recebimento por cancelamento é distinta de impedir que o ato seja publicado.

**Origem/evidência:** ED-47, L08-58, `628c5ea1`, #221; teste
`backend/tests/unit/editais/test_publicacao_com_periodo_cancelado.py` e mensagem da validação.
**Alternativas:** A ratificar impeditivo geral; B propor distinção entre primeira publicação e
retificação de cancelamento; C analisar cenários antes de escolher severidade.
**Impactos:** evita edital inicialmente incapaz de receber inscrições, mas pode alcançar ato de
retificação que deva formalizar cancelamento. **Risco de manter:** bloquear ato legítimo dependendo
do contexto de aplicação. **Risco de modificar:** permitir publicação incoerente que não recebe inscrições.
**Recomendação:** C, demonstrando primeira publicação e retificação de cancelamento ao setor.
A regra atual foi lida, mas esses percursos não foram reexecutados; não afirmar que exceção existe.
**Pergunta:** confirma analisar os dois percursos antes de ratificar o impeditivo geral (C)?

### DEC-15.08 — Coerência de denominação só para código transversal

**Funcionalidade e regra atual:** documentos por modalidade entre Perfis. A 044 bloqueia denominações
divergentes do mesmo código quando usado por documento transversal; não exige coerência universal
de todos os códigos repetidos em Perfis independentes.

**Origem/evidência:** [044, D1 e D-001](../../specs/044-recorte-transversal-documental/spec.md);
ED-47, L08-01, `6fefec8a`; `validation.py`, `_denominacoes_do_codigo`.
D1 foi registrado como decisão humana mais ampla; D-001 é interpretação restritiva atribuída ao agente.
**Alternativas:** A ratificar recorte ao uso transversal; B exigir coerência universal; C aviso
universal com impeditivo somente no uso. **Impactos:** determina se Perfis independentes podem
reutilizar código com significado diferente. **Risco de manter:** confusão em leituras humanas ou
rotinas que pressuponham catálogo global. **Risco de modificar:** bloquear retificações de editais
antigos por identidade que nunca declararam entre Perfis.
**Recomendação:** A; o domínio só precisa equivalência onde o edital afirma alcance transversal.
Validar com elaboradores que códigos independentes não são apresentados como identidade global.
**Pergunta:** ratifica limitar coerência obrigatória aos códigos usados transversalmente (A)?

### DEC-15.09 — Linha de habilitação ao sorteio no PDF

**Funcionalidade e regra atual:** PDF imprime universo do sorteio. `_habilitacao_ao_sorteio` lê o
método que governa; sem etapa habilitante informa todas as inscrições submetidas; com etapa válida,
apenas as habilitadas nela. Referência não resolvida não é convertida em “todas”.

**Origem/evidência:** ED-47, L08-51, `233e8b36`, 054; função e linha “Habilitação” em
`publicacoes/infrastructure/pdf.py`. Ausência de requisito específico não autoriza inventar universo.
**Alternativas:** A ratificar explicitação fiel; B retirar linha e depender de outro trecho aprovado;
C revisar frase com comissão antes de ratificar. **Impactos:** torna visível quem entra no sorteio.
**Risco de manter:** frase pode ser tomada como norma nova se divergir de relação/etapas efetivas.
**Risco de modificar:** ocultar alcance do sorteio em documento oficial.
**Recomendação:** A para apresentação derivada, com conferência operacional de equivalência ao universo
real antes de aceite; não ratificar novo critério de habilitação por esse texto.
**Pergunta:** ratifica mostrar habilitação já declarada, sem criar regra de participação (A)?

### DEC-15.10 — Chave do documento exigido não editável

**Funcionalidade e regra atual:** documentos e vínculos de arquivos enviados. `documentRequirements/key`
é não retificável; nome/instruções são campos distintos e retificáveis.

**Origem/evidência:** ED-47, E2E-004/lote 03; [026, matriz](../../specs/026-contrato-de-mutabilidade-normativa/matriz.md),
seção documental; razão em `mutabilidade.py`: chave liga o exigido ao arquivo já enviado.
**Alternativas:** A ratificar estabilidade da chave; B propor alteração com remapeamento versionado;
C esclarecer caso concreto de correção que nome/instruções não atendem.
**Impactos:** protege rastreabilidade documental; limita correção de identificador mal escolhido.
**Risco de manter:** chave errada exige rito distinto, ainda não definido, em vez de correção simples.
**Risco de modificar:** desligar documentos enviados ou atribuí-los a exigência diferente.
**Recomendação:** A; eventual remapeamento é incremento próprio e não pode mudar o sentido histórico.
Isso não decide inclusão/remoção de exigência, pendente na DEC-07.
**Pergunta:** ratifica chave estável, corrigindo apresentação por nome/instruções (A)?

### DEC-15.11 — Registro de unidades pela implantação, sem tela

**Funcionalidade e regra atual:** unidades e cabeçalhos institucionais. D-002 da 060 prevê registro
versionado mantido pela implantação, sincronizado a partir de `unidades.json`; não há tela central.

**Origem/evidência:** [060, D-002](../../specs/060-unidades-e-autoridades/spec.md), ED-47/lote 09;
`backend/processo_seletivo/unidades/unidades.json` e procedimento documentado de sincronização.
**Alternativas:** A ratificar manutenção versionada com responsável editorial; B propor tela e papel
central; C validar rotina antes. **Impactos:** mudança de cabeçalho depende de implantação e revisão
de diff; autoridades continuam com gestão própria, não passam a arquivo por esta decisão.
**Risco de manter:** demora e dependência técnica para correção editorial.
**Risco de modificar:** ampliar acesso a dado institucional sem papel central e perder revisão.
**Recomendação:** A, com Cefor aprovando conteúdo e implantação aplicando; testar fluxo com responsáveis
antes da operação. Não atribuir competência editorial à TI por presunção.
**Pergunta:** ratifica catálogo versionado sem tela, com aprovação editorial do Cefor (A)?

### DEC-15.07 — Identificador da regra normativa como estrutural

**Funcionalidade e regra atual:** identidade do fundamento da modalidade. `normativeRule/id` é
estrutural; fundamento, versão e vigência têm tratamento próprio, não se confundem com troca do ID.

**Origem/evidência:** ED-47 menciona seis reclassificações. Conferência do histórico da matriz
encontrou a linha já como **E** na adição em `0c3f0135`; a emenda `1d721b93` enumera cinco
restaurações e não inclui este ID. Isso corrige a leitura da pauta: não foi demonstrada uma sexta
reclassificação na mesma revisão. Permanece questão de atribuição/ratificação de identidade.
**Alternativas:** A ratificar estabilidade; B propor troca versionada com integridade comprovada;
C esclarecer decisão histórica e caso de uso antes de deliberar.
**Impactos:** distingue corrigir conteúdo e trocar identidade normativa.
**Risco de manter:** eventual erro de vinculação sem rito claro de correção.
**Risco de modificar:** quebrar proveniência ou sugerir mesma norma onde há outra.
**Recomendação:** C quanto à atribuição histórica; tecnicamente preservar identidade estável.
Não recomendar liberar troca de ID nem ampliar bloqueio de outros campos.
**Pergunta:** confirma esclarecer a origem e o caso concreto antes de ratificar uma suposta sexta reclassificação (C)?

### DEC-15.16 — Intervenção após dez minutos em teste operacional

**Funcionalidade afetada:** método de homologação, não regra funcional implementada.
**Regra especificada/proposta:** roteiro sugere, após dez minutos sem avanço, oferecer seguir/parar;
se persistir dificuldade, ajuda mínima registrada e etapa fora da comparação com estimativa.

**Origem/evidência:** GO-31 e [roteiro assistido](../roteiro-teste-operacional-assistido-28-2026.md),
§2.1, que diz expressamente ser proposta sem decisão da DP-18.
**Alternativas:** A aprovar método proposto; B encerrar tarefa sem ajuda; C acordar protocolo com
observadores e usuários antes da sessão. **Impactos:** muda interpretação de conclusão autônoma e
comparação de tempo. **Risco de manter sem aprovar:** observadores aplicarem métodos diferentes.
**Risco de modificar após ensaio:** perder comparabilidade ou induzir conclusão artificial.
**Recomendação:** C; definir previamente e registrar toda intervenção, sem mudar métricas após ver resultado.
**Pergunta:** confirma pactuar protocolo na DEC-14 antes das sessões (C), sem considerá-lo regra já ratificada?

## 4. Como deliberar sem aprovar implementação

Cada resposta deve citar identificador e alternativa. Pode ratificar o mérito, pedir evidência,
encaminhar ao setor competente ou adiar com condição de retomada. “Concordo com a análise” não será
interpretado como aprovação de todas as regras. Resposta coletiva só vale se indicar os itens e o
alcance expressamente. Sem resposta, todos continuam pendentes.

Nas opções de consulta/esclarecimento, a aprovação é **do encaminhamento**, não da regra atual.
Nas opções A de ratificação, registrar limites e dependências em separado; não declarar homologação.
Nenhuma resposta desta rodada implica autorização para modificar specs, código ou executar Fase 3.

Registro por item após resposta: alternativa; alcance; fundamento; responsável e competência;
data; evidência da fala humana; consultas/validações pendentes; autorização de implementação
(nesta fase: inexistente). Este relatório deixa todos esses campos sem ratificação.

## 5. Rodada apresentada agora — R1

1. **DEC-15.13:** A ratificar bloqueio; B propor retirada; **C consultar Cefor/encarregado antes**.
   Recomendação: **C**, sem alterar regra enquanto pendente.
2. **DEC-15.12:** A ratificar modelo com confirmação institucional; B propor hierarquia;
   **C consultar Cefor antes da ratificação**. Recomendação: **C**.
3. **DEC-15.14:** **A papel exportador separado**; B permissão em papel existente; C validar rotina
   antes de escolher. Recomendação: **A**, com concessão institucional explícita ainda pendente.
4. **DEC-15.15:** A auditoria condicional atual; B auditar toda prévia; **C esclarecer cobertura dos
   dados exibidos antes**. Recomendação: **C**.

As rodadas R2 a R4 ficam preparadas para apresentação posterior, após a resposta à R1. As perguntas
detalhadas estão disponíveis para inspeção, sem exigir dezesseis decisões simultâneas.

## 6. Verificação e limites da execução

Somente este relatório foi acrescentado pela Fase 2. Documentos da Fase 1 preservados, inclusive
eventuais imprecisões históricas, com esclarecimentos registrados aqui. Não houve execução de
testes de produto, acesso a banco, migrations, chamadas pagas, alterações de refs ou envio externo.
Leitura de código não comprova homologação, cobertura integral de cenários ou conclusão jurídica.

**FASE 2 — DEC-15 ANALISADA, AGUARDANDO RATIFICAÇÃO HUMANA.**
