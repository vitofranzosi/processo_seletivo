"""A reconciliação com a jornada anterior — na implantação, e não no primeiro acesso de ninguém.

**Por que aqui.** Enquanto ela não acontece, o identificador que decide a propriedade de cada
inscrição continua derivado da `SECRET_KEY`. Rotacionar a chave nesse intervalo tornaria o que a
pessoa submeteu inalcançável por ela — e em silêncio, porque nada quebra: a busca simplesmente
deixa de achar. Migração é o único ponto que roda antes de tudo, uma vez, em toda implantação
(FR-040).

**O que ela nunca faz**: reescrever `identity_subject` (FR-042), marcar endereço como verificado
(FR-043) ou escolher um dado para desempatar (FR-047). Ela copia; nunca atribui.

**O que ela faz quando não consegue.** Inscrição enviada sem CPF utilizável **interrompe** a
implantação (FR-046): a restrição que `inscricoes.0003` instala não caberia sobre ela, e seguir
exigiria escolher um número por conta própria. Grupo com mais de um `subject` é **relatado sem
interromper** (FR-044) — suas inscrições ficam intactas e sem novo dono, inalcançáveis pela área
até tratamento operacional. Rascunho sem CPF utilizável também é relatado, e também fica intacto
(FR-045).

Nada disso menciona CPF no registro técnico (FR-009): o relatório fala por identificador de
inscrição e por `subject`.
"""

import logging
import uuid

from django.db import migrations
from django.utils import timezone

# Função pura, sem dependência de modelo: a mesma conferência que a `009` aplica na captura. É a
# metade que a restrição de banco não consegue expressar — ela afirma onze dígitos, e os dígitos
# verificadores ficam aqui e no domínio (D-017).
from processo_seletivo.inscricoes.domain.pessoais import cpf_valido

logger = logging.getLogger("processo_seletivo.identidade.reconciliacao")

LIMITE_DO_RELATO = 20


def _utilizavel(cpf: str) -> bool:
    return bool(cpf) and len(cpf) == 11 and cpf.isdigit() and cpf_valido(cpf)


def _enumerar(identificadores):
    mostrados = ", ".join(str(item) for item in identificadores[:LIMITE_DO_RELATO])
    resto = len(identificadores) - LIMITE_DO_RELATO
    return f"{mostrados}{f' e mais {resto}' if resto > 0 else ''}"


def reconciliar(apps, schema_editor):
    Inscricao = apps.get_model("inscricoes", "Inscricao")
    CandidateIdentity = apps.get_model("identidade", "CandidateIdentity")

    inscricoes = list(
        Inscricao.objects.all()
        .order_by("-created_at")
        .values("id", "identity_subject", "cpf_normalizado", "nome", "status")
    )
    if not inscricoes:
        return

    # 1. A verificação que pode parar tudo. Antes de criar qualquer coisa: interromper depois de
    #    gravar metade deixaria o banco num estado que ninguém pediu.
    enviadas_sem_cpf = [
        registro["id"]
        for registro in inscricoes
        if registro["status"] == "SUBMETIDA" and not _utilizavel(registro["cpf_normalizado"])
    ]
    if enviadas_sem_cpf:
        raise RuntimeError(
            "A reconciliação da 010 não pode prosseguir: há inscrição enviada sem CPF utilizável, "
            "e a restrição que a próxima migração instala não caberia sobre ela. Seguir exigiria "
            "escolher um dado por conta própria, que é o que esta migração se proíbe. "
            f"Inscrições a tratar: {_enumerar(enviadas_sem_cpf)}."
        )

    # 2. Rascunho sem CPF utilizável: relatado, intacto, não reconciliado.
    rascunhos_sem_cpf = [
        registro["id"]
        for registro in inscricoes
        if registro["status"] != "SUBMETIDA" and not _utilizavel(registro["cpf_normalizado"])
    ]
    if rascunhos_sem_cpf:
        logger.warning(
            "Rascunhos sem CPF utilizável ficam intactos e não reconciliados: %s",
            _enumerar(rascunhos_sem_cpf),
        )

    # 3. Agrupa o que sobra. `subjects` é dicionário para preservar a ordem de chegada — a
    #    primeira inscrição de cada grupo é a mais recente, e é dela que sai o nome.
    grupos = {}
    for registro in inscricoes:
        cpf = registro["cpf_normalizado"]
        if not _utilizavel(cpf):
            continue
        grupo = grupos.setdefault(cpf, {"subjects": {}, "nome": "", "inscricoes": []})
        grupo["subjects"].setdefault(registro["identity_subject"], True)
        grupo["inscricoes"].append(registro["id"])
        if not grupo["nome"]:
            grupo["nome"] = registro["nome"]

    agora = timezone.now()
    criadas = 0
    for cpf, grupo in grupos.items():
        subjects = list(grupo["subjects"])
        if len(subjects) > 1:
            # Só acontece se a `SECRET_KEY` tiver rotacionado durante a vigência da `009`. Falhar
            # aqui é falhar onde alguém está olhando — e não na tela de um candidato às 23h.
            logger.warning(
                "CPF com mais de um identificador estável não gera identidade; inscrições "
                "intactas e sem novo dono. Identificadores: %s. Inscrições: %s.",
                _enumerar(subjects),
                _enumerar(grupo["inscricoes"]),
            )
            continue
        CandidateIdentity.objects.create(
            id=uuid.uuid4(),
            subject=subjects[0],
            nome=grupo["nome"],
            cpf_normalizado=cpf,
            created_at=agora,
        )
        criadas += 1

    logger.info("Reconciliação da 010: %d identidades materializadas.", criadas)


def desfazer(apps, schema_editor):
    """Reverter esta migração não apaga nada — e não precisa apagar.

    A primeira versão recusava a reversão, para não remover acesso legítimo de quem já tivesse
    associado credencial. Estava errada por dois motivos. O prático: quem reverte além daqui
    reverte também `0001`, que derruba as três tabelas — não há linha a preservar. O de projeto: a
    Constituição exige que a migração aplique nas duas rotas que a produção percorre, instalação
    limpa e upgrade incremental, e uma migração que recusa voltar torna a segunda inverificável.

    O que continua valendo é o que a ida garante: nenhuma inscrição mudou de titular, então voltar
    não devolve dono nenhum a ninguém.
    """


class Migration(migrations.Migration):
    dependencies = [
        ("identidade", "0001_identidade"),
        # A reconciliação lê `Inscricao` inteira, inclusive `cpf_normalizado` e `nome`, que a
        # segunda migração de `inscricoes` já garantia existirem.
        ("inscricoes", "0002_documento_submetido"),
    ]

    operations = [migrations.RunPython(reconciliar, desfazer)]
