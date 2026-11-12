# Research: Minhas atividades

As decisões de produto estão na [spec](spec.md) (D-001 a D-010). Aqui ficam as escolhas técnicas, de
R-001 a R-013, cada uma com a alternativa descartada. Os caminhos são relativos a
`backend/processo_seletivo/`.

## R-001 — Um módulo de leitura novo, `interface/atividades.py`, que não decide "sua"

**Decisão.** A leitura entre Editais mora num módulo próprio, ao lado de `trabalho.py` (104) e de
`andamento.py` (127). Ele tem duas partes:
- uma função que toca o banco (`ler(ator, agora)`): escolhe os Editais, chama `andamento.do_edital`
  e a carga;
- funções puras sobre `Providencia`: filtrar pela base, agrupar entre Editais, ordenar e montar as
  frases de cobertura. Elas têm teste unitário sem banco.

**Por quê.** A regra de "sua" já existe em `_Leitor.e_sua`, e é a que o Centro usa. O módulo só filtra
o que a derivação marcou como SUA, e por isso não pode divergir dela (D-005).

**Descartado.** Pôr a leitura em `trabalho.py`. A `104` promete custo constante na Lista (a FR-2806 da
`104`); misturar ali uma leitura linear no número de Editais presididos tornaria o contrato do módulo
ambíguo.

## R-002 — A escolha dos Editais, em três consultas

**Decisão.**
1. Os Processos presididos: `MembroComissao` com `identity_subject`, `ativo=True`,
   `funcao=PRESIDENTE` e `processo__institution_scope` do ator.
2. Os Editais desses Processos com `status` em `PUBLICADO` ou `ENCERRADO`, de Processo fora de
   `PROCESSO_FINAL`, com `select_related("processo")`.
3. As alocações ativas à conferência (`AlocacaoAConferencia`) da pessoa, com o Edital e o
   `perfil_id`, nos mesmos filtros de estado. `perfil_id` nulo é todos os Perfis.

Um Edital presidido não entra pela conferência: lá, a presidência já confere (edge case da spec).

**Por quê.** É a FR-6854 e a D-002: a presidência vem do vínculo, e não de `pode_gerir_comissao`, que
devolve `PERMISSAO_SISTEMICA` antes de olhar a presidência. A consulta 1 é a mesma que a página já faz
por `comissoes_da_pessoa`; o plano reaproveita aquele resultado em vez de repetir a leitura.

**Descartado.** Filtrar `comissoes_da_pessoa` depois e consultar Edital por Processo: seria uma
consulta por Processo.

## R-003 — O filtro da base, sobre o nível 1 de cada Edital

**Decisão.** Para cada Edital lido, a página toma `andamento.nivel_1.itens`, já agrupados dentro do
Edital (a decisão de agrupamento da `127`), e aplica:

| Edital lido por | Entra em "Para fazer agora" | Marca |
|---|---|---|
| presidência | `grupo == SUA`, `responsavel` em {`CONDUZ`, `CONFERE`}, natureza fora de {`FORMALIZACAO`, `RECURSO`, `AVALIAR`} | Presidência |
| alocação à conferência | `grupo == SUA`, `responsavel == CONFERE`, `perfil_id` alcançado pela alocação | Alocação |

| Edital lido por | Entra em "Em espera nos seus Editais" |
|---|---|
| presidência | `grupo == EM_ESPERA` (*Aguarda* e *Impedido*), natureza fora de `FORMALIZACAO` |
| alocação à conferência | nada (FR-6868) |

**Por quê.**
- `PUBLICA` e `JULGA` são papéis da unidade (D-004).
- `FORMALIZACAO` fica fora pela 7ª decisão do estudo, inclusive o que tem `responsavel=CONDUZ` (definir
  os documentos).
- `AVALIAR` sai da carga para todos (R-005), e não da derivação, para que a avaliação apareça uma vez
  só, pelo mesmo caminho para quem preside e para quem não.
- O Gestor alocado à conferência recebe da derivação toda conferência como SUA, porque
  `_pode_conferir` aceita `conduz`. O filtro por `perfil_id` restringe aos Perfis da alocação
  (FR-6857). O mesmo vale para o resto da condução: no Edital lido só pela conferência, nada que não
  seja `CONFERE` entra.

**Descartado.** Expor a base em `Alcance` (a análise G do estudo o sugeria). O `Alcance` continuaria
reduzindo a presidência a um booleano para o Centro, e a página já sabe a base pelo caminho por que
leu o Edital.

## R-004 — Um Edital que não pôde ser lido

**Decisão.** A página chama `do_edital` só em Edital `PUBLICADO` ou `ENCERRADO` (R-002). Nesses, um
`None` só pode vir de duas causas: a falta de versão vigente (`DomainError`) ou a exceção que
`do_edital` registra no log e engole. As duas são "não pôde ser lido agora" (FR-6874). A página guarda
o Edital numa lista própria, sem mudar `do_edital`.

**Descartado.** Fazer `do_edital` propagar a exceção para esta página. O Centro depende de ele não
derrubar a tela, e um parâmetro novo só para distinguir o que o filtro de estado já distingue seria
superfície a mais.

## R-005 — A avaliação pela carga, para todos

**Decisão.** A view já calcula `comissao_selectors.minhas_etapas(ator)` e
`avaliacao_selectors.carga_nas_etapas(...)`. Cada Etapa com `pendentes > 0` vira uma linha de
natureza `AVALIAR`, com:
- a frase "Avaliar N inscrições", feita pela mesma função do andamento (`_n`, exposta como
  `andamento.ato_de_avaliar(n)`);
- o link da Mesa (`interface:minha-etapa`);
- a marca "Alocação".

O lugar é a Etapa e o Edital.

**A divergência de número (D-010).** Em `situacoes_da_etapa`, o Centro limita a contagem por
`a_avaliar = min(sem_conclusao − carentes, abertas − carentes)`. Numa Etapa com inscrição sem avaliador
suficiente, isso dá menos do que a Mesa. Reproduzir o limite pediria `resumo_da_etapa` em cada Etapa
alocada, que é a derivação que a D-003 evita. A linha diz o número da Mesa. O teste de coerência
compara a Etapa e o link sempre, e o texto quando `carentes == 0`.

**Descartado.**
- Usar a célula `AVALIAR` da derivação nos Editais presididos e a carga nos outros: o mesmo ato teria
  duas fontes, conforme o caminho.
- Calcular o resumo por Etapa: medido no estudo, é o que custava ~1700 consultas ao avaliador.

## R-006 — O agrupamento entre Editais

**Decisão.** Uma função pura `agrupar_entre_editais(linhas)` junta linhas com a mesma chave:
- em "Para fazer": `(situacao, natureza, ato, base, lista_vazia)`, **só se o ato não tem dígito**;
- em "Em espera": `(situacao, natureza, ato, razao)`, pelo texto inteiro, data incluída, e só se o
  **ato** não tem dígito (FR-6870). A data está na razão, e por isso esperas com datas diferentes
  ficam em linhas diferentes.

O grupo guarda a lista ordenada dos `(Edital, providência)` que o compõem. Cada um mantém o seu link. O
grupo diz "N Editais".

**Por quê.** É a regra do `providencias.agrupar` dentro do Edital: só junta o ato sem número, porque
somar contagens exigiria flexionar o texto de novo (FR-6865).

**Descartado.** Juntar por natureza, independentemente do texto: "Convocar 3 titulares" e "Convocar 2"
viraria "Convocar titulares em 2 Editais", uma frase que a derivação não escreve.

## R-007 — A ordem

**Decisão.** A chave é `(situação: OBSOLETO=0, PENDENTE=1; Edital: (year, number, id); índice em que a
derivação emitiu o item)`. As linhas de avaliação entram como `PENDENTE` do Edital delas, depois das
providências do mesmo Edital. O grupo toma a posição do primeiro membro.

**Por quê.** `providencias.ordenar` põe à frente, entre as suas, as que têm `ate` e `desde` (a FR-4082
da `127`). Dentro de um Edital isso é coerente com o cartão. Entre Editais, misturaria o fim das
inscrições com o prazo do candidato (D-007). A página relê `nivel_1.brutas` na ordem de emissão, e não
`itens`, para a ordem; usa `itens` para o agrupamento dentro do Edital.

**A ser verificado na implementação.** `Nivel1` agrupa e ordena junto. Para não reimplementar o
agrupamento, a página chama `providencias.agrupar(brutas)`, que preserva a ordem de emissão, e não
`ordenar`. O teste unitário prende isso.

## R-008 — A fase de cada linha

**Decisão.** `centro.fase_da_providencia(item, centro.etapas_governadas(andamento.perfis))`, com o nome
de `conceitos.NOMES`. A avaliação é `conceitos.AVALIACAO`.

**Por quê.** É a taxonomia que a terceira entrega vai usar para "frente" (o §5 da rodada 4). Uma
segunda classificação divergiria.

## R-009 — A versão vigente uma vez por requisição (segundo incremento)

**Decisão.** Ficam em `publicacoes/application/selectors.py`:
- um contexto `versao_vigente_da_requisicao()`, com `contextvars`;
- dentro dele, `effective_version(edital_id=…, at=…)` memoriza o resultado por `edital_id`, **só
  quando `at` é `None` ou o instante com que o contexto foi aberto**.

Uma chamada com outro `at`, que é a leitura de um ato histórico pela norma que ele citou, passa direto
ao banco. As views de leitura, "Minhas atividades" e o Centro, abrem o contexto em volta da montagem.
Nenhum comando o abre.

**Por quê.**
- É a D-009: dentro da requisição não há estado que precise de invalidação.
- O cuidado com `at` evita trocar a versão histórica pela vigente. A memória do projeto registra que
  o ato histórico não lê a versão vigente.
- O estudo mediu −19% para a presidência, com os mesmos itens.

**Descartado.**
- Memorizar dentro de `_Leitor`: as funções de outras features chamam `effective_version` direto, e
  não passam pelo leitor.
- Cache entre requisições: precisaria de invalidação a cada ato publicado.

**Risco.** Uma GET que publicasse no meio leria a versão antiga. Nenhuma view de leitura publica, e o
teste prende que o contexto só é aberto em GET.

## R-010 — A nota da faixa da Lista

**Decisão.** `trabalho.FORA_DA_FAIXA` continua a única fonte das famílias fora (a FR-4325 da `129`), e
passa a dizer onde está cada coisa:
- o que é da presidência ou de alocação (classificação, sorteio, convocação, documentos) está em
  "Minhas atividades";
- o resultado, a formalização, o Requerimento, os avisos e o encerramento seguem "no detalhe de cada
  Edital".

O link é do template: `_acoes_disponiveis.html` desenha a constante e, depois dela, o link para
`interface:minhas-etapas`. Assim a constante continua texto puro, e as duas frases a contêm por
inteiro.

**Por quê.** A FR-6881 pede o link sem prometer na página o que ela não mostra. O resultado é do
Publicador (D-004), e não pode ser mandado para lá.

**Testes que mudam junto:** `test_organizacao_da_lista.py`, nas famílias e no "detalhe de cada
Edital"; e `test_trabalho_do_ator.py`, se fixar a frase.

## R-011 — O nome visível

**Decisão.**
- `navegacao.py`: o rótulo da `Secao`.
- `minhas_etapas.html`: o título, o `h1` e a trilha.
- `minha_etapa.html` e `mesa_inscricao.html`: as trilhas.
- `lista.html`: "Ver minhas atribuições" passa a "Ver minhas atividades".
- Os comentários que nomeiam a página ficam: são registro.

A rota `interface:minhas-etapas`, o nome da view e o template mantêm o nome antigo (FR-6852).

**Testes que fixam o texto** (11 arquivos, levantados em 12/11): `test_politica_de_conteudo`,
`test_paineis_e_telas_de_apoio`, `test_decisoes_da_etapa_4`, `test_andamento_do_edital`,
`test_caminho_ate_a_mesa`, `test_lista`, `test_shell_da_gestao`, `test_telas_de_uso_diario`,
`test_auditoria_passagem_da_retificacao`, `test_carga_nas_etapas` e `test_acesso_a_etapa`. Cada um é
conferido: muda a asserção sobre o **nome visível**, e não a sobre a rota.

## R-012 — O teto por Edital presidido

**Decisão.** `tests/performance/test_minhas_atividades_em_escala.py` usa os cenários de
`tests/fixtures/andamento.py` (`certame_s1`, `certame_p1`), como `test_andamento_em_escala.py`. É **um
cenário por teste**: a idempotência da publicação faz dois cenários colidirem. Em cada teste:
- a página da presidência do cenário (1 Edital presidido) menos a página de uma identidade do mesmo
  escopo sem vínculo nenhum (0 Edital presidido) deve ficar `≤ TETO_POR_EDITAL`;
- a mesma diferença deve ser igual com 3 e com 30 inscrições, como lá.

No membro:
- a página dele com 1 e com 11 comissões tem o mesmo número de consultas (SC-2272). As comissões
  extras são Processos sem Edital publicado, que não colidem;
- um espião em `andamento.do_edital` conta zero chamadas.

O número do teto é **medido na tarefa** e gravado com folga de ~20%, como os tetos de
`test_andamento_em_escala.py`. O estudo mediu, nos cenários de treinamento, cerca de 98 consultas por
Edital sem R-009 e 79 com ela, em Editais de formato variado (38 a 189). A medição com o cenário
fixo da fixture é a que vale.

**Por quê.** É a 8ª decisão do estudo: uma requisição, teto por Edital. O custo é linear por
construção, porque a página chama `do_edital` uma vez por Edital lido. O teste prende o termo
linear, e não a soma de dezenas de Editais.

**Descartado.** Montar 3 Editais presididos num teste só: colidem pela idempotência da publicação.

## R-013 — O que esta feature não toca

- `andamento.py` não muda de regra. Ele ganha só uma função pública para a frase da avaliação
  (R-005).
- `trabalho.do_ator` não muda de custo.
- Nenhum modelo, migration, permissão ou tabela append-only. O `M` do `provisionar` continua o mesmo.
- O pouso do login institucional continua na Lista (6ª decisão do estudo).
