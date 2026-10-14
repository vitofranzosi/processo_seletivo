# Contrato das telas públicas — 072

O que as telas passam a garantir, na forma que os testes cobram. Rotas e parâmetros **não mudam**: os
cinco parâmetros da consulta, `?destino=` e a âncora `#vaga-<perfil>` continuam os mesmos.

## Vitrine — `GET /selecoes/`

| Elemento | Garantia |
|---|---|
| `<title>` | começa por "Processos seletivos" |
| `h1` | "Processos seletivos", com a unidade quando o catálogo tem uma só (FR-1611) |
| linha de contagem | quantas seleções com inscrições abertas, ou que não há nenhuma (FR-1612) |
| consulta | `role="search"`, `method="get"`; campo `busca` e botão fora do `<details class="mais-filtros">`; unidade, situação, Perfil e ordem dentro; `open` no `<details>` quando um dos quatro está aplicado (FR-1600 a FR-1603) |
| cartão — link | o texto do único link é o título do Edital, ou o do Processo sem ele (FR-1604) |
| cartão — ordem fixa | marca · título · oferta por Perfil · lugares · período · acompanhamento · convite · dados de apoio (FR-1614) |
| cartão — oferta | até 3 Perfis, cada um nome + quantidade, e "e mais N" (FR-1607, FR-1608) |
| cartão — acompanhamento | as frases da D-004, ou nada (FR-1629 a FR-1633) |
| cartão — convite | "Ver vagas e inscrever-se" (aberta), "Ver resultados e prazo de recurso", "Ver resultados", ou "Ver a seleção" (FR-1634) |
| cartão — dados de apoio | Processo, código, "Edital NN/AAAA" (omitido se já está no título) e a sigla da unidade (FR-1605, FR-1606) |
| sem resultado de consulta | uma frase, com caminho para as abertas (se houver) e para o catálogo (FR-1613) |

## Seleção — `GET /selecoes/<edital>/`

| Elemento | Garantia |
|---|---|
| volta | "← Voltar aos resultados" só com consulta; senão "← Todas as seleções" (FR-1618) |
| resumo da oferta | no cabeçalho, antes do botão do PDF; até 5 Perfis com quantidade, cada um com link para `#vaga-<perfil>`; ação para `#vagas-titulo` (FR-1615, FR-1616) |
| Requerimento | frase antes do primeiro Perfil quando `matriculationRequest.moment` é na inscrição (FR-1626) |
| vaga indicada | `.perfil:target` com borda e etiqueta textual (FR-1617) |
| mensagem de volta | dentro do Perfil da volta, `role="status"`, uma vez; resposta privada quando presente (FR-1622, FR-1625) |
| convite | o mesmo `POST` de hoje para abrir rascunho (FR-1624) |

## Acesso — `acesso`, `acesso/codigo`, `acesso/reconciliar`, `meus-dados`

| Elemento | Garantia |
|---|---|
| contexto | com destino de vaga: Perfil, "Edital NN/AAAA" e título; sem destino de vaga: nada (FR-1619) |
| `h1` do acesso | com destino de vaga, diz que se confirma o e-mail para se inscrever; sem, "Entrar" (FR-1619; Q7) |
| equivalência | o corpo da resposta não varia com a existência de identidade para o e-mail (FR-1620) |
| código | ajuda sobre spam junto do reenvio (FR-1621) |
| "Seus dados" | finalidade de nome e CPF (FR-1627 — texto pendente de validação) |
