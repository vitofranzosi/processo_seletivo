# Quickstart — 076

## Subir

Num banco com `seed_demo` (o `ps_inventario_telas` do inventário de 16/10 serve), a partir de
`backend/`:

```bash
LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_inventario_telas DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true ASSISTENTE_PILOTO=true uv run python manage.py runserver 8076
```

## Percurso

1. Abrir `http://localhost:8076/gestao/`, entrar pela demonstração como **Gestor**.
2. A barra mostra *Trabalho* (Processos Seletivos, Minhas Etapas, Visão Geral) e *Unidade*
   (Autoridades da unidade, Modelos de aviso); Processos Seletivos está destacado.
3. Abrir um Edital. O caminho do topo diz `GPS › Processos Seletivos`, em texto, a
   trilha da tela continua logo abaixo, e a barra destaca Processos Seletivos. Seguir "Visão Geral" pela barra: chega sem passar pela lista.
4. "Trocar identidade" → página de acesso com continuar e trocar. Entrar como **Elaborador**: a
   barra não tem Visão Geral nem o grupo *Unidade*. Abrir `/gestao/visao-geral` à mão: a mesma
   recusa de antes.
5. Entrar pela presidência de uma comissão: a barra tem Processos Seletivos e Minhas Etapas.
6. A 375 px (`resize_window` preset mobile): a barra começa recolhida; "Seções" a abre, por toque e
   por Enter; Tab entra nos itens; nenhuma rolagem horizontal.
7. Esc fecha a barra aberta; tocar fora dela também.
8. Só pelo teclado, na tela larga: o primeiro Tab mostra "Pular para o conteúdo", que leva o foco
   ao conteúdo; sem ele, a ordem é marca, seções, Sair, Trocar identidade. A 375 px, a barra do topo continua à vista ao rolar.

## A barra retrátil (US5)

9. Na tela larga, o controle na última linha da barra diz "Recolher a barra lateral". Acioná-lo — clique,
   Enter ou toque — recolhe a barra a uma faixa de ícones; o controle passa a dizer "Expandir a
   barra lateral", o conteúdo ganha a largura, e nenhum ícone muda de lugar — o controle fica sob o
   ponteiro para expandir de novo.
10. Recolhida: o ponteiro ou o foco do teclado num ícone mostra o nome da seção; a seção atual
    continua marcada; o pé mostra as iniciais e o "Sair" como ícone.
11. Abrir outra seção e recarregar: a barra já aparece recolhida, sem passar pela expandida.
12. A 375 px, com a preferência recolhida guardada: o painel "Seções" é o de sempre, com nomes.
13. Na Alocação por Etapa, a barra fica no topo, qualquer que seja a preferência.
14. Sem preferência guardada (`localStorage.removeItem("gps.barra")`), a barra começa expandida a
    1280 px e recolhida a 1100 px — e expandida num tablet de toque, em qualquer largura.

## Inventário

Com o mesmo ambiente, a partir de `backend/`:

```bash
AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py <pasta-de-saída>
```

Com `BARRA=recolhida` (ou `expandida`) na mesma linha, o roteiro grava a preferência antes de cada
página. Comparar o `resultados.json` da saída com o da linha de base, tela a tela: status, `scrollWidth`
contra `clientWidth` a 375 e a 1280.
