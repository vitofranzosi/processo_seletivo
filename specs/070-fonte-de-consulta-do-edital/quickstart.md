# Quickstart — validar a 070

Roteiro para provar a feature de ponta a ponta. Há duas partes:

- **A. Automática**: a suíte, com a matriz da auditoria.
- **B. Pelo canal do ator**: o setor de seleção, na gestão. É o `SC-538` e o princípio VI.

Os detalhes das respostas estão em [contracts/resposta.md](contracts/resposta.md); os da tela, em
[contracts/tela.md](contracts/tela.md).

## Pré-requisitos

- **PostgreSQL local** e o `.env` da worktree com `POSTGRES_USER` ajustado (`CLAUDE.md`, "Subir o
  ambiente").
- **Ambiente da worktree:** `cd backend && uv sync --extra dev`, uma vez.
- **Um banco próprio desta worktree**, para não disputar `test_processo_seletivo` com outra sessão.

## A. Automática

1. **Casos de domínio**, sem banco, sobre o corpus copiado (`R-016`). São os `CA-*` de conteúdo, a
   cobertura (`R-015`), o literal (`SC-534`) e o guardião de importação (`R-009`):

   ```bash
   cd backend && uv run pytest tests/unit/duvidas -q
   ```

   **Esperado:** todos passam. O guardião de cobertura nomeia qualquer campo não classificado.

2. **Integração** pelo fluxo real, contra PostgreSQL:
   - versão no instante, antes e depois da fronteira (`CA-17`, `CA-19`);
   - mudança de versão (`CA-18`);
   - Retificação não publicada ignorada (`SC-532`);
   - origem de cada valor e os dois cenários do achado (`SC-535`);
   - desfecho (`CA-29`);
   - orçamento de consultas (`R-019`).

   ```bash
   cd backend && TEST_DB_ENGINE=postgresql DB_RUNTIME_USER="$USER" DB_USER="$USER" DB_NAME=ps_070 uv run pytest tests/integration/duvidas tests/interface/test_duvidas.py -q
   ```

   **Esperado:** todos passam. O alvo `make test-pg` roda a suíte inteira e não aceita um
   subconjunto. Por isso o par de variáveis vai à mão. `$USER` é o superusuário do PostgreSQL desta
   máquina (Homebrew); troque se for outro. Sem `TEST_DB_ENGINE` **e** o usuário, a suíte cai para
   SQLite sem avisar (`CLAUDE.md`).

3. **Os guardiões que a tela aciona** (`R-018`):

   ```bash
   cd backend && uv run pytest tests/test_gramatica_das_portas.py tests/test_citacoes_de_requisito.py tests/interface/test_acessibilidade.py tests/interface/test_estaticos.py -q
   ```

4. **A verificação completa do projeto**, antes do PR:

   ```bash
   cd backend && make lint check test-pg DB_NAME=ps_070
   ```

## B. Pelo canal do ator (`SC-538`)

**Preparação.** O `seed_demo` publica o Edital 01/2026 com as duas Retificações do corpus, a segunda
com vigência futura de 15 dias. Use um banco próprio, criado antes; no macOS com PostgreSQL do
Homebrew, com `LC_ALL` exportado:

```bash
LC_ALL=en_US.UTF-8 createdb ps_070_demo
```

```bash
cd backend && make preparar DB_NAME=ps_070_demo
```

```bash
cd backend && make seed DB_NAME=ps_070_demo
```

```bash
cd backend && make runserver DB_NAME=ps_070_demo INTERFACE_SELETOR_IDENTIDADE=true
```

Pelo `make`, as duas são variáveis do Make, e não prefixo de ambiente. O `Makefile` carrega o
`.env` e exporta tudo; um `manage.py` chamado à mão não enxergaria o `.env` (`CLAUDE.md`).

**Roteiro.**

1. **Entrar na conferência.** Em `/gestao/`, identifique-se como gestor da unidade `cefor`, abra o
   Edital 01/2026 e siga "Ver as respostas do assistente de dúvidas (validação interna)".
2. **Conferir o canal.** Os pontos para revisão mostram a Retificação de vigência futura. Não mostram
   canal divergente: o 01/2026 não tem seções, e o canal é o institucional.
3. **`P-01` agora.**
   - A resposta diz o término vigente e avisa que a Retificação publicada prorroga a partir da data
     de vigência.
   - O cartão do Evento traz a descrição literal, com "isenção de taxa até o 5º dia".
   - O cartão do término leva ao documento da **publicação original**.
4. **`P-01` depois da fronteira.** Repita com `em` igual à data de vigência da segunda Retificação
   mais um dia, informando a versão da resposta anterior.
   - A resposta começa pelo aviso de mudança.
   - Ela diz o novo término.
   - O cartão leva ao documento **da Retificação** que o fixou.
5. **`P-03` para o Perfil de docência.** 3 vagas imediatas: 2 de ampla concorrência e 1 PPP. A ampla
   concorrência e o total levam ao documento da primeira Retificação; a linha PPP, ao da original.
6. **`P-08` para o Perfil técnico.** O tipo é "O Edital não informa", e a explicação não diz que não
   cabe recurso.
7. **Seguir os links.** Cada "Abrir o documento deste ato" abre o PDF do ato. Nenhum link se chama
   "Edital completo".
8. **Teclado e celular.** Repita os passos 3 e 4 só com teclado. A 375 px de largura, a página não
   rola na horizontal.

**Os Editais 91 e 92/2026** cobrem o canal com exclusividade, o recurso em três fontes e o anexo da
prova de títulos. Eles são publicados pelo ajudante de testes do `R-016`. Para olhá-los no navegador,
use o mesmo ajudante num shell sobre uma cópia do banco de demonstração, como a memória do projeto
registra para Editais de demonstração.

## Resultado esperado, em uma linha

Toda resposta diz a versão, o tipo e a origem de cada informação. Nenhum link chama documento de
"Edital completo". Nenhuma chamada a serviço externo.
