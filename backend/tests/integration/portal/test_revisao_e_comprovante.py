"""A revisão, o envio e o comprovante, pela tela (US5 e US7 da 009).

Duas telas depois da identificação, e a segunda é esta. O que se prova aqui é o percurso: o que a
pessoa lê antes de confirmar, o que ela recebe depois, e o que acontece quando ela volta.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL


def _completar(inscricao, *, faltando=False):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    requisitos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if not faltando:
        requisitos.append((DOCUMENTO_DO_PERFIL, "diploma.pdf"))
    for requisito, nome in requisitos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_revisao_resume_tudo_com_editar_em_cada_bloco(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:revisao", args=[completa.id])).content.decode()

    assert "Professor de Informática" in corpo
    assert "Maria Silva" in corpo
    assert "rg.pdf" in corpo and "diploma.pdf" in corpo
    assert corpo.count("Editar") == 3, "oportunidade, dados e documentos"
    assert corpo.count(reverse("portal:inscricao", args=[completa.id])) >= 3


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_faltando_documento_a_revisao_nao_oferece_enviar(client, inscricao_de_maria):
    incompleta = _completar(inscricao_de_maria, faltando=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:revisao", args=[incompleta.id])).content.decode()

    assert "Falta enviar: Diploma de graduação" in corpo
    assert "Enviar inscrição" not in corpo
    assert "Declarações" not in corpo, "não se pede aceite do que não se pode enviar"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_leva_ao_comprovante(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    resposta = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    assert resposta["Location"] == reverse("portal:comprovante", args=[completa.id])
    corpo = client.get(resposta["Location"]).content.decode()
    enviada = Inscricao.objects.get()
    assert enviada.protocolo in corpo
    assert "Inscrição realizada" in corpo
    assert "Professor de Informática" in corpo
    assert "rg.pdf" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_marcar_as_declaracoes_o_envio_e_recusado(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    resposta = client.post(reverse("portal:revisao", args=[completa.id]), {"veracidade": "on"})

    assert "declarações são obrigatórias" in resposta.content.decode()
    assert Inscricao.objects.get().status == Inscricao.Status.RASCUNHO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_duplo_envio_pela_tela_nao_cria_duas(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    declaracoes = {"veracidade": "on", "ciencia": "on"}

    primeira = client.post(reverse("portal:revisao", args=[completa.id]), declaracoes)
    segunda = client.post(reverse("portal:revisao", args=[completa.id]), declaracoes)

    assert primeira["Location"] == segunda["Location"], "o segundo clique leva ao mesmo lugar"
    assert Inscricao.objects.filter(status=Inscricao.Status.SUBMETIDA).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_inscricao_enviada_nao_volta_para_a_revisao(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    revisao = client.get(reverse("portal:revisao", args=[completa.id]))
    inscricao = client.get(reverse("portal:inscricao", args=[completa.id]))

    assert revisao["Location"] == reverse("portal:comprovante", args=[completa.id])
    assert inscricao.status_code == 200, "a tela abre, e é a de uma inscrição enviada"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_e_privado_e_imprimivel(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    resposta = client.get(reverse("portal:comprovante", args=[completa.id]))

    assert "no-store" in resposta.headers["Cache-Control"]
    assert "@media print" in resposta.content.decode(), "a página se prepara para o papel"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_ja_enviou_reencontra_o_comprovante_na_selecao(client, inscricao_de_maria, selecao):
    """US7: voltar depois e achar o que fez, sem portal do candidato."""
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    corpo = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()

    assert "Ver comprovante" in corpo
    assert reverse("portal:comprovante", args=[completa.id]) in corpo
    assert "Continuar inscrição" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_o_comprovante_alheio_nao_e_alcancavel(client, inscricao_de_maria):
    from tests.fixtures.candidato import JOAO

    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )
    identificar(client, JOAO)

    assert client.get(reverse("portal:comprovante", args=[completa.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_das_declaracoes_recebe_o_foco_e_aponta_o_que_falta(client, inscricao_de_maria):
    """SC-UX-005: alcançar o motivo da recusa.

    Quem acionou o botão estava no fim da página, e `role=alert` anuncia o que **muda** numa página
    já carregada — não o que já veio no HTML da resposta. Sem mover o foco, para quem usa leitor de
    tela o envio simplesmente não acontece e nada é dito.
    """
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    corpo = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on"}
    ).content.decode()

    assert 'data-recusa' in corpo and 'tabindex="-1"' in corpo
    assert 'href="#ciencia"' in corpo, "o resumo leva à declaração que falta"
    assert 'href="#veracidade"' not in corpo, "a que foi marcada não é cobrada"
    assert "portal/recusa.js" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_nao_apaga_a_declaracao_ja_marcada(client, inscricao_de_maria):
    """SC-UX-007: nenhuma recusa obriga a repetir o que já estava certo."""
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    corpo = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on"}
    ).content.decode()

    marcada = corpo[corpo.index('id="veracidade"') :][:220]
    esquecida = corpo[corpo.index('id="ciencia"') :][:220]
    assert "checked" in marcada, "volta marcada"
    assert "checked" not in esquecida
    assert 'aria-invalid="true"' in esquecida, "e a que falta é anunciada como inválida"
    assert 'aria-invalid="true"' not in marcada


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_pode_ser_baixado_e_reencontrado(client, inscricao_de_maria):
    """L1 da auditoria de percurso: o comprovante precisa ser levável.

    O protocolo é a única prova que a pessoa leva, e sair da tela não pode significar perdê-la.
    Uma ação só: enquanto havia duas, elas dividiam a decisão — e a impressão da página era pior
    em tudo o que importa aqui.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    completa = _completar(inscricao_de_maria)
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-comprovante-imprimivel",
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert "Baixar o comprovante em PDF" in corpo, "e é a única ação"
    assert reverse("portal:comprovante-pdf", args=[enviada.id]) in corpo
    assert "Imprimir esta página" not in corpo, "duas ações dividiam a mesma decisão"
    assert 'class="principal"' in corpo and "a.principal{display:inline-block" in corpo, (
        "o link é estilizado como ação principal — `button.principal` o deixava sem estilo"
    )
    assert "Guarde o número do protocolo" in corpo
    assert "identifique-se com o mesmo CPF" in corpo, "diz como voltar a este comprovante"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_tres_etapas_dizem_onde_a_pessoa_esta(client, inscricao_de_maria):
    """L3: identificação, dados, documentos, revisão e comprovante eram cinco momentos sem nome.

    Quem se inscreve num concurso costuma fazê-lo uma vez na vida, e a incerteza sobre "quanto
    ainda falta" é o que faz fechar a aba.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    inscricao = client.get(reverse("portal:inscricao", args=[completa.id])).content.decode()
    assert "Etapa 1 de 3" in inscricao
    assert 'aria-label="Etapas da inscrição"' in inscricao

    revisao = client.get(reverse("portal:revisao", args=[completa.id])).content.decode()
    assert "Etapa 2 de 3" in revisao
    assert revisao.count('class="concluida"') == 1, "a primeira já passou"

    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-etapas",
    )
    comprovante = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()
    assert "Etapa 3 de 3" in comprovante
    assert comprovante.count('class="concluida"') == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_se_identifica_como_documento(client, inscricao_de_maria):
    """O comprovante é lido por quem não estava na tela.

    Pode ser apresentado numa banca, anexado a um recurso, guardado por um ano. Sem dizer de quem
    é, o que atesta e sob qual versão do Edital, é um texto com um código no meio.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    completa = _completar(inscricao_de_maria)
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-documento",
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert "Instituto Federal do Espírito Santo" in corpo, "o órgão que emitiu"
    assert "Comprovante de inscrição" in corpo
    assert enviada.protocolo in corpo
    assert "Versão do Edital" in corpo, "a que regras esta inscrição respondeu"
    assert "recebida</strong> pelo sistema" in corpo, "o que o documento atesta"
    assert "não implica deferimento" in corpo, "e o que ele não atesta"
    assert "recebido em" in corpo, "cada documento com a hora em que chegou"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_papel_nao_leva_navegacao_nem_botao(client, inscricao_de_maria):
    """No papel, um "Etapa 3 de 3" faz o comprovante parecer a captura de uma tela pela metade."""
    corpo = (
        __import__("pathlib")
        .Path("processo_seletivo/portal/templates/portal/base.html")
        .read_text(encoding="utf-8")
    )

    impressao = corpo[corpo.index("@media print{") :]
    for fora_do_papel in ("header.topo", ".nao-imprime", ".pular", ".etapas"):
        assert fora_do_papel in impressao.split("}")[0], f"{fora_do_papel} não vai para o papel"
    assert ".timbre{display:block" in impressao, "e o timbre só existe nele"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_permite_verificar_cada_arquivo(client, inscricao_de_maria):
    """D9: o que transforma o comprovante de lista em prova.

    Com o resumo criptográfico, o candidato demonstra depois que o arquivo em mãos é o que
    entregou, e a comissão afirma que o arquivo que abriu é o que foi recebido. Sem ele,
    "documento2.pdf" identifica tanto quanto um nome de arquivo identifica — quase nada.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
    from processo_seletivo.inscricoes.models import DocumentoSubmetido

    completa = _completar(inscricao_de_maria)
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-verificavel",
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    for documento in DocumentoSubmetido.objects.filter(inscricao=enviada):
        assert documento.content_hash in corpo, "o resumo inteiro, não um prefixo"
    assert "SHA-256" in corpo
    assert "shasum -a 256" in corpo, "e como conferi-lo"
    assert "certutil -hashfile" in corpo, "inclusive em Windows"
    assert "bytes" in corpo or "KB" in corpo, "o tamanho de cada arquivo"
    assert "Comprovante emitido em" in corpo, "o documento diz de quando é"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_cabe_em_uma_pagina(client, inscricao_de_maria):
    """Duas páginas separam o documento do que ele atesta.

    O que caía na segunda folha era justamente o parágrafo que diz o que o comprovante prova. O
    papel é tratado como o meio que é: corpo menor, dados em duas colunas, e nenhum documento
    partido ao meio.
    """
    corpo = (
        __import__("pathlib")
        .Path("processo_seletivo/portal/templates/portal/base.html")
        .read_text(encoding="utf-8")
    )

    impressao = corpo[corpo.index("@media print{") :]
    assert "@page{margin:" in impressao, "margem do papel definida pelo documento"
    assert "font-size:10.5pt" in impressao, "corpo dimensionado para papel, não para tela"
    assert ".dados{grid-template-columns:auto 1fr auto 1fr" in impressao, "dados em duas colunas"
    assert "break-inside:avoid" in impressao, "nenhum documento partido entre folhas"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_se_identifica_pelo_protocolo_no_titulo(client, inscricao_de_maria):
    """O navegador usa o `<title>` como nome do arquivo ao salvar em PDF.

    Sem o protocolo ali, o candidato termina com "Comprovante de inscrição — Cefor_Ifes.pdf" na
    pasta de downloads, indistinguível do comprovante de qualquer outra seleção — e é justamente o
    protocolo que identifica este.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    completa = _completar(inscricao_de_maria)
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-titulo",
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert f"<title>Comprovante {enviada.protocolo} — Cefor/Ifes</title>" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_traz_o_codigo_que_prova_que_e_ele(client, inscricao_de_maria):
    """O resumo de cada arquivo responde pelos anexos; este responde pelo papel.

    E o mesmo código aparece na consulta administrativa, porque é comparando os dois que se recusa
    um comprovante alterado.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
    from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao
    from processo_seletivo.inscricoes.models import DocumentoSubmetido

    completa = _completar(inscricao_de_maria)
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-codigo",
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    esperado = codigo_de_verificacao(
        enviada, DocumentoSubmetido.objects.filter(inscricao=enviada)
    )
    assert esperado in corpo
    assert "Código de verificação" in corpo
    assert "para confirmar que\n    nada foi alterado" in corpo or "nada foi alterado" in corpo


@pytest.fixture
def enviada(inscricao_de_maria):
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    return enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-pdf",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_em_pdf_e_um_arquivo_com_nome_proprio(client, enviada):
    """FR-063: gerado no servidor, e não impresso pelo navegador.

    Nome de arquivo próprio, sem o endereço que o navegador escreve na folha, e sem depender de
    quem imprime lembrar de desligar cabeçalhos.
    """
    identificar(client, MARIA)

    resposta = client.get(reverse("portal:comprovante-pdf", args=[enviada.id]))

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"
    assert f'filename="Comprovante {enviada.protocolo}.pdf"' in resposta["Content-Disposition"]
    assert "attachment" in resposta["Content-Disposition"], "veio buscar arquivo para guardar"
    assert "no-store" in resposta["Cache-Control"]
    assert resposta.content.startswith(b"%PDF-")


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_mesmo_comprovante_gera_sempre_o_mesmo_arquivo(client, enviada):
    """Determinismo é o que permite publicar o resumo do próprio documento.

    Se o arquivo mudasse a cada download — por um relógio lido na geração, por exemplo —, o resumo
    publicado deixaria de conferir na segunda vez, e a verificação viraria uma promessa quebrada.
    """
    from hashlib import sha256

    identificar(client, MARIA)
    endereco = reverse("portal:comprovante-pdf", args=[enviada.id])

    primeiro = client.get(endereco).content
    segundo = client.get(endereco).content

    assert primeiro == segundo
    pagina = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()
    assert sha256(primeiro).hexdigest() in pagina, "e a página publica o resumo do arquivo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_pdf_do_comprovante_diz_o_que_o_papel_precisa_dizer(client, enviada):
    """O que se lê num visualizador — protocolo, código, resumos e o que o documento atesta."""
    from processo_seletivo.inscricoes.models import DocumentoSubmetido

    identificar(client, MARIA)

    conteudo = client.get(reverse("portal:comprovante-pdf", args=[enviada.id])).content

    assert enviada.protocolo.encode() in conteudo
    assert b"COMPROVANTE DE INSCRI" in conteudo
    assert b"Instituto Federal do Esp" in conteudo
    for documento in DocumentoSubmetido.objects.filter(inscricao=enviada):
        assert documento.content_hash.encode() in conteudo, "o resumo de cada anexo"
    assert b"deferimento" in conteudo, "o que o documento não prova"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_pdf_de_outro_candidato_nao_e_entregue(client, enviada):
    """Titularidade decide, como em toda página da inscrição: conhecer o id não autoriza."""
    from tests.fixtures.candidato import JOAO

    identificar(client, JOAO)

    assert client.get(reverse("portal:comprovante-pdf", args=[enviada.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_rascunho_nao_tem_comprovante_em_pdf(client, inscricao_de_maria):
    """Não há o que comprovar antes do envio."""
    identificar(client, MARIA)

    resposta = client.get(reverse("portal:comprovante-pdf", args=[inscricao_de_maria.id]))

    assert resposta.status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_pdf_cabe_em_uma_pagina_no_caso_de_referencia(client, enviada):
    """Um comprovante de duas folhas se separa, e o que ia na segunda era o que ele atesta.

    O caso de referência tem três documentos e três resumos de 64 caracteres. Com muitos anexos o
    documento cresce, e aí a paginação é legítima — o rodapé de cada folha traz protocolo e código.
    """
    identificar(client, MARIA)

    conteudo = client.get(reverse("portal:comprovante-pdf", args=[enviada.id])).content

    assert conteudo.count(b"/Type /Page ") == 1
    assert b"P\\341gina 1 de 1" in conteudo or b"gina 1 de 1" in conteudo
