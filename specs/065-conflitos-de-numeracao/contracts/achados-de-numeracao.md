# Contrato — os achados de numeração e de remissão

O que as superfícies existentes passam a receber. Nenhum endpoint, campo ou tela novos: os achados
viajam pela estrutura de pendências que a etapa Conteúdo, a Revisão, a página do Edital, a resposta
da submissão e a confirmação da Retificação já usam.

## 1. Códigos e severidade por ato

| Código | Publicação e submissão | Retificação | Requisito |
|---|---|---|---|
| `typed_numbering_conflict` | **impeditivo** | não emitido | `FR-1200`, `FR-1210`, `D-001` |
| `typed_numbering_conflict_in_retification` | não emitido | aviso | `FR-1213`, `D-002` |
| `typed_numbering_suspected_title` | aviso | aviso | `FR-1201`, `FR-1211` |
| `cross_reference_ambiguous` | aviso | aviso | `FR-1206`, `FR-1211` |
| `cross_reference_without_target` | aviso | aviso | `FR-1207`, `FR-1211` |
| `cross_reference_suspected` | aviso | aviso | `FR-1208`, `FR-1211` |

Garantias:

- **G1** — nenhum código de aviso coincide com o de um impeditivo (a confirmação da Retificação
  descarta os que coincidem).
- **G2** — nenhum achado afirma que uma remissão está correta; não há código, contagem ou texto de
  "remissão conferida" (`FR-1209`, `SC-467`).
- **G3** — o conflito de numeração impede a submissão e a publicação do Edital; nada desta feature
  impede a Retificação (`D-001`, `D-002`).
- **G4** — o Edital publicado não recebe nenhum destes achados fora de uma Retificação em composição
  (`FR-1218`).

## 2. Caminho e destino

| Onde está o texto | Caminho do achado | Destino na interface |
|---|---|---|
| seção textual | `/sections/id=<uuid>/content` | etapa Conteúdo, âncora `#titulo-<chave da seção>` (`D-008`) |
| texto do Perfil (descrição, atribuições, requisito…) | o caminho do campo, como `_textos_impressos` o dá | a etapa dos Perfis, como hoje |
| nome ou instrução de documento exigido | idem | a etapa Inscrição, como hoje |
| descrição ou local de Evento | idem | a etapa Cronograma, como hoje |

## 3. A mensagem

Escrita para quem elabora (`UX-159`): sem código, caminho ou nome de campo; o título da seção como a
tela o mostra; o número da seção igual ao da legenda (`UX-160`). Os exemplos normativos estão na spec
(*Exemplos de mensagem*). Cada mensagem traz:

| Código | Obrigatório na mensagem |
|---|---|
| conflito (os dois) | "comprovado"; a seção pelo título e pelo número impresso, ou "o preâmbulo"; cada parágrafo em conflito, com ordinal, número digitado e trecho de até oitenta caracteres; o número pelo qual os subitens da seção começam; e, na Retificação, que o aviso não impede o ato |
| título transcrito | "suspeita"; seção, parágrafo e a linha |
| ambígua | a remissão literal; onde está; cada item com aquele número; que o sistema não sabe qual foi citado |
| sem destino | a remissão literal; onde está; que o documento não tem item com o número; como deixar explícita a remissão a outro ato |
| suspeita | "suspeita"; a remissão literal; onde está; o motivo |

## 4. Ordem

Seção a seção, na ordem do documento: os achados de numeração de uma seção e logo depois os de
remissão dela; em seguida as remissões dos demais campos (`D-007`, `UX-161`).

## 5. Na Revisão

O conflito, impeditivo, nunca é dobrado. As remissões repetidas se dobram em "{n} avisos de remissão", abrindo-se como as demais (`D-016`).
