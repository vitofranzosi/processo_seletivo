# Manifesto — Edital nº 92/2026 (simulado)

> **Edital simulado.** Não é ato real do Ifes. Foi publicado pelo fluxo real do sistema, num banco
> isolado, com dados fictícios marcados “DEMONSTRAÇÃO” no título, no preâmbulo e nos endereços dos
> polos. Nenhum dado pessoal.

## Identificação

| Campo | Valor |
|---|---|
| Ato | Edital nº 92/2026 — Seleção de cadastro de reserva de tutores presenciais e a distância para atuarem nos cursos técnicos e de pós-graduação do Programa Universidade Aberta do Brasil (UAB) ofertados pelo Cefor/Ifes (DEMONSTRAÇÃO) |
| Processo | `PS-AUD-B-2026` — Seleção de Tutores UAB — Cadastro de Reserva 2026 (DEMONSTRAÇÃO) |
| Unidade | Centro de Referência em Formação e em Educação a Distância (Cefor) |
| Autoridade | só o cargo (Diretora-Geral do Cefor), como o registro inicial do Cefor está hoje (060, FR-1124) |
| Origem do conteúdo | roteiro `cenario_b_corrigido.py` da auditoria do PDF (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`), calibrado contra o Edital real 90/2026 do Cefor. O roteiro `cenario_b.py` original é recusado na submissão desde a `065` (conflito de numeração); o corrigido troca só os números digitados nos subitens |
| Gerado em | 2026-10-11, commit `bbc8e04c`, banco `ps_libras_corpus` |

## Versões

| Versão | Publicação | Conteúdo (SHA-256) | Documento (SHA-256, início) | Páginas | Arquivos |
|---|---|---|---|---|---|
| **v1 — original** | 11/10/2026 | `34bc1a9f9a9f3de85933ca10fc2544c0bc39c19a34c94e9b1562b6fb1e68d2ca` | `8795882f3e1c27cf…` | 14 | [`fonte/pub1.pdf`](fonte/pub1.pdf), [`fonte/pub1-canonico.json`](fonte/pub1-canonico.json) |
| **v2 — Retificação** | 11/10/2026, vigência imediata | `b695a0e1c0d80c634e6d038c900e8115adcf278693e6a3e954692e5521ea8495` | `a78c93424f8d9cd1…` | 14 | [`fonte/pub2.pdf`](fonte/pub2.pdf), [`fonte/pub2-canonico.json`](fonte/pub2-canonico.json), [`fonte/pub2-alteracoes.json`](fonte/pub2-alteracoes.json) |

## Características do processo seletivo

| Dimensão | Configuração |
|---|---|
| Oferta | bolsas de tutoria (UAB/CAPES), cadastro de reserva |
| Perfis | 18: 2 tutores a distância (6 e 4 vagas imediatas) e 16 tutores presenciais por polo (0 vaga imediata), todos com cadastro limitado a 15; 20 horas semanais |
| Modalidades | AC, PPIQ (30%), PcD (5%), PTT (sem percentual), com fundamentos longos; reversão pelo saldo não preenchido |
| Classificação | um marco por pontuação (prova de títulos); corte fixo de 10 + 5 suplentes para a análise documental; empate admite excedente; continuação admitida; recurso de 3 dias; 3 critérios de desempate sobre 2 dados declarados e a Etapa |
| Etapas | Prova de títulos (pontuada, máx. 100) e Análise documental (decisória) |
| Cronograma | 18 Eventos, 4 de recurso, com locais e descrições longas |
| Documentos | 6 de todos (1 facultativo), 2 por Perfil, 3 por modalidade |
| Seções textuais | 11 preenchidas, **com numeração de subitens digitada pelo gestor** |
| Normas executadas | teto de 1 inscrição; sem Requerimento de Matrícula |
| Anexos | 6 (rótulos; conteúdo fora do PDF) |
| Convocação | por mensagem individual |

## Contexto legal

**Seleção de bolsistas de tutoria (UAB/CAPES), com cadastro de reserva.** Não é ingresso em curso e, à
primeira leitura, tampouco contratação temporária da Lei nº 8.745/1993: não encontrei norma que exija a
tradução do edital em Libras para este tipo de certame. Alcançam-no, em tese, normas gerais — o art. 26 do
Decreto nº 5.626/2005 (atendimento às pessoas surdas na administração federal) e, se a bolsa for tratada
como trabalho, o art. 34, § 3º, da LBI. O escopo da tradução é decisão institucional, e o enquadramento,
jurídico ([`../../auditoria-sistema.md`](../../auditoria-sistema.md), §13). A Retificação que retira a
seção de atendimento à pessoa com deficiência retira a cláusula do edital, não direitos previstos em lei.

## Escopo analisado

- **Todo o texto da v1**, em 224 linhas de cobertura: [cobertura.md](cobertura.md). Os 16 blocos de
  tutor presencial têm uma linha por elemento, para que nenhum desapareça da matriz.
- **A v2 por diferença**: [retificacoes.md](retificacoes.md).
- Pacote: [roteiro-producao.md](roteiro-producao.md) · [oportunidades-reuso.md](oportunidades-reuso.md).
- **Camada comunicativa (rodada 2):** três narrativas — [inscrição](narrativas/inscricao.md), [classificação](narrativas/classificacao.md) e [recurso](narrativas/recurso.md) — e o [mapa da cobertura por intenção](narrativas/README.md).

## Fora do escopo

- O conteúdo dos seis anexos.
- Documentos e páginas fora do PDF do Edital.

## Limitações

- A configuração é de estresse (18 Perfis), escolhida pela auditoria para expor repetição. Ela
  aumenta a repetição **interna**, que não deve ser lida como recorrência entre editais.
- O pedido de comprovante de residência só ao TP-01 (seção 5, grupo 2) é conteúdo da simulação:
  registrado na cobertura, não corrigido.
