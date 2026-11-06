"""O agrupamento e a ordem fixa do nível 1 (127, FR-4082, FR-4083, FR-4085, D-016).

A derivação devolve um conjunto; a apresentação ordena sempre do mesmo jeito: as da pessoa, as de
outros papéis, as que esperam. Nada aqui é escolha de "próximo passo".
"""

from datetime import UTC, datetime, timedelta

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import providencias as p

AGORA = datetime(2026, 11, 6, 12, tzinfo=UTC)


def prov(ato, *, situacao=a.PENDENTE, sua=False, responsavel=a.CONDUZ, lista="", **extra):
    base = {
        "natureza": extra.pop("natureza", a.RELACAO),
        "chave": extra.pop("chave", (ato, lista)),
        "onde": extra.pop("onde", f"Cefor · {lista}" if lista else "Cefor"),
        "ato": ato,
        "situacao": situacao,
        "responsavel": responsavel,
        "sua": sua,
        "marco_id": extra.pop("marco_id", "m1"),
        "listas": (lista,) if lista else (),
        "lugar": extra.pop("lugar", "Cefor"),
    }
    base.update(extra)
    return p.Providencia(**base)


def test_a_ordem_e_suas_depois_de_outros_papeis_depois_as_que_esperam():
    itens = [
        prov("Aguardar a extração", situacao=a.AGUARDA, responsavel="", razao="dia 10"),
        prov("Publicar o resultado definitivo", responsavel=a.PUBLICA),
        prov("Congelar a relação", sua=True),
    ]
    nivel = p.Nivel1(itens)
    assert [i.ato for i in nivel.itens] == [
        "Congelar a relação",
        "Publicar o resultado definitivo",
        "Aguardar a extração",
    ]
    assert p.contagem(nivel) == "3 providências em aberto · 1 é sua"


def test_as_suas_com_prazo_vem_primeiro_pelo_prazo_mais_proximo():
    itens = [
        prov("Sem prazo", sua=True),
        prov("Prazo longe", sua=True, ate=AGORA + timedelta(days=9)),
        prov("Prazo perto", sua=True, ate=AGORA + timedelta(days=1)),
    ]
    assert [i.ato for i in p.Nivel1(itens).itens] == ["Prazo perto", "Prazo longe", "Sem prazo"]


def test_as_de_outros_papeis_ficam_agrupadas_por_papel():
    itens = [
        prov("Publicar", responsavel=a.PUBLICA),
        prov("Distribuir", responsavel=a.CONDUZ, natureza=a.DISTRIBUIR),
        prov("Publicar outro", responsavel=a.PUBLICA, marco_id="m2"),
    ]
    assert [i.responsavel for i in p.Nivel1(itens).itens] == [a.CONDUZ, a.PUBLICA, a.PUBLICA]


def test_o_mesmo_ato_em_varias_listas_do_marco_e_uma_providencia():
    """D-016: "Congelar a relação" em três listas é uma coisa a fazer numa tela só."""
    itens = [prov("Congelar a relação", sua=True, lista=nome) for nome in ("Ampla", "PPI", "PcD")]
    nivel = p.Nivel1(itens)
    assert nivel.total == 1
    assert nivel.itens[0].onde_por_extenso == "Cefor · Ampla, PPI e PcD"


def test_o_ato_com_numero_nao_se_junta():
    """ "Emitir 1 comunicação" em duas listas não é "Emitir 1 comunicação" nas duas."""
    itens = [prov("Emitir 1 comunicação", sua=True, lista=nome) for nome in ("Ampla", "PPI")]
    assert p.Nivel1(itens).total == 2


def test_o_que_espera_pela_mesma_razao_vira_uma_linha():
    razao = "As inscrições ficam abertas até 10/11"
    itens = [
        prov("Congelar a relação", situacao=a.AGUARDA, responsavel="", razao=razao),
        prov("Distribuir a Prova", situacao=a.AGUARDA, responsavel="", razao=razao, lugar="Prova"),
    ]
    nivel = p.Nivel1(itens)
    assert nivel.total == 1
    assert nivel.itens[0].ato == "Congelar a relação; Distribuir a Prova"


def test_listas_de_telas_diferentes_levam_a_conducao_do_marco():
    """Item 15 da revisão: "Publicar — Ampla e PPI" não pode levar só à prévia da Ampla."""
    itens = [
        prov("Publicar o resultado", sua=True, lista="Ampla", url="/previa/1", url_do_marco="/m"),
        prov("Publicar o resultado", sua=True, lista="PPI", url="/previa/2", url_do_marco="/m"),
    ]
    assert p.Nivel1(itens).itens[0].url == "/m"
    mesma_tela = [
        prov("Congelar a relação", sua=True, lista="Ampla", url="/sorteio"),
        prov("Congelar a relação", sua=True, lista="PPI", url="/sorteio?lista=2"),
    ]
    assert p.Nivel1(mesma_tela).itens[0].url == "/sorteio"


def test_a_semente_de_varios_perfis_e_uma_providencia_so():
    """Item 14 da revisão: uma observação serve a todo marco da mesma fonte e referência."""
    chave = (a.SEMENTE, "LOTERIA_FEDERAL", "6116")
    itens = [
        prov(
            "Observar a extração",
            sua=True,
            natureza=a.SEMENTE,
            marco_id="",
            chave=chave,
            lugar=nome,
            onde=nome,
        )
        for nome in ("Design", "Tecnologias")
    ]
    nivel = p.Nivel1(itens)
    assert nivel.total == 1 and nivel.itens[0].onde_por_extenso == "Design; Tecnologias"


def test_cinco_e_mais_n():
    itens = [prov(f"Ato {n}", sua=True, marco_id=str(n)) for n in range(7)]
    nivel = p.Nivel1(itens)
    assert len(nivel.mostradas) == 5 and len(nivel.demais) == 2


def test_sem_providencia_o_nivel_e_falso_e_a_contagem_vazia():
    nivel = p.Nivel1([])
    assert not nivel and p.contagem(nivel) == ""


def test_nenhuma_sua():
    assert p.contagem(p.Nivel1([prov("Publicar", responsavel=a.PUBLICA)])) == (
        "1 providência em aberto · nenhuma é sua"
    )


def test_a_atencao_numa_frase_so():
    assert p.frase_da_atencao([a.Atencao("Entrevista")]) == (
        "Entrevista está declarada no Edital, e nenhum ato do GPS depende do resultado dela."
    )
    assert p.frase_da_atencao([a.Atencao("A"), a.Atencao("B")]).startswith("A e B estão")


def test_o_lugar_vem_dito_e_nao_recortado_do_nome_do_perfil():
    """Item 1 do code review: o nome do Perfil pode ter " · "."""
    nome = "Oferta de Vagas · Polo Vitória"
    item = p.Providencia.da_celula(
        a.Celula(a.PENDENTE, natureza=a.CORTE, ato="Emitir o corte", responsavel=a.CONDUZ),
        onde=f"{nome} · PCD",
        sua=True,
        chave=("corte",),
        lista=("pcd", "PCD"),
        lugar=nome,
    )
    assert item.onde_por_extenso == "Oferta de Vagas · Polo Vitória · PCD"
