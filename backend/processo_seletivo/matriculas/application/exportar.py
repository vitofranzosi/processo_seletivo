"""O comando: permissão, montagem, relatório e registro (`FR-446`, `FR-447`, `FR-455`, `FR-456`).

**Dois passos, e eles existem por causa da tela.** `compor` lê tudo, aplica os 34 serializadores e
devolve as linhas e as lacunas **sem escrever nada**; `gerar` faz o mesmo e produz o arquivo,
registrando o ato. A separação é o que permite mostrar o resumo das lacunas **antes** do download
(`UX-060`) sem montar a planilha duas vezes — e depois dele ninguém lê o resumo.

**E os dois são amarrados por uma assinatura.** Sem ela, a separação abriria o buraco que ela
existe para fechar: um `POST` direto baixaria o arquivo sem que resumo nenhum tivesse sido lido, e
uma sucessão de requerimento entre o `GET` e o `POST` entregaria um arquivo diferente do que foi
conferido — com a pessoa achando que conferiu. `assinatura_da_composicao` é o mesmo mecanismo que
`assinatura_da_previa` da `017` e `assinatura_da_proposta` da `014` já usam, e pela mesma razão.

**A norma é a do ato que alcançou cada pessoa, e não a de hoje** (Princípio II). Perfil, Modalidade
e polo saem da versão que a convocação — ou o ato de ordenação divulgado — citou. Ler a vigente
faria uma Retificação mudar, em silêncio, o arquivo de quem já foi chamado.

**A exportação lê, e só lê** (`FR-449`). A única escrita de uma geração completa é a linha de
`GeracaoDeArquivo`, e isso é verificado contando as escritas, não lendo o código (`SC-156`).

**O arquivo não é persistido** (`FR-456`): os bytes vão na resposta e somem. O que fica é o registro
— quem, quando, qual população, quantas linhas, sob quais regras —, e ele **não contém dado de
candidato**.
"""

from dataclasses import dataclass
from hashlib import sha256

from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity
from processo_seletivo.matriculas.application import populacao as populacao_da_geracao
from processo_seletivo.matriculas.domain import colunas, lacuna, nomes
from processo_seletivo.matriculas.infrastructure import planilha
from processo_seletivo.matriculas.models import GeracaoDeArquivo
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.canonical import canonical_sha256


@dataclass(frozen=True)
class Composicao:
    """O que a geração produziria — lido, conferido e ainda não escrito em lugar nenhum."""

    populacao: object
    linhas: tuple
    relatorio: tuple
    requerimentos: tuple
    versao_do_resultado: str
    assinatura: str

    @property
    def quantidade(self) -> int:
        return len(self.linhas)

    @property
    def nomeia_pessoas(self) -> bool:
        """Se o relatório expõe **quem** declarou o quê (`FR-440`, `FR-453`).

        É o que distingue uma leitura comum de um acesso a dado sensível nominal, e é por isso que
        a prévia que o traz é registrada na trilha (Princípio III).
        """
        return any(item.pessoas for item in self.relatorio)


def assinatura_da_composicao(linhas, requerimentos) -> str:
    """A identidade do que foi conferido na tela, para o download recusar o que mudou.

    **Cobre as células e os requerimentos de que elas saíram.** As células, porque é o que a pessoa
    leu; os requerimentos, porque uma sucessão troca o conteúdo **e** a proveniência, e um arquivo
    idêntico vindo de outra declaração continua sendo outro arquivo.

    **Não cobre o instante**: ele não existe na prévia, e incluí-lo faria toda confirmação falhar.
    """
    return canonical_sha256(
        {"linhas": [list(linha) for linha in linhas], "requerimentos": list(requerimentos)}
    )


def _codigo_do_edital(edital) -> str:
    """Como o Edital é chamado numa conversa — `77/2026`, e não o UUID dele.

    A recusa por grafia de Modalidade nomeia o Edital (`FR-441`), e quem a lê precisa reconhecer de
    qual certame se fala sem consultar o banco.
    """
    return f"{edital.number}/{edital.year}"


def _conteudos_por_versao(alcancados) -> dict:
    """O conteúdo publicado de **cada** versão citada pelos atos, numa consulta só.

    Uma consulta por pessoa custaria uma leitura de snapshot por linha do arquivo, e um Edital de
    porte real tem centenas de convocados — é o mesmo crescimento que a `SC-090` da `019` proibiu.
    """
    identificadores = {alcancado.versao_id for alcancado in alcancados}
    return {
        str(versao.id): versao.content
        for versao in VersaoConsolidada.objects.filter(id__in=identificadores)
    }


def _perfil_do_conteudo(conteudo, profile_id):
    return next(
        (
            perfil
            for perfil in conteudo.get("profiles") or []
            if str(perfil.get("id")) == str(profile_id)
        ),
        {},
    )


def _codigo_da_modalidade(perfil, inscricao, edital):
    """O `code` publicado da Modalidade escolhida, ou `None` quando não há Modalidade.

    **`None` é ampla concorrência** (`D-003`), e não falta de dado.

    **O perfil vem da versão do ato que alcançou a pessoa**, e é isso que impede o caso mais feio
    desta função: uma Retificação que remova a Modalidade faria a leitura da norma de hoje não a
    encontrar e **recusar a geração** de quem concorreu legitimamente por ela. Sob a versão certa,
    ela está lá.

    Não encontrá-la ali é outra coisa, e continua sendo recusa: significa que a Inscrição aponta
    uma Modalidade que o Edital **daquele ato** não publicava, e emitir a coluna vazia mandaria a
    pessoa ao Registro Acadêmico sem a forma de ingresso que decide sob qual reserva ela entra.
    """
    if inscricao.modality_id is None:
        return None
    for modalidade in perfil.get("competitionModalities") or []:
        if str(modalidade.get("id")) == str(inscricao.modality_id):
            return modalidade.get("code", "")
    raise DomainError(
        nomes.MODALIDADE_DESCONHECIDA,
        f"A Inscrição {inscricao.protocolo} concorre por uma Modalidade que o Edital "
        f"{_codigo_do_edital(edital)} não publicava na versão do ato que a alcançou. A exportação "
        "não escolhe outra: a correspondência precisa ser acertada antes de gerar o arquivo.",
        422,
    )


def _identidades(alcancados) -> dict:
    """Nome e credencial principal de cada pessoa, em duas consultas — e não duas por pessoa."""
    subjects = {alcancado.inscricao.identity_subject for alcancado in alcancados}
    identidades = {
        identidade.subject: identidade
        for identidade in CandidateIdentity.objects.filter(subject__in=subjects)
    }
    principais = {
        credencial.identidade_id: credencial.email_como_informado
        for credencial in CandidateEmail.objects.filter(
            identidade__subject__in=subjects, principal=True
        )
    }
    return {
        subject: (identidade.nome, principais.get(identidade.id, ""))
        for subject, identidade in identidades.items()
    }


def _versao_da_convocacao(edital, marco_id) -> str:
    """O resumo dos atos de ordenação que as chamadas daquele marco citam (`FR-447`).

    É o que responde *"sob qual ordem aquelas pessoas foram chamadas"* — a mesma pergunta que o
    resumo do conteúdo publicado responde para um resultado divulgado.
    """
    atos = sorted(
        {
            str(ato)
            for ato in Convocacao.objects.filter(edital=edital, marco_id=marco_id).values_list(
                "ato_de_ordenacao_id", flat=True
            )
        }
    )
    return sha256("|".join(atos).encode()).hexdigest()


def _versao_do_resultado(edital, escolhida) -> str:
    if escolhida.especie == nomes.RESULTADO:
        return PublicacaoResultado.objects.values_list("conteudo_publico_hash", flat=True).get(
            pk=escolhida.referencia
        )
    return _versao_da_convocacao(edital, escolhida.referencia)


def compor(*, ator, edital, especie: str, referencia: str) -> Composicao:
    """Tudo o que o arquivo teria, **sem escrever nada** — a leitura que a tela mostra antes.

    A ordem das linhas é `CLASSIF_CURSO_FINAL` e, no empate, o protocolo (`FR-446`). Hoje a primeira
    chave é constante, porque a coluna sai vazia enquanto a `Q-2` não for respondida — de modo que a
    ordem efetiva é a do protocolo. Quando a questão for respondida, a ordem passa a ser a da
    classificação **sem que esta linha mude**, e é por isso que ela é escrita assim e não como uma
    ordenação por protocolo.
    """
    require_permission(ator, nomes.EXPORTAR, institution_scope=edital.institution_scope)
    escolhida = populacao_da_geracao.escolher(edital, especie, referencia)
    alcancados = populacao_da_geracao.alcancados_de(edital, escolhida)
    declaracoes = populacao_da_geracao.declaracoes_de(alcancados)
    populacao_da_geracao.exigir_completude(escolhida, alcancados, declaracoes)

    conteudos = _conteudos_por_versao(alcancados)
    identidades = _identidades(alcancados)

    montadas = []
    for alcancado in alcancados:
        inscricao = alcancado.inscricao
        conteudo = conteudos.get(alcancado.versao_id, {})
        perfil = _perfil_do_conteudo(conteudo, inscricao.profile_id)
        nome, email = identidades.get(inscricao.identity_subject, ("", ""))
        requerimento = declaracoes.por_inscricao[inscricao.id]
        dossie = colunas.Dossie(
            protocolo=inscricao.protocolo,
            # O nome da identidade, e o congelado da Inscrição quando aquela ainda não o tem: um
            # `NOME` vazio num arquivo de matrícula seria pior que o nome de meses atrás.
            nome=nome or inscricao.nome,
            cpf=inscricao.cpf_normalizado,
            email=email or inscricao.email,
            requerimento=requerimento,
            modalidade_code=_codigo_da_modalidade(perfil, inscricao, edital),
            polo=perfil.get("locality", ""),
            edital_codigo=_codigo_do_edital(edital),
        )
        textos, lacunas = colunas.linha(dossie)
        montadas.append((textos, lacunas, requerimento.id))

    ordenadas = sorted(montadas, key=lambda item: (item[0][2], item[0][0]))
    linhas = tuple(textos for textos, _, _ in ordenadas)
    requerimentos = tuple(str(identificador) for _, _, identificador in ordenadas)
    return Composicao(
        populacao=escolhida,
        linhas=linhas,
        relatorio=lacuna.consolidar(
            [
                (quem, coluna, achada)
                for _, lacunas, _ in ordenadas
                for quem, coluna, achada in lacunas
            ]
        ),
        requerimentos=requerimentos,
        versao_do_resultado=_versao_do_resultado(edital, escolhida),
        assinatura=assinatura_da_composicao(linhas, requerimentos),
    )


@dataclass(frozen=True)
class Arquivo:
    """Os bytes entregues e o registro que fica. O primeiro some; o segundo, não."""

    conteudo: bytes
    nome: str
    composicao: Composicao
    geracao: object


def gerar(*, ator, edital, especie: str, referencia: str, confirmacao_do_resumo: str) -> Arquivo:
    """O arquivo e o registro do ato (`FR-447`, `UX-060`).

    **`confirmacao_do_resumo` é obrigatório, e é o que torna a `UX-060` verificável.** A regra é
    *"a tela mostra o resumo das lacunas **antes** do download"*, e uma regra que só a tela cumpre é
    cumprida enquanto ninguém colar o endereço. Aqui quem não passou pela prévia não tem a
    assinatura, e quem passou por uma prévia que envelheceu tem a assinatura errada — os dois são
    recusados, com a mesma frase, porque é o mesmo fato: **este arquivo não é o que foi conferido**.

    **O registro é a única escrita.** Ele guarda quem, quando, qual população, quantas linhas, de
    que versão do resultado saiu e sob qual versão dos mapeamentos — e os requerimentos por
    **identificador**, que é o que responde *"qual era"* depois de uma sucessão sem guardar uma
    segunda cópia da declaração (§9, *Edge Cases*; §18, *Auditoria*).
    """
    composicao = compor(ator=ator, edital=edital, especie=especie, referencia=referencia)
    if (confirmacao_do_resumo or "") != composicao.assinatura:
        raise DomainError(
            nomes.RESUMO_NAO_CONFERIDO,
            "O que seria gerado agora não é o que foi conferido: alguém corrigiu um requerimento, "
            "registrou um desfecho ou convocou mais alguém nesse intervalo. Leia o resumo das "
            "lacunas de novo antes de baixar.",
            409,
            campo="confirmacao_do_resumo",
        )
    conteudo = planilha.montar(composicao.linhas)
    with command_context() as agora:
        geracao = GeracaoDeArquivo.objects.create(
            edital=edital,
            populacao_especie=composicao.populacao.especie,
            populacao_referencia=composicao.populacao.referencia,
            populacao_rotulo=composicao.populacao.rotulo,
            quantidade_de_linhas=composicao.quantidade,
            versao_do_resultado=composicao.versao_do_resultado,
            versao_dos_mapeamentos=colunas.VERSAO_DOS_MAPEAMENTOS,
            requerimentos=list(composicao.requerimentos),
            gerado_por=ator.subject,
            gerado_em=agora,
        )
    return Arquivo(
        conteudo=conteudo,
        nome=f"matriculas-{edital.number}-{edital.year}-{agora:%Y%m%d-%H%M}.xlsx",
        composicao=composicao,
        geracao=geracao,
    )
