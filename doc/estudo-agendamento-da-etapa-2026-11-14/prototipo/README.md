# Protótipo navegável do agendamento

```bash
python3 doc/estudo-agendamento-da-etapa-2026-11-14/prototipo/servidor.py 8166
```

Abra <http://localhost:8166/>. No painel do app, a entrada `agendamento-prototipo` do
`.claude/launch.json` faz o mesmo.

## Como é feito

- **Folhas reais, sem cópia.** O servidor serve `/static/shared/`, `/static/interface/` e
  `/static/portal/` direto de `backend/processo_seletivo/*/static/`. As telas da gestão carregam as
  sete folhas de `FOLHAS_DA_GESTAO`; as de conferir, também `telas/convocacao-conferir.css`, como a
  tela real. As peças novas estão em `static/agenda.css` (gestão), `static/agenda-portal.css` e
  `static/agenda-correio.css` (a moldura dos e-mails, transcrita de `estilos.json`).
- **CSP de produção.** `style-src 'self'; script-src 'self'`. Nenhum estilo ou script em linha.
- **Páginas são fragmentos** em `paginas/`, envolvidos pelo servidor na moldura da gestão, do portal
  ou do e-mail.
- **Estado no `sessionStorage`**, para o percurso atravessar as páginas. "Recomeçar" o apaga.
  Nada fala com o GPS.

## O que foi verificado (14/11, Chromium do painel)

| # | Verificação | Resultado |
|---|---|---|
| 1 | Etapa sem agenda mostra o estado vazio e o caminho | ok |
| 2 | Configuração 23/11, 08–12 e 13–17, 10+5, 1 banca = 32 horários; "Faltam 11" para 43 | ok |
| 3 | Acrescentar 24/11 leva a 64, "Cabem as 43, sobram 21" | ok |
| 4 | Janela 13:00–13:10 com 20 min recusa, e o botão de salvar desabilita | ok |
| 5 | Preencher mostra a prévia (32 recebem, 11 sobram) e só "Aplicar" grava | ok |
| 6 | Outro operador ocupa o horário escolhido: recusa nomeada e grade atualizada | ok |
| 7 | Conferência com 9 sem horário: impedimento com a lista e "Voltar à montagem" | ok |
| 8 | Conferência completa: fatos, prévia pública, mensagem, autoridade; publicação | ok |
| 9 | Agenda publicada: 41 enviados, 1 na fila, 1 não entregue com reenvio | ok |
| 10 | Remarcação com horário e motivo; só a pessoa é avisada; "remarcado em" | ok |
| 11 | Página pública no celular, busca por nome; área do candidato com o aviso de mudança | ok |
| 12 | E-mail de remarcação na moldura do GPS, no celular | ok |
| 13 | Cenário B: duas bancas lado a lado; página pública só com protocolo | ok |
| 14 | Console sem erro nem violação de CSP | ok |

Dois achados do próprio protótipo, já corrigidos nele: o portal tem uma classe `.protocolo`
(caixa com borda) que as peças novas não podem reusar; e o `display` das listas vence o `hidden`, o
que a busca precisa forçar.

## O que não está no protótipo

- o cancelamento da R-22 (só a sinalização da inclusão, R-21);
- a tela da Ocorrência com o horário (entrega D);
- o Centro de Controle e Minhas atividades com a pendência "montar a agenda";
- a escolha do veículo da publicação (Q-3), que seguiria a `159`.
