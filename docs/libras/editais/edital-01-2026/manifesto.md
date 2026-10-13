# Manifesto — Edital nº 01/2026 (simulado)

> **Edital simulado.** Não é ato real do Ifes. É o primeiro Edital da demonstração do sistema
> (`manage.py seed_demo`), publicado pelo fluxo real num banco isolado. Nenhum dado pessoal.

## Identificação

| Campo | Valor |
|---|---|
| Ato | Edital nº 01/2026 — Professor Substituto e Técnico-Administrativo |
| Processo | `PS-DEMO-2026` — Processo Seletivo Simplificado 2026 |
| Unidade | Centro de Referência em Formação e em Educação a Distância (Cefor) |
| Autoridade | só o cargo (“Reitora”), como o `seed_demo` cadastra |
| Origem do conteúdo | `backend/processo_seletivo/processos/management/commands/seed_demo.py` (`perfis`, `etapas`, `cronograma`, `documentos_exigidos`, `_retificar`) |
| Gerado em | 2026-10-11, commit `bbc8e04c`, banco `ps_libras_corpus`. **As datas do Cronograma são relativas ao instante da geração** (“às 09h43”): outra execução do `seed_demo` dá outras datas e outros hashes |

## Versões

| Versão | Publicação | Vigência | Conteúdo (SHA-256) | Documento (início) | Páginas | Arquivos |
|---|---|---|---|---|---|---|
| **v1 — original** | 11/10/2026 | imediata | `c29f09d938a8780677c8f764d5b8d954a0515647888bc9260106efa20eedacbb` | `83c527b33f1226ae…` | 4 | [`fonte/pub1.pdf`](fonte/pub1.pdf), [`fonte/pub1-canonico.json`](fonte/pub1-canonico.json) |
| **v2 — Retificação a** | 11/10/2026 | imediata | `c05270a337024e047d7f6a5b2dd1bace47b4171bcd0d7bdff459844cf70a6329` | `bbc6f3d58ecaad32…` | 4 | [`fonte/pub2.pdf`](fonte/pub2.pdf), [`fonte/pub2-canonico.json`](fonte/pub2-canonico.json), [`fonte/pub2-alteracoes.json`](fonte/pub2-alteracoes.json) |
| **v3 — Retificação b** | 11/10/2026 | **26/10/2026** (futura) | `f23684d2e41bfdaa9cf916ed900eacc23c43b74bbf636eff2418b631797bc008` | `ab886c6b403cf544…` | 4 | [`fonte/pub3.pdf`](fonte/pub3.pdf), [`fonte/pub3-canonico.json`](fonte/pub3-canonico.json), [`fonte/pub3-alteracoes.json`](fonte/pub3-alteracoes.json) |

## Características do processo seletivo

| Dimensão | Configuração |
|---|---|
| Oferta | seleção de pessoal: professor substituto e técnico |
| Perfis | 2: DOC-INFO (2 vagas, cadastro limitado a 6) e TEC-LAB (0 vaga, cadastro ilimitado) |
| Modalidades | DOC-INFO: AC e PPP (20%, Lei 12.990/2014); TEC-LAB: só AC; sem reversão declarada |
| Classificação | um marco por Perfil, por pontuação (soma ponderada de duas Etapas). DOC-INFO: recurso de 5 dias, corte fixo de 2 + 1 suplente, empate estrito, sem continuação. TEC-LAB: **sem recurso declarado**, corte de 3 sem Etapa governada, empate com excedente, sem continuação |
| Etapas | Prova objetiva (eliminatória e classificatória, peso 2, nota mínima 6), Análise de títulos (peso 1), Análise documental (decisória) |
| Cronograma | 3 Eventos; o primeiro traz na descrição “com isenção de taxa até o 5º dia” |
| Documentos | 1 de todos, 1 por Perfil, 1 por modalidade |
| Seções textuais | **nenhuma**: sem preâmbulo; Da Inscrição e Da Matrícula saem só pelas normas que o sistema acrescenta |
| Normas executadas | teto de 1 inscrição; Requerimento de Matrícula no ato da inscrição, com declaração |
| Anexos | 2 |
| Convocação | por mensagem individual |

## Contexto legal

**Seleção de professor substituto e de técnico (demonstração).** A admissão de professor substituto é
hipótese da Lei nº 8.745/1993 (art. 2º, IV), por processo seletivo simplificado (art. 3º), e alcança o
Decreto nº 9.508/2018, que assegura reserva de vagas e tratamento diferenciado, requerido na inscrição, e
prevê prova em vídeo com intérprete de Libras para o candidato com deficiência auditiva. Não encontrei
norma que exija a tradução **do edital** em Libras neste tipo de certame. O enquadramento é ilustrativo —
o Perfil técnico do `seed_demo` não corresponde necessariamente a uma hipótese daquela lei —, e é da área
jurídica ([`../../auditoria-sistema.md`](../../auditoria-sistema.md), §13).

## Escopo analisado

- **Todo o texto da v1**, em 54 linhas: [cobertura.md](cobertura.md).
- **As v2 e v3 por diferença**, inclusive a vigência futura: [retificacoes.md](retificacoes.md).
- Pacote: [roteiro-producao.md](roteiro-producao.md) · [oportunidades-reuso.md](oportunidades-reuso.md).
- **Camada comunicativa (rodada 2):** três narrativas — [inscrição](narrativas/inscricao.md), [classificação](narrativas/classificacao.md) e [recurso](narrativas/recurso.md) — e o [mapa da cobertura por intenção](narrativas/README.md).

## Por que este edital, e não os outros do `seed_demo`

O `seed_demo` publica também o 26/2026 (sorteio, um Perfil técnico EaD) e o 51/2026 (seleção concluída),
e deixa o 76/2027 em elaboração. O 01/2026 foi escolhido por ser o único com **duas Retificações, uma
delas com vigência futura**, e por ter configuração distante dos outros dois do corpus (seleção de
pessoal, duas Etapas pontuadas, marcos diferentes por Perfil). O 26/2026 repetiria, em menor escala, o
sorteio do 91/2026. Os PDFs dos outros ficaram fora do corpus.

## Limitações

- Sem texto livre de seção, este edital mede o que o sistema escreve sozinho, e só isso. A sua
  recorrência alta frente aos outros dois (86% das palavras em unidades já vistas, na versão 2 do
  catálogo; 93% na versão 1) é efeito dessa
  ausência.
