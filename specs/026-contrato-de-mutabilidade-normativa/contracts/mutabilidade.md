# Contrato — mutabilidade normativa

O que esta feature expõe não é uma API HTTP: é um **contrato interno** entre três leitores — o
guardião, a interface de Retificação e quem for escrever a próxima spec que acrescente conteúdo
publicado. Este documento diz a forma dele e o que ele obriga de cada lado.

---

## 1. A forma

```python
# backend/processo_seletivo/editais/domain/mutabilidade.py

class Natureza(StrEnum):
    RETIFICAVEL = "RETIFICAVEL"
    NAO_RETIFICAVEL = "NAO_RETIFICAVEL"
    DERIVADO = "DERIVADO"
    ESTRUTURAL = "ESTRUTURAL"


@dataclass(frozen=True)
class Mutabilidade:
    natureza: Natureza
    razao: str = ""


# chave: (coleção, caminho relativo dentro da entidade)
CONTRATO: dict[tuple[str, str], Mutabilidade]
```

**Chave `(coleção, caminho relativo)`** — `("classificationMilestones", "drawMethod/normalization/rule")`,
e não `("classificationMilestones", "rule")`.

O nome sozinho colide **entre** coleções: `name` existe em cinco e `order` em três, e é a correção
que o PR #113 já pagou no rótulo em português. O último segmento colide **dentro** da mesma
coleção: `drawMethod/normalization/rule` e `drawMethod/substitutionRule/rule` cairiam na mesma
chave, e os dois `text` também — o contrato não conseguiria representar nominalmente os dez campos
do seu próprio canário 4.

O caminho relativo é a grafia que `interface/retificacao.py` já usa em `CAMPOS_REGRA`
(`normativeRule/percentage`). Não se inventa convenção nova.

**A razão é obrigatória para `NAO_RETIFICAVEL` e proibida para as outras três.** Construir um
`Mutabilidade(NAO_RETIFICAVEL)` sem razão, ou um `RETIFICAVEL` com razão, é erro na carga do módulo
— não na execução de um teste. Quem escreve o contrato descobre no `import`.

### Uma função de leitura, e uma só

```python
def natureza_de(colecao: str, caminho: str) -> Mutabilidade
```

Levanta `KeyError` para par não declarado. **Não devolve um padrão.** Um padrão seria a decisão
implícita que D-008 proíbe: o campo novo herdaria silenciosamente a natureza mais conveniente, que
é exatamente o estado de hoje com outro nome.

---

## 2. O que o guardião obriga

`tests/contract/test_mutabilidade.py` publica **um** Edital de verdade — o mesmo caminho que
`test_toda_colecao_de_entidades_do_snapshot_esta_declarada` já usa — e percorre recursivamente o
conteúdo canônico.

| Direção | Falha quando | Requisito |
|---|---|---|
| snapshot → contrato | a travessia encontra `(coleção, campo)` que `CONTRATO` não declara | FR-301 |
| contrato → snapshot | `CONTRATO` declara `(coleção, campo)` que a travessia não encontra | FR-302 |
| razão | alguma `NAO_RETIFICAVEL` tem razão vazia | FR-299 |
| alcance | algum `RETIFICAVEL` não é oferecido pelo canal do ator | FR-304 |

A mensagem de falha nomeia o campo e o caminho onde ele apareceu. É o que separa este guardião de
um `assert len(...)`: quem quebrou a suíte precisa ler **qual** decisão faltou, não descobrir que
faltou alguma.

**A travessia é a fonte, e a lista é a consequência** (D-004, R-004). Ninguém mantém à mão o
conjunto de campos; ele sai do Edital publicado. Um campo acrescentado ao conteúdo publicado
derruba a suíte no mesmo commit que o acrescenta — e não no primeiro Edital publicado com ele.

### Onde a travessia para: objeto opaco

**Seis** objetos do conteúdo publicado são opacos — `classificationInformation`, `callInformation`
e os quatro de `normativeRule` (`calculation`, `rounding`, `distribution`, `callRules`). O critério
**não é** ser `JSONField`: é **nada no sistema ler o conteúdo**. A tabela com os leitores está em
[data-model.md](../data-model.md).

O `rounding` do marco e o `parameters` do desempate são `JSONField` e **não** são opacos: a forma
deles é conhecida e cobrada, e o cálculo depende dela. A travessia desce nos dois.

**A travessia não desce neles, e o contrato classifica o objeto inteiro.** Descer produziria um
guardião cujo domínio muda de Edital para Edital: o mesmo campo presente num e ausente noutro faria
a suíte alternar entre falhar por FR-301 e falhar por FR-302 conforme a fixture. A classificação
passaria a depender da amostra, e não da norma.

A lista dos opacos é **declarada**, nunca inferida de o valor ser `dict`: `appealWindow`,
`drawMethod`, `cutRule`, `vacancyReversion`, `normativeRule`, `rounding` e `parameters` também são
objetos, têm forma conhecida, e a travessia desce em todos.

### O alcance do guardião em relação ao que já existe

Hoje o único guardião do gênero está em `tests/contract/test_retificacoes_api.py:101`: compara
`ETAPA_PUBLICADA` com `CAMPOS_ETAPA` da tela, descontando `NAO_SAO_NORMA = {"id", "order",
"scheduleEventId"}`. Ele funciona, e cobre **uma** coleção entre doze. Esta feature não o substitui
por outro mecanismo: generaliza o mesmo argumento para todas, com as três exclusões daquele
conjunto passando a ser naturezas nomeadas (`ESTRUTURAL` as duas primeiras, e a terceira com razão
escrita) em vez de um literal local.

---

## 3. O que a interface obriga

`interface/retificacao.py` continua dona da **apresentação** — rótulo, tipo de controle, ordem dos
campos na tela. Deixa de ser dona de **quais** campos existem.

| Antes | Depois |
|---|---|
| `CAMPOS_*` é a lista autoritativa; um campo esquecido simplesmente não aparece | `CONTRATO` é a lista autoritativa; um campo `RETIFICAVEL` sem apresentação derruba a suíte |
| A ausência de um campo na tela não tem registro | A ausência tem natureza e razão, e a tela a declara (FR-312) |

**Campo de valor fechado não vira caixa de texto** (FR-311). `appealWindow/unit` admite exatamente
`DIAS_CORRIDOS` hoje, e `reserveType` admite `NONE`, `LIMITED`, `UNLIMITED`; publicar por texto
livre o que o domínio depois recusa produz Retificação que falha depois do ato do ator.

**A declaração de exclusão é por bloco de coleção, e não por campo** (R-006). Repetir a mesma frase
sob cada campo do marco é a prática que `test_medida_dos_campos` já reprova no assistente:
explicação que não muda de um cartão para o outro não se imprime uma vez por cartão.

---

## 4. Os quatro canários, campo a campo

O que cada um exercita, e por que os quatro e não um.

### Canário 1 — local do Evento (`schedule` / `location`)

Um campo escalar de texto, e o caso mais simples. Vale como canário por um motivo concreto:
`publicacoes/application/publish_edital.py:261` emite `location` no conteúdo publicado, e
`EVENTO_PUBLICADO` em `editais/domain/validation.py` **não o declara**. Nenhum teste acusa, porque
o guardião de hoje confere coleções e não campos. O campo existe no conteúdo, governa onde a pessoa
comparece, e não tem nem forma declarada nem decisão de mutabilidade.

A 021 tem como critério de aceitação uma Retificação que altera o local; a tela não tem o campo.

### Canário 2 — requisitos de participação (`profiles` / `requirements`)

Uma **coleção de texto** dentro de uma entidade. Exercita o que o endereçamento por identidade da
004 não resolve sozinho: item de lista não tem identidade estável, e retificar "o terceiro
requisito" não é endereçar — é contar. O desenho precisa dizer se a correção substitui a lista
inteira ou um item, e a resposta muda o que o ato registra.

Decide quem pode concorrer. É a natureza com mais consequência e a forma mais simples.

### Canário 3 — janela recursal (`classificationMilestones` / `appealWindow`)

Um **objeto composto** com três campos de naturezas diferentes: `admits` (booleano que governa se
os outros dois existem), `durationDays` (inteiro positivo) e `unit` (lista fechada de um valor
só). Exercita FR-311 e a coerência entre campos do mesmo objeto: `admits: false` com
`durationDays` declarado é contradição que `_validar_janela_recursal` já recusa na elaboração, e a
Retificação precisa recusar pelo mesmo critério.

Governa um direito com prazo. Corrigi-lo cedo demais ou tarde demais tem efeito sobre quem recorre.

### Canário 4 — método do sorteio (`classificationMilestones` / `drawMethod`)

**Dez campos**, e é a conta que fecha com a spec — todos na coleção `classificationMilestones`,
com estes caminhos relativos:

```text
drawMethod/algorithm              drawMethod/normalization/rule
drawMethod/source                 drawMethod/normalization/text
drawMethod/occurrence             drawMethod/substitutionRule/rule
drawMethod/occurrenceAt           drawMethod/substitutionRule/text
drawMethod/derivation             drawMethod/qualifyingStageId
```

Os dois últimos pares são o que quebra a chave por último segmento: `normalization` e
`substitutionRule` são objetos, o validador cobra `rule` e `text` de cada um
(`editais/domain/perfis.py:283`), e os quatro colidiriam dois a dois.

É o caso onde a contradição de hoje é mais visível: a 021 determina que alterar o método é
Retificação, a própria tela do sorteio manda retificá-lo, e a Retificação não oferece um único dos
dez.

A fronteira do congelamento **já existe** e não é trabalho desta feature (R-005):
`sorteios/models.py:48` grava `metodo_hash` em `RelacaoDeHabilitados` no congelamento e
`models.py:213` o copia e confere no `Sorteio`. Retificar o método vigente não alcança relação
congelada porque a relação não relê o método — ela carrega o seu. FR-309 é garantido
estruturalmente; o que falta é o teste de fronteira que o declare, e os campos na tela.

---

## 5. O que o contrato NÃO faz

- **Não declara a forma** das coleções aninhadas em `validation.py`. Enumerar um campo e declarar o
  tipo dele são coisas diferentes, e a segunda tem razão escrita para não ter sido feita (015,
  T-009). O limite fica registrado; a spec não o fecha. É o que a FR-300 reescrita diz: enumerar
  não depende de declarar forma.
- **Não faz todo campo aparecer na tela** (D-006). Ausência deliberada continua ausência, desde que
  justificada por norma e protegida por teste.
- **Não reclassifica Edital publicado** (FR-314). Mudar a natureza de um campo é decisão nova, e
  vale do commit para a frente.
- **Não decide nada sozinho** (D-008). Cada entrada de `CONTRATO` é escrita nominalmente por uma
  pessoa, em revisão de código. Não há inferência por nome, tipo ou coleção.
