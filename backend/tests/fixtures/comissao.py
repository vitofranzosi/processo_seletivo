"""Um Processo publicado com Etapas — a precondição de tudo na 011.

`complete_draft` e `rascunho_de_selecao` não declaram Etapas: as features anteriores não
precisavam delas. A 011 precisa de duas no mesmo Edital, para que "alocado em A1 e não em A2"
seja demonstrável, e de um segundo Processo para que "Etapa de outro Processo" também seja.
"""

from tests.fixtures.edital import complete_draft, identificador
from tests.fixtures.publicacao import publish_original

ETAPA_A1 = 410
ETAPA_A2 = 411
# Os Documentos Exigidos que a `012` precisa para abrir a inscrição como instrumento de trabalho.
# Ficam aqui, e não em `snapshot.py`, porque estes acompanham o mesmo `seed` das Etapas.
DOCUMENTO_A = 420
DOCUMENTO_B = 421


def etapas(seed=0, *, avaliacoes=None, maxima=None, minima=None):
    """As duas Etapas dos cenários. `avaliacoes` e `maxima` declaram o que a `012` acrescentou.

    Ficam opcionais de propósito: a maioria dos testes fala de Etapa **sem** declaração, que é o
    caso do Edital publicado antes do incremento — e é ali que a leitura da ausência vale.
    """
    declaracao = {}
    if avaliacoes is not None:
        declaracao["evaluationsPerRegistration"] = avaliacoes
    if maxima is not None:
        declaracao["maximumScore"] = maxima
    if minima is not None:
        declaracao["minimumScore"] = minima
    return [
        {
            "id": identificador(ETAPA_A1, seed),
            "name": "Análise documental",
            "order": 1,
            "eliminatory": True,
            "classificatory": False,
            "scheduleEventId": identificador(402, seed),
            **declaracao,
        },
        {
            "id": identificador(ETAPA_A2, seed),
            "name": "Prova didática",
            "order": 2,
            "eliminatory": False,
            "classificatory": True,
        },
    ]


def documentos_exigidos(seed=0):
    """Dois requisitos: um obrigatório para todos, um que ninguém precisa apresentar.

    O segundo existe para provar que **a lista é a dos requisitos**, e não a dos arquivos:
    requisito sem arquivo aparece como requisito sem arquivo (FR-025 da `012`).
    """
    return [
        {
            "id": identificador(DOCUMENTO_A, seed),
            "key": "identificacao",
            "name": "Documento de identificação",
            "instructions": "Frente e verso, em arquivo único.",
            "required": True,
            "order": 1,
        },
        {
            "id": identificador(DOCUMENTO_B, seed),
            "key": "diploma",
            "name": "Diploma de graduação",
            "required": True,
            "order": 2,
        },
    ]


def rascunho_com_etapas(seed=0, *, com_documentos=False, **declaracao):
    base = {**complete_draft(seed), "stages": etapas(seed, **declaracao)}
    if com_documentos:
        base["documentRequirements"] = documentos_exigidos(seed)
    return base


def publicar_processo_com_etapas(
    api_client, manager_headers, process_payload, *, seed=0, com_documentos=False, **declaracao
):
    """Cria, elabora, submete, homologa e publica — pelo canal administrativo, como a 009 faz."""
    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_com_etapas(seed, com_documentos=com_documentos, **declaracao),
    )


def constituir(gestor, processo, pessoas, *, prefixo="constituir"):
    """Constitui a comissão pelo command, e devolve `{subject: membro}`.

    `prefixo` existe porque a chave de idempotência é derivada da posição: constituir em duas
    chamadas separadas reusaria `...-0` com outro conteúdo, e a reserva recusaria — corretamente.
    """
    from processo_seletivo.comissoes.application.comissao import adicionar_membro

    membros = {}
    for indice, (subject, funcao) in enumerate(pessoas):
        membro, _ = adicionar_membro(
            actor=gestor,
            processo_id=processo.id,
            identity_subject=subject,
            funcao=funcao,
            idempotency_key=f"{prefixo}-{processo.id}-{indice}",
            correlation_id="fixture",
        )
        membros[subject] = membro
    return membros


def alocar_em(gestor, processo, membro, edital, etapa_id, *, chave=None):
    from processo_seletivo.comissoes.application.alocacao import alocar

    alocacao, _ = alocar(
        actor=gestor,
        processo_id=processo.id,
        membro_id=membro.id,
        edital_id=edital.id,
        etapa_id=etapa_id,
        idempotency_key=chave or f"alocar-{membro.id}-{etapa_id}",
        correlation_id="fixture",
    )
    return alocacao


def inscrever(edital, quantos=1, *, primeiro=1, documentos=()):
    """Inscrições **submetidas** — o único estado atribuível (FR-012).

    O protocolo é o que a tela mostra e o que a trilha guarda, então ele nasce aqui em vez de
    ficar em branco: sem ele, as asserções teriam de falar por UUID.
    """
    from django.utils import timezone

    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    criadas = []
    for numero in range(primeiro, primeiro + quantos):
        # **Nasce rascunho, e é promovida depois.** Documento de inscrição enviada não é alterado
        # nem criado — a guarda da 009 vale no agregado —, e a transição real acontece por
        # `compare_and_swap`, que atualiza pelo queryset. A fixture faz o mesmo percurso.
        inscricao = Inscricao.objects.create(
            created_at=agora,
            identity_subject=f"cpf:candidato-{numero:04d}",
            edital=edital,
            profile_id="00000000-0000-0000-0000-000000000401",
            nome=f"Candidata {numero}",
            cpf="111.444.777-35",
            cpf_normalizado="11144477735",
            email=f"candidata{numero}@exemplo.br",
        )
        for requirement_id in documentos:
            anexar(inscricao, requirement_id)
        Inscricao.objects.filter(pk=inscricao.pk).update(
            status=Inscricao.Status.SUBMETIDA,
            protocolo=f"{numero:04d}",
            submitted_at=agora,
            versao_aceita=versao,
            declaracoes_aceitas_em=agora,
        )
        inscricao.refresh_from_db()
        criadas.append(inscricao)
    return criadas


def anexar(inscricao, requirement_id, *, corpo=b"conteudo do documento"):
    """Um documento apresentado, com o resumo que a integridade confere depois.

    O `content_hash` nasce do conteúdo real: é ele que sustenta "o que o avaliador abre é o que o
    candidato enviou", e forjá-lo faria o teste de divergência não testar nada.
    """
    import hashlib

    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.utils import timezone

    from processo_seletivo.inscricoes.models import DocumentoSubmetido

    bytes_do_arquivo = b"%PDF-1.4\n" + corpo
    return DocumentoSubmetido.objects.create(
        inscricao=inscricao,
        requirement_id=requirement_id,
        arquivo=SimpleUploadedFile(
            "documento.pdf", bytes_do_arquivo, content_type="application/pdf"
        ),
        nome_original="documento.pdf",
        tamanho=len(bytes_do_arquivo),
        content_hash=hashlib.sha256(bytes_do_arquivo).hexdigest(),
        uploaded_at=timezone.now(),
    )


def abrir_arquivo(client, url):
    """Consome a resposta de arquivo e fecha **o arquivo** — não a resposta.

    A cópia verificada é um `SpooledTemporaryFile`, e deixá-la pendurada é o vazamento que a suíte
    trata como erro. Mas `resposta.close()` dispara `request_finished`, que fecha a conexão do
    banco e derruba o resto do teste: fecha-se o que precisa ser fechado.
    """
    resposta = client.get(url)
    resposta.conteudo_servido = b""
    if getattr(resposta, "streaming", False):
        # Os bytes ficam guardados na própria resposta: consumir o iterador uma segunda vez
        # devolveria vazio, e quem quer conferir o que foi servido precisa deles.
        resposta.conteudo_servido = b"".join(resposta.streaming_content)
        arquivo_servido = getattr(resposta, "file_to_stream", None)
        if arquivo_servido is not None:
            arquivo_servido.close()
    return resposta
