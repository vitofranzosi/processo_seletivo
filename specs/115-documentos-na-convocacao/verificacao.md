# Verificação: Documentos e conferência na convocação (115)

Medida em 03/11/2026, na worktree `nice-zhukovsky-0b4397`, contra PostgreSQL, com os grupos
`navegador` e `assistente` instalados e `DB_NAME=ps115`, 4 workers (`make test-pg`).

## A suíte

| Medição | Commit | Passaram | Pulados | Falharam | Tempo |
|---|---|---|---|---|---|
| Linha de base (T002) | `83cd5863` (`main`) | 14677 | 12 | 0 | 608 s |
| Depois da implementação (T050) | `0062d311` | 14810 | 12 | 3 | 686 s |
| Os 3 isolados, duas vezes (`tests/navegador`, 2 workers) | `0062d311` | 12 de 12 | — | 0 | 17 s |

**As 3 falhas da rodada completa não são do diff.** As três caíram no mesmo worker (`gw2`), as três
com `TargetClosedError` — o Chromium fechou no meio do caso —, e uma delas é a jornada de unidades
da `110`, que esta feature não toca. Na rodada completa anterior (`b80an6xlo`, sobre o commit
`75d7737a`) as mesmas jornadas tinham passado. Rodada isolada, duas vezes: os 12 testes de
navegador passam. A soma é **14813 passando e 12 pulados**, +136 casos sobre a linha de base.

**Os pulados são os mesmos 12, um a um** (comparados por arquivo e motivo, sem número de linha): os
10 do vocabulário da composição, a recusa por vendor e o E2E da Caixa. Nenhum teste novo pula.

`make lint check`: `ruff check` e `ruff format --check` verdes; `manage.py check` sem achado;
`makemigrations --check` sem mudança pendente.

## O que mudou em teste existente, e por quê

Cada número abaixo é contagem que a mudança desloca de propósito, com a razão escrita no teste:

| Teste | De → para | Razão |
|---|---|---|
| `seguranca/test_homologacao_preservada.py` | 46 → 49 tabelas append-only | as três da convocação (`ItemDaListaDaConvocacao`, `ApresentacaoDeDocumento`, `ConferenciaDeDocumento`) |
| `migrations/test_migrations.py` | `editais` 23 → 24; `comissoes` 1 → 2 | o momento do Documento Exigido; a alocação à conferência |
| `integration/publicacoes/test_elevacao_de_versao.py` | `SCHEMA_VERSION` 17 → 18; degraus de documento (9, 17) → (9, 17, 18) | o degrau do momento |
| `unit/duvidas/test_cobertura.py` (via `VERSAO_DO_ESQUEMA`) | 17 → 18 | os dois campos classificados como regra |
| `unit/editais/test_validacao_inscricao.py` | 2 → 3 documentos na fixture | o Edital máximo publica o documento da convocação, para o contrato alcançá-lo |
| `unit/convocacao/test_append_only.py` | 4 → 7 modelos | os três da convocação, nenhum deles vaga |
| `performance/test_relatorio.py` | 118 → 119 consultas | a trilha do Edital reúne os documentos da convocação numa união só |
| `performance/test_comissao_em_escala.py` | 21 → 22 consultas | a pergunta única se algum Edital do Processo pede documento na convocação |
| `interface/test_telas_de_resultado_e_atos.py` | 22 → 23 `botao` | "Registrar indeferimento", o indeferimento pelas pendências (FR-3594) |
| `interface/test_folha_estatica.py` | + `convocacao-documentos.css` | a folha da página filha |
| `integration/duvidas/test_corpus_pelo_fluxo_real.py` | compara com o corpus **elevado** | o corpus foi publicado na versão 17; o fluxo de hoje publica na 18 |
| `specs/033-…/inventario-das-negativas.md` | + 4 funções | as portas novas que respondem 404 |

## Divergências entre a implementação e a spec

Nenhuma decisão aprovada (D-001 a D-019) foi alterada. Uma redação de requisito foi lida de modo
mais estreito, e fica aqui para a revisão:

- **FR-3569 (a seção do PDF).** A spec pede "uma seção própria e neutra". A implementação a escreve
  como **subseção com título próprio** — *"Documentos exigidos na convocação"* — dentro da seção
  gerada dos documentos, e não como entrada nova no catálogo de seções. Uma entrada nova mudaria a
  topologia de seções de todo Edital composto daqui em diante, que a Retificação confere contra a
  do Edital publicado, e a seção existiria vazia na maioria deles. Do jeito feito, o título só
  aparece quando há documento na convocação, o Edital sem eles sai byte a byte como saía
  (`unit/publicacoes/test_secao_da_convocacao.py`), e o título é neutro. **Se a revisão preferir a
  entrada no catálogo, é mudança localizada** em `editais/domain/secoes.py` e
  `publicacoes/infrastructure/pdf.py`.

## A demonstração no navegador (T047, T051)

As cinco jornadas de `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` rodam num
Chromium de verdade, com o candidato a 375 px e a comissão em desktop. A fixture reprova qualquer
violação da política de conteúdo no console, e o candidato não pode ter rolagem horizontal.

| Jornada | O que se vê |
|---|---|
| Aluno, molde do 72/2026 | quatro documentos pedidos; três enviados; dois conformes e o histórico pendente; o aceite recusado nomeando o que falta; a pendência lida e complementada no portal; tudo conforme; aceite; "Apto para formalização" |
| Bolsista, molde do 146/2025 | a gestão aloca o membro à conferência na tela de alocações; o bolsista baixa o modelo e devolve a Ficha/Termo; o membro alocado confere e não vê o desfecho; a presidência aceita; nenhuma tela diz bolsa concedida nem vinculado |
| Certificado, molde do 89/2026 | o item nasce atendido pelo documento da inscrição; a comissão abre o arquivo da inscrição e confere; nenhum arquivo novo no armazenamento |
| Chamada nova | a reclassificada chamada de novo vê "Aproveitado da chamada anterior"; o "conforme" sem abrir é recusado; abrindo, é aceito |
| Prazo vencido | a frase única do prazo; nenhum envio oferecido; nenhum desfecho nasce do vencimento |

As capturas estão em [`capturas/`](capturas/), geradas com `NAVEGADOR_CAPTURAS`:

- candidato: [lista a 375 px](capturas/candidato-lista-a-375px.jpg),
  [pendência a 375 px](capturas/candidato-pendencia-a-375px.jpg),
  [Ficha do bolsista com o modelo](capturas/bolsista-ficha-com-modelo-a-375px.jpg),
  [certificado aproveitado](capturas/candidata-certificado-aproveitado-a-375px.jpg),
  [chamada nova](capturas/candidata-chamada-nova-a-375px.jpg),
  [prazo vencido](capturas/candidata-prazo-vencido-a-375px.jpg);
- comissão: [documentos da convocação](capturas/comissao-documentos-da-convocacao.jpg),
  [condução com "Apto para formalização"](capturas/comissao-conducao-apto-para-formalizacao.jpg),
  [alocação à conferência](capturas/gestao-alocacao-a-conferencia.jpg).

Na primeira leitura das capturas, a página da comissão tinha os botões de opção desalinhados e o
formulário de conferência aberto em todo item. Foram corrigidos antes destas capturas, no padrão
`fieldset.opcoes` da gestão, com o formulário recolhido onde não há versão a conferir. No portal, o
envio de outro arquivo passou a nascer aberto no item pendente.

## O que esta verificação não cobre

- **A validação por pessoas** — uma chamada real conduzida por quem confere, com o tempo de análise
  medido — não está aqui: é o que a auditoria (Anexo II) já apontava como a melhor medida do valor.
- **Uso em produção com dado real** continua bloqueado pela QI-3 (quais documentos são exigíveis),
  pela QI-4 (guarda e destinação) e pelo MAT-08 (varredura de PDF), como a spec registra.
- **O orçamento de consultas da condução com documentos em escala** não tem teste próprio: o teste
  de desempenho da condução (`performance/test_convocacao.py`) continua verde, e a leitura dos
  documentos é agregada (três consultas para o recorte inteiro, `leituras_por_chamada`), mas a
  medição com dezenas de convocações **com** documentos não foi feita.
