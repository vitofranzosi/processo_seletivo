# Verificação — o Edital 28/2026, original × gerado pelo sistema

**29/09/2026**, na `054`. O original é o PDF *"Edital 28.2026 … retificado em 24.08.2026"* (em
`~/Downloads`, fora do repositório), lido com `pdftotext -layout`. O gerado foi **publicado pelo fluxo
real** num banco próprio (`ps_054_demo`): Processo e Edital criados, rascunho gravado, submetido,
homologado e publicado pela API, com a autoridade do catálogo; depois, uma Retificação que muda o
prazo do certificado (13.3, de 180 para 120 dias), também publicada. Os dois documentos são os
`DocumentoPublicado` que o sistema gravou — nada foi composto à parte.

**Como o texto chegou ao sistema** (E10 = B, transcrição): cada seção do original foi copiada para a
seção do catálogo que a recebe (research, R-001), parágrafo a parágrafo, sem edição. Os 7 polos viraram
7 Perfis de 40 vagas, com o quadro AC 28 · PcD 2 · PPI 10; o Requerimento de Matrícula foi declarado
na convocação. **Nenhum dado pessoal**: o nome de quem assina está só no fecho do original, e não foi
copiado; a demonstração usa a autoridade do catálogo, que só tem o cargo.

## 1. Seção a seção

| Original | Gerado | Situação |
|---|---|---|
| Título: *EDITAL Nº 28/2026 – CURSO PÓS-GRADUAÇÃO LATO SENSU EM INFORMÁTICA NA EDUCAÇÃO NA MODALIDADE EaD DO IFES/CEFOR* | brasão, órgão em quatro linhas, e *EDITAL Nº 28/2026 — CURSO DE PÓS-GRADUAÇÃO …* | ✅ o ato sai de número e ano (RC-20); o órgão é da `008` |
| Preâmbulo: *A Diretora do Centro … faz saber …* | o mesmo texto, sem número | ✅ (transcrito na Apresentação) |
| 1. Informações gerais | **1. Informações Gerais sobre o Curso** | ✅ tem lugar (antes da `054`, não tinha). ⚠️ o **Quadro 1** (matriz curricular) não tem como ser escrito: a seção textual não tem tabela (DP-20, propriedade 2) |
| 2. Público-alvo | **2. Público-Alvo** | ✅ tem lugar (antes, não tinha) |
| 3. Requisitos | **3. Requisitos Gerais de Participação** | ✅ |
| 4. Vagas — 4.1 a 4.3 (texto) e Quadro 2 por polo, com *Total de vagas 280* | **4. Perfis de Vaga** — tabela dos 7 Perfis terminando em **Total 280**, e por Perfil o quadro de vagas, as modalidades e o marco | ✅ **a oferta vem antes da inscrição**, como no original; ✅ o total (FR-997). ⚠️ o texto de 4.1 a 4.3 (os 25%/5% da Resolução CS 10/2017, a reversão ao AC, a concorrência concomitante) é **dado estruturado** no sistema — regra normativa da Modalidade e reversão declarada —, e a demonstração não os declarou; numa transcrição real, eles entram por ali, e não como prosa |
| 5. Inscrições (a lista de documentos 5.4 em alíneas) | **5. Da Inscrição** | ✅. A lista 5.4 veio como texto; declarada como Documentos Exigidos, ela sairia na seção gerada 6, logo abaixo |
| 6. Da verificação da veracidade da autodeclaração | **6. Da Verificação da Autodeclaração** (6 e 7 do original, com o título do 7 como subtítulo) | ✅ tem lugar (antes, não tinha) |
| 7. Do procedimento complementar … elegibilidade PcD | dentro da 6 | ✅ |
| 14. Da entrevista dos candidatos PcD | **7. Do Atendimento à Pessoa com Deficiência** | ✅ tem lugar; **muda de posição** (sai depois da verificação, e não depois do certificado — research, R-001) |
| 8. Processo seletivo (sorteio) | **8. Critérios de Classificação** | ✅ o texto é o do Edital: *"O Processo Seletivo se dará por sorteio…"*. Antes da `054`, a seção intocada publicaria *"observará a pontuação obtida nas Etapas"* |
| Anexo I – Cronograma (depois do fecho) | **9. Cronograma** (no corpo, em tabela) | ↔ decisão da `DP-20`: continua seção |
| 9. Recurso | **10. Dos Recursos** | ✅ |
| 10. Matrícula no curso | **11. Da Matrícula**, terminando em *"O Requerimento de Matrícula será enviado quando o candidato for convocado. Ao enviá-lo, o candidato declarará:"* e a declaração, recuada | ✅ tem lugar (antes, não tinha); ✅ **a declaração publicada** (FR-996) |
| 11. Acesso e informações sobre o curso | **12. Do Acesso ao Curso** | ✅ tem lugar (antes, não tinha) |
| 12. Homologação da matrícula | **13. Da Homologação da Matrícula** | ✅ tem lugar (antes, não tinha) |
| 13. Certificado | **14. Do Certificado** | ✅ tem lugar (antes, não tinha) |
| 15. Disposições finais | **15. Disposições Finais** | ✅ |
| Fecho: *Vitória - ES, 07 de abril de 2026* · nome · *Diretora do Centro de Referência …* · *Portaria nº 797, de 08 de abril de 2022* | *Vitória (ES), 29 de setembro de 2026.* · *Autoridade responsável pelo ato* · *Diretora-Geral do Centro de Referência em Formação e em Educação a Distância* | ✅ local e data (FR-989). ⏳ nome e portaria: **com o Cefor** — entram no catálogo e saem sem outra mudança (SC-365). ⚠️ o **cargo** diverge: o original diz *"Diretora do Centro…"*, o catálogo *"Diretora-Geral do Centro…"*; é para conferir junto com o nome |
| Anexos II a VI (requerimento, autodeclarações, termo LGPD) | — | ↔ anexo é arquivo à parte (`020`); a demonstração não os carregou, e a seção Anexos, vazia, não sai |
| — | verificação de integridade e SHA-256 | da `008` |

**15 de 15** seções numeradas do original têm seção correspondente (SC-361). Antes da `054`, **8 de
15** não tinham.

## 2. O consolidado da Retificação

O documento da Retificação difere do original em três pontos, e só neles (diff do texto extraído,
sem o SHA-256 do rodapé):

1. a marca, logo abaixo do anúncio: *"Versão consolidada. Publicado em 29 de setembro de 2026;
   retificado em 29 de setembro de 2026."* (FR-995) — as duas datas são a mesma porque a demonstração
   publicou e retificou no mesmo dia;
2. o item 13.3, com o prazo novo;
3. uma quebra de linha no item 1.6.1, deslocada pelas duas linhas da marca.

O documento original continua sem marca, e não foi regenerado.

## 3. O que a verificação mostrou e a spec não previa

**A numeração dos subitens transcritos deixa de casar com a da seção a partir da 9.** O texto
transcrito carrega os números do original — *"9.1 Caberá recurso…"* sob **10. DOS RECURSOS**,
*"10.1 Considerações sobre a matrícula"* sob **11. DA MATRÍCULA** —, porque o Cronograma entra no
corpo como seção 9, onde o original o tinha como Anexo I. As seções 1 a 8 e a 15 casam; da 9 à 14, o
subitem fica um número atrás da seção. As remissões internas (*"conforme item 8.3"*, *"item 5.4"*)
continuam certas, porque apontam para seções que não mudaram de número.

É a propriedade 2 da `DP-20` — *"o 4.1 que o autor digitar no texto é número dele, e não do
documento"* — materializada no Edital do teste operacional. **Registro, e não escopo desta feature**:
a conferência da homologação (E10 = B) tem de renumerar o subitem transcrito, ou o Cronograma volta a
ser discutido como anexo, ou uma spec futura numera o subitem. É decisão do usuário.
