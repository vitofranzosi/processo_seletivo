# Rastreabilidade — 073

Caminhos de teste relativos a `backend/tests/`. "Guia" é `doc/implantacao-em-producao-ubuntu.md`.
"Humana" é a validação em homologação que o agente não faz ([quickstart.md](quickstart.md), B e C).

| Requisito | Onde é provado |
|---|---|
| FR-1650 | Guia, §10.4, na ordem do contrato; `test_guia_configurar_verificar.py` (a seção existe e o §16.5 remete a ela) |
| FR-1651 | `test_guia_configurar_verificar.py` (toda variável dos blocos é lida pelas settings; a senha só como marcador) |
| FR-1652 | `test_guia_configurar_verificar.py` (a leitura com segredos plantados não os imprime; a primeira linha é o módulo de settings; a ressalva do processo de diagnóstico está no texto) |
| FR-1653 | `test_guia_configurar_verificar.py` (a conexão contra o SMTP falso que aceita não recebe `MAIL FROM`; o Ollama falso não recebe `/api/chat`; a ressalva da versão está no texto) |
| FR-1654, FR-1655 | `test_guia_configurar_verificar.py` (cada última linha da tabela é a que o exemplo produz; nenhuma linha de tempo esgotado tem causa única; "465" não aparece como causa) |
| FR-1656 | Guia, §10.4, passo 7; `test_guia_configurar_verificar.py` (os dois instantes estão no passo) |
| FR-1657 | `test_guia_configurar_verificar.py` (a §10.4 não remete a `specs/` nem a arquivo de código) |
| FR-1658 | `README.md`, § Produção; revisão |
| FR-1660 | `test_configuracao_producao.py` (`EMAIL_HOST` ausente e só com espaços recusam) |
| FR-1661 | `unit/duvidas/test_verificar_servico.py` (desconhecido × vazio) |
| SC-620 | **Humana** — quickstart B |
| SC-621 | `test_guia_configurar_verificar.py` (segredos plantados, zero ocorrências) |
| SC-622 | `test_guia_configurar_verificar.py` (o SMTP falso não recebe `MAIL FROM`; o Ollama falso não recebe `/api/chat`) |
| SC-623 | `test_guia_configurar_verificar.py` (sintomas reproduzíveis localmente); **Humana** — quickstart B e C, para os demais |
| SC-624 | `test_configuracao_producao.py`; `unit/duvidas/test_verificar_servico.py` |
