# Contrato — `019` Convocação, Chamada e Suplência

**O canal do ator desta feature é a interface administrativa**, e a área do candidato é o canal da
`US6`. Este contrato descreve as **rotas da gestão e do portal** e os **códigos de recusa** — e não
uma API pública: a Constituição já fixou que entidade de persistência não é contrato.

Erros usam `application/problem+json`; commands irreversíveis exigem `Idempotency-Key`; leitura e
escrita concorrentes usam `ETag` / `If-Match`, como o resto do sistema.

---

## 1. Gestão

| Rota | Método | O que faz |
|---|---|---|
| `/gestao/editais/<id>/marcos/<marco>/convocacao` | GET | a leitura do recorte: os quatro números da `016`, mais convocados, respondidos, vagas que voltaram a faltar e se a lista alcançada esgotou |
| `/gestao/editais/<id>/marcos/<marco>/convocacao` | POST | convoca — `inscricao`, `especie`, `vencimento`, `fundamento` |
| `/gestao/editais/<id>/marcos/<marco>/convocacao/<conv>/desfecho` | POST | registra o desfecho — `especie`, `fundamento`, e `atestado` quando é inércia |
| `/gestao/editais/<id>/marcos/<marco>/convocacao/<conv>/comunicar` | POST | emite a comunicação na forma declarada |
| `/gestao/editais/<id>/marcos/<marco>/convocacao/historico` | GET | o histórico com a proveniência de cada ato |
| `/gestao/inscricoes/<id>/atestado` | POST | atesta fato externo — `especie`, `conclusao` |

A rota de convocação **não** aceita `lista_id` no corpo: o recorte vem do marco e do Perfil, como na
`016`. Marco que não corta não tem faixa, e a recusa o diz.

## 2. Portal do candidato

| Rota | Método | O que faz |
|---|---|---|
| `/portal/minhas-inscricoes/<id>/convocacao` | GET | a chamada, o que fazer, e até quando — *"enviado em"*, nunca *"recebido em"* |

A tela distingue *"não há convocação"* de *"você não foi chamado"* (`FR-294`), e o acesso a ela é
registrado na trilha sem mover o relógio (`FR-288b`).

## 3. Códigos de recusa

| Código | Quando |
|---|---|
| `apuracao_ausente` | o recorte não tem apuração emitida — chamar para vaga que ninguém apurou é prometer o que não se sabe existir |
| `apuracao_obsoleta` | a apuração vigente já se sabe para trás; a mensagem nomeia a causa |
| `sem_deficit` | a apuração vigente não registra vaga faltante |
| `fora_da_faixa` | a Inscrição não está na faixa vigente — convocar fora dela é selecionar, e seleção é da `014` |
| `ordem_nao_vigente` | o ato de ordenação do recorte foi sucedido |
| `precedencia_na_ordem` | existe habilitado antes dela, sem convocação e sem desfecho, e o ato não traz fundamento |
| `convocacao_vigente_existente` | a pessoa já tem convocação vigente naquele recorte |
| `reabilitado_a_frente` | há Inscrição reabilitada por deferimento no topo da fila (`FR-292b`) |
| `vencimento_anterior_ao_envio` | o vencimento informado precede o envio (`FR-269b`) |
| `desfecho_ja_registrado` | a convocação já tem desfecho |
| `atestado_obrigatorio` | inércia sem atestado de fato externo |
| `reclassificado_antes_do_esgotamento` | chamada de reclassificado com suplentes por esgotar |
| `lista_alcancada_esgotada` | não há mais quem chamar dentro do teto publicado; a faixa seguinte é ato da `014` |
| `empate_na_fronteira_do_alvo` | empate residual não julgado atravessa a fronteira do alvo (`R-002` da pesquisa) |
| `forma_de_comunicacao_nao_declarada` | o Perfil publicado não declarou `callForm` |

### Guarda de implantação, e não de domínio

| Código | Quando |
|---|---|
| `envio_sem_revisao_da_010` | mensagem individual antes da revisão escrita da `FR-084` da `010` |

Está separada de propósito: não é regra do certame, é recusa de subir com duas normas contraditórias
vigentes no mesmo repositório.

## 4. O que o contrato **não** expõe

- **Nenhuma rota conta vaga.** O número vem da `016`, e a `UX-035` verifica por varredura que esta
  feature não o afirma por conta própria.
- **Nenhuma rota emite faixa.** Pedir faixa continua sendo ato da `014`, pela `016`.
- **Nenhuma rota apaga.** Correção é sucessão, com motivo.
- **Nenhum campo diz recebido, lido ou entregue.**
