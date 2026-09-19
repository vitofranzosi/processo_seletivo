# Rastreabilidade — 035 · Sorteio executável

**Uma linha por `FR-`, uma por `SC-`, e uma por fixture ou teste alterado, com o motivo.**
Implementada em 18/09/2026 sobre a `main` `9b72d75`, na qual os artefatos da `035` já estavam
integrados pelo PR #136. A `034` está especificada e **não** implementada; as duas tocam
`editais/domain/validation.py` em funções diferentes, e não houve colisão.

Os três portões estão em [antes-do-sorteio-executavel.md](antes-do-sorteio-executavel.md) (`T002`),
[inventario-do-metodo.md](inventario-do-metodo.md) (`T003`, `T004`, `T011`) e
[varredura-da-amostra.md](varredura-da-amostra.md) (`T028`).

---

## Requisitos funcionais

### A forma, na composição

| | Onde está | Prova |
|---|---|---|
| **FR-507** algoritmo e fonte são **escolha**, reusando a função da Retificação | `interface/forms.py` `opcoes_do_metodo` (movida de `retificacao.py`), `templatetags/interface_extras.py` `escolhas_do_metodo`, e os dois templates de composição | `test_metodo_do_marco.py::test_o_algoritmo_e_a_fonte_do_marco_sao_escolhidos_e_nao_digitados`, `::test_o_algoritmo_e_a_fonte_do_metodo_comum_tambem_sao_escolhidos` |
| **FR-508** a ocorrência declara a forma e a razão dela | `_marco.html` e `compor_classificacao.html`, `<span class="oculto" id="ajuda-ocorrencia-…">` | `::test_a_ocorrencia_ensina_forma_exemplo_e_consequencia` |
| **FR-509** a formulação é a do campo do instante, e não uma segunda | a ajuda tem **forma, exemplo e consequência**, e as duas telas trazem o mesmo texto palavra por palavra | idem — as três partes são afirmadas uma a uma |
| **FR-510** a derivação em prosa **permanece** texto livre | nenhuma mudança de espécie; só o rótulo na Retificação (`T013`) | `::test_a_derivacao_em_prosa_continua_texto_livre_nas_duas_telas`, e a varredura de leitores no inventário, que continua devolvendo **zero** |
| **FR-511** valor fora do vocabulário continua legível e não é oferecido | `escolhas_do_metodo` acrescenta a opção `de_origem`, `selected` e `disabled` | `::test_valor_fora_do_vocabulario_continua_legivel_e_nao_e_oferecido` e a contraprova `::test_o_valor_de_hoje_nao_e_marcado_como_vindo_da_origem` |

### A sexta guarda

| | Onde está | Prova |
|---|---|---|
| **FR-512** a ocorrência é recusada quando não tem a forma, no mesmo lugar e momento das cinco | `editais/domain/perfis.py` `_validar_forma_da_ocorrencia`, chamada de `_validar_metodo_de_sorteio` — a função única por onde passam o método próprio **e** o comum | `test_forma_da_ocorrencia_na_composicao.py::test_a_ocorrencia_em_prosa_e_recusada_ao_gravar_o_rascunho`, `::test_o_metodo_comum_do_edital_recebe_a_mesma_recusa` |
| **FR-513** a recusa nomeia campo, forma e razão | a frase de `_validar_forma_da_ocorrencia`, na gramática das cinco vizinhas | `::test_a_recusa_nomeia_o_campo_a_forma_e_a_razao_da_forma` — e ela afirma também que *"não é executável"* **não** aparece |
| **FR-514** a guarda não torna irretificável nenhum Edital do acervo | `editais/domain/validation.py`: `_coerencia_do_metodo_de_sorteio` passa a receber `ato`, e liga a sexta guarda só em `ATO_DE_PUBLICACAO` — o mesmo recorte de `_metodo_do_sorteio_publicavel`, escrito pela `032` | `test_acervo_com_ocorrencia_em_prosa_continua_retificavel.py`, **5 casos**, incluindo a contraprova de que a publicação continua impedida |
| **FR-515** a conferência reutiliza a regra do motor | `sorteios/domain/substituicao.py` `derivavel`, que **aplica** a derivação e olha o desfecho | `test_forma_da_ocorrencia.py::test_a_consulta_e_a_derivacao_nunca_discordam` |

### A recusa, no dia

| | Onde está | Prova |
|---|---|---|
| **FR-516** a tela distingue as duas causas | `sorteios/application/previa.py` `_causa_da_recusa`, despachando pelo **código** da recusa e não pela frase; `RECUSA_POR_FORMA_DA_REFERENCIA` nomeia o código | `test_recusa_do_sorteio.py::test_a_leitura_nomeia_a_declaracao_como_causa` e `::test_sem_recusa_alguma_a_leitura_devolve_nada` |
| **FR-517** na causa da declaração, qual campo e o que ele precisa conter — e só então a Retificação | `sorteio.html`, ramo `causa == "declaracao"`, nesta ordem | `::test_a_referencia_nao_derivavel_nomeia_a_declaracao_e_nao_a_fonte` |
| **FR-518** na indisponibilidade real, a frase de hoje, inalterada | o `{% else %}` do mesmo bloco, **não tocado** | `::test_a_cadeia_esgotada_de_verdade_continua_dizendo_o_que_dizia`, que esgota a cadeia pelo caminho real — a fonte é consultada seis vezes e responde que não publicou |

### O que não muda

| | Como se confere |
|---|---|
| **FR-519** nenhum conteúdo publicado reescrito, nenhum vocabulário alargado | `T027`: o retrato de `T002` reexportado e comparado. E por leitura do diff: `chave.ALGORITMOS`, `fontes.FONTES`, `normalizacao.REGRAS` e `substituicao.REGRAS` estão **intocados** — `substituicao.py` ganha uma função e uma constante, e nenhuma entrada em `REGRAS` |
| **FR-520** nenhuma capacidade, papel ou regra de autorização nova, e nenhum sorteio já realizado muda | por leitura do diff: o diff não toca `autorizacao/`, `comissoes/` nem `identidade/`, e não introduz nenhuma `can(` nova. O resultado dos sorteios, por `T027` |
| **FR-521** a direção de dependência entre sorteio e classificação permanece | a guarda vive em `editais/domain` e **lê** `sorteios/domain`; `previa.py` importa de `editais/domain/perfis`, e **não** de `interface` — registrado no docstring de `_causa_da_recusa` |

---

## Critérios de sucesso

| | Resultado |
|---|---|
| **SC-176** os cenários 3 e 5 chegam ao fim, sem saber de antemão que a ocorrência termina em número | **cumprido** — cenário 3 do quickstart percorrido pela interface, do congelamento à verificação pública. Ver *Os percursos*, abaixo |
| **SC-177** zero Editais publicam método inexecutável, pela **mesma** conferência do motor | **cumprido** — `test_forma_da_ocorrencia.py` compara as duas respostas para 10 referências, e não as duas implementações |
| **SC-178** 100% das recusas nomeiam campo, forma e razão, e nenhuma descreve o sintoma | **cumprido** — há **uma** recusa nesta família, e o teste dela afirma as três partes e a ausência da frase-sintoma |
| **SC-179** nenhum valor publicado deixa de ser legível, e nenhum sorteio muda de resultado | **cumprido** — `T027`, comparação contra o retrato de `T002` |
| **SC-180** a varredura registra como cada Edital da amostra declara, ou não, a ocorrência | **cumprido** — [varredura-da-amostra.md](varredura-da-amostra.md): **dez** Editais de sorteio, `R-7` confirmado e estendido de quatro para dez |
| **SC-181** nenhuma migration, nenhum vocabulário alargado | **cumprido** — `make check` roda `makemigrations --check` e não detecta mudança |

---

## Fixtures e testes alterados, e por quê

| Arquivo | O que mudou | Por quê |
|---|---|---|
| `tests/unit/publicacoes/test_pdf_classificacao.py` | as **três** declarações de `occurrence` — linhas 417, 432 e 591 — de `concurso 6100 da Loteria Federal` para `Concurso 6100` e `Concurso 6101`; e as **duas** asserções que liam esses valores | **`T024`: conserta as fixtures, e nunca a regra.** Elas são a evidência do defeito, não um obstáculo: alguém do próprio projeto escreveu a referência como uma pessoa escreve, com o número no meio e a fonte repetida no fim. Afrouxar a derivação para achar o número em qualquer posição faria `concurso 6100 de 2026` derivar para **2027** |
| `tests/interface/test_metodo_do_marco.py` | o leitor `_valor` de `test_a_recusa_do_metodo_comum_nao_apaga_o_que_foi_digitado` passa a ler `<select>` **além de** `<input>` | a garantia que o teste prende é que a recusa **não apaga o que se acertou**, e ela não é sobre a forma do controle. Lendo só o `<input>`, ele passaria a não guardar nada sobre os dois campos que viraram escolha — em silêncio, e verde |
| `tests/interface/test_metodo_do_marco.py` | **seis casos novos**, acrescentados **ao fim** | a `US1`. O que está acima guarda a `021`, a `026` e a `030`; reescrever qualquer daqueles apagaria regressão que ninguém reporia — foi o que a `030` fez com `test_round_trip_do_rascunho.py` |
| `tests/interface/test_retificar_metodo_de_sorteio.py` | a asserção do rótulo, de `Ocorrência que fixa a semente` para `que fixará` | `T013`. Dois rótulos para o mesmo campo é o que o Princípio I proíbe, e o que fica é o de `CAMPOS_DO_METODO` — de onde o documento publicado tira os dele desde a `032` |
| `tests/unit/sorteios/test_forma_da_ocorrencia.py` | **novo**, 23 casos | `T006`. O `SC-177` dito como comparação de respostas |
| `tests/unit/editais/test_forma_da_ocorrencia_na_composicao.py` | **novo**, 10 casos | `T016` e `T017`. A guarda, a frase dela, e o que **não** dispara |
| `tests/integration/editais/test_acervo_com_ocorrencia_em_prosa_continua_retificavel.py` | **novo**, 5 casos | `T018`. A `FR-514`, com o acervo **construído** com o defeito: uma garantia sobre conteúdo que não existe não é garantia |
| `tests/interface/test_recusa_do_sorteio.py` | **novo**, 5 casos | `T022`. As duas causas, e a contraprova de que a frase da indisponibilidade real não mudou |

**Nenhum arquivo existente foi reescrito.** As três alterações em arquivos existentes são
acréscimo ao fim (os seis casos novos) ou correção pontual de linha (as fixtures e os dois
rótulos), e estão listadas acima uma a uma.

---

## Uma decisão de engenharia que o `T004` autorizou, e um achado que ele não autoriza

**O portão `T004` mediu zero.** Nenhum dos 17 bancos desta máquina tem Edital publicado com
ocorrência fora da forma, e por isso a guarda foi para junto das outras cinco, em
`editais/domain/perfis.py`, como a tarefa previa para este desfecho.

**O recorte por ato continua obrigatório, e o zero não o dispensa.** O alcance da guarda não é
função do censo de hoje: `_coerencia_do_metodo_de_sorteio` roda também no ato de Retificação, e
qualquer conteúdo publicado antes desta feature — aqui ou em produção — passaria por ela. O censo
diz que nada quebra hoje; a `FR-514` diz que nada pode prender amanhã.

**E um achado de passagem ficou registrado e não corrigido**, no inventário: as duas telas de
composição montam à mão os `<option>` da regra de normalização e da de substituição, com rótulos em
prosa, enquanto `opcoes_do_metodo` lê os mesmos dois vocabulários de quem os executa. São duas
origens para o mesmo vocabulário — o que a `FR-507` proíbe para o algoritmo e a fonte. A `FR-507`
nomeia **o algoritmo e a fonte**, e corrigir os outros dois obriga a decidir o que fazer com os
rótulos em prosa, que são melhores do que o identificador cru. É desenho de vocabulário de tela, e
é de quem governa o backlog.

---

## Os percursos, e o que eles produziram

Feitos pela **interface administrativa e pelo portal**, em 19/09/2026, num Edital composto do zero
para isto — o `76/2027`, nascido a partir do `51/2026` e levado à publicação pela tela.

### Cenário 1 — a composição ensina (`T023`)

O algoritmo e a fonte são `<select>` nas **duas** telas, com as opções vindas de quem as executa
(`IFES-SORTEIO-SHA256-v1`; `Fonte de demonstração`, `Loteria Federal`). A ocorrência traz a ajuda
com forma, exemplo e consequência. A derivação continua `<input type="text">`.

**E vale no fragmento que o htmx troca**: trocar a forma da ordem para *por sorteio* recompõe o
cartão do marco já com os `select`. É a razão de a escolha ser uma tag de template e não contexto
de view — são três pontos de renderização, e o quarto entraria sem as listas.

### Cenário 2 — a sexta guarda recusa, e diz o quê (`T023`)

Escrita a ocorrência como uma pessoa escreve — `concurso 6100 da Loteria Federal` — e gravado o
passo, a tela respondeu:

> *"Ocorrência que a regra de substituição declarada não sabe derivar: 'concurso 6100 da Loteria
> Federal'. Ela deve terminar no número da ocorrência — como `5900` ou `Concurso 5900` —, porque é
> do número final que a regra deriva a substituta quando a fonte não publica. A fonte já é declarada
> em campo próprio; repeti-la depois do número põe o número no meio, e ali a regra não o encontra."*

E logo abaixo: *"O que você digitou foi preservado abaixo."* Corrigida para `Concurso 6100`, gravou.

### Cenário 3 — o sorteio de ponta a ponta (`T025`, **`SC-176`**)

O percurso inteiro, pela interface: publicar o Edital → três inscrições pelo portal → **congelar a
relação** → **observar a ocorrência** → **realizar o sorteio** → **verificação pública**.

| Passo | Resultado |
|---|---|
| Relação congelada | 3 participantes, resumo `09b419d3dbe8b5c2…` |
| Ocorrência observada | `Fonte de demonstração — Concurso 6100`, material `12345 67890 11223 44556 77889` |
| Sorteio realizado | manifesto `f29c8f1a2b59c94c…` |
| Verificação pública | *"Sorteio verificado: 3 participantes; relação íntegra; semente íntegra; ordem reproduzida integralmente."* — os cinco itens conferem |

**O passo que decide**: a tela **ofereceu** *"Observar a ocorrência Concurso 6100 na fonte"*. É
exatamente onde o cenário 3 da reauditoria parava, lendo que a ocorrência e todas as substitutas
estavam indisponíveis.

E a publicação do Edital passou pela aferição **com a sexta guarda ligada** — a prova de que o
método composto pela tela atravessa o impedimento da `D-001`.

### Cenário 4 — a recusa do acervo (`T026`)

O Edital do acervo foi construído como ele nasce: uma **Retificação** trocou a ocorrência por
`concurso 6101 da Loteria Federal`. A Retificação **passou** — é a `FR-514` funcionando, e não há
achado impeditivo. Aberta a tela do sorteio:

> *"A ocorrência declarada no Edital — concurso 6101 da Loteria Federal — não pôde ser lida pela
> regra de substituição publicada. O campo **Ocorrência** — a ocorrência concreta que fixará a
> semente — precisa terminar no número da ocorrência… A fonte não foi consultada, e não há o que
> esperar dela. Corrigir a declaração exige Retificação…"*

A frase da indisponibilidade real **não** aparece. A contraprova dela — cadeia esgotada de verdade,
com a fonte consultada seis vezes — está em `test_recusa_do_sorteio.py`.

### Cenário 5 — o acervo não se mexeu (`T027`, `SC-179`)

O retrato de `T002` foi reexportado e comparado. **Todas as linhas do "antes" continuam presentes e
idênticas** — cada publicação, cada versão consolidada e, o que mais importa, o sorteio já
realizado: semente, resumo do método, resumo do manifesto e a ordem posição a posição. O sorteio
novo é acréscimo, e não alteração.

---

## Um defeito meu, encontrado no percurso e corrigido

A primeira escrita da `FR-511` marcava a opção herdada com `disabled`, para que ela ficasse legível
sem ser escolhível. **Medido no navegador, isso perdia o valor**:

```
<option selected disabled>  →  select.value === "HERDADO"
                               new FormData(form).get(campo) === null
```

O valor não é submetido. Seria exatamente a perda que a `FR-511` existe para impedir — e **nenhum
teste de Python a pegaria**, porque eles afirmam sobre o HTML renderizado e não sobre o que o
navegador envia. É a mesma armadilha que `test_round_trip_do_rascunho.py` já registrava por escrito
para o campo oculto.

O `disabled` saiu. O que impede a opção herdada de ser escolha **válida** é o rótulo, que diz que o
sistema não a executa, e `_validar_algoritmo_publicado`, que recusa ao gravar. E entrou um teste —
`test_a_opcao_herdada_nao_e_disabled_porque_disabled_nao_e_submetido` — para que ninguém a
reintroduza.

---

## A verificação

```bash
cd backend && make lint check test-pg
```

| | Antes (`T002`) | Depois |
|---|---|---|
| `ruff check` | limpo | **limpo** |
| `ruff format --check` | limpo | **limpo** |
| `make check` (inclui `makemigrations --check`) | — | **No changes detected** — `SC-181` |
| Suíte contra PostgreSQL | 7213 passando, 12 pulados | **7267 passando, 12 pulados, 0 falhas** |

**Reconferido depois do rebase sobre a `main` que já traz a `034`** (PR #138), em 19/09/2026:
**7343 passando, 11 pulados, 0 falhas**, com `ruff check`, `ruff format --check` e
`makemigrations --check` limpos. As duas features tocam `editais/domain/validation.py` em funções
diferentes, como a spec previu: o único conflito do rebase foi no `.claude/launch.json`, onde as
duas acrescentaram uma entrada — e as duas ficaram, porque apagar a do outro é o defeito que aquele
arquivo já registrou.

*A contagem de pulados caiu de 12 para 11 porque a `034` entrou junto; ela não é efeito desta
feature.*

Os 54 casos a mais são os quatro arquivos novos e os sete acrescentados ao fim de
`test_metodo_do_marco.py`. **Nenhum teste existente foi removido**, e os três arquivos existentes
alterados estão na tabela acima, um a um, com o motivo.

### As duas promessas que comando nenhum prova, conferidas por leitura do diff

- **Nenhuma capacidade nova, nenhum papel novo, nenhuma regra de autorização nova** (`FR-520`): o
  diff não toca `autorizacao/`, `comissoes/` nem `identidade/`, e não introduz nenhuma chamada
  `can(` nova.
- **Nenhum vocabulário alargado** (`FR-519`, `SC-181`): `chave.ALGORITMOS`, `fontes.FONTES`,
  `normalizacao.REGRAS` e `substituicao.REGRAS` estão intocados. `substituicao.py` ganha uma função
  consultável e uma constante com o nome de um código de recusa que já existia — e **nenhuma**
  entrada nova em `REGRAS`.
