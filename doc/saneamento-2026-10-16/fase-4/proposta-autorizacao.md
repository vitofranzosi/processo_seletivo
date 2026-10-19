# Proposta de autorização operacional específica — ainda não concedida

Versão 1, 16/10/2026. Escopo proposto: [cenários P01/P06/P07/P15](plano-demonstracoes.md).
Não constitui autorização atual. Nenhum recurso abaixo foi criado, iniciado ou inspecionado em
execução nesta Fase 4. Nomes e endereços são **destinos exatos propostos**, não infraestrutura confirmada.

## Ambiente proposto e manifesto obrigatório

| Recurso | Identificação proposta / limite |
|---|---|
| Host | Máquina Windows do workspace `D:\projetos\cefor\processo_seletivo`, sem serviço público |
| Código | Commit `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`, fonte somente leitura durante execução; sem incorporar alterações da main local |
| Projeto isolado | `cefor_homologacao_f4_20261016` |
| Serviço de aplicação | `cefor-f4-app-20261016`; URL somente `http://127.0.0.1:18084` |
| PostgreSQL | Serviço `cefor-f4-pg-20261016`, porta interna 5432, **sem porta de banco publicada no host**; PostgreSQL 18 |
| Banco | `ps_homologacao_f4_20261016`, não `processo_seletivo`, `ps_filme` ou `ps_video` |
| Acesso de aplicação | Role restrita `ps_f4_runtime`, papéis/proteções já provisionados na baseline; sem contornar imutabilidade |
| Rede | `cefor-f4-rede-20261016`, interna, sem saída para provedores; somente app ↔ banco e acesso local aprovado |
| Volume PostgreSQL | `cefor_f4_pg_20261016`, exclusivo, sem ligação a volume de desenvolvimento |
| Mídia | Volume exclusivo `cefor_f4_midia_20261016`; nenhuma montagem de mídia real |
| Evidência/downloads | `D:\projetos\cefor\processo_seletivo\doc\saneamento-2026-10-16\fase-4\evidencias-futuras\execucao-01`, a criar somente após autorização; não sobrescrever pasta existente |
| Dataset | `f4-sintetico-v1`, com manifesto e hash, somente identidades/documentos fictícios; namespace “HOMOLOGAÇÃO — SEM VALOR OFICIAL” |
| Relógio | Instante T0 registrado; fuso de apresentação America/Sao_Paulo; janelas sintéticas relativas, sem alterar relógio do host |

**Antes de autorização executável**, confirmar no manifesto: responsável nominal, disponibilidade
da porta/nomes, imagens de aplicação/PostgreSQL com digests imutáveis, versão de dependências,
origem/hash da baseline **exclusivamente sintética e já com esquema**, caminhos reais dos volumes,
triggers/privilégios, política de rede, ausência de conectores externos e plano de guarda de evidências.
Não foram inventados digests ou uma baseline inexistente para completar o formulário.

Se recursos/porta já existirem, não reutilizar por suposição, parar ou substituir. Submeter variante
identificada ao usuário. Não usar `.env` ou dump do desenvolvimento como configuração/baseline.
Credenciais sintéticas só por canal operacional seguro, nunca na evidência ou comando impresso.

**Impedimento atual:** ambiente e baseline não foram confirmados. Aprovar o texto do plano não
autoriza criar esquema, migrations, restaurar dump ou provisionar roles. Se isso for necessário,
preparar autorização de preparação separada com alvo e operações, antes de qualquer comando.

## Escopo a selecionar na autorização humana

| Bloco | Operações que a autorização futura deverá nomear | Exclusões |
|---|---|---|
| M — memória | Ler fixtures e aplicar conteúdo sintético em memória para P01/P06-A/P07; salvar evidência nova | Sem acesso de banco/rede; não equivalente a homologação |
| B01 — período | Leituras, tentativas de publicação, Retificações sintéticas, rascunhos/envios sintéticos e leitura da trilha para P01-A/B/C | Sem cancelar ato real, mudar regra ou reabrir certame real |
| B06 — sorteio | Retificações, relação congelada sintética e tentativa de ordenação/conversão pelos comandos existentes, por subcaso aprovado | Sem fonte externa; sem forçar sucesso; nenhuma conversão administrativa real ratificada |
| B07 — identidade | Retificação de campos permitidos e tentativa recusada de ID; leitura de snapshots/vínculos | Sem mecanismo novo ou substituição legítima ainda não decidida; sem SQL para trocar ID |
| B15 — exportação | GET que pode gerar auditoria, POST de geração e download local sintético, testes de negação e escopo | Sem conceder papel real, exportar dado real, importar no RA ou criar novo log no produto |

Atos sintéticos são registros privados de ensaio, sem valor oficial; não publicar em portal real
ou anunciar como atos do Cefor. Não homologar modelo ainda não ratificado por sucesso técnico.

Limites propostos para aprovação: uma execução identificada, até 20 Editais sintéticos e 100
inscrições sintéticas no conjunto; até 5000 registros de trilha novos, com contagem antes/depois.
São teto de contenção, não estimativa exata ou critério funcional. Ao atingir limite, pausar e
apresentar necessidade antes de ampliar. Não apagar dados para caber no orçamento.

## Evidências previstas

Manifesto de ambiente/dataset, hashes do código/artefatos, ficha por cenário, respostas sanitizadas,
capturas do produto, IDs/versões/atos antes/depois, eventos de auditoria, arquivo sintético com
hash e distinção entre geração/resposta/recebimento. Sem credenciais, cookies, tokens de sessão,
declarações reais ou logs integrais desnecessários. Gravar participantes somente por autorização
específica do protocolo; ensaio técnico pode ocorrer sem pessoas externas e sem gravação pessoal.

## Riscos, interrupção e recuperação

- Destino errado, volume compartilhado ou dado real: parar imediatamente sem tentar “sanear” apagando.
- Saída de e-mail, inferência, fonte externa, URL pública ou qualquer custo externo: não prosseguir.
- Trigger/privilégio ausente, erro que ameaça integridade, comando inesperado ou divergência do
  commit/manifesto: pausar e registrar, sem bypass ou alteração de código.
- Resultado inesperado, crescimento de dados fora do limite ou contexto administrativo não
  decidido: encerrar o subcaso e pedir deliberação, não improvisar regra.

Recuperação permitida somente se explicitamente incluída na autorização futura: parar aplicação
isolada, manter banco/volumes/evidências restritos e registrar último estado. Sem `down -v`, drop,
truncate, reset, exclusão, restauração sobre banco existente ou rollback de ato normativo.
Baseline para nova tentativa deve ser recurso novo e autorizado. Descarte de ambiente é autorização
posterior separada; preservação é o padrão até decisão humana de guarda/destinação.

## Modelo de concessão a preencher pelo usuário

“Autorizo a execução **[identificador]**, no manifesto **[versão/hash confirmado]**, sob responsabilidade
de **[nome/função]**, somente para blocos **[M/B01/B06/B07/B15 e subcasos]**, com as escritas sintéticas,
limites, evidências e interrupções descritas. **[Autorizações específicas adicionais ou nenhuma]**.
Não autorizo migrations, dados reais, serviços pagos, envio externo, exclusão, alterações funcionais,
specs, commits, push, merge ou aplicação administrativa real. Guarda/destinação: **[definir]**.”

Campos não preenchidos não são autorização. É possível aprovar primeiro apenas o plano/protocolo
ou subconjunto de cenários, mantendo os demais pendentes. Depois da execução, a aceitação dos
resultados e a ratificação das regras continuam deliberações próprias.
