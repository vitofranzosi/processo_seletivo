# Verificação: Cinco ajustes de leitura dos Documentos Exigidos (132)

Feita em 07/11/2026, na branch `claude/funny-benz-83fc71` sobre a `main` em `cd1d46d9`.

## A suíte

`make lint check test-pg`, com `DB_NAME=spec132`, `TEST_DB_ENGINE=postgresql` e `DB_USER` do
superusuário local, 4 workers, sem o grupo `assistente`, com o grupo `navegador`:

- lint e check verdes;
- **17 332 passaram, 13 pulados, 1 falha**, em 910 s. A falha era
  `integration/convocacao/test_documentos_da_convocacao.py::test_o_fundamento_do_indeferimento_vem_das_pendencias`,
  da `115`, que fixava o motivo **com** o ponto final — o ".;" que a FR-4516 tira. O caso foi
  revisto, com a razão no comentário, e passa; nenhuma outra falha.

Os casos novos: 29 em `interface/test_ajustes_dos_documentos.py`, 5 em
`integration/portal/test_anuncio_dos_documentos.py`, 6 em
`unit/convocacao/test_fundamento_das_pendencias.py` e 5 em `javascript/somente-leitura.test.js`.

## As telas

Num clone descartável de `gps_docs_demo` (`createdb -T gps_docs_demo spec132_demo`, migrado para
a `main` atual; a origem não foi tocada), servido na porta 8132. O Edital 90/2026 está publicado
com oito documentos em dois momentos; o 91/2026 é o rascunho que partiu dele. As capturas estão em
[capturas/](capturas/), pelo Chromium do Playwright, a 1280 px.

| Ajuste | Antes | Depois |
|---|---|---|
| Revisão por momento | `antes-1-revisao-documentos.png`: um bloco, "Documentos Exigidos (8)", com "Pedido" em cada item | `depois-1-revisao-documentos.png` e `depois-1-revisao-documentos-na-convocacao.png`: "na inscrição (4)" e "na convocação (4)", sem "Pedido", números 1–8 mantidos |
| Somente leitura | `antes-2-*`: campos, setas e lixeira ativos no 90/2026 publicado; "Avançar" como botão | `depois-2-*`: campos desabilitados, sem setas, lixeira nem acrescentar; "Avançar ›" como link nas cinco etapas |
| Simulação em leitura | — | `depois-2-classificacao-simulacao.png`: "Simular sorteio" no 90/2026 publicado, como homologador; a prévia responde com o marco "Sorteio público" |
| Ajuda dos documentos | `antes-3-como-preencher.png`: chave, instrução, alcance, modelo | `depois-3-como-preencher.png`: mais momento, aproveitamento, obrigatório e condição |
| Página pública | `antes-4-pagina-publica.png`: "4 documentos que serão pedidos", sem marca | `depois-4-pagina-publica.png`: "1 documento obrigatório na inscrição"; Currículo e Comprovante de residência com "(facultativo)" |
| Fundamento | ver abaixo | `depois-5-fundamento.png` |

**A simulação no navegador de verdade (SC-1403).** O pedido de "Simular sorteio" levou 28
parâmetros do cartão, entre eles o `-name` e o `-orderProduction` do marco, que estão em campos
desabilitados — sem `somente-leitura.js` eles não iriam. O console não registrou violação de CSP
nem erro.

**"Avançar" antes da 132.** No 90/2026 publicado, o clique em "Avançar ›" na Inscrição devolvia a
mesma etapa com "Não foi possível salvar: Este Edital não está em elaboração ou você não tem
permissão para editá-lo." Depois, é link para Anexos.

**O fundamento.** No 93/2026, uma conferência pendente registrada pela tela, no clone, com o motivo
"O arquivo está ilegível: não é possível ler o número do documento." A função antiga, aplicada aos
mesmos itens, dava:

> Documentação exigida na convocação não atendida — Documento de identificação com foto: O arquivo
> está ilegível: não é possível ler o número do documento.; Comprovante de escolaridade; Laudo
> médico atualizado.

A tela agora oferece "…ler o número do documento; Comprovante de escolaridade; Laudo médico
atualizado." Com o motivo no último item, a antiga terminava em "..".

## O que não foi verificado

- A vista do conjunto com mais de um Perfil em somente leitura ("Ver", "Aberto" no lugar de
  "Editar", "Em edição"): o 90/2026 tem um Perfil só, e a vista não monta a tabela. A mudança é de
  rótulo, em `vista-do-conjunto.js`, sem teste automático.
- Telas estreitas: os ajustes não mudam folha nem estrutura dos cartões.
