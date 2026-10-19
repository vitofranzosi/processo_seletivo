# Dossiê técnico — quatro pendências da DEC-15

Data: 16/10/2026. Legenda de evidências e comandos no [índice](README.md).
Todas as execuções desta fase foram puras, com conteúdo sintético; nenhum ato foi persistido.

## DEC-15.01 — Evento de inscrições cancelado

**D:** demonstração aprovada, impeditivo ainda não ratificado. **L:**
`backend/processo_seletivo/editais/domain/validation.py`, `_periodo_de_inscricoes_cancelado`,
retorna lista vazia se `ato != ATO_DE_PUBLICACAO`. A recusa é condicionada à primeira publicação.
`publicacoes/application/retificacoes.py`, `_assert_conteudo_publicavel`, passa `ATO_DE_RETIFICACAO`.
O cálculo de advertências também compara chamadas com atos distintos; não confundir esse cálculo
com o impedimento efetivo de publicar a Retificação.

**Correção de incerteza histórica:** a análise inicial da Fase 2 não afirmava haver exceção e
recomendava demonstrá-la. Agora existe evidência direta da exceção implementada e teste executado.
Não existe evidência nesta fase de que todo ato de cancelamento será publicado com sucesso.

### Observação reproduzível por cenário

Fonte executada: `backend/tests/unit/editais/test_publicacao_com_periodo_cancelado.py`;
o [reprodutor](reproduzir-em-memoria.py) acrescenta a troca de designação em memória.
Instante sintético fixo: 07/10/2026 às 12h, America/Sao_Paulo. Eventos de datas futuras, dois IDs
de teste e um único evento designado. Não há objetos persistidos de Edital ou inscrição.

| Cenário | Estado inicial representado / operação | Validações e resultado **O** | Impactos / consequências |
|---|---|---|---|
| 01-A — primeira publicação | Conteúdo candidato à publicação, evento designado CANCELADO; chamar validador com ato de publicação | `registration_period_cancelled` com `BLOCKING_ERROR` | Esse achado impede primeiro ato, se levado ao comando; recepção no estado cancelado é recusada pelo domínio. Não foram criadas inscrições |
| 01-B — Retificação que cancela | Representação do conteúdo resultante de Edital já publicado, agora com evento CANCELADO; chamar validador com ato de Retificação | Nenhum `registration_period_cancelled` | Cancelamento de recebimento e publicabilidade são distintos. Não comprova aprovação do ato completo ou efeitos nas inscrições existentes |
| 01-C — substituir evento | Conteúdo resultante: evento antigo CANCELADO perde designação; outro PLANEJADO ganha a designação; ato de Retificação | Nenhum `registration_period_cancelled` | Possível nova janela depende das datas/estado e demais validações. Não autoriza reabertura administrativa nem invalidação de aceitas |

Em todos há outros achados porque o snapshot é mínimo: `description_missing`, `field_format_invalid`,
`field_required`, `profiles_required`. Logo **não se conclui “publicação aceita”** em B/C. A exceção
observada é somente deste impeditivo. Os IDs simplificados e ausência de Perfis são intencionais
na fixture de unidade e não formam Edital publicável de demonstração.

**L — receber inscrições:** `inscricoes/domain/periodo.py` distingue estado cancelado e permite
recebimento por Edital apenas PUBLICADO. Não executar essa leitura como se comprovasse toda a
submissão. **H:** inscrição anterior permanece íntegra nos três percursos completos; precisa de
evidência de integração/operacional. Candidatos novos precisam receber orientação correspondente
ao evento/data efetivamente vigente.

**R:** submeter a distinção já implementada ao produto/Cefor, preservando a exceção até decisão;
não “corrigir” o código para alcançar resultado esperado. Não ratificar impeditivo geral com base
na primeira linha: ele não é geral no código observado.

### Procedimento persistente preparado — não executado

Após autorização específica, usar instância PostgreSQL exclusiva e já preparada, banco novo
identificado para esta sessão, armazenamento de mídia próprio e dados sintéticos. Conferir host,
porta, nome e papéis sem expor senha; recusar prosseguir se apontar ao desenvolvimento. Sem serviço
de e-mail real ou inferência. Não usar `ps_filme`, `ps_video` ou banco original. Nenhum reset ou limpeza.

1. Pela jornada destinada ao ator, preparar um Edital completo, autoridades sintéticas e atores
   sintéticos distintos onde exigido. Obter aprovação do ambiente e de cada gravação prevista.
2. A: tentar primeira publicação com único evento cancelado; guardar achados e ausência de ato novo.
3. B: em outro Edital inicialmente válido e publicado, enviar inscrição sintética enquanto permitido;
   preparar/publicar Retificação de cancelamento; guardar atos, versões e resultados das validações.
4. C: a partir de estado cancelado, preparar Retificação que designa evento válido; conferir
   publicabilidade e recepção antes/depois da vigência, sem modificar registros anteriores.
5. Para cada caso: estado do Edital/Evento, operação, validações, resultado observado, impacto em
   inscrições anteriores e novas, consequências administrativas e recomendação; capturas, IDs,
   timestamps, versões e trilha. Esperado e observado em campos separados.

Se declarar cancelamento só estiver disponível pela API, registrar essa limitação do canal do
operador e separar demonstração técnica de homologação de jornada. Não demonstrar por shell como
se fosse conclusão de jornada. Dados persistidos ficam preservados; sua destinação exige decisão
específica. Se houver necessidade de migration, interromper e solicitar nova autorização.

## DEC-15.06 — três cenários de método de sorteio

Fontes: `publicacoes/domain/elevacao.py`, `changes.py`, `editais/domain/mutabilidade.py`,
`sorteios/domain/metodo.py`, `sorteios/application/relacao.py`, `sorteios/application/sorteio.py`;
`backend/tests/contract/test_elevacao_degrau_10.py` executado;
`backend/tests/integration/editais/test_mutabilidade_do_metodo_de_sorteio.py` somente lido.

| Cenário | Comportamento / possibilidade de Retificação | Restrições e impactos | Autorização / recomendação |
|---|---|---|---|
| 06-A — ausência histórica | **O:** elevação de versão anterior grafa `drawMethod=None`, sem inventar método; teste puro aplica método completo por REPLACE | **L:** método ausente não fornece padrão; comando exige método declarado. Conversão técnica de formato não é publicação de norma | Autoridade deve confirmar método a declarar; **R:** preservar ausência e exigir ato explícito, sem adotar fonte padrão |
| 06-B — edital já prevê sorteio, procedimento não realizado | **L:** contrato permite objeto antes ausente e campos do método retificáveis; validação deve conferir conteúdo. Texto que prevê sorteio não equivale automaticamente a método estruturado | Relação pode estar congelada mesmo sem sorteio realizado; teste de integração lido afirma hash/método congelados não relidos pela Retificação. Não assumir que editar método atual atualiza relação | Confirmar previsão normativa, relação existente e efeito temporal com comissão/autoridade; **R:** conferir completo e vigente antes de congelar, sem reescrever relação existente |
| 06-C — passar de pontuação para sorteio | **L:** possibilidade genérica de escrever método não é permissão administrativa de conversão; `sorteio.py` contém recusa `ordering_act_already_exists` quando já há ordenação, conforme contexto do comando | Não demonstrado percurso completo de mudança de espécie. Notas, ordem, corte, recurso e convocação podem ser afetados. Existência da recusa não prova bloqueio universal em toda fase | **R:** manter não ratificado; mapear fases e sucessores e submeter ao Cefor/autoridade normativa. Não inferir aplicação segura por passar REPLACE em memória |

Restrições temporais: datas de ocorrência, vigência e estado dos atos são dimensões diferentes.
Não foi identificada nesta leitura prova de uma única regra administrativa por fase cobrindo A/B/C.
A relação congelada carrega método/hash próprios; alteração futura de conteúdo não deve ser
interpretada como mutação de atos anteriores. A demonstração com relação, sorteio, notas ou
convocações demanda autorização de persistência; fonte externa real não é necessária nem autorizada.

**Lacunas de evidência:** execução completa de B/C; reação da interface por fase; matriz dos atos
dependentes e decisão institucional. Pergunta pendente: que alcance pode ser ratificado por cenário,
com qual rito e quais limitações? Responsáveis: produto, comissão e autoridade administrativa competente.

## DEC-15.07 — identidade, fundamento, versão e vigência

**L — origem recuperada no Git:** `git log --all -G 'normativeRule/id'` nos arquivos do contrato e
matriz localiza `0c3f0135` (13/09/2026), que introduz a linha estrutural na matriz, e `be700cba`
(13/09), que introduz o contrato executável com `estrutural()`. `1d721b93` restaura outras cinco
capacidades, não demonstra reclassificação deste ID. Isso identifica origem documental/técnica,
**não fala humana de aprovação**. ED-47 e a divergência de contagem ficam preservadas como histórico.

| Campo | Significado técnico e tratamento observado |
|---|---|
| `normativeRule/id` | Identidade estrutural do objeto; contrato recusa alteração direta |
| `foundation` | Texto de fundamento; retificável sem trocar ID |
| `version` | Versão declarada da regra; retificável; não substitui a versão do Edital/ato |
| `effectiveFrom` | Vigência declarada da regra; retificável; não presumir que coordena sozinha todos os efeitos de Retificação |

**O — demonstração sintética em memória:** corrigir `foundation` aceito; alterar `version` aceito;
alterar `effectiveFrom` aceito; trocar `id` recusado com `CampoNaoRetificavel`. Entradas independentes,
sem validar publicação completa ou efeitos em cotas/inscrições. JSON preservado nesta pasta.

**Cenário de fundamento incorreto:** a correção textual no mesmo objeto é tecnicamente endereçável;
admissibilidade jurídica e vigência precisam de decisão competente. Não traduzir sucesso da função
em autorização normativa. **Cenário de substituição legítima:** troca direta de ID é recusada;
alterar versão/fundamento conserva identidade, mas **não demonstra substituição normativa legítima**.
Novo objeto/vínculo ou nova entidade e seus efeitos não foram implementados nem aprovados.

Vínculos a mapear na demonstração completa: Modalidade dentro do Perfil, versão canônica publicada,
regra/fundamento congelados no ato, quadro de vagas, inscrições por modalidade, classificação,
reversão e documentos gerados. **H:** cada referência afetável deve ser enumerada com seu caminho/ID;
esta lista de superfícies não comprova catálogo completo de FKs ou dependências reais.

**R — alternativas a deliberar:** correção textual versionada quando continua a mesma identidade;
nova versão com limites temporais aprovados; procedimento de nova identidade/vínculo somente após
especificação de sucessão e impactos. Manter estabilidade provisória conforme R4. Demonstração
persistente futura: dois editais sintéticos, um com fundamento errado e outro com substituição
institucionalmente exemplificada; comparar snapshots e referências antes/depois, sem apagar ato.

## DEC-15.15 — dados e auditoria de prévias/exportação

**L:** `interface/views.py` (view de exportação), `interface/templates/interface/matriculas.html`,
`matriculas/application/exportar.py`, `matriculas/domain/{colunas,lacuna,nomes}.py`,
`matriculas/models.py`. Testes somente lidos: `tests/interface/test_exportacao_de_matriculas.py`,
`tests/integration/matriculas/test_nao_escreve_fora.py`, `test_geracao.py` e `test_lacunas.py`.

### Superfícies e operações distintas

| Operação/superfície | Dados apresentados ou processados | Evidência de auditoria em código | Limite |
|---|---|---|---|
| GET sem população escolhida | Edital, opções de população e rótulos | Não identificado evento específico nesta ramificação | Rótulos/pequenos grupos podem identificar indiretamente; política ainda não ratificada |
| GET prévia sem lacuna nominal | População, quantidade, colunas/razões, contagens e aviso de renda; dados completos são compostos no servidor | `nomeia_pessoas=False`: sem `MATRICULA_PREVER` nessa ramificação | Não expor as 34 células na página não elimina tratamento ou inferência por contagem |
| GET prévia nominal | Nome + protocolo e declaração não suportada no destino (ex.: cor/raça indígena) no relatório | `nomeia_pessoas=True`: `record_event`, operação `MATRICULA_PREVER`, ator/escopo/correlação/contexto | Evento referencia, não copia declaração; cobertura do critério continua por ratificar |
| Erro de composição | `DomainError.detail` exibido como erro na tela; recusas podem nomear inscrição/modalidade/edital | Retorno de erro antes do ramo nominal; não identificado evento específico nessa view | Inventariar exceções e mensagens; não concluir “sem nomes” só porque não há composição bem-sucedida |
| POST geração | Recompõe população, confere assinatura de prévia, monta planilha em memória | Cria `GeracaoDeArquivo`: ator, instante, população, quantidade, versões, IDs de requerimentos | IDs são ligáveis a pessoas por contexto; não chamá-los anonimizados |
| Resposta/download | Mesma requisição POST entrega bytes como attachment; resposta privada | Registro da geração é evidência do servidor; não identificado evento separado de recebimento no cliente | Não comprova download concluído, abertura, cópia externa ou importação RA |

**Arquivo — 34 colunas inventariadas:** INSC, NOME, CLASSIF_CURSO_FINAL, COD_CURSO, COD_TURNO,
COD_FORMA_INGRESSO, CPF, SEXO, ESTADO_CIVIL, EMAIL, DATA_NASCIMENTO, COR, NOME_MAE, NOME_PAI,
CIDADE_NATAL, COD_NACIONALIDADE, RG, EMISSOR, IDENTIDADE_DATA, TITULO_ELE, ZONA_ELE, SECAO_ELE,
CEP, ENDEREÇO, NÚMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, CELULAR, RENDA_PER_CAPITA_PNP,
NECESSIDADES_ESPECIAIS, NOME_POLO, COD_POLO. Algumas saem vazias por decisão do mapeamento.

**Exposição potencial:** identificadores diretos (nome/CPF/RG/contatos), filiação e endereço;
cor/raça e necessidades especiais merecem tratamento como conteúdo sensível na avaliação;
renda é dado pessoal de contexto socioeconômico, sem classificação jurídica definitiva aqui.
Protocolo, modalidade, população, polo e contagens pequenas podem reidentificar ou revelar
atributo por combinação. A assinatura oculta do resumo deriva do conteúdo; não deve ser registrada
ou exposta fora do necessário. Não foram lidos dados reais, arquivos exportados ou logs de produção.

**R:** deliberar política por superfície, incluindo erro, e por operação; minimizar evento sem
copiar conteúdo; avaliar auditoria de toda prévia versus nominalidade antes de implementar.
Não recomendar “logar a planilha”. Não declarar download concluído quando só há geração/resposta.
**Pendente:** validar inventário com equipe/encarregado, observar cenários sintéticos por interface
com persistência autorizada (evento é escrita), decidir cobertura e testar permissões/escopo.
