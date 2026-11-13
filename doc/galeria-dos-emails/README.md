# Galeria dos e-mails do GPS

Prévias de cada e-mail que o GPS envia, com dados fictícios. Nada aqui foi enviado.

- `depois/` — o HTML e o texto puro (com o assunto) de cada mensagem, e o `index.html` com as prévias
  lado a lado, em 600 e em 375 px. Abre direto do disco.
- `antes/` — as mensagens como saíam antes da auditoria de 13/11/2026: texto puro, e o HTML da
  convocação.

O relatório da auditoria está em [`../auditoria-dos-emails-2026-11-13.md`](../auditoria-dos-emails-2026-11-13.md).

## Gerar de novo

De `backend/`, sem banco:

```bash
uv run python scripts/galeria_dos_emails.py --saida ../doc/galeria-dos-emails/depois
```

O script grava também um `.eml` por mensagem, que abre num cliente de e-mail de verdade — Apple Mail,
Outlook, Thunderbird — sem envio. Os `.eml` não são versionados: levam data e Message-ID novos a cada
geração.

## Capturas de tela

Não são versionadas. Para tirá-las, com o Chrome instalado, de `doc/galeria-dos-emails/depois/`:

```bash
for f in [0-9]*.html; do "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=680,1500 --screenshot="$PWD/${f%.html}-600.png" "file://$PWD/$f"; done
```

A captura em 375 px precisa de uma moldura: o Chrome sem janela não desce abaixo de ~500 px de
largura, e a captura direta sai cortada. Abra a página num `<iframe width="375">` e capture a moldura.
