# Minuta ao correio institucional — SMTP, disponibilidade e monitoramento

**NÃO ENVIADA.** Preparada em 16/10/2026; remetente, destinatário nominal e prazo aguardam definição.
Referências: DEC-05; GO-25 e GO-27; spec 073 e §25 do guia de implantação.

Assunto proposto: requisitos de envio transacional e homologação do acesso de candidatos.

O e-mail é o fator de acesso do candidato. Precisamos confirmar a infraestrutura institucional e
seus limites antes de definir implantação. A 073 foi integrada, mas sua validação operacional com
pessoa da TI permanece pendente.

1. Qual serviço, porta, modo de segurança (STARTTLS ou TLS implícito), requisitos de autenticação
   e restrições de rede são suportados? Não presumir suporte da aplicação a todas as opções.
2. Qual remetente institucional, domínio, SPF/DKIM/DMARC e política de resposta devem ser usados?
3. Quais limites de taxa, tamanho, destinatários e volume em picos de inscrição são aplicáveis?
4. Quais disponibilidade, redundância, filas, tentativas, retorno de rejeição/bounce e monitoração
   serão oferecidos? Quem recebe alertas e qual procedimento de contingência é permitido?
5. Como disponibilizar homologação, contas/destinatários de teste e uma pessoa para seguir §10.4?
6. Que observabilidade permite distinguir falha de conexão, autenticação, rejeição e entrega sem
   expor endereços ou códigos de acesso em logs desnecessários?

Proposta de produto, ainda não aprovada: aviso uniforme de falha transitória para qualquer endereço,
sem confirmar se há cadastro. Não antecipar alteração da mensagem neutra atual.

Resposta esperada: parâmetros não secretos, responsáveis, limites e plano de homologação. Credenciais
devem ser fornecidas somente por canal seguro próprio, nunca anexadas à resposta desta minuta.
Nenhum teste de envio está autorizado por este documento.
