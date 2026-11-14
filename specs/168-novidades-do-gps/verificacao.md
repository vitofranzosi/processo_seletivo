# Verificação — Novidades do GPS

*14/11/2026, sobre a `main` em `cf6327c8`, sem commit.*

## Suíte

- `ruff check` e `ruff format --check`: limpos.
- Suíte inteira contra PostgreSQL, 4 workers: **20 185 passando e 24 pulados, sem falha** (549s).
- Depois dos achados da revisão de código de 14/11: **20 192 passando e 24 pulados, sem falha** (705s).
- Depois da segunda revisão de 14/11 (registro, notas novas, casos institucionais): **20 232 passando
  e 24 pulados, sem falha** (634s).
- Depois da extensão a setembro (109 notas): **20 326 passando e 24 pulados, sem falha** (957s).
- Depois da reescrita como anúncio (90 notas): **20 380 passando e 24 pulados, sem falha** (897s).
- Novos: `tests/novidades/test_catalogo.py`, `tests/novidades/test_rascunho.py` e
  `tests/interface/test_novidades.py`.

## Conteúdo inicial (SC-2502, FR-7426)

- **90 notas, de 15/09 a 14/11** (`D-010`, P-4 respondida em 14/11). A primeira versão tinha 45 (de
  17/10), a segunda revisão de 14/11 levou a 62, e a extensão a setembro, a 109.
- **Reescritas como anúncio** (`D-011`, FR-7427), depois que o usuário leu as 109 e teve dificuldade de
  entender: título que promete o ganho, duas frases em "você", "Na prática" em 85 das 90 (todas as de
  categoria Novidade), nenhuma palavra do sistema. As miúdas de cada quinzena foram reunidas em notas
  "Pequenas melhorias", e por isso o total caiu de 109 a 90, com os mesmos PRs. A reescrita foi feita
  em três frentes, uma por mês, com a diretriz, três notas-modelo e um conferidor dos mesmos limites
  da suíte; os exemplos que citavam fato não conferido foram generalizados na integração.
- **Todo PR da janela tem destino.** Cada PR mergeado desde 15/09 é citado por uma nota, está em
  `[[sem_nota]]` de `curadoria.toml` com o motivo (51 PRs), ou é só de documentação (154).
  `rascunhar_novidades.py` diz "Nada pendente".
- 55 PRs da janela de outubro entraram na `main` fora da ordem do número — a razão de o roteiro cortar
  pela data do merge.
- **Setembro foi curado em três frentes paralelas**, com as mesmas regras escritas (o guia e as da
  suíte), e revisado na integração: os rótulos entre aspas foram procurados no código, e o texto que
  não aparece literal é título de nota ou exemplo do próprio Edital. A nota de setembro descreve a
  capacidade como ela existe hoje; a tela refeita depois, ou a capacidade substituída, foi para o
  registro com o motivo.
- As datas são a do último merge de cada nota, no horário de Brasília, calculadas dos dados do GitHub.
- As notas foram conferidas no código e na Documentação do Sistema; **não** foram abertas, uma a uma,
  na tela.

## Navegador (SC-2504, UX-804, UX-805)

Entrada `novidades-168` do `.claude/launch.json`, banco `ps_novidades`, como `demo.gestor`:

- primeira entrada: a barra mostra "9+"; a página diz que é a primeira visita, e o número some;
- depois da extensão a setembro, por `curl` com sessão própria (o painel perdeu a sessão para outro
  runserver em `localhost`): a primeira visita diz "desde 15 de setembro de 2026", a linha do tempo
  tem 9 páginas e a última termina em setembro;
- com três notas desmarcadas no banco: a barra mostra "3", e a página abre com "Desde sua última
  visita", listando as três;
- console sem erro; sem rolagem horizontal a 375, 1.280 e 1.440 px; barra recolhida mostra o ponto
  no canto do ícone.

## Não verificado

- A entrada institucional e a troca de unidade têm casos próprios pelo provedor simulado
  (`tests/seguranca/test_novidades_na_entrada_institucional.py`), mas não foram percorridas num
  navegador.
- SC-2501 é validação humana.
