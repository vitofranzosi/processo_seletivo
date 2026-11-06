# Quickstart: verificar a 126

## 1. Suíte

```bash
cd backend && DB_NAME=ps_spec126 make lint check test-pg
```

Os testes da feature isolados:

```bash
cd backend && PYTEST_ADDOPTS="tests/interface/test_orientacao_p0.py tests/unit/interface/test_conferencia_da_ordem.py tests/integration/relatorio/test_convocacao_sem_comunicacao.py" DB_NAME=ps_spec126 make test-pg PYTEST_WORKERS=0
```

## 2. No navegador, sobre o Edital 35 pseudonimizado

Pré-requisito: o container `ps-sorteio-35` (porta 55435, usuário `postgres`) com o banco
`processo_seletivo_guia`.

1. Clonar e migrar um banco descartável:

   ```bash
   PGPASSWORD=estudo psql -h localhost -p 55435 -U postgres -c "create database ps_spec126 template processo_seletivo_guia"
   ```

   e `manage.py migrate` com `DB_HOST=localhost DB_PORT=55435 DB_NAME=ps_spec126` e o superusuário.
2. Subir o `runserver` da worktree contra esse banco, com `INTERFACE_SELETOR_IDENTIDADE=true`.
3. Entrar pelo seletor de identidade como quem conduz (botão `identidade_sugerida`, esperar a navegação).
4. Conferir, antes (na `main`) e depois (nesta branch):

| Tela | Esperado depois |
|---|---|
| Condução do marco do Polo Vitória | *Não se aplica* nas células, "Nada a conduzir neste marco", nenhum gesto (SC-1212) |
| Convocação do Polo Vitória, ampla | não se aplica; sem "Ir para a apuração" nem faixa seguinte (SC-1213) |
| Confirmação de Encerrar do 35 | "sem comunicação enviada", e não "aguardando resposta" (SC-1214) |
| Sorteio do 35 Cefor | o aviso de congelamento não é a primeira frase dos recortes (SC-1215) |
| Corte de um recorte com ordem, depois de emitir | "Corte emitido para …", sucessão recolhida (SC-1210, SC-1211) |

5. A confirmação da ordem por pontuação sem resultado (SC-1216) não tem caso no clone do 35; ela é
   verificada pela suíte (`test_orientacao_p0.py`) e por captura de um cenário montado pelos helpers dos
   testes, se houver tempo.

O banco descartável pode ser apagado ao fim: `drop database ps_spec126`.
