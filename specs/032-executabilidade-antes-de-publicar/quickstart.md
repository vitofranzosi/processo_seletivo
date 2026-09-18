# Quickstart — como se verifica que esta feature funcionou

Quatro cenários. Os três primeiros reencenam, pela interface administrativa, os Editais que a
auditoria de 16/09/2026 publicou quebrados; o quarto é a prova de que o acervo não se mexeu. Sem
shell e sem banco nos três primeiros — é o que o Princípio VI cobra.

## Pré-requisitos

```bash
cd backend && make lint check test-pg
```

`test-pg`, nunca `test`: sem o par `TEST_DB_ENGINE=postgresql` **e** `POSTGRES_USER` a suíte cai para
SQLite e 33 testes falham por motivo que não é o diff. `lint` são dois passos — `ruff check` **e**
`ruff format --check`.

Para subir a interface, `INTERFACE_SELETOR_IDENTIDADE=true`, senão `/gestao/` devolve 503.

---

## Cenário 1 — o Edital que não classifica ninguém (P1, `FR-457`, `SC-157`)

É o Edital 03/2026 da auditoria, reencenado.

**Monte**: um Edital com um Perfil, três vagas, uma Etapa classificatória. Percorra o assistente até
o fim **sem acrescentar marco algum**. Abra a etapa de Revisão.

| O que observar | Esperado |
|---|---|
| A Revisão | acusa erro impeditivo — hoje ela responde `IMPEDE: []` |
| A mensagem | nomeia o Perfil e diz que sem marco ninguém é classificado por ele |
| O caminho de volta | leva à etapa **Classificação**, não à de Perfis |
| Submeter | é recusado, com a mesma frase |

**E o contraprova que importa**: grave o rascunho no meio, com o Perfil ainda sem marco. **A gravação
é aceita.** A família é impeditiva no ato de publicação, nunca na gravação.

---

## Cenário 2 — o sorteio que o documento não contava (P2, `FR-464`–`FR-468`, `SC-158`)

É o Edital 04/2026 da auditoria, reencenado.

**Monte**: um Edital com um Perfil e um marco cuja ordem é **por sorteio**. Declare o método comum do
Edital, completo. Publique e abra o documento.

| O que observar | Esperado |
|---|---|
| A seção do marco | traz **Ordem: por sorteio** |
| `Combinação` e `Normalização` | **ausentes** — hoje o documento imprime "soma ponderada da Etapa…", que é falso |
| O bloco `Sorteio` | algoritmo, fonte, ocorrência e instante, derivação, normalização da semente e o que vale se a ocorrência faltar |
| `Método:` | diz **comum a este Edital** |

**Depois**, declare no marco um método próprio diferente do comum e publique outro Edital: o
documento imprime o próprio e diz **diverge do comum deste Edital**.

**E a recusa**: monte um terceiro Edital com marco por sorteio e **sem método** — nem próprio, nem
comum. A publicação é recusada nomeando o marco. Hoje ela passa.

**Prova de reprodutibilidade (`SC-158`)**: com o documento na mão e sem acesso ao sistema, uma
terceira pessoa consegue dizer qual ocorrência fixará a semente e o que acontece se ela faltar.

---

## Cenário 3 — a cota e o corte que ninguém avisou (P1 e P3, `FR-461`–`FR-463`, `FR-470`–`FR-472`)

**Monte**: um Perfil com quadro 7/1/2 — sete na ampla, uma e duas em duas Modalidades reservadas —,
cujo marco ordena **por pontuação**, e **sem regra de corte**.

Na etapa de Classificação, ainda compondo:

| O que observar | Esperado |
|---|---|
| O cartão do marco, com o corte em branco | declara que sem corte não há convocação — hoje ele fala só da Etapa seguinte |

Na Revisão:

| O que observar | Esperado |
|---|---|
| Aviso do corte | nomeia a cadeia inteira: corte → geração → faixa → convocação |
| Aviso da reserva | nomeia a causa — a ordem daquele marco é emitida em lista única — e não o sintoma |
| Impedimento | **nenhum**: os dois são avisos, e a publicação continua possível |

Publique, receba inscrições, consolide e emita a ordem. Na tela de **Ocupação**:

| O que observar | Esperado |
|---|---|
| Recortes reservados | **não** oferecem "Apurar a ocupação deste recorte"; declaram por quê |
| Recorte da ampla | continua oferecendo, e funciona |
| "Pedir a faixa seguinte" | **não** é oferecido, e a tela diz que a faixa exige o corte |

Hoje, os três botões aparecem idênticos e dois deles sempre falham.

**Contraprova do falso positivo (`FR-461`)**: monte um marco cuja regra de corte declara
**não governar Etapa alguma** — é o Edital 69/2026 da amostra. **Nenhum aviso é emitido.** A regra
existe, a faixa nasce e a convocação alcança. Se este cenário produzir aviso, a feature está
treinando a pessoa a ignorar a família inteira.

**Contraprova da grafia-armadilha (`FR-470`)**: num Perfil que declara uma Modalidade chamada "Ampla
concorrência" e a aponta como a da ampla, **nenhum aviso de reserva é emitido** para ela. O recorte
da ampla é o `NULL` da linha geral, e confundir os dois produziria aviso em todo Edital que nomeia a
ampla.

---

## Cenário 4 — o acervo não se mexeu (`FR-460`, `FR-469`, `SC-161`)

Este usa o banco, e é o único que usa — não há como observar imutabilidade pela tela.

**Antes de aplicar a feature**, registre o conteúdo e o resumo criptográfico das versões vigentes de
todos os Editais publicados. **Depois**, registre de novo.

| O que observar | Esperado |
|---|---|
| Conteúdo e resumo de cada versão | idênticos, um a um |
| Degraus de elevação | nenhum acrescentado |
| Retificação de Edital do acervo sem marco, sem método ou com reserva | **continua sendo aceita** |

O último é o que mais importa, e é o que quase se perde: a feature existe para evitar que um Edital
seja publicado quebrado. Tornar irretificável justamente o Edital que já foi publicado quebrado
trocaria um problema por outro pior.
