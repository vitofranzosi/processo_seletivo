# Verificação — 063 · Acompanhamento pela situação do candidato

Medido em 07/10/2026 no navegador do painel, numa cópia (`ps_063_demo`) do banco de demonstração
da `062` (`ps_062_demo`), já nas migrations da `main` (a `063` não tem migration). Servidor na porta
8063, com cookies próprios da porta, `PORTAL_IDENTIDADE_DEMO=true` e `INTERFACE_SELETOR_IDENTIDADE=true`.
Cada pessoa entrou pelo portal com o próprio e-mail e o código lido do log do servidor; o desfecho
do caso (e) foi registrado pela gestão, na tela da convocação, como `paulo.presidente`. Nenhum
passo da jornada usou shell.

## 1. Os cinco casos, a 1280 × 900

| Caso | Quem | O que a tela disse |
|---|---|---|
| (a) duas listas | Edson Ferreira da Silva, Edital 72/2026, Técnico de Laboratório | Situação **Aguardando chamada**. Por quê: "Ampla concorrência: 8º lugar no resultado definitivo de Classificação final — Técnico de Laboratório, publicado em 23/09/2026."; "Pessoas pretas, pardas e indígenas: 2º lugar …"; "Você concorre em mais de uma lista, e cada lista tem a sua classificação." Dois cartões: "Ampla concorrência — Classificação final — Técnico de Laboratório" (8º lugar) e "Pessoas pretas, pardas e indígenas — Classificação final — Técnico de Laboratório" (2º lugar). Captura: [a-duas-listas-1280](capturas/a-duas-listas-1280.jpg) |
| (b) classificação sem ocupação | o mesmo | "Nada por enquanto." e "Novas chamadas, se houver, serão publicadas conforme o Edital." Nenhuma palavra de ocupação, embora o recorte tenha apuração emitida. |
| (c) cadastro reserva | o mesmo | "O Edital prevê cadastro reserva de até 9 pessoas para este Perfil." e "As convocações deste Perfil são feitas por mensagem individual à pessoa convocada." Nada de pertença ao cadastro. |
| (d) convocação aberta | Mariana Coutinho Reis, Edital 72/2026, Matemática | Situação **Convocado**. Por quê: "Convocação para vaga inicial pela lista Ampla concorrência, 1ª chamada, registrada em 01/10/2026." O que fazer: "Preencher o Requerimento de Matrícula." (botão), "Prazo desta convocação: até 09/10/2026 às 18h00." e "Se você não atender no prazo, a comissão poderá registrar o não atendimento desta convocação." Abaixo, o painel da convocação só com os dados. Captura: [d-convocacao-aberta-1280](capturas/d-convocacao-aberta-1280.jpg) |
| (e) desfecho | Ana Silva, Edital 51/2026, depois do *Aceite* registrado pela gestão | Situação **Vaga aceita**. Por quê: "Registrado em 07/10/2026: Aceite da vaga manifestado pela candidata no prazo da convocação." e a convocação. O que fazer: "Nada por enquanto." e o caminho para conferir o Requerimento enviado. Nenhum "matriculado". Captura: [e-vaga-aceita-1280](capturas/e-vaga-aceita-1280.jpg) |

**Contratação.** Nenhum ato do domínio a confirma (L-3), e a demonstração não a mostra. O Edital
72/2026 da demonstração, de servidor, declara Requerimento de Matrícula na convocação — é por isso
que a Mariana lê "Requerimento de Matrícula": a tela diz o que o Edital declarou, sem decidir por
tipo de certame (princípio 6).

## 2. A 375 px

| Caso | `scrollWidth` | `clientWidth` |
|---|---|---|
| (a)–(c) Edson | 375 | 375 — nenhum elemento de `main` passa da borda |
| (d) Mariana | 375 | 375 |
| (e) Ana | 375 | 375 |

Captura: [a-duas-listas-375](capturas/a-duas-listas-375.jpg).

## 3. A suíte

`make lint check test-pg DB_NAME=ps_063`: lint e formatação limpos (1306 arquivos), `check` sem
problemas, **9438 passando e 11 pulados** em 1180 s — os mesmos onze do `AGENTS.md`. Depois das correções da revisão de código (08/10), **9446 passando e 11 pulados** em 925 s.

## 4. O que se viu e não é desta feature

- O Cronograma do Edital 72/2026 diz, num evento, "Convocação dos classificados dentro das vagas
  imediatas". É texto do Edital, no bloco do processo, e não afirmação da tela sobre a pessoa.
- Ana Silva foi convocada no Edital 51/2026 com o resultado ainda preliminar e a janela recursal
  aberta, e por isso o topo dela oferece recurso ao lado de "Vaga aceita". É o estado que o
  `seed_demo` monta, e a tela o diz como ele está.
