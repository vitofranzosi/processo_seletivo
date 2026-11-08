# Inventário conceitual e contrato conferido

08/11/2026 · base `da566ff2` · POC local, sem alteração de negócio. Caminhos de código abaixo
partem de `backend/processo_seletivo/`. A investigação combinou modelos, funções puras, comandos,
seletores, testes, specs e templates. As dificuldades pedagógicas são inferências de inspeção,
não resultados de observação com operadores.

## Matriz

| Conceito | Significado no GPS | Regra verificada e dependência | Fonte no código / spec | Dificuldade pedagógica |
|---|---|---|---|---|
| Processo / Edital | Processo agrupa editais; Edital publica norma versionada | Não são sinônimos; mudança de norma publicada exige Retificação | Constituição; `processos/models.py`; `publicacoes/application/retificacoes.py` | Confundir recipiente, norma e oferta |
| Perfil de Vaga | Oferta em que inscrições concorrem | Tem vagas, modalidades e marcos; a etapa pertence ao Edital | `editais/models/perfis.py:9`; `editais/models/etapas.py:11` | Supor uma classificação única do edital inteiro |
| Inscrição | Participação da pessoa num perfil | Inscrição enviada não é resultado de habilitação; pode haver inscrições distintas | `inscricoes/application/submissao.py`; `inscricoes/models.py` | Trocar participação por aptidão ou classificação |
| Modalidade / lista / recorte | Forma de concorrência declarada / eixo da ordem e dos atos | Ampla declarada; reservadas não são categorias conhecidas por nome pelo motor; atos por perfil, marco e lista | `editais/models/perfis.py`; `classificacao/application/calculo.py`; specs 015 e 016 | Contar duas vezes a pessoa em duas listas |
| Etapa pontuada | Avaliação que conclui com número | Uma avaliação prevista é consolidável; mais de uma não tem regra de combinação | `resultados/domain/regra.py:55`; `avaliacoes/application/avaliacao.py`; spec 013 | Imaginar barema ou média de banca implementados |
| Etapa decisória | Decisão sem nota | Favorável habilita e desfavorável elimina na etapa eliminatória; enumerada no marco é porta, não parcela | `resultados/domain/regra.py:151`; `classificacao/domain/combinacao.py:92`; specs 013 e 015 | Inventar nota zero para uma decisão |
| Mínimo / eliminação | Consequência local da etapa | Abaixo do mínimo elimina **se eliminatória**; igualdade habilita; ausência por ocorrência não equivale a zero | `resultados/domain/regra.py:117`; `resultados/application/ocorrencia.py` | Achar que média alta compensa eliminação anterior |
| Habilitação / progressão | Condições para participar da etapa | Eliminação em qualquer anterior exclui; habilitação da imediatamente anterior quando aplicável; corte governante precisa alcançar | `resultados/domain/progressao.py`; `resultados/application/prontidao.py`; decisão RC-112 | Tratar habilitação como um estado universal e permanente |
| Peso / combinação | Composição numérica de etapas no marco | Peso é da etapa; soma ou média conforme publicado; arredonda uma vez; ausência não vira zero | `classificacao/domain/combinacao.py:80,103`; `editais/domain/marcos.py`; spec 015 | Misturar nota de etapa e pontuação combinada |
| Marco | Declaração de uma produção de ordem para um perfil | Pontuação ou sorteio; enumeração, desempates, corte e recurso. Marco não é o ato emitido nem sua divulgação | `editais/models/perfis.py:233`; `classificacao/application/emissao.py`; specs 015 e 030 | Reduzir marco a data, etapa ou lista publicada |
| Classificação / posição | Ordem emitida por marco e lista | Pontuação primeiro; critérios em sequência; empate residual compartilha posição (1,1,3) | `classificacao/domain/desempate.py:157,205`; `classificacao/application/calculo.py`; spec 015 | A posição parece explicar-se sozinha, mas omite sua causa |
| Desempate | Separação de grupos de mesma pontuação | Maior nota de etapa, maior/menor fato; ausência tem política publicada; etapa só de desempate não soma | `classificacao/domain/desempate.py`; spec 114 | Achar que nome, protocolo ou chegada resolvem empate |
| Sorteio | Produção verificável de ordem por chaves | Relação, recorte, semente, número público e domínio entram no SHA-256; todos recebem posição, sem nota ou corte | `sorteios/domain/chave.py`; specs 021 e 098 | Representar sorteio como uma prova com nota aleatória |
| Corte / faixa | Aplicação da regra publicada à ordem vigente | Alvo fixo ou quadro + suplentes; **por lista**; conta pessoas, não rótulos de posição; empate na fronteira da faixa | `classificacao/domain/faixa.py:124`; `classificacao/application/corte.py`; spec 014 | Confundir quantidade que avança com vagas finais |
| Etapa governada | Destino explicitamente alimentado por um corte | Declarada; `NONE` significa corte terminal sem participação posterior; obsolescência do corte trava trabalho novo | `classificacao/domain/faixa.py:87`; `classificacao/application/emissao_do_corte.py`; spec 014 | Supor que todo corte necessariamente leva a outra etapa |
| Suplente / cadastro reserva | Pessoa alcançada além do alvo / configuração do perfil | Faixa pode incluir suplentes; cadastro reserva não cria sozinho outro corte ou efeito de ocupação | `classificacao/domain/faixa.py`; `ocupacao/domain/apuracao.py`; inventário do estudo de 07/11 | Usar lista reservada, cadastro reserva e suplência como equivalentes |
| Apuração | Ato reproduzível de ocupação por recorte | Registra publicadas, efetivas e ocupadas; faltantes = efetivas − ocupadas; lê faixa, habilitação, movimentos e efeitos | `ocupacao/domain/apuracao.py:257`; `ocupacao/application/emissao.py`; spec 016 | Pensar que é apenas pegar os primeiros da classificação |
| Titular / ocupante | Janela inicial / conjunto que conta na ocupação | Janela antes do filtro de habilitação; titular eliminado não ocupa, deixando déficit; titulares habilitados contam antes de convocar | `ocupacao/domain/apuracao.py:123,187`; spec 019, regra R-001 | Ler “ocupada” como matrícula ou promover suplente sem ato |
| Concorrência concomitante | Exclusão de quem ocupa pela ampla da sequência reservada | Sai antes da janela reservada; não transfere quantidade; caso dinâmico tem limitações registradas | `ocupacao/domain/apuracao.py:100,219`; spec 016; estudo de concorrência de 07/11 | Confundir exclusão da pessoa com movimento de vaga |
| Reversão | Movimento de saldo reservado para ampla | Só se declarada e segundo espécie publicada; não é a concomitância | `ocupacao/domain/reversao.py`; `ocupacao/application/movimento.py`; spec 016 | Supor que qualquer reserva vazia reverte automaticamente |
| Preliminar / definitiva | Naturezas de divulgação de um ato | Publicar exige ato vigente e não obsoleto; definitiva enfrenta janela aberta, recursos, reavaliações e providências pendentes | `divulgacao/domain/publicabilidade.py:241`; `divulgacao/application/publicar.py:98`; specs 017 e 018 | Confundir emitir ordem com tornar pública; supor definitiva automática |
| Recurso / sucessão | Contestação e cadeia de atos que a decisão alcança | Correção pode produzir Resultado sucessor; ordem fica obsoleta e requer sucessora citando decisão; não reescreve passado | `recursos/application/julgar.py`; `classificacao/application/emissao.py`; spec 018 | Imaginar que julgar atualiza todas as telas e atos automaticamente |
| Janela | Prazo recursal aplicável ao ato divulgado | Dias corridos; exclui começo e inclui vencimento; nova natureza do mesmo ato não reabre; novo ato tem outra âncora | `recursos/domain/janela.py:164`; `divulgacao/domain/publicabilidade.py`; spec 018 | Confundir prazo não declarado com zero dias |
| Convocação | Ato individual ligado à ordem, faixa e apuração | Permissão, escopo, fila, faixa, apuração e déficit conforme espécie; titular pode ser chamado com déficit zero; comando não exige definitiva universalmente | `convocacao/application/convocar.py:38,110,434`; specs 019 e 050 | Achar que posição ou ocupação já chamam a pessoa |
| Comunicação | Registro da comunicação da chamada | Canal publicado: mensagem individual ou publicação com referência; envio não comprova leitura; não atendimento exige condições e registro | `convocacao/application/comunicar.py`; `convocacao/application/desfechar.py`; spec 125 | Igualar ato, envio, leitura e vencimento |
| Documentação | Lista da chamada, arquivos versionados e conferência | Lista nasce com chamada; abrir versão antes de conforme; pendente pede correção; não se aplica depende de condição publicada e ciência | `convocacao/application/documentos.py:555,726`; specs 115, 117 e 131 | Documento recebido parece aprovado ou desfecho registrado |
| Desfecho | Registro de resultado da chamada e seu efeito | Aceite/regularização incluem; cinco outros excluem. Apuração seguinte no mesmo ato, salvo impedimentos como reversão | `convocacao/domain/nomes.py`; `convocacao/application/desfechar.py:103,277`; spec 019 | Supor que chamada de suplente já preenche a vaga |
| Formalização / matrícula | Encaminhamento documental e resultado institucional posterior | Pacote e planilha exportados registram exportação; não comprovam matrícula em sistema externo | `formalizacao/application/exportar.py`; `matriculas/application/exportar.py`; specs 117 e 031 | Confundir aceite, requerimento enviado, exportação e matrícula efetiva |

## Dependências usadas pela história

Prova → Resultado → ordens do marco 1 → preliminares → recurso e Resultado sucessor →
ordens sucessoras → divulgação e prazo → definitivas → cortes por lista → união na Entrevista →
Resultados → ordens do marco 2 → cortes terminais → apurações → divulgação definitiva no contexto
seguinte → convocações → comunicações → arquivos → conferências → desfechos → apurações seguintes.

Esta é uma escolha narrativa. A ordem de publicação, corte e apuração não é imposição universal:
a convocação não consulta a definitiva como portão geral. Corte terminal não governa etapa; sorteio
pode vir antes de qualquer avaliação. O aplicativo avisa que entrar numa cena assume atos anteriores.

## Fontes estudadas

- Guia anterior localizado por busca de nome em `/Users/saymoncastro/Downloads/guia-ps-etapas-classificacao-autocontido.html`.
  SHA-256: `42d8d04da33b63f497af60eed445e7e118604da51551d7327cf74967441482fb`.
  Tem 13 capítulos, modo apresentação, seleção de candidato, tabela completa e glossário. Seu texto
  e JavaScript foram lidos; não foi copiado. Preservamos a explicação individual e a cadeia de atos,
  com elenco menor e demonstrações causais. O título “até a matrícula” ultrapassa o que seu próprio
  capítulo 12 exercita (aceites; formalização fora do estudo); a POC diz explicitamente “aceite” e
  não comprova matrícula externa. O arquivo autocontido inclui capturas; a versão do estudo está
  em `doc/estudo-classificacao-demonstrativa-2026-11-07/index.html`.
- Estudos [classificação](../estudo-classificacao-demonstrativa-2026-11-07.md),
  [inventário detalhado](../estudo-classificacao-demonstrativa-2026-11-07/inventario.md),
  [concorrência](../estudo-concorrencia-concomitante-2026-11-07.md),
  [orientação](../estudo-orientacao-da-jornada-2026-11-06/README.md),
  [sorteio](../estudo-sorteio-edital-35-2026-11-05.md) e guia documental de 06/11.
- Templates reais: `interface/templates/interface/_marco.html`, `compor_classificacao.html`,
  `marco.html`, `corte.html`, `ocupacao.html`, `convocacao.html`, `convocacao_documentos.html`;
  `portal/templates/portal/convocacao.html`. Três capturas reais já existentes foram inspecionadas
  e embutidas com aviso de que pertencem a outros cenários; origens em `embutir_capturas.py`.
- Testes unitários: `tests/unit/resultados/test_regra.py`, `classificacao/test_faixa.py`,
  `classificacao/test_desempate.py`, `ocupacao/test_apuracao.py`, `sorteios/test_chave_fechada.py`.
- Integração: `tests/integration/classificacao/test_calculo.py`, `test_corte_apos_recurso.py`,
  `test_previa_equivale_ao_oficial.py`, `test_citacao_de_decisao.py`;
  `ocupacao/test_concomitancia.py`; `convocacao/test_recusas.py`, `test_suplencia.py`,
  `test_documentos_da_convocacao.py`, `test_apuracao_seguinte.py`;
  `divulgacao/test_publicabilidade_por_recurso.py`.

## Divergências e limites: registro separado do conteúdo básico

| Identificador local | Evidência vigente | Tratamento no guia | Decisão posterior |
|---|---|---|---|
| ACH-01 · empate estrito | `_marco.html:651` diz “A faixa para no alvo”; `faixa.calcular` recusa fronteira atravessada de alvo + suplentes; PDF conserva redação ambígua. Achado anterior de 19/10 | Laboratório ensina **recusa do motor**, sinalizando a divergência; caso básico sem empate residual | Alinhar norma, documento e interface; não trocar regra nesta POC |
| ACH-02 · fixo por lista | Revisão/PDF usam “os N primeiros” para alvo fixo; motor e atos são por lista. Confirmado no estudo e nas chamadas de corte | Dizer “4 por lista” e mostrar união de cinco, com nomes repetidos visíveis | Tornar alcance explícito antes de publicar e explicar união na etapa governada |
| ACH-03 · concorrência dinâmica | `ocupantes_pela_ampla`, efeitos e fila são por recorte; estudo de 07/11 reproduz retorno após desistência e dupla ocupação entre listas | Demonstrar concomitância **estática**; nova chamada entre duas pessoas só da ampla; aviso no laboratório e em Fontes | Decisão institucional antes de ajuste técnico; não afirmar migração automática |
| ACH-04 · significado de ocupada | Código conta titulares habilitados antes da convocação; telas priorizam números agregados | Lugares mostram nomes e uma frase diz “nenhuma convocação feita ainda” | Exibir origem individual da ocupação no produto |
| ACH-05 · comentários envelhecidos | `faixa.etapa_governada` ainda explica que todo marco enumera etapa, mas `editais.domain.marcos.exige_etapa` dispensa no sorteio declarado | Usar validação vigente e teste do método; sorteio independente sem notas | Manter documentação interna sem mudar norma publicada |
| ACH-06 · terminal descrito como progressão | Subtítulo de `corte.html` define faixa como trecho que progride à próxima etapa, mesmo com `governedStage=NONE` | Separar corte intermediário de terminal explicitamente | Adaptar texto ao papel do corte |

Nenhum achado foi convertido em spec ou tarefa de negócio. A spec 133 é apenas desta POC pedida.
