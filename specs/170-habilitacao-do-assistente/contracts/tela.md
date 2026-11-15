# Contrato da tela: "Assistente do Edital"

Na administração institucional, ao lado de "Unidades". Ela é oferecida na barra só a quem tem
`assistente:habilitar` no escopo institucional (FR-7513).

## Rotas

| Rota | Método | O que faz |
|---|---|---|
| `/gestao/administracao-do-assistente` | GET | a página |
| `/gestao/administracao-do-assistente/piloto/<habilitar\|desabilitar>` | GET, POST | GET mostra a confirmação; POST com motivo confirma |
| `/gestao/administracao-do-assistente/editais/<uuid>/<habilitar\|desabilitar>` | GET, POST | idem, para a página pública de um Edital |

Toda rota exige a permissão no escopo institucional e a entrada institucional. Sem isso, ela recusa
com 403, antes de ler qualquer coisa, como em Unidades.

## A página

1. **Configuração do serviço.** Diz "configuração completa" ou lista o que falta, em palavras
   (UX-810). Mostra o serviço, o modelo, o endereço e o tempo-limite, e "credencial: presente" ou
   "ausente", nunca o valor. Com a configuração completa, lembra o comando de verificação da `073`.
   Abrir a página não chama o modelo.
2. **Piloto da gestão.** Mostra o estado (habilitado desde quando, por quem e com que motivo; ou
   desabilitado) e o botão de habilitar ou desabilitar. O botão só aparece com a configuração
   completa. Se a configuração estiver incompleta e o piloto habilitado, a seção diz as duas coisas.
   Se o atalho estiver ligado, ela diz "demonstração ligada neste ambiente".
3. **Página pública dos Editais.** Lista os Editais com seleção pública: número, ano, unidade, título
   e estado. Cada um tem o botão de habilitar ou desabilitar. Um Edital habilitado que perdeu a
   página aparece como "sem página pública". **Em produção**, a seção diz que a página pública não
   abre enquanto os requisitos estiverem pendentes, e não oferece habilitar.
4. **Requisitos da abertura em produção.** Mostra `RA-1` a `RA-12`, com a espécie de cada um, todos
   pendentes. É só leitura.
5. **Histórico.** Todos os atos, do mais recente para o mais antigo, com autor pelo nome, instante,
   frente, Edital e motivo.

## A confirmação

A confirmação diz a consequência antes do motivo (UX-812). O campo de motivo é obrigatório. O POST
reconfere tudo no servidor (FR-7531).

| Recusa | Código | Status | Quando |
|---|---|---|---|
| Sem motivo | `motivo_obrigatorio` | 422 | o motivo está vazio depois de aparado; volta à mesma confirmação |
| Configuração incompleta | `configuracao_incompleta` | 409 | ao habilitar; a mensagem lista o que falta |
| Nada muda | `assistente_ja_habilitado` / `assistente_ja_desabilitado` | 409 | o estado mudou entre a página e a confirmação, ou o pedido foi montado à mão |
| Sem página pública | `edital_sem_pagina_publica` | 409 | ao habilitar um Edital sem seleção pública agora |
| Produção | `abertura_publica_em_producao` | 409 | ao habilitar a página pública com `AMBIENTE_DE_PRODUCAO`; a mensagem lista `RA-1` a `RA-12` (UX-811) |

## O que muda fora da página

- **A página do Edital na gestão** ganha uma linha para quem a alcança: "Assistente na página
  pública: aberto desde <data>" ou "não aberto" (FR-7522, UX-814).
- **A página pública da seleção**, com `?assistente=encerrado` e sem o painel, mostra o aviso: "O
  assistente desta seleção foi encerrado. As informações oficiais estão nesta página e no Edital."
  (UX-813, R-9).
- **As rotas do assistente no portal** respondem como na `074` quando o Edital não atende. A exceção
  é a sessão que tinha conversa naquele Edital: ela é redirecionada para o aviso, salvo em produção.
- **A tela do piloto e a entrada nela** continuam com a negativa da FR-1464 da `071` quando o piloto
  não atende.
