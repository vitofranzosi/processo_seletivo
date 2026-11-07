"""O fundamento pré-redigido do indeferimento sem ".." (132, FR-4516, SC-1406, D-008).

A frase junta "nome: motivo" com "; " e termina em ponto. Quem confere escreve o motivo como frase,
e o texto saía com ".;" no meio e ".." no fim — os dois motivos do banco de demonstração terminam
em ponto.
"""

from processo_seletivo.convocacao.domain.documentos import fundamento_das_pendencias

INICIO = "Documentação exigida na convocação não atendida — "


def test_o_ponto_final_do_motivo_cede_a_pontuacao_da_frase():
    texto = fundamento_das_pendencias(
        [
            ("Comprovante de escolaridade", "O arquivo está ilegível."),
            ("Laudo médico", "Emitido há mais de 90 dias."),
        ]
    )

    assert texto == (
        INICIO + "Comprovante de escolaridade: O arquivo está ilegível; "
        "Laudo médico: Emitido há mais de 90 dias."
    )
    assert ".." not in texto
    assert ".;" not in texto


def test_o_motivo_sem_ponto_sai_como_antes():
    texto = fundamento_das_pendencias([("Laudo médico", "emitido há mais de 90 dias")])

    assert texto == INICIO + "Laudo médico: emitido há mais de 90 dias."


def test_o_item_sem_motivo_sai_so_com_o_nome():
    texto = fundamento_das_pendencias([("Laudo médico", ""), ("Currículo", "sem assinatura.")])

    assert texto == INICIO + "Laudo médico; Currículo: sem assinatura."


def test_reticencias_e_interrogacao_ficam():
    """Só o ponto final simples cede: reticências e "?" dizem algo de quem conferiu."""
    texto = fundamento_das_pendencias(
        [("Laudo médico", "a data não se lê..."), ("Currículo", "é o do Edital anterior?")]
    )

    assert "a data não se lê...;" in texto
    assert "é o do Edital anterior?" in texto


def test_o_espaco_depois_do_ponto_nao_o_esconde():
    texto = fundamento_das_pendencias([("Laudo médico", "Emitido há mais de 90 dias.  ")])

    assert texto == INICIO + "Laudo médico: Emitido há mais de 90 dias."


def test_sem_pendencia_nao_ha_fundamento():
    assert fundamento_das_pendencias([]) == ""
