# Roteiro de validação — Exportação de matrículas (`031`)

**Escrito em 18/09/2026, antes da implementação.** Cada cenário é percorrível **pelo canal de quem
conduz** — sem shell, sem banco e sem chamada manual —, que é o que a Constituição cobra no
Princípio VI. O `C7` existe justamente para provar isso.

> **`C0` cedo, e ele não é deste repositório** — mas ele **não segura os demais**. Enquanto a `Q-1`
> não for respondida, três células e a `C9` ficam em aberto; o resto do roteiro percorre e prova.
> §5 da spec mede o que a espera custaria.

---

## Preparar

```bash
cd backend && make DB_NAME=ps_demo_031 lint check test-pg
```

`test-pg`, e não `test`: a recusa por privilégio e a trigger de append-only do registro de geração
**não são exercidas** no modo padrão da suíte.

Para percorrer à mão:

```bash
cd backend
make DB_NAME=ps_demo_031 seed
make DB_NAME=ps_demo_031 runserver
```

`DB_NAME` vai **como variável do Make** — o `include .env` sobrepõe prefixo de ambiente, e sem isso
esta worktree semeia o banco de outra. O seletor de identidade precisa estar ligado
(`INTERFACE_SELETOR_IDENTIDADE`), ou `/gestao/` devolve 503.

**O papel precisa de `matricula:exportar`.** Ela nasce concedida a ninguém (`FR-455`): se a opção não
aparecer no Edital, é autorização, e não rota quebrada.

---

## C0 — A pergunta que se faz cedo *(Fase 0)*

Fora do sistema. Enviar ao Registro Acadêmico **duas linhas sintéticas** — nunca a linha `2` da
amostra (`D-006`) — com `COD_CURSO`, `COD_TURNO` e `COD_POLO` vazias.

| Pergunta | O que muda se a resposta for outra |
|---|---|
| Aceita célula vazia nas três? (`Q-1`) | se não, a `D-001` cai e a feature precisa de um cadastro de códigos |
| Aceita protocolo opaco `INS-2026-K7M4Q2PX`? (`Q-3`) | se não, `INSC` vira lacuna — o protocolo **não** será tornado sequencial |
| `CLASSIF_CURSO_FINAL` é classificação ou numeração? (`Q-2`) | fecha a `T017d` |
| Usa ISO 3166-1 alpha-2 na coluna 16? (`Q-7`) | se sim, estrangeiro também sai exato (`D-008`) |
| O que esperam de quem declarou cor **indígena**? (`R-1`) | é contradição do próprio destino: `PPP` reserva vaga e `COR` não comporta o valor |

---

## C1 — O arquivo de um Edital *(US1, `FR-433`, `FR-436`, `FR-437`)*

1. `/gestao/` → Edital com convocados → **Exportar para matrícula**.
2. Escolher a população — a chamada, ou o resultado. **Não há padrão implícito**: sem escolher, o
   botão não gera.
3. Baixar.

**Conferir no arquivo**, e não no código:

- uma aba só, chamada `Import_ModeloCefor`
- 34 cabeçalhos em `A1:AH1`, com `ENDEREÇO` e `NÚMERO` **acentuados**
- dados a partir da linha 2, **sem** linha de exemplo
- uma linha por convocado, e nenhuma linha artificial

---

## C2 — O que o Excel costuma estragar *(`FR-437`, `SC-144`)*

Com um convocado cujo CPF começa por zero:

| Célula | Esperado | O que erra se o formato não for `@` |
|---|---|---|
| `CPF` | `01234567890` | vira `1234567890` — o zero some |
| `DATA_NASCIMENTO` | `12/07/1994` | vira `34527`, o serial do Excel |
| `ZONA_ELE` | `034` | vira `34` |
| `CEP` | `29040-860` | vira número, e o hífen some |

**Abrir o arquivo e reler**, não confiar na visualização: é a ida e volta que prova.

---

## C3 — As lacunas, ditas antes do download *(US2, `FR-439`, `FR-452`)*

Antes de baixar, a tela mostra o resumo. Conferir que ele nomeia:

- **`COD_CURSO`, `COD_TURNO`, `COD_POLO`** — *"vocabulário do sistema acadêmico, preencher no
  destino"*, e **não** como erro
- **`RENDA_PER_CAPITA_PNP`** — o aviso da `FR-452`, que aparece **em toda geração**, inclusive numa
  sem nenhuma outra lacuna: a coluna traz faixa da **soma da família** num campo que o destino define
  como **por pessoa**
- **`COR`**, com o nome de quem declarou **indígena** (`FR-440`)

**Se o aviso da renda não estiver lá, o cenário falhou** — mesmo que o arquivo esteja perfeito. Ele é
o que impede o número de viajar sem etiqueta.

---

## C4 — A geração que se recusa *(US3, `FR-435`, `FR-441`)*

| Tentativa | Esperado |
|---|---|
| População com alguém **sem requerimento enviado** | recusa, **nomeando quem falta** |
| População com um **rascunho** | ele não entra; a recusa diz que ninguém declarou aquilo |
| Edital que **não exige** requerimento | recusa dizendo isso — e **não** um arquivo de zero linhas |
| Modalidade com `code` desconhecido | recusa, nomeando **o código e o Edital**; a grafia publicada não é reescrita |

---

## C5 — O que não se consegue fazer

- **Gerar sem `matricula:exportar`**, inclusive colando o endereço direto: recusado (`SC-150`).
- **Gerar de um Edital fora do escopo do ator**: 404, indistinguível de inexistente.
- **Encontrar o arquivo no servidor depois de baixar**: ele não existe (`FR-456`). Procurar no
  armazenamento faz parte do cenário.

---

## C6 — O mesmo arquivo, duas vezes *(US4, `FR-446`)*

Gerar, baixar, gerar de novo sem mudar nada, e **comparar célula a célula**. Iguais.

Depois: corrigir o requerimento de uma pessoa pelo portal, gerar de novo. O arquivo traz o
**vigente**, e o registro da geração guarda qual era.

---

## C7 — A jornada inteira, sem shell *(Princípio VI)*

**É este o cenário que decide se a feature está entregue.** Do começo ao fim, só pelo navegador:

1. Entrar em `/gestao/` com papel que tem `matricula:exportar`.
2. Abrir o Edital com convocados.
3. Encontrar a opção **no menu do Edital** — sem saber a URL de cor.
4. Escolher a população.
5. Ler o resumo das lacunas.
6. Baixar o arquivo.
7. Abrir o arquivo e conferir uma linha contra o dossiê da pessoa.

**Nenhum passo pode exigir `manage.py`, `psql` ou chamada a função.** A Constituição é explícita:
*"demonstrar por chamada manual aquilo que o canal do ator não oferece NÃO satisfaz esta
exigência"*.

---

## C8 — As varreduras

```bash
cd backend && make DB_NAME=ps_demo_031 lint check test-pg
```

| Varredura | O que ela pega aqui |
|---|---|
| `test_citacoes_de_requisito.py` | `FR-`, `SC-`, `UX-` e `D-` desta spec que não resolvam |
| `test_sem_dado_pessoal_da_amostra.py` | qualquer dado da linha `2` da planilha que tenha entrado como fixture |
| `make provisionar` | precisa dizer **`32 de 32`** — o registro de geração é append-only |
| Nenhum app importa `matriculas` | é a prova de que a feature continua sendo ponta de leitura |

---

## C9 — A importação de verdade *(`SC-143`)*

**Fora deste repositório, e é o único critério que ele não consegue verificar.** Gerar um arquivo de
um Edital de teste e **importar no ambiente do Registro Acadêmico**.

Tudo acima pode estar verde com o arquivo sendo recusado lá: o que este repositório prova é
coerência com a leitura da planilha, e o que decide é o importador.
