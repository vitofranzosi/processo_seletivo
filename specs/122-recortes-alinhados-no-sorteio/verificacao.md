# Verificação: 122

## T001 — Levantamento do acervo na instalação

**Dispensado pelo usuário em 05/11/2026** (*"esquece a VM"*). Não houve execução, e não há números. A
implementação seguiu sem eles; o portal continua fora do escopo (FR-3915).

## T002 — Testes que mudaram de expectativa

Dois, e os dois por decisão desta feature:

| Arquivo | Caso | Antes | Agora |
|---|---|---|---|
| `tests/interface/test_previa_do_sorteio.py` | `test_perfil_sem_reserva_tem_uma_lista_e_nao_fala_de_cotas` | a prévia dizia que a Modalidade apontada *"ganha uma lista própria no sorteio do certame"* | diz que ela não tem sorteio próprio (FR-3895) |
| `tests/interface/test_destinos_do_edital.py` | `_divulgacao`, e o caso do Publicador puro | o caminho de divulgação era a prévia do ato | é o quadro da condução, `#divulgacao`, e a prévia está a um clique dele (FR-3906, FR-3907) |

Os demais testes que citam `generalCompetitionModalityId` (40 arquivos) não mudaram: nenhum sorteava a
lista da Modalidade apontada.

## Suíte contra PostgreSQL

`make test-pg`, 4 workers, banco `ps122`, sem os grupos `assistente` e `navegador`, depois de US1 a US5:
**16470 passaram, 19 pulados, nenhuma falha**, em 699 s (05/11/2026). A rodada final, com o teste das
seis superfícies e a jornada no navegador, está abaixo.

## A jornada no navegador (SC-1165)

`tests/navegador/test_jornada_dos_recortes.py`, com `NAVEGADOR_CAPTURAS`. As capturas estão em
[`capturas/`](capturas/):

1. `…-01-sorteio.png` — a presidência na tela do sorteio: três recortes, a frase da Modalidade apontada
   e, no fim, *"Registros fora da operação atual"* com a relação, o sorteio e o ato de AC, cada um com
   a frase de quem nasceu excedente e sem botão;
2. `…-02-quadro.png` — o Publicador puro chega ao quadro pelo único *"divulgar o resultado"* da página
   do Edital; os três recortes pelo nome, cada célula de publicação *"Falta"* com link para a prévia;
3. `…-03-quadro-feito.png` — depois de divulgar os três, um a um pela prévia: três *"Feito"*;
4. `…-04-supervisao.png` — a Supervisão sem nenhum sinal sobre a lista de AC.

## T040 — percurso humano

**Não feito nesta sessão.** A jornada foi verificada no navegador pela suíte; percorrê-la à mão num
banco de demonstração fica com o usuário.
