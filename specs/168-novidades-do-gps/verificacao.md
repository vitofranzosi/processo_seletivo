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

## Revisão editorial de 14/11: a vitrine das capacidades (`D-012`, `D-013`)

*A vitrine saiu em 15/11 (`D-014`; ver a seção seguinte). Fica o registro do que foi medido.*

**O que mudou.** A página ganhou "Descubra o que o GPS já faz", com dez capacidades (seis à vista); o
histórico ganhou a relevância (110 notas: 14 transformadoras, 51 relevantes, 45 incrementais), o "faz parte de"
e a linha enxuta do incremental; o "Desde sua última visita" abre pela mudança de maior peso. As seis
notas "Pequenas melhorias" foram desfeitas em 21 notas de um assunto cada; o kit foi separado em
textos (disponíveis) e peças (condicionadas). Entraram as notas dos PRs mergeados durante a revisão:
a agenda da Etapa (167), a habilitação do assistente (170), a legibilidade das confirmações (#557) e a
própria página. A nota do piloto do assistente deixou de depender de `ASSISTENTE_PILOTO`, que a 170
passou a recusar em produção. O registro continua em "Nada pendente".

**Teste de descoberta — avaliação heurística, e não teste com operador.** Para cada uma de cinco
capacidades, o cartão responde às três perguntas sem abrir o detalhe técnico:

| Capacidade | O que consigo fazer? | Por que facilita? | Onde encontro? |
|---|---|---|---|
| Agenda das entrevistas | Montar a agenda com dias, horários e bancas | "sem montar planilhas"; cada candidato vê o horário | "Por onde começar": distribuição da Etapa, cartão Agenda |
| Centro de Controle | Ver o que falta em cada Edital e de quem é a vez | "um clique leva ao lugar certo" | Processos Seletivos → Edital publicado (com link) |
| Convocação com documentos | Convocar, receber e conferir documentos | "sem e-mail nem planilha" | A convocação de cada lista |
| Barema | Pontuar item a item com total calculado | "acaba a planilha paralela" | Cartão da Etapa pontuada, seção Barema |
| Edital guiado | Montar o Edital e receber o PDF oficial | "documento oficial pronto, em linguagem simples" | Novo Processo Seletivo (com link) |

A SC-2511 — a mesma pergunta feita a alguém da comissão — continua pendente.

**Suíte inteira contra PostgreSQL**, com a `main` de 15/11 integrada: **21 224 passando, 25 pulados,
sem falha** (554s).

**No navegador** (entrada `novidades-168`, `demo.gestor`): a vitrine, o detalhe aberto de uma
capacidade, a linha do tempo com transformadora e incremental, e o celular, sem erro no console e sem
rolagem horizontal a 375 e 1.280 px. **Limitação conhecida:** no celular os seis destaques à vista
ficam empilhados e somam bastante rolagem antes do histórico; um carrossel ou cartões mais baixos no
estreito ficam para depois da validação com pessoas.

**A faixa de identificadores.** A `169` usa FR-7400 a 7435 e UX-800 a 803, que se sobrepõem à faixa
da `168`; a revisão abriu em FR-7601, SC-2511 e UX-821, e a pergunta de quem renumera é a P-5.

## 15/11: a vitrine retirada (`D-014`)

**O que mudou.** A seção "Descubra o que o GPS já faz", os dez cartões, a tabela `[[capacidade]]` e o
"faz parte de" saíram; o arquivo só aceita `[[nota]]`. Ficam a relevância, o peso visual, o bloco da
visita aberto pela mudança de maior peso e as notas de um assunto cada. A primeira visita aponta
"Comece por aqui", na Documentação do Sistema. A limitação do celular da seção anterior deixa de
existir com a vitrine.

**Suíte inteira contra PostgreSQL: 21 190 passando, 25 pulados, sem falha** (610s). São 34 casos a
menos que em 14/11: os da vitrine e das capacidades, parametrizados por cartão, e os das classes que
saíram da folha, contra três novos — o arquivo só com notas, a âncora da primeira visita e a página sem
vitrine.

**No navegador** (`novidades-168`, `demo.gestor`): o histórico vem logo depois do bloco da visita, sem
erro no console e sem rolagem horizontal.

**A curadoria de 15/11.** Três PRs entraram na `main` depois da revisão. O #551 (171) e o #558
(entrega D da 167) ganharam nota própria. O #559 completa o #557 e entrou na nota da legibilidade das
confirmações. O roteiro voltou a "Nada pendente", e o arquivo tem 112 notas.
