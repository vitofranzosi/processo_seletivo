# Verificação: A jornada não aponta o ato errado (133)

Feita em 08/11/2026, na branch `claude/133-jornada-sem-ato-errado`, sobre a `main` em `da566ff2`.

## A análise cruzada (spec × plano × tarefas)

`/speckit-analyze` antes de implementar. Não houve achado crítico. Houve um médio e cinco baixos,
todos incorporados às tarefas antes da implementação (commit `7a48f516`):

- **I1:** os quatro instantes passam a ser as paradas equivalentes da versão reduzida do 900.
- **C1:** acrescentado o teste de que a tela da convocação e o cartão concordam.
- **C2:** acrescentado `makemigrations --check`.
- **C3:** acrescentado o caso do sorteio que é marco intermediário.
- **C4:** acrescentado o POST direto às rotas.
- **C5:** acrescentado o desempenho da tela do corte.

## Linha de base

`make test-pg`, com `DB_NAME=ps_133` e 4 workers, na branch antes de qualquer mudança de código:
**17282 passando, 21 pulados, sem falha** (1419s).

**Ressalva:** parte dessa rodada correu enquanto os módulos novos e `andamento.py` eram editados na
mesma worktree. Como o código importa sob demanda, a linha de base pode ter lido parte do código
novo. Por isso, a suíte que vale é a final, abaixo, e a comparação é por lista de pulados e de
falhas, e não por total.

## Suíte final

| Rodada | Resultado |
|---|---|
| 1ª, com tudo implementado | **17345 passando, 21 pulados, 2 falhas** (739s) |
| 2ª, depois dos ajustes abaixo | **17347 passando, 21 pulados, sem falha** (713s, 4 workers) |
| 3ª, depois dos achados da revisão do PR #432 (abaixo) | **17352 passando, 21 pulados, sem falha** (784s, 4 workers) |

As duas falhas da 1ª rodada:

1. **`tests/test_dependencia_da_ocupacao.py::test_a_ocupacao_le_classificacao_so_pelas_portas_declaradas`.**
   O guardião da `016` limita o que a ocupação importa de `classificacao`. A regra do marco
   intermediário não ordena, não desempata e não escolhe ninguém. Ela entrou na lista permitida, com
   a razão, e os três módulos da ocupação passaram a importá-la como módulo completo.
2. **`tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`.**
   É o teste de tempo que o `CLAUDE.md` registra como oscilante com 4 workers. Isolado, passou três
   vezes em três, e também com os outros 114 testes da ocupação em 4 workers. A recusa acrescenta à
   apuração uma leitura de dicionário sobre um conteúdo que ela já tinha lido.

**Pulados:** os mesmos 21 da linha de base. São 10 do vocabulário, a recusa por vendor, o E2E da
Caixa e 9 arquivos do grupo `navegador`, que não estava instalado nesta worktree.

`make lint` (`ruff check` e `ruff format --check`) passou. `manage.py makemigrations --check
--dry-run` deu *No changes detected* (SC-1428).

## Os testes ajustados pela frase do corte (R-008)

A frase nova é a correta nos cenários com lista reservada e alvo fixo. Cada expectativa abaixo
passou a dizer "de cada lista de concorrência":

| Teste | O que mudou |
|---|---|
| `unit/publicacoes/test_pdf_classificacao.py::test_o_documento_imprime_o_desfecho_do_empate_no_corte` (2 parâmetros) | "os 10 (dez) primeiros classificados de cada lista de concorrência." |
| `unit/publicacoes/test_pdf_classificacao.py::test_o_alvo_de_um_concorda_com_o_numero` | o singular e o singular com suplente |
| `unit/publicacoes/test_redacao_no_documento.py::test_cada_frase_do_contrato_sai_onde_a_variante_existe` | a frase do contrato |
| `unit/interface/test_revisao.py::test_a_classificacao_mostra_o_metodo_comum_e_o_que_o_marco_declara` | a linha "Corte:" da Revisão |
| `unit/interface/test_revisao.py::test_o_marco_que_diverge_diz_em_que` | idem |
| `unit/publicacoes/test_documento_da_auditoria_depois_da_069.py::test_o_documento_sai_com_os_bytes_gravados` (B) e `test_itens_do_documento.py::test_o_documento_da_auditoria_sai_com_os_bytes_esperados_depois_da_069[B]` | os bytes esperados do cenário B passam a ser os de `demonstracao/B-*-133.pdf`, gravados pelo compositor. Os da `096` ficam onde estão, como evidência dela |

**O guardião da diferença**, `unit/publicacoes/test_documento_da_auditoria_depois_da_133.py`, prova
nos três documentos do B que o texto da `133` é o da `096` com o complemento, e nada mais. É o
mesmo método da `096`.

**FR-4555.** O documento publicado é servido dos bytes gravados. O guardião é
`integration/publicacoes/test_acervo_da_069.py::test_o_documento_publicado_antes_e_servido_com_os_bytes_gravados`,
e nenhuma rotina desta feature recompõe documento.

**FR-4556.** O quadro de alterações da Retificação vem das mudanças do conteúdo
(`alteracoes_legiveis(conteudo_base, alteracoes)`), e não da prosa composta. A mudança de redação
não gera alteração.

## Demonstração no navegador (princípio VI)

Feita nos bancos de fase do estudo de convergência, com o **Edital 900 completo** (18 candidatos,
três listas), migrados para a branch e servidos pelo `servidor.py` do estudo de 07/11, com o relógio
no instante de cada banco. As capturas "antes" estão em
`doc/estudo-convergencia-ux-2026-11-07/capturas/`, e as "depois" em `capturas/`.

| Instante | Antes (estudo) | Depois (`capturas/`) |
|---|---|---|
| 10/12, preliminar e prazo até 12/12 | "SUA: Emitir o corte" (`01-t2-…`) | `depois-10-12-o-que-fazer-agora.jpg`: "Aguarda · recomendação · Emitir o corte — … até 12/12/2026: um recurso deferido tornaria o corte obsoleto…", com "nenhuma é sua". `depois-10-12-tela-do-corte.jpg`: "Recomendação: aguarde.", antes do botão, que continua |
| 13/12, ordem da ampla obsoleta, quem publica | "Pendente: Publicar o resultado definitivo" da ampla | `depois-13-12-quem-publica.jpg`: só as definitivas da PCD e da PPI. A da ampla fica *Depois* |
| 29/12, apuração do marco 2 | 1º item "SUA: Apurar a ocupação" do marco 1 (`03-t5-…`) | `depois-29-12-o-que-fazer-agora.jpg`: só "Convocar 4 titulares", "Convocar 1 titular" e "Convocar 1 titular". `depois-29-12-ocupacao-do-marco-1.jpg` e `…-convocacao-do-marco-1.jpg`: o aviso com o link da Classificação final, sem ato |
| 05/01, Bruno desistiu e Rafael pendente | só "Aguarda: resposta de 1 convocação" (`07-t6-…`) | `depois-05-01-o-que-fazer-agora.jpg`: "SUA: Chamar a próxima da fila" e a resposta de Rafael em espera |
| 06/01, 6 vagas ocupadas | "SUA: Apurar a ocupação" (marco 1) | a sonda: nenhuma providência |

A sonda do estudo (`doc/estudo-convergencia-ux-2026-11-07/roteiro/sonda.py andamento <instante>`)
foi rodada nos cinco bancos, e confirma o que as capturas mostram.

**Polimento anotado, fora do escopo.** A ocupação do marco intermediário ainda diz "Ocupação ainda
não apurada" em cada lista. É verdade, mas é ruído abaixo do aviso. Fica para quem retomar a tela.

## A revisão do PR #432

`/code-review` (alto esforço) achou nove pontos, todos corrigidos no commit `eff2c08b`:

1. **A espera do corte sumia com a publicação de um ato anterior.** Ordem sucessora emitida e não
   publicada, prazo ainda correndo: o cartão voltava a dizer "SUA: Emitir o corte", e a tela do
   corte dizia "aguarde". Agora as duas leem `andamento.espera_da_lista`, que afere o ato vigente
   quando a preliminar publicada é de outro. Teste:
   `test_com_a_sucessora_ainda_nao_publicada_o_corte_continua_esperando_o_prazo`.
2. **"Próximo nesta lista" pulava para a Etapa paralela.** Sem nada da pessoa, o que se pratica agora
   é procurado só no trecho do marco (a FR-4090 da `127`). Teste:
   `test_sem_nada_de_ninguem_a_praticar_no_marco_o_proximo_nao_pula_para_a_etapa_paralela`.
3. **A convocação do marco intermediário listava a fila.** As seções "Quem pode ser chamado" e "…
   para regularizar" saem. Teste: `test_a_convocacao_do_marco_intermediario_nao_lista_a_fila`.
4. **O lote recusava pelo motivo errado.** A recusa vem antes da prévia. Teste:
   `test_o_lote_sem_apuracao_recusa_pelo_motivo_verdadeiro`.
5. **O sorteio com recurso declarado também espera.** O comportamento é o que a FR-4541 descreve, e
   está preso em `test_o_sorteio_com_recurso_declarado_tambem_espera`. **Decidido pelo usuário em
   08/11 (D-006 da spec):** a espera vale também para o sorteio, sem bloquear a emissão. O rito do
   Edital 35, por si só, não justifica exceção. Pendência encerrada.
6. **Reuso:** a tela do corte usa `conducao_do_marco.marco_publicado`.
7. **Leitura evitada:** a espera só é aferida para quem emite.
8. **Conta repetida:** a data do prazo sai da própria `Afericao` (campo `ate`, preenchido por
   `_impedimento_da_definitiva`), e não de uma segunda chamada a `janela_aberta_ate`.
9. **Leitura repetida:** o aviso do marco intermediário lê a versão vigente uma vez (por
   `marco_publicado`).
