"""O cenário da demonstração da 149, num banco novo — o mesmo dos testes de integração.

Rodar de `backend/`, num banco migrado e vazio (ver o quickstart):

    DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps148demo DB_USER=$USER \
    DB_RUNTIME_USER=$USER DJANGO_ALLOWED_HOSTS=localhost,testserver \
    ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps148demo \
    uv run python manage.py shell < ../specs/149-publicacao-das-convocacoes/demonstracao/montar.py

Monta: um Edital por publicação, com a ampla e a reserva PPI da mesma vaga; uma convocação em cada;
a 1ª publicação de convocados no GPS, com as duas; a correção do vencimento da convocação da ampla;
e a 2ª publicação, que leva a correção. Deixa ainda uma terceira pessoa convocada e não publicada,
para a prévia da gestão ter o que mostrar.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APIClient

from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.publicar import (
    previa_da_publicacao,
    publicar_convocados,
)
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from tests.conftest import ator_institucional
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO, garantir_o_cefor
from tests.fixtures.convocacao import apurar, convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import MODALIDADE_PPI
from tests.fixtures.recortes import emitir_recorte
from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

garantir_o_cefor()
gestor = ator_institucional("carlos", "comissao:gerir")
cabecalhos = {
    "HTTP_AUTHORIZATION": "Bearer gestor-a|cefor|processo:criar,processo:ativar,edital:criar",
    "HTTP_IDEMPOTENCY_KEY": "demo-148-processo-0001",
    "HTTP_X_CORRELATION_ID": "demo-148",
}
processo = {
    "institutionalCode": "PS-2026-148",
    "title": "Processo Seletivo para Tutoria a Distância 2026",
    "firstEdital": {"number": "48", "year": 2026, "title": "Tutores a distância"},
}
cenario = montar_cenario_da_convocacao(
    gestor,
    APIClient(),
    cabecalhos,
    processo,
    prefixo="demo-148",
    forma=FORMA_POR_PUBLICACAO,
    ppi=1,
    modalidades={2: MODALIDADE_PPI},
    documentos=cenarios.documentos_do_aluno(),
)
edital = cenario[0]
prazo = timezone.now() + timedelta(days=7)

_, ampla = cenarios.convocar_primeira(cenario, gestor, chave="demo-148-ampla", vencimento=prazo)
emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="demo-148-ordem-ppi")
emitir_corte(
    actor=gestor,
    processo_id=edital.processo_id,
    edital_id=edital.id,
    perfil_id=PROFILE_ID,
    marco_id=MARCO,
    lista_id=MODALIDADE_PPI,
    idempotency_key="demo-148-corte-ppi",
    correlation_id="demo-148",
    confirmacao_do_calculo=assinatura_do_corte(
        calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=MODALIDADE_PPI)
    ),
)
apurar(edital, gestor, chave="demo-148-apura-ppi", lista_id=MODALIDADE_PPI)
fila = selectors.contexto_do_recorte(
    edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=MODALIDADE_PPI
)["fila"]
convocar(
    edital,
    gestor,
    fila[0],
    lista_id=MODALIDADE_PPI,
    idempotency_key="demo-148-ppi",
    vencimento=prazo,
)


def publicar(chave):
    return publicar_convocados(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        recortes=None,
        alcance_confirmado=previa_da_publicacao(edital=edital, at=timezone.now())["assinatura"],
        autoridade=str(AUTORIDADE_DO_RESULTADO),
        declaracao_do_veiculo="item 7.2 do Edital nº 48/2026",
        idempotency_key=chave,
        correlation_id="demo-148",
    )


print("1ª:", publicar("demo-148-publicacao-1"))
corrigir(edital, gestor, Convocacao.objects.get(id=ampla.id), chave="demo-148-correcao")
print("2ª:", publicar("demo-148-publicacao-2"))
print("Edital:", edital.id, "Processo:", edital.processo_id)

# A suplente, para a prévia da gestão ter o que mostrar: a titular corrigida desiste, a apuração
# seguinte sai com o desfecho, e a próxima da fila é convocada — e fica aguardando publicação.
corrigida = Convocacao.objects.get(convocacao_anterior=ampla)
cenarios.desfechar(edital, gestor, corrigida, "DESISTENCIA_EXPRESSA", "demo-148-desiste")
seguinte = selectors.contexto_do_recorte(
    edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
)["fila"]
print("Suplente:", convocar(edital, gestor, seguinte[0], idempotency_key="demo-148-sup",
                            vencimento=prazo)["id"])
