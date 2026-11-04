"""A verificação, a montagem do pacote e o registro da exportação (117, US4 e US5).

**Dois passos síncronos para mais de uma pessoa** (D-018). A resposta do download é o ZIP, e o
navegador não mostra página: dizer *parcial* só depois deixaria o operador descobrir as exclusões ao
abrir o arquivo, se descobrir. Por isso:

- **a verificação** lê e confere todos os arquivos, sem montar pacote e sem guardar nada, e mostra
  o resultado com as pessoas excluídas e o motivo; devolve um comprovante assinado (D-024);
- **o download** confere o comprovante antes de ler qualquer arquivo, revalida as autorizações,
  relê **todas** as pessoas do alcance — inclusive as excluídas — na mesma passagem que monta o
  pacote, recompõe o resumo e só serve se ele for o mesmo. O ZIP servido é sempre exatamente o
  verificado (FR-3689, FR-3689b).

**Uma pessoa só é um clique** (FR-3685): com tudo íntegro, o ZIP; com falha, uma página com o
motivo, sem pacote e sem registro.

**Uma leitura por arquivo em cada passo** (FR-3690): o hash é conferido na mesma leitura que copia,
e a cópia vai para um temporário em memória até 2 MB. A pessoa entra no ZIP só inteira (FR-3694).

**A trava é de transação, e por servidor** (FR-3692, D-019): `pg_try_advisory_xact_lock` sem espera,
no início da transação da verificação ou da montagem. Sai no commit, no rollback ou com a conexão
fechada — inclusive com o worker morto — e não cobre a transferência, que acontece depois do commit.

**O registro é a única escrita** (FR-3693, FR-3698): gravado depois de o pacote estar montado e
antes de a resposta começar. Os eventos de falha — arquivo indisponível, integridade, recusa e
interrupção — vão para a trilha **depois** da transação da operação, em transação própria: o
rollback da montagem não os apaga.
"""

import logging
import uuid
from dataclasses import dataclass, field
from hashlib import sha256
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.formalizacao.application import comprovante
from processo_seletivo.formalizacao.application.conjunto import aptos, tamanho_legivel
from processo_seletivo.formalizacao.application.definir import perfis_do_edital, vigente
from processo_seletivo.formalizacao.domain import caminhos, nomes
from processo_seletivo.formalizacao.domain.autorizacao import inexistente, pode_acessar
from processo_seletivo.formalizacao.infrastructure.pacote import Pacote, manifesto
from processo_seletivo.formalizacao.models import ExportacaoDeFormalizacao
from processo_seletivo.portal.arquivos import LIMITE_EM_MEMORIA
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.arquivos import BLOCO

# O log diz só a classe do erro e o identificador do Edital: nada de nome, CPF ou nome de arquivo,
# nem a mensagem da exceção, que às vezes os carrega (FR-3703).
logger = logging.getLogger("processo_seletivo.formalizacao")


class LimiteExcedido(DomainError):
    """A seleção passa do limite configurado; recusada antes de ler arquivo algum (FR-3691)."""

    def __init__(self, pessoas, total, limite):
        super().__init__(
            nomes.LIMITE_EXCEDIDO,
            f"A seleção soma {_megabytes(total)}, acima do limite de {_megabytes(limite)} de uma "
            "exportação. Divida a seleção: o tamanho de cada pessoa está abaixo.",
            409,
        )
        self.pessoas = pessoas
        self.total = total
        self.limite = limite


class VerificacaoDefasada(DomainError):
    def __init__(self):
        super().__init__(nomes.VERIFICACAO_DEFASADA, nomes.DEFASADA, 409)


class PessoaIncompleta(DomainError):
    """A pessoa única com documento indisponível ou divergente: página com o motivo (FR-3685)."""

    def __init__(self, leitura):
        super().__init__(
            nomes.PESSOA_INCOMPLETA,
            f"O pacote desta pessoa não foi gerado: {leitura.causador.nome} — "
            f"{nomes.ROTULO_DA_SITUACAO[leitura.motivo]}. Nada foi baixado nem registrado.",
            409,
        )
        self.leitura = leitura


class ExportacaoInterrompida(DomainError):
    """A exceção inesperada, já desfeita e registrada (FR-3714)."""

    def __init__(self):
        super().__init__("formalizacao_exportacao_interrompida", nomes.INTERROMPIDA, 500)


def _megabytes(tamanho):
    return tamanho_legivel(tamanho)


def limite_em_bytes():
    return settings.EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB * 1024 * 1024


# ---------------------------------------------------------------------------
# A leitura
# ---------------------------------------------------------------------------


@dataclass
class Leitura:
    """O que a leitura dos arquivos de uma pessoa concluiu."""

    pessoa: object
    motivo: str | None = None
    causador: object = None
    #: `{objeto_id: sha256 lido}` dos arquivos que se leram até o fim.
    lidos: dict = field(default_factory=dict)
    #: `{objeto_id: caminho no pacote}` dos documentos que entraram.
    caminhos: dict = field(default_factory=dict)
    #: `{objeto_id: INDISPONIVEL | INTEGRIDADE}` de cada arquivo que falhou.
    falhas: dict = field(default_factory=dict)

    @property
    def incluida(self):
        return self.motivo is None


@dataclass
class Verificacao:
    """O resultado de compor e ler um alcance — o que a tela mostra e o que o resumo cobre."""

    edital: object
    designacao: object
    definicao: object
    alcance: str
    perfil_id: str
    pedidas: list
    pessoas: list

    @property
    def incluidas(self):
        return [leitura for leitura in self.pessoas if leitura.incluida]

    @property
    def excluidas(self):
        return [leitura for leitura in self.pessoas if not leitura.incluida]

    @property
    def resultado(self):
        return nomes.COMPLETO if not self.excluidas else nomes.PARCIAL

    @property
    def parcial(self):
        return self.resultado == nomes.PARCIAL

    @property
    def documentos(self):
        return sum(len(leitura.pessoa.incluiveis) for leitura in self.incluidas)

    @property
    def tamanho(self):
        return sum(leitura.pessoa.tamanho for leitura in self.incluidas)

    @property
    def tamanho_legivel(self):
        return _megabytes(self.tamanho)

    def conteudo(self):
        """O conteúdo verificado, que entra no resumo e nunca no comprovante (FR-3689b)."""
        return {
            "definicao": str(self.definicao.id),
            "designacao": str(self.designacao.id),
            "incluidas": [
                {
                    "inscricao": leitura.pessoa.inscricao_id,
                    "convocacao": leitura.pessoa.convocacao_id,
                    "chamada": leitura.pessoa.chamada_id,
                    "desfecho": str(leitura.pessoa.desfecho.id),
                    "documentos": [
                        {"origem": d.origem, "id": d.objeto_id, "sha256": d.hash_esperado}
                        for d in leitura.pessoa.incluiveis
                    ],
                }
                for leitura in sorted(self.incluidas, key=lambda x: x.pessoa.inscricao_id)
            ],
            "excluidas": [
                {
                    "inscricao": leitura.pessoa.inscricao_id,
                    "desfecho": str(leitura.pessoa.desfecho.id),
                    "documento": {
                        "origem": leitura.causador.origem,
                        "id": leitura.causador.objeto_id,
                    },
                    "motivo": nomes.MOTIVO_DA_EXCLUSAO[leitura.motivo],
                }
                for leitura in sorted(self.excluidas, key=lambda x: x.pessoa.inscricao_id)
            ],
        }

    @property
    def resumo(self):
        return comprovante.resumo_canonico(self.conteudo())


def _ler_pessoa(pessoa, pacote, falhas):
    """Lê cada arquivo incluível uma vez, conferindo o hash na mesma leitura (FR-3690).

    Com `pacote`, copia para temporários e, se a pessoa estiver inteira, a acrescenta ao ZIP. Os
    arquivos depois da primeira falha ainda se leem — cada divergência tem o seu evento (FR-3696) —,
    mas não se copiam: a pessoa já está fora (FR-3694).
    """
    leitura = Leitura(pessoa=pessoa)
    copias = []
    try:
        for documento in pessoa.incluiveis:
            copia = None
            if pacote is not None and leitura.motivo is None:
                copia = SpooledTemporaryFile(max_size=LIMITE_EM_MEMORIA)
            resumo = sha256()
            tamanho = 0
            try:
                with documento.fonte.arquivo.open("rb") as origem:
                    for bloco in iter(lambda origem=origem: origem.read(BLOCO), b""):
                        resumo.update(bloco)
                        tamanho += len(bloco)
                        if copia is not None:
                            copia.write(bloco)
            except (OSError, ValueError):
                # `ValueError` é o campo de arquivo sem arquivo associado: para quem lê, é o mesmo
                # arquivo que não está lá.
                if copia is not None:
                    copia.close()
                falhas.append((nomes.ARQUIVO_INDISPONIVEL, documento))
                leitura.falhas[documento.objeto_id] = nomes.INDISPONIVEL
                if leitura.motivo is None:
                    leitura.motivo, leitura.causador = nomes.INDISPONIVEL, documento
                continue
            calculado = resumo.hexdigest()
            leitura.lidos[documento.objeto_id] = calculado
            if calculado != documento.hash_esperado:
                if copia is not None:
                    copia.close()
                falhas.append(("INTEGRIDADE", documento))
                leitura.falhas[documento.objeto_id] = nomes.INTEGRIDADE
                if leitura.motivo is None:
                    leitura.motivo, leitura.causador = nomes.INTEGRIDADE, documento
                continue
            if copia is not None:
                copia.seek(0)
                copias.append((documento, copia, tamanho))
        if pacote is not None and leitura.incluida and copias:
            pasta = caminhos.pasta_da_pessoa(pessoa.protocolo, pessoa.nome)
            arquivos = caminhos.arquivos_da_pessoa(
                [(documento.requisito_id, documento.chave) for documento, _, _ in copias]
            )
            for documento, copia, tamanho in copias:
                caminho = caminhos.caminho(pasta, arquivos[documento.requisito_id])
                pacote.acrescentar(caminho, copia, instante=documento.enviado_em, tamanho=tamanho)
                leitura.caminhos[documento.objeto_id] = caminho
    finally:
        for _, copia, _ in copias:
            copia.close()
    return leitura


def _ler(pessoas, pacote, falhas):
    return [_ler_pessoa(pessoa, pacote, falhas) for pessoa in pessoas]


# ---------------------------------------------------------------------------
# A trava e a trilha
# ---------------------------------------------------------------------------


def _trancar(actor):
    """A trava consultiva de transação, sem espera, por servidor (FR-3692)."""
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_try_advisory_xact_lock(%s, %s)",
            [nomes.CLASSE_DA_TRAVA, nomes.chave_da_trava(actor.subject)],
        )
        livre = cursor.fetchone()[0]
    if not livre:
        raise DomainError(nomes.EXPORTACAO_EM_ANDAMENTO, nomes.EM_ANDAMENTO, 409)


def _evento(actor, operacao, aggregate, *, reason, correlation_id, detalhe=None):
    record_event(
        actor=actor,
        permission=nomes.CAPACIDADE,
        operation=operacao,
        aggregate=aggregate,
        now=timezone.now(),
        correlation_id=correlation_id,
        reason=reason,
        new_state="",
        new_revision=None,
        detalhe=detalhe,
    )


def _registrar_falhas(actor, falhas, correlation_id):
    """Os eventos de arquivo, cada um em transação própria, sem nome de arquivo (FR-3695)."""
    for operacao, documento in falhas:
        with transaction.atomic():
            _evento(
                actor,
                operacao,
                documento.objeto,
                reason=f"requisito {documento.requisito_id}",
                correlation_id=correlation_id,
            )


def _registrar_recusa(actor, edital, motivo, correlation_id):
    with transaction.atomic():
        _evento(actor, nomes.RECUSAR, edital, reason=motivo, correlation_id=correlation_id)


def _registrar_interrupcao(actor, edital, erro, correlation_id):
    logger.error(
        "exportacao_de_formalizacao_interrompida",
        extra={"edital": str(edital.id), "erro": type(erro).__name__},
    )
    with transaction.atomic():
        _evento(
            actor,
            nomes.INTERROMPER,
            edital,
            reason=type(erro).__name__,
            correlation_id=correlation_id,
        )


# ---------------------------------------------------------------------------
# O alcance
# ---------------------------------------------------------------------------


def _uuids(valores):
    try:
        return sorted({str(uuid.UUID(str(valor))) for valor in valores if str(valor).strip()})
    except ValueError:
        raise inexistente() from None


def _populacao(acesso, definicao, alcance, perfil_id, pedidas, *, estrito):
    """As pessoas do alcance, no alcance da designação. Fora dele, a operação inteira cai.

    `estrito` é a verificação e a pessoa única: um id que não é de pessoa apta no alcance é
    **inexistente** (FR-3682). No download, os ids vêm do comprovante, e a pessoa que deixou de
    estar apta entre os dois passos é **verificação defasada** (FR-3689b).
    """
    falta = inexistente if estrito else VerificacaoDefasada
    perfis = list(acesso.designacao.perfis) or None
    if alcance == nomes.RECORTE and perfil_id:
        conhecidos = {perfil.id for perfil in perfis_do_edital(acesso.edital)}
        if perfil_id not in conhecidos or not acesso.cobre(perfil_id):
            raise falta()
        perfis = [perfil_id]
    inscricoes = pedidas if alcance in (nomes.SELECAO, nomes.PESSOA) else None
    pessoas = aptos(
        acesso.edital,
        definicao=definicao,
        perfis=perfis,
        inscricoes=inscricoes,
        com_exportacoes=False,
    )
    if inscricoes is not None and set(inscricoes) - {p.inscricao_id for p in pessoas}:
        raise falta()
    return pessoas


def _exigir_documentos(pessoas):
    if not any(pessoa.incluiveis for pessoa in pessoas):
        raise DomainError(
            nomes.SEM_DOCUMENTO,
            "Não há documento definido para a formalização nestas pessoas. Nada foi lido.",
            409,
        )


def _exigir_limite(pessoas):
    total = sum(pessoa.tamanho for pessoa in pessoas)
    limite = limite_em_bytes()
    if total > limite:
        raise LimiteExcedido(pessoas, total, limite)


def _definicao(edital):
    definicao = vigente(edital)
    if definicao is None or not definicao.requisitos:
        raise DomainError(
            nomes.SEM_DOCUMENTO,
            "A condução ainda não definiu os documentos que vão ao setor. Nada foi lido.",
            409,
        )
    return definicao


# ---------------------------------------------------------------------------
# A verificação
# ---------------------------------------------------------------------------


def verificar(actor, *, edital_id, alcance, perfil_id="", pessoas=(), correlation_id=""):
    """Lê e confere todo o alcance, sem montar pacote, e devolve `(verificação, comprovante)`.

    O comprovante é `None` quando nenhuma pessoa é incluível: não há o que baixar (FR-3684).
    """
    if alcance not in (nomes.SELECAO, nomes.RECORTE):
        raise DomainError(nomes.ALCANCE_INVALIDO, "Escolha as pessoas ou todos os aptos.", 422)
    pedidas = _uuids(pessoas) if alcance == nomes.SELECAO else []
    if alcance == nomes.SELECAO and not pedidas:
        raise DomainError(
            nomes.SEM_PESSOA, "Marque ao menos uma pessoa, ou escolha todos os aptos.", 422
        )
    perfil_id = _uuids([perfil_id])[0] if perfil_id else ""
    acesso = pode_acessar(actor, edital_id)
    definicao = _definicao(acesso.edital)
    populacao = _populacao(acesso, definicao, alcance, perfil_id, pedidas, estrito=True)
    _exigir_documentos(populacao)
    try:
        _exigir_limite(populacao)
    except LimiteExcedido:
        _registrar_recusa(actor, acesso.edital, nomes.RECUSA_LIMITE, correlation_id)
        raise
    falhas = []
    try:
        with transaction.atomic():
            _trancar(actor)
            leituras = _ler(populacao, None, falhas)
    except DomainError:
        _registrar_falhas(actor, falhas, correlation_id)
        raise
    except Exception as erro:
        _registrar_falhas(actor, falhas, correlation_id)
        _registrar_interrupcao(actor, acesso.edital, erro, correlation_id)
        raise ExportacaoInterrompida() from None
    _registrar_falhas(actor, falhas, correlation_id)
    verificacao = Verificacao(
        edital=acesso.edital,
        designacao=acesso.designacao,
        definicao=definicao,
        alcance=alcance,
        perfil_id=perfil_id,
        pedidas=pedidas,
        pessoas=leituras,
    )
    with transaction.atomic():
        _evento(
            actor,
            nomes.VERIFICAR,
            acesso.edital,
            reason=(
                f"{nomes.ROTULO_DO_ALCANCE[alcance]}: {verificacao.resultado.lower()}, "
                f"{len(verificacao.incluidas)} de {len(verificacao.pessoas)} pessoas, "
                f"{verificacao.documentos} documentos."
            ),
            correlation_id=correlation_id,
            detalhe={
                "alcance": alcance,
                "resultado": verificacao.resultado,
                "incluidas": len(verificacao.incluidas),
                "total": len(verificacao.pessoas),
                "documentos": verificacao.documentos,
                "tamanho": verificacao.tamanho,
            },
        )
    emitido = comprovante.emitir(actor, verificacao) if verificacao.incluidas else None
    return verificacao, emitido


# ---------------------------------------------------------------------------
# A montagem
# ---------------------------------------------------------------------------


@dataclass
class Gerado:
    """O pacote pronto para servir, e o registro dele."""

    arquivo: object
    nome: str
    exportacao: ExportacaoDeFormalizacao


def _montar(
    actor,
    verificar_antes,
    *,
    acesso,
    definicao,
    alcance,
    perfil_id,
    pedidas,
    pessoas,
    correlation_id,
):
    """A transação da montagem: trava, lê e copia, confere, manifesta e registra (FR-3698).

    `verificar_antes(verificacao)` levanta a recusa quando o lido não é o esperado — o resumo
    diferente no download, a pessoa incompleta na exportação de uma pessoa só. Qualquer recusa ou
    exceção desfaz a transação, descarta o temporário e solta a trava; nada é servido.
    """
    falhas = []
    pacote = None
    try:
        with transaction.atomic():
            _trancar(actor)
            pacote = Pacote()
            leituras = _ler(pessoas, pacote, falhas)
            verificacao = Verificacao(
                edital=acesso.edital,
                designacao=acesso.designacao,
                definicao=definicao,
                alcance=alcance,
                perfil_id=perfil_id,
                pedidas=pedidas,
                pessoas=leituras,
            )
            verificar_antes(verificacao)
            agora = timezone.now()
            identificador = uuid.uuid4()
            pacote.acrescentar_manifesto(
                _manifesto(actor, verificacao, identificador, agora), instante=agora
            )
            quantidade = pacote.quantidade
            arquivo, tamanho, hash_do_pacote = pacote.fechar()
            exportacao = ExportacaoDeFormalizacao.objects.create(
                id=identificador,
                edital=acesso.edital,
                designacao=acesso.designacao,
                definicao=definicao,
                alcance=alcance,
                perfil_id=perfil_id or None,
                resultado=verificacao.resultado,
                pessoas=[_pessoa_do_registro(leitura) for leitura in leituras],
                documentos=[
                    {
                        "inscricao": leitura.pessoa.inscricao_id,
                        "origem": documento.origem,
                        "id": documento.objeto_id,
                        "sha256": leitura.lidos[documento.objeto_id],
                    }
                    for leitura in verificacao.incluidas
                    for documento in leitura.pessoa.incluiveis
                ],
                quantidade_de_arquivos=quantidade,
                tamanho=tamanho,
                hash_do_pacote=hash_do_pacote,
                exportado_por=actor.subject,
                unidade_de_atuacao=actor.institution_scope,
                exportado_em=agora,
            )
            _evento(
                actor,
                nomes.EXPORTAR,
                acesso.edital,
                reason=f"Exportação {exportacao.id}: {verificacao.resultado.lower()}.",
                correlation_id=correlation_id,
                detalhe={
                    "exportacao": str(exportacao.id),
                    "resultado": verificacao.resultado,
                    "incluidas": len(verificacao.incluidas),
                    "total": len(verificacao.pessoas),
                },
            )
    except DomainError:
        if pacote is not None:
            pacote.descartar()
        _registrar_falhas(actor, falhas, correlation_id)
        raise
    except Exception as erro:
        if pacote is not None:
            pacote.descartar()
        _registrar_falhas(actor, falhas, correlation_id)
        _registrar_interrupcao(actor, acesso.edital, erro, correlation_id)
        raise ExportacaoInterrompida() from None
    _registrar_falhas(actor, falhas, correlation_id)
    nome = caminhos.nome_do_pacote(
        f"{acesso.edital.number}/{acesso.edital.year}",
        timezone.localtime(exportacao.exportado_em),
        parcial=exportacao.resultado == nomes.PARCIAL,
    )
    return Gerado(arquivo=arquivo, nome=nome, exportacao=exportacao)


def _pessoa_do_registro(leitura):
    registro = {
        "inscricao": leitura.pessoa.inscricao_id,
        "convocacao": leitura.pessoa.convocacao_id,
        "situacao": nomes.INCLUIDA if leitura.incluida else nomes.NAO_INCLUIDA,
    }
    if not leitura.incluida:
        registro["motivo"] = nomes.MOTIVO_DA_EXCLUSAO[leitura.motivo]
    return registro


def baixar(actor, *, edital_id, token, correlation_id=""):
    """O download do pacote verificado: comprovante, autorizações, releitura, resumo (FR-3689)."""
    # A matriz primeiro: sem o papel é 403, fora do alcance é 404, e o comprovante de quem já não
    # alcança o Edital não chega a ser lido. Os dois antes de qualquer arquivo.
    acesso = pode_acessar(actor, edital_id)
    try:
        payload = comprovante.conferir(actor, token)
        if payload.get("edital") != str(acesso.edital.id):
            raise comprovante.invalida()
    except DomainError as recusa:
        motivo = (
            nomes.RECUSA_EXPIRADA
            if recusa.code == nomes.VERIFICACAO_EXPIRADA
            else nomes.RECUSA_INVALIDA
        )
        _registrar_recusa(actor, acesso.edital, motivo, correlation_id)
        raise
    try:
        if str(acesso.designacao.id) != payload["designacao"]:
            raise VerificacaoDefasada()
        definicao = vigente(acesso.edital)
        if definicao is None or str(definicao.id) != payload["definicao"]:
            raise VerificacaoDefasada()
        pessoas = _populacao(
            acesso,
            definicao,
            payload["alcance"],
            payload["perfil"],
            list(payload["pessoas"]),
            estrito=False,
        )
    except VerificacaoDefasada:
        _registrar_recusa(actor, acesso.edital, nomes.RECUSA_DEFASADA, correlation_id)
        raise
    try:
        _exigir_limite(pessoas)
    except LimiteExcedido:
        _registrar_recusa(actor, acesso.edital, nomes.RECUSA_LIMITE, correlation_id)
        raise

    def conferir_o_resumo(verificacao):
        if (
            verificacao.resumo != payload["resumo"]
            or verificacao.resultado != payload["resultado"]
            or not verificacao.incluidas
        ):
            raise VerificacaoDefasada()

    try:
        return _montar(
            actor,
            conferir_o_resumo,
            acesso=acesso,
            definicao=definicao,
            alcance=payload["alcance"],
            perfil_id=payload["perfil"],
            pedidas=list(payload["pessoas"]),
            pessoas=pessoas,
            correlation_id=correlation_id,
        )
    except VerificacaoDefasada:
        _registrar_recusa(actor, acesso.edital, nomes.RECUSA_DEFASADA, correlation_id)
        raise


def exportar_pessoa(actor, *, edital_id, inscricao_id, correlation_id=""):
    """A exportação de uma pessoa só, num clique (FR-3685)."""
    pedidas = _uuids([inscricao_id])
    acesso = pode_acessar(actor, edital_id)
    definicao = _definicao(acesso.edital)
    pessoas = _populacao(acesso, definicao, nomes.PESSOA, "", pedidas, estrito=True)
    _exigir_documentos(pessoas)
    try:
        _exigir_limite(pessoas)
    except LimiteExcedido:
        _registrar_recusa(actor, acesso.edital, nomes.RECUSA_LIMITE, correlation_id)
        raise

    def exigir_inteira(verificacao):
        if verificacao.excluidas:
            raise PessoaIncompleta(verificacao.excluidas[0])

    try:
        return _montar(
            actor,
            exigir_inteira,
            acesso=acesso,
            definicao=definicao,
            alcance=nomes.PESSOA,
            perfil_id="",
            pedidas=pedidas,
            pessoas=pessoas,
            correlation_id=correlation_id,
        )
    except PessoaIncompleta:
        _registrar_recusa(actor, acesso.edital, nomes.RECUSA_PESSOA_INCOMPLETA, correlation_id)
        raise


# ---------------------------------------------------------------------------
# O manifesto
# ---------------------------------------------------------------------------

COLUNAS = (
    "Protocolo",
    "Nome",
    "Perfil",
    "Chamada",
    "Requisito",
    "Momento",
    "Situação",
    "Caminho no pacote",
    "SHA-256",
    "Envio",
    "Conferência",
)


def _instante(valor):
    return timezone.localtime(valor).strftime("%d/%m/%Y %H:%M") if valor else ""


def frase_do_resultado(resultado, incluidas, total):
    if resultado == nomes.COMPLETO:
        return f"Pacote completo: {incluidas} de {total} pessoas incluídas"
    return f"Pacote parcial: {incluidas} de {total} pessoas incluídas"


def _manifesto(actor, verificacao, identificador, agora):
    from processo_seletivo.seguranca.application.acessos import nomes_dos_autores

    edital = verificacao.edital
    perfis = {perfil.id: perfil.nome for perfil in perfis_do_edital(edital)}
    alcance = nomes.ROTULO_DO_ALCANCE[verificacao.alcance]
    if verificacao.perfil_id:
        alcance += f" do Perfil {perfis.get(verificacao.perfil_id, verificacao.perfil_id)}"
    cabecalho = [
        ("Edital", f"{edital.number}/{edital.year} — {edital.title}"),
        ("Alcance", alcance),
        ("Versão da definição", str(verificacao.definicao.id)),
        ("Instante", _instante(agora)),
        ("Autor", nomes_dos_autores({actor.subject})[actor.subject]),
        ("Exportação", str(identificador)),
        (
            "Resultado",
            frase_do_resultado(
                verificacao.resultado, len(verificacao.incluidas), len(verificacao.pessoas)
            ),
        ),
    ]
    linhas = [list(COLUNAS)]
    for leitura in verificacao.pessoas:
        pessoa = leitura.pessoa
        for documento in pessoa.documentos:
            if documento.objeto_id in leitura.falhas:
                situacao = nomes.ROTULO_DA_SITUACAO[leitura.falhas[documento.objeto_id]]
            elif documento.incluivel and not leitura.incluida:
                situacao = "pessoa não incluída"
            else:
                situacao = documento.rotulo
            conferencia = (
                nomes.SEM_CONFERENCIA_NA_CONVOCACAO
                if documento.sem_conferencia
                else _instante(documento.conferido_em)
            )
            linhas.append(
                [
                    pessoa.protocolo,
                    pessoa.nome,
                    pessoa.perfil_nome,
                    pessoa.chamada,
                    documento.nome,
                    documento.momento,
                    situacao,
                    leitura.caminhos.get(documento.objeto_id, ""),
                    documento.hash_esperado,
                    _instante(documento.enviado_em),
                    conferencia,
                ]
            )
    return manifesto(cabecalho, linhas)
