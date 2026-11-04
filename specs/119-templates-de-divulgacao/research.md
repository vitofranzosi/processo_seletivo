# Research: Templates de Divulgação por Família e Formato

As decisões técnicas desta spec. As decisões de produto são as T-1 a T-9 do
[estudo](../../doc/estudo-templates-de-divulgacao-2026-11-04.md), aceitas em 04/11/2026, e não se
repetem aqui. Cada decisão abaixo traz o que foi decidido, por quê, e o que foi descartado.

## D-001 — Três incrementos, na ordem do estudo

**Decisão**: (1) motor generalizado sem mudar a peça; (2) Pós Lato Sensu nos três formatos, com a
ficha versão 2, a escolha na tela e a galeria por template; (3) as demais famílias, uma por PR —
FIC, Libras, UAB/bolsista, Aperfeiçoamento, Internos, TMD.

**Por quê**: o incremento 1 isola o risco de regressão numa peça que já está em aprovação; a prova é
a referência byte a byte. A Pós Lato Sensu tem uma fonte só (Poppins), estrutura simples e o maior
número de exemplos. Uma família por PR mantém a revisão visual humana em tamanho legível.

**Descartado**: entregar as sete famílias de uma vez (21 templates num PR, revisão inviável);
começar pela FIC (três fontes, faixa de situação e contato: a família mais complexa).

## D-002 — A peça da `111` vira a família Institucional, com o mesmo identificador de template

**Decisão**: a declaração da família Institucional reproduz as constantes de hoje (cores, faixas,
corpos, recaídas). O identificador `feed-1080x1350 · 1` não muda, e as exportações registradas
continuam comparáveis.

**Por quê**: o identificador entra no manifesto e na trilha; mudá-lo sem mudar a peça seria registrar
uma diferença que não existe.

**Descartado**: redesenhar a Institucional na mesma passada (misturaria generalização com mudança
visual, e a referência deixaria de provar nada).

## D-003 — Família é módulo Python declarativo, não arquivo de dados

**Decisão**: cada família é um módulo em `interface/kit_familias/` que constrói objetos imutáveis
(`Familia`, `Template`, `Caixa`), registrados num dicionário único.

**Por quê**: a declaração passa pelo `ruff`, é importada pelos testes sem leitor próprio, e um erro de
digitação quebra na importação, e não na primeira geração. As famílias mudam por PR, nunca pela
tela.

**Descartado**: JSON ou YAML (exigiria esquema e validador próprios, sem ganho: ninguém edita fora do
código); tabela no banco (a comunicação não edita templates pelo sistema, e a Constituição pede
simplicidade).

## D-004 — O template declara caixas; formas decorativas são ativos

**Decisão**: o compositor só conhece caixas de texto, retângulos, linhas e imagens, como na `111`.
Balões, manchas, chevrons, losangos e moldura de foto são **ativos SVG fixos** da família,
posicionados pelo template e embutidos como estão. Recorte de foto em círculo ou losango é um
`clipPath` declarado pela família.

**Por quê**: a geometria testável é a do texto; o desenho fixo é aprovado uma vez, com o template. O
balão de altura variável do Lato Sensu é retângulo arredondado mais a ponta como ativo — a altura vem
da caixa medida.

**Descartado**: um interpretador de formas no compositor (superfície grande, sem teste geométrico
útil).

## D-005 — Fontes da família num módulo próprio, sem tocar a fonte do ato

**Decisão**: `interface/kit_fontes.py` lê cada TrueType com o leitor que `publicacoes` já tem e
expõe uma métrica por fonte. Os subconjuntos ficam em `kit_ativos/fontes/`, com `ORIGEM.md` e o
resumo de cada arquivo. O texto continua normalizado pela `grafia` da `111`, e cada subconjunto cobre
o repertório dela; o que faltar recusa, nomeando caractere e fonte (FR-3823). O rasterizador recebe
as fontes da família por arquivo, sem fontes do sistema.

**Por quê**: a métrica e o subconjunto da Edital Sans servem ao ato publicado. Ampliá-los para o kit
arriscaria o compositor do PDF, que é o documento oficial.

**Descartado**: registrar as fontes do kit em `publicacoes/infrastructure/fonte.py` (acoplamento com
o ato); deixar o rasterizador usar fontes do sistema (PNG diferente por máquina).

## D-006 — Imagens reduzidas fora do repositório, embutidas em `data:`

**Decisão**: a comunicação entrega a imagem licenciada; ela é reduzida ao tamanho de uso uma vez, com
o `sips` do macOS como as marcas da `111`, e versionada com origem, licença, aprovação e resumo. O SVG
a embute em `data:`, que a política do anexo SVG da `111` já admite. JPEG para foto, PNG para
ilustração.

**Por quê**: o projeto não usa `PIL`; o tratamento é uma vez por imagem, e o resultado é o que se
aprova. Embutir mantém o SVG inteiro em si e o rasterizador sem acesso externo.

**Descartado**: redimensionar em tempo de geração (dependência nova e bytes variáveis por versão da
biblioteca).

## D-007 — Banner a 1500 × 850 até a resposta da comunicação

**Decisão**: o formato banner é declarado em 1500 × 850, o dobro dos 750 × 425 do arquivo, e nenhum
banner é liberado antes da P-3.

**Por quê**: o dobro cobre tela de alta densidade sem mudar a proporção; trocar o tamanho depois é
mudança de uma declaração de formato e das referências do banner.

**Descartado**: esperar a resposta para começar (bloquearia o incremento 2 inteiro por um número).

## D-008 — A escolha não é guardada; vai no evento da exportação

**Decisão**: o `detalhe` do evento de exportação da `111` ganha `familia`, `familia_versao`,
`variante`, `formato_da_peca`, `template`, `template_versao`, `imagem` e `imagem_sha256`. A
pré-escolha da tela lê o evento de exportação **de peça** (PNG, SVG ou ZIP com peça) mais recente do
Edital; as exportações de texto não trazem família.

**Por quê**: é a regra da `111` (nada guardado, manchete registrada), e o registro já existe. Ler a
última exportação dá a continuidade que a comunicação espera sem campo novo no Edital.

**Descartado**: guardar a família no Edital ou no Processo (mudança de modelo; T-2 a deixa para
depois).

## D-009 — Impressão versão 2, com a versão 1 calculada da ficha atual

**Decisão**: a ficha calcula as duas impressões. Exportação registrada na versão 1 é comparada com a
versão 1 da ficha atual; na versão 2, com a versão 2. A faixa da diferença usa os `campos` gravados.

**Por quê**: a regra da `111` para versão anterior — "material de versão anterior do kit: confira" —
acenderia em toda exportação já feita, no dia da implantação, sem mudança nenhuma. Calcular a v1 da
ficha atual é exato, porque a v2 só acrescenta campos.

**Descartado**: migrar os eventos gravados (a trilha é append-only).

## D-010 — Uma configuração nova lista os templates liberados, com a versão

**Decisão**: `KIT_DE_DIVULGACAO_TEMPLATES`, lista de `familia/formato@versao`, vazia em produção, e
em desenvolvimento e teste preenchida a partir do registro (todos, na versão do código). Entrada
malformada ou desconhecida recusa a subida das settings. A `KIT_DE_DIVULGACAO_PECA` continua valendo
para a Institucional, sem mudança.

**Por quê**: a chave booleana da `111` não distingue templates, e mudá-la de tipo quebraria a
implantação que a lê. A liberação é da operação (P-4), como na `111`.

**Descartado**: liberar por família inteira (o banner espera a P-3 mesmo com o post aprovado);
liberar sem versão (uma troca de foto herdaria a aprovação anterior em silêncio).

## D-011 — Contraste e sobreposição contra caixas de cor lisa

**Decisão**: toda caixa de texto declara a cor do fundo sobre a qual fica, e o teste calcula a razão
AA pelas duas cores declaradas. A área da imagem e dos ativos decorativos entra no teste geométrico
como obstáculo.

**Por quê**: contraste medido sobre foto não é determinável sem rasterizar e amostrar; proibir texto
sobre foto torna a regra verificável e segue o que os templates já fazem.

**Descartado**: amostrar o PNG (frágil e lento).

## D-012 — "Formato da peça" não é "formato do arquivo"

**Decisão**: a rota de exportação da `111` já usa `formato` para o tipo de arquivo (`png`, `svg`,
`md`, `txt`, `zip`). O formato desta spec vai em `formato_da_peca` (`post`, `story`, `banner`), no
formulário e na consulta da prévia.

**Por quê**: evita mudar a rota existente e a confusão entre os dois.

## D-013 — A varredura de vocabulário lê o registro de famílias

**Decisão**: o teste de vocabulário do kit itera sobre todas as famílias registradas e todas as suas
frases fixas, com a lista da FR-3414 da `111` e os termos da FR-3814.

**Por quê**: uma lista literal de frases deixaria família nova escapar da regra em silêncio.

## D-014 — Resumo do template fixado por versão

**Decisão**: o resumo de um template é o SHA-256 da sua declaração em JSON canônico (caixas, frases,
paleta, recortes, posições) concatenada aos resumos, em ordem, dos ativos, imagens do banco e fontes
que ele usa. O módulo da família guarda `RESUMOS = {(formato, versao): "<sha>"}`. Um teste recalcula
e compara: alterar qualquer insumo sem subir a versão, ou subir a versão sem gravar o resumo,
reprova. A galeria imprime o identificador, a versão e os doze primeiros caracteres do resumo em
cada peça, e a aprovação registrada em `verificacao.md` cita os três (FR-3833, FR-3834).

**Por quê**: a liberação nomeia uma versão (D-010), e a versão só significa alguma coisa se nomear um
conteúdo único. O resumo fixado transforma "esqueci de subir a versão" em falha de suíte, e não em
aprovação herdada em produção. Tudo fica no código e na documentação: nenhuma tabela, nenhum fluxo
de aprovação no sistema.

**Descartado**: confiar na disciplina de subir a versão (é exatamente o erro que se quer evitar);
registrar a aprovação no banco (fluxo novo sem necessidade: quem libera é a operação, por
implantação).

## D-015 — O ZIP de família lista cada formato, incluído ou não

**Decisão**: para família da comunicação, o manifesto ganha `versao_do_manifesto: 2` e a lista
`pecas`, uma entrada por formato da família, com template, versão, resumo, inclusão, motivo e
arquivos (data-model). O evento da exportação leva a mesma lista. Os arquivos levam o formato no
nome. O ZIP da Institucional não muda.

**Por quê**: com vários formatos, "a peça foi incluída?" deixa de ter resposta única; a auditoria
precisa reconstruir que post e que story saíram, em que versão, e por que o banner não saiu. Manter o
ZIP da Institucional intacto preserva as exportações e os testes da `111`.

**Descartado**: um ZIP por formato (três envios e três registros para o que a comunicação baixa de
uma vez); campos singulares repetidos com sufixo (ilegível e sem lugar para o motivo por formato).
