# Rastreabilidade — 171 · A orientação da verificação da autodeclaração

**Frase que governa**: *a verificação entra onde cada pessoa já trabalha, e cada tela diz só o que os
dados permitem afirmar.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações dos arquivos de teste:

- **US** — `tests/unit/portal/test_situacao_do_passo.py` (o degrau, puro)
- **PD** — `tests/portal/test_degrau_do_passo.py` (o acompanhamento, com banco, e o custo)
- **PV** — `tests/portal/test_verificacao_por_video.py` (o degrau com o vídeo da `166`)
- **VP** — `tests/portal/test_vocabulario_do_passo.py` (a varredura)
- **UE** — `tests/unit/editais/test_periodo_da_etapa.py` e `test_advertencia_do_nome.py`
- **IP** — `tests/integration/resultados/test_participa_com_conteudo.py`
- **AV** — `tests/integration/avisos/test_aviso_do_passo.py`
- **PE** — `tests/interface/test_pendencias_da_etapa_restrita.py`
- **C18** — `tests/integration/treinamento/test_cenario_c18.py`
- **G** — os guardiões atravessados: as naturezas do Centro, a coerência do andamento, as contagens
  de modelos iniciais e de cenários, as varreduras do aviso
- **navegador** — o percurso do `quickstart.md`, §3

---

## Requisitos funcionais

| Requisito | Onde entrou | Teste |
|---|---|---|
| FR-7300 | `portal/passo_da_etapa.py`, `portal/situacao.py` (`PASSO_*`) | US, PD |
| FR-7301 | `portal/passo_da_etapa.py` (`_restritas_que_alcancam`) | PD |
| FR-7302 | `portal/passo_da_etapa.py` (`participa_da_etapa`) | PD, IP |
| FR-7303 | `portal/situacao.py` (`_situacao_do_passo`, linha na convocação) | US |
| FR-7304 | `portal/situacao.py` (`CONSEQUENCIA_DA_AUSENCIA`, `VER_O_EDITAL`) | US, PD |
| FR-7305 | `editais/domain/cronograma.py` (`periodo_da_etapa`) | UE, US |
| FR-7306 | `portal/passo_da_etapa.py` (estados), `portal/situacao.py` | US, PD |
| FR-7307 | `portal/passo_da_etapa.py` (os visíveis ficam de fora) | PD |
| FR-7308 | `portal/passo_da_etapa.py` (derivado) | PD |
| FR-7309 | `portal/passo_da_etapa.py` (ordem), `portal/situacao.py` (`_linha_de_outro_passo`) | US |
| FR-7310 | nenhum código: o degrau não simula horário (requisito negativo) | revisão |
| FR-7311 | `portal/passo_da_etapa.py` (sem restrita, nenhuma consulta) | PD |
| FR-7312 | `portal/passo_da_etapa.py` (`_estado_do_video`), `portal/situacao.py` | PV, VP |
| FR-7313 | `portal/passo_da_etapa.py` (o vídeo enviado com a chave desligada) | PV |
| FR-7314 | `portal/views.py`, `acompanhamento.html`, `_verificacao_por_video.html` removido | PD, PV |
| FR-7315 | `avisos/domain/nomes.py` (`PASSO`), `avisos/models.py`, `avisos/0004_origem_passo` | AV |
| FR-7316 | `avisos/application/comando.py`, `confirmar.py` (`confirmar_aviso_do_passo`), `interface/avisos.py` | AV |
| FR-7317 | `avisos/application/comando.py` (a chave de sempre) | AV |
| FR-7318 | `avisos/application/destinatarios.py` (`universo_do_passo`) | AV |
| FR-7319 | `avisos/domain/modelos_iniciais.py` (`MODELO_DO_PASSO`), `avisos/domain/variaveis.py` | AV, G |
| FR-7320 | `avisos/application/modelos.py` (`chave_inicial`) | AV, G |
| FR-7321 | `avaliacoes/application/selectors.py` (`pendentes_por_membro`), `interface/andamento.py` | PE |
| FR-7322 | `interface/andamento.py` (`nota_do_alcance`) | PE, C18 |
| FR-7323 | `interface/andamento.py` (`AVISAR`), `interface/centro.py`, `interface/conceitos.py` | PE, C18, G |
| FR-7324 | `interface/andamento.py` (`sem_desfecho_vencido`) | PE |
| FR-7325 | `interface/andamento.py` (`_a_encaminhar`) | PE |
| FR-7326 | `comissoes/application/selectors.py` (`fim`), `interface/atividades.py`, `_atividade.html` | PE, C18 |
| FR-7327 | a regra de Minhas atividades da `160`, sem mudança | PE |
| FR-7328 | `avaliacoes/application/selectors.py` (a conta da Mesa) | PE |
| FR-7329 | nenhuma rota de gestão nova além da confirmação do aviso, que é a tela dos avisos | revisão |
| FR-7330 | `portal/situacao.py` (texto fixo) | US, VP |
| FR-7331 | `tests/portal/test_vocabulario_do_passo.py` (`TELAS`) | VP |
| FR-7332 | a varredura com nome e rótulos neutros | VP |
| FR-7333 | `treinamento/catalogo.py` (`montar_c18`), `treinamento/construcao.py` | C18, G |
| FR-7334 | `tests/integration/treinamento/test_cenario_c18.py` | C18 |
| FR-7335 | o C18 usa os atores e a carga dos outros cenários | C18, G |
| FR-7336 | `editais/domain/validation.py` (`_nome_da_restrita_com_termo_tecnico`) | UE |
| FR-7337 | `treinamento/catalogo.py` (`montar_c19`), `treinamento/servico.py` (`exige_verificacao_por_video`), `treinamento/amostras/video-de-treinamento.mp4` | `tests/integration/treinamento/test_cenario_c19.py` |

## Requisitos de experiência

| Requisito | Onde entrou | Teste |
|---|---|---|
| UX-790 | `portal/situacao.py` | US, VP |
| UX-791 | `portal/situacao.py` (porquê de uma linha) | US |
| UX-792 | `acompanhamento.html`, sem mudança de folha | navegador |
| UX-793 | `pendentes_por_membro` (ordem decrescente) | PE |
| UX-794 | `Acao.consequencia` no mesmo cartão | US |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| SC-2410 | C18 |
| SC-2411 | VP |
| SC-2412 | AV |
| SC-2413 | PE |
| SC-2414 | PD |
| SC-2415 | PV |
| SC-2416 | humano: o percurso da equipe no C18 |
