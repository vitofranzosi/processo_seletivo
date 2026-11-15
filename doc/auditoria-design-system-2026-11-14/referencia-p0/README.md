# A referência do piloto, tirada depois da P0

*14/11/2026, sobre a branch da P0 (as correções em `d7211e90`). É contra esta referência, e não
contra o `medicoes/telas.csv` de 14/11 sobre `37ed0ad0`, que o piloto se compara: o critério 1 do
piloto ("nada fora do piloto muda") lê as diferenças linha a linha deste `telas.csv`, e confere as
capturas das demais telas por amostra de 20.*

| Arquivo | O que é |
|---|---|
| [`telas.csv`](telas.csv) | uma linha por padrão de tela, com as colunas do `telas.csv` do estudo |
| [`capturas/`](capturas/) e [`capturas.csv`](capturas.csv) | uma captura por padrão de tela, tirada a 1440 px, página inteira, reduzida a 960 px em JPEG; o índice diz de que tela e de que identidade é cada uma |
| [`scripts/montar_banco.sh`](scripts/montar_banco.sh) | monta o banco do zero |
| [`scripts/rastrear_tudo.sh`](scripts/rastrear_tudo.sh) | roda o instrumento inteiro e grava o `telas.csv` |
| [`scripts/montar_telas_csv.py`](scripts/montar_telas_csv.py) | a junção do rastreio e das larguras no `telas.csv`, que o estudo fez à mão e não deixou em script |
| [`scripts/medir_p0.py`](scripts/medir_p0.py) | a sonda da P0: Visão Geral e todas as confirmações de ato, nas cinco larguras |

## Os estados, os dados e as permissões

**129 telas**, contra 131 do estudo. Faltam o recurso visto pelo candidato (`/selecoes/recursos/<id>`),
que nenhum dos quatro candidatos deste banco tem, e a verificação pública do sorteio, cujo endereço o
`complemento.py` do estudo traz fixo, com o identificador do banco de 14/11.

**O banco** é `ps_p0_referencia`, no cluster local, montado por `scripts/montar_banco.sh`:
migrations da branch, `semear_unidades`, `seed_demo` e os 17 cenários de treinamento
(`carregar_cenarios_de_treinamento`, C01 a C17, rodada 1). Nenhum dado foi acrescentado à mão, e o
instrumento só lê: o único POST é o da entrada pela identidade de demonstração. **Ele fica no
cluster, intocado, para o piloto medir sobre os mesmos registros.** Há uma cópia de segurança
(`pg_dump -Fc`, 3,9 MB) fora do repositório, na pasta de notas das sessões deste trabalho; ela
restaura com `pg_restore --no-owner -d <banco novo>`.

**A data importa.** O `seed_demo` e os cenários datam prazos a partir do dia em que rodam: o
período de inscrições, a janela recursal e o "até 14/11/2026" que aparece nas telas. Remontado
noutro dia, o banco tem os mesmos registros e outros prazos, e algumas telas mudam de estado
(período aberto que fecha, recurso que deixa de caber). **Para comparar com esta referência, meça
no `ps_p0_referencia` como ele está**, e não num banco remontado; remontar serve para conferir que
o procedimento reproduz a mesma forma, e não os mesmos números de prazo.

**As identidades e os papéis**, todos pela entrada de demonstração (`INTERFACE_SELETOR_IDENTIDADE`):

| Identidade | Papéis | O que cobre |
|---|---|---|
| `paulo.presidente` | os dez papéis da demonstração | a gestão, a partir de `/gestao/` |
| `treino.presidencia` | os dez papéis | a gestão, a partir de `/gestao/` e `/gestao/visao-geral`; e o complemento: as telas que só se alcançam por URL montada, entre elas as confirmações de ato |
| `treino.avaliacao1` | nenhum papel institucional | a vista de quem avalia |
| `treino.formalizacao` | Formalização | a vista do setor |
| sem identidade | — | o portal público e as telas de entrada |
| quatro candidatos fictícios | — | o portal autenticado: `ana@exemplo.test` (convocada no `seed_demo`), e os primeiros inscritos de C08 (resultado e recursos), C10 (convocação) e C11 (entrega documental) |

Os dez papéis: elaborador, homologador, publicador, gestor, julgador, auditor, exportador,
comunicação, formalização e participante do piloto do assistente.

## Para reproduzir

```bash
sh doc/auditoria-design-system-2026-11-14/referencia-p0/scripts/montar_banco.sh ps_p0_referencia
```

Depois, o servidor `referencia-p0` do `.claude/launch.json` (porta 8166), e:

```bash
cd backend && uv sync --extra dev --extra navegador && uv run playwright install chromium
```

```bash
cd backend && sh ../doc/auditoria-design-system-2026-11-14/referencia-p0/scripts/rastrear_tudo.sh <pasta de trabalho>
```

**A porta.** O instrumento do estudo traz fixa a 8165, que é a da entrada `auditoria-visual`, com
o banco do estudo. O roteiro não o altera: copia os quatro scripts para `<pasta>/instrumento/` e
troca só o endereço, para a 8166 ou para a que `PORTA` disser. A referência desta pasta foi gravada
com a entrada na 8165, antes da troca, e saiu do `ps_p0_referencia`: os 17 Editais que o rastreio
visitou existem nele, e nenhum no `ps_auditoria_visual`. A sonda `medir_p0.py` lê a mesma `PORTA`.

O passo do portal espera o código de acesso de cada candidato: o roteiro grava
`<pasta>/pedido-candN.txt` com o e-mail, o código sai no terminal do servidor, e quem o lê o
escreve em `<pasta>/codigo-candN.txt`. As capturas saem em `<pasta>/cap/`, em PNG; as desta pasta
são as do representante de cada padrão, convertidas por
`sips --resampleWidth 960 -s format jpeg -s formatOptions 50`. Para comparar pixel a pixel, use as
PNG da pasta de trabalho, e não estas.

**As colunas do `telas.csv` são as do estudo**, e a definição de cada uma foi conferida contra o
`telas.csv` de 14/11 nas 91 telas cuja altura não mudou: a folha própria é toda folha que não seja
os tokens nem a comum da gestão; os tamanhos de fonte contam os que somam ao menos 1% do texto; a
assinatura de botão é o par (altura, fonte). O estudo fez essa junção à mão, e ela agora está em
`scripts/montar_telas_csv.py`.
