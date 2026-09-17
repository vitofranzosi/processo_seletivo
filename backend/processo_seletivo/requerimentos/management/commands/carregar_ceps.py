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

**Cada execução é uma geração, e a ativação é atômica.** A redação anterior fazia `upsert` em lotes
sobre a mesma tabela, e duas consequências só apareceram quando a operação passou a ser recorrente:
carga interrompida no meio deixava a base numa **mistura** — parte nova, parte velha, e nada dizendo
qual linha era qual —, e o CEP que a fonte **removeu** ficava para sempre, porque `upsert` nunca
apaga o que não veio.

A carga agora escreve numa geração nova, invisível para quem consulta, e só no fim — **numa
transação** — a vigência muda de dono. Interrupção não ativa nada: a geração anterior continua
inteira e respondendo. E a nova só tem o que a fonte mandou.

**Duas cargas simultâneas são impedidas por trava do próprio banco.** `pg_try_advisory_lock` é a
ferramenta exata: ela não depende de linha nenhuma, e é **liberada quando a conexão cai** — de modo
que um job morto não deixa a trava pendurada, que é o defeito de quem a implementa com uma coluna.

**O que este comando não é**: sincronização. Ele carrega o que o arquivo traz. Base desatualizada
produz CEP não reconhecido, que é o caminho degradado normal da `FR-390` — e não um erro.

**Ele lê o `.zip` direto, e essa não é conveniência.** A fonte distribui **um arquivo JSON por
CEP** — 1.209.314 deles no instantâneo de 17/09/2026. Descompactar produz mais de um milhão de
inodes só para serem lidos uma vez e apagados; num sistema de arquivos comum isso custa mais do que
a carga inteira, e em alguns esgota o limite de arquivos do volume antes de terminar. Ler de dentro
do arquivo compactado é uma abertura em vez de um milhão.
"""

import hashlib
import json
import zipfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.requerimentos.domain.endereco import normalizar
from processo_seletivo.requerimentos.models import CargaDeCep, ReferenciaDeCep

LOTE = 2000
# O número da trava consultiva. Arbitrário e fixo: o que importa é que só este comando o use.
TRAVA = 292_026


class Command(BaseCommand):
    help = "Carrega a base local de referência de CEP a partir de um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument("origem", help="arquivo `.zip`, JSON, ou diretório de arquivos JSON")
        parser.add_argument(
            "--se-mudou",
            action="store_true",
            help="não faz nada quando a geração vigente já tem este mesmo resumo",
        )
        parser.add_argument(
            "--manter-anteriores",
            action="store_true",
            help="não recolhe as gerações que deixaram de ser vigentes",
        )

    def handle(self, *args, **opcoes):
        origem = Path(opcoes["origem"])
        if not origem.exists():
            raise CommandError(f"Origem não encontrada: {origem}")
        resumo = self._resumo_do_arquivo(origem)
        vigente = CargaDeCep.objects.filter(vigente=True).first()
        if opcoes["se_mudou"] and vigente is not None and vigente.checksum == resumo:
            self.stdout.write(f"A geração {vigente.geracao} já tem este resumo. Nada a fazer.")
            return
        if not self._travar():
            # **Recusa, e não espera.** Um job mensal que fica bloqueado atrás de outro só descobre
            # o problema no tempo limite; recusar na hora é o que faz o alerta disparar cedo.
            raise CommandError("Outra carga de CEPs está em andamento. Esta execução não faz nada.")
        try:
            self._carregar(origem, resumo, opcoes)
        finally:
            self._destravar()

    def _carregar(self, origem, resumo, opcoes):
        anterior = CargaDeCep.objects.filter(vigente=True).first()
        carga = CargaDeCep.objects.create(
            geracao=(
                CargaDeCep.objects.order_by("-geracao").values_list("geracao", flat=True).first()
                or 0
            )
            + 1,
            origem=origem.name,
            checksum=resumo,
            iniciada_em=timezone.now(),
        )
        gravados = 0
        try:
            for lote in self._lotes(origem):
                for linha in lote:
                    linha.carga = carga
                # `ignore_conflicts` porque a fonte pode repetir um CEP entre arquivos, e uma
                # duplicata no meio de 1,2 milhão de linhas não é motivo para perder a carga.
                with transaction.atomic():
                    ReferenciaDeCep.objects.bulk_create(lote, ignore_conflicts=True)
                gravados += len(lote)
        except Exception as erro:
            # A carga que falhou **fica registrada**, e é o que o alerta de operação lê. Ela não é
            # ativada, e a geração anterior continua respondendo inteira.
            CargaDeCep.objects.filter(pk=carga.pk).update(falha=str(erro)[:2000])
            raise
        self._ativar(carga, gravados, anterior)
        if not opcoes["manter_anteriores"]:
            self._recolher(carga)
        self.stdout.write(
            f"Geração {carga.geracao} ativada: {gravados} CEPs de referência carregados."
        )

    def _ativar(self, carga, gravados, anterior):
        """A troca de dono da vigência, **numa transação**.

        É este bloco que torna a carga atômica para quem consulta: ou a geração anterior responde
        inteira, ou a nova responde inteira. Nunca uma mistura.

        **A anterior é desmarcada antes**, e não depois: o índice parcial único admite **uma**
        vigente, e inverter a ordem faria o `UPDATE` colidir consigo mesmo.
        """
        with transaction.atomic():
            if anterior is not None:
                CargaDeCep.objects.filter(pk=anterior.pk).update(vigente=False)
            CargaDeCep.objects.filter(pk=carga.pk).update(
                vigente=True, concluida_em=timezone.now(), linhas=gravados
            )

    def _recolher(self, vigente):
        """As gerações que não são a vigente. Fora da transação da troca, de propósito.

        Apagar 1,2 milhão de linhas demora, e prender a troca de vigência a essa demora faria a
        janela de indisponibilidade ser a do recolhimento — que é justamente o que a ativação
        atômica existe para evitar. Se o recolhimento falhar, a base vigente continua correta e
        sobra espaço ocupado, que é um problema de disco e não de dado.
        """
        CargaDeCep.objects.exclude(pk=vigente.pk).delete()

    def _resumo_do_arquivo(self, origem):
        """O `sha256` do arquivo, ou `""` para diretório — que não tem resumo estável."""
        if origem.is_dir():
            return ""
        digestor = hashlib.sha256()
        with origem.open("rb") as arquivo:
            for pedaco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digestor.update(pedaco)
        return digestor.hexdigest()

    def _travar(self) -> bool:
        if connection.vendor != "postgresql":
            return True
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [TRAVA])
            return bool(cursor.fetchone()[0])

    def _destravar(self):
        if connection.vendor != "postgresql":
            return
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_unlock(%s)", [TRAVA])

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
