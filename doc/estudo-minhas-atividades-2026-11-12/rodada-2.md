# Rodada 2: "Minhas Etapas" como lugar da visão pessoal (12/11/2026)

**O que se avaliou.** O usuário propôs, depois de ver a tela "Minhas Etapas" vazia de uma identidade
com nove papéis, que a visão pessoal more ali, renomeada "Minhas atividades", e não na faixa da Lista.
Na Lista, a faixa ficaria só como resumo. A proposta mantém D-2, D-3 e D-4. Ela também pede duas
verificações antes de especificar:
- quanto de "Minhas Etapas" se reaproveita, e quem depende da página;
- como a agregação fica eficiente sem outra lógica de negócio.

**Veredito.** A mudança de D-1 procede, e por uma razão mais forte do que a de navegação: o
**custo**. A proposta tem três pontos que o estudo ajusta:
- o resumo da Lista não pode ter número;
- o rascunho de tela usa contadores e abas que dão peso ao que não é ação;
- os exemplos devem usar as frases da derivação, e não frases novas.

---

## 1. Por que "Minhas Etapas" é melhor lugar que a Lista

| Critério | Faixa da Lista (rodada 1) | "Minhas atividades" (rodada 2) |
|---|---|---|
| Quem paga a derivação | **toda** abertura da Lista, que é a página inicial de todos os papéis | só quem abre a própria página |
| Contrato de custo | a FR-2806 da 104 (custo constante) teria de ceder, ou a faixa carregaria à parte | nenhum contrato existente a romper |
| Recorte dos Editais | o mesmo | **2 consultas** para os Editais das comissões da pessoa (medido) |
| Entrada | é onde todos chegam | já é onde a presidência chega na demonstração (`views.py:773`; `test_jornada_da_presidente.py`) e onde o guia da equipe manda começar |
| O que a página já tem | a lista de Processos | as comissões que a pessoa integra, com as rotas da presidência (achado UX-24 do estudo de 11/11), e as Etapas com a carga de cada uma |
| Estado vazio | — | hoje mente por omissão para quem tem papéis (a tela do usuário). Passa a dizer o trabalho real |

A rodada 1 recomendou a Lista para não abrir "dois lugares para a mesma pergunta". O argumento é
real, mas pesa menos do que o custo pago por todos. Ele se resolve com a nota da faixa apontando para
a página, como o usuário propõe.

## 2. O que se reaproveita, e quem depende da página

**Reaproveitável sem mudança:**
- **A view `minhas_etapas`** (`interface/views.py:12090`). Não exige permissão, e o estado vazio não
  é recusa.
- **`comissao_selectors.comissoes_da_pessoa`**: o recorte dos Editais.
- **`comissao_selectors.minhas_etapas` e `avaliacao_selectors.carga_nas_etapas`**: a avaliação, numa
  agregação só.
- **O bloco "Comissões que você integra"** e os cartões de Etapa com medidor
  (`templates/interface/minhas_etapas.html`, `static/interface/telas/minhas-etapas.css`).
- **As regras de estado vazio** (`preside`, `sem_papel_nem_atribuicao`), que só precisam de frases
  novas.

**Dependências, que mandam manter o endereço:**
- As rotas da Mesa pendem de `minhas-etapas/<edital>/<etapa>/…` (`urls.py:874-909`), e a hierarquia
  é proposital (R-003 da 076, `navegacao.py:10`).
- A seção ativa da barra para a Etapa aberta pela gestão (FR-1752 da 077,
  `test_shell_da_gestao.py:208-242`).
- O pouso da demonstração (`views.py:773`) e o link "Ver minhas atribuições" da Lista
  (`lista.html:24`).
- O item de avaliação da 104 e a URL da Mesa no andamento (`trabalho.py:209`, `andamento.py:338`).
- 28 arquivos de teste citam a página ou a rota. A guarda da 011 (`test_011_intocada.py`) prende o
  domínio — guarda, alocação e comissão —, e não a tela, então não é afetada.

**Conclusão.** Muda o **nome visível**: a barra, o título, a trilha e a trilha da Mesa ("Minhas
atividades › Minha Mesa"). O endereço e o nome da rota ficam. "Atividade" não colide com nenhum
termo da gestão: não aparece em template nenhum, nem como coluna de cronograma.

O custo do nome está fora do código:
- **112 arquivos de `doc/` citam "Minhas Etapas"**, entre eles o guia da equipe de treinamento e o
  manual;
- a D-007 da 104 adiou a troca de nome até validar com pessoas.

O incremento pode trocar o nome e atualizar o guia e o manual. As specs e os estudos antigos ficam
como registro.

## 3. A eficiência da agregação, medida

[`validacao/custo_por_tabela.py`](validacao/custo_por_tabela.py), saída em
[`validacao/custo.txt`](validacao/custo.txt):

| Identidade | Recorte | Derivação nos Editais do recorte | Itens seus |
|---|---|---|---|
| presidência | 2 consultas, 11 Editais | 1079 consultas, 1,1 s (38 a 189 por Edital) | 20 |
| avaliador | 2 consultas, 11 Editais | **1696 consultas, 1,8 s** | **1** |

**Três reduções, todas sem regra nova.** Nenhuma muda a regra da 127. Mudam só **em quais Editais**
ela roda, e **quantas vezes relê a mesma coisa**.

1. **Derivar só onde algo pode ser seu (a maior).** Pela própria `e_sua` (`andamento.py:2708-2722`),
   quem não conduz, não publica, não julga e não retifica só pode ter três coisas como suas:
   - **avaliar**, que sai da carga da Mesa, a mesma conta de `carga_nas_etapas`;
   - **conferir**, só com `AlocacaoAConferencia`;
   - **a formalização**, só com designação.

   Para o avaliador, a página não roda a derivação nenhuma vez, e as 1696 consultas viram as poucas
   que a página já faz. A derivação roda só onde a pessoa preside ou está alocada à conferência. A
   equivalência é provável por teste: para um ator sem essas bases, as "suas" da derivação ⊆
   {avaliar, conferir, formalização}, em todos os cenários.
2. **Reler a versão vigente uma vez por Edital.** `publicacoes_versaoconsolidada` e
   `publicacoes_provenienciaconteudo` somam 274 das 1079 consultas da presidência, cerca de 25 por
   Edital. As funções de outras features que a derivação chama releem a versão vigente cada uma por
   si. Memorizá-la dentro de `_Leitor` vale também para o Centro, que paga o mesmo hoje.
3. **A 104 uma vez, e não por Edital** (V-6). `_trabalho_da_104` chama `trabalho.do_ator` com um
   Edital por vez. A página chama uma vez e entrega o resultado a cada `do_edital`, como já faz com
   `em_curso`.

**Não é preciso leitura em lote nem cache.** Cache por Edital exigiria invalidar a cada ato, o que é
uma segunda fonte de verdade com outro nome. Leitura em lote reescreveria vinte funções de outras
features. Com a redução 1, o custo cresce com os Editais que a pessoa **preside**, e não com os que
ela integra. A spec deve fixar um teto por Edital presidido, no molde de `test_andamento_em_escala.py`.

**O que continua caro, e fica fora do MVP:** o Publicador. "Publicar o resultado" não tem fronteira de
comissão (V-7). Julgar recursos não é caro: a 104 já o conta por agregação.

## 4. Os ajustes à proposta

**O resumo na Lista não pode ter número.** "Você tem 12 atividades" na Lista custaria a derivação
inteira na página de todos, e isso desfaz a razão da mudança. A faixa mantém os itens que já deriva
barato, e a nota de cobertura (`FORA_DA_FAIXA`) passa a apontar para "Minhas atividades" em vez de
"o detalhe de cada Edital". Os testes que fixam essa frase mudam junto.

**Sem contadores no alto e sem abas.** O rascunho tem três contadores (4 para fazer, 3 aguardando, 2
Etapas atribuídas) e três abas.
- Os contadores repetem o que as seções já dizem. Também põem "aguardando" no mesmo peso que "para
  fazer", que a própria proposta pede para evitar.
- Abas escondem a avaliação de quem também preside.

O estudo sugere três seções na mesma página:
1. "Para fazer agora", aberta;
2. "Em espera nos seus Editais", recolhida, com a data dita pelo que ela é;
3. "Suas Etapas de avaliação", com os cartões de hoje.

A contagem vai no título da seção, como os wireframes 1 e 2 mostram.

**Os textos são os da derivação.** "Conferir participantes habilitados" não é um ato do GPS. Os do
sorteio são três: "Congelar a relação", "Observar a extração" e "Sortear". Uma página que escreve
frases próprias para os mesmos atos volta a ter duas fontes. O ganho da proposta é justamente
mostrar o que o Centro mostra.

**A marca de base é boa.** "Ação disponível · Presidência" diz por que a linha é sua, e responde à
D-2 por construção: a linha do Gestor diria "permissão de gestão", e é isso que fica fora. O estudo
adota a marca.

**"Publicar resultado · Papel autorizado" é o caso caro** (item 3), e fica para depois.

## 5. Os três conceitos de designação

A tabela do usuário (atividade derivada, responsável operacional, delegação de autorização) é mais
precisa que a C1/C2 da [análise](analise.md#c-comparação-de-alternativas). O estudo a adota. Uma
verificação a completa: **hoje, o responsável operacional que tem algo para executar coincide com as
alocações que já existem.** O membro que não preside só pratica dois atos:
- avaliar, alocado à Etapa;
- conferir documentos, alocado à conferência.

Na preparação do sorteio, não há ato que um membro possa praticar. Por isso "João prepara o sorteio"
não tem linha executável, e a decisão de adiar a designação genérica se confirma.

## 6. Decisões revistas

| # | Rodada 1 | Rodada 2 |
|---|---|---|
| D-1 | a faixa da Lista | **"Minhas Etapas", renomeada "Minhas atividades", mesmo endereço.** Na Lista, a faixa fica, sem número, apontando para lá |
| D-2 | o Gestor não vê a condução como sua | mantida; a marca de base a torna visível |
| D-3 | adiar a designação | mantida, com os três conceitos do usuário; o responsável operacional executável já são as alocações |
| D-4 | sem prazo inventado | mantida |
| D-5 | visão pessoal, depois coordenação | mantida. A primeira entrega inclui as reduções 1 a 3 de custo |
| **D-6** (nova) | — | **Pouso do login institucional.** Hoje vai para a Lista (`views.py:872`). (a) Manter, e confiar na nota da faixa; (b) quem tem vínculo de comissão pousa em "Minhas atividades". O estudo sugere (a) no MVP e (b) depois de medir com a comissão real: a D-001 da 104 lembra que mudar a entrada custa um clique por dia a quem só consulta |
