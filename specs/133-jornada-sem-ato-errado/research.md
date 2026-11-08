# Research: A jornada não aponta o ato errado

Decisões técnicas do plano. As decisões de produto estão na spec (D-001 a D-005). Os caminhos são
relativos a `backend/processo_seletivo/`. Tudo foi lido na `main` em `da566ff2`.

## R-001 — A regra mora em `classificacao`, pura, com uma camada de aplicação para a recusa

**Decision.** São dois módulos.

- `classificacao/domain/marco_intermediario.py` recebe o Perfil do conteúdo (dict) e o id do marco.
  Ele devolve o marco posterior que lê a Etapa governada, ou `None`. A Etapa governada sai de
  `faixa.etapa_governada(marco["cutRule"])`, e o marco que a lê é qualquer outro marco do Perfil com
  essa Etapa em `stages`.
- `classificacao/application/marco_intermediario.py` monta o impedimento a partir do conteúdo vigente
  e do Perfil: a frase, o nome do marco, o nome da Etapa e o id do marco que apura. Ele também
  levanta a recusa (`DomainError("apuracao_em_marco_intermediario", frase, 409)`).

**Rationale.** É o desenho da `128` (`ordem_sem_resultado.py`): a regra é pura e testável sem banco,
e a aplicação dá a frase e a recusa. Os quatro comandos, a condução, a derivação e as três telas
leem a mesma função (FR-4531).

O conteúdo vem de quem chama, sem consulta nova:

- os comandos já leem a versão vigente (`effective_version`);
- a condução e o andamento já têm `conteudo`.

`etapa_governada` e `stages` são não retificáveis (`editais/domain/mutabilidade.py:326, 391`). Por
isso a resposta não depende do instante.

**Alternatives considered.**

- Um campo `intermediario` no marco: é estado novo e configuração duplicada, e a constituição (II)
  exige fonte única.
- Ler a ordem dos marcos no Perfil: rejeitada em D-001.
- Pôr a regra em `ocupacao`: `convocacao` e `interface` também a leem, e o conceito é de marco.

## R-002 — Onde cada comando recusa

**Decision.**

| Comando | Ponto | Por quê |
|---|---|---|
| `ocupacao/application/emissao.py`, `_apurar` | logo depois de `effective_version`, antes de qualquer leitura de corte ou gravação | É a conta única da tela da ocupação, do gesto "Apurar" da condução e do efeito de desfecho e de acréscimo (`emitir_sucessora_por_efeito`). Uma recusa alcança os três |
| `ocupacao/application/acrescimo.py`, `acrescentar_vagas` | sob a trava, antes de `_previa` | O acréscimo grava o registro antes de pedir a apuração seguinte. Sem a recusa própria, o registro sairia mesmo com a apuração recusada |
| `ocupacao/application/causar_faixa.py`, `causar_faixa_seguinte` | no início | Só existiria com apuração legada no marco intermediário, mas é ato que alcança pessoas (R1) |
| `convocacao/application/convocar.py`, `convocar` | sob a trava, antes da leitura do contexto do recorte | É a porta da chamada individual e da correção da `120` (`correcao=`) (FR-4534 e a clarificação de 08/11) |
| `convocacao/application/convocar.py`, `convocar_em_sequencia` | no início | **Corrigido na implementação:** o lote de titulares (`fluxo.convocar_titulares`) não passa por `convocar`, e grava pela própria função. São os dois únicos pontos que criam `Convocacao`. O teste do lote acusou a lacuna |

`desfechar`, `comunicar`, `atestar` e a conferência de documentos **não** recusam (D-002, FR-4535).

**Rationale.** A recusa sob `comando_de_comissao` sobe como `DomainError`, e o contexto desfaz a
transação, a reserva de idempotência inclusive. É o mesmo caminho das recusas existentes, como
`ordem_nao_vigente` (FR-4536).

**Alternatives considered.** Recusar só nas views: a regra continuaria acessível pela API e pela
conduta do marco, o oposto de R1.

## R-003 — O desfecho num marco intermediário legado continua

**Decision.** Nada muda em `desfechar._apuracao_seguinte`. A recusa que `_apurar` levanta já é
capturada (`except DomainError`) e vira `apuracaoPendente` com o código e a frase. O desfecho é
gravado.

**Rationale.** É D-002: encerrar o que existe continua possível. Um teste prova o desfecho de uma
convocação legada num marco intermediário.

## R-004 — A previsão começa na célula da condução

**Decision.**

- `conducao_do_marco._celula_da_apuracao` devolve `{"estado": "nao_se_aplica", "nota": <frase curta>,
  "url": ""}` quando o marco é intermediário, mesmo havendo apuração legada.
- `_alcance_da_apuracao` põe cada recorte do marco como `IMPEDIDO`, com a frase da recusa.
- `situacao_da_apuracao` da `127` já devolve *Não se aplica* quando a célula diz, e
  `situacoes_da_convocacao` já devolve *Não se aplica* quando a apuração diz. A contagem "apuração N
  de M" já exclui *Não se aplica*.
- As views `ocupacao` e `convocacao` recebem `marco_intermediario` (frase, nome e URL do marco que
  apura). Os templates trocam os formulários pelo aviso, e o que já existe continua legível.

**Rationale.** Uma mudança na célula basta para a condução, o nível 1, o nível 2 e o "Próximo nesta
lista", porque todos leem a célula. É a lição da `103` e da `104`: uma derivação só.

**Alternatives considered.** Uma regra nova em `andamento._pontos_do_marco` para não criar os pontos
do marco intermediário: esconderia a publicação, que continua legítima, e duplicaria a regra.

## R-005 — A espera do corte lê a aferição da definitiva, por uma função pura

**Decision.**

- **A função.** `andamento.espera_do_corte(marco, *, divulgado, definitiva)` é pura. Ela recebe se o
  resultado da lista já foi divulgado e a aferição da definitiva (`{"nivel", "codigo", "mensagem",
  "ate"}`), e devolve `None` ou `{"ate", "razao"}`. As regras:
  - o marco sem recurso declarado (`appealWindow.admits` falso) dá `None`;
  - sem divulgação, a espera é "o prazo de recurso começa com a divulgação do resultado";
  - com divulgação e aferição em espera (`JANELA_ABERTA`, `RECURSO_PENDENTE`, `REAVALIACAO_PENDENTE`,
    `PROVIDENCIA_PENDENTE`, o mesmo conjunto de `situacao_do_resultado`), a espera usa a data e a
    frase da aferição;
  - nos demais casos, `None`.
- **No andamento.** `_resultado` passa a devolver também o que leu da aferição. `_marco` deriva o
  resultado **antes** do corte e entrega a espera a `situacao_do_corte`, que devolve `AGUARDA`
  (`responsavel=""`, `recomendacao=True`, `ato="Emitir o corte"`, a razão com a consequência, `ate`).
- **A `Celula`.** Ganha `recomendacao: bool = False`. É campo de apresentação, e não estado.
  `_providencia.html` desenha a marca "recomendação" quando o campo está ligado.
- **O "Próximo nesta lista".** `da_lista` prefere, entre as abertas, uma da pessoa; sem ela, uma
  praticável (*Pendente* ou *Obsoleto*) de qualquer papel; e só então a primeira em espera
  (FR-4543).
- **A tela do corte.** A view `corte` chama `publicabilidade.aferir` para a ordem vigente da lista,
  com a natureza da definitiva quando já há preliminar, e passa o resultado pela **mesma**
  `espera_do_corte`. A consequência sai antes do formulário de emissão. O comando não muda (FR-4545).

**Rationale.** A FR-4546 pede uma regra só. A aferição já é a autoridade sobre a janela e as
pendências (`divulgacao/domain/publicabilidade.py`), e a célula do resultado já a lê (`_resultado`).
Uma segunda leitura do prazo divergiria na primeira mudança dele.

**Alternatives considered.** Calcular o prazo a partir da primeira publicação dentro do andamento: é
uma segunda regra. Recusar no comando: rejeitado por R2.

## R-006 — `em_aberto` conta só a chamada que ainda não ocupa

**Decision.** Em `andamento._Leitor._convocacao`, a chave passa a ser esta:

```python
"em_aberto": sum(
    1
    for lin in linhas
    if lin["desfecho"] is None and lin["convocacao"].especie != nomes.VAGA_INICIAL
)
```

**Rationale.** A convocação `VAGA_INICIAL` é de titular, e o titular conta como ocupado desde a
apuração (`ocupacao/domain/apuracao.py`, `titulares_iniciais`). Descontá-la de `faltando` era contar
a mesma vaga duas vezes. `SUPLENCIA` e `PARA_REGULARIZAR` ainda não ocupam: elas respondem pela vaga a
ocupar, e descontá-las evita a chamada dupla (D-004). Na sonda de 05/01, `faltando=1`, a única linha
em aberto é `VAGA_INICIAL` (Rafael), então `sem_chamada=1`, e a fila tem Diana.

## R-007 — A ordem obsoleta prevalece sobre a publicação feita

**Decision.** Em `situacao_do_resultado`, a primeira verificação passa a ser `ordem.situacao ==
OBSOLETO`, que dá `DEPOIS` com a razão atual, qualquer que seja o estado da publicação.

O corte obsoleto continua pela aferição: com preliminar feita, ela dá `IMPEDIMENTO` com o código do
corte obsoleto, e a célula sai `IMPEDIDO`, com `quem_resolve=CONDUZ`. É o "não *Pendente*" que a
FR-4551 e a FR-4552 exigem.

**Rationale.** É o defeito da sonda T3. Com a preliminar feita, `_resultado` pula a aferição quando a
ordem está obsoleta e cai no ramo "preliminar sem definitiva", que diz *Pendente*.

**Ajuste na spec.** A FR-4551 dizia *Depois* também para o corte obsoleto. O que a aferição devolve é
*Impedido* com a razão, que cumpre a FR-4552, e é a mesma frase da prévia de publicação. A spec é
ajustada para "*Impedido* ou *Depois*, com a razão, e nunca *Pendente*".

## R-008 — A frase do corte fixo, com o inventário da FR-1398 da `069`

**Decision.** `pdf.frases_do_corte(marco, etapas, *, sem_cadastro, com_reservadas=False)`. Com
`com_reservadas`, o alvo fixo diz "os N (por extenso) primeiros classificados de cada lista de
concorrência", e o caso de um diz "o 1 (um) primeiro classificado de cada lista de concorrência".
`com_reservadas` é verdadeiro quando o Perfil declara ao menos uma modalidade que não é a ampla.

**Inventário dos leitores** (a FR-1398 da `069`):

| Leitor | Classe | Como cumpre a FR-1397 da `069` |
|---|---|---|
| `pdf.py`, documento plano (linha 2538) | **congelado na publicação** | Os bytes do documento publicado não se regeneram. A frase nova sai só em documento composto depois, inclusive o consolidado de Retificação, que é documento novo (o *Assumption* da `067`) |
| `apresentacao.py`, documento por perguntas (linha 1133) | **congelado na publicação** | Igual |
| `interface/revisao.py:607` | **reconstruído na exibição** | A Revisão "MAY usar a redação nova", pois descreve a mesma regra da versão aplicável, e a frase nova diz o que o motor faz desde sempre |

O ato de ordenação, o portal e os avisos **não** leem `frases_do_corte`.

**Rationale.** A regra não muda, só a frase. A comparação de alterações da Retificação
(`publicacoes/domain/alteracoes.py`) compara o conteúdo, e não a prosa. Um teste prova que a
Retificação sem mudança no corte não aponta alteração do corte (SC-1426).

**Alternatives considered.** Uma redação 3, com versão gravada na publicação: é muito maior que a
mudança, e a `067` corrigiu frases da redação 2 com o mesmo princípio.

**Risco a conferir na implementação.** Testes de documento que comparam bytes ou texto de cenários
com alvo fixo e reservadas (`tests/unit/publicacoes/test_documento_da_auditoria_*`,
`test_redacao_*`). Cada expectativa alterada é listada em `verificacao.md`, com o motivo.

## R-009 — A regressão dos quatro instantes, por uma fixture reduzida do Edital 900

**Decision.** A fixture `tests/fixtures/marco_intermediario.py` monta, pelos mesmos comandos de
`doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/reproduzir.py` e com o relógio de
`tests.fixtures.relatorio.em`, um Perfil com:

- uma Etapa pontuada, a Prova;
- o marco 1, que lê a Prova, com corte fixo por lista que governa a Entrevista, e recurso de 3 dias;
- a Entrevista;
- o marco 2, que lê a Prova e a Entrevista, com corte pelo quadro, mais suplentes;
- as listas ampla e PcD;
- seis a oito inscrições.

Ela expõe paradas: depois da ordem, depois da preliminar, depois do recurso deferido, depois da
apuração do marco 2 e depois de uma desistência com titular pendente. Os testes de derivação chamam
`andamento.do_edital` em cada parada e conferem o que a sonda do estudo conferiu (FR-4557).

**Rationale.** A suíte não tem cenário com dois marcos ligados por Etapa governada. Os testes da
`127` provam a família P3 só nas funções puras. Os bancos de fase do estudo servem à demonstração, e
não à suíte. Uma versão reduzida mantém o tempo da suíte e cobre os quatro defeitos.

## R-010 — A frase e a nota

**Decision.**

- **A recusa** (contrato em [contracts/recusas.md](contracts/recusas.md)): "A {nome do marco} decide
  quem participa da Etapa {Etapa governada}: ela não apura vagas nem convoca. As vagas são apuradas
  e convocadas na {nome do marco que lê}."
- **A nota da célula:** "decide quem vai à {Etapa}; as vagas são da {marco que lê}".
- **A espera do corte:**
  - com o prazo aberto: "Aguarde o fim do prazo de recurso, até {data}: o corte decide quem participa
    da {Etapa}, e um recurso deferido o tornaria obsoleto, com sucessão motivada";
  - sem governada: "…decide quem segue no processo…";
  - sem divulgação: "O prazo de recurso começa com a divulgação do resultado; o corte depois dele
    evita sucessão".

**Rationale.** As frases dizem o que o marco decide, o caminho e a consequência, sem identificador
interno (FR-4537). Partem das maquetes A1 a A3 do estudo.
