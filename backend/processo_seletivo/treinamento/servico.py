"""Carregar, verificar e restaurar cenários (134, FR-4610 a FR-4626).

**Três garantias, e cada uma tem o seu lugar.**

1. *Só acrescenta.* Nenhum caminho deste módulo apaga linha, e nenhum altera linha que o gerador não
   criou: a escrita é dos comandos da aplicação, e o único `UPDATE` direto é o do manifesto.
2. *Tudo ou nada por cenário.* A montagem e o manifesto estão na mesma transação: se um passo
   recusa, o cenário inteiro some, e o que fica no banco é o que havia antes (FR-4612).
3. *Não sobrescreve.* Um cenário pronto não é tocado de novo pela carga, e um vestígio sem manifesto
   — um Processo com o código reservado que o gerador não reconhece — é relatado, não reaproveitado
   (FR-4614).

**Restaurar não é apagar** (D-002). Publicação, trilha e as tabelas append-only recusam exclusão,
por gatilho e por privilégio, e a Constituição a proíbe. Restaurar é criar a rodada seguinte do
cenário, do zero e com as datas de hoje, e cancelar a anterior pelos comandos de cancelamento —
que deixam o histórico inteiro, e tiram o Processo antigo da aba "Em andamento".
"""

from dataclasses import dataclass, field

from django.conf import settings
from django.db import transaction
from django.test.utils import override_settings
from django.utils import timezone

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.treinamento import ambiente
from processo_seletivo.treinamento.catalogo import CENARIOS, POR_CODIGO, concurso_da_rodada
from processo_seletivo.treinamento.construcao import GESTAO, MARCA, Montagem
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from processo_seletivo.treinamento.retrato import diferencas, retratar

PREFIXO_DO_CODIGO = "SIM-TREINAMENTO-"


class Recusa(Exception):
    """Uma recusa do gerador, com a frase para quem roda o comando."""


@dataclass
class Situacao:
    cenario: object
    manifesto: CenarioDeTreinamento | None = None
    vestigios: list = field(default_factory=list)
    problemas: list = field(default_factory=list)
    mudancas: list = field(default_factory=list)
    avisos: list = field(default_factory=list)

    @property
    def estado(self):
        if self.problemas:
            return "INCONSISTENTE"
        if self.manifesto is None:
            return "CONFLITO" if self.vestigios else "AUSENTE"
        if self.mudancas:
            return "EXERCITADO"
        return "INTACTO"


def escolher(codigos):
    """Os cenários pedidos, na ordem do catálogo; todos, sem pedido."""
    if not codigos:
        return list(CENARIOS)
    pedidos = {codigo.strip().upper() for codigo in codigos}
    desconhecidos = sorted(pedidos - set(POR_CODIGO))
    if desconhecidos:
        raise Recusa(
            f"Cenário desconhecido: {', '.join(desconhecidos)}. "
            f"Os do catálogo são {', '.join(POR_CODIGO)}."
        )
    return [cenario for cenario in CENARIOS if cenario.codigo in pedidos]


def autoridade_vigente(unidade, escolhida=None):
    """A autoridade que assina os atos fictícios — sem criar nenhuma, e sem mudar nenhuma.

    **O gerador não cria configuração institucional** (FR-4615): uma autoridade é registro da
    unidade, com motivo e trilha, e quem a cadastra é o Gestor pela tela.

    **E só usa, sem pedir, autoridade que já foi usada** (FR-4616). O primeiro ato praticado com uma
    autoridade grava `usada_em`, e a partir dali o nome, o cargo e a nomeação dela ficam imutáveis
    (060, FR-1121): um gerador que escolhesse uma autoridade recém-cadastrada congelaria, em
    silêncio, um registro que a equipe ainda pode estar completando. A suíte achou isto — o
    instantâneo linha a linha acusou a autoridade alterada. Sem autoridade já usada, a carga é
    recusada e diz como escolher uma por extenso, com `--autoridade`.
    """
    from processo_seletivo.shared.tempo import ZONA
    from processo_seletivo.unidades.application.selectors import autoridades_vigentes

    hoje = timezone.now().astimezone(ZONA).date()
    vigentes = list(autoridades_vigentes(unidade, hoje))
    if escolhida:
        for autoridade in vigentes:
            if str(autoridade.pk) == str(escolhida):
                return str(autoridade.pk)
        raise Recusa(f"A autoridade {escolhida} não é vigente na unidade {unidade}.")
    usadas = [autoridade for autoridade in vigentes if autoridade.usada_em is not None]
    if usadas:
        return str(usadas[0].pk)
    if not vigentes:
        raise Recusa(
            f"A unidade {unidade} não tem autoridade vigente para assinar os atos. Cadastre uma "
            "pela tela de autoridades do Gestor e rode de novo — o gerador não cria configuração "
            "institucional."
        )
    opcoes = "; ".join(f"{autoridade.pk} ({autoridade.cargo})" for autoridade in vigentes)
    raise Recusa(
        f"Nenhuma autoridade vigente da unidade {unidade} foi usada ainda, e o primeiro uso torna "
        "o cadastro dela imutável (FR-1121). Escolha uma por extenso com --autoridade, sabendo "
        f"disso: {opcoes}."
    )


def _vestigios(cenario, unidade):
    """Processos com o código reservado do cenário que nenhum manifesto reconhece."""
    numero = int(cenario.codigo[1:])
    base = f"{PREFIXO_DO_CODIGO}{numero:03d}"
    candidatos = ProcessoSeletivo.objects.filter(institution_scope=unidade).filter(
        institutional_code__in=[base] + [f"{base}-R{rodada}" for rodada in range(2, 100)]
    )
    reconhecidos = set(
        CenarioDeTreinamento.objects.filter(unidade=unidade, codigo=cenario.codigo).values_list(
            "processo_id", flat=True
        )
    )
    return [processo for processo in candidatos if processo.id not in reconhecidos]


def _conferir_propriedade(manifesto):
    """O que impede tratar o Processo do manifesto como do gerador (FR-4613, FR-4622)."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    problemas = []
    processo = manifesto.processo
    if not processo.institutional_code.startswith(PREFIXO_DO_CODIGO):
        problemas.append(f"o Processo {processo.id} não tem mais o código reservado.")
    if processo.institution_scope != manifesto.unidade:
        problemas.append("o Processo é de outra unidade que a do manifesto.")
    criacao = (
        RegistroAuditoria.objects.filter(aggregate_id=processo.id, operation="CRIAR")
        .order_by("occurred_at")
        .first()
    )
    if criacao is None or criacao.correlation_id != manifesto.correlation_id:
        problemas.append(
            "a trilha não mostra o Processo criado pelo gerador nesta rodada "
            f"(esperado {manifesto.correlation_id})."
        )
    registrados = set(manifesto.registros.get("edital", []))
    existentes = {
        str(pk) for pk in Edital.objects.filter(processo=processo).values_list("id", flat=True)
    }
    if not registrados <= existentes:
        problemas.append("um Edital registrado no manifesto não está mais no Processo.")
    return problemas


def situacao(cenario, unidade):
    manifesto = (
        CenarioDeTreinamento.objects.select_related("processo")
        .filter(
            unidade=unidade, codigo=cenario.codigo, situacao=CenarioDeTreinamento.Situacao.PRONTO
        )
        .first()
    )
    resultado = Situacao(
        cenario=cenario, manifesto=manifesto, vestigios=_vestigios(cenario, unidade)
    )
    if manifesto is None:
        return resultado
    resultado.problemas = _conferir_propriedade(manifesto)
    if not resultado.problemas:
        resultado.mudancas = diferencas(manifesto.retrato, retratar(manifesto.processo))
    if manifesto.versao_da_definicao != cenario.versao:
        resultado.avisos.append(
            f"gerado com a versão {manifesto.versao_da_definicao} da receita; a atual é "
            f"{cenario.versao}. Restaure para ter a atual."
        )
    if cenario.validade_dias is not None:
        vence = manifesto.criado_em + timezone.timedelta(days=cenario.validade_dias)
        if timezone.now() >= vence:
            resultado.avisos.append(
                f"o prazo do estado inicial venceu em {timezone.localtime(vence):%d/%m/%Y}: "
                "restaure para ter datas novas."
            )
    return resultado


def _proxima_rodada(cenario, unidade):
    ultima = (
        CenarioDeTreinamento.objects.filter(unidade=unidade, codigo=cenario.codigo)
        .order_by("-rodada")
        .values_list("rodada", flat=True)
        .first()
    )
    return (ultima or 0) + 1


def conflitos_de_montagem(cenario, unidade, rodada, ano):
    """O que impediria a rodada de nascer, conferido **antes** de qualquer escrita (FR-4614)."""
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    conflitos = []
    montagem = Montagem(
        codigo=cenario.codigo, rodada=rodada, unidade=unidade, autoridade_id="", titulo=""
    )
    if ProcessoSeletivo.objects.filter(
        institution_scope=unidade, institutional_code=montagem.codigo_do_processo
    ).exists():
        conflitos.append(f"já existe Processo {montagem.codigo_do_processo} na unidade.")
    if Edital.objects.filter(institution_scope=unidade, number=montagem.numero, year=ano).exists():
        conflitos.append(f"já existe Edital {montagem.numero}/{ano} na unidade.")
    if cenario.exige_fonte_de_demonstracao:
        if not getattr(settings, "SORTEIO_FONTE_DE_DEMONSTRACAO", False):
            conflitos.append(
                "a fonte de demonstração do sorteio não está ligada neste ambiente "
                "(SORTEIO_FONTE_DE_DEMONSTRACAO)."
            )
        elif OcorrenciaDaFonte.objects.filter(
            referencia=concurso_da_rodada(cenario.codigo, rodada)
        ).exists():
            conflitos.append(
                f"o concurso {concurso_da_rodada(cenario.codigo, rodada)} da fonte de "
                "demonstração já foi observado por outro certame."
            )
    return conflitos


def planejar(codigos, unidade):
    """O que a carga faria, sem escrever nada — a pré-visualização (FR-4604)."""
    plano = []
    ano = timezone.now().year
    for cenario in escolher(codigos):
        atual = situacao(cenario, unidade)
        if atual.manifesto is not None:
            plano.append((cenario, "MANTER", [f"rodada {atual.manifesto.rodada} já existe"]))
            continue
        if atual.vestigios:
            codigos_achados = ", ".join(p.institutional_code for p in atual.vestigios)
            plano.append((cenario, "RECUSAR", [f"Processo sem manifesto: {codigos_achados}"]))
            continue
        rodada = _proxima_rodada(cenario, unidade)
        conflitos = conflitos_de_montagem(cenario, unidade, rodada, ano)
        plano.append(
            (cenario, "RECUSAR" if conflitos else "CRIAR", conflitos or [f"rodada {rodada}"])
        )
    return plano


def _correio_inerte():
    """Nenhuma mensagem sai durante a montagem (FR-4634).

    A inscrição manda comprovante e a convocação comunica: são os comandos da aplicação, e eles
    enviam. O correio de memória do Django guarda a mensagem no processo e a descarta com ele; o
    domínio `.test` das pessoas fictícias é a segunda barreira, para o que escapasse disto.
    """
    return override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")


def montar(cenario, unidade, *, rodada, autoridade_id, saida=None, por="linha de comando"):
    """Uma rodada nova do cenário, inteira ou nenhuma, com o manifesto na mesma transação."""
    ano = timezone.now().year
    conflitos = conflitos_de_montagem(cenario, unidade, rodada, ano)
    if conflitos:
        raise Recusa(f"{cenario.codigo}: " + " ".join(conflitos))
    with _correio_inerte(), transaction.atomic():
        montagem = Montagem(
            codigo=cenario.codigo,
            rodada=rodada,
            unidade=unidade,
            autoridade_id=autoridade_id,
            titulo=cenario.nome,
            saida=saida,
        )
        cenario.montar(montagem)
        processo = ProcessoSeletivo.objects.get(pk=montagem.processo.id)
        return CenarioDeTreinamento.objects.create(
            unidade=unidade,
            codigo=cenario.codigo,
            rodada=rodada,
            versao_da_definicao=cenario.versao,
            processo=processo,
            correlation_id=montagem.correlacao,
            registros=montagem.registros,
            retrato=retratar(processo),
            banco=ambiente.banco_conectado(),
            criado_em=timezone.now(),
            criado_por=por,
        )


def carregar(codigos, unidade, *, saida=None, por="linha de comando", autoridade=None):
    """Cria só os cenários que não existem; relata e pula os demais (FR-4611)."""
    resultados = []
    plano = planejar(codigos, unidade)
    autoridade_id = None
    for cenario, decisao, motivos in plano:
        if decisao != "CRIAR":
            resultados.append((cenario, decisao, motivos))
            continue
        autoridade_id = autoridade_id or autoridade_vigente(unidade, autoridade)
        if saida is not None:
            saida.write(f"{cenario.codigo} — {cenario.nome}")
        try:
            manifesto = montar(
                cenario,
                unidade,
                rodada=_proxima_rodada(cenario, unidade),
                autoridade_id=autoridade_id,
                saida=saida,
                por=por,
            )
        except Exception as erro:  # noqa: BLE001 — a recusa do domínio vira linha do relatório
            resultados.append((cenario, "FALHOU", [_frase(erro)]))
            continue
        resultados.append(
            (
                cenario,
                "CRIADO",
                [f"rodada {manifesto.rodada}", manifesto.processo.institutional_code],
            )
        )
    return resultados


def _frase(erro):
    codigo = getattr(erro, "code", "") or erro.__class__.__name__
    detalhe = getattr(erro, "detail", None) or str(erro)
    return f"{codigo}: {detalhe}. Nada deste cenário foi gravado."


def plano_de_restauracao(codigo, unidade):
    """O que a restauração fará — e as recusas, antes de qualquer escrita (FR-4620 a FR-4623)."""
    cenario = escolher([codigo])[0]
    atual = situacao(cenario, unidade)
    if atual.manifesto is None:
        raise Recusa(
            f"{cenario.codigo} não tem rodada registrada nesta unidade: use "
            "carregar_cenarios_de_treinamento para criá-lo."
        )
    if atual.problemas:
        raise Recusa(
            f"{cenario.codigo}: a propriedade do Processo não se comprova — "
            + " ".join(atual.problemas)
            + " Nada foi alterado; examine o Processo antes de decidir."
        )
    rodada = _proxima_rodada(cenario, unidade)
    conflitos = conflitos_de_montagem(cenario, unidade, rodada, timezone.now().year)
    if conflitos:
        raise Recusa(f"{cenario.codigo}: " + " ".join(conflitos))
    processo = atual.manifesto.processo
    editais = list(
        Edital.objects.filter(processo=processo).exclude(
            status__in=[Edital.Status.ENCERRADO, Edital.Status.CANCELADO]
        )
    )
    return {
        "cenario": cenario,
        "manifesto": atual.manifesto,
        "rodada_nova": rodada,
        "a_cancelar": editais,
        "processo_a_cancelar": processo
        if processo.status
        not in (ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO)
        else None,
        "mudancas": atual.mudancas,
    }


def restaurar(codigo, unidade, *, saida=None, por="linha de comando", autoridade=None):
    """A rodada nova e o cancelamento da anterior, na mesma transação (FR-4624, FR-4625)."""
    from processo_seletivo.processos.application.finalizacao import cancel_edital, cancel_process

    plano = plano_de_restauracao(codigo, unidade)
    cenario, anterior = plano["cenario"], plano["manifesto"]
    autoridade_id = autoridade_vigente(unidade, autoridade)
    with _correio_inerte(), transaction.atomic():
        # A anterior sai de PRONTO **antes** de a nova nascer: a constraint de uma rodada em uso por
        # cenário recusaria as duas juntas — e é ela que garante que nunca convivam.
        CenarioDeTreinamento.objects.filter(pk=anterior.pk).update(
            situacao=CenarioDeTreinamento.Situacao.SUBSTITUIDO,
            substituido_em=timezone.now(),
        )
        novo = montar(
            cenario,
            unidade,
            rodada=plano["rodada_nova"],
            autoridade_id=autoridade_id,
            saida=saida,
            por=por,
        )
        CenarioDeTreinamento.objects.filter(pk=anterior.pk).update(substituido_por=novo)
        gestor = Montagem(
            codigo=cenario.codigo,
            rodada=anterior.rodada,
            unidade=unidade,
            autoridade_id="",
            titulo="",
        ).ator(GESTAO)
        motivo = (
            f"Cenário de treinamento {cenario.codigo} restaurado: substituído pela rodada "
            f"{novo.rodada} ({novo.processo.institutional_code}). {MARCA}."
        )
        correlacao = f"{anterior.correlation_id}-substituida"
        for edital in plano["a_cancelar"]:
            edital.refresh_from_db()
            cancel_edital(
                actor=gestor,
                edital_id=edital.id,
                expected_revision=edital.revision,
                reason=motivo,
                idempotency_key=f"{correlacao}-edital-{edital.id.hex[:12]}",
                correlation_id=correlacao,
            )
        if plano["processo_a_cancelar"] is not None:
            processo = ProcessoSeletivo.objects.get(pk=anterior.processo_id)
            cancel_process(
                actor=gestor,
                processo_id=processo.id,
                expected_revision=processo.revision,
                reason=motivo,
                idempotency_key=f"{correlacao}-processo",
                correlation_id=correlacao,
            )
    return anterior, novo
