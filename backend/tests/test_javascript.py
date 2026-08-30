"""Executa os testes de comportamento dos scripts da interface (FR-022 e FR-026 da 003).

Os testes de interface em Python exercitam o que o servidor renderiza. O que acontece **depois**,
no navegador, ficava provado só por busca de string no fonte — o que demonstra que a mensagem foi
escrita, não que ela aparece na situação certa.

`node --test` roda os scripts contra um DOM mínimo e afirma o efeito. Node não é dependência do
projeto: quando não existe, estes testes são ignorados e o resto da suíte segue. O runner do
GitHub Actions já o traz, então a CI os executa.

O que continua fora: a integração com o navegador de verdade — movimentação de foco, anúncio pelo
leitor de tela, o balão que `reportValidity` desenha. Isso é verificação manual, descrita em
quickstart.md.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent
node = pytest.mark.skipif(shutil.which("node") is None, reason="node não está instalado")


@node
@pytest.mark.integration
def test_scripts_da_interface_se_comportam_como_especificado():
    resultado = subprocess.run(
        # Glob explícito: passar o diretório faz o runner tentar carregá-lo como módulo.
        ["node", "--test", "javascript/*.test.js"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    # O runner reporta sucesso mesmo sem encontrar arquivo algum; sem isto, renomear a pasta
    # transformaria a suíte de JavaScript em silêncio aprovado.
    assert "# pass 41" in resultado.stdout or "pass 41" in resultado.stdout, resultado.stdout
