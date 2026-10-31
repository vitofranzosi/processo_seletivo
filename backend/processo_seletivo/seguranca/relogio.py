"""O instante que a sessão institucional confere contra os prazos (107, `D-009`).

Uma função só, e não `timezone.now()` espalhado: os testes de prazo fixam o relógio aqui, e a
duração máxima e a inatividade se verificam no limite exato, sem `sleep`.
"""

from django.utils import timezone


def agora():
    return timezone.now()
