"""A detecção do giro do rosto na gravação do vídeo (176), do lado do servidor.

**O servidor não detecta nada.** Quem estima para onde o rosto aponta é o aparelho da pessoa, no
palco da página de gravação, e nada dessa leitura volta para cá (FR-8000, FR-8031). Este módulo só
diz **se** a página oferece a detecção e **de onde** o navegador baixa o motor.

**Por que a regra da análise foi revista, e até onde** (D-001 da `176`, Q-1 decidida pelo usuário em
15/11). A FR-7150 da `166` e a R-19 do estudo proibiam detecção de rosto "no projeto", porque a
garantia é que nenhuma máquina participe do juízo sobre a aparência da pessoa. Uma estimativa do
giro que nasce e morre na memória do aparelho, só para passar ao passo seguinte, não participa do
juízo: a comissão nem sabe que ela existiu. O servidor continua sem analisar nada — o guardião
`tests/test_sem_inferencia_sobre_o_video.py` recusa visão computacional no lock e no código
Python —, e no navegador ele admite **um** motor, este, na versão e nos resumos abaixo, e só na
gravação.

**Duas chaves** (D-004): a do vídeo e a própria. A detecção tem pendência própria — a validação
com a CPVA e o encarregado de dados, a P-13 — e exige uma exceção própria da política de conteúdo
(`'wasm-unsafe-eval'`), que não deve valer só porque o vídeo vale.
"""

from django.conf import settings

from processo_seletivo.shared.estaticos import estatico

# `@mediapipe/tasks-vision` 1.2.0 (27/10/2026, Apache 2.0), e não a 1.2.3 de 11/11: dependência nova
# entra com pelo menos duas semanas de publicada (research T-001). Os arquivos são os do pacote, sem
# alteração — o resumo de cada um é o do pacote publicado, e o teste o confere. Tirar a linha do
# mapa de fonte do módulo, que aponta para um arquivo que não veio, mudaria o resumo: o navegador só
# o pede com as ferramentas de desenvolvimento abertas.
VERSAO_DO_MOTOR = "1.2.0"
PASTA = "portal/deteccao"
MOTOR = f"{PASTA}/tasks-vision-{VERSAO_DO_MOTOR}/vision_bundle.mjs"
CARREGADOR = f"{PASTA}/tasks-vision-{VERSAO_DO_MOTOR}/vision_wasm_internal.js"
BINARIO = f"{PASTA}/tasks-vision-{VERSAO_DO_MOTOR}/vision_wasm_internal.wasm"
# Os pontos do rosto, float16, versão 1 (Q-4, D-006). O pacote do modelo traz também o das
# expressões (`face_blendshapes`), que a página **não liga**: a detecção lê só a direção do rosto
# (FR-8001).
MODELO = f"{PASTA}/face_landmarker-float16-1.task"
LICENCA = f"{PASTA}/LICENSE-2.0.txt"

ARQUIVOS = {
    MOTOR: "870da5cfc43bfcf2a8b0f14e8152dae8c7e701722e1191b0e592b94b81b4127a",
    CARREGADOR: "85c1a342be70427987f900969a5f26e17557351111364e6585e97fb03e93e108",
    BINARIO: "bcc13df22d3d69ec8cbe8e280989356d844ae00f4523eb82072d2484f44134dc",
    MODELO: "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff",
    LICENCA: "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}

# Os passos que avançam sozinhos, e para que lado (D-002): só os dois perfis. O documento e o passo
# de frente continuam pelo toque. O lado é o **da pessoa** (D-005), e quem o lê é o `deteccao.js`.
GIRO_DO_PASSO = {"perfil-esquerdo": "esquerda", "perfil-direito": "direita"}


def ligada() -> bool:
    """A página oferece a detecção: as duas chaves ligadas (FR-8020)."""
    return bool(
        getattr(settings, "VERIFICACAO_POR_VIDEO", False)
        and getattr(settings, "VERIFICACAO_DETECCAO_DO_GIRO", False)
    )


def enderecos() -> dict:
    """Os endereços do motor, com a versão do conteúdo no `?v=` (089): o `nginx` só guarda em cache
    o que vem versionado, e o navegador baixa uma vez por versão (FR-8016)."""
    return {
        "motor": estatico(MOTOR),
        "carregador": estatico(CARREGADOR),
        "binario": estatico(BINARIO),
        "modelo": estatico(MODELO),
    }
