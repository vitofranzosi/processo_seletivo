"""Quando o requerimento abre — e por que "vigente" seria o gatilho errado (029, `D-004`).

**A distinção que este arquivo prende.** *Classificado* diz que a pessoa foi ordenada; não diz que
ela pode ocupar vaga. *Vigente* diz que ninguém sucedeu a convocação; não diz que ela ainda espera
resposta. O fato que abre o requerimento é **chamada em aberto**: convocação vigente **sem
desfecho** — há vaga, ela é sua, e você ainda não respondeu.

**O que este arquivo não alcança.** `chamada_em_aberto` lê convocações, desfechos e sucessões;
injetar um sentinela aqui prova a política e **não** prova o predicado — e é o predicado que erra.
Ele é preso contra convocações de verdade em
`tests/integration/requerimentos/test_chamada_em_aberto.py`, e os dois arquivos são as duas metades
da mesma garantia.

**O beco já foi percorrido uma vez.** `convocar.py::_em_aberto_da_pessoa` registra que a primeira
versão daquele bloqueio olhava só a vigência, e o reclassificado que voltava à fila era recusado
quando chegava a vez dele. Quem trocar `chamada_em_aberto` por `vigentes` numa refatoração
distraída não é barrado ao escrever a linha — é barrado aqui.
"""

from types import SimpleNamespace

from processo_seletivo.requerimentos.domain import disponibilidade, nomes


def conteudo(momento=None, texto="Declaro, sob as penas da Lei…"):
    if momento is None:
        return {"matriculationRequest": None}
    return {"matriculationRequest": {"moment": momento, "declarationText": texto}}


class TestOEditalQueNaoDeclara:
    def test_sem_declaracao_nao_e_exigido(self):
        apurado = disponibilidade.apurar(conteudo())

        assert apurado.exigido is False
        assert apurado.disponivel is False
        assert apurado.estado_de_leitura == nomes.NAO_APLICAVEL

    def test_chave_ausente_e_lida_como_nao_declarado(self):
        """O acervo anterior ao degrau 16 não tem a chave: ler ausente e `None` igual é o certo."""
        assert disponibilidade.apurar({}).exigido is False

    def test_momento_desconhecido_nao_vira_exigencia(self):
        """Valor fora da lista fechada é lido como não declarado, nunca como terceiro momento."""
        assert disponibilidade.apurar(conteudo("QUANDO_DER")).exigido is False


class TestNaInscricao:
    def test_abre_sem_depender_de_chamada(self):
        apurado = disponibilidade.apurar(conteudo(nomes.NA_INSCRICAO))

        assert apurado.exigido is True
        assert apurado.disponivel is True
        assert apurado.estado_de_leitura == nomes.DISPONIVEL

    def test_a_metade_que_a_submissao_consulta(self):
        """`exigido_na_inscricao` **não alcança `convocacao`**, e é por isso que ela existe.

        Se a submissão da inscrição consultasse a política inteira, `inscricoes` passaria a importar
        `convocacao` — que importa `inscricoes` de volta pela FK da `Convocacao` — e o ciclo entre
        apps se fecharia. Nenhum teste o proíbe hoje; este repositório mantém duas varreduras
        dedicadas a sentido de dependência, e fechar ciclo com elas por perto é escolher o defeito
        que elas existem para impedir.
        """
        assert disponibilidade.exigido_na_inscricao(conteudo(nomes.NA_INSCRICAO)) is True
        assert disponibilidade.exigido_na_inscricao(conteudo(nomes.NA_CONVOCACAO)) is False
        assert disponibilidade.exigido_na_inscricao(conteudo()) is False


class TestNaConvocacao:
    def test_sem_chamada_em_aberto_fica_indisponivel(self):
        apurado = disponibilidade.apurar(conteudo(nomes.NA_CONVOCACAO), chamada_em_aberto=None)

        assert apurado.exigido is True
        assert apurado.disponivel is False
        assert apurado.estado_de_leitura == nomes.AINDA_INDISPONIVEL

    def test_com_chamada_em_aberto_abre(self):
        chamada = object()

        apurado = disponibilidade.apurar(conteudo(nomes.NA_CONVOCACAO), chamada_em_aberto=chamada)

        assert apurado.disponivel is True
        assert apurado.estado_de_leitura == nomes.DISPONIVEL

    def test_a_chamada_concreta_viaja_junto(self):
        """Quem abre o rascunho precisa **persistir** a chamada em `convocacao_autorizadora`.

        Devolver só um booleano obrigaria a aplicação a perguntar de novo — e duas leituras da mesma
        pergunta divergiriam no dia em que uma delas mudasse.
        """
        chamada = object()

        apurado = disponibilidade.apurar(conteudo(nomes.NA_CONVOCACAO), chamada_em_aberto=chamada)

        assert apurado.chamada is chamada

    def test_as_duas_ausencias_sao_estados_distintos(self):
        """*"Este certame não pede requerimento"* ≠ *"ainda não chegou a sua vez"* (`FR-405`).

        Colapsá-las diria a quem ainda tem chance que ela não tem — a mesma distinção que a tela de
        convocação já é obrigada a fazer.
        """
        nao_pede = disponibilidade.apurar(conteudo()).estado_de_leitura
        ainda_nao = disponibilidade.apurar(conteudo(nomes.NA_CONVOCACAO)).estado_de_leitura

        assert nao_pede != ainda_nao


class TestOsCincoEstadosDeLeitura:
    """`FR-405`: os cinco são alcançáveis, e nenhum é coluna.

    **A asserção de que os cinco aparecem é o ponto.** Uma redação anterior devolvia só três — o
    vocabulário declarava *em preenchimento* e *enviado*, e `estado_de_leitura` nunca os produzia.
    Um estado declarado e inalcançável é tela que nunca se escreve.
    """

    def rascunho(self):
        return SimpleNamespace(status=nomes.RASCUNHO)

    def enviado(self):
        return SimpleNamespace(status=nomes.ENVIADO)

    def test_sem_linha_e_disponivel(self):
        apurado = disponibilidade.apurar(conteudo(nomes.NA_INSCRICAO))

        assert apurado.enviado is False
        assert apurado.estado_de_leitura == nomes.DISPONIVEL

    def test_com_rascunho_e_em_preenchimento(self):
        apurado = disponibilidade.apurar(conteudo(nomes.NA_INSCRICAO), requerimento=self.rascunho())

        assert apurado.estado_de_leitura == nomes.EM_PREENCHIMENTO

    def test_com_envio_e_enviado(self):
        apurado = disponibilidade.apurar(conteudo(nomes.NA_INSCRICAO), requerimento=self.enviado())

        assert apurado.enviado is True
        assert apurado.estado_de_leitura == nomes.ESTADO_ENVIADO

    def test_enviado_continua_legivel_depois_de_a_chamada_fechar(self):
        """**A ordem da leitura é a regra** (`FR-406`).

        A chamada que abriu o requerimento pode ser desfechada depois do envio. Lido na outra
        ordem, o estado diria *"ainda indisponível"* a quem já enviou — e o que a pessoa mandou
        sumiria da vista dela.
        """
        apurado = disponibilidade.apurar(
            conteudo(nomes.NA_CONVOCACAO), chamada_em_aberto=None, requerimento=self.enviado()
        )

        assert apurado.disponivel is False, "a chamada fechou: não há mais o que escrever"
        assert apurado.estado_de_leitura == nomes.ESTADO_ENVIADO, "e o enviado continua legível"

    def test_os_cinco_sao_alcancaveis(self):
        alcancados = {
            disponibilidade.apurar(conteudo()).estado_de_leitura,
            disponibilidade.apurar(conteudo(nomes.NA_CONVOCACAO)).estado_de_leitura,
            disponibilidade.apurar(conteudo(nomes.NA_INSCRICAO)).estado_de_leitura,
            disponibilidade.apurar(
                conteudo(nomes.NA_INSCRICAO), requerimento=self.rascunho()
            ).estado_de_leitura,
            disponibilidade.apurar(
                conteudo(nomes.NA_INSCRICAO), requerimento=self.enviado()
            ).estado_de_leitura,
        }

        assert alcancados == set(nomes.ESTADOS_DE_LEITURA)
