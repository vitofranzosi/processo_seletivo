"""As regras dos Documentos Exigidos, e só elas.

Duas perguntas: a coleção é bem formada — chaves e ordens distintas, nome presente —, e cada
requisito se aplica a algo que existe no próprio Edital. A segunda é o que impede um requisito
inalcançável: um documento restrito a um Perfil que ninguém pode escolher nunca seria pedido a
ninguém, e ninguém perceberia.

O que **não** está aqui, deliberadamente: qualquer noção de condição, operador ou expressão. A
aplicabilidade tem quatro formas e elas se leem por ausência de campo, não por linguagem.
"""

from processo_seletivo.editais.domain.perfis import RecusaDeCampo

SEM_RESTRICAO = None


class DocumentRequirementValidationError(RecusaDeCampo):
    pass


def validate_document_requirement(requirement: dict) -> None:
    if not (requirement.get("key") or "").strip():
        raise DocumentRequirementValidationError(
            "O Documento Exigido precisa de uma chave estável.",
            campo="key",
            identidade=requirement.get("id", ""),
        )
    if not (requirement.get("name") or "").strip():
        raise DocumentRequirementValidationError(
            "O Documento Exigido precisa de um nome.",
            campo="name",
            identidade=requirement.get("id", ""),
        )
    if requirement.get("order", 0) < 0:
        raise DocumentRequirementValidationError(
            "A ordem do Documento Exigido não pode ser negativa.",
            campo="order",
            identidade=requirement.get("id", ""),
        )


def validate_document_requirements(requirements: list[dict], *, profiles: list[dict]) -> None:
    """Contra os Perfis **desta gravação**, e não contra o banco.

    O rascunho é substituído inteiro: um Perfil removido no mesmo envio já não existe, e conferir
    contra o banco recusaria o que a pessoa acabou de fazer. É a mesma decisão que
    `validate_stages` tomou para o vínculo com o Evento.
    """
    keys = [(requirement.get("key") or "").strip() for requirement in requirements]
    if len(keys) != len(set(keys)):
        raise DocumentRequirementValidationError(
            "Documentos Exigidos não podem repetir chave no Edital."
        )
    orders = [requirement.get("order", 0) for requirement in requirements]
    if len(orders) != len(set(orders)):
        raise DocumentRequirementValidationError(
            "Documentos Exigidos não podem repetir ordem no Edital."
        )
    por_perfil = {str(profile["id"]): profile for profile in profiles}
    for requirement in requirements:
        validate_document_requirement(requirement)
        _validate_aplicabilidade(requirement, por_perfil)


def _validate_aplicabilidade(requirement: dict, por_perfil: dict) -> None:
    perfil_id = requirement.get("profileId") or SEM_RESTRICAO
    modalidade_id = requirement.get("modalityId") or SEM_RESTRICAO
    if perfil_id is not SEM_RESTRICAO and str(perfil_id) not in por_perfil:
        raise DocumentRequirementValidationError(
            "O Documento Exigido aponta um Perfil que não é deste Edital.",
            campo="profileId",
            identidade=requirement.get("id", ""),
        )
    if modalidade_id is SEM_RESTRICAO:
        return
    perfis = [por_perfil[str(perfil_id)]] if perfil_id is not SEM_RESTRICAO else por_perfil.values()
    modalidades = {
        str(modalidade["id"])
        for profile in perfis
        for modalidade in profile.get("competitionModalities") or []
    }
    if str(modalidade_id) not in modalidades:
        # A mensagem separa os dois casos porque a correção é outra: sem Perfil declarado, a
        # modalidade não existe em Edital nenhum; com Perfil declarado, ela existe mas é de outro.
        motivo = (
            "não pertence ao Perfil declarado"
            if perfil_id is not SEM_RESTRICAO
            else "não é de nenhum Perfil deste Edital"
        )
        raise DocumentRequirementValidationError(
            f"O Documento Exigido aponta uma modalidade que {motivo}.",
            campo="modalityId",
            identidade=requirement.get("id", ""),
        )


def aplicaveis(requirements: list[dict], *, profile_id: str, modality_id: str | None) -> list[dict]:
    """Os requisitos que valem para uma inscrição — as quatro combinações, e nada além.

    Função pura sobre o conteúdo publicado: é ela que a entrega 4 usa para decidir o que pedir ao
    candidato, e é aqui que a decisão fica, longe de qualquer view.
    """
    escolhidos = []
    for requirement in requirements:
        perfil = requirement.get("profileId") or SEM_RESTRICAO
        modalidade = requirement.get("modalityId") or SEM_RESTRICAO
        if perfil is not SEM_RESTRICAO and str(perfil) != str(profile_id):
            continue
        if modalidade is not SEM_RESTRICAO and (
            modality_id is None or str(modalidade) != str(modality_id)
        ):
            continue
        escolhidos.append(requirement)
    return sorted(escolhidos, key=lambda item: item.get("order", 0))


def modelo_do_requisito(conteudo: dict, requisito: dict) -> dict | None:
    """O Anexo que este requisito manda usar, resolvido **dentro daquela versão** (020, FR-020).

    Mora no domínio, e não em cada tela, porque as duas telas que a fazem — o portal, que oferece o
    modelo ao candidato, e a mesa, que mostra à banca o que estava valendo — precisam responder a
    **mesma** pergunta sobre conteúdos **diferentes**: o portal lê a versão vigente, a mesa lê a
    versão aceita pela Inscrição. Duplicar a resolução faria as duas divergirem no dia em que a
    forma do anexo mudasse.

    Devolve `None` quando o requisito não fornece modelo — o caso mais comum — e também quando o
    vínculo aponta um anexo que aquela versão não publica. A segunda ausência não deveria existir,
    porque a validação a recusa como referência pendurada (FR-023); tratá-la aqui é o que impede
    uma versão antiga, publicada antes daquela regra, de quebrar a tela de quem avalia.
    """
    vinculo = requisito.get("attachmentId")
    if not vinculo:
        return None
    for anexo in conteudo.get("attachments") or []:
        if str(anexo.get("id")) == str(vinculo) and anexo.get("artifactId"):
            return {"rotulo": anexo.get("label", ""), "artefato_id": anexo["artifactId"]}
    return None
