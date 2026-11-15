#!/bin/sh
# Roda o instrumento do estudo inteiro contra o servidor `referencia-p0` (porta 8166) e grava, em
# <pasta>, os rastreios, as larguras, as capturas e o telas.csv. Rode a partir de backend/.
# O instrumento traz a porta 8165 fixa, que é a da `auditoria-visual`, com o banco do estudo: as
# cópias em <pasta>/instrumento/ trocam só o endereço, para as duas entradas conviverem e o
# rastreio não medir o banco errado em silêncio. PORTA=8165 mede a `auditoria-visual`.
# O portal autenticado pede o código de acesso, que sai no terminal do servidor: o passo 3 espera
# um arquivo <pasta>/codigo-candN.txt para cada candidato, escrito à mão por quem lê o código.
set -e
W=${1:?pasta de trabalho}; M=../doc/auditoria-design-system-2026-11-14/medicoes
R=../doc/auditoria-design-system-2026-11-14/referencia-p0/scripts
mkdir -p "$W/instrumento"; cp $M/metricas.js $M/largura.js "$W"/
PORTA=${PORTA:-8166}
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
# 3. O portal autenticado, por quatro candidatos fictícios.
uv run python $M/portal.py "$W" ana@exemplo.test cefor-c08r1p01@treinamento.exemplo.test \
  cefor-c10r1p01@treinamento.exemplo.test cefor-c11r1p01@treinamento.exemplo.test
# 4. Uma visita por padrão, nas cinco larguras; depois o telas.csv.
python3 $R/montar_telas_csv.py "$W" representantes
uv run python $M/larguras.py "$W"
python3 $R/montar_telas_csv.py "$W" csv
