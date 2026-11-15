# Quanto dos estados da Ocupação a suíte já monta

Levantamento de 14/11/2026, pedido pelo segundo parecer antes de decidir se a Ocupação de vagas
fica no piloto ([decisão 2](05-roadmap.md#decisões-que-ficam-com-o-usuário)). Nada no produto nem
na suíte foi alterado.

## Resposta curta

**A suíte já desenha 51 dos 63 ramos visíveis da tela**, em 54 testes de 13 arquivos. Todos os
estados que o plano listava para o piloto têm teste de tela que os monta, com duas ressalvas: a
apuração obsoleta só é desenhada por uma das sete causas, e o recorte sem quadro só para quem não
retifica. Dos 12 ramos que nenhum teste desenha, 7 já são montados em teste de domínio, sem
passar pela tela.

O levantamento também corrige o plano em dois pontos: a tela tem **sete** formulários, e não
cinco, e a lista de estados deixava de fora o bloco da vaga sem quem a ocupe, da `155`.

O custo que sobra não é montar cenário. É **fotografar** os estados: as fixtures vivem no banco de
teste, que some no fim de cada caso, e os cenários de treinamento só chegam a um estado da tela.

## Como foi medido

Um plugin temporário do pytest envolve `Template.render` e grava, a cada desenho de
`interface/ocupacao.html`, quais trechos literais de cada ramo do template estão no HTML, por
recorte. A suíte inteira rodou uma vez com ele, contra PostgreSQL, 4 workers, sobre `48ed1ddc`:
**19 865 passando, 13 pulados, 638 s**. Uma segunda passada, só nos 13 arquivos, acrescentou o
número "A ocupar" de cada recorte.

| Arquivo | O que faz |
|---|---|
| [`medicoes/registro_da_ocupacao.py`](medicoes/registro_da_ocupacao.py) | o plugin, com a tabela ramo → trecho |
| [`medicoes/registro_da_ocupacao_v2.py`](medicoes/registro_da_ocupacao_v2.py) | a segunda passada |
| [`medicoes/agregar_ocupacao.py`](medicoes/agregar_ocupacao.py) | conta testes e arquivos por ramo |

Para repetir, de `backend/`, com as variáveis do `make test-pg`:

```bash
PYTHONPATH=../doc/auditoria-design-system-2026-11-14/medicoes REGISTRO_DA_OCUPACAO=/tmp/registro uv run pytest -p registro_da_ocupacao -n 4 --dist worksteal -q
```

**O que a medida diz, e o que não diz.** Ela conta teste que **desenha** o ramo, e não teste que o
confere: um estado pode aparecer no HTML sem que nenhum `assert` olhe para ele. Não diz nada sobre
aparência. E o ramo é reconhecido por um trecho literal do template; se o texto mudar, a tabela do
plugin muda junto.

## De onde vêm os cenários

| Fixture | Onde | O que monta |
|---|---|---|
| `rascunho_com_quadro`, `montar_cenario_da_ocupacao` | `tests/fixtures/ocupacao.py` (121 linhas) | Edital publicado com quadro, ordem e corte emitidos. Parâmetros: vagas da linha geral, cota, espécie de reversão, regra de corte, cadastro de reserva, documentos |
| `certame_sorteado_com_quadro` | `tests/fixtures/ocupacao_sorteada.py` (233 linhas) | o mesmo, com sorteio |
| `cenario` | `tests/interface/conftest.py` | o cenário padrão das telas |
| `com_continuacao`, `sem_regra_de_corte` | `tests/interface/test_ocupacao.py` | Edital que admite faixa seguinte; marco sem corte |
| `reserva` | `tests/interface/test_acrescimo.py` | Perfil com cadastro de reserva, que aceita acréscimo |
| `silente`, `reversao_que_nao_sai`, `prazo_encerrado` | `tests/interface/test_destinacao_na_ocupacao.py` | a vaga sem quem a ocupe, nos casos da `155` |

Os 54 testes se concentram em três arquivos: `test_ocupacao.py` (21), `test_destinacao_na_ocupacao.py`
(10) e `test_acrescimo.py` (6). Os outros dez arquivos somam 17.

## Os estados que o plano listava

Número de testes que desenham cada um.

| Estado, por recorte | Testes | Observação |
|---|---:|---|
| Sem quadro de vagas | 1 | só para quem não retifica; a variante com o link da Retificação, nenhum |
| Não apurado, com ordem (botão de apurar) | 29 | |
| Não apurado, sem ordem (a razão no lugar do botão) | 20 | |
| Recorte sem inscrito | 5 | |
| Apurado, com vaga a ocupar | 25 | 11 para quem emite, 14 para quem só lê |
| Apurado, sem vaga a ocupar | 13 | 12 para quem emite, 1 para quem só lê |
| Apuração obsoleta, com a sucessão aberta | 1 | pela causa "efeito posterior"; as outras seis causas, nenhum |
| Com vagas acrescidas | 4 | a lista, o acréscimo e o desfazimento nela |
| Com movimento de vaga entre recortes | 1 | a reversão de cota |
| Quem pode emitir | 34 | |
| Quem só lê | 25 | 5 com a frase de a quem pedir |

| Retorno de cada gesto | Recusa | Sucesso |
|---|---:|---:|
| Apurar ou pedir a faixa seguinte (a frase da recusa é a mesma) | 2 | 4 (apuração) e 1 (faixa) |
| Acrescentar vaga | 1 | 3 |
| Desfazer o acréscimo | 1 | 1 |
| Declarar a vaga não preenchida | 1 | 3 |
| Desfazer a declaração | 1 | 1 |

## O que o plano não listava, e a tela tem

- **Sete formulários, e não cinco.** Os dois que faltavam estão na parcial
  `_situacao_da_vaga.html`, da `155`: declarar a vaga não preenchida e desfazer a declaração.
- **O bloco da vaga sem quem a ocupe.** A frase da situação (14 testes), o Edital silente com os
  dois caminhos (3), a declaração na lista (3), a que não se desfaz por ter chamada dependente (1)
  e a frase para quem não apura (1).
- **O marco intermediário**, que não apura e aponta o marco que apura (2).
- **O próximo passo depois de um ato**: "Próximo nesta lista" (10), "Ainda neste marco" (4) e o
  retorno ao Centro (10).
- **Duas telas de conferência** recebem os atos e são templates próprios:
  `ocupacao_acrescimo.html` (7 testes, 1 com recusa) e `ocupacao_nao_preenchida.html` (4, 1 com
  recusa). O plano não diz se entram no piloto; é ponto para a spec.

## Os 12 ramos que nenhum teste desenha

| Ramo | Já é montado fora da tela? | Leitura do custo |
|---|---|---|
| Obsoleta por ordem sucedida | sim, `tests/integration/ocupacao/test_obsolescencia.py` | abrir a tela no fim do mesmo cenário |
| Obsoleta por movimento posterior | sim, o mesmo arquivo | idem |
| Obsoleta por corte que mudou | sim, o mesmo arquivo | idem |
| Obsoleta por acréscimo posterior | sim, `tests/integration/ocupacao/test_acrescimo.py` | idem |
| Obsoleta por declaração posterior | sim, `tests/integration/ocupacao/test_nao_preenchida.py` | idem |
| Obsoleta por quadro retificado | não achei teste que a monte por Retificação | Retificação do quadro depois da apuração |
| Sucesso com a apuração seguinte pendente | sim, `test_com_outra_causa_presente_grava_e_nao_emite`, no `test_acrescimo.py` de integração | repetir o cenário pela tela |
| Acréscimo recusado fora da linha geral | sim, a recusa, em unidade e integração | Perfil com reserva e cota; `rascunho_com_quadro` tem os dois parâmetros |
| Acréscimo com processo administrativo | não | preencher o campo opcional do formulário |
| Sem quadro, para quem retifica | não | o cenário existente, com outro papel |
| "Nada mais em aberto nesta lista" | não; nenhum teste cita a frase | depende de achar a lista sem pendência |
| Nota do cadastro legado | só em unidade, sobre um dicionário | o mais caro: nenhum Edital da suíte nasce com o número digitado de antes da `162` |

A coluna do custo é leitura minha do código, e não medida.

## O custo que este levantamento não resolve

- **Fotografar não é o mesmo que montar.** A comparação do piloto precisa das telas em imagem, nas
  larguras do estudo. As fixtures rodam no banco de teste. O caminho que já existe é o de
  `tests/navegador/`, que sobe o `live_server` e grava capturas com `NAVEGADOR_CAPTURAS`; nenhuma
  jornada de lá passa pela Ocupação hoje.
- **Os cenários de treinamento chegam a um estado só.** O rastreio do estudo visitou a Ocupação uma
  vez, como `treino.presidencia`. A leitura com a equipe, que o aceite pede, precisa de mais do
  que isso num banco que a equipe abra.
- **As 25 combinações por recorte** que a suíte desenha não são todas as que a tela admite. O
  piloto precisa escolher quais fotografar, e isso é da spec.
