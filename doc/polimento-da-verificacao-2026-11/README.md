# O polimento das telas do candidato na verificação por vídeo — antes e depois

Capturas da spec `174` (FR-7893), em 15/11/2026: a `main` em `499491be` (**antes**) e a branch
`claude/174-polimento-da-verificacao-do-candidato` (**depois**), nas larguras de 375, 768, 1280 e 1920
px. O rosto é sempre a imagem da câmera simulada do Chromium: nenhuma captura tem pessoa real. O nome
da Etapa ("Heteroidentificação") e o da Modalidade ("Pretos e pardos") são os da *fixture* da suíte,
e não texto fixo da tela.

## Como foram feitas

- **Depois**: a própria jornada no navegador da feature, com as capturas ligadas.

  ```bash
  cd backend && NAVEGADOR_CAPTURAS=../doc/polimento-da-verificacao-2026-11/depois \
    PYTEST_ADDOPTS="tests/navegador/test_jornada_do_video.py" make test-pg PYTEST_WORKERS=0
  ```

- **Antes**: [`captura_antes.py`](captura_antes.py), um teste descartável que percorre as telas da
  `166` como eram. Ele vai para `backend/tests/navegador/` de uma worktree da `main` anterior à
  `174`, roda do mesmo jeito, e não entra na suíte.

As imagens foram convertidas para JPEG (qualidade 60) para caber no repositório.

## O que mudou, tela a tela

| Tela | Antes | Depois |
|---|---|---|
| Acompanhamento (`01`) | selo tracejado; o prazo no meio da frase; "Ver como funciona" | selo em pílula com ícone; "Prazo: até …" em linha própria antes do porquê; "Escolher entre vídeo e entrevista ao vivo" |
| Escolha (`02`) | título fixo "Verificação da autodeclaração"; "vaga para pessoas pretas e pardas"; dois botões iguais sem explicação; coluna encostada à esquerda | o nome da Etapa como título e os três momentos; a Modalidade pelo nome publicado; o prazo; dois cartões iguais que dizem o que cada forma é; coluna centrada |
| Antes de gravar (`03`) | seis itens numa lista; "Escolha uma das duas respostas" vermelho em repouso | três itens com ícone, o documento incluído; "Quem vê o seu vídeo" num bloco; a idade em opções grandes; a recusa só depois de "Continuar" |
| Câmera (`04`, antes) | "Abrir a câmera" e depois "Ir para a gravação"; medidor minúsculo | — (fundida ao palco) |
| Palco, preparo (`04`, depois) | — | a câmera abre no "Continuar"; o guia com a explicação; a lista dos passos só pelos títulos; o medidor largo com "Fale alguma coisa…"; "Começar a gravar" à vista |
| Gravação (`05`) | a instrução abaixo do vídeo, o roteiro inteiro repetido embaixo, "Próximo passo" fora do vídeo | "Passo N de 4", o título e a instrução sobre o vídeo, no alto; "Próximo" no polegar; "Gravando" e o tempo; "Parar e recomeçar" no canto oposto; no celular, a tela inteira |
| Revisão (`06`, depois) | duração em "m:ss" e tamanho em MB | "Duração: 1 min 12 s. O envio vai usar cerca de N MB da sua internet." |
| Comprovante (`06` antes, `07` depois) | número do envio e SHA-256 em destaque no topo; "72.3 segundos" | "Seu vídeo foi enviado" com ícone e data no topo; "E agora?"; "Assistir"; os dados para conferência no fim, com "Código de conferência do arquivo (SHA-256)" |

## O que a jornada no navegador mede

A 375×667, 768×1024, 1280×800 e 1920×1080, do acompanhamento ao comprovante, com câmera e microfone
simulados: a coluna centrada (diferença das margens ≤ 1 px, SC-2650); o palco na altura da tela com a
instrução, "Próximo" e "Não consigo usar a câmera" à vista em cada passo, no celular (SC-2651); nenhum
gesto entre "Continuar" e "Começar a gravar" (SC-2652); nenhum elemento `hidden` visível (SC-2653); o
pedido de envio com a versão do roteiro, as quatro marcas em ordem e o formato (SC-2654); a faixa da
instrução com contraste ≥ 4,5:1 sobre um quadro branco (SC-2656); e a confirmação no primeiro quadro do
comprovante (SC-2659). No computador, o avanço é por Espaço, com o foco em "Próximo".

**O achado que só ela pegou**: o vídeo espelhado (`transform: scaleX(-1)`) vai para a camada dos
elementos posicionados, e ficava **por cima** de "Próximo", interceptando o toque. As camadas do palco
ganharam `z-index`.

## O que ainda não foi verificado

- **Aparelhos reais** (FR-7892, SC-2655): um iPhone com Safari e um Android com Chrome, pelo quickstart
  da spec, passo 5. A câmera exige contexto seguro, e o celular que abre `http://<ip>:porta` não a
  consegue pedir (research T-016).
- **Três pessoas de fora da equipe técnica** (SC-2658, Q-4): quickstart, passo 6.
- **Leitor de tela** (T039, T040): ver [acessibilidade.md](acessibilidade.md).
- O pedido de tela acesa só se comprova num aparelho real; o Chromium da suíte não apaga a tela.
