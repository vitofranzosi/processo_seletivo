# T125 — o roteiro percorrido pelo navegador

**Executado em** 07/09/2026, contra `ps018_demo` semeado por `seed_demo` neste worktree, servidor
em `127.0.0.1:8018` a partir de `.claude/launch.json` → `spec-018`.

**Como foi percorrido.** Pelas telas, alternando atores, sem shell e sem banco durante a jornada.
Duas ressalvas honestas sobre o instrumento, e não sobre o produto:

- os cliques do painel de navegação falhavam de forma intermitente (a aba fica oculta e a página
  não é desenhada). Onde isso ocorreu, o formulário **da própria página** foi submetido por
  `requestSubmit()` — é o mesmo `POST`, com o mesmo `CSRF` e a mesma validação de servidor; o que
  se perde é a prova do clique, não a do fluxo;
- o código de acesso do candidato foi lido do console do servidor, que é onde o *backend* de e-mail
  de desenvolvimento o escreve. É o que qualquer pessoa faria na demonstração.

---

## O que cada passo mostrou

| # | passo | evidência |
|---|---|---|
| 1 | **Elisa vê o próprio Resultado** | *"Prova objetiva — Eliminada · pontuação 4,0000 — pontuação inferior à nota mínima da Etapa (4,0000 < 6,0000)"*. Ela está **fora do universo do ato** e vê assim mesmo. Fecha o E2E17-004 |
| 2 | **Elisa recorre** | protocolo `REC-2026-PQ6BRQ2F`, instante, situação *"Aguardando análise de admissibilidade"* e objeto nomeado pela Etapa — *"o meu resultado da Prova objetiva"* |
| 3 | **Quem produziu o ato não julga** | como `paulo.presidente`, que consolidou: *"Você não pode julgar este recurso. Você consolidou o resultado atacado."* — e **os botões não são oferecidos** |
| 4 | **A admissibilidade** | como `julia.julgadora`: admitida com motivo escrito, e o formulário de julgamento aparece com as quatro espécies e a Etapa alcançada |
| 5 | **Deferir fixando a correção** | sucessor **HABILITADA · 6,5000**, com a consequência **derivada** da mínima 6,0 — o formulário não tem campo de consequência. O atacado permanece **ELIMINADA · 4,0000** |
| 6 | **A cadeia a jusante reage** | a tela do marco diz *"O ato vigente está obsoleto"* e nomeia as **duas** causas: *"participante reingressou"* e *"resultado superado por recurso"*. Nada foi emitido nem publicado automaticamente |
| 7 | **A progressão retroativa** | na Mesa da Etapa 2: *"Reabilitada por recurso: decisão de 07/09/2026 no recurso REC-2026-PQ6BRQ2F."* |
| — | **O que a candidata lê ao fim** | *"Habilitada · pontuação 6,5000"*, com *"Resultado corrigido em cumprimento da decisão de 07/09/2026 no recurso REC-2026-PQ6BRQ2F. O resultado anterior permanece registrado."*, e o recurso listado em **Seus recursos** |
| — | **A janela declarada** | a lista administrativa mostra **"Dentro do prazo"** — o degrau 8 computando a janela de 5 dias que o `seed_demo` declara no marco |

Os passos 8 a 11 — vedação de piora, reavaliação determinada, definitividade e a janela vencida —
têm cobertura automatizada própria em `test_pejus.py`, `test_reavaliacao.py`,
`test_definitividade.py` e `test_janela.py`, e não foram repetidos à mão.

---

## O que a caminhada encontrou

**O roteiro não era percorrível, e a razão não estava no produto.** Dois defeitos do
`seed_demo`, os dois corrigidos:

1. **as inscrições semeadas eram inalcançáveis pelo próprio dono.** Elas nasciam com
   `identity_subject` sintético, e nenhum login produz esse valor: quem entrasse com o e-mail da
   Elisa criava uma identidade nova e vazia, e a inscrição dela respondia 404 — corretamente, e
   para ninguém. O seed passa a criar a identidade e a credencial verificada, que são exatamente as
   linhas que o produto cria quando alguém prova o controle do e-mail;
2. **quem consolidava não era a presidência.** O `seed_demo` consolidava e emitia como
   `gustavo.gestor`, que o seletor de identidade nem oferece — e o passo 3 ficava indemonstrável,
   porque não havia como entrar como quem produziu o ato atacado. Os dois atos passam a ser
   praticados por `paulo.presidente`, que é quem os pratica no certame e quem o roteiro nomeia.

Nenhuma das duas correções é atalho de demonstração: as duas aproximam o seed do que o produto faz.
