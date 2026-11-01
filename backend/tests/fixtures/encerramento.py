"""O encerramento como era antes da `113` — para os testes que precisam de um estado que ela impede.

**Por que existe.** Desde a `113` (FR-3528) encerrar recusa o Edital com período de inscrições por
vir ou em curso, prazo recursal correndo, recurso ou providência pendente, e Retificação homologada.
Vários testes anteriores dependem justamente de um Edital encerrado **nessas** condições: a página
pública diz "encerrado" de um Edital cujo período ainda corria (`047`), a Retificação homologada de
um Edital encerrado é recusada (A-09), a Agenda só mostra o que passou. Esses estados continuam
existindo — em Editais encerrados antes da regra — e o que esses testes provam continua valendo
para eles.

**O que é contornado é só a conferência nova.** O comando roda inteiro — permissão, travas,
idempotência, `AtoAdministrativo`, auditoria —, e só a lista de impedimentos vem vazia. Gravar o
estado direto pelo ORM pularia o ato administrativo, que alguns desses testes leem.
"""

from unittest import mock

from processo_seletivo.processos.application import pendencias_do_edital
from processo_seletivo.processos.application.finalizacao import close_edital


def encerrar_antes_da_113(**argumentos):
    """`close_edital` com os mesmos argumentos, sem a conferência de impedimentos da `113`."""
    with mock.patch.object(pendencias_do_edital, "impedimentos", return_value=[]):
        return close_edital(**argumentos)
