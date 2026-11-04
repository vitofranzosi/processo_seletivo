"""A porta da fonte externa da semente, e os seus adaptadores (021, R-005).

**A fronteira que este módulo desenha.** A *identidade* da fonte, a ocorrência, a derivação, a
normalização e a regra de substituição são **conteúdo normativo publicado**: vivem no `drawMethod`
do marco, e alterá-las é Retificação. O *acesso* à fonte é implementação — qual biblioteca, qual
tempo limite, quantas tentativas —, e é o que mora aqui, configurado por ambiente.

Confundir as duas coisas seria deixar uma implantação de software mudar o sentido de um Edital já
publicado, que é exatamente o que a FR-014 proíbe.

O adaptador devolve **material bruto**, e nada mais: nem semente normalizada — normalizar é regra do
método (D-016) —, nem juízo sobre o que fazer quando a ocorrência falta. A ausência é um desfecho
declarado, e quem decide o que fazer com ela é a regra publicada.
"""

import time
from dataclasses import dataclass

from django.utils.module_loading import import_string

from processo_seletivo.shared.api.problems import DomainError


@dataclass(frozen=True)
class Observacao:
    """O que a fonte devolveu sobre uma ocorrência.

    `indisponivel` não é erro: é desfecho previsto, e é ele que aciona a regra de substituição
    publicada. `evidencia` é o que se observou — o que a fonte respondeu, e quando —, porque
    aplicar a substituição sem registrar o que a motivou seria afirmar indisponibilidade sem lastro
    (FR-015, R-006).

    **`ocorrida_nao_antes_de` é o instante mais cedo em que a ocorrência pode ter acontecido**,
    conforme a fonte publica — e não quando nós a lemos. A distinção é a feature inteira: a FR-016
    exige que a ocorrência seja **posterior ao congelamento**, e comparar o instante da leitura
    permitiria congelar a relação já sabendo o resultado e só depois registrá-lo no sistema.

    **O nome diz o que o dado é, e não mais do que ele é.** A Loteria Federal publica
    `dataApuracao: "11/09/2024"` — uma data, sem horário. A versão anterior deste campo se chamava
    `ocorrida_em` e o adaptador carimbava `20:00`, um horário que a fonte não publica: uma relação
    congelada no mesmo dia passava ou falhava por causa de um instante inventado. Agora o adaptador
    devolve o **início do dia publicado**, que é o limite inferior verdadeiro, e a comparação exige
    que o congelamento seja anterior a ele. Onde a fonte publicar o horário, o limite inferior é o
    próprio horário, e a garantia fica mais apertada sem mudar de forma.

    O adaptador que não souber dizer quando a ocorrência aconteceu não serve para semear sorteio, e
    o comando o recusa.

    **`falha_de_acesso` não é `indisponivel`, e confundir os dois custava a extração do certame.**
    `indisponivel` significa que a fonte **respondeu** e não havia extração — é o fato que a regra
    de substituição publicada consome, e ele fica gravado para sempre numa linha append-only.
    `falha_de_acesso` significa que não foi possível falar com a fonte: rede fora, tempo esgotado,
    serviço no chão. A segunda hipótese não afirma nada sobre o mundo, e tratá-la como a primeira
    fazia cinco segundos de rede ruim, ao vivo, **queimarem para sempre a extração que o Edital
    declarou** e empurrarem o certame para a seguinte — que talvez só aconteça na semana que vem, e
    sem nenhum caminho de volta, porque a linha não se altera nem se apaga.

    Falha de acesso, portanto, **não grava nada**: o comando recusa, diz o que houve, e quem opera
    tenta de novo.
    """

    material_bruto: str = ""
    ocorrida_nao_antes_de: object = None
    indisponivel: bool = False
    falha_de_acesso: bool = False
    evidencia: str = ""


# O teto da SC-1097: a espera que a conferência pode acrescentar a um ato, somadas as chamadas.
ESPERA_MAXIMA_DA_CONFERENCIA = 15.0


class FonteExterna:
    """A porta. Um método, e ele não decide nada.

    **`PUBLICA_SO_A_DATA` é a granularidade da fonte, e mora no adaptador** (102, FR-2647). Quem a
    conhece é quem devolve o limite inferior — a Loteria Federal devolve a meia-noite porque a Caixa
    não publica o horário —, e uma declaração longe dele divergiria na primeira mudança. A
    publicação do Edital a lê para recusar a extração que o sorteio nunca aceitaria; nunca é
    deduzida do conteúdo do Edital nem da resposta da fonte. O padrão é a fonte que publica a hora.
    """

    PUBLICA_SO_A_DATA = False

    # **A forma e a conferência da referência também são da fonte, e o padrão é "não se aplica"**
    # (116, D-008). Fonte que não as declara aceita a ocorrência de forma livre e não é consultada
    # antes dos atos: nenhuma fonte é obrigada a implementar o que não sabe, e a falta de
    # conferência não vira advertência em todo Edital dela. A forma é uma expressão compilada.
    FORMA_DA_REFERENCIA = None
    SABE_CONFERIR = False

    def observar(self, *, fonte: str, referencia: str) -> Observacao:  # pragma: no cover - contrato
        raise NotImplementedError

    def consultar_ultimo(self):  # pragma: no cover - contrato
        """O último concurso realizado, em `ConsultaDoUltimo`. Uma tentativa, nunca levanta."""
        raise NotImplementedError

    def consultar_data(self, numero):  # pragma: no cover - contrato
        """O dia em que o concurso foi realizado, ou `None`. Uma tentativa, nunca levanta."""
        raise NotImplementedError

    def conferir_referencias(self, referencias, *, fonte, agora):
        """`referência → Situacao`, com no máximo uma consulta principal (116, FR-3631).

        **A situação sai do último concurso, e a data só do realizado.** A consulta pelo número de
        um concurso futuro devolve o mesmo 500 de um erro do serviço; por isso ela nunca decide, e
        só acontece para referência já sabida realizada, uma vez por número distinto (FR-3629). A
        referência fora da forma não gera chamada nenhuma, e sem referência válida a principal
        também não acontece.
        """
        from django.conf import settings

        from processo_seletivo.sorteios.domain import conferencia

        numeros = {
            referencia: conferencia.numero_do_concurso(referencia) for referencia in referencias
        }
        inicio = time.monotonic()
        consulta = self.consultar_ultimo() if any(numeros.values()) else None
        ultimo = consulta.ultimo if consulta is not None else None
        datas = {}
        if ultimo is not None:
            # **A espera tem teto, e não só cada chamada** (SC-1097). Com quatro concursos
            # realizados e a Caixa lenta, quatro datas de 5 segundos passariam dos 15; e a data só
            # enfeita a mensagem — a recusa vale sem ela (FR-3629). A data que não cabe no teto
            # não é pedida.
            limite = float(getattr(settings, "SORTEIO_CONFERENCIA_TIMEOUT_SEGUNDOS", 5))
            for numero in sorted({n for n in numeros.values() if n and n <= ultimo.numero}):
                if time.monotonic() - inicio + limite > ESPERA_MAXIMA_DA_CONFERENCIA:
                    break
                datas[numero] = self.consultar_data(numero)
        return {
            referencia: conferencia.situacao(
                fonte=fonte,
                referencia=referencia,
                consulta=consulta,
                consultada_em=agora,
                data_da_referencia=datas.get(numero),
            )
            for referencia, numero in numeros.items()
        }


# **O vocabulário de fontes, fechado e ligado ao adaptador que cada uma executa** (FR-076).
#
# Sem esta tabela, `source` era texto livre: um Edital podia declarar `Random.org`, o sistema
# consultava a Caixa de qualquer jeito — `LoteriaFederal.observar` ignorava o argumento `fonte` — e
# o manifesto publicava uma fonte que nunca foi consultada. A identidade da fonte é conteúdo
# normativo; se ela não determinar de onde a semente vem, não é conteúdo normativo de nada.
#
# Acrescentar fonte é publicar adaptador, e não escrever uma linha no Edital.
FONTES = {
    "Loteria Federal": (
        "processo_seletivo.sorteios.infrastructure.fontes.loteria_federal.LoteriaFederal"
    ),
}

# O falso, endereçável por nome: é o que permite ao `seed_demo`, ao roteiro do `quickstart` e à
# suíte sortearem sem rede. **Fora de `FONTES`, e só no vocabulário onde a configuração o liga**
# (046, `FR-757`): a semente dele é fixa, e um Edital de produção que o declarasse publicaria um
# sorteio cujo resultado se conhece antes da extração (`RC-72`).
#
# **São duas, ligadas pela mesma chave** (102, D-007). A segunda publica só a data, como a Caixa, e
# é a única maneira de ver sem rede a recusa do Edital 72/2026: congelar e sortear no mesmo dia.
# Uma segunda chave seria mais uma variável que produção precisa recusar.
FONTES_DE_DEMONSTRACAO = (
    (
        "Fonte de demonstração",
        "processo_seletivo.sorteios.infrastructure.fontes.loteria_federal.FonteDeTeste",
    ),
    (
        "Fonte de demonstração (só a data)",
        "processo_seletivo.sorteios.infrastructure.fontes.loteria_federal.FonteDeTesteSoData",
    ),
)


def fontes_publicadas():
    """O vocabulário de fontes **deste ambiente**: nome publicado → adaptador.

    **Lido a cada chamada, e não montado no import**: um dicionário congelado no primeiro import não
    responderia a `override_settings`, e os casos que exercitam produção dentro da suíte veriam o
    vocabulário do ambiente de teste.

    **O ambiente decide se o nome existe, e nunca para onde ele aponta.** A escolha do adaptador
    continua sendo pelo nome que o Edital publicou (021, FR-076); o que a configuração faz é tirar
    da lista, em produção, um nome que nenhum Edital real pode declarar. A composição oferece, a
    validação aceita e a execução roda a partir desta mesma função — uma fonte só para as três.
    """
    from django.conf import settings

    vocabulario = dict(FONTES)
    if getattr(settings, "SORTEIO_FONTE_DE_DEMONSTRACAO", False):
        vocabulario.update(FONTES_DE_DEMONSTRACAO)
    return vocabulario


def fonte_declarada(nome):
    """O adaptador que executa a fonte **que o Edital declarou**, e não o que o ambiente escolheu.

    A configuração continua existindo para o que é operação — tempo limite, tentativas —, e deixou
    de decidir *de onde* a semente vem: isso é norma publicada. O que ela decide é só se o nome
    pertence ao vocabulário deste ambiente (`fontes_publicadas`).
    """
    vocabulario = fontes_publicadas()
    caminho = vocabulario.get(nome)
    if caminho is None:
        raise DomainError(
            "draw_source_not_supported",
            f"Fonte não publicada por este sistema: {nome!r}. "
            f"As publicadas são: {', '.join(sorted(vocabulario))}.",
            422,
            campo="source",
        )
    return import_string(caminho)()


def publica_so_a_data(nome):
    """Se a fonte publicada com este nome publica só a data — `True`, `False` ou `None`.

    `None` para nome fora do vocabulário **deste ambiente**: essa fonte já tem achado próprio
    (`draw_source_not_supported`, `draw_method_invalid`), e quem pergunta se cala para não empilhar
    dois relatos sobre uma causa só. A classe é importada e não instanciada: a pergunta é sobre o
    adaptador, e não uma chamada a ele.
    """
    caminho = fontes_publicadas().get(nome)
    if caminho is None:
        return None
    return bool(import_string(caminho).PUBLICA_SO_A_DATA)


def _classe(nome):
    caminho = fontes_publicadas().get(nome)
    return import_string(caminho) if caminho is not None else None


def forma_da_referencia(nome):
    """A forma que a fonte exige da referência, ou `None` — livre, ou fonte fora do vocabulário.

    Lida da classe, como `publica_so_a_data`, sem instanciar o adaptador (116, FR-3625).
    """
    classe = _classe(nome)
    return getattr(classe, "FORMA_DA_REFERENCIA", None) if classe is not None else None


def sabe_conferir(nome):
    """Se a fonte responde à conferência da referência — `True`, `False` ou `None` (116, D-008).

    `None` para nome fora do vocabulário deste ambiente, pela mesma razão de `publica_so_a_data`.
    """
    classe = _classe(nome)
    if classe is None:
        return None
    return bool(getattr(classe, "SABE_CONFERIR", False))


__all__ = [
    "FonteExterna",
    "Observacao",
    "fonte_declarada",
    "fontes_publicadas",
    "forma_da_referencia",
    "publica_so_a_data",
    "sabe_conferir",
]
