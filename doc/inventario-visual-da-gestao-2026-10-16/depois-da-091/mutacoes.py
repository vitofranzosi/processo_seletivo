"""Prova por mutação dos guardiões repontados e dos novos (091, FR-2110, SC-813).

    mutacoes.py            (de backend/, com o ambiente da suíte contra PostgreSQL)

Para cada linha: planta no arquivo a violação que o guardião existe para pegar, roda o teste dele e
exige que **reprove**; desfaz e segue. No fim, roda os mesmos testes sem mutação e exige que passem.

As da 089 (1 a 23) plantavam no `gestao.css`, que a 091 dividiu: aqui, `COMUM` é "o arquivo da folha
comum que tem o trecho" — achado entre os sete —, e o que se acrescentava no fim do `gestao.css` vai
para o fim do último deles, `telas.css`, que é onde a soma termina. As de 24 em diante são dos
guardiões que a 091 repontou para os arquivos de tela, e dos que ela criou.
"""

import subprocess
import sys
from pathlib import Path

ESTATICOS = Path("processo_seletivo/interface/static/interface")
AREAS = ["base", "moldura", "impressao", "componentes", "formularios", "tabelas", "telas"]
FOLHA_COMUM = [ESTATICOS / "gestao" / f"{area}.css" for area in AREAS]
COMUM = "folha comum"
TOKENS = Path("processo_seletivo/shared/static/shared/tokens.css")
TELAS = ESTATICOS / "telas"
GRUPOS = ESTATICOS / "grupos"
MODELOS = Path("processo_seletivo/interface/templates/interface")
PORTAL = Path("processo_seletivo/portal/templates/portal")
POLITICA = Path("processo_seletivo/shared/politica_de_conteudo.py")

T_ACESS = "tests/interface/test_acessibilidade.py"
T_POL = "tests/interface/test_politica_de_conteudo.py"
T_FOLHA = "tests/interface/test_folha_estatica.py"

# (nº, arquivo, trecho de antes ou None para acrescentar no fim, trecho de depois, testes)
MUTACOES = [
    # ---- as da 089, repontadas ----
    (1, COMUM, "\n.marca-irreversivel{", "\n.zzmut.marca-irreversivel{",
     f"{T_ACESS}::test_nenhum_modificador_fica_sem_a_base_que_o_usa"),
    (1, COMUM, "\n.oculto{", "\n.ocultx{",
     f"{T_ACESS}::test_nenhuma_classe_citada_deixa_de_existir_na_folha"),
    (1, TOKENS, "--texto:#1c1c1c;", "--texto:#bbbbbb;", f"{T_ACESS}::test_contraste_atende_wcag_aa"),
    (1, COMUM, ".distribuicao-moldura{overflow-x:visible}", ".distribuicao-moldura{overflow-x:auto}",
     f"{T_ACESS}::test_o_cabecalho_da_matriz_nao_e_fixado_dentro_de_um_contentor_de_rolagem"),
    # As regras das terminais moram em `grupos/terminais.css` desde a 091 (eram do parcial).
    (2, COMUM, None, ".terminais .botao{color:red}\n",
     "tests/interface/test_polish_da_057.py::test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas"),
    (2, COMUM, None, ".requisitos-apresentados{color:red}\n",
     "tests/interface/test_polish_da_057.py::test_os_documentos_da_inscricao_seguem_a_mesa"),
    (3, COMUM, None, ".colunas.ao-topo{color:red}\n",
     "tests/interface/test_polish_da_058.py::test_as_terminais_moram_num_parcial_das_duas_telas"),
    (4, COMUM, None, ".imutavel code{overflow-wrap:anywhere}\n",
     "tests/interface/test_telas_de_uso_diario.py::test_cada_correcao_vale_so_na_sua_tela"),
    (5, COMUM, None, "main .zzmut{max-width:600px}\n",
     "tests/interface/test_larguras.py::test_nenhuma_das_bases_crava_largura_em_pixel"),
    (6, COMUM, None, ".so-admite{display:none}\n",
     "tests/interface/test_campos_que_a_escolha_governa.py::test_a_folha_nunca_esconde_por_padrao"),
    (7, COMUM, ".assistente .estado{font-size:.75rem;", ".assistente .estado{text-transform:uppercase;font-size:.75rem;",
     "tests/interface/test_polish_da_056.py::test_a_situacao_da_etapa_continua_em_texto"),
    (8, COMUM, None, ".acoes .marca-irreversivel{align-self:center}\n",
     "tests/interface/test_achados_das_revisoes.py::test_a_marca_nao_estica_em_linha_flexivel"),
    (9, COMUM, None, ".distribuicao thead th .codigo{display:block}\n", "tests/interface/test_alocacoes.py"),
    (10, COMUM, ".acao.desabilitado{color:var(--texto-fraco);", ".acao.desabilitado{color:var(--verde);",
     "tests/interface/test_lista.py"),
    (11, COMUM, ".s-PRESIDENTE{", ".s-PRESIDENTX{", "tests/interface/test_comissao.py"),
    (13, COMUM, None, "{% comment %}\n",
     "tests/interface/test_estaticos.py::test_nenhuma_sintaxe_de_template_nas_folhas_estaticas"),
    (14, TOKENS, " --pagina:96rem;", "",
     "tests/portal/test_resultado_publico.py::test_a_pagina_nao_tem_largura_fixa_que_force_rolagem_horizontal"),
    (14, TOKENS, " --pagina:96rem;", "",
     "tests/interface/test_larguras.py::test_as_duas_larguras_vivem_nos_tokens"),
    (15, COMUM, "th,td{text-align:left;padding:.5rem .75rem;", "th,td{text-align:left;padding:.4rem .75rem;",
     "tests/interface/test_polish_da_055.py::test_a_celula_tem_o_preenchimento_do_portal"),
    (16, TOKENS, "--leitura:68ch;", "--leitura:70ch;", "tests/interface/test_medida_dos_campos.py"),
    (17, COMUM, "background:linear-gradient(to right,var(--branco) calc(4.25rem - 1px)",
     "background:linear-gradient(to left,var(--branco) calc(4.25rem - 1px)",
     "tests/interface/test_shell_da_gestao.py::test_a_folha_recolhe_so_na_tela_larga_e_sem_movimento_forcado"),
    (18, COMUM, None, ".zzmoldura{overflow-x:auto}\n",
     "tests/interface/test_telas_de_quem_elabora.py::test_toda_moldura_que_rola_e_referencia_do_que_carrega"),
    (19, COMUM, ".tabela-rolavel{overflow-x:auto}", ".tabela-rolavel{overflow-x:scroll}",
     "tests/interface/test_acessibilidade_da_classificacao.py::test_o_conteiner_limita_a_rolagem_horizontal"),
    (20, COMUM, ".tabela-rolavel,.rolagem,.rolagem-da-tabela,.serie .barras{position:relative}",
     ".rolagem,.rolagem-da-tabela,.serie .barras{position:relative}", "tests/interface/test_visao_dos_perfis.py"),
    (21, COMUM, ".tabela-rolavel,.rolagem,.rolagem-da-tabela,.serie .barras{position:relative}",
     ".rolagem,.rolagem-da-tabela,.serie .barras{position:relative}", "tests/interface/test_visao_da_classificacao.py"),
    (22, COMUM, ".tabela-rolavel{overflow-x:auto}", ".tabela-rolavel{overflow-x:scroll}",
     "tests/integration/interface/test_inscricoes_recebidas.py::test_a_tabela_larga_rola_dentro_de_si_mesma"),
    (23, COMUM, ".barra-lateral,.cabecalho-de-contexto>a{display:none}", ".barra-lateral,.cabecalho-de-contexto{display:none}",
     "tests/interface/test_decisoes_da_etapa_4.py::test_no_papel_sai_o_cabecalho_sem_trocar_identidade_e_sem_a_barra"),
    (23, COMUM, ".cabecalho-de-contexto{display:block;min-height:0;", ".cabecalho-de-contexto{display:block;white-space:nowrap;min-height:0;",
     "tests/interface/test_decisoes_da_etapa_4.py::test_no_papel_a_trilha_quebra_a_linha"),
    # ---- o estilo das telas, lido dos arquivos (estilo_do_bloco) ----
    # Uma classe que só esta regra define: `.filtros-da-visao`, a primeira tentativa, tem outras
    # regras no mesmo arquivo, e renomear uma delas não a tirava da folha — mutação fraca, e não
    # guardião fraco.
    (24, TELAS / "visao-geral.css", ".o-que-nao-medimos .limite-permanente{", ".o-que-nao-medimos .limite-permanentx{",
     f"{T_ACESS}::test_nenhuma_classe_citada_deixa_de_existir_na_folha"),
    (24, GRUPOS / "aviso.css", ".texto-do-aviso{", ".texto-do-avisx{",
     f"{T_ACESS}::test_nenhuma_classe_citada_deixa_de_existir_na_folha"),
    (25, TELAS / "comissao.css", "#identity_subject{max-width:20rem}", "#identity_subject{max-width:22rem}",
     "tests/interface/test_polish_da_055.py::test_os_campos_da_comissao_tem_largura_pelo_conteudo"),
    (26, TELAS / "compor-conteudo.css", "fieldset.secao.gerada{border:0;", "fieldset.secao.gerada{border:1px;",
     "tests/interface/test_polish_da_056.py::test_a_secao_gerada_nao_tem_caixa_e_o_caminho_fica_na_frase"),
    (26, TELAS / "compor-cronograma.css", ".campo.local{flex:0 1 20rem}", ".campo.local{flex:0 1 21rem}",
     "tests/interface/test_polish_da_056.py::test_a_faixa_do_evento_poe_as_datas_juntas_e_o_local_no_fim"),
    (26, TELAS / "compor-anexos.css", "#anexos-lista>.vazio{max-width:none}", "#anexos-lista>.vazio{max-width:10rem}",
     "tests/interface/test_polish_da_056.py::test_a_navegacao_da_etapa_nao_herda_a_medida_de_leitura"),
    (26, TELAS / "compor-revisao.css", "grid-template-columns:min(16rem,40%) 1fr", "grid-template-columns:min(18rem,40%) 1fr",
     "tests/interface/test_polish_da_058.py::test_a_coluna_de_rotulos_da_revisao_tem_uma_largura_so"),
    (27, TELAS / "marco.css", ".gestos{display:flex;flex-wrap:wrap", ".gestos{display:flex",
     "tests/interface/test_polish_da_057.py::test_a_conducao_destaca_so_o_primeiro_gesto"),
    (28, GRUPOS / "terminais.css", "flex-direction:row", "flex-direction:column",
     "tests/interface/test_polish_da_058.py::test_as_terminais_moram_num_parcial_das_duas_telas"),
    (29, TELAS / "sorteio.css", ".imutavel code{overflow-wrap:anywhere}", ".imutavel code{overflow-wrap:normal}",
     "tests/interface/test_telas_de_uso_diario.py::test_cada_correcao_vale_so_na_sua_tela"),
    (30, TELAS / "visao-geral.css", None, ".zzmut{max-width:600px}\n",
     "tests/interface/test_larguras.py::test_o_estilo_de_pagina_tambem_nao_crava_largura_em_pixel"),
    (31, TELAS / "retificar.css", None, ".zzmoldura{overflow-x:auto}\n",
     "tests/interface/test_telas_de_quem_elabora.py::test_toda_moldura_que_rola_e_referencia_do_que_carrega"),
    (32, TELAS / "lista.css", None, "{% comment %}\n",
     "tests/interface/test_estaticos.py::test_nenhuma_sintaxe_de_template_nas_folhas_estaticas"),
    (32, GRUPOS / "serie.css", ".altura-3{height:3%;}", ".altura-3{height:3%}",
     "tests/interface/test_estaticos.py::test_nenhuma_sintaxe_de_template_nas_folhas_estaticas"),
    (33, MODELOS / "lista.html", "{% estatico 'interface/telas/lista.css' %}\">",
     "{% estatico 'interface/telas/lista.css' %}\"><link rel=\"stylesheet\" href=\"{% estatico 'interface/telas/visao-geral.css' %}\">",
     f"{T_FOLHA}::test_cada_folha_de_tela_e_carregada_so_por_quem_a_usa"),
    (33, MODELOS / "aviso.html", "<link rel=\"stylesheet\" href=\"{% estatico 'interface/grupos/aviso.css' %}\">", "",
     f"{T_FOLHA}::test_cada_folha_de_tela_e_carregada_so_por_quem_a_usa"),
    (34, MODELOS / "minhas_etapas.html", "largura-{{ item.carga.percentual }}", "largura-{{ item.carga.concluidas }}",
     "tests/interface/test_completude_das_etapas.py"),
    (34, TELAS / "minhas-etapas.css", ".largura-37{width:37%;}", "",
     f"{T_POL}::test_uma_classe_por_valor_de_zero_a_cem"),
    # ---- a política e o que ela recusaria ----
    (35, MODELOS / "lista.html", "<h1>Processos Seletivos</h1>", "<h1 style=\"color:red\">Processos Seletivos</h1>",
     f"{T_POL}::test_nenhum_modelo_da_gestao_tem_estilo_embutido"),
    (35, MODELOS / "base.html", "<body>", "<body><style>.x{}</style>",
     f"{T_POL}::test_nenhum_modelo_da_gestao_tem_estilo_embutido"),
    (36, PORTAL / "vitrine.html", None, "<script>alert(1)</script>\n",
     f"{T_POL}::test_nenhum_modelo_tem_script_embutido_nem_atributo_de_evento"),
    (36, MODELOS / "lista.html", "<h1>Processos Seletivos</h1>", "<h1 onclick=\"x()\">Processos Seletivos</h1>",
     f"{T_POL}::test_nenhum_modelo_tem_script_embutido_nem_atributo_de_evento"),
    (37, ESTATICOS / "mesa.js", None, "\nx.setAttribute(\"style\", \"color:red\");\n",
     f"{T_POL}::test_nenhum_script_escreve_estilo_que_a_politica_recusaria"),
    (38, MODELOS / "base.html", '"includeIndicatorStyles":false,', "",
     f"{T_POL}::test_toda_pagina_com_htmx_herda_a_configuracao_que_o_desarma"),
    (39, POLITICA, '("style-src", "\'self\'"),', '("style-src", "\'self\' \'unsafe-inline\'"),',
     f"{T_POL}::test_a_politica_so_permite_a_propria_origem_e_nada_embutido"),
    (40, POLITICA, 'EM_RECUSA = ("/gestao/",)', 'EM_RECUSA = ("/gestaox/",)',
     f"{T_POL}::test_toda_tela_da_gestao_recebe_a_politica_em_recusa"),
    (41, POLITICA, "    if _e_pagina_de_depuracao(resposta):\n        return None\n", "",
     f"{T_POL}::test_a_pagina_de_depuracao_fica_fora_so_com_debug"),
    # Reconhecer a depuração pelo status, e não pela marca: a recusa da própria gestão (404) perde a política.
    (42, POLITICA, "_MARCA_DA_DEPURACAO in resposta.content[:2048]", "resposta.status_code in (404, 500)",
     f"{T_POL}::test_a_recusa_da_propria_gestao_recebe_a_politica_mesmo_com_debug"),
    (43, Path("processo_seletivo/interface/prototipo_do_assistente.py"), "@em_observacao\n", "",
     "tests/interface/test_prototipo_do_assistente.py::test_o_fundo_do_portal_fica_sob_a_politica_do_portal"),
]


def arquivo_com(trecho):
    """O arquivo da folha comum que tem o trecho, ou o último, para o que se acrescenta no fim."""
    if trecho is None:
        return FOLHA_COMUM[-1]
    donos = [arquivo for arquivo in FOLHA_COMUM if trecho in arquivo.read_text()]
    assert len(donos) == 1, (trecho, donos)
    return donos[0]


def rodar(testes):
    r = subprocess.run(
        ["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "-x", *testes.split()],
        capture_output=True,
        text=True,
    )
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


falhas = []
for numero, arquivo, antes, depois, testes in MUTACOES:
    if arquivo == COMUM:
        arquivo = arquivo_com(antes)
    original = arquivo.read_text()
    if antes is None:
        mutado = original + depois
    else:
        assert original.count(antes) == 1, (numero, arquivo, antes)
        mutado = original.replace(antes, depois)
    arquivo.write_text(mutado)
    try:
        codigo, resumo = rodar(testes)
    finally:
        arquivo.write_text(original)
    reprovou = codigo != 0
    print(
        f"{numero:>2} {'REPROVA' if reprovou else 'PASSA  '} {arquivo.parent.name}/{arquivo.name}: "
        f"{(antes or '+')[:40]!r} -> {depois.strip()[:40]!r} | {testes.split('::')[-1][:60]} | {resumo}",
        flush=True,
    )
    if not reprovou:
        falhas.append(numero)

codigo, resumo = rodar(" ".join(sorted({t for m in MUTACOES for t in m[4].split()})))
print("sem mutação:", "passa" if codigo == 0 else "REPROVA", "|", resumo)
sys.exit(1 if falhas or codigo else 0)
