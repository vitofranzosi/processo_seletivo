# Quickstart: A habilitação do assistente do Edital

Como provar a feature. Os roteiros A e B são automáticos; o C é a demonstração humana (SC-2457); o
D é o passo de implantação.

## A — A suíte

```bash
cd backend && make lint check test-pg
```

- O percurso inteiro, com a porta falsa da suíte (SC-2451), está em
  `tests/navegador/test_jornada_do_assistente.py`. Ele pede o grupo `navegador`. Para assistir, use
  `make test-navegador`.
- As recusas de produção (SC-2453) estão em `tests/test_configuracao_producao.py` e em
  `tests/portal/test_assistente_habilitado.py`, com `AMBIENTE_DE_PRODUCAO=True`.
- As suítes da `071` e da `074` têm de passar sem mudança (SC-2455).

## B — A configuração de produção recusa

Com as configurações de produção, a inicialização é recusada em três casos, cada um com a variável
nomeada na mensagem:

- `ASSISTENTE_PILOTO=true`;
- `ASSISTENTE_SERVICO=openrouter`, com o piloto desligado;
- `ASSISTENTE_TEMPO_LIMITE_SEGUNDOS=115`, com o serviço `ollama`.

Os casos estão em `tests/test_configuracao_producao.py`. O pré-voo do guia de implantação mostra o
mesmo.

## C — A demonstração, com o serviço real

É o ambiente de homologação funcional da `110`:

- as configurações de desenvolvimento;
- o seletor de identidade desligado;
- o provedor de homologação;
- **nenhuma chave de demonstração do assistente**.

Para o serviço, siga o roteiro de troca do assistente (`doc/troca-do-servico-do-assistente.md`). A
credencial vem de um arquivo fora do repositório, e o tokenizer em `ASSISTENTE_TOKENIZER`.

1. Entre como o Administrador institucional cadastrado no ambiente (roteiro G da `110`). Abra
   "Assistente do Edital" e confira "configuração completa", e que a credencial aparece só como
   presente.
2. Habilite o piloto e o Edital A, cada um com motivo.
3. Entre como alguém com o papel Participante do piloto e faça uma pergunta no A pela gestão.
4. Numa janela anônima, sem login, abra a página da seleção do A, abra o painel e pergunte. Abra a
   página do B e confira que não há painel.
5. Como administrador, desabilite o A. Na janela anônima, pergunte de novo: aparece o aviso de
   encerrado, e o painel do provedor não registra a chamada.
6. Habilite o A de novo e pergunte: a conversa é nova.

Registre uma captura de cada passo. Pelo `.claude/launch.json`, a entrada da demonstração é uma
linha nova. Não sobrescreva o arquivo, porque ele é versionado.

## D — Antes do deploy em cada ambiente instalado

É o passo 0 da migração da `110`. Liste os vínculos vigentes do `administrador-institucional`. Se
houver algum, o usuário autoriza expressamente que essas pessoas passem a habilitar o assistente, ou
a implantação retira o papel antes do deploy (FR-7510). Depois, rode `ps-migrar` e confira a linha
de provisionamento: o `M` vai a 66, e o `N` não é zero.
