# Ações do operador e revisão das receitas

Inspeção estática de 16/10/2026. Nenhum comando abaixo foi executado. Fonte:
[operar.py](../fase-5b.1/operar.py), [tarefas.py](../fase-5b.1/isolamento/tarefas.py),
[baseline](../fase-5b.1/baseline.json) e [receitas](../fase-5b.1/cenarios.json).

## Comandos e efeitos reais

Na raiz do repositório, o comando exato de cada linha é o prefixo
`backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-5b.1/operar.py`
seguido dos argumentos da primeira coluna. São instruções futuras, não autorização.
Exceto `validar`, todas as ações consultam contexto Docker antes de validar a autorização.
Todas exigem configuração sintética válida; ações posteriores à inspeção exigem engine aprovada.

| Argumentos | Pré-condições adicionais | Recursos e leitura/escrita | Risco e interrupção | Evidência produzida / limite |
|---|---|---|---|---|
| `validar` | Arquivo independente preenchido, hashes íntegros | Leitura de arquivos; sem Docker | Configuração incorreta: recusar; não prova runtime | Mensagem de validação, sem recibo de execução |
| `inspecionar` | Ação expressamente aprovada; endpoint local | Leitura de contexto e engine | Endpoint remoto ou divergente: parar | ID da engine no terminal; não prova isolamento |
| `provisionar` | Imagens locais aprovadas; nomes livres; sem recibo anterior | Cria containers, rede, volumes e recibo; inicia PG, inicializa cluster e banco | Erro de inspect, identidade divergente ou criação parcial: interromper e inventariar | Recibo de IDs; não comprova esquema nem prontidão |
| `esquema` | Recibo íntegro, banco iniciado e vazio; DDL explicitamente autorizado | Cria container de tarefa; provisiona papéis, migra, concede privilégios, cria marcador e controle | Tabelas existentes, falha ou proteção insuficiente: parar sem reparar | Container preservado e recibo; recibo não indica sucesso da tarefa |
| `conferir` | Esquema existente; tarefa ainda não registrada | Cria container e recibo; leitura do banco e plano de migrations | Falha de guarda: parar; não repetir automaticamente | Resultado interno capturado pelo subprocesso; recibo não contém verificações detalhadas |
| `baseline` | Contagens, relógio e carga aprovados; sem Processo nem reserva anterior | Cria tarefa/recibo; INSERT de reserva, comandos de domínio, atos, trilha e arquivos | Falha parcial não tem rollback global; teto não demonstrado: não iniciar | Saída do gerador não é persistida como relatório completo pelo operador |
| `iniciar` | Guardas do banco atendidas; serviço web aprovado | Inicia app; leituras de prontidão; solicitações posteriores podem escrever | Banco/identidade/proteção divergentes: recusar; não migrar automaticamente | Estado do container; sem prova de jornada ou autorização administrativa |
| `demonstrar --cenario P01-A` | App e subcaso aprovados; responsável operacional | Lê recibos, imprime receita e URL; não executa nem restringe jornada | Sessão permite outras ações web; interromper desvio | Texto da receita; nenhuma evidência de demonstração concluída |
| `evidencias` | Destino e custódia aprovados; arquivo ainda ausente | Grava `evidencia-recursos.json` com hashes/recibo | Destino ocupado ou identidade divergente: recusar | Metadados de recursos; não contém resultado dos cenários |
| `preservar` | Contenção aprovada | Para app; mantém PG e volumes | Não equivale a desligamento completo; falha: inventariar | Sem recibo específico do resultado |
| `encerrar` | Parada de todos os IDs registrados aprovada | Para containers do recibo, inclusive tarefas | Pode interromper operações; identidade divergente: recusar | Recursos preservados; sem relatório de parada dedicado |
| `descartar` | Aprovação própria, custódia decidida, todos parados e confirmação literal de UUID/IDs | Remove containers por ID, rede por ID e volumes por nome após revalidação | Concorrência e remoção parcial; interromper sem força nem ampliação de alvos | Recibos permanecem; não há recuperação automática de descarte parcial |

Para os outros treze subcasos, substituir apenas `P01-A` por um ID da tabela abaixo, sempre
mediante aprovação individual. Não executar Compose diretamente para contornar o operador.

## Autorizações e efeitos indiretos

A lista de ações impede selecionar outra ramificação pelo argumento, mas não constitui controle
de acesso à aplicação nem separação de credenciais por tarefa. `provisionar` inclui start/initdb;
`conferir` não é integralmente leitura de infraestrutura; todas as tarefas recebem segredos de
administração/migration, inclusive as que não precisam deles. `iniciar` disponibiliza a aplicação
inteira e o seletor de identidade de demonstração. Autorizar `demonstrar` não limita as URLs,
atores ou comandos acessíveis pela sessão web. A autorização é um arquivo local, sem assinatura
ou vínculo criptográfico com o aprovador: exige custódia e registro humano verificável.

Recomenda-se corrigir e revisar esses limites em etapa própria antes de autorizar execução.
Não há correção nesta fase. Evidência de autorização não substitui evidência de sucesso.

## Baseline

Há intenção de determinismo semântico: código, número 31/2026, argumentos e T0 fixos;
UUIDs, arquivos e bytes não são prometidos como determinísticos. O relógio é substituído apenas
durante o seed, enquanto a aplicação continuará usando a data real. Isso pode fechar janelas
antes da demonstração. A reprodução precisa fixar e aprovar a data de avaliação e comparar
saídas normalizadas em duas instalações novas, futuramente autorizadas.

O gerador usa comandos existentes e entradas fictícias, sem importar bases reais. Essa constatação
de fonte não comprova a população final. `seed_demo` prepara unidade/autoridades antes de verificar
Processo existente; a reserva anterior ao seed e a ausência de transação global tornam falhas
parciais relevantes. Limites de 20 Editais, 100 inscrições e 5000 eventos ainda não estão comprovados
nem impostos pelo gerador. O seed cria base navegável; não materializa automaticamente todas as
variantes. Não há runner automatizado das 14 receitas, nem manifesto completo de IDs de saída
produzido e capturado pelo operador.

## Cobertura e pré-condições das 14 receitas

Todos os dados, documentos e identidades devem ser sintéticos. Cada variante exige estado próprio,
IDs registrados e roteiro da Fase 4; nenhum resultado esperado abaixo é resultado observado.

| ID | Pré-condição / objetivo | Dependência e limite de cobertura |
|---|---|---|
| P01-A | Edital completo não publicado, único Evento cancelado; primeira publicação | Integração de validação e publicação; deve recusar sem ato |
| P01-B | Edital publicado, inscrições rascunho/enviada; cancelar por Retificação | Escrita de ato privado e tentativa de inscrição; verificar preservação histórica |
| P01-C | Evento cancelado e outro válido aberto; substituir designação | Calendário, vigência e novo envio; depende do relógio |
| P06-A | Snapshot anterior ao degrau 10 sem método | Elevação pode ser em memória; declaração posterior requer ambiente e ato |
| P06-B | Sorteio previsto, antes da realização, com/sem relação congelada | Comparar versão/hash; dois estados distintos, não uma única execução |
| P06-C | Classificação por pontos, com/sem ordem emitida | Registrar recusa/fronteira existente; não autoriza conversão administrativa |
| P07-A | Regra fictícia com fundamento incorreto | Retificar campos permitidos; conferir versões e vínculos |
| P07-B | Duas identidades fictícias; tentativa de alterar id | Recusa estrutural pode ser em memória; não demonstra substituição legítima aprovada |
| P15-A | Ator autorizado, sem população escolhida | GET e inventário de metadados/trilha; ausência de nominal não prova anonimização |
| P15-B | Relatório com lacunas agregadas | Comparar HTML/trilha; identificar possibilidade de identificação indireta |
| P15-C | Declaração fictícia de cor/raça incompatível com destino | Prévia nominal e evento; dado sensível exclusivamente sintético |
| P15-D | População incompleta/modalidade desconhecida | Recusa, mensagem e trilha; inventariar exposição por erros |
| P15-E | Prévia válida e requerimentos enviados, assinatura válida/obsoleta | POST, geração e recebimento separados; sem integração RA real |
| P15-F | Ator sem permissão e de outro escopo | GET/POST negados e ausência de arquivo; não conceder permissões para passar |

Os cenários exercitam as quatro pendências técnicas, mas não encerram consultas institucionais,
as 43 condições ou homologação humana. Variantes temporais e subcasos precisam de inventário
prévio próprio. Nunca transformar o resultado esperado em regra nova para fazer um caso passar.

## Recuperação e evidências futuras

Não limpar tabelas, reexecutar seed, trocar IDs ou apagar recibos para recuperar falhas.
Preservar estado, saída sanitizada, exit code, horário, IDs e dificuldade observada. Recuperação
deverá usar novo ambiente com identidade e autorização próprias, ou procedimento revisado aprovado.
O descarte é separado e permanece proibido nesta fase. Coletar resultados por subcaso, sem dumps
ou logs integrais que exponham credenciais, e distinguir visualização, geração e download.
