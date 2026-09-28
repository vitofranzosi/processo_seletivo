# A relação do sorteio se congela com o período de inscrições aberto

**Encontrado em**: 27/09/2026, no ensaio da parte 2 do
[teste operacional assistido](roteiro-teste-operacional-assistido-28-2026.md), contra a `main` em
`f6efe0dd`.

**Estado**: **registrado, não corrigido.** Não bloqueia nada — é o contrário: o sistema deixa fazer o
que deveria recusar. A decisão de corrigir é do usuário.

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
