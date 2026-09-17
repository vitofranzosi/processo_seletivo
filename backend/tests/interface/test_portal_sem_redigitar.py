"""A promessa-manchete da feature: informar uma vez (029, `SC-120`, `FR-378`, `FR-380`, `UX-056`).

**Asserção sobre *ausência* é a que envelhece mal sem teste.** Basta alguém acrescentar um `input`
de nome "para facilitar a conferência", e a promessa inteira cai sem que nada acuse: a tela continua
funcionando, os testes continuam verdes, e o candidato volta a redigitar o que o sistema já sabe.
É o critério-manchete da `§20` e era o único sem tarefa.

**Perfil, modalidade, protocolo e Edital são derivados, nunca perguntados** (`FR-380`). Eles saem da
Inscrição e do conteúdo publicado; pedi-los seria mandar a pessoa repetir o que já escolheu — e
abriria a possibilidade de o que ela digitasse divergir do que ela de fato escolheu.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Os controles que **não** podem existir nesta tela. O nome é o do `name=`/`id=`, e não o rótulo:
# é o que um `POST` usaria, e é o que alguém acrescentaria sem pensar.
NUNCA_PERGUNTADOS = (
    "nome",
    "cpf",
    "email",
    "perfil",
    "profile_id",
    "modalidade",
    "modality_id",
    "protocolo",
    "edital",
    "edital_id",
)


@pytest.fixture
def tela(client, selecao_na_inscricao, candidatos_registrados):
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()
    resposta = client.get(reverse("portal:requerimento", args=[inscricao.id]))
    return inscricao, resposta.content.decode()


def controles(corpo):
    """Os `name=` de todo `input`, `select` e `textarea` que a tela oferece."""
    return set(re.findall(r'<(?:input|select|textarea)[^>]*\sname="([^"]+)"', corpo))


class TestOQueNaoSePergunta:
    def test_nenhum_dos_derivados_aparece_como_campo_de_entrada(self, tela):
        _, corpo = tela

        oferecidos = controles(corpo)

        intrusos = sorted(oferecidos & set(NUNCA_PERGUNTADOS))
        assert intrusos == [], (
            f"a tela voltou a perguntar o que o sistema já sabe: {intrusos}. "
            "Se o campo é mesmo necessário, ele vem da Inscrição ou da identidade — não do teclado."
        )

    def test_os_unicos_campos_sao_os_do_formulario_do_requerimento(self, tela):
        """A lista é fixa, e o Edital não a configura — só liga e agenda (`D-002`).

        Sem esta asserção, "não pergunta nome" continuaria verdadeiro enquanto a tela crescesse
        com qualquer outro campo que ninguém decidiu coletar.
        """
        from processo_seletivo.portal import requerimento as formulario

        _, corpo = tela
        # Os que **não** são declaração da pessoa: o token do CSRF, os que transportam o estado da
        # tela — versão exibida, revisão exibida, modo de conferência — e o aceite.
        #
        # **A lista é fechada de propósito.** Foi ela que acusou o campo `revisao` no dia em que o
        # controle otimista entrou: qualquer controle novo no formulário aparece aqui e obriga
        # alguém a dizer se é declaração ou é mecanismo. Um `**extras` no lugar dela deixaria
        # passar o campo de nome que esta feature existe para não pedir.
        administrativos = {
            "csrfmiddlewaretoken",
            "versao_exibida",
            "declaracao_exibida",
            "revisao",
            "atualizando",
            "aceite",
        }

        oferecidos = controles(corpo) - administrativos

        assert oferecidos == {campo.nome for campo in formulario.CAMPOS}


class TestOQueSeInformaSemPerguntar:
    def test_nome_cpf_e_email_aparecem_como_informacao_com_o_caminho_da_correcao(self, tela):
        """`FR-378` e `UX-053`: campo desabilitado sem explicação é o defeito que isto evita."""
        inscricao, corpo = tela

        assert inscricao.nome in corpo
        assert inscricao.cpf in corpo
        assert reverse("portal:meus-dados") in corpo, "o caminho para corrigir o nome e o CPF"
        assert reverse("portal:conta") in corpo, "o caminho para corrigir o e-mail"

    def test_o_protocolo_e_a_vaga_aparecem_sem_serem_perguntados(self, tela):
        inscricao, corpo = tela

        assert inscricao.protocolo in corpo

    def test_nenhum_controle_desabilitado_carrega_dado_da_pessoa(self, tela):
        """Somente leitura é legítimo para o que veio do CEP; para identidade, não.

        A distinção: o município volta a abrir quando a referência não responde, e a tela diz de
        onde ele veio. Um campo de nome trancado não abre nunca, e não diz nada.
        """
        _, corpo = tela

        trancados = re.findall(
            r'<(?:input|select)[^>]*\sname="([^"]+)"[^>]*(?:readonly|disabled)', corpo
        )

        assert not set(trancados) & set(NUNCA_PERGUNTADOS)


class TestADeclaracao:
    def test_a_declaracao_aparece_por_extenso_e_o_aceite_e_um_ato_explicito(self, tela):
        """`UX-056`: aceitar tem de ser um gesto, e não uma caixa já marcada.

        Caixa pré-marcada transforma o aceite em omissão — e o que se guarda passa a provar que a
        pessoa não desmarcou, que é coisa diferente de ela ter concordado.
        """
        _, corpo = tela

        assert DECLARACAO in corpo, "o texto vem do Edital publicado, e aparece inteiro"
        aceite = re.search(r'<input[^>]*id="aceite"[^>]*>', corpo)
        assert aceite, "o aceite é um controle nativo"
        assert "checked" not in aceite.group(0), "aceite não nasce marcado"
