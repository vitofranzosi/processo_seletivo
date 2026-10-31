# Pendências da auditoria institucional de 30/10/2026 — o que já se resolveu, e o que segue aberto

Conferido em 31/10/2026 na `main` em `ca1e53ed` (depois do #343, da `106` no #345 e da `107` no
#346), e na branch da `109`. É o item 7 do pedido da `109`, e **não reescreve** a
[auditoria](auditoria-administracao-institucional-2026-10-30.md), que fica como o retrato de
30/10. A nota de 31/10 da própria auditoria (PR #347, *Atualização de 31/10/2026*, no resumo
executivo) já registra o que mudou nos papéis, no registro de unidades, na marca e no canal; este
documento não a repete, e a usa como ponto de partida.

> **Não viram escopo por estarem escritas aqui.** Priorizar é do usuário. A coluna "Situação" diz o
> que o código faz hoje, e não o que deveria fazer.

## Legenda

| Situação | Quer dizer |
|---|---|
| **resolvida** | o código da `main` cobre a lacuna, com teste |
| **resolvida em parte** | cobre o mecanismo; falta o que a coluna "Falta" diz |
| **em andamento** | há sessão ou PR aberto, sem merge |
| **aberta** | nada mudou desde 30/10 |

## A matriz (§3 da auditoria)

| # | Capacidade | Situação | Por quê | Falta |
|---|---|---|---|---|
| M-01 | Autenticar servidor na gestão | **resolvida em parte** (`106`) | adaptador de contrato fixo, sessão institucional, produção recusa o seletor em execução e provedor de teste | o adaptador real do provedor (decisões 1 e 6 de `doc/ativacao-do-sso-institucional.md`); a gestão responde 503 em produção |
| M-02 | Atribuir papel a uma pessoa | **resolvida** (`106`, `107`) | vínculo pessoa × unidade × papel no banco, concedido pela tela "Acessos da unidade", com confirmação, motivo e trilha | — (a demonstração continua com autoconcessão, por desenho) |
| M-03 | Vincular a unidade; atuar em mais de uma | **resolvida** (`106`, `107`) | vínculos em várias unidades, unidade ativa, troca pela barra sem levar permissão | — |
| M-04 | Revogar quem saiu | **resolvida** (`106`, `107`) | revogação na tela, válida na requisição seguinte; "quem atua na unidade" por pessoa | — |
| M-05 | Registrar entrada, saída e papéis da sessão | **resolvida** (`106`, `107`) | eventos `ENTRADA`, `SAIDA`, `TROCA_DE_UNIDADE`, `ACESSO_CONCEDER`, `ACESSO_REVOGAR`; término por prazo na trilha | a leitura dessa trilha é a M-22 |
| M-06 | Conferir o identificador de membro da comissão | **aberta** | o `identity_subject` da comissão continua texto livre | a busca da pessoa na inclusão (fora da `107`, de propósito) |
| M-07 | Segregação por pessoa | **resolvida em parte** (`106`) | no modo institucional o `subject` é o identificador interno da pessoa, estável | a segregação mais estrita é emenda à FR-021 da `001`, fora da ativação |
| M-09 | Registrar nova unidade | **aberta**, por decisão | o mecanismo continua o `unidades.json` + `sincronizar_unidades`; a orientação de 31/10 o mantém até revisão arquitetural própria | o autor real na trilha (ator `implantacao`) |
| M-10 | Renomear unidade sem afetar o publicado | **resolvida em parte** (`060`, `109`) | o PDF e o comprovante leem o ato; com a `109`, a página pública da seleção também | a Q-5; o cartão da vitrine continua com a sigla atual do registro |
| M-11 | Operar uma segunda unidade | **em andamento** (`109`) | a marca, a assinatura e o canal passam a vir do registro | ver a §Segunda unidade abaixo |
| M-13 | Substituto e delegação | **aberta** | — | a Q-4 |
| M-14 | Ver quem cadastrou ou encerrou uma autoridade | **em andamento** (sessão "Trilha da unidade, só leitura", `108`) | — | o merge |
| M-15 | Vigência retroativa assimétrica | **aberta** | — | investigar |
| M-16 | Mudar o canal de atendimento | **em andamento** (`109`) | canal opcional por unidade no registro; o `PORTAL_ATENDIMENTO` vira o institucional e a recaída | a P-2 da `109` |
| M-17 | Identidade institucional no código | **em andamento** (`109`) | a sigla da unidade sai do registro; a do Ifes fica em constante | — |
| M-18 | Diagnosticar aviso não enviado | **aberta** | — | o grupo 3 (correio) |
| M-19 | Diagnosticar código de acesso e comprovante | **aberta** | — | idem |
| M-22 | Consultar a trilha administrativa | **em andamento** (`108`) | — | o merge |
| M-23 | Exportar a trilha | **aberta** | — | a Q-6 |
| M-24 | Ver falhas operacionais | **aberta** | — | a auditoria propôs não criar central |
| M-25 | Retenção e descarte | **aberta** | a `auth_user` da `106` acrescentou nome e e-mail de servidores ao que a política precisa cobrir | a Q-7 |
| M-26 | `seed_demo` em produção | **resolvida** (#343) | a marca `AMBIENTE_DE_PRODUCAO` recusa antes de qualquer escrita | — |
| M-28 | Numerar o Edital | **aberta** | — | a Q-10 |
| M-29 | Códigos de modalidade do Registro Acadêmico | **aberta** | — | a Q-11 |
| M-30 | Base de CEP | **resolvida em parte** (#343) | o alerta nomeia as duas causas; o runbook diz que o job não baixa o arquivo | o responsável pela reposição, "a definir pela instituição" |

As linhas que a auditoria marcou "manter" ou "—" (M-08, M-12, M-20, M-21, M-27) não tinham
pendência, e não se repetem.

## As jornadas (§4)

| Jornada | Situação |
|---|---|
| J-1, cadastrar ou ativar uma unidade | **aberta**, pelo mesmo mecanismo (M-09); a `109` acrescenta o canal opcional ao arquivo |
| J-2, substituir a autoridade | sem pendência na auditoria |
| J-3 e J-4, conceder e revogar acesso | **resolvidas** pela `107` |
| J-5, diagnosticar notificação | **aberta** (grupo 3) |
| J-6, alterar configuração institucional sem mudar código | **em andamento**: a `109` tira do código a sigla e o canal por unidade |
| J-7, primeiro acesso em produção | **resolvida em parte**: o comando de administração institucional existe (`106`, `107`); falta o provedor real |
| J-8, saber quem alterou uma autoridade | **em andamento** (`108`) |
| J-9, exclusão do piloto | **resolvida** (#343, evento por unidade) |

## Os riscos (§5)

| Risco | Situação |
|---|---|
| R-1, identidade inexistente em produção | **resolvido em parte**: a arquitetura existe; o provedor real, não |
| R-2, autoconcessão na demonstração | **aceito**: o seletor continua igual, e produção o recusa |
| R-3, o Gestor concentra capacidades | **mitigado**: a concessão de acesso é papel próprio, separado do Gestor (decisão 4 do roteiro de ativação) |
| R-4, trilha sem leitor | **em andamento** (`108`) |
| R-5, silêncio do correio | **aberto** |
| R-6, retenção indefinida | **aberto** |
| R-7, `seed_demo` sem guarda | **resolvido** (#343) |
| R-8, eventos com escopo vazio | **aceito por decisão**, inalterado |

## As questões institucionais (§9)

| # | Situação |
|---|---|
| Q-1, de onde vêm papel e unidade | **decidida** (parecer de 30/10 e `106`): o diretório só autentica, e os vínculos ficam no GPS — o comentário acima do `PAPEIS` foi corrigido na `109` |
| Q-2, qual provedor | **aberta** (decisão 1 do roteiro de ativação) |
| Q-3, administração global | **decidida** em 30/10: duas pessoas designadas por ato formal (decisão 3 do roteiro) |
| Q-4 a Q-8, Q-10, Q-11 | **abertas** |
| Q-9, quando entra a segunda unidade | **aberta**; a `109` prepara o que não depende da data |

## Segunda unidade: o que a `109` faz, e o que continua dependendo de decisão

O que passa a sair do registro, sem mudar código, está no
[inventário da `109`](../specs/109-identidade-multiunidade/inventario.md). O que continua aberto,
com a resposta provisória que preserva o Cefor, está nas perguntas P-1 a P-7 do
[`research.md` da `109`](../specs/109-identidade-multiunidade/research.md). A mais relevante é a
P-1: o que o portal, a página de acesso, a 404 e o código de acesso dizem quando houver mais de uma
unidade ativa. A `109` implementa "Ifes" sozinho.

O cadastro continua o `unidades.json` e o `sincronizar_unidades`. O que precisaria ser revisto para
administrar as unidades pelo banco está no mesmo `research.md`, em *As dependências do
`unidades.json` que permanecem*.
