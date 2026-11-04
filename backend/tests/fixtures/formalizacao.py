"""O cenário da entrega documental à formalização (117) e os atalhos que os testes dela usam.

**Funções aqui, fixtures no `conftest.py` de cada pasta**, pela regra de `tests/fixtures/corte.py`.

O Edital é o da convocação da `019`, com documentos dos dois momentos no molde do 72/2026:

- **na inscrição**: identificação (obrigatória), certificado do curso e títulos (facultativos);
- **na convocação**: certidão, histórico, certificado do ensino médio e comprovante de residência.

As pessoas aptas são **inscrições enviadas** com os documentos da inscrição, e **convocações
gravadas direto** no recorte, como a medição da `115` faz: o cenário da `019` só tem uma vaga
faltante, e o que se exercita aqui é a leitura de muitas pessoas, e não a fila. Os documentos da
convocação, a conferência e o desfecho passam pelos serviços — é o que o produto produz, e o que a
formalização lê.
"""

import hashlib
from dataclasses import dataclass, field

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from processo_seletivo.convocacao.application.documentos import gravar_lista_da_chamada
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.formalizacao.application.definir import definir
from processo_seletivo.formalizacao.models import DesignacaoParaFormalizacao
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.ocupacao.application.selectors import apuracao_vigente
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    _documento,
)
from tests.fixtures.edital import PROFILE_ID, identificador

TITULOS = identificador(1171, 0)
CERTIFICADO_DO_CURSO = identificador(1172, 0)

#: Os da inscrição que cada pessoa apta enviou, e os da convocação que ela apresentou.
DA_INSCRICAO = (IDENTIDADE, CERTIFICADO_DO_CURSO, TITULOS)
DA_CONVOCACAO = (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)
#: A definição do Cenário A: identificação, certidão e histórico, e o certificado da inscrição.
DEFINICAO_DO_CENARIO_A = (IDENTIDADE, CERTIDAO, HISTORICO, CERTIFICADO_DO_CURSO)


def documentos_da_formalizacao():
    return [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        _documento(
            CERTIFICADO_DO_CURSO, "certificado", "Certificado do curso", 2, obrigatorio=False
        ),
        _documento(TITULOS, "titulos", "Títulos para pontuação", 3, obrigatorio=False),
        _documento(CERTIDAO, "certidao", "Certidão de nascimento", 4, momento="AT_CALL"),
        _documento(HISTORICO, "historico", "Histórico escolar", 5, momento="AT_CALL"),
        _documento(
            CERTIFICADO_DO_MEDIO,
            "certificado-medio",
            "Certificado do ensino médio",
            6,
            momento="AT_CALL",
        ),
        _documento(RESIDENCIA, "residencia", "Comprovante de residência", 7, momento="AT_CALL"),
    ]


@dataclass
class Cenario:
    edital: object
    #: `[(inscricao, convocacao)]` das pessoas com aceite.
    aptas: list = field(default_factory=list)
    indeferidas: list = field(default_factory=list)
    sem_resposta: list = field(default_factory=list)

    @property
    def inscricoes_aptas(self):
        return [inscricao for inscricao, _ in self.aptas]


def corpo(rotulo, tamanho=None):
    """O conteúdo de um arquivo: distinto por pessoa e documento, e do tamanho pedido."""
    base = f"{rotulo}\n".encode()
    if tamanho:
        base = (base * (tamanho // len(base) + 1))[:tamanho]
    return base


def anexar(inscricao, requirement_id, conteudo):
    bytes_do_arquivo = b"%PDF-1.4\n" + conteudo
    return DocumentoSubmetido.objects.create(
        inscricao=inscricao,
        requirement_id=requirement_id,
        arquivo=SimpleUploadedFile(
            "documento enviado.pdf", bytes_do_arquivo, content_type="application/pdf"
        ),
        nome_original="documento enviado.pdf",
        tamanho=len(bytes_do_arquivo),
        content_hash=hashlib.sha256(bytes_do_arquivo).hexdigest(),
        uploaded_at=timezone.now(),
    )


def inscrever(edital, numero, *, nome=None, tamanho=None, documentos=DA_INSCRICAO):
    """Uma inscrição enviada com os documentos da inscrição — o percurso de `inscrever` da `011`."""
    versao = effective_version(edital_id=edital.id)
    agora = timezone.now()
    inscricao = Inscricao.objects.create(
        created_at=agora,
        identity_subject=f"cpf:formalizacao-{numero:04d}",
        edital=edital,
        profile_id=PROFILE_ID,
        nome=nome or f"Pessoa {numero:03d}",
        cpf="111.444.777-35",
        cpf_normalizado="11144477735",
        email=f"formalizacao{numero}@exemplo.test",
    )
    for requisito in documentos:
        anexar(inscricao, requisito, corpo(f"inscricao {numero} {requisito}", tamanho))
    Inscricao.objects.filter(pk=inscricao.pk).update(
        status=Inscricao.Status.SUBMETIDA,
        protocolo=f"INS-2026-F{numero:04d}",
        submitted_at=agora,
        versao_aceita=versao,
        declaracoes_aceitas_em=agora,
    )
    inscricao.refresh_from_db()
    return inscricao


def convocar_direto(edital, inscricao):
    apuracao = apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None)
    convocacao = Convocacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        inscricao=inscricao,
        especie="VAGA_INICIAL",
        fundamento="Gravada para o cenário da formalização.",
        apuracao=apuracao,
        ato_de_ordenacao_id=apuracao.ato_id,
        corte_id=apuracao.corte_id,
        versao=effective_version(edital_id=edital.id),
        criado_por="cenario-117",
        criado_em=timezone.now(),
    )
    gravar_lista_da_chamada(convocacao, versao=convocacao.versao)
    return convocacao


def tornar_apta(edital, gestor, inscricao, convocacao, *, numero, tamanho=None):
    """Os quatro documentos da convocação apresentados e conformes, e o aceite."""
    for requisito in DA_CONVOCACAO:
        cenarios.apresentar(
            inscricao,
            convocacao,
            requisito,
            corpo=corpo(f"convocacao {numero} {requisito}", tamanho),
        )
        cenarios.conferir(
            gestor, convocacao, requisito, "CONFORME", chave=f"f117-{numero}-{requisito}"
        )
    cenarios.desfechar(edital, gestor, convocacao, nomes_da_convocacao.ACEITE, f"f117-ac-{numero}")


def montar_cenario_da_formalizacao(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    aptas=5,
    indeferidas=0,
    sem_resposta=0,
    tamanho=None,
    nomes=None,
    documentos=None,
    da_inscricao=DA_INSCRICAO,
    prefixo="formalizacao-117",
):
    """O Edital com documentos dos dois momentos e `aptas` pessoas com aceite e tudo conferido.

    `indeferidas` e `sem_resposta` acrescentam convocações que **não** dão aptidão; `tamanho`, em
    bytes, faz cada arquivo ter aquele tamanho (o Cenário A usa 1,5 MB); `nomes`, os nomes das
    pessoas aptas, na ordem — é por eles que entram os nomes hostis; `da_inscricao`, os documentos
    da inscrição que cada uma enviou.
    """
    edital, _, _ = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=documentos or documentos_da_formalizacao(),
        prefixo=prefixo,
    )
    cenario = Cenario(edital=edital)
    numero = 0
    for posicao in range(aptas):
        numero += 1
        nome = nomes[posicao] if nomes and posicao < len(nomes) else None
        inscricao = inscrever(edital, numero, nome=nome, tamanho=tamanho, documentos=da_inscricao)
        convocacao = convocar_direto(edital, inscricao)
        tornar_apta(edital, gestor, inscricao, convocacao, numero=numero, tamanho=tamanho)
        cenario.aptas.append((inscricao, convocacao))
    for _ in range(indeferidas):
        numero += 1
        inscricao = inscrever(edital, numero)
        convocacao = convocar_direto(edital, inscricao)
        cenarios.desfechar(
            edital,
            gestor,
            convocacao,
            nomes_da_convocacao.INDEFERIMENTO,
            f"f117-in-{numero}",
            "Não apresentou os documentos.",
        )
        cenario.indeferidas.append((inscricao, convocacao))
    for _ in range(sem_resposta):
        numero += 1
        inscricao = inscrever(edital, numero)
        cenario.sem_resposta.append((inscricao, convocar_direto(edital, inscricao)))
    return cenario


def definir_documentos(edital, gestor, requisitos=DEFINICAO_DO_CENARIO_A, motivo="Portaria 1/2026"):
    return definir(actor=gestor, edital_id=edital.id, requisitos=requisitos, motivo=motivo)


def designar_direto(edital, pessoa, *, perfis=(), por="gil"):
    """A designação gravada direto, para os testes que não exercitam a gestão de acessos."""
    return DesignacaoParaFormalizacao.objects.create(
        edital=edital,
        pessoa=pessoa,
        perfis=[str(perfil) for perfil in perfis],
        motivo="Memorando 12/2026",
        designado_por=por,
        unidade_de_atuacao=edital.institution_scope,
        designado_em=timezone.now(),
    )


def falhar_na_montagem(monkeypatch, erro=None):
    """A exceção inesperada no meio da montagem do pacote (FR-3714): a segunda entrada falha."""
    from processo_seletivo.formalizacao.infrastructure import pacote

    erro = erro or RuntimeError("falha injetada")
    original = pacote.Pacote.acrescentar
    chamadas = {"n": 0}

    def acrescentar(self, *args, **kwargs):
        chamadas["n"] += 1
        if chamadas["n"] == 2:
            raise erro
        return original(self, *args, **kwargs)

    monkeypatch.setattr(pacote.Pacote, "acrescentar", acrescentar)
    return chamadas


def servido(resposta):
    """Os bytes de uma resposta de arquivo, com o arquivo fechado — e a resposta, não.

    `resposta.close()` dispara `request_finished`, que fecha a conexão do banco e derruba o resto do
    teste (`abrir_arquivo`, em `tests/fixtures/comissao.py`). Fecham-se só os recursos dela.
    """
    if not getattr(resposta, "streaming", False):
        return resposta.content
    conteudo = b"".join(resposta.streaming_content)
    for fechar in getattr(resposta, "_resource_closers", []):
        fechar()
    resposta._resource_closers = []
    return conteudo
