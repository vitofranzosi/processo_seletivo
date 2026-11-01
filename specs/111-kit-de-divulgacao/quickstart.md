# Quickstart: Kit de Divulgação do Edital

Demonstração ponta a ponta pela interface (Princípio VI). Caminhos relativos a `backend/`.

## Preparar

1. Banco próprio desta worktree, preparado e com o corpus publicado:

   ```bash
   createdb -h localhost ps_kit
   ```

   ```bash
   make preparar DB_NAME=ps_kit
   ```

   ```bash
   uv run python manage.py shell < scripts/publicar_corpus_do_piloto.py
   ```

   O 91/2026 publicado com a Retificação de prorrogação basta para o §A.
2. O runserver com o seletor de identidade ligado (`INTERFACE_SELETOR_IDENTIDADE=true`). Escolha uma
   pessoa com o papel **Comunicação** na unidade Cefor, atribuído pela gestão de acessos da `107`.

## §A — Textos (incremento A)

1. Editais → 91/2026 → **Kit de divulgação**.
2. Confira:
   - o término vigente vem da Retificação nº 1;
   - as quatro localidades aparecem com as quantidades;
   - a legenda não tem "abertas" nem "faltam".
3. **Copiar** a legenda: a tela anuncia "Copiado".
4. **Exportar .md**: o arquivo baixa. Em Auditoria, aparece `EXPORTAR_MATERIAL` com a impressão.
5. Publique outra Retificação que mude o término. Reabra o kit: a faixa diz "término das inscrições
   (antes → agora)".
6. Troque para uma pessoa sem o papel. A ação some, e o endereço do kit recusa com a frase canônica.

## §B — Peça (incremento B)

1. A mesma tela mostra a prévia 1080 × 1350, com o texto alternativo ao lado.
2. **Exportar PNG** e **Exportar SVG**: as duas peças são a mesma composição. O SVG embute a fonte e
   não abre script nenhum (`default-src 'none'; style-src 'unsafe-inline'; font-src data:`).
3. 92/2026: a peça conta 18 opções e usa o título do Processo, e a tela diz que o título do Edital não
   coube.

## §C — Pacote e galeria (incremento C)

1. **Exportar ZIP** duas vezes: os dois arquivos têm o mesmo resumo SHA-256.
2. Gere a galeria de revisão:

   ```bash
   uv run python scripts/galeria_do_kit.py --saida /tmp/galeria-kit
   ```

   Ela traz um PNG por cenário de referência e o ZIP de cada um, e é o que vai para a comunicação
   (SC-1054).
