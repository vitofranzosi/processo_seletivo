"""As regras dos Documentos Exigidos, e só elas.

Duas perguntas: a coleção é bem formada — chaves e ordens distintas, nome presente —, e cada
requisito se aplica a algo que existe no próprio Edital. A segunda é o que impede um requisito
inalcançável: um documento restrito a um Perfil que ninguém pode escolher nunca seria pedido a
ninguém, e ninguém perceberia.

O que **não** está aqui, deliberadamente: qualquer noção de condição, operador ou expressão. A
aplicabilidade tem cinco formas e elas se leem por ausência de campo, não por linguagem. A quinta,
`modalityCode`, é a da `044`: a Modalidade de um código **em todos os Perfis que a têm** — "todo
candidato PcD", que o Edital escreve numa frase e o recorte por identidade só dizia em N linhas.
"""

from dataclasses import dataclass

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
    codigo = requirement.get("modalityCode") or SEM_RESTRICAO
    if codigo is not SEM_RESTRICAO:
        _validate_recorte_por_codigo(requirement, codigo, por_perfil)
        return
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


def _validate_recorte_por_codigo(requirement: dict, codigo: str, por_perfil: dict) -> None:
    """As três recusas do recorte transversal que a gravação já sabe responder (044, D-010).

    **Em qualquer etapa**, e é deliberado: o rascunho confere os documentos contra os Perfis de cada
    gravação, e já recusa assim o documento cuja Modalidade exata deixou de existir. Por isso a
    etapa Perfis pode ser recusada por causa de um documento — e é por isso que toda mensagem daqui
    **nomeia o documento**: quem renomeou uma Modalidade não está olhando para a lista de
    documentos, e precisa saber qual deles ficaria sem ninguém a quem ser pedido.

    A coerência de denominação **não** está aqui: renomear é edição em curso, e travar a gravação a
    cada renomeação travaria o trabalho no meio. Ela é da publicação (R-007).
    """
    nome = requirement.get("name", "")
    identidade = requirement.get("id", "")
    if (requirement.get("profileId") or SEM_RESTRICAO) is not SEM_RESTRICAO or (
        requirement.get("modalityId") or SEM_RESTRICAO
    ) is not SEM_RESTRICAO:
        raise DocumentRequirementValidationError(
            f"O Documento Exigido '{nome}' recorta pela modalidade '{codigo}' em todos os Perfis, "
            "e por isso não pode declarar também um Perfil ou a modalidade de um Perfil. Escolha "
            "um recorte só.",
            campo="modalityCode",
            identidade=identidade,
        )
    com_o_codigo = [
        (perfil, modalidade)
        for perfil in por_perfil.values()
        for modalidade in perfil.get("competitionModalities") or []
        if str(modalidade.get("code") or "").strip() == codigo
    ]
    if not com_o_codigo:
        raise DocumentRequirementValidationError(
            f"O Documento Exigido '{nome}' é pedido de quem concorre na modalidade '{codigo}', "
            "mas nenhum Perfil deste Edital tem modalidade com esse código. Ele não seria pedido a "
            "ninguém.",
            campo="modalityCode",
            identidade=identidade,
        )
    for perfil, modalidade in com_o_codigo:
        ampla = perfil.get("generalCompetitionModalityId")
        if ampla and str(ampla) == str(modalidade.get("id")):
            raise DocumentRequirementValidationError(
                f"O Documento Exigido '{nome}' é pedido de quem concorre na modalidade "
                f"'{codigo}', mas ela é a ampla concorrência no Perfil "
                f"'{_rotulo_do_perfil(perfil)}'. A ampla concorrência não recorta documento: use "
                "'Todas as modalidades'.",
                campo="modalityCode",
                identidade=identidade,
            )


# ---------------------------------------------------------------------------
# A aplicabilidade (044): o veredito de cada documento, e não só o filtro
# ---------------------------------------------------------------------------

OBRIGATORIO = "OBRIGATORIO"
FACULTATIVO = "FACULTATIVO"
NAO_SE_APLICA = "NAO_SE_APLICA"
SITUACOES = (OBRIGATORIO, FACULTATIVO, NAO_SE_APLICA)

TODOS = "TODOS"
PERFIL = "PERFIL"
PERFIL_E_MODALIDADE = "PERFIL_E_MODALIDADE"
MODALIDADE_EM_TODOS_OS_PERFIS = "MODALIDADE_EM_TODOS_OS_PERFIS"
# A forma que a #161 recusa na publicação quando outro Perfil tem modalidade de mesma
# denominação. Ela continua existindo como forma porque há versões publicadas antes da recusa, e
# inscrições que as aceitaram.
TODOS_COM_MODALIDADE_DE_UM_PERFIL = "TODOS_COM_MODALIDADE_DE_UM_PERFIL"
FORMAS = (
    TODOS,
    PERFIL,
    PERFIL_E_MODALIDADE,
    MODALIDADE_EM_TODOS_OS_PERFIS,
    TODOS_COM_MODALIDADE_DE_UM_PERFIL,
)


@dataclass(frozen=True)
class Recorte:
    """A quem o documento é pedido: a forma, e os parâmetros que ela usa."""

    forma: str
    perfil_id: str | None = None
    modalidade_id: str | None = None
    modalidade_codigo: str | None = None


@dataclass(frozen=True)
class Veredito:
    """O que um documento é para uma inscrição, e por quê (044, D-003).

    É a mesma forma que a linha da lista exigida grava: um veredito, uma linha. `requisito` é o
    documento como está no conteúdo, e é daí que a tela lê nome e instrução.
    """

    requisito: dict
    situacao: str
    recorte: Recorte
    divergente_do_publicado: bool = False


def recorte_de(requisito: dict) -> Recorte:
    """A forma do recorte, lida por presença de campo."""
    perfil = requisito.get("profileId") or SEM_RESTRICAO
    modalidade = requisito.get("modalityId") or SEM_RESTRICAO
    codigo = requisito.get("modalityCode") or SEM_RESTRICAO
    if codigo is not SEM_RESTRICAO:
        return Recorte(MODALIDADE_EM_TODOS_OS_PERFIS, modalidade_codigo=str(codigo))
    if perfil is not SEM_RESTRICAO and modalidade is not SEM_RESTRICAO:
        return Recorte(PERFIL_E_MODALIDADE, perfil_id=str(perfil), modalidade_id=str(modalidade))
    if perfil is not SEM_RESTRICAO:
        return Recorte(PERFIL, perfil_id=str(perfil))
    if modalidade is not SEM_RESTRICAO:
        return Recorte(TODOS_COM_MODALIDADE_DE_UM_PERFIL, modalidade_id=str(modalidade))
    return Recorte(TODOS)


def aplicabilidade(conteudo: dict, *, profile_id: str, modality_id: str | None) -> list[Veredito]:
    """O veredito de **cada** Documento Exigido para uma inscrição, na ordem declarada (FR-705).

    É a regra única. O cartão público, o rascunho, o bloqueio do envio, a gravação da lista e a
    reconstrução leem daqui — e o `aplicaveis` abaixo é só o filtro sobre ela. Devolver o veredito
    inteiro, e não o filtro, é o que permite gravar o "não se aplica" com a razão (FR-717): quem
    recebesse só os aplicáveis teria de **deduzir** o resto, e deduzir é recalcular (D-003).

    O recorte por código se resolve **no Perfil da inscrição**: o documento vale quando a Modalidade
    que ela escolheu, lida ali, tem aquele código (FR-701). O PcD do C1 e o PcD do C2 são objetos
    distintos; o que eles têm em comum é o código, e é só isso que o recorte afirma.
    """
    perfis = _perfis(conteudo)
    perfil_da_inscricao = perfis.get(str(profile_id))
    modalidade_escolhida = _modalidade_do_perfil(perfil_da_inscricao, modality_id)
    vereditos = []
    for requisito in sorted(
        conteudo.get("documentRequirements") or [], key=lambda item: item.get("order", 0)
    ):
        recorte = recorte_de(requisito)
        aplica = _se_aplica(recorte, profile_id, modality_id, modalidade_escolhida)
        divergente = (
            not aplica
            and recorte.forma == TODOS_COM_MODALIDADE_DE_UM_PERFIL
            and modalidade_escolhida is not None
            and _rotulo_da_modalidade(modalidade_escolhida)
            in _denominacoes_alargadas(requisito, perfis)
        )
        if not aplica:
            situacao = NAO_SE_APLICA
        elif requisito.get("required", True):
            situacao = OBRIGATORIO
        else:
            situacao = FACULTATIVO
        vereditos.append(Veredito(requisito, situacao, recorte, divergente))
    return vereditos


def aplicaveis(conteudo: dict, *, profile_id: str, modality_id: str | None) -> list[dict]:
    """Os requisitos que valem para uma inscrição, e nada além — o filtro sobre `aplicabilidade`.

    Função pura sobre o conteúdo publicado: é ela que decide o que pedir ao candidato, e é aqui que
    a decisão fica, longe de qualquer view. Recebe o **conteúdo**, e não só a coleção de
    documentos, porque o recorte por código precisa dos Perfis para ler o código da Modalidade
    escolhida.
    """
    return [
        veredito.requisito
        for veredito in aplicabilidade(conteudo, profile_id=profile_id, modality_id=modality_id)
        if veredito.situacao != NAO_SE_APLICA
    ]


def _se_aplica(recorte: Recorte, profile_id, modality_id, modalidade_escolhida) -> bool:
    if recorte.forma == TODOS:
        return True
    if recorte.forma == PERFIL:
        return recorte.perfil_id == str(profile_id)
    if recorte.forma == PERFIL_E_MODALIDADE:
        return (
            recorte.perfil_id == str(profile_id)
            and modality_id is not None
            and (recorte.modalidade_id == str(modality_id))
        )
    if recorte.forma == TODOS_COM_MODALIDADE_DE_UM_PERFIL:
        return modality_id is not None and recorte.modalidade_id == str(modality_id)
    # MODALIDADE_EM_TODOS_OS_PERFIS
    return modalidade_escolhida is not None and (
        str(modalidade_escolhida.get("code") or "").strip() == recorte.modalidade_codigo
    )


def perfis_que_o_documento_publicado_alcanca(documento: dict, perfis) -> tuple:
    """O que a #161 pergunta, e a Mesa também: `(dono, modalidade, outros)`.

    Um documento "Todos os Perfis" + a Modalidade de um Perfil é pedido, pelo portal, só no Perfil
    `dono` — a aplicação é por identidade. O documento publicado, sem Perfil declarado, escreve o
    grupo **pelo nome**, e por isso o exige de todo Perfil com modalidade de mesma denominação: os
    `outros`. Lista vazia é a forma coerente; lista cheia é a divergência.

    Mora aqui, e não na validação, porque tem dois leitores (044, R-004): a publicação, que a
    impede, e a lista exigida, que a mostra a quem analisa (FR-727). Dois códigos para a mesma
    pergunta divergiriam no primeiro ajuste de rótulo.
    """
    lista = list(perfis.values()) if isinstance(perfis, dict) else list(perfis)
    dono, modalidade = next(
        (
            (perfil, item)
            for perfil in lista
            for item in perfil.get("competitionModalities") or []
            if str(item.get("id")) == str(documento.get("modalityId"))
        ),
        (None, None),
    )
    if dono is None:
        return None, None, []
    rotulo = _rotulo_da_modalidade(modalidade)
    if not rotulo:
        return dono, modalidade, []
    outros = [
        perfil
        for perfil in lista
        if perfil is not dono
        and any(
            _rotulo_da_modalidade(item) == rotulo
            for item in perfil.get("competitionModalities") or []
        )
    ]
    return dono, modalidade, outros


def _denominacoes_alargadas(documento, perfis) -> set[str]:
    _dono, modalidade, outros = perfis_que_o_documento_publicado_alcanca(documento, perfis)
    return {_rotulo_da_modalidade(modalidade)} if outros else set()


def rotulo_da_modalidade(modalidade: dict) -> str:
    """O que o documento publicado escreve: o nome, e o código quando não há nome."""
    return _rotulo_da_modalidade(modalidade)


def _rotulo_da_modalidade(modalidade: dict | None) -> str:
    if not modalidade:
        return ""
    return str(modalidade.get("name") or modalidade.get("code") or "").strip()


def _rotulo_do_perfil(perfil: dict | None) -> str:
    if not perfil:
        return ""
    return str(perfil.get("code") or perfil.get("name") or "").strip()


def _perfis(conteudo: dict) -> dict:
    return {
        str(perfil.get("id")): perfil
        for perfil in conteudo.get("profiles") or []
        if isinstance(perfil, dict) and perfil.get("id")
    }


def _modalidade_do_perfil(perfil: dict | None, modality_id) -> dict | None:
    if perfil is None or modality_id is None:
        return None
    return next(
        (
            item
            for item in perfil.get("competitionModalities") or []
            if str(item.get("id")) == str(modality_id)
        ),
        None,
    )


def denominacao_do_codigo(conteudo: dict, codigo: str) -> str:
    """A denominação que o Edital dá ao código, lida no primeiro Perfil que o tem.

    Qualquer um serve: a publicação impede denominações diferentes para um código que algum
    documento transversal refere (FR-706). Sem nenhum Perfil com o código, devolve o próprio código
    — a validação já recusou esse documento, e aqui só não se inventa nome.
    """
    for perfil in conteudo.get("profiles") or []:
        for modalidade in perfil.get("competitionModalities") or []:
            if str(modalidade.get("code") or "").strip() == codigo:
                return _rotulo_da_modalidade(modalidade) or codigo
    return codigo


def razao_legivel(veredito: Veredito, conteudo: dict) -> str:
    """A razão escrita para quem lê (UX-081): a quem o documento é pedido, pela **denominação**."""
    recorte = veredito.recorte
    perfis = _perfis(conteudo)
    perfil = _rotulo_do_perfil(perfis.get(recorte.perfil_id)) if recorte.perfil_id else ""
    if recorte.forma == TODOS:
        frase = "pedido de todos os candidatos"
    elif recorte.forma == PERFIL:
        frase = f"pedido de quem concorre ao Perfil {perfil}"
    elif recorte.forma == MODALIDADE_EM_TODOS_OS_PERFIS:
        denominacao = denominacao_do_codigo(conteudo, recorte.modalidade_codigo or "")
        frase = f"pedido de quem concorre em {denominacao}, em todos os Perfis"
    modalidade = None
    if recorte.forma in (PERFIL_E_MODALIDADE, TODOS_COM_MODALIDADE_DE_UM_PERFIL):
        dono = perfil
        for candidato in perfis.values():
            achada = _modalidade_do_perfil(candidato, recorte.modalidade_id)
            if achada is not None:
                modalidade = achada
                dono = dono or _rotulo_do_perfil(candidato)
                break
        frase = f"pedido de quem concorre ao Perfil {dono} em {_rotulo_da_modalidade(modalidade)}"
    if veredito.situacao == NAO_SE_APLICA:
        frase = f"Não se aplica: {frase}"
    if veredito.divergente_do_publicado:
        # A denominação sai do **recorte**, e não do documento: numa linha gravada o recorte é o
        # registro, e o documento da versão é só de onde vêm nome e instrução.
        denominacao = _rotulo_da_modalidade(modalidade)
        frase += (
            f" — o Edital publicado o exigia de todo candidato em {denominacao}. O portal não o "
            "pediu a esta inscrição."
        )
    return frase


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
