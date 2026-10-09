"""As telas dos avisos complementares aos candidatos (066, contracts/telas.md).

**Módulo próprio, e não `views.py`**, que já passa de oito mil linhas. O custo da separação está
pago em `tests/test_gramatica_das_portas.py`: o inventário de negativas varre também este módulo,
e todo `raise Http404` daqui precisa de linha em
`specs/033-navegacao-por-capacidade/inventario-das-negativas.md`.
"""
