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
3. Abrir um Edital. O caminho do topo diz `Gestão de Processos Seletivos › Processos Seletivos`, a
   trilha da tela continua logo abaixo, e a barra destaca Processos Seletivos. Seguir "Visão Geral" pela barra: chega sem passar pela lista.
4. "Trocar identidade" → página de acesso com continuar e trocar. Entrar como **Elaborador**: a
   barra não tem Visão Geral nem o grupo *Unidade*. Abrir `/gestao/visao-geral` à mão: a mesma
   recusa de antes.
5. Entrar pela presidência de uma comissão: a barra tem Processos Seletivos e Minhas Etapas.
6. A 375 px (`resize_window` preset mobile): a barra começa recolhida; "Seções" a abre, por toque e
   por Enter; Tab entra nos itens; nenhuma rolagem horizontal.
7. Esc fecha a barra aberta; tocar fora dela também.
8. Só pelo teclado, na tela larga: o primeiro Tab mostra "Pular para o conteúdo", que leva o foco
   ao conteúdo; sem ele, a ordem é marca, seções, pessoa e Sair, caminho, Trocar identidade.

## Inventário

Com o mesmo ambiente, a partir de `backend/`:

```bash
AVISO=c1841d6c-924b-41a8-8d9a-99a17aacb900 uv run --with playwright --with pillow python ../doc/inventario-visual-da-gestao-2026-10-16/capturar.py <pasta-de-saída>
```

Comparar o `resultados.json` da saída com o da linha de base, tela a tela: status, `scrollWidth`
contra `clientWidth` a 375 e a 1280.
