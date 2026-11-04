"""O ZIP da exportação e o manifesto dele, num temporário sem nome (117, FR-3686 a FR-3688).

**Sem nome no sistema de arquivos** (FR-3688): `TemporaryFile` usa `O_TMPFILE` no Linux, e nos
outros POSIX desfaz o nome logo depois de abrir. Só o processo o lê, e ele deixa de existir quando é
fechado — no fim da resposta, na desconexão do cliente, numa exceção ou na morte do processo. Não há
URL, cópia nem cache dele depois.

**Sem compressão e determinístico** (SC-1108): `ZIP_STORED`, a data de cada entrada é a do envio do
documento, as permissões são fixas e a ordem é a do seletor. Duas exportações do mesmo alcance, sem
mudança, dão entradas de documento idênticas byte a byte; o manifesto muda, porque diz quando e
quem.

**Os caminhos vêm de `domain/caminhos.py`**, montados só com valores do sistema, e a marca UTF-8 do
ZIP vai em toda entrada — o nome com acento abre igual no Windows e no macOS.

**O hash do pacote numa leitura** do temporário pronto: o ZIP volta ao cabeçalho de cada entrada
para gravar o tamanho, e por isso o resumo não pode ser calculado enquanto se escreve.
"""

import csv
import hashlib
import io
import shutil
import tempfile
import zipfile

from django.utils import timezone

from processo_seletivo.formalizacao.domain.caminhos import neutralizar
from processo_seletivo.shared.arquivos import BLOCO

#: A marca de nome em UTF-8 do formato ZIP (bit 11 do campo de *flags*).
MARCA_UTF8 = 0x800
#: `-rw-r--r--`, de arquivo comum, para que o descompactador não invente permissão.
PERMISSOES = 0o100644 << 16
#: A menor data que o formato ZIP representa.
MENOR_DATA = (1980, 1, 1, 0, 0, 0)
BOM = "﻿"
MANIFESTO = "manifesto.csv"


def _data(instante):
    if instante is None:
        return MENOR_DATA
    local = timezone.localtime(instante) if timezone.is_aware(instante) else instante
    data = local.timetuple()[:6]
    return max(data, MENOR_DATA)


def _entrada(caminho, instante, tamanho):
    info = zipfile.ZipInfo(caminho, date_time=_data(instante))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = PERMISSOES
    info.flag_bits |= MARCA_UTF8
    info.file_size = tamanho
    return info


def manifesto(cabecalho, linhas):
    """O `manifesto.csv`: UTF-8 com BOM, RFC 4180, toda célula neutralizada (FR-3713).

    `cabecalho` é uma lista de pares (campo, valor); `linhas`, de listas com as colunas da tabela.
    """
    saida = io.StringIO()
    escritor = csv.writer(saida, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    for campo, valor in cabecalho:
        escritor.writerow([neutralizar(campo), neutralizar(valor)])
    escritor.writerow([])
    for linha in linhas:
        escritor.writerow([neutralizar(celula) for celula in linha])
    return (BOM + saida.getvalue()).encode("utf-8")


class Pacote:
    """O ZIP em construção. `fechar` devolve o arquivo rebobinado, o tamanho e o SHA-256."""

    def __init__(self):
        self.arquivo = tempfile.TemporaryFile()
        self.zip = zipfile.ZipFile(self.arquivo, "w", zipfile.ZIP_STORED, allowZip64=True)
        self.quantidade = 0

    def acrescentar(self, caminho, conteudo, *, instante, tamanho):
        """Copia `conteudo` (um arquivo já conferido, rebobinado) para a entrada `caminho`."""
        with self.zip.open(_entrada(caminho, instante, tamanho), "w") as destino:
            shutil.copyfileobj(conteudo, destino, BLOCO)
        self.quantidade += 1

    def acrescentar_manifesto(self, dados, *, instante):
        self.zip.writestr(_entrada(MANIFESTO, instante, len(dados)), dados)

    def fechar(self):
        self.zip.close()
        self.arquivo.seek(0)
        resumo = hashlib.sha256()
        tamanho = 0
        for bloco in iter(lambda: self.arquivo.read(BLOCO), b""):
            resumo.update(bloco)
            tamanho += len(bloco)
        self.arquivo.seek(0)
        return self.arquivo, tamanho, resumo.hexdigest()

    def descartar(self):
        """Fecha tudo, sem levantar: é chamado no caminho da falha, e não pode escondê-la."""
        try:
            self.zip.close()
        except Exception:  # noqa: BLE001 — o ZIP pode estar no meio de uma entrada
            pass
        self.arquivo.close()
