# Plano de produção do Centro de Controle (09/11/2026)

**Origem.** Em 09/11 o usuário aprovou a versão 2 para implementação incremental:

> *"Aprovado para iniciar a implementação incremental. […] A única distinção que faço é entre estar
> pronto para implementar — sim — e estar pronto para substituir definitivamente a interface em
> produção — ainda depende dos testes, das decisões pendentes relevantes e da correção do cenário
> 008."*

Este documento substitui a sequência do [06](06-plano-de-implementacao.md) onde as duas divergem. O 06
continua valendo pelo detalhe de cada correção (C3) e pelos riscos.

## 1. As decisões pendentes, classificadas

D-1 e D-8 estão decididas desde 09/11. Nenhuma das pendentes é tomada aqui. Esta seção só diz **o que
cada uma bloqueia**.

| # | Decisão | Classe | Por quê | O que a implementação faz até lá |
|---|---|---|---|---|
| D-2 | Onde mora o Centro de Controle | **Postergável** até o incremento 3 | A estratégia pedida é implantar "mantendo a experiência anterior acessível durante a validação". O incremento 1 entra numa rota própria do Edital, ao lado do detalhe atual, e a pergunta só precisa de resposta na hora de trocar o padrão | Rota nova, ligada nos dois sentidos ao detalhe atual. O detalhe não muda |
| D-3 | Os nomes das fases e dos passos | **Validável com operadores** | É exatamente o que o teste com pessoas mede, e nenhum código depende do texto | Os nomes da versão 2, todos num módulo só, para que trocá-los seja editar uma tabela |
| D-4 | O critério do destaque | **Validável com operadores**, e **bloqueante para a liberação geral** | A regra (d) da versão 2 só fica segura com a spec 135 (lista vazia) | Implementa a regra (d), dita na tela. A liberação espera a 135 |
| D-5 | Observar a extração antes de congelar todas as relações | **Postergável** para o Centro de Controle; recomendada **logo**, pelo risco | É regra da tela do sorteio, e não do Centro. Mas é um ato irreversível de um clique | Nada. O Centro só mostra o que a derivação diz (a semente fica *Ainda não* até haver relação congelada) |
| D-6 | Quem vê o detalhe por lista | **Postergável** | Preservar a regra atual (D-004 da `127`: quem conduz ou audita) não exige decisão; só mudá-la exigiria | A regra atual, testada no HTML |
| D-7 | Quem aprova os textos pedagógicos | **Bloqueante para a liberação geral**; não bloqueia o desenvolvimento | Os textos vão ao ar como explicação oficial do GPS | Textos da versão 2 marcados como provisórios no módulo de conceitos. A liberação espera a aprovação |

**Bloqueia o desenvolvimento:** nenhuma.

**Bloqueia a liberação geral:**
- a D-4, junto com a spec 135 implementada;
- a D-7;
- a validação com operadores.

**Bloqueia a troca do padrão (incremento 3):** a D-2.

## 2. A divisão mínima: três specs, mais a 135

| Spec | Incremento | Problema | Escopo | Depende de |
|---|---|---|---|---|
| **135** (PR #440, só a spec) | — | A derivação diz menos do que sabe: lista vazia, preliminar como texto, espera que oferece o já feito, contagens sem escopo | As quatro correções da C3 | Nada. **Gate da liberação geral** |
| **136** — Centro de Controle do Edital | 1 | O operador não vê onde a seleção está, o que é dele e o que vem depois | A página do Edital publicado, com as quatro camadas da versão 2, numa rota própria; os conceitos num módulo único; o link de e para o detalhe atual | Nada para começar. A 135 para liberar |
| **137** — O Processo agrega os Editais | 2 | O Processo diz "nenhum ato" ao lado de um Edital com providências (A-02) | "Onde cada Edital está" com mini-trilha e contagens, numa leitura em lote; o "O que fazer agora" do Processo dá lugar ao agregado (D-8); "Próximos marcos" honesto (A-10) | 136 (reusa a composição) |
| **138** — O Centro de Controle passa a ser o padrão | 3 | A troca definitiva | O detalhe do Edital publicado passa a ser o Centro; a vista anterior fica acessível por um ciclo; os ajustes que a validação com operadores pedir (D-3, D-4) | 136, 137, a D-2, a D-7, a validação e a 135 |

**O que fica fora da divisão, de propósito:**
- **C6 (sorteio).** Entra quando a D-5 for decidida, como spec própria, sem relação com o Centro.
- **Nenhuma spec de "componentes genéricos".** O que o Centro precisa nasce dentro da 136.

**Por que a 136 junta a C1, a C2 e a C4 do plano anterior.** Separadas, cada uma entregaria uma página
pela metade, ou mexeria no detalhe atual — e a estratégia é não mexer nele até o incremento 3. Juntas,
elas formam uma página nova que nasce completa, numa rota própria, sem regressão possível na atual.

## 3. Critérios de aceite

### 135
- Os da própria spec: o SC-1460 ao SC-1466.
- No C08 da `134`, a única providência da presidência diz que a lista PPP não tem inscritos.

### 136 — Centro de Controle do Edital

**Fidelidade ao domínio**
- Toda situação vem do `Andamento` da `127`. O teste de coerência:
  - a marca "sua" de uma fase existe **se, e só se**, há providência sua nela;
  - o andamento de uma fase é *Concluída* **se, e só se**, todas as células dela estão *Feito* ou *Não
    se aplica*;
  - a soma das providências mostradas é o `Nivel1.total`.
- Nenhuma regra nova de disponibilidade nem de autorização. Todo botão leva à tela real do ato.
- Um teste prova que um papel sem permissão **não recebe** o link, e que a tela real recusa mesmo
  assim (404 ou recusa).

**Leitura**
- Nos 14 cenários publicados da `134`, como presidência, aparecem na primeira dobra a 1440 × 900:
  - a frase "Onde estamos";
  - o mapa;
  - a primeira providência, ou a frase de que não há nenhuma.
- **Fase consultada × fases em curso.** O realce do cartão escolhido é diferente do sinal de "em curso"
  e da marca de ação, e o cartão consultado leva `aria-current`. Um teste confere que, no C12,
  Classificação consultada e Convocação em curso aparecem distintas, e que o texto "fase consultada"
  existe para leitor de tela.
- **O destaque** segue as três regras e escreve "Por que esta". No C06, é "Fixar os participantes"; no
  C12, nenhum; no C08, "Classificar a lista" — com a menção à lista vazia **depois da 135**.

**Papéis**
- Testes com presidência, avaliação, Gestor e Publicador nos C06, C08 e C12:
  - quem não `ve_a_matriz` não recebe a tabela por lista (conferido no HTML);
  - "Nenhuma ação é sua agora", quando for o caso;
  - Encerrar e Cancelar só para quem os tem, e recolhidos.

**Casos-limite**
- O Edital sem providência: o C14 depois do encerramento, ou a fixture.
- O prazo vencido.
- O impedimento com "quem resolve".
- A Retificação em curso.
- Dois Perfis no mesmo Edital, por fixture de teste, porque **nenhum cenário da 134 tem**.

**Técnico**
- O orçamento de consultas da página é fixo por Edital, no molde da FR-4120 da `127`.
- Nenhuma rolagem horizontal a 375 px.
- Nenhuma violação de CSP.
- Teclado: o Tab percorre o mapa e as providências na ordem visual.
- Os guardiões de acessibilidade, de estáticos, de vocabulário e de citações passam.

**Coexistência**
- O detalhe atual não muda nem um byte de comportamento: a suíte dele passa sem alteração.
- O link entre os dois é de ida e volta.

### 137 — Processo agregado
- Com 1, 3 e 10 Editais, o número de consultas não cresce por Edital além do orçamento combinado.
- Um Processo com dois Editais (por fixture) mostra os dois, com a mini-trilha e as contagens.
- Nenhum Processo diz "nenhum ato" quando um Edital dele tem providência da pessoa: é o A-02, como
  teste.

### 138 — Troca do padrão
- A decisão D-2 está registrada.
- A validação com operadores foi feita, e os ajustes que ela pediu estão aplicados.
- A 135 está mergeada.
- A vista anterior continua acessível por um ciclo.

## 4. A sequência

```
agora ──► 135: plan → tasks → implement (sessão própria) ────────────────┐
     └──► 136: specify → plan → tasks → implement (sessão própria) ──────┤
                                                                         ▼
                         validação com 3–5 operadores na homologação (136 + 135)
                                                                         ▼
                                   137 (Processo) ──► 138 (troca, com D-2, D-7)
```

- **A 135 e a 136 correm em paralelo, e não tocam os mesmos arquivos.**
  - A 135 mexe em `interface/andamento.py` e `providencias.py`.
  - A 136 **lê** essas duas e escreve arquivos novos.
  - Quem mergear depois roda a suíte sobre a outra.
- **A 137 pode começar** assim que a composição da 136 estiver estável no plano dela. Não precisa
  esperar a validação.

## 5. A validação com operadores

| | |
|---|---|
| **Quem** | 3 a 5 integrantes de comissões ou da equipe de seleção, ao menos um que nunca conduziu um sorteio no GPS |
| **Onde** | Homologação, com a 135 e a 136 implantadas, numa rodada nova dos cenários C06, C08 e C12 (`restaurar_cenario_de_treinamento`) |
| **Como** | 30 minutos por pessoa, falando em voz alta. A pessoa usa o Centro de Controle, sem ver a tela atual antes |
| **Tarefas** | (1) Diga em que ponto a seleção do C12 está. (2) O que você faria primeiro no C06, e por quê? (3) Por que o sorteio do C06 ainda não pode ser feito? (4) No C12, o que está esperando prazo, e até quando? (5) Onde está a lista PPP do C12, e o que falta nela? (6) No C08, há algo para você fazer? |
| **Perguntas finais** | O mapa mostra uma fase atual, ou várias? Os nomes "Fixar os participantes" e "Vagas" fazem sentido? O "Por que esta" convenceu? |
| **O que se mede** | Acerto por tarefa, tempo, hesitações, e as palavras que a pessoa usa para descrever o estado |
| **Critério para o incremento 3** | Pelo menos 4 de 5 pessoas acertam as tarefas 1, 2 e 4 sem ajuda, e nenhuma lê o mapa como "uma fase atual" |
| **Registro** | Um `doc/validacao-centro-de-controle-<data>.md`, com as respostas e as decisões D-3 e D-4 que dele saírem |

**Ressalva de honestidade.** A validação não substitui a correção da 135. Uma interface que mostra com
clareza uma ação equivocada é pior do que uma confusa.
