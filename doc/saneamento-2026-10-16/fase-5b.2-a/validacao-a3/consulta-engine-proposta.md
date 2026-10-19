# Consulta à engine — proposta para aprovação humana

Data: 19/10/2026. **Não executada. Aguarda autorização específica e confirmação das pré-condições.**

## 1. Comando exato proposto

Executar futuramente a partir de `D:\projetos\cefor\processo_seletivo`, uma única vez:

```powershell
backend/.venv/Scripts/python.exe -B doc/saneamento-2026-10-16/fase-5b.1/operar.py inspecionar
```

É o operador preservado da revisão **5B.2-A.2**, não um novo script A.3. Não substituir por
`conferir`, que cria/inicia container de tarefa, nem por Compose ou comando direto que ignore as guardas.

Chamada interna prevista, com campos ainda dependentes de confirmação humana:

```text
docker --config <pasta-exclusiva-aprovada> --host <endpoint-local-aprovado> info --format {{.ID}}
```

Essa segunda linha explica os argumentos montados pelo operador; não é um comando instanciado
adicional para executar. O endpoint não foi identificado nem inventado nesta análise.

## 2. Justificativa e fluxo inspecionado

Identificar o ID da engine local já ativa é pré-condição para vincular aprovações futuras ao
servidor correto. Não comprova isolamento de recursos ainda inexistentes nem compatibilidade da plataforma.

Em `operar.py:253`, `main` valida integridade e autorização; `autorizar:119` verifica revisão,
ação única/escopo, hashes, endpoint e cliente exclusivo. Só depois chama `docker:148` com `info`.
O ramo `inspecionar` imprime ID/UUID e retorna antes dos ramos de criação, tarefa, parada ou evidências.
`configuracao=None` evita leitura de `homologacao.env`; não há carregamento de `backend/.env` nesse fluxo.
Os módulos de contrato/política importados têm constantes e definições, sem inicialização de Django.

## 3. Pré-condições obrigatórias, ainda não satisfeitas

1. Aprovação humana expressa dessa única consulta, responsável e janela de execução.
2. Endpoint **exato**, confirmado pelo responsável como local e associado a engine já ativa,
   sem mecanismo de ativação automática necessário à consulta. Apenas começar com `npipe://`
   ou `unix://` não é prova suficiente: a guarda atual só verifica esse prefixo.
3. Binário Docker confiável identificado por caminho e hash, resolvido pelo PATH que o subprocesso
   usará; não executar versão/diagnóstico Docker adicional para descobri-lo sem autorização.
4. Preparação expressamente autorizada de
   `doc/saneamento-2026-10-16/fase-5b.1/docker-cliente/config.json`, único arquivo nessa pasta,
   conteúdo `{}`, sem atalhos/junções, credenciais, helpers ou contexto herdado. Não criado agora.
5. Preparação expressamente autorizada de `fase-5b.1/autorizacao.json` com identidade
   `5dadcc37-7015-4a5a-b1a1-727dd7e3d901`, revisão `5B.2-A.2`, aprovador, referência,
   endpoint e hashes atuais do Compose/integridade/cliente. Ação e escopo devem ser exatamente:

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

Esse fragmento é incompleto e não autoriza nada. ID da engine não pode ser preenchido por suposição;
o ramo de inspeção serve para descobri-lo. O código simbólico de recurso não substitui o endpoint real.

6. Ausência de DOCKER_HOST/CONTEXT/TLS_VERIFY/CONFIG e COMPOSE_FILE conflitantes; o operador recusa
   essas variáveis e fornece ambiente reduzido ao subprocesso. Não imprimir valores secretos.
7. Artefatos idênticos aos hashes revisados, cliente mínimo e ausência de interferência concorrente
   nos arquivos/binary/endpoint durante a consulta.
8. Custodiante, destino novo para resultado sanitizado e prazo máximo de observação definidos.
   O subprocesso atual **não implementa timeout**; a aprovação deve aceitar supervisão/interrupção
   somente do cliente ou solicitar revisão estática própria antes de executar. Não parar a engine.

## 4. Efeitos esperados

Leitura dos arquivos de contrato/integridade/autorização/cliente e uma consulta de metadados à
engine. Saída esperada: JSON com `engine` não vazio e `identidade` do laboratório, exit code zero.
Nenhuma conexão SQL, listagem de candidatos, chamada a registry, pull, build, Compose ou alteração
de container/rede/volume/banco está presente no ramo selecionado.

O operador não grava recibo ou evidência nesse ramo. Salvar a saída sanitizada no destino aprovado
será uma gravação documental separadamente incluída na autorização futura, sem sobrescrever arquivos.

## 5. Efeitos indiretos e riscos

A execução cria processos Python/cliente e lê arquivos. A engine/SO podem registrar acesso,
métricas ou logs; não prometer ausência absoluta de escrita no host. A consulta de info pode
processar internamente mais metadata que o ID impresso. O perfil humano que acessa o daemon
pode ter poderes superiores aos da ação escolhida.

Endpoint em estado desconhecido, serviço com ativação por conexão ou binário substituído podem
invalidar as premissas. Esses estados não foram examinados operacionalmente; sem confirmação
positiva a consulta não deve ocorrer. Hashes/arquivo local de aprovação não são assinatura digital
nem barreira contra administrador do host. Não há controle de tempo automático no script atual.

## 6. Critérios de sucesso

Aprovação, endpoint, arquivos e binário conferidos; execução única do comando aprovado;
exit code zero; ID não vazio e diferente de `<no value>`; UUID esperado; registro de data,
responsável e resultado sanitizado. Sucesso significa **engine identificada por consulta de leitura**.
Não aprova plataforma, imagens, isolamento, criação de recursos ou regra administrativa.

## 7. Critérios de interrupção

Pré-condição ausente, hash divergente, autorização/cliente inválidos, endpoint não comprovado local,
daemon inativo, permissão negada, ausência de resposta no prazo pactuado, pedido de credencial,
ID/JSON ausente/inválido ou operação fora do escopo. Encerrar tentativa sem fallback, retry,
elevação, mudança de endpoint, inicialização de serviço ou reparo. Eventual interrupção deve
atingir só o cliente autorizado, não daemon, VM ou recursos existentes.

## 8. Evidências futuras

Referência da deliberação, responsável, janela/instante, comando, HEAD, hashes dos artefatos e do
binário/cliente, endpoint sanitizado, exit code, ID e UUID; falha com categoria sanitizada, sem
stderr bruto/stack trace, token, senha, env ou configuração completa. Caminho, hash e custódia
do registro novo. Não preencher resultado observado antes da execução.

## 9. Garantia e limite verificáveis

Por inspeção, o ramo não contém start/up/create/migrate/seed/remove e retorna antes dos outros
ramos. Não há fallback de inicialização no operador. Essa é a garantia **do comando sob as
pré-condições descritas**, não uma observação de estado da máquina. Não é possível garantir
somente com o relatório que endpoint/binário/serviço externos obedecerão às premissas.

Pedido para a próxima rodada: autorizar exclusivamente a consulta acima e os arquivos de controle/
registro enumerados, fornecendo endpoint local confirmado, responsável, janela, custódia e modo
de interrupção. Se desejar apenas aprovar o desenho, registrar isso sem autorização de execução.
