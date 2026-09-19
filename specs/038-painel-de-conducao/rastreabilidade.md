# Rastreabilidade — 038 · Painel de condução do Processo vivo

**Frase que governa**: *"Não é fazer um dashboard: é não desligar o guia que já existe."* O sistema
já calculava estes estados; eles só não estavam reunidos. A feature **reúne e encaminha**.

**A `037` foi integrada antes da `US2b`** — e antes da `US1`, que mexe no mesmo arquivo. Conferido
por **ancestralidade**, e não pela ponta do log:

```
git merge-base --is-ancestor fcb448f origin/main   →  verdadeiro
git merge-base --is-ancestor fcb448f HEAD          →  verdadeiro
```

`git log -1` diria "sim" para uma `main` que não a tivesse trazido. A `037` alterou
`interface/views.py` (213 linhas), `acoes.py` e `detalhe.html`; a `US1` e a `US2b` só tocaram
`views.py` depois disso.

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-556** | `views.processo_detalhe` e `processo_detalhe.html`: a região *Onde cada Edital está*, com contagens, **série** e **próximos marcos** — *quanto chegou, o que vem, e o que pede ação* | `test_a_pagina_do_processo_apresenta_o_pulso_e_a_atencao`, `test_quem_alcanca_o_processo_le_o_estado_e_nao_recebe_caminho` |
| **FR-557** | as três leituras fundidas (`sinais_da_etapa`, `sinais_do_recurso`, `sinais_do_marco`); `divulgacao_do_ato` extraída de `views.py` | `test_o_processo_e_a_supervisao_dizem_a_mesma_coisa_do_mesmo_edital` — compara **as frases**, não a presença |
| **FR-558** | `alcance()` ganhou as quatro chaves; a **Atenção** pende de o ator alcançar ao menos uma espécie, e o Pulso não pende de nada além do Processo | `test_quem_alcanca_o_processo_le_o_estado_e_nao_recebe_caminho`, `test_quem_preside_recebe_a_atencao_na_mesma_regiao`, `test_sem_a_porta_da_divulgacao_o_sinal_nao_e_montado` |
| **FR-559** | `processo_detalhe.html`, mesma forma da Supervisão e mesmo parcial `_sinal.html` | `test_sem_nenhuma_condicao_o_processo_tambem_declara_a_ausencia_em_uma_linha` |
| **FR-560** | `avaliacao_parada` (`UX-063`) | `test_avaliacao_distribuida_e_nao_concluida_produz_o_sinal`, `test_concluidas_as_avaliacoes_o_sinal_some` |
| **FR-561** | `sinais_do_recurso` (`UX-005` + `UX-064`), **um ato só** | `test_recurso_com_julgador_disponivel_produz_o_sinal`, **`test_a_mesma_peca_nunca_dispara_os_dois_sinais`** |
| **FR-562** | `ato_sem_divulgacao` (`UX-066`), lendo `divulgacao_do_ato` | `test_ato_emitido_e_nao_divulgado_produz_o_sinal`, `test_divulgado_o_ato_o_sinal_some` |
| **FR-563** | `recorte_sem_ocupacao` (`UX-065`) | `test_ordem_emitida_sem_ocupacao_apurada_produz_o_sinal`, `test_sem_ato_de_ordenacao_o_recorte_nao_sinaliza` |
| **FR-564** | nenhuma mensagem nomeia pessoa | **três** varreduras, porque nenhum cenário dispara as quatro: `test_o_recurso_e_o_recorte_nao_nomeiam_pessoa`, `test_o_ato_sem_divulgacao_nao_nomeia_pessoa`, `test_a_avaliacao_parada_nao_nomeia_pessoa` |
| **FR-565** | `FR-024` da `022` tachada e marcada **SUBSTITUÍDA**, com as dez nomeadas por extenso | `test_o_requisito_que_fecha_o_catalogo_nomeia_as_especies_que_o_produto_apresenta` — **lê a spec**, não uma cópia |
| **FR-566** | conferível **lendo o diff**: nenhuma permissão nova (as quatro reusam `comissao:gerir`, `recurso:julgar`, `auditoria:consultar` e `resultado:publicar`); nenhuma ajuda instrucional nos cartões; nenhum conteúdo publicado reescrito; nada apagado | `git diff` — nenhuma linha removida de conteúdo normativo, nenhuma migration |
| **FR-567** | nenhum estado novo: `UX-063` sai de `resumo_da_etapa`, `UX-064` do cálculo do `UX-005`, `UX-065` de `ato_vigente` + `apuracao_vigente`, `UX-066` da derivação **extraída** | `makemigrations --check` → *No changes detected*; `make preparar` → **33 de 33** |

**Os dois casos-limite da spec que a primeira implementação não cumpria**, corrigidos depois da
revisão e prendidos por teste:

| Caso-limite | O que faltava | O que o prende |
|---|---|---|
| *"Ator que alcança o Processo e nenhum dos destinos. **Lê o estado** e não recebe caminho algum."* | a região inteira pendia de `pode_supervisionar`: quem alcançava o Processo e não a Supervisão não lia **estado nenhum** | `test_quem_alcanca_o_processo_le_o_estado_e_nao_recebe_caminho` |
| *"**Edital encerrado ou cancelado.** Não produz sinal de trabalho pendente — o que parou, parou por ato."* | "publicado" queria dizer apenas *tem conteúdo vigente*, e um Edital encerrado continua tendo: as quatro espécies seguiam montadas, **com destino** | `test_edital_parado_por_ato_nao_aponta_trabalho_pendente` (encerrado **e** cancelado) e `test_o_edital_parado_nao_silencia_as_especies_anteriores` |

A segunda correção é **assimétrica de propósito**: `alcance_no_edital` retira apenas as quatro
espécies de trabalho pendente. As seis anteriores continuam como estavam — o `UX-001` e o `UX-002`
falam do conteúdo publicado, que um Edital encerrado continua tendo; o `UX-004` fala de ordem que
envelheceu, e ela envelhece depois do encerramento como antes.

**A `FR-567` não precisou tirar nada do escopo.** As quatro se mostraram deriváveis com o que
existe, e a quarta não era menos derivável: era derivável **no lugar errado**.

## 2. Critérios de sucesso

| `SC-` | Como foi conferido |
|---|---|
| **SC-196** | percorrido **pela interface**, cenário 1: a página do Processo abre com o pulso e a Atenção na primeira tela. Sem shell e sem banco |
| **SC-197** | **zero divergências**: Processo e Supervisão lidos lado a lado no mesmo Processo semeado — mesmos 12/0/12, mesmas séries, mesmos próximos marcos, mesmas frases, mesma ordem. E não *podem* divergir: não há segundo cálculo. O teste compara **frase a frase**; a redação anterior conferia só o dígito `4`, e por isso passava com o Pulso pela metade |
| **SC-198** | **os quatro** disparam, e os quatro destinos foram **abertos**: distribuição da Etapa, recursos do Edital, ocupação do marco (*"Apurar a ocupação deste recorte"*) e publicação do ato (*"nada impede esta divulgação"*) |
| **SC-199** | **zero** mensagens nomeando pessoa (três varreduras + leitura no percurso); **zero** destinos a quem não os abre — `helena.semnada` alcança o Processo, **lê o Pulso** e não recebe sinal nem caminho; `paulo.presidente`, sem `resultado:publicar`, não recebe o `UX-066` |
| **SC-200** | o requisito nomeia **exatamente** as dez que o produto apresenta, conferido contando as duas listas — e o teste lê a spec do disco |

## 3. Testes alterados — **recontados caso a caso**

Os artefatos previam **34 casos em 4 arquivos**. São **37 em 5**: o `R-7` não lista
`tests/unit/interface/test_supervisao.py`, que guarda `assert len(ESPECIES) == 6` e que estas
espécies tornariam vermelho por construção.

| Arquivo | Antes | Agora | Novos | Motivo |
|---|---|---|---|---|
| `tests/integration/supervisao/test_sinais.py` | 13 | 32 | +19 | as quatro espécies, as **duas contraprovas obrigatórias**, a invariância por marco do `UX-066`, as três varreduras de nome de pessoa e os **três** casos do Edital parado por ato |
| `tests/interface/test_supervisao.py` | 15 | 20 | +5 | a `US1` pelo canal: apresenta, **diz o mesmo frase a frase**, lê o estado sem receber caminho, recebe a Atenção quando alcança, declara a ausência |
| `tests/acceptance/test_supervisao_do_processo.py` | 1 | 2 | +1 | a `SC-200`, lendo a `FR-024` emendada do disco |
| `tests/unit/interface/test_supervisao.py` | 3 | 3 | 0 (**1 emendado**) | o guardião do catálogo: seis → dez, com as dez nomeadas |
| `tests/integration/supervisao/test_fronteira.py` | 5 | 5 | 0 (**1 emendado**) | `processo_detalhe.html` entrou na varredura de termos proibidos: a Atenção passou a ser apresentada ali |
| **Total** | **37** | **62** | **+25** | |

Contados como o `pytest` os coleta: são **61 funções** e **62 casos**, porque o do Edital parado é
parametrizado sobre *encerrado* e *cancelado* — dois estados, um corpo. Conferido com
`pytest --collect-only` sobre os cinco arquivos.

**Os vizinhos permaneceram**: 15, 13, 5, 1 e 3 continuam lá. Dois foram **emendados** e nenhum
reescrito: o guardião do catálogo (seis → dez) e a varredura de termos proibidos dos templates,
que passou a ler `processo_detalhe.html`.

## 4. Orçamento de consulta — **remedido, espécie por espécie**

**A descoberta que muda a forma da `T021`**: os guardiões **não têm número escrito**. Os dois medem
em execução e cobram **invariância sob escala**. Não havia número a ajustar — e é por isso que a
razão precisou ser escrita ao lado do teste, e não cravada num `assert`.

| Guardião | O que escala | Antes | Depois |
|---|---|---|---|
| `test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas` | recursos pendentes (1 → 4) | 21 | **22** |
| `test_o_custo_da_pagina_cresce_com_o_que_mudou_e_nao_com_o_tamanho_do_processo` | inscrições (5 → 10) | 32 | **32** |

| Espécie | Custo | Razão |
|---|---|---|
| `UX-063` | **nenhum** | lê `completas` e `sem_conclusao` do mesmo `resumo_da_etapa` que o `UX-003` já busca |
| `UX-064` | **nenhum** | mesmo `recursos_do_edital` e mesmo `impedidos_por_recurso` do `UX-005`, partidos em dois desfechos |
| `UX-065` | **uma por recorte com ato** | `apuracao_vigente`, que a Supervisão não lia. O `ato_vigente` é o mesmo do `UX-004` |
| `UX-066` | **uma por marco** | a cadeia de publicações é do marco; o recorte é filtro sobre as linhas dela. Preguiçosa: marco sem ato não a paga |

**O `+1` do primeiro guardião é o `apuracao_vigente` do único recorte com ato daquele cenário.** O
`UX-066` não aparece ali porque a `presidenta` do teste não tem `resultado:publicar`, e sinal que o
ator não alcança não chega a ser calculado — o custo dele é medido onde ele existe, por
`test_a_divulgacao_e_lida_uma_vez_por_marco_e_nao_por_recorte`, que compara o **acréscimo da
espécie** e não o total da página, e que prende o `+1` ainda quando um segundo recorte ganha ato.

**Nenhuma das quatro escala com a fila**: nem por recurso, nem por inscrição, nem por participante.

## 5. O percurso, pela interface

Banco próprio (`ps_038_percurso`), `seed_demo` com três Editais, servidor em `:8041`. **Nada foi
atravessado por banco nem por relógio**; o único uso do `psql` foi ler o e-mail de uma candidata
para entrar no portal, que é diagnóstico e não atalho — o código de acesso veio do terminal do
servidor, que é de onde ele sai.

| Cenário | Resultado |
|---|---|
| **1 — o Processo conduz** | o pulso (contagens, série e próximos marcos) e a Atenção aparecem; Supervisão e Processo dizem **o mesmo**; `helena.semnada` **lê o estado** e não recebe sinal nem caminho; o Processo de 2027, sem Edital publicado, declara a ausência em **uma linha** |
| **2 — avaliação parada** | alocada a comissão e distribuídas as 7 inscrições **sem concluir**, a Etapa *Prova objetiva* **deixou de ser `UX-003` e virou `UX-063`**. As outras Etapas seguiram em cobertura — a fronteira é **por Etapa** |
| **3 — recurso** | recurso interposto pelo portal e admitido pela gestão → **`UX-064`**. Declarados os impedimentos dos **três** membros sobre a peça, o `UX-064` **sumiu** e o **`UX-005` apareceu**. Nunca os dois |
| **4 — recorte e ato** | o sorteio do Edital 63 tem ordem emitida e nada apurado (**`UX-065`**) e ato não divulgado (**`UX-066`**); os dois destinos abrem nas telas que resolvem |
| **4b — o Edital que parou por ato** | encerrado o Edital 63 pela interface, os três sinais de trabalho pendente dele (`UX-063`, `UX-065`, `UX-066`) **sumiram**, e o `UX-001`, o `UX-002` e o `UX-003` do mesmo Edital **ficaram** |
| **5 — o que não pode ter mudado** | nenhuma das quatro mensagens nomeia pessoa; o requisito e o produto contam **dez**; o orçamento foi remedido com a razão por espécie; as espécies antigas continuam disparando |

### O que o percurso **não** alcançou, e fica registrado

**`UX-004` e `UX-046` não dispararam no ambiente semeado** — não por defeito, mas porque as
condições deles não ocorrem ali: nenhum ato ficou obsoleto, e nenhum Perfil publica vaga imediata
sem linha do quadro. As duas espécies continuam cobertas pelos casos que já existiam
(`test_o_ato_obsoleto_aparece_sem_que_seja_preciso_abrir_o_marco` e os do `UX-046`), verdes na
suíte. Registro em vez de forçar o estado por banco, que é o protocolo da `034`.

**Um efeito colateral do percurso, declarado pelo próprio produto antes do ato**: impedir
`joana.avaliadora` inativou três atribuições com avaliação concluída, e por isso as contagens de
cobertura do Edital 88 mudaram entre uma leitura e outra. É consequência de domínio, mostrada na
confirmação, e não do diff.

## 6. Verificação

```
cd backend && make lint check test-pg
```

- `ruff check .` — **All checks passed!**
- `ruff format --check .` — **1132 files already formatted**
- `manage.py check` — **no issues**
- `makemigrations --check --dry-run` — **No changes detected** (esta feature **não tem migration**)
- `make preparar` — **33 de 33** tabelas append-only

| Suíte | Passando | Pulados |
|---|---|---|
| **antes** (`fcb448f`, árvore limpa) | **7454** | 11 |
| **depois** | **7479** | 11 |

**O briefing dizia 7406 para o "antes", e a medição deu 7454.** Os pulados batem; os passados não.
A árvore estava limpa em `fcb448f`, de modo que a diferença não é do diff — é do número de
referência, medido antes de alguma integração que chegou à `main` em 19/09. Está registrada em
[antes-do-painel.md](antes-do-painel.md), e o "antes" usado aqui é o **medido**.

**7454 + 25 = 7479**, e os 25 são exatamente os casos novos da tabela da seção 3 — nenhum caso
existente deixou de rodar, e nenhum caso novo foi pulado. Os 11 pulados são os mesmos de antes.

> **A contagem mudou depois da revisão**, e a conta de fechamento é a única prova de que ela mudou
> pela razão certa: a primeira entrega tinha 21 casos novos e fechava em 7475; as quatro correções
> acrescentaram quatro casos — os três do Edital parado por ato e o do ator que alcança o Processo
> sem alcançar sinal — e fecham em 7479.
