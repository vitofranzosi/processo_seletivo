# Contrato — Requerimento de Matrícula (`029`)

**Fase 1** · 16/09/2026. Três fronteiras: o **conteúdo publicado**, as **rotas** e o **contrato de
saída** que a exportação futura consome.

---

## 1. Conteúdo publicado

### 1.1 Forma

Objeto na raiz, ausente quando o Edital não exige requerimento.

```json
{
  "matriculationRequest": {
    "moment": "AT_ENROLLMENT",
    "declarationText": "Declaro, sob as penas da Lei, que as informações fornecidas…"
  }
}
```

| Campo | Tipo | Domínio |
|---|---|---|
| `moment` | string | `AT_ENROLLMENT` \| `AT_CALL` |
| `declarationText` | string | não vazio |

**A chave está sempre presente; `null` é o "não exige".**

```json
{ "matriculationRequest": null }
```

Não existe `"NOT_REQUIRED"` como terceiro valor, e **não se omite a chave** (`FR-368`): é a forma que
`publish_edital` já pratica em `vacancyReversion` — objeto quando declarado, `null` quando não. Duas
grafias do mesmo fato seriam a contradição que a regra evita.

### 1.2 Conferência na publicação

| Achado | Severidade | Quando |
|---|---|---|
| `matriculation_request_without_declaration` | **erro impeditivo** | `moment` declarado e `declarationText` vazio ou ausente (`FR-407`, `SC-136`) |

Condicionado ao ato de publicação, pelo parâmetro que `validate_for_publication` já recebe. **Não
vale em Retificação** — uma exigência impeditiva sem esse recorte bloquearia Retificações que nada
têm com o requerimento, que é a lição que a `027` deixou escrita.

### 1.3 Mutabilidade

| Caminho | Natureza | Retificável por |
|---|---|---|
| `/matriculationRequest/moment` | **não retificável** | — |
| `/matriculationRequest/declarationText` | **retificável** | `/matriculationRequest/declarationText` |

O aceite guarda o resumo do texto **exibido** (`FR-393`), de modo que retificar a declaração não
reescreve o que ninguém leu.

---

## 2. Rotas

### 2.1 Área do Candidato

| Método | Rota | Efeito |
|---|---|---|
| `GET` | `/inscricoes/<uuid>/requerimento` | a tela, no estado em que estiver |
| `POST` | `/inscricoes/<uuid>/requerimento` | grava o rascunho; `acao=enviar` envia |
| `GET` | `/inscricoes/<uuid>/requerimento/anterior/<uuid>` | um requerimento sucedido, somente leitura (`UX-059`); o segundo identificador MUST ser resolvido **dentro da cadeia** da Inscrição titular |
| `POST` | `/requerimento/cep` | consulta de referência, **com o CEP no corpo** e proteção CSRF |

**Titularidade em todas**, por `_inscricao_do_titular`; a recusa é indistinguível de inexistente
(`FR-399`). **Nenhum dado pessoal no endereço** — o identificador é o da Inscrição, que é a
convenção que o portal já pratica.

**A consulta de CEP não é exceção de autorização**: ela exige sessão de candidato, e devolve apenas
dado público de referência. Sem sessão, recusa — uma rota aberta de consulta de CEP seria um serviço
de terceiros hospedado por engano.

**E ela é `POST`, com o CEP no corpo.** A primeira redação deste contrato usava
`GET /requerimento/cep/<cep>`, e isso contradizia a própria `FR-401`: endereço em URL viaja para log
de servidor, histórico de navegador e cabeçalho de referência sem que ninguém decida isso. A
varredura da `FR-401` reprovaria a rota que este contrato oferecia.

### 2.2 Recusas

| Código | Quando | HTTP |
|---|---|---|
| `matriculation_request_not_required` | o Edital não declara requerimento (`FR-371`) | 404 |
| `matriculation_request_unavailable` | declarado *na convocação*, sem chamada em aberto (`FR-373`) | 409 |
| `matriculation_request_closed` | a chamada foi desfechada; leitura permanece, escrita não (`FR-374`, `FR-411`) | 409 |
| `matriculation_request_already_sent` | tentativa de alterar o enviado (`FR-396`) | 409 |
| `successor_not_authorized` | sucessor sem chamada em aberto (`FR-408`) | 409 |
| `declaration_not_accepted` | envio sem aceite (`FR-394`) | 422 |
| `edital_updated` | o Edital foi retificado, ou o texto da declaração mudou, entre a exibição e o envio (`FR-393`) | 409 |
| `field_required` / `field_constraint_violated` | campos | 422 |

E uma recusa que **não é desta rota**, e sim da submissão da inscrição:

| Código | Quando | HTTP |
|---|---|---|
| `matriculation_request_required` | `POST /inscricoes/<uuid>/enviar` com o momento *na inscrição* e sem requerimento enviado (`FR-370`) | 422 |

**`edital_updated` é reaproveitado, e não inventado.** A submissão da inscrição já recusa com esse
código o mesmo fato — o Edital mudou entre a leitura e a confirmação. Um segundo nome obrigaria a
tela a tratar duas palavras como sinônimas.

**404 para *não exigido*, e 409 para *ainda indisponível***: a primeira é ausência de recurso; a
segunda é recurso que existe e ainda não abriu. Colapsá-las diria a quem ainda tem chance que ela não
tem — que é a distinção que a tela de convocação já é obrigada a fazer.

### 2.3 Gestão

| Método | Rota | Permissão |
|---|---|---|
| `GET` | `/gestao/inscricoes/<uuid>` (dossiê, bloco novo) | `inscricao:consultar` |

**Sem rota de listagem** (`FR-400`): superfície nova sobre dado pessoal sem jornada que a peça.

### 2.4 Trilha

| Operação | Quando | Agregado |
|---|---|---|
| `REQUERIMENTO_ENVIAR` | envio de requerimento raiz | o **requerimento** |
| `REQUERIMENTO_SUCEDER` | envio de sucessor | o **requerimento** |
| `ALTERAR_REQUERIMENTO` | quem elabora declara momento e texto | o **Edital** |

**O agregado do envio é o requerimento, e não a Inscrição.** `record_event` lê `status` e `revision`
do que recebe: com a Inscrição ali, o registro diria o estado e a revisão *dela* — que este ato não
muda — e a trilha afirmaria, em duas colunas, algo que não aconteceu. A Inscrição, o Edital, a versão
aceita e o resumo da declaração entram **por escrito** na razão, que é o que a `FR-397` exige.

**As três têm rótulo em `interface/views.py::OPERACOES`.** A varredura global — `test_trilha_legivel`
— coleta apenas literais `operation="…"`; as duas primeiras chegam como **constante** e escapam
dela. O rótulo é conferido por asserção própria em
`tests/integration/requerimentos/test_auditoria.py`, e a cegueira da varredura fica registrada em
`requerimentos/domain/nomes.py` como achado — não como escopo desta feature.

---

## 3. Contrato de saída — o que a exportação futura vai compor

**Não é implementado aqui** (`FR-404`). É o mapa que a `FR-403` manda manter, e o artefato que a
`SC-133` verifica.

| Coluna | Origem | Campo |
|---|---|---|
| `INSC` | inscrição | `Inscricao.protocolo` — **formato divergente** do sistema acadêmico |
| `NOME` | identidade | `CandidateIdentity.nome` |
| `CLASSIF_CURSO_FINAL` | resultado | posição na ordem — **e o destino pede numeração sequencial das linhas** |
| `COD_CURSO` | — | **sem fonte** |
| `COD_TURNO` | — | **sem fonte** |
| `COD_FORMA_INGRESSO` | oferta | `ModalidadeConcorrencia.code` + correspondência **inexistente** |
| `CPF` | identidade | `cpf_normalizado`, sem pontuação |
| `SEXO` | requerimento | `sexo` |
| `ESTADO_CIVIL` | requerimento | `estado_civil` + flexão derivada de `sexo` |
| `EMAIL` | identidade | credencial principal (`FR-378`) |
| `DATA_NASCIMENTO` | requerimento | `data_de_nascimento` |
| `COR` | requerimento | `cor_raca` — **o destino não tem *indígena*** (`R-4`) |
| `NOME_MAE` / `NOME_PAI` | requerimento | `nome_da_mae`, `nome_do_pai` |
| `CIDADE_NATAL` | requerimento | `municipio_natal` — a UF **não tem coluna** |
| `COD_NACIONALIDADE` | requerimento + tabela | `nacionalidade` + correspondência **inexistente** |
| `RG` / `EMISSOR` / `IDENTIDADE_DATA` | requerimento | `rg`, `rg_orgao_emissor`, `rg_expedido_em` |
| `TITULO_ELE` / `ZONA_ELE` / `SECAO_ELE` | — | **sem fonte** (`Q-4`) |
| `CEP` … `ESTADO` | requerimento | `cep`, `logradouro`, `numero`, `complemento`, `bairro`, `municipio`, `uf` |
| `CELULAR` | requerimento | `telefone_celular` |
| `RENDA_PER_CAPITA_PNP` | requerimento | `renda_familiar_faixa` — **mede a soma da família; a coluna significa per capita** (`R-7`) |
| `NECESSIDADES_ESPECIAIS` | requerimento | `necessidade_especifica` |
| `NOME_POLO` | oferta | `PerfilVaga.locality`, texto livre |
| `COD_POLO` | — | **sem fonte** |

**A tabela acima agrupa colunas afins numa linha só** — filiação, documento, endereço — e por isso
não serve para contar. O mapa **coluna a coluna**, com a conta que fecha nas 34, está em
[contrato-de-saida.md](../contrato-de-saida.md), e é ele que a `SC-133` verifica: 21 do
requerimento, 3 da identidade, 2 da oferta, 1 da inscrição, 1 da classificação e **6 sem fonte**.

Uma redação anterior desta linha dizia *"16 colunas do requerimento · 8 derivadas · 5 sem fonte"*,
que não reconcilia com nada — nem com as 34 colunas, nem com as 23 linhas desta tabela. Era contagem
feita de cabeça sobre uma tabela agrupada, e é exatamente o tipo de número que só se descobre errado
quando um teste passa a somá-lo.

Nenhuma conversão é inventada: onde não há regra, o mapa diz que não há.

---

## 3.1 Limite conhecido do documento publicado

O `declarationText` **não é renderizado no PDF do Edital**: o compositor materializa coleções, e
campo de raiz fica de fora — como já acontece com `maxInscricoesPorCandidato`. O texto existe no
conteúdo publicado, é citável e é exibido por extenso na tela do aceite; o que ele não faz é aparecer
no documento. Registrado em `Q-10`.

## 4. O que este contrato **não** promete

Planilha, arquivo de importação, chamada a sistema acadêmico, análise, deferimento, indeferimento e
qualquer coordenada geográfica. Os quatro do meio são da convocação; os demais são de features que
ainda não existem.
