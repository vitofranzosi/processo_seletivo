# Quickstart: verificar a confirmação da inscrição por e-mail

## Pré-requisitos

O ambiente do README, com o banco preparado e um Edital com inscrições abertas. O jeito mais curto é o
`seed_demo`, cujo Edital com prazo aberto aceita inscrição de quem entra pelo portal. Na execução
nativa, o correio é o de console: **a mensagem sai no terminal do `runserver`**, e é de lá que se lê o
código de acesso e a confirmação. No compose, as duas chegam em <http://localhost:8025>.

## 1. O caminho feliz

1. Entre no portal com um e-mail novo, abra a vaga do Edital aberto, preencha e envie.
2. A tela do comprovante diz **"✓ Inscrição enviada"** e, logo abaixo, "Enviamos a confirmação para
   ‹e-mail› em ‹data› às ‹hora›".
3. No terminal (ou no coletor), a mensagem: assunto **"Sua inscrição foi enviada — Edital NN/AAAA"**,
   protocolo e código de verificação em destaque, "O que acontece agora", o link "Ver meu comprovante",
   e nenhum CPF, telefone ou anexo.

## 2. O link sem sessão

1. Saia do portal e abra o link da mensagem.
2. O portal pede o e-mail; depois do código, abre o comprovante daquela inscrição.

## 3. A falha e a nova tentativa

1. Suba o servidor com um correio que recusa (por exemplo, `DJANGO_EMAIL_BACKEND` apontando para SMTP
   numa porta fechada) e envie outra inscrição.
2. O comprovante diz "Não conseguimos enviar a confirmação…" e oferece **"Enviar a confirmação de
   novo"**. A inscrição está enviada.
3. Volte ao correio de console, aperte o botão: a mensagem sai, e a tela passa a dizer que foi enviada.
4. Apertar de novo numa aba antiga não manda nada.
5. Com o correio fora do ar, apertar "Enviar a confirmação de novo" logo depois da falha não tenta: a
   tela pede para esperar um minuto.

## 4. As provas automatizadas

```bash
cd backend && PYTEST_ADDOPTS="tests/integration/inscricoes/test_confirmacao_por_email.py tests/integration/portal/test_confirmacao_de_inscricao.py tests/unit/test_apresentacao_dos_emails.py tests/integration/test_envios_em_duas_partes.py tests/test_situacoes_de_mensagem.py" make test-pg PYTEST_WORKERS=0 DB_NAME=ps_181
```

E, antes do PR, `make lint check` e a suíte inteira contra PostgreSQL (uma de cada vez no cluster).
