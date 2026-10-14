"""Publica no banco da equipe os Editais da matriz do piloto do assistente (071, T048).

Rode num banco **próprio**, preparado e sem `seed_demo` — o 01/2026 do seed toma o número do 01/2026
do corpus —, no shell do quickstart da `071`, com `testserver` nos hosts aceitos:

    DJANGO_ALLOWED_HOSTS=localhost,testserver uv run python manage.py shell \\
        < scripts/publicar_corpus_do_piloto.py

Publica pelo fluxo real — rascunho, submissão, homologação, publicação e Retificações — os Editais
01, 91 e 92/2026 do corpus da `070`, e os quatro de teste que o corpus não tem, como as fixtures da
suíte os publicam (`tests/fixtures/editais_do_piloto.py`). Imprime o deslocamento em dias, que é o
`--deslocamento-dias` de `avaliar_assistente`.

**Por que em `scripts/`, e não um comando de gestão.** Ele publica pelos ajudantes da suíte
(`tests/fixtures/corpus.py`), que falam com a API como `testserver` e pedem o grupo de dependências
de desenvolvimento. Um comando no pacote levaria a produção a importar a suíte; repetir os ajudantes
num comando faria duas cópias do caminho de publicação do corpus, que precisam concordar. É
ferramenta da equipe, como o `carga_publica.py`.

**Os de teste têm número próprio** — 901 a 904 —, porque a unicidade de número e ano por unidade não
deixa uma cópia do 91/2026 no mesmo banco, e os identificadores do conteúdo são remapeados, porque
Perfis, Eventos, marcos e anexos têm identidade global. Nenhum dos dois muda o que os casos medem: o
texto e os valores são os do 91/2026.

Registra no banco a autoridade signatária da suíte (`tests/fixtures/autoridades.py`): os ajudantes
publicam com ela, e um banco só da avaliação não tem outra que eles conheçam.

Recusa se algum Edital da matriz já estiver no banco: publicar de novo com outro deslocamento faria
os instantes da matriz caírem em outra versão.
"""

import json
import math
import re
import uuid
from datetime import timedelta

from rest_framework.test import APIClient

from processo_seletivo.processos.models import Edital
from tests.fixtures.autoridades import garantir_o_cefor
from tests.fixtures.corpus import deslocamento_ate_agora, publicar_do_corpus
from tests.fixtures.editais_do_piloto import publicar

#: O número de cada Edital de teste na matriz (`duvidas/avaliacao/matriz.json`).
DE_TESTE = {
    "piloto-instrucao": "901",
    "piloto-dois-canais": "902",
    "piloto-fic": "903",
    "piloto-cancelado": "904",
}
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def _proprio(chave, numero):
    """O número próprio e identificadores novos, os mesmos em todo o conteúdo (`uuid5`)."""

    def mudar(conteudo):
        texto = UUID.sub(
            lambda achado: str(uuid.uuid5(uuid.NAMESPACE_URL, f"{chave}:{achado.group()}")),
            json.dumps(conteudo),
        )
        conteudo.clear()
        conteudo.update(json.loads(texto))
        conteudo["number"] = numero

    return mudar


def principal():
    numeros = ["01", "91", "92", *DE_TESTE.values()]
    existentes = sorted(
        Edital.objects.filter(year=2026, number__in=numeros).values_list("number", flat=True)
    )
    if existentes:
        raise SystemExit(
            f"Já estão neste banco: {', '.join(f'{n}/2026' for n in existentes)}. "
            "Use um banco novo: publicar de novo deslocaria a matriz para outra versão."
        )
    # Dias inteiros: o `--deslocamento-dias` da avaliação é inteiro, e meio dia a mais ou a menos
    # levaria um instante da matriz para o outro lado de uma fronteira de vigência.
    dias = math.ceil(deslocamento_ate_agora().total_seconds() / 86400)
    deslocamento = timedelta(days=dias)
    # O signatário dos ajudantes é a autoridade da suíte, que o banco da equipe não tem.
    garantir_o_cefor()
    cliente = APIClient()
    for nome in ("01", "91", "92"):
        publicar_do_corpus(cliente, nome, chave=f"piloto-{nome}", deslocamento=deslocamento)
        print(f"Publicado: {nome}/2026, com as Retificações do corpus")
    for chave, numero in DE_TESTE.items():
        publicar(cliente, chave, mais=_proprio(chave, numero), deslocamento=deslocamento)
        print(f"Publicado: {numero}/2026 ({chave})")
    print(f"Deslocamento: {dias} dias — avaliar_assistente --deslocamento-dias {dias}")


principal()
