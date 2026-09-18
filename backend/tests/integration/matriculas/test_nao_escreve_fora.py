"""A exportação **lê** — contado em gravações, e não lido no código (`FR-449`, `SC-156`, `SC-155`).

**Por que contar, e não inspecionar.** *"Esta feature não escreve"* é uma promessa que nenhuma
leitura de código mantém por muito tempo: basta alguém acrescentar um `update` *"para marcar como
exportado"*, e a promessa cai sem que nada acuse. O que a prende é ler o SQL que saiu e conferir em
quais tabelas ele escreveu.

**E o arquivo não fica no servidor** (`FR-456`): quem procura no armazenamento não acha nada, porque
nada foi gravado — e é assim que a feature dispensa uma política de retenção em vez de adiá-la.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.matriculas.application.exportar import compor, gerar
from processo_seletivo.matriculas.application.populacao import opcoes
from processo_seletivo.matriculas.models import GeracaoDeArquivo
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

REGISTRO = GeracaoDeArquivo._meta.db_table

# As tabelas que esta feature **lê** e nas quais nunca escreve. **Os nomes saem dos modelos**, e não
# de literais: uma tabela escrita à mão que não case com nada faz a asserção passar sem medir nada,
# que é o modo de um teste de proibição morrer sem avisar.
PROIBIDAS = frozenset(
    modelo._meta.db_table
    for modelo in (Inscricao, RequerimentoDeMatricula, Convocacao, RegistroAuditoria)
)

ESCRITA = ("insert into ", "update ", "delete from ")


def gerar_do(quem_exporta, edital):
    """A geração como a tela a faz: compor a prévia, e confirmar com a assinatura dela."""
    escolhida = opcoes(edital)[0]
    argumentos = {
        "ator": quem_exporta,
        "edital": edital,
        "especie": escolhida.especie,
        "referencia": escolhida.referencia,
    }
    return gerar(**argumentos, confirmacao_do_resumo=compor(**argumentos).assinatura)


def escritas(consultas):
    """As tabelas em que o SQL capturado escreveu, uma vez cada."""
    alcancadas = set()
    for consulta in consultas:
        sql = consulta["sql"].lower()
        for verbo in ESCRITA:
            if verbo not in sql:
                continue
            resto = sql.split(verbo, 1)[1].lstrip()
            alcancadas.add(resto.split()[0].strip('"').strip())
    return alcancadas


def test_uma_geracao_completa_escreve_so_o_registro(cenario, quem_exporta):
    """`SC-156`: a única escrita é a linha da `FR-447`.

    Nem trilha de auditoria: o registro **é** a trilha desta feature, e duplicá-lo criaria duas
    fontes para o mesmo fato. Nem marca de *"já exportado"* na inscrição — a exportação não altera
    requerimento, inscrição, resultado nem Edital.
    """
    edital, _ = cenario
    with CaptureQueriesContext(connection) as consultas:
        gerar_do(quem_exporta, edital)
    alcancadas = escritas(consultas)
    assert alcancadas == {REGISTRO}
    assert not alcancadas & PROIBIDAS


def test_nenhum_arquivo_fica_no_servidor(cenario, quem_exporta, raiz_de_arquivos):
    """`SC-155`, `FR-456`: verificado **no armazenamento**, e não pela ausência de código que grave.

    O arquivo é o artefato mais concentrado de dado pessoal deste sistema. Guardá-lo criaria um
    acervo com prazo de retenção, expurgo e backup próprios; não guardá-lo dispensa os três.
    """
    edital, _ = cenario
    arquivo = gerar_do(quem_exporta, edital)
    assert arquivo.conteudo
    restantes = [caminho for caminho in raiz_de_arquivos.rglob("*") if caminho.is_file()]
    assert not [caminho for caminho in restantes if caminho.suffix == ".xlsx"]


def test_o_registro_nao_pode_ser_alterado(cenario, quem_exporta):
    """`FR-447`: append-only, por gatilho **e** por privilégio ausente.

    O gatilho recusa mesmo quem tenha privilégio; o privilégio ausente recusa mesmo que o gatilho
    seja removido. Nenhuma das duas depende de a aplicação se comportar — e nenhuma das duas é
    exercitada fora do PostgreSQL, que é por que esta suíte roda `make test-pg`.
    """
    from django.db import DatabaseError

    edital, _ = cenario
    arquivo = gerar_do(quem_exporta, edital)
    with pytest.raises(DatabaseError):
        GeracaoDeArquivo.objects.filter(pk=arquivo.geracao.pk).update(quantidade_de_linhas=999)
