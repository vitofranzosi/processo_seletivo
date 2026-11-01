# Checklist: segurança, autorização, acessibilidade e qualidade gráfica

**Purpose**: conferir, na revisão de cada PR do kit, o que a suíte não prova sozinha, ou só prova em
parte.
**Created**: 2026-10-31 · **Revisto**: 2026-11-01, depois da [revisão crítica](../revisao-critica.md)
**Feature**: [spec.md](../spec.md)

Cada item cita o requisito. Item marcado é item conferido no PR; item com **humano** é conferido por
pessoa. **Verde nos guardiões de citação e de dado pessoal prova os artefatos, e não a
implementação**: estes itens são conferidos sobre o código.

## Autorização

- [ ] CHK001 A capacidade `material:gerar` não está em nenhum papel além de `comunicacao` (FR-3403)
- [ ] CHK002 Toda rota do kit faz, nesta ordem: escopo (404), capacidade (recusa explicada), Edital publicado (409) (FR-3402)
- [ ] CHK003 As rotas novas estão no inventário das negativas da `033`, e o módulo em `MODULOS_DE_VIEW` (FR-3402)
- [ ] CHK004 A pessoa só do papel `comunicacao` não pratica ato nenhum. Testado por ato, e não por amostra (FR-3403)
- [ ] CHK005 Nenhuma view do kit lê `PerfilVaga`, `EventoCronograma`, `RevisaoEdital` nem Retificação fora de `PUBLICADA` (FR-3404)
- [ ] CHK006 Nenhuma pessoa recebeu o papel antes da resolução da P-2 (leitura de conteúdo não publicado verificada no backend, em spec própria) — **humano**

## Segurança da entrega

- [ ] CHK007 Todo texto entra no SVG como nó escapado, já normalizado pela grafia. O único atributo vindo de dado é `data-campo`, com valor de lista fechada (D-008, D-009)
- [ ] CHK008 O SVG exportado leva `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; font-src data:` e `X-Content-Type-Options: nosniff`. A fonte embutida é a única coisa que a política admite (FR-3422, FR-3442; D-014, D-021)
- [ ] CHK009 O rasterizador não resolve recurso externo: nenhum `resources_dir`, nenhum `href` fora de `data:` gerado pelo sistema, fontes só por arquivo (D-007)
- [ ] CHK010 Respostas privadas (`no-store`) em tela, prévia e exportações (FR-3442)
- [ ] CHK011 A manchete chega como **índice** da lista fechada que a tela ofereceu. O backend recalcula a lista e recusa índice fora dela, ou manchete quando um título oficial cabe (422). Não existe caminho de texto livre (FR-3427; D-013)
- [ ] CHK012 O evento de exportação não contém dado pessoal além do ator (FR-3436)
- [ ] CHK013 Licença do `resvg-py` e das transitivas registrada em `verificacao-do-motor.md` antes do `pyproject` (D-007)
- [ ] CHK014 Em host local, nenhum link absoluto e nenhuma peça (FR-3447)
- [ ] CHK015 A prévia e a exportação conferem a impressão vista na tela e recusam com 409 se o Edital mudou (FR-3446)
- [ ] CHK016 O evento de exportação tem estado anterior igual ao atual, rótulo legível na trilha e não conta no relatório da trilha (FR-3436)

## Correção do que se afirma

- [ ] CHK017 As **frases fixas, a composição e as manchetes** não contêm termo da FR-3414, em nenhum cenário de referência. **Valores oficiais literais** (título, nome do Perfil, localidade) não são alterados nem reprovados: a conferência os aponta (FR-3414, EC-26)
- [ ] CHK018 Modo neutro: nenhuma frase do kit, nos textos ou na peça, fala de inscrição. Um valor oficial que contenha a palavra é apontado, e não removido (FR-3416, EC-26)
- [ ] CHK019 Retificação a vigorar: conteúdo futuro nunca aplicado antes da vigência; anúncio na tela, nas notas e no manifesto (FR-3440)
- [ ] CHK020 Prorrogação dita só com término vigente posterior ao original, pela regra movida sem mudança; com a mesma data, a hora nas duas pontas (FR-3417, EC-25)
- [ ] CHK021 Nada de "curso", "campus" ou "polo" que o dado não escreveu (FR-3409)
- [ ] CHK022 Total de vagas só quando toda opção tem vaga imediata, e sempre como "N vagas em K opções" (FR-3425, EC-11)
- [ ] CHK023 A proveniência usa `origens`/`acrescimos`, e nunca o caminho exato da `ProvenienciaConteudo` (FR-3408)
- [ ] CHK024 Desfecho depois de exportação gera "não deve mais circular"; exportações antigas continuam listadas (FR-3445, FR-3439)
- [ ] CHK025 A busca indicada leva a sigla da unidade (FR-3418, EC-24)

## Acessibilidade da tela

- [ ] CHK026 Nenhum `style=`, `<style>`, `<script>` embutido nem `on*=` no template (FR-3444)
- [ ] CHK027 "Copiar" é `<button>` nativo, alcançável pelo teclado, com o resultado anunciado por `aria-live` (FR-3420)
- [ ] CHK028 A prévia tem `alt` com o texto alternativo da peça (FR-3433)
- [ ] CHK029 Tela legível a 375 px e com texto a 200%, sem rolagem horizontal da página (FR-3444) — **humano**, com captura
- [ ] CHK030 As faixas (desatualização, desfecho, a vigorar, neutro, omissão, host local, termo apontado) têm texto, e não só cor (FR-3443)

## Qualidade gráfica da peça

- [ ] CHK031 Nenhum texto abaixo de 24 px; margem de 80 px; contraste AA das cores do template (FR-3428)
- [ ] CHK032 Teste geométrico verde nos cenários e nos sintéticos da D-016, inclusive palavra partida (FR-3429)
- [ ] CHK033 O título nunca truncado; a omissão é dita na tela (FR-3426)
- [ ] CHK034 Rodapé medido; o endereço longo desce até o mínimo ou recusa (FR-3431)
- [ ] CHK035 Espaço livre distribuído com pouca oferta: o corpo desce 35% da folga (FR-3434) — e **humano**, na galeria
- [ ] CHK036 Com excesso de informação, a peça conta e manda à página em vez de listar (FR-3425) — **humano**, na galeria
- [ ] CHK037 O SVG exportado desenha com a Edital Sans fora do GPS (navegador e uma ferramenta de design) (FR-3422) — **humano**
- [ ] CHK038 SVG de referência atualizado quando o template muda, com o diff revisado (D-016)
- [ ] CHK039 A marca é o ativo oficial, com `ORIGEM.md` (FR-3432) — **humano**, depois da P-3
- [ ] CHK040 A galeria dos cenários de referência foi aprovada pela comunicação (SC-1054) — **humano**
