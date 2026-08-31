# Fase 0 — Pesquisa e decisões: Inscrição Simples e Documentos do Candidato

**Feature**: [spec.md](./spec.md) | **Plano**: [plan.md](./plan.md) | **Data**: 2026-08-31

Cada decisão abaixo foi tomada contra o repositório, não contra o hábito. Onde uma alternativa
razoável foi descartada, o motivo está escrito — é o que impede que ela volte pela porta dos fundos
na implementação.

## O ponto de partida — o que já existe e o que não existe

A spec verificou quatro premissas que a primeira redação dava por certas e que são falsas. Elas
governam metade das decisões:

1. **Não há armazenamento de arquivo.** Nenhum `FileField` no código, nenhuma raiz de mídia em
   `config/settings/`, e o único binário persistido é `DocumentoPublicado.bytes`, coluna binária.
2. **O tipo do Evento é texto livre** (`editais/models/cronograma.py:26`) e já viaja no snapshot
   (`publish_edital.py:140`). Designar o período é mudança canônica, não de tela.
3. **Ampla Concorrência não existe no domínio.** `ModalidadeConcorrencia` é livre por Perfil, e
   `AC` só aparece na convenção do `seed_demo`.
4. **O modelo de autorização é institucional.** `require_permission` decide permissão e escopo
   (`seguranca/application/authorization.py`); nada nele sabe de quem é um registro.

E três mecanismos servem sem alteração: `shared/idempotency.py`, a auditoria de
`auditoria/application.py` e a guarda `_exigir` de `config/settings/production.py`.

## D-001 — Onde vive a designação do período de inscrições

**Decisão**: uma marca no próprio Evento — `EventoCronograma.is_registration_period` —, com
`UniqueConstraint` parcial por Cronograma (`condition=Q(is_registration_period=True)`). No conteúdo
publicado ela aparece como `isRegistrationPeriod` dentro de cada item de `schedule`.

**Racional**: pertencimento e unicidade ficam garantidos pela estrutura, não por conferência. O
Evento marcado é, por construção, do Cronograma daquele Edital; e o banco impede o segundo. A marca
já nasce endereçável pela Retificação — `/schedule/id=<uuid>/isRegistrationPeriod` — porque
`/schedule` já é coleção com chave (`publicacoes/domain/colecoes.py`), então a gramática não muda.
E o snapshot ganha um campo booleano, não uma chave nova na raiz.

**Alternativas consideradas**:

- *Chave estrangeira em `Cronograma` apontando o Evento.* Lê melhor em prosa, mas o pertencimento
  ("o Evento é deste Cronograma") vira invariante de duas linhas, que constraint nenhuma expressa —
  passaria a depender de conferência em código, que é o que a marca dispensa.
- *Campo no `Edital`.* `Edital` vive em `processos`, e `EventoCronograma` em `editais`, que já
  importa `processos`. A referência inverteria a dependência entre os apps.
- *Valor reservado no `type` do Evento.* É a taxonomia que a spec proíbe (`FR-002`), e sobre um
  campo de texto livre que nada valida.

**Consequência para a Retificação**: duas marcas verdadeiras no mesmo Cronograma são alcançáveis por
duas Alterações sucessivas, que o banco de uma Publicação nova não vê. Por isso `validate_for_publication`
ganha uma conferência de coerência — no mesmo lugar e no mesmo formato de `_coerencia_das_etapas`,
que já percorre coleção e emite achado impeditivo.

## D-002 — Como o Documento Exigido entra no conteúdo publicado

**Decisão**: coleção nova na raiz, `documentRequirements`, com chave estável, registrada em
`COLECOES_COM_CHAVE`; forma publicada declarada em `editais/domain/validation.py` no mesmo formato
de `PERFIL_PUBLICADO` e `EVENTO_PUBLICADO`, transcrita do contrato e conferida por teste.

**Racional**: é a quinta coleção de um arranjo que já existe quatro vezes. Endereçamento, validação
de forma, hash e consolidação passam a valer para ela sem nenhuma linha nova de mecanismo.

**Forma**: `id`, `key`, `name`, `instructions`, `required`, `order`, `profileId` (anulável),
`modalityId` (anulável). Os dois últimos anuláveis são a aplicabilidade inteira — `FR-006` proíbe
qualquer outra dimensão.

**Alternativa rejeitada**: aninhar os documentos dentro de cada Perfil. Quebra o caso "para todos",
que é o mais comum nos Editais reais, e duplicaria o mesmo requisito em cada Perfil — divergência
garantida na primeira Retificação.

## D-003 — Como o documento publicado enuncia os documentos exigidos

**Decisão**: entrada nova no catálogo de seções — `documentos-exigidos`, gerada, com
`source="documentRequirements"`, imediatamente após a seção textual `inscricao` que já existe
(`editais/domain/secoes.py`).

**Racional**: é exatamente o mecanismo que já compõe Perfis, Etapas e Cronograma a partir de uma
coleção do snapshot. A identidade da seção é `uuid5` sobre `(edital.id, key)`, como as demais, e
nenhuma migration é necessária para o catálogo.

**Alternativa rejeitada**: compor a lista dentro da seção textual `inscricao`. A entrada do catálogo
é textual **ou** gerada — "cada tipo usa um, e nunca os dois" —, e o híbrido pediria um terceiro
tipo para atender um caso.

**Efeito colateral aceito**: `_topologia_das_secoes` valida o catálogo depois da publicação, então a
entrada nova faz parte do incremento canônico e viaja com ele.

## D-004 — Onde a elaboração declara o contrato de inscrição

**Decisão**: etapa nova do assistente, `Inscrição`, entre `Etapas de Avaliação` e `Conteúdo`, que
reúne a designação do período e os documentos exigidos.

**Racional**: `FR-007` pede preferir a alteração menor **quando ela couber coerentemente**, e aqui
não cabe. Documento exigido "para todos" não pertence à etapa de Perfis; documento exigido não é
Cronograma; e partir o mesmo contrato em duas etapas obrigaria quem elabora a procurar metade dele
em cada lugar. A posição é a mesma lógica que já ordenou o assistente: depois do Cronograma, porque
a designação escolhe um Evento; depois dos Perfis e das Modalidades, porque a aplicabilidade os
referencia.

**Encaixe**: `ETAPAS_COMPOSICAO`, `ETAPAS_GRAVAVEIS`, `COLECAO_DA_ETAPA` (`documentRequirements`),
`LEITURA_DA_ETAPA` e `replace_draft` — todos com um item a mais. Os fragmentos de linha
(adicionar/remover/ordenar) reusam `fragmentos/*` e `ordenacao.js`, já exercitados por Perfis,
Modalidades e Eventos.

## D-005 — O incremento canônico

**Decisão**: `SCHEMA_VERSION` 3 → 4, uma vez, na entrega 2, carregando as três mudanças de forma:
`isRegistrationPeriod` no Evento, `documentRequirements` na raiz, seção nova no catálogo.

**Consequência declarada**: `_assert_versao_canonica` recusa consolidar conteúdo de versão divergente
(`publicacoes/application/retificacoes.py:483-500`), e a decisão registrada ali é não converter e não
atualizar em massa. Editais publicados sob a versão 3 deixam de ser retificáveis; os dados de
demonstração são recriados pela seed. É o mesmo termo que a `007` registrou ao subir para a 3.

**A 008 não participa**: o plano dela declara que não toca domínio, snapshot, hash nem migration. O
que as liga é `publicacoes/infrastructure/pdf.py`, onde as duas escrevem — disputa de arquivo, não
de versão.

## D-006 — Armazenamento dos documentos do candidato

**Decisão**: campo de arquivo do próprio framework, com armazenamento de sistema de arquivos
configurado para uma raiz privada declarada em configuração, fora da árvore estática, sem URL
pública. O nome físico é derivado da Inscrição e do requisito, opaco, e nunca o nome enviado; o nome
original fica como metadado. Produção recusa subir sem a raiz declarada e absoluta, na guarda
`_exigir` já existente.

**Racional**: é a capacidade mínima que atende `FR-051` a `FR-053` sem introduzir nada externo. O
armazenamento é trocável depois sem que a semântica da aplicação mude, porque nada além do campo
conhece o caminho.

**Alternativa rejeitada — coluna binária, como `DocumentoPublicado`**: aquele caso é um documento por
publicação, imutável, pequeno e parte do ato. Este é até 10 MB por requisito, por candidato,
substituível durante o rascunho e lido em streaming. Guardá-lo em coluna faria cada leitura carregar
o conteúdo inteiro em memória e cada substituição inflar a tabela.

**Alternativa rejeitada — armazenamento em nuvem**: `FR-051` pede privacidade, não elasticidade, e a
spec proíbe introduzi-lo sem necessidade concreta.

## D-007 — Como um documento chega a quem pode vê-lo

**Decisão**: view mediada nos dois canais — no `portal` para o titular, no `interface` para o ator
institucional autorizado. Resposta em streaming, `Content-Disposition: inline`, `Cache-Control:
no-store`. Na entrega administrativa, o conteúdo é copiado uma vez, o resumo é calculado
**sobre a cópia**, e é a cópia verificada que vai para a resposta; divergindo, nada é servido e o
fato é registrado (`FR-053a`).

*Corrigido durante a entrega 6.* A primeira redação dizia "recalculado durante o streaming", e isso
não se sustenta: bytes enviados não voltam, e descobrir a divergência no meio do arquivo deixaria
quem consulta com meio documento e nenhuma explicação. Verificar antes e **reabrir o arquivo pelo
caminho** também não serve — foi assim que a primeira implementação aprovou um conteúdo e serviu
outro. O que fecha a janela é conferir e servir os mesmos bytes.

**Racional**: calcular na leitura administrativa é onde a integridade importa — é o momento em que o
arquivo vira evidência. Fazê-lo em toda leitura do candidato dobraria o custo de cada visualização do
próprio rascunho sem nada a provar.

**Rejeitado**: varredura periódica do acervo. Não há operação, agendador nem alarme para consumi-la.

## D-008 — A identidade do candidato

**Decisão**: eixo próprio em `portal/identidade.py`, com chave de sessão distinta da institucional
(`interface/identidade.py` usa `interface_identidade`), e provedor de demonstração explícito,
rotulado na tela, atrás de configuração própria — recusada em produção pela guarda `_exigir`.

**Racional**: espelha uma fronteira que o projeto já desenhou uma vez, e que a `002` documentou como
"quando o diretório institucional for integrado, só este módulo muda".

**Consequência**: os dois eixos coexistem na mesma sessão sem se confundir, porque as chaves são
distintas e cada canal lê apenas a sua. Um servidor identificado no `/gestao/` não é candidato; um
candidato identificado no portal não é ator institucional.

## D-009 — Titularidade

**Decisão**: função de domínio própria em `inscricoes/domain/titularidade.py`, chamada por toda view
do portal que toque uma Inscrição ou um Documento Submetido, e testada em `tests/authorization/`
junto das demais provas anti-IDOR.

**Racional**: `require_permission` responde "este ator pode praticar esta operação neste escopo?".
A pergunta do candidato é outra — "este registro é dele?" — e nenhuma composição das permissões
existentes a responde. Escrever a segunda como se fosse a primeira é como se cria um IDOR com
aparência de autorização.

## D-010 — O canal público

**Decisão**: app `portal`, com URLs próprias sob um prefixo público, base de template própria e
responsiva, e nenhum acesso a comando administrativo. Reaproveita a linguagem visual pela **parcial
de tokens** descrita em D-017.

**Racional**: `interface` é o canal do ator institucional — seu processador de contexto injeta
identidade e papéis em todo template, e a base carrega o cabeçalho de gestão. Servir o candidato de
lá significaria carregar esse contexto em página pública e compartilhar a chave de sessão, contra
`FR-020` e `FR-021`.

## D-011 — Progresso de envio sem dependência nova

**Decisão**: o formulário de cada requisito envia por htmx com codificação multipart, e uma barra de
progresso é alimentada pelo evento de progresso do próprio htmx; enquanto o envio corre, a ação fica
desabilitada e um aviso de "não feche esta página" é exibido. Sem envio corre, sem barra.

**Racional**: o htmx já está embarcado e emite progresso de requisição; o alvo de `FR-048` é
informar, não medir com precisão. Nenhuma biblioteca nova, nenhum upload em pedaços, nenhuma
retomada — a spec não pede e o volume não justifica.

## D-012 — Persistência sem `Salvar`

**Decisão**: cada arquivo é enviado numa requisição própria e persiste na hora; os campos pessoais e
a modalidade são gravados na transição para a revisão, que é o próprio `Revisar inscrição`. Nada de
gravação automática contínua e nada de rascunho em `localStorage`.

**Racional**: é a leitura mínima que satisfaz `FR-041`, `FR-049` e `SC-UX-007` ao mesmo tempo, e
depende só do que o navegador já faz. Gravação automática exigiria mecanismo, conflito e resolução —
para uma tela com quatro campos.

## D-013 — O protocolo

**Decisão**: `INS-<ano do envio>-<oito caracteres>`, alfabeto sem os pares ambíguos na leitura em voz
alta e na transcrição (`0`/`O`, `1`/`I`/`L`), sorteado por gerador criptográfico, com
`UniqueConstraint`; colisão recomeça a geração, no máximo um punhado de vezes, e depois falha alto.

**Racional**: `FR-062` pede único, legível e opaco, sem sequência global. Sequência exigiria
serialização entre inscrições concorrentes para produzir um número que ninguém precisa que seja
ordenado.

## D-014 — Estados, concorrência e idempotência

**Decisão**: `Inscricao` carrega `status` e `revision`; a transição para `SUBMETIDA` usa
`compare_and_swap`; o envio reserva idempotência com `reserve()` sob a operação
`inscricao:submeter:<id>`; e as três unicidades — inscrição por identidade/Edital/Perfil, documento
por inscrição/requisito, protocolo — são `UniqueConstraint` no banco.

**Racional**: `record_event` lê `aggregate.status` e `aggregate.revision`
(`auditoria/application.py:26-28`), então os dois campos são a condição de reusar a auditoria como
está. `IdempotencyRecord` é único por `(escopo, ator, operação, chave)` e não pressupõe ator
institucional. Nenhum mecanismo novo.

**Ator do candidato**: um `Actor` com o subject da identidade externa, o escopo institucional do
Processo alvo e **conjunto de permissões vazio**. Ele existe para atravessar idempotência e
auditoria; `require_permission` o recusa em qualquer comando administrativo, que é a propriedade
desejada. O campo `permission` do registro de auditoria recebe o rótulo da operação
(`inscricao:submeter`), que não é permissão concedida a ninguém — e essa distinção fica escrita no
próprio módulo.

## D-015 — A versão reconhecida pelo rascunho

**Decisão**: a Inscrição guarda duas referências de versão consolidada — a **reconhecida**,
atualizada a cada confirmação do candidato, e a **aceita**, gravada uma vez no envio.

**Racional**: sem a primeira, `FR-059` só sabe comparar com a vigente e reavisaria a cada tentativa
de envio; com ela, a confirmação vale até que outra versão passe a vigorar. Sem a segunda, não há o
que a Constituição exige de cada Inscrição: sob qual regra a pessoa se inscreveu.

## D-016 — `no-store` nas respostas com dado pessoal

**Decisão**: decorador aplicado às views do portal que exibem dados da inscrição e às duas telas
administrativas da US6, além da entrega de arquivo. Não é middleware global.

**Racional**: middleware global marcaria também a vitrine pública, que é conteúdo institucional
cacheável e é justamente o que se quer barato. A marcação explícita diz, no ponto, que aquela
resposta tem dado pessoal.

## D-017 — Uma linguagem visual, dois canais

**Decisão**: o bloco de tokens do `<style>` de `interface/templates/interface/base.html` sai para uma
parcial de template compartilhada, incluída pelo `<style>` das duas bases. Cada base mantém as suas
regras; o portal nasce com as consultas de mídia que `FR-079` exige e que o produto ainda não tem —
o estilo atual não tem nenhuma.

**Racional**: é a menor mudança que evita duas paletas divergindo. Extrair a folha inteira para
arquivo estático mexeria em todas as telas administrativas sem que nada nesta feature peça; duplicar
os tokens garante divergência na primeira mudança de cor.

**Acessibilidade**: o portal herda o padrão já vigente — link de pular, foco visível, contraste
declarado, rótulo e erro associados ao campo. Não há padrão novo a inventar, e `FR-080` é
verificação, não construção.
