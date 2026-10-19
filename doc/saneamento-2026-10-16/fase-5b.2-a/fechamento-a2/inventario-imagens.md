# Inventario de imagens e digests observados

Consulta HTTPS publica em 16/10/2026, entre 14:14:36 e 14:14:41 UTC. Nenhum Docker, pull, build, blob de configuracao ou camada foi obtido. Tokens anonimos de acesso a repositorios publicos ficaram somente em memoria. O nome `pull` no scope do protocolo Registry autoriza leitura publica de manifestos; nao representa execucao de pull de imagem.

Os bytes UTF-8 dos indices/manifestos e headers publicos estao em [metadados-publicos.json](metadados-publicos.json). O SHA-256 calculado coincidiu com Docker-Content-Digest; nos seis manifestos de plataforma tambem coincidiu com o descritor do indice. Isto verifica integridade dos metadados recebidos por TLS, nao assinatura do fornecedor, vulnerabilidades ou funcionamento da imagem.

| Imagem / origem | Tag consultada e versao declarada | Digest do indice observado |
|---|---|---|
| `docker.io/library/postgres` | `18`; `18.6` | `sha256:74935e72241653ca55e0414067e6d8763aceb8a810eb51b452253ec3dcfc4336` |
| `docker.io/library/python` | `3.13-slim-bookworm`; `3.13.16-slim-bookworm` | `sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641` |
| `ghcr.io/astral-sh/uv` | `0.9`; `0.9.30` | `sha256:538e0b39736e7feae937a65983e49d2ab75e1559d35041f9878b7b7e51de91e4` |

| Imagem | Plataforma candidata | Digest do manifesto |
|---|---|---|
| postgres | `linux/amd64` | `sha256:885953109528ad3dfc90362b1a6f50a78620b5315be19f187753d267e484dc5b` |
| postgres | `linux/arm64/v8` | `sha256:a63b24165ea0eacced7585766d790ac08bbaefe10a1841f87783a4505d29a69c` |
| python | `linux/amd64` | `sha256:f040863673aea2570c3ff6a5c3fb4c673a016cbc5375005ad145915922b6b78a` |
| python | `linux/arm64/v8` | `sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d` |
| uv | `linux/amd64` | `sha256:e96d483a9ed7924d2acf01bdd1d537d0d5e6d8f21b74fff3373005f6c9446696` |
| uv | `linux/arm64` | `sha256:10e89aa55522210851c055c9b261c9c9b4a50ea8ab891e23fe7e138a56287a3e` |

## Fonte, Dockerfile e estrategia

- PostgreSQL: Docker Official Image; annotations apontam o commit `e00e1bd34ec5c8a8e7ad89b273b3d42efaf6d5bc`, caminho `18/trixie`, e base Debian trixie-slim por digest. O Compose apenas referencia imagem, nao a constroi. O Dockerfile de origem foi identificado por metadata, nao baixado/executado.
- Python: Docker Official Image; annotations apontam o commit `d2a898cb88e46203577eabc62cdcf6e92aaee176`, caminho `3.13/slim-bookworm`, e base Debian bookworm-slim por digest. Versao observada 3.13.16 difere do Python local 3.13.15 registrado em 5A; nada foi atualizado.
- uv: GHCR publico da Astral; indice declara versao 0.9.30 e revisao `ea4560831e503c6ce34d18739476a71ac6e9a9de`. Nao presumir versao exata a partir da tag 0.9.
- Aplicacao: nenhuma imagem final disponivel ou ID comprovado. Fonte prevista no commit `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`; Dockerfile de desenvolvimento permanece intacto. O [Dockerfile exclusivo proposto](Dockerfile.homologacao.proposta) fixa os indices Python/uv observados, remove apt/make e bloqueia a entrada por padrao. Nao foi construido ou aprovado para uso.
- Imagens auxiliares de builder: nenhuma selecionada; se a engine requerer builder separado, registrar imagem/digest e obter aprovacao antes de qualquer aquisicao implicita.

O Dockerfile proposto usa `uv sync --locked --extra dev --no-install-project --no-build`, sem assistente, tokenizer, download de Python ou build de sdist. Exige que o lock e as wheels compativeis permitam essa combinacao; isso ainda nao foi exercitado. A importacao do projeto pelo working_dir e dependencias de bibliotecas nativas/PDF precisam de validacao futura. Nao substituir silenciosamente por instalacao com build.

Build futuro depende de registries publicos e das URLs de pacotes no lock, contexto exportado e sanitizado, plataforma, builder e politica de cache/rede aprovados. Retirar apt evita uma fonte mutavel adicional; nao comprova build offline ou byte a byte. Se make passar a ser necessario, revisar explicitamente em vez de acrescentar apt sem controle. Nenhum pacote foi baixado nesta etapa.

Fixar `repositorio@sha256:...`, escolher plataforma apos inspecao autorizada da engine e guardar digest do indice e do manifesto. Comparar config digest e camadas depois de aquisicao autorizada. Guardar ID final, log sanitizado, hashes do contexto/lock/Dockerfile e parametros. Alteracao de base requer nova revisao/aprovacao, nunca atualizacao automatica da tag.

## Fontes publicas e limites

- [Metadata Docker Hub PostgreSQL 18](https://hub.docker.com/v2/repositories/library/postgres/tags/18).
- [Manifestos Docker Registry PostgreSQL](https://registry-1.docker.io/v2/library/postgres/manifests/18).
- [Manifestos Docker Registry Python](https://registry-1.docker.io/v2/library/python/manifests/3.13-slim-bookworm).
- [Manifestos GHCR uv](https://ghcr.io/v2/astral-sh/uv/manifests/0.9).

O navegador de pesquisa nao conseguiu acessar as tres URLs iniciais. A coleta direta bem-sucedida usou somente GET HTTPS de token anonimo e manifestos, sem proxy/heranca Docker nem autenticacao privada, com limite de 2 MiB/resposta e sem redirecionamentos. O [coletor documental](consultar_metadados_publicos.py) foi executado uma vez; nao e script de provisionamento. Validacao e testes posteriores usaram somente os dados locais.

Tags sao moveis: estes digests descrevem o instante observado. As arquiteturas sao candidatas, nao escolha humana nem prova de compatibilidade da engine. Origem declarada e hash nao substituem analise de procedencia/seguranca, autorizacao de aquisicao ou ensaio operacional. Digests nao foram inseridos em homologacao.env; esse arquivo nao foi criado.
