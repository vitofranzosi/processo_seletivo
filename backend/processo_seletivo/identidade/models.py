"""A identidade do candidato, suas credenciais e o desafio que prova o controle de um endereço.

Três tabelas, e nenhuma delas concede permissão: o candidato não é ator institucional, e é a
Inscrição que ele possui, não um escopo (P-006). A ligação com `Inscricao` é **por valor**, através
do `subject` — não é chave estrangeira, e não passa a ser: a `010` tem proibição expressa de tocar
naquele campo (FR-042). É essa ausência que obriga o bloqueio compartilhado da reconciliação.
"""

import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

PREFIXO = "cand"
# Dez minutos, e o mesmo prazo para as duas coisas que expiram: o código e a decisão de
# reconciliar que ele abre. Duas durações diferentes seriam duas explicações a dar.
VALIDADE_EM_MINUTOS = 10
TETO_DE_TENTATIVAS = 5


def novo_subject() -> str:
    """Opaco, estável, e devendo nada a segredo de configuração nem a dado pessoal (FR-002).

    O provedor de demonstração derivava o identificador do CPF por meio da `SECRET_KEY`, e por
    isso a propriedade de cada inscrição era refém da rotação de um segredo — trocá-lo tornaria o
    que a pessoa submeteu inalcançável por ela, em silêncio. Aqui não há nada a rotacionar.

    O prefixo mantém os dois conjuntos distinguíveis para sempre, inclusive depois que a
    identificação por declaração desaparecer: um `subject` diz de onde veio.
    """
    return f"{PREFIXO}:{uuid.uuid4().hex}"


class CandidateIdentity(models.Model):
    """Quem é a pessoa para o sistema, de forma persistente.

    `nome` e `cpf_normalizado` existem porque a Inscrição os exige — o nome vai no comprovante, e é
    por ele que a conferência documental acontece (FR-004). Ambos nascem vazios: a identidade que a
    reconciliação materializa já os traz, e a que o primeiro acesso cria só os ganha na primeira
    inscrição. Identidade sem credencial e sem nome é estado válido, e não defeito.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=255, unique=True)
    nome = models.CharField(max_length=255, blank=True)
    # Declarado pelo titular, nunca provado — a validação dos dígitos diz apenas que o número é um
    # CPF possível (FR-006, FR-007). Ele não decide propriedade nem acesso em nenhum caminho, e
    # **não** é único: duas identidades podem declarar o mesmo, e a coincidência é assinalada onde
    # importa em vez de bloqueada onde machuca (FR-064).
    cpf_normalizado = models.CharField(max_length=11, blank=True)
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Identidade {self.subject}"


class CandidateEmail(models.Model):
    """Um endereço cujo controle foi provado.

    Não existe linha "não verificada": esta tabela guarda credencial. O endereço que a `009`
    gravou numa Inscrição é indício histórico, e indício não autentica ninguém (FR-015).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identidade = models.ForeignKey(
        CandidateIdentity, on_delete=models.CASCADE, related_name="credenciais"
    )
    email_canonico = models.CharField(max_length=254)
    # O endereço como a pessoa informou, preservado para exibição e nada além: ele nunca decide
    # identidade — a mesma regra que a 009 aplica ao nome de arquivo enviado.
    email_como_informado = models.CharField(max_length=254)
    principal = models.BooleanField(default=False)
    verified_at = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        constraints = [
            # Exclusividade **por restrição**, e não por consulta prévia (FR-011). Verificar antes
            # de gravar perde a corrida entre duas confirmações simultâneas, e o que se perde
            # nessa corrida é a exclusividade de uma credencial.
            models.UniqueConstraint(
                Lower("email_canonico"), name="uq_credencial_email_canonico"
            ),
            # Uma identidade **que tenha credencial** tem exatamente uma principal. A restrição é
            # parcial porque a outra metade — não ficar sem principal — não é invariante de linha:
            # a reconciliação cria identidade sem credencial alguma, e isso é estado válido.
            models.UniqueConstraint(
                fields=["identidade"],
                condition=Q(principal=True),
                name="uq_credencial_principal_por_identidade",
            ),
        ]

    def __str__(self):
        return self.email_canonico


class DesafioDeAcesso(models.Model):
    """A tentativa de provar o controle de um endereço — e, quando é o caso, o que ela abre.

    **Consumir o código não é o fim da linha.** Havendo participação anterior associada àquele
    endereço, esta mesma linha passa a portar a reconciliação pendente, e é ela que conta as
    tentativas de CPF (D-016). A sessão não serviria de portadora — uma aba nova zeraria a
    contagem, que é justamente o caminho de quem está adivinhando. E a identidade alvo serviria de
    alvo: um terceiro esgotaria as tentativas e impediria o titular legítimo de reconciliar, que é
    a mesma classe de bloqueio que esta feature passou três revisões eliminando (FR-052c).

    Não é dado permanente de domínio (FR-033): linha terminal é descartável por rotina.
    """

    class Finalidade(models.TextChoices):
        ENTRAR = "ENTRAR"
        ADICIONAR_CREDENCIAL = "ADICIONAR_CREDENCIAL"
        # A retomada é finalidade própria, e não um `ENTRAR` com outro nome: ela move credenciais e
        # descarta uma identidade. Um código pedido para entrar não pode autorizar isso (FR-028).
        RETOMAR = "RETOMAR"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_canonico = models.CharField(max_length=254)
    finalidade = models.CharField(max_length=30, choices=Finalidade.choices)
    codigo_hash = models.CharField(max_length=255)
    # Resumo da origem, e nunca o endereço de rede em claro: a contagem por origem não precisa
    # saber de onde veio, só distinguir uma origem da outra (D-005, Princípio III).
    origem_hash = models.CharField(max_length=64, blank=True)
    expira_em = models.DateTimeField()
    tentativas_codigo = models.PositiveSmallIntegerField(default=0)
    tentativas_cpf = models.PositiveSmallIntegerField(default=0)
    consumido_em = models.DateTimeField(null=True, blank=True)
    # Enquanto presente e futuro, esta linha porta a reconciliação pendente (FR-052b).
    reconciliacao_ate = models.DateTimeField(null=True, blank=True)
    # A identidade que a reconciliação criaria vínculo — anotada no consumo, para que a
    # confirmação do CPF não precise refazer a busca e não possa ser desviada para outra.
    # `SET_NULL`, e não `CASCADE`: este campo **anota** qual identidade o convite anunciou, e não
    # compõe nada com ela. Com `CASCADE`, apagar uma identidade levaria junto os desafios que a
    # apontam — inclusive os que contam tentativas de CPF, que é registro de segurança. Hoje não
    # dispararia, porque alvo vem sempre de identidade com inscrição e `retomar()` só descarta as
    # vazias; mas isso é proteção do fluxo, não do modelo. Perdido o alvo, a anotação deixa de
    # valer e o desafio permanece.
    reconciliacao_alvo = models.ForeignKey(
        CandidateIdentity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    criado_em = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["email_canonico", "criado_em"]),
            models.Index(fields=["origem_hash", "criado_em"]),
        ]

    def __str__(self):
        return f"Desafio {self.finalidade} para {self.email_canonico}"
