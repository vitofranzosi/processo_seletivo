# Acessibilidade das telas da verificação por vídeo (174, T039 e T040)

Registro de 15/11/2026. O que se conferiu, como, e o que ficou pendente.

## Conferido por teste, no Chromium (`tests/navegador/test_jornada_do_video.py`)

| O quê | Como |
|---|---|
| O foco fica em "Próximo" durante toda a gravação (FR-7869) | `document.activeElement` a cada passo |
| Espaço avança o passo, sem atalho de tecla de letra | a jornada a 768, 1280 e 1920 px grava só com o teclado depois de "Começar a gravar" |
| O anúncio de cada passo: "Passo N de 4: título." (UX-875) | o texto da região `aria-live="assertive"` a cada passo |
| O momento da jornada por `aria-current="step"`, e não só por cor | o atributo no item "Gravar" ao entrar no palco |
| A recusa da idade aparece só depois de "Continuar" e leva o foco à pergunta (FR-7865) | a recusa escondida no carregamento; o foco no `fieldset` depois do clique |
| Nada escondido aparece em repouso (FR-7854) | `display` computado de todo `[hidden]` em cada tela |
| O texto sobre o vídeo tem contraste ≥ 4,5:1 no pior caso (SC-2656) | a cor computada da faixa, composta sobre branco puro |

## Conferido por leitura do template

- A ordem do documento é a do contrato (`specs/174-…/contracts/telas.md`): instrução antes de "Próximo",
  "Não consigo usar a câmera" depois dele.
- Os ícones são `aria-hidden`, e a palavra vem sempre ao lado (UX-873).
- O `fieldset` da idade cita a recusa por `aria-describedby`; cada opção é um `label` com o rádio dentro.
- O palco tem título de segundo nível só para leitor de tela ("Gravação do vídeo"), que recebe o foco ao
  abrir, como as outras telas da página.

## Pendente, e por quê

- **VoiceOver no macOS e no iPhone, NVDA no Windows** (T039, T040): pede uma pessoa ouvindo a tela; não
  há como fazê-lo num teste automático, e esta sessão não o fez. A verificação em aparelho real
  (quickstart da spec, passo 5) é a ocasião de fazê-lo no iPhone.
- **Libras na fala do passo 4**: a tela não muda nada para ela (o avanço é pelo gesto, sem relógio, e o
  texto do roteiro já oferece Libras); a validação com pessoas de fora (SC-2658) pode incluir alguém que
  se comunique em Libras.
