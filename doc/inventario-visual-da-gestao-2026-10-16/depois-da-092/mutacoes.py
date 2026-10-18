"""Prova por mutação dos guardiões do portal, repontados e novos (092, FR-2139, SC-823).

    mutacoes.py            (de backend/, com o ambiente da suíte contra PostgreSQL)

Para cada linha: planta no arquivo a violação que o guardião existe para pegar, roda o teste dele e
exige que **reprove**; desfaz e segue. No fim, roda os mesmos testes sem mutação e exige que passem.

O molde é o da 091 (`depois-da-091/mutacoes.py`), com uma diferença: uma mutação pode ter mais de uma
troca no mesmo arquivo — mover um trecho é tirar de um lugar e pôr noutro.

Não rode com outra suíte da mesma worktree em curso: o arquivo mutado é o da árvore de trabalho.
"""

import subprocess
import sys
from pathlib import Path

PORTAL_CSS = Path("processo_seletivo/portal/static/portal/portal.css")
MODELOS = Path("processo_seletivo/portal/templates/portal")
BASE = MODELOS / "base.html"
DOCUMENTOS = MODELOS / "_documentos.html"
INSCRICAO = MODELOS / "inscricao.html"
POLITICA = Path("processo_seletivo/shared/politica_de_conteudo.py")
PROTOTIPO = Path("processo_seletivo/interface/prototipo_do_assistente.py")

T_ACESS = "tests/interface/test_acessibilidade.py"
T_ACESS_P = "tests/interface/test_acessibilidade_do_portal.py"
T_POL = "tests/interface/test_politica_de_conteudo.py"
T_FOLHA = "tests/interface/test_folha_estatica.py"
T_COMPROVANTE = "tests/integration/portal/test_revisao_e_comprovante.py"
T_ENVIO = "tests/integration/inscricoes/test_envio_de_arquivo.py"
T_CRONO = "tests/integration/portal/test_cronograma_publico.py"
T_055 = "tests/interface/test_polish_da_055.py"

FIM = None  # acrescentar no fim do arquivo

# (nº, arquivo, [(trecho de antes, ou FIM, trecho de depois), ...], testes)
MUTACOES = [
    # ---- a folha do portal, lida pelo texto (`FOLHA_DO_PORTAL`, `PORTAL_CSS`) ----
    (1, PORTAL_CSS, [("\n.abertas-agora{", "\n.zzmut.abertas-agora{")],
     f"{T_ACESS}::test_nenhum_modificador_fica_sem_a_base_que_o_usa"),
    (2, PORTAL_CSS, [("\n.acao-principal{", "\n.acao-principalx{")],
     f"{T_ACESS}::test_nenhuma_classe_citada_deixa_de_existir_na_folha"),
    (3, PORTAL_CSS, [(FIM, ".zzmut{width:600px}\n")],
     f"{T_ACESS_P}::test_nada_no_portal_fixa_largura_em_pixel"),
    (4, PORTAL_CSS, [(".perfil:target{border-left:6px solid", ".perfil:target{border-left:5px solid")],
     f"{T_ACESS_P}::test_a_vaga_indicada_nao_depende_so_de_cor"),
    (5, PORTAL_CSS, [("[type=file]){height:2.625rem}", "[type=file]){height:2.5rem}")],
     f"{T_055}::test_uma_altura_por_folha_para_os_controles_de_uma_linha"),
    (6, PORTAL_CSS, [(".grade-de-campos .largo>:is(input,select){max-width:40rem}",
                      ".grade-de-campos .largo>:is(input,select){max-width:41rem}")],
     f"{T_055}::test_o_campo_curto_do_requerimento_nao_estica_a_linha"),
    (7, PORTAL_CSS, [(FIM, ".envio .linha{display:flex}\n")],
     "tests/interface/test_polish_da_057.py::test_o_envio_de_documento_e_uma_linha"),
    (8, PORTAL_CSS, [("  .timbre{display:block;", "  .timbre{display:flex;")],
     f"{T_COMPROVANTE}::test_o_papel_nao_leva_navegacao_nem_botao"),
    (9, PORTAL_CSS, [("html,body{font-size:10.5pt;", "html,body{font-size:11pt;")],
     f"{T_COMPROVANTE}::test_o_comprovante_cabe_em_uma_pagina"),
    # ---- a folha que a página aplica (`folha_aplicada`, `folha_da_pagina`) ----
    (10, PORTAL_CSS, [("@media print{", "@media screen and (max-width:0){")],
     f"{T_COMPROVANTE}::test_o_comprovante_e_privado_e_imprimivel"),
    (11, PORTAL_CSS, [("a.principal{display:inline-block;", "a.principal{display:block;")],
     f"{T_COMPROVANTE}::test_o_comprovante_pode_ser_baixado_e_reencontrado"),
    (12, PORTAL_CSS, [(".progresso[hidden]{display:none}", ".progresso[hidden]{display:block}")],
     f"{T_ENVIO}::test_o_aviso_de_nao_fechar_a_pagina_fica_escondido_em_repouso"),
    (13, PORTAL_CSS, [(".escolher input[type=file]{position:absolute;", ".escolher input[type=file]{position:relative;")],
     f"{T_ENVIO}::test_o_campo_de_arquivo_do_navegador_nao_aparece_cru"),
    (14, PORTAL_CSS, [(".selecao .situacao{font-size:.9375rem}", ".selecao .situacao{color:red;font-size:.9375rem}")],
     "tests/portal/test_peso_da_vitrine.py::test_a_situacao_da_vitrine_nao_e_pintada_pela_regra_da_outra_tela"),
    (15, PORTAL_CSS, [(FIM, "main{width:900px}\n")],
     "tests/portal/test_resultado_publico.py::test_a_pagina_nao_tem_largura_fixa_que_force_rolagem_horizontal"),
    (16, PORTAL_CSS, [(FIM, ".zzmut{max-width:600px}\n")],
     "tests/interface/test_larguras.py::test_nenhuma_das_bases_crava_largura_em_pixel"),
    (17, PORTAL_CSS, [("repeat(auto-fill,minmax(min(26rem", "repeat(auto-fit,minmax(min(26rem")],
     "tests/interface/test_larguras.py::test_a_vitrine_usa_a_tela_em_duas_colunas"),
    (33, PORTAL_CSS, [(".documento.secundaria{background:var(--branco)", ".documento.secundaria{background:var(--verde)")],
     "tests/integration/portal/test_detalhe_selecao.py::test_ler_o_edital_nao_disputa_a_decisao_com_inscrever_se"),
    (34, PORTAL_CSS, [('a.titulo::after{content:"";position:absolute;inset:0}', 'a.titulo::after{content:"";position:absolute;inset:1px}')],
     "tests/integration/portal/test_detalhe_selecao.py::test_o_cartao_da_vitrine_e_alvo_inteiro"),
    # ---- o arquivo novo nas varreduras ----
    (18, PORTAL_CSS, [(FIM, "{% comment %}\n")],
     "tests/interface/test_estaticos.py::test_nenhuma_sintaxe_de_template_nas_folhas_estaticas"),
    (19, PORTAL_CSS, [(FIM, "/* FR-9999 */\n")],
     "tests/test_citacoes_de_requisito.py::test_nenhuma_citacao_aponta_para_requisito_inexistente"),
    (20, PORTAL_CSS, [(".largura-37{width:37%;} ", "")],
     f"{T_POL}::test_uma_classe_por_valor_de_zero_a_cem"),
    # ---- os modelos do portal ----
    (21, DOCUMENTOS, [('<div class="feito largura-', '<div style="width:1%" class="feito largura-')],
     f"{T_POL}::test_nenhum_modelo_tem_estilo_embutido"),
    (22, BASE, [("</head>", "<style></style>\n</head>")],
     f"{T_POL}::test_nenhum_modelo_tem_estilo_embutido"),
    (23, DOCUMENTOS, [("documentos.total 100 %}", "documentos.total 10 %}")],
     f"{T_POL}::test_a_barra_de_documentos_leva_a_classe_do_percentual"),
    (24, DOCUMENTOS, [('class="feito largura-{%', 'class="feito largurx-{%')],
     f"{T_ENVIO}::test_o_progresso_dos_documentos_e_barra_e_nao_segunda_frase"),
    (25, BASE, [("<link rel=\"stylesheet\" href=\"{% estatico 'portal/portal.css' %}\">\n", "")],
     f"{T_FOLHA}::test_a_base_do_portal_carrega_a_folha_dele"),
    (26, BASE, [("<link rel=\"stylesheet\" href=\"{% estatico 'shared/tokens.css' %}\">\n", ""),
                ("<link rel=\"stylesheet\" href=\"{% estatico 'portal/portal.css' %}\">\n",
                 "<link rel=\"stylesheet\" href=\"{% estatico 'portal/portal.css' %}\">\n"
                 "<link rel=\"stylesheet\" href=\"{% estatico 'shared/tokens.css' %}\">\n")],
     f"{T_FOLHA}::test_as_outras_bases_carregam_os_tokens_antes_de_qualquer_regra"),
    (27, INSCRICAO, [('{% include "portal/_resumo_documentos.html" %}\n', ""),
                     ('<h2 id="seus-dados">Seus dados</h2>\n',
                      '<h2 id="seus-dados">Seus dados</h2>\n{% include "portal/_resumo_documentos.html" %}\n')],
     f"{T_ENVIO}::test_quantos_documentos_faltam_aparece_junto_ao_cabecalho"),
    (28, BASE, [("<body>\n", "<body>\n<p>Acontecendo agora</p>\n")],
     f"{T_CRONO}::test_evento_sem_termino_nao_acontece_para_sempre"),
    (29, BASE, [("<body>\n", '<body>\n<p class="linha-do-tempo"></p>\n')],
     f"{T_CRONO}::test_sem_evento_publicado_a_secao_some_inteira"),
    # ---- a política ----
    (30, POLITICA, [("            resposta[CABECALHO] = POLITICA", "            resposta[CABECALHO + \"-Report-Only\"] = POLITICA")],
     f"{T_POL}::test_o_portal_e_o_resto_do_html_recebem_a_politica_em_recusa"),
    (31, POLITICA, [("    if CABECALHO in resposta:\n        return False\n", "    if CABECALHO in resposta:\n        return False\n    if b'lang=\"pt-BR\"' in resposta.content[:200] and b'class=\"pular\"' in resposta.content and b'/selecoes/' in resposta.content:\n        return False\n")],
     f"{T_POL}::test_o_portal_e_o_resto_do_html_recebem_a_politica_em_recusa"),
    (32, PROTOTIPO, [("    return HttpResponse(html)\n", "    return HttpResponse(html, headers={\"Content-Security-Policy-Report-Only\": \"default-src *\"})\n")],
     "tests/interface/test_prototipo_do_assistente.py::test_o_fundo_do_portal_fica_sob_a_recusa"),
]


def rodar(testes):
    r = subprocess.run(
        ["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "-x", *testes.split()],
        capture_output=True,
        text=True,
    )
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


falhas = []
for numero, arquivo, trocas, testes in MUTACOES:
    original = arquivo.read_text()
    mutado = original
    for antes, depois in trocas:
        if antes is FIM:
            mutado += depois
        else:
            assert mutado.count(antes) == 1, (numero, arquivo, antes)
            mutado = mutado.replace(antes, depois)
    arquivo.write_text(mutado)
    try:
        codigo, resumo = rodar(testes)
    finally:
        arquivo.write_text(original)
    reprovou = codigo != 0
    antes, depois = trocas[0]
    print(
        f"{numero:>2} {'REPROVA' if reprovou else 'PASSA  '} {arquivo.name}: "
        f"{(antes or '+')[:40]!r} -> {depois.strip()[:40]!r} | {testes.split('::')[-1][:60]} | {resumo}",
        flush=True,
    )
    if not reprovou:
        falhas.append(numero)

codigo, resumo = rodar(" ".join(sorted({m[3] for m in MUTACOES})))
print("sem mutação:", "passa" if codigo == 0 else "REPROVA", "|", resumo)
sys.exit(1 if falhas or codigo else 0)
