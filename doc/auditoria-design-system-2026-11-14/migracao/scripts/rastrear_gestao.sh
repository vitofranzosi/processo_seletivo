#!/bin/sh
# O `rastrear_tudo.sh` da referência sem o passo do portal autenticado: a migração é da gestão, e o
# portal não muda (ele não carrega as folhas da gestão). Grava, em <pasta>, os rastreios, as
# larguras, as capturas e o telas.csv, contra o servidor da porta PORTA. Rode a partir de backend/.
#
#   PORTA=8172 sh rastrear_gestao.sh <pasta-antes>    # a `main`, entrada `piloto-antiga`
#   PORTA=8175 sh rastrear_gestao.sh <pasta-depois>   # esta branch, entrada `migracao-ds`
#
# As duas entradas servem o mesmo `ps_piloto_validacao`, a cópia migrada da referência
# (`piloto/scripts/montar_banco_da_validacao.sh referencia`).
set -e
W=${1:?pasta de trabalho}; M=../doc/auditoria-design-system-2026-11-14/medicoes
R=../doc/auditoria-design-system-2026-11-14/referencia-p0/scripts
mkdir -p "$W/instrumento"; cp $M/metricas.js $M/largura.js "$W"/
PORTA=${PORTA:?a porta do servidor}
for f in rastrear complemento portal larguras; do
  sed "s#localhost:8165#localhost:$PORTA#" $M/$f.py > "$W/instrumento/$f.py"
done
M="$W/instrumento"
T=elaborador,homologador,publicador,gestor,julgador,auditor,exportador,comunicacao,formalizacao,participante-piloto-assistente
# 1. A gestão, por quatro identidades, e o público sem identidade.
uv run python $M/rastrear.py "$W" paulo.presidente $T /gestao/ 900 3
uv run python $M/rastrear.py "$W" treino.presidencia $T /gestao/,/gestao/visao-geral 900 3
uv run python $M/rastrear.py "$W" treino.avaliacao1 "" /gestao/ 200 3
uv run python $M/rastrear.py "$W" treino.formalizacao formalizacao /gestao/ 200 3
uv run python $M/rastrear.py "$W" anonimo "" /selecoes/,/gestao/identificar,/gestao/identificar/demonstracao 200 3
# 2. As telas que só se alcançam por URL montada: as confirmações de ato, entre elas.
uv run python $M/complemento.py "$W"
# 4. Uma visita por padrão, nas cinco larguras; depois o telas.csv.
python3 $R/montar_telas_csv.py "$W" representantes
uv run python $M/larguras.py "$W"
python3 $R/montar_telas_csv.py "$W" csv
