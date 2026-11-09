"""Os passos com que os cenários se montam — todos pelos comandos da aplicação (134, FR-4640).

**Nenhuma linha de domínio é escrita por aqui.** Cada passo chama o mesmo comando que a tela
chama, com um ator que tem só a capacidade daquele passo: a segregação de funções, a idempotência,
a trilha e as recusas do domínio valem para o gerador como valem para a pessoa. Quando um comando
recusa, o cenário inteiro é desfeito (a transação é do serviço), e a recusa chega a quem rodou o
comando com a frase do domínio — que é a regra funcionando, e não obstáculo a contornar.

**Os moldes são os do `seed_demo`**, e não outros: são os rascunhos que a suíte prova publicáveis a
cada commit (`tests/integration/test_seed_demo.py`). O que muda é só o que precisa mudar — os
identificadores, que `identificadores.remapear` troca pelos da rodada, e as quantidades.

A única exceção ao "pelo comando" é a mesma do `seed_demo`, e pela mesma razão: a credencial
verificada de quem já se inscreveu (`dar_acesso`), que representa uma prova de e-mail que já
aconteceu, e sem a qual a pessoa fictícia não teria como entrar no portal.
"""

import copy
from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from processo_seletivo.processos.management.commands import seed_demo as molde
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.treinamento import identificadores as ids
from processo_seletivo.treinamento.identificadores import MOLDE, do_molde

# Quem pratica cada passo. Identificadores próprios, que se denunciam na trilha e na página de
# acesso da demonstração — e que **não** começam por `pessoa-`, o formato do identificador
# institucional (`doc/homologacao-com-o-seletor-de-demonstracao.md`).
GESTAO = "treino.gestao"
ELABORACAO = "treino.elaboracao"
HOMOLOGACAO = "treino.homologacao"
PUBLICACAO = "treino.publicacao"
PRESIDENCIA = "treino.presidencia"
AVALIACAO_1 = "treino.avaliacao1"
AVALIACAO_2 = "treino.avaliacao2"
EQUIPE = (GESTAO, ELABORACAO, HOMOLOGACAO, PUBLICACAO, PRESIDENCIA, AVALIACAO_1, AVALIACAO_2)

# Os papéis que cada ator exerce, nos nomes do seletor (`interface/identidade.PAPEIS`). O gerador
# não inventa capacidade: cada ator recebe só as permissões que o papel dele dá na tela.
_PERMISSOES = {
    GESTAO: (
        "processo:criar",
        "edital:criar",
        "edital:cancelar",
        "processo:cancelar",
        "comissao:gerir",
        "inscricao:consultar",
    ),
    ELABORACAO: (
        "edital:elaborar",
        "edital:submeter",
        "retificacao:elaborar",
        "retificacao:submeter",
    ),
    HOMOLOGACAO: ("edital:homologar", "retificacao:homologar"),
    PUBLICACAO: ("edital:publicar", "retificacao:publicar", "resultado:publicar"),
    # Presidir e avaliar não são papéis: a base é o vínculo com a comissão do Processo.
    PRESIDENCIA: (),
    AVALIACAO_1: (),
    AVALIACAO_2: (),
}

# O texto que marca todo arquivo e todo ato do gerador. Vai no PDF fictício, nas justificativas e
# nos pareceres — de modo que nenhum documento produzido em treinamento se passe por ato real
# (FR-4633).
MARCA = "TREINAMENTO — DADO FICTÍCIO, SEM VALOR LEGAL"


def pdf_ficticio(titulo):
    """Um PDF de uma página, válido, com a marca de treinamento escrita nele."""
    # Latin-1 é o que a fonte padrão do PDF escreve; o travessão não existe nela e sairia "?".
    texto = f"{MARCA} - {titulo}".replace("—", "-").encode("latin-1", "replace")
    texto = texto.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    conteudo = b"BT /F1 12 Tf 40 760 Td (" + texto + b") Tj ET"
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(conteudo)).encode() + b" >>\nstream\n" + conteudo + b"\nendstream",
    ]
    corpo = b"%PDF-1.4\n"
    posicoes = []
    for numero, objeto in enumerate(objetos, 1):
        posicoes.append(len(corpo))
        corpo += f"{numero} 0 obj\n".encode() + objeto + b"\nendobj\n"
    xref = len(corpo)
    corpo += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    for posicao in posicoes:
        corpo += f"{posicao:010d} 00000 n \n".encode()
    corpo += (
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode()
    return corpo


def arquivo_ficticio(titulo, nome):
    return SimpleUploadedFile(nome, pdf_ficticio(titulo), content_type="application/pdf")


# ---------------------------------------------------------------------------------------------
# Os moldes do rascunho
# ---------------------------------------------------------------------------------------------

DOC_IDENTIFICACAO = do_molde("61")
DOC_DIPLOMA = do_molde("62")
DOC_RESIDENCIA = do_molde("63")
DOC_AUTODECLARACAO = do_molde("64")
PERFIL = do_molde("b1")
MARCO = do_molde("a1")
ETAPA_PROVA = do_molde("d1")
ETAPA_TITULOS = do_molde("d2")
ETAPA_DOCUMENTAL = do_molde("d3")
AMPLA = do_molde("e1")
RESERVADA = do_molde("e2")
EVENTO_INSCRICOES = do_molde("c1")


def perfil_de_notas(*, vagas=4, janela="declarada"):
    """O Perfil docente do `seed_demo`, com desempate declarado e quatro vagas.

    **O desempate é pela nota da prova**, que é o critério que não pede fato declarado do candidato.
    É ele que torna o empate dos totais um exercício: dois candidatos com a mesma soma e provas
    diferentes se separam, e dois com tudo igual permanecem empatados (o empate residual).
    """
    perfil = copy.deepcopy(molde.perfis(MOLDE, janela_recursal=janela)[0])
    perfil["immediateVacancies"] = vagas
    for linha in perfil["vacancyTable"]:
        linha["immediateVacancies"] = vagas - 1 if linha["modalityId"] is None else 1
    marco = perfil["classificationMilestones"][0]
    marco["tiebreakers"] = [
        {
            "id": do_molde("a9"),
            "order": 1,
            "type": "MAIOR_PONTUACAO_NA_ETAPA",
            "parameters": {"stageId": ETAPA_PROVA},
            "whenMissing": "ULTIMO_NO_CRITERIO",
        }
    ]
    marco["cutRule"]["targetCount"] = vagas
    marco["cutRule"]["surplusCount"] = 2
    return [perfil]


def perfil_de_sorteio(*, vagas=4):
    """O Perfil do sorteio do `seed_demo`, só com a ampla concorrência e menos vagas que inscritos.

    **Menos vagas que inscritos** é o que torna o sorteio um exercício: com as quarenta vagas do
    molde, todo inscrito estaria classificado e a ordem não decidiria nada.
    """
    perfil = copy.deepcopy(molde.perfil_de_sorteio(MOLDE)[0])
    perfil["immediateVacancies"] = vagas
    perfil["competitionModalities"] = [
        m for m in perfil["competitionModalities"] if m["id"] == AMPLA
    ]
    perfil.pop("vacancyTable", None)
    perfil["classificationMilestones"][0]["cutRule"]["targetCount"] = vagas
    return [perfil]


def documentos_de_notas():
    """A identificação na inscrição; diploma, residência e autodeclaração na convocação (115).

    A autodeclaração é só da modalidade reservada: para quem concorre na ampla, o item da
    convocação nasce **não se aplica** — o caso da `131` que a conferência precisa mostrar.
    """
    return [
        {
            "id": DOC_IDENTIFICACAO,
            "key": "identificacao",
            "name": "Documento de identificação com foto",
            "instructions": "Frente e verso em arquivo único.",
            "required": True,
            "order": 1,
        },
        {
            "id": DOC_DIPLOMA,
            "key": "diploma",
            "name": "Diploma de graduação",
            "instructions": "Diploma ou certidão de conclusão, com histórico.",
            "required": True,
            "order": 2,
            "moment": "AT_CALL",
            "profileId": PERFIL,
        },
        {
            "id": DOC_RESIDENCIA,
            "key": "residencia",
            "name": "Comprovante de residência",
            "instructions": "Emitido nos últimos três meses.",
            "required": True,
            "order": 3,
            "moment": "AT_CALL",
        },
        {
            "id": DOC_AUTODECLARACAO,
            "key": "autodeclaracao",
            "name": "Autodeclaração étnico-racial",
            "instructions": "Conforme o modelo do Anexo do Edital.",
            "required": True,
            "order": 4,
            "moment": "AT_CALL",
            "modalityId": RESERVADA,
        },
    ]


def documentos_de_sorteio():
    return documentos_de_notas()[:1]


def metodo_do_sorteio(concurso):
    """O método do `seed_demo`, com a **Fonte de demonstração** e um concurso próprio da rodada.

    **A fonte é a de demonstração, e não a Loteria Federal** (134, D-004). A extração da Caixa é
    fato futuro e público: um cenário que dependesse dela faria o operador esperar o sábado — o
    que o pedido proíbe — ou citaria um concurso já realizado, que a conferência da `116` acusa e
    que tornaria o resultado conhecido antes do congelamento. A fonte de demonstração existe para
    isto (046, `FR-757`): o nome dela é publicado no Edital, no manifesto e no comprovante, ela só
    existe onde `SORTEIO_FONTE_DE_DEMONSTRACAO` a liga, e produção recusa subir com a chave.

    **O concurso é da rodada**: a ocorrência é única por fonte e referência no acervo inteiro, e
    duas rodadas que citassem o mesmo número partilhariam a observação — a segunda recusaria.
    """
    metodo = molde.metodo_comum_do_edital(MOLDE)
    metodo["occurrence"] = concurso
    metodo["derivation"] = (
        f"Concurso {concurso} da fonte de demonstração (cenário de treinamento, sem valor legal)."
    )
    return metodo


# ---------------------------------------------------------------------------------------------
# A montagem
# ---------------------------------------------------------------------------------------------


@dataclass
class Montagem:
    """Uma rodada de um cenário em construção: os identificadores dela e o que já foi criado."""

    codigo: str
    rodada: int
    unidade: str
    autoridade_id: str
    titulo: str
    saida: object = None
    agora: object = None
    registros: dict = field(default_factory=dict)
    pessoas: list = field(default_factory=list)

    def __post_init__(self):
        self.agora = self.agora or timezone.now()
        self.correlacao = f"treinamento-{self.codigo}-r{self.rodada}"

    # -- identidade e atores --------------------------------------------------------------

    def id(self, molde_ou_posicao):
        posicao = molde_ou_posicao[-2:] if len(molde_ou_posicao) == 36 else molde_ou_posicao
        return ids.identificador(self.codigo, self.rodada, posicao)

    def ator(self, subject, *extras):
        return Actor(subject, self.unidade, frozenset(_PERMISSOES[subject]) | frozenset(extras))

    def chave(self, passo):
        """A chave de idempotência do passo: única por rodada, entre 16 e 128 caracteres."""
        return f"{self.correlacao}-{passo}"[:128]

    def remapear(self, valor):
        return ids.remapear(valor, self.codigo, self.rodada)

    def anotar(self, especie, *valores):
        self.registros.setdefault(especie, []).extend(str(valor) for valor in valores)

    def dizer(self, texto):
        if self.saida is not None:
            self.saida.write(f"  {texto}")

    @property
    def numero(self):
        """O número do Edital: `SIM07`, e `SIM07R2` a partir da segunda rodada."""
        base = f"SIM{self.codigo[1:]}"
        return base if self.rodada == 1 else f"{base}R{self.rodada}"

    @property
    def codigo_do_processo(self):
        base = f"SIM-TREINAMENTO-{int(self.codigo[1:]):03d}"
        return base if self.rodada == 1 else f"{base}-R{self.rodada}"

    # -- Processo e Edital ----------------------------------------------------------------

    def criar(self):
        from processo_seletivo.processos.application.commands import (
            create_process_with_first_edital,
        )
        from processo_seletivo.processos.models import Edital

        rotulo = f"{self.codigo_do_processo} — {self.titulo} (FICTÍCIO)"
        self.dizer(f"Criando o Processo {self.codigo_do_processo}…")
        processo, _ = create_process_with_first_edital(
            actor=self.ator(GESTAO),
            data={
                "institutionalCode": self.codigo_do_processo,
                "title": rotulo[:255],
                "firstEdital": {
                    "number": self.numero,
                    "year": self.agora.year,
                    "title": f"Edital {self.numero}/{self.agora.year} — {self.titulo} "
                    "(treinamento)",
                    "description": (
                        f"{MARCA}. Edital fictício do cenário {self.codigo}, criado pelo gerador "
                        "de cenários de treinamento para exercício da equipe de seleção."
                    ),
                },
            },
            idempotency_key=self.chave("processo"),
            correlation_id=self.correlacao,
        )
        edital = Edital.objects.get(processo=processo)
        self.processo, self.edital = processo, edital
        self.anotar("processo", processo.id)
        self.anotar("edital", edital.id)
        return edital

    def elaborar(self, *, perfis, inicio, duracao_dias, documentos, metodo=None, etapas=None):
        """Grava o rascunho: os moldes remapeados, com o período de inscrições pedido.

        `inicio` e `duracao_dias` são o período de inscrições; os demais eventos do molde se
        deslocam junto, para que a sequência do cronograma continue coerente.
        """
        from processo_seletivo.editais.application.draft import replace_draft

        calendario = molde.cronograma(inicio, MOLDE)
        calendario[0]["endAt"] = inicio + timedelta(days=duracao_dias)
        argumentos = {
            "profiles": self.remapear(perfis),
            "schedule": self.remapear(calendario),
            "stages": self.remapear(self._etapas(etapas)),
            "document_requirements": self.remapear(documentos),
        }
        if metodo is not None:
            argumentos["draw_method"] = self.remapear(metodo)
        replace_draft(
            actor=self.ator(ELABORACAO),
            edital_id=self.edital.id,
            expected_revision=self.edital.revision,
            correlation_id=self.correlacao,
            **argumentos,
        )
        self.edital.refresh_from_db()

    @staticmethod
    def _etapas(escolhidas):
        """As Etapas do molde: todas, ou só as `escolhidas` (identificadores do molde).

        O Edital de sorteio fica só com a Etapa que o marco enumera: as outras duas do molde
        apareciam como providência de distribuição e como alerta de avaliador na supervisão, ruído
        que confundia o exercício do sorteio (visto no navegador, no C07).
        """
        todas = molde.etapas(MOLDE)
        if escolhidas is None:
            return todas
        return [etapa for etapa in todas if etapa["id"] in escolhidas]

    def publicar(self):
        from processo_seletivo.publicacoes.application.publish_edital import (
            homologate_edital,
            publish_edital,
            submit_edital,
        )

        self.dizer("Submetendo, homologando e publicando o Edital…")
        edital, _, _ = submit_edital(
            actor=self.ator(ELABORACAO),
            edital_id=self.edital.id,
            expected_revision=self.edital.revision,
            idempotency_key=self.chave("submeter"),
            correlation_id=self.correlacao,
        )
        edital, _ = homologate_edital(
            actor=self.ator(HOMOLOGACAO),
            edital_id=edital.id,
            expected_revision=edital.revision,
            reason=f"Conferido para treinamento. {MARCA}.",
            idempotency_key=self.chave("homologar"),
            correlation_id=self.correlacao,
        )
        publish_edital(
            actor=self.ator(PUBLICACAO),
            edital_id=edital.id,
            expected_revision=edital.revision,
            autoridade_id=self.autoridade_id,
            reason=f"Publicação de Edital de treinamento. {MARCA}.",
            idempotency_key=self.chave("publicar"),
            correlation_id=self.correlacao,
        )
        self.edital.refresh_from_db()

    def retificar(self, mudancas, justificativa, passo):
        from processo_seletivo.publicacoes.application.retificacoes import (
            create_retification,
            publish_retification,
            transition_retification,
        )
        from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

        base = VersaoConsolidada.objects.filter(edital=self.edital).latest("materialized_at")
        retificacao, _ = create_retification(
            actor=self.ator(ELABORACAO),
            edital_id=self.edital.id,
            data={
                "baseSnapshotId": base.id,
                "justification": f"{justificativa} {MARCA}.",
                "changes": mudancas,
            },
            idempotency_key=self.chave(f"{passo}-elaborar"),
            correlation_id=self.correlacao,
        )
        for acao, quem in (("submeter", ELABORACAO), ("homologar", HOMOLOGACAO)):
            retificacao, _ = transition_retification(
                actor=self.ator(quem),
                retificacao_id=retificacao.id,
                expected_revision=retificacao.revision,
                action=acao,
                reason="Conferido para treinamento.",
                idempotency_key=self.chave(f"{passo}-{acao}"),
                correlation_id=self.correlacao,
            )
        publish_retification(
            actor=self.ator(PUBLICACAO),
            retificacao_id=retificacao.id,
            expected_revision=retificacao.revision,
            autoridade_id=self.autoridade_id,
            idempotency_key=self.chave(f"{passo}-publicar"),
            correlation_id=self.correlacao,
        )
        self.anotar("retificacao", retificacao.id)
        self.edital.refresh_from_db()

    def encerrar_inscricoes(self, encerramento):
        """O prazo encerrado por Retificação, como no `seed_demo` (`028`, FR-355).

        Publicar com o prazo já vencido é recusado — um certame que ninguém pode disputar —, e o
        ato que existe para encurtar o prazo é a Retificação.
        """
        self.dizer("Encerrando as inscrições por Retificação…")
        self.retificar(
            [
                {
                    "targetPath": f"/schedule/id={self.id(EVENTO_INSCRICOES)}/endAt",
                    "operation": "REPLACE",
                    "newValue": encerramento.isoformat(),
                }
            ],
            "Encerramento do prazo de inscrições do cenário de treinamento.",
            "encerrar",
        )

    # -- Candidatos --------------------------------------------------------------------------

    def dar_acesso(self, pessoa):
        """Identidade e e-mail verificado da pessoa fictícia, como em `seed_demo._dar_acesso`."""
        from processo_seletivo.identidade.domain.enderecos import canonizar
        from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity

        identidade, _ = CandidateIdentity.objects.get_or_create(
            subject=pessoa["subject"],
            defaults={
                "nome": pessoa["nome"],
                "cpf_normalizado": pessoa["cpf"].replace(".", "").replace("-", ""),
                "created_at": self.agora,
            },
        )
        CandidateEmail.objects.get_or_create(
            email_canonico=canonizar(pessoa["email"]),
            defaults={
                "identidade": identidade,
                "email_como_informado": pessoa["email"],
                "principal": True,
                "verified_at": self.agora,
                "created_at": self.agora,
            },
        )
        self.anotar("identidade_do_candidato", identidade.pk)

    def identidade(self, pessoa):
        from processo_seletivo.portal.identidade import IdentidadeDoCandidato

        return IdentidadeDoCandidato(
            pessoa["subject"], pessoa["nome"], pessoa["cpf"], pessoa["email"]
        )

    def inscrever(self, quantidade, *, reservada=()):
        """Inscrições **enviadas** pelo caminho do portal: abrir, escolher, anexar, enviar.

        `reservada` são as ordens (1, 2, …) de quem concorre na modalidade reservada; as demais
        concorrem na ampla. Precisa rodar com o período aberto — é a regra do envio.
        """
        from processo_seletivo.inscricoes.application.rascunho import (
            abrir_inscricao,
            anexar_documento,
            gravar_dados,
        )
        from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

        self.dizer(f"Enviando {quantidade} inscrições fictícias pelo caminho do portal…")
        inscricoes = []
        inicio = len(self.pessoas)
        for ordem in range(inicio + 1, inicio + quantidade + 1):
            pessoa = ids.pessoa(self.codigo, self.rodada, ordem)
            self.pessoas.append(pessoa)
            self.dar_acesso(pessoa)
            identidade = self.identidade(pessoa)
            inscricao = abrir_inscricao(
                identidade=identidade,
                edital_id=self.edital.id,
                profile_id=self.id(PERFIL),
                correlation_id=self.correlacao,
            )
            modalidade = self.id(RESERVADA if ordem in reservada else AMPLA)
            inscricao = gravar_dados(
                identidade=identidade,
                inscricao=inscricao,
                dados={"modality_id": modalidade},
                correlation_id=self.correlacao,
            )
            anexar_documento(
                identidade=identidade,
                inscricao=inscricao,
                requirement_id=self.id(DOC_IDENTIFICACAO),
                arquivo=arquivo_ficticio(
                    f"Identificacao de {pessoa['nome']}", "identificacao-ficticia.pdf"
                ),
                correlation_id=self.correlacao,
            )
            inscricao = enviar_inscricao(
                identidade=identidade,
                inscricao=inscricao,
                declaracoes={"veracidade": True, "ciencia": True},
                idempotency_key=self.chave(f"inscricao-{ordem:02d}"),
                correlation_id=self.correlacao,
            )
            self.anotar("inscricao", inscricao.id)
            inscricoes.append(inscricao)
        return inscricoes

    # -- Comissão e avaliação -------------------------------------------------------------

    def constituir_comissao(self, *, alocar_em=()):
        """Presidência e dois avaliadores, alocados nas Etapas pedidas (019, 018 FR-068).

        Dois avaliadores pela razão do `seed_demo`: a reavaliação determinada por recurso exige
        avaliador diverso do que concluiu a original.
        """
        from processo_seletivo.comissoes.application.alocacao import alocar
        from processo_seletivo.comissoes.application.comissao import adicionar_membro
        from processo_seletivo.comissoes.domain.funcoes import Funcao

        self.dizer("Constituindo a comissão…")
        gestor = self.ator(GESTAO)
        self.membros = {}
        for indice, (subject, funcao) in enumerate(
            (
                (PRESIDENCIA, Funcao.PRESIDENTE),
                (AVALIACAO_1, Funcao.MEMBRO),
                (AVALIACAO_2, Funcao.MEMBRO),
            )
        ):
            membro, _ = adicionar_membro(
                actor=gestor,
                processo_id=self.processo.id,
                identity_subject=subject,
                funcao=funcao,
                idempotency_key=self.chave(f"membro-{indice}"),
                correlation_id=self.correlacao,
            )
            self.membros[subject] = membro
            self.anotar("membro", membro.id)
        for etapa in alocar_em:
            for subject in (AVALIACAO_1, AVALIACAO_2):
                alocar(
                    actor=gestor,
                    processo_id=self.processo.id,
                    membro_id=self.membros[subject].id,
                    edital_id=self.edital.id,
                    etapa_id=self.id(etapa),
                    idempotency_key=self.chave(f"alocar-{etapa[-2:]}-{subject[-1]}"),
                    correlation_id=self.correlacao,
                )

    def distribuir(self, etapa, inscricoes, avaliador=AVALIACAO_1):
        from processo_seletivo.avaliacoes.application.distribuicao import distribuir

        distribuir(
            actor=self.ator(GESTAO),
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            etapa_id=self.id(etapa),
            membro_ids=[self.membros[avaliador].id],
            inscricao_ids=[item.id for item in inscricoes],
            idempotency_key=self.chave(f"lote-{etapa[-2:]}"),
            correlation_id=self.correlacao,
        )

    def avaliar(self, etapa, notas, *, consolidar=True):
        """Distribui, conclui e consolida uma Etapa. `notas` é {inscrição: pontuação ou sentido}.

        Pontuação é `Decimal`; nas Etapas decisórias, a chave vale `"FAVORAVEL"` ou
        `"DESFAVORAVEL"`, e não há nota.
        """
        from processo_seletivo.avaliacoes.application.avaliacao import concluir
        from processo_seletivo.publicacoes.application.selectors import effective_version
        from processo_seletivo.resultados.application.consolidacao import (
            consolidar as consolidar_etapa,
        )

        inscricoes = list(notas)
        self.distribuir(etapa, inscricoes)
        versao = effective_version(edital_id=self.edital.id)
        quem = self.ator(AVALIACAO_1)
        for inscricao, valor in notas.items():
            decisoria = isinstance(valor, str)
            concluir(
                ator=quem,
                edital=self.edital,
                etapa_id=self.id(etapa),
                inscricao_id=inscricao.id,
                pontuacao=None if decisoria else valor,
                parecer=f"Avaliação de treinamento. {MARCA}.",
                expected_revision=1,
                versao_reconhecida=versao.id,
                correlation_id=self.correlacao,
                **({"sentido": valor} if decisoria else {}),
            )
        if consolidar:
            consolidar_etapa(
                actor=self.ator(PRESIDENCIA),
                processo_id=self.processo.id,
                edital_id=self.edital.id,
                etapa_id=self.id(etapa),
                inscricao_ids=[item.id for item in inscricoes],
                idempotency_key=self.chave(f"consolidar-{etapa[-2:]}"),
                correlation_id=self.correlacao,
            )

    # -- Ordem, resultado, corte, apuração e convocação ------------------------------------

    def emitir_ordem(self, lista=None, quem=PRESIDENCIA):
        from processo_seletivo.classificacao.application.calculo import calcular_ordem
        from processo_seletivo.classificacao.application.emissao import (
            assinatura_da_proposta,
            emitir_ordem,
        )
        from processo_seletivo.classificacao.models import AtoDeOrdenacao

        lista_id = self.id(lista) if lista else None
        self.dizer("Emitindo a ordem classificatória…")
        proposta = calcular_ordem(
            edital=self.edital,
            perfil_id=self.id(PERFIL),
            marco_id=self.id(MARCO),
            lista_id=lista_id,
        )
        emitir_ordem(
            actor=self.ator(quem),
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            perfil_id=self.id(PERFIL),
            marco_id=self.id(MARCO),
            lista_id=lista_id,
            idempotency_key=self.chave(f"ordem-{lista[-2:] if lista else 'ampla'}"),
            correlation_id=self.correlacao,
            confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=None),
        )
        ato = AtoDeOrdenacao.objects.get(
            edital=self.edital, marco_id=self.id(MARCO), lista_id=lista_id, sucessores__isnull=True
        )
        self.anotar("ato_de_ordenacao", ato.id)
        return ato

    def divulgar(self, ato, natureza="PRELIMINAR", declaracao=""):
        """Divulga o ato. `declaracao` é a do encerramento do prazo, que o definitivo exige quando o
        marco não tem janela computável (a FR-085 da `018`) — e recusa quando tem."""
        from processo_seletivo.divulgacao.application.publicar import (
            assinatura_da_previa,
            publicar_resultado,
        )
        from processo_seletivo.divulgacao.domain.conteudo import compor

        self.dizer(f"Divulgando o resultado {natureza.lower()}…")
        publicacao = publicar_resultado(
            actor=self.ator(PUBLICACAO),
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            marco_id=self.id(MARCO),
            ato_id=ato.id,
            natureza=natureza,
            autoridade=self.autoridade_id,
            confirmacao_da_previa=assinatura_da_previa(
                ato=ato, publicacao_anterior=None, projecao=compor(ato)
            ),
            idempotency_key=self.chave(f"divulgar-{natureza.lower()}"),
            correlation_id=self.correlacao,
            declaracao_de_encerramento=declaracao,
        )
        self.anotar("publicacao_de_resultado", publicacao.id)
        return publicacao

    def cortar_e_apurar(self):
        from processo_seletivo.classificacao.application.corte import calcular_corte
        from processo_seletivo.classificacao.application.emissao_do_corte import (
            assinatura_da_proposta,
            emitir_corte,
        )
        from processo_seletivo.ocupacao.application.emissao import emitir_apuracao

        self.dizer("Emitindo a faixa de corte e apurando a ocupação…")
        presidencia = self.ator(PRESIDENCIA)
        emitir_corte(
            actor=presidencia,
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            perfil_id=self.id(PERFIL),
            marco_id=self.id(MARCO),
            idempotency_key=self.chave("corte"),
            correlation_id=self.correlacao,
            confirmacao_do_calculo=assinatura_da_proposta(
                calcular_corte(
                    edital=self.edital, perfil_id=self.id(PERFIL), marco_id=self.id(MARCO)
                )
            ),
        )
        emitir_apuracao(
            actor=presidencia,
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            perfil_id=self.id(PERFIL),
            marco_id=self.id(MARCO),
            lista_id=None,
            idempotency_key=self.chave("apurar"),
            correlation_id=self.correlacao,
            motivo="",
        )

    def convocar(self, inscricao, ordem):
        from processo_seletivo.convocacao.application.convocar import convocar
        from processo_seletivo.convocacao.models import Convocacao

        convocar(
            actor=self.ator(PRESIDENCIA),
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            perfil_id=self.id(PERFIL),
            marco_id=self.id(MARCO),
            inscricao_id=inscricao.id,
            especie="VAGA_INICIAL",
            fundamento=f"Convocação de treinamento. {MARCA}.",
            vencimento=self.agora + timedelta(days=30),
            idempotency_key=self.chave(f"convocar-{ordem:02d}"),
            correlation_id=self.correlacao,
        )
        convocacao = Convocacao.objects.filter(edital=self.edital, inscricao=inscricao).latest(
            "criado_em"
        )
        self.anotar("convocacao", convocacao.id)
        return convocacao

    def comunicar(self, convocacao, ordem):
        from processo_seletivo.convocacao.application.comunicar import comunicar

        comunicar(
            actor=self.ator(PRESIDENCIA),
            processo_id=self.processo.id,
            convocacao_id=convocacao.id,
            idempotency_key=self.chave(f"comunicar-{ordem:02d}"),
            correlation_id=self.correlacao,
        )

    def itens(self, convocacao):
        from processo_seletivo.convocacao.models import ItemDaListaDaConvocacao

        return {
            str(item.requisito_id): item
            for item in ItemDaListaDaConvocacao.objects.filter(chamada=convocacao).exclude(
                situacao=ItemDaListaDaConvocacao.Situacao.NAO_SE_APLICA
            )
        }

    def apresentar(self, convocacao, inscricao, requisito, versao=1):
        """O convocado entrega um arquivo fictício para um item, pelo comando do portal.

        `versao` muda o conteúdo: o mesmo arquivo reenviado é reconhecido pelo resumo e não conta
        como entrega nova, que é o que a correção de uma pendência precisa ser.
        """
        from processo_seletivo.convocacao.application.documentos import apresentar

        pessoa = next(p for p in self.pessoas if p["subject"] == inscricao.identity_subject)
        item = self.itens(convocacao)[self.id(requisito)]
        nome = f"{item.chave}-ficticio.pdf"
        apresentada = apresentar(
            identidade=self.identidade(pessoa),
            inscricao_id=inscricao.id,
            item_id=item.id,
            arquivo=arquivo_ficticio(f"{item.chave} de {pessoa['nome']} (versao {versao})", nome),
            nome_original=nome,
            correlation_id=self.correlacao,
        )
        self.anotar("apresentacao", apresentada.apresentacao.id)
        return apresentada.apresentacao

    def conferir(self, convocacao, requisito, apresentacao, resultado, motivo=""):
        from processo_seletivo.convocacao.application.documentos import conferir

        item = self.itens(convocacao)[self.id(requisito)]
        return conferir(
            actor=self.ator(PRESIDENCIA),
            item_id=item.id,
            apresentacao_id=apresentacao.id,
            resultado=resultado,
            motivo=motivo,
            idempotency_key=self.chave(f"conferir-{str(item.id)[:8]}"),
            correlation_id=self.correlacao,
        )

    # -- Sorteio -----------------------------------------------------------------------------

    def congelar_relacao(self):
        from processo_seletivo.sorteios.application.relacao import publicar_relacao

        self.dizer("Congelando a relação de participantes do sorteio…")
        relacao = publicar_relacao(
            actor=self.ator(PRESIDENCIA),
            processo_id=self.processo.id,
            edital_id=self.edital.id,
            perfil_id=self.id(PERFIL),
            marco_id=self.id(MARCO),
            idempotency_key=self.chave("relacao"),
            correlation_id=self.correlacao,
        )
        self.anotar("relacao_do_sorteio", relacao["relacao"])
        return relacao


def notas_de(inscricoes, valores):
    return {
        inscricao: Decimal(valor) for inscricao, valor in zip(inscricoes, valores, strict=False)
    }
