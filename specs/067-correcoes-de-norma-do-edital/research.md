# Pesquisa — 067, correções de norma do Edital em PDF

As decisões do responsável pelo produto são `D-001` a `D-003`, na spec. As desta pesquisa são de
desenho, nascem em `D-004` e são do plano: nenhuma muda o que a spec afirma, e cada uma diz o que foi
descartado.

O mapa de onde cada coisa mora foi levantado sobre `99d32e16` e está resumido no fim (*Mapa*).

---

## D-004 — "Sob sorteio" é a forma **declarada**, nas três superfícies

**Decisão.** A dispensa de arredondamento (validação), a omissão do arredondamento e do empate no
corte (documento) e a omissão dos dois na Revisão dependem de `orderProduction == "POR_SORTEIO"` —
a forma **declarada** do marco —, por uma função única em `editais/domain/marcos.py`
(`declara_sorteio(marco)`).

**Por quê.** Hoje três lugares respondem "este marco sorteia?" de jeitos diferentes: o compositor lê
só o campo declarado (`pdf.py`, `sorteia = forma == POR_SORTEIO`); a Revisão resolve também o método
comum do Edital (`marco_ordena_por_sorteio`); a validação olha o método próprio
(`ordena_por_sorteio(…, metodo_declarado=…)`). As três concordam quando a forma está declarada, e
divergem no marco anterior à `030`, que não a declara. A spec escolheu esse marco como **acervo**: ele
continua exigindo e imprimindo arredondamento, como sempre saiu (casos-limite, *Sorteio*). Ler a
forma inferida mudaria a saída de um marco antigo que carrega método — e documento publicado não muda
de conteúdo, que é a razão que o comentário do compositor já registra.

**Descartado.** Usar `marco_ordena_por_sorteio` nas três: alcançaria o acervo sem forma declarada e
deixaria a validação dependente do método comum, que é campo de outra etapa.

**Consequência.** Na Revisão, o bloco do sorteio e a combinação continuam governados pela forma
resolvida (como hoje); só o arredondamento e o empate passam a seguir a declarada, que é a do
documento — a Revisão mostra o que o documento imprime.

## D-005 — A frase de recurso continua em `pdf._janela_recursal`, e o prazo vira função própria

**Decisão.** `_janela_recursal(marco)` passa a compor a frase de `FR-1300` a `FR-1302`. O trecho do
prazo — `2 (dois) dias corridos` — sai para `prazo_do_recurso(marco)`, pública, que a frase e o aviso
de conferência leem. O nome é `marco.name`, depois `marco.code`; sem os dois, a frase de hoje.

**Por quê.** A Revisão já importa `_janela_recursal` do compositor (`revisao.py`): mudar a função
muda as quatro superfícies de uma vez (`FR-1304`). E o aviso precisa dizer o prazo com a mesma
grafia do documento — uma segunda redação de "2 (dois) dias corridos" na validação seria a segunda
fonte que o Princípio II proíbe.

**As aspas.** “ e ” (U+201C, U+201D) estão no cp1252 (0x93, 0x94), e por isso no WinAnsi das fontes
do documento; a `grafia` não as normaliza. O nome entra como está: se ele trouxer aspas, saem as
dele dentro das da frase (caso-limite).

**Descartado.** Mover a frase para `vocabulario_da_regra` — seria melhor casa para o ED-05, que vai
reescrever as frases; aqui, mudaria o módulo de mais funções do que a feature precisa.

## D-006 — O aviso de conferência é uma conferência a mais em `validate_for_publication`

**Decisão.** `_conferencia_do_recurso(snapshot)` em `editais/domain/validation.py`, registrada ao lado
das demais, devolve no máximo **um** `ValidationFinding(Severity.WARNING, "appeal_schedule_review",
mensagem, "schedule")`.

- **Código único nos dois atos.** O aviso nunca é impeditivo em ato nenhum, então o código não
  coincide com impeditivo de publicação, e `advertencias_do_ato` da Retificação não o descarta — a
  armadilha que obrigou a `065` a dar código próprio ao aviso da Retificação não se aplica.
- **Caminho `schedule`.** A tradução de destino da interface já leva o segmento `schedule` à etapa
  Cronograma (`DESTINO_DA_PENDENCIA`); o caminho exato `/schedule` é o do período de inscrições e vai
  para a Inscrição — por isso `schedule`, sem a barra (`UX-191`).
- **Evento de recurso** por `\brecurs\w*`, sem distinguir maiúsculas, sobre `type` e `description`
  (`FR-1305`).
- **O período** com a grafia do documento: `pdf._instante` (que já converte para o fuso
  institucional e usa `humano.instante`). A importação do compositor pela validação é **adiada**
  (dentro da função), como a `065` fez com `itens_do_documento` (a decisão 004 da `065`).
- **Agrupamento**: por (nome do marco, frase do prazo), com os códigos dos Perfis na ordem do
  conteúdo; acima de seis Perfis, o aviso diz "N Perfis" em vez de enumerá-los — o B tem 18, e a
  enumeração ocuparia a mensagem inteira.

**Por quê.** É o lugar de toda conferência que a Revisão, a submissão, a homologação, a publicação e
a Retificação mostram, e ele já não roda sobre Edital publicado fora de uma Retificação (`FR-1328`).
Nenhuma consulta nova: é função do snapshot que as cinco portas já montam.

**Descartado.** Calcular o aviso na Revisão apenas: a confirmação da submissão e a da Retificação não
o veriam, e a spec pede o aviso nos atos (`FR-1309`).

## D-007 — "Perfil sem vaga imediata" é um predicado só, no domínio do quadro

**Decisão.** `sem_vaga_imediata(perfil)` em `editais/domain/quadro.py`: `immediateVacancies` inteiro
igual a 0 **e** quadro declarado com todas as linhas em 0 (`FR-1320`). O compositor
(`_quadro_de_vagas_do_perfil`, que já chama a reversão), a contagem de tabelas
(`tabelas_do_documento`) e a Revisão leem o mesmo predicado.

**Por quê.** A contagem de tabelas da `065` precisa seguir o documento — o guardião
`test_itens_do_documento.py` compõe e compara, e reprovaria se só o compositor mudasse. Um predicado
só é o que impede o documento e a contagem de discordarem sobre o mesmo Perfil.

**Quadro ausente** continua sem quadro (acervo da `025`); **total 0 com linha positiva** é incoerente,
a validação recusa, e o predicado responde "tem vaga", para que o erro apareça no documento da prévia.

**Descartado.** Ler só `immediateVacancies == 0`: o Perfil incoerente perderia o quadro, que é o que
mostraria a incoerência.

## D-008 — A tela do marco não mostra nem grava arredondamento sob sorteio declarado

**Decisão.** Em `_marco.html`, os campos "Casas decimais" e "Arredondamento" só aparecem quando o
marco **não declara** sorteio; sob sorteio, viajam ocultos com os valores do padrão de marco novo
(`ARREDONDAMENTO_PADRAO`) quando o marco não tem arredondamento, ou com os dele quando tem. Em
`forms.py`, o marco que declara sorteio é gravado com `rounding: {}`. A ajuda passa a dizer que o
arredondamento é da ordem por pontuação (`UX-193`).

**Por quê.** Os valores ocultos são o que faz a troca de forma, que recompõe o cartão por `htmx` a
partir do que o formulário enviou, devolver os campos preenchidos ao voltar para pontuação
(`FR-1316`) — sem eles, o cartão recomposto viria com os campos em branco e o marco por pontuação
seria recusado por uma omissão que a pessoa não fez. E gravar `{}` sob sorteio é o que tira do
conteúdo publicado a regra inerte: o documento já não a imprimiria, mas o conteúdo continuaria
afirmando uma conta que não existe.

**Diferente do empate, de propósito.** O desfecho de empate sob sorteio viaja oculto **e é
preservado** (`FR-928`), para não apagar o que um Edital anterior declarou. Aqui o mesmo argumento
não vale: o arredondamento sob sorteio nunca teve efeito, e preservá-lo é preservar o defeito que a
ED-03 aponta.

**A Retificação** não muda de tela: o arredondamento continua retificável onde está declarado. Só a
dica de vazio — "Não declarado — a publicação será impedida" — passa a ser condicionada à forma
(`FR-1317`).

## D-009 — A recusa da emissão de marco por sorteio passa a vir antes do cálculo

**Decisão.** Em `classificacao/application/emissao.py`, a conferência "este marco sorteia" passa a
rodar **antes** de `calcular_ordem`, sobre o conteúdo da versão vigente no instante do comando, com a
mesma recusa (`ordering_milestone_is_drawn`).

**Por quê.** Hoje `calcular_ordem` roda primeiro, e um marco por sorteio que enumera Etapas, com
pontuação de todos e sem arredondamento, chegaria a `combinar → arredondar` e levantaria
`RegraIncompleta` sem tratamento — erro interno no lugar da recusa (`FR-1318`). Hoje o caso é
inalcançável porque a validação exige o arredondamento; esta feature o torna alcançável.

**Descartado.** Fazer `calcular_ordem` recusar marcos por sorteio: ela é lida também pelas telas, e
mudar o contrato dela alcança caminhos que já se protegem antes (`selectors.py`,
`conducao_do_marco.py`).

## D-010 — Os bytes: o que muda de propósito e o que prova que só isso mudou

**Decisão.**

- **A fixture de contrato** (`tests/contract/fixtures/documento_publicado_v1.pdf`) **não muda**: o
  snapshot dela não tem marco com forma declarada, regra de recurso, empate nem Perfil sem vaga
  imediata. Ela continua byte a byte — é a prova de `SC-505`.
- **Os PDFs da auditoria** (`doc/auditoria-edital-pdf-2026-10-08/pdf/`) **não são sobrescritos**:
  são evidência de uma auditoria datada. O guardião de bytes da `065`
  (`test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes`) passa a comparar com os
  documentos esperados **depois desta feature**, gravados em
  `specs/067-correcoes-de-norma-do-edital/demonstracao/` (`A-publicado-067.pdf`,
  `B-publicado-067.pdf`), e ganha um irmão que compara o **texto** de cada um com o PDF da auditoria
  e exige que a diferença seja exatamente a lista pretendida (`SC-502`).
- O texto vem do mesmo extrator dos testes de contrato (`texto_de`, que decodifica o fluxo de
  conteúdo), comparando linhas sem cabeçalho e rodapé de página — a paginação pode mudar.

**Por quê.** Atualizar uma fixture de bytes é apagar a evidência que ela guardava, a menos que outra
coisa diga o que mudou. O teste de diferença de texto é essa outra coisa, e fica na suíte.

**Descartado.** Regravar os PDFs da auditoria no lugar: a auditoria deixaria de mostrar o que
auditou.

## D-011 — O consolidado de Retificação segue a composição nova; o quadro de alterações não muda

**Decisão.** Nenhum código novo: o consolidado é composto pela mesma função, no ato. A remoção do
arredondamento sob sorteio pela tela de composição **não** alcança a Retificação (a Retificação
edita por caminho); o consolidado de um Edital antigo com arredondamento sob sorteio simplesmente
deixa de imprimi-lo.

**Por quê.** É o `FR-1196` da `064`, que o usuário aprovou para as atribuições, aplicado a esta
feature; a spec o registra em *Assumptions*.

---

## D-012 — Na Revisão, o resultado é "deste marco", e o nome fica na linha da denominação

**Decisão.** `_janela_recursal(marco, *, objeto=None)`: o documento não passa `objeto`, e a frase
nomeia o marco entre aspas; a Revisão passa `objeto="deste marco"`.

**Por quê.** Achado na implementação de US1: a Revisão agrupa os marcos de mesma regra de Perfis
diferentes — 16 Perfis com o mesmo corte são um item, não dezesseis —, e agrupa pelos pares
`(rótulo, valor)` do marco, **sem** a denominação, que nasce do Perfil (030, a derivada "Classificação
final — nome do Perfil"). Com o nome dentro da frase de recurso, cada Perfil virou um grupo, e dois
testes do agrupamento da Revisão caíram. A denominação já é a linha de cima de cada grupo; a frase
diz "deste marco", e o objeto continua dito.

**Descartado.** Agrupar ignorando a linha de recurso (esconderia divergência real de prazo); e
substituir o nome depois do agrupamento por uma marca (mais código para dizer a mesma coisa que a
linha da denominação já diz).

---

## Mapa (levantado em 09/10/2026, `99d32e16`)

| Peça | Onde | O que muda |
|---|---|---|
| Frase do recurso | `publicacoes/infrastructure/pdf.py::_janela_recursal` | nomeia o resultado (D-005) |
| Arredondamento e empate no documento | `pdf.py::_marcos` | omitidos sob sorteio declarado (D-004) |
| Quadro e reversão | `pdf.py::_quadro_de_vagas_do_perfil`, `_reversao_declarada` | omitidos sem vaga imediata (D-007) |
| Contagem de tabelas | `pdf.py::tabelas_do_documento` | segue o predicado (D-007) |
| Revisão do marco | `interface/revisao.py::_leitura_do_marco` | arredondamento e empate pela forma declarada |
| Revisão do Perfil | `interface/revisao.py` (linha da reversão) | nota "não sai no documento" (`UX-192`) |
| Exigência do arredondamento | `editais/domain/validation.py::_arredondamento_do_marco` (chamada em `_coerencia_dos_marcos`) | dispensada sob sorteio declarado; forma ainda conferida |
| Aviso de recurso | `validation.py` (novo `_conferencia_do_recurso`) | D-006 |
| Tela do marco | `interface/templates/interface/_marco.html`, `interface/forms.py`, ajuda `_como_preencher_o_marco.html` | D-008 |
| Dica da Retificação | `interface/retificacao.py` (vazio de `rounding/mode`) | condicionada à forma |
| Emissão | `classificacao/application/emissao.py` | D-009 |
| Predicados | `editais/domain/marcos.py` (`declara_sorteio`), `editais/domain/quadro.py` (`sem_vaga_imediata`) | novos |

Consumidores conferidos e **não** alterados: `sorteios/` (a ordem sorteada não lê arredondamento),
`divulgacao/domain/conteudo.py::_escala` (cai na escala padrão sem arredondamento),
`publicacoes/domain/alteracoes.py` (os rótulos do arredondamento continuam para a Retificação),
`editais/domain/mutabilidade.py` (o arredondamento continua retificável), a validação do desfecho de
empate (`FR-928`, já dispensa sob sorteio).
