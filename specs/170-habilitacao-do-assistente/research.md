# Research: A habilitação do assistente do Edital pela interface

As decisões técnicas do plano. As decisões de produto estão na spec, de `D-001` a `D-008`. As daqui
são `R-1` a `R-10`, e cada uma diz o que foi escolhido, por quê, e o que se descartou.

## R-1 — Uma tabela no app `duvidas`

**Decisão.** A tabela `HabilitacaoDoAssistente` fica em `duvidas`, ao lado da `TrocaDoPiloto`.

**Por quê.** O assistente é desse app, e os leitores (a tela do piloto, o painel e o comando de
avaliação) já importam dele.

**Descartado.** Um app novo: seria uma estrutura paralela para uma tabela só. E a tabela de Unidades:
ela não é append-only, e a habilitação não é dado da unidade.

## R-2 — O estado é o último ato, pela ordem da frente

**Decisão.** A chave é UUID, e cada ato tem uma `ordem` dentro da sua frente — o piloto, ou a página
de um Edital —, alocada sob a trava (R-3) e única por frente, como a `ordem` da `TrocaDoPiloto`. O
estado é o ato de maior ordem.

**Por quê.** Os atos de uma frente são serializados pela trava, e por isso a ordem é a real.
Desempatar pelo instante pediria um segundo critério, que, aleatório, falharia no meio da suíte (a
limpeza dos casos transacionais desordena o heap). **A chave não é inteira** porque a trilha guarda o
agregado como UUID, e uma chave inteira viraria `UUID(int=pk)` em silêncio — o defeito que a `108`
registrou no aviso interrompido. *Revisto na implementação, em 14/11: o plano dizia chave
sequencial.*

**Descartado.** Uma tabela de estado ao lado do histórico: seriam duas fontes. E um campo
`vigente`: exigiria UPDATE, que a tabela append-only não admite.

## R-3 — A serialização por trava consultiva, e não por `FOR UPDATE`

**Decisão.** O ato toma `pg_advisory_xact_lock` com uma chave derivada da frente e do Edital, como a
administração institucional da `107` faz em `seguranca/application/acessos.py`. Sob a trava, ele
relê o último ato e recusa o ato que não muda nada (FR-7530, FR-7531).

**Por quê.** `SELECT ... FOR UPDATE` pede privilégio de UPDATE, que o runtime não tem na tabela
append-only. A suíte, que conecta como superusuário, não veria o erro, e o vigia
`sem_trava_em_append_only` do `tests/conftest.py` o recusaria.

## R-4 — Produção pela `AMBIENTE_DE_PRODUCAO`

**Decisão.** A regra da página pública lê `settings.AMBIENTE_DE_PRODUCAO`. O valor é `False` no
`base.py` e o literal `True` no `production.py`. A regra é aplicada no ato e a cada requisição
(FR-7518, FR-7519).

**Por quê.** É a configuração de ambiente que o projeto já usa no seletor de identidade, nos
cenários de treinamento, no `seed_demo` e na autenticação. Como é literal, nenhuma variável de
ambiente a desfaz.

**Descartado.** Uma variável nova, como `ASSISTENTE_ABERTURA_PUBLICA`: alguém poderia ligá-la em
produção.

## R-5 — A conversa nova pela marca da habilitação

**Decisão.** A chave da conversa na sessão passa de `edital_id` para `edital_id:marca`, em que a marca
é o identificador do ato de habilitação vigente, ou `demonstracao` com o atalho. O mesmo vale para o
teto de conversas da `074`. `conversa_da_sessao` recebe a marca como argumento.

**Por quê.** Uma habilitação nova muda a marca, e com ela a conversa: o histórico, que é lido pela
conversa (`historico_permitido`), começa vazio (FR-7525). Não há consulta nova nem coluna nova na
`TrocaDoPiloto`.

**Descartado.** Comparar o instante da primeira troca com o da habilitação: custa uma consulta por
envio, para chegar ao mesmo resultado.

## R-6 — A configuração completa, sem rede

**Decisão.** Uma função `configuracao_do_servico()` em `duvidas/infrastructure/inferencia` devolve
duas coisas: o que está completo, e a lista do que falta, em códigos. Ela confere o serviço
conhecido, o endereço, o modelo, o arquivo do tokenizer, a biblioteca `tokenizers` e a credencial do
OpenRouter. Não abre conexão.

**Por quê.** É a mesma condição que `conversar` e `tokens._tokenizer` já usam para os estados
`NAO_CONFIGURADO` e `SEM_TOKENIZER`, reunida num lugar que a página pode ler. O que a função vê é o
mesmo que a pergunta veria.

**Descartado.** Chamar `verificar_servico_de_inferencia` da página: faria chamada de rede, e a spec o
proíbe (FR-7502).

## R-7 — O `test.py` mantém o atalho ligado

**Decisão.** `ASSISTENTE_PILOTO = True` continua no `config/settings/test.py`. Os casos desta feature
o desligam por `settings`.

**Por quê.** É um atalho de demonstração fora de produção, e a suíte não é produção. Desligá-lo por
padrão obrigaria cada caso da `071` a gravar uma habilitação, sem ganho de cobertura. O SC-2455 pede
essas suítes sem mudança.

## R-8 — A trilha: o piloto no escopo institucional, o Edital no da unidade

**Decisão.** O evento da habilitação do piloto é gravado com o ator no escopo institucional. O do
Edital é gravado com o ator no escopo da unidade do Edital, pelo mesmo artifício da `110` (`Actor`
com o código da unidade e as mesmas permissões). As duas operações, `HABILITAR_ASSISTENTE` e
`DESABILITAR_ASSISTENTE`, ganham rótulo em `trilha_da_unidade.py`.

**Por quê.** É o que põe o ato sobre o Edital diante do auditor da unidade (FR-7529), sem mudar a
trilha da `108`.

## R-9 — O aviso de encerrado pelo redirecionamento

**Decisão.** Um envio para um Edital que não atende mais, de uma sessão que tinha conversa naquele
Edital, redireciona para a página da seleção com `?assistente=encerrado`. A página mostra o aviso só
quando o painel não é oferecido. Sem conversa na sessão, ou em produção, a resposta é 404, como na
`074`.

**Por quê.** Assim o visitante recebe a mensagem (UX-813), e quem nunca conversou continua sem saber
que a rota existe. Forjar o parâmetro só mostra um aviso verdadeiro, ou nenhum.

## R-10 — A página no molde de Unidades

**Decisão.** `interface/habilitacao_do_assistente.py` segue `interface/unidades.py`. O ator precisa
do escopo institucional com a permissão, e depois passa pela recusa da sessão de demonstração, as
duas antes de ler. A conferência só lê, e a confirmação chama o caso de uso. Os erros são
`DomainError` com código. O ícone da seção é um dos que o sprite já tem.

**Por quê.** É o padrão que o usuário pediu, e os guardiões de autorização, CSP e acessibilidade já o
conhecem.
