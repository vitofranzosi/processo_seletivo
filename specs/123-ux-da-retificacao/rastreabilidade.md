# Rastreabilidade: o MVP de UX da Retificação (123)

Cada requisito → as tarefas que o implementam → os testes que o verificam. **Escrita antes da
implementação:** os nomes de teste são os arquivos planejados em `plan.md`, e os casos serão
conferidos contra eles ao fim (T038). Caminhos relativos a `backend/tests/`. Abreviações:

- `cc` = `unit/publicacoes/test_conferencia_do_conteudo.py`
- `cp` = `unit/interface/test_cartao_do_caminho.py`
- `mb` = `interface/test_retificar_busca_marca_base.py`
- `ci` = `interface/test_retificar_conferencia_impeditivos.py`
- `js` = `javascript/retificacao.test.js`
- `nv` = `navegador/test_jornada_da_retificacao_123.py`
- `vf` = `specs/123-ux-da-retificacao/verificacao.md`

A faixa aberta no cabeçalho da spec começa em FR-3917 e SC-1173, que são requisitos e têm linha
abaixo.

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3917 (texto de busca por campo; caixa, acento, todas as palavras) | T034 | `js` (normalização, várias palavras); `mb` (SC-1174); `nv` cenários A–C |
| FR-3918 (valor só do campo curto e nominal) | T034 | `js` (elegibilidade); `mb` (zero texto longo pelo valor) |
| FR-3919 (a partir de 2 caracteres) | T034 | `js` (1 caractere não filtra) |
| FR-3920 (lista por campo, até 25, contagem) | T034, T035 | `js` (teto e frase); `nv` cenário E |
| FR-3921 (cartão visível se algum campo corresponde; seções) | T034 | `js`; `nv` cenários A–C |
| FR-3922 («Ir ao campo»: desesconde, rola, foca; teclado) | T022, T034 | `js` (`irAoCampo`); `nv` teclado |
| FR-3923 (Enter não envia; foca o 1º resultado) | T034 | `js`; `nv` teclado |
| FR-3924 (busca não altera, não envia; escondido continua enviado) | T034 | `js` (sem `name`; valor intacto); `nv` cenário A (o término digitado sobrevive) |
| FR-3925 (sem termos equivalentes) | T034 | `js` («recursal» não acha «Prazo em dias») |
| FR-3926 (lista respeita «Só o que eu alterei») | T034 | `js` |
| FR-3927 (dois estados, cada um com palavra) | T020, T022, T023 | `mb`; `js`; `nv` cenário D |
| FR-3928 (proposta = o que «Criar»/«Gravar» gravaria; sem segundo cálculo) | T012, T019 | `mb` (criação, edição, gesto) |
| FR-3929 (cartão na proposta; linha nova; remoção da edição à parte) | T019, T020 | `mb`; `cp` (`ADD` por identidade, `REMOVE` sem cartão) |
| FR-3930 (as duas frases da barra) | T021, T022 | `js` (tabela de contracts §1.5); `nv` cenário D e edição |
| FR-3931 («Só o que eu alterei» nos dois estados) | T022 | `js`; `nv` cenário D |
| FR-3932 («Ir ao campo»/«Ir ao cartão» no resumo) | T018, T021, T022 | `mb`; `nv` cenário D |
| FR-3933 (só referências opacas no HTML) | T018, T021 | `mb` (sem caminho normativo) |
| FR-3934 (conferência recusada não marca) | T019, T022 | `mb` (`data-proposta="recusada"`); `js` |
| FR-3935 (a frase da base: incorpora e situação) | T027, T028 | `mb` (três situações) |
| FR-3936 (a base não muda) | T026 | `mb` (`input[name=base]`); suítes da `103` (T008) |
| FR-3937 (Retificar: «Como funciona», colunas, somente leitura) | T029 | `mb`; `interface/test_acoes.py` (T025) |
| FR-3938 (detalhe e confirmações) | T030 | `mb` (cinco telas); `nv` cenário G |
| FR-3939 (sem o "antes" de hoje, sem reapontar) | T029, T030 | `mb` (nenhuma coluna ou botão novo nas cinco telas) |
| FR-3940 (mesmas funções, ordem e parâmetros) | T004, T013 | `cc` (espião de argumentos) |
| FR-3941 (mesma frase; só a guarda quando ela para) | T004, T013, T014 | `cc`; `ci` |
| FR-3942 (link ao cartão, à coleção, à seção ou nenhum) | T006, T013, T014 | `cp`; `ci`; `nv` cenário B |
| FR-3943 (a conferência não grava) | T004, T013 | `cc`; `ci` (contagem de Retificações) |
| FR-3944 (a criação confere de novo; botão continua; criação recusada mostra a seção) | T004, T013, T014 | `ci` (relógio e Resultado no intervalo; recusa de «Criar» com a seção, R-013) |
| FR-3945 (advertência fora da conferência) | T013 | `ci` (formulário com só advertência não abre a seção) |
| FR-3946 (preservação) | T008, T038 | as suítes existentes (lista em `plan.md`); `nv` regressão ponta a ponta; `vf` |
| FR-3947 (CSP e classes com regra) | T015, T023, T031, T035, T039 | guardiões de estáticos e acessibilidade; `nv` (`violacoes == []`) |
| FR-3948 (375 px; nomes acessíveis) | T021, T023, T035 | `nv` cenário E a 375; `mb` (`aria-label`) |
| FR-3949 (jornada de navegador, com teclado) | T036 | `nv` |
| FR-3950 (medição da segunda etapa) | T041 | `doc/medicao-retificacao-123-<data>/` |

## Critérios de sucesso

| Critério | Tarefas | Verificação |
|---|---|---|
| SC-1173 (≤ 2 ações até o campo, demo e ampliado) | T034, T036 | `nv` cenários A–C e E (contagem de ações) |
| SC-1174 (os quatro termos; zero texto longo; ≤ 25 no ampliado) | T033, T034 | `mb`; `nv` cenário E |
| SC-1175 (3 de 3 marcados; filtro; 1 ação por linha) | T019–T022 | `nv` cenário D |
| SC-1176 (duas frases; nada de "Nada alterado…") | T022 | `js`; `nv` cenário D |
| SC-1177 (edição abre marcada) | T019, T020 | `mb`; `nv` edição |
| SC-1178 (nenhum "Vigente hoje"; data da vigência) | T026–T030 | `mb`; `nv` cenário G |
| SC-1179 (impeditivo na conferência, mesma frase, zero criadas) | T004, T013, T014 | `cc`; `ci`; `nv` cenário B |
| SC-1180 (a criação recusa o que surge no intervalo) | T004 | `ci` |
| SC-1181 (regressão; CSP; 375 px) | T038, T039 | `vf`; `nv` |
| SC-1182 (medição registrada e apresentada) | T041 | `doc/medicao-retificacao-123-<data>/` |

## Casos-limite

| Caso | Tarefas | Teste |
|---|---|---|
| Termo com 1 caractere | T034 | `js` |
| Várias palavras no mesmo campo | T034 | `js` |
| Termo que só casa com o nome do cartão: um resultado de cartão | T034 | `js`; `mb` (SC-1174) |
| Acento e caixa | T034 | `js` |
| Mais resultados que o teto | T034 | `js`; `nv` cenário E |
| Cartão escondido por «Só o que eu alterei» fora da lista | T034 | `js` |
| Linha acrescentada: visível, fora da lista | T034 | `js` |
| Resultado em cartão escondido: desesconde e foca | T022, T034 | `js`; `nv` |
| Campo de arquivo: foco no seletor, arquivo mantido | T022 | `js` |
| Justificativa e vigência fora da busca e das contagens | T022, T034 | `js` (caso de hoje mantido) |
| Conferência recusada sem marca | T019, T022 | `mb`; `js` |
| Campo que volta à base: dois selos até reconferir | T022 | `js` |
| Remoção marcada na criação entra na proposta | T019 | `mb` |
| Gesto: destinos na proposta | T019 | `mb` |
| Troca de arquivo conta um cartão | T019 | `mb` |
| Impeditivo sem cartão: sem link ou link à seção (se na página); campo da raiz à Identificação | T006, T013 | `cp`; `ci` |
| Impeditivo numa linha acrescentada nesta tela | T006, T013, T018 | `cp` (mapa `novas`); `ci` |
| Linha do quadro, Modalidade ou critério acrescentado marca só a linha nova | T006, T019 | `cp`; `mb` |
| Recusa de guarda antes dos achados | T004, T013 | `cc`; `ci` |
| Base com vigência exatamente agora: vigora | T027 | `mb` |
| Base que é a Publicação original | T027, T028 | `mb` |
| Somente leitura com a frase e o título novo | T029 | `mb`; `interface/test_acoes.py` |
| 375 px sem rolagem lateral | T023, T035 | `nv` cenário E a 375 |
