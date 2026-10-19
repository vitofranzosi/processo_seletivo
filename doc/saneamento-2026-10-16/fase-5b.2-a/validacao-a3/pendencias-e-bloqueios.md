# Pendências, bloqueios e riscos — A.3

## Antes de consultar a engine

| Pendência | Evidência atual | Necessidade para liberar somente a consulta |
|---|---|---|
| Autorização humana específica | Nenhuma concedida; exemplo não operacional permanece vazio | Aprovar comando `inspecionar`, uma tentativa e escopo de leitura |
| Endpoint local e engine já ativa | Não consultados; a guarda verifica apenas prefixo de URI | Responsável confirmar endereço exato/localidade e funcionamento prévio, sem iniciar serviço para viabilizar a consulta |
| Binário/PATH confiável | Operador chama `docker` pelo PATH, sem shell | Identificar caminho/hash do executável por inspeção de arquivo, sem executar Docker adicional não aprovado |
| Cliente e autorização independentes | `docker-cliente/config.json` e `autorizacao.json` ausentes | Autorização expressa dos dois arquivos de controle mínimos, hashes/aprovador/referência e cliente `{}`; não copiar config existente |
| Prazo e interrupção | `subprocess.run` sem timeout | Aprovar limite/supervisão manual só do cliente; ou autorizar revisão de timeout antes da consulta |
| Custódia e destino | Não informados; ramo inspecionar só imprime JSON | Definir registro novo, conteúdo sanitizado, responsável e retenção |

Nenhuma dessas pendências foi resolvida por iniciar processos ou consultar serviços nesta rodada.
Sua enumeração encerra a análise preparatória, não a validação operacional.

## Riscos operacionais documentados

1. Endpoint ou binário divergente pode invalidar a premissa de leitura local. Um prefixo de URI
   e hashes de artefatos do projeto não identificam sozinhos o serviço/executável externo.
2. A conexão a um endpoint com ativação por acesso pode acionar infraestrutura externa ao código
   inspecionado. Exigir confirmação de engine já ativa e de que essa ativação não é necessária;
   sem isso não tentar. Não há evidência de que esse mecanismo exista nesta máquina.
3. O usuário host pode ter poderes amplos no daemon; o operador é guarda de fluxo, não ACL Docker.
   Arquivos locais podem mudar após a conferência. Operação de leitura pode gerar logs/métricas.
4. Sem timeout automático, uma resposta bloqueada pode deixar o cliente aguardando. Não converter
   essa espera em permissão para reiniciar daemon/VM ou trocar contexto.
5. O ID retornado não demonstra rede interna, volumes exclusivos, papel mínimo, egress bloqueado,
   integridade SQL, baseline válida ou sessão restrita. Esses aceites exigem gates separados.
6. O registro A.2 de 29 testes não é execução nova nem prova de operação real. Os mocks usados
   para testar criação/consulta evitam efeitos e não certificam a API Docker ou PostgreSQL.

Esses riscos são limites da garantia estática e condições para operação futura, não incidentes
observados. Não foi detectada execução, vazamento ou perda de evidência por esta análise.

## Gates posteriores que permanecem fechados

- Plataforma/procedência/imagem final/build: escolher arquitetura após inspeção autorizada,
  aprovar digests/contexto/builder/wheels. Nenhum pull/build autorizado.
- Recursos e bootstrap: aprovação própria de create; executor segregado para initdb/start com
  estruturas administrativas expressamente enumeradas; não criar banco da app por efeito oculto.
- Banco/papéis/migrations/concessões: revisar executores e política SQL de gatilhos/funções.
  Não inferir aprovação das etapas pelo grafo de dependências.
- Baseline: aprovar T0/janelas, orçamento, catálogo e complementos por cenário; preservar falha
  parcial e proibir limpeza/reexecução para encobrir resultado.
- Web/homologação: decidir autenticação, permissões sintéticas, controles técnicos/procedimentais,
  protocolo e participantes. Não confundir bloqueio da partida com ACL de cenário.
- Custódia/descarte: definir retenção, alvos/IDs e recuperação parcial antes de autorizar qualquer
  remoção. Parada e descarte não são efeitos autorizados de uma consulta de leitura.

## Próxima decisão e ponto de parada

Entregar os seis documentos e solicitar aprovação explícita da consulta descrita em
[consulta-engine-proposta.md](consulta-engine-proposta.md), acompanhada dos parâmetros e
arquivos mínimos. A execução termina nessa solicitação; não há consulta automática posterior
ao relatório. Sem resposta expressa, o estado continua aguardando autorização.

**A.3: preparação concluída; operação pendente. 5B.2-A integral: não concluída.**
Não alterar registros de ratificação DEC-15 nem declarar pendência encerrada por aprovação documental.
