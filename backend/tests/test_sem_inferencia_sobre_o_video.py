"""Nenhuma inferência automática sobre o vídeo (166, FR-7150; R-19 do estudo).

O sistema não analisa o vídeo de nenhuma forma — nada de detecção de rosto, de tom de pele, de
"qualidade", de miniatura ou de transcrição. A única verificação automática é técnica: contêiner,
tamanho, duração e resumo. **A inferência racial por IA é proibida em qualquer forma**, e o primeiro
passo de qualquer uma delas é uma dependência: este guardião as recusa no projeto inteiro, nas
dependências declaradas, no lock e no código.

**A exceção do aparelho** (176, D-001, FR-8024; Q-1 decidida pelo usuário em 15/11). O palco da
gravação pode estimar, no aparelho da pessoa, para onde o rosto aponta, só para passar sozinho aos
perfis; nada dessa leitura sai do navegador. A garantia do servidor não muda, e no navegador ela
passa a admitir **um** motor: o do manifesto de `portal/deteccao.py`, nos resumos dele, servido só
pela página da gravação. Os três últimos casos abaixo cobram isso.
"""

import ast
import hashlib
import pathlib
import re

from processo_seletivo.portal import deteccao

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# Visão computacional, reconhecimento facial, decodificação de mídia e transcrição. O nome é o do
# pacote no índice, normalizado; o módulo é o que o código importaria.
PROIBIDOS = {
    "opencv-python": "cv2",
    "opencv-python-headless": "cv2",
    "opencv-contrib-python": "cv2",
    "mediapipe": "mediapipe",
    "face-recognition": "face_recognition",
    "dlib": "dlib",
    "deepface": "deepface",
    "insightface": "insightface",
    "retina-face": "retinaface",
    "mtcnn": "mtcnn",
    "facenet-pytorch": "facenet_pytorch",
    "torchvision": "torchvision",
    "scikit-image": "skimage",
    "imageio-ffmpeg": "imageio_ffmpeg",
    "ffmpeg-python": "ffmpeg",
    "av": "av",
    "moviepy": "moviepy",
    "pymediainfo": "pymediainfo",
    "openai-whisper": "whisper",
    "faster-whisper": "faster_whisper",
    "speechrecognition": "speech_recognition",
    "vosk": "vosk",
}


def _normalizar(nome):
    return re.sub(r"[-_.]+", "-", nome).lower()


def test_nenhuma_dependencia_de_analise_de_imagem_ou_som_no_lock():
    lock = (RAIZ / "uv.lock").read_text(encoding="utf-8")
    pacotes = {_normalizar(nome) for nome in re.findall(r'^name = "([^"]+)"', lock, re.M)}
    assert not pacotes & set(PROIBIDOS), sorted(pacotes & set(PROIBIDOS))


def test_nenhuma_dependencia_de_analise_declarada():
    declarado = (RAIZ / "pyproject.toml").read_text(encoding="utf-8").lower()
    achados = [
        nome for nome in PROIBIDOS if re.search(rf'["\s]{re.escape(nome)}\s*[<>=~!;"\[]', declarado)
    ]
    assert not achados, achados


def test_nenhum_import_de_analise_no_codigo():
    modulos = set(PROIBIDOS.values())
    achados = []
    for arquivo in sorted((RAIZ / "processo_seletivo").rglob("*.py")):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                nomes = [alias.name for alias in no.names]
            elif isinstance(no, ast.ImportFrom) and no.module:
                nomes = [no.module]
            else:
                continue
            for nome in nomes:
                if nome.split(".")[0] in modulos:
                    achados.append(f"{arquivo.relative_to(RAIZ)}: {nome}")
    assert not achados, achados


# --- a exceção do aparelho (176) --------------------------------------------------------------

ESTATICOS = RAIZ / "processo_seletivo"
PASTA_DO_MOTOR = ESTATICOS / "portal" / "static" / deteccao.PASTA
# O que denuncia um motor de visão no navegador: o nome do pacote, a classe do motor e o binário.
MARCAS_DE_MOTOR = ("tasks-vision", "FaceLandmarker", "mediapipe", "vision_wasm")


def _resumo(arquivo):
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


def test_o_motor_do_aparelho_e_so_o_do_manifesto():
    """FR-8023, FR-8024: nenhum arquivo a mais na pasta do motor, e cada um com o resumo registrado.
    Trocar de versão é trocar o manifesto, num PR que o revisor vê."""
    presentes = {
        f"portal/{arquivo.relative_to(PASTA_DO_MOTOR.parent).as_posix()}": _resumo(arquivo)
        for arquivo in sorted(PASTA_DO_MOTOR.rglob("*"))
        if arquivo.is_file()
    }
    assert presentes == deteccao.ARQUIVOS


def test_nenhum_outro_estatico_traz_motor_de_visao():
    """FR-8024: fora da pasta do motor, só `deteccao.js` o nomeia — é quem o carrega."""
    achados = []
    for arquivo in sorted(ESTATICOS.glob("*/static/**/*")):
        if not arquivo.is_file() or PASTA_DO_MOTOR in arquivo.parents:
            continue
        if arquivo.name == "deteccao.js" or arquivo.suffix in {".png", ".jpg", ".svg", ".woff2"}:
            continue
        texto = arquivo.read_text(encoding="utf-8", errors="ignore")
        achados += [f"{arquivo.relative_to(RAIZ)}: {m}" for m in MARCAS_DE_MOTOR if m in texto]
    assert not achados, achados


def test_so_a_pagina_da_gravacao_carrega_a_deteccao():
    """FR-8003, FR-8024: nem a revisão, nem o comprovante, nem a Mesa leem o rosto."""
    citam = sorted(
        modelo.relative_to(ESTATICOS).as_posix()
        for modelo in ESTATICOS.glob("*/templates/**/*.html")
        if "deteccao.js" in modelo.read_text(encoding="utf-8")
        or any(m in modelo.read_text(encoding="utf-8") for m in MARCAS_DE_MOTOR)
    )
    assert citam == ["portal/templates/portal/verificacao.html"]
