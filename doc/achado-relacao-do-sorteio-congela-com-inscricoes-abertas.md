# A relação do sorteio se congela com o período de inscrições aberto

**Encontrado em**: 27/09/2026, no ensaio da parte 2 do
[teste operacional assistido](roteiro-teste-operacional-assistido-28-2026.md), contra a `main` em
`f6efe0dd`.

**Estado**: **decidido e corrigido em 27/09/2026**, antes da spec do passo 1. Ver
[a decisão e a correção](#a-decisão-e-a-correção-2709), no fim. Até aqui, o texto é o registro como
foi feito.

---

## O que se viu

Edital reduzido do ensaio, com o período de inscrições de 18h56 a 19h20. Às 18h57, com cinco
inscrições submetidas e o período em curso, *"Publicar e congelar a relação"* do recorte
*"Todos os inscritos"* foi aceito:

> Relação congelada em 27/09/2026 18:57 por ensaio.conducao, com 5 participantes.

A relação é o **compromisso do universo** do sorteio. Quem se inscrevesse entre 18h57 e 19h20 ficaria
fora dela, e a única saída seria *"Publicar relação nova, sucedendo a atual"*, com motivo escrito — um
segundo ato público para corrigir o primeiro.

## O que está escrito

A User Story 1 da [`021`](../specs/021-sorteio-publico-auditavel/spec.md) começa por *"Encerradas as
inscrições, quem conduz o certame publica a relação"*, e o cenário 1 dela parte de *"período
encerrado"*. A pré-condição está no **Given**, e nenhum FR a transforma em recusa.
`sorteios/application/relacao.py::publicar_relacao` confere o método, o motivo da sucessão e a
relação vazia, e não confere o período.

**A distribuição já recusa o mesmo caso.** `recusa_por_inscricoes_em_curso` impede distribuir
enquanto o período corre (anexo B da reavaliação de 27/09, §3). As duas telas partem do mesmo fato —
o universo de inscrições —, e só uma delas espera ele se fechar.

## Por que importa no teste

Na parte 2 do roteiro, quem opera pode chegar à tela do sorteio antes de o período acabar: o marco
aparece na página do Edital desde a publicação. Se a pessoa congelar a relação cedo, a ficha registra
uma **recuperação de erro** que a estimativa não previu, e o observador precisa saber que o sistema não
a impediria. O roteiro manda começar a parte 2 **depois** do término.

## O que não se decidiu aqui

- **Recusa ou aviso.** Um Edital pode ter sorteio de um marco cuja relação não depende do período
  (uma segunda chamada, por exemplo). A `021` não trata desse caso.
- **Qual período.** O Evento marcado como período de inscrições é o natural; um Edital com
  reabertura teria dois.

Nada foi corrigido. Registro, não escopo.

---

## A decisão e a correção (27/09)

**A decisão é do usuário, em 27/09/2026**: recusar publicar e congelar a relação enquanto o período
de inscrições do Edital estiver em curso, como a distribuição já recusa.

**O apoio.** A User Story 1 da [`021`](../specs/021-sorteio-publico-auditavel/spec.md) — *"Encerradas
as inscrições, quem conduz o certame publica a relação"* — e o cenário 1 dela, que parte de *"período
encerrado"*. A `D-002` da mesma spec chama a relação de *"compromisso do universo"*, e um universo que
ainda cresce não se compromete. Nenhum FR novo: a pré-condição que estava no *Given* passou a ser
conferida no comando.

**As duas perguntas que ficaram abertas acima.**

- **Recusa ou aviso.** Recusa. O caso da segunda chamada não existe no sistema de hoje: toda relação é
  projeção das inscrições **submetidas** do recorte (`sorteios/domain/projecao.py`), com ou sem Etapa
  de habilitação, e por isso toda relação depende do período. A Etapa de habilitação também não abre
  exceção: o resultado dela depende de distribuir, e distribuir já espera o período.
- **Qual período.** O Evento designado como período de inscrições (`inscricoes/domain/periodo.py`),
  que é o único que o sistema conhece e o mesmo que a distribuição lê. Um Edital com reabertura
  retificaria o término desse Evento, e a regra acompanha.

**A correção.**

- `sorteios/application/relacao.py::publicar_relacao` chama `recusa_por_inscricoes_em_curso`, a mesma
  função da distribuição, sobre o conteúdo da versão vigente, depois de conferir o método. Vale também
  para a relação **sucessora**: suceder com o período aberto repetiria o defeito.
- A função (`avaliacoes/domain/conjunto.py`) ganhou o parâmetro `consequencia`, porque o que cada ato
  deixa para trás é outro. A regra, o código `inscricoes_em_curso`, o status **409** e a saída por
  Retificação são os mesmos. A mensagem diz até quando esperar, o que se perderia e o que fazer:

  > As inscrições ficam abertas até 27/09/2026 às 19:20. Congelar a relação agora deixaria fora do
  > sorteio quem se inscrever depois; publique-a depois do término. Antecipar o término publicado é
  > ato de Retificação; encerrar o Edital é outro ato, mais amplo e irreversível.

- **A tela anuncia antes do clique**, como a Mesa faz com a distribuição: `sorteios/application/previa.py`
  devolve a mesma recusa, e `interface/sorteio.html` a mostra uma vez, acima dos recortes, e não
  oferece o botão de congelar enquanto ela vale.
- **409, e não 404 nem 403**: não entra no inventário de negativas da `033`.

**Testes**: `backend/tests/integration/sorteios/test_relacao_espera_o_periodo.py` (recusa, mensagem,
prévia e a contraprova depois do encerramento), `backend/tests/interface/test_sorteio_espera_o_periodo.py`
(a tela) e o caso novo de `backend/tests/unit/avaliacoes/test_conjunto.py`.
