"""O comando de demonstração é caminho documentado no README e não tinha teste algum.

`seed_demo` percorre o fluxo normativo inteiro — cria Processo e Edital, compõe Perfis e
Cronograma, submete, homologa, publica e retifica, com atores distintos em cada etapa. É o que o
README manda rodar para ver o sistema no ar, e era a maior superfície do projeto sem cobertura
nenhuma: qualquer mudança de assinatura nos commands só apareceria para quem tentasse a
demonstração, que costuma ser alguém conhecendo o projeto pela primeira vez.
"""

from io import StringIO

import pytest
from django.core.management import call_command

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada

pytestmark = pytest.mark.integration


def _executar(**opcoes):
    saida = StringIO()
    call_command("seed_demo", stdout=saida, **opcoes)
    return saida.getvalue()


@pytest.mark.django_db(transaction=True)
def test_a_demonstracao_percorre_o_fluxo_ate_a_retificacao():
    saida = _executar(codigo="PS-TESTE-0001", numero="70", ano=2026)

    processo = ProcessoSeletivo.objects.get(institutional_code="PS-TESTE-0001")
    # **Dois Editais, e não um** (017, T072). O primeiro está com as inscrições abertas — é ele que
    # demonstra a jornada do candidato; o segundo tem o prazo vencido, e é nele que existe resultado
    # divulgado. Um Edital só não conseguiria ser os dois: distribuir exige o conjunto fechado.
    edital = Edital.objects.get(processo=processo, number="70")
    assert edital.status == Edital.Status.PUBLICADO
    assert edital.perfis.count() >= 2
    assert edital.cronograma.eventos.count() >= 3
    # Publicação original mais as Retificações publicadas.
    assert Publicacao.objects.filter(edital=edital).count() >= 2
    assert Retificacao.objects.filter(edital=edital, status=Retificacao.Status.PUBLICADA).exists()
    assert VersaoConsolidada.objects.filter(edital=edital).count() >= 2
    assert str(edital.id) in saida


@pytest.mark.django_db(transaction=True)
def test_a_demonstracao_chega_ao_resultado_divulgado():
    """A 017 na demonstração: ato emitido, resultado divulgado e o endereço público na saída.

    O que isto protege é o percurso inteiro — comissão, banca, avaliação, consolidação, ordem e
    divulgação —, feito pelos mesmos commands da aplicação. Semear a publicação por `INSERT`
    produziria uma linha que o sistema nunca teria aceitado, e a demonstração passaria a mostrar um
    estado inalcançável.
    """
    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from processo_seletivo.divulgacao.models import PublicacaoResultado, SituacaoDivulgada

    saida = _executar(codigo="PS-TESTE-0010", numero="20", ano=2026)

    processo = ProcessoSeletivo.objects.get(institutional_code="PS-TESTE-0010")
    concluido = Edital.objects.get(processo=processo, number="70")
    assert concluido.status == Edital.Status.PUBLICADO

    ato = AtoDeOrdenacao.objects.get(edital=concluido)
    publicacao = PublicacaoResultado.objects.get(edital=concluido)
    assert publicacao.ato_id == ato.id
    assert publicacao.publicado_por == "paula.publicadora"
    assert publicacao.signatario_nome == "Diretora do Cefor"
    assert publicacao.documento.bytes, "a demonstração precisa do documento oficial"

    # Quatro consideradas, três com posição e uma sem — é o que torna a fronteira visível.
    situacoes = SituacaoDivulgada.objects.filter(publicacao=publicacao)
    assert situacoes.count() == 4
    assert situacoes.filter(situacao=SituacaoDivulgada.Situacao.SEM_POSICAO).count() == 1
    conteudo = bytes(publicacao.conteudo_publico).decode()
    assert "Daniel Rocha" not in conteudo, "quem não recebeu posição não é nomeado publicamente"
    assert "Ana Silva" in conteudo

    assert f"/selecoes/resultados/{publicacao.id}/" in saida

    # O `--ano` vale para os **dois** Editais: eles são do mesmo Processo, e um certame não tem
    # dois anos. Uma demonstração histórica ou futura precisa que os dois acompanhem o argumento.
    assert concluido.year == 2026
    assert (
        Edital.objects.filter(processo=processo).values_list("year", flat=True).distinct().count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_a_segregacao_de_funcoes_e_respeitada_pela_demonstracao():
    """A demonstração precisa passar pelas mesmas recusas do domínio, não contorná-las.

    Se elaborar, homologar e publicar fossem a mesma pessoa, o command recusaria — e uma
    demonstração que só funcionasse driblando a regra não demonstraria o sistema.
    """
    _executar(codigo="PS-TESTE-0002", numero="71", ano=2026)

    from processo_seletivo.publicacoes.models import Homologacao, RevisaoEdital

    revisao = RevisaoEdital.objects.filter(edital__number="71").latest("submitted_at")
    homologacao = Homologacao.objects.get(revisao=revisao)
    publicacao = Publicacao.objects.filter(edital__number="71", revisao=revisao).get()

    assert len({revisao.prepared_by, homologacao.homologated_by, publicacao.published_by}) == 3


@pytest.mark.django_db(transaction=True)
def test_repetir_o_mesmo_codigo_e_recusado_com_a_saida_explicada():
    """Não há como recriar: apagar a demonstração exigiria excluir Publicações.

    A Constituição proíbe e as triggers de imutabilidade recusam. O comando diz o que fazer em
    vez de falhar com erro de banco — e o teste existe porque havia uma flag `--recriar`
    declarada, documentada no `--help` e jamais lida pelo `handle`.
    """
    from django.core.management.base import CommandError

    _executar(codigo="PS-TESTE-0003", numero="72", ano=2026)

    with pytest.raises(CommandError, match="Use --codigo"):
        _executar(codigo="PS-TESTE-0003", numero="72", ano=2026)

    assert ProcessoSeletivo.objects.filter(institutional_code="PS-TESTE-0003").count() == 1


@pytest.mark.django_db(transaction=True)
def test_o_comando_nao_oferece_uma_flag_que_nao_poderia_cumprir():
    from django.core.management import get_commands, load_command_class

    comando = load_command_class(get_commands()["seed_demo"], "seed_demo")
    parser = comando.create_parser("manage.py", "seed_demo")

    assert "--recriar" not in parser.format_help()


@pytest.mark.django_db(transaction=True)
def test_duas_demonstracoes_convivem_com_codigos_distintos():
    _executar(codigo="PS-TESTE-0004", numero="73", ano=2026)
    _executar(codigo="PS-TESTE-0005", numero="74", ano=2026)

    demonstracoes = ProcessoSeletivo.objects.filter(institutional_code__startswith="PS-TESTE-")
    assert demonstracoes.count() == 2


@pytest.mark.django_db(transaction=True)
def test_a_demonstracao_chega_ao_sorteio_constituido_e_verificavel():
    """O terceiro Edital fecha o ciclo da 021 pelos commands da aplicação (021, SC-006).

    **Pelos mesmos commands**, como o resto deste arquivo: congelar a relação, observar a ocorrência
    e constituir o ato — nesta ordem, que é a inversão que organiza a feature. Semear o sorteio por
    `INSERT` produziria um ato que a aplicação nunca teria aceitado, e a demonstração passaria a
    mostrar um estado que o sistema não sabe alcançar.
    """
    from processo_seletivo.classificacao.models import OrigemDaOrdem
    from processo_seletivo.sorteios.application.verificacao import verificar
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio

    _executar(codigo="PS-TESTE-0006", numero="20", ano=2026)

    sorteio = Sorteio.objects.get()
    relacao = RelacaoDeHabilitados.objects.get()

    assert sorteio.relacao_id == relacao.id
    assert sorteio.ato.origem == OrigemDaOrdem.SORTEIO
    assert relacao.quantidade == 7
    assert relacao.metodo_hash == sorteio.metodo_hash, "o ato roda sob o método comprometido"
    assert sorteio.semente_normalizada, "a semente nasceu do material observado"
    assert verificar(sorteio)["integro"] is True, "a demonstração passa na própria verificação"


@pytest.mark.django_db(transaction=True)
def test_a_relacao_da_demonstracao_e_congelada_antes_da_ocorrencia():
    """A ordem dos fatos, que é a feature: universo comprometido **antes** de a semente existir."""
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados

    _executar(codigo="PS-TESTE-0007", numero="21", ano=2026)

    relacao = RelacaoDeHabilitados.objects.get()
    ocorrencia = OcorrenciaDaFonte.objects.get()

    assert relacao.publicada_em < ocorrencia.observada_em
