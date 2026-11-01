# Research: Kit de Divulgação do Edital

Decisões técnicas do plano, cada uma com a razão e a alternativa descartada. As medidas vêm da
[POC de 31/10/2026](../../doc/poc-kit-de-divulgacao-2026-10-31/README.md), sobre o corpus da `070`
republicado pelo fluxo real.

## D-001 — Uma spec integrada, em três incrementos

- **Decision**: uma feature só, entregue em três incrementos, cada um demonstrável pela interface.
  - **A** — ficha, kit textual, tela, porta e rastreabilidade: FR-3401 a FR-3421, FR-3435 a FR-3436,
    FR-3439 a FR-3448, nos formatos `md` e `txt`. É o produto permanente.
  - **B** — peça SVG e PNG, depois da verificação do motor: FR-3422 a FR-3434, e a FR-3438 no que toca
    à peça.
  - **C** — ZIP, manifesto e galeria de revisão: a FR-3437, a FR-3438 no que toca ao pacote e a
    SC-1054.
- **Rationale**: a ficha é o núcleo e não depende da peça, enquanto a peça depende da ficha e de duas
  entradas externas, a marca e o motor. Partir em incrementos deixa o A útil enquanto o B espera a P-3
  e a P-4, sem duas features a manter separadas. É o pedido do usuário, que recusou dividir a
  funcionalidade.
- **Alternatives considered**:
  - **duas specs (textual e visual)**: recusada pelo usuário, e artificial, porque as duas
    compartilham ficha, tela, porta e registro;
  - **um incremento só**: atrasaria o textual até a marca chegar.

## D-002 — A ficha mora no portal; as leituras de que ela precisa descem para `publicacoes`

- **Decision**: `processo_seletivo/portal/ficha.py`, módulo de leitura sem gravação. Antes dele, três
  leituras mudam de lugar, **sem mudança de comportamento**, para que a ficha não importe nada da
  `interface/`:
  1. `retificacoes_a_vigorar` sai de `interface/agenda.py` para `publicacoes/application/selectors.py`,
     ao lado de `effective_version` e `versoes_vigentes`. A agenda passa a importar de lá;
  2. a comparação original × vigente sai de `interface/relatorio_do_edital.py` (`_versoes` e a regra em
     linha de `fatos_do_edital`) para `publicacoes/application/selectors.py`, como
     `versoes_original_e_vigente` e `prorrogacao(original, vigente)`. O relatório passa a usá-las, e a
     cópia em linha desaparece;
  3. `origens` e `acrescimos` saem de `duvidas/domain/origem.py` para `publicacoes/domain/origem.py`,
     com a `070` importando de lá.

  A ficha usa ainda `periodo_de_inscricoes`, `desfechos`, `leitura.situacao_publica`,
  `leitura.quantidade_da_oferta`, `TIPOS_COM_RESERVA`, `vagas_do_conteudo` (`interface/visao_geral.py`,
  a única importação da interface, e só de função pura) e `identificacao.do_ato`. A numeração
  "Retificação nº N" é a do relatório, por `published_at`, também movida para `publicacoes`.

  A equivalência com a página é garantida **por teste** (FR-3407). A página não é reescrita para
  consumir a ficha.
- **Rationale**:
  - O `portal/leitura.py` já é "o que duas telas leem", e o seu cabeçalho registra o custo de duas
    verdades sobre "em curso". A ficha é a terceira leitora, e mora junto.
  - A revisão independente mostrou que a ficha da POC importava `interface/agenda.py` e
    `interface/relatorio_do_edital.py`. O segundo carrega classificação, convocação, ocupação e
    recursos, e o portal passaria a depender da gestão.
  - A revisão mostrou também que a POC lia `ProvenienciaConteudo` pelo caminho exato, exatamente a
    leitura que `duvidas/domain/origem.py` documenta como errada: a tabela só acrescenta, e o Perfil
    substituído inteiro guarda registro antigo.
  - As leituras movidas são consultas e funções puras sobre conteúdo publicado. Nenhum comando de
    publicação muda (FR-3405).
- **Alternatives considered**:
  - **ficha em `interface/`**: a ficha deixaria de poder servir à página;
  - **ficha em `publicacoes/application`**: a situação pública é regra do portal;
  - **deixar as leituras onde estão e importá-las**: dependência portal → interface;
  - **página consumindo a ficha agora**: adiada, e só vale se uma terceira divergência aparecer.

## D-003 — Modos da ficha, sem abstração de marco

- **Decision**: a ficha tem três modos: com período, neutro e sem material (FR-3410). Um marco futuro,
  como o resultado publicado, entra como **modo novo**, com os seus campos e as suas regras de texto,
  quando tiver spec.
- **Rationale**:
  - O usuário pediu que a arquitetura admita outros marcos sem obrigá-los às regras de inscrição e
    sem abstração antecipada.
  - Os marcos não compartilham fonte: resultado é por Perfil × etapa × lista e nominal, e convocação
    não é publicada. Uma interface comum hoje seria desenhada sobre um caso só.
- **Alternatives considered**: um "Marco de comunicação" genérico com catálogo de tipos. Seria
  abstração sem segundo caso, e o tipo do Evento do cronograma é texto livre (`047`, RC-76).

## D-004 — Desatualização pela impressão dos campos, e não pelo resumo do conteúdo

- **Decision**: a impressão é o SHA-256 da serialização canônica só dos campos que o material afirma
  (FR-3411). A desatualização compara a impressão de cada exportação registrada com a de agora,
  agrupando por impressão (FR-3439).
- **Rationale**: a POC mediu as duas formas.
  - No 92/2026, uma Retificação que só mudou uma seção textual mudou o `content_hash` da versão e
    **não** mudou a impressão. Pelo resumo do conteúdo seria falso alarme; pela impressão, nenhuma
    faixa.
  - No 91/2026, a impressão mudou e o kit nomeou o término e as vagas de um polo.
- **Alternatives considered**: `content_hash`, que dá falso alarme a cada Retificação de cláusula, e o
  alarme que dispara sempre deixa de ser lido. O identificador da versão muda até em rematerialização
  sem mudança de conteúdo.

## D-005 — Registro pela trilha de auditoria, sem tabela nova

- **Decision**: cada exportação grava `record_event` com operação própria (`EXPORTAR_MATERIAL`) sobre o
  Edital. O registro segue três regras:
  - estado e revisão anteriores iguais aos atuais, como a emissão da `099`, porque não é transição;
  - o `detalhe` do [data-model](data-model.md);
  - o rótulo "Exportação do kit de divulgação" em `OPERACOES` (`interface/views.py`) e a operação em
    `OPERACOES_QUE_NAO_CONTAM` (`interface/relatorio_trilha.py`).

  O guardião da trilha legível passa a varrer também `interface/*.py`, de onde a `EMITIR_RELATORIO`
  já escapava.

  A leitura das exportações é `RegistroAuditoria.objects.filter(aggregate_type="Edital",
  aggregate_id=…, operation="EXPORTAR_MATERIAL").order_by("-occurred_at")`. Ela usa o índice
  `(aggregate_type, aggregate_id, occurred_at)`, e quem lê é o próprio kit, em nome de quem tem
  `material:gerar`, sem exigir `auditoria:consultar`. A faixa não diz quem exportou.
- **Rationale**:
  - O precedente de **ler o `detalhe`** funcionalmente é o `APLICAR_A_TODOS` (`interface/views.py`). A
    `099` só conta eventos.
  - A trilha já é append-only nas duas camadas e tem ator, instante e escopo. Não há migration nem
    tabela nova para o provisionamento contar.
  - Exportações concorrentes geram dois eventos, e a FR-3439 agrupa por impressão, de modo que a
    ordem entre eles não importa.
  - Os campos afirmados são dado público do ato, sem dado pessoal.
- **Alternatives considered**:
  - **tabela `GeracaoDeMaterial` no molde de `GeracaoDeArquivo` (`031`)**: consulta tipada, ao custo de
    migration, gatilho e privilégio, desproporcional a um evento por exportação;
  - **sessão do navegador**: perderia a desatualização entre pessoas e entre dias;
  - **filtro por operação na trilha do Edital**: fica como melhoria, se o volume diluir os atos
    normativos na leitura do auditor.

## D-006 — Nenhum arquivo guardado; determinismo como prova

- **Decision**: nada gerado é guardado. A prova do que saiu é a regeneração determinística:
  - o SVG é texto estável;
  - o ZIP tem data fixa em toda entrada e ordem fixa;
  - o PNG é do rasterizador com fontes fixas e sem fontes do sistema.
- **Rationale**: na POC, os 10 SVG e os 10 PNG foram idênticos entre duas gerações. Guardar arquivos
  numa tabela append-only acumularia para sempre peças de marca antiga, e daria duas verdades.
- **Alternatives considered**: guardar o PNG de cada exportação, com custo permanente de
  armazenamento e nenhum ganho de prova.

## D-007 — Motor: SVG composto em Python, PNG pelo `resvg-py`, depois de uma verificação

- **Decision**: a composição gera SVG. O PNG sai do `resvg-py`, com as fontes da Edital Sans
  passadas por arquivo e `skip_system_fonts=True`. A dependência só entra no `pyproject.toml` depois
  de uma verificação registrada em `verificacao-do-motor.md`, que cobre:
  1. **licença** do `resvg-py` e das dependências transitivas. O metadado do PyPI não a declara;
     o resvg é MIT/Apache-2.0;
  2. **Linux de implantação**: wheel para a arquitetura do servidor com Python 3.13, instalada na
     imagem;
  3. **fontes e caracteres**: a peça de cada cenário de referência, com caracteres acentuados, "º",
     "–" e "—";
  4. **segurança**: nenhum recurso externo resolvido (sem `resources_dir`, sem `href` fora de
     `data:`), e entrada sempre gerada pelo sistema;
  5. **reprodutibilidade**: o mesmo PNG em duas execuções no servidor. A comparação com o PNG do Mac é
     registrada, e não exigida;
  6. **lote pequeno**: 20 gerações seguidas, com o tempo de cada uma;
  7. **versão fixada** no `pyproject.toml` e no `uv.lock`.
- **Rationale**:
  - O resvg é o rasterizador de SVG mais conforme entre os embarcáveis, e roda sem biblioteca de
    sistema numa imagem que só instala `make`.
  - Na POC: 42–56 ms por peça, determinístico, com wheels para manylinux e musllinux em x86_64 e
    aarch64 (versão 0.5.0, de 24/08/2026).
  - Um teste já proíbe `import PIL` em `processo_seletivo/` (`tests/unit/test_leitura_do_documento_submetido.py`).
- **Alternatives considered**:
  - **CairoSVG**: exige `libcairo2` no sistema, e a imagem de produção não é versionada. **É a
    alternativa se o `resvg-py` reprovar na verificação.**
  - **Pillow**: barrado pelo guardião, e não desenha SVG, de modo que não haveria exportação SVG.
  - **Chromium em produção**: centenas de MB, processo por requisição, pixels que mudam com a
    versão.
  - **Rasterizador próprio**: rasterizar glifo TrueType com antisserrilhado é outro projeto.
  - **Rasterizar no navegador**: não reproduzível, e frágil sob a CSP.

**Se a verificação reprovar o `resvg-py` e o CairoSVG**, o incremento B entrega só o SVG e o kit
textual, e a P-4 volta ao usuário.

## D-008 — A composição é um modelo de caixas; o SVG é a serialização dele

- **Decision**: o compositor produz uma lista de elementos posicionados: texto com campo, corpo,
  peso, âncora e caixa medida; retângulos; linhas. Um serializador escreve o SVG a partir dessa
  lista.
  - Cada `<text>` leva `data-campo` com o campo da ficha de onde veio.
  - Os valores entram como nó de texto escapado, e nunca como atributo livre.
  - O teste geométrico (FR-3429) e as conferências de coerência (FR-3423) leem o modelo e o SVG.
- **Rationale**:
  - Na POC, as conferências sobre o SVG provaram coerência. O que escapou foi a geometria: o
    endereço passou da margem e a quantidade invadiu o rótulo.
  - Com as caixas explícitas, colisão e área útil viram aritmética, e o teste é barato e exato.
  - Um template Django não mede texto, e as posições dependem da medida.
- **Alternatives considered**: medir depois, rasterizando e procurando pixels, que é lento e frágil.

## D-009 — Medir e quebrar com a fonte e a regra do Edital, desenhando o texto medido

- **Decision**: a largura vem de `MetricaEmbutida` (`publicacoes/infrastructure/fonte.py`), e a quebra
  de `_quebrar` (`publicacoes/infrastructure/pdf.py`), por um **apelido público** acrescentado ao lado,
  sem renomear nem tocar o corpo da função.
  - O texto desenhado é o texto **normalizado** por `grafia.normalizar`, o mesmo que a métrica mediu.
  - Uma quebra que parta palavra é tratada como "não cabe" (FR-3429).
- **Rationale**:
  - Uma medida só para quebrar e para desenhar.
  - O apelido não muda nenhum byte do Edital, e as fixtures de contrato do PDF o provam.
  - A revisão mostrou que a métrica mede o texto normalizado e o rasterizador recebia o cru, e que a
    `_quebrar` parte palavra longa. Um endereço partido no rodapé mudaria o destino.
- **Alternatives considered**:
  - **reimplementar a quebra no kit**: seria a segunda regra de quebra do sistema;
  - **renomear `_quebrar`**: toca o compositor do ato sem necessidade.

## D-010 — Marca oficial versionada; a peça liga por ambiente, depois da aprovação do template

- **Decision**:
  - Os ativos oficiais (P-3) entram versionados ao lado do compositor, com um `ORIGEM.md` que diz
    procedência, manual e licença de uso, como as fontes do Edital.
  - A chave de ambiente `KIT_DE_DIVULGACAO_PECA` liga a peça: ligada em desenvolvimento e teste, com
    o marcador declarado enquanto não há ativo, e **desligada em produção** até a aprovação (P-6).
    Produção não recusa subir sem ela.
  - A aprovação é do **template** (SC-1054), uma vez. Mudar o template é nova versão, com SVGs de
    referência atualizados e nova revisão humana.
  - Peça a peça não há aprovação.
- **Rationale**:
  - A marca não existe no repositório, e inventá-la foi o defeito M9 da análise de 12/10.
  - A chave separa o que já se pode entregar (o textual) do que espera a comunicação, no precedente
    exato dos avisos (`066`, `AVISOS_AOS_CANDIDATOS`).
- **Alternatives considered**:
  - **produção sem peça até a marca, sem chave**: exigiria deploy para ligar;
  - **aprovação por peça**: recusada pelo usuário e pelo estudo (Eixo I).

## D-011 — Endereço: o da requisição; na peça e na legenda, caminho curto e busca

- **Decision**:
  - O link vem de `request.build_absolute_uri` sobre a rota da seleção, como nos avisos.
  - A peça e a legenda trazem o caminho curto da vitrine ("domínio/selecoes") e "busque por N/AAAA – SIGLA".
  - O resumo e o texto para mensagens trazem o link completo e as âncoras por Perfil.
- **Rationale**:
  - Não há setting de endereço absoluto, e a geração é sempre numa requisição.
  - O endereço da seleção é um UUID que ninguém digita, e link em legenda de rede social não é
    clicável. A busca pelo número existe e leva à mesma página (`portal/leitura.py`). Como o número só é único por unidade (`uq_edital_scope_number_year`), a busca leva a sigla (EC-24).
- **Alternatives considered**:
  - **setting novo de URL base**: só necessário fora de requisição, o que não acontece;
  - **QR Code**: inútil numa peça vista no próprio celular, e pediria dependência (estudo, Eixo E).

## D-012 — Capacidade própria, papel restrito, negar por padrão

- **Decision**:
  - A capacidade é `material:gerar`, num papel `comunicacao` ("Comunicação", P-1) que só a carrega.
  - Ela entra no catálogo de papéis e descrições (`interface/identidade.py`), atribuível pela gestão
    de acessos da `107`, e não é concedida a nenhum papel existente.
  - A porta confere escopo e capacidade, no roteiro das views da gestão (`obter_edital` + base de
    permissão), e entra no inventário das negativas da `033`.
- **Rationale**:
  - Precedentes: `exportador` (`031`) e `participante-piloto-assistente` (`071`).
  - Quem divulga não pratica ato: a capacidade não toca a segregação de elaborar, homologar e
    publicar.
- **Alternatives considered**:
  - **reaproveitar `visao:consultar`**: daria o kit a todo `gestor` e a visão a toda a comunicação;
  - **capacidade dentro de `publicador`**: misturaria ato oficial com divulgação.

**O que a capacidade não resolve (P-2).** A lista, o detalhe e a prévia do rascunho de Edital da
unidade se abrem hoje a qualquer pessoa da unidade (`interface/views.py`, `lista`, `detalhe`,
`_edital_com_previa`). A tela do kit lê só o publicado, mas a pessoa do papel chega ao kit pelo
detalhe, e vê o que a política vigente mostra a qualquer integrante. Corrigir isso muda a leitura de
todos os papéis. O usuário o encaminhou, em 01/11, a uma spec própria, que define quem lê conteúdo
não publicado e o verifica no backend. Uma entrada própria do papel na barra **não** substitui essa
verificação: as URLs do detalhe e da prévia continuariam abertas por acesso direto.

## D-013 — Manchete: escolha numa lista fechada, só quando falta título

- **Decision**: quando nenhum título oficial cabe (FR-3426), a tela oferece uma lista de manchetes
  derivadas da ficha, das quais a pessoa escolhe uma. A lista tem:
  - o nome comum das opções, quando todas têm o mesmo nome;
  - o nome de cada opção, quando há até quatro;
  - "nome — localidade" da opção única.

  Só entram as que cabem e passam a FR-3414. Não há texto livre. A escolha viaja na requisição, entra
  só na peça e é registrada na exportação. Nada é guardado no Edital.
- **Rationale**:
  - O usuário pediu "manchete curta controlada, sem alterar os dados oficiais nem introduzir
    afirmações não comprovadas".
  - A revisão independente mostrou que o texto livre com filtros (sem algarismo, sem endereço,
    vocabulário) deixava passar "Curso gratuito para todo o país". Só a lista fechada cumpre o "sem
    afirmação não comprovada".
  - Na POC, o título do Processo bastou nos três Editais, e a manchete é a terceira opção, e rara.
- **Alternatives considered**:
  - **texto livre com filtros**: recusado pela revisão;
  - **campo novo no Edital**: seria mudança normativa e passaria por Retificação;
  - **sem manchete**: contraria o pedido, e deixa sem título o Edital de título longo com Processo
    longo.

## D-014 — Prévia por imagem da própria origem; SVG só na exportação

- **Decision**:
  - A prévia é um `<img>` que pede por GET o PNG ao endpoint do kit, com a impressão conferida na
    query (FR-3446), sem registrar. A CSP aceita porque é `'self'`.
  - O SVG sai só na exportação, como anexo, com `X-Content-Type-Options: nosniff` e uma política
    própria, `default-src 'none'; style-src 'unsafe-inline'; font-src data:`, que admite só a fonte
    embutida (D-021). A política do projeto só se aplica a `text/html`.
- **Rationale**: SVG embutido no HTML seria desenhado pelo navegador com outra fonte, e a prévia
  divergiria do PNG. Servido como imagem, ele é o mesmo arquivo da exportação.
- **Alternatives considered**: `data:` na prévia, recusado pela CSP (`img-src 'self'`).

## D-015 — Copiar por script em arquivo, sem registro

- **Decision**: um script estático usa a API de área de transferência, com um botão nativo por texto e
  `aria-live` para "Copiado". Sem script, os textos ficam em `<pre>` selecionável. Copiar não
  registra (P-5).
- **Rationale**: a CSP proíbe script embutido. O registro por cópia exigiria envio assíncrono para um
  gesto que não produz arquivo, e o kit textual já registra quando exportado.
- **Alternatives considered**: registrar a cópia por `fetch`, que fica para a P-5.

## D-016 — Qualidade gráfica: quatro redes, duas humanas

- **Decision**:
  1. **teste geométrico** sobre o modelo de caixas (FR-3429), nos cenários de referência e em casos
     sintéticos no limite: título de 60, 120 e 210 caracteres; rótulo de opção de 90; endereço de 60;
     4, 5 e 66 opções;
  2. **SVG de referência** dos cenários de referência em `tests/fixtures/kit_referencias/`. Mudar o template
     muda o arquivo, e o diff passa por revisão;
  3. **galeria** dos cenários de referência, gerada por comando de demonstração, para a revisão da
     comunicação (SC-1054);
  4. **conferência de um Edital real** pela comunicação (SC-1058).
- **Rationale**: na POC, as conferências automáticas ficaram verdes com quatro defeitos visuais, e
  só a inspeção os pegou. Geometria e revisão humana cobrem coisas diferentes.
- **Alternatives considered**: comparação de pixels do PNG, que varia por rasterizador e plataforma e
  é frágil.

## D-017 — A varredura de vocabulário lê o material gerado, em todos os estados

- **Decision**: o teste de vocabulário gera o kit de cada cenário de referência e varre as frases fixas, a composição e as manchetes, nos textos e em cada nó da peça. Os valores
  literais da ficha não são reprovados: a conferência os aponta (FR-3414, EC-26). As frases fixas também ficam numa lista nomeada, para o diff mostrar
  mudança de redação.
- **Rationale**: o template quase não tem texto, e a frase nasce da combinação de forma fixa com
  valor. É a lição da varredura de vocabulário com lista literal: tela nova escapa da regra que só
  lê templates.
- **Alternatives considered**: varrer os módulos de texto, o que não vê a frase composta.

## D-018 — Impressão versionada, com a identidade de cada Perfil e sem host

- **Decision**: a impressão leva um número de versão (`versao_da_impressao`, começando em 1),
  registrado no evento junto dos campos. Os campos têm três regras:
  - cada oferta carrega o `perfil_id`;
  - as ofertas entram ordenadas pela identidade, e não pela ordem publicada;
  - o endereço entra só pelo **caminho**.

  Exportação com versão de impressão diferente da atual é comparada recalculando a impressão nova a
  partir dos campos gravados. Se faltar campo, a faixa diz "material de versão anterior do kit:
  confira" (FR-3448).
- **Rationale**: a revisão mostrou três falsos alarmes possíveis.
  - Mudar a serialização mudaria toda impressão no dia do deploy.
  - Sem a identidade, Perfil renomeado vira "retirado + acrescentado", e reordenar sem mudar nada
    dispararia a faixa.
  - Abrir a gestão por http e https, ou por outro nome, mudaria o host.
- **Alternatives considered**: impressão sem versão, que é o falso alarme em massa na primeira
  evolução.

## D-019 — Um instante conferido, levado da tela à exportação

- **Decision**: a tela calcula a ficha e põe a impressão conferida na URL da prévia e num campo oculto
  do formulário de exportação. A prévia e a exportação recalculam a ficha no instante delas. Se a
  impressão diferir, recusam com 409 e "o Edital mudou desde que você abriu o kit" (FR-3446).
- **Rationale**: tela, prévia e exportação são três requisições. Na passagem de uma vigência, a
  pessoa conferiria X e baixaria Y. A recusa obriga a reabrir e conferir o novo.
- **Alternatives considered**: congelar o instante da tela e reusá-lo na exportação. A exportação
  afirmaria uma versão que já não vigora no instante do download.

## D-020 — Host local não produz link nem peça

- **Decision**: a regra `HOSTS_LOCAIS` / `_host_local` de `interface/relatorio.py` (`099`/`100`) é
  reaproveitada. Em host local, os textos saem sem link absoluto, a peça não é gerada e a tela diz por
  quê (FR-3447).
- **Rationale**: o endereço vem da requisição (D-011), e uma peça com "localhost/selecoes" é destino
  falso numa imagem que circula. O relatório já resolveu isso do mesmo jeito.
- **Alternatives considered**: setting de endereço público, que fica para a P-9.

## D-021 — O SVG exportado embute a fonte

- **Decision**: o SVG exportado leva um `<style>` com `@font-face` em `data:` com a Edital Sans
  (subconjunto WinAnsi, sob OFL), regular e negrito. O PNG não precisa, porque o rasterizador recebe
  as fontes por arquivo. A política do anexo SVG admite só essa fonte (D-014).
- **Rationale**: a revisão mostrou que o SVG da POC dizia `font-family="Edital Sans"` sem a fonte.
  Aberto no navegador, no Inkscape ou numa ferramenta de design, ele desenharia com outra fonte, e as
  caixas medidas extravasariam: o arquivo entregue deixaria de ser "a mesma composição" (FR-3422). A
  OFL permite embutir.
- **Alternatives considered**:
  - **tirar o SVG do MVP**: contraria o pedido, que inclui SVG;
  - **converter texto em contorno**: o SVG perderia o texto, e com ele a acessibilidade e a
    conferência por `data-campo`.

