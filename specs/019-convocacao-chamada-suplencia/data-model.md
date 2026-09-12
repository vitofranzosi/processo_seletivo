# Modelo de dados — `019` Convocação, Chamada e Suplência

**Fase 1 do plano.** Quatro entidades novas em `convocacao`, uma em `ocupacao` (a porta), e uma
linha nova na constraint de `resultados`. **Todas as tabelas novas são append-only**, com gatilho
*e* privilégio ausente — as duas camadas que a Constituição exige e que o provisionamento conta no
`N de M`.

---

## 1. `Convocacao` — o ato que chama uma pessoa para a vaga

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `edital` | FK `processos.Edital`, `PROTECT` | |
| `perfil_id` | UUID | identidade publicada, **não** FK — a mesma razão da `016` |
| `marco_id` | UUID | |
| `lista_id` | UUID nulo | `NULL` = ampla concorrência, a grafia do resto do sistema |
| `inscricao` | FK `inscricoes.Inscricao`, `PROTECT` | |
| `especie` | texto | `VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR` — e **não** `REGULARIZACAO`, que é espécie de **desfecho**: o mesmo termo para ato e desfecho confunde tela e código |
| `vencimento` | datetime nulo | informado por quem convoca (`FR-269`); nulo = Edital sem prazo |
| `fundamento` | texto | obrigatório; o *"no interesse da Administração"* do 77 entra aqui |
| `apuracao` | FK `ocupacao.ApuracaoDeOcupacao`, `PROTECT` | a proveniência do déficit (`FR-294`) |
| `ato_de_ordenacao_id` | UUID | proveniência da ordem lida |
| `corte_id` | UUID nulo | proveniência da faixa lida; nulo quando o marco não corta |
| `versao` | FK `publicacoes.VersaoConsolidada`, `PROTECT` | o conteúdo publicado que valia |
| `convocacao_anterior` | FK `self`, nula, `PROTECT` | sucessão; correção nunca é `UPDATE` |
| `motivo_da_sucessao` | texto | obrigatório no sucessor |
| `criado_em`, `criado_por` | | |

**Constraints.**

- **Uma convocação vigente por pessoa e recorte** — unicidade parcial da **raiz** e do **sucessor**,
  nas três metades que o `NULL` do `lista_id` obriga (é o par que a `015`, a `017` e a `016` já
  escreveram; em SQL `NULL = NULL` não é verdadeiro).
- `ck_convocacao_especie` — espécie entre as três nomeadas.
- `ck_convocacao_sucessao` — sucessor tem `motivo_da_sucessao` não vazio; raiz tem vazio.
- **Vigência não é coluna.** Vigente é a convocação que ninguém sucedeu, como a apuração da `016`
  e o corte da `014`. Coluna exigiria `UPDATE`, proibido nesta tabela.

## 2. `DesfechoDaConvocacao` — o que a pessoa respondeu, ou o que a Administração concluiu

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `convocacao` | FK `Convocacao`, `PROTECT` | **um por convocação** (`FR-273`) |
| `especie` | texto | os sete da `R-006` da pesquisa |
| `fundamento` | texto | obrigatório |
| `atestado` | FK `AtestadoDeFatoExterno`, nula, `PROTECT` | **obrigatória** na inércia |
| `resultado_sucessor` | FK `resultados.ResultadoEtapa`, nula, `PROTECT` | presente na regularização |
| `efeito` | FK `ocupacao.EfeitoDeOcupacao`, nula, `PROTECT` | o que foi escrito na porta |
| `registrado_em`, `registrado_por` | | |

**Constraints.**

- `uq_desfecho_por_convocacao` — unicidade em `convocacao`.
- `ck_desfecho_especie` — espécie entre as sete.
- `ck_desfecho_inercia_exige_atestado` — `especie = INERCIA` ⇒ `atestado` presente. É a `FR-277`
  dita por forma, e não apenas por código: fato externo sem atestante não entra.
- `ck_desfecho_regularizacao_exige_sucessor` — `especie = REGULARIZACAO` ⇒ `resultado_sucessor`
  presente. É a `D-008` dita por forma.

**Espécies, e o efeito de cada uma** — a tabela está na `R-006` da [pesquisa](research.md). Duas
delas incluem (aceite, regularização); quatro excluem; a reclassificação exclui **e** move na fila.

## 3. `AtestadoDeFatoExterno` — o que aconteceu fora, e quem atestou

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `inscricao` | FK, `PROTECT` | |
| `especie` | texto | `NAO_ACESSO_AO_AMBIENTE`, `AUSENCIA_NA_PRIMEIRA_SEMANA`, `NAO_ENTREGA_PRESENCIAL` |
| `conclusao` | texto | o que a pessoa competente concluiu |
| `referencia_do_prazo` | texto | o prazo que o Edital declarou, **copiado do conteúdo publicado** |
| `atestado_em`, `atestado_por` | | quem atestou é obrigatório (`D-004`) |

**O sistema não detém o artefato** e não infere o fato: registra que alguém competente concluiu.

## 4. `ComunicacaoEmitida` — que o sistema enviou, não que chegou

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `convocacao` | FK, `PROTECT` | |
| `forma` | texto | `PUBLICACAO` ou `MENSAGEM_INDIVIDUAL`, lida do conteúdo publicado |
| `destinatario` | texto | vazio quando a forma é publicação |
| `enviado_em` | datetime nulo | **nulo enquanto o envio não teve sucesso** |
| `resultado` | texto | `ENVIADA` ou `FALHA` |
| `detalhe_tecnico` | texto | registro da falha, sem dado pessoal |

**O prazo corre de `enviado_em`** (`D-009`). Nenhum campo diz recebido, lido ou entregue — e a
`UX-039` varre a tela, porque o campo que não existe não impede a prosa de mentir.

## 5. `EfeitoDeOcupacao` — a porta, e ela mora em `ocupacao`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `edital` | FK `processos.Edital`, `PROTECT` | |
| `perfil_id`, `marco_id`, `lista_id` | UUID / UUID / UUID nulo | o recorte de sempre |
| `inscricao_id` | UUID | **identidade, não FK** — `ocupacao` não depende de `inscricoes` por isto |
| `especie` | texto | `EXCLUSAO` ou `INCLUSAO` |
| `fundamento` | texto | obrigatório |
| `ato_de_origem_id` | UUID | o desfecho que o produziu, **opaco** (`R-003`) |
| `rotulo_da_origem` | texto | *"desfecho de convocação"* — para a trilha ser legível |
| `registrado_em`, `registrado_por` | | |

**Por que aqui e não em `convocacao`:** FK de `ocupacao` para a feature nova inverteria a
dependência no grafo de migrations, e a `016` deixaria de migrar sozinha. `ato_de_origem_id` é UUID
pela mesma razão.

**Constraints.**

- `ck_efeito_especie` — entre as duas.
- **Nenhuma unicidade por inscrição e recorte.** Duas exclusões da mesma pessoa em ciclos diferentes
  são fatos distintos; o que a apuração faz é **conjunto**, não soma — e é o que evita o `−2` que a
  `R-001` nomeia.

## 6. A alteração em `resultados`: a quinta linha legítima

`Origem` ganha `REGULARIZACAO`, e `ck_resultado_origem` passa a admitir cinco linhas:

```
raiz por avaliação        AVALIACAO      · avaliação sim · anterior não
sucessor por reavaliação  AVALIACAO      · avaliação sim · anterior sim
raiz por ocorrência       OCORRENCIA     · avaliação não · anterior não
sucessor por recurso      RECURSO        · avaliação não · anterior sim · decisão sim
sucessor por regularização REGULARIZACAO · avaliação não · anterior sim · desfecho sim   ← nova
```

**A fonte jurídica continua obrigatória em todo sucessor** — o que muda é qual. No sucessor por
regularização ela é o desfecho da convocação, e não uma `DecisaoRecurso` (`R-005`). O gatilho que
confere Resultado contra a fonte ganha o ramo correspondente.

## 7. A mudança na apuração da `016`

**`apurar` deixa de receber conjunto e passa a receber sequência ordenada** (`R-001`):

```
antes   apurar(publicadas, dentro_da_faixa, habilitadas, movimentos_lidos, ocupantes_da_ampla)
depois  apurar(publicadas, progrediram_em_ordem, habilitadas, movimentos_lidos,
               ocupantes_da_ampla, efeitos_lidos)
```

`ocupadas` passa a ser `|titulares habilitados − excluídos ∪ incluídos|`, limitado a `efetivas`;
titular inicial é quem está entre as primeiras `efetivas` posições **por pessoa**. `efeitos_lidos`
são os que **aquela** apuração leu — congelamento, pela mesma razão que `movimentos_lidos` já o é.

**A apuração ganha causa de obsolescência nova:** efeito posterior à apuração vigente. É a quinta da
lista, ao lado de ordem sucedida, corte obsoleto, quadro retificado e movimento posterior.

## 8. Conteúdo publicado: degrau 15

| Chave | Onde | Significado |
|---|---|---|
| `callForm` | Perfil publicado | `PUBLICATION` ou `INDIVIDUAL_MESSAGE`; **ausente = não declarou** |

**As duas formas são vocabulário do conteúdo publicado**, e moram onde o publicado as define —
`publicacoes/domain/vocabulario_da_regra.py` é o precedente —, não em `convocacao/domain/nomes.py`.
Duas grafias do mesmo valor em módulos diferentes é como uma delas fica para trás numa renomeação.

Degrau **15** eleva os Editais anteriores com a chave ausente, o documento passa a exibi-la quando
declarada, e `"/profiles/*/callForm"` entra no catálogo de Retificação **antes** da primeira
emissão — a lição que a `025` registrou como a que não teria conserto.
