# Contrato das rotas de entrada — 075

| Rota | Método | Com seletor | Sem seletor |
|---|---|---|---|
| `interface:identificar` — `/gestao/identificar` | GET | 200, página de acesso; `?proximo=` repassado à escolha | 503, "Autenticação institucional não configurada", sem ação |
| `interface:identificar` | POST | com nome: 302 ao destino seguro, ou à lista (com papel) / Minhas Etapas (sem papel); sem nome: 422 na escolha, com a recusa | 503, nada gravado |
| `interface:identificar-demonstracao` — `/gestao/identificar/demonstracao` | GET | 200, a escolha | 503 |
| `interface:sair` — `/gestao/sair` | POST | 302 à página de acesso | igual |
| qualquer porta da gestão sem identidade | GET | 302 a `/gestao/identificar?proximo=<caminho>` | igual |
| qualquer porta da gestão sem identidade | POST | 302 a `/gestao/identificar`, sem destino | igual |

**Campos do envio**: `identidade_sugerida` (prioridade sobre `subject`, como hoje), `subject`,
`papeis` (repetível), `proximo`, `csrfmiddlewaretoken`.

**Destino aceito**: caminho relativo, mesmo host, dentro de `/gestao/`, que não seja
`/gestao/identificar` nem `/gestao/sair`.

**Portal**: a vitrine e as páginas públicas trazem "Minhas inscrições" (ao acesso do candidato sem
sessão, às inscrições com sessão) e, só com `metodos_de_acesso`, "Área de gestão" para
`/gestao/`.
