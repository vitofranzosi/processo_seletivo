# Insumos para o plano — 065, conflitos de numeração

**Não é normativo.** Reúne o que a investigação de 08/10/2026 encontrou no código e o que a spec pediu
como entrega à parte: componentes afetados, complexidade e plano de validação. O plano decide.
Requisitos estão em [spec.md](spec.md).

---

## 1. Componentes afetados

| Componente | Arquivo | O que muda | Observação |
|---|---|---|---|
| Validação da publicação | `backend/processo_seletivo/editais/domain/validation.py` | novas regras registradas em `validate_for_publication`, com códigos próprios (conflito de numeração, título transcrito, remissão ambígua, remissão sem destino, remissão suspeita) | o molde existe: `_anexo_citado_sem_rotulo` (remissão, aviso, RC-21) e `_caractere_sem_grafia` (trecho de texto livre, impeditivo). Reaproveitar `_secoes_textuais`, `_textos_impressos` e `_caminho_da_entidade`. O parâmetro `ato` já distingue publicação e Retificação (decisão pendente 2) |
| Regra de numeração | `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` — `numeracao`, `_materializaveis`, `_paragrafos`, `grupos_de_atribuicoes`, `_Numerador` | expor, **a partir do compositor**, os "itens do documento" de `FR-1205`: números das seções, das subseções geradas (Perfis, subseções comuns da `064`, Etapas) e quantas tabelas o documento terá | **o risco principal da feature.** A contagem de tabelas depende da composição (a tabela de Perfis só existe com mais de um Perfil; quadro e modalidades por Perfil; Cronograma). Reimplementar a contagem na validação criaria a segunda regra que a `054` (`FR-985`) existe para não ter. Avaliar também a direção da dependência: a validação é domínio e hoje importa `publicacoes.domain.grafia`; `numeracao` mora na infraestrutura e já é lida pela interface |
| Parágrafos e grafia | `pdf._paragrafos`, `publicacoes/domain/grafia.normalizar` | nenhuma | a contagem de parágrafos e a normalização (que remove o espaço de largura zero colado do Word) são as do documento, por `FR-1198` |
| Destino da pendência | `backend/processo_seletivo/interface/views.py` — `CODIGOS_DO_TEXTO_DA_SECAO`, `DESTINO_DO_TEXTO_DA_SECAO`, `_destino` | incluir os códigos novos de seção; **novo**: destino por seção (`#titulo-<chave>`, que a legenda já tem em `compor_conteudo.html`) em vez do topo da etapa (`#conteudo-titulo`) | remissões em outros campos (documentos, Perfis, Eventos) já caem nas etapas deles pelo caminho da entidade |
| Agrupamento na Revisão | `backend/processo_seletivo/interface/templatetags/interface_extras.py` — `RESUMO_DAS_REPETIDAS` | decidir se remissões repetidas se dobram como as de anexo | só aviso se dobra; impeditivo nunca (comentário do próprio arquivo) |
| Retificação | `publicacoes/application/retificacoes.py`, `interface/retificacao.py` | os mesmos achados, todos como aviso (`D-002`) | `validate_for_publication(..., ato=ATO_DE_RETIFICACAO)` já é o caminho; a tela da Retificação já usa `pdf.numeracao` |
| Etapa Conteúdo | `interface/templates/interface/compor_conteudo.html`, `interface/static/interface/conteudo.js` | nenhuma obrigatória | as pendências já saem no topo da etapa; aviso ao digitar, no navegador, seria melhoria opcional e nunca a fronteira (Princípio IV) |
| PDF | `pdf.py` (composição) | **nenhuma** | `FR-1219`; a fixture de bytes do contrato do documento publicado não muda |
| Modelo e API | — | nenhuma migration, nenhum campo | os achados já viajam na resposta da submissão |
| Documentação | `README.md` (tabela de incrementos) | uma linha da `065` | exigida por `tests/test_readme_acompanha_o_codigo.py` |

## 2. Estimativa de complexidade

| Parte | Complexidade | Por quê |
|---|---|---|
| Conflito de numeração (`FR-1198` a `FR-1203`) | **Pequena** | leitura do começo de cada parágrafo contra um número que já existe |
| Lista de números legítimos e o conjunto de prova (`SC-464`) | **Pequena a média** | a forma é simples; o trabalho é cobrir cada caso com teste |
| Itens do documento sem segunda regra (`FR-1205`) | **Média** | é o ponto em que é fácil duplicar a composição |
| Remissões (`FR-1204` a `FR-1209`) | **Média** | lista, intervalo, exclusão de outro ato, cruzamento com os itens |
| Mensagens, agrupamento e destino por seção (`FR-1214` a `FR-1217`, `UX-159` a `UX-161`) | **Pequena** | infraestrutura de pendências existente |
| Retificação (`FR-1213`) | **Pequena** | `D-002`: tudo aviso, sem comparar com o publicado |
| **Total** | **Média** | da ordem do RC-21 mais a parte de remissões |

## 3. Plano de validação com os PDFs reais

Os artefatos de partida estão em `doc/auditoria-edital-pdf-2026-10-08/`:
`pdf/` (os documentos da auditoria), `snapshots/` (o conteúdo publicado congelado de A e de B),
`cenarios/` (os roteiros que publicam pelo fluxo real e o `confirmar_numeracao.py`, protótipo
exploratório da conferência — **não** é a implementação).

1. **Cenário B, sem correção.** Rodar `cenario_b.py` sobre o código novo. Esperado: os 5 achados de
   numeração (15 parágrafos) e a remissão ambígua "item 8.1" (`SC-462`, `SC-463`), e a submissão
   recusada pelos conflitos (`SC-469`, `D-001`). Guardar as mensagens.
2. **Cenário B corrigido só pelas mensagens.** Cópia do roteiro com as seções reescritas conforme os
   achados (3.x→4.x, 4.x→6.x, 8.x→11.x e "item 8.1"→"item 11.1", 11.x→12.x, 14.x→15.x). Publicar e:
   - extrair o texto (`pdftotext -layout`) e conferir por script que todo parágrafo numerado começa
     pelo número da sua seção e que "11.1" corresponde a um item só (`SC-465`);
   - conferir 44 páginas, como antes;
   - comparar o texto com `pdf/B-publicado.pdf`: só os números corrigidos diferem;
   - renderizar as pp. 39–44 com CoreGraphics (`qrender_all.py`) e com `pdftoppm`, e olhar.
3. **Cenário A.** Rodar `cenario_a.py` e `cenario_a2.py` (com a Retificação): **zero** achados de
   numeração e de remissão (`SC-464`).
4. **Bytes do documento.** Renderizar `snapshots/A-conteudo-publicado.json` e
   `snapshots/B-conteudo-publicado.json` com o código novo por `render_old.py` (a raiz extraída é a do
   código novo) e comparar com `pdf/A-publicado.pdf` e com o documento B gravado: bytes idênticos
   (`SC-466`, `FR-1219`). O harness já reproduziu o publicado byte a byte na auditoria.
5. **Imutabilidade.** Num banco de demonstração com Editais publicados, registrar o SHA-256 de todo
   documento gravado antes da implantação e conferir depois (`SC-466`). A página de um Edital publicado
   com conflito não mostra achado (User Story 4).
6. **Retificação que desloca a numeração.** Sobre o B corrigido e publicado, uma Retificação que
   esvazia "Do Atendimento à Pessoa com Deficiência" (7): as seções seguintes passam a sair com número
   menor, os conflitos aparecem como avisos e a Retificação é publicada (`SC-470`, `D-002`).
   Inspecionar o consolidado e registrar o deslocamento, que é a consequência aceita da decisão.
7. **Falsos positivos.** Conjunto de prova com ao menos 40 parágrafos **sintéticos**, uma linha por
   caso da tabela de *Edge Cases* (sem dado pessoal: `doc/` e testes são varridos por
   `test_sem_dado_pessoal_da_amostra.py`). Como exploração, sem versionar: rodar a conferência sobre o
   texto dos nove Editais reais da amostra e revisar cada achado à mão — cada um deve ser conflito
   verdadeiro ou limitação já registrada na spec.
8. **Suíte.** `cd backend && make lint check test-pg`, com `tests/test_citacoes_de_requisito.py`
   (que varre `specs/`) e o guardião do README.

## 4. Medições desta investigação, para conferência

- Cenário B: 23 parágrafos começam por número de subitem; 15 em conflito, em 5 seções; 8 coerentes,
  em 2 seções. Uma remissão interna ("item 8.1"), com dois destinos. Cenário A: nenhum parágrafo
  numerado.
- Amostra (nove Editais, `pdftotext`, contagem por linha e por isso aproximada): 77 remissões
  "item/itens/subitem N" e 15 a "Quadro N". Começos de linha numéricos mais frequentes: `9.9`
  (213, mais 71 com espaço de largura zero colado depois), datas `99/99/9999` (106), `9.9.9` (45),
  ordinais `99º`/`9ª`, horas `99h`, e números de lei quebrados no começo da linha (`99.999/9999`).
