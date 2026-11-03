# Quickstart: Documentos e conferência na convocação

Roteiro para demonstrar a feature depois de implementada, pelo portal e pela gestão, sem banco nem
shell (Constituição, VI). Os Editais são **moldes**, com dados fictícios. Os PDFs reais ficam em
`~/Downloads` e não entram no repositório.

## Preparação

- Ambiente local pelo `make preparar`, com `INTERFACE_SELETOR_IDENTIDADE=true`.
- Correio local: o código de acesso do portal sai no terminal do servidor, ou em
  <http://localhost:8025> no compose.
- Três identidades na gestão:
  - a presidência da comissão do Processo;
  - um membro ativo da comissão, alocado à conferência só do Perfil A;
  - um auditor.

## Cenário 1 — Aluno, molde do 72/2026 (US1)

1. Elaborar o Edital do curso técnico com vaga imediata. Na inscrição, a identificação. Na convocação,
   obrigatórios: certidão, histórico, certificado do ensino médio e comprovante de residência.
2. Publicar e ler o PDF: duas seções, *"Quais documentos enviar?"* e a da convocação.
3. Inscrever três candidatos pelo portal: só a identificação é pedida.
4. Encerrar o período, classificar (sorteio ou ordem) e convocar o primeiro, com vencimento.
5. No portal, a convocada vê quatro itens *"Falta enviar"* e envia três.
6. Na gestão, a condução mostra *para conferir*, 3 de 4 recebidos. Abrir **Documentos da convocação**,
   abrir cada arquivo e conferir: dois *conforme* e o histórico *pendente* com motivo.
7. Tentar o aceite: recusado, com os nomes dos itens.
8. No portal, a convocada lê o motivo e envia o histórico de novo, e depois o quarto documento.
9. Conferir os dois *conforme* e registrar o aceite. A linha mostra *"Apto para formalização"*.

## Cenário 2 — Bolsista, molde do 146/2025 (US2)

1. Edital de uma vaga, sem Requerimento de Matrícula. Na convocação, *Ficha de Cadastramento/Termo de
   Compromisso*, obrigatória, com o modelo como anexo do Edital.
2. Classificar e convocar. No portal, baixar o modelo, apresentar o PDF assinado.
3. Conferir *conforme* e aceitar. Nenhuma tela diz bolsa concedida ou vinculado.

## Cenário 3 — Aproveitamento, molde do certificado do 89/2026 (US3)

1. Edital de vaga imediata, com dois Documentos Exigidos:
   - na inscrição, *Certificado do curso de formação*, facultativo;
   - na convocação, o mesmo, obrigatório, *atendido pelo documento da inscrição*.
2. Inscrever a candidata A com o certificado e o candidato B sem ele.
3. Convocar os dois. No portal de A, o item diz *"Atendido pelo documento enviado na inscrição em
   DD/MM"*. No de B, *"Falta enviar"*.
4. Na gestão, abrir o item de A: é o arquivo da inscrição, com a data do envio original.

## Cenário 4 — Chamada nova da mesma inscrição (US8)

1. No cenário 1, registrar a reclassificação da convocada, depois de dois documentos *conformes* e um
   *pendente*.
2. Convocar de novo a mesma inscrição. No portal, os dois itens dizem *"Aproveitado da chamada
   anterior, enviado em DD/MM. A comissão vai conferir de novo"*, e o pendente diz *"Falta enviar"*.
3. Na gestão, os aproveitados estão *recebido, aguardando conferência*. O "conforme" sem abrir o
   arquivo é recusado.

## Cenário 5 — Um prazo só para a chamada (US4)

1. Edital com Requerimento *na convocação* e documentos na convocação. Convocar com vencimento
   próximo e enviar a comunicação.
2. Depois do vencimento, tentar enviar um documento e o requerimento: as duas recusas têm a mesma
   frase, e o requerimento continua legível.
3. Corrigir a convocação com vencimento novo: os dois reabrem.
4. Repetir num Edital sem documento na convocação: o requerimento também é recusado depois do
   vencimento, com a mesma frase.
5. Convocar sem enviar a comunicação: o requerimento continua aberto, porque o prazo não corre.

## Negativos

| Caso | Como provocar | Esperado |
|---|---|---|
| Acesso indevido | o membro do Perfil A abre a URL de um convocado do Perfil B; o auditor abre um arquivo; um candidato abre a URL de outro | recusa de inexistente; recusa de autorização para o auditor |
| Prazo vencido | convocação com vencimento no passado próximo; enviar depois | recusa com o prazo e "a comissão vai decidir"; nada gravado; nenhum desfecho sozinho |
| Envio duplicado | enviar o mesmo arquivo duas vezes; duplo clique | uma apresentação só, com a resposta "já recebido" |
| Arquivo inválido | foto JPG, PDF renomeado, arquivo vazio, acima de 10 MB | as recusas da inscrição |
| Documento pendente | aceitar com um obrigatório pendente | recusa nomeando o item |
| Sem exigência documental | Edital sem documento na convocação | portal e condução idênticos aos de antes |

## Verificação

```bash
cd backend && make lint check test-pg
```

Com o grupo `navegador` instalado, as três jornadas também rodam em
`tests/navegador/test_jornada_dos_documentos_da_convocacao.py`.
