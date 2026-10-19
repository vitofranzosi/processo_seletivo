# Minuta à TI — autenticação e integração institucional

**NÃO ENVIADA.** Preparada em 16/10/2026; remetente, destinatário nominal e prazo aguardam definição.
Referências: DEC-01, DEC-02; GO-01, GO-02, GO-03, GO-05 e GO-22 da auditoria.

Assunto proposto: definição da integração de identidade e requisitos de homologação do Sistema de
Processos Seletivos do Cefor.

Solicitamos orientação sobre a solução institucional suportada para autenticar servidores no
sistema. O produto é local, sem candidatos reais conforme premissa registrada em 14/10; não se
solicita ativação de produção nesta minuta. O usuário indicou LDAP em 28/08, sujeito à confirmação
da TI. O seletor de identidade de desenvolvimento não é solução de produção.

1. A solução suportada é LDAP direto, autenticação por proxy com identidade remota, SSO ou outra?
2. Quais identificador estável, atributos, grupos e regras de desligamento são disponibilizados?
3. Como conceder, revisar e revogar os oito papéis atuais, com escopo por unidade e menor privilégio?
   Quem responde por essa concessão? Não presumir que grupo de diretório confere todo papel.
4. Quais controles de sessão, saída, expiração, autenticação adicional e auditoria são exigidos?
5. Quais ambientes, certificados, conectividade e interlocutores estarão disponíveis para homologação?
6. Caso o piloto seja aprovado, quem hospeda, empacota, atualiza, monitora e responde por incidentes,
   backup e restauração? Quais dependências e antecedência são necessárias?

Resposta esperada: solução recomendada e suportada, contrato de identidade sem segredos, responsáveis,
condições de teste e estimativa de prazo. Não enviar senhas, tokens ou certificados privados.
O resultado fundamentará especificação própria; esta consulta não autoriza implementação.

Aceite da consulta: resposta identificável da TI, com autoridade responsável e pontos ainda pendentes.
