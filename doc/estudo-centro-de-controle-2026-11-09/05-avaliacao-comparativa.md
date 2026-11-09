# Entrega 5 — Avaliação comparativa

**Natureza da evidência.** Esta avaliação reúne três coisas:
- a medição automatizada das tarefas pelo Playwright (`prototipo/validar.py`);
- a inspeção heurística das capturas;
- a conferência do estado na tela de cada ato.

**Não houve teste com operadores.** Os números abaixo dizem **onde** está a resposta. Não dizem se uma
pessoa a encontra, nem se a entende. A validação humana segue em aberto, como a de toda a série
126–133 (SC-1245, SC-990 e o roteiro do estudo de 06/11).

## As tarefas medidas

"Primeira dobra" é o que cabe numa janela de 1440 × 900 sem rolar. A medição conta só o texto
visível: o que está dentro de um bloco recolhido não conta.

| Cenário | Tarefa | Tela atual | Proposta |
|---|---|---|---|
| C06 | T1 Situação operacional dita em palavras | ausente | na primeira dobra |
| C06 | T2 Próxima operação do operador | na primeira dobra | na primeira dobra |
| C06 | T3 Por que o sorteio ainda não pode | ausente | na primeira dobra |
| C06 | T5 O que é congelar a relação | ausente | um clique ("Entenda"), de propósito |
| C06 | T5b A Etapa de títulos não segura o sorteio | ausente | na primeira dobra |
| C12 | T1 Situação operacional dita em palavras | ausente | na primeira dobra |
| C12 | T4 Onde está a lista PPP | na primeira dobra | na primeira dobra |
| C12 | T6 Pendência atribuída ao operador | na primeira dobra | na primeira dobra |
| C12 | T7 Espera com data (resposta dos convocados) | na primeira dobra | na primeira dobra |
| C12 | T8 Histórico de etapa concluída | só abrindo um bloco recolhido | na primeira dobra |
| C08 | T7 Corte aguarda o prazo de recurso | na primeira dobra | na primeira dobra |
| C08 | T1 Situação operacional dita em palavras | ausente | na primeira dobra |

As tarefas que a tabela não mede, avaliadas por inspeção:
- **T9 (voltar do detalhe ao Centro de Controle).** Na implementação recomendada é gratuita: o caminho
  de navegação das telas de ato já aponta para o detalhe do Edital, que **passa a ser** o Centro de
  Controle. No protótipo, que mora em outra URL, a volta leva à tela atual. É uma limitação da
  maquete, e não da proposta.
- **"Diferenciar disponível de aguardando prazo".** Na tela atual, a diferença está na marca "Aguarda"
  dentro de uma lista corrida. Na proposta, há uma seção própria com a data no rótulo, e a data também
  aparece no cartão da fase ("◷ espera até 14/11").

**Altura da página.** Tela atual: 1586 px (C06) e 1756 px (C12). Proposta: 1908 px e 2044 px. A
proposta é **mais longa**, porque traz o detalhe da fase e a tabela por lista abertos. O ganho não é de
volume; é de ordem: as respostas sobem.

## Por que a proposta orienta melhor

1. **Diz onde estamos em palavras.** A tela atual exige montar o estado a partir do selo, da linha de
   contagens recolhida e das providências.
2. **Separa as quatro dimensões de estado**: administrativa, operacional, temporal e da providência.
   "Publicado" deixa de parecer resposta.
3. **Mostra o paralelismo sem fingir linearidade.** Várias fases acesas ao mesmo tempo, e por lista. É
   a objeção da 127 à barra de fases, respondida, e não contornada.
4. **Liga cada providência a uma fase e a um porquê.** O C06 deixa de sugerir que é preciso avaliar os
   títulos antes de sortear.
5. **O detalhe da fase vira roteiro.** Relação → Semente → Sorteio, com "vale para todas as listas" na
   semente. É a ordem que o guia da equipe ensinava em prosa.
6. **Rebaixa o fim de ciclo.** Encerrar e cancelar saem do cartão das providências.
7. **O Processo deixa de contradizer o Edital.**

## Riscos

| Risco | Como aparece | Mitigação proposta |
|---|---|---|
| A trilha ser lida como "fase única" | Um cartão aceso pode ser tomado como "a" fase | A frase "N frentes ao mesmo tempo"; vários cartões acesos; "1 de 2 listas" |
| Destaque errado | O C08 destacou a ordem de uma lista **vazia** como "Sua próxima ação" | Destacar só com a lacuna G-1 resolvida; até lá, sem destaque, ou com "lista sem inscritos" |
| Agregação que esconde uma célula | "Em andamento" pode cobrir uma lista *Depois* e outra *Feito* | A tabela por lista e o roteiro mostram a célula; regra pura e testada |
| Divergir da 127 | Duas leituras do mesmo estado | Nenhuma: a composição só lê o `Andamento`. A coerência se prova por teste (macrofase ACAO se, e só se, existe célula `A_PRATICAR`) |
| Texto pedagógico errado | "Entenda" explica uma regra de modo impreciso | Fonte única, revisada por quem conduz certames, e conferida com os guias (D-7) |
| Página mais longa | 20 a 30% mais altura | As respostas ficam na primeira dobra; o resto é consulta |
| Vazamento por agregação | A jornada e "onde estamos" para quem não `ve_a_matriz` | Mostram o que o nível 1 já mostra a todos. O detalhe por lista segue restrito (D-6) |
| Desempenho | Mais leitura por página | Nenhuma: o mesmo `Andamento`. O Processo agregado, sim, pede leitura em lote (G-2) |

## O que não foi validado
- **Pessoas.** Nenhum operador usou o protótipo.
- **Dois Perfis, dois Editais no Processo, vários marcos, sorteio com habilitação, corte ausente.**
  Nenhum cenário os tem. A proposta os trata por construção, mas **não foram vistos**.
- **Recurso interposto e julgado.** O C08 tem o prazo aberto e nenhum recurso; a fase "Resultado e
  recursos" com recurso pendente não foi vista com dado real.
- **Retificação em curso.** Nenhum cenário publicado tem uma; a faixa existe no template, mas não foi
  vista.
- **Leitor de tela.** Só foram verificadas a estrutura (títulos, `aria-current`, `scope` nas tabelas,
  tabelas com cabeçalho), a ordem do Tab e o foco. Não houve sessão com VoiceOver nem NVDA.
- **O botão "Observar a ocorrência" antes do congelamento (A-03).** Não foi praticado.
