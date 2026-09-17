# Pesquisa — Requerimento de Matrícula (`029`)

**Fase 0** · 16/09/2026 · medido contra o repositório em `5f37eec`.

> Cada achado abaixo foi **medido**, e não suposto. Onde a medição desmentiu a expectativa, a
> correção está escrita no próprio achado — é o formato que a `028` usou, e pela mesma razão: uma
> estimativa errada que ninguém confere vira decisão de arquitetura.

---

## T-001 — A declaração do Edital entra na raiz do conteúdo publicado, e três lugares a cobram

**Decisão**: a declaração é um objeto na raiz do snapshot — `matriculationRequest`, com `moment` e
`declarationText` —, emitido por `publicacoes/application/publish_edital.py::edital_snapshot`.

**Razão**: é do Edital, e não do Perfil (`FR-369`), e a raiz é onde o snapshot já guarda o que
limita o certame inteiro — `maxInscricoesPorCandidato` está lá com a razão escrita: *"da raiz porque
limita o **total** da pessoa no certame"*.

**O que isso obriga, e foi medido**: três artefatos falham por omissão se o campo entrar sozinho.

| Onde | O que cobra |
|---|---|
| `editais/domain/mutabilidade.py::CONTRATO` | classificação campo a campo; o guardião *"compara o que o snapshot publica com o que este dicionário classifica, falhando por **omissão** nos dois sentidos"* |
| `tests/contract/test_forma_publicada.py` | catorze testes sobre a forma publicada, entre eles `test_todo_campo_do_conteudo_publicado_e_obrigatorio` |
| `interface/retificacao.py::CAMPOS_REGRA` | o caminho `/matriculationRequest/declarationText` precisa ser oferecível, ou o texto nasce irretificável |
| `shared/canonical.py::SCHEMA_VERSION` **e** `publicacoes/domain/elevacao.py` | mudar a **forma** publicada exige subir a versão de esquema (hoje **15**) e acrescentar o degrau que eleva o acervo |

> **Este quarto mecanismo faltou nas três primeiras passadas desta pesquisa**, e o achado é do tipo
> que só aparece meses depois, numa consulta histórica: sem subir a `SCHEMA_VERSION`, conteúdo antigo
> e novo conviveriam sob o mesmo número, e `VERSOES_ELEVAVEIS` passaria a mentir sobre o que sabe
> elevar. **O degrau acrescenta a chave com `null`**: é a forma que o emissor pratica em
> `vacancyReversion` e `callForm` — chave sempre presente, `null` quando o Edital não declarou.
> *(A primeira redação deste achado dizia o contrário — "sem a chave" —, copiada de uma recomendação
> de revisão que não foi conferida contra `publish_edital.py:233`. Corrigido em 16/09/2026.)*

**A chave do contrato é `(coleção, caminho relativo)`**, e o caminho aninhado já tem precedente
literal: `("profiles", "vacancyReversion/kind")`. Logo `(RAIZ, "matriculationRequest/moment")` e
`(RAIZ, "matriculationRequest/declarationText")` são a grafia da casa, e não uma invenção.

**Não é coleção.** `publicacoes/domain/colecoes.py` declara coleções com chave estável; um objeto de
dois campos na raiz não entra ali, e não precisa — o endereçamento por caminho já o alcança.

**Alternativas consideradas**: campo no Perfil (recusado pela `FR-369` — repartiria configuração sem
caso); coleção própria (recusado — um objeto de dois campos não é coleção); dois campos soltos na
raiz em vez de um objeto (recusado pela razão que a `016` registrou ao modelar `vacancyReversion`:
*"para que um campo novo da mesma decisão entre sem um segundo degrau canônico"*).

---

## T-002 — O precedente que esta feature **não** pode repetir

**Medição**: `max_inscricoes_por_candidato` é campo publicado e **não tem caminho de escrita na
interface**. A varredura encontra três ocorrências no código de produção: a coluna no modelo, a
emissão no snapshot, e `seed_demo.py:789` gravando por `Edital.objects.filter(pk=…).update(…)`.
Nenhuma tela, nenhum comando de aplicação, nenhum endpoint.

**Consequência para esta feature**: a Constituição, em VI, diz que *"uma capacidade que o domínio
sustenta mas que nenhuma interface alcança NÃO DEVE ser considerada entregue"*. Um campo novo no
conteúdo publicado sem tela seria repetir, com conhecimento de causa, o que já está lá por descuido.
**A `FR-407` é, por isso, obrigação de plano e não de escopo opcional**: a declaração nasce com
comando, tela e teste de interface, ou não nasce.

*(Este achado é governança, e não escopo desta feature: o `maxInscricoesPorCandidato` sem tela
continua como está. Fica registrado para virar registro próprio.)*

---

## T-003 — A tela existe, e nenhuma etapa nova é criada

**Medição**: `interface/views.py::ETAPAS_COMPOSICAO` tem **nove** etapas, e a sexta é
`("inscricao", "Inscrição", "interface/compor_inscricao.html")` — a que já reúne o período de
inscrições e os **Documentos Exigidos**, com a razão escrita: *"a aplicabilidade de cada documento
referencia Perfil e modalidade que precisam existir"*.

**Decisão**: a declaração do requerimento entra nessa etapa. É onde quem elabora decide o que se
pede ao candidato, e é onde o Anexo em papel é declarado — ou deixa de ser (`R-3` da spec pede
exatamente essa frase de ajuda, e ela cabe aqui).

**Nenhuma etapa nova, nenhum template novo** — campos num template existente.

**E o comando não passa por `replace_draft`.** Medido: a assinatura de
`editais/application/draft.py::replace_draft` recebe `profiles, schedule, stages, sections,
document_requirements` — **nenhum campo de raiz**. O molde certo é
`editais/application/identificacao.py::update_edital_identification`: permissão, `command_context()`,
`select_for_update`, `ensure_processo_accepts_changes`, estado `EM_ELABORACAO`, `expected_revision`.

**Por que isso importa mais do que parece**: `replace_draft` *"substitui o rascunho inteiro: o que
não for reenviado é apagado"*, e é um caminho que já produziu perda de dado neste repositório. A
declaração fica **fora** dele, por construção.

---

## T-004 — A conferência de publicação já tem o mecanismo, e a feature só acrescenta um caso

**Medição**: `editais/domain/validation.py::validate_for_publication(snapshot, *, ato, agora)` já
recebe o ato, e achados condicionados a ele já existem — `_eventos_vencidos` abre com
`if ato != ATO_DE_PUBLICACAO: return []`.

**Decisão**: *momento declarado sem texto de declaração* entra como **erro impeditivo**
(`FR-407`, `SC-136`), no mesmo mecanismo. Zero estrutura nova.

**Razão de ser impeditivo e não advertência**: aceite sem texto é aceite de nada, e o resumo
criptográfico da `FR-393` seria resumo de string vazia. Publicação é ato imutável — o Edital
nasceria com um requerimento inaceitável e a correção seria Retificação.

---

## T-005 — A imutabilidade condicional tem precedente literal, e ele resolve a `FR-396`

**Medição**: `publicacoes/migrations/0007_imutabilidade_do_historico.py` implementa exatamente o
padrão que a `FR-396` pede, e escreve a razão:

> *"`Retificacao` e `AlteracaoNormativa` **mudam legitimamente enquanto o ato está em curso** (…).
> O que precisa ser imutável é o que já produziu efeito, então a trigger é condicional ao estado
> final."*

E a forma:

```sql
CREATE TRIGGER retificacao_final_imutavel
BEFORE UPDATE OR DELETE ON publicacoes_retificacao
FOR EACH ROW WHEN (OLD.status IN ('PUBLICADA', 'CANCELADA'))
EXECUTE FUNCTION reject_final_retification_mutation();
```

**Decisão**: a mesma forma, com `WHEN (OLD.status = 'ENVIADO')`, sobre `UPDATE OR DELETE`.

**A tabela NÃO entra em `TABELAS_APPEND_ONLY`**, e o total permanece **31**. A razão está escrita na
própria política de privilégios: `Inscricao` e `Retificacao` ficam de fora *"de propósito — mudam
legitimamente enquanto o ato está em curso, e a imutabilidade delas é condicional ao estado final, o
que só a trigger consegue expressar"*. Quem contar as tabelas depois desta feature deve continuar
lendo `31 de 31`.

**Uma armadilha da migration-fonte, e por que não nos alcança**: ela adverte que *"numa trigger
BEFORE, o valor devolvido é a linha que segue adiante: devolver OLD num UPDATE descartaria a
alteração em silêncio"*. Nossa função apenas levanta exceção, e nunca retorna — o risco não existe
aqui, e o registro fica para quem editar a migration depois.

---

## T-006 — *Chamada em aberto* já é um predicado do sistema, e reescrevê-lo seria repetir um beco

**Medição**: `convocacao/application/selectors.py` expõe `vigentes(convocacoes)` — *"as que ninguém
sucedeu"* — e `desfecho_de(convocacao)` — o desfecho vigente ou `None`. A composição dos dois é
exatamente *chamada em aberto*, e `convocacao/application/convocar.py::_em_aberto_da_pessoa` já a
faz, com a lição registrada:

> *"**Chamada em aberto, e não 'chamada vigente'** (…) A primeira versão bloqueava por convocação
> vigente, sem olhar o desfecho, e produzia um beco."*

**Decisão**: o gatilho da `FR-373` e a autorização da `FR-408` consomem um seletor **único**, em
`convocacao/application/selectors.py`, construído sobre os dois que já existem. Não se escreve um
segundo predicado no módulo do requerimento: duas leituras de "em aberto" divergiriam, e a `019` já
pagou esse preço uma vez.

**Custo de consulta medido**: `portal/views.py::convocacao` já carrega as convocações da inscrição
com `prefetch_related("desfechos", "comunicacoes")`. A tela do requerimento precisa de
`desfechos` apenas — uma consulta com um prefetch.

---

## T-007 — Titularidade, recusa indistinguível e conferência já existem

**Medição**: `portal/views.py::_inscricao_do_titular(request, inscricao_id)` devolve
`(registro, identidade, versao)` e já produz a recusa indistinguível de inexistente que a `FR-399`
pede — a `009` a escreveu como *"a **mesma** recusa que a titularidade produz, e não um 404 do
framework"*. `_conferencia` já é a tela *"o que o sistema recebeu, sem redigitar e sem reenviar"*,
que é o molde da `FR-406`.

**Decisão**: reuso direto dos três. Zero mecanismo novo de autorização, e **nenhuma permissão nova**
(`§13` da spec).

---

## T-008 — A base de CEP existe, é MIT, e traz o código IBGE — as coordenadas é que não se sustentam

**Medição externa**, feita em 16/09/2026 sobre os dois repositórios que a spec nomeia:

| Base | O que traz | Licença |
|---|---|---|
| [`SeuAliado/OpenCEP`](https://github.com/SeuAliado/OpenCEP) | **1.192.347** CEPs, de Correios e IBGE | aberta |
| [`gpfconfea/banco-ceps`](https://github.com/gpfconfea/banco-ceps) | os campos `cep, logradouro, complemento, bairro, localidade, uf, **ibge**, latitude, longitude`, em arquivos JSON | **MIT** |

**Decisão**: carregar a base local por comando de manutenção, numa tabela de referência própria com
`cep, logradouro, bairro, municipio, uf, codigo_ibge` — e **sem latitude e longitude**.

**Razão, e ela deixou de ser preferência para virar evidência**: o próprio `banco-ceps` adverte que
*"a confiabilidade e a disponibilidade das coordenadas obtidas por raspagem podem ser variáveis e
inconsistentes"*, porque elas são montadas em três camadas — Nominatim, AwesomeAPI e raspagem. A
`D-008` da spec recusou persistir coordenada por não ter consumidor; a pesquisa acrescenta a segunda
razão, mais forte: **a fonte não afirma a qualidade do que entrega.** O campo `ibge`, ao contrário,
vem do IBGE por meio do OpenCEP, e é exatamente o que a `FR-388` precisa.

**Alternativa recusada**: consulta a serviço de terceiro em tempo real. Transmitiria continuamente o
CEP de candidatos identificados para fora da instituição (Princípio III), e poria um certame em
curso na dependência de disponibilidade alheia.

**Não medido, e é tarefa do `$speckit-tasks`**: o tamanho do dump e o tempo de carga. A porta do
domínio (`FR-389`) torna a escolha substituível, então a medição não bloqueia o desenho.

---

## T-009 — Orçamento de consulta declarado

| Tela | Consultas acrescentadas |
|---|---|
| `portal:inscricao` e `portal:acompanhamento` | **+2** — o requerimento vigente da Inscrição, e a chamada em aberto |
| `portal:inscricoes` (a lista) | **0** — a lista não exibe o estado do requerimento, e exibi-lo seria leitura por listagem |
| dossiê da inscrição, na gestão | **+1** — o requerimento vigente, junto do que a tela já carrega |

**A recusa é deliberada e é regra da casa**: estado por linha de listagem é a leitura que este
repositório já reprovou. Quem quiser saber o estado abre a inscrição.

---

## T-010 — O que muda fora da feature, medido depois de uma correção

**A primeira redação deste achado dizia que a varredura por `requerimento|matrícula` no backend "só
encontra o vocabulário proibido da `016`". Errado, e a medição corrigiu.**

`requerimento` aparece **41 vezes**, e a maioria esmagadora num lugar só: as fixtures de
`tests/interface/test_compor_anexos.py`, onde o Anexo de exemplo se chama literalmente
`ANEXO I — REQUERIMENTO`. Isso não é ruído — **é a evidência de que o Anexo é o que esta feature
substitui**, escrita no próprio repositório por quem montou a fixture a partir dos Editais reais.

**Nada quebra por omissão**: nenhum teste afirma ausência de requerimento, e o campo novo do
snapshot é aditivo. O que a feature acrescenta fora dela é:

- **a declaração num Edital do `seed_demo`**, e ele precisa ser um que chegue à **convocação**, ou o
  cenário da `US2` não terá como ser demonstrado. O comando monta os Editais por caminhos distintos
  (`_edital_reaproveitado`, `_edital_encerrado`, `_edital_de_sorteio`), e a escolha é do
  `$speckit-tasks`;
- **o campo novo nos três guardiões do T-001**, que falham por omissão até serem atualizados — o que
  é o comportamento desejado deles.

---

## T-013 — A varredura de vocabulário da `UX-058` tem molde, e ele não alcança as telas novas por acidente

**Medição**: existem três varreduras — `test_vocabulario_da_ocupacao.py`,
`test_vocabulario_do_corte.py` e `test_vocabulario_da_convocacao.py` — e todas enumeram **os arquivos
que leem**, numa lista literal (`DA_016 = [TEMPLATES / "ocupacao.html", …]`).

**Duas consequências, e as duas importam**:

1. **Os templates desta feature não quebram as varreduras existentes**, porque não estão nas listas
   delas. Não há custo escondido.
2. **A `UX-058` precisa da sua própria**, no mesmo molde, com a sua lista. E com a mesma cirurgia que
   as três já praticam: a varredura lê o texto **sem comentário e sem docstring**, porque *"explicar
   por que uma palavra está proibida exige escrevê-la"*. Quem esquecer isso escreve um teste que
   falha pelo próprio comentário que o explica.

**Os termos proibidos desta feature** são os da `UX-058` — *deferido*, *indeferido*, *homologado*,
*matrícula efetivada* —, e cada um viaja com a frase que diz o que ele afirmaria indevidamente, que
é o formato que as três existentes usam para que a falha ensine a fronteira.

---

## T-014 — As varreduras por `glob` do repositório, todas as 19

**Por que este achado existe.** Seis auditorias desta feature encontraram, uma por rodada, a mesma
classe de defeito: uma convenção que o repositório impõe **por varredura** e que as tarefas não
mencionavam — a `SCHEMA_VERSION`, a fixture do Edital máximo, os alvos do `Makefile`,
`config/settings/base.py`, o `reverse_sql`, a proibição de armazenamento no navegador. As tarefas
foram escritas a partir dos módulos que a feature **toca**; o repositório também cobra os módulos que
**observam** toda feature.

**Por que ele não tem coluna de alcance.** A primeira redação desta tabela trazia uma coluna
*"alcança esta feature"*, com oito das dezenove marcadas — e ela estava errada em duas, justamente
nas que dependiam de eu lembrar que a feature **também edita** templates de `interface/`, e não só
cria os do portal. A enumeração por script acertou as 19; o julgamento de alcance, feito à mão,
errou. A coluna saiu: ela tinha validade de uma feature e aparência de fato permanente. **O alcance
se decide arquivo a arquivo, quando a tarefa cria ou edita o arquivo** — e as restrições que
importam estão dobradas nas tarefas, onde quem implementa as lê.

**Levantamento de 16/09/2026**, por `grep -rl 'rglob\|\.glob('` sobre `backend/tests/`.

| Varredura | Padrão | O que ela cobra |
|---|---|---|
| `test_acessibilidade.py` | `*.html` | canal **administrativo**: contraste, marcação nativa, link de salto — parametrizado sobre **todo** template de `interface/`, e sobre as **duas folhas de estilo**, dos dois canais |
| `test_acessibilidade_do_portal.py` | `*.html` | a mesma rubrica no canal do candidato: controle nativo, **rótulo ligado por `id`**, nenhuma largura em pixel, estado que não dependa só de cor |
| `test_armazenamento_no_navegador.py` | `*.html`, `*.js` | nada do candidato em `localStorage`, `sessionStorage`, `indexedDB` ou `document.cookie` |
| `test_estaticos.py` | `*.html` | estático encontrável pelo *finder*; e, por etapa nomeada — incluindo **`revisao`** —, nenhuma sintaxe de template chegando ao navegador |
| `test_trilha_legivel.py` | `application/*.py` | todo `operation="…"` de `record_event` tem nome legível em `interface/views.py::OPERACOES` |
| `test_migrations.py` | `[0-9]*.py` | folha única por app; **toda operação reversível**; migration **não importa** `processo_seletivo.*`; aplica do zero e recria os gatilhos |
| `test_situacoes_de_mensagem.py` | `*.py` | o número de chamadas de `send_mail` está preso à `FR-084` da `010`; acrescentar uma exige revisar aquela norma antes |
| `test_vigencia_do_resultado.py` | `*.py` | toda leitura de efeito consome `ResultadoEtapa.vigentes`, ou declara a exceção em `EXCECOES` |
| `test_leitura_do_documento_submetido.py` | `*.py` | o sistema **não lê** o conteúdo do que o candidato enviou |
| `test_citacoes_de_requisito.py` | `*.py`, `*.html`, `*.js`, `*.md` | toda citação `FR-`/`SC-`/`UX-`/`D-` aponta para identificador que existe |
| `test_dependencia_da_convocacao.py` | `*.py`, `0*.py` | `ocupacao`, `classificacao` e `resultados` não importam `convocacao` — nem no código, nem nas migrations |
| `test_dependencia_da_ocupacao.py` | `*.py` | a `016` não importa o que ordena |
| `test_ancora_removida.py` | `*.py` | a âncora saiu inteira, e não parcialmente |
| `test_invariantes_da_declaracao_unica.py` | `*.html`, `*.py`, `00*_*.py` | os oito invariantes da `027` |
| `test_invariantes_do_quadro.py` | `*.py` | os oito invariantes da `025` |
| `test_sem_gerador_pseudoaleatorio.py` | `*.py` | a ordem do sorteio não depende de gerador pseudoaleatório |
| `test_superficies_da_semente.py` | `*sorteio*.html`, `relacao*.html` | nenhuma superfície aceita semente, em nenhum verbo |
| `test_vetores_de_sorteio.py` | `*.json` | os vetores normativos do sorteio |
| `test_arquivo_e_transacao.py` | `*.pdf` | disco e banco não são a mesma transação, e a ordem entre eles é regra |

**Duas leituras que não se deve tirar desta tabela.** A primeira: que varredura ausente é licença —
`convocacao` importa `inscricoes`, e nenhum teste proíbe `inscricoes` de alcançar `convocacao`, mas
fechar esse ciclo continua sendo o defeito que as duas varreduras de dependência existem para
impedir. A segunda: que a lista basta — ela cobre o que é verificado **por `glob`**, e não o que é
verificado por fixture, como a `conteudo_maximo` do guardião de mutabilidade.

---

## T-011 — A renda vira lista fechada no domínio, e nada mais

**Decisão**: as sete faixas da `FR-412` entram como `TextChoices` no domínio do requerimento, com os
rótulos exatos do formulário institucional. Sem tabela, sem configuração por Edital, sem conversão.

**Razão**: a clarificação de 16/09/2026 fixou tanto as faixas quanto o que elas medem. A divergência
com a coluna de destino é **de significado, não de forma** — e por isso mora no contrato de saída e
no rótulo do campo (`R-7`), onde alguém a lê, e não numa tabela de conversão que a esconderia.

---

## T-012 — Nada a fazer sobre documentos

**Medição**: `DocumentoExigido` já é do Edital, com aplicabilidade opcional por Perfil e modalidade,
e a etapa `inscricao` já o compõe. A `FR-395` decidiu que retirar o Anexo assinado é **ato de quem
elabora**.

**Consequência**: zero código. O que a feature acrescenta é a frase de ajuda na etapa que já existe,
dizendo a quem elabora que o Anexo passou a ser dispensável quando há requerimento estruturado — que
é a mitigação que o `R-3` pede, e ela é texto, não mecanismo.

---

## T-015 — A base de CEP, medida (17/09/2026)

**A `T-008` decidiu pela base local sem saber o que ela custava.** A medição foi feita depois, e o
que ela encontrou muda o comando, não a decisão.

| | |
|---|---|
| Forma | **um arquivo JSON por CEP** — não um dump único |
| Arquivos | **1.209.314** |
| Tamanho | 379 MB comprimidos · 278 MB descomprimidos |
| Carga | **31 s**, lendo o `.zip` em fluxo |
| Linhas gravadas | 1.209.314 |

**O achado que importa é a forma.** `carregar_ceps` recebia uma pasta e fazia `rglob("*.json")`.
Contra a base real isso significa descompactar 1,2 milhão de arquivos — mais inodes do que a carga
inteira custa — e materializar uma lista de um milhão de caminhos antes de ler o primeiro registro.
O comando passou a aceitar o `.zip` e a percorrê-lo em fluxo: **uma abertura em vez de um milhão**.

**31 segundos é barato o bastante para não haver desculpa.** O caminho degradado da `FR-390`
continua correto e testado — base ausente não impede envio —, mas ele deixa de ser o estado normal
de uma instalação: carregar é um comando, e leva menos tempo do que rodar a suíte.

**O campo que justifica tudo continua sendo o `ibge`.** Conferido na carga real:
`29040860 → Rua Barão de Mauá, Jucutuquara, Vitória/ES, IBGE 3205309`. Latitude e longitude vêm no
registro e são descartadas na leitura (`D-008`).
