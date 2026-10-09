"""O despacho dos avisos: a quarta situação em que o sistema envia mensagem (`FR-084` da `010`).

**É o único lugar dos avisos que chama o servidor de correio**, e o módulo que
`tests/test_situacoes_de_mensagem.py` declara como a quarta situação. A `FR-084` foi revisada em
2026-10-09 para admiti-la, com as redações anteriores preservadas: o aviso complementar vinculado a
ato oficial, **sem efeito nenhum** sobre prazo, classificação, situação ou direito.
"""

#: A data da revisão da `FR-084` da `010` que admite esta situação, conferida contra a spec por
#: `tests/test_situacoes_de_mensagem.py`. Constante, e não leitura de `specs/` em tempo de execução,
#: pela mesma razão escrita em `convocacao/application/comunicar.py`: o contêiner de produção não
#: carrega a árvore de documentação.
REVISAO_DA_FR_084_PELA_066 = "2026-10-09"
