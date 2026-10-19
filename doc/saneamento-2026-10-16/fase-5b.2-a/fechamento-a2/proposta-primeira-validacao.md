# Proposta de autorização — primeira validação operacional

**Não autorizada por este documento.** A autorização atual permite revisão/testes puros e
metadados públicos, não consulta à engine local nem execução do operador.

## Escopo proposto P0: inspeção local sem provisionamento

Objetivo: confirmar que o cliente exclusivo consegue consultar a identidade de uma engine
local **já ativa**, sem criar ou iniciar recursos. Isso não comprova isolamento de banco/rede/
armazenamento, pois o laboratório ainda não existe. Não usar “P0 concluída” como aprovação do ambiente.

O aprovador deve preencher, antes de qualquer chamada:

- Responsável técnico e aprovador; referência da deliberação e janela.
- Endpoint exato `npipe://...` ou `unix://...`, confirmado como local. Nenhum endpoint foi descoberto nesta fase.
- Caminho exclusivo `doc/saneamento-2026-10-16/fase-5b.1/docker-cliente/config.json`, contendo apenas `{}`,
  sem atalho, credencial/helper, contexto ou outros arquivos; criação desse arquivo deve constar da autorização.
- Arquivo novo de autorização `fase-5b.1/autorizacao.json`, ação única `inspecionar`, revisão `5B.2-A.2`,
  hashes atuais do Compose/integridade/cliente, aprovador e referência; sem senha ou config de banco.
- Destino novo e custodiante da evidência sanitizada, com retenção definida. Não sobrescrever arquivo existente.

Escopo exato esperado pela guarda, além dos demais campos obrigatórios:

```json
{
  "acoes": ["inspecionar"],
  "cenarios": [],
  "escopo": {
    "recursos": ["engine-local-no-endpoint-aprovado"],
    "operacoes": ["engine.ler-identidade"]
  }
}
```

Esse fragmento não é arquivo de autorização completo e não foi criado como concessão operacional.

Comando futuro, somente após aprovação e preenchimento dos arquivos exatos:

```powershell
backend/.venv/Scripts/python.exe -B doc/saneamento-2026-10-16/fase-5b.1/operar.py inspecionar
```

Efeitos: leitura dos artefatos/cliente/autorização e `docker --config <cliente exclusivo>
--host <endpoint aprovado> info --format {{.ID}}`. Sem `homologacao.env`, imagens, Compose,
listas de dados pessoais, conexão SQL ou criação de recibos de recursos. Salvar stdout sanitizado
no destino aprovado é efeito de coleta documental a autorizar expressamente.

## Aceite, risco e interrupção

Aceite P0: aprovação específica verificável, hashes e cliente corretos, resposta bem-sucedida com
ID não vazio, endpoint local, arquivo de evidência sanitizado e resultado declarado como inspeção
de engine. Não preencher identidade da engine por suposição. O ID observado ainda deve ser aprovado
antes de qualquer operação posterior.

Interromper se daemon não estiver ativo, houver erro de permissão/comunicação, cliente/configuração
divergente, endpoint remoto ou herdado, ID ausente, pedido de credencial, saída inesperada ou desvio
de escopo. **Não iniciar daemon**, mudar de contexto, elevar privilégio, fazer pull ou criar recurso
para obter resposta. Falha é evidência, não autorização de reparo.

Riscos residuais: endpoint/daemon podem pertencer a outro uso; usuário com acesso à API pode ter
privilégios maiores que a operação; arquivos continuam sob controle do host. Aprovar endpoint,
operador e custódia explicitamente. Cliente/Compose/imagens locais não foram inspecionados nesta fase.

## Autorizações posteriores separadas

P0 não inclui versão/plataforma do servidor, inspect de imagens ou inventário de recursos além do
ID. Se esses metadados adicionais forem desejados, revisar a ação/escopo antes de executá-los,
ou autorizar sequência independente de comandos somente leitura, revisada e nominada. Não ampliar
o comando por iniciativa do operador. As arquiteturas de registry não escolhem a arquitetura local.

Aquisição, build, criação de recursos, bootstrap/start PG, banco/papéis, migrations/concessões,
carga, web, demonstrações, evidência ampliada, parada e descarte continuam gates próprios.
Não criar bancos/containers “para testar o isolamento” sob autorização P0. Nenhuma aprovação
administrativa, homologação ou ratificação DEC-15 resulta dessa validação inicial.
