"""Carrega a base local de referência de CEP (029, `D-009`, `FR-388`).

**Por que base local, e não consulta a serviço de terceiro.** Consultar em tempo real transmitiria
continuamente o CEP de candidatos identificados para fora da instituição — o que a minimização do
Princípio III desaconselha — e poria um certame em curso na dependência de disponibilidade alheia.
Uma base carregada por comando é reprodutível, não cai, e não muda sob os pés de quem está
preenchendo.

**A fonte é `gpfconfea/banco-ceps`** (MIT), que estende o `OpenCEP` — Correios e IBGE — com campos
que este comando **descarta**: latitude e longitude. A própria fonte adverte que a confiabilidade
delas é variável, porque são montadas em três camadas, com raspagem como último recurso. O campo que
interessa é `ibge`, e é ele que justifica carregar a base em vez de digitar município e UF à mão.

**O que este comando não é**: sincronização. Ele carrega o que o arquivo traz, substituindo linha a
linha. Base desatualizada produz CEP não reconhecido, que é o caminho degradado normal da `FR-390` —
e não um erro.

**Ele lê o `.zip` direto, e essa não é conveniência.** A fonte distribui **um arquivo JSON por
CEP** — 1.209.314 deles no instantâneo de 17/09/2026. Descompactar produz mais de um milhão de
inodes só para serem lidos uma vez e apagados; num sistema de arquivos comum isso custa mais do que
a carga inteira, e em alguns esgota o limite de arquivos do volume antes de terminar. Ler de dentro
do arquivo compactado é uma abertura em vez de um milhão.
"""

import json
import zipfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from processo_seletivo.requerimentos.domain.endereco import normalizar
from processo_seletivo.requerimentos.models import ReferenciaDeCep

LOTE = 2000


class Command(BaseCommand):
    help = "Carrega a base local de referência de CEP a partir de um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument("origem", help="arquivo JSON, ou diretório de arquivos JSON")

    def handle(self, *args, **opcoes):
        origem = Path(opcoes["origem"])
        if not origem.exists():
            raise CommandError(f"Origem não encontrada: {origem}")
        gravados = 0
        for lote in self._lotes(origem):
            with transaction.atomic():
                ReferenciaDeCep.objects.bulk_create(
                    lote,
                    update_conflicts=True,
                    update_fields=["logradouro", "bairro", "municipio", "uf", "codigo_ibge"],
                    unique_fields=["cep"],
                )
            gravados += len(lote)
        self.stdout.write(f"{gravados} CEPs de referência carregados.")

    def _lotes(self, origem):
        """Em lotes porque a base é da ordem de 10⁶ linhas: uma transação só a manteria inteira em
        memória e prenderia a tabela do começo ao fim da carga.
        """
        lote = []
        for registro in self._registros(origem):
            linha = self._linha(registro)
            if linha is None:
                continue
            lote.append(linha)
            if len(lote) >= LOTE:
                yield lote
                lote = []
        if lote:
            yield lote

    def _registros(self, origem):
        """Os registros da origem, seja ela um `.zip`, uma pasta ou um arquivo só.

        **Em fluxo, e nunca materializando a lista de nomes.** `sorted(rglob(...))` sobre a base
        real construiria uma lista de um milhão de caminhos antes de ler o primeiro registro.
        """
        if zipfile.is_zipfile(origem):
            with zipfile.ZipFile(origem) as arquivo:
                for nome in arquivo.namelist():
                    if nome.endswith(".json"):
                        yield from self._do_texto(arquivo.read(nome).decode("utf-8"))
            return
        caminhos = origem.rglob("*.json") if origem.is_dir() else iter([origem])
        for caminho in caminhos:
            yield from self._do_texto(caminho.read_text(encoding="utf-8"))

    def _do_texto(self, texto):
        """Um registro, ou vários: a fonte distribui um objeto por arquivo, mas um dump em lista é
        a forma que qualquer outra origem usaria, e aceitar as duas não custa nada."""
        try:
            conteudo = json.loads(texto)
        except json.JSONDecodeError:
            # **Arquivo corrompido não derruba a carga.** A base é montada por raspagem, e a própria
            # fonte publica a lista dos CEPs que falharam: um registro ilegível é o caminho
            # degradado normal, e abortar por causa dele deixaria a tabela pela metade.
            return
        yield from conteudo if isinstance(conteudo, list) else [conteudo]

    def _linha(self, registro):
        """Uma linha da base, ou `None` quando o registro não traz CEP utilizável.

        **Latitude e longitude são descartadas aqui**, e não ignoradas na leitura: o que não entra
        na tabela não precisa de política de exibição depois, e não vira o campo que alguém acha que
        pode mostrar como "onde a pessoa mora".
        """
        if not isinstance(registro, dict):
            return None
        cep = normalizar(registro.get("cep"))
        if not cep:
            return None
        return ReferenciaDeCep(
            cep=cep,
            logradouro=(registro.get("logradouro") or "").strip(),
            bairro=(registro.get("bairro") or "").strip(),
            municipio=(registro.get("localidade") or registro.get("municipio") or "").strip(),
            uf=(registro.get("uf") or "").strip()[:2],
            codigo_ibge=(registro.get("ibge") or "").strip()[:7],
        )
