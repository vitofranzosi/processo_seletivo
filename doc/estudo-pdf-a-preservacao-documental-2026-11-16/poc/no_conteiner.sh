#!/bin/sh
# uso: no_conteiner.sh IMAGEM "comando" — copia a pasta da POC para dentro e traz de volta amostras/ e saida/
P=$(cd "$(dirname "$0")" && pwd)
IMG=$1; shift
COPYFILE_DISABLE=1 tar -C "$P" -cf - --exclude img . | docker run --rm -i --network none --entrypoint sh "$IMG" -c "mkdir -p /poc && tar -xf - -C /poc && cd /poc && { $* ; } 1>&2 && tar -cf - amostras saida" | tar -xf - -C "$P"
