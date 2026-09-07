"""Toda leitura de efeito consome `ResultadoEtapa.vigentes`, e as exceções são declaradas.

**Por que existe.** O defeito que esta varredura impede **não produz erro**. Antes da 018, a
unicidade incondicional do par `(inscricao, etapa_id)` tornava impossível existirem dois Resultados
do mesmo par, e por isso `ResultadoEtapa.objects` era, na prática, o vigente. A sucessão removeu
essa garantia — e as leituras que continuassem em `objects` passariam a responder "existe algum"
onde perguntavam "existe o vigente", **em silêncio**:

- o **universo do ato** passaria a citar o Resultado superado. `comparar()` não veria mudança
  nenhuma quando o deferimento acontecesse, o ato não ficaria obsoleto, e a cadeia inteira a
  jusante ficaria cega ao recurso. **É o defeito fatal**, e o único que só o filtro corrige;
- os `Exists` da progressão continuariam excluindo quem teve a eliminação **superada**, tornando o
  deferimento inofensivo exatamente onde ele deveria valer;
- o dicionário de pontuações de `calcular_ordem` colapsaria — este a ordenação determinística
  cobre sozinha, e por isso ela fica no código mesmo com o filtro.

Nenhum teste funcional denuncia isso enquanto não houver um recurso deferido em fixture — e a
próxima feature que escrever `ResultadoEtapa.objects.filter(...)` para responder "existe resultado?"
reintroduz o defeito sem que nada acuse. Por isso a garantia é estrutural, no molde do que
`tests/migrations/test_migrations.py` e a varredura de vocabulário da `013` já fazem.

**As exceções são poucas e cada uma tem razão escrita.** Elas estão abaixo, e acrescentar uma exige
escrever por que aquele ponto precisa ver o superado — que é exatamente a conversa que este teste
existe para forçar (018, T-004, FR-061, FR-062).
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
APLICACAO = RAIZ / "backend" / "processo_seletivo"

USO = re.compile(r"ResultadoEtapa\.objects\.(\w+)")

# Escrever é sempre por `objects`: o manager de vigência é de leitura, e `create` não filtra nada.
ESCRITA = {"create", "bulk_create"}

# Cada entrada é um ponto que **precisa** ver o superado, e a razão pela qual precisa.
EXCECOES = {
    # A reprodução histórica lê os Resultados por `pk__in` dos ids gravados na proveniência do ato.
    # É isso que mantém a IO-5 da `015` verdadeira — a mesma proveniência reproduz a mesma ordem —,
    # e um filtro de vigência aqui quebraria a reprodução no dia do primeiro deferimento.
    "classificacao/application/reproducao.py": (
        "reprodução histórica: lê por id do universo gravado, e o superado é entrada legítima"
    ),
    # A recusa de reabertura protege a Avaliação que fundamentou **qualquer** Resultado, superado
    # inclusive: reabrir mudaria a conclusão histórica que aquele Resultado afirma, e ele continua
    # existindo e sendo consultável (013, D-002).
    # `objeto_atacado` resolve **o que a pessoa clicou**, que pode já ter sido superado enquanto a
    # página estava aberta. Filtrar por vigência devolveria 404 "não encontrado" onde a resposta
    # certa é a recusa que explica o que aconteceu e aponta o vigente (FR-009) — quem lê "não
    # encontrado" conclui que o sistema perdeu o resultado dela. A decisão sobre vigência fica em
    # `_recusar_se_superado`, no mesmo módulo.
    #
    # A dispensa é **deste** módulo, e não da view que o chama: `portal/views.py` tem mil e
    # setecentas linhas, e isentá-lo inteiro deixaria passar calada qualquer leitura futura de
    # efeito no portal. Foi por isso que a busca migrou para cá.
    "recursos/application/interpor.py": (
        "revalidação da interposição: precisa achar o objeto superado para recusá-lo com a "
        "mensagem que aponta o vigente, em vez de responder 404"
    ),
    # O histórico do par responde "o que já valeu", e não "o que vale hoje". Filtrar por vigência
    # aqui devolveria uma linha só e destruiria exatamente a informação que a consulta existe para
    # dar — é a leitura em que ver o superado **é** o requisito (FR-064).
    #
    # A dispensa alcança o módulo inteiro, e por isso `resultados_visiveis` e as demais leituras
    # de efeito que moram nele continuam em `vigentes` por escolha, e não por varredura. É a
    # fraqueza conhecida desta exceção, e o preço de manter as duas consultas juntas: separá-las
    # em módulos só para satisfazer a varredura esconderia a relação entre elas.
    "resultados/application/selectors.py": (
        "histórico do par: a consulta existe para mostrar o superado ao lado do vigente"
    ),
    # O cumprimento da reavaliação pergunta "existe **algum** sucessor deste Resultado protegido?",
    # e a resposta certa inclui o sucessor que já foi sucedido de novo: a decisão foi cumprida
    # naquele momento, e um segundo recurso depois não a torna pendente outra vez. Filtrar por
    # vigência aqui reabriria pendências já cumpridas — silenciosamente, e só nos casos raros de
    # cadeia com três elos (FR-066).
    "recursos/application/selectors.py": (
        "cumprimento da reavaliação: existir sucessor cumpre a decisão, mesmo que ele já tenha "
        "sido sucedido depois"
    ),
    "avaliacoes/application/avaliacao.py": (
        "guarda de reabertura: a Avaliação fonte de um Resultado superado continua protegida"
    ),
}


def _ocorrencias():
    for arquivo in sorted(APLICACAO.rglob("*.py")):
        if "/migrations/" in str(arquivo):
            continue
        texto = arquivo.read_text(encoding="utf-8")
        for metodo in USO.findall(texto):
            yield arquivo.relative_to(APLICACAO).as_posix(), metodo


def test_nenhuma_leitura_de_efeito_escapa_do_manager_de_vigencia():
    fora_do_contrato = [
        (caminho, metodo)
        for caminho, metodo in _ocorrencias()
        if metodo not in ESCRITA and caminho not in EXCECOES
    ]

    assert not fora_do_contrato, (
        "Leitura de `ResultadoEtapa.objects` fora do contrato de vigência: "
        f"{fora_do_contrato}. Use `ResultadoEtapa.vigentes`, ou declare a exceção em "
        "`EXCECOES` explicando por que aquele ponto precisa ver o Resultado superado."
    )


def test_as_excecoes_declaradas_continuam_existindo():
    """Uma exceção que não corresponde mais a nenhum uso é lixo que engana quem lê.

    Se um destes pontos deixar de usar `objects`, a entrada sai — e quem a remover terá de decidir
    conscientemente, em vez de herdar uma permissão sem consumidor.
    """
    usados = {caminho for caminho, _ in _ocorrencias()}

    orfas = sorted(set(EXCECOES) - usados)

    assert not orfas, f"Exceções declaradas e sem uso correspondente: {orfas}"


def test_o_manager_de_vigencia_existe_e_nao_e_o_padrao():
    """`vigentes` é nomeado, e `objects` continua vendo tudo.

    Um default que escondesse os superados faria o caminho correto ser o exótico — e a reprodução
    histórica, que **precisa** vê-los, passaria a ser a chamada estranha.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    nomes = [manager.name for manager in ResultadoEtapa._meta.managers]

    assert nomes[0] == "objects", "o manager padrão precisa continuar vendo os superados"
    assert "vigentes" in nomes
