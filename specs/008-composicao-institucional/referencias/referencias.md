# Referências visuais da 008

O que estas imagens são, de onde vieram e por que não são os PDFs originais.

## Por que imagens, e não os documentos

As referências existem para **comparação visual**: pôr o documento gerado ao lado de um Edital real
e conferir a rubrica de inspeção. Para isso, a página renderizada serve melhor que o PDF — é o que
se olha, não pode refluir, e não carrega as fontes embutidas do original.

Os três PDFs somavam **14 MB**, sendo 11,5 MB só o Edital 73, e entrariam no histórico do
repositório para sempre. As páginas que interessam, renderizadas a 120 dpi, somam **1,6 MB**.

Os originais não estão versionados. Cada um é identificado abaixo por fonte, número, ano e página,
como a spec admite em `### Referências visuais`.

## O estado inicial

| Arquivo | O que é |
|---|---|
| `estado-inicial-apos-007.pdf` | O documento que o sistema produzia ao fim da `007`, antes desta feature. Fica em PDF porque tem 6 KB e é gerado pelo próprio sistema |

## Os alvos

Todos são Editais públicos do Centro de Referência em Formação e em Educação a Distância
(Cefor/Ifes), obtidos do portal da instituição.

| Arquivo | Edital | Página | O que se compara nela |
|---|---|---|---|
| `alvo-edital-146-2025-p1.jpg` | 146/2025 — Assistente Pedagógico, Equipe UAB | 1 | Brasão, órgão em quatro linhas, ato e objeto numa sentença, preâmbulo sem número, `TABELA 1 — Quadro de vagas` com cabeçalho sombreado |
| `alvo-edital-146-2025-p9.jpg` | 146/2025 | 9 | Fechamento: praça e data, nome e cargo da autoridade |
| `alvo-edital-146-2025-p10.jpg` | 146/2025 | 10 | Anexo com o cronograma em quadro, cabeçalho institucional repetido |
| `alvo-edital-62-2026-p1.jpg` | 62/2026 — Bolsistas Pronatec | 1 | Cabeçalho institucional e `QUADRO 1` de áreas de atuação |
| `alvo-edital-62-2026-p2.jpg` | 62/2026 | 2 | Numeração hierárquica de itens e alíneas em texto corrido |
| `alvo-edital-73-2026-p1.jpg` | 73/2026 — Assistente Pedagógico UAB | 1 | Abertura, preâmbulo e início da matéria normativa |
| `alvo-edital-73-2026-p2.jpg` | 73/2026 | 2 | Itens numerados, alíneas e parágrafos |

## Como foram geradas

Renderizadas a 120 dpi, JPEG com qualidade 0,72, a partir dos PDFs originais. A resolução foi
escolhida por legibilidade: a 120 dpi o corpo do texto e as linhas dos quadros continuam nítidos,
que é o que a comparação exige.
