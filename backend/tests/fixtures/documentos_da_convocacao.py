"""Os cenários da `115` e os atalhos que os testes dela usam.

**Funções aqui, fixtures no `conftest.py` de cada pasta**, pela regra de `tests/fixtures/corte.py`.

Três moldes, todos de **vaga imediata**, sobre o cenário da convocação da `019`:

- `ALUNO`, no molde do 72/2026: identidade na inscrição, quatro documentos de matrícula na
  convocação;
- `BOLSISTA`, no molde do 146/2025: a Ficha/Termo da agência na convocação, com modelo anexo;
- `CERTIFICADO`, no molde do 89/2026: o certificado facultativo na inscrição e obrigatório na
  convocação, que aproveita o da inscrição.
"""

from django.core.files.uploadedfile import SimpleUploadedFile

from processo_seletivo.convocacao.application import documentos as servico
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.models import Convocacao
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID, identificador

IDENTIDADE = identificador(1151, 0)
CERTIDAO = identificador(1152, 0)
HISTORICO = identificador(1153, 0)
CERTIFICADO_DO_MEDIO = identificador(1154, 0)
RESIDENCIA = identificador(1155, 0)
FICHA = identificador(1156, 0)
CERTIFICADO = identificador(1157, 0)
CERTIFICADO_NA_CONVOCACAO = identificador(1158, 0)


def _documento(
    identidade, chave, nome, ordem, *, momento="AT_ENROLLMENT", obrigatorio=True, **extra
):
    return {
        "id": identidade,
        "key": chave,
        "name": nome,
        "instructions": extra.pop("instrucao", ""),
        "required": obrigatorio,
        "order": ordem,
        "moment": momento,
        **extra,
    }


def documentos_do_aluno():
    """O 72/2026 em miniatura: a identificação na inscrição, o Anexo I na convocação."""
    return [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        _documento(
            CERTIDAO, "certidao", "Certidão de nascimento ou casamento", 2, momento="AT_CALL"
        ),
        _documento(
            HISTORICO,
            "historico",
            "Histórico escolar do ensino médio",
            3,
            momento="AT_CALL",
            instrucao="Todas as páginas, em arquivo único.",
        ),
        _documento(
            CERTIFICADO_DO_MEDIO,
            "certificado-medio",
            "Certificado de conclusão do ensino médio",
            4,
            momento="AT_CALL",
        ),
        _documento(RESIDENCIA, "residencia", "Comprovante de residência", 5, momento="AT_CALL"),
    ]


def documentos_do_bolsista():
    """O 146/2025 em miniatura: a Ficha de Cadastramento/Termo de Compromisso na convocação."""
    return [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        _documento(
            FICHA,
            "ficha-termo",
            "Ficha de Cadastramento e Termo de Compromisso do Bolsista",
            2,
            momento="AT_CALL",
            instrucao="Preenchida e assinada, no modelo do Edital.",
        ),
    ]


def documentos_do_certificado():
    """O 89/2026 em miniatura: o mesmo certificado nos dois momentos, ligado pelo aproveitamento."""
    return [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        _documento(
            CERTIFICADO,
            "certificado",
            "Certificado do curso de formação",
            2,
            obrigatorio=False,
        ),
        _documento(
            CERTIFICADO_NA_CONVOCACAO,
            "certificado-na-convocacao",
            "Certificado do curso de formação",
            3,
            momento="AT_CALL",
            reusesRequirementId=CERTIFICADO,
        ),
    ]


def montar(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    documentos,
    documentos_da_inscricao=None,
    prefixo="documentos-115",
    **kwargs,
):
    """O cenário da convocação da `019`, com os Documentos Exigidos que o caso pede."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        documentos=documentos,
        documentos_da_inscricao=documentos_da_inscricao,
        **kwargs,
    )


def primeira_da_fila(edital, inscricoes):
    alvo = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]
    return next(i for i in inscricoes if i.id == alvo)


def convocar_primeira(cenario, gestor, chave="convocar-115", **kwargs):
    edital, _, inscricoes = cenario
    pessoa = primeira_da_fila(edital, inscricoes)
    declarado = convocar(edital, gestor, pessoa.id, idempotency_key=chave, **kwargs)
    return pessoa, Convocacao.objects.get(id=declarado["id"])


def comunicar(edital, gestor, convocacao, chave="comunicar-115"):
    from processo_seletivo.convocacao.application.comunicar import comunicar as emitir

    return emitir(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        idempotency_key=chave,
        correlation_id="teste-115",
    )


def desfechar(edital, gestor, convocacao, especie, chave, fundamento="Registrado em processo."):
    from processo_seletivo.convocacao.application.desfechar import desfechar as registrar

    return registrar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        especie=especie,
        fundamento=fundamento,
        idempotency_key=chave,
        correlation_id="teste-115",
    )


class Titular:
    """A identidade do candidato como o portal a tem: o `subject` da inscrição."""

    def __init__(self, inscricao):
        self.subject = inscricao.identity_subject


def pdf(corpo=b"documento da convocacao", nome="documento.pdf"):
    return SimpleUploadedFile(nome, b"%PDF-1.4\n" + corpo, content_type="application/pdf")


def item(convocacao, requisito_id):
    raiz = servico.raiz_da_chamada(convocacao)
    return raiz.itens_da_lista.get(requisito_id=requisito_id)


def apresentar(inscricao, convocacao, requisito_id, *, corpo=b"documento da convocacao"):
    arquivo = pdf(corpo)
    return servico.apresentar(
        identidade=Titular(inscricao),
        inscricao_id=inscricao.id,
        item_id=item(convocacao, requisito_id).id,
        arquivo=arquivo,
        nome_original=arquivo.name,
        correlation_id="teste-115",
    )


def abrir(ator, apresentacao):
    """O registro de consulta que a entrega na gestão grava — o que a FR-3611 lê."""
    from django.utils import timezone

    from processo_seletivo.auditoria.application import record_event

    record_event(
        actor=ator,
        permission="",
        operation=servico.CONSULTAR_APRESENTACAO,
        aggregate=apresentacao,
        now=timezone.now(),
        correlation_id="teste-115",
        new_state="",
        new_revision=None,
    )


def conferir(ator, convocacao, requisito_id, resultado, *, chave, abrir_antes=True, **kwargs):
    alvo = item(convocacao, requisito_id)
    vigente = alvo.apresentacoes.order_by("-numero").first()
    if abrir_antes and vigente is not None and resultado == "CONFORME":
        abrir(ator, vigente)
    return servico.conferir(
        actor=ator,
        item_id=alvo.id,
        apresentacao_id=kwargs.pop("apresentacao_id", vigente.id if vigente else None),
        resultado=resultado,
        idempotency_key=chave,
        correlation_id="teste-115",
        **kwargs,
    )


def lido(convocacao, requisito_id):
    leitura = servico.leitura_da_chamada(convocacao)
    return next(i for i in leitura.itens if str(i.item.requisito_id) == str(requisito_id))


def arquivos_no_armazenamento(raiz):
    """Quantos arquivos há sob a raiz — para provar que o aproveitamento não copia nada."""
    from pathlib import Path

    return sum(1 for caminho in Path(raiz).rglob("*") if caminho.is_file())
