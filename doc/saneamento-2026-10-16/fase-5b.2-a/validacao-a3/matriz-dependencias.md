# Matriz de dependências — evidência e classificação A.3

Data: 19/10/2026. Classificação limitada ao objeto descrito em cada linha:

- **VALIDADA**: verificação documental/estática realizada nesta rodada com resultado consistente.
- **PARCIALMENTE VALIDADA**: há evidência útil, mas falta comprovação adicional para seu uso operacional.
- **PENDENTE**: falta informação, decisão ou evidência; não significa erro nem autorização.
- **BLOQUEADA**: execução vedada nesta rodada e/ou recusada no artefato atual.
- **NÃO CONFORME**: contradição ou divergência objetivamente constatada frente ao requisito/fonte.

Nenhuma classificação documental aprova uma operação. Não foi constatada divergência de hash
ou contradição de versão nos arquivos comparados que justifique classificá-los NÃO CONFORME.
Os controles incompletos e decisões ausentes permanecem discriminados abaixo.

| ID | Dependência / objeto avaliado | Classificação | Evidência objetiva e limitação | Próxima ação / responsável proposto |
|---|---|---|---|---|
| D01 | Branch, HEAD e diff rastreado | VALIDADA | Git indica `001-decisoes-pendentes`, HEAD `6fc3a85a…`; nenhum arquivo rastreado alterado | Preservar estado; operador técnico |
| D02 | Manifesto técnico | VALIDADA | 12 SHA-256 recalculados; conjunto exato igual a OBRIGATORIOS extraído do AST | Revalidar antes de operação; técnico |
| D03 | Histórico A.1/A.2 | VALIDADA | 17 fontes atuais, 19 documentos/propostas A.2, 15 cópias pré-A.1 e seis cópias A.1 corretos; cadeia inicial A.2/final A.1 coincide | Manter custódia; técnico/produto |
| D04 | Índice PostgreSQL local | VALIDADA | SHA-256 dos bytes preservados coincide com digest/header; tabela abaixo | Sem nova consulta remota; aprovação de uso ainda separada |
| D05 | Índice Python local | VALIDADA | Mesmo confronto de bytes/digest/header | Idem |
| D06 | Índice uv local | VALIDADA | Mesmo confronto de bytes/digest/header | Idem |
| D07 | Manifestos PostgreSQL amd64/arm64 | VALIDADA | Dois SHA-256, JSON, plataforma e tamanho correspondem aos descritores do índice | Não comprova execução; técnico |
| D08 | Manifestos Python amd64/arm64 | VALIDADA | Dois SHA-256, JSON, plataforma e tamanho correspondem aos descritores do índice | Não comprova execução; técnico |
| D09 | Manifestos uv amd64/arm64 | VALIDADA | Dois SHA-256, JSON, plataforma e tamanho correspondem aos descritores do índice | Não comprova execução; técnico |
| D10 | Correspondência de referências/versões/digests no snapshot | VALIDADA | Versões declaradas 18.6, 3.13.16-slim-bookworm e 0.9.30; JSON, inventário e digests das bases propostas coerentes | Versão declarada não é versão executada; técnico |
| D11 | Procedência externa, atualidade das tags e segurança de imagens | PARCIALMENTE VALIDADA | Registros locais de coleta em 16/10 e annotations existem; não há assinatura/reconsulta atual nem conteúdo de camadas verificado na A.3 | Aprovação de referências e evidência adequada antes de aquisição; técnico/aprovador |
| D12 | Plataforma e engine locais | PENDENTE | Nenhuma consulta operacional feita; arquiteturas do registry não identificam a máquina | P0 somente após autorização e pré-condições; responsável técnico |
| D13 | Dockerfile e reprodução de build | PARCIALMENTE VALIDADA | Bases por digest presentes e coerentes; sem apt, entrada bloqueada; compatibilidade de wheels/lock/importação/builder não exercitada | Revisar ambiente/contexto e aprovar build separado; técnico |
| D14 | Imagem final da aplicação e aquisição/build | BLOQUEADA | Não há imagem final/ID comprovado; comandos bloqueados no operador e não autorizados agora | Gate próprio após escolha de plataforma/procedência; aprovador |
| D15 | Plano segregado de inicialização | PARCIALMENTE VALIDADA | Plano distingue create, initdb/start, banco/papéis, migrations, carga, web e descarte; grafo tem 18 nós; não é executor/state machine | Revisar executores e pré-condições reais; técnico |
| D16 | Bootstrap/banco/papéis/migrations/concessões | BLOQUEADA | Nomes presentes em BLOQUEADAS; PG recebe `POSTGRES_DB=postgres`, Django aponta ao banco exclusivo | Implementação/revisão e autorização futuras distintas; técnico/aprovador |
| D17 | Autorização de ação única/escopo na fonte | VALIDADA | `validar_escopo` exige lista `[acao]`, revisão, recursos/efeitos exatos e cenários vazios; seis escopos correspondem ao operador | Validação estática não concede autorização; aprovador |
| D18 | Isolamento do endpoint/binário/host em execução | PARCIALMENTE VALIDADA | Código exige prefixo npipe/unix, cliente `{}`, hashes e ambiente reduzido; prefixo não prova localidade, PATH/binário/ativação de serviço não conferidos | Confirmação positiva e custódia antes de P0; técnico |
| D19 | Aprovação/arquivos operacionais de P0 | PENDENTE | `autorizacao.json`, `docker-cliente` e configuração real ausentes; exemplo tem ações/escopo vazios | Confirmar endpoint, responsável/janela/destino e autorizar preparação restrita; humano |
| D20 | Consulta à engine | BLOQUEADA | Nenhuma operação Docker autorizada nesta rodada; apenas comando preparado | Autorizar especificamente P0; humano |
| D21 | Proteções SQL e conferência de banco | BLOQUEADA | `politica-protecoes.json` permanece PENDENTE; conferência exigiria container e banco, não simples leitura de arquivos | Mapear/revisar política e preparar esquema em gates próprios; técnico |
| D22 | Critérios e cobertura planejada da baseline | PARCIALMENTE VALIDADA | Critérios cobrem origem, referências, relógio, canonicalização, orçamento e 14 receitas; nenhuma carga/contagem demonstrada | Manifesto/T0/catálogo e complementos aprovados; produto/técnico |
| D23 | Baseline e recuperação de estado | BLOQUEADA | Seed/carga não executados; ação baseline recusada; falha parcial/recuperação ainda precisam de plano aprovado | Não reexecutar/apagar dados; decisão específica futura |
| D24 | Controle de sessão e protocolo | PARCIALMENTE VALIDADA | Operador e launcher bloqueiam partida; propostas distinguem conta/proxy/procedimento; seletor de identidade continua true | Pactuar autenticação/perfis/roteiros; produto/Cefor/homologação |
| D25 | Web/demonstrações/descarte | BLOQUEADA | Ações recusadas e sem aprovação; não há ACL por cenário ou recuperação de descarte comprovadas | Gates próprios; aprovador/homologação |
| D26 | Resultado dos 29 testes A.2 | PARCIALMENTE VALIDADA | `evidencia-a2.json` registra 29 OK, zero falhas/erros, 0,033 s; AST mostra 19 herdados + dez novos | Nenhum teste executado A.3; não há relatório bruto anexado para atestar novamente a execução; eventual novo ensaio puro exige escopo compatível |
| D27 | Custódia, tempo e prova da consulta futura | PENDENTE | Destino/responsável/janela não indicados; `subprocess.run` não tem timeout; ramo inspecionar não grava evidência | Aprovar supervisão/limite e gravação sanitizada; ou revisar guardas em fase própria |

## Digests efetivamente recalculados

Fonte: [metadados-publicos.json](../fechamento-a2/metadados-publicos.json). Para cada índice:
`sha256(indice_bytes_utf8.encode('utf-8'))` comparado ao digest e header preservados. Para cada
plataforma: cálculo análogo em `manifesto_bytes_utf8`, confronto com header/descritor e comparação
de JSON, plataforma e tamanho. Nenhum digest foi aceito apenas por constar em Markdown.

| Objeto | Referência/plataforma | Digest conferido |
|---|---|---|
| Índice PostgreSQL | `docker.io/library/postgres:18` | `sha256:74935e72241653ca55e0414067e6d8763aceb8a810eb51b452253ec3dcfc4336` |
| Manifesto PostgreSQL | linux/amd64, 3439 bytes | `sha256:885953109528ad3dfc90362b1a6f50a78620b5315be19f187753d267e484dc5b` |
| Manifesto PostgreSQL | linux/arm64/v8, 3441 bytes | `sha256:a63b24165ea0eacced7585766d790ac08bbaefe10a1841f87783a4505d29a69c` |
| Índice Python | `docker.io/library/python:3.13-slim-bookworm` | `sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641` |
| Manifesto Python | linux/amd64, 1752 bytes | `sha256:f040863673aea2570c3ff6a5c3fb4c673a016cbc5375005ad145915922b6b78a` |
| Manifesto Python | linux/arm64/v8, 1754 bytes | `sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d` |
| Índice uv | `ghcr.io/astral-sh/uv:0.9` | `sha256:538e0b39736e7feae937a65983e49d2ab75e1559d35041f9878b7b7e51de91e4` |
| Manifesto uv | linux/amd64, 669 bytes | `sha256:e96d483a9ed7924d2acf01bdd1d537d0d5e6d8f21b74fff3373005f6c9446696` |
| Manifesto uv | linux/arm64, 669 bytes | `sha256:10e89aa55522210851c055c9b261c9c9b4a50ea8ab891e23fe7e138a56287a3e` |

A coleta registrada ocorreu em 16/10/2026, 14:14:36–14:14:41 UTC. A verificação A.3 em 19/10 é
somente local. Headers e annotations preservados não são assinatura independente; os digests
demonstram consistência dos bytes disponíveis, não segurança, compatibilidade ou aprovação das imagens.

## Fontes e alcance da autorização

[Evidência A.1](../correcao-a1/evidencia-a1.json), [evidência A.2](../fechamento-a2/evidencia-a2.json),
[operador](../../fase-5b.1/operar.py), [política de ações](../../fase-5b.1/isolamento/politica_operacional.py),
manifesto técnico e relatórios listados no README A.3. Nenhuma alteração foi feita nessas fontes.
Estados PENDENTE/BLOQUEADA fora do escopo de execução não impedem concluir a preparação documental,
mas impedem declarar a fase 5B.2-A integral concluída ou executar os gates respectivos.
