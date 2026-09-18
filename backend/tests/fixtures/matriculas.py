"""O cenário da exportação de matrículas (`031`) e os atalhos que os testes dela usam.

**Funções ficam aqui, e a fixture fica no `conftest.py` de cada pasta** — a regra que
`tests/fixtures/corte.py` registra e que a `029` já seguiu.

O cenário é o da convocação da `019` — Edital publicado com quadro, ordem, corte, Resultados e
apuração —, mais **as chamadas praticadas** e **os requerimentos enviados**. Sem os dois últimos não
há o que exportar: a população é quem foi chamado, e só entra quem declarou.

**Os requerimentos são gravados direto no modelo**, e não pelo comando `enviar` da `029`. A razão é
a que o `conftest` daquela feature já escreve: uma fixture que atravessa comando alheio passa a
quebrar quando aquele comando muda, e a quebra aparece aqui, longe da causa. O que estes testes
exercitam é a **exportação** — o envio tem os testes dele.

**Nenhum valor daqui vem da linha `2` da planilha de amostra** (`D-006`).
"""

from datetime import date

from django.utils import timezone

from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import regra
from tests.fixtures.publicacao import publish_original
from tests.fixtures.requerimento import declarar as declarar_no_edital

DECLARACAO = "Declaro, sob as penas da Lei, que as informações prestadas são verdadeiras."

# A Modalidade de grafia **divergente**, publicada de propósito: `PPP` — *"pessoas pretas, pardas e
# indígenas"*, Lei 12.990/2014 — onde o comentário da planilha de importação prevê `PPI`. Duas
# letras, o mesmo instituto jurídico, e nenhuma das duas pontas sabe da outra (`D-003`, `FR-441`).
#
# Ela é o caso real do `seed_demo` deste repositório, e existe aqui para que a recusa da `SC-147`
# seja exercitada contra um Edital **publicado**, e não contra um código inventado no teste.
MODALIDADE_DIVERGENTE = "00000000-0000-4000-8000-000000000481"
LINHA_DIVERGENTE = "00000000-0000-4000-8000-000000000482"


def publicar_coletando_requerimento(api_client, manager_headers, process_payload, draft, **extras):
    """Publica o Edital **declarando que ele coleta o Requerimento de Matrícula** (`029`, `D-002`).

    **Sem isto o cenário é irreal, e a primeira redação destes testes era.** Nem todo certame deste
    sistema matricula alguém — há Editais de servidores, tutores e bolsistas —, e a exportação só
    existe onde o Edital declara o requerimento. Um cenário que gravava requerimentos num Edital
    que nunca os pediu exercitava um estado que o produto não produz.

    **`AT_CALL`**, que é o caso do 69 e do 46: o requerimento abre quando a pessoa é convocada, que
    é exatamente a população que esta feature exporta.
    """
    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=draft,
        antes_de_submeter=declarar_no_edital("AT_CALL"),
        **extras,
    )


def publicar_com_grafia_divergente(api_client, manager_headers, process_payload, draft):
    """Publica o mesmo rascunho, com uma Modalidade a mais cuja grafia o destino não reconhece.

    **Com linha no quadro, e de zero vagas**: a conferência da `025` recusa Modalidade declarada sem
    linha quando o quadro é completo, e zero vaga não muda a apuração da ampla concorrência — o que
    se exercita aqui é a saída, e não a repartição de vagas.
    """
    perfil = draft["profiles"][0]
    perfil.setdefault("competitionModalities", []).append(
        {
            "id": MODALIDADE_DIVERGENTE,
            "code": "PPP",
            "name": "Pessoas pretas, pardas e indígenas",
            "vacancies": 0,
        }
    )
    perfil["vacancyTable"].append(
        {
            "id": LINHA_DIVERGENTE,
            "modalityId": MODALIDADE_DIVERGENTE,
            "immediateVacancies": 0,
        }
    )
    return publicar_coletando_requerimento(api_client, manager_headers, process_payload, draft)


def montar_cenario_da_exportacao(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    prefixo="matriculas-031",
    quantos=2,
    # Uma sobrescrita de declaração por convocado, na ordem. **Existe porque requerimento enviado é
    # imutável**: o teste que precisa de alguém que declarou cor indígena não pode corrigir o
    # requerimento depois — ele tem de nascer assim.
    declaracoes=(),
    # Repassado até `montar_cenario_do_corte` — ver a razão escrita em `tests/fixtures/ocupacao.py`.
    # O padrão **declara o requerimento**: sem isso a exportação recusa o certame inteiro, e com
    # razão.
    publicar=None,
):
    """Edital publicado, `quantos` convocados e o requerimento enviado de cada um.

    Três vagas na linha geral e faixa de três — alvo 2 mais um excedente —, porque é o recorte em
    que há déficit para chamar mais de uma pessoa. Com o quadro padrão a segunda chamada é recusada
    por ausência de vaga faltante, que é a `019` funcionando e não obstáculo a contornar.

    Devolve `(edital, convocadas)`.
    """
    edital, _, inscricoes = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        geral=3,
        cut=regra(surplusCount=1),
        publicar=publicar or publicar_coletando_requerimento,
    )
    convocadas = list(inscricoes[:quantos])
    variacoes = list(declaracoes) + [{}] * (quantos - len(declaracoes))
    for ordem, inscricao in enumerate(convocadas):
        convocar(edital, gestor, inscricao, idempotency_key=f"{prefixo}-convocar-{ordem}")
        declarar(edital, inscricao, **variacoes[ordem])
    return edital, convocadas


def campos_declarados(**sobrescritas):
    """Um requerimento completo. Cada teste sobrescreve o que ele exercita."""
    valores = {
        "data_de_nascimento": date(1994, 7, 12),
        "municipio_natal": "Cariacica",
        "uf_natal": "ES",
        "nacionalidade": requerimento_nomes.BRASIL,
        "sexo": requerimento_nomes.FEMININO,
        "cor_raca": requerimento_nomes.PARDA,
        "estado_civil": requerimento_nomes.CASADO,
        "nome_da_mae": "Antônia Ferreira Gonçalves",
        "nome_do_pai": "",
        "rg": "0123456",
        "rg_orgao_emissor": "SSP-ES",
        "rg_expedido_em": date(2015, 6, 1),
        "titulo_eleitoral": "012345678901",
        "zona_eleitoral": "034",
        "secao_eleitoral": "0128",
        "telefone_celular": "(27) 98888-7766",
        "necessidade_especifica": "NENHUMA",
        "renda_familiar_faixa": requerimento_nomes.DE_UM_E_MEIO_A_DOIS_E_MEIO,
        "cep": "29040860",
        "logradouro": "Rua das Palmeiras",
        "numero": "s/n",
        "bairro": "Jucutuquara",
        "municipio": "Vitória",
        "uf": "ES",
    }
    valores.update(sobrescritas)
    return valores


def declarar(edital, inscricao, *, status=requerimento_nomes.ENVIADO, **sobrescritas):
    """O requerimento daquela pessoa, no estado pedido.

    O envio exige instante, versão, resumo e aceite — é o que a `ck_requerimento_enviado_completo`
    diz no banco, e é por isso que um rascunho não pode simplesmente mudar de `status`.
    """
    agora = timezone.now()
    enviado = status == requerimento_nomes.ENVIADO
    return RequerimentoDeMatricula.objects.create(
        inscricao=inscricao,
        status=status,
        disponibilizado_em=agora,
        created_at=agora,
        enviado_em=agora if enviado else None,
        versao_aceita=effective_version(edital_id=edital.id) if enviado else None,
        declaracao_hash="a" * 64 if enviado else "",
        declaracao_aceita_em=agora if enviado else None,
        **campos_declarados(**sobrescritas),
    )
