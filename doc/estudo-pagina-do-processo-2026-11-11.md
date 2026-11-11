# Estudo da página do Processo Seletivo — rodada 1 (11/11/2026)

Relatório completo, com as capturas: <https://claude.ai/artifact/GBEBV6rtKUVYnduNvwX95X>. Este
arquivo guarda o texto no repositório. A decisão do usuário — alternativa B com os seis ajustes —
virou a spec [`147`](../specs/147-pagina-do-processo/spec.md).

## Pedido

Revisão de UI/UX da página de detalhe do Processo Seletivo, com ponto de controle antes de
implementar: investigar, construir duas alternativas com os templates e as folhas reais, validar em
cenários, papéis e larguras, e recomendar. Princípios: **o Processo permite compreender e
administrar o conjunto; o Edital permite compreender e conduzir a seleção.** Vetados: novo
dashboard, motor de workflow, estados novos, indicadores artificiais, persistência de apresentação.

## Diagnóstico, por impacto

1. **"O que fazer agora" oferecia o excepcional e calava o trabalho.** `atos_processo.disponiveis`
   filtra só por permissão e situação; o impedimento (`pending_editais`) vinha depois, recolhido. As
   condições de atenção e as ações da pessoa não apareciam no cartão. A faixa da 104
   (`trabalho.do_ator`) não era lida.
2. **"Onde cada Edital está" crescia em linha reta.** Por Edital: parágrafo, gráfico, título e lista
   de marcos. 2.791 px com 4 Editais, 10.369 px com 31 (14 gráficos, 15 "Sem cronograma vigente",
   20 sinais no fim), a 1366 px.
3. **O mesmo Edital em três lugares**: a tabela, o acompanhamento e a Atenção.
4. Atenção sem agrupamento por Edital, e sem marca na linha.
5. O ciclo Em elaboração → Ativo → Encerrado em cartão de largura total, repetindo o selo.
6. Acessos sem nome de grupo; "Abrir a Supervisão" repetido.
7. "Aguardando quem elabora" para todo papel sem elaboração, inclusive quem só avalia.
8. Série diária sem valor com poucos pontos, repetida para períodos encerrados.
9. Polimento: filete entre o título dos marcos e a lista, marcadores fora do recuo, datas sem dizer
   se são início, prazo ou evento.
10. O estado "Processo sem Edital" não nasce pela aplicação — `create_process_with_first_edital`
    sempre cria o primeiro —, e só serve a dado legado.

## O que pertence a quem

| Informação ou ação | Nível | Origem |
|---|---|---|
| Título, código, situação, ciclo | Processo | modelo, `_trilha_processo` |
| Supervisão, Comissão, Alocação, Auditoria | Processo | `pode_gerir_comissao`, `auditoria:consultar` |
| Novo Edital, Ativar, Encerrar, Cancelar | Processo | `edital:criar`, `atos_processo`, `pending_editais` |
| Elaborar o Edital / Aguardando quem elabora | Edital | o primeiro em elaboração |
| Inscrições recebidas, em preenchimento, 24 h | agregado | `supervisao.pulso` |
| Período, série, próximos marcos | Edital | `pulso.por_edital` |
| Atenção | Edital | `supervisao.sinais` |
| Retificação em curso | Edital | `em_curso_por_edital` (hoje fora da página) |
| Ações da pessoa | Edital | `trabalho.do_ator` (hoje fora da página) |
| Onde estamos, mapa de fases, providências por lista | Edital | `andamento` — fica no Edital |

## Dados da validação

Banco `ps_ux_147`: `seed_demo`; os 15 cenários de treinamento; PS-EAD-2026-2 (4 Editais); PS-UAB-2026
(31 Editais, montados aplicando as receitas da 134 a Editais irmãos); PS-ENCERRADO-2025 e
PS-CANCELADO-2026. A carga dos cenários exige `ARQUIVOS_CANDIDATOS_RAIZ` no ambiente do comando.

## Alternativas, medidas

| Cenário (1366 × 768) | Hoje | A | B |
|---|---:|---:|---:|
| Em elaboração, 1 Edital | 1.128 | 914 | 1.079 |
| Ativo, 1 Edital com atenção | 1.594 | 1.277 | 1.240 |
| Ativo, 4 Editais | 2.791 | 1.986 | 2.001 |
| Ativo, 31 Editais | 10.369 | 6.919 | 4.042 |
| Encerrado | 931 | 863 | 908 |
| Cancelado | 1.005 | 959 | 908 |

A: sem rolagem lateral da página, mas a tabela corta inscrições e marco a 390 px. B: sem rolagem
lateral em 390, 1366, 1440, 1920 e 3440 px, com a barra aberta e recolhida. Consultas: +2 fixas nas
duas; a avaliadora pagava 72 → 195 porque a faixa calculava a carga de todas as Etapas dela.

## Recomendação e decisão

B, com seis ajustes: sem duplicar o próximo passo; sem a região de Atenção para quem não alcança
espécie alguma; linha de uma altura para o Edital em preparo; Atenção antes dos marcos no estreito;
carga de avaliação recortada ao Processo na consulta; o ciclo em uma linha. O usuário escolheu "B com
os ajustes" em 11/11/2026; as quatro decisões abertas (série só em curso, "Aguardando quem elabora"
só para quem gere, finais recolhidos no Processo ativo, este registro) seguiram a recomendação e
estão no `research.md` da 147.

## Resultado da implementação

Medido no mesmo banco, depois da 147: PS-UAB-2026 com 3.663 px a 1366 × 768; PS-EAD-2026-2 com
2.026 px; nenhuma rolagem lateral nas cinco larguras. Consultas: +1 para cada papel; a avaliadora,
72 → 128, porque ela tem alocações em 14 Editais **deste** Processo — a carga cresce com as
alocações da própria pessoa, como na Lista (104), e não mais com as de outros Processos.
