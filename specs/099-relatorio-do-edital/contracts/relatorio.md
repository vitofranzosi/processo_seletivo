# Contrato: Relatório do Edital

## Rotas (gestão)

| Método | Rota | Nome | Resposta |
|---|---|---|---|
| `GET` | `/gestao/editais/<uuid>/relatorio` | `interface:relatorio-do-edital` | página com a camada executiva e o formulário "Baixar PDF" |
| `POST` | `/gestao/editais/<uuid>/relatorio/pdf` | `interface:relatorio-do-edital-pdf` | `application/pdf`, `Content-Disposition: attachment; filename="relatorio-edital-NN-AAAA-emissao-N.pdf"` |

### Respostas de recusa

| Situação | Resposta |
|---|---|
| sem identidade de sessão | o pedido de identificação da gestão |
| Edital inexistente ou de outra unidade | 404 "não encontrado" |
| da unidade, sem gestão da comissão nem presidência do Processo | 403, a recusa explicada da `033`: *"Esta operação depende da permissão de gerir a comissão ou da presidência deste Processo — cada uma basta sozinha. Peça…"* |
| Edital em elaboração, em revisão ou homologado | 409, *"O relatório fica disponível quando o Edital for publicado."* |
| falha de serialização na emissão | 409, *"Outro registro foi gravado agora. Baixe o relatório de novo."* |

Página e PDF: `Cache-Control: private, no-store` (`marcar_como_privada`).

## Ação no detalhe do Edital

`Acao("Relatório do Edital", url, motivo)` em `interface/acoes.py`: motivo vazio quando a porta e o
estado permitem; motivo preenchido, com o controle desabilitado, quando o Edital ainda não foi
publicado. Quem não alcança a porta não vê a ação.

## Ordem do documento

**Camada executiva** — a primeira página é o painel (FR-2602):

1. Identificação institucional, título e espécie.
2. Ficha: seleção; dados até e o número da emissão; situação no GPS; situação das providências.
3. Visão geral.
4. Principais números: os seis indicadores em cartões.
5. Pontos de atenção.

Em página nova:

6. Resultados por perfil de vaga.
7. Procura ao longo do período (gráfico por dia, ou por semana) ao lado de Alterações e recursos
   (FR-2536, FR-2605).
8. Datas principais, com a natureza de cada uma (FR-2606).
9. Documentos oficiais: a página pública e os resultados vigentes, com link só em host público
   (FR-2539, FR-2603).

**Anexo técnico**, em página nova:

- A. Etapas de avaliação, por Perfil.
- B. Classificação e vagas por lista.
- C. Recursos e convocações por perfil.
- D. Cronograma: previsto, retificado e registrado.
- E. Documentos e verificação.
- F. Como cada número foi obtido.
- G. O que o GPS não registra.
- H. Sobre esta emissão.

Toda página do PDF traz no alto *"Relatório do Edital NN/AAAA · relatório de <espécie>"* e *"dados até
DD/MM/AAAA, HHhMM · emissão nº N"*, e no pé a natureza gerencial e *"página X de Y"* (FR-2552).

## Frases fixas

| Onde | Texto |
|---|---|
| natureza | "Relatório gerencial com base nos registros do GPS. Não é ato administrativo e não substitui as publicações oficiais." |
| espécie, acompanhamento | "Relatório de acompanhamento" + "ainda há providência em curso" ou "o Edital segue publicado" |
| espécie, encerramento | "Relatório de encerramento — não há providência pendente registrada no GPS. Atividades que o GPS não acompanha, como a matrícula, não estão refletidas aqui." |
| espécie, interrupção | "Relatório de interrupção — Edital cancelado em DD/MM/AAAA" |
| integridade | "O resumo SHA-256 permite conferir que um arquivo tem o mesmo conteúdo do documento registrado no GPS. Ele não comprova, sozinho, a publicação oficial: a referência é a página pública da seleção." |
| privacidade | "detalhe omitido: menos de 5 inscrições neste perfil" |
| matrícula | "O GPS não registra matrículas. Este relatório mostra convocações aceitas, e não matrículas efetivadas." |
| endereço local | "O endereço público da seleção não aparece nesta emissão: ela foi feita num ambiente local, e o endereço não valeria para quem recebe o arquivo." |
