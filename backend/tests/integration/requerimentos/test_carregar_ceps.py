"""A carga da base de referência de CEP (029, `T-008`, `T-015`, `D-008`).

**O que a medição de 17/09/2026 encontrou, e que este arquivo prende.** A fonte não distribui um
dump: distribui **um arquivo JSON por CEP** — 1.209.314 deles. O comando recebia uma pasta e fazia
`rglob("*.json")`, o que contra a base real significa descompactar um milhão e duzentos mil arquivos
para lê-los uma vez, e materializar uma lista de um milhão de caminhos antes do primeiro registro.

Ele passou a ler o `.zip` **em fluxo**: uma abertura em vez de um milhão. A carga inteira leva 31
segundos.

**Cada carga é uma geração, e a ativação é atômica.** O `upsert` linha a linha da primeira redação
tinha duas consequências que só aparecem na operação recorrente: carga interrompida deixava a base
numa **mistura**, e o CEP que a fonte **removeu** ficava para sempre. A geração resolve as duas — e
os testes abaixo exercitam exatamente esses dois casos, porque são eles que nenhum teste de caminho
feliz alcança.

**E latitude e longitude são descartadas na leitura** (`D-008`). Elas vêm em todo registro da fonte,
e a própria fonte adverte que a confiabilidade delas é variável. O que não entra na tabela não
precisa de política de exibição depois, e não vira o campo que alguém acha que pode mostrar como
*"onde a pessoa mora"*.
"""

import json
import zipfile

import pytest
from django.core.management import call_command

from processo_seletivo.requerimentos.domain import endereco
from processo_seletivo.requerimentos.models import CargaDeCep, ReferenciaDeCep

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# Um registro na forma exata da fonte, com as coordenadas que o comando joga fora.
DA_FONTE = {
    "cep": "29040860",
    "logradouro": "Rua Barão de Mauá",
    "complemento": "",
    "bairro": "Jucutuquara",
    "localidade": "Vitória",
    "uf": "ES",
    "ibge": "3205309",
    "latitude": "-20.3076396",
    "longitude": "-40.3208734",
}


def zip_com(registros, tmp_path, nome="ceps.zip"):
    """Um `.zip` no formato da fonte: um arquivo por CEP, dentro de uma pasta."""
    caminho = tmp_path / nome
    with zipfile.ZipFile(caminho, "w") as arquivo:
        arquivo.writestr("banco-ceps-main/README.md", "# base\n")
        for registro in registros:
            arquivo.writestr(
                f"banco-ceps-main/cep/{registro['cep']}.json",
                json.dumps(registro, ensure_ascii=False),
            )
    return caminho


class TestOZip:
    def test_carrega_do_zip_sem_descompactar(self, tmp_path):
        """A forma real da fonte, e a que a medição obrigou a suportar."""
        origem = zip_com([DA_FONTE], tmp_path)

        call_command("carregar_ceps", str(origem))

        linha = ReferenciaDeCep.objects.get(cep="29040860")
        assert linha.municipio == "Vitória"
        assert linha.uf == "ES"
        assert linha.codigo_ibge == "3205309"
        assert linha.logradouro == "Rua Barão de Mauá"

    def test_o_que_nao_e_json_no_zip_e_ignorado(self, tmp_path):
        """O `README` e o `requirements.txt` vêm junto no arquivo da fonte."""
        origem = zip_com([DA_FONTE], tmp_path)

        call_command("carregar_ceps", str(origem))

        assert ReferenciaDeCep.objects.count() == 1

    def test_registro_ilegivel_nao_derruba_a_carga(self, tmp_path):
        """A base é montada por raspagem, e a fonte publica a lista dos CEPs que falharam.

        Abortar por causa de um arquivo corrompido deixaria a tabela pela metade — e metade de uma
        base de referência é pior do que nenhuma: o CEP não encontrado passa a significar duas
        coisas.
        """
        caminho = tmp_path / "ceps.zip"
        with zipfile.ZipFile(caminho, "w") as arquivo:
            arquivo.writestr("cep/29040860.json", json.dumps(DA_FONTE))
            arquivo.writestr("cep/quebrado.json", "{ isto não é json")
            arquivo.writestr("cep/01001000.json", json.dumps({**DA_FONTE, "cep": "01001000"}))

        call_command("carregar_ceps", str(caminho))

        assert ReferenciaDeCep.objects.count() == 2


class TestOQueNaoEntraNaTabela:
    def test_latitude_e_longitude_sao_descartadas(self, tmp_path):
        """`D-008`: o que não entra na tabela não precisa de política de exibição depois."""
        origem = zip_com([DA_FONTE], tmp_path)

        call_command("carregar_ceps", str(origem))

        colunas = {campo.name for campo in ReferenciaDeCep._meta.get_fields()}
        assert not colunas & {"latitude", "longitude", "lat", "lng"}


class TestAsOutrasOrigens:
    def test_uma_pasta_de_arquivos_continua_funcionando(self, tmp_path):
        """Quem já tem a base descompactada não é obrigado a recompactá-la."""
        pasta = tmp_path / "cep"
        pasta.mkdir()
        (pasta / "29040860.json").write_text(json.dumps(DA_FONTE), encoding="utf-8")

        call_command("carregar_ceps", str(pasta))

        assert ReferenciaDeCep.objects.filter(cep="29040860").exists()

    def test_um_dump_em_lista_tambem(self, tmp_path):
        """A forma que qualquer outra origem usaria. Aceitar as duas não custa nada."""
        arquivo = tmp_path / "dump.json"
        arquivo.write_text(
            json.dumps([DA_FONTE, {**DA_FONTE, "cep": "01001000"}]), encoding="utf-8"
        )

        call_command("carregar_ceps", str(arquivo))

        assert ReferenciaDeCep.objects.count() == 2

    def test_origem_inexistente_recusa_com_mensagem(self, tmp_path):
        from django.core.management.base import CommandError

        with pytest.raises(CommandError, match="não encontrada"):
            call_command("carregar_ceps", str(tmp_path / "nao-existe.zip"))


class TestACargaERepetivel:
    def test_carregar_duas_vezes_atualiza_em_vez_de_duplicar(self, tmp_path):
        """A chave primária é o CEP: recarregar é substituir, e não acumular.

        É o que torna a atualização da base um comando só, sem passo de limpeza antes — e sem a
        janela em que a tabela fica vazia enquanto a carga corre.
        """
        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))
        atualizado = {**DA_FONTE, "bairro": "Bairro Renomeado"}

        call_command("carregar_ceps", str(zip_com([atualizado], tmp_path, "outro.zip")))

        assert ReferenciaDeCep.objects.count() == 1, "a geração anterior foi recolhida"
        assert ReferenciaDeCep.objects.get(cep="29040860").bairro == "Bairro Renomeado"


class TestAPortaLeOQueFoiCarregado:
    def test_o_cep_carregado_e_encontrado_pela_porta_do_dominio(self, tmp_path):
        """A carga e a leitura são duas metades: sem esta asserção, a primeira pode gravar num
        formato que a segunda não encontra — e nada acusaria."""
        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))

        achado = endereco.referencia_de_cep("29.040-860")

        assert achado is not None
        assert achado.municipio == "Vitória"
        assert achado.codigo_ibge == "3205309"


class TestAGeracao:
    """A ativação atômica, e as duas coisas que ela conserta."""

    def test_o_cep_removido_da_fonte_some_da_base(self, tmp_path):
        """**O `upsert` nunca apagava.** Um CEP extinto ficava respondendo para sempre.

        É o defeito mais silencioso da carga anterior: a base cresce, nunca encolhe, e um endereço
        que os Correios desativaram continua sendo oferecido como se valesse.
        """
        antigo = {**DA_FONTE, "cep": "01001000"}
        call_command("carregar_ceps", str(zip_com([DA_FONTE, antigo], tmp_path)))
        assert ReferenciaDeCep.objects.count() == 2

        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path, "sem-o-antigo.zip")))

        assert ReferenciaDeCep.objects.filter(cep="01001000").exists() is False
        assert endereco.referencia_de_cep("01001000") is None

    def test_a_geracao_nova_so_responde_depois_de_ativada(self, tmp_path):
        """A carga escreve invisível: quem consulta continua vendo a anterior, **inteira**.

        A asserção é sobre a porta do domínio, e não sobre a tabela: é ela que a tela usa, e é nela
        que a mistura apareceria.
        """
        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))
        vigente = CargaDeCep.objects.get(vigente=True)
        futura = CargaDeCep.objects.create(
            geracao=vigente.geracao + 1,
            origem="parcial.zip",
            checksum="0" * 64,
            iniciada_em=vigente.iniciada_em,
        )
        ReferenciaDeCep.objects.create(
            carga=futura, cep="29040860", municipio="ERRADO", uf="XX", codigo_ibge="0000000"
        )

        achado = endereco.referencia_de_cep("29040860")

        assert achado.municipio == "Vitória", "a geração não ativada não responde"

    def test_uma_carga_interrompida_nao_ativa_nada(self, tmp_path, monkeypatch):
        """**A garantia inteira, num teste.** Falha no meio deixa a base anterior respondendo.

        Sem isto, o que se prometeria é que a carga *costuma* terminar — e o caso que importa é
        justamente o em que ela não termina.
        """
        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))
        boa = CargaDeCep.objects.get(vigente=True)

        from processo_seletivo.requerimentos.management.commands import carregar_ceps

        def explodir(self, origem):
            yield {**DA_FONTE, "cep": "01001000"}
            raise OSError("o arquivo acabou no meio")

        monkeypatch.setattr(carregar_ceps.Command, "_registros", explodir)
        with pytest.raises(OSError):
            call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path, "quebra.zip")))

        assert CargaDeCep.objects.get(vigente=True).pk == boa.pk
        assert endereco.referencia_de_cep("29040860").municipio == "Vitória"

    def test_a_carga_que_falhou_fica_registrada_para_o_alerta(self, tmp_path, monkeypatch):
        """O que não se registra não se alerta — e a falha é o que a operação precisa saber."""
        from processo_seletivo.requerimentos.management.commands import carregar_ceps

        def explodir(self, origem):
            raise OSError("rede caiu")
            yield  # pragma: no cover

        monkeypatch.setattr(carregar_ceps.Command, "_registros", explodir)
        with pytest.raises(OSError):
            call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))

        assert CargaDeCep.objects.latest("geracao").falha
        assert CargaDeCep.objects.filter(vigente=True).exists() is False

    def test_duas_vigentes_sao_recusadas_pelo_banco(self, tmp_path):
        """`uq_carga_de_cep_vigente_unica`: a regra é do banco, e não promessa de código.

        Duas vigentes fariam a consulta devolver duas linhas para o mesmo CEP, e o que a tela
        mostraria dependeria da ordem do plano de execução.
        """
        from django.db import IntegrityError, transaction

        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))
        vigente = CargaDeCep.objects.get(vigente=True)

        with pytest.raises(IntegrityError), transaction.atomic():
            CargaDeCep.objects.create(
                geracao=vigente.geracao + 1,
                origem="outra.zip",
                checksum="1" * 64,
                iniciada_em=vigente.iniciada_em,
                vigente=True,
            )


class TestNaoRecarregarOQueJaEstaLa:
    def test_se_mudou_nao_faz_nada_quando_o_resumo_e_o_mesmo(self, tmp_path):
        """O deploy comum **confere**; ele não reimporta 379 MB por rotina."""
        origem = zip_com([DA_FONTE], tmp_path)
        call_command("carregar_ceps", str(origem))
        antes = CargaDeCep.objects.get(vigente=True)

        call_command("carregar_ceps", str(origem), "--se-mudou")

        assert CargaDeCep.objects.get(vigente=True).pk == antes.pk
        assert CargaDeCep.objects.count() == 1, "nem geração nova foi aberta"

    def test_se_mudou_carrega_quando_o_arquivo_e_outro(self, tmp_path):
        call_command("carregar_ceps", str(zip_com([DA_FONTE], tmp_path)))

        call_command(
            "carregar_ceps",
            str(zip_com([{**DA_FONTE, "bairro": "Outro"}], tmp_path, "novo.zip")),
            "--se-mudou",
        )

        assert ReferenciaDeCep.objects.get(cep="29040860").bairro == "Outro"

    def test_o_resumo_do_arquivo_fica_registrado(self, tmp_path):
        """É o que responde *"esta base é de qual instantâneo?"* sem abrir o banco."""
        import hashlib

        origem = zip_com([DA_FONTE], tmp_path)
        esperado = hashlib.sha256(origem.read_bytes()).hexdigest()

        call_command("carregar_ceps", str(origem))

        assert CargaDeCep.objects.get(vigente=True).checksum == esperado
