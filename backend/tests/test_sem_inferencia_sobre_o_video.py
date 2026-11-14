"""Nenhuma inferência automática sobre o vídeo (166, FR-7150; R-19 do estudo).

O sistema não analisa o vídeo de nenhuma forma — nada de detecção de rosto, de tom de pele, de
"qualidade", de miniatura ou de transcrição. A única verificação automática é técnica: contêiner,
tamanho, duração e resumo. **A inferência racial por IA é proibida em qualquer forma**, e o primeiro
passo de qualquer uma delas é uma dependência: este guardião as recusa no projeto inteiro, nas
dependências declaradas, no lock e no código.
"""

import ast
import pathlib
import re

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
