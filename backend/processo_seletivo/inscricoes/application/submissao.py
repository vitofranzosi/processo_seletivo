"""O envio da inscrição: o ato que produz efeito administrativo.

**Tudo é revalidado aqui, e nada é herdado da tela** (FR-060). A tela validou para não oferecer o
que seria recusado; ela não é fronteira de segurança, e entre o que ela mostrou e o que chega
podem ter passado uma Retificação, o fim do prazo, o cancelamento do Edital ou um POST montado à
mão. Dez eixos, e a lista está escrita como lista de propósito: uma verificação que some não
aparece como erro, aparece como inscrição aceita que não devia ter sido.
"""

import hashlib
from datetime import date

from django.conf import settings
from django.db import IntegrityError, connection, transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain.documentos import aplicaveis
from processo_seletivo.inscricoes.application.rascunho import (
    _apagar_depois_do_commit,
    _modalidade_escolhida,
    _rascunho_travado,
    _versao_vigente,
    ator_do_candidato,
    requisitos_da_inscricao,
)
from processo_seletivo.inscricoes.domain.arquivos import ASSINATURA_PDF, resumo
from processo_seletivo.inscricoes.domain.protocolo import gerar
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao, ValorDeFato
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap
from processo_seletivo.shared.idempotency import reserve

SUBMETER = "inscricao:submeter"
TENTATIVAS_DE_PROTOCOLO = 5


def _travar_o_par(inscricao):
    """Serializa **este candidato neste Edital**, antes de qualquer leitura que decida o ato.

    **Por que não `select_for_update` sobre as inscrições dele.** Travar linhas não serializa a
    ausência delas: nas duas primeiras submissões concorrentes não existe linha submetida para
    bloquear, as duas contam zero e as duas passam pelo teto. E `count()` é agregação — não há o
    que travar num resultado que o banco calcula.

    O advisory lock trava o **par**, exista linha ou não, e é liberado no fim da transação. A chave
    é determinística: o mesmo par produz sempre o mesmo inteiro, e colidir custaria serialização
    desnecessária entre dois candidatos, nunca correção.

    Fora do PostgreSQL é no-op, e é honesto que seja: SQLite serializa a escrita inteira, e a
    corrida que este lock impede não existe lá.
    """
    if connection.vendor != "postgresql":
        return
    material = f"{inscricao.identity_subject}:{inscricao.edital_id}".encode()
    chave = int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=True)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [chave])


def _travar_o_edital(inscricao):
    """`FOR SHARE` no Edital, para que a versão lida não mude debaixo deste ato.

    Compatível entre submissões — várias pessoas enviam ao mesmo tempo sem se bloquear — e
    conflitante com o `FOR UPDATE` que a publicação de Retificação toma sobre a mesma linha
    (`publicacoes/application/retificacoes.py:611`). É isso que impede uma Retificação de ser
    publicada **entre** a leitura da versão vigente e a gravação do ato.
    """
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM processos_edital WHERE id = %s FOR SHARE", [str(inscricao.edital_id)]
        )


def edital_foi_retificado(inscricao, versao_vigente) -> bool:
    """A versão que a pessoa reconheceu deixou de ser a vigente (FR-059, FR-059a).

    Compara com a **reconhecida**, e não com a vigente de quando ela abriu: confirmar uma vez vale
    até que outra versão passe a vigorar, e comparar com a de abertura faria o aviso voltar a cada
    tentativa de envio.
    """
    return inscricao.versao_reconhecida_id != versao_vigente.pk


def documentos_que_a_retificacao_invalida(inscricao, versao):
    """O que a Retificação deixou de exigir — e que, por isso, precisa sair.

    Enquanto ele estiver lá, o envio é recusado por documento inaplicável e o candidato não tem o
    que fazer: a tela lista os requisitos **vigentes**, e o arquivo órfão não aparece em nenhum
    deles. É um beco, e a saída não pode ser apagar em silêncio — daí a lista, mostrada antes de
    a pessoa confirmar (FR-031, FR-059).
    """
    aplicaveis_agora = {
        str(requisito["id"])
        for requisito in aplicaveis(
            versao.content.get("documentRequirements") or [],
            profile_id=str(inscricao.profile_id),
            modality_id=None if inscricao.modality_id is None else str(inscricao.modality_id),
        )
    }
    por_id = {
        str(requisito.get("id")): requisito
        for requisito in versao.content.get("documentRequirements") or []
    }
    return [
        {
            "id": str(documento.requirement_id),
            "requisito": por_id.get(str(documento.requirement_id), {}).get(
                "name", "documento que deixou de ser exigido"
            ),
            "arquivo": documento.nome_original,
        }
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
        if str(documento.requirement_id) not in aplicaveis_agora
    ]


def reconhecer_versao(*, identidade, inscricao, versao, correlation_id=""):
    """Registra que a pessoa viu a alteração — e descarta o que a alteração tornou inaplicável.

    As duas coisas juntas, numa transação: confirmar que leu e ficar com um documento que o Edital
    não exige mais deixaria a inscrição num estado que só o envio revelaria, e revelaria como
    recusa sem saída.
    """
    with command_context() as agora:
        travada = _rascunho_travado(inscricao, versao.content, agora)
        caminhos = []
        for documento in DocumentoSubmetido.objects.filter(
            inscricao=travada,
            requirement_id__in=[
                item["id"] for item in documentos_que_a_retificacao_invalida(travada, versao)
            ],
        ):
            caminhos.append(documento.arquivo.name)
            documento.delete()
            record_event(
                actor=ator_do_candidato(identidade, travada.edital),
                permission="inscricao:remover",
                operation="REMOVER",
                aggregate=travada,
                now=agora,
                correlation_id=correlation_id,
                reason=f"requisito {documento.requirement_id}",
            )
        compare_and_swap(
            Inscricao.objects,
            pk=travada.pk,
            expected_revision=travada.revision,
            versao_reconhecida=versao,
        )
        travada.refresh_from_db()
        for caminho in caminhos:
            _apagar_depois_do_commit(caminho)
        return travada


def pendencias_para_enviar(conteudo, inscricao) -> list[str]:
    """Os requisitos obrigatórios sem documento — o que impede enviar, nomeado (FR-056)."""
    enviados = {
        str(documento.requirement_id)
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
    }
    return [
        requisito.get("name", "")
        for requisito in requisitos_da_inscricao(conteudo, inscricao)
        if requisito.get("required", True) and str(requisito["id"]) not in enviados
    ]


def enviar_inscricao(
    *, identidade, inscricao, declaracoes, idempotency_key, correlation_id="", fatos=None
):
    """Revalida tudo, grava o ato e devolve a Inscrição enviada.

    A idempotência é a do projeto, e não uma inventada aqui: duplo clique e reenvio do mesmo POST
    reservam a mesma chave e devolvem o mesmo resultado. A unicidade persistente é a segunda
    barreira, e é ela que responde se duas requisições escaparem por caminhos diferentes (FR-061).
    """
    ator = ator_do_candidato(identidade, inscricao.edital)
    with command_context() as agora:
        idem = reserve(
            actor=ator,
            operation=f"inscricao:submeter:{inscricao.pk}",
            key=idempotency_key,
            payload={},
        )
        if idem.result_id:
            return Inscricao.objects.get(pk=idem.result_id)
        # As duas travas vêm **antes** de qualquer leitura que decida o ato, e nessa ordem: o par
        # candidato–Edital, que serializa o teto; e o Edital em `FOR SHARE`, que impede uma
        # Retificação de ser publicada entre a leitura da versão e a gravação. Uma redação anterior
        # afirmava, em comentário, que a versão era lida depois da trava — e o código a lia antes.
        _travar_o_par(inscricao)
        _travar_o_edital(inscricao)
        versao = _versao_vigente(inscricao.edital_id)
        conteudo = versao.content
        # 1 e 2 — período aberto e Edital recebendo; e a trava, que resolve o estado obsoleto.
        travada = _rascunho_travado(inscricao, conteudo, agora)
        # 3 — a versão aceita é a que a pessoa reconheceu; se mudou, ela revê antes de confirmar.
        if edital_foi_retificado(travada, versao):
            raise DomainError(
                "edital_updated",
                "O Edital foi atualizado. Revise as alterações antes de confirmar sua inscrição.",
                409,
            )
        # 4 — o Perfil continua existindo no conteúdo que passa a valer.
        if not _perfil_existe(conteudo, travada.profile_id):
            raise DomainError(
                "profile_not_available",
                "O Perfil desta inscrição não existe mais no Edital vigente.",
                409,
            )
        # 5 — a modalidade continua sendo do Perfil, e continua obrigatória quando há escolha.
        modalidade = _modalidade_escolhida(conteudo, travada.profile_id, travada.modality_id)
        # 6 e 7 — só documentos aplicáveis, e todos os obrigatórios presentes.
        _conferir_documentos(conteudo, travada)
        pendentes = pendencias_para_enviar(conteudo, travada)
        if pendentes:
            raise DomainError(
                "missing_required_documents",
                "Falta enviar: " + ", ".join(pendentes) + ".",
                422,
            )
        # 8 — formato, tamanho e integridade do que está guardado.
        _conferir_arquivos(travada)
        # 9 — as duas declarações, obrigatórias e no ato.
        if not (declaracoes.get("veracidade") and declaracoes.get("ciencia")):
            raise DomainError(
                "declarations_required",
                "As duas declarações são obrigatórias para enviar a inscrição.",
                422,
            )
        # 10 — o teto de Inscrições por candidato neste Edital (D-3), já serializado pelo par.
        _conferir_o_teto(travada, conteudo)
        # 11 — os fatos que o Edital declara, na forma que ele declarou.
        valores = _valores_dos_fatos(conteudo, travada, fatos or {})
        # 12 — unicidade, garantida pelo banco; aqui só se transforma em recusa legível.
        _gravar_o_ato(travada, modalidade=modalidade, versao=versao, agora=agora)
        # O congelamento é da **mesma transação** que muda o status: um valor gravado fora dela
        # existiria para uma inscrição que não chegou a ser submetida, e uma submissão sem os
        # valores seria classificável sobre fato que ninguém declarou.
        _congelar(travada, valores, versao=versao, agora=agora)
        travada.refresh_from_db()
        record_event(
            actor=ator,
            permission=SUBMETER,
            operation="SUBMETER",
            aggregate=travada,
            now=agora,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            previous_state=Inscricao.Status.RASCUNHO,
            # Edital, versão e Perfil, que é o que a Constituição exige que se possa responder
            # depois; sem CPF e sem nome de arquivo (FR-078, FR-090).
            reason=(f"edital {travada.edital_id} versao {versao.pk} perfil {travada.profile_id}"),
        )
        idem.result_id = travada.pk
        idem.result_type = "Inscricao"
        idem.response_status = 201
        idem.save()
        return travada


def _conferir_o_teto(inscricao, conteudo):
    """Quantas Inscrições esta pessoa já enviou neste Edital, e quantas o Edital admite (D-3).

    **A serialização é do par, e já aconteceu** — em `_travar_o_par`, no início do ato. Aqui a
    consulta é comum de propósito: `select_for_update` num `count()` não travaria coisa alguma.

    **Conta apenas submetidas.** Rascunho não é ato: abandonar um não pode custar um direito, e a
    `009` já o trata assim em toda parte.
    """
    teto = conteudo.get("maxInscricoesPorCandidato")
    if teto is None:
        return
    ja_enviadas = (
        Inscricao.objects.filter(
            identity_subject=inscricao.identity_subject,
            edital_id=inscricao.edital_id,
            status=Inscricao.Status.SUBMETIDA,
        )
        .exclude(pk=inscricao.pk)
        .count()
    )
    if ja_enviadas >= teto:
        raise DomainError(
            "registration_limit_reached",
            f"Este Edital admite {teto} inscrição(ões) por candidato, e você já enviou "
            f"{ja_enviadas}.",
            409,
        )


def _valores_dos_fatos(conteudo, inscricao, informados):
    """Os fatos declarados pelo Perfil, com o valor informado, na forma do tipo publicado.

    Não há valor opcional: se o Edital declara o fato, ele é exigido. Declarar um fato é dizer que
    uma regra publicada o consome, e o que fazer com ausência é decisão do **cálculo**, declarada
    em `whenMissing` — não tolerância aqui.
    """
    perfil = next(
        (
            item
            for item in conteudo.get("profiles") or []
            if str(item.get("id")) == str(inscricao.profile_id)
        ),
        None,
    )
    valores = []
    for fato in (perfil or {}).get("declaredFacts") or []:
        bruto = (informados.get(str(fato["id"])) or "").strip()
        if not bruto:
            raise DomainError(
                "declared_fact_required",
                f"Informe {fato.get('label', 'o dado exigido')} para enviar a inscrição.",
                422,
            )
        try:
            if fato["type"] == "DATA":
                valores.append((fato["id"], date.fromisoformat(bruto), None))
            else:
                valores.append((fato["id"], None, int(bruto)))
        except ValueError as exc:
            raise DomainError(
                "declared_fact_invalid",
                f"{fato.get('label', 'O dado exigido')} não está na forma que o Edital declarou.",
                422,
            ) from exc
    return valores


def _congelar(inscricao, valores, *, versao, agora):
    """O que a pessoa informou, gravado sob a versão que vigorava no instante do ato."""
    ValorDeFato.objects.bulk_create(
        [
            ValorDeFato(
                inscricao=inscricao,
                fato_id=fato_id,
                valor_data=valor_data,
                valor_inteiro=valor_inteiro,
                congelado_em=agora,
                versao=versao,
            )
            for fato_id, valor_data, valor_inteiro in valores
        ]
    )


def _gravar_o_ato(inscricao, *, modalidade, versao, agora):
    """A gravação, com o protocolo sorteado de novo se colidir.

    Duas unicidades protegem esta tabela, e elas não significam a mesma coisa: a de identidade,
    Edital e Perfil diz "esta pessoa já enviou"; a do protocolo diz "sorteei um número que já
    existe". Traduzir as duas na mesma recusa faria o candidato ler que já se inscreveu quando o
    que aconteceu foi um sorteio infeliz — e ele não teria o que fazer com essa informação.
    """
    for tentativa in range(TENTATIVAS_DE_PROTOCOLO):
        protocolo = _protocolo_inedito(agora.year)
        try:
            with transaction.atomic():
                compare_and_swap(
                    Inscricao.objects,
                    pk=inscricao.pk,
                    expected_revision=inscricao.revision,
                    status=Inscricao.Status.SUBMETIDA,
                    modality_id=modalidade,
                    submitted_at=agora,
                    protocolo=protocolo,
                    versao_aceita=versao,
                    declaracoes_aceitas_em=agora,
                )
            return
        except IntegrityError as exc:
            if Inscricao.objects.filter(protocolo=protocolo).exclude(pk=inscricao.pk).exists():
                if tentativa < TENTATIVAS_DE_PROTOCOLO - 1:
                    continue
                raise DomainError(
                    "protocol_generation_failed",
                    "Não foi possível gerar o protocolo. Tente novamente.",
                    500,
                ) from exc
            raise DomainError(
                "duplicate_submission", "Esta inscrição já foi enviada.", 409
            ) from exc


def _perfil_existe(conteudo, profile_id) -> bool:
    return any(
        str(perfil.get("id")) == str(profile_id) for perfil in conteudo.get("profiles") or []
    )


def _conferir_documentos(conteudo, inscricao):
    """Nenhum documento guardado pode pertencer a requisito que deixou de se aplicar (FR-044).

    O caminho que chega aqui é o do tempo passando: o arquivo foi aceito quando o requisito valia,
    e uma Retificação o restringiu depois. Recusar o envio é o que impede a inscrição carregar
    documento que ninguém pediu.
    """
    aplicaveis_agora = {
        str(requisito["id"]) for requisito in requisitos_da_inscricao(conteudo, inscricao)
    }
    intrusos = [
        str(documento.requirement_id)
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
        if str(documento.requirement_id) not in aplicaveis_agora
    ]
    if intrusos:
        raise DomainError(
            "document_not_applicable",
            "Há documento enviado para requisito que não se aplica mais a esta inscrição. "
            "Revise os documentos antes de enviar.",
            409,
        )


def _conferir_arquivos(inscricao):
    """Formato, tamanho e integridade do que está guardado — no ato do envio.

    É o momento em que o arquivo deixa de ser rascunho e passa a ser peça de um ato administrativo.
    Conferir de novo custa uma leitura por documento, uma vez por inscrição, e é o que sustenta a
    afirmação de que o que a comissão vai abrir é o que o candidato enviou (FR-053a, FR-060).
    """
    limite = settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES
    for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao):
        with documento.arquivo.open("rb") as conteudo:
            if not conteudo.read(len(ASSINATURA_PDF)).startswith(ASSINATURA_PDF):
                raise DomainError(
                    "stored_file_invalid",
                    f"O arquivo de '{documento.nome_original}' não é mais um PDF válido. "
                    "Envie o documento novamente.",
                    422,
                )
            conteudo.seek(0)
            if resumo(conteudo) != documento.content_hash:
                raise DomainError(
                    "stored_file_corrupted",
                    f"O arquivo de '{documento.nome_original}' não confere com o que foi "
                    "recebido. Envie o documento novamente.",
                    422,
                )
        if documento.tamanho > limite:
            raise DomainError(
                "file_too_large",
                f"O arquivo de '{documento.nome_original}' excede o limite.",
                422,
            )


def _protocolo_inedito(ano: int) -> str:
    """Sorteia até achar um que ainda não existe; a unicidade final é do banco.

    Cinco tentativas e depois falha alto: com trinta e um caracteres e oito posições, colidir cinco
    vezes seguidas não é azar — é sinal de que alguma coisa está errada, e insistir esconderia.
    """
    for _ in range(TENTATIVAS_DE_PROTOCOLO):
        protocolo = gerar(ano)
        if not Inscricao.objects.filter(protocolo=protocolo).exists():
            return protocolo
    raise DomainError(
        "protocol_generation_failed",
        "Não foi possível gerar o protocolo. Tente novamente.",
        500,
    )
