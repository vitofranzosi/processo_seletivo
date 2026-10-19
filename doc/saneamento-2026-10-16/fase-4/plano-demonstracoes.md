# Plano controlado das demonstrações — não executar nesta fase

Versão 1, 16/10/2026. Pendências: DEC-15.01, .06, .07 e .15. Autorização proposta em
[documento próprio](proposta-autorizacao.md); nenhum ato persistente foi produzido pela Fase 4.

## Contrato comum dos cenários

Cada linha da seção seguinte herda explicitamente os itens C1–C7 abaixo; objetivo, estado, dados,
operações, resultado e evidência específicos aparecem em sua linha. Isso não dispensa aprovação
do cenário e do ambiente antes da execução.

- **C1 — ambiente:** somente o ambiente exato proposto no documento de autorização, com manifesto
  confirmado. PostgreSQL isolado, esquema previamente preparado e mídia sintética exclusiva.
  Não criar/migrar banco por comando de teste. Se não houver baseline autorizada, interromper.
- **C2 — dados:** IDs sintéticos distintos por cenário; Editais “HOMOLOGAÇÃO — SEM VALOR OFICIAL”;
  atores/unidades/autoridades fictícios e documentos assim marcados. Nenhuma carga do desenvolvimento.
  T0 é instante real registrado da execução, datas de janela relativas; não retroagir ato real.
- **C3 — leitura/escrita:** GET pode gravar auditoria (.15). Leitura de bytes/estado e aplicação
  pura em memória ficam separadas de API/browser com banco. Usar permissões explícitas e segregação;
  não desabilitar triggers, constraints ou privilégios. Nenhuma edição SQL corretiva.
- **C4 — atos:** publicações e sucessores são registros sintéticos de demonstração em ambiente
  privado, sem valor de ato oficial, sem exposição a candidatos reais. Preservar versões e trilha.
  Autoria, horário, correlação, ato anterior e posterior, achados e versão do código em cada ficha.
- **C5 — evidência/aprovação:** guardar esperado e observado separados, capturas sanitizadas do
  produto, caminhos/IDs/hashes e contagem de registros antes/depois. Aprovação técnica significa
  comportamento conhecido e íntegro, não licitude de ato nem ratificação. Divergência vira achado,
  nunca motivo para alterar código/spec. Aceite por produto e revisor do cenário.
- **C6 — recuperação:** pausar ações; desativar acesso do ensaio e parar apenas serviços isolados
  autorizados, mantendo volumes, logs e evidências. Não apagar, truncar, sobrescrever, desfazer
  publicação ou restaurar sobre estado existente. Nova tentativa usa cenário/namespace novo.
  Restauração em volume novo ou descarte demandam autorização própria e revisão do alvo absoluto.
- **C7 — riscos/contenção:** impedir rede externa, e-mail e inferência; interromper se destino não
  corresponder ao manifesto, surgir dado real, ato escapar do namespace ou falhar preservação.
  Limites do cenário e do orçamento de registros estão na proposta. Não usar banco de filmagem.

## DEC-15.01 — três cenários, sem mudar implementação

Evidência anterior em memória: primeira publicação gera `registration_period_cancelled`; Retificação
não gera esse código. Snapshot mínimo tinha outros erros. Aqui o plano exige edital completo;
sucesso integral ainda é **expectativa a observar**, não resultado já obtido.

| ID / objetivo | Estado e dados específicos | Leituras / escritas e atos esperados | Resultado esperado e critérios de aprovação | Evidências e risco específico |
|---|---|---|---|---|
| P01-A — primeira publicação com evento cancelado | Edital completo homologado para ensaio, não publicado; único evento designado CANCELADO, janela futura; nenhuma inscrição | Ler revisão; solicitar publicação com ator adequado. Tentativa pode gerar trilha/recusa; não deve criar publicação bem-sucedida | Impeditivo próprio, mensagem/caminho corretos; sem primeiro ato publicado. Outros achados devem ser discriminados | Captura/response, estado e atos antes/depois; risco de atribuir recusa de outro requisito ao cancelamento. Herda C1–C7 |
| P01-B — cancelar por Retificação | Outro edital válido PUBLICADO, janela aberta; uma inscrição enviada e outra rascunho, todos sintéticos | Publicar Retificação que declara evento CANCELADO; ler calendário e histórico; tentar novo envio sintético | Espera-se ausência do impeditivo específico no ato de Retificação; demais validações podem recusar. Se efetivado, recepção segue período cancelado e aceitas permanecem íntegras; não presumir prazo administrativo | Nove campos exigidos pela R3, hashes/IDs das inscrições/atos; risco de confundir ato publicado e recebimento. C1–C7 |
| P01-C — designar evento válido | Estado publicado cancelado preparado separadamente; evento antigo preservado; novo evento válido com janela definida | Retificar designação antiga para falso e nova para verdadeiro; ler cronograma, vigência e tentar novo envio | Exatamente uma designação; ausência desse impeditivo não garante aceitação completa; recepção deve corresponder à nova vigência/janela, sem alterar aceitas | Eventos e calendário antes/depois, versão aceita e trilha; risco de transformar demonstração em autorização de reabertura. C1–C7 |

Ficha obrigatória de cada P01: estado inicial do Edital, estado do Evento, operação, validações,
resultado observado, impacto em existentes, impacto em novas, consequência administrativa a
deliberar e recomendação. Cancelamento só via API, se assim implementado, será evidência técnica
separada da limitação da jornada administrativa; não apresentar shell/API como homologação de tela.

## DEC-15.06 — separar os três alcances

| ID / objetivo | Estado e dados específicos | Leituras / escritas e atos esperados | Resultado esperado e critérios de aprovação | Evidências e risco específico |
|---|---|---|---|---|
| P06-A — compatibilidade histórica | Snapshot sintético versão anterior ao degrau 10; método ausente; nenhum ato real | Em memória elevar e aplicar método completo; variante persistente somente se baseline sintética antiga e publicável estiver aprovada | Ausência vira nulo sem padrão; método pode ser endereçado. Publicação exige validação completa; não gerar norma implícita | Snapshot/versão antes/depois, achados e origem; risco de confundir migração de conteúdo com migration de banco. Esta última proibida. C1–C7 |
| P06-B — método em edital que já prevê sorteio | Texto/estrutura sintéticos coerentes com sorteio; sem procedimento realizado. Subcasos: sem relação e com relação congelada | Retificação de método e, quando autorizado, congelamento de relação sintética; comparar hash/método congelado e vigente | Relação antiga não reescrita; confirmar método declarado completo e efeitos em nova relação/ato permitido. Não obter números de fonte externa | PDF, versões, hash e universo antes/depois; ausência de sorteio realizado não implica ausência de compromisso congelado. C1–C7 |
| P06-C — pontuação para sorteio | Edital sintético por pontuação; subcasos sem ordem e com ordem sintética emitida | Tentar operação pelas APIs existentes, registrar validações e eventual recusa `ordering_act_already_exists`; não contornar recusa nem inventar comando de conversão | Objetivo é conhecer alcance e fronteiras, não obrigar sucesso. Se aceito tecnicamente, regra permanece sem ratificação administrativa | Cadeia das notas/ordem/corte/dependentes e resposta por subcaso. Risco de confundir endereçamento com autorização. C1–C7 |

Por P06 registrar: regra implementada, possibilidade de Retificação, restrições temporais e de
estado, impacto em candidatos/atos, autoridade necessária e recomendação. Antes de converter
espécie com efeitos persistentes, o operador deve ter autorização explícita desse subcaso sintético;
sem ela só analisa leitura/memória. Nenhum resultado aprova conversão em certame real.

## DEC-15.07 — correção e substituição normativa

| ID / objetivo | Estado e dados específicos | Leituras / escritas e atos esperados | Resultado esperado e critérios de aprovação | Evidências e risco específico |
|---|---|---|---|---|
| P07-A — corrigir fundamento errado | Modalidade de Perfil sintético, mesmo ID de regra, fundamento propositalmente fictício; edital/inscrição sintéticos publicados na baseline autorizada | Em memória aplicar `foundation`, `version`, `effectiveFrom`; depois, se autorizado, Retificação e comparação das referências antigas | Campos endereçáveis não implicam correção juridicamente válida. Publicação/versionamento preservam versão anterior e vínculos | Origem Git, identidade/fundamento/versão/vigência separados, IDs/bytes antes/depois; risco de corrigir conteúdo trocando identidade. C1–C7 |
| P07-B — substituir regra por outra | Exemplo institucional de substituição **ainda a fornecer**; duas identidades sintéticas distintas e mapa de vínculos proposto | Demonstrar recusa da troca direta de ID; mapear referências. Sucessão bem-sucedida só será planejada/executada após nova deliberação sobre mecanismo legítimo | Esperado atualmente: recusa de ID estrutural. Não há critério aprovado de sucesso administrativo da substituição; registrar bloqueio e alternativas | Caminhos/versões/modalidades, inscrições/quadro/classificação/documentos potencialmente afetados; risco de simular legitimidade sem norma. C1–C7 |

Fonte histórica recuperada e limites seguem no dossiê Fase 3. P07-B **não autoriza implementar ou
executar mecanismo novo**, trocar ID por SQL, substituir entidade inteira para driblar guarda ou
alterar fundamento para disfarçar outra identidade. Critério de aceite desta fase futura pode ser
“recusa demonstrada e alternativa pendente”, não “substituição concluída”.

## DEC-15.15 — superfícies de prévia, geração e entrega

Para todos P15: operador sintético com permissão separada, outro sem permissão e terceiro de outro
escopo; populações sintéticas com requerimentos enviados. Nenhum arquivo real/RA é utilizado.

| ID / objetivo | Estado e dados específicos | Leituras / escritas e atos esperados | Resultado esperado e critérios de aprovação | Evidências e risco específico |
|---|---|---|---|---|
| P15-A — entrada sem população | Edital apto a exportação, sem escolha no GET | Ler opções; comparar trilha antes/depois. GET pode criar sessão técnica, não presumir zero escrita | Localizar metadados e eventual identificação indireta; condição atual de prévia não foi ratificada | HTML/captura sanitizada, contagens/eventos; risco de inferência por pequeno grupo. C1–C7 |
| P15-B — prévia sem pessoas nomeadas | Relatório apenas agregado, sem lacuna nominal | GET compõe dados no servidor; observar ausência/presença de evento próprio | Leitura de código prevê ausência de `MATRICULA_PREVER`; confirmar e avaliar suficiência, sem aprovar por passar | Dados visíveis/ocultos versus tratados, antes/depois da trilha; risco de chamar agregado “anônimo”. C1–C7 |
| P15-C — prévia nominal | Declaração sintética não comportada pelo destino (exemplo cor/raça) | GET e gravação de `MATRICULA_PREVER` prevista | Evento deve referenciar contexto sem copiar declaração; nome/protocolo fictícios visíveis onde previsto | Campos do evento, HTML e relatório; risco de evidência expor pessoa real se dataset errado. C1–C7 |
| P15-D — recusa/erro | População incompleta ou modalidade sintética não reconhecida, sem alterar código | GET/POST existentes para provocar `DomainError`; observar mensagem e auditoria | Inventariar dados nomeados e caminho de saída; não presumir política por ausência de composição | Erro, quem/quais campos expostos, eventos; risco de erro nominal fora da condição de auditoria. C1–C7 |
| P15-E — gerar e receber resposta | Prévia válida, assinatura confirmada; subcaso assinatura obsoleta | POST monta XLSX, cria `GeracaoDeArquivo` se sucesso, retorna attachment; baixar somente ao diretório autorizado | Registro comprova geração, não recebimento/importação. Assinatura obsoleta deve ser recusada; conferir 34 colunas sintéticas | Hash/nome/tamanho e recebimento local separados de registro do servidor; nenhuma importação RA. C1–C7 |
| P15-F — permissões/escopo | Mesmos recursos, ator sem permissão e ator de outra unidade | GET/POST autorizados para observar recusas; auditar eventual tentativa conforme implementado | Recusa sem exportar conteúdo; nenhum aumento de permissão para fazer passar | Status, ausência de arquivo, eventos e escopo; risco de usar papel real ou conceder acesso indevido. C1–C7 |

Geração, resposta, recebimento local, abertura e importação são eventos distintos. Somente os três
primeiros podem ser incluídos no escopo proposto; abertura local sintética depende da ferramenta
aprovada e importação RA permanece excluída. Não criar novo evento no código para satisfazer matriz.

## Entrega após execução futura

Ficha por cenário/subcaso com os onze itens deste plano: objetivo, estado, dados, ambiente,
leituras/escritas, atos/auditoria, esperado, evidência, aceite, recuperação e risco/contenção.
Documento de resultado com hipóteses e observações separadas; lista dos casos não executados e
motivo; hashes e custódia; deliberações posteriores necessárias. Não preencher “observado” por leitura.
