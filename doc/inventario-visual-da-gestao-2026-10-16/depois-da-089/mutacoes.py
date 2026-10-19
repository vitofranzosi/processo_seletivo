"""Prova por mutação dos guardiões repontados (089, FR-2038, SC-793).

    mutacoes.py            (de backend/, com o ambiente da suíte contra PostgreSQL)

Para cada linha do R-005: planta no arquivo estático a violação que o guardião existe para pegar,
roda o teste dele e exige que **reprove**; desfaz e segue. No fim, roda os mesmos testes sem mutação
e exige que passem. Uma linha que não reprova é um guardião enfraquecido.
"""

import subprocess
import sys
from pathlib import Path

GESTAO = Path("processo_seletivo/interface/static/interface/gestao.css")
TOKENS = Path("processo_seletivo/shared/static/shared/tokens.css")

# (nº do R-005, arquivo, trecho de antes ou None para acrescentar no fim, trecho de depois, testes)
MUTACOES = [
    (1, GESTAO, "\n.marca-irreversivel{", "\n.zzmut.marca-irreversivel{",
     "tests/interface/test_acessibilidade.py::test_nenhum_modificador_fica_sem_a_base_que_o_usa"),
    (1, GESTAO, "\n.oculto{", "\n.ocultx{",
     "tests/interface/test_acessibilidade.py::test_nenhuma_classe_citada_deixa_de_existir_na_folha"),
    (1, TOKENS, "--texto:#1c1c1c;", "--texto:#bbbbbb;",
     "tests/interface/test_acessibilidade.py::test_contraste_atende_wcag_aa"),
    (1, GESTAO, ".distribuicao-moldura{overflow-x:visible}", ".distribuicao-moldura{overflow-x:auto}",
     "tests/interface/test_acessibilidade.py::test_o_cabecalho_da_matriz_nao_e_fixado_dentro_de_um_contentor_de_rolagem"),
    (2, GESTAO, None, ".terminais .botao{color:red}\n",
     "tests/interface/test_polish_da_057.py::test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas"),
    (2, GESTAO, None, ".requisitos-apresentados{color:red}\n",
     "tests/interface/test_polish_da_057.py::test_os_documentos_da_inscricao_seguem_a_mesa"),
    (3, GESTAO, None, ".colunas.ao-topo{color:red}\n",
     "tests/interface/test_polish_da_058.py::test_as_terminais_moram_num_parcial_das_duas_telas"),
    (4, GESTAO, None, ".imutavel code{overflow-wrap:anywhere}\n",
     "tests/interface/test_telas_de_uso_diario.py::test_cada_correcao_vale_so_na_sua_tela"),
    (5, GESTAO, None, "main .zzmut{max-width:600px}\n",
     "tests/interface/test_larguras.py::test_nenhuma_das_bases_crava_largura_em_pixel"),
    (6, GESTAO, None, ".so-admite{display:none}\n",
     "tests/interface/test_campos_que_a_escolha_governa.py::test_a_folha_nunca_esconde_por_padrao"),
    # A regra de `regra()` é a primeira que casa: a mutação muda a que existe, e não acrescenta outra.
    (7, GESTAO, ".assistente .estado{font-size:.75rem;", ".assistente .estado{text-transform:uppercase;font-size:.75rem;",
     "tests/interface/test_polish_da_056.py::test_a_situacao_da_etapa_continua_em_texto"),
    (8, GESTAO, None, ".acoes .marca-irreversivel{align-self:center}\n",
     "tests/interface/test_achados_das_revisoes.py::test_a_marca_nao_estica_em_linha_flexivel"),
    (9, GESTAO, None, ".distribuicao thead th .codigo{display:block}\n",
     "tests/interface/test_alocacoes.py"),
    (10, GESTAO, ".acao.desabilitado{color:var(--texto-fraco);", ".acao.desabilitado{color:var(--verde);",
     "tests/interface/test_lista.py"),
    (11, GESTAO, ".s-PRESIDENTE{", ".s-PRESIDENTX{",
     "tests/interface/test_comissao.py"),
    (13, GESTAO, None, "{% comment %}\n",
     "tests/interface/test_estaticos.py::test_nenhuma_sintaxe_de_template_nas_folhas_estaticas"),
    # O `"--pagina" in folha` do resultado público já casava com o `var(--pagina)` da folha do portal
    # antes da 089, e não pega a declaração sumida; quem a pega é o guardião das larguras, logo abaixo.
    # O resultado público lia `"--pagina" in folha`, que casava também com o `var(--pagina)` da folha
    # do portal: a declaração sumida passava. A 089 o apertou para `--pagina:`.
    (14, TOKENS, " --pagina:96rem;", "",
     "tests/portal/test_resultado_publico.py::test_a_pagina_nao_tem_largura_fixa_que_force_rolagem_horizontal"),
    (14, TOKENS, " --pagina:96rem;", "",
     "tests/interface/test_larguras.py::test_as_duas_larguras_vivem_nos_tokens"),
    (15, GESTAO, "th,td{text-align:left;padding:.5rem .75rem;", "th,td{text-align:left;padding:.4rem .75rem;",
     "tests/interface/test_polish_da_055.py::test_a_celula_tem_o_preenchimento_do_portal"),
    (16, TOKENS, "--leitura:68ch;", "--leitura:70ch;",
     "tests/interface/test_medida_dos_campos.py"),
    (17, GESTAO, "background:linear-gradient(to right,var(--branco) calc(4.25rem - 1px)", "background:linear-gradient(to left,var(--branco) calc(4.25rem - 1px)",
     "tests/interface/test_shell_da_gestao.py::test_a_folha_recolhe_so_na_tela_larga_e_sem_movimento_forcado"),
    (18, GESTAO, None, ".zzmoldura{overflow-x:auto}\n",
     "tests/interface/test_telas_de_quem_elabora.py::test_toda_moldura_que_rola_e_referencia_do_que_carrega"),
    (19, GESTAO, ".tabela-rolavel{overflow-x:auto}", ".tabela-rolavel{overflow-x:scroll}",
     "tests/interface/test_acessibilidade_da_classificacao.py::test_o_conteiner_limita_a_rolagem_horizontal"),
    (20, GESTAO, ".tabela-rolavel,.rolagem,.rolagem-da-tabela,.serie .barras{position:relative}", ".rolagem,.rolagem-da-tabela,.serie .barras{position:relative}",
     "tests/interface/test_visao_dos_perfis.py"),
    (21, GESTAO, ".tabela-rolavel,.rolagem,.rolagem-da-tabela,.serie .barras{position:relative}", ".rolagem,.rolagem-da-tabela,.serie .barras{position:relative}",
     "tests/interface/test_visao_da_classificacao.py"),
    (22, GESTAO, ".tabela-rolavel{overflow-x:auto}", ".tabela-rolavel{overflow-x:scroll}",
     "tests/integration/interface/test_inscricoes_recebidas.py::test_a_tabela_larga_rola_dentro_de_si_mesma"),
    # O guardião da impressão da 088, que chegou com o merge da `main`, depois do inventário.
    (23, GESTAO, ".barra-lateral,.cabecalho-de-contexto>a{display:none}", ".barra-lateral,.cabecalho-de-contexto{display:none}",
     "tests/interface/test_decisoes_da_etapa_4.py::test_no_papel_sai_o_cabecalho_sem_trocar_identidade_e_sem_a_barra"),
    (23, GESTAO, ".cabecalho-de-contexto{display:block;min-height:0;", ".cabecalho-de-contexto{display:block;white-space:nowrap;min-height:0;",
     "tests/interface/test_decisoes_da_etapa_4.py::test_no_papel_a_trilha_quebra_a_linha"),
]


def rodar(testes):
    r = subprocess.run(["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "-x", *testes.split()],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


falhas = []
for numero, arquivo, antes, depois, testes in MUTACOES:
    original = arquivo.read_text()
    if antes is None:
        mutado = original + depois
    else:
        assert original.count(antes) == 1, (numero, antes)
        mutado = original.replace(antes, depois)
    arquivo.write_text(mutado)
    try:
        codigo, resumo = rodar(testes)
    finally:
        arquivo.write_text(original)
    reprovou = codigo != 0
    print(f"{numero:>2} {'REPROVA' if reprovou else 'PASSA  '} {arquivo.name}: {(antes or '+')[:40]!r} -> {depois.strip()[:40]!r} | {testes.split('::')[-1][:60]} | {resumo}", flush=True)
    if not reprovou:
        falhas.append(numero)

codigo, resumo = rodar(" ".join(sorted({t for m in MUTACOES for t in m[4].split()})))
print("sem mutação:", "passa" if codigo == 0 else "REPROVA", "|", resumo)
sys.exit(1 if falhas or codigo else 0)
