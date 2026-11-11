# Research: A página do Processo Seletivo (147)

## 1. O pedido e a rodada 1

O pedido (11/11/2026) foi uma revisão de UI/UX da página de detalhe do Processo Seletivo, com ponto
de controle: investigar, construir duas alternativas com os templates e as folhas reais, validar em
cenários, papéis e larguras, e só implementar depois da escolha. Dois princípios guiaram: **o
Processo permite compreender e administrar o conjunto; o Edital permite compreender e conduzir a
seleção.** Ficaram vetados novo dashboard, motor de workflow, estados, indicadores artificiais e
persistência de apresentação.

A rodada 1 está publicada como relatório, com as capturas, em
<https://claude.ai/artifact/GBEBV6rtKUVYnduNvwX95X>, e registrada em
`doc/estudo-pagina-do-processo-2026-11-11.md`. O resumo:

- **Dados.** Banco `ps_ux_147`: `seed_demo`, os 15 cenários de treinamento (`134`), um Processo de 4
  Editais e um de 31, montados aplicando as receitas da `134` a Editais irmãos, e um Processo
  encerrado e um cancelado.
- **Medidas da página atual, a 1366 × 768.** 2.791 px com 4 Editais; 10.369 px com 31 (14 gráficos,
  15 linhas "Sem cronograma vigente", 20 sinais no fim). Consultas: 66 e 284, para o gestor.
- **Alternativa A** (conservadora): mesma ordem; cabeçalho compacto; ações da pessoa no cartão; atos
  recolhidos no cartão; tabela com inscrições e próximo marco; acompanhamento recolhível. 6.919 px
  com 31 Editais; a tabela rola dentro da moldura a 390 px.
- **Alternativa B** (acompanhamento): topo no padrão do Edital; ações e atenção lado a lado; Editais
  agrupados em lista; série só em curso; Administração no fim. 4.042 px com 31 Editais; sem rolagem
  lateral em nenhuma largura.
- **Custo.** As duas: +2 consultas fixas. Exceção: quem avalia, 72 → 195, porque a faixa calcula a
  carga de todas as Etapas da pessoa.

## 2. Os seis ajustes à alternativa B

A validação mostrou seis pontos, e o usuário escolheu "B com os ajustes":

1. **Sem duplicar o próximo passo.** O elaborador via "Elaborar o Edital 30/2026" e, logo abaixo,
   "Continuar a elaboração — Edital 30/2026". O botão fica; o item sai da lista (`FR-5303`).
2. **Sem a região de Atenção para quem não alcança espécie alguma.** O protótipo escrevia uma frase
   no lugar; ela afirmaria uma ausência, que é o que a `038` proibiu (`FR-5318`).
3. **Linha de uma altura só para Edital em preparo.** "Ainda não publicado" repetia o selo
   (`FR-5313`).
4. **No celular, Atenção antes dos marcos** (`UX-440`).
5. **Carga de avaliação recortada ao Processo antes do cálculo** (`FR-5309`).
6. **O ciclo em uma linha, com símbolo e texto**, vindo da alternativa A (`FR-5302`).

## 3. As decisões que o relatório deixou abertas

O relatório pediu quatro decisões além da escolha. O usuário respondeu só "B com os ajustes"; as
quatro foram tomadas pela recomendação do relatório e ficam aqui para revisão no PR:

- série diária só no período em curso — `D-004`;
- "Aguardando quem elabora" só para quem gere — `D-005`;
- Encerrados e cancelados recolhidos no Processo ativo — `D-006`;
- registrar o estudo em `doc/` — feito.

## D-001 — Alternativa B, e não a evolução da página atual

**Decisão.** Reorganizar a página pelo acompanhamento: topo com a situação do conjunto; o que fazer e
o que pede atenção; os Editais; a série em curso; a administração.

**Razão.** Só B escala (4.042 px contra 6.919 px com 31 Editais), só B não corta informação no
celular, e B usa o vocabulário e o desenho da página do Edital. O custo de B é revisar requisitos de
três features e os testes que os ancoram — trabalho de uma vez.

**Descartada.** A — menor ruptura, mas mantém o mesmo Edital em dois lugares e a tabela que não cabe
no celular.

## D-002 — As ações da pessoa vêm da faixa da 104

**Decisão.** "O que fazer agora" lê `trabalho.do_ator`, a mesma função da faixa "Ações disponíveis
para você" da Lista, recortada aos Editais do Processo.

**Razão.** A faixa já responde "o que eu tenho a fazer" com as regras dos detalhes, e com custo que
não cresce com o número de Editais. Uma segunda regra divergiria da Lista na primeira mudança.

**Descartadas.** As providências do andamento (`127`) por Edital — dezenas de consultas por Edital;
os atos de cada Edital (`acoes.do_edital`) — a `129` os tirou da Lista pelo mesmo custo.

## D-003 — O andamento de cada Edital fica na página do Edital

**Decisão.** A linha do Edital diz fatos — situação, inscrições, próximo marco, atenção, ações da
pessoa — e leva ao Edital. Fase, mapa e providências por lista não vêm.

**Razão.** É a distinção do pedido, e o custo: a derivação do andamento é por Edital e cara.

## D-004 — A série diária só no período em curso

**Decisão.** "Submissões por dia" mostra só os Editais com período em curso. Encerrado o período, a
série fica na Supervisão.

**Razão.** Com o período encerrado, o total já diz o que importa, e a série repetida por Edital era o
que mais alongava a página. Revisa a apresentação de `FR-556` da `038`; o pulso e a Atenção continuam
na página.

**Descartada.** Série de todo Edital recolhida em `details` (alternativa A) — esconde sem resolver.

## D-005 — "Aguardando quem elabora" só para quem gere o Processo

**Decisão.** A frase aparece para quem não elabora **e** pode criar Edital ou gerir a comissão do
Processo.

**Razão.** Ela nasceu para que o gestor soubesse que o certame espera outra pessoa. Para quem só
avalia, julga ou divulga, ela ocupa o lugar do trabalho dele com o de outro papel.

## D-006 — Encerrados e cancelados recolhidos no Processo ativo

**Decisão.** No Processo ativo ou em elaboração, o grupo vem recolhido com a contagem; no encerrado e
no cancelado, aberto.

**Razão.** No Processo em curso, o Edital que terminou raramente é o que se procura; no Processo
final, ele é o conteúdo.
