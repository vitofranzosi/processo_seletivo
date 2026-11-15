# Contrato: telas e rotas

As telas seguem as do protótipo aprovado (`doc/estudo-agendamento-da-etapa-2026-11-14/prototipo/`,
segunda rodada, `04-redesign.md`); o arquivo de cada uma está na coluna *Protótipo*. As frases estão
em [recusas.md](recusas.md). Ajuste visual que mude a interação volta ao protótipo antes (Assumptions).

## Gestão

Prefixo: `editais/<uuid:edital_id>/agenda-da-etapa/<uuid:etapa_id>/` (namespace `interface`). Toda
rota passa pela guarda comum (research T-021): Edital fora do escopo → 404; sem a base da gestão da
comissão — a permissão de gerir a comissão, ou a presidência (`D-013`) — → recusa da gramática das
portas; os comandos repetem a conferência no servidor; Etapa ausente da versão vigente → 404. Cada 404 tem linha no
inventário da `033`.

| Rota | Nome | Método | O que faz | Protótipo | Entrega |
|---|---|---|---|---|---|
| *(página da Etapa)* `editais/<e>/distribuicao/<etapa>` | `distribuicao` | GET | seção "Agenda": vazio que ensina (UX-765) e "Configurar a agenda"; com agenda, o estado e o caminho | `etapa.html` | A |
| `configurar` | `agenda-configurar` | GET, POST | formulário: forma (controle segmentado), duração, intervalo, um dia por linha com pares de horas e "+ janela", uma banca por linha, orientações; ao lado (abaixo no estreito), o simulador. POST grava ou recusa a lista inteira (§1); com `atalho`, devolve o formulário acrescido sem gravar | `configurar.html` | A |
| `capacidade` | `agenda-capacidade` | POST (htmx) | fragmento do simulador: veredito, medidor, conta numa linha, sobras, atalhos com o ganho, "lista ainda aberta"; nunca grava (FR-7205, UX-760) | `configurar.html` | A |
| `montar` | `agenda-montar` | GET | cabeçalho com a ação que falta (UX-764), resumo único com o `.medidor` (UX-761), abas por dia com "ocupados/total", grade horário × banca, painel de ação | `montar.html` | A |
| `painel` | `agenda-painel` | GET (htmx) | `?pessoa=<inscricao>`: a pessoa, o seletor de horário (dia em botões, horários livres por banca), "Mudar de horário" e "Liberar"; `?horario=<banca>@<inicio>`: o horário livre e quem está sem horário, com busca `?busca=`; sem parâmetro: "Pessoas sem horário" e "Não participa mais" (FR-7217) | `montar.html` | A |
| `preencher` | `agenda-preencher` | POST (htmx) | sem `assinatura`: a prévia no painel (veredito, tabela dia × banca, sobras, ordem, "Ver quem vai para cada horário"), nada gravado (FR-7214); com `assinatura`: aplica ou recusa `agenda_mudou_desde_a_previa` com a prévia nova (FR-7215) | `montar.html` | A |
| `agendar` | `agenda-agendar` | POST | agenda ou muda uma pessoa (`inscricao`, `banca`, `inicio`); recusa `horario_ocupado`, `pessoa_ja_agendada`, `pessoa_nao_participa` (§3) | `montar.html` | A |
| `liberar` | `agenda-liberar` | POST | libera o horário de uma pessoa antes da publicação | `montar.html` | A |
| `conferir` | `agenda-conferir` | GET | a moldura da conferência da `140` (`convocacao-conferir.css`): quatro linhas de prontidão, impedimentos com o caminho, fatos, prévia exata da página pública, assunto e texto da mensagem de uma pessoa, os avisos que a publicação criará — quantos e para quem — ou a frase de que estão desligados (`D-011`), veículo, autoridade e o botão "Publicar a agenda e avisar as pessoas"; não grava nada (FR-7220 a FR-7222) | `conferir.html` | B |
| `publicar` | `agenda-publicar` | POST | `assinatura`, `autoridade`, `veiculo`, `declaracao` ou `onde`/`quando`, `idempotency_key`; cria o ato ou devolve o existente (FR-7223); redireciona para `publicada` | `conferir.html` | B |
| `publicada` | `agenda-publicada` | GET | "Documento da publicação" e o de cada ato posterior (`D-012`); resumo dos avisos num número só e o detalhe (enviados, na fila, não entregues com "Reenviar o aviso"; ou "avisos desligados"); "Passou a participar depois da publicação" com "Agendar esta pessoa"; "Tem horário e não participa mais" com "Cancelar o agendamento"; a lista vigente com "Remarcar" por linha (FR-7233, FR-7240) | `publicada.html` | B (lista, entrantes e saintes), C (avisos) |
| `remarcar/<uuid:inscricao_id>` | `agenda-remarcar` | GET, POST | o horário atual, o seletor de horário (o mesmo componente), "de → para" à vista, o motivo e "Remarcar e avisar esta pessoa"; para quem não tem horário publicado, a mesma tela é a inclusão, com "Agendar e avisar esta pessoa" (FR-7241, FR-7242) | `remarcar.html` | C |
| `cancelar/<uuid:inscricao_id>` | `agenda-cancelar` | GET, POST | quem deixou de participar, o motivo e "Cancelar o agendamento" (FR-7243) | *(não está no protótipo; segue a moldura de `remarcar.html`)* | C |
| `reenviar` | `agenda-reenviar` | POST | `aviso`, `chave_idempotencia`: o aviso filho de quem não recebeu, com o mesmo texto; recusa `aviso_nao_reenviavel` (T-024) | *(não está no protótipo)* | C |

`montar` com a agenda publicada não tem "Preencher automaticamente" nem "Liberar"; cada linha leva a
"Remarcar" (US5, cenário 1). `agendar`, `liberar` e `preencher` recusam `agenda_publicada`.

O reenvio é da própria agenda publicada (research T-024): `reenviar` (POST, `aviso`), que repete o
texto da pessoa num aviso filho; a tela de reenvio da `066` recusa a origem `AGENDA`, como recusa a
pendência da `134`.

## Portal

| Rota | Nome | O que mostra | Protótipo | Entrega |
|---|---|---|---|---|
| `<uuid:edital_id>/` (seleção) | `selecao` | a seção "Agendas", por `_agendas_da_selecao.html`: uma linha por agenda publicada, com a Etapa e o período | `publica.html` | B |
| `agendas/<uuid:agenda_id>/` | `agenda-da-etapa` | cabeçalho (unidade, Edital, Etapa, signatário, veículo, data); os documentos dos atos, em ordem, com a frase de que a agenda vigente é a publicação com os atos posteriores (FR-7248); busca `?busca=`; a agenda vigente por dia, cada horário com hora, banca (se mais de uma), nome e protocolo ou só protocolo (`D-009`), e "remarcado em" (FR-7227, FR-7245); nunca o endereço da sala (FR-7226) | `publica.html` | B |
| `agendas/<uuid:agenda_id>/atos/<uuid:ato_id>/documento.pdf` | `agenda-documento` | os bytes gravados do documento do ato, com `ETag` e `attachment`, nada recomposto, como `convocados_em_pdf` da `149`; sem linha, 404 (FR-7224, FR-7248, `D-012`) | — | B (publicação), C (atos individuais) |
| `inscricoes/<uuid:inscricao_id>/` | `inscricao` | o bloco "Seu horário", por Etapa com agenda (FR-7228, FR-7229, FR-7245) | `candidato.html` | B |

O e-mail segue `email.html` do protótipo, na moldura comum de `shared/correio` (entrega C).

## Fora das telas

| Comando | Quando |
|---|---|
| `manage.py despachar_avisos` | envia os avisos da origem `AGENDA` como os demais (C); em desenvolvimento, à mão |
