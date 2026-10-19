"""As entradas da demonstração na página de acesso (075, `D-003`).

**Tudo aqui é da demonstração, e sai inteiro quando o diretório institucional chegar.** O que fica
em `identidade.py` — os métodos de entrada, a sessão, os papéis — é o que a autenticação real
também usa; o que mora aqui só existe porque, sem diretório, alguém precisa escolher quem é.

Os dados são os do banco: as comissões vêm de `identidades_com_trabalho`, e o nome sugerido para
cada responsabilidade, de quem a exerceu na trilha de auditoria. Nada é inventado para preencher a
lista; responsabilidade que ninguém exerceu entra com `demo.<papel>`, que se denuncia na auditoria.
"""

from __future__ import annotations

import re

from django.db.models import Count

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.interface import identidade

# O ícone de cada responsabilidade na lista: a mesma família de traço do sprite da página.
ICONES = {
    "elaborador": "inscricao",
    "homologador": "escudo",
    "publicador": "documento",
    "gestor": "camadas",
    "julgador": "balanca",
    "auditor": "busca",
    "exportador": "lista",
    "participante-piloto-assistente": "frasco",
}

# Sujeitos da trilha que não são pessoas da equipe: o candidato tem eixo próprio, e a implantação é
# o comando que prepara o banco.
_FORA_DA_EQUIPE = ("cand:", "implantacao")

# A partir de quantas entradas a busca aparece (`FR-1695`). Abaixo disso, ela é um campo a mais
# entre a pessoa e uma lista que cabe inteira na tela.
LIMIAR_DA_BUSCA = 8


def iniciais(subject):
    partes = [p for p in re.split(r"[^A-Za-zÀ-ÿ]+", subject) if p]
    return "".join(p[0] for p in partes[:2]).upper() or "?"


def comissoes(escopo=identidade.ESCOPO_PADRAO):
    """Uma entrada por pessoa com vínculo ativo: presidir e avaliar **não são papéis**."""
    entradas = []
    for pessoa in comissao_selectors.identidades_com_trabalho(escopo):
        if pessoa["preside"]:
            responsabilidade = "Presidência de comissão"
        elif pessoa["etapas"]:
            responsabilidade = "Avaliação"
        else:
            responsabilidade = "Membro de comissão"
        detalhes = sorted(set(pessoa["preside"]) | set(pessoa["integra"]))
        if pessoa["etapas"]:
            plural = "s" if pessoa["etapas"] > 1 else ""
            detalhes.append(f"{pessoa['etapas']} Etapa{plural} alocada{plural}")
        if pessoa["pendentes"]:
            plural = "ões pendentes" if pessoa["pendentes"] > 1 else "ão pendente"
            detalhes.append(f"{pessoa['pendentes']} avaliaç{plural}")
        entradas.append(
            {
                "subject": pessoa["subject"],
                "iniciais": iniciais(pessoa["subject"]),
                "responsabilidade": responsabilidade,
                "detalhes": detalhes,
            }
        )
    return entradas


def _quem_exerceu(escopo):
    """Por permissão, quantas vezes cada pessoa da equipe a usou nesta trilha — uma consulta só."""
    contagem = {}
    linhas = (
        RegistroAuditoria.objects.filter(institution_scope=escopo)
        .values("actor_subject", "permission")
        .annotate(vezes=Count("event_id"))
    )
    for linha in linhas:
        if linha["actor_subject"].startswith(_FORA_DA_EQUIPE):
            continue
        contagem.setdefault(linha["permission"], {})[linha["actor_subject"]] = linha["vezes"]
    return contagem


def responsabilidades(escopo=identidade.ESCOPO_PADRAO):
    """Uma entrada por papel, com o nome de quem mais o exerceu neste ambiente.

    O nome é sugestão, e não inferência de papel: a trilha diz que alguém usou uma permissão, e o
    papel continua sendo o da entrada escolhida. O empate se desfaz pela ordem do nome, para que a
    lista não mude de uma abertura para outra.
    """
    exerceu = _quem_exerceu(escopo)
    entradas = []
    for chave, (rotulo, permissoes) in identidade.PAPEIS.items():
        placar = {}
        for permissao in permissoes:
            for subject, vezes in exerceu.get(permissao, {}).items():
                placar[subject] = placar.get(subject, 0) + vezes
        subject = min(placar, key=lambda s: (-placar[s], s)) if placar else f"demo.{chave}"
        entradas.append(
            {
                "chave": chave,
                "rotulo": rotulo,
                "descricao": identidade.DESCRICOES[chave],
                "icone": ICONES.get(chave, "camadas"),
                "subject": subject,
            }
        )
    return entradas
