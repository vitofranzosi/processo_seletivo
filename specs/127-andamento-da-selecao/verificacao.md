# Verificação: Andamento da seleção (127)

## B1 — o nível 1 (06/11/2026)

### Suíte

`make lint check` verde (os dois passos do `ruff` e `makemigrations --check`, sem migration).

`make test-pg` com `DB_NAME=spec127`, 4 workers, `worksteal`, com o grupo `assistente` e sem o
`navegador`, sobre a `main` em `250efe97` mais o B1, numa máquina com outras duas suítes no mesmo
cluster (carga 15):

**16 791 passaram, 20 pulados, 8 falharam, em 2613 s.** O teardown ficou ~25 min parado no
`DROP DATABASE`, à espera do checkpoint do cluster disputado (`suite-presa-no-drop-database`).

As oito falhas, e o que foi feito com cada uma:

| Falha | Causa | Destino |
|---|---|---|
| `test_acessibilidade::…[_providencias.html-]` | classe `de-outros` sem regra na folha | regra acrescentada |
| `test_folha_estatica::test_cada_folha_de_tela_e_carregada_so_por_quem_a_usa` | a folha nova não estava no registro | `andamento.css` → `detalhe.html` |
| `test_polish_da_057::test_o_detalhe_desenha_as_terminais_…` | o template trocou `grupo.principal %}{% include` | o peso da principal sai da view (`peso_da_principal`) |
| `test_politica_de_conteudo::…[detalhe.html]` | `{% if %}` dentro do bloco de estilo | a folha passa a vir sempre |
| `test_citacoes_de_requisito::…inexistente` | o teto da faixa citado como identificador | escrito por extenso |
| `test_readme_acompanha_o_codigo::…tabela_de_incrementos` | a `127` fora da tabela do README | linha acrescentada |
| `test_fluxo::test_detalhe_mostra_a_trilha_e_quem_atuou` | a trilha sai depois da publicação (D-002) | o teste passa a provar a ausência; a trilha da pré-publicação é provada em `test_andamento_do_edital` |
| `test_ocupacao::test_a_apuracao_cabe_no_dobro_…` | o teste de tempo que oscila sob carga (CLAUDE.md) | passou isolado, com `-k dobro` |

Rodada de conferência, com as correções, dos arquivos afetados e dos da feature (`DB_NAME=spec127c`,
4 workers): **2048 passaram**. Depois das correções da revisão (abaixo), os arquivos da feature e os
do detalhe: **433 passaram**. Linha de base do CLAUDE.md (02/11, `4dbc5872`): 14 638 e 14 pulados; a
diferença no total é a `main` de hoje, que tem mais features, mais os ~110 casos desta.

### Revisão independente

Um subagente que não escreveu o código leu o diff com quatro focos: recomendação que o backend
recusa, generalidade entre métodos, permissões e custo. Quinze achados; o que foi feito:

| # | Achado | Gravidade | Feito |
|---|---|---|---|
| 1 | "Publicar o resultado" sem a aferição da prévia, com ordem obsoleta, corte obsoleto ou reingresso | alta | a mesma aferição; ordem obsoleta → *Depois*; impedimento → *Impedido* |
| 2 | Convocação ignora a Etapa governada com a apuração feita | alta | *Depois* da governada, também na apuração obsoleta |
| 3 | `COM_PENDENCIA` contado como "conferir" | média | passa a esperar o candidato |
| 4 | Processo em estado final ainda "seu"; "quem elabora Retificações" no Edital encerrado | média | D-021 |
| 5 | Sortear sem a ocorrência válida; anular sem os insumos | média | a mesma condição da tela; anular sem insumo → *Impedido* |
| 6 | Recusa do indicador vira *Pendente* | média | todos os pontos do marco *Impedido*, com a frase |
| 7 | Método de sorteio comum do Edital (S3) | média | métodos resolvidos na entrada (`metodo_que_governa`) |
| 8 | A aferição recalcula a ordem a cada abertura | média (custo) | **registrado**: o recálculo é o da prévia; o teste de escala ganhou o cenário de convocação |
| 9 | Leituras repetidas (versão vigente, ato) | média (custo) | **registrado**: 199 consultas no Edital com três listas convocáveis, constante com as convocações |
| 10 | As frases da Retificação somem com providência da pessoa | média/baixa | voltam, sem o "Nenhum ato" |
| 11 | Avaliador sem providência numa Etapa sem efeito | baixa | a avaliação da pessoa aparece |
| 12 | Convocação "feita" com vaga sobrando | baixa | *Impedido*, com a razão |
| 13 | Espera nunca se junta; ponto duplo | baixa | agrupa pela primeira frase; a razão sem o ponto final |
| 14 | "Observar a extração" repetida por marco | baixa | uma por fonte e referência |
| 15 | A providência juntada leva só à primeira lista | baixa | leva à condução do marco |

Os itens 8 e 9 são otimização: passar a versão vigente e o ato do indicador adiante às funções das
telas. Ficam como pendência técnica desta feature, e não mudam o que se lê.

### O banco do estudo (inspeção, não teste com pessoas)

O clone do banco do estudo (`ps_base` da sessão da `126`, que é o retrato com os Editais 35, 57, 51,
91, 72, 26 e 90) restaurado em container próprio (`ps-spec127`, porta 55437) e migrado. As capturas
"antes" rodam a `main` exportada com `git archive`; as "depois", esta branch. **Este banco é
anterior ao `ps_jornada` do estudo** (o 35 ainda não tem convocação, e o corte das reservadas não foi
emitido), e por isso o 35 não lê exatamente o que a maquete `N1` previa.

Quatro desvios apareceram só com os dados reais, e viraram decisões (D-018 a D-020): a faixa
seguinte e a apuração sem corte, a progressão do S2, o lugar longo.

| Edital | Papel | Lido no nível 1 | Bate com o estudo? |
|---|---|---|---|
| 35 | gestor | Sua: convocar 4 titulares (ampla); Sua: emitir o corte (PCD e PPI); quem publica: definitivo; Atenção às duas Etapas | sim, para este retrato do banco (CA2 pedia o retrato posterior) |
| 35 | publicador | Sua: publicar o resultado definitivo | sim |
| 35 | elaborador | três de outros papéis, sem link; sem "Nenhum ato" | sim |
| 57 | gestor | Sua: congelar a relação (Tecnologias); Aguarda: a extração 6116, prevista para 09/11 | sim (SC-1232, CA3) |
| 91 | presidência | Sua: avaliar 12 (Prova de Títulos); Sua: distribuir 12 (Desempenho Didático); Atenção: a Entrevista | sim (SC-1233, CA9) |
| 51 | gestor | Sua: distribuir 1 (Análise de títulos); Sua: emitir 1 comunicação; quem publica: definitivo | em parte: a ordem da PPP é *Depois* da Análise de títulos, que tem uma inscrição sem avaliador (a `G3` a dizia pendente); a da ampla foi emitida antes, que é o `G-01` da `126` |
| 72 | gestor | Sua: realizar o sorteio; Atenção: "Sorteio" e Avaliação documental | sim (S2, G-05) |
| 26 | gestor | Sua: distribuir 7 (Análise de títulos); Sua: emitir o corte; quem publica: o resultado | sim; a Prova objetiva virou Atenção (D-019) |
| 90 | elaborador | o cartão de hoje, com a trilha e o bastão | sim |

**Medidas** (`capturas/depois-b1/medidas.json`, a 1280 px): a lista das providências termina entre
358 e 492 px; as da pessoa, entre 332 e 408 px (UX-232, SC-1240). Nenhuma página rola de lado, a
1280 nem a 375 px (SC-1241). A página ficou mais alta (35, gestor: 1767 → 2022 px), porque o cartão
"Classificação" continua: o B2 o substitui pelo nível 2 recolhido.

### Validação com pessoas

Não feita. O roteiro do estudo (`validacao.md`) vale com as telas implementadas no lugar das
maquetes, e a SC-1245 espera o usuário. **Inspeção não substitui teste com pessoas.**

## Code review dos três PRs (06/11/2026)

Feito com o `/code-review` (esforço alto), um por PR, depois das revisões independentes. Os achados
e o que se fez:

| PR | Achados | Corrigidos | Registrados, sem correção |
|---|---|---|---|
| #415 (B1) | 8 | o lugar da providência recortado do nome do Perfil (com " · "); a falha da derivação derrubando o detalhe (agora volta ao cartão de antes, com log); a carga do avaliador lida do rótulo da `104` (agora `ObjetoDeTrabalho.quantidade`); a conferência consultada por lista; a expectativa recalculada; a docstring contra a D-017 | o andamento inteiro derivado para todo papel, e as avaliações de todos os Editais da pessoa — custo, junto da pendência de passar a versão vigente adiante |
| #416 (B2) | 7 | quem só publica via a matriz da convocação (agora vê o Perfil recolhido, D-004); a contagem por Perfil com as Etapas do Edital; a Etapa citada pelo marco tirada da sequência; Perfis homônimos (agora com o número de inscritos); a condição repetida | o `resumo_dos_marcos` lido sem leitor; a view gravando os destinos nos objetos do andamento |
| #417 (transições) | 6 | "sua" refeito na view (agora `Andamento.e_sua`, a regra do nível 1, com a mesa e a conferência); o Edital inteiro derivado por ato (agora só o Perfil do marco); a semente apontando uma lista só; "Ainda neste marco" sem situação nem papel; testes em ordenação, ocupação e sorteio | — |

A tela dos documentos da convocação recebeu a transição e não tem teste próprio: o cenário pede a
infraestrutura de arquivos da suíte.

Suíte depois das correções, sobre a pilha inteira (B1 + B2 + `126` + transições): **16 910 passaram,
20 pulados, nenhuma falha, em 678 s.**
