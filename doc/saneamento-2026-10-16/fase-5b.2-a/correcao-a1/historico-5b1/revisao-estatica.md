# Relatório de revisão estática — Fase 5B.1

Data: 16/10/2026. **ARTEFATOS PREPARADOS; PROVISIONAMENTO NÃO AUTORIZADO.**

## Arquivos criados e modificados

Criados exclusivamente nesta pasta (15 arquivos):

- `compose.homologacao.yaml`.
- `homologacao.env.example`.
- `operar.py`.
- `isolamento/contrato.py`.
- `isolamento/settings_homologacao.py`.
- `isolamento/iniciar_aplicacao.py`.
- `isolamento/tarefas.py`.
- `baseline.json`.
- `cenarios.json`.
- `autorizacao.example.json`.
- `integridade.json`.
- `revisao-estatica.json`.
- `README.md`.
- `procedimentos.md`.
- `revisao-estatica.md` (este relatório).

Arquivos existentes modificados: **nenhum**. O Compose/Dockerfile/entrypoint, settings e código
funcional existentes não foram alterados. Os settings novos são somente do laboratório, montados
por arquivo independente, sem modificar importação/configuração das execuções existentes.

## Verificações realmente executadas

| Verificação estática | Resultado | Limite da evidência |
|---|---|---|
| Parser AST nos cinco arquivos Python novos | Sintaxe válida | Não importa módulos, não executa funções ou prova comportamento |
| Parser YAML e asserções estruturais | Três serviços com profiles, sem env_file/build/depends_on, rede interna, app loopback e banco sem porta | Não é validação de runtime/Compose instalado; interpolação de imagens permanece pendente |
| JSONs e 14 receitas únicas | Parse e cobertura dos IDs consistentes | Receitas manuais, não execução ou baseline produzida |
| Exemplo de autorização | Lista de ações/cenários vazia | Não há autorização operacional concedida |
| SHA-256 de dez artefatos técnicos | Registrados em `integridade.json` | Detecta alteração relativa à versão revisada; não é assinatura digital ou prova de procedência de imagem |
| Links locais e espaços finais | Conferidos antes da entrega | Não verifica disponibilidade de serviço externo nem âncora de documentação |
| `git diff --name-only`, `git diff --check`, HEAD/status | Nenhum arquivo rastreado modificado; HEAD `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`; pasta de saneamento continua não commitada | Não substitui controle institucional de versões; nenhum commit autorizado |

[Resultado estruturado](revisao-estatica.json), revisão 3. A primeira análise identificou problema
de aspas YAML no tmpfs durante a preparação; foi corrigido e o parsing repetido. Não houve
tentativa de iniciar Docker para verificar. Scripts novos **não foram executados**, nem `validar`;
somente AST, parse de dados e asserções externas sobre a estrutura dos arquivos.

## Controles preparados

- Configuração de seleção explícita e fechada; host/banco/role e settings próprios; `.env` da
  imagem recusado e arquivo independente restrito ao laboratório, sem herança de HOM_* do shell.
- Digests obrigatórios e `pull_policy: never`; exemplo não executável até escolha de imagem.
- Rótulos UUID/finalidade/projeto mais recibos de IDs/engine/volumes; recusa de nomes ocupados.
- Conferência de rede, mounts, driver/opções de volume e portas, sem imprimir Config.Env.
- App sem migration/seed/provisionamento, papel runtime e marker de banco administrado separado.
- Tarefas de esquema e baseline explícitas; carga reservada uma vez, preservando falha parcial.
- Console sem SMTP, assistente desligado, sorteio demonstrativo; dados exclusivamente fictícios.
- Contenção sem apagar; descarte só após parada, aprovação de ação e confirmação literal UUID/IDs,
  revalidando propriedade. Nenhum `down -v`, remoção recursiva de paths ou força.

## Riscos e dependências restantes

1. Não existe prova de isolamento em execução. A API de metadados Docker/Rancher pode representar
   paths Windows, volumes ou rede de forma diferente da prevista. Guardas devem recusar; eventual
   ajuste precisa de revisão, não de bypass. Criação parcial pode deixar recursos sem recibo completo;
   preservar e instruir incidente, sem repetição/limpeza automática.
2. Imagens e engine não selecionadas. App deve ter label de revisão, usuário/diretório corretos,
   dependências e nenhum `.env` real; labels precisam de evidência externa de build, não só declaração.
3. Roles/migrations/marker/triggers e execução em filesystem read-only não foram exercitados.
   Verificação de trigger habilitada e privilégio ausente é guarda inicial; sua semântica deve ser
   conferida em ensaio posterior, não certificada por esta análise.
4. Scripts de operação consultam metadados e executam estado persistente somente na fase futura.
   Ação `provisionar` inclui criação/start do PG e initdb no volume novo; `esquema` é outra ação.
   Containers de tarefa são preservados e registrados; sem `--rm` automático.
5. Configuração e autorização reais do laboratório ainda não existem. O exemplo só contém valores
   fictícios; não usar credenciais institucionais. Autorização JSON não é assinatura; operador com
   controle do host/daemon é fronteira de confiança. Recibos/hashes reduzem acidente, não fraude por admin.
6. Baseline inicial preparada, não gerada: parâmetros/relógio fixos não garantem bytes ou UUIDs
   iguais. Contagens e cobertura ainda precisam de revisão/ensaio. Negativos são receitas manuais
   auditáveis; não existe executor completo que realize todos os cenários automaticamente.
7. Tempo fixo pode tornar janelas impróprias para sessão futura; revisar manifesto antes da carga,
   sem modificar critério retroativamente. Seed pode falhar depois de gravar parte dos atos;
   reserva bloqueia repetição e nenhum dado é apagado para reparar.
8. Coleta automática limita-se a recibos/hashes. Saída de comandos é capturada sem anexar logs
   integrais para evitar exposição; capturas, trilha de domínio e resultados de cenário são
   evidências adicionais sob custódia aprovada. Console contém OTP sintético e precisa de acesso restrito.
9. Descarte pode ser parcialmente concluído se Docker recusar recurso em uso; não forçar.
   Preservar remanescentes, inventariar e pedir nova decisão. Restauração em recurso novo e suíte
   persistente/limpeza de banco de teste não estão implementadas como atalhos neste operador.
10. Protocolo, pessoas, decisões institucionais e mérito .01/.06/.07/.15 permanecem pendentes.
    Nenhuma imagem, script, teste ou geração futura ratifica regra administrativa.

## Próximas autorizações

Ver [procedimentos](procedimentos.md): inspeção local de metadados e seleção de imagens; criação
de configuração/autorização independentes; aquisição/build; `provisionar`; `esquema`; `conferir`;
`baseline`; `iniciar`; `demonstrar` por subcaso; `evidencias`; `preservar`/`encerrar`; e somente
depois eventual `descartar`. Cada uma deve nomear engine, manifesto/hashes, responsável, alvo,
operações e limites. Não se presume aprovação de todo o conjunto por aceitar esta revisão.

**FASE 5B.1 — ARTEFATOS DE ISOLAMENTO PREPARADOS; PROVISIONAMENTO NÃO AUTORIZADO.**
