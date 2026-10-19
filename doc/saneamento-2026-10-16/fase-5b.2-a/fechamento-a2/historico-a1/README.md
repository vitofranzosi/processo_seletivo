# Fase 5B.1 — artefatos técnicos de isolamento

> **Adendo 5B.2-A.1 (16/10/2026):** os artefatos técnicos desta pasta foram revisados.
> O texto abaixo registra o desenho original, não o procedimento vigente. `provisionar`,
> inicialização PG/web, esquema, baseline, demonstração e descarte estão bloqueados.
> A criação futura é `criar-recursos`, sem start. Consultar a
> [revisão vigente e matriz de correções](../fase-5b.2-a/correcao-a1/README.md).
> O conteúdo original foi preservado em cópia com hashes; nenhuma execução operacional foi autorizada.

**FASE 5B.1 — ARTEFATOS DE ISOLAMENTO PREPARADOS; PROVISIONAMENTO NÃO AUTORIZADO.**

Data: 16/10/2026. Fonte funcional prevista:
`6fc3a85a9ce58a973dc0e29bc38085dfd055f171`. Configurações existentes preservadas.

## Artefatos

- [Compose independente](compose.homologacao.yaml), sem `env_file`, `build`, entrypoint de
  desenvolvimento ou banco externo; serviços sob profiles explícitos.
- [Exemplo sintético](homologacao.env.example), sem credenciais copiadas. Digests estão
  deliberadamente não definidos: a validação futura recusará esse exemplo como ambiente pronto.
- [Contrato de isolamento](isolamento/contrato.py), [settings exclusivos](isolamento/settings_homologacao.py),
  [inicialização web](isolamento/iniciar_aplicacao.py) e [tarefas explícitas](isolamento/tarefas.py).
- [Operador com gates](operar.py), [exemplo de autorização vazia](autorizacao.example.json) e
  `integridade.json` com hashes dos artefatos técnicos revisados.
- [Baseline parametrizada](baseline.json), [14 receitas complementares](cenarios.json), gerador explícito e variantes referidas
  ao [plano F4](../fase-4/plano-demonstracoes.md).
- [Procedimentos e autorizações 5B.2](procedimentos.md) e [revisão estática](revisao-estatica.md).

## Seleção e falha segura

Só `HOMOLOGACAO_SELECIONADA=SIM`, ID fixo do laboratório, settings exclusivos e conexão interna
são aceitos. Os scripts não leem `backend/.env`; o operador aceita somente o arquivo novo
`homologacao.env` nesta pasta, recusa atalhos/junções e variáveis herdadas conflitantes.
O subprocesso Docker recebe ambiente mínimo e o manifesto explicitamente nomeado, sem defaults
de Compose. Daemon deve ser local e ter ID aprovado; não basta ter nome “homologação”.

Rótulos de identidade/finalidade/projeto, IDs de containers/rede, data de criação e driver/opções
dos volumes, mounts, rede e portas são comparados com recibo exclusivo. Recursos preexistentes
não são adotados. Banco possui marcador administrado fora do schema funcional, papel runtime
sem alteração desse marcador; app confere marcador, destino, privilégios, triggers e migrations
pendentes antes de servir. Essa implementação **ainda não foi exercitada em Docker/PostgreSQL**.

O console de e-mail não tem transporte SMTP; OTPs fictícios ficam em log local de acesso restrito.
Não é experiência completa com coletor visual. Assistente e integrações estão desligados; fonte
de sorteio é de demonstração. Rede interna é barreira adicional, a verificar efetivamente em 5B.2.

## Limites importantes

Inicializar a web não chama provisão, migration, sincronização ou seed. A ação **provisionar**,
se futuramente autorizada, cria containers/volumes e inicia PostgreSQL: sua imagem oficial
inicializa cluster e banco novos no volume vazio. Essa escrita é parte expressa daquela ação,
não uma consequência escondida de iniciar app. A tarefa **esquema** é outro gate.

Gerador `baseline` fixa parâmetros e relógio, reserva execução e usa `seed_demo` sem alterar regras.
Reprodutibilidade é semântica, não promessa de bytes/UUIDs iguais. Cobertura e quantidade produzida
precisam ser verificadas antes de considerar a baseline homologada. Casos negativos e variações
P01/P06/P07/P15 são receitas manuais do roteiro, não um executor automático completo criado aqui.
A ação `demonstrar` somente verifica autorização e libera instrução de sessão manual; não simula
aceite nem executa atos no lugar do usuário. Substituição legítima .07 continua sem mecanismo aprovado.

O arquivo de autorização é registro operacional de deliberação humana externa, não assinatura
digital. Administrador que pode alterar arquivos/daemon permanece fronteira de confiança. Hashes
e rótulos previnem acidentes; não são prova criptográfica de independência de administrador host.

## Estado atual

Somente arquivos desta pasta foram criados. Nenhum script preparado foi executado, nem mesmo seu
modo `validar`. Revisão usou parsers AST/YAML/JSON e leitura de fontes, sem importar os módulos
novos, carregar settings, acessar daemon/banco ou executar código de baseline. Sem testes
persistentes, serviços, migrations, carga, demonstração, e-mail, commit, push ou merge.

Referências Fase 5A consultadas: [inventário](../fase-5a/inventario-tecnico.md),
[isolamento](../fase-5a/isolamento.md), [baseline](../fase-5a/baseline-planejada.md),
[responsáveis](../fase-5a/responsabilidades.md), [plano](../fase-5a/plano-5b-e-autorizacao.md),
[43 condições](../fase-5a/evidencias-43-condicoes.md). A autorização atual cobre G1, não G2 em diante.
