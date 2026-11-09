# Como ler o resultado do INPI

Guia para transformar a lista do pePI numa avaliação de risco. É uma leitura
preliminar, de quem conhece o produto, não um parecer: diga isso no relatório.

## O que o INPI compara

Marca é sinal + mercado. O examinador olha três coisas juntas:

1. **O sinal**: grafia, som e ideia. "Viu Sumiu" e "VIU" dividem uma palavra;
   "Selar" e "Selaria" dividem um radical, mas não a ideia.
2. **A classe de Nice e a especificação**: a mesma palavra em classes sem
   afinidade convive (o "SELAR" da DuPont em química não atrapalha um "Selar"
   de software). A especificação, na ficha do processo, diz o que a classe
   cobre de fato: duas marcas na classe 42 podem não ter nada em comum, ou ter
   tudo (a "TECNOLOGIA VIU" lista "segurança bancária por meio de senha"
   e "SaaS"; isso muda o risco de um produto de senhas).
3. **A situação**: pedido pendente conta (vale a data de depósito); marca
   extinta, arquivada ou nula não bloqueia mais; indeferida pode ainda estar no
   prazo de recurso.

## Os incisos da Lei 9.279/96 que mais aparecem

- **Art. 124, XIX**: não se registra "reprodução ou imitação, no todo ou em
  parte, ainda que com acréscimo, de marca alheia registrada, para distinguir
  ou certificar produto ou serviço idêntico, semelhante ou afim, suscetível de
  causar confusão ou associação". É o motivo do risco quando a nossa marca
  contém, inteira, a parte distintiva de uma marca viva da mesma classe.
  Palavras genéricas da marca alheia ("Tecnologia", "Soluções", "Brasil")
  não contam como parte distintiva.
- **Art. 124, VI**: sinal genérico, comum ou simplesmente descritivo do
  serviço não se registra sozinho ("Senha Segura" para um cofre de senhas).
  Palavra comum que só sugere ("Selar") costuma passar.
- **Art. 125**: marca de alto renome é protegida em todas as classes. O pePI
  a lista no topo da primeira página, sem número de processo e com a situação
  "Alto Renome" (a Havaianas na busca "vai", 2026-11-09). Igual ao nome ou
  contida nele: risco alto, em qualquer classe, e a classe do produto não a
  afasta. Parecida no som ou na ideia: no mínimo risco médio. Diga no
  relatório, citando o artigo.

## Classes que importam para software

- **9**: software e aplicativo baixável.
- **42**: SaaS, desenvolvimento, hospedagem, segurança da informação.
- **35**: publicidade, gestão de negócios, marketplace.
- **38**: telecomunicações e envio de mensagens.
- **45**: serviços jurídicos e de segurança (inclusive alguns de identidade).

Para outro ramo, pergunte ao usuário o que o produto faz e escolha as classes
pela lista de Nice; na dúvida, rode sem `--classe` e leia as classes que
aparecem.

## Estratégia de busca

1. A marca inteira, radical, sem classe: acha o igual e as que a contêm. A
   busca radical ignora espaços ("esvai" acha "Inglês vai"), o que cobre a
   grafia separada, mas traz ruído.
2. A grafia junta e as variantes óbvias ("viusumiu", "viu e sumiu").
3. Cada palavra distintiva sozinha, radical, nas classes do produto. É aqui
   que aparece o risco do art. 124, XIX.
4. **O radical da sílaba tônica ou final**, nas classes do produto, e a marca
   **com uma letra a menos ou com hífen**. Marca de uma palavra só esconde o
   conflito aqui: "Esvai" não tem nenhuma marca igual, mas "vai" na classe 09
   leva a "E-vai", do Banco do Brasil. Ela difere por uma letra, tem a mesma
   tônica e está viva nas classes 09 e 42.
5. Variantes de grafia e som que a busca radical não pega (k/c, s/z/ç, letra
   dobrada, y/i, ph/f), quando a marca tiver alguma.
6. Ficha (`detalhe`) de cada marca viva que pareça conflitar, para ler a
   especificação antes de dar o risco.

Classe sempre com dois dígitos no pePI ("09", não "9"). O script completa
sozinho, mas na busca à mão no site o "9" acha só parte da classe.

## Escala de risco

- **Alto**: marca viva igual ou quase igual (grafia ou som) na mesma classe ou
  em classe afim, com especificação que cobre o produto.
- **Médio**: marca viva na mesma classe que contém a parte distintiva da nossa
  (art. 124, XIX, "com acréscimo"), ou a mesma palavra num serviço vizinho. O
  argumento a favor é o conjunto: expressão com sentido próprio pode passar,
  sem garantia, e o titular pode se opor.
- **Baixo**: só divide palavra comum, ou o conflito está em classe sem
  afinidade, ou as marcas parecidas estão mortas.

Suba um nível quando a especificação da marca alheia cobrir o mesmo serviço
(não só a mesma classe). Desça quando as especificações forem de mercados
claramente diferentes dentro da mesma classe.

**Diluição:** quando a palavra em comum é corriqueira e já convive em dezenas
de marcas vivas na mesma classe ("VAI", "TECH", "SMART"), o INPI tende a
aceitar mais uma, e o titular de cada uma tem pouca força para se opor. Nesse
caso, a palavra sozinha não sobe o risco mesmo com especificação igual. O que
pesa é a marca que fica **perto do conjunto** da nossa: grafia e som quase
iguais, como E-vai e Esvai. Diga no relatório quando a diluição for o motivo
de rebaixar.

## Limites que o relatório deve dizer

- Busca radical não é fonética, nem pega marca figurativa sem texto.
- O pePI mostra o que já foi publicado: pedido depositado nos últimos dias
  pode ainda não aparecer.
- Antes de investir na marca (domínio caro, material, registro), vale a busca
  de anterioridade de um advogado de marcas.
