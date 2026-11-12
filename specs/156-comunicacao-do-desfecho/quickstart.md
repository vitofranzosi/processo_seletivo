# Quickstart: verificar a 156

Roteiro de verificação, de ponta a ponta. Os dados são fictícios.

## Pré-requisitos

- Worktree própria e banco de teste próprio (`DB_NAME` único), com `backend/.env` copiado.
- `cd backend && uv sync --extra dev`.
- `LC_ALL` exportado no macOS.

## Suíte

```bash
cd backend && make lint check test-pg
```

O que precisa passar, além do resto:

- `tests/test_situacoes_de_mensagem.py`: seis situações, três no despacho, e a revisão da `156` na
  FR-084 escrita;
- `tests/test_vocabulario_do_desfecho.py` (nova, SC-2120), com as varreduras de vocabulário da
  convocação, dos documentos, do Requerimento e do aviso;
- `tests/seguranca/test_homologacao_preservada.py`: 60 tabelas append-only;
- `tests/integration/test_database_permissions.py`: as duas tabelas novas sem `UPDATE` nem `DELETE`.

O provisionamento informa `N de 60`.

## No navegador

1. Suba um banco de demonstração com o cenário de treinamento C09 (`carregar_cenarios_de_treinamento`,
   com `CENARIOS_DE_TREINAMENTO=true`) e o runserver com `INTERFACE_SELETOR_IDENTIDADE=true`.
2. Pela gestão, convoque e registre os três desfechos do estudo: **aceite** (Alice), **desistência**
   (Cecília, primeiro pelo pedido no portal) e **não atendimento** (Davi, pelo lote dos vencidos).
3. Pelo portal, com o código de acesso que sai no terminal do servidor, abra a convocação e o
   acompanhamento de cada um, **a 390 px e em tela larga**:
   - aceite: *"Vaga aceita"*, a frase simples, *"O Edital explica o que vem depois em «…»"* com o
     caminho para a página do Edital, e o contato como link;
   - desistência: o pedido com protocolo, a frase de que pedir ainda não é desistir, os envios ainda
     oferecidos, o cancelamento, e depois do registro a frase da desistência;
   - não atendimento: a data do fim do prazo na frase simples, o fundamento só dentro de *"Fundamento
     do registro"*;
   - em nenhuma: *"faixa vigente"*, *"recorte"*, *"Espécie"* ou *"o atendimento institucional"* fora
     do fundamento recolhido.
4. Na gestão: o cartão com o pedido e o atalho; o "O que fazer agora" com *"Registrar a desistência
   pedida pelo portal"*; o lote dos vencidos sem a pessoa que pediu; a confirmação de encerrar com a
   linha dos pedidos pendentes.
5. Com `AVISOS_DE_DESFECHO=true` e `AVISOS_AOS_CANDIDATOS=true`: marque *"Avisar a pessoa por e-mail"*
   num desfecho, veja *"Aviso solicitado"*, rode `manage.py despachar_avisos` e leia, no terminal
   **do comando**, a mensagem neutra; o cartão passa a *"Aviso enviado em …"*. Com qualquer uma das
   duas desligada, a opção não aparece.

## Evidência para o PR

Capturas das três telas do candidato nas duas larguras, do cartão com o pedido e da mensagem do aviso
no terminal; e a saída do `make lint check test-pg`.
