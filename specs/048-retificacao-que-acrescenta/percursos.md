# Percursos pela tela — 048

**Onde**: servidor da worktree (`retificacao-048` em `.claude/launch.json`, porta 8048), banco
`processo_seletivo_048`, `seed_demo --janela-recursal ausente`, em 26/09/2026. Edital 01/2026 do
`seed_demo`.

**Como**: o painel do navegador estava oculto (viewport zero), e por isso os formulários foram
preenchidos e enviados pelo DOM da página servida — os mesmos campos, os mesmos botões, os mesmos
POST que a pessoa faria —, e lidos pelo texto da página. Nenhum passo passou por API, shell ou
banco. As identidades foram segregadas: **ana.elaboradora** (elaborar e submeter),
**hugo.homologador** (homologar), **paula.publicadora** (publicar).

## Percursos 2, 4, 5 e 6 — num ato só

1. **A tela antes.** Na seção *Perfis de Vaga*, a frase *"Modalidades de Concorrência ainda não são
   definidas por aqui"* não existe mais, e há os botões *Acrescentar Modalidade de Concorrência* e
   *Acrescentar critério de desempate*. Os marcos do `seed`, publicados sem janela, oferecem só
   *"Prazo de recurso, em dias corridos"*, com *"Em branco — este marco continua sem prever
   recurso."*; nenhum controle *"admite?"*. Os dois Perfis oferecem o gatilho da reversão em
   *"Nenhum"*.
2. **O que foi declarado.** Modalidade `EP — Escola pública` no Perfil DOC-INFO, com fundamento,
   versão, percentual e 0 vagas; critério 1 no marco *Classificação final*, maior pontuação na Prova
   objetiva; prazo de recurso de 3 dias no mesmo marco; reversão *"A quantidade que ficou sem
   preencher"* no Perfil DOC-INFO.
3. **A conferência** (*Ver o que vai mudar*) listou **exatamente cinco** alterações, cada uma com
   *"vigente hoje: —"* e o depois por extenso — a reversão, o prazo `3`, a Modalidade, a linha do
   quadro `0 vaga(s)`, o critério. Nenhum objeto nasceu sem ser pedido (os marcos têm corte; a
   janela do outro marco ficou em branco e não nasceu). As linhas acrescentadas voltaram
   preenchidas depois do POST.
4. **Criar, submeter, homologar, publicar**, cada ato pela sua identidade. A tela do ato mostrou
   *"Janela recursal — Admite recurso em 3 dia(s) corrido(s)"*, *"Reversão de vaga reservada — A
   quantidade que ficou sem preencher"* e *"1 — Maior pontuação numa Etapa"*.
5. **Depois da publicação.** A página pública da seleção lê *"Concorrência: Ampla concorrência;
   Pessoas pretas, pardas e indígenas; Escola pública"*. A tela de Retificação passou a oferecer a
   janela nascida com os três campos de alteração, e a Modalidade e o critério como entidades.

## O que o percurso encontrou

- **A tela do ato diz "—" para a linha do quadro acrescentada.** É anterior à `048` (a linha do
  quadro acrescentada pela `025` já chegava assim), e a `048` a torna mais visível, porque a cota
  acrescentada leva a linha junto. Corrigido depois do percurso (`objeto_legivel`), e preso por
  `test_a_tela_do_ato_diz_a_linha_do_quadro_acrescentada`.
- **O *"O que mudou"* público desta Retificação diz 1**, e ela fez cinco alterações. É o `RC-111`,
  registrado como achado A-4 da spec, e confirmado aqui no navegador.

## Não percorridos pela tela, e por quê

- **Percurso 1 (o Perfil sem a ampla ganha a ampla)**: o Edital do `seed_demo` declara a ampla, e
  montar um Perfil sem ela pela composição é o percurso inteiro do assistente, fora do que esta
  feature muda. Provado de ponta a ponta por
  `tests/integration/inscricoes/test_modalidade_acrescentada_por_retificacao.py`, pela aplicação e
  pela inscrição.
- **Percurso 3 (a regra de corte que nasce)**: os marcos do `seed_demo` cortam. O caminho da tela do
  corte até a regra é provado por `test_o_caminho_da_regra_termina_na_regra_daquele_marco` e
  `test_o_marco_por_sorteio_tambem_chega_a_regra`, que seguem o link e leem o destino.
- **Percurso 7 (regressão)**: provado por `test_retificar_so_um_texto_emite_so_um_texto`, que monta o
  POST **a partir da marcação** — e reprovou numa mutação que oferecia o booleano da janela.
