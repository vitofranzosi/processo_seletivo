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

**Camada executiva**:

1. Identificação.
2. Espécie.
3. Situação no GPS.
4. Situação das providências.
5. Dados até.
6. Visão geral.
7. Indicadores.
8. Pontos de atenção.
9. Resultados por perfil de vaga.
10. Procura.
11. Alterações e recursos.
12. Datas principais.
13. Documentos oficiais.

**Anexo**:

- A. Etapas por Perfil.
- B. Classificação e vagas por lista.
- C. Recursos por Perfil.
- D. Cronograma.
- E. Documentos e verificação.
- F. Como cada número foi obtido.
- G. O que o GPS não registra.
- H. Sobre esta emissão.

Toda página do PDF traz, no rodapé de identificação, *"Relatório do Edital NN/AAAA · dados até
DD/MM/AAAA, HHhMM · relatório gerencial"* e a paginação.

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
