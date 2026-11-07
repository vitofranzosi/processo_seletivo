# Estudo de caso — a classificação por etapas no GPS (Edital 900/2026, demonstrativo)

**Data:** 07/11/2026 · **Base:** `main` em `f5fc1c5d` · **Ambiente:** banco isolado `ps_estudo_classif`,
relógio da aplicação deslocado fase a fase (09/11/2026 a 06/01/2027) · **Dados:** todos fictícios.

Este estudo é **independente** do estudo do sorteio do Edital 35/2026
([estudo-sorteio-edital-35-2026-11-05.md](estudo-sorteio-edital-35-2026-11-05.md)). Ele monta um único
processo seletivo por classificação, do zero, e o conduz até a matrícula, para responder duas perguntas:

- **A.** O que o GPS realmente executa hoje num processo seletivo por classificação?
- **B.** Um operador consegue entender e usar isso sem conhecer a implementação?

| Entrega | Onde está |
|---|---|
| A. Estudo de caso completo | este documento |
| B. Guia HTML pedagógico | [estudo-classificacao-demonstrativa-2026-11-07/index.html](estudo-classificacao-demonstrativa-2026-11-07/index.html) |
| C. Matriz de capacidades exercitadas | seção 12 |
| D. Diagnóstico de UX/UI | seção 13 |
| E. Roteiro de reprodução | [estudo-classificacao-demonstrativa-2026-11-07/roteiro-de-reproducao.md](estudo-classificacao-demonstrativa-2026-11-07/roteiro-de-reproducao.md) |
| Inventário das capacidades | [estudo-classificacao-demonstrativa-2026-11-07/inventario.md](estudo-classificacao-demonstrativa-2026-11-07/inventario.md) |
| Diário de configuração e execução | [estudo-classificacao-demonstrativa-2026-11-07/diario.md](estudo-classificacao-demonstrativa-2026-11-07/diario.md) |
| Elenco, notas e scripts | [estudo-classificacao-demonstrativa-2026-11-07/reproducao/](estudo-classificacao-demonstrativa-2026-11-07/reproducao/) |

**Como foi feito.** O Edital foi configurado **à mão, pela interface**, como faria quem conhece o edital e
não o GPS. Cada salvamento ficou registrado no diário. A execução usou duas vias:

- os gestos que mais dizem sobre a experiência foram praticados **pela tela**: emitir a ordem, publicar a
  preliminar, julgar o recurso, emitir a ordem sucessora, convocar, conferir documentos, registrar
  desfechos e emitir a apuração com reversão;
- a carga de dados (18 inscrições, cerca de 60 notas, consolidações) rodou por script, chamando **os
  mesmos comandos** que as telas chamam, cada um com o relógio no dia do ato.

O mesmo script reproduz o certame inteiro num banco vazio. **A reprodução foi conferida: o banco
recriado do zero é idêntico ao do estudo em todas as posições, notas, apurações e convocações.**

---

## 1. Resumo

**O que o GPS executa (A).** Tudo o que este caso pediu existe e funcionou de ponta a ponta, sem
contornar regra nenhuma:

- quatro Etapas encadeadas: uma decisória eliminatória, uma só classificatória e duas eliminatórias com
  nota mínima;
- dois marcos de classificação, um intermediário e um final, com média ponderada, arredondamento e três
  critérios de desempate;
- um corte que decide quem vai à Etapa seguinte;
- três listas de concorrência (ampla, PcD e PPI), com concorrência simultânea;
- preliminar e definitiva, um recurso deferido com correção de nota, a ordem sucessora e um recurso
  indeferido;
- a apuração das vagas e a convocação com documentos, com conferência e reapresentação;
- duas desistências, a reversão da vaga PcD para a ampla e uma nova convocação.

Ao fim, as 6 vagas estão ocupadas por aceite: 5 na ampla (4 publicadas e 1 revertida) e 1 na PPI.

**O que não existe.** Quatro capacidades estão ausentes:

- nota por critério dentro de uma Etapa: a nota da Etapa é um número só, e o barema fica fora do sistema;
- combinação de duas avaliações da mesma Etapa;
- peso diferente da mesma Etapa em marcos diferentes;
- simulação com as notas reais.

**O operador entende (B)?** A resposta depende do ponto do processo.

- **Configurar** não é mais o ciclo "salva, erra, corrige": foram 12 salvamentos, 1 recusa (de
  preenchimento) e nenhuma volta por erro de regra. O risco mudou de lugar. Uma decisão com consequência
  grande foi **aceita em silêncio**, e a Revisão a descreve de um jeito que não é o que o motor faz:
  - o corte fixo de 8 vale **para cada lista**;
  - a Revisão diz "os 8 primeiros";
  - 12 pessoas foram à Entrevista.
- **Executar** é bem guiado nos atos. A tela diz o que o ato grava, recusa o que não pode e propõe o
  próximo passo. Mas **as telas não explicam por que alguém ficou em cada posição**: não mostram notas por
  Etapa nem o critério que separou um empate. A explicação existe em dois lugares escondidos:
  - no ato emitido, entre 34 identificadores internos;
  - no simulador, mas para candidatos fictícios.

  A candidata que perdeu a 6ª posição no desempate, Sofia (C07), vê "7º lugar" e nada mais.
- **O simulador** é uma boa ferramenta para entender **a regra**, e não para prever **o efeito nos
  candidatos**. No experimento deste estudo, inverter dois critérios de desempate:
  - para o simulador, "não mudou para ninguém";
  - com as notas reais, tiraria da faixa o candidato que acabou matriculado.

As oportunidades de melhoria estão na seção 13. As decisões de governança estão na seção 14 e ficam
**com a equipe**: nada aqui virou spec.

---

## 2. Inventário resumido

O inventário completo está em [inventario.md](estudo-classificacao-demonstrativa-2026-11-07/inventario.md),
com caminhos de código. A tabela abaixo diz o que o caso precisou saber antes de escolher o cenário.

| Recurso | O que representa | Como se configura | Restrições que pesaram no desenho | Estado |
|---|---|---|---|---|
| Etapa de Avaliação | Um momento do certame, igual para todos os Perfis | Composição › Etapas: nome, Evento, forma, mínima, máxima, peso, caráter, avaliações por inscrição | **Uma nota por Etapa.** Não há barema nem nota por critério. Mais de uma avaliação trava a Etapa ("regra de combinação ausente") | Implementado |
| Forma decisória | Etapa sem nota (Deferido/Indeferido) | "Com decisão, sem nota" + rótulos | Precisa ser eliminatória; sem isso, não tem Resultado | Implementado |
| Caráter eliminatório / classificatório | Duas caixas independentes | Etapas | Nota mínima só elimina se a Etapa for eliminatória. Nota igual à mínima habilita | Implementado |
| Peso | Quanto a nota da Etapa pesa | Na **Etapa**, não no marco | O mesmo peso vale em todos os marcos | Implementado |
| Dependência entre Etapas | Quem chega a cada Etapa | **Implícita na ordem**, sem campo | Quem é eliminado em qualquer Etapa anterior sai. A **imediatamente anterior** precisa habilitar. Não há Etapa paralela nem condicional | Implementado |
| Marco classificatório | Uma ordem: quais Etapas entram, como combinar, desempate, corte, recurso | Composição › Classificação, por Perfil | O marco enumera só Etapas classificatórias. A decisória enumerada é "porta" e não soma | Implementado |
| Combinação | Soma ou média ponderada, normalização, arredondamento (0–4 casas; meio para cima, meio para par, truncar) | Cartão do marco | Arredonda **uma vez**, no fim. Sem nota numa Etapa enumerada, a pessoa fica sem posição (nunca vale zero) | Implementado |
| Desempate | Critérios em ordem: maior nota numa Etapa; maior ou menor valor de um fato declarado | Cartão do marco | **Só esses três tipos.** Idade entra como fato "data de nascimento" que o candidato declara. O empate que sobra não se resolve: a posição fica dividida (1, 1, 3) | Implementado |
| Corte | Quem avança: alvo fixo ou do quadro, suplentes, empate na última posição, Etapa governada, faixa seguinte | Cartão do marco | O alvo fixo vale **para cada lista**. O corte não muda a ordem, só seleciona dela | Implementado |
| Modalidades e quadro | Ampla, reservadas (livres) e vagas por lista | Perfis | A ampla é o universo inteiro, com cotistas; cada reservada tem só os autodeclarados | Implementado |
| Concorrência simultânea | O cotista dentro das vagas da ampla ocupa pela ampla | Automática | A fila da ampla não exclui quem aceitou a reservada (achado do estudo do sorteio) | Implementado, com lacuna |
| Reversão | Vaga reservada não preenchida passa à ampla | Perfis: "só quando esgota" / "a quantidade que ficou sem preencher" | Lista reservada **sem inscrito** não reverte (achado registrado) | Implementado |
| Prévia (simulador) | O motor oficial sobre 20 candidatos **fictícios** | Botão no cartão do marco | Não usa notas reais. Calcula um marco só. Não simula convocação | Implementado (094/095) |
| Resultados | Preliminar e definitiva, **por marco e por lista** | Ato emitido › Publicar | Não existe publicação de uma Etapa isolada. A definitiva espera a janela de recurso | Implementado |
| Recursos | Titular recorre de uma publicação ou de um Resultado | Portal; gestão: admitir, instruir, julgar | Quatro espécies de decisão. Não se reforma para pior | Implementado |
| Ocupação e convocação | Apuração por lista, chamadas, desfechos, documentos | Marco › Ocupação, Convocação | "Ocupada" conta o titular antes de ele responder | Implementado |

---

## 3. O caso

**Processo Seletivo Demonstrativo — Especialização em Docência (DEMO)**, Edital 900/2026.

| Item | Configuração |
|---|---|
| Perfil | ESP-DOC — Especialização em Docência para a Educação Profissional, turma DEMO. 6 vagas imediatas. Cadastro de reserva limitado a 6. Convocação por mensagem individual |
| Modalidades | AC (a ampla); PcD (5 %); PPI (20 %). Fundamento: norma fictícia DEMO |
| Quadro de vagas | Ampla 4 · PcD 1 · PPI 1 |
| Reversão | "A quantidade que ficou sem preencher" (`ON_BALANCE`) |
| Fato declarado | Data de nascimento: o candidato informa na inscrição, e o desempate a lê |
| Documentos | Na inscrição: Diploma e Currículo Lattes. Na convocação: Identidade (todos) e Laudo (só PcD) |

**As Etapas, na ordem que o GPS usa para decidir quem chega a cada uma:**

| # | Etapa | Forma | Nota | Mínima | Peso | Caráter |
|---|---|---|---|---|---|---|
| 1 | Análise dos requisitos | decisória (Deferido/Indeferido) | — | — | — | eliminatória |
| 2 | Análise do currículo | pontuada | 0–100 | — | 1 | só classificatória |
| 3 | Prova escrita | pontuada | 0–100 | 60 | 3 | eliminatória e classificatória |
| 4 | Entrevista | pontuada | 0–100 | 60 | 2 | eliminatória e classificatória |

**Os dois marcos:**

| | Marco 1 — Classificação para a entrevista | Marco 2 — Classificação final |
|---|---|---|
| Etapas que entram | Currículo (1) e Prova (3) | Currículo (1), Prova (3) e Entrevista (2) |
| Combinação | média ponderada, 2 casas, meio para cima | média ponderada, 2 casas, meio para cima |
| Fórmula | `(CUR + 3·PRO) / 4` | `(CUR + 3·PRO + 2·ENT) / 6` |
| Desempate | 1º maior nota na Prova · 2º data de nascimento mais antiga | 1º maior nota na Entrevista · 2º maior nota na Prova · 3º data de nascimento mais antiga |
| Corte | alvo **fixo 8**, sem suplentes, empate admite excedente | alvo **do quadro** + 2 suplentes, empate admite excedente |
| Etapa que o corte alimenta | **Entrevista** | nenhuma (fim da jornada) |
| Faixa seguinte | não admite | admite |
| Recurso | 3 dias corridos | 3 dias corridos |

**A estrutura de dependências, como o GPS a executa:**

```text
 inscrição ──► [1] Requisitos (decisória, elimina) ── Indeferido: sai de tudo
                   │ Deferido
                   ▼
               [2] Currículo (nota, não elimina) ──────────────┐ peso 1
                   │ todos seguem                              │
                   ▼                                           │
               [3] Prova (nota, mín. 60, elimina) ─────────────┤ peso 3
                   │ < 60 ou ausente: sai                      │
                   ▼                                           ▼
             ┌─ MARCO 1: (CUR + 3·PRO)/4 ── ordem por lista (ampla, PcD, PPI)
             │     corte FIXO 8 em CADA lista ── governa a Entrevista
             │     quem não entra em nenhuma faixa: para aqui
             ▼
               [4] Entrevista (nota, mín. 60, elimina) ─── só quem está numa faixa do marco 1
                   │ < 60 ou ausente: sai
                   ▼
               MARCO 2: (CUR + 3·PRO + 2·ENT)/6 ── ordem por lista
                   corte = vagas da lista + 2 suplentes ── não governa Etapa
                   ▼
               Ocupação (por lista; concorrência simultânea; reversão) ──► Convocação ──► Aceite
```

Três regras moram **fora** de qualquer campo e decidem quem chega a cada Etapa:

1. quem é **eliminado em qualquer Etapa anterior** sai de tudo o que vem depois;
2. a Etapa **imediatamente anterior** precisa ter **habilitado** a pessoa;
3. o **corte** do marco 1 restringe a Entrevista a quem está numa das três faixas.

Por isso o Currículo (só classificatório) foi posto **antes** da Prova. Se viesse depois, quem fosse
eliminado na Prova nem apareceria na ordem do marco 1, porque o universo de um marco é quem participa da
última Etapa que ele enumera.

---

## 4. A configuração, à mão (seção 6 do pedido)

O diário completo está em [diario.md](estudo-classificacao-demonstrativa-2026-11-07/diario.md), itens
C01–C12. O percurso:

| # | O que se tentou decidir | Onde | O que aconteceu |
|---|---|---|---|
| 1 | Criar o processo | Gestor › Novo Processo Seletivo | 1 tentativa. O Elaborador não tem o botão, e nada lhe diz quem cria |
| 2 | A oferta (vagas, modalidades, quadro) | Perfis de Vaga | 2 salvamentos. Recusa **"quadro soma 8 e o Perfil declara 6"**, porque a linha geral nasce com o total (6). Os seletores "qual é a ampla" e "reversão" **só aparecem depois do 1º salvamento** |
| 3 | O fato que o desempate consome | Perfis › Fatos | Ajuda curta e certa ("idade sai de data") |
| 4 | O cronograma | Cronograma | 1 salvamento, 1 aviso legítimo (Evento em 2027). O período de inscrições **não** se marca aqui (é na 6ª etapa) |
| 5 | Etapas, notas, mínimas, pesos, caráter | Etapas de Avaliação | 1 salvamento, 1 aviso (Etapa sem Evento: corrige-se em **outra** etapa do assistente) |
| 6 | Os marcos, a combinação, o desempate, o corte | Classificação | 2 salvamentos, sem pendência. Cada marco novo **nasce como "Classificação final"**, com código igual ao do Perfil, corte pelo quadro e "não governa Etapa": para o marco intermediário é preciso desfazer 4 padrões |
| 7 | Período, teto e documentos | Inscrição | 1 salvamento |
| 8 | Conferir tudo | Revisão | Só avisos. A Revisão imprime **a frase normativa** de cada decisão (seção 4.1) |
| 9 | Submeter, homologar, publicar | atos | Três papéis. A publicação parou por falta de **autoridade signatária**, que só o Gestor cadastra |

**Total:** 12 salvamentos com efeito, **1 recusa** (de preenchimento) e nenhuma configuração errada
recusada. Uma configuração ambígua foi aceita sem aviso (4.1).

### 4.1 As respostas às 12 perguntas da configuração

1. **Como se cria:** o Gestor cria o Processo junto com o 1º Edital; o Elaborador compõe em 9 etapas.
2. **A oferta:** Perfis de Vaga. Vagas imediatas, cadastro de reserva, modalidades, qual é a ampla,
   quadro por lista e reversão.
3. **A forma de classificação:** por marco, no cartão. "Pela pontuação combinada das Etapas" ou "Por
   sorteio".
4. **As Etapas:** Etapas de Avaliação. Valem para todos os Perfis.
5. **Os critérios de cada Etapa:** **não existem dentro do GPS**. A Etapa recebe uma nota só, e o barema
   fica no papel da banca. "Critério" no GPS é **critério de desempate**.
6. **Pesos e notas:** peso, nota máxima e nota mínima ficam na Etapa. O marco escolhe as Etapas e a
   operação (soma ou média ponderada, normalização, arredondamento).
7. **Mínimos:** "Nota mínima" na Etapa. **Só elimina se a Etapa for eliminatória.** Não há nota final
   mínima no marco.
8. **Dependências:** pela **ordem** das Etapas (regras 1 e 2 da seção 3) e pela "Etapa que o corte
   alimenta" (regra 3). Não há campo "Etapa B depende de A".
9. **Desempate:** critérios em ordem no cartão do marco, cada um com "quando o valor não existe".
10. **Classificação × quadro de vagas:** o corte "Quantas vagas o quadro publicar no recorte" e a
    apuração da ocupação leem o quadro de cada lista.
11. **Cronograma:** o Evento se vincula à Etapa só para datas. **Nada no cronograma comanda a
    classificação**: o próprio aviso diz "O sistema não relaciona o Cronograma aos marcos".
12. **Verificar se a configuração é válida:** a Revisão ("O que falta para submeter" e "O que será
    congelado na submissão") e o simulador.

**O ciclo "configura, salva, recebe erro, corrige" persiste?** Não, neste caso. As mensagens nomeiam o
número e o lugar ("o quadro soma 8 e o Perfil declara 6 — excesso de 2"). O problema que sobra é o
oposto: **o que passa sem erro**. A frase da Revisão para o corte do marco 1 é:

> Corte: Passam para a Etapa "Entrevista" os 8 (oito) primeiros classificados.

O motor aplica 8 em **cada** lista (ampla, PcD e PPI). A prévia mostrava isso em 09/11, sob a forma "14
candidatos poderiam participar"; a Revisão não. O marco 2, que usa o alvo do quadro, diz "de cada lista
de concorrência".

---

## 5. As correlações entre as Etapas (seção 7 do pedido)

| Pergunta | O que o GPS faz | Onde se vê no caso |
|---|---|---|
| A 2ª Etapa depende da aprovação na 1ª? | Sim. Quem é eliminado numa Etapa anterior sai de tudo, e a imediatamente anterior precisa habilitar | C05 (Indeferida nos Requisitos) não recebe currículo, prova nem posição |
| Uma Etapa pode ser só classificatória? | Sim (Currículo). Ela sempre habilita e só soma | C03 tem o melhor currículo (95) e não é salva por ele |
| A nota mínima elimina ou só impede progressão? | **Elimina**, se a Etapa for eliminatória: a pessoa sai de tudo. Numa Etapa não eliminatória, a mínima **não faz nada** | C03 (55 < 60) e C14 (52) sem posição no marco 1; C15 (Entrevista 55) sem posição no marco 2 |
| O resultado compõe uma nota acumulada? | Sim, no marco: média ponderada das Etapas enumeradas | Fórmulas da seção 3 |
| Pesos diferentes? | Sim, por Etapa (1, 3, 2), mas o **mesmo** peso em todos os marcos | Prova pesa 3 nos dois marcos |
| Ausentes? | A presidência registra uma **Ocorrência**: o Resultado é "eliminada", com o motivo digitado. Nunca vira zero | C04 (Prova) e C18 (Entrevista) |
| Nota não informada? | Sem conclusão não há Resultado. Num marco, sem nota numa Etapa enumerada a pessoa fica sem posição ("Sem pontuação nas Etapas enumeradas") | não ocorreu |
| O que acontece quando uma nota é corrigida? | O recurso deferido cria um **Resultado sucessor** (o antigo fica legível). A ordem emitida fica **obsoleta**, a publicação e o corte travam até a ordem sucessora | C10: Prova 68 → 76 |
| Como evitar usar resultado não definitivo? | A **publicação definitiva** é recusada com recurso pendente ou com a janela aberta. Mas **cortar e seguir não exige a definitiva**: a tela propõe "Emitir o corte" logo depois da ordem | seção 10 |
| Como a mudança numa Etapa afeta as dependentes? | Ordem obsoleta, depois corte obsoleto, depois a Etapa governada bloqueada (distribuir, concluir e consolidar recusam). Quem é reabilitado antes do marco só alcança o corte com a ordem sucessora (achado aberto) | C10 entra na faixa só depois da sucessora |

---

## 6. O elenco e a tabela completa (seção 8 do pedido)

Notas (0–100) e resultados como o GPS os gravou, lidos do banco do estudo depois da execução. "s/p" quer
dizer sem posição. As posições "AMPLA:n" são na lista da ampla, que inclui os cotistas.

| Cód. | Nome (fictício) | Mod. | Req. | Cur. | Prova | Marco 1 | Posição M1 | Entrevista? | Entr. | Marco 2 | Posição M2 | Faixa M2 | Desfecho |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | Helena Prado | AC | Def. | 90 | 92 | 91,50 | AMPLA 1 | ampla | 95 | 92,67 | AMPLA 1 | sim | **Aceite** (ampla) |
| C02 | Bruno Taveira | AC | Def. | 80 | 85 | 83,75 | AMPLA 3 | ampla | 88 | 85,17 | AMPLA 3 | sim | **Desistência** |
| C03 | Lívia Montes | AC | Def. | **95** | **55 ✗** | — | s/p (nota < 60) | — | — | — | — | — | eliminada na Prova |
| C04 | Otávio Rangel | AC | Def. | 70 | ausente ✗ | — | s/p (ausência) | — | — | — | — | — | eliminado na Prova |
| C05 | Marina Couto | AC | **Indef. ✗** | — | — | — | — | — | — | — | — | — | eliminada nos Requisitos |
| C06 | Rafael Quintão | AC | Def. | 78 | 76 | 76,50 | AMPLA 5 ᵃ | ampla | 80 | 77,67 | AMPLA 4 | sim | **Aceite** (doc. reapresentado) |
| C07 | Sofia Arruda | AC | Def. | 66 | 80 | 76,50 | AMPLA 4 ᵃ | ampla | 74 | 75,67 | AMPLA 7 ᶜ | não | aguarda (1ª fora da faixa) |
| C08 | Caio Bettencourt | AC | Def. | 72 | 74 | 73,50 | AMPLA 6 ᵇ | ampla | 80 | 75,67 | AMPLA 6 ᶜ | sim (suplente) | **Aceite** (vaga de C02) |
| C09 | Diana Ferraz | AC | Def. | 72 | 74 | 73,50 | AMPLA 7 ᵇ | ampla | 82 | 76,33 | AMPLA 5 | sim (suplente) | **Aceite** (vaga revertida) |
| C10 | Gustavo Lemos | AC | Def. | 60 | 68 → **76** ᵈ | 72,00 | AMPLA 8 (era 11) | ampla | 70 | 71,33 | AMPLA 9 | não | — |
| C11 | Patrícia Nogueira | AC | Def. | 68 | 70 | 69,50 | AMPLA 10 | **não** | — | — | — | — | para no marco 1 |
| C12 | Renato Sales | AC | Def. | 50 | 62 | 59,00 | AMPLA 14 | **não** | — | — | — | — | para no marco 1 |
| C13 | Elisa Viana | PcD | Def. | 64 | 72 | 70,00 | AMPLA 9 · PcD 1 | **pela PcD** | 76 | 72,00 | AMPLA 8 · PcD 1 | PcD | **Desistência**, e daí a reversão |
| C14 | Fábio Guerra | PcD | Def. | 75 | **52 ✗** | — | s/p | — | — | — | — | — | eliminado na Prova |
| C15 | Iara Batista | PcD | Def. | 58 | 66 | 64,00 | AMPLA 12 · PcD 2 | pela PcD | **55 ✗** | — | s/p | — | eliminada na Entrevista |
| C16 | João Benedito | PPI | Def. | 85 | 88 | 87,25 | AMPLA 2 · PPI 1 | ampla e PPI | 84 | 86,17 | AMPLA 2 · PPI 1 | ampla e PPI | **Aceite pela ampla** (concorrência simultânea) |
| C17 | Kátia Moura | PPI | Def. | 62 | 70 | 68,00 | AMPLA 11 · PPI 2 | pela PPI | 72 | 69,33 | AMPLA 10 · PPI 2 | PPI | **Aceite** (vaga PPI) |
| C18 | Luan Tavares | PPI | Def. | 55 | 64 | 61,75 | AMPLA 13 · PPI 3 | pela PPI | ausente ✗ | — | s/p | — | eliminado na Entrevista |

Notas da tabela:

- **ᵃ** empate em 76,50 no marco 1, separado pelo 1º critério (maior nota na Prova: 80 > 76).
- **ᵇ** empate em 73,50 e na Prova (74 = 74), separado pelo 2º critério (data de nascimento mais antiga:
  05/06/1980 < 01/12/1992).
- **ᶜ** empate em 75,67 no marco 2, separado pelo 1º critério (maior nota na Entrevista: 80 > 74).
- **ᵈ** correção fixada no recurso REC-2026-Y5Q24ANH.

As posições do marco 1 são as da ordem sucessora, já com a correção; na preliminar, C10 era 11º e C13
era 8º.

**Quem foi à Entrevista (12):** os 8 da faixa da ampla (C01, C16, C02, C07, C06, C08, C09, C10), mais
C13 e C15 pela PcD, mais C17 e C18 pela PPI. C16 está em duas faixas e conta uma vez.

### 6.1 O cálculo completo de seis situações

**C01 — desempenho alto em tudo.**
Marco 1: `(90 + 3·92) / 4 = 366 / 4 = 91,50` → 1º.
Marco 2: `(90 + 3·92 + 2·95) / 6 = 556 / 6 = 92,666… → 92,67` (meio para cima, 2 casas) → 1º. Titular
da ampla, aceite.

**C03 — a melhor nota de currículo, eliminada por uma condição.**
O Currículo (95) não elimina e sempre habilita. A Prova (55) é eliminatória com mínima 60: 55 < 60 dá
"pontuação inferior à nota mínima da Etapa (55,0000 < 60,0000)". O marco 1 a lista "sem posição", com
esse motivo. Se o Currículo fosse classificatório e entrasse sozinho, ela seria 1ª; a nota mínima da
Prova a tira de tudo.

**C07 × C06 — empate resolvido pelo 1º critério (marco 1).**
C07: `(66 + 3·80) / 4 = 306 / 4 = 76,50`. C06: `(78 + 3·76) / 4 = 306 / 4 = 76,50`.
1º critério (maior Prova): 80 > 76 → C07 4ª, C06 5º.

**C08 × C09 — o 1º critério não separa; o 2º separa (marco 1).**
Os dois: `(72 + 3·74) / 4 = 294 / 4 = 73,50`. A Prova empata (74 = 74). A data de nascimento separa:
05/06/1980 é mais antiga que 01/12/1992 → C08 6º, C09 7º.

**C08 × C07 — o desempate que decide uma vaga (marco 2).**
C08: `(72 + 222 + 160) / 6 = 454 / 6 = 75,67`. C07: `(66 + 240 + 148) / 6 = 454 / 6 = 75,67`.
1º critério (maior Entrevista): 80 > 74 → **C08 6º**, o último da faixa (4 vagas + 2 suplentes); **C07
7ª**, fora. C08 acabou matriculado. Com a Prova como 1º critério, a ordem se inverteria (80 > 74 para
C07): ver seção 8.

**C16 — cotista que ocupa pela ampla.**
Marco 2: `(85 + 3·88 + 2·84) / 6 = 517 / 6 = 86,17`. É 2º na ampla e 1º na PPI. Dentro das 4 vagas da
ampla, **ocupa pela ampla**. A apuração da PPI o exclui, e a vaga PPI vai a C17 (69,33, 10º na ampla).

**C10 — o recurso que muda a progressão.**
Antes: `(60 + 3·68) / 4 = 264 / 4 = 66,00`, 11º, fora da faixa de 8. Depois da correção:
`(60 + 3·76) / 4 = 288 / 4 = 72,00`, 8º, dentro. C13, que era 8ª, passa a 9ª na ampla, mas **continua indo
à Entrevista pela lista PcD**. Ninguém perde a Entrevista com a correção, porque C13 tem outra faixa.

---

## 7. A execução, etapa por etapa (seção 10 do pedido)

| Data | Ato | Quem | Como | O que o GPS calculou e mostrou |
|---|---|---|---|---|
| 09/11 | Edital publicado | Elaborador, Homologador, Publicador | tela | 3 papéis; autoridade cadastrada pelo Gestor |
| 16–27/11 | 18 inscrições, com Diploma, Currículo e data de nascimento | candidatos | script (serviços do portal) | O valor declarado congela no envio |
| 28/11 | comissão (presidente + 2 avaliadores), alocação nas 4 Etapas | Gestor | script | — |
| 30/11–01/12 | Requisitos: 17 Deferidos, 1 Indeferido; consolidação | avaliadora, presidência | script | C05 eliminada, com o motivo |
| 02–03/12 | Currículo de 17; consolidação | avaliador | script | todos habilitados ("a Etapa não tem caráter eliminatório") |
| 05/12 | Ocorrência: C04 ausente na Prova | presidência | script | Resultado "eliminada", motivo digitado |
| 06–07/12 | Prova de 16; consolidação | avaliadora | script | C03 e C14 eliminados (< 60) |
| **09/12** | **Ordem do marco 1, ampla** | presidência | **tela** | proposta = conferir.py; conferência; ato |
| 09/12 | ordens PcD e PPI | presidência | script | — |
| **09/12** | **Preliminar da ampla** | Publicador | **tela** | prévia da lista pública |
| 09/12 | preliminares PcD e PPI | Publicador | script | — |
| 10/12 | C10 recorre ("questões 3 e 4 somam 76") | candidato | script (serviço do portal) | "Dentro do prazo" |
| **13/12** | **Admissão e correção fixada (68 → 76)** | Julgador | **tela** | "Recurso deferido — o resultado foi corrigido" |
| **13/12** | **Ordem sucessora da ampla, com motivo** | presidência | **tela** | "O ato vigente está obsoleto… Mudanças posição a posição" |
| 14/12 | Definitivas do marco 1 (3 listas) | Publicador | script | a sucessora vai direto à definitiva |
| 14/12 | Cortes do marco 1 (3 listas) | presidência | script | 8 + 2 + 3 → 12 na Entrevista |
| 17/12 | Ocorrência: C18 ausente na Entrevista | presidência | script | — |
| 18–19/12 | Entrevista de 11; consolidação | avaliador | script | C15 eliminada (55) |
| 21/12 | Ordens do marco 2 e preliminares | presidência, Publicador | script | = conferir.py |
| 22–26/12 | C07 recorre da Entrevista; indeferido | candidata, Julgador | script | — |
| 28/12 | Definitivas e cortes do marco 2 | Publicador, presidência | script | ampla 6 na faixa; PcD 1; PPI 2 |
| 29/12 | Apuração das 3 listas | presidência | script | ampla 4/4/4; PcD 1/1/1; PPI 1/1/1 (C16 fora da PPI) |
| **04/01** | **Convocação dos titulares** (ampla 4, PcD 1, PPI 1) | presidência | **tela** | lote com conferência do texto ao candidato |
| 05/01 | Identidade apresentada (C01, C16, C06, C17) | candidatos | script | — |
| **05/01** | **Conferência**: C01, C16 Conforme; C06 Pendente (ilegível) | presidência | **tela** | Conforme exige ter aberto a versão |
| **05/01** | **Desfechos**: aceites C01, C16; desistências C02 e C13 | presidência | **tela** | ampla: "apuração seguinte emitida no mesmo ato"; PcD: "não saiu: moveria vaga para a ampla" |
| **05/01** | **Apuração PcD com motivo**, depois a da ampla | presidência | **tela** | "Reversão de cota: 1 vaga… para a ampla"; ampla 4 publicadas / 5 efetivas |
| **05/01** | **Convocação de C09 (titular) e C08 (vaga que vagou)** | presidência | **tela** | — |
| 06/01 | C06 reapresenta; C09 e C08 apresentam | candidatos | script | — |
| **06/01** | **Conferências e aceites** de C06, C09, C08, C17 | presidência | **tela** | final: ampla 4/5/5/0; PcD 1/0/0/0; PPI 1/1/1/0 |

As telas de cada momento estão no guia. As visões do candidato foram capturadas para C03 (eliminada),
C07 (fora da faixa por desempate), C10 (recorrente) e C08 (convocado).

---

## 8. O simulador (seção 9 do pedido)

| Pergunta | Resposta, medida neste caso |
|---|---|
| Quando se usa? | Na etapa Classificação da composição, pelo botão "Simular classificação" do cartão do marco. **Funciona também no Edital publicado**: a tela abre com os controles habilitados e sem "Salvar", e nada é gravado |
| Que dados recebe? | O que está **digitado** no cartão (mesmo sem salvar) e o que está gravado nas outras etapas: pesos, fatos, quadro, reversão. Os candidatos são **20 fictícios**, numa "população estável" ou num de 11 casos-limite |
| O que calcula? | A ordem e o corte de **um** marco, por lista, com o **motor oficial** (a equivalência é testada), e uma rodada de ocupação "sob hipóteses" |
| O que mostra? | Quantos avançam por lista, quem chega à Etapa seguinte (a união das faixas), o detalhe de cada empate **critério a critério** ("Separou" / "Não separou: valores iguais") e a classificação completa com notas por Etapa |
| Explica o efeito de cada Etapa? | Mostra a jornada: Etapas e marcos com estado "simulado", "não calculado aqui", "indeterminado". **Não decompõe o peso**: cada candidato fictício tem a mesma nota em todas as Etapas (95/95/95), então o peso nunca muda nada na simulação |
| Verifica eliminações, pesos e desempates? | Desempates, muito bem. Eliminação, só **plantada** ("eliminado na Etapa do marco"), não calculada pela nota mínima. Pesos, não (ver acima) |
| Ajuda a achar configuração incoerente? | Sim, no caso que importou: em 09/11, antes de publicar, mostrava "PCD: 9 autodeclarados; 8 avançariam" e "14 candidatos poderiam participar" da Entrevista, revelando o corte fixo por lista. Mas também emite um alerta de vagas ("empate na 4ª pararia a apuração") para o marco intermediário, que nunca apura vaga |
| Corresponde ao processamento efetivo? | Sim, para a mesma entrada: é o mesmo motor. A entrada é que não é a real |
| O que não cobre? | Notas reais; encadeamento de marcos ("Classificação final: indeterminado"); convocação, desistência e faixa seguinte; recurso; Retificação. A própria tela o diz, num bloco claro |

**O experimento pedido: alterar um critério e ver o efeito, sem tocar nos atos.** No Edital já
publicado e executado, foram feitas duas alterações, sem salvar:

1. **Inverter os critérios 1 e 2 do marco final** (Prova antes da Entrevista).
   - O simulador respondeu: **"Com a última alteração, a consequência não mudou para ninguém."**
   - Com as notas reais (o mesmo motor, por `conferir.py`): **C07 passa a 6ª e entra na faixa; C08 cai
     para 7º e sai**. C08 foi quem acabou convocado e matriculado.
2. **Alvo do marco 1 de 8 para 6.** O simulador respondeu bem: "Avançam: 9 → 6. Pessoas com deficiência
   (PCD): avançam 8 → 6. Poderiam participar da Etapa seguinte: 14 → 10. Mudaram de situação: Gabriela,
   Heitor e Íris".

**Avaliação:** o simulador é **ferramenta de compreensão da regra**: mostra o que um critério, um alvo ou
um desfecho de empate faz com uma população pensada para expor esses efeitos. **Não é ferramenta de
compreensão do caso**: não responde "o que acontece com estas pessoas se eu mudar isto", nem depois de
todas as notas existirem.

Um risco menor: os nomes fictícios (Bruno, Elisa, Fábio, Sofia…) coincidem com os de candidatos reais
deste caso.

---

## 9. Modalidades de concorrência: o que muda em relação ao sorteio (seção 11 do pedido)

| Ponto | Classificação (este caso) | Sorteio (Edital 35) |
|---|---|---|
| De onde vem a ordem | Notas das Etapas, combinadas e desempatadas pelos critérios publicados | Chave sorteada a partir da semente pública |
| Mesmos critérios para todas as listas? | Sim: a ordem de cada lista é o mesmo cálculo sobre um universo diferente | Um sorteio por lista |
| Lista da ampla | **Todos** os inscritos do Perfil, cotistas inclusive (C16, C13, C17 aparecem nela) | Idem |
| Lista reservada | Só os autodeclarados daquela modalidade | Idem |
| Empate | Possível e frequente; resolvido pelos critérios, e o que sobra fica com posição dividida | Praticamente impossível |
| Corte | Pode **governar uma Etapa** (marco 1 → Entrevista); o alvo fixo vale **por lista** | Não governava Etapa no 35 |
| Concorrência simultânea | Na **apuração** (C16 ocupa pela ampla; a PPI vai a C17), não no corte: o corte da PPI lista C16 como "progride" | Idem; foi o achado central do estudo do sorteio |
| Dupla alocação | A fila da reservada exclui quem ocupa a ampla. A fila da ampla **não** exclui quem aceitou a reservada (lacuna do estudo do sorteio; não exercitada aqui) | Idem |
| Reserva não preenchida | `ON_BALANCE`: a desistência da única PcD **não** emite a apuração seguinte sozinha ("moveria vaga para a ampla… emita-a na ocupação"). Emitida à mão, ela gera o movimento, e a ampla passa a 5 efetivas | Não exercitado no 35 |

---

## 10. Resultados, recursos e correções (seção 12 do pedido)

- **Quando há resultado preliminar:** quando a presidência emite a ordem de um marco e o Publicador a
  divulga como preliminar. **Não existe resultado de Etapa publicado sozinho.** O candidato vê o Resultado
  de cada Etapa ("Prova escrita — Habilitada · pontuação 80") só quando um marco que a enumera foi
  publicado.
- **Como é publicado:** por **ato e por lista**. Cada marco deste caso teve 3 preliminares e 3
  definitivas. O público vê posição, nome, protocolo, modalidade e pontuação de quem tem posição; não vê
  notas por Etapa nem valores de desempate.
- **Como o candidato consulta:** Portal › Acompanhar. Mostra a situação ("Eliminado", "Aguardando
  chamada"), o "por quê", a posição em cada lista e marco, e o Resultado de cada Etapa com o motivo.
- **O recurso:** só o titular interpõe, pelo portal, dentro da janela do marco (3 dias corridos a partir
  da 1ª publicação). O Julgador:
  - admite (com motivo);
  - **não vê o objeto atacado nem a prova** sem um ato de instrução da presidência ou do Gestor;
  - julga numa de 4 espécies. Para "fixar a correção", escolhe a Etapa e digita a nota.
- **Como a correção se registra:** um Resultado sucessor, com origem RECURSO. O anterior permanece.
- **Como afeta o que vem depois:** a ordem fica obsoleta, a presidência emite a sucessora (o motivo é
  obrigatório) e a publicação e o corte travam até lá. **A sucessora foi publicada direto como
  definitiva**: o público nunca viu uma "preliminar corrigida".
- **Quando o resultado é definitivo:** a definitiva é recusada com recurso pendente ou janela aberta.
- **Histórico:** tudo é append-only. Resultados, atos, publicações, decisões e conferências ficam
  legíveis; "Histórico de atos" em cada recorte.

---

## 11. Da classificação final à convocação (seção 13 do pedido)

1. **Ordem final:** o ato do marco 2 em cada lista.
2. **Corte:** vagas da lista + 2 suplentes, sem governar Etapa. É a faixa que a convocação pode alcançar
   primeiro; "Faixa seguinte: admite" permite ir além quando a lista acaba.
3. **Apuração:** cada lista apura as próprias vagas. "Ocupadas" conta os **titulares desde a apuração**,
   antes de qualquer convocação.
4. **Quem pode ser convocado:** a tela da convocação mostra a fila. Os titulares estão "para vaga
   inicial"; os suplentes, "para vaga que vagou".
5. **Convocação:** "Convocar os titulares num ato só". A tela:
   - mostra quem entra e por que o suplente fica de fora;
   - mostra o fundamento que o candidato lerá;
   - oferece o prazo do Cronograma;
   - com complemento, obriga a conferir o texto.

   A lista de documentos é gravada também no lote, depois do #425.
6. **Documentos:** o candidato apresenta pelo portal e a presidência confere.
   - "Conforme" exige ter aberto a versão.
   - "Pendente" exige motivo, que o candidato lê.
   - A reapresentação gera a versão 2, e as duas conferências ficam no histórico.
   - O aceite é recusado enquanto houver documento obrigatório sem "Conforme" ou "Não se aplica".
7. **Desistência na ampla (C02):** o desfecho emite a apuração seguinte no mesmo ato ("1 a ocupar").
8. **Desistência na PcD (C13), a única da lista:** o desfecho **não** emite a apuração. Ela "moveria vaga
   deste recorte para a ampla". A presidência emite a apuração da PcD na tela da Ocupação (com motivo) →
   "Reversão de cota: 1 vaga da lista reservada para a ampla". Depois, a da ampla: 4 publicadas, **5
   efetivas**.
9. **Nova convocação:** com 5 efetivas, **C09 passa a titular** ("para vaga inicial") e **C08 entra "para
   vaga que vagou"** (a de C02). Os dois foram convocados, conferidos e aceitos.
10. **Desfecho administrativo:** as 6 vagas ocupadas por aceite. C07 é a próxima da fila da ampla, fora da
    faixa vigente. Ficaram exercitáveis e não exercitados:
    - a faixa seguinte;
    - o cadastro de reserva;
    - o Requerimento de Matrícula;
    - a formalização;
    - o encerramento.

---

## 12. Matriz de capacidades (entrega C)

**Utilizadas no cenário**

| Recurso | Exercitado? | Resultado | Limitações observadas |
|---|---|---|---|
| Etapa decisória eliminatória (Requisitos) | sim | C05 Indeferida, eliminada de tudo | Sem parecer exigido além do desfavorável |
| Etapa só classificatória (Currículo) | sim | soma no marco, nunca elimina | Uma nota mínima ali seria aceita e inócua, sem aviso |
| Etapa eliminatória com mínima (Prova, Entrevista) | sim | C03, C14, C15 eliminados | Mínima por Etapa apenas; não há nota final mínima |
| Nota máxima | sim | 100 em todas | — |
| Peso por Etapa | sim | 1 / 3 / 2 | Mesmo peso em todos os marcos |
| Média ponderada + arredondamento 2 casas, meio para cima | sim | 92,666… → 92,67 | Formatos de exibição variam (91,5 / 70 / 76,50) |
| Marco intermediário com corte que governa Etapa | sim | 12 à Entrevista | Corte fixo por lista não dito na Revisão |
| Marco final com corte pelo quadro + suplentes | sim | faixas 6 / 1 / 2 | — |
| Desempate por nota de Etapa enumerada | sim | C07 × C06; C08 × C07 | Não aparece na tela de ordenação nem para o candidato |
| Desempate por fato (data, menor valor) | sim | C08 × C09 | O fato é autodeclarado e não verificado |
| Empate admite excedente (`ADMITS_SURPLUS`) | configurado | não acionado (sem empate na fronteira) | — |
| Faixa seguinte "não admite" / "admite" | configurado | não acionado | — |
| Modalidades AC / PcD / PPI e quadro | sim | 4 / 1 / 1 | Seletores só aparecem depois do 1º salvamento |
| Concorrência simultânea | sim | C16 ocupa pela ampla; PPI vai a C17 | As telas não dizem quem ocupa nem por quê |
| Reversão `ON_BALANCE` | sim | 1 vaga PcD → ampla | A apuração precisa ser emitida à mão, em outra tela |
| Fato declarado (nascimento) | sim | lido pelo desempate | — |
| Documentos na inscrição | sim | Diploma, Currículo | Não há vínculo entre requisito e documento (achado anterior) |
| Ocorrência (ausência) | sim | C04, C18 | — |
| Ordem por lista, preliminar e definitiva | sim | 12 publicações | A sucessora foi direto à definitiva |
| Recurso com correção fixada | sim | C10: 68 → 76, ordem sucessora | O Julgador não vê o objeto sem instrução |
| Recurso indeferido | sim | C07 | — |
| Ordem obsoleta e sucessão com motivo | sim | "Mudanças posição a posição" | Por protocolo, sem nome e sem efeito no corte |
| Convocação em lote e individual | sim | 6 + 2 convocações | — |
| Documentos na convocação, conferência, reapresentação | sim | C06 versão 2 | — |
| Desfechos aceite / desistência expressa | sim | 6 aceites, 2 desistências | "Próximo" não aponta o suplente |
| Apuração sucessora à mão (reversão) | sim | ampla 4 → 5 efetivas | — |
| Simulador (094/095) | sim, 2 experimentos | regra sim, caso não | ver seção 8 |
| Portal: acompanhamento, resultado público | sim | situação, por quê, Etapas | Sem explicação do desempate |

**Disponíveis e não utilizadas** (existem no código; o caso não precisou delas, ou ficaram para não
complicar):

| Recurso | Por que ficou de fora |
|---|---|
| Soma ponderada; normalização pela soma dos pesos; truncar; meio para par | Uma operação basta para o caso |
| Maior valor de fato (inteiro, como tempo de experiência); "o critério não se aplica" | — |
| Empate estrito (`STRICT`) | Recusa o corte com empate na fronteira; o caso não teve empate ali |
| Desempate por Etapa não enumerada (114) | Exigiria uma Etapa só para desempatar |
| Reavaliação determinada; providência a jusante; recurso não admitido; instrução do recurso | Um deferido e um indeferido bastaram |
| Impedimento de avaliador, rodízio, reabertura de avaliação | Avaliação por script |
| Faixa seguinte (`continuar_corte`); acréscimo de vagas do cadastro de reserva (097) | A fila não se esgotou |
| Reversão "só quando esgota" (`ON_EXHAUSTION`) | Uma espécie basta |
| Indeferimento, não atendimento, inércia, regularização, reclassificação; correção da convocação (120) | Aceite e desistência bastaram |
| Requerimento de Matrícula, formalização (117), exportação de matrículas, avisos (066), Retificação, encerramento | Pós-convocação, fora do núcleo classificatório |

**Ausentes** (o pedido mencionava; o sistema não tem):

| Capacidade | Como o caso contornou |
|---|---|
| Nota por critério dentro de uma Etapa (barema) | A banca soma fora e lança o total |
| Combinação de 2 ou mais avaliações da mesma Etapa | Uma avaliação por Etapa |
| Peso da Etapa diferente por marco | Mesmo peso nos dois marcos |
| Nota final mínima no marco | Só mínimas por Etapa |
| Etapas paralelas ou condicionais | Ordem total; o Currículo foi posto antes da Prova |
| Homologação de inscrição como ato | Etapa decisória "Análise dos requisitos" |
| Ato de "julgar o empate residual" | Não houve empate residual |
| Simulação com as notas reais | Conta à parte com o motor puro (`conferir.py`) |
| Publicar o resultado de uma Etapa sozinha | Publica-se o marco |

---

## 13. Diagnóstico de UX/UI (entrega D)

Ordenado por impacto na pergunta B. Cada item tem a evidência (diário, capturas) e uma sugestão. **São
sugestões, não decisões.**

**Alto**

**D1 — A ordem não explica a posição.**
- *Evidência:* ordenação, prévia de publicação, resultado público e acompanhamento mostram só a nota
  combinada (capturas 18, 22, 25, 62). O "critério que separou" existe no ato emitido (21b), entre 34
  UUIDs e códigos internos (`MAIOR_PONTUACAO_NA_ETAPA · 21d3cfed…`).
- *Efeito:* Sofia (C07) vê "7º lugar · 75,67", sem saber que empatou com o 6º e perdeu pela Entrevista.
- *Sugestão:* levar à ordenação e ao acompanhamento a explicação que o simulador já sabe produzir (a
  tabela "critério a critério"), com as notas por Etapa.

**D2 — O corte fixo vale por lista, e a Revisão diz outra coisa.**
- *Evidência:*
  - a Revisão diz "os 8 primeiros classificados" (13);
  - o motor aplica 8 em cada lista e 12 foram à Entrevista;
  - a tela do corte, aberta na ampla, diz "Fora da faixa" para C13, C15, C17 e C18, que **vão** à
    Entrevista por outra lista (24);
  - não há tela que diga quem vai à Etapa seguinte.
- *Sugestão:* a frase do documento dizer "de cada lista" no alvo fixo, e a tela do corte (ou a Etapa
  governada) mostrar a união das faixas, com a lista por onde cada pessoa chega. Ver também a decisão G1.

**D3 — O simulador não simula o caso.**
- *Evidência:* seção 8, experimento 1 ("não mudou para ninguém", e mudaria a matrícula); notas iguais em
  todas as Etapas escondem o peso.
- *Sugestão:* uma opção "com as notas consolidadas" quando elas existem (só leitura), e uma população
  fictícia com notas diferentes por Etapa.

**Médio**

**D4 — A dependência entre Etapas é implícita.**
- *Evidência:* as setas ↑↓ das Etapas parecem só arrumação. A Revisão não escreve "só os Deferidos fazem
  a Prova". Pôr o Currículo antes da Prova era decisão de regra, e não de ordem visual (seção 3).
- *Sugestão:* não um Gantt. Um **trilho vertical** na Revisão e na etapa Classificação: cada Etapa com o
  conector do que ela faz com quem passa (*elimina*, *só soma*, *porta*, *corta para…*) e cada marco
  entre as Etapas que ele lê. A função `classificacao/domain/jornada.py` já produz essa sequência para a
  prévia.

**D5 — O marco novo nasce como "Classificação final".**
- *Evidência:* o código é igual ao do Perfil, o corte é pelo quadro e "não governa Etapa", inclusive no
  2º marco (C07, C08 do diário).
- *Sugestão:* o 2º marco não herdar o padrão de marco único; o 1º, quando houver Etapa depois dele,
  perguntar se é intermediário.

**D6 — O "próximo passo" ignora a janela e a fila.**
- *Evidência:*
  - logo depois de emitir a ordem, "Próximo: Emitir o corte", antes da preliminar e do recurso (E03,
    E05);
  - depois da desistência de C02, "Próximo: resposta de 1 convocação", em vez de chamar o suplente
    (E15).
- *Sugestão:* considerar a janela recursal e o "a ocupar".

**D7 — "Ocupada" e a concorrência simultânea não se explicam.**
- *Evidência:*
  - "4 ocupadas" antes de qualquer convocação;
  - C09 conta como ocupada antes de ser chamada;
  - nenhuma tela diz que C16 ocupa pela ampla e que por isso a PPI vai a C17 (40, 41).
- *Sugestão:* listar os ocupantes por lista, com a marca "ocupa pela ampla".

**D8 — Recurso: decisão sem efeito visível.**
- *Evidência:*
  - o Julgador não vê o objeto sem instrução (23);
  - a decisão diz só "o resultado foi corrigido";
  - a ordem obsoleta lista as mudanças **por protocolo, sem nome**, e sem dizer que a 8ª posição é a
    fronteira do corte (22b).
- *Sugestão:* nomes nas "mudanças posição a posição" e a marca da linha do corte.

**Baixo**

- **D9** Peso único por Etapa e mínima inócua em Etapa não eliminatória, sem aviso na Etapa (C06 do
  diário).
- **D10** Perfis: seletores "qual é a ampla" e "reversão" só depois do 1º salvamento; linhas novas
  rotuladas "Modalidade nova"; linha geral pré-preenchida com o total (C03).
- **D11** Critério de desempate: "O que ele compara" oferece Etapas e fatos quaisquer que sejam o tipo
  (C07).
- **D12** Edital publicado: a etapa Classificação abre com controles habilitados e sem "Salvar", e o
  passo "Cronograma" aparece "pendente" (S01). Útil para simular, confuso como estado.
- **D13** Andamento "apuração 0 de 6" e links de ocupação e convocação também no marco intermediário
  (E01); o simulador alerta "empate pararia a apuração" num marco que não apura vagas (C09).
- **D14** Formatos de nota diferentes entre telas (91,5 · 70 · 76,50).
- **D15** O Evento acrescentado no fim do Cronograma fica fora de ordem para o candidato (61), sem aviso
  na composição.
- **D16** A reversão exige ir da convocação à ocupação, emitir na PcD e depois na ampla, com motivo nas
  duas. O texto guia cada passo, mas são três telas para um fato só (E16).

**O que funciona bem** (para não perder na hora de mudar):

- as mensagens da validação nomeiam número e lugar;
- a Revisão imprime a frase normativa de cada decisão;
- a conferência antes de emitir;
- a detecção e explicação da ordem obsoleta;
- a tela da convocação;
- a recusa de "Conforme" sem abrir o documento;
- a mensagem da reversão;
- o acompanhamento do candidato, com o Resultado de cada Etapa e o motivo.

---

## 14. Decisões para a equipe (governança: registradas, não tomadas)

- **G1.** Corte fixo **por lista**: é a norma pretendida para editais com entrevista (8 da ampla + até 8
  de cada reservada)? Se for, a frase do documento precisa dizer "de cada lista". Se não for, falta a
  espécie "fixo no total".
- **G2.** A ordem sucessora de um recurso pode ir **direto à definitiva**, sem preliminar corrigida? Hoje
  pode.
- **G3.** A prévia deve poder usar as **notas reais**, só leitura, depois que elas existem?
- **G4.** Barema dentro da Etapa e peso por marco: são necessidades dos editais do Cefor, ou o total
  lançado basta?
- **G5.** Explicação do desempate ao candidato: o que é publicável (valores comparados? datas de
  nascimento são dado pessoal)?
- **G6.** "Ocupada" antes da resposta: a mesma pergunta do estudo do sorteio (Q6–Q8), agora com a
  reversão.

---

## 15. Os 12 critérios de aceitação, respondidos

| # | A equipe consegue explicar… | Onde |
|---|---|---|
| 1 | Como configurar um processo por classificação | §3, §4; guia, cap. 1–3 |
| 2 | Como definir Etapas e critérios de pontuação | §2, §4.1 (critério = desempate; não há barema) |
| 3 | Como configurar relações e dependências | §3 (as três regras), §5 |
| 4 | Como o GPS determina quem avança | §5; §6 (tabela); guia, cap. 5 e 7 |
| 5 | Como notas e pesos produzem a classificação | §6.1 (6 cálculos) |
| 6 | Como se resolvem empates | §6.1 (C07 × C06; C08 × C09; C08 × C07) |
| 7 | Como se aplicam modalidades e reservas | §9, §11 (C16, reversão) |
| 8 | Como o simulador ajuda a configurar | §8 |
| 9 | Como se produzem e publicam resultados | §10 |
| 10 | Como recursos e correções afetam a classificação | §6.1 (C10), §10 |
| 11 | Como a classificação final leva à convocação | §11 |
| 12 | Como o processo continua depois da convocação | §11, itens 6–10 |

**O ponto que o pedido mandou registrar.** Para explicar a posição de **Sofia (C07)** e de **Caio
(C08)**, foi preciso uma de três fontes:

- abrir o ato emitido e achar o critério entre UUIDs;
- reconstituir a conta fora do sistema;
- usar o simulador, que fala de outras pessoas.

É o problema de clareza mais importante do estudo (D1).
