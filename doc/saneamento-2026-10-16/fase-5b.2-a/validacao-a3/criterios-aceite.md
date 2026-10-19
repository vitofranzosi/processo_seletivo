# Critérios de aceite e evidência verificável — A.3

Data: 19/10/2026. Estes critérios encerram somente o trabalho documental autorizado.
Aceite operacional de P0 ou de qualquer gate posterior permanece separado.

## Critérios da preparação documental

| Critério | Evidência / resultado |
|---|---|
| Branch/HEAD/working tree identificados | Branch e commit completos no README; status só mostra saneamento não rastreado; nenhum arquivo rastreado modificado |
| Governança examinada | Constituição 1.2.0 lida integralmente e limites da solicitação atual aplicados |
| Relatórios A.1/A.2 lidos | README, matrizes, operações, validação A.1; oito entregáveis A.2 e evidências JSON examinados; fontes técnicas inspecionadas |
| Integridade independente das alegações Markdown | SHA-256 recalculado dos arquivos e bytes brutos OCI preservados; resultados detalhados abaixo e na matriz |
| Resultados de teste corretamente qualificados | Registro histórico 29 OK examinado e contagem AST 19+10 confirmada; zero testes de guarda executados nesta rodada |
| Dependências classificadas | D01–D27 em matriz-dependencias.md, com objeto, limite, evidência e próximo responsável |
| Consulta pronta para deliberação | Comando exato, pré-condições ainda necessárias, efeitos/limites e critérios definidos; não executada |
| Autorizações explícitas | Matriz conforme pedido, sem herdar permissões anteriores; nenhum arquivo ativo de aprovação criado |
| Alterações restritas à A.3 | Seis documentos novos; os 103 arquivos de saneamento pré-existentes devem permanecer iguais ao snapshot inicial |
| Limitações/encerramento registrados | Status documental A.3 explícito; 5B.2-A integral não concluída; ponto de parada é o pedido humano |

Critério de falha desta preparação: documento obrigatório ausente, divergência não explicada,
arquivo anterior alterado, operação fora de escopo ou status que transforme proposta em autorização.
Nenhum desses fatos foi identificado na revisão final. Gates futuros pendentes não são ocultados
nem encerrados para satisfazer a conclusão documental.

## Doze hashes recalculados

Base dos caminhos: `doc/saneamento-2026-10-16/fase-5b.1/`. Resultado de cálculo sobre os
bytes atuais comparado ao `integridade.json` e à evidência A.2; conjunto de nomes também
confrontado com OBRIGATORIOS extraído por AST, sem chamar a função do operador.

| Artefato | SHA-256 calculado em A.3 | Confronto |
|---|---|---|
| `autorizacao.example.json` | `a0fed569fccf98a22b0181f8c6fab2b79ad3c5125a52bae2ac507a1568b5d000` | Coincide |
| `baseline.json` | `9766ace9d1fd8a7250dd409b2b8dabcafbbdd11e0ce29ae261cfd9d59c54e97b` | Coincide |
| `cenarios.json` | `3813b6193ca68e6b828391d2e5463206e1b541552710c46488835d2518ca4d97` | Coincide |
| `compose.homologacao.yaml` | `1dcbb2314a5e7b3e3c2ec2fb135bbb3daad73b884137c0092c349597eeebc06f` | Coincide |
| `homologacao.env.example` | `5e3f08e55f99db85c0331ba5b6cfe1a8d0183d0a77e0752239f21c45e83cdf07` | Coincide |
| `isolamento/contrato.py` | `80b0316aafcac4c97532080402bcbfbfbca75bec5cb55cae3a2db13742876747` | Coincide |
| `isolamento/iniciar_aplicacao.py` | `51552a3c9f62d0d311d6d5dcdd203a5d357786912e9d3ee2c63c3aaedb5df21f` | Coincide |
| `isolamento/politica-protecoes.json` | `1fba2dac871dd024ff06e1f2f6f91882474b88f03bc2029e9eb1498bb022598d` | Coincide |
| `isolamento/politica_operacional.py` | `36c2d9441e048c3931f217531178b917ea9bd4f0f13bd7980ee9a06da18f1fef` | Coincide |
| `isolamento/settings_homologacao.py` | `cdb95950abace0b6c7710cb7f93c2b0a911f12789c4508226b654bec0f37a81f` | Coincide |
| `isolamento/tarefas.py` | `d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4` | Coincide |
| `operar.py` | `cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78` | Coincide |

As referências históricas da A.1 têm onze entradas porque precedem a inclusão da política A.2.
A divergência esperada de versão não é tratada como perda: a cadeia foi conferida contra as
cópias preservadas e os manifests anteriores, em vez de exigir hash antigo de fonte revisada.

Alterações anteriores registradas pela A.2 e confirmadas: em `fase-5b.1/`, foram revisados
`README.md`, `procedimentos.md`, `operar.py`, `compose.homologacao.yaml`,
`autorizacao.example.json` e `integridade.json`; foi acrescentado
`isolamento/politica_operacional.py`. As seis revisões possuem cópias anteriores em
`fechamento-a2/historico-a1/`. A lista de alterações A.1 permanece em seu relatório e
`evidencia-a1.json`; o estado final ali registrado coincide com o inicial da A.2.
Não houve alteração adicional dessas fontes na A.3.

## Impressões digitais das evidências lidas

| Arquivo | SHA-256 observado na A.3 |
|---|---|
| `correcao-a1/evidencia-a1.json` | `1d0cb6c4940d82bfc16e2f8a1cc6e5648899baf5dae74059c4e0f3df93286c20` |
| `fechamento-a2/evidencia-a2.json` | `89c63716cbe65a6064138153b0a4a05c60752a0f30e5a0ef79363f68844c14ca` |
| `fechamento-a2/metadados-publicos.json` | `498b27bc248d1aefc2d3a38018299fd0682fcb7ceed2f366276c99f1e3ef8719` |

Esses três hashes são impressões digitais observadas agora, não assinaturas ou raízes externas
de confiança. A.2 não inclui hash de si mesma no seu próprio manifesto. Nenhuma evidência
histórica foi regravada para fazê-la coincidir com esta verificação.

## Método efetivamente executado

- Comandos Git somente leitura para branch/HEAD/status/diff e leitura integral dos relatórios.
- Python local com `-B`, bibliotecas de parsing e `hashlib`: AST sem importar os módulos
  operacionais, JSON/YAML e asserções locais sobre fontes/dados. Nenhum shell/script gerado de
  operação, runner de testes de guarda, Django ou settings foi executado/importado.
- Recalcular cada índice via SHA-256 dos bytes de `indice_bytes_utf8`; conferir digest/header
  preservados e JSON. Nos seis filhos, também conferir descritor único, plataforma e tamanho.
- Comparar 17 hashes vigentes, 19 documentos/propostas e as cópias históricas de 15 e seis arquivos.
  Conferir os hashes iniciais A.2 contra os finais A.1; fotografar 103 arquivos antes da escrita.
- Conferir links locais, presença dos seis entregáveis e preservação dos arquivos anteriores
  depois de escrever a documentação. Inspeção de arquivos não é consulta ao Docker.

O valor de teste 29/0/0 e duração 0,033 s vem do JSON A.2, não de cronômetro desta rodada.
Não existe log bruto de execução anexado a esse resultado estruturado. A inspeção AST confirma
estrutura/contagem, não garante execução ou comportamento. Essa limitação está classificada em D26.

Não foram feitas consultas de rede, registry, engine, banco ou aplicação na A.3. Não houve
instalação de dependências, serviço, build, carga, teste persistente, e-mail ou operação Git mutável.
O estado de recursos externos não é inferido da ausência de chamadas feitas por esta análise.

## Aceite futuro P0 — ainda pendente

Necessários: aprovação específica, parâmetros/cliente/binário e hashes conferidos, confirmação
de engine local já ativa, limite de observação e destino. Só então uma execução de `inspecionar`
poderá gerar evidência de ID/UUID e exit code, conforme o documento de consulta.
Uma falha impede prosseguir, sem inicialização/reparo ou segunda operação automática.

Sucesso futuro de P0 não declara plataforma aprovada, isolamento demonstrado ou fase 5B.2-A integral
concluída. Essas condições continuam dependentes dos gates listados em pendencias-e-bloqueios.md.

## Conferência final da preservação

Resultado observado: **103/103 arquivos anteriores preservados**, nenhum removido/alterado;
somente os seis Markdown desta pasta acrescentados. Nenhum arquivo rastreado ou staged mudou;
HEAD permaneceu o indicado no README. Links locais e espaços finais dos seis documentos conferidos.

SHA-256 do mapa inicial de caminhos relativos à raiz → SHA-256 de cada arquivo:
`626aea8dbebc8d868a2e225093eb5e8e7af0c6b476843efade0d5a310db41323`.
Canonicalização usada: `json.dumps(mapa, sort_keys=True, separators=(',', ':')).encode('utf-8')`.
O mapa abrange os 103 arquivos pré-existentes em `doc/saneamento-2026-10-16/`, excluindo a nova
`validacao-a3/`; a comparação final recalculou cada entrada. É fotografia de integridade local,
não assinatura ou prova de autoria. Nenhum manifesto histórico foi atualizado por esta conferência.
