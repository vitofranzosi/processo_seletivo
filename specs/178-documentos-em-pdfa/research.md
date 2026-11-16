# Research — 178 · Os documentos que o GPS compõe nascem em PDF/A

O ponto de partida é o estudo de 16/11/2026 (`doc/estudo-pdf-a-preservacao-documental-2026-11-16.md`,
§1.2, §4.2, §5.1, §7 e §8), que mediu com o veraPDF 1.30.4 o que falta aos PDFs do GPS. Aqui ficam
as escolhas da implementação e o que foi medido nela.

## R-001 — Os objetos novos vão depois dos de sempre

**Decisão**: o perfil e os metadados são os dois últimos objetos do arquivo, e o catálogo ganha
`/Metadata` e `/OutputIntents` no fim do dicionário.

**Por quê**: os números dos objetos de página não andam, e por isso os fluxos de conteúdo — que citam
recursos por nome, e não por número — saem idênticos. É o que permite provar a FR-8159 byte a byte por
página, e não só "visualmente igual".

**Medido**: os cinco PDFs do cenário da auditoria, o documento publicado do contrato e os exemplares do
Edital, da Retificação e dos dois relatórios têm **todos** os `/Contents` idênticos aos de antes
(`test_documento_da_auditoria_depois_da_178.py`).

## R-002 — O `/ID` é o SHA-256 do corpo

**Decisão**: os 16 primeiros bytes do SHA-256 de tudo o que vem antes do trailer (objetos e tabela de
referências), repetidos nos dois elementos.

**Por quê**: a norma só exige que o identificador exista; a especificação do PDF sugere um resumo do
conteúdo. Derivado do corpo, ele mantém o determinismo — a promessa de "mesmo conteúdo, mesmos bytes"
que sustenta o resumo publicado do comprovante (FR-063a da `009`).

## R-003 — Metadados mínimos, coerentes com o `/Info`

**Decisão**: `pdfaid:part` e `pdfaid:conformance` sempre; `dc:title` e `dc:creator` só quando o `/Info`
tem título e autor (o Edital e os relatórios), com o mesmo texto; nenhuma data, nenhum produtor.

**Por quê**: a regra 6.6.3 cobra que as duas descrições concordem, e a forma mais segura é o XMP não
dizer nada que o `/Info` não diga. Datas quebrariam o determinismo. A família não tem `/Info`, e os
metadados declaram só a conformidade (FR-8153).

**Fluxo sem filtro**: a norma proíbe compressão no fluxo dos metadados.

## R-004 — O perfil sRGB2014 do ICC

**Decisão**: `sRGB2014.icc`, do registro do ICC, versionado em `publicacoes/infrastructure/cor/` com
`LICENSE` e `ORIGEM.md` (resumo `384b832d…`, 3024 bytes, ICC v2, classe `mntr`).

**Alternativas**: o `srgb.icc` do Ghostscript, que a prova de conceito usou, não tem licença de
redistribuição escrita; o `sRGB_v4_ICC_preference.icc` é v4 e perceptual, com 60 KB; um perfil gerado
aqui seria nosso, mas não o de referência. O do ICC tem a licença mais aberta possível ("copied,
distributed, embedded … without restriction") para o perfil inalterado.

**Sem compressão**: 3 KB não justificam fazer os bytes do documento dependerem da `zlib` da máquina —
a razão de a fonte embutida vir comprimida de antemão (`fontes/ORIGEM.md`).

## R-005 — A família embute a Edital Sans e é medida por ela

**Decisão**: `render_documento` desenha com a Edital Sans nos mesmos recursos `F1` e `F2`, e **recusa**
composição medida pela Helvetica. Os cinco chamadores passam `Composicao(metrica=METRICA_DO_EDITAL)`.

**Por quê**: desenhar com uma fonte e justificar pela largura de outra deixaria linhas além da margem
nos caracteres em que as tabelas divergem ("í", "ª", "º"). A recusa torna o erro impossível de passar
calado.

**Medido**: nos exemplares de comprovante, resultado, inscrições, convocados e agenda, o texto extraído
é o mesmo palavra a palavra, e o número de páginas é o mesmo (SC-2824). Os arquivos crescem de ~11–27
KB para ~68–85 KB — a fonte, ~51 KB comprimida, é o grosso.

## R-006 — O escritor antigo, congelado

**Decisão**: o corpo de `render_documento` até a `178` vira `_documento_com_a_helvetica`, sem mudança
de um byte, e `render_documento(..., pdfa=False)` o chama. Só `render_comprovante_pdf(pdfa=False)` o
pede.

**Medido**: `render_comprovante_pdf(conteudo, pdfa=False)` reproduz `comprovante_v1.pdf`, a fixture da
`main` de 12/10.

## R-007 — O corte gravado na inscrição

**Decisão**: `Inscricao.comprovante_em_pdfa`. A migration o cria falso em toda linha existente e só
depois muda o padrão para verdadeiro; o envio o grava verdadeiro.

**Alternativas**: uma data de corte no código (rejeitada em D-005); um `NULL` para "antes" (a coluna
booleana com padrão diz o mesmo sem o terceiro estado).

**O gatilho da enviada**: `ADD COLUMN ... DEFAULT false` é alteração de catálogo no PostgreSQL 11+ e não
percorre linha; o `inscricao_enviada_imutavel` (`0007`) não dispara. O teste desfaz e refaz a migration
sobre uma inscrição enviada pelo caminho da aplicação.

## R-008 — A validação no CI, em lote

**Decisão**: um job `pdfa` grava os nove exemplares (`PDFA_EXEMPLARES`), roda o veraPDF uma vez sobre a
pasta, e `scripts/conferir_o_verapdf.py` compara o relatório JSON com o manifesto. O veredito `test`
passa a exigir o job.

**Por que o manifesto**: o veraPDF valida cada arquivo contra o nível que ele **declara**. Sem o
manifesto, um documento que passasse a declarar 2b passaria verde. Provado com sabotagem local: um
exemplar com `conformance B` e outro sem `/F 4` reprovaram, com o arquivo e a regra (6.3.2-1).

**A imagem**: `verapdf/cli:v1.30.4`, presa pelo resumo `sha256:f085855d…`. Pelo espelho
`mirror.gcr.io` primeiro, como as outras imagens do workflow, com o Docker Hub de reserva.

## Resultado no veraPDF 1.30.4 (16/11/2026)

| Exemplar | Declara | Resultado |
|---|---|---|
| Edital publicado | 2u | PASS |
| Retificação (consolidado) | 2u | PASS |
| Comprovante (novo) | 2u | PASS |
| Resultado divulgado | 2u | PASS |
| Publicação das inscrições | 2u | PASS |
| Publicação dos convocados | 2u | PASS |
| Agenda | 2u | PASS |
| Relatório do Edital | 2a | PASS |
| Relatório consolidado | 2a | PASS |
| Cenários A e B da auditoria (5 PDFs) | 2u | PASS |
| Prévia do Edital | — | não declara (D-003) |
