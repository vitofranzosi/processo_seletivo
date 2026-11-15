# Verificação: A habilitação do assistente do Edital pela interface

## A suíte (14/11/2026)

`make lint check test-pg`, com os grupos `assistente` e `navegador` instalados: **20435 passando, 12
pulados e 1 falha**. A falha era um falso positivo do guardião da `164`
(`tests/test_leitores_da_consequencia.py`), que procura a grafia feminina em maiúsculas da
consequência do Resultado: a situação do assistente na trilha usava a mesma grafia. Ela passou a
ser `HABILITADO`/`DESABILITADO`, e o guardião, os testes da feature, a trilha e o percurso no
navegador passaram de novo (61 casos). A provisão confere **66 de 66** tabelas append-only.

## A demonstração com o serviço real (SC-2457)

Feita pelo agente em 14/11, na entrada `habilitacao-do-assistente-170` (configurações de
desenvolvimento, seletor desligado, provedor de homologação, OpenRouter com o limite de gasto da
chave), **sem nenhuma chave de demonstração**. Perguntas sintéticas, sobre conteúdo publicado.

| Passo | O que se viu |
|---|---|
| 1 | A Administradora entrou pelo provedor de homologação; a página disse "Configuração completa", com a credencial só como "presente", sem chamar o modelo |
| 2 | Habilitou o piloto e a página pública do 91, cada um com motivo |
| 3 | A participante do piloto perguntou pela gestão e recebeu a resposta conferida do modelo |
| 4 | Na página pública do 91, sem login na gestão, a pergunta livre foi respondida pelo modelo; a página do 92, numa aba sem sessão, não ofereceu o assistente |
| 5 | A Administradora desabilitou o 91 e o piloto; o 91 deixou de oferecer o painel, a pergunta enviada depois recebeu a recusa, e a página do aviso disse que o assistente foi encerrado |

No banco: **duas** trocas chamaram o serviço, cada uma antes da desabilitação da sua frente, e
nenhuma depois; os quatro atos estão no histórico com nome e motivo, e na trilha — o piloto no
escopo institucional, o 91 no `cefor`.

**Observado, e não defeito da feature.** Na aba em que a Administradora também tinha entrado, o
envio depois da desabilitação recebeu 404, e não o aviso: o navegador mandou o cookie de outra
sessão, porque não separa os cookies de `localhost` por porta nem por aba (a mesma armadilha que a
memória do projeto registra para a gestão). Com cada uma das sessões que conversaram, o servidor
redireciona para o aviso, conferido no próprio servidor; e o teste de navegador, com um contexto por
pessoa, prova o aviso de ponta a ponta. O quickstart manda usar janela anônima para o visitante.

## Produção

Coberta por teste, e não por demonstração: o ato que abriria a página pública é recusado,
nomeando `RA-1` a `RA-12`; o ato gravado num banco levado para produção não abre o painel; e a
inicialização recusa `ASSISTENTE_PILOTO`, serviço externo e tempo-limite acima de 110 s
(`tests/test_configuracao_producao.py`, `tests/integration/duvidas/test_habilitacao.py`,
`tests/portal/test_assistente_habilitado.py`).
