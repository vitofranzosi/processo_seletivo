"""O kit textual, sobre fichas montadas à mão (111, FR-3412 a FR-3421, FR-3425)."""

import dataclasses
import re

from processo_seletivo.interface import kit_textos
from processo_seletivo.portal.ficha import COM_PERIODO, NEUTRO, SEM_MATERIAL, Ficha, Oferta


def _oferta(identidade, nome, localidade, vagas, reserva=False):
    quantidade = f"{vagas} vaga{'s' if vagas != 1 else ''}" if vagas else ""
    if reserva:
        quantidade = f"{quantidade} e cadastro reserva" if quantidade else "cadastro reserva"
    return Oferta(identidade, nome, localidade, vagas, reserva, quantidade, f"#vaga-{identidade}")


QUATRO_POLOS = tuple(
    _oferta(str(i), "Especialização em Informática na Educação", f"Polo {nome}", 40)
    for i, nome in enumerate(("Bom Jesus do Norte", "Iúna", "São Mateus", "Vargem Alta"))
)


def _ficha(**mudar):
    base = dict(
        modo=COM_PERIODO,
        motivo="",
        edital_id="e",
        numero="91",
        ano="2026",
        identificacao="Edital nº 91/2026",
        titulo="Edital nº 91/2026 – Curso de Pós-graduação em Informática na Educação",
        titulo_sem_numero="Curso de Pós-graduação em Informática na Educação",
        titulo_do_processo="Processo Seletivo de Alunos",
        unidade_sigla="Cefor",
        referencia="2026-11-05T09:00:00-03:00",
        referencia_texto="05/11/2026, 09h00",
        situacao_chave="aberto",
        situacao_rotulo="Aberta",
        periodo_estado="aberto",
        inicio="2026-11-04T09:00:00-03:00",
        fim="2026-11-21T23:59:00-03:00",
        cancelado=False,
        inicio_data="04/11/2026",
        inicio_hora="09h00",
        fim_data="21/11/2026",
        fim_hora="23h59",
        periodo_curto="04/11 a 21/11/2026",
        prorrogado=False,
        fim_original_texto="",
        fim_vigente_texto="",
        ofertas=QUATRO_POLOS,
        nomes_iguais=True,
        total_de_vagas=160,
        caminho="/selecoes/e/",
        endereco="https://gps.exemplo.ifes.edu.br/selecoes/e/",
        caminho_curto="gps.exemplo.ifes.edu.br/selecoes",
        versao_id="v",
        versao_hash="h",
        versao_desde="2026-10-31T11:00:00-03:00",
        versao_desde_texto="31/10/2026, 11h00",
        versao_ato="Publicação original de 31/10/2026",
        retificacao_a_vigorar=None,
        retificacao_a_vigorar_texto="",
        campos={},
        impressao="abc",
    )
    base.update(mudar)
    return Ficha(**base)


def _tudo(ficha):
    return "\n".join(kit_textos.compor(ficha).values())


def test_formas_por_modo():
    assert set(kit_textos.compor(_ficha())) == set(kit_textos.TITULOS)
    assert kit_textos.compor(_ficha(modo=SEM_MATERIAL, motivo="Edital cancelado.")) == {}
    neutro = kit_textos.compor(_ficha(modo=NEUTRO, inicio_data="", fim_data=""))
    assert "Edital publicado" in neutro["chamada_para_o_site"]


def test_prazo_em_data_e_hora_absolutas():
    texto = _tudo(_ficha())
    assert "Inscrições de 04/11/2026 a 21/11/2026, até as 23h59 (horário de Brasília)." in texto
    assert not re.search(r"\b(faltam?|hoje|amanhã|último dia|abertas)\b", texto, re.IGNORECASE)


def test_periodo_sem_termino():
    ficha = _ficha(fim=None, fim_data="", fim_hora="", periodo_curto="a partir de 04/11/2026")
    assert "Inscrições a partir de 04/11/2026, às 09h00." in _tudo(ficha)


def test_modo_neutro_nao_fala_de_inscricao():
    ficha = _ficha(modo=NEUTRO, inicio=None, fim=None, inicio_data="", fim_data="")
    assert not re.search(r"inscri", _tudo(ficha), re.IGNORECASE)


def test_prorrogacao_com_as_duas_pontas():
    ficha = _ficha(prorrogado=True, fim_original_texto="21/11/2026", fim_vigente_texto="26/11/2026")
    assert "o término passou de 21/11/2026 para 26/11/2026" in _tudo(ficha)


def test_prorrogacao_so_de_hora():
    ficha = _ficha(
        prorrogado=True,
        fim_original_texto="21/11/2026, 12h00",
        fim_vigente_texto="21/11/2026, 23h59",
    )
    assert "passou de 21/11/2026, 12h00 para 21/11/2026, 23h59" in _tudo(ficha)


def test_legenda_sem_link_com_busca_e_sigla():
    textos = kit_textos.compor(_ficha())
    assert "https://" not in textos["legenda"]
    assert "busque por 91/2026 – Cefor" in textos["legenda"]
    assert textos["texto_para_mensagem"].endswith("https://gps.exemplo.ifes.edu.br/selecoes/e/")


def test_ressalva_em_todo_texto_publicavel():
    textos = kit_textos.compor(_ficha())
    for chave in ("legenda", "ressalva"):
        assert "Em caso de divergência, vale o Edital." in textos[chave]


def test_notas_sem_validade_prometida():
    notas = " ".join(kit_textos.notas_para_quem_divulga(_ficha()))
    assert "válido até" not in notas.lower()
    assert "pode mudar os dados" in notas


def test_localidades_so_com_localidade_em_todas():
    assert "em 4 localidades" in _tudo(_ficha())
    sem = tuple(dataclasses.replace(o, localidade="") for o in QUATRO_POLOS)
    texto = _tudo(_ficha(ofertas=sem))
    assert "localidades" not in texto
    assert "4 opções de oferta" in texto


def test_total_sempre_com_o_numero_de_opcoes():
    texto = _tudo(_ficha())
    assert "160 vagas em 4 opções" in texto
    assert not re.search(r"160 vagas(?! em)", texto)


def test_opcoes_indistintas_contam():
    iguais = tuple(dataclasses.replace(o, localidade="") for o in QUATRO_POLOS)
    legenda = kit_textos.compor(_ficha(ofertas=iguais))["legenda"]
    assert "•" not in legenda
    assert "Confira todas as opções na página oficial." in legenda


def test_legenda_conta_acima_de_quatro():
    cinco = (
        *QUATRO_POLOS,
        _oferta("9", "Especialização em Informática na Educação", "Polo Serra", 40),
    )
    legenda = kit_textos.compor(_ficha(ofertas=cinco, total_de_vagas=200))["legenda"]
    assert "•" not in legenda
    assert "200 vagas em 5 opções" in legenda


def test_host_local_sem_link_absoluto():
    textos = kit_textos.compor(_ficha(endereco=None, caminho_curto=None))
    assert "https://" not in "\n".join(textos.values())
    assert "links_por_opcao" not in textos
    assert "link_oficial" not in textos
    assert textos["resumo"].endswith("na página oficial.")


def test_markdown_e_texto_trazem_conferencia_e_notas():
    ficha = _ficha()
    textos = kit_textos.compor(ficha)
    notas = kit_textos.notas_para_quem_divulga(ficha)
    markdown = kit_textos.em_markdown(ficha, textos, notas)
    texto = kit_textos.em_texto(ficha, textos, notas)
    assert "## Informações oficiais" in markdown and "## Legenda para rede social" in markdown
    assert texto.startswith("INFORMAÇÕES OFICIAIS")


def test_chamada_sem_inicio_mantem_brasilia_maiusculo():
    ficha = _ficha(inicio=None, inicio_data="", inicio_hora="", periodo_curto="até 21/11/2026")
    chamada = kit_textos.compor(ficha)["chamada_para_o_site"]
    assert chamada.endswith("inscrições até 21/11/2026, às 23h59 (horário de Brasília).")
