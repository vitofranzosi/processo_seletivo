# Rodada de refinamento (09/11/2026) — protótipo, versão 2

**Origem.** A revisão do usuário de 09/11 deu o conceito por aprovado e pediu uma rodada curta de
refinamento antes da implementação:

> *"Preserve sua arquitetura de informação, a separação entre Processo e Edital, a representação de
> frentes paralelas e a integração com as operações reais. Faça uma rodada curta de refinamento de
> UX, concentrada na clareza dos estados, na linguagem pedagógica, na hierarquia das providências e
> na redução da densidade visual."*

**Escopo.** Só o protótipo e este estudo. A investigação não foi reaberta, nenhum modelo de workflow
foi criado e o código de produção não mudou.

## Decisões registradas nesta rodada

| # | Decisão | Registro |
|---|---|---|
| D-1 | Macrofases simultâneas, sem "fase atual" única | **Decidida: (a)**, pela aprovação do conceito em 09/11 ("Representação de atividades paralelas — um dos maiores acertos"). A spec da C1 registra que revê a recusa da `127` |
| D-8 | O Processo agrega; o Centro de Controle pertence ao Edital | **Decidida: (a)**, em 09/11 ("Eu preservaria exatamente essa arquitetura") |
| D-2 a D-7 | — | **Seguem pendentes.** A revisão recomendou a (a) na D-2, mas não a decidiu |

## O que mudou, item por item

### A. O andamento da fase está separado do que ela oferece

**O problema apontado.** "Ação disponível" não deveria ser estado da fase. Uma fase pode estar
parcialmente concluída e ter várias ações ao mesmo tempo, algumas de quem não pode agir.

**O que mudou.** Agora são duas leituras, com dados e desenho próprios.

- **Andamento** (`centro.agregar`). São quatro valores, só pelos atos já feitos:
  - ✓ Concluída;
  - ◐ Em curso;
  - ○ Ainda não começou;
  - — Não se aplica.

  No cartão, o andamento é a borda superior e o sinal.
- **O que a fase oferece agora, e a quem.** São as providências da `127`, contadas na fase como
  marcas:
  - 1 sua (verde cheio);
  - 1 de outro papel (contorno);
  - ◷ até 14/11 (amarelo);
  - ⊘ impedida (vermelho);
  - "nada a fazer agora", quando a fase está em curso e nada está aberto (Vagas no C12).

A legenda ("Como ler o mapa") explica as duas leituras lado a lado.

**Evidência.**
- `proposta-c06-avaliacao1.png`: o avaliador vê as mesmas fases "Em curso", com "1 de outro papel", e
  não "1 sua".
- `proposta-c12-dobra.png`: Vagas "Em curso · 1 de 2 listas concluídas", com "nada a fazer agora".
- Comparar com `v1-proposta-c06-dobra.png` e `v1-proposta-c12-dobra.png`.

### B. Os passos falam a língua de quem conduz, e o termo técnico vem depois

**O problema apontado.** "Relação · Semente · Sorteio" exige saber o que são relação, semente e
congelar.

**O que mudou.** Cada passo tem um **nome simples**, um **"no GPS: …"** com o termo técnico, e uma
**frase curta sempre visível**.

| Ponto da 127 | Nome simples | No GPS |
|---|---|---|
| Relação | Fixar os participantes | congelar a relação |
| Semente | Obter a semente pública | observar a extração |
| Sorteio | Realizar o sorteio | sorteio |
| Ordem | Classificar a lista | emitir a ordem |
| Corte | Definir até onde se chama | emitir o corte |
| Apuração | Distribuir as vagas entre as listas | apurar a ocupação |
| Resultado | Divulgar o resultado | publicar resultado |
| Convocação | Convocar e decidir | convocação |
| Etapa | o nome da Etapa no Edital ("Prova objetiva") | — |

As providências cujo nome no GPS é jargão (relação, semente, ordem, corte, apuração) passam a ter o
nome simples como título. O nome da `127` fica em "no GPS".

A revisão sugeriu "Preparar os candidatos" para o primeiro passo. O protótipo usa **"Fixar os
participantes"**: o ato não prepara ninguém, ele torna imutável quem participa e com que número. Os
nomes seguem provisórios (D-3) e são o principal ponto a validar com operadores.

### C. O destaque tem um critério, e a tela o diz

**O problema apontado.** No C08 a ação aparecia destacada; no C06 a tela dizia que não ordena. Faltava
critério explicável.

**O que mudou.** Três regras fixas (`centro._destaque`), e a tela escreve "Por que esta: …":

1. **Uma ação sua só.** É ela, porque não há outra. Exemplo: o C08.
2. **Várias, e só uma destrava os passos seguintes, enquanto as outras correm em paralelo.** É a que
   destrava, e a tela diz quais passos esperam por ela.
   - Exemplo: no C06, "Fixar os participantes" é destacada, porque "Obter a semente pública →
     Realizar o sorteio" esperam por ela.
   - A distribuição dos títulos é paralela: a derivação da `127` já sabe que nada a jusante lê essa
     Etapa (D-019 de lá).
   - É uma dependência inequívoca, e não uma prioridade inventada.
3. **Qualquer outro caso: nenhum destaque.** A tela diz: *"Todas já podem ser feitas — o que depende de
   outro ato ainda não aparece aqui — e o GPS não escolhe a ordem entre elas."*
   - Exemplo: no C12, conferir documentos (Convocação) e classificar a PPP são independentes.

**Ressalva que continua valendo.** No C08, a regra 1 destaca "Classificar a lista — PPP", e a PPP não
tem inscritos. A tela fica correta só depois da spec 135 (C3, PR #440), que faz a providência dizer
que a lista é vazia.

### D. Menos texto à vista; o resto sob demanda

**O problema apontado.** Três blocos "Entenda: …" por fase, ocupando espaço.

**O que mudou.**
- **Sempre visível:** uma frase por passo e por providência — o "o que é".
- **Sob demanda:** um "Entenda o ato" por providência, e **um só** "Entenda os passos desta fase" no
  fim do detalhe, com o "por quê" e o "ao confirmar" de cada passo. Antes eram três blocos soltos.

### E. O mapa mais compacto, em três grupos

**O que mudou.**
- **Três grupos**, com rótulo discreto:
  - **Abertura:** Edital e Inscrições;
  - **Seleção:** Avaliação, Classificação, Resultado e recursos, e Vagas;
  - **Ocupação:** Convocação e Conclusão.

  Os grupos orientam a leitura e não mudam regra nenhuma.
- **Cartões mais baixos.** O resumo foi para uma linha, e as marcas ocupam o rodapé do cartão.
- **Abaixo de 1180 px**, os grupos empilham; **a 390 px**, as fases viram lista vertical.

Não houve Gantt nem animação.

### F. "Onde estamos" sem contar frentes

**O problema apontado.** "4 frentes ao mesmo tempo" deixa de dizer alguma coisa quando muitas fases
estão parcialmente ativas.

**O que mudou.** Duas frases:
1. **Quais fases têm algo em aberto agora.** Uma fase em curso sem nada a fazer não entra.
2. **De quem é.** Por exemplo, no C12: *"Há algo em aberto em classificação, resultado e recursos e
   convocação. 2 ações são suas e 2 aguardam prazo ou resposta (a primeira até 14/11)."*

Para o avaliador do C06: *"2 estão com outros papéis."*

### G. O dado do C06 (a Etapa de títulos num Edital de sorteio)

**Conferido no código.** O dado é coerente com a aplicação, mas não é realista.

- O gerador da `134` parte do modelo de sorteio do `seed_demo`, cujo marco enumera a "Análise de
  títulos".
- O gerador já remove as outras duas Etapas do modelo, por confundirem o exercício (comentário em
  `treinamento/construcao.py`, `_etapas`).
- A derivação está certa: a Etapa é esperada, dá visibilidade e recurso, e nada a jusante a lê.
- Um Edital real de sorteio dificilmente teria títulos que não pesam em nada. Mas a validação de
  publicação aceita esse caso, por isso o aviso "Paralela ao sorteio" continua útil.

**Registro, não escopo:** tirar essa Etapa do cenário C06 é decisão de quem mantém a `134`.

## Validação (inspeção automatizada, sem pessoas)

Os 23 casos do roteiro da proposta foram refeitos com quatro identidades (presidência, avaliação,
Gestor e Publicador), a 1440 e a 390 px: **nenhuma rolagem horizontal e nenhuma violação de CSP**.

As tarefas, na primeira dobra a 1440 × 900 ([validacao-automatizada.txt](validacao-automatizada.txt)):

| | Versão 1 | Versão 2 |
|---|---|---|
| Tarefas na primeira dobra | 11 de 12 (a 12ª atrás de "Entenda", de propósito) | **14 de 15**. A exceção é o "ver o ato" do C12, a 933 px |
| Novas tarefas | — | "por que esta ação" (C06), "ações independentes, sem ranking" (C12), "fase em curso com marca de ação sua" (C06): todas na primeira dobra |
| "O que é congelar a relação" | atrás de "Entenda" | na primeira dobra (a frase curta do passo) |
| "Por que o sorteio ainda não pode" | na primeira dobra (tabela) | na primeira dobra (no próprio passo: *"Ainda não começou: nenhuma relação deste marco está congelada"*) |
| Altura da página, C06 | 1908 px | **2164 px** (a tela atual tem 1586) |
| Altura da página, C12 | 2044 px | **2159 px** (a tela atual tem 1756) |

Dois recuos apareceram durante a rodada e foram corrigidos:
- **A tarefa "próxima operação" sumiu.** A medição procurava "Congelar a relação", e a tela passou a
  dizer "Fixar os participantes". O padrão da tarefa foi corrigido; a tela estava certa.
- **"Por que o sorteio ainda não pode" desceu** para 1128 px, porque o roteiro empurrou a tabela. O
  motivo passou para dentro do passo.

**Custo assumido.** A versão 2 é **mais longa** que a 1: o roteiro com frase curta e o destaque com o
seu porquê ocupam espaço. As respostas continuam na primeira dobra; o resto é consulta. Se a altura
pesar no teste com operadores, os candidatos a recolher são a tabela da fase e o "Também sua".

## O que continua sem validação
- **Operadores.** Ninguém usou o protótipo. As três perguntas a fazer:
  1. A trilha é lida como uma posição única?
  2. Os nomes simples dos passos e das fases ("Vagas") fazem sentido?
  3. O critério do destaque é aceito?
- **Cenários ausentes da 134.** Dois Perfis, dois Editais no mesmo Processo, recurso interposto,
  Retificação em curso.
- **O destaque de lista vazia (C08)** depende da spec 135.

## Plano de implementação, com o que se reutiliza

A ordem continua **C3 → C1 → C2** (06-plano-de-implementacao.md). O que a rodada acrescenta ao
escopo:
- **C1:** as duas leituras e o critério do destaque.
- **C2:** o roteiro com nomes simples e o motivo de "ainda não".
- **C4:** a estrutura dos conceitos (`simples`, `termo`, `curta`, `porque`, `ao_confirmar`).

**O que se reutiliza, sem mudança:**

| Peça existente | Papel no Centro de Controle |
|---|---|
| `interface/andamento.do_edital` e `Andamento` / `PerfilNoAndamento` / `Ponto` / `Celula` (127) | Toda a derivação: situação por ponto e por lista, responsável, razão, prazo, link |
| `andamento.Alcance.de` | "Seu papel aqui"; quem vê o detalhe por lista (`ve_a_matriz`) |
| `interface/providencias.Nivel1` / `Providencia` (127) | As providências: sua, de outro papel, em espera; o agrupamento por ato |
| `andamento.matricula_fora`, `andamento.linha_das_inscricoes` | A nota da matrícula; a linha das inscrições |
| `interface/acoes.do_edital` / `hierarquia` (104/057) | As consultas da Administração; Encerrar e Cancelar, recolhidos |
| `interface/atos_retificacao.em_curso` (103) | A Retificação em curso, como faixa |
| `views._documentos_publicados`, `views._marcos_publicados`, `views._pendencias`, `participantes_do_edital` | Documentos, telas do marco, validação do conteúdo, quem atuou |
| `supervisao.sinais` / `alcance`, `pending_editais`, `atos_processo.disponiveis` | A página do Processo |
| `_acao_do_edital.html`, `telas/andamento.css`, `grupos/terminais.css`, `shared/tokens.css` | Desenho dos atos de fim de ciclo, situações da 127, tokens |

**O que é novo** (tudo de apresentação, sem tabela nem regra de disponibilidade):

| Peça nova | Conteúdo | Vem do protótipo |
|---|---|---|
| `interface/centro.py` | Macrofases, `agregar`, `juntar`, o critério do destaque, "onde estamos", roteiro | `prototipo/centro.py`, sem os conceitos |
| `interface/conceitos.py` (C4) | Fonte única dos nomes simples e das frases; lida também pelos "Termos desta tela" | `CONCEITOS` |
| Template do detalhe reorganizado + parciais do mapa, do destaque e do roteiro | As quatro camadas | `prototipo/templates/prototipo/centro.html` |
| `interface/telas/centro.css` | O mapa, as marcas, o roteiro | `prototipo/static/prototipo/centro.css` |

**Testes que a implementação herda do protótipo:**
- **Funções puras** de `agregar`, `juntar` e `_destaque` nas famílias S1–S3 e P1–P3 da `127`.
- **Coerência:** a marca "sua" de uma fase existe se, e só se, há providência sua nela.
- **Template por papel,** conferindo no HTML que quem não `ve_a_matriz` não recebe tabela por lista.
- **As tarefas de `prototipo/validar.py`,** como teste de navegador do grupo `navegador`.
- **O orçamento de consultas** da `127`, sem crescer.
