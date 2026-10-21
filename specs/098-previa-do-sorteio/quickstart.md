# Quickstart: validar a prévia do sorteio

## Hoje, antes da implementação: o protótipo

De dentro de `backend/`, com o Python do projeto:

```bash
PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test uv run python ../specs/098-previa-do-sorteio/prototipo/medicao.py
```

Saída esperada (os tempos variam com a máquina; as porcentagens, ±5 pontos com outra base de semente):

```text
32 inscritos, 2 reservadas: uma rodada 0.2 ms; 1000 rodadas 0.09 s
500 inscritos, 6 reservadas: uma rodada 1.6 ms; 1000 rodadas 1.39 s
reversão não declarada — PPI: sobra em 72% das rodadas, … PcD: sobra em 54% das rodadas, …
reversão ON_BALANCE — … média cedida 1.01 …
reversão ON_EXHAUSTION — … média cedida 0.00 …
```

É a [R-001](research.md#r-001--o-que-o-motor-faz-com-a-população-da-história-1-medido) e a
[R-003](research.md#r-003--quanto-custa-e-se-as-1000-rodadas-cabem).

## Depois da implementação: pela interface

Pré-requisitos: banco migrado e preparado (`make preparar`), `INTERFACE_SELETOR_IDENTIDADE=true`, uma
identidade com permissão de compor Edital.

1. Na composição de um Edital em rascunho, crie um Perfil com 10 vagas na linha geral e as Modalidades
   PPI (3 vagas) e PcD (2 vagas). Grave.
2. Na etapa Classificação, no marco do Perfil, escolha a forma **sorteio** e a regra de corte pelo
   quadro, sem suplentes.
3. Aperte **Simular sorteio**. Confira:
   - a faixa da semente, com cinco números de seis dígitos e o selo de fictícia (FR-2481, FR-2482);
   - a população sugerida: 20 só na ampla, 6 PPI, 4 PcD (FR-2487);
   - a jornada com o resumo por recorte, e a ampla dizendo que tem os 30 (FR-2488);
   - o resumo das rodadas, dizendo que fez 1.000, com a PPI sobrando vaga perto de 72% das vezes
     (FR-2501, FR-2503) e a frase de comportamento atual (FR-2507).
4. Aperte **Sortear de novo**: a semente muda, a rodada muda, o resumo varia poucos pontos (FR-2484,
   SC-929).
5. Mude a PPI para 15: o anúncio diz que a semente foi mantida (FR-2485); a ampla passa a 39.
6. Abra o detalhe, escolha a PPI no seletor: cada linha tem a posição na PPI e a posição na ampla
   (FR-2494).
7. No passo Perfis, declare a reversão "Só quando a lista reservada esgota", grave, e simule de novo: o
   resumo diz que nada seria cedido em todas as rodadas (FR-2499, FR-2503).
8. No navegador, edite o campo oculto `semente` e recalcule: o painel recusa e oferece sortear de novo
   (FR-2483, SC-931).
9. A 375 px, repita 4 e 6 sem rolagem horizontal da página (FR-2510).

## Pela suíte

```bash
cd backend && make lint check test-pg
```

Os testes da feature estão listados em `tasks.md` e na matriz `rastreabilidade.md`. Os que provam a
garantia central são o de equivalência (R-009), o de ausência de efeito (SC-930) e a varredura de
`test_sem_gerador_pseudoaleatorio.py`, que tem de continuar verde sem emenda (R-004).
