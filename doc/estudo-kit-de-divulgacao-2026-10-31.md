# Estudo de viabilidade: Kit de Divulgação de Processos Seletivos

**Data:** 2026-10-31 · **Commit:** `81ce6e94` (main) · **Natureza:** diagnóstica — nada foi
implementado, nenhuma spec foi aberta, nenhuma regra mudou.

> **Não vira escopo por estar escrito aqui.** Aprovar, recortar e ordenar é do responsável pelo
> produto. Este estudo para aqui e aguarda decisão antes de qualquer especificação.

> **Atualização do mesmo dia.** Depois deste estudo, o produto decidiu que o kit entrega **textos e
> peça juntos**, os dois derivados de uma ficha única, e não em duas etapas. A
> [POC integrada](poc-kit-de-divulgacao-2026-10-31/README.md) prova essa arquitetura e recomenda
> **uma spec integrada**. Onde as duas divergem sobre o recorte, vale a POC. Os eixos A a J continuam
> sendo a base de evidência.

Convenção de certeza usada em todo o documento:

- **Fato**: verificado no código, com caminho.
- **Inferência**: conclusão a partir de fatos, sem medição.
- **Hipótese**: depende de validação com a comunicação institucional ou de medição.

Caminhos relativos a `backend/processo_seletivo/`, salvo indicação.

---

## 0. Veredito em uma frase

**Implementar com ajustes, em duas etapas.** Primeiro uma *ficha de divulgação*: textos e dados
oficiais, com selo de versão e aviso de desatualização. Ela não pede dependência nova e reaproveita
quase tudo o que a página pública já calcula. As **peças visuais** ficam para uma segunda spec,
condicionada a três entradas que hoje não existem:

- os ativos oficiais de marca;
- o aceite da comunicação sobre um template;
- a decisão sobre a dependência de rasterização.

O motivo é que o risco da proposta não está no desenho, e sim em **afirmar, numa imagem que circula
por semanas, o que o sistema não comprova** — e essa parte se resolve sem desenho nenhum.

---

## 7.1 Resumo executivo

**Recomendação: implementar com ajustes.**

| | |
|---|---|
| **Benefícios esperados** | Dados conferidos na origem: número, período vigente, oferta por Perfil, localidade e link oficial. Chamadas que o sistema comprova no instante da geração. Texto alternativo pronto. Selo que liga cada material a uma versão do Edital. Aviso quando uma Retificação o torna antigo |
| **Principais riscos** | (1) Chamada que expira sem que a peça saiba — "inscrições abertas" numa imagem repostada depois do prazo. (2) Inexistência de marca oficial no repositório. (3) Rasterização exige dependência nova e revisão de um guardião. (4) Volume e adoção não demonstrados: o sistema não está em produção |
| **Complexidade** | Etapa 1 (ficha): **baixa a média**, toda reaproveitamento. Etapa 2 (peças): **média a alta**, quase toda nova (motor, template, ativos, testes visuais) |
| **Condições para avançar** | Etapa 1: decidir a capacidade e o vocabulário das chamadas. Etapa 2: manual ou ativos de marca fornecidos, um template aprovado pela comunicação, decisão sobre `resvg-py` ou Pillow, e pelo menos um Edital real divulgado com a ficha |

---

## 1. O que o sistema já sabe, e o que não sabe

O GPS já faz quase todo o trabalho difícil do kit, por outro motivo: a **página pública da seleção**
precisou resolver as mesmas perguntas, e as resolveu com regra escrita e testada. Quatro decisões já
pagas valem diretamente para um criativo:

1. **Só a versão vigente é fonte** — *Fato*.
   - `effective_version(edital_id, at)` (`publicacoes/application/selectors.py:27`) devolve a
     `VersaoConsolidada` com `valid_from <= at`.
   - As tabelas relacionais ficam no estado do dia da publicação, porque a Retificação não as
     reescreve (`interface/visao_geral.py:445-447`; `interface/views.py:1771`).
   - Um gerador que lesse `PerfilVaga` ou `EventoCronograma` divulgaria o Edital **original**
     depois da primeira Retificação.
2. **O desfecho vence o período** — *Fato*.
   - `portal/leitura.py:239` (`situacao_publica`).
   - Até a `047`, um Edital cancelado dentro do prazo anunciava "Aberta — faltam 19 dias"
     (`FR-761`).
3. **A oferta é por Perfil, não a soma** — *Fato*. `portal/views.py:410-420` e
   `leitura.quantidade_da_oferta` (`portal/leitura.py:571`). "3 vagas" num cartão de dois Perfis
   se lia como três para cada um (`072`, `FR-1607`).
4. **Muitos Perfis cabem com teto e "+N"** — *Fato*. `leitura.os_primeiros` (`portal/leitura.py:586`),
   com o teto de 5 do resumo da oferta.

O que o sistema **não** sabe, e que a proposta supunha (*Fato*, salvo indicação):

| Suposto pela proposta | Realidade no código |
|---|---|
| "Modalidade ou tipo de seleção" | **Não existe taxonomia de natureza do Processo** (`processos/models.py:74-77`). A `072` deixou "curso, cargo, bolsa" como questão a estudar (Q4) |
| "Curso" | Não há campo. O curso está no `name` do Perfil, texto livre, e a `069` (`FR-1365`) proíbe escrever "curso", "polo" ou "turma" que não estejam no dado |
| "Campus" | Não há campo. Há `locality`, texto livre por Perfil (`editais/models/perfis.py:26`), e **uma** Unidade por Edital |
| "URL da página oficial" | Existe e é estável: `/selecoes/<uuid>/` (`portal/urls.py:120`). **Não é legível**: 36 caracteres de UUID, impossível de digitar a partir de uma imagem |
| "QR Code" | Nenhuma biblioteca, nenhum uso |
| "Inscrição externa" | **Não existe o conceito.** O mais próximo é `NAO_DESIGNADO`, um Edital sem período designado (`inscricoes/domain/periodo.py:51-60`); o sistema não sabe onde nem quando essa inscrição acontece |
| "Resultados publicados" como marco do Edital | Resultado é publicado **por Perfil × marco × lista** (`divulgacao/models.py:35`), preliminar ou definitivo. Não existe "resultado do Edital" |
| "Convocação" como marco público | **O sistema não publica convocação** (`convocacao/models.py:374-383`; `047`, `:612`; `072`, `:541`) |
| Marca institucional | Só o brasão da República, PNG de 60×59 px (`publicacoes/infrastructure/brasao.png`). Não há logo do Ifes nem do GPS. A identidade visual é a questão Q2 da auditoria de 12/10, em aberto |
| Gatilho pós-publicação | Não há sinal, evento nem fila depois de publicar ou retificar (busca por `Signal`, `receiver`, `on_commit`). O que existe é a trilha (`record_event`) |

**Aviso de nome** — *Fato*. O app `divulgacao/` publica **resultados**
(`PublicacaoResultado`), e não faz marketing. Uma feature chamada "Kit de divulgação" que
morasse num módulo `divulgacao` criaria ambiguidade com o vocabulário do domínio. A recomendação é
outro nome de módulo (§7.9).

---

## 7.2 Inventário técnico

| Componente existente | Onde | Papel atual | Reuso no kit | Lacuna |
|---|---|---|---|---|
| Versão vigente | `publicacoes/application/selectors.py:27` `effective_version`; `:328` `versoes_vigentes` | Fonte única do publicado em vigor | **Direto**: é a única fonte admissível | — |
| Identificador da versão | `VersaoConsolidada.content_hash`, `valid_from`, `source_publication` (`publicacoes/models_retificacao.py:8-19`) | Prova do conteúdo | Selo da peça; base do aviso de desatualização | O hash cobre o conteúdo **inteiro**: marcaria como antiga uma peça cujos campos não mudaram |
| Retificação de vigência futura | `interface/agenda.py:701` `retificacoes_a_vigorar` | Agenda anuncia a mudança antes de valer | Avisar, na geração, que o material vence numa data conhecida | — |
| Período de inscrições | `inscricoes/domain/periodo.py:51` `periodo_de_inscricoes` | Futuro, aberto, encerrado ou não designado; período cancelado | **Direto**: decide as chamadas | "Sem término" significa aberto sem prazo |
| Desfecho | `processos/application/selectors.py:62-130` (`Desfecho`, `desfechos`) | Encerrado ou cancelado, com data do ato | **Direto**: desfecho bloqueia chamada | — |
| Situação pública | `portal/leitura.py:239` `situacao_publica`, `:256` `estado_na_vitrine`, `:211` `SITUACAO_DO_CARTAO` | Marca da vitrine e da seleção | **Direto** | Funções do portal; o kit as importaria da gestão |
| Leitura da seleção | `portal/views.py:132` `_selecao`, `:394` `_selecao_da_vitrine`, `:455` `_dias_ate` | Monta cartão e página | **Extrair** para módulo de leitura (são privadas de `views.py`) | `_selecao` usa a unidade **viva** (`institution_scope.upper()`, `:148`), não a congelada |
| Oferta e teto | `portal/leitura.py:571` `quantidade_da_oferta`, `:586` `os_primeiros` | "2 vagas e cadastro reserva"; teto com "+N" | **Direto** | — |
| Vagas do conteúdo | `interface/visao_geral.py:442` `vagas_do_conteudo` | `QuadroDoEdital(total, por Perfil, com_vaga, tem_reserva)` | Total e Perfis com vaga | Mora em `interface/` |
| Texto das vagas por lista | `interface/relatorio_do_edital.py:1819` `texto_das_vagas`, `:373` `_vagas_por_lista` | "N (X ampla, Y reservadas)" | Possível, fora do MVP | Privadas; ampla concorrência com duas grafias (memória do projeto) |
| Original × vigente | `relatorio_do_edital.py:340` `_versoes`, `:540-548` (prorrogado, término original) | Relatório de execução | "Prazo prorrogado" comprovado | — |
| Unidade congelada | `Publicacao.unidade_sigla/nome/local` (`publicacoes/models.py:75-79`) | Identifica o ato | Assinatura da peça | — |
| Formatação de instante | `shared/tempo.py` (`ZONA`), `agenda._hora`/`_meia_noite` (`interface/agenda.py:365-370`), `relatorio_do_edital.instante_por_extenso` (`:320`) | Datas no fuso institucional | **Direto** | — |
| Variáveis fechadas | `avisos/domain/variaveis.py:23-140` (`validar`, `escapar`, `resolver`) | Texto controlado dos avisos (066) | **Padrão** para os textos do kit | O corpo do aviso é texto livre; no kit não seria |
| Rodapé fixo | `avisos/domain/mensagem.py:28-49` | "A publicação oficial é a referência…" | **Padrão** da ressalva do kit | — |
| Resumo só de dado estruturado | `069`, `FR-1370` (resumo no PDF que declara repetir o Edital) | Precedente normativo | **Padrão** da ficha | — |
| Ações do detalhe | `interface/acoes.py:92-190` `_navegacao`; `Acao.motivo` (`:58`) | Botões por capacidade, com motivo quando indisponível | **Direto**: a ação entra como "Relatório do Edital" (`:173-184`) | — |
| Registro de geração | `matriculas/models.py:27` `GeracaoDeArquivo` (append-only); `interface/relatorio.py:161` (`record_event(EMITIR_RELATORIO, sha256)`) | Quem gerou, quando, sobre o quê | **Padrão** do registro do kit, sem guardar arquivo | — |
| Métrica e quebra de texto | `publicacoes/infrastructure/fonte.py:199` `MetricaEmbutida.largura`; `pdf.py:490` `_quebrar` | Quebra por largura real da fonte | **Etapa 2**: quebrar texto em SVG (SVG não quebra sozinho) | Privadas do compositor; extração não pode mudar bytes do PDF (fixtures `tests/contract/fixtures/*_v1.pdf`) |
| Fonte | `publicacoes/infrastructure/fontes/EditalSans-*.ttf` (Liberation Sans 2.1.5, OFL, subconjunto cp1252) | Fonte embutida do Edital | **Etapa 2**: fonte das peças | Só cp1252: sem emoji, setas, ✓ |
| Repertório | `publicacoes/domain/grafia.py:83-105` (`normalizar`, `representavel`, `sem_grafia`) | Recusa caractere sem grafia | **Etapa 2**: conferir título antes de desenhar | — |
| Compositor gráfico | `interface/diagramacao.py` (cor RGB, cartões, PDF marcado) | Relatórios 099/100 | Prova de que a equipe compõe gráfico à mão; **não rasteriza** | Só PDF |
| Tokens de cor | `shared/static/shared/tokens.css:14-17` (`--verde` #15803d, `--verde-escuro` #0b5a2a…) | Paleta do produto | Ponto de partida, **não** é identidade do Ifes | Não é o manual de marca |
| CSP | `shared/politica_de_conteudo.py:39-51` (`img-src 'self'`) | Recusa inline e `data:` | Prévia por URL da própria origem | — |
| Guardião de imagem | `tests/unit/test_leitura_do_documento_submetido.py:24-52` | Proíbe `import PIL` (e `cv2`, `fitz`…) em todo `processo_seletivo/` | — | **Bloqueia Pillow** até revisão do guardião |
| Imagem Docker | `Dockerfile:11-22` | Só `make`; "não é imagem de produção" | — | Nada rasteriza SVG nem HTML; produção não é versionada |

---

## 7.3 Matriz de disponibilidade de dados

Formato pedido: **Campo → origem → regra → confiabilidade → exceções → recomendação**.
"Conteúdo" é `effective_version(edital_id, at=agora).content`.

| Campo | Origem | Regra de obtenção | Confiabilidade | Exceções | Recomendação |
|---|---|---|---|---|---|
| Número e ano | `content.number`, `content.year` (`publish_edital.py:346-351`) | Literal | **Alta**. Não retificáveis (`editais/domain/mutabilidade.py:177-185`) | `number` é `CharField` | Usar sempre. É também a **chave de busca** da vitrine (`portal/leitura.py:375`) |
| Título do Edital | `content.title` | Literal | **Alta** como dado; **baixa** como manchete. É texto livre, longo e costuma repetir o número (`numero_no_titulo`, `portal/views.py:431-433`) | Retificável (`mutabilidade.py:186`) | Na ficha, usar inteiro. Na peça, só com manchete curta (decisão D-3) |
| Título do Processo | `content.processoTitle` | Derivado | Média: repetido entre Editais ("Processo Seletivo Simplificado 2026", achado C-02 da auditoria de 12/10) | — | Não usar como manchete |
| Tipo de seleção | — | **Não existe** | — | — | **Não inferir.** Nem pela forma da ordem (`POR_SORTEIO`), nem pelo nome. Fica fora |
| Curso / opção | `content.profiles[].name` | Literal, por Perfil | Alta como texto publicado; **não** é "curso" | Perfil pode ser cargo, bolsa, turma (59/2026: o código de vaga **é** a turma) | Chamar de "vaga" ou "opção", nunca de "curso", sem o dado dizer (`069`, `FR-1365`; `072`, Q6) |
| Localidade | `content.profiles[].locality` | Literal, por Perfil | Alta como texto; **sem semântica** de campus ou polo | Vazio = não declarado | Sempre **na linha do Perfil**, nunca agrupada à parte. Vazio não vira frase (`portal/views.py:424-430`) |
| Unidade | `Publicacao.unidade_sigla` / `unidade_nome` (`publicacoes/models.py:75-79`) | Congelada no ato | **Alta** | O portal mostra a viva em `_selecao` (`portal/views.py:148`) | Usar a **congelada da publicação vigente** (`source_publication`) |
| Vagas por Perfil | `profiles[].immediateVacancies`, `reserveType`, `reserveLimit` | `quantidade_da_oferta` | **Alta** | Perfil só com cadastro reserva; `0` sem reserva não se escreve | Reusar `quantidade_da_oferta` |
| Total de vagas | `vagas_do_conteudo(conteudo).total` | Soma das imediatas | Aritmeticamente alta; **comunicacionalmente perigosa** com vários Perfis (`072`, `FR-1607`) | Cadastro reserva fica fora da soma | Só como "N vagas em K opções", e só com todos os Perfis com vaga imediata. Decisão D-4 |
| Vagas por modalidade (cotas) | `profiles[].vacancyTable[]` | `modalityId = null` é a ampla concorrência | Média: duas grafias de ampla concorrência; quadro parcial é legítimo (`editais/domain/validation.py:3212`) | — | **Fora do MVP.** A página pública também não mostra (`072`, Q8) |
| Vagas acrescidas (097) | `ocupacao/models.py:284` `AcrescimoDeVagas` | Fato operacional, não norma | — | Não estão no conteúdo publicado | **Não divulgar** pelo kit: o Edital continua dizendo o que publicou |
| Período de inscrições | `schedule[]` com `isRegistrationPeriod` → `periodo_de_inscricoes` | Único Evento designado (`editais/models/cronograma.py:65-69`); `CANCELADO` prevalece | **Alta** | Sem término: aberto sem prazo. Sem designado: `NAO_DESIGNADO` | Usar só por essa função, e **sempre em data absoluta** |
| Situação das inscrições | `situacao_publica(periodo, desfecho)` | Desfecho vence período | **Alta, no instante da geração**; nula depois | Período cancelado tem marca própria | Ela decide **qual peça existe**, mas nunca é escrita como presente atemporal (§C) |
| Prorrogação | `relatorio_do_edital.py:540-548` (`prorrogado`, `termino_original`) | Original × vigente | Alta | — | "Prazo prorrogado até…" só quando comprovado |
| Próximo Evento | `leitura.agora_e_proximo` (`portal/leitura.py:101`) | Descrição publicada | Alta como **citação**; o tipo é texto livre (`cronograma.py:26-37`) | Nada liga Evento a ato (`validation.py:1617-1625`) | Fora das peças. Na ficha, só como citação: "Próximo, previsto para dd/mm: <descrição>" |
| URL da seleção | `reverse("portal:selecao")` + `request.build_absolute_uri` (precedente: `interface/avisos.py:64-73`) | Estável entre Retificações; responde para encerrado e cancelado (`portal/views.py:480-490`) | **Alta** | **Sem setting de URL base**: geração fora de requisição não tem host. O relatório omite link em host local (`interface/relatorio.py:214-219`) | No texto, URL completa. Por Perfil, a âncora `#vaga-<id>`, que já existe. **Na imagem, não**: UUID não se digita |
| QR Code | — | Não existe | — | — | **Fora do MVP** (§E) |
| PDF oficial | `public-document/<publicacao_id>` | Publicação **de origem** da versão vigente | Média: pode não conter todas as Retificações em vigor (LAC-07 da auditoria de 12/10) | — | Levar à página da seleção, não ao PDF |
| Resultado publicado | `PublicacaoResultado` (`divulgacao/models.py:35`; vigente em `divulgacao/application/selectors.py:16-33`) | Por Perfil × marco × lista; preliminar ou definitivo | Alta como fato; **nominal** | Vários resultados, naturezas diferentes | Fora do MVP |
| Convocação | — | Não é pública | — | — | **Impossível**: fora |

---

## Eixo A — Arquitetura e dados (síntese)

**Achado A-1 — A fonte é uma só, e já é a do portal.** *Certeza: alta.*
- **Evidência.** `effective_version` e as leituras de `portal/leitura.py` e `portal/views.py:132-455`.
- **Consequência.** O kit não precisa de regra nova de dados: precisa **ler o que a página da
  seleção lê, no mesmo instante, pelas mesmas funções**. Peça e página coincidem por construção.
- **Recomendação.** Extrair de `portal/views.py` uma leitura nomeada, a "ficha da seleção". A
  página e o kit a consumiriam igualmente. O `portal/leitura.py:1-15` registra o custo de já ter
  tido duas verdades sobre "em curso".

**Achado A-2 — A unidade aparece de três formas no portal.** *Certeza: alta.*
- **Evidência.** São três leituras, cada uma num lugar:

  | Forma | Onde |
  |---|---|
  | Escopo vivo | `_selecao` (`portal/views.py:148`) |
  | Sigla atual do registro | vitrine (`:366`) |
  | Sigla congelada | moldura (`:641`) |

- **Consequência.** Uma peça assinada com a sigla viva poderia divergir do ato.
- **Recomendação.** O kit usa a congelada da `source_publication` da versão vigente. A divergência
  do portal é **achado à parte** (§7.7, R-12), e não escopo do kit.

**Achado A-3 — Não há edital multiunidade.** *Certeza: alta.*
- **Evidência.** Uma Unidade por Edital (`Edital.institution_scope`). "Vários campi" só existe como
  `locality` livre por Perfil.
- **Consequência.** O cenário "vários campi" é, no dado, um Edital com Perfis de localidades
  diferentes.
- **Recomendação.** A associação certa é **linha a linha**: Perfil → localidade → quantidade.
  Agrupar por localidade exigiria comparar texto livre, e "Polo Serra" e "Serra" são iguais para
  quem lê e diferentes para o sistema. Não agrupar.

---

## Eixo B — Integração ao fluxo de publicação

**Fatos.**
- Publicar (`publish_edital`, `publicacoes/application/publish_edital.py:682`) e retificar
  (`publish_retification`, `publicacoes/application/retificacoes.py:915`) são transações únicas. Elas
  terminam com `record_event` e redirecionam para `detalhe?ato=publicar` (`interface/views.py:4176`).
- Não há gancho pós-ato.
- A homologação é de papel (`homologador`). A segregação proíbe que a mesma pessoa elabore,
  homologue e publique (`publish_edital.py:705`).
- A troca de versão por vigência futura é **puramente temporal**: nenhum ato a marca.

| Alternativa | Avaliação |
|---|---|
| **A. Detalhe do Edital publicado** | **Recomendada.** Segue o padrão do "Relatório do Edital": `Acao` em `interface/acoes.py:173-184`, visível só a quem tem a capacidade, e indisponível **com motivo** fora dos estados admitidos. Não toca a publicação, porque é leitura posterior. Funciona igual para o Edital retificado |
| **B. Passo imediato após publicar** | **Descartada como passo.** (1) Quem publica é o `publicador`, e quem divulga é a comunicação: a segregação faz deles pessoas diferentes. (2) Um passo depois da publicação induz a lê-la como parte do ato. (3) Não há gancho, e criar um seria acoplar o ato à divulgação, o que a premissa proíbe. No máximo, a faixa "Ato registrado" (`detalhe.html:10-12`) poderia levar ao kit para quem já tem a capacidade. Isso é dispensável |
| **C. Área própria de materiais** | **Prematura.** Uma lista de "Editais a divulgar" pressupõe volume e uso que não estão demonstrados. Se vier, o lugar natural é a **Agenda** (`101`, `interface/agenda.py`), que já projeta períodos e Retificações a vigorar por unidade |
| **D. No portal, para qualquer visitante** | Tentadora, porque todo dado é público e nenhuma permissão seria necessária. **Descartada.** Faria do GPS um gerador público de imagens com a marca institucional: abuso de carga, peça "oficial" fora do controle da comunicação. E a decisão de quem divulga é institucional (Princípio III) |
| **D'. Prévia de compartilhamento (Open Graph) na página da seleção** | **Complementar, não substituta.** Hoje não há `og:` nem `description` (`portal/templates/portal/base.html:4-10`; achado C-16, `072`, `:535`). Com `og:title` e `og:description` vindos da mesma ficha, **todo compartilhamento do link** ganha prévia correta, sem kit nenhum. É mudança de portal, presa à Q2 da `072`. Recomendo registrar como spec própria e pequena, sem `og:image` no primeiro passo |

**Permissão.** *Fato*: não existe papel de comunicação (`interface/identidade.py:31-137`).
Os precedentes de capacidade nova com papel próprio, negada por padrão, são `exportador`
(`031`) e `participante-piloto-assistente` (`071`). O catálogo exige descrição para todo papel
(`tests/interface/test_entrada_da_gestao.py:38`). A gestão de acessos da `107` já atribui papel a
uma pessoa que não tem outro.

**Recomendação.** Uma capacidade própria (nome provisório `material:gerar`), num papel próprio
("Comunicação"), não concedida a ninguém por padrão. O risco aqui não é de sigilo: o kit só lê
dado público vigente. É de **quem fala em nome da instituição**, e isso se decide por papel. Se ela
também vai para o `publicador` ou o `gestor` é a decisão D-1.

---

## Eixo C — Comunicação ao longo do ciclo

**Princípio que governa este eixo** — *Inferência, apoiada em fatos*. A página pública calcula a
situação **a cada leitura**, com um `agora` só para a página inteira (`portal/views.py:493`). Uma
imagem não recalcula nada: ela congela o `agora` em que foi gerada e circula por dias ou semanas.
Daí três regras:

1. **Nenhuma peça usa tempo relativo.** "Faltam 3 dias", "amanhã", "último dia" e "hoje" ficam
   falsos em 24 horas. A peça diz **data e hora absolutas**: "Inscrições até 10/11/2026, às 23h59".
   - *Fato adicional*: o "Último dia." da página significa *menos de 24 horas*, e não o dia do
     calendário (`portal/templates/portal/_periodo.html`; `_dias_ate`, `portal/views.py:455`).
     Copiado para uma peça, estaria errado mesmo no dia em que foi gerada.
2. **A situação escolhe a peça, e não entra nela como fato atemporal.** "Inscrições abertas" só é
   oferecida se, no instante da geração, `periodo.estado == ABERTO` e não há desfecho. Mesmo assim, a
   peça diz o **período**, e não "estão abertas".
3. **Toda peça tem validade**, calculada e escrita no selo: até o fim do período, ou até o início,
   para a peça de "em breve". Também é antecipada pela vigência de uma Retificação já publicada
   (`retificacoes_a_vigorar`).

| Marco | O sistema comprova? | Como | Peça no MVP? |
|---|---|---|---|
| Edital publicado, inscrições futuras | **Sim** | `Publicacao` + `periodo.estado == FUTURO` | **Sim**: "Inscrições de dd/mm a dd/mm" |
| Inscrições abertas | **Sim, no instante** | `ABERTO` e sem desfecho | **Sim**, a mesma peça com a data final em destaque. "Abertas" fica só como título da peça, com validade |
| Últimos dias | Derivável (`fim - agora`) | — | **Não como peça própria.** É a mesma peça com a data. "Últimos dias" e "última oportunidade" são juízos, e a segunda é proibida (§H) |
| Inscrições encerradas | Sim | `ENCERRADO` | **Não.** Não há chamada à ação, e o risco é o de C-03 da auditoria de 12/10: "encerrada" calada sobre o que vem depois |
| Resultado publicado | Sim, **por Perfil × marco × lista**, preliminar ou definitivo | `PublicacaoResultado` vigente | **Não no MVP.** Sem "resultado do Edital"; é conteúdo nominal; a vitrine só diz a natureza quando é a mesma em todos (`portal/leitura.py:611-642`). Candidato forte da etapa seguinte, **só em texto**: "Resultado preliminar publicado para <Perfil>; prazo de recurso até dd/mm" |
| Convocação | **Não** | Não é pública | **Impossível** |
| Prorrogação | Sim | Original × vigente | **Sim, como variação** da peça de inscrições: "Prazo prorrogado até…" |
| Edital cancelado ou encerrado | Sim | `Desfecho` | **Kit indisponível, com motivo** |
| Sem período designado (inscrição fora do GPS) | Sim, a **ausência** | `NAO_DESIGNADO` | Só ficha neutra ("Edital publicado; consulte as condições"), **sem nenhuma frase de inscrição**. A `024` (`FR-149`) proíbe chamá-lo de encerrado; o mesmo vale para chamá-lo de aberto |

Distinções pedidas — *Fato*:

| Par | Como o sistema as separa |
|---|---|
| Edital publicado × inscrições abertas | Independentes. `recebe_inscricoes` exige as duas (`inscricoes/domain/periodo.py:93-100`) |
| Data prevista × vigente | A prevista é o que a versão vigente declara. Uma data passada **não prova** que o ato aconteceu (`101`, D-006; `FR-2640-2642`). A Retificação só vale de `valid_from` em diante |
| Resultado interno × publicado | `AtoDeOrdenacao` × `PublicacaoResultado` (`specs/017-…/spec.md:251-256`) |
| Comunicação informativa × publicação oficial | Os avisos já declaram isso em rodapé fixo: "Este aviso não substitui a publicação" (`avisos/domain/mensagem.py:28-49`). O kit deve ter o equivalente em toda peça e todo texto |

---

## Eixo D — Retificações, validade e rastreabilidade

**Cenário do enunciado.** Um criativo diz "até 10/11". Uma Retificação prorroga até 17/11.

**O que existe** — *Fato*:
- Cada versão tem `content_hash` (`shared/canonical.py:172`) e `valid_from`.
- A Retificação pode ter vigência futura (`retificacoes.py:936-938`).
- `relatorio_do_edital` já sabe dizer "prorrogado, término original X".

**Proposta: registrar a geração, não os arquivos.**

1. **A geração é determinística**: a mesma versão, o mesmo instante de referência e a mesma versão do
   template dão o mesmo texto, e, na etapa 2, os mesmos bytes. Guardar os arquivos não acrescenta
   prova; acrescenta armazenamento e uma segunda verdade.
2. **Um registro append-only por geração**, no molde de `GeracaoDeArquivo`
   (`matriculas/models.py:27`). O registro guarda:
   - quem gerou e quando;
   - a versão (`id`, `content_hash`, `valid_from`);
   - a peça escolhida (o marco);
   - a **impressão da ficha**: SHA-256 só dos campos que o material usou — número, título, período,
     ofertas, localidades, unidade;
   - a validade calculada.

   Tabela append-only nova soma 1 ao `M` do provisionamento (`CLAUDE.md`, "N de M"), com gatilho e
   privilégio ausente, como as outras.
3. **"Potencialmente desatualizado" = impressão diferente**, e não `content_hash` diferente. Uma
   Retificação que muda só o desempate não deve marcar a peça como antiga; uma que muda `endAt`
   deve.
   - *Inferência*: o `content_hash` inteiro geraria falso alarme a cada Retificação, e o alarme que
     dispara sempre deixa de ser lido.
4. **Onde o aviso aparece**: na página do kit, ao abrir, e como linha no detalhe do Edital, para
   quem tem a capacidade. Exemplo: *"Material gerado em 03/11 sobre a versão de 01/11. Desde então,
   a Retificação nº 1 mudou: término das inscrições (10/11 → 17/11). Gere de novo."* O "de → para"
   sai da comparação das duas fichas, e não do "O que mudou" público, que cala valores (`047`,
   RC-111).
5. **Na geração**, se há Retificação publicada a vigorar, o kit avisa e põe a data no selo: *"Este
   material descreve o Edital até 15/11; a partir daí vale a Retificação nº 2."*
6. **Regenerar** é gerar de novo. Não há versionamento de peça, aprovação de peça nem histórico de
   arquivos.

**O que fica fora, e por quê.** O sistema não sabe onde a peça foi publicada, quem a repostou,
nem se a comunicação a apagou. Rastrear a peça no mundo é trabalho da comunicação. O GPS garante o
que é dele: **que material gerou, sobre qual versão, e se essa versão ainda vale**.

| Opção | Custo | Consistência | Auditoria | Veredito |
|---|---|---|---|---|
| Guardar os arquivos | Armazenamento por geração; arquivos de marca antiga ficam para sempre (append-only) | Duas verdades, arquivo e regeneração | Prova "o que foi entregue" | **Não**: a regeneração determinística já prova |
| Só metadados + regeneração | Uma linha por geração | Uma verdade | Prova versão, campos e instante | **Sim** |
| Nada (gerar e esquecer) | Zero | — | Não sabe avisar desatualização | Não atende o eixo |

*Ressalva — Inferência*: "mesmos bytes" na etapa 2 vale com fonte, rasterizador e template fixados
por versão. Uma atualização do rasterizador pode mudar pixels. O registro guarda a versão do
template, e o teste de determinismo compara SVG (texto), não PNG.

---

## Eixo E — Identidade visual e qualidade

**Fatos.**
- Não há logo do Ifes, nem da Rede Federal, nem do GPS em arquivo.
- O único raster é o brasão de 60×59 px, baixo demais para 1080 px.
- A única fonte é a Edital Sans (Liberation Sans), em subconjunto cp1252.
- A paleta do produto (`tokens.css`) não é o manual de marca.
- A `072` adiou a identidade visual (Q2), e a `075` registrou que "o símbolo dos protótipos é um
  marcador de lugar" (`doc/estudo-acesso-a-gestao-2026-10-16.md:236-238`).

**Consequência.** **Não há como produzir peça institucional hoje sem inventar marca**, e inventar
marca foi justamente o defeito M9 da análise de 12/10: "marca desenhada para o mockup… que lembra o
IF sem ser os ativos oficiais" (`doc/analise-edital-linguagem-simples-2026-10-12.md:346`). Este é o
**impedimento principal da etapa 2**, e ele não é técnico.

**Regras de composição para a etapa 2** — *Inferência*, a validar com a comunicação:

- **Hierarquia fixa, de três níveis**: manchete; período em data absoluta; oferta. Rodapé com
  unidade, "Edital nº X/2026" e o caminho curto ("<domínio>/selecoes"), com o selo de versão em
  corpo pequeno.
- **Orçamento de texto por zona**, medido com a métrica real (`MetricaEmbutida.largura`, `_quebrar`),
  e **recusa em vez de encolher**: se a manchete não cabe em duas linhas no corpo mínimo, a peça
  não é gerada e a tela pede manchete curta.
  - É o que o compositor gráfico já faz ao recusar texto fora da área útil
    (`interface/diagramacao.py:130-133`).
  - Fonte que encolhe até caber é a peça ilegível que o enunciado quer evitar.
- **Muitos Perfis**, em três regimes:
  - **1 a 3 Perfis**: um por linha, "nome — localidade — quantidade".
  - **4 ou mais**: a peça não lista. Diz "N opções" e, se todas têm vaga imediata, "N vagas no
    total", sempre em frase. A ficha textual lista todas.
  - Teto e "+N" seguem `os_primeiros`.
  - O limiar 3 é *Hipótese*: depende do corpo mínimo legível em 1080 px, a medir no protótipo.
- **Margem de segurança**:
  - Stories: as faixas superior e inferior ficam sob a interface do aplicativo, e o conteúdo
    essencial vai para o centro.
  - Feed 4:5: margem uniforme.
  - Os números exatos dependem do aplicativo e mudam. São *Hipótese* a fixar com a comunicação.
- **Contraste**: o mesmo critério WCAG AA que `test_acessibilidade.py` já aplica aos tokens
  (4,5:1), conferido por teste sobre as cores do template.
- **Repertório**: título passa por `grafia.normalizar` e `representavel`. Caractere sem grafia
  **recusa** a geração com o caractere nomeado, como no Edital (`pdf.py:439-461`), e nunca vira "?".
- **Texto alternativo**: sai da mesma ficha, e é praticamente a transcrição da peça. Vai para o
  pacote e para a tela, ao lado da imagem.
- **Biblioteca de templates**: um template, com até duas proporções, aprovado pela comunicação.
  "Pequena biblioteca homologada" só depois de o primeiro estar em uso. Nada de editor, cor
  escolhida pelo usuário, upload de imagem ou fonte.

**Formatos** — avaliação crítica:

| Formato | Avaliação | MVP da etapa 2 |
|---|---|---|
| Feed 4:5, 1080×1350 | É o retrato recomendado do feed, e serve também a Facebook e LinkedIn | **Sim**, o único obrigatório |
| Stories 9:16, 1080×1920 | Efêmero, com zonas cobertas pela interface; pede composição diferente, e não só a mesma esticada | **Sim, se** a comunicação confirmar uso; senão, depois |
| Quadrado 1:1, 1080×1080 | Redundante com o 4:5; *Hipótese*: o 4:5 cobre o mesmo uso | **Não** |
| Banner do site | Dimensão desconhecida; depende do CMS do portal institucional | **Não**, até a comunicação dar a medida |

**QR Code.** Numa peça vista no próprio celular, ele não serve: não se escaneia a própria tela.
Serve em cartaz impresso, que está fora do escopo, e pediria dependência (`segno`, Python puro) ou
codificador próprio. **Fora.**

---

## Eixo F — Motor de geração

Restrições verificadas — *Fato*:
- Nada no projeto rasteriza.
- A imagem Docker instala só `make`, e a de produção não é versionada (`config/settings/production.py:215`).
- A CSP só admite imagem da própria origem.
- Um guardião proíbe `import PIL`.
- O projeto justifica cada dependência por escrito: o comentário do `openpyxl` em `pyproject.toml`
  diz "a quarta".

| Alternativa | Qualidade | Dependência | Docker / produção | Testabilidade | Veredito |
|---|---|---|---|---|---|
| **SVG por template + `resvg-py` → PNG** | Alta: o resvg é o renderizador SVG mais conforme e determinístico entre os embarcáveis | Uma: roda em Rust, com wheels manylinux/musllinux e sem biblioteca de sistema ([PyPI](https://pypi.org/project/resvg-py/), [docs](https://resvg-py.readthedocs.io/en/latest/)) | Sem `apt` | SVG é texto: teste por conteúdo e por determinismo. PNG só em teste de fumaça | **Preferida**, sujeita a um *spike* (ver abaixo) |
| SVG + CairoSVG | Boa | Python **e** `libcairo2` de sistema | Pacote de sistema numa imagem que não é versionada | Igual | Segunda opção |
| Pillow, composição direta | Boa para texto e retângulo; sem SVG | Uma, com wheels e FreeType embutido | Sem `apt` | Só pixels: teste mais frágil | **Viável**, mas exige rever o guardião, e não dá exportação SVG |
| HTML/CSS + Chromium (Playwright) | Muito alta | Chromium em produção (centenas de MB) | Processo de navegador por requisição, sandbox, fontes do sistema | Pixels variam por versão do navegador | **Descartada.** A equipe já o usa, mas fora de produção (`filme-de-lancamento/producao/capture.py`; Playwright só no CI) |
| Rasterizar no navegador do usuário (canvas) | Varia por navegador | Zero | — | Não reproduzível; fonte em SVG-imagem é frágil sob CSP | **Descartada** |
| Compositor PDF próprio (`diagramacao.py`), entregando PDF | Vetorial e ótima | Zero | — | Já testado | **Insuficiente.** Rede social pede PNG/JPG. Serve como formato extra, para impressão |
| Rasterizador próprio em Python | — | Zero | — | — | **Descartada.** Rasterizar glifo TrueType com antisserrilhado é outro projeto. Escrever PDF à mão é texto; rasterizar não é |

**O spike que decide entre `resvg-py` e Pillow** (meio dia a um dia; *Hipótese* a medir):

1. Wheel para Python 3.13, nas arquiteturas de produção (x86_64; arm64, se houver).
2. Carga da Edital Sans por arquivo, sem fontes do sistema.
3. Mesmos bytes em duas execuções e em duas máquinas.
4. Tempo de uma peça 1080×1350.
5. Estado de manutenção. Há vários pacotes de nome parecido (`resvg`, `resvglite`, `svg2png-py`), e
   isso é risco de abandono.

**Segurança do texto.**
- O SVG sai de template Django com autoescape, e cada valor entra como nó de texto, nunca como
  atributo livre.
- Servido para prévia como `image/svg+xml`, o SVG **não recebe a CSP**, que vale só para
  `text/html` (`shared/politica_de_conteudo.py:69-79`). A resposta precisa de cabeçalho próprio
  (`Content-Security-Policy: default-src 'none'`) e `X-Content-Type-Options: nosniff`.
- A alternativa é a prévia ser só PNG.

**Síncrono basta** — *Inferência*:
- As exportações existentes são todas síncronas: matrículas, relatório 099 e 100
  (`interface/relatorio.py:145`).
- Uma peça vetorial simples rasterizada em 1080 px é ordem de dezenas a centenas de milissegundos,
  número a confirmar no spike. Com duas peças e um ZIP por `zipfile`, que já está na biblioteca
  padrão, não há razão para fila. Fila exigiria "necessidade demonstrada" (Princípio V).

**ZIP.** `zipfile` com datas fixadas no `ZipInfo`, para o pacote ser reproduzível. Ele leva:
- as peças;
- `textos.txt`, com legenda, chamada, texto curto, link e texto alternativo;
- `manifesto.json`, com versão, `content_hash`, impressão, gerado em, válido até e template.

Na etapa 1 o "pacote" é desnecessário: os textos se copiam da tela.

---

## Eixo G — Experiência do usuário

**O fluxo de seis passos é longo demais.**

| Passo proposto | Cortar? | Por quê |
|---|---|---|
| 1. Identificação e situação | **Manter** | É a confirmação de dados, e é o que o usuário precisa conferir |
| 2. Momento de comunicação | **Cortar** | O sistema já sabe o momento: a situação decide qual peça existe (Eixo C). Oferecer "inscrições abertas" num Edital de inscrições futuras é oferecer o erro |
| 3. Template | **Cortar** | Um template só no MVP |
| 4. Pré-visualização | **Manter** | É onde se confere |
| 5. Formatos | **Cortar** | Gera-se tudo o que é oferecido; quem não quer o Stories não o usa |
| 6. Exportação | **Manter**, um botão | — |

O fluxo resultante é **uma tela**: o kit do Edital, já composto, com o que precisa de conferência
marcado. Na etapa 2 entra um campo, a manchete curta, só quando o título não cabe.

**Wireframe — CONCEITUAL, etapa 1** (dentro da moldura da gestão, `076`; a ação vem do detalhe do
Edital):

```
┌ GPS ─ Editais › Edital nº 59/2026 › Material de divulgação ───────────────────┐
│                                                                                 │
│  Material de divulgação                                                         │
│  Edital nº 59/2026 — Curso de Libras Iniciante A1 · Cefor                       │
│  Dados da versão vigente desde 30/07/2026 14h00 (Retificação nº 1)              │
│                                                                                 │
│  ┌ Situação neste instante (31/10/2026 10h12) ───────────────────────────────┐ │
│  │ ● Inscrições abertas até 10/11/2026, às 23h59                              │ │
│  │   Este material vale até 10/11/2026, 23h59.                                │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ⚠ Gerado em 03/11 sobre a versão de 01/11. Desde então mudou:                  │
│    término das inscrições (10/11 → 17/11). Os textos abaixo já são os novos.    │
│                                                                                 │
│  Confira antes de usar                                                          │
│   Oferta    Turma terça noite — Vitória — 20 vagas                              │
│             Turma sábado manhã — Vitória — 20 vagas e cadastro reserva          │
│   Endereço  https://…/selecoes/7c1e…/                     [Copiar]              │
│                                                                                 │
│  Legenda para rede social                                 [Copiar]              │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │ Edital nº 59/2026 do Cefor/Ifes: Curso de Libras Iniciante A1.           │   │
│  │ Inscrições de 20/10 a 10/11/2026, às 23h59.                              │   │
│  │ São 2 opções de turma… (texto controlado, ver Eixo H)                    │   │
│  │ Condições, documentos e cronograma na página da seleção.                 │   │
│  │ As informações repetem o Edital; em caso de divergência, vale o Edital.  │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│  Chamada curta para o site                                [Copiar]              │
│  Texto para mensagem                                      [Copiar]              │
│                                                                                 │
│  [ Registrar e copiar tudo ]                                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

*Nota*: "turma" aparece no exemplo porque o `name` do Perfil a contém. O sistema não a escreveria
por conta própria (`FR-1365`).

**Etapa 2** acrescenta, abaixo da situação, as prévias (`<img>` da própria origem, com o texto
alternativo ao lado) e o botão "Baixar pacote (.zip)".

**Estados que a tela precisa ter:**

| Estado | O que a tela diz |
|---|---|
| Edital não publicado | A ação aparece indisponível com motivo, como o relatório: "Disponível depois da publicação" |
| Desfecho | "Edital cancelado em dd/mm. Não há material de divulgação para um Edital que não recebe inscrições." A ação continua visível, com motivo. Esconder faz a pessoa procurar |
| `NAO_DESIGNADO` | Só a ficha neutra, com a explicação: "Este Edital não recebe inscrições pelo GPS; o material não fala de inscrição" |
| Período encerrado | Indisponível, com motivo. Resultado fica para a etapa seguinte |
| Retificação a vigorar | Faixa de atenção, com a data no selo |
| Desatualizado | Faixa, com a lista "de → para" dos campos |
| Título não cabe ou caractere sem grafia (etapa 2) | Campo de manchete com limite visível, ou o caractere nomeado |
| Sem localidade ou sem vaga imediata | Nada a dizer: a frase some, e a ausência não vira "não informado" (`024`, D-009) |

---

## Eixo H — Conteúdo textual

**Determinístico, sem IA** — *Fato e Inferência*. Os textos combinam poucos dados estruturados em
poucas formas, e o projeto já tem o padrão de variáveis fechadas (`avisos/domain/variaveis.py`).
Não há necessidade que template não atenda. A IA do projeto é piloto interno, com produção recusando
a página pública (`071`, `FR-1462`; `074`, `FR-1683`). Texto publicitário gerado por modelo seria
o primeiro texto público não determinístico do sistema, sem a validação que a `071` exige para
abrir ao público.

**Diferença em relação aos avisos.** No aviso, o corpo é livre e a unidade o escreve. No kit,
**o texto é do sistema, não editável na tela**: quem quiser outro texto copia e muda fora, e a
responsabilidade por esse texto passa a ser de quem o mudou. Se a unidade precisar de texto próprio
recorrente, a etapa seguinte pode ter **modelos com variáveis fechadas**, como os avisos. Não no MVP.

**Textos do MVP** — o conjunto das formas é finito, e cada uma tem um teste por estado:

| Texto | Composição | Varia por marco? |
|---|---|---|
| Legenda | Identificação + período absoluto + oferta (até 3 Perfis, ou "N opções") + chamada à página + ressalva | Sim: futuro, aberto e prorrogado. Encerrado e desfecho não têm legenda |
| Chamada curta para o site | "Edital nº X/2026 — <título>: inscrições até dd/mm/aaaa" | Sim |
| Texto para mensagem | Legenda sem quebra de linha, com o link da seleção ou da âncora do Perfil | Sim |
| Link oficial | `/selecoes/<uuid>/`; por Perfil, `#vaga-<id>` | Não |
| Texto alternativo (etapa 2) | Transcrição da peça, em ordem de leitura | Segue a peça |
| Ressalva | "As informações repetem o Edital nº X/2026, vigente em dd/mm/aaaa. Em caso de divergência, vale o Edital." | Fixa |

**Vocabulário** — uma varredura nova, no padrão de `tests/portal/test_vocabulario_das_telas_publicas.py`:

- **Proibidas sempre**: "última oportunidade", "não perca", "garanta sua vaga", "vagas garantidas",
  "aprovado", "classificado", "resultado disponível", "resultado final"; e tempo relativo ("faltam",
  "amanhã", "hoje", "último dia", "últimos dias").
  - A lista `PROIBIDAS` do portal (`tests/portal/test_acompanhamento_pela_situacao.py:55-66`)
    entra inteira.
- **Condicionadas ao estado**: "inscrições abertas" só com `ABERTO` e sem desfecho. "Prorrogado"
  só com prorrogação comprovada. "Inscrições" nunca com `NAO_DESIGNADO`.
- **Vocabulário interno proibido** como na `069` (`FR-1366`): marco, recorte, faixa, apuração,
  homologa.
- A varredura **lê o texto gerado em todos os estados**, e não o template. O template quase não
  tem texto, e a frase nasce da combinação.

---

## Eixo I — Governança institucional

**Divisão proposta**, de acordo com o enunciado e com o que o código sustenta:

| Ator | Faz | Não faz |
|---|---|---|
| GPS | Lê só o publicado vigente; compõe textos (e peças, na etapa 2) de regra fixa; registra a geração; avisa desatualização | Não publica em rede; não guarda peça; não decide quando divulgar |
| Comunicação institucional | Aprova o template (fora do sistema, uma vez por template; a versão aprovada entra no código); decide onde e quando publicar | Não altera dado oficial pelo kit |
| Quem tem a capacidade | Gera, confere, copia, baixa | Não edita o dado |

**Sem novo fluxo de homologação de peça** — *Recomendação*. A aprovação acontece **no template**,
uma vez. Peça por peça, ela seria uma segunda homologação para um ato que não é ato. A Constituição
exige autorização para **divulgação de resultado** (`.specify/memory/constitution.md:158`), e o
kit não divulga resultado. É comunicação informativa. A ressalva fixa e a distância em relação ao
ato oficial (nenhum passo dentro da publicação) são o que mantém essa diferença visível.

**Exposição de dado não publicado** — *Fato e Recomendação*. O risco é real e localizado:
- o rascunho e as tabelas relacionais (`interface/visao_geral.py:445`);
- as versões de vigência futura: ler "a última `VersaoConsolidada`" sem `valid_from__lte` vazaria
  a Retificação antes da hora.

A recomendação é um **teste de fronteira** como o `tests/portal/test_fronteira_publica.py`: o
módulo do kit não importa modelos de `editais` nem lê `VersaoConsolidada` por outro caminho que não
`effective_version`.

---

## Eixo J — Evolução futura

| Possibilidade | Valor | Recomendação |
|---|---|---|
| Endereço legível (`/selecoes/59-2026/`) | **Alto** para qualquer divulgação: a peça poderia imprimir o endereço | Fora do kit. É decisão de portal, já registrada (`072`, `:543`). **Talvez seja mais valiosa que a etapa 2 inteira** |
| Prévia de compartilhamento (Open Graph) | Alto e barato | Spec pequena de portal (Eixo B, D') |
| Origem de campanha (`?origem=`) | Médio | A `024` (D-008) vedou instrumentação; o caminho proporcional, de contador agregado e lista fechada, está em `doc/auditoria-ux-conversao-2026-10-12/jornada-publica.md:202-215`. **Decisão própria com LGPD**, não do kit |
| Ifes Ads | Incerto | A API pública da versão vigente (`/api/v1/public/editais/<id>/versao-vigente`) já basta para um gerador externo. Não integrar agora (`doc/auditoria-de-consolidacao-2026-10-15/roadmap-consolidado.md:137`) |
| Peça por Perfil (uma por curso ou polo) | Médio em editais grandes | Depois do template único em uso. A âncora `#vaga-<id>` já dá o destino |
| Resultado publicado, em texto | Médio | Próximo marco natural, com cautela nominal |
| Regeneração automática após Retificação | Baixo | Não há gancho, e não precisa: o aviso de desatualização basta. Gerar sem ninguém pedir produziria material que ninguém confere |
| Editor de peça, templates por unidade, cores por campus | Baixo e caro | **Não.** É o "Canva dentro do GPS" |

---

## 6. Avaliação crítica de produto

| Pergunta | Resposta | Natureza |
|---|---|---|
| O volume justifica? | A numeração chega a **173/2025** no Cefor (`doc/achados-editais-externos.md`). Isso inclui seleções de pessoal (tutor, designer), que têm divulgação diferente. Só uma unidade está registrada (`unidades/unidades.json`), e **o sistema não está em produção** (`README.md:384`) | Fato + Hipótese |
| Quanto trabalho se elimina? | Na etapa 1: ler o PDF para extrair datas, oferta e link, e redigir a legenda. É o trabalho **propenso a erro**. Na etapa 2: montar a arte, que a comunicação já faz rápido com template próprio | Hipótese a medir com a comunicação, cronometrando um Edital real |
| O que ainda exige conferência? | Manchete; nome do Perfil como chamada (texto do elaborador, não da comunicação); se o momento é bom para divulgar | Inferência |
| A comunicação usaria diretamente? | **Desconhecido.** O mais provável é que a comunicação tenha ferramenta e marca próprias. Se for o caso, ela pode querer **os dados, e não a arte**. Uma ficha exportável em CSV (para *bulk create* em ferramenta de design) atenderia sem template no GPS | Hipótese crítica |
| Templates bons o bastante? | Sem ativos de marca, **não**. Com eles, um template rígido cobre o caso comum (1 a 3 Perfis) e degrada com dignidade no resto | Inferência |
| Ganho maior em multicampi? | Sim, no dado: a associação Perfil × localidade × vagas é onde se erra à mão. Mas multicampi aqui é **multiPerfil numa unidade**, e outras unidades ainda não usam o sistema | Fato + Inferência |
| Centralizado ou por unidade? | Centralizado: um template, com a assinatura da unidade vinda do registro. Variação por unidade é custo de manutenção sem caso demonstrado | Recomendação |
| Risco de criativos pouco úteis? | Sim, se houver peça por marco. Por isso uma peça, cuja situação o sistema decide | Inferência |
| A manutenção pode superar o benefício? | **Na etapa 2, pode.** Template visual muda com a campanha, com o aplicativo e com o manual. Cada mudança é deploy e teste. É o argumento central para separar as etapas e condicionar a segunda ao uso da primeira | Inferência |

---

## 7.4 Alternativas de arquitetura

**Alternativa 1 — Ficha primeiro, peças depois (recomendada).**
- Uma leitura pura, a "ficha da seleção", extraída das funções do portal. Ela entra com
  `(versão vigente, publicação de origem, desfecho, agora)` e devolve dados e situação.
- Sobre ela, um compositor de textos com formas fechadas.
- Uma tabela append-only de geração.
- Uma tela na gestão, chegada pela ação do detalhe.
- Na etapa 2, o compositor SVG lê a **mesma** ficha. Nada do que a etapa 1 constrói se descarta.

**Alternativa 2 — Kit completo de uma vez.** Ficha, SVG e rasterização na mesma spec.
- **Contra:** a spec fica bloqueada por marca e dependência, que não dependem da equipe. A parte
  útil espera a parte incerta.

**Alternativa 3 — GPS só exporta dados.** Uma ficha em CSV/JSON, e a comunicação compõe a peça na
própria ferramenta.
- **A favor:** o GPS não carrega template, fonte nem raster.
- **Contra:** perde a garantia de que a peça diz o que a ficha diz.
- **É a alternativa 1 parada na etapa 1**, com um botão de CSV a mais. Se a comunicação confirmar
  que não usaria a arte do GPS, é esta que fica.

**Alternativa 4 — HTML renderizado por navegador em produção.** Descartada no Eixo F.

---

## 7.5 Proposta de experiência

- **Onde.** Ação "Material de divulgação" no detalhe do Edital (`interface/acoes.py`, `_navegacao`).
  Ela aparece para quem tem a capacidade e fica indisponível, com motivo, fora de `PUBLICADO` com
  período futuro ou aberto, ou sem período designado. Opcionalmente, na Agenda (`101`), uma coluna
  com o último material gerado e o sinal de desatualização. Etapa posterior.
- **Fluxo.** Abrir → conferir o bloco "Confira antes de usar" → copiar (etapa 1) ou baixar o pacote
  (etapa 2). O "Registrar e copiar" grava a geração. *Abrir* não grava: só a ação explícita conta
  como "material gerado". Abrir para conferir não é gerar.
- O wireframe conceitual está no Eixo G.

---

## 7.6 Definição do MVP (etapa 1)

**Entra:**
1. A ficha da seleção: leitura pura, extraída, que a página da seleção também passa a consumir.
2. As chamadas condicionadas pelo estado: futuro, aberto e prorrogado. Desfecho, encerrado e não
   designado têm as respostas do Eixo G.
3. Os textos: legenda, chamada curta, texto para mensagem, link (geral e por Perfil) e ressalva.
4. O selo de versão e validade em todo texto.
5. O registro append-only da geração, com a impressão da ficha.
6. O aviso de desatualização ("de → para") e o aviso de Retificação a vigorar.
7. A capacidade e o papel próprios, negados por padrão.
8. Os testes de fronteira, de vocabulário por estado e de matriz de cenários (§5).

**Fica de fora:** peças visuais, ZIP, QR Code, resultado, convocação, encerramento, modelos editáveis,
IA, Open Graph (spec própria), endereço legível, instrumentação, vagas por modalidade, vagas
acrescidas.

**Templates:** nenhum visual. As formas textuais são fixas e versionadas no código.

**Formatos:** texto. CSV da ficha só se a decisão D-6 pedir.

**Dados usados:**
- número, ano e título;
- unidade congelada;
- período vigente e prorrogação;
- Perfis, com nome, localidade e oferta;
- URL e âncoras;
- versão, `valid_from` e Retificação a vigorar.

**Validações indispensáveis:**
- só `effective_version`;
- desfecho vence período;
- nenhum tempo relativo;
- nenhuma frase de inscrição em `NAO_DESIGNADO`;
- ausência não vira frase;
- vocabulário proibido ausente em todos os estados;
- impressão estável para o mesmo dado;
- a ação negada a quem não tem a capacidade, com teste de autorização.

**MVP da etapa 2** (para a spec seguinte):
- um template;
- Feed 4:5, e Stories se confirmado;
- SVG + PNG + ZIP + texto alternativo;
- recusa por excesso de texto;
- determinismo por SVG.

**Decisões pendentes:** §Decisões, ao final.

---

## 7.7 Riscos e impedimentos

| # | Risco | Gravidade | Impacto | Evidência | Mitigação |
|---|---|---|---|---|---|
| R-1 | Peça congelada afirma situação vencida | **Alta** | Desinformação com marca institucional | `_dias_ate` e "Último dia" (`portal/views.py:455`; `_periodo.html`) são de página viva | Sem tempo relativo; validade no selo; situação escolhe a peça |
| R-2 | Ler o relacional ou a versão futura | **Alta** | Divulgar o Edital original, ou uma Retificação antes da hora | `visao_geral.py:445`; `valid_from` futuro | Teste de fronteira; só `effective_version` |
| R-3 | Ausência de marca oficial | **Alta** (etapa 2) | Peça não institucional; repete o M9 | Só `brasao.png` de 60 px | Etapa 2 condicionada aos ativos |
| R-4 | Dependência de raster | Média | Nova dependência; guardião de PIL | `test_leitura_do_documento_submetido.py:24-52` | Spike; preferir `resvg-py`, que não toca o guardião |
| R-5 | Comunicação não adota | **Alta** (produto) | Feature sem uso, mantida para sempre | Não demonstrado | Etapa 1 barata; medir uso antes da 2 |
| R-6 | "Curso" e "campus" inferidos de texto livre | Média | Rótulo falso | `FR-1365`; `locality` livre | Nunca nomear o que o dado não diz |
| R-7 | Total de vagas enganoso | Média | "40 vagas" lido como de cada opção | `072`, `FR-1607` | Soma só em frase, com o número de opções |
| R-8 | Falso alarme de desatualização | Baixa | Aviso ignorado | `content_hash` cobre tudo | Impressão só dos campos usados |
| R-9 | SVG servido sem CSP | Média (etapa 2) | Injeção em SVG | CSP só em `text/html` (`politica_de_conteudo.py:69-79`) | Cabeçalho próprio; autoescape |
| R-10 | URL absoluta sem setting | Baixa | Link errado fora de requisição | Nenhum `SITE_URL` | Gerar só em requisição, como os avisos |
| R-11 | Manutenção visual supera o benefício | Média | Custo contínuo | — | Um template; sem variação por unidade |
| R-12 | **Achado à parte:** o portal mostra a unidade de três formas | Baixa | Divergência entre moldura, cartão e página | `portal/views.py:148`, `:366`, `:641` | **Registro, não escopo** |
| R-13 | Nome do módulo colide com `divulgacao` | Baixa | Confusão de vocabulário | `divulgacao/models.py:1-15` | Outro nome de módulo |

---

## 7.8 Estimativa relativa de esforço

Escala relativa, em que **P** é próximo de uma tela simples com teste, **M** cerca de duas a três
vezes isso e **G** acima de M, com incerteza. A referência de tamanho é a spec `099`, Relatório do
Edital, que é **G**.

| Componente | Etapa 1 | Etapa 2 | Justificativa |
|---|---|---|---|
| Backend: ficha + textos + registro | **M** | P | A extração da ficha toca a página da seleção, que tem testes densos. Os textos são poucas formas, mas com matriz de estados |
| Motor de composição | — | **M–G** | SVG com quebra por métrica; extrair `_quebrar` e a métrica do `pdf.py` sem mudar bytes do Edital |
| Templates | — | **M** + tempo da comunicação | O desenho é fora da equipe; a codificação é média |
| Interface | **P** | P | Uma tela, uma ação; padrão do relatório |
| Exportação | P (copiar) | P (ZIP) | `zipfile` |
| Testes | **M** | **M** | Matriz de cenários, vocabulário por estado, fronteira, determinismo. Na etapa 2, contraste e excesso de texto |
| Integração com a publicação | **Nenhum** | Nenhum | Por desenho: não toca o ato |
| Dependência e implantação | — | **P–M** | Spike + `pyproject` + documentação de implantação |

**Total: etapa 1 ≈ M**, menor que a `099`. **Etapa 2 ≈ G**, comparável à `099`, e com a maior
parte da incerteza fora do código.

---

## 7.9 Recomendações para a futura spec

**Objetivo.** Dar à comunicação, a partir do Edital publicado, textos de divulgação com dados
oficiais e chamadas que o sistema comprova, ligados a uma versão e avisando quando ficam antigos.

**Escopo.** O MVP da §7.6.

**Requisitos funcionais candidatos** (sem numeração: a faixa `FR-` é global e atribuída na
especificação, como registra a memória do projeto):

- O material lê **somente** a versão vigente no instante da geração.
- A situação das inscrições, com o desfecho prevalecendo, determina quais textos existem.
- Nenhum texto usa tempo relativo; todo prazo vem em data e hora absolutas, no fuso institucional.
- Todo texto traz a ressalva de que repete o Edital, e o selo de versão e validade.
- Edital sem período designado não recebe nenhuma frase sobre inscrição.
- A oferta é dita por Perfil; a soma só em frase com o número de opções.
- Localidade e nome do Perfil aparecem literais e nunca são rotulados como curso, campus ou polo.
- A geração é registrada (append-only) com versão, impressão e validade; abrir a tela não registra.
- O material aponta desatualização pela impressão, nomeando os campos e os valores "de → para".
- Retificação publicada a vigorar é anunciada e limita a validade.
- A ação é oferecida só a quem tem a capacidade própria; fora dos estados admitidos, aparece
  indisponível com motivo.

**Requisitos não funcionais:**
- nenhuma dependência nova na etapa 1;
- geração síncrona com número fixo de consultas, no padrão do orçamento de consultas do projeto;
- sem estilo nem script embutido (CSP);
- acessibilidade AA da tela;
- textos reproduzíveis (os mesmos dados dão o mesmo texto).

**Critérios de aceitação essenciais** (os cenários da §5 viram casos):
- Edital de inscrições futuras não produz "abertas".
- Retificação que prorroga marca o material anterior como desatualizado, com "10/11 → 17/11", e o
  novo diz 17/11.
- Edital cancelado dentro do período não oferece material.
- Pessoa sem a capacidade recebe a recusa canônica.
- A varredura de vocabulário passa em todos os estados.

**Dependências:**
- extração da ficha a partir de `portal/views.py`, com regressão da página da seleção;
- papel novo no catálogo (`interface/identidade.py`), com descrição;
- `test_gramatica_das_portas.py` e o inventário de negativas da `033`, se houver `Http404` novo;
- `MODULOS_DE_VIEW`, se o módulo de view for novo;
- a contagem `M` do provisionamento, pela tabela append-only nova.

**Decisões arquiteturais necessárias:** onde mora a ficha (domínio de portal ou módulo
compartilhado); o nome do módulo novo (não `divulgacao`); impressão por campo ou por hash completo
(recomendado: por campo).

**Questões em aberto:** as decisões a seguir.

---

## 5. Cenários de validação

| Cenário | Comportamento recomendado | Base |
|---|---|---|
| Publicado, inscrições futuras | Texto "Inscrições de dd/mm a dd/mm"; nunca "abertas"; validade até o início | `periodo.py:75` (`FUTURO`) |
| Inscrições em andamento | Período absoluto; validade até o fim; sem "faltam" | `ABERTO`; R-1 |
| Muitos cursos | Ficha lista todos; texto curto diz "N opções"; peça (etapa 2) não lista acima de 3 | `os_primeiros`; `FR-1607` |
| Vários campi | Linha Perfil → localidade → oferta; nunca agrupa localidade | `locality` livre; A-3 |
| Retificado | Selo com a versão; aviso por impressão | Eixo D |
| Prazo prorrogado | Novo texto com a data nova e "prazo prorrogado", comprovado por original × vigente | `relatorio_do_edital.py:540-548` |
| Sem dados opcionais | Sem localidade: omite. Sem término: "a partir de dd/mm", sem prazo. Sem vaga imediata: "cadastro reserva" | `quantidade_da_oferta`; `periodo.py` |
| Inscrição externa | Só a ficha neutra; nenhuma frase de inscrição; destino é a página da seleção, porque o sistema não conhece outro | `NAO_DESIGNADO` |
| Processo encerrado | Edital com desfecho próprio: indisponível. Desfecho só do Processo: segue o período e diz o fato | `047`, D-003 |
| Usuário sem permissão | Ação ausente no detalhe; rota responde a recusa canônica | `require_authorization_base` (`seguranca/application/authorization.py:151`) |
| *Acrescido:* Retificação com vigência futura | Aviso na geração; validade limitada | `retificacoes_a_vigorar` |
| *Acrescido:* período cancelado | Indisponível ("Período cancelado"), nunca "encerradas em" com data futura | `Periodo.cancelado` |
| *Acrescido:* cancelado dentro do período | Indisponível; nada de "abertas" | `test_desfecho_publico.py:139` |
| *Acrescido:* Unidade renomeada depois da publicação | Assinatura congelada | `Publicacao.unidade_*` |
| *Acrescido:* título que repete o número | Não repetir "59/2026" duas vezes | `numero_no_titulo` |
| *Acrescido:* caractere sem grafia (etapa 2) | Recusa nomeando o caractere | `grafia.py` |
| *Acrescido:* vaga acrescida (097) | Não entra: não é norma publicada | `ocupacao/models.py:284` |
| *Acrescido:* conteúdo de esquema antigo | A ficha tolera, como a página | `elevacao.py:15-20` |
| *Acrescido:* Perfil só com cadastro reserva entre Perfis com vaga | Soma "N vagas" não se escreve; só a oferta por Perfil | `com_vaga` em `vagas_do_conteudo` |

---

## Encerramento

### 1. Veredito

**Implementar com ajustes.**
- **Faz sentido**: o GPS já calcula, com regra testada, quase tudo o que um material de divulgação
  precisa afirmar.
- **Não faz sentido** começar pelas imagens. Faltam marca oficial, decisão de dependência e
  evidência de uso.
- O que justifica a feature é a **correção** do que se afirma. A arte é a parte de menor risco para
  a comunicação e a de maior custo para o GPS.

### 2. MVP recomendado

A **ficha de divulgação**, com:
- textos de regra fixa, escolhidos pela situação comprovada;
- datas absolutas;
- oferta por Perfil;
- ressalva e selo de versão e validade;
- registro da geração;
- aviso de desatualização "de → para".

Fica na gestão, pela ação do detalhe do Edital publicado, com capacidade própria. Sem dependência
nova e sem tocar a publicação.

### 3. Principais decisões pendentes

| # | Decisão | Opções |
|---|---|---|
| D-1 | Quem tem a capacidade | (a) papel "Comunicação" só; (b) também `publicador`; (c) também `gestor` |
| D-2 | A comunicação usaria arte gerada pelo GPS? | Validar com um Edital real; se não, a etapa 2 vira CSV (alternativa 3) |
| D-3 | Manchete curta | (a) título do Edital truncado com recusa; (b) campo digitado no kit, registrado na geração; (c) campo novo no Edital, que seria **mudança normativa**: não recomendado |
| D-4 | Total de vagas em frase | (a) nunca; (b) "N vagas em K opções" quando todas têm vaga imediata |
| D-5 | Ativos de marca e manual | Quem fornece; se é a marca do Ifes, da unidade ou ambas (liga-se à Q2 da `072`) |
| D-6 | CSV da ficha no MVP | (a) não; (b) sim, para ferramenta de design da comunicação |
| D-7 | Rasterizador da etapa 2 | `resvg-py` (preferido), CairoSVG, ou Pillow com revisão do guardião |
| D-8 | Formatos da etapa 2 | Feed 4:5 só, ou Feed + Stories |
| D-9 | Open Graph e endereço legível | Specs próprias de portal, antes ou depois do kit |

### 4. Recorte para uma única spec SDD/SpecKit

**"Material de divulgação do Edital — ficha e textos"**, a etapa 1 inteira, e nada da etapa 2.

- **Entradas exigidas antes do `/speckit-specify`**: D-1, D-3 (só para a ficha: o título inteiro
  basta), D-4 e D-6.
- **Fora, por decisão escrita na spec:** peças, ZIP, QR, resultado, convocação, Open Graph,
  endereço legível, instrumentação.
- A etapa 2 nasce como spec própria só quando D-2, D-5 e D-7 estiverem respondidas.

### 5. Critérios objetivos de conclusão da etapa 1

1. Cada cenário da §5 tem caso automatizado, e todos passam contra PostgreSQL (`make test-pg`).
2. A página da seleção e o material leem a **mesma** ficha. Um teste prova que, para o mesmo `agora`,
   período, oferta e situação coincidem.
3. Um teste de fronteira prova que o módulo do material não lê tabelas de elaboração nem versão
   futura.
4. A varredura de vocabulário passa em todos os estados, inclusive para tempo relativo.
5. Uma Retificação de prorrogação marca o material anterior como desatualizado, com os valores
   "de → para", e o novo material diz a data nova.
6. Pessoa sem a capacidade não vê a ação, e a rota a recusa com a frase canônica.
7. Nenhuma dependência nova em `pyproject.toml`. `make lint check test-pg` verde.
8. Um Edital real (amostra em `~/Downloads`), montado pela interface, produz textos que a comunicação
   confere e aprova **sem correção de dado**. É a validação humana, como os SC humanos das specs
   anteriores.
