# Validação estática e testes negativos

## Escopo seguro

Executados parsers AST/YAML/JSON, hashes, estrutura e testes de unidade em memória. Os testes
importam apenas `operar.py` e `contrato.py`, sem settings/Django. Subprocessos e rede são bloqueados
por mocks; chamadas de `main` em teste usam dependências simuladas e nenhuma operação externa.
Não há banco, temporário, Docker, serviço ou escrita de domínio. Uso de `-B` evita bytecode.

Comando realmente usado para os testes puros:

```powershell
backend/.venv/Scripts/python.exe -B doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/test_guardas_puras.py
```

O resultado estruturado final está em [evidencia-a1.json](evidencia-a1.json). Importar os dois
módulos de guarda para testes não equivale a executar o script operacional de provisionamento.
Nenhum comando Docker/Compose foi chamado. Resultados puros não comprovam comportamento de
engine, PostgreSQL, publicação, egress, autenticação, e-mail ou armazenamento.

## Casos cobertos em memória

- Docker sem autorização não chama subprocesso; ações bloqueadas não leem configuração.
- Autorização antiga, ação extra bloqueada, endpoint remoto e hash divergente são recusados.
- Inspeção autorizada pode dispensar digests/configuração de banco.
- Falhas de comunicação/permissão não se tornam ausência; inventário truncado/nulo/duplicado falha.
- Inventário válido vazio e nomes válidos são aceitos; metadata nula e recibo incompleto falham.
- Conjunto de hashes incompleto falha; política pendente não abre cursor.
- Gatilho esperado é aceito; alheio, desabilitado ou função alterada são recusados.
- Herança Docker é recusada; criação simulada chama apenas create, sem start/up/migrations/carga.

## Testes negativos adicionais propostos — não executados

| Guarda | Caso negativo | Resultado esperado / autorização necessária |
|---|---|---|
| Arquivos | Substituir bind/arquivo após preflight; junção Windows no cliente/config | Recusar antes da operação; ensaio local de arquivos exige destino temporário autorizado |
| Cliente | Credential helper, auths, pasta extra ou hash alterado | Recusa sem subprocesso; expandir testes puramente simulados |
| Banco | Nome/papel/major/marker errados; marcador extra | Recusa; PG exclusivamente sintético, somente após gates de banco |
| Proteções | UPDATE/DELETE concedidos; trigger errada com nome certo; função alterada | Recusa por privilégio/hash; montagem de estado inválido só em instalação descartável autorizada |
| Recursos | Volume remoto, options bind, socket, mount ausente/extra, rede/porta inesperada | Recusa; primeiro metadata simulada, depois inspeção de recursos novos autorizados |
| Concorrência | Nome ocupado entre inventário e create; recurso substituído após conferência | Interromper/preservar; validar exclusividade e procedimento, não alegar lock técnico existente |
| Falha parcial | Compose create ou run falha após criar parte dos recursos; escrita de recibo falha | Estado não é sucesso, sem repetição/remoção; inventário e recuperação aprovados separadamente |
| Read-only | Tentar INSERT em transação de conferência | PG deve negar; teste com escrita tentada depende de autorização específica em banco sintético |
| Sessão | Tentar iniciar por ação antiga ou launcher | Bloqueado; não ensaiar web enquanto política/protocolo pendentes |
| Carga/descarte | Solicitar baseline/esquema/descartar mesmo em autorização local | Bloqueado antes de Docker; reabilitar exige revisão aprovada, não só editar ações |
| Build | Tag solta, base ausente, fonte de pacote inesperada, pedido de credencial | Não iniciar ou interromper; nenhum build autorizado nesta etapa |

Os casos operacionais acima são propostas, não resultados. Nenhuma falha autoriza bypass,
alteração de regra funcional, exclusão, execução com privilégios maiores ou uso de dados reais.
