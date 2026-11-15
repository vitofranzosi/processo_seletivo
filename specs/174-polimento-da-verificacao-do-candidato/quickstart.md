# Quickstart: validar o polimento das telas do candidato

Roteiro de verificação da `174`. A forma de cada tela está em [contracts/telas.md](contracts/telas.md);
as decisões técnicas, em [research.md](research.md).

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado e um `DB_NAME` próprio (*As armadilhas caras*, no
  `CLAUDE.md`). Nenhuma migration nova: o `M` da preparação é o mesmo de antes.
- `uv sync --extra dev --extra navegador` e `uv run playwright install chromium`, para a jornada no
  navegador.
- O #564 mergeado, ou os tokens da `172` presentes em `shared/static/shared/tokens.css` (T-009).

## 1. A prova de que nada mudou no envio

```bash
cd backend && DB_NAME=ps_174 make test-pg PYTEST_ADDOPTS="tests/integration/verificacao tests/unit/verificacao tests/contract"
```

Esperado: tudo passa **sem nenhum arquivo destes diretórios alterado** pela feature (FR-7887,
SC-2654). Depois, `node --test tests/javascript/gravacao.test.js`: os testes de hoje passam sem
mudança, e os novos também.

## 2. As telas e o acompanhamento

```bash
cd backend && DB_NAME=ps_174 make test-pg PYTEST_ADDOPTS="tests/portal tests/unit/portal tests/interface/test_folha_estatica.py tests/interface/test_larguras.py"
```

Esperado: as páginas renderizadas trazem as frases do contrato; a política de conteúdo da página de
gravação é a de hoje, diretiva a diretiva (SC-2657); nenhum template tem `style=` nem `<script>` sem
`src`; toda classe nova tem regra na folha.

## 3. A jornada no navegador, com câmera simulada

```bash
cd backend && DB_NAME=ps_174 make test-pg PYTEST_ADDOPTS="tests/navegador/test_jornada_do_video.py"
```

A jornada percorre, a 375×667 e a 1280×800, do acompanhamento ao comprovante, com a câmera e o
microfone simulados do Chromium (T-015). Esperado:

| Medida | Critério |
|---|---|
| margens da coluna a 1280 px | diferença ≤ 1 px (SC-2650) |
| palco a 375×667, em cada passo | altura = janela, sem rolagem; instrução, "Próximo" e "Não consigo usar a câmera" visíveis (SC-2651) |
| gestos entre "Continuar" e "Começar a gravar" | zero (SC-2652) |
| elementos `hidden` no carregamento de cada tela | todos com `display: none` (SC-2653) |
| corpo do início do envio | a versão do roteiro, quatro marcas em ordem, o formato (SC-2654) |
| faixa da instrução | contraste calculado ≥ 4,5:1 sobre branco e sobre preto (SC-2656) |
| comprovante a 375 px | confirmação e data no primeiro quadro; dados abaixo de "E agora?" (SC-2659) |

Para assistir: `make test-navegador` com o mesmo `PYTEST_ADDOPTS`.

## 4. As capturas antes e depois (FR-7893)

O script em `doc/polimento-da-verificacao-2026-11/` sobe a `main` e a branch em duas portas e captura,
com a câmera simulada, cada tela da página da gravação, o comprovante, a situação sem gravação e o
acompanhamento com passo, a 375, 768, 1280 e 1920 px. A saída é uma pasta por largura e um `README.md`
com a comparação. O rosto é sempre a imagem simulada; nenhuma captura tem pessoa real.

## 5. Os aparelhos reais (FR-7892, SC-2655)

A câmera só abre em contexto seguro (T-016). Suba o servidor da worktree na porta 8174, com
`VERIFICACAO_POR_VIDEO=true`, `INTERFACE_SELETOR_IDENTIDADE=true` e o cenário C18 carregado
(`CENARIOS_DE_TREINAMENTO=true`, `carregar_cenario_de_treinamento C18 --banco <DB_NAME>`).

**Android, pelo cabo.** Ligue a depuração USB, conecte e rode:

```bash
adb reverse tcp:8174 tcp:8174
```

No Chrome do celular, abra `http://localhost:8174` — contexto seguro, sem nada sair da máquina.

**iPhone, por certificado local.** Gere um certificado com `mkcert` para o nome da máquina na rede,
instale e confie a autoridade no iPhone (Ajustes › Geral › Sobre › Ajustes de Confiança de
Certificados), e ponha um proxy TLS na frente do `runserver` (por exemplo, `caddy reverse-proxy`). Só
neste ambiente, acrescente o nome a `ALLOWED_HOSTS` e a `https://<nome>` a `CSRF_TRUSTED_ORIGINS`.

Em cada aparelho, do acompanhamento ao comprovante:

1. o acompanhamento mostra o selo com ícone, o prazo em linha própria e "Escolher entre vídeo e
   entrevista ao vivo";
2. "Continuar" pede a câmera e o microfone, e o palco aparece sem outro toque;
3. o palco ocupa a tela, em retrato, com a instrução no alto e "Próximo" ao alcance do polegar;
4. com o celular parado por três minutos no palco, a tela não apaga;
5. a pessoa grava tocando só em "Começar a gravar", três vezes em "Próximo" e uma em "Terminar a
   gravação";
6. bloquear a tela no meio da gravação descarta a tomada, com a explicação (a FR-7115 da `166`);
7. o comprovante abre pela confirmação, e o vídeo enviado toca, não espelhado, com o documento legível.

Registre o modelo, o sistema e o navegador de cada aparelho no `README.md` das capturas.

## 6. Três pessoas de fora da equipe técnica (SC-2658, Q-4)

Com o mesmo ambiente do passo 5, peça a cada pessoa, no próprio celular: *"Você se inscreveu numa
seleção e precisa fazer este passo. Faça como faria em casa."* Não ajude nem explique. Anote se ela
chegou ao comprovante, onde hesitou e, depois, como descreveria a tela. Os vídeos são de teste: apague
o banco e a pasta de arquivos do ambiente ao terminar, e não guarde nenhuma captura com o rosto delas.

## 7. A suíte inteira

`make lint check test-pg`, sozinha no cluster, uma vez, no fim.
