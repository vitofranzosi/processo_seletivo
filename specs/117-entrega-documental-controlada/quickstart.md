# Quickstart: Entrega documental controlada

Roteiro da demonstração no navegador, para depois da implementação. Os dados são fictícios, e os
cenários são os do pedido.

## Preparação

```bash
cd backend && make preparar
```

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8017
```

- Use um **banco próprio**. O cenário vem das fixtures da `115` (moldes 72, 146 e 89), estendidas por
  `montar_cenario_da_formalizacao` (T032).
- **Atores** (pelo seletor de identidade):
  - **Ana**, presidência da comissão;
  - **Gil**, administrador de acessos da unidade;
  - **Rui**, Registro Acadêmico, fora da comissão;
  - **Bia**, Coordenação UAB;
  - **Caio**, auditor;
  - **Duda**, de outra unidade.

## Cenário A — Matrícula, 40 aptos (molde 72/2026)

O Edital pede:

- **na inscrição**: certificado e títulos;
- **na convocação**: identidade, CPF, histórico e comprovação de renda.

São 40 aceites, 6 indeferimentos e 4 sem resposta.

1. Ana abre *Documentos para a formalização* na condução. A lista vem sem marcação. Ela marca
   identidade, CPF, histórico e certificado.
2. Ana marca a renda, e a tela avisa que é documento de modalidade de reserva. Marca os títulos, e a
   tela avisa que é documento da inscrição. Ela desmarca os dois.
3. Ana tenta gravar sem motivo, e a gravação é recusada. Com motivo, grava. O histórico mostra a
   versão.
4. Gil concede o papel Formalização a Rui, em **Acessos**, e o designa para o 72/2026, sem restrição.
5. Rui abre **Formalização** na barra e depois o Edital. Vê:
   - 40 pessoas;
   - 4 documentos cada;
   - o certificado marcado *"enviado na inscrição; sem conferência na convocação"*;
   - nenhuma renda e nenhum título.
6. Rui marca *Selecionar todos* e pede *Verificar e exportar*. A tela mostra primeiro *"Pacote
   completo: 40 pessoas"*, depois o alcance, os documentos e o tamanho. Ele clica *Baixar pacote (40
   pessoas)*.
7. Abra o ZIP: 40 pastas, 4 PDFs cada e `manifesto.csv`, com *completo* no cabeçalho.
8. Confira com `sha256sum`:
   - três arquivos contra o manifesto;
   - o ZIP contra o histórico da página.
9. Liste o temporário do processo e a raiz privada: nenhum arquivo novo.

## Cenário B — Bolsista (molde 146/2025)

1. Ana define a Ficha/Termo e o certificado. Gil designa Bia, só no Perfil de tutor.
2. Bia visualiza a Ficha e baixa o certificado, que sai como `‹protocolo›-certificado.pdf`.
3. Caio, na trilha do Edital, vê *Documento visualizado* e *Download individual disponibilizado*. Não
   tem botão para abrir.
4. Nenhuma tela diz *bolsa concedida*, *obtido* ou *recebido*.

## Cenário C — Finalidades diferentes

Numa pasta do Cenário A, confira a **ausência** de:

- títulos (classificação);
- renda (reserva).

No molde 89, o certificado da inscrição aproveitado por referência aparece **uma vez**.

## Cenário D — Desfecho sucedido

1. Ana corrige o aceite de uma pessoa já exportada para indeferimento.
2. Rui recarrega a página: a pessoa saiu.
3. A nova verificação de *Selecionar todos* tem 39 pessoas.
4. O histórico continua mostrando a exportação anterior, com 40.

## Cenário E — Controle de acesso

Repita por URL direta e por POST forjado, copiados da sessão de Rui:

| Quem | Tentativa | Esperado |
|---|---|---|
| Bia (Perfil de tutor) | documento de aluno | 404 |
| Bia | POST de verificação com id de aluno na seleção | 404, nada lido |
| Rui, designação revogada por Gil | a página | 404 |
| Rui, papel revogado e designação vigente | a página | 403, nomeando o papel |
| Ana | a página da formalização / designar | 403 / 403 |
| Gil | designar a si mesmo | recusa de autodesignação |
| Gil | a página da formalização | 403 |
| Duda | qualquer URL | 404 |
| Caio | exportar | 403 |

## Cenário F — Falha operacional

Num Edital de 5 aptos:

1. Pelo shell, apague o arquivo de uma apresentação e acrescente um byte ao de outra.
2. Abrir o arquivo apagado na página de documentos da convocação dava erro 500 antes da feature.
   Agora a resposta é *"Arquivo indisponível"*, e a trilha registra.
3. Rui seleciona as 5 e verifica. **Antes de qualquer download**, a tela diz *"Pacote parcial: 3 de 5
   pessoas"* e nomeia as 2, com *arquivo indisponível* e *arquivo diferente do conferido*. O botão diz
   *Baixar pacote parcial (3 pessoas)*.
4. Rui baixa `…-parcial.zip`, com 3 pastas. O manifesto traz *3 de 5* no cabeçalho e as linhas das 2
   excluídas, com o motivo. O histórico repete. A trilha tem `INTEGRIDADE`.
5. **Verificação defasada**: verifique de novo, corrija o arquivo apagado pelo shell e clique em
   baixar. O download é recusado, nada é servido, e a tela oferece verificar de novo.
6. **Pessoa única com falha**: *Exportar esta pessoa* numa das 2 devolve uma página com o motivo, e
   não um ZIP. Não há registro de exportação.
7. **Limite**: configurado em 1 MB, a verificação é recusada antes de ler, mostrando o tamanho por
   pessoa.
8. **Concorrência**: duas abas de Rui verificando ao mesmo tempo. A segunda recebe *"Uma exportação
   sua já está em andamento"*.
9. **Exceção**: com a falha injetada pela fixture de teste, a tela diz *"A exportação não foi
   concluída. Nada foi baixado nem registrado."*. O histórico não muda, e a trilha tem *exportação
   interrompida*.

**Validação de capacidade (na VM, pela TI, e não aqui).** Siga a §5.4 do diagnóstico, com um pacote no
limite configurado. O limite de produção é o que a medição sustentar.

## Capturas

Capture a 1280 px e a 375 px:

- a definição, com os avisos e o histórico;
- a designação em Acessos;
- a página do Edital;
- a verificação completa e a parcial;
- o histórico;
- a recusa de arquivo indisponível.
