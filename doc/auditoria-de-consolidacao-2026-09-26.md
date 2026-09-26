# Auditoria de consolidação — o que as auditorias anteriores ainda representam hoje

**Data:** 26/09/2026
**Contra:** a `main` em `bb774d9` (merge do #168, 25/09 23:23), com a worktree sincronizada com `origin/main`
**Atualização:** 26/09, depois dos merges do #171 (`2f38dc2`, só o registro do achado), do #173 (`47876ad`,
a 044) e do #172 (`8e6fb4a`). Mudaram RC-51 a RC-54, RC-56 e RC-101, as contagens da §1 e dos anexos 5 e 6,
e todas as passagens deste documento e desses dois anexos que tratavam os três PRs como abertos. Depois,
no mesmo dia, o #183 (`8e7c698`) corrigiu o `ValorDeFato`, e o RC-101 passou a RESOLVIDO, com as contagens,
o anexo 6 e as decisões nº 19 e nº 21 do anexo 7. O inventário da §2 e a reconciliação entre lotes
registram o que as fontes eram, e só ganharam o desfecho. Fora isso, o documento descreve a `main` em
`bb774d9`.
**Objeto:** os achados, recomendações e decisões de **21 relatórios e registros** produzidos entre 02/09 e
25/09 — ver o inventário na §2.
**Método:** leitura de código, testes, specs e histórico do git. **Nada foi executado**: nem a suíte, nem
o servidor, nem um percurso pela interface. Quando uma conclusão depende de percurso, ela vem marcada
`[VALIDAR]`.
**Anexos:** as sete matrizes por lote, com o bloco completo de cada achado — origem, recomendação, rastro
posterior, specs, evidência com `caminho:linha`, estado, pertinência, resíduo e confiança —, em
[`auditoria-de-consolidacao-2026-09-26/`](auditoria-de-consolidacao-2026-09-26/).

> **A pergunta.** De tudo que já foi identificado nas auditorias anteriores, o que ainda representa uma
> lacuna real do sistema hoje?

---

## Como ler este documento

- **A §3 é a reconciliação; os anexos são a evidência.** Os sete lotes foram lidos de forma independente
  e, em quatro pontos, discordaram entre si. Nesses casos a §3 decide e explica por quê (ver o fim da §3).
- **`RC-nn` é o identificador da unidade consolidada.** Ele é criado aqui e não colide com nenhum
  identificador do repositório. Cada unidade junta todos os IDs antigos que descrevem o mesmo problema,
  por exemplo `ACH-41` + `E-4` + `13.5`.
- **Estados.** RESOLVIDO · RESOLVIDO POR OUTRO CAMINHO · PARCIALMENTE RESOLVIDO · NÃO IMPLEMENTADO ·
  IMPLEMENTADO, MAS NÃO VALIDADO · SUPERADO / OBSOLETO · DUPLICADO / ABSORVIDO · CONTRADITO POR DECISÃO
  POSTERIOR.
- **Grupos do resíduo.** **A**, lacuna real: contradiz requisito escrito, deixa um fluxo incompleto ou
  publica o que não executa. **B**, evolução relevante. **C**, ideia opcional. **—**, sem resíduo.
- **"Fora da main"** quer dizer que a implementação existe numa branch ou num PR aberto que ainda não foi
  mesclado. Esses itens são classificados como IMPLEMENTADO, MAS NÃO VALIDADO. Para a `main` de hoje, a
  lacuna continua aberta.

---

## 1. Resumo executivo

### Estado geral

Os sete lotes produziram **~300 linhas de rastreabilidade**, a partir de 21 fontes, e elas se
sobrepõem. As **34 linhas** que os próprios lotes marcaram como DUPLICADO / ABSORVIDO, e todas as
repetições entre relatórios, foram fundidas na unidade que as absorve. O resultado são **110 unidades
consolidadas** na matriz da §3. Por isso nenhuma unidade leva o rótulo DUPLICADO / ABSORVIDO: a
consolidação é a própria fusão, e a coluna "IDs antigos" de cada linha registra o que foi fundido nela.

| Estado | Unidades |
|---|---:|
| RESOLVIDO | 28 |
| RESOLVIDO POR OUTRO CAMINHO | 3 |
| PARCIALMENTE RESOLVIDO | 11 |
| NÃO IMPLEMENTADO | 48 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 5 |
| SUPERADO / OBSOLETO | 3 |
| CONTRADITO POR DECISÃO POSTERIOR | 12 |
| **Total** | **110** |

Lido pela pergunta da auditoria:

- **31** unidades estão resolvidas, pelo caminho recomendado ou por outro.
- **15** foram eliminadas por decisão consciente (12) ou por obsolescência (3) e **não devem voltar ao
  backlog** (§7).
- **70** carregam algum resíduo. São 64 unidades abertas, parciais ou não validadas, mais seis resolvidas
  que deixaram uma sobra: RC-02, RC-45, RC-54, RC-72, RC-87 e RC-102. Separadas por natureza:

| Grupo | Unidades | O que são |
|---|---:|---|
| **A** — lacuna real | **11** | contradizem requisito escrito, deixam fluxo incompleto ou publicam o que não executam |
| **B** — evolução relevante | **35** | ganho claro, sem defeito |
| **C** — opcional | **24** | polimento e higiene |

- **Validação antes de trabalho.** Das 11 unidades A, **nenhuma está mais em PR aberto**: RC-52 e RC-53
  entraram na `main` pelo #173, e o RC-54, que é C, pelo #172, os três em 26/09. **Três exigem percurso pela tela** antes de qualquer spec:
  RC-08, RC-58 e, entre as B, RC-32. E **uma depende do Ifes**: RC-92.
- **O que sobra de fato como trabalho novo de grupo A são oito unidades**: RC-29, RC-37, RC-38, RC-39,
  RC-72, RC-78, RC-79 e RC-80. Quatro delas são o painel da `038` e a Retificação. O RC-101, que foi a
  nona enquanto esteve desbloqueado, foi corrigido pelo #183 em 26/09.

**O fato que mais pesa.** Desde a auditoria de convergência de 20/09, **as três recomendações
prioritárias dela não receberam trabalho nem decisão registrada**. São elas: fechar a `038`, derivar o
`status` do Evento e a `D-G5`. O esforço foi para a visão institucional (`040`–`042`), para o estudo de
esforço e sua onda de correções, para a `043` e para a `044`. Foi trabalho real e bem feito, mas em
outra direção. **Das sete condicionantes de saída do piloto (`C1`–`C7`), só a `C3` fechou.**

### Mapa residual — só o que merece atenção

| | Unidade | Grupo | Onde está a prova |
|---|---|---|---|
| RC-78 | O painel afirma **"Nenhuma condição de atenção"** a quem só enxerga parte do Processo | A | `processo_detalhe.html:140` · `views.py:3946-3960` |
| RC-79 | Recurso **aguardando admissibilidade** não produz sinal | A | `supervisao.py:1165` |
| RC-80 | `schedule.status` é declarado **derivado** e nada o deriva, gerando `UX-002` permanente; `UX-001`/`UX-002` levam a uma Retificação que não os resolve | A | `mutabilidade.py:432` · `supervisao.py:1273` |
| RC-37 | A Retificação **não acrescenta Modalidade**: Edital publicado sem conserto (`D-G5`, decidida em 19/09) | A | `retificacao.py:1054` |
| RC-29 | Etapa com **duas avaliações** publica ato que **nunca consolida**, e há dois irmãos com o mesmo defeito de momento | A | `validation.py:234` · `regra.py:57-95` |
| RC-58 | **Cadastro de reserva não é convocável**: convocar exige vaga faltante apurada, e `reserveLimit` publicado não tem efeito | A `[VALIDAR]` | `convocar.py:100-152` · nenhum consumidor de `reserveLimit` |
| RC-72 | **"Fonte de demonstração"** do sorteio pode ser escolhida e publicada em produção | A | `fontes/__init__.py:83-92` · `production.py` sem guarda |
| RC-39 | O **"O que mudou"** público omite a mudança de recorte do documento, contra a `FR-130` da `024` | A | `alteracoes.py:89-95` |
| RC-52/53 | Recorte transversal e lista exigida gravada: **integrados pelo #173 em 26/09**, com a Mesa percorrida; falta só recompor o 140/2025 (T065) | — `[VALIDAR]` | `documentos.py:206-290` · `mesa.py:135` · `inscricoes/0005` |
| RC-101 | `ValorDeFato` era append-only **por uma camada só**: **corrigido pelo #183 em 26/09**, com gatilho e guarda de modelo | — | `papeis.py:39` · `inscricoes/models.py:137-183` |
| RC-08 | Restaurar o rascunho local **perde coleções aninhadas e regrava a perda**, contra a `FR-020` da `002` | A `[VALIDAR]` | `rascunho.js:81-133` (inalterado desde 08/09) |
| RC-38 | Janela recursal, corte e reversão "podem nascer" por Retificação, **mas a tela não oferece o caminho** | A (janela) / B | `mutabilidade.py:515-548` · `retificacao.py:764,852,859` |
| RC-92 | **Autenticação institucional real** | A (depende do Ifes) | `seguranca/api/authentication.py:7-23` |
| RC-32 | A tela do Edital **publicado** mostra **"Impede — corrija antes de publicar"** quando as inscrições encerram | B `[VALIDAR]` | `views.py:845-847` · `detalhe.html:168-180` |
| RC-47/48 | Portal: página da seleção com o título do Processo, **sem as vagas por Modalidade** e **sem o prazo recursal** na página pública do resultado | B | `selecao.html:2,23,144` · `resultado.html` |
| RC-30 | `D-G1` (marco sem declaração de corte vira impedimento) não executada | B | `validation.py:1735` |

### Topologia da dívida

A dívida que restou **não está espalhada**. Ela se concentra em quatro focos, e nenhum deles reescreve o
que já foi publicado. As duas camadas append-only seguiam de pé na última medição (`33 de 33`, 20/09), e
nenhum commit da `main` tocou `seguranca/papeis.py` nem as migrations desde então. A única exceção de
integridade era o RC-101, uma tabela protegida por uma camada só, sem dano observado. O #183 a corrigiu em
26/09, e nenhuma tabela append-only depende mais de uma camada só.

1. **Condução**: quatro unidades A e B no painel da `038`. É a superfície mais nova, e a única que
   quebra o padrão mais forte do produto, a ausência honesta.
2. **Publicar o que não se executa até o fim**: cinco unidades A. As duas avaliações, o cadastro de
   reserva, a Modalidade que não se acrescenta, a fonte de demonstração e os objetos que "podem nascer"
   sem porta. É a mesma doença que a `032` atacou, em pontos que ela não cobriu.
3. **Trabalho decidido e não feito**: uma unidade A, o "O que mudou" que a decisão de 25/09 mandou
   para a fila das diretas e ninguém pegou. As outras duas foram feitas em 26/09: a `044` entrou pelo
   #173, e o `ValorDeFato` foi corrigido pelo #183.
4. **Implantação**: autenticação, correio, retenção e Registro Acadêmico. É dívida real, mas com
   dependência externa.

O que **não** apareceu como dívida: avaliação, resultado, classificação, sorteio executável, recurso do
lado do candidato e matrícula no lado que sai. As auditorias de 13/09 e 16/09 os apontavam, e fecharam.

### Próxima onda recomendada

- **Onda A — fechar o que já foi decidido e o que afirma o que não sabe.** Fechar a `038` (RC-78, RC-79,
  RC-80, RC-81, RC-82); o RC-39; a varredura "publica e não
  executa" (RC-29, RC-30, RC-72, RC-32). É pequena e média, quase toda com decisão já tomada.
- **Onda B — Edital publicado com conserto e oferta executável até o fim.** Uma Retificação que acrescenta
  o que o contrato já permite (RC-37 + RC-38) e o cadastro de reserva convocável (RC-58), este depois
  de validado.
- **Onda C — candidato e documento.** O portal (RC-47, RC-48, RC-49), as conferências baratas do
  documento (RC-20, RC-21, RC-12, RC-31), o reuso com estado de revisão (RC-45) e as diretas da
  composição (RC-09, RC-10, RC-11).
- **Trilha paralela de implantação**: RC-92, RC-93 e RC-94, que dependem do Ifes.

---

## 2. Inventário das auditorias encontradas

Estão em ordem cronológica. A coluna **"Estado da fonte"** diz o que já venceu no próprio documento. Nenhum
deles deve ser lido sozinho.

| # | Documento | Data | Objetivo e escopo | IDs que produz | O que deixou para depois | Estado da fonte hoje |
|---|---|---|---|---|---|---|
| 1 | [`auditoria-exploratoria-e2e-2026-09-02.md`](auditoria-exploratoria-e2e-2026-09-02.md) | 02/09 | E2E funcional de 001–012; jornadas por ator; handoffs, autorização, escala | `E2E-001…021`, gate da 013, gates de produção G1–G4/G22 | notificações de handoff, retenção, identidade real | quase toda fechada; resíduo em RC-92/93, RC-67 |
| 2 | [`doc/e2e/*`](e2e/) (014, 015, 016, 017, 018, 019, 020, 025) | 03–12/09 | percurso exploratório de cada feature | `E2E14-…`, `E2E15-…`, `G16-…`, `O16-…`, `E2E17-…`, `E2E18-…`, `019 §4`, `POLISH020-…` | vários "pendentes" por feature | resíduos em RC-38, RC-46, RC-49, RC-62, RC-63 |
| 3 | [`avaliacao-de-capacidade-editais-2026-09-07…12.md`](avaliacao-de-capacidade-editais-2026-09-12.md) (5 docs) | 07–12/09 | sete (depois treze) Editais reais contra o repositório | `L-1…L-6`, pressões, "lacunas de autoria" | L-2 (Etapa por modalidade), heteroidentificação, escala | cumulativa; a de 12/09 é a última palavra |
| 4 | [`achados-editais-externos.md`](achados-editais-externos.md) | 07–12/09 | perguntas de domínio dos Editais lidos | `P-1…P-13` | P-2/P-3 (cadastro de reserva, validade), P-8, P-13 | perguntas, não defeitos — RC-58 é o que dela sobra como lacuna |
| 5 | [`auditoria-exploratoria-ux-2026-09-13.md`](auditoria-exploratoria-ux-2026-09-13.md) | 13/09 | primeira UX ponta a ponta | top 10, QW1–13, 11.1–11.5, anexo §16 | visão global, "Meu trabalho" | top 10 fechado ou absorvido |
| 6 | [`auditoria-granularidade-normativa-2026-09-15.md`](auditoria-granularidade-normativa-2026-09-15.md) | 15/09 | fidelidade do Edital real (140/2025) à estrutura normativa | `AX-1…AX-17`, experimentos E-1…E-3, H-1…H-3 | quase tudo — pediu decisões ao usuário | **ficou 4 dias fora do git**; re-varrida em 19/09 |
| 7 | [`auditoria-exploratoria-ux-2026-09-16.md`](auditoria-exploratoria-ux-2026-09-16.md) + [diário](diario-reauditoria-2026-09-16.md) | 16/09 | reauditoria de UX com seis cenários | `ACH-01…ACH-61`, raízes `E-1…E-7`, melhorias 13.1–13.7 | P0 a P2 | os seis P0 fecharam (030–037) |
| 8 | [`reavaliacao-ux-2026-09-18.md`](reavaliacao-ux-2026-09-18.md) | 18–19/09 | mede o que a 030–037 fechou | fechamentos; **`D-G1…D-G5`** (§14-bis) | D-G1, D-G2, D-G3, D-G5 (**decididas, não executadas**) | medições valem; decisões pendentes de execução |
| 9 | [`relatorio-longitudinal-produto-001-a-037-2026-09-19.md`](relatorio-longitudinal-produto-001-a-037-2026-09-19.md) | 19/09 (versionado em 21/09) | retrato de produto 001–037 | preâmbulo com 7 itens | heteroidentificação, barema, notificação interna | **fora do git por 2 dias**; o item 6 ("42 controles, e cresceu") é artefato de contagem (§7) |
| 10 | [`varredura-dos-dezessete-2026-09-19.md`](varredura-dos-dezessete-2026-09-19.md) | 19/09 | re-varredura dos AX | estado dos AX | — | vencida: 3 AX fecharam depois |
| 11 | [`auditoria-de-convergencia-pos-038-2026-09-20.md`](auditoria-de-convergencia-pos-038-2026-09-20.md) | 20/09 | maturidade pós-038; "pronto para piloto controlado" | `N-01…N-10`, condicionantes `C1…C7` | seus três "próximos investimentos" | **1 de 7 condicionantes fechada** (C3) |
| 12 | [`docs/visao-sistema/index.html`](../docs/visao-sistema/index.html) | 20/09 | o sistema reconstruído do código | repete N-*, D-G*, C7; acrescenta 4 itens | — | vencido em N-03 |
| 13 | [`estudo-esforco-de-cadastro-2026-09-21.md`](estudo-esforco-de-cadastro-2026-09-21.md) + [diário](diario-estudo-esforco-2026-09-21.md) | 21/09 (revisto em 25/09) | esforço de autoria em 5 Editais; fidelidade do PDF | §5.1–5.12, A/M/B, E1–E11, "três decisões" | E2, E5, E10, TF-1, estado de revisão do reuso | grupos A/B/C do §12 corrigidos em 25/09 |
| 14 | [`achado-documento-condicional-no-portal.md`](achado-documento-condicional-no-portal.md) | 25/09 | reproduz AX-14 pela tela | — | virou a 044 | contenção por #161; 044 mesclada pelo #173 em 26/09 |
| 15 | [`conferencia-envio-e-analise-documental.md`](conferencia-envio-e-analise-documental.md) | 25/09 | envio e análise do documento condicional | — | "O que mudou" sem recorte | resíduo RC-39 sem dono |
| 16 | [`inventario-supervisao-do-processo.md`](inventario-supervisao-do-processo.md) | 09/09 | o que a supervisão deveria ver | Parte 3 | status do Evento "declarado" | premissa contradita pelo contrato da 026 (RC-80) |
| 17 | 15 achados avulsos `doc/achado-*.md` | 08–25/09 | um defeito ou lacuna cada | — | vários | ver RC-13, RC-26, RC-29, RC-33, RC-38, RC-41, RC-52, RC-74, RC-103, RC-108 |
| 18 | registros de decisão: `decisao-*.md`, `descoberta-*.md`, `decisoes-pre-vertical.md`, `briefing-*.md` | 03–25/09 | decisões de domínio e de escopo | D-1…D-4, decisão C da 018, D1–D5 do recorte | — | usados para o rótulo CONTRADITO (anexo 7, Parte 2) |
| 19 | PRs abertos #171, #172, #173 e issue #117 | 15–26/09 | — | — | — | #173 = a 044 implementada; #171 bloqueado por ela. **Os três mesclados em 26/09**; o #171 era só o registro, e a correção (RC-101) veio no #183, no mesmo dia |
| 20 | branch local `claude/spec-039-alcance` | 19–20/09 | spec 039 (catálogo de Modalidades), nunca mesclada | — | — | contradita pela decisão de 25/09 (RC-102) |
| 21 | notas de memória do usuário | — | decisões registradas fora de `doc/` | — | — | três delas decidem classificação (sem carga retroativa; equipe de 2–3; ValorDeFato após a 044) |

**Lição de método, que se repetiu duas vezes.** Duas fontes centrais ficaram fora do git por dias. A de
15/09 ficou quatro dias; a de 19/09, dois. Features inteiras foram priorizadas sem elas. Esta auditoria
só é possível porque as duas foram versionadas depois. O mesmo risco existe hoje com a branch da `039`,
que parece trabalho em curso e não é.

---

## 3. Matriz consolidada de rastreabilidade

Uma linha por unidade consolidada. A evidência é o ponto de código que decide; o bloco completo de cada ID
antigo está no anexo indicado na coluna "Anexo". Caminhos relativos a `backend/processo_seletivo/`, salvo
quando indicado.

### 3.1 Composição e autoria do Edital

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-01 | 13/09 #1 · 11.1 | vagas imediatas publicadas sem linha no quadro → uma declaração de vagas | 025, 027 | `validation.py:2401-2418` (completude com a ampla) | RESOLVIDO | não | — | nenhuma | 2 |
| RC-02 | 13/09 #3 · QW1 · E-5 · ACH-04 | ajuda invisível ou longe do campo → ajuda junto do campo | 030 (`como-preencher` por etapa, recolhido) | `compor_perfis.html:23-90` | RESOLVIDO POR OUTRO CAMINHO | parcialmente | ACH-04: a FR-426 vale na Classificação e não na etapa Perfis · C | nenhuma | 2, 3 |
| RC-03 | 13/09 #6 · 11.2 · ACH-09/10/36 · LONG-6 | Classificação com 28–30 decisões → perguntas que revelam blocos | 030, 035, 037 | 6 controles na chegada de um marco simples; `_marco.html` tem 42 tags, 12–13 delas `hidden` | RESOLVIDO | não | o "42, e cresceu" do longitudinal é artefato de contagem (§7) | nenhuma | 2, 3 |
| RC-04 | ACH-16 · D-G4 | "Peso (opcional)" que impede → antecipar | 037; D-G4 encerrou | `_etapa.html:146` | RESOLVIDO | não | — | nenhuma | 3, 4 |
| RC-05 | estudo §5.1 · A1 · QW1 · §9.A.1 | "Cadastro Reserva limitado" inalcançável; PDF dizia "ilimitado" | #159 (`cf18a6b`) | `validacao.js:50` (`:checked`) | RESOLVIDO | não | ver RC-58: o limite sai publicado e não tem efeito | nenhuma | 6 |
| RC-06 | estudo §5.4 · §5.5 · §5.8 · §5.10 · QW2–4, 8, 11 | `*` ausente; UUID no IMPEDE; seletor de Evento ambíguo; bloco do quadro que não some | #162, #163 | `views.py:727-775` (`nomes_dos_caminhos`); `_etapa.html:27,114` | RESOLVIDO | não | — | nenhuma | 6 |
| RC-07 | E-3 (exp. 15/09) · estudo §6.2/§6.4/E1/A2 · ACH-61 | nenhum "duplicar"; ~530 interações na etapa Perfis → duplicar e aplicar a todos | 030 (método comum); 043 (`0479f4e`) | `editais/domain/duplicacao.py`; 043 mediu 101 interações | PARCIALMENTE RESOLVIDO | parcialmente | TF-1 (aplicar a todos) e a curva linear · B | nenhuma imediata; TF-1 só com evidência de correção em massa | 5, 6, 3 |
| RC-08 | AX-16 · NOVO-2 do lote 5 | restaurar rascunho local perde Modalidades, regras, fatos, quadro e marcos da cópia; a tela fica inerte; o autosave regrava | nenhuma; `FR-020` da 002 exige "retomar sem redigitação" | `interface/static/interface/rascunho.js:81,104-133,225` (último commit `4e9f0a0`, 08/09) | NÃO IMPLEMENTADO | sim | perda silenciosa na etapa mais cara · **A** `[VALIDAR]` | validar pela tela; corrigir, ou restringir a salvaguarda às etapas sem coleção aninhada | 5 |
| RC-09 | estudo §5.7 · §5.11 · M4 · M12 | quadro mostra "Modalidade nova"; seletor da ampla com rótulo antigo até gravar | nenhuma | `views.py:2504`; `_perfil.html:187-197` (o mesmo cartão já usa `hx-get` sem JS inline) | NÃO IMPLEMENTADO | sim | quantidade na lista errada no reuso · B | corrigir (direta) | 6 |
| RC-10 | estudo §5.12 · M8 · M14 · QW6/13 | Revisão soterra o IMPEDE sob ~45 avisos repetidos | #163 colapsou só as famílias por Evento | `templatetags/interface_extras.py:335-351`; nenhuma ordenação por severidade | PARCIALMENTE RESOLVIDO | sim | colapso por Perfil (32 dos 45) e severidade primeiro · B; âncora do ano = decisão FR-344 | corrigir (direta) | 6 |
| RC-11 | estudo M16 | `<select multiple>` de Etapas: clique simples zera a seleção | nenhuma | `_marco.html:104-114` | NÃO IMPLEMENTADO | sim | caixas de marcação · B | corrigir (direta) | 6 |
| RC-12 | AX-9 · E2E15 opp. (a) · NOVO-1 do lote 5 | teto de inscrições por candidato executado e não publicado; **nem declarável na composição** | `FR-063` da 015 (MUST poder publicar) | `inscricoes/application/submissao.py:307` executa; nenhum uso em `pdf.py`, portal ou `forms.py` | NÃO IMPLEMENTADO | sim | norma executada sem publicação · B | corrigir: renderizar e decidir o campo na etapa Inscrição | 5, 1 |
| RC-13 | achado atribuições por polo · AX-11 · estudo E2 · §15 decisão 2 · TF-1 | o que o Edital declara uma vez mora no Perfil (16 cópias) | 043 (digitação); `c0403a9` (cabeçalho) | `editais/models/perfis.py:33-35` | PARCIALMENTE RESOLVIDO | parcialmente | PDF e Retificação em N cópias, sem conferir igualdade · B | **decisão E2** do usuário antes de spec | 7, 6, 5 |
| RC-14 | AX-5 · AX-6 · P-5 · H-1/H-2 · ACH-52 · estudo §7.3 · B4 | Curso, Área, Campus e turma sem forma | 040 G-004 registra o limite | `editais/models/perfis.py:9-95` | NÃO IMPLEMENTADO | parcialmente | custo de leitura, não integridade · C | nenhuma isolada (junto de RC-64) | 5, 3, 1 |
| RC-15 | estudo §5.6 · M5 · QW5 | Casas decimais, Arredondamento e Alvo num marco de sorteio | #162 escondeu o Alvo | `_marco.html:156-167` | PARCIALMENTE RESOLVIDO | parcialmente | decisão de domínio sobre o que a publicação exige · C | decisão do usuário | 6 |
| RC-16 | ACH-03/15 · ACH-05 · ACH-07 · ACH-11 · ACH-13/34 · ACH-14 · ACH-19 · estudo B5 · M9 · §7.1 · B10 · E2E14 §4 | microcópia e acabamento da composição (selos, "Chave" inventada, "marcado", Cronograma sem painel etc.) | parte em 030/037 | ver anexos 2 e 6, item a item | PARCIALMENTE RESOLVIDO | parcialmente | polimento · C | varredura de polish, sem spec | 2, 6, 1 |

### 3.2 Documento publicado (PDF)

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-17 | AX-13 | nove cabeçalhos idênticos "perfil Tutor Presencial" | `c0403a9` | `publicacoes/infrastructure/pdf.py:1940-1952` | RESOLVIDO | não | — | nenhuma | 5, 7 |
| RC-18 | estudo B1 · QW7/14 · §9-bis 1–3 | "Nº" cortado; datas em três linhas; linhas fundidas | #164 (`d0352f5`) | `pdf.py:751-759, 924-961`; `tests/unit/publicacoes/test_tabela_do_documento.py` | RESOLVIDO | não | sem verificação visual nesta auditoria | nenhuma | 6 |
| RC-19 | ACH-50 · 13.7(b) | documento de sorteio publicava método falso | 032 | `pdf.py:1238-1330, 1402` | RESOLVIDO | não | — | nenhuma | 3 |
| RC-20 | AX-8 | capa usa o título ("EDITAL 140/2025") e o rodapé usa o número (149/2026) | nenhuma | `pdf.py:879-889`; `validation.py:1366-1370` só exige título | NÃO IMPLEMENTADO | sim | o ato se identifica com dois números · B | corrigir: conferir título × número/ano na publicação | 5 |
| RC-21 | AX-12 · estudo §14 | remissão "ANEXO IV" sem anexo publicado; **materializou-se** no 140/2025 | 020 | `validation.py:2104-2161` não lê as seções | NÃO IMPLEMENTADO | sim | integridade referencial · B | corrigir: aviso na Revisão | 5 |
| RC-22 | estudo §9.A.3 · §9-bis 4 · Caso 3 | Evento só com data sai "às 00h" (9 de 11; 11 de 13) | nenhuma | `_evento.html:48-50` (`required`); `publicacoes/infrastructure/humano.py:53-80` | NÃO IMPLEMENTADO | parcialmente | falta o estado "sem hora declarada" · B | decisão de modelo de instante | 6 |
| RC-23 | estudo M7 · §9.B | fecho com cargo, sem nome, portaria, local nem data; catálogo em código | 008 FR-033…046 | `publicacoes/domain/autoridades.py:27-63` | NÃO IMPLEMENTADO | parcialmente | antes de produção · B `[VALIDAR com o Cefor]` | validar o fecho com o Cefor | 6 |
| RC-24 | AX-3 · estudo M10 · A5 · E5 · §15 decisão 3 | 12 seções fixas; oito seções do 140/2025 viram parágrafo; inscrição antes dos Perfis | 006 FR-034/036 | `editais/domain/secoes.py:1-11, 83-110` | NÃO IMPLEMENTADO | sim, como decisão | hierarquia do documento · B | **decisão do usuário** | 5, 6 |
| RC-25 | estudo A9 · E10 · §15 decisão 1 | 0 de 7 atos normativos transcritos; LGPD citada sem existir | nenhuma | seções textuais livres | NÃO IMPLEMENTADO | parcialmente | processo do Cefor · C | **decisão E10** (redação no sistema × transcrição) | 6 |
| RC-26 | estudo M6 · B3 · ACH-18/33 · ACH-21 · AX-2 · anexo sem destinatário | total de vagas ausente; numeração tela × PDF; requisito × documento; anexo sem finalidade | 020, 024 | `pdf.py:1658-1708`; `compor_conteudo.html:19` | NÃO IMPLEMENTADO | parcialmente | polimento · C | diretas oportunistas | 6, 5, 2 |

### 3.3 Validação: executabilidade antes de publicar

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-27 | E-7 · ACH-49 · ACH-46 (a,b,c) · 13.7 · 13/09 #10 · QW2 · E2E-017 | a validação não perguntava se o Edital executa | 032, 037 | `validation.py:1660-1805` (Perfil sem marco, sorteio sem método); `views.py:2855-2868` (corte sempre oferecido) | RESOLVIDO | não como raiz | a **classe** continua gerando casos: RC-29, RC-58, RC-72 | nenhuma | 3 |
| RC-28 | AX-14 · AX-17 · E-2 (exp.) · achado do portal §3 | documento publicado diz "toda a modalidade"; a execução aplica a um Perfil só | #161 (`01d9163`) | `validation.py:2213-2275` (IMPEDE `document_requirement_modality_scope_ambiguous`) | RESOLVIDO | não | o custo 5n segue em RC-52; o acervo anterior a 25/09 fica em `[VALIDAR]` | nenhuma | 5, 6 |
| RC-29 | achado duas avaliações (21/09) · LONG-1 · NOVO-1 do lote 7 | `evaluationsPerRegistration > 1` publica e a consolidação recusa a **Etapa inteira**; eliminatória pontuada sem nota mínima e decisória não eliminatória têm o **mesmo** defeito de momento | 012, 013, 032 (não cobre) | `validation.py:234` (`minimo=1`); `resultados/domain/regra.py:57-95`; `tests/integration/resultados/test_prontidao.py:67` | NÃO IMPLEMENTADO | sim, na forma **aviso** — a D-008 (03/09) recusou proibir na elaboração o que o Edital pode publicar | ato imutável que não conclui · **A** | corrigir: aviso na Revisão + `como-preencher`; spec de combinação só com Edital de dupla leitura | 7, 3 |
| RC-30 | D-G1 · issue #117 | marco sem declaração de corte publica com aviso → **impeditivo** (decidido em 19/09); subtração por código | 032 FR-461 | `validation.py:1735` (`WARNING`); `test_hardening_pos_auditoria.py:1100` prende o aviso; `retificacoes.py:583-588` | NÃO IMPLEMENTADO | sim | decisão tomada e não executada · B (o corte pode nascer por Retificação, o que atenua) | spec curta, e a #117 junto | 4, 7 |
| RC-31 | AX-1 · AX-7 (resíduo) · AX-11 · E-1 (exp.) | nenhuma conferência **entre Perfis**: 3% × 30% da mesma lei; "menor valor" × "maior" no desempate | 043 (cópia exata); 044 confronta só a **denominação** | `validation.py:2563` (confronto dentro da linha); `retificacao.py:335` (critério só retifica a ordem) | PARCIALMENTE RESOLVIDO | sim, como **aviso** — mover para o Edital foi recusado em 25/09 | integridade do publicado · B | spec curta: aviso de divergência entre Perfis de mesmo código | 5 |
| RC-32 | ACH-29 · NOVO-1 do lote 2 | a validação de publicação continua na tela do Edital **publicado**; hoje, com `agora`, ela exibe **"Impede — o período de inscrições encerrou… antes de publicar"** e julga o relacional, não a versão vigente | 028 (impeditivo novo) | `interface/views.py:2787` → `_pendencias` → `validate_for_publication(…, ato=ATO_DE_PUBLICACAO, agora=agora)` (`:845-847`); `detalhe.html:168-180` | NÃO IMPLEMENTADO | sim | falso impedimento em ato publicado · B `[VALIDAR]` | corrigir: validar a versão vigente com o ato da Retificação, ou não validar publicado | 2 |
| RC-33 | achado igualdade da soma · achado ampla não remapeada (instância) | a soma não lia a ampla declarada | 027 FR-317 | `validation.py:2401-2418` | RESOLVIDO | não | — | nenhuma | 5 |
| RC-34 | N-08 · §6 da convergência | os avisos de composição do Edital não chegam à Atenção | 038 FR-565 (catálogo fechado) | `supervisao.py:495-506` | NÃO IMPLEMENTADO | parcialmente | a convergência mandou **não** juntar sem decidir a fronteira · C | nenhuma; revisitar depois de RC-30 | 4 |

### 3.4 Retificação

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-35 | 13/09 #7 · QW9 · 11.5 · 13/09 §9.6 · anexo §16 · decisão de mutabilidade | JSON Pointer e UTC na Retificação; alcance sem decisão → renderizador único; contrato | 026; `_onde_e_campo` | `editais/domain/mutabilidade.py:121-133`; `tests/contract/test_mutabilidade.py:303,339` | RESOLVIDO POR OUTRO CAMINHO | não | — | nenhuma | 2, 5 |
| RC-36 | E2E-001/002/021 · E2E14-005 · E2E17 §13 | devolução e cancelamento; retificar a espécie do alvo; objetos sem tela | 026 (razão normativa) | anexo 1 | RESOLVIDO | não | — | nenhuma | 1 |
| RC-37 | **D-G5** · REAV §13 · convergência §20.3 · 039 US2 | Edital publicado sem a ampla (ou sem uma cota) **não tem conserto** → Retificação que acrescenta Modalidade, com cinco restrições | nenhuma na main; a US2 da 039, não mesclada, a absorvia | `interface/retificacao.py:1054` (`SECOES_QUE_ACRESCENTAM = {perfis, cronograma, anexos}`); `retificar.html:158-159` | NÃO IMPLEMENTADO | sim — "a coisa mais grave da lista" (19/09 e 20/09) | Edital sem correção possível · **A** | spec (junto de RC-38) | 4, 3, 5 |
| RC-38 | G16-001 · achado objeto que nasce só pelo método · NOVO-1 do lote 1 · NOVO-3 do lote 5 | o contrato diz que janela recursal, corte e reversão **podem nascer** por Retificação, mas a tela só mostra os campos se o objeto já existe; critério de desempate **se remove e não se acrescenta** | 026 FR-313 | `mutabilidade.py:515-548`; `retificacao.py:764,852,859,925-936`; `tests/interface/test_retificar_reversao.py:84` prende a ausência | NÃO IMPLEMENTADO | sim | Edital sem prazo recursal não o ganha pela tela · **A** (janela) / B (corte, reversão, critério) | spec única com RC-37: "a Retificação acrescenta o que o contrato já permite" | 1, 5 |
| RC-39 | conferência 25/09 · decisão D4.3 | a Retificação declarou 7 alterações e o portal mostrou 6; faltou a do laudo que passou a valer só no C1 | 024 FR-130 (MUST identificar o alterado); a 044 exclui de propósito | `publicacoes/domain/alteracoes.py:89-95` (sem `profileId`/`modalityId`); `:14` (caminho não reconhecido não produz linha) | NÃO IMPLEMENTADO | sim — decidido em 25/09 "para a fila das diretas", sem dono | o candidato não é avisado · **A** | corrigir (duas entradas no dicionário); cruzar `CAMPOS` com o contrato | 6, 7 |
| RC-40 | E-3 · 13.4 · LONG-5 · ACH-31 · ACH-32 · E2E-018 | duas gramáticas → **uma tabela** de vocabulário; `REPLACE` na tela do ato; bloco do sorteio num marco que não sorteia | 024 D-009; `7b04cb3` unificou a gestão | `views.py:3387-3408` × `alteracoes.py:24-52` (já divergem: "Modalidade" × "Modalidade de concorrência") | PARCIALMENTE RESOLVIDO | parcialmente | deriva silenciosa entre gestão e portal · C | unificar a tabela ao tocar essas telas | 3, 2 |

### 3.5 Reaproveitamento

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-41 | 13/09 #2 · 13/09 #4 · 11.4 · E2E17-007 · achado etapa governada · achado ampla não remapeada | cronograma vencido publicado; segundo Edital; referências do Edital anterior | 023, 028; `6f0f988`, `643e865` | `editais/domain/reaproveitamento.py:143-144, 164-183`; `tests/unit/editais/test_reaproveitamento.py:396,417` | RESOLVIDO | não | — | nenhuma | 2, 7, 5 |
| RC-42 | classe do remapeamento (achados de 15/09 e 25/09) | o próximo campo de referência atravessa a cópia de novo; a 043 reusa `remapear` | 043 aplicou o guardião à duplicação, não ao reuso | dois casos em dez dias, mesma causa (fixture sem o campo) | PARCIALMENTE RESOLVIDO | sim | dívida técnica · B | teste guardião "campo do contrato ⇒ fixture rica de reuso" | 5, 7 |
| RC-43 | estudo QW15 · §5.2 · Caso 7 · A8 · E9 · §15 frente 3 · §5.3 · A4 · E4 · **D-G3** ("a regra do reaproveitamento é a parte não óbvia") · NOVO-1 do lote 6 | o reuso copia 10.900 caracteres de outro certame; herda ocorrência e cláusula do sorteio; o banner avisa em bloco → estado "reaproveitado, a revisar" | #163 nomeia o texto no banner | `compor_base.html:70-83`; `views.py:3662` conta seções **com texto**, não as herdadas; `reaproveitamento.py:304-320` copia seções e `drawMethod` | PARCIALMENTE RESOLVIDO | sim, **por etapa ou seção**, não campo a campo | prosa de outro certame publicada; o aviso vira ruído permanente · B | spec pequena "reuso com estado de revisão", absorvendo a regra do reuso da D-G3 | 6, 4 |

### 3.6 Portal do candidato e inscrição

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-44 | ACH-42 · 13.2 · 13/09 P2/P3 (seis itens) · E2E17-004/005 · E2E17 §10.3 · E2E-003 | parecer não chegava ao titular; eliminado cedo sem notícia; vigente sem selo | 036, 017, 024 | `recursos/application/selectors.py:617-700`; `tests/portal/test_parecer_do_titular.py` | RESOLVIDO | não | — | nenhuma | 3, 1, 2 |
| RC-45 | #167 · conferência §1/§3 · D2 (correções diretas) | instrução do documento não chegava à Mesa; facultativo sem marca na Revisão | `a2b1e1f` | `avaliacoes/application/mesa.py:131-135`; `portal/templates/portal/revisao.html:97` | RESOLVIDO | não | o **cartão público** da vaga continua sem a marca · C | opcional | 6 |
| RC-46 | 019 §4.2 | reconciliação do portal não chegava ao CPF | 019 | inscrições criadas por script no relatório | IMPLEMENTADO, MAS NÃO VALIDADO | parcialmente | pode ser artefato do cenário · B | validar com inscrição criada pelo portal | 1 |
| RC-47 | ACH-53 · 13/09 P2 | a página da seleção tem como `<h1>` o título do **Processo**; o título do Edital não aparece; concorrências **sem quantidade** | 010, 024 | `portal/templates/portal/selecao.html:2,23,144`; `portal/views.py:188-190` passa só os nomes | NÃO IMPLEMENTADO | sim | o cotista não vê quantas vagas há na lista dele · B | corrigir (direta) | 3, 2 |
| RC-48 | 13/09 QW12 · convergência §6-bis/§7 · ACH-41 (a parte executável) | a página pública do resultado **não diz o prazo recursal**; o acompanhamento diz | 017 FR-055 (MAY) | `portal/templates/portal/resultado.html` (nada além de `:38-41`); `acompanhamento.html:160` | NÃO IMPLEMENTADO | sim | quem chega pela lista pública não sabe que há prazo · B | corrigir; dizer também a data-limite na prévia da divulgação | 4, 2, 3 |
| RC-49 | E2E15-007 | o rascunho e "Minhas inscrições" não avisam que o prazo acabou | 009, 010 | anexo 1 | NÃO IMPLEMENTADO | sim | só se descobre ao anexar ou enviar · B | corrigir (direta) | 1 |
| RC-50 | ACH-01 · ACH-23 · ACH-24 · E2E-011 · E2E15-013 · QW13 · POLISH020-015/016 · E2E25 §4 | raiz pública sem caminho para a gestão; declaração sem link; comprovante "disponível enquanto…"; e-mail com "Concorrência:" vazio | parte em 024 | anexos 1 e 2 | NÃO IMPLEMENTADO | parcialmente | polimento · C (ACH-24 depende de política de guarda) | varredura de polish | 1, 2 |

### 3.7 Documentos exigidos e análise documental

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-51 | #161 · achado do portal | "Todos os Perfis" + Modalidade de um só: PDF e portal divergiam | `01d9163` | ver RC-28 | RESOLVIDO | não | a terceira saída e a divergência nas inscrições antigas (FR-727) entraram com o #173 | nenhuma | 6 |
| RC-52 | estudo §5.9 · A7 · E6 (modalidade) · Caso 5 · §15 frente 1 · AX-10 · AX-14 (custo) · AX-17 · decisão D1/D1a/D3/D5 | "todo PcD" custa 112 linhas; o atalho publicou **9 obrigatórios como facultativos** → recorte por **código** da Modalidade | **044, mesclada pelo #173** (`47876ad`, 26/09; CI verde) | `editais/domain/documentos.py:206-290` (recorte por código), `editais/domain/validation.py:2234-2321` (código inexistente, da ampla, denominação divergente), migration `editais/0022`; percurso pela tela em `specs/044-recorte-transversal-documental/rastreabilidade.md` | RESOLVIDO | sim — é a frente decidida pelo usuário | a T065 não foi feita: a redução 112 → 7 no 140/2025 (SC-260, SC-261) é afirmada por construção, e não medida `[VALIDAR]` · — | demonstrar a T065, se a medição for pedida | 6, 5 |
| RC-53 | conferência §3/§6 · decisão D4 | a Mesa **recalcula** a lista; "não se aplica" não existe; nada registra o que foi pedido | **044, mesclada pelo #173** (`inscricoes/0005`, três camadas append-only) | `avaliacoes/application/mesa.py:135` lê a lista gravada, e `:171-217` monta "Não se aplicam"; `inscricoes/migrations/0005_item_da_lista_exigida.py`; `inscricoes_itemdalistaexigida` em `seguranca/papeis.py:120`; Mesa percorrida no navegador (`rastreabilidade.md` da 044, `0c4e6b0`) | RESOLVIDO | sim — a Constituição (`constitution.md:200-201`) pede reproduzir os documentos exigidos de cada Inscrição | — | nenhuma | 6 |
| RC-54 | conferência §3/§7 · 044 "Riscos e lacunas" | o filtro de concorrência repete "PcD" por Perfil sem dizer de qual | **PR #172**, mesclado em 26/09 (`8e6fb4a`) | `interface/templates/interface/inscricoes.html:64` — a opção leva o nome do Perfil quando há mais de um | RESOLVIDO | sim | o seletor não se restringe ao Perfil escolhido, registrado em `doc/achado-filtro-de-concorrencia-sem-perfil.md` · C | nenhuma | 6, 5 |
| RC-55 | AX-15 · estudo E7 · A10 · Caso 8 · H-3 · reversão hierárquica | submodalidades de PPIQ, reversão entre elas e ordem de convocação sem forma | 044 exclui por decisão (§1, §3) | `editais/models/perfis.py:110-119` (Modalidade plana) | NÃO IMPLEMENTADO | sim, como evolução — a amostra tem um Edital só com essa forma | 3 documentos do 140/2025 seguem facultativos mesmo com a 044 · B | nenhuma agora; reabrir com um segundo Edital | 5, 6, 1 |
| RC-56 | conferência §3–§5 · E2E-012 | a lista da Mesa sem Perfil nem completude; nenhum juízo por documento | a 044 recusa o juízo por documento | `mesa_inscricao.html:90-91` | NÃO IMPLEMENTADO | parcialmente | conveniência · C | reavaliar agora que o #173 entrou (a lista gravada já traz a razão de cada documento) | 6, 1 |

### 3.8 Oferta, ocupação e convocação

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-57 | ACH-47 · E-1 · 13.1 · L-1 · R-006 · Q-2 · Q-1 · arco 014/016/019 · PR #85 · G16-002 · O16-002 · L-5/L-6 · P-11 | reserva publicada sem apuração; cauda do processo não fechava | 014, 016, 019, 025, 027, 034, 035 | `classificacao/application/emissao.py:20-47` (ordem por recorte); `editais/domain/recortes.py:33-60` | RESOLVIDO | não | — | nenhuma | 3, 1 |
| RC-58 | **P-1 · P-2 · P-3** · estudo M15 · E8 · NOVO-6 do lote 1 · NOVO-1 do lote 3 | Edital **só de cadastro de reserva** publica "0 vagas" e **não convoca**: convocar exige vaga faltante apurada; o **"Cadastro Reserva limitado em N"** sai publicado e **nada o aplica**; não há prazo de validade | nenhuma; `reserveType`/`reserveLimit` existem desde a 001 e a 040 trata "vagas 0 — zero legítimo" | `convocacao/application/convocar.py:100-152`; nenhuma ocorrência de `reserveType`/`reserveLimit` em `ocupacao/`, `convocacao/` ou `classificacao/`; `pdf.py:1683-1685` imprime o limite | NÃO IMPLEMENTADO | sim — é a mesma doença do ACH-47, "aceita, publica e não executa", numa família da amostra (140/2025, 173/2025) | fluxo incompleto para um tipo de Edital que o produto aceita · **A** `[VALIDAR]` | validar pela tela e confirmar se a família está no alvo do piloto; depois, spec | 1, 3, 6 |
| RC-59 | ACH-59 · cascata 14/2026 · LONG-3 | grupos 1→2→3 são ordem de chamada, não reserva; os avisos empurram para repartir | a decisão do encadeamento já nomeou a forma (`callRules`) | `validation.py:2480`; nenhuma prioridade entre listas | NÃO IMPLEMENTADO | sim, quando a família entrar no alvo | B | nenhuma agora | 3, 1 |

### 3.9 Comissão, alocação, distribuição e avaliação

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-60 | 13/09 #8 · 13/09 #5 · QW6 · ACH-38 · gate da 013 · E2E15-016 · E2E-008/009 (parte) | "Impedimento" com dois sentidos; presidência mandada divulgar; julgador sem porta | 013, 033, 037 | anexos 1 e 2 | RESOLVIDO | não | E2E-008/009: filtros da Mesa (C) | nenhuma | 1, 2 |
| RC-61 | ACH-60 · ACH-61 (trabalho) · convergência §10/§16 · 040 G-004 | alocação `Etapa × avaliador` e distribuição sem Perfil, polo ou modalidade; 7 polos = 21 colunas | 011, 012; a 040–042 **não** toca | `comissoes/models.py:76-83`; `distribuicao.html` e `alocacoes.html` com 0 ocorrências de Perfil | NÃO IMPLEMENTADO | parcialmente — a **coluna e o filtro** são leitura (sim); o **escopo por Perfil** é autorização (decidir antes) | B | corrigir a coluna e o filtro; decisão de governança para o escopo | 3, 4 |
| RC-62 | E2E15-003 · NOVO-3 do lote 1 | a Mesa aceita concluir avaliação de inscrição que já tem Resultado na própria Etapa | 013 | anexo 1 | NÃO IMPLEMENTADO | sim | a guarda precisa excetuar a reavaliação determinada · B | decisão curta e correção | 1 |
| RC-63 | E2E18-001 · NOVO-2 do lote 1 | "reavaliação determinada inexequível" | 018 | o caminho existe: `avaliacoes/application/distribuicao.py:317-341`; a recusa aponta para o lugar errado (`avaliacao.py:366-369`) | IMPLEMENTADO, MAS NÃO VALIDADO | parcialmente | o diagnóstico de 04/09 provavelmente estava errado; a mensagem está errada · B | percorrer pela tela e corrigir a mensagem | 1 |
| RC-64 | ACH-56 · AX-4 · estudo E11 · L-3 · D-4 · P-7 · LONG-3 | barema inexistente; Etapa do Edital inteiro, sem alcance por Perfil ou curso | D-4 (04/09) **adiou**, não recusou | `editais/models/etapas.py:11-20` (docstring registra o preço); zero ocorrências de "barema" | NÃO IMPLEMENTADO | sim, quando a família de prova de títulos entrar no alvo | a nota não é conferível contra norma publicada · B (A numa leitura estrita de `constitution.md:203-205`) | spec quando priorizado | 3, 5, 1 |
| RC-65 | L-2 · LONG-2 · CLVA/CPVA | heteroidentificação sem fluxo, sem comissão própria e sem Etapa aplicável só a quem declarou a Modalidade | nenhuma | zero ocorrências de `heteroidentifica` | NÃO IMPLEMENTADO | sim, para os Editais com PPI da amostra (28/2026, 57/2026) | a verificação acontece fora do sistema · B | spec **depois** do alcance da Etapa (RC-64) | 3, 1 |
| RC-66 | 13/09 #9 · NOVO-3 do lote 2 | "Remover da comissão" num clique; desativa em cascata as alocações; dado como fechado em 16/09 sem teste | 011 | `comissao.html:101-111`; `interface/views.py:4489-4497` | PARCIALMENTE RESOLVIDO | sim | último ato em cascata sem conferência · C | corrigir (prévia, como os demais) | 2 |
| RC-67 | LONG-4 · E2E-016 · §3 do longitudinal | nenhuma notificação a avaliador, comissão, gestor ou julgador | 012 §21 declarou fora de escopo | `send_mail` só em identidade, inscrição e convocação | NÃO IMPLEMENTADO | não agora — o painel e a lista cobrem uma equipe de 2–3; depende de RC-92 | C | reavaliar depois de RC-79 e RC-92 | 3, 1 |

### 3.10 Resultado, classificação e divulgação

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-68 | ACH-40 · 13.3 · E-2 (parte) · QW7 · QW10 · ACH-35 · ACH-02 · ACH-30 · E2E-015 · E2E15-012 · REAV §4.4 | publicador sem caminho até a ação; 404 mudo por vínculo; fragmento que lia Edital de outra unidade | 033, 037 | `views.py:2887-2940` (derivação por destino); `views.py:2197-2215` | RESOLVIDO | não | o que sobra são as três recusas da D-G2 (RC-94) | nenhuma | 2, 3 |
| RC-69 | ACH-39 · ACH-44 · ACH-45 · N-09 · E2E18-003 · E2E-010 · ACH-17 | UUID nas telas de ato; `cand:…` e "o meu resultado" na tela de quem julga; quatro casas decimais | FR-092 da 018 exige proveniência **respondível**, não UUID | `ato_ordenacao.html:77-78`; `recurso.html:27,33,35,37`; `recursos/application/selectors.py:113-130,252-259` | NÃO IMPLEMENTADO | parcialmente | nome ao lado do identificador · C | uma varredura só | 2, 3, 4, 1 |
| RC-70 | ACH-28 · ACH-37 · coluna MODALIDADE "Não declarada" · E2E18-004 · ACH-26 | aviso de segregação em Edital já publicado; rótulo "Consultar ato e proveniência"; coluna vazia | — | `detalhe.html:58-62`; `ordenacao.html:166,174` | NÃO IMPLEMENTADO | parcialmente | polimento · C | varredura de polish | 2, 3 |

### 3.11 Sorteio

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-71 | ACH-48 · ACH-51 · ACH-55 · achado faixa de sucesso · rito E-01…E-12 | sorteio sem Etapa recusado; fonte em texto livre; método em prosa; faixa única | 021, 030, 035; PR #97 | `sorteios/infrastructure/fontes/__init__.py:83-110`; `sorteios/domain/substituicao.py:113-136` | RESOLVIDO | não | — | nenhuma | 3, 7 |
| RC-72 | **D-G3** · NOVO-1 do lote 4 | o Cefor passa a declarar fonte pública externa → atendido pelo vocabulário fechado de fontes (021/032); **resta um furo**: "Fonte de demonstração" (semente fixa `12345 67890…`) é oferecida no seletor e **não é recusada em produção** | 021 FR-076, 032 FR-467 | `fontes/__init__.py:88-92` (sem condição de ambiente); `interface/forms.py:318-322` (`sorted(FONTES)`); `config/settings/production.py` sem guarda | RESOLVIDO POR OUTRO CAMINHO | sim, para o furo | sorteio publicado com semente previsível · **A** | corrigir: a mesma barreira de produção dos seletores de identidade, sem quebrar o `seed_demo` | 4 |
| RC-73 | ACH-54 · "três nomes para duas coisas" (sorteio) · 034 FR-491a/D-004 · 13/09 §5 | o sorteio oferece recorte à AC declarada, que não tem vagas; nenhuma quantidade por recorte | 034 **adiou** para "spec própria", que nunca foi escrita | `sorteios/application/previa.py:43-50, 168-203` × `editais/domain/recortes.py:33-60` | NÃO IMPLEMENTADO | sim — uma ordem sorteada nesse recorte não alimenta a ocupação | B | spec curta: vagas por recorte + aviso; retirar o recorte excedente é a parte grande | 3, 5 |
| RC-74 | achado fonte real sem gatilho · convergência §18 | o E2E contra a Caixa não roda em lugar nenhum; a última medição é de 10/09 | 021, 035 | `.github/workflows/backend.yml` sem `schedule`; `tests/interface/test_sorteio_com_a_fonte_de_producao.py:48-52` | NÃO IMPLEMENTADO | sim — com a D-G3, todo sorteio futuro depende do contrato com a Caixa | B | workflow agendado, não bloqueante | 7, 4 |

### 3.12 Recursos

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-75 | ACH-43 · 13.2 · inventário 09/09 (a) | o julgador decidia sem poder ver a prova → ato de instrução | 036 | `recursos/models.py:314-416`; `interface/views.py:7765` | RESOLVIDO | não | — | nenhuma | 3 |
| RC-76 | ACH-41 · E-4 · 13.5 · longitudinal §14.2 | "Cabe recurso até 18/09" × Cronograma "06/10–07/10" → confrontar as fontes | nenhuma | `recursos/domain/janela.py:1-18` (janela **relativa** ao ato); `_evento.html:19-20` (tipo do Evento em texto livre) | NÃO IMPLEMENTADO | parcialmente — a recomendação original **não é executável**: não há vínculo declarado entre Evento e marco, e casar por texto foi vetado | B | a parte viável está em RC-48; o confronto pleno exige designar o Evento de recurso (decisão de modelo) | 3, 5, 2 |

### 3.13 Condução do Processo vivo

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-77 | ACH-25 · E-6 · 13.6 · 13/09 §9.7 · 11.3 · E2E-013 | a visão global some quando o Processo fica vivo | 038 (painel); 040–042 (visão **entre** Processos, declaram não tocar a Atenção) | `supervisao.py:1391-1398` (lista plana); `visao_geral.html:350-369` ("O que esta página não mede") | PARCIALMENTE RESOLVIDO | sim, pelos componentes abaixo | B | remedir depois de RC-78…82 | 4, 3 |
| RC-78 | **N-01** · C1 · convergência §22 Q4/Q12 | "Nenhuma condição de atenção neste Processo" é dita a quem alcança uma espécie e não vê as outras | 022 FR-004, 038 FR-559 | `processo_detalhe.html:139-141`; `supervisao.html:139-141`; `views.py:3946-3960`; `supervisao.py:1302-1337` | NÃO IMPLEMENTADO | sim — é o único ponto em que o produto quebra a ausência honesta | falso "tudo em dia" assim que houver segregação de funções · **A** | corrigir (texto + condição) | 4 |
| RC-79 | **N-02** · C2 · NOVO-2 do lote 4 | recurso **aguardando admissibilidade** não produz sinal; "Recursos recebidos (N)" conta também os já decididos | 038 FR-561 (escrito só para "aguardando julgamento") | `supervisao.py:1162-1167`; `interface/acoes.py:120-127` | NÃO IMPLEMENTADO | sim — "vale mais do que sorteio e matrícula juntos" (20/09) | a peça com prazo fica invisível exatamente enquanto o prazo corre · **A** | spec curta ou emenda da 038: espécie nova × ampliar `UX-064` | 4 |
| RC-80 | **N-05 · N-06** · C5 · C6 · §17 E-4 · inventário 09/09 (e) · ACH-08 (deslocado) | `schedule.status` é `derivado()` e nada o deriva: fica PLANEJADO para sempre, gera `UX-002` permanente, e `UX-001`/`UX-002` levam a uma Retificação que não alcança a causa | 026, 022 D-004, 038 | `editais/domain/mutabilidade.py:432`; `editais/models/cronograma.py:29`; `supervisao.py:635-662, 1273-1274`; `mutabilidade.py:447` (`scheduleEventId` estrutural) | NÃO IMPLEMENTADO | sim — mas há **duas doutrinas** no repositório (declarado, no inventário de 09/09 × derivado, na 026), e o `UX-001` não se resolve derivando | 9 dos 15 sinais do gestor são ruído ou beco · **A** | spec curta: escolher a doutrina, derivar; decidir a natureza do `UX-001` | 4 |
| RC-81 | **N-04** · C4 | sinal sem caminho não diz a quem pedir | 037 (o padrão "peça a alguém" já existe no Edital) | `_sinal.html:16-18`; `supervisao.py:1240-1259` | NÃO IMPLEMENTADO | sim, depois de RC-80 | B | corrigir depois de RC-80 | 4 |
| RC-82 | **N-07** · ACH-27 (deslocado) | "2 de 5 sem avaliador suficiente" conta quem foi eliminado antes | 013, 022 | `supervisao.py:686`; `avaliacoes/application/selectors.py:193-238` | NÃO IMPLEMENTADO | sim | o número contradiz a lista logo abaixo · B | corrigir (com RC-80) | 4, 2 |
| RC-83 | N-03 · C3 | "Abrir a Supervisão" oferecido a quem a Supervisão recusa | `4ec1cbb` | `processo_detalhe.html:72`; `tests/interface/test_supervisao.py:533-569` | RESOLVIDO | não | — | nenhuma | 4 |
| RC-84 | N-10 · §7 (prazo em três formas) · §8 ("7 de 7" sem unidade; "sem marco" sem consequência) | exportação vazia recarrega sem mensagem; "Faltam 19 dias" × "2 semanas, 5 dias" × só a data | 031, 038 | `views.py:4186-4187`; `supervisao.html:102` (`timeuntil`); `_sinal.html:13-15` | NÃO IMPLEMENTADO | parcialmente | polimento · C | junto de RC-80/RC-82 | 4 |
| RC-85 | §6 sorteio fora do painel · §6/§13 matrícula fora do painel | sorteio vencido e requerimentos pendentes sem sinal | 038 D-002 registrou a exclusão | `supervisao.py:495-506` | NÃO IMPLEMENTADO | não agora — a convergência recomendou **não** ampliar o painel antes de limpar o ruído | C | medir no piloto | 4 |
| RC-86 | §18 custo de consulta | ~17 consultas por Edital publicado; linear | 022, 038; 040 tem custo fixo de 5 | `supervisao.py:1364-1384` | IMPLEMENTADO, MAS NÃO VALIDADO | parcialmente | medição única, não otimização · C | validar com 10+ Editais | 4 |
| RC-87 | §16 responsabilidade · presidência única (08/09) | nomear responsável individual no painel?; piso de identidades não dito | 038 FR-564; decisão 018 §5 | `supervisao.py:1141-1145` | RESOLVIDO | não — manter a decisão | antecipar a falta de julgador depende de RC-92 · C | nenhuma | 4, 7 |

### 3.14 Identidade, autorização e implantação

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-92 | **C7** · T056 (002) · G3 · convergência §18 | o seletor de identidade é demonstração; nenhum provedor real | 002, 003 FR-016…018 (produção recusa subir insegura) | `seguranca/api/authentication.py:7-23` ("adaptador provisório"); `interface/identidade.py:107-120`; `config/settings/production.py:1-20, 92-103` | NÃO IMPLEMENTADO | sim | sem isso não há operação além de piloto assistido · **A** (depende do Ifes) | spec, depois da definição do provedor | 4, 1 |
| RC-93 | E2E-020 · G1 · G2 · G4 · G22 | código de acesso por e-mail como ponto único de falha; retenção e descarte de documentos; rascunhos visíveis à gestão sem decisão escrita | — | anexo 1 | NÃO IMPLEMENTADO | sim | decisões de implantação e LGPD · B | decisão do usuário e da instituição | 1 |
| RC-94 | **D-G2** · REAV §8 · E-2 (resto) · longitudinal QW6 | `criar_edital`, `reaproveitar` e `supervisao` devolvem 404 a quem vê o objeto e não tem capacidade → 403 (decidido em 19/09); as outras quatro ficam 404 | 033 (inventário das negativas) | `interface/views.py:400-403, 1460-1461, 4020-4021` | NÃO IMPLEMENTADO | parcialmente — depois do N-03 e das guardas de oferta, o 404 só aparece a quem digita a URL | coerência de taxonomia · C | spec curta, se a D-G2 for mantida | 4, 3 |
| RC-95 | §13 · §18 · condição de saída do piloto | exportação para o Registro Acadêmico nunca importada no destino | 029, 031 | `interface/views.py:4152-4247` | IMPLEMENTADO, MAS NÃO VALIDADO | sim | responsabilidade compartilhada com o sistema de destino · B | validar com o setor dono | 4 |
| RC-96 | Escala / T059 · T063 (375 px) | 2719 vagas; medição no Cefor; telas estreitas | — | anexo 1 | IMPLEMENTADO, MAS NÃO VALIDADO | parcialmente | C | validar na infraestrutura real | 1 |
| RC-97 | E2E-019 · E2E-014 | todos veem todos os Processos do escopo; "Ou entre por outro nome" | FR-003 da 002 | anexo 1 | SUPERADO / OBSOLETO | não | — | nenhuma | 1 |

### 3.15 Integridade de dados, engenharia e documentação

| RC | IDs antigos | Problema original → recomendação | Specs · implementação | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-98 | contrato de mutabilidade (13–14/09) | campo publicado sem natureza declarada → invariante com guardião | 026 | `tests/contract/test_mutabilidade.py:303,339`; o contrato cresceu de 123 para 139 entradas | RESOLVIDO | não | o "retificável" não garante canal de exibição (RC-12) nem porta de acréscimo (RC-38) | nenhuma | 5 |
| RC-99 | ACH-06 · ACH-12 · ACH-20 · B6 · B7 · B8 · E2E15-015 · LONG-§10.10 | `name` em inglês; desempate por idade; vigência densa; Anexos sem "Salvar rascunho"; papéis crus no seletor; cancelamento "sem dizer por quê"; a 037 "em deriva" | — | ver os anexos 2, 3 e 6 | SUPERADO / OBSOLETO | não | — | nenhuma | 2, 3, 6 |
| RC-100 | NOVO-2 do lote 2 · NOVO-2 do lote 3 · longitudinal preâmbulo item 6 | "`_marco.html` com 42 controles, e cresceu" | — | 13 dos 42 são `hidden`; os visíveis foram de 28 para 29, e na chegada são 6 | SUPERADO / OBSOLETO | não | a medição do longitudinal é que estava errada | corrigir o texto do longitudinal, se desejado | 2, 3 |
| RC-101 | PR #171 · achado ValorDeFato · memória "corrigir depois da 044" | `inscricoes_valordefato` está na lista append-only, mas sem gatilho e sem recusa no modelo | 015 D-2; a correção foi **decidida para depois da `0005` da 044**, que entrou com o #173; **feita pelo #183** (`8e7c698`, 26/09) | `inscricoes/migrations/0006_valor_de_fato_append_only.py` (gatilho `valor_de_fato_append_only`); `ValorDeFato.save`/`delete` em `inscricoes/models.py`; `tests/integration/test_imutabilidade_do_historico.py` | RESOLVIDO | sim — contradizia a regra de duas camadas independentes | `PosicaoNaOrdem`, `RevisaoEdital` e `GeracaoDeArquivo` seguem com duas camadas de três, só registradas por decisão · — | nenhuma | 6, 7 |
| RC-102 | spec 039 (branch local) | catálogo de Modalidades no Edital; alcance declarável | nunca mesclada; sem registro explícito de abandono | `git log main..claude/spec-039-alcance` | CONTRADITO POR DECISÃO POSTERIOR | não, o catálogo; **sim** as duas peças que ela absorvia (D-G5 → RC-37; alcance da Etapa → RC-64) | risco de governança: parece trabalho em curso · C | registrar o encerramento e apagar ou arquivar a branch | 5 |
| RC-103 | Status Draft (41 de 44 specs com estado errado) · README (`31 de 31`; tabela até a 025; "5402 passando") · contagens divergentes · manual atrás do código · suíte em SQLite · testes em UTC · teste CSRF instável · `seed_demo --numero` · guarda de citações (`UX-062`) · derivação duplicada de `pode_retificar` · grade dos cartões | higiene de documentação, teste e ferramenta | — | `README.md:73, 206-214`; `backend/Makefile:36-37`; `tests/integration/identidade/test_adicionar_credencial.py:46-52`; `processos/management/commands/seed_demo.py:579-582`; `interface/views.py:6320` | NÃO IMPLEMENTADO | parcialmente | nada disso afeta produção · C | uma varredura de higiene; a convenção de `Status` é decisão do usuário | 7, 4, 3, 1 |

### 3.16 Recomendações contraditas por decisão posterior

Estas unidades estão na matriz porque foram rastreadas até o fim, não porque sobre trabalho. A §7 explica
cada uma.

| RC | IDs antigos | Problema original → recomendação | Decisão ou requisito que a contradiz | Evidência atual | Estado | Faz sentido? | Resíduo · grupo | Próxima ação | Anexo |
|---|---|---|---|---|---|---|---|---|---|
| RC-88 | estudo §5.2 · E3 · 1ª versão do §15 | Edital encerrado não publica → spec de "registro de Edital já executado" | `doc/decisao-sem-carga-retroativa.md` (25/09) | `editais/domain/validation.py:2055-2096` (`registration_period_closed`, impeditivo) | CONTRADITO POR DECISÃO POSTERIOR | não | consequência aceita: a primeira oferta de cada família nasce do zero · — | nenhuma | 6, 7 |
| RC-89 | convergência §4 "Recurso sem prova" · §6-bis | o recorrente não tem campo de anexo → anexo de prova | `018` FR-007 / D-011 ("MUST NOT aceitar anexos na V1") | `portal/templates/portal/recorrer.html` sem `type="file"`; `specs/018-…/spec.md:896` | CONTRADITO POR DECISÃO POSTERIOR | não, salvo revisão da D-011 | — | nenhuma | 3, 4 |
| RC-90 | P-4 · segunda instância · terceiro ou procurador | impugnação; recurso contra a relação de habilitados; órgão recursal distinto | decisão do escopo institucional do recurso (1B, 2A, 4B) | `recursos/domain/elegibilidade.py:25-69` | CONTRADITO POR DECISÃO POSTERIOR | não na V1 | — | nenhuma | 1, 7 |
| RC-91 | estudo E6 (condição sobre o candidato) · achado do portal, item 3 | sexo, idade e vínculo sem forma → estado "obrigatório sob condição" | decisão D2 de 25/09 (opção 1 assumida; opção 2 em spec própria, com LGPD) | `editais/domain/documentos.py:97-114` | CONTRADITO POR DECISÃO POSTERIOR | parcialmente | o documento sai "(facultativo)" no ato · — (vira B se a D2 for reaberta) | nenhuma até reabrir a D2 | 6 |
| RC-104 | E2E-004 | Retificar para acrescentar ou remover Documento Exigido | razão normativa no contrato (`026`); D-009 da `044` | `editais/domain/mutabilidade.py` | CONTRADITO POR DECISÃO POSTERIOR | não | — | nenhuma | 1 |
| RC-105 | estudo B9 · QW9 | o reuso copiar a Descrição | `023` FR-007 | `editais/domain/reaproveitamento.py:289` | CONTRADITO POR DECISÃO POSTERIOR | não | — | nenhuma | 6 |
| RC-106 | estudo A6 · QW10 · §9.D · Caso 4 | imprimir o método do sorteio uma vez só | `032` FR-465/466 | `publicacoes/infrastructure/pdf.py:1271-1343` | CONTRADITO POR DECISÃO POSTERIOR | parcialmente: remeter preservaria a garantia, mas exige emendar o requisito | páginas a mais · — | decisão do usuário | 6 |
| RC-107 | P-10 | turma como recorte de vaga | `019` §7 | — | CONTRADITO POR DECISÃO POSTERIOR | não | — | nenhuma | 1 |
| RC-108 | E2E15 opp. (b) · E2E17 §13 · achado do objeto normativo sem forma | rota para `reproduzir_ato`; tela para `classificationInformation`/`callInformation` | Clarifications da `015`; campos opacos na `026` | `editais/domain/mutabilidade.py:153-156, 247-260` | CONTRADITO POR DECISÃO POSTERIOR | pouco | dois campos publicados sem leitor · — | nenhuma | 1, 5 |
| RC-109 | ACH-22 | retomar a intenção de inscrição depois do login | decisão de segurança | anexo 2 | CONTRADITO POR DECISÃO POSTERIOR | não | — | nenhuma | 2 |
| RC-110 | Edital grande (46/2026) · P-8 | forma completa do Edital grande; inscrição que nasce fora do sistema | fora do alvo (`doc/achados-editais-externos.md`) | — | CONTRADITO POR DECISÃO POSTERIOR | não | falta registrar se o 76/2026 também sai do alvo · — | decisão de alvo | 1 |

A numeração da §3 não é contínua por domínio: as linhas acima reaproveitam os números RC-88 a RC-91,
que tinham ficado vagos, e seguem em RC-104 a RC-110. São 110 unidades, sem número repetido.

### Onde os lotes discordaram, e o que vale

| Tema | Lotes | Decisão aqui | Por quê |
|---|---|---|---|
| `ACH-41` (duas datas do recurso) | lote 5: A · lotes 2 e 3: B | **B** (RC-76) + a parte executável em RC-48 | nenhum requisito escrito é violado; a recomendação original pressupõe um vínculo Evento↔marco que o modelo não tem; o acompanhamento mostra a data autoritativa |
| `D-G2` (403) | lote 3: B · lote 4: C | **C** (RC-94) | depois de `4ec1cbb`, a interface não oferece mais os três caminhos; a legitimidade da decisão não muda, o impacto sim |
| `E-6` / `ACH-25` | lote 3: absorvido · lote 4: parcial | **PARCIALMENTE RESOLVIDO** (RC-77) | a `040` cobre a metade "entre Processos"; a condução dentro do Processo está como em 20/09 |
| a 044 | lote 6: "sem PR" · lote 5: PR #173 | **PR #173 aberto** (confirmado em `gh pr list`, 26/09; `test` pendente, `compose` verde) | o PR foi aberto durante esta auditoria, e mesclado no mesmo dia (`47876ad`) |

---

## 4. Achados resolvidos

**27 unidades** (24 RESOLVIDO + 3 por outro caminho), agrupadas pela capacidade que passou a existir.
Todas foram conferidas no código de hoje. Entre os IDs antigos que elas fundem estão os seis P0 de
16/09 (`ACH-40`, `ACH-43`, `ACH-46`, `ACH-47`, `ACH-49`, `ACH-50`), nove itens do top 10 de 13/09 (o
décimo, "Remover da comissão", é o RC-66) e quatro das sete raízes de 16/09 (`E-1`, `E-2`, `E-5`, `E-7`).

| Capacidade entregue | Unidades | Quem entregou |
|---|---|---|
| A cauda do processo fecha: reserva por recorte, corte sempre alcançável, sorteio executável do congelamento à verificação | RC-27, RC-57, RC-71 | 032, 034, 035, 037 |
| O recurso é decidido com a prova, e o parecer chega ao titular | RC-44, RC-75 | 036 |
| A navegação deriva da permissão | RC-68, RC-83 | 033, `4ec1cbb` |
| A composição se explica e ficou menos densa | RC-02, RC-03, RC-04, RC-06 | 030, 037, #162, #163 |
| O quadro de vagas é uma fonte só | RC-01, RC-33 | 025, 027 |
| O documento publicado não contradiz a execução no recorte documental | RC-28, RC-51 | #161 |
| O reuso não leva referências nem cronograma do Edital anterior | RC-41 | 023, 028, `643e865` |
| A Retificação tem contrato e fala português | RC-35, RC-36, RC-98 | 026, 024 |
| O PDF: cabeçalho, tabelas e método | RC-17, RC-18, RC-19 | `c0403a9`, #164, 032 |
| O cadastro reserva limitado se declara pela tela | RC-05 | #159 |
| A fonte do sorteio vem de vocabulário fechado (D-G3) | RC-72 (com o furo à parte) | 021, 032, 035 |
| Decisões de governança encerradas | RC-04 (D-G4), RC-87 (responsável individual) | — |

**Dois fechamentos que vale nomear, porque os relatórios os davam como abertos:**

- **`ACH-43` / "recurso sem prova".** A convergência listou "Recurso sem prova — ABERTO" por causa do
  recorrente sem campo de anexo. Mas o achado de 16/09 era sobre o **julgador**, e a `036` o fechou. A
  ausência de anexo do recorrente é **requisito**: FR-007 da `018`, D-011. Ver §7.
- **`AX-14`, o mais grave dos AX de integridade.** A varredura de 19/09 dizia "0 de 17 fechados". O `AX-14`
  fechou em 25/09, pelo #161, e fechou pela via que ele próprio listava: a conferência de publicação.

---

## 5. Achados parcialmente resolvidos

Para cada um: o que foi feito, o que não foi e por que o resto importa.

| RC | Resolvido | Não resolvido | Por que o resto importa |
|---|---|---|---|
| RC-07 duplicar e escala | duplicar Perfil (530 → 101 interações) | aplicar a todos (TF-1); a curva continua linear | corrigir um erro copiado 15 vezes continua custando 15 edições — é aí que as cópias divergem |
| RC-10 Revisão | colapso das famílias por Evento | colapso por Perfil (32 dos 45 avisos); severidade primeiro | com 16 Perfis, o IMPEDE continua misturado a ~40 linhas, na tela em que a decisão de publicar é tomada |
| RC-13 conteúdo comum aos Perfis | digitação (043) e cabeçalho | PDF e Retificação em N cópias sem conferir igualdade | a 043 **barateou** produzir as cópias, e com isso **aumentou** o risco de divergência que o achado previa |
| RC-15 marco de sorteio | Alvo escondido | Casas decimais e Arredondamento | ruído, com valor padrão já preenchido |
| RC-16 microcópia da composição | a maior parte (030/037) | "Chave" inventada, selos, "marcado" | polimento |
| RC-31 divergência entre Perfis | cópia exata (043); confronto de denominação (044, mesclada pelo #173) | percentual, fundamento, desempate e tipo de fato | o E-1 de 15/09 publicou 3% e 30% da mesma lei em tabelas vizinhas, e isso continua publicável sem sinal |
| RC-40 vocabulário | gestão com uma fonte (`retificacao_ui`) | portal com outra, e elas já divergem; `REPLACE` | deriva silenciosa |
| RC-42 remapeamento | as duas instâncias | o guardião da classe | dois casos em dez dias, e a 043 dobrou a superfície |
| RC-43 reuso | o banner nomeia o texto | estado "a revisar"; ocorrência do sorteio herdada; o banner conta seções com texto | prosa de outro certame vira ato imutável; o aviso que nunca some deixa de ser lido |
| RC-45 facultativo | Mesa e Revisão | o cartão público da vaga | o candidato vê o facultativo como exigido antes de entrar |
| RC-66 atos em um clique | todos, menos um | "Remover da comissão" | inativa em cascata as alocações da pessoa |
| RC-77 visão global | Processo e Supervisão concordam; a visão entre Processos existe | a condução dentro do Processo (RC-78…82) | ver §6 |

---

## 6. Achados que parecem ter se perdido no caminho

Critério: **auditoria → recomendação relevante → nenhuma decisão posterior encontrada → nenhuma spec
suficiente → nenhuma implementação suficiente**. Para cada um, digo como cheguei à conclusão.

### 6.1 Os três "próximos investimentos" da convergência de 20/09

A convergência terminou com uma ordem explícita: **(1) fechar a `038`**, isto é, N-01, N-02, N-03 e N-04;
**(2) derivar o que está declarado derivado**, N-06, e com ele N-05; **(3) `D-G5`**. E acrescentou: "Não
recomendo outro painel".

**Como cheguei à conclusão.** `git log --since=2026-09-19` sobre `interface/supervisao.py`,
`processo_detalhe.html`, `supervisao.html` e `_sinal.html` devolve **um** commit, `4ec1cbb`, que fechou o
N-03. Nenhum `doc/decisao-*`, nenhuma spec e nenhuma nota de memória registra que os outros foram adiados
ou recusados. As specs `040`–`042` declaram expressamente que **não tocam** a Atenção
(`specs/040-…/spec.md:34-37`). O que entrou depois foi uma visão **entre** Processos, que a própria
convergência não pedia.

**Não é necessariamente erro de priorização.** A equipe inicial é de 2–3 pessoas acumulando papéis, e a
própria convergência mostrou que quem acumula papéis **não encontra** N-01 nem N-04. Mas então a decisão
de adiar deveria estar escrita. Sem ela, **a condição de saída do piloto não tem dono**. → RC-78, RC-79,
RC-80, RC-81, RC-37.

### 6.2 Quatro decisões de governança de 19/09, tomadas e não executadas

`D-G1` (RC-30), `D-G2` (RC-94), a regra do reaproveitamento da `D-G3` (RC-43) e `D-G5` (RC-37).

**Como cheguei à conclusão.** Cada uma diz "Cria: spec". `grep` por `D-G` em `specs/` só as encontra
citadas como fora de escopo na `022` e na `038`. O código confirma cada uma no estado de antes: a
severidade continua `WARNING`, `raise Http404` continua lá e `SECOES_QUE_ACRESCENTAM` continua sem
Modalidade.

A `D-G5` tem um agravante. **A única spec que a absorvia, a `039`, foi contradita pela decisão de 25/09
sem que ninguém dissesse para onde a `D-G5` vai.** Ela ficou órfã duas vezes.

### 6.3 Achados de 15/09 que a varredura manteve abertos e ninguém tomou

- **`AX-16`**, restaurar o rascunho (RC-08). A varredura de 19/09 o marcou "❓ percurso" e ninguém o
  percorreu. `rascunho.js` não muda desde 08/09. É o único dos 17 AX que **contradiz requisito escrito**
  (FR-020 da `002`), e a `043` aumentou a superfície dele.
- **`AX-8`**, capa com outro número (RC-20); **`AX-12`**, remissão a anexo inexistente (RC-21), que se
  **materializou** no estudo de 21/09; **`AX-9`**, teto não publicado (RC-12). Os três têm conserto
  barato, e nenhum aparece numa spec ou num registro de decisão.

### 6.4 Cadastro de reserva: uma pergunta de 07/09 que nunca virou decisão

`P-2` ("A oferta tem quantidade conhecida? … Ocupar sem quantidade é caso normal, não borda") e `P-3`
(validade) foram registradas como perguntas. Nenhuma feature as respondeu: `grep` por "cadastro de
reserva" nas specs da `016` e da `019` não encontra nada.

**Como cheguei à conclusão.** `convocar.py:100-152` recusa convocar sem apuração com déficit.
`reserveType` e `reserveLimit` não têm consumidor em `ocupacao/`, `convocacao/` nem `classificacao/`. O
`#159` de 25/09 tornou o "limitado" **alcançável pela tela** e, com isso, **publicável**, mas não
executável. → RC-58.

### 6.5 Três deferimentos explícitos para uma "spec própria" que nunca foi escrita

- **`ACH-54`**: a `034` (`FR-491a`/`D-004`) mandou registrar a divergência dos recortes do sorteio e "é
  spec própria". A `035` e a `036` repetem o registro. Nenhuma spec foi escrita. → RC-73.
- **Fonte real do sorteio sem gatilho** (10/09): pedia decidir onde vive o gatilho, e ninguém decidiu. →
  RC-74.
- **`E2E15-003`**, a Mesa depois do Resultado (09/09): "decisão curta" pedida, não tomada. → RC-62.

### 6.6 O que 25/09 decidiu "para a fila das diretas" e ficou sem dono

A decisão do recorte documental listou correções diretas. Duas foram feitas, no `#167`. A terceira — o
**"O que mudou" listar a mudança de recorte** — não foi. A `044` a exclui de propósito ("continuam fora:
a correção deles é da fila das diretas"). → RC-39. Ela contradiz a FR-130 da `024` e é a mais recente
candidata a se perder.

### 6.7 Um achado dado como fechado sem teste

**"Remover da comissão"** (13/09 #9): a reauditoria de 16/09 o deu como fechado junto dos demais atos
operacionais e não o testou. O código ainda faz a desativação em cascata num clique. → RC-66.

---

## 7. Recomendações antigas que NÃO devem virar backlog

Esta é a seção que elimina dívida fictícia. Cada linha diz **por que** o item sai.

### 7.1 Contraditas por decisão ou requisito posterior

São as unidades RC-88 a RC-91, RC-102 e RC-104 a RC-110 da §3.16, mais a parte estrutural do RC-31.

| Recomendação antiga | Decisão que a contradiz | Onde está registrada |
|---|---|---|
| Registrar Edital já executado / carga retroativa (estudo §5.2, E3) | o produto não terá carga retroativa; o IMPEDE "inscrições encerradas" é correto | `doc/decisao-sem-carga-retroativa.md` (25/09) |
| Mover Modalidade e cota para o Edital; catálogo de Modalidades (AX-7 estrutural, `039`) | "A Modalidade continua sendo do Perfil. Mover a propriedade dela para o Edital está fora de questão" | `doc/decisao-recorte-documental.md`; 043 §2; 044 §3; Constituição "Cotas DEVEM ser definidas por Perfil" |
| Anexo de prova pelo recorrente (convergência "Recurso sem prova") | "A interposição MUST NOT aceitar anexos na V1" | `018` FR-007 / D-011 |
| Impugnação; recurso contra a relação de habilitados; segunda instância; terceiro ou procurador recorrer (P-4 e a 2ª instância) | escopo institucional do recurso: 1B, 2A, 4B | `doc/decisao-018-escopo-institucional-do-recurso.md` |
| Documento por condição sobre o candidato (sexo, idade, vínculo) coletando atributos (E6) | D2: opção 1, informativa, como estado assumido; a opção 2 fica para spec própria com LGPD | `doc/decisao-recorte-documental.md` |
| Retificação acrescentar ou remover Documento Exigido (E2E-004) | razão normativa no contrato de mutabilidade | `editais/domain/mutabilidade.py`; 044 D-009 |
| Copiar a Descrição no reuso (estudo B9) | "a identificação — número, ano, título e descrição — não deve ser copiada" | `023` FR-007 |
| Imprimir o método do sorteio uma vez só no documento (estudo A6/QW10) | cada marco de sorteio imprime o método que o governa | `032` FR-465/466 (mudar exige emendar o requisito) |
| Turma como recorte de vaga (P-10) | fora de escopo | `019` §7 |
| `reproduzir_ato` com rota; `classificationInformation`/`callInformation` com tela | Clarifications da `015`; campos opacos na `026` | ver o anexo 1 |
| Retomar a intenção de inscrição (ACH-22) | decisão de segurança | ver o anexo 2 |
| O Edital grande (46/2026) como alvo | fora do alvo | `doc/achados-editais-externos.md` |

### 7.2 Resolvidas, ou baseadas em medição que não se confirmou

- **"`_marco.html` tem 42 controles, e cresceu"** (preâmbulo do longitudinal, item 6). É artefato de
  contagem: 13 são `hidden`, e na chegada de um marco simples há 6. Os lotes 2 e 3 chegaram a isso de
  forma independente. → RC-100.
- **"Reavaliação determinada inexequível"** (E2E18-001). O caminho existe e tem teste de domínio
  (`distribuicao.py:317-341`). O que está errado é a **mensagem** da recusa. Validar pela tela antes de
  reabrir. → RC-63.
- **"Cancelamento do Processo impedido sem dizer por quê"** (estudo B8). A explicação existe desde a
  `038`, num `<details>`. → RC-99.
- **"A Retificação precisa do renderizador humano do portal"** (longitudinal QW7). Não se aplica: a gestão
  precisa do antes e do depois, e o portal os recusa por D-009. O conserto certo é **uma tabela**. → RC-40.
- **Anexos sem "Salvar rascunho"** (B6): a etapa é de ações imediatas, por desenho. **Papéis crus no
  seletor** (B7): o seletor é de demonstração e recusa subir em produção.

### 7.3 Pertencem a outro sistema, ou só se resolvem fora do software

- **Validação da importação no Registro Acadêmico** (RC-95): é do setor dono do destino. O software já
  entrega o que pode — colunas vazias explicadas e nenhum valor inventado.
- **Redação dos Editais em conformidade com a `D-G3`**: é ato institucional. O produto já não aceita
  fonte fora do vocabulário.
- **Autenticação** (RC-92): o adaptador é do software; o provedor é do Ifes.

### 7.4 Seriam overengineering hoje

| Recomendação | Por que não agora |
|---|---|
| Nomear responsável individual no painel | o produto não liga identidade concreta a papel; a equipe de 2–3 acumula papéis; o que falta é a **capacidade a pedir** (RC-81) — decisão mantida em 20/09 |
| Acrescentar sorteio e matrícula ao painel | a convergência mediu que o painel já tem 60% de linhas sem caminho; ampliar antes de limpar piora o sinal (RC-85) |
| Juntar avisos de composição e sinais de Atenção | naturezas diferentes; sem critério de fronteira vira lista plana de 25 linhas (RC-34) |
| Pôr `scheduleEventId` e `status` na Retificação | mascararia o N-06; o contrato está certo ao chamá-los de estrutural e derivado |
| Trocar 404 por 403 em bloco | as quatro recusas de vínculo protegem enumeração e devem ficar em 404 |
| Detectar contradição entre prosa herdada e método estruturado | exige heurística frágil; o estado "a revisar" do reuso resolve mais barato (RC-43) |
| Métrica de condução / observabilidade exportada | com 2–3 pessoas, o painel é a métrica |
| Marcar o reuso campo a campo | por etapa e por seção resolve o caso medido |
| Grade de 12 colunas nos cartões | o próprio achado a declarou "não é defeito" |
| Barema, submodalidade, cascata e heteroidentificação **antes** de a família entrar no alvo | a Constituição (§V) pede nada de estrutura antes de haver Edital que a consuma (ver RC-55, RC-59, RC-64, RC-65) |

---

## 8. Specs que absorveram múltiplos achados

O movimento inverso: specs posteriores que fecharam, de uma vez, achados de relatórios diferentes. É
também o mapa da consolidação arquitetural.

| Spec | Resolve | Resolve parcialmente | Torna obsoleto | Cria base para |
|---|---|---|---|---|
| **`026` contrato de mutabilidade** | 13/09 §9.6 e anexo §16; decisão de mutabilidade; E2E14-005 | — | pôr "todos os campos" na Retificação | RC-38 (os "pode nascer" estão no contrato, falta a porta) |
| **`027` estrutural de vagas** | 13/09 #1 / 11.1; igualdade da soma; O16-002 | "três nomes para duas coisas" (a declaração da ampla) | — | RC-73 |
| **`030` composição que se explica** | E-5; ACH-09/10/36; ACH-48; 13/09 #3 (outro caminho); 13/09 #6 | ACH-61 (método comum); ACH-51; ACH-04 | a grade explicativa separada | — |
| **`032` executabilidade** | E-7; ACH-49; ACH-50; ACH-46 (a, b) | ACH-47 (nomeado) | — | RC-29, RC-30 (a mesma família de verificação) |
| **`033` navegação por capacidade** | E-2; ACH-40; ACH-35; ACH-38 | — | — | RC-94 (o inventário das negativas) |
| **`034` ordem por recorte** | ACH-47; metade do E-1; PR #85 | "três nomes" em classificação e ocupação | — | RC-73 (deixou o sorteio de fora de propósito) |
| **`035` sorteio executável** | ACH-51; ACH-55; a outra metade do E-1 | — | — | RC-72, RC-74 |
| **`036` instrução do recurso** | ACH-43; ACH-42; 13/09 #5 | — | "conceder documentos ao julgador" | — |
| **`037` quatro becos** | ACH-02; ACH-30; ACH-08; ACH-16; ACH-46 (c); os QW 2–5 do longitudinal | — | — | — |
| **`038` painel de condução** | inventário de 09/09 (a, b) | E-6 / ACH-25 | — | RC-78…82 (os defeitos da própria feature) |
| **`043` duplicar Perfil** | E-3 (exp.) no que é digitação | estudo E1/§6.4; ACH-61; atribuições por polo; AX-1/7/11 família (d) | — | TF-1 |
| **`044` recorte transversal (#173)** | estudo §5.9/E6; conferência D4; FR-727; custo do AX-14 | AX-10; AX-17 | a primeira forma do AX-17 | o **primeiro confronto entre Perfis** do sistema (denominação) — o passo inicial de RC-31 |
| **`#161` (`01d9163`, sem spec)** | AX-14 e AX-17 na integridade; achado do portal §3 | — | — | a 044 |

**Uma observação de arquitetura.** As três raízes de 16/09 que continuam abertas — E-3, E-4 e E-6 —
atravessaram **cinco** features sem serem tocadas, e a razão é a mesma nas três: **nenhuma é local a uma
tela**. A E-4 só avança caso a caso, e só onde o modelo **declara** a relação entre as duas fontes, como o
#161 e a `044` fizeram. A "validação que ataca a classe inteira", recomendada em 16/09, não é
executável. É por isso que ela não aparece aqui como uma spec.

---

## 9. Mapa atual de evolução por domínio

| Domínio | Resolvido | Pendências (A/B) | Oportunidades (C) |
|---|---|---|---|
| **Composição e autoria** | explicação no lugar, densidade, duplicar Perfil, quadro único, correções de 25/09 | **RC-08** rascunho local (A); RC-09, RC-10, RC-11 diretas; RC-12 teto; RC-13 decisão E2 | RC-14, RC-15, RC-16 |
| **Documento publicado** | tabelas, cabeçalho, método do sorteio | RC-20 número; RC-21 anexos citados; RC-22 hora; RC-23 fecho; RC-24 seções (decisão) | RC-25 (decisão E10), RC-26 |
| **Validação antes de publicar** | executabilidade (032), documento × execução (#161) | **RC-29** duas avaliações (A); RC-30 D-G1; RC-31 entre Perfis; RC-32 validação em Edital publicado | RC-34 |
| **Retificação** | contrato, vocabulário da gestão | **RC-37** Modalidade (A); **RC-38** o que "pode nascer" (A/B); **RC-39** "O que mudou" (A) | RC-40 |
| **Reaproveitamento** | referências, cronograma, segundo Edital | RC-42 guardião; RC-43 estado de revisão | — |
| **Portal e inscrição** | parecer, notícia do eliminado, facultativo na Revisão | RC-47 título e vagas; RC-48 prazo recursal público; RC-49 prazo no rascunho; RC-46 validar | RC-50 |
| **Documentos exigidos e Mesa** | contenção #161, instrução na Mesa, recorte transversal e lista gravada (RC-52, RC-53, #173), filtro de concorrência (RC-54, #172) | RC-55 submodalidade | resíduo do RC-54, RC-56 |
| **Oferta, ocupação e convocação** | ordem por recorte, cauda completa | **RC-58** cadastro de reserva (A, validar); RC-59 cascata | — |
| **Comissão e avaliação** | mesa, distribuição, impedimentos, julgador | RC-61 Perfil/polo; RC-62 Mesa após Resultado; RC-63 validar; RC-64 barema e alcance; RC-65 heteroidentificação | RC-66, RC-67 |
| **Resultado e divulgação** | prévia exemplar, publicador com caminho | — | RC-69, RC-70 |
| **Sorteio** | executável ponta a ponta, vocabulário fechado | **RC-72** fonte de demonstração (A); RC-73 recortes; RC-74 gatilho da fonte real | — |
| **Recursos** | instrução, parecer, tempestividade | RC-76 datas (parte viável em RC-48) | — |
| **Condução** | Processo = Supervisão; visão entre Processos | **RC-78, RC-79, RC-80** (A); RC-81, RC-82; RC-77 remedir | RC-84, RC-85, RC-86 |
| **Identidade e implantação** | barreira de produção | **RC-92** autenticação (A); RC-93 correio e retenção; RC-95 Registro Acadêmico | RC-94 D-G2, RC-96 |
| **Integridade e engenharia** | append-only 34/34, contrato de mutabilidade, `ValorDeFato` nas três camadas (RC-101, #183) | — | RC-102, RC-103 |

---

## 10. Backlog residual consolidado

A prioridade segue seis critérios: (1) fluxo quebrado ou incompleto; (2) risco operacional; (3) impacto
para candidato, operador ou comissão; (4) frequência; (5) dependências; (6) esforço e oportunidade de
consolidação.

**Não atribuo número de spec.** Onde digo "parece justificar uma futura spec", a numeração deve ser tirada
do repositório no momento em que ela for escrita. A faixa `FR-` é global desde a `024`; meça o teto
antes.

### P1 — fechamento necessário

**B-1 · Fechar a `038`: a condução que não afirma o que não mediu**
- **Problema.** O painel diz "nada a fazer" a quem só vê parte do Processo. O recurso que acabou de chegar
  é invisível. Nove dos quinze sinais do gestor são ruído permanente ou beco.
- **Origem.** Convergência de 20/09: C1, C2, C4, C5, C6; N-01, N-02, N-04…N-07. E-6 (16/09). Inventário de
  09/09 (e).
- **Situação atual.** O painel e a Supervisão concordam e o N-03 foi fechado. Nada mais mudou desde 20/09.
- **Lacuna residual.** RC-78, RC-79, RC-80, RC-81 e RC-82, mais a unidade da medida (RC-84).
- **Escopo mínimo.**
  - A frase de ausência relativa ao alcance do leitor.
  - A admissibilidade no sinal do recurso.
  - A doutrina do `status` do Evento: derivar na leitura, ou tirá-lo da comparação.
  - O destino do `UX-001`.
  - "Peça a quem…" nos sinais sem caminho.
  - O denominador da cobertura sobre os participantes.
- **Fora de escopo.** Sorteio e matrícula no painel, agregação por Edital, responsável individual e
  qualquer painel novo.
- **Dependências.** Duas decisões curtas do usuário: a doutrina do `status` e a espécie nova × ampliar o
  `UX-064`. O N-04 vem **depois** do N-05/N-06.
- **Evidência.** §3.13.
- **Natureza.** fechamento de fluxo e correção.
- **Por que P1.** É condição de saída do piloto. É a única superfície que quebra a ausência honesta. É
  pequena. E sem ela, as próximas features serão conduzidas por um instrumento que não é confiável.
- **Justifica uma futura spec** — curta, ou emenda da `038`.

**B-2 · O que dependia da `044`**
- **Problema.** O "O que mudou" omite a mudança de recorte do documento. O recorte transversal e a lista
  gravada, que eram o centro desta evolução, entraram com o #173, e o `ValorDeFato` foi corrigido pelo
  #183, os dois em 26/09.
- **Origem.** Estudo de 21/09 §5.9/E6; AX-10, AX-14 e AX-17; a conferência e a decisão de 25/09; o PR
  #171.
- **Situação atual.** A `044` está na `main` (#173, `47876ad`, CI verde), e a Mesa foi percorrida pela
  tela depois do merge (`0c4e6b0`). O #171 entrou como registro, e a correção veio no #183
  (`inscricoes/0006`, gatilho e guarda de modelo).
- **Lacuna residual.** RC-39 ("O que mudou" sem o recorte), que é independente e barato. Da `044` fica
  só a T065 (recompor o 140/2025), que é medição, e não lacuna.
- **Escopo mínimo.**
  - As duas entradas de `alteracoes.py`.
- **Fora de escopo.** Submodalidade (RC-55) e condição sobre o candidato (decisão D2).
- **Dependências.** Nenhuma.
- **Natureza.** transparência.
- **Por que P1.** É pequeno e já decidido, e a FR-130 da `024` é violada hoje.
- **Não precisa de spec nova.**

**B-3 · O que o Edital publica e não executa: a varredura que a `032` não fez**
- **Problema.** Três coisas publicam o que o sistema não sabe executar ou auditar, e uma afirma um
  impedimento que não existe:
  - uma Etapa com duas avaliações publica um ato que não se consolida;
  - uma eliminatória sem nota mínima tem o mesmo defeito de momento;
  - um sorteio pode sair com a semente de demonstração;
  - um Edital publicado mostra "Impede" falso.
- **Origem.** O achado de 21/09 (duas avaliações); o NOVO-1 dos lotes 4 e 7; a `D-G1` e a issue #117; o
  ACH-29 de 16/09.
- **Situação atual.** A `032` cobre o marco classificatório, e só ele.
- **Lacuna residual.** RC-29, RC-72, RC-30 e RC-32.
- **Escopo mínimo.**
  - **Aviso**, e não IMPEDE, para as três formas de Etapa inconsolidável — a D-008 recusou proibir na
    elaboração.
  - A barreira de produção para a "Fonte de demonstração".
  - A `D-G1` impeditiva no ato de publicação, com a #117 junto.
  - A validação do Edital publicado sobre a versão vigente, com o ato da Retificação.
- **Fora de escopo.** Uma regra de combinação de avaliações.
- **Dependências.** Nenhuma técnica.
- **Natureza.** correção e governança.
- **Por que P1.** São atos imutáveis, e o conserto é pequeno. A fonte de demonstração é o único furo de
  auditabilidade encontrado nesta auditoria.
- **Justifica uma futura spec curta.** A barreira da fonte cabe numa correção direta.

**B-4 · A Retificação acrescenta o que o contrato já permite**
- **Problema.** Um Edital publicado sem uma Modalidade, sem janela recursal ou com um critério de
  desempate errado não tem conserto pela tela.
- **Origem.** `D-G5` (19/09); G16-001 (09/09); o achado do objeto que nasce só pelo método (14/09); AX-1
  (15/09); o NOVO-1 do lote 1.
- **Situação atual.** O contrato da `026` já declara "pode passar a existir". A tela não oferece o
  caminho, e um teste prende essa ausência.
- **Lacuna residual.** RC-37 e RC-38.
- **Escopo mínimo.**
  - Acrescentar Modalidade a um Perfil de Edital publicado, com as cinco restrições da `D-G5`.
  - Acrescentar a janela recursal.
  - Acrescentar um critério de desempate.
  - Corte e reversão só se couberem sem regra nova.
- **Fora de escopo.** O catálogo de Modalidades no Edital (contradito) e retificar campos derivados ou
  estruturais.
- **Dependências.** Nenhuma técnica. Decidir se corte e reversão entram.
- **Natureza.** fechamento de fluxo.
- **Por que P1.** É "o único caso de Edital publicado sem correção possível", dito em 19/09 e em 20/09, com
  decisão tomada. O único remédio de hoje é cancelar e republicar.
- **Justifica uma futura spec.** Não é pequena.

**B-5 · Cadastro de reserva executável** — *P1 depois de validado*
- **Problema.** Um Edital só de cadastro de reserva publica e não convoca, e o limite de suplentes
  publicado não tem efeito.
- **Origem.** P-1, P-2 e P-3 (07–12/09); estudo M15/E8 (21/09); os NOVOS dos lotes 1 e 3.
- **Situação atual.** Nada. O #159 tornou o "limitado" publicável.
- **Lacuna residual.** RC-58.
- **Escopo mínimo.**
  - **Primeiro, validar pela tela**: publicar um Edital com 0 vagas imediatas e cadastro de reserva,
    classificar e tentar convocar.
  - Confirmar a semântica pretendida de `reserveLimit`.
  - Só então especificar a convocação para a reserva e a relação entre o limite e o `cutRule`.
- **Fora de escopo.** Prazo de validade e prorrogação (P-3) na primeira versão, se não for exigido.
- **Dependências.** Confirmar se a família está no alvo do piloto (Editais de tutoria da UAB costumam ser
  de reserva).
- **Natureza.** fechamento de fluxo.
- **Por que P1.** É a mesma classe do ACH-47, que em 16/09 foi S4/P0: "aceita, publica e não executa".
- **Justifica uma futura spec**, depois da validação.

**B-6 · Rascunho local que restaura sem perder** — *P1 depois de validado*
- **Problema.** A salvaguarda promete retomar sem redigitação, perde coleções aninhadas em silêncio e
  regrava a perda.
- **Origem.** AX-16 (15/09); o NOVO-2 do lote 5 (a `043` ampliou a superfície).
- **Situação atual.** Código de 08/09.
- **Lacuna residual.** RC-08.
- **Escopo mínimo.**
  - Reproduzir em cinco minutos: um Perfil com uma Modalidade, sair sem gravar, restaurar.
  - Se confirmar, corrigir a recriação das coleções aninhadas **ou** restringir a salvaguarda às etapas
    sem coleção aninhada.
- **Fora de escopo.** Reescrever o mecanismo de rascunho.
- **Dependências.** Nenhuma.
- **Natureza.** correção.
- **Por que P1.** Contradiz a FR-020 da `002`, é perda silenciosa na etapa mais cara, e o conserto
  mínimo é pequeno.
- **Correção direta, sem spec.**

**B-7 · Autenticação institucional real, com correio e retenção** — *P1 de implantação, trilha paralela*
- **Origem.** C7 (20/09); T056 da `002`; G1–G4/G22 e E2E-020 (02/09).
- **Lacuna residual.** RC-92 e RC-93.
- **Escopo mínimo.**
  - O adaptador contra o provedor do Ifes (gestão), separado do candidato.
  - SMTP institucional com redundância para o código de acesso.
  - A política de retenção e descarte de documentos.
  - Uma decisão escrita sobre rascunhos visíveis à gestão.
- **Dependências.** **Externas**: o provedor e a política institucional. Aparece também em RC-67 e RC-87,
  que dependem de ligar identidade a papel.
- **Natureza.** operação e segurança.
- **Por que P1.** Sem isso não há produção, por desenho.
- **Justifica uma futura spec** quando o provedor estiver definido.

### P2 — evolução relevante

**B-8 · O candidato vê o Edital certo, as vagas da sua lista e o prazo que corre**
- **Problema.**
  - A página da seleção leva o título do Processo, sem o do Edital.
  - As concorrências aparecem sem quantidade.
  - A página pública do resultado não diz o prazo recursal.
  - O rascunho não avisa que o prazo acabou.
- **Origem.** ACH-53 e 13/09 P2; 13/09 QW12 e convergência §7; E2E15-007; a parte executável do ACH-41.
- **Situação atual.** Não implementado.
- **Lacuna residual.** RC-47, RC-48 e RC-49.
- **Escopo mínimo.**
  - `h1` com o título do Edital.
  - A quantidade do quadro ao lado de cada concorrência.
  - A janela do marco na página pública do resultado.
  - A data-limite na prévia da divulgação.
  - O aviso de prazo encerrado no rascunho.
- **Fora de escopo.** Confrontar a janela com o Evento do Cronograma, que exige modelar o vínculo (RC-76).
- **Dependências.** Nenhuma.
- **Natureza.** UX e transparência.
- **Por que P2.** É o candidato, e é frequente. Mas nenhum requisito é violado: a FR-055 é MAY.
- **Parece justificar uma spec curta**, ou um conjunto de diretas.

**B-9 · Conferências baratas do documento publicado**
- **Origem.** AX-8, AX-12 e AX-9 (15/09); AX-1, AX-7 e AX-11 (15/09); E-1 (15/09).
- **Lacuna residual.** RC-20, RC-21, RC-12 e RC-31.
- **Escopo mínimo.**
  - **Avisos** na Revisão: título × número/ano; "ANEXO X" citado sem rótulo; divergência de desempate,
    percentual, fundamento ou tipo de fato entre Perfis de mesmo código.
  - Renderizar o teto de inscrições, e decidir se ele ganha campo na etapa Inscrição.
- **Fora de escopo.** Mover qualquer coisa para o Edital, e IMPEDE onde a divergência pode ser legítima.
- **Dependências.** O confronto de denominação da `044` (B-2) é o precedente, e o aviso de percentual
  mora ao lado dele.
- **Natureza.** integridade do publicado.
- **Por que P2.** Cada aviso é pequeno, e os casos já foram observados em Editais reais. Nenhum deles é
  ato inexequível.
- **Parece justificar uma spec.**

**B-10 · Reuso com estado de revisão**
- **Origem.** Estudo E9, Caso 7, §5.3 e A4 (21/09); a `D-G3` ("a regra do reaproveitamento é a parte não
  óbvia"); 023 §resíduo ("quarto estado *reaproveitada*"); o NOVO-1 do lote 6; RC-42.
- **Lacuna residual.** RC-43 e RC-42.
- **Escopo mínimo.**
  - A etapa ou seção marcada como "vinda da oferta anterior" até ser gravada.
  - Não herdar a ocorrência do sorteio.
  - Um banner que distingue o herdado do revisado.
  - O teste guardião do remapeamento.
- **Fora de escopo.** Marcação campo a campo e detecção semântica de prosa.
- **Dependências.** Recomendado antes: medir N→N+1 por reuso (estudo §14).
- **Natureza.** UX e integridade.
- **Parece justificar uma spec pequena.**

**B-11 · Diretas da composição e da Revisão**
- RC-09 (rótulos defasados até gravar), RC-10 (colapso por Perfil e severidade primeiro) e RC-11 (caixas
  de marcação no lugar do `select multiple`).
- **Natureza.** UX.
- **Por que P2.** O ganho é maior justamente nos Editais multipolo, que são 4 dos 5 da amostra.
- **Sem spec.**

**B-12 · Organização do trabalho por Perfil**
- **Origem.** ACH-60 e ACH-61 (16/09); convergência §10 e §16.
- **Lacuna residual.** RC-61.
- **Escopo mínimo.** Coluna e filtro de Perfil na distribuição e na alocação. É leitura, sem autorização
  nova.
- **Fora de escopo.** Comissão local enxergando só o seu polo: exige decisão de governança e Edital real
  multipolo. Este já existe (o estudo de 21/09 cadastrou o 140/2025 e o 28/2026), então **a decisão pode
  ser tomada**.
- **Natureza.** operação.
- **Correção direta** para a parte de leitura.

**B-13 · Sorteio coerente com a ocupação, e a fonte real observada**
- RC-73: vagas por recorte e aviso do recorte sem linha no quadro.
- RC-74: workflow agendado, não bloqueante.
- **Por que P2.** Uma ordem sorteada num recorte que a ocupação ignora é trabalho perdido em ato público.
  E a `D-G3` pôs todo sorteio futuro na dependência da Caixa.
- **Spec curta** para o RC-73. **Decisão de operação** para o RC-74.

**B-14 · Mesa e reavaliação**
- RC-62: a guarda "Resultado vigente na própria Etapa", com exceção para a reavaliação determinada.
- RC-63: percorrer o caminho da reavaliação e corrigir a mensagem que manda ao julgamento de recurso.
- **Por que P2.** Impede avaliação que não produz efeito, e desfaz um diagnóstico errado que ainda está
  no manual.

**B-15 · Validações de destino e de escala**
- RC-95 (Registro Acadêmico), RC-86 (custo de consulta com 10+ Editais), RC-46 (reconciliação do portal)
  e RC-96.
- **Natureza.** validação, não desenvolvimento. É condição de saída do piloto (20/09).

**B-16 · Documento: hora, fecho e seções**
- RC-22, RC-23 e RC-24. As três começam por **decisão**: o modelo de instante com "sem hora", o que o
  fecho do Cefor precisa conter, e o conjunto e a ordem das seções.
- **Justifica spec** só depois das decisões.

### P3 — oportunidade futura

- **B-17 · Famílias fora do alvo atual.** Alcance da Etapa por Perfil e barema (RC-64); heteroidentificação
  (RC-65), que depende do alcance da Etapa; cascata de grupos (RC-59); submodalidades (RC-55); conteúdo
  comum aos Perfis e TF-1 (RC-13, RC-07). **Cada uma espera uma decisão de alvo**, e juntas formam o que um
  dia pode ser a spec de "alcance da Etapa".
- **B-18 · Varredura de polish.** RC-69 e RC-40 (identificadores de máquina e tabela única de
  vocabulário); RC-70, RC-84, RC-66, RC-50, RC-16, RC-26, RC-45 (cartão público) e RC-56.
- **B-19 · Governança pendente de execução, de baixo impacto.** RC-94 (`D-G2`) e RC-34 (fronteira
  avisos × Atenção, depois da B-3).
- **B-20 · Higiene de engenharia e documentação.** RC-103 (Status das specs, README, manual, contagens,
  `make test` sem PostgreSQL, testes em UTC, teste do CSRF, `seed_demo --numero`, guarda de citações,
  derivação duplicada) e RC-102 (encerrar a branch da `039`). **Uma** varredura, sem spec. A convenção de
  `Status` é decisão do usuário.
- **B-21 · Notificação a ator interno** (RC-67): só depois da B-1 e da B-7.

---

## 11. Dependências entre as evoluções restantes

```
B-2 (a 044, mesclada pelo #173) ──► B-2b (RC-101, ValorDeFato: `0006`, mesclada pelo #183)
      └─────────────► B-9 (o aviso de percentual mora ao lado do confronto de denominação)

B-1 ─ decisão da doutrina do `status` ──► N-06 ──► N-05 ──► N-04
   └─ decisão espécie × `UX-064` ───────► N-02
   └─ depois de limpo ─► RC-77 (remedir) ─► RC-85 (sorteio e matrícula no painel?) ─► B-21 (notificação)

B-3 (D-G1 impeditiva) ─► RC-34 (a fronteira avisos × Atenção fica menor)
                      └► issue #117 (a severidade condicionada ao ato passa a existir)

B-4 (Retificação acrescenta) ─ independente da 039 (contradita); faz fronteira com RC-73 (recortes do sorteio)

B-5 (cadastro de reserva) ─ validar ─► decisão de alvo ─► spec; toca RC-30 (corte) e a ocupação

B-7 (autenticação) ─► RC-87 (antecipar a falta de julgador) · B-21 (e-mail interno) · a produção

RC-64 (alcance da Etapa) ─► RC-65 (heteroidentificação) · barema
```

**O que pode ser feito isoladamente, hoje:** B-6, B-8, B-11, B-12 (a leitura), o RC-39 dentro da B-2,
a barreira da fonte de demonstração dentro da B-3, e a B-20.

**O que é melhor resolver junto:**
- B-3 com a #117.
- B-4 como uma spec só: Modalidade, janela e critério, e não três.
- B-9 depois da B-2.
- B-10 absorvendo a regra do reuso da D-G3.

---

## 12. Ondas sugeridas de evolução

Os agrupamentos saem das dependências e da natureza, não da ordem dos relatórios.

**Onda A — fechar o que já foi decidido e o que afirma o que não sabe**
B-1 (fechar a 038) · B-2 (o "O que mudou"; a 044 e o ValorDeFato já entraram) · B-3 (o que publica e não executa) ·
B-6 (rascunho, se confirmar).
*Critério da onda:* a decisão já existe ou a correção é pequena; todas atacam um instrumento que hoje
afirma mais do que sabe — o painel, a validação, o documento ou o rascunho. Ao fim dela, as condicionantes
C1, C2, C5 e C6 do piloto fecham.

**Onda B — Edital publicado com conserto, e oferta executável até o fim**
B-4 (a Retificação acrescenta) · B-5 (cadastro de reserva, depois de validado).
*Critério:* são as duas formas restantes de "Edital publicado que não chega ao fim", e as duas precisam de
spec.

**Onda C — candidato, documento e custo de autoria**
B-8 (portal) · B-9 (conferências do documento) · B-10 (reuso com revisão) · B-11 (diretas da composição) ·
B-12 (Perfil na distribuição) · B-13 (sorteio e recortes) · B-14 (Mesa).
*Critério:* ganho claro, nenhum ato inexequível em jogo. Podem entrar em qualquer ordem dentro da onda; a
B-9 depois da B-2.

**Trilha paralela — implantação**
B-7 (autenticação, correio, retenção) · B-15 (validações de destino e de escala) · B-16 (as decisões do
documento).
*Critério:* dependem do Ifes, do setor de Registro Acadêmico e de decisões institucionais, e não
bloqueiam as ondas.

**Depois, e só com decisão de alvo:** B-17 (as famílias). Polish e higiene (B-18, B-19, B-20) entram como
varreduras oportunistas quando se tocar nas telas envolvidas.

---

## 13. Incertezas que precisam de validação humana

### Decisões que só o usuário pode tomar

**Registradas em [`decisoes-pendentes-da-consolidacao.md`](decisoes-pendentes-da-consolidacao.md)**, cada uma
com o que já está fixado, as opções com as consequências e uma recomendação — a decisão fica com o
usuário. As do item 9 e a Diretoria do item 12 já tinham registro próprio e aparecem lá só como índice.

1. **Doutrina do `status` do Evento.** A `022` (D-004) o trata como declarado; o contrato da `026`,
   como derivado. A interface não oferece o campo, e qualquer das duas escolhas fecha o ruído (RC-80). → DP-01
2. **Admissibilidade no painel**: espécie nova, ou `UX-064` cobrindo as duas situações (RC-79)? → DP-02
3. **O `UX-001` em Edital publicado**: sinal sem destino, dito como fato estrutural, ou aviso de
   composição fora da Atenção (RC-80)? → DP-03
4. **O adiamento da B-1 foi deliberado?** Se foi, falta o registro. Se não foi, é o primeiro item. → DP-04
5. **Cadastro de reserva está no alvo do piloto?** E qual é a semântica de `reserveLimit`: limite
   executável ou texto normativo (RC-58)? → DP-05
6. **O Cefor usa dupla leitura?** Isso decide se o RC-29 fica só no aviso ou ganha spec de combinação. → DP-06
7. **A `D-G2` continua valendo**, agora que a interface não oferece mais os três caminhos (RC-94)? → DP-07
8. **A `039` está encerrada?** Registrar, e dizer onde ficam a `D-G5` (RC-37) e o alcance da Etapa
   (RC-64). A decisão de 25/09 foi de produto, ou só uma leitura do texto constitucional? A memória
   "a Constituição preserva valor, não campo" mostra que a distinção já importou uma vez. → DP-08
9. **Decisões pendentes do estudo de 21/09** (já registradas no próprio estudo, §12 e §15):
   - E10 (redação × transcrição);
   - E5 (seções);
   - E2 (conteúdo comum não-cota);
   - FR-344 (âncora do ano);
   - FR-465/466 (remeter o método);
   - casas decimais no marco de sorteio.
10. **A `D-011` continua?** Admitir prova nova no recurso é pergunta normativa, não lacuna de UX. → DP-09
11. **Quais famílias entram no alvo**: prova de títulos (barema), PPI com heteroidentificação, cascata
    (14/2026), submodalidade (140/2025). → DP-10
12. **Papel próprio de Diretoria** (pendente desde a `040`) (já registrado na `040`, D-008) e **convenção do campo `Status`** das specs. → DP-12
13. **O escopo de trabalho por Perfil** (RC-61) pode ser decidido: o Edital real multipolo que a
    convergência pedia já foi cadastrado. → DP-11

### Verificações que exigem percurso ou ambiente
- **RC-08** (AX-16), **RC-32** (o "Impede" falso em Edital publicado), **RC-58** (convocar a reserva),
  **RC-63** (E2E18-001) e **RC-46** (019 §4.2): todos foram lidos de ponta a ponta no código, e nenhum foi
  percorrido nesta auditoria.
- **PR #173**: mesclado em 26/09 com o CI verde (7831 passando, 11 pulados), e a Mesa percorrida pela
  tela depois (`0c4e6b0`). Falta a T065, o 140/2025 recomposto.
- **Acervo publicado antes do #161** com "Todos os Perfis + Modalidade de um só": só a base real responde.
- **A fonte de demonstração**: há algum controle fora do repositório — implantação, revisão de Edital —
  que já impeça usá-la em produção?
- **O fecho do documento** (RC-23): o que um ato do Cefor precisa conter.
- **RC-95**: a importação real no Registro Acadêmico.

### Limites desta auditoria
- **Nada foi executado.** Os estados vêm da leitura de código, de testes e do histórico. Onde o
  comportamento depende de estado de banco ou de interação, a marca é `[VALIDAR]`.
- **Os anexos foram produzidos por sete leitores independentes**, cada um sobre um conjunto de relatórios.
  Conferi pessoalmente no código as afirmações que decidem prioridade: D-G1, D-G2, D-G5, N-01, N-02, N-06,
  AX-16, `alteracoes.py`, o consumo de `reserveLimit`, a fonte de demonstração, o portal, a validação do
  Edital publicado e a convocação sem déficit. As demais estão como os anexos as registram.
- **As contagens da §1 são por unidade consolidada**, e dependem de como os IDs antigos foram fundidos. As
  contagens por lote, que não se somam porque se sobrepõem, estão no fim de cada anexo.
