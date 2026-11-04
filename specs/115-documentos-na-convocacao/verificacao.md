# Verificação: Documentos e conferência na convocação (115)

Medida em 03/11/2026, na worktree `nice-zhukovsky-0b4397`, contra PostgreSQL, com os grupos
`navegador` e `assistente` instalados e `DB_NAME=ps115`, 4 workers (`make test-pg`).

## A suíte

| Medição | Commit | Passaram | Pulados | Falharam | Tempo |
|---|---|---|---|---|---|
| Linha de base (T002) | `83cd5863` (`main`) | 14677 | 12 | 0 | 608 s |
| Depois da implementação (T050) | `0062d311` | 14810 | 12 | 3 | 686 s |
| Os 3 isolados, duas vezes (`tests/navegador`, 2 workers) | `0062d311` | 12 de 12 | — | 0 | 17 s |
| Depois da revisão de código | `fd23362c` | 14821 | 12 | 2 | 641 s |

**As 3 falhas da rodada completa não são do diff.** As três caíram no mesmo worker (`gw2`), as três
com `TargetClosedError` — o Chromium fechou no meio do caso —, e uma delas é a jornada de unidades
da `110`, que esta feature não toca. Na rodada completa anterior (`b80an6xlo`, sobre o commit
`75d7737a`) as mesmas jornadas tinham passado. Rodada isolada, duas vezes: os 12 testes de
navegador passam. A soma é **14813 passando e 12 pulados**, +136 casos sobre a linha de base.

**Na rodada depois da revisão de código, as 2 falhas foram:**
- o teste de tempo da ocupação (`performance/test_ocupacao.py`, o "dobro"), que o `AGENTS.md` registra
  como instável com 4 workers; isolado, passou três vezes de três;
- um teste da Fase 2 que afirmava que o anúncio público **não** continha a certidão da convocação.
  A correção 5 da revisão passou a anunciá-la, à parte, e o teste agora confere exatamente isso.

A soma dessa rodada é **14823 passando e 12 pulados**.

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
  (`unit/publicacoes/test_secao_da_convocacao.py`), e o título é neutro. **Aceita pelo usuário em
  04/11/2026**: fica como subseção.

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

## O que a revisão de código corrigiu (03/11/2026)

O *code review* do PR #369 encontrou dez pontos, e os dez foram corrigidos, cada um com teste:

1. **A pendência sobre o que nem chegou** aparecia como "a apresentar", e o motivo sumia do portal.
   Passa a ser *pendente*, e a convocação, *com pendência*.
2. **A conferência sem versão indicada**, sobre item com arquivo, gravava-se sem apresentação, e o
   estado lia *complementado*. Passa a julgar a vigente.
3. **O envio depois do "conforme"** era recusado só pela tela; o comando aceitava e desfazia a
   prontidão. O comando recusa (`documento_ja_conferido`).
4. **A linha nova de documento**, acrescentada pelo botão, nascia sem as opções de aproveitamento.
5. **O assistente (P-05) e a página pública** calavam os documentos da convocação; os dois os dizem
   agora, à parte dos da inscrição.
6. **A alocação a Perfil que o Edital não tem** era aceita; passa a ser recusada, e a comissão sem
   presidente também, como na alocação à Etapa.
7. **Com o Processo em estado final**, o candidato enviava e ninguém podia conferir; o envio é
   recusado e o formulário some.
8. **A condução subia a cadeia de sucessão elo a elo** por linha; as raízes saem numa consulta.
9. **A recusa de integridade da gestão** estava escrita duas vezes; ficou numa função.
10. **A leitura das pendências** filtrava por `id()` sobre pares; passou a um predicado direto.

## A condução com documentos em escala (03/11/2026)

`performance/test_conducao_com_documentos.py` abre a tela da condução pela rota, como a comissão,
com 5 e depois com 45 convocações que pedem os documentos do aluno. O cenário tem o que a leitura
percorre: a lista gravada pelo serviço em cada chamada; um terço com certidão conforme e histórico
pendente; um terço com a certidão à espera de conferência; um terço sem nada enviado; e uma chamada
em cada cinco corrigida por sucessora.

| Convocações com documentos | Consultas (ordem padrão) | Consultas (ordem `documentos`) |
|---|---|---|
| 5 | 94 | 94 |
| 45 | 94 | 94 |

A curva é plana: o custo é do recorte, e não da linha. **O teste reprova a regressão que a correção
8 da revisão tirou**: com a cadeia subida elo a elo por linha (`raiz_da_chamada` em cada uma), a
mesma medição vai de 94 a 102 e falha, conferido trocando a linha à mão e desfazendo em seguida.

## O que esta verificação não cobre

- **A validação por pessoas** — uma chamada real conduzida por quem confere, com o tempo de análise
  medido — não está aqui: é o que a auditoria (Anexo II) já apontava como a melhor medida do valor.
- **Uso em produção com dado real.** Em 04/11/2026 o usuário decidiu a QI-3 (não há lista
  institucional: cada Edital declara os seus documentos) e adiou a QI-4 (guarda e destinação; o GPS
  não é GED) e o MAT-08 (varredura de PDF). As duas adiadas continuam na lista de pendências da
  spec, e **nenhuma das três bloqueia mais a produção**.
