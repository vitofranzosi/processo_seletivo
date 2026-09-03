# Briefing — Revisão de compatibilidade 012–013: a Etapa publica a forma da conclusão

**Escrito em 03/09/2026**, depois de a revisão do handoff anterior encontrar um fato que ele não
tinha como conhecer. Substitui, como ponto de partida da próxima sessão, a seção *"Dependência que
precisa cair antes"* e a *"Ordem de execução da revisão da 012"* de
[`briefing-013-resultado-da-etapa.md`](briefing-013-resultado-da-etapa.md). O restante daquele
documento — a fronteira, os seis invariantes e as lacunas registradas — continua valendo e descreve
a feature que vem **depois** desta.

A decisão que motiva tudo está em [`decisao-012-conclusao-decisoria.md`](decisao-012-conclusao-decisoria.md)
e não é reaberta aqui. O que muda é o **alcance** dela.

## O fato que mudou o escopo

O briefing da 013 foi escrito às 11:32 numa branch que **não continha** `specs/013-consolidacao-resultado-etapa/`
nem o app `processo_seletivo/resultados/` — verificável em `git ls-tree bc90820`. A 013 foi mergeada
às 19:29 (PR #26) e aquele briefing às 19:34 (PR #27). Ele descreve, de boa-fé, um repositório que
deixou de existir cinco minutos antes de ele entrar.

Consequência direta: **o passo "`/specify` da 013" não se aplica.** A 013 existe, está implementada,
e pressupõe pontuação do começo ao fim — no domínio, na tabela e na trigger.

```text
012 pontuada ─┐
              ├── já implementadas e em main
013 pontuada ─┘
                  ↓
        três Editais reais do Cefor/Ifes
                  ↓
   o contrato entre as duas é estreito demais
```

Isso não invalida o trabalho anterior: ele atendeu, corretamente, a família de Edital que estava à
vista. O que a análise dos Editais 35/57 revelou é que o **contrato entre 012 e 013** — não a 012
sozinha — pressupõe que avaliar produz número.

## A frase que governa

> **Avaliar deixa de significar pontuar. A Etapa publica qual das duas formas de conclusão ela
> exige, e as duas atravessam o sistema inteiro — da Mesa ao Resultado oficial — sem que nenhuma
> escala numérica seja inventada onde o Edital não publicou nenhuma.**

E o limite, que é o que impede esta rodada de inchar:

> Generalizar a 013 é ensiná-la a oficializar as duas formas de conclusão que já existem. **Não** é
> trazer para dentro dela classificação, vagas, sorteio, recurso ou convocação — que continuam
> sendo o arco 014–019 descrito no briefing da 013.

## Por que emendar só a 012 seria pior do que não emendar

```text
012 aceita DECISORIA
        ↓
013 não aceita DECISORIA
        ↓
o avaliador conclui "indeferido" e a Etapa nunca produz resultado
```

O objetivo desta rodada é reduzir a distância entre o sistema e os Editais reais. Entregar uma
fronteira quebrada no meio do caminho seria criar uma lacuna nova para eliminar outra — e a lacuna
nova seria silenciosa, que é a espécie pior.

## O que **não** muda, e precisa ser dito na emenda

- **P-006 permanece inteiro.** Avaliar continua não sendo decidir. O campo chama-se `sentido`, e não
  `decisão`, exatamente por isso. Duas análises documentais podem afirmar sentidos opostos; resolver
  isso continua sendo da 013 — que é onde `REGRA_DE_COMBINACAO_AUSENTE` já mora.
- **As recusas do §21 da 012 continuam valendo por inteiro** — barema, avaliação cega, distribuição
  automática, recurso, comunicação. A conclusão decisória é o que permite **não** pontuar; ela não
  é barema por outro nome.
- **O comportamento PONTUADA existente é invariante de não regressão**, e não apenas "preservado".
  Toda Etapa hoje publicada é pontuada, todo Resultado hoje gravado é pontuado, e nenhum deles pode
  mudar de comportamento por causa desta revisão.
- **A progressão já é agnóstica à forma.** `resultados/domain/progressao.py` consome `HABILITADA` e
  `ELIMINADA`, nunca pontuação. Um `DESFAVORAVEL` que eliminar entra na progressão sem uma linha de
  mudança — é a evidência concreta de que generalizar a 013 não a infla.

---

## D-008 — para o §5 da SPEC 012

*Texto a ser transplantado para `specs/012-mesa-de-avaliacao/spec.md`, §5.*

**Uma Avaliação concluída precisa possuir a conclusão completa segundo a forma que a Etapa
publicou.** "Completa" deixa de significar *tem nota* e passa a significar *tem o que a forma exige*.
Os dez pontos abaixo são a decisão; o corpo da spec passa a estar escrito conforme eles.

1. **A Etapa publica `forma = PONTUADA | DECISORIA`.** É conteúdo normativo, pelo mesmo argumento
   de P-007 que obrigou `maximumScore` a ser publicado (D-001): regra que afeta direito do candidato
   não pode ser configuração de tela.
2. **A forma `DECISORIA` publica `rotuloFavoravel` e `rotuloDesfavoravel`.** O domínio guarda sempre
   `FAVORAVEL | DESFAVORAVEL`; o rótulo que o avaliador lê e o PDF imprime é dado publicado, pelo
   padrão de `ModalidadeConcorrencia`. Sem objeto genérico e **sem default institucional** — prefill
   editável na tela de elaboração é conveniência, não norma.
3. **Conteúdo em `schemaVersion` ≤ 5 sem `forma` é lido como `PONTUADA`**, e a ausência dos rótulos
   é correta porque não se aplicam. Todo o domínio anterior só admitia essa forma; a leitura não
   inventa nada. Esta leitura vive em **dois lugares distintos, e a emenda nomeia os dois**:
   - o consumo — `avaliacoes/domain/previsao.py`, cujo contrato já é *"o que a ausência quer dizer,
     num lugar só"*;
   - a elevação no caminho de Retificação — `publicacoes/domain/elevacao.py`, que hoje fixa
     `VERSAO_DE_ORIGEM = 4` e declara explicitamente *"elevar não é um mecanismo genérico de
     compatibilidade: é este incremento, e só ele"*. **O segundo incremento colide com essa frase**,
     e a D-008 tem de dizer se a elevação vira cadeia (4 → 5 → 6) ou se a origem passa a ser um
     conjunto. É decisão de spec, pelo mesmo motivo que a D-002 foi.
4. **A revisão produz `SCHEMA_VERSION` 6, e não reescreve a história do incremento 4 → 5.**

   ```text
   012 original      v4 → v5   + evaluationsPerRegistration, + maximumScore
   revisão da 012    v5 → v6   + forma, + rotuloFavoravel, + rotuloDesfavoravel
   ```

   D-001, FR-008 e o §26 afirmam hoje "um incremento canônico, e só um". Os três passam a ser
   **decisão histórica da 012 original**, verdadeira no seu contexto; a D-008 registra que uma
   mudança de requisito posterior exige um segundo incremento canônico. Fingir que os cinco campos
   nasceram juntos exigiria mentir em `elevacao.py`, que documenta o 4 → 5 como fato consumado.
5. **A conclusão copia a forma da versão contra a qual foi validada.** `forma` aparece em dois
   lugares com funções diferentes, e eles não são fontes concorrentes:

   ```text
   Etapa publicada  → "a regra vigente determina a forma X"
   ConclusaoAvaliacao → "esta avaliação foi concluída sob a forma X"
   ```

   Na transação de conclusão, o sistema lê a forma **do conteúdo da versão consolidada** (FR-096,
   que já exige exatamente isso para a Etapa), valida contra ela e grava aquela mesma forma na
   linha. É a desnormalização que mantém a `CheckConstraint` local — uma constraint do PostgreSQL
   não referencia outra tabela — e é a mesma preservação de sentido que FR-071 já faz com a versão.
6. **`PONTUADA` exige pontuação e não admite sentido.**
7. **`DECISORIA` exige sentido e não admite pontuação.** As duas juntas substituem
   `ck_avaliacao_concluida_completa`, que continua sendo o que define `CONCLUIDA` no banco:

   ```sql
   forma = 'PONTUADA'  → pontuacao NOT NULL AND sentido IS NULL
   forma = 'DECISORIA' → sentido   NOT NULL AND pontuacao IS NULL
   ```
8. **`DESFAVORAVEL` exige parecer.** Em `PONTUADA` a regra atual de FR-034 permanece intacta — nota
   abaixo do mínimo em Etapa eliminatória. A assimetria é deliberada e precisa ser escrita como tal:
   em `DECISORIA` o desfavorável é justamente o caso em que o candidato mais precisará da
   fundamentação para recorrer, e a obrigatoriedade não depende do caráter da Etapa. Exigir parecer
   também no favorável é configuração futura, e não se generaliza agora.
9. **Aplicabilidade dos campos normativos de pontuação, por forma:**

   ```text
   PONTUADA    maximumScore aplicável · minimumScore aplicável conforme a Etapa
               sentido ausente · rótulos ausentes
   DECISORIA   maximumScore ausente  · minimumScore ausente
               sentido aplicável · rótulos obrigatórios
   ```

   **`weight` fica fora dessa condicionalidade**, e a verificação no código fecha a questão:
   `resultados/domain/compatibilidade.py` o exclui de propósito — *"peso e caráter classificatório
   pertencem à composição entre Etapas, que esta feature recusa"* — e `regra.py` repete *"`classificatory`
   não entra… Peso, idem"*. Hoje `weight` não alimenta cálculo nenhum: é declaração normativa para a
   composição que 015 fará. Não é campo de nota, e condicioná-lo à forma seria acoplá-lo a uma
   distinção que não é a dele.
10. **Todos os campos normativos da Etapa introduzidos pela 012 — inclusive `forma` e os rótulos —
    são alcançáveis pela Retificação no canal institucional suportado.** O requisito é de
    **capacidade**, e não de contagem de linhas: `interface/retificacao.py` hoje declara cinco
    campos em `CAMPOS_ETAPA` e deixa `maximumScore` e `evaluationsPerRegistration` de fora, mas essa
    é observação da implementação atual e a spec precisa sobreviver ao refactor. A metade
    `documentRequirements` da E2E-004 continua fora desta rodada — é grupo novo no formulário, e
    trabalho de outra natureza.

## D-008 na SPEC 013 — a contraparte

*Mesma decisão, do outro lado da fronteira. Numeração a confirmar contra o §2 da 013.*

1. **`ResultadoEtapa` passa a admitir as duas formas**, pela mesma estrutura e pelo mesmo motivo da
   `ConclusaoAvaliacao`: pontuação quando a fonte é pontuada, sentido quando é decisória, e a forma
   gravada na linha para que a constraint continue local. A tabela é append-only por privilégio
   (`seguranca/papeis.py`) e por trigger, exatamente como `avaliacoes_conclusaoavaliacao` — a
   migração tem a mesma restrição de implantação que a decisão já mapeou um nível acima.
2. **A trigger `resultado_etapa_coerente` passa a conferir por forma.** Hoje ela compara
   `fonte.pontuacao IS DISTINCT FROM NEW.pontuacao`; uma conclusão decisória não tem pontuação, e a
   conferência precisa alternar como a `CheckConstraint` alterna. Isso é o coração da garantia da
   013 e não pode voltar para a aplicação.
3. **`impedimento_da_regra` deixa de exigir nota mínima em Etapa decisória.** Hoje
   `regra.py` recusa consolidar Etapa eliminatória sem `minimumScore` — *"aceitar 'eliminatória sem
   critério' seria deixar a consequência para quem implementa decidir"*. A análise documental dos
   35/57 é **eliminatória, decisória e sem nota mínima**, e isso é normal. Sem esta alteração, o
   sistema aceitaria o indeferimento na 012 e recusaria produzir Resultado procurando uma nota
   mínima que o Edital nunca publicou — que é a fronteira quebrada descrita acima.
4. **`consequencia` ganha o ramo decisório**, sem inventar escala: `DESFAVORAVEL` não vira zero e
   `FAVORAVEL` não vira um. O motivo exibível cita o rótulo publicado, e não o enum interno.
5. **`CAMPOS_COMPARADOS` passa a incluir `forma`.** É o furo mais silencioso do conjunto: uma
   Retificação que virasse `PONTUADA → DECISORIA` não seria detectada como norma divergente, e a
   013 consolidaria uma conclusão pontuada sob norma decisória — exatamente o que aquela função
   existe para impedir. Os rótulos **não** entram: mudar "Deferido" para "Deferido(a)" não altera
   consequência nenhuma, e compará-los faria correção de redação bloquear consolidação pendente,
   pelo mesmo argumento que já mantém nome e cronograma fora da lista.
6. **A progressão não muda.** `ELIMINADA` continua sendo `ELIMINADA`, qualquer que seja a forma que
   a produziu. É o limite que mantém esta rodada estreita.

## A pergunta que ainda está aberta

Uma só, e ela precisa fechar **antes do `/plan`**, porque altera domínio e constraint:

> **O que uma Etapa `DECISORIA` e não eliminatória produz como consequência?**

`FAVORAVEL` habilita, e `DESFAVORAVEL` em Etapa eliminatória elimina — os dois casos dos Editais 35
e 57. O terceiro caso não tem resposta óbvia: se a Etapa não é eliminatória, um desfavorável que
habilita é absurdo, e um desfavorável que elimina aplica caráter eliminatório que o Edital não
publicou.

Três saídas, e a recomendação é a terceira:

| saída | o que afirma | custo |
|---|---|---|
| `DESFAVORAVEL` sempre elimina | o sentido carrega a consequência, e `eliminatory` não a modula na forma decisória | inventa efeito onde o Edital não o publicou |
| `DECISORIA` implica `eliminatory` | a forma decisória só existe em Etapa eliminatória; publicar o contrário é recusado | fecha por validação, e nenhum dos três Editais exercita o contrário |
| impedimento explícito na 013 | a Etapa é consolidável, mas a combinação decisória + não eliminatória cai em `REGRA_INSUFICIENTE`, com a frase que diz por quê | consistente com o que `regra.py` **já** faz para eliminatória sem nota mínima |

A terceira é a que não inventa norma e não fecha porta: usa o mecanismo de recusa que a 013 já tem,
com a mesma voz. Mas é decisão de quem governa a spec, e não do `/plan`.

## Testes que a rodada precisa produzir

Além da ida e volta das duas formas nas duas features:

- `INSERT` cru violando a constraint da conclusão → prova que o invariante continua no banco;
- `INSERT` cru violando a trigger do Resultado → o mesmo, um nível acima;
- Etapa `DECISORIA` + conclusão com pontuação → banco e domínio recusam;
- Etapa `PONTUADA` + conclusão com sentido → banco e domínio recusam;
- leitura de snapshot versão 5 depois do salto para 6 → compatibilidade sem reescrita histórica;
- Retificação que troca a forma da Etapa depois de conclusões gravadas → a conclusão histórica
  continua interpretável, e a 013 recusa consolidar por norma divergente;
- `forma` e rótulos no documento materializado → P-007 é realidade, e não só modelo;
- recusa pelo canal HTTP real nos POSTs de escrita da Mesa → a lacuna que a E2E-015 registra;
- Etapa decisória eliminatória **sem** nota mínima consolida e elimina → a regressão que a
  contraparte 3 na 013 existe para impedir;
- todo o comportamento pontuado hoje verde continua verde, sem alteração de asserção.

## Ordem de execução

```text
1. branch própria
2. emendar specs/012 — D-008 no §5 e revisão transversal (mapa abaixo)
3. emendar specs/013 — a contraparte, no §2 e nas seções do mapa
4. modelo, constraint e migração da 012 · snapshot v6 · elevação · CAMPOS_ETAPA
5. Mesa: dois instrumentos conforme a forma
6. PDF: forma e rótulos no documento publicado
7. modelo, trigger e domínio da 013
8. testes
```

Emendar as duas specs **antes** do código é o que impede a contradição que o Princípio V proíbe.
Implementar contra a 012 vigente, que ainda diz que concluir exige pontuação, e contra a 013
vigente, que ainda diz que o Resultado é uma nota, criaria a divergência entre spec e código que o
projeto trata como defeito.

## Mapa da revisão transversal

**A emenda não é pontual.** A premissa *avaliar = registrar pontuação* está distribuída pelas duas
specs, e o objetivo do mapa é eliminá-la **preservando explicitamente o comportamento pontuado**.

### `specs/012-mesa-de-avaliacao/spec.md`

| seção | o que está lá hoje | o que a emenda faz |
|---|---|---|
| §1 Visão | "registrando pontuação e parecer" | neutraliza para a afirmação do avaliador |
| §2 Frase que governa | "registrar a avaliação" | permanece; confirmar que o entorno não recaia em nota |
| §4 A cadeia | `Avaliação → 013` | permanece correto |
| §5 Decisões | D-001 "um incremento, e só um" | D-001 vira decisão histórica; entra D-008 |
| §6 Problema | "a pontuação é anotada em papel" | descritivo; ajuste menor |
| §7 P-006 | exemplos falam de "nota" | troca para "afirmação do avaliador" |
| §7 P-007 | enumera pontuação máxima, caráter e nota mínima | inclui forma e rótulos na enumeração |
| §8.2 Avaliação | conceito e FRs pressupõem pontuação | conceito ganha forma e sentido; FRs revistos |
| §9 | FR-007/FR-008/FR-066 | separa o que é da Etapa do que é da forma pontuada |
| §14 US4 | FR-031, FR-033, FR-034, FR-103 — maior concentração | reescrita por forma, com FR-034 conforme D-008.8 |
| §18 | FR-088 — validação dentro da transação | vale também para forma e sentido |
| §19 | FR-054 — a trilha não guarda parecer nem pontuação | **acrescenta o sentido**: é conteúdo do juízo pelo mesmo motivo |
| §22 | FR-100 — "a Retificação se comporta como antes" | reancora o "antes", que hoje aponta para a 012 original |
| §23 | SC-006, SC-007, SC-016, SC-023 | critérios por forma, com os pontuados preservados |
| §24 | EC-005 — Retificação altera pontuação máxima | acrescenta o EC da mudança de **forma**, que é de outra espécie |
| §25 | S1 e S5 | slices passam a nomear as duas formas |
| §26 | "um incremento canônico, e só um" | passa a refletir o segundo incremento |
| §27 | gate item 2 e frase final | item 2 vira "conclusão válida segundo a forma publicada"; a frase final permanece. **O gate deixa de ser portão** — a 013 já passou por ele — e passa a ser registro histórico |

### `specs/013-consolidacao-resultado-etapa/spec.md`

| seção | o que está lá hoje | o que a emenda faz |
|---|---|---|
| §1 herança da 012 | "Avaliação possui pontuação total e parecer"; "versão canônica 5" | herda as duas formas e a versão 6 |
| §2 D-001 | "a pontuação consolidada é o total da única Avaliação" | vale para a forma pontuada; a decisória copia o sentido |
| §2 D-002 | reabertura muda a pontuação | generaliza para "muda a conclusão" |
| §2 D-005 | quatro campos comparados | acrescenta `forma`; rótulos ficam de fora, e a spec diz por quê |
| US2, US4 | cenários e consulta em pontuação | ganham o par decisório |
| Edge Cases | "eliminatória sem nota mínima não consolida" | passa a valer só na forma pontuada |
| FR-016, FR-017, FR-025, FR-044 | pontuação consolidada e eliminação por nota | ramificam por forma |
| FR-041 | trilha sem pontuação nem parecer | acrescenta o sentido, como FR-054 da 012 |
| Key Entities | `ResultadoEtapa` registra pontuação exata | registra a conclusão conforme a forma |
| Measurable Outcomes | SC-003, SC-008 | preservam o pontuado e acrescentam o decisório |
| Assumptions | "nota mínima é a única regra estruturada de eliminação" | deixa de ser verdade: o sentido é a segunda |

## Depois desta rodada

A espinha dorsal passa a percorrer os dois caminhos que os Editais reais exercitam:

```text
inscrição → distribuição → avaliação humana ─┬─ pontuada  ─┐
                                             └─ decisória ─┴─→ Resultado oficial da Etapa
```

O que ainda falta para os 35/57 é outra camada inteira — sorteio auditável, progressão da fila,
classificação, alocação de vagas e cotas, heteroidentificação, recurso e convocação —, e continua
registrada como lacuna no briefing da 013. Mas o bloqueio fundamental sai do caminho: **o sistema
deixa de pressupor que avaliar significa dar uma nota.**
