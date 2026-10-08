"""A unidade e a autoridade de um ato de publicação: lidas, conferidas e congeladas (060).

Edital e Retificação fazem a mesma coisa nos mesmos três passos: conferir a autoridade contra a
unidade do Edital e a data do ato, compor o documento com as duas, e congelar as duas na Publicação.
Um lugar só, para que os dois fluxos não divirjam na próxima mudança — e para que o documento e a
Publicação digam a mesma unidade, porque saem do mesmo objeto.
"""

from dataclasses import dataclass

from processo_seletivo.publicacoes.infrastructure.pdf import AutoridadeSignataria, UnidadeDoAto
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.application.autoridades import autoridade_para_o_ato
from processo_seletivo.unidades.application.selectors import exigir_unidade


@dataclass(frozen=True)
class ContextoDoAto:
    unidade: object
    autoridade: object
    data_do_ato: object

    @property
    def para_o_compositor(self):
        return UnidadeDoAto(cabecalho=tuple(self.unidade.cabecalho), local=self.unidade.local)

    @property
    def assinante(self):
        return AutoridadeSignataria(
            nome=self.autoridade.nome,
            cargo=self.autoridade.cargo,
            ato_de_nomeacao=self.autoridade.ato_de_nomeacao,
        )

    @property
    def colunas(self):
        """O que a Publicação congela — a autoridade e a unidade como estavam no ato (FR-1128)."""
        return {
            "signatory_id": self.autoridade.pk,
            "signatory_name": self.autoridade.nome,
            "signatory_role": self.autoridade.cargo,
            "signatory_appointment": self.autoridade.ato_de_nomeacao,
            **colunas_da_unidade(self.unidade),
        }


def colunas_da_unidade(unidade):
    return {
        "unidade_codigo": unidade.codigo,
        "unidade_sigla": unidade.sigla,
        "unidade_nome": unidade.nome,
        "unidade_cabecalho": list(unidade.cabecalho),
        "unidade_local": unidade.local,
    }


def unidade_para_o_compositor(unidade):
    """A Unidade registrada, como a prévia a compõe — a prévia não é ato e não congela nada."""
    return UnidadeDoAto(cabecalho=tuple(unidade.cabecalho), local=unidade.local)


def contexto_do_ato(edital, autoridade_id, now):
    """A unidade do Edital e a autoridade conferida, na data do ato no fuso institucional.

    A unidade é exigida registrada, e não ativa: a Retificação de um Edital de unidade desativada
    continua possível, porque o certame em curso precisa terminar (FR-1110).
    """
    unidade = exigir_unidade(edital.institution_scope)
    data_do_ato = now.astimezone(ZONA).date()
    autoridade = autoridade_para_o_ato(
        autoridade_id, unidade_codigo=unidade.codigo, data_do_ato=data_do_ato, now=now
    )
    return ContextoDoAto(unidade=unidade, autoridade=autoridade, data_do_ato=data_do_ato)
