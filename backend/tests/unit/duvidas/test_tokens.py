"""A contagem pelo tokenizer do modelo, e o que acontece sem ele (071, `R-006`, `FR-1479`)."""

import importlib.util

import pytest

from processo_seletivo.duvidas.infrastructure import tokens


@pytest.fixture(autouse=True)
def _sem_cache():
    tokens._tokenizer.cache_clear()
    yield
    tokens._tokenizer.cache_clear()


def test_sem_o_arquivo_nao_ha_contagem(settings, tmp_path):
    settings.ASSISTENTE_TOKENIZER = str(tmp_path / "nao-existe.json")

    with pytest.raises(tokens.SemTokenizer):
        tokens.contar([{"role": "user", "content": "Até quando vão as inscrições?"}])


def test_sem_caminho_configurado_nao_ha_contagem(settings):
    settings.ASSISTENTE_TOKENIZER = ""

    with pytest.raises(tokens.SemTokenizer):
        tokens.contar([{"role": "user", "content": "x"}])


@pytest.mark.skipif(
    importlib.util.find_spec("tokenizers") is None,
    reason="a `tokenizers` é do grupo opcional `assistente`, e não de desenvolvimento",
)
def test_a_contagem_real_soma_o_acrescimo_por_mensagem(settings, tmp_path):
    """Um tokenizer mínimo, montado aqui, que separa por espaço: o que importa é a soma."""
    from tokenizers import Tokenizer, models, pre_tokenizers

    vocabulario = {"[UNK]": 0, "Até": 1, "quando": 2, "vão": 3}
    modelo = Tokenizer(models.WordLevel(vocab=vocabulario, unk_token="[UNK]"))
    modelo.pre_tokenizer = pre_tokenizers.WhitespaceSplit()
    arquivo = tmp_path / "tokenizer.json"
    modelo.save(str(arquivo))
    settings.ASSISTENTE_TOKENIZER = str(arquivo)
    settings.ASSISTENTE_TOKENS_POR_MENSAGEM = 4

    mensagens = [{"role": "system", "content": "Até quando"}, {"role": "user", "content": "vão"}]

    assert tokens.contar(mensagens) == (2 + 4) + (1 + 4)
