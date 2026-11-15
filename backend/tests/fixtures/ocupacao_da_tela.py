"""Os cenários da tela da Ocupação, como funções (172, T005).

Moravam como *fixtures* locais em `tests/interface/test_ocupacao.py`, `test_acrescimo.py` e
`test_destinacao_na_ocupacao.py`, e a fotografia do piloto do design system precisa dos mesmos
estados, montados do mesmo jeito: uma *fixture* local não se importa de outro módulo sem arrastar o
arquivo inteiro. Subiram para cá **sem mudar o que montam**, e as *fixtures* daqueles arquivos
passaram a chamá-las.
"""


def com_continuacao(gestor, api_client, manager_headers, process_payload):
    """O cenário da ocupação com um Edital que **admite** continuação além da faixa (014, D-011).

    O cenário base é o do 14/2026, que não a admite: ali o comando recusa a faixa seguinte, e a tela
    deixou de oferecê-la (achado 02 do estudo de 11/11/2026). Quem quer ver o botão precisa do 77.
    """
    from tests.fixtures.corte import regra
    from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="tela-016-continua",
        geral=3,
        cut=regra(continuation="ALLOWED"),
    )


def sem_regra_de_corte(gestor, api_client, manager_headers, process_payload):
    """O cenário da ocupação com o marco **sem** regra de corte, e sem ato de corte emitido.

    Não é `montar_cenario_da_ocupacao`: aquele emite o corte, e um marco sem regra não tem corte a
    emitir. O que este cenário exercita é o que a `016` já admitia por escrito — *"marco que não
    corta continua tendo ocupação apurável"* —, e é justamente por isso que o recorte chega a
    `CURRENT` com déficit e a tela chega a oferecer a faixa.
    """
    from tests.fixtures.corte import montar_cenario_do_corte
    from tests.fixtures.legado import publicar_como_acervo
    from tests.fixtures.ocupacao import rascunho_com_quadro

    def monta(cut=None):
        base, pontuada = rascunho_com_quadro(geral=3)
        # A chave sai inteira: `{}` seria uma segunda grafia da ausência, e o marco do acervo não a
        # tem — ele tem `cutRule` nulo, que é o que o degrau 13 escreve.
        base["profiles"][0]["classificationMilestones"][0].pop("cutRule", None)
        return base, pontuada

    return montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-032-sem-corte",
        draft_factory=monta,
        # O marco do acervo (046, `FR-752`): a `FR-463` continua valendo sobre ele.
        publicar=publicar_como_acervo,
    )


def reserva(gestor, api_client, manager_headers, process_payload):
    """O Perfil do TMD: 0 vagas, cadastro de reserva, faixa de dois e três habilitadas."""
    from tests.fixtures.convocacao import habilitar_na_etapa_governada
    from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

    edital, _, inscricoes = montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="interface-097",
        geral=0,
        reserva="UNLIMITED",
    )
    habilitar_na_etapa_governada(edital, inscricoes[:3])
    return edital, inscricoes


def encerrar_o_prazo(monkeypatch):
    """A janela de definitividade fechada: a declaração de vaga não preenchida passa a caber."""
    monkeypatch.setattr(
        "processo_seletivo.divulgacao.domain.publicabilidade.janela_aberta_ate",
        lambda **_: None,
    )


def pela_desistencia(gestor, api_client, manager_headers, process_payload, prefixo, *, reversao):
    """A V-1 pelo caminho do ator: a cotista é chamada e desiste, e o desfecho emite a apuração.

    **Todos habilitados na Etapa que o corte governa**: com a Etapa por consolidar, o Centro diz que
    a convocação espera por ela, e o ramo da vaga sem quem a ocupe nunca é lido. **A espécie da
    chamada é a que a posição determina** (`especie=None`): supor que a cotista é titular tornaria o
    caso dependente da ordem que o sorteio produz.
    """
    from processo_seletivo.convocacao.domain import nomes as nomes_da_conducao
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI
    from tests.fixtures.ocupacao_sorteada import certame_sorteado_com_quadro
    from tests.integration.convocacao.test_suplencia import chamar, responder
    from tests.integration.ocupacao.test_concomitancia import apurar, emitir_cortes, habilitar
    from tests.integration.ocupacao.test_condicao_do_esgotamento import sem_concomitancia

    certame = certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        com_corte=True,
        quantos=8,
        geral=1,
        reversao=reversao,
    )
    cotista = certame["cotista_ppi"]
    emitir_cortes(certame, gestor)
    habilitar(certame, certame["inscricoes"])
    apurar(certame, gestor, chave=f"{prefixo}-ampla")
    sem_concomitancia(certame, cotista)
    apurar(certame, gestor, chave=f"{prefixo}-ampla-2", motivo="Saída da ampla registrada")
    apurar(certame, gestor, lista_id=PPI, chave=f"{prefixo}-ppi")
    chamada = chamar(
        certame, gestor, cotista.id, lista_id=PPI, chave=f"{prefixo}-chamar", especie=None
    )
    responder(
        certame, gestor, chamada["id"], nomes_da_conducao.DESISTENCIA_EXPRESSA, f"{prefixo}-sai"
    )
    return certame


def reversao_que_nao_sai(gestor, api_client, manager_headers, process_payload):
    """A V-1 sob a reversão por esgotamento: a apuração conta a posição de quem desistiu e não
    cede, e o resultado definitivo está publicado."""
    from processo_seletivo.ocupacao.domain import nomes
    from tests.integration.ocupacao.test_condicao_do_esgotamento import publicar_definitivo

    certame = pela_desistencia(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "tela-rev-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    publicar_definitivo(certame)
    return certame


def silente(gestor, api_client, manager_headers, process_payload):
    """O C09: sem reversão declarada, a lista PPI esgotada e o resultado definitivo publicado."""
    from tests.integration.ocupacao.test_condicao_do_esgotamento import publicar_definitivo

    certame = pela_desistencia(
        gestor, api_client, manager_headers, process_payload, "tela-np-155", reversao=None
    )
    publicar_definitivo(certame)
    return certame
