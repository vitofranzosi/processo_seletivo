# Verificação: Os textos que o operador do sorteio lê (124)

## As três telas no navegador (SC-1192)

Conferidas em 06/11/2026 no painel do aplicativo, contra o `live_server` da suíte (PostgreSQL), com um
Edital publicado de sorteio pela Loteria Federal, concurso 6098, e o adaptador **real** da Caixa. A
fonte inacessível foi simulada trocando `urllib.request.urlopen` no processo do servidor por uma
chamada que levanta `URLError(TimeoutError)`; depois, pela mesma troca, por uma resposta da forma da
Caixa (`dataApuracao` 04/11/2026). Identidades de demonstração, sem nome real.

1. **A recusa com a fonte inacessível.** Ao clicar em "Observar a ocorrência 6098 na fonte", a faixa
   diz: *"Não foi possível obter os números na fonte: Não foi possível falar com Loteria Federal
   agora, e por isso nada foi registrado: a ocorrência '6098' continua sendo a que vale, e
   observá-la de novo é o próximo passo. Falha de acesso não é ausência de extração — registrá-la
   como indisponibilidade descartaria a extração que o Edital declarou. Concurso 6098 de Loteria
   Federal: a Caixa não respondeu a tempo, em 3 tentativa(s)."* Sem `URLError`, sem `<urlopen`, sem
   asteriscos. O log do servidor trouxe `observacao_sem_acesso_a_fonte` com as três falhas técnicas.
2. **O limite inferior.** Com a Caixa de volta, a observação registrou a ocorrência e o campo diz:
   *"04/11/2026 — a fonte publica só a data da extração, sem o horário. O sistema conta desde 00h00
   desse dia: é o limite inferior, e não a hora em que a extração aconteceu, e é ele que se compara
   com o congelamento."* A frase "só a data, sem o horário" é a do aviso da `102`, que aparece logo
   abaixo na mesma tela; a primeira redação ("só o dia… e não a hora") foi trocada por ela.
3. **A ajuda da etapa.** Na Classificação, com o marco por sorteio, "Como preencher estes campos"
   tem o item "Ocorrência que fixará a semente", com link para o cartão do marco (âncora presente na
   página). As duas descrições `.oculto` do campo continuam apontadas. Nenhuma violação de CSP no
   console.

## Suíte

`cd backend && make lint check test-pg`, em 06/11/2026 sobre `250efe97` mais esta branch, com os
grupos `assistente` e `navegador` instalados, 4 workers: `ruff check` e `ruff format --check`
verdes, `check` sem problema, e **16755 passando e 12 pulados, sem falha**, em 850s. Os 12 são os
da seção de armadilhas do `CLAUDE.md` para quem tem os dois grupos.
