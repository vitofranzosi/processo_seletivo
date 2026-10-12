# Manifesto — Edital nº 91/2026 (simulado)

> **Edital simulado.** Não é ato real do Ifes. Foi publicado pelo fluxo real do sistema, num banco
> isolado, com dados fictícios marcados “DEMONSTRAÇÃO” no título e no preâmbulo. Nenhum dado pessoal.
>
> **Número em colisão (rodada 3).** O Cefor publicou em 2026 um Edital 91/2026 **real**, de outro objeto: a seleção
> de professores regentes para os cursos da UAB. Este pacote não tem relação com ele.

## Identificação

| Campo | Valor |
|---|---|
| Ato | Edital nº 91/2026 — Curso de Pós-graduação Lato Sensu em Informática na Educação na modalidade EaD (DEMONSTRAÇÃO) |
| Processo | `PS-AUD-A-2026` — Processo Seletivo de Alunos — Pós-graduação EaD 2027/1 (DEMONSTRAÇÃO) |
| Unidade | Centro de Referência em Formação e em Educação a Distância (Cefor) |
| Autoridade | Diretora-Geral do Cefor, com nome e portaria fictícios |
| Origem do conteúdo | roteiro `cenario_a.py` da auditoria do PDF de 08/10/2026 (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`), calibrado contra o Edital real 28/2026 do Cefor |
| Gerado em | 2026-10-11, commit `bbc8e04c`, banco `ps_libras_corpus` |

## Versões

| Versão | Publicação | Conteúdo (SHA-256) | Documento (SHA-256, início) | Páginas | Arquivos |
|---|---|---|---|---|---|
| **v1 — original** | 11/10/2026 | `083468eb97dfa5843555132992abdf88a6a2085bd14fb16e8a64551f1b8ee132` | `0c69fb0fedb9a1ec…` | 6 | [`fonte/pub1.pdf`](fonte/pub1.pdf), [`fonte/pub1-canonico.json`](fonte/pub1-canonico.json) |
| **v2 — Retificação** | 11/10/2026, vigência imediata | `d0186c039d8f02c4d9369be743a86926067e6001ec3fe09535d53134236c337c` | `47c9c1204096adf3…` | 6 | [`fonte/pub2.pdf`](fonte/pub2.pdf), [`fonte/pub2-canonico.json`](fonte/pub2-canonico.json), [`fonte/pub2-alteracoes.json`](fonte/pub2-alteracoes.json) |

O hash de conteúdo é o que o próprio PDF imprime no rodapé e na verificação de integridade. O hash do
documento é o do arquivo, exposto pela API como `documentHash` e não impresso.

## Características do processo seletivo

| Dimensão | Configuração |
|---|---|
| Oferta | curso de pós-graduação lato sensu, a distância |
| Perfis | 4 polos (INF-BJN, INF-IUN, INF-SMT, INF-VAL), 40 vagas cada, sem cadastro de reserva, 480 h |
| Modalidades | AC, PPI (25%) e PcD (5%), fundamento Resolução CS nº 10/2017; reversão por ausência de aprovados |
| Classificação | um marco por sorteio (método comum do Edital, Loteria Federal); corte pelo quadro de vagas + 15 suplentes; continuação admitida; recurso de 2 dias contra a ordem do sorteio |
| Etapas | Análise documental (decisória, eliminatória) |
| Cronograma | 10 Eventos, 2 com local |
| Documentos | 5 de todos (1 facultativo), 1 por modalidade PPI, 1 por modalidade PcD |
| Seções textuais | 13 preenchidas |
| Normas executadas | teto de 1 inscrição; Requerimento de Matrícula no ato da inscrição, com declaração |
| Anexos | 3 (rótulos; conteúdo fora do PDF) |
| Convocação | por publicação |

## Contexto legal

**Ingresso em curso de pós-graduação de instituição federal de educação profissional e tecnológica.** À
primeira leitura, o certame está no alcance do art. 30 da LBI (Lei nº 13.146/2015), cujo inciso VII exige a
**tradução completa do edital e de suas retificações em Libras**, e cujos incisos I a VI preveem medidas de
acessibilidade no processo seletivo; e dos arts. 14 e 21 do Decreto nº 5.626/2005. Neste tipo de certame, o
reuso só pode servir à preparação e à produção **dentro** da tradução integral. O enquadramento é da área
jurídica ([`../../auditoria-sistema.md`](../../auditoria-sistema.md), §13).

## Escopo analisado

- **Todo o texto da v1**, em 101 linhas de cobertura, inclusive cabeçalho, fecho, verificação de
  integridade e rodapés: [cobertura.md](cobertura.md).
- **A v2 por diferença** em relação à v1: [retificacoes.md](retificacoes.md).
- Pacote: [roteiro-producao.md](roteiro-producao.md) · [oportunidades-reuso.md](oportunidades-reuso.md).
- **Camada comunicativa (rodada 2):** três narrativas — [inscrição](narrativas/inscricao.md), [classificação](narrativas/classificacao.md) e [recurso](narrativas/recurso.md) — e o [mapa da cobertura por intenção](narrativas/README.md).

## Fora do escopo

- O conteúdo dos três anexos (só os rótulos saem no PDF).
- Páginas do portal, documento do resultado, avisos e convocação (ver
  [`../../auditoria-sistema.md`](../../auditoria-sistema.md), §9).
- A prévia em elaboração (não é ato).

## Limitações

- O texto livre foi redigido pela auditoria de 08/10, com forma plausível; a sua recorrência frente a
  outros editais não diz nada sobre a prática real do Cefor.
- A data do ato (11 de outubro de 2026) é a da geração do corpus, não uma data de calendário de seleção.
