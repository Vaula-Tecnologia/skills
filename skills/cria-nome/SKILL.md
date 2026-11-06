---
name: cria-nome
description: Cria nomes de produto, empresa ou serviço com domínio .com.br livre. Gera candidatos em ondas de variações (a palavra do produto e suas flexões, verbos, metáforas, expressões curtas, nomes inventados), confere cada onda no registro.br e entrega uma lista curta com o motivo e o risco de cada nome. Use sempre que o usuário pedir sugestões de nome, quiser batizar ou rebatizar algo, disser que o nome que queria "já tem dono" ou "não está disponível no registro.br", pedir variações de um nome, ou quiser um nome com .com.br livre, mesmo que não fale em domínio. A busca de marca no INPI dos finalistas é da skill busca-marca.
---

# Cria nome

Acha um nome bom cujo `.com.br` esteja livre. O que pesa aqui é o volume:
quase toda palavra curta e óbvia do português já está registrada. Num caso real
(o ViuSumiu, em 2026-11-06), de uns 120 nomes consultados, lacre, selo, cifra,
cripta, psiu, xiu, fugaz, relance e sésamo estavam tomados. As expressões
escritas juntas, como viusumiu, leusumiu e derelance, estavam livres. Por isso
a skill gera muitos candidatos, confere em lote e segue para onde há nome livre
e bom. O caso completo, onda por onda, está em `references/exemplo-viusumiu.md`.

Domínio livre não quer dizer marca livre. Esta skill escolhe o nome e confere o
domínio. O risco no INPI é da `busca-marca`, que roda depois, só nos finalistas.

## 1. O briefing

Antes de gerar, tenha estas respostas. Deduza da conversa o que puder e
pergunte o resto numa rodada só:

- **O que o produto faz e para quem**, numa frase. O nome bom conta a promessa
  ou cria uma imagem dela.
- **O tom**: sério e corporativo, leve, bem-humorado. E o que evitar.
- **As restrições**: só `.com.br`? Pode ser inventado? Tamanho máximo? Nome em
  português ou também em inglês?
- **O nome que já tinham**, se houver. Ele é o ponto de partida das variações.
- **A ligação com uma marca-mãe**: o produto vai ter casa própria ou fica sob a
  marca da empresa? Um nome que amarra o produto à empresa ("vaulink", da
  Vaula) atrapalha quem quer que ele cresça sozinho.

Restrição dita é restrição. Se o usuário pediu só `.com.br`, não proponha
`.app.br` nem `.com`, nem como alternativa: no caso real, o usuário corrigiu
isso no meio da busca.

**Se o nome que ele queria já tem dono**, abra o site desse domínio antes de
gerar variações. Pode ser uma página parada, ou um produto do mesmo ramo. No
teste da "Fluxa", o `fluxa.com.br` era um sistema de gestão no ar. Aí qualquer
"Fluxa + complemento" herda o conflito de marca e manda cliente para o
concorrente, e as variações devem se afastar do nome, não só ganhar um
sufixo.

## 2. As ondas

Uma onda é um lote de 20 a 40 nomes de uma família, conferido numa chamada só
do script. Comece pelas famílias baratas de descartar e vá para onde há nome
livre. As famílias:

1. **A palavra do produto e o nome antigo**: flexões, conjugações, derivados
   (sigilo: sigilar, sigilou, sigiloso). Quase sempre tomados, mas mostram o
   terreno.
2. **Verbos da ação do produto**, no infinitivo e no passado (selar, cifrar,
   esvai, esvaiu). Verbo vira chamada de botão ("Selar senha") e soa como
   produto.
3. **Metáforas e imagens** do que o produto faz sentir (relance, lampejo,
   fumaça, sussurro).
4. **Expressões curtas**, de duas ou três palavras escritas juntas, que contam
   o produto (viu sumiu, leu apagou, numa olhada). É a família que mais tem
   domínio livre, e a que mais gruda na cabeça.
5. **Inventados**: corte de palavra, fusão de duas, raiz latina (sigillum),
   onomatopeia (psiu), troca de letra (k por c, y por i). Use pouco a troca de
   letra: ela falha no teste do telefone.
6. **Vizinhos do finalista**: quando um nome bom aparecer livre, confira as
   variações dele (viusumiu: leusumiu, olhousumiu, viuesumiu). Isso mostra se
   a família é forte e ajuda a escolher a melhor grafia.

Escreva o domínio como o registro.br aceita: minúsculas, sem acento, sem
espaço (ç vira c, ã vira a, "Sésamo" vira `sesamo`). Diga quando o domínio
perde o acento do nome. Hífen é permitido, mas as pessoas esquecem; evite.

Pare quando houver três nomes fortes livres ou por volta de 150 consultas. O
caso real precisou de 4 ondas e uns 120 nomes. Mais que isso, revise o briefing
com o usuário antes de seguir.

## 3. A consulta

O script de domínio é o da `busca-marca`, na pasta vizinha desta skill:

```sh
python <pasta desta skill>/../busca-marca/scripts/dominio.py selar esvai viusumiu leusumiu --markdown
python <pasta desta skill>/../busca-marca/scripts/dominio.py selar esvai --json
```

O padrão é `.com.br`. Com `--markdown`, cada onda sai como tabela (Domínio,
Situação por extenso, Observação com a data em que o registrado expira): guarde
cada uma, porque é a lista completa do relatório. O script faz uma pausa de
1,2 s entre pedidos (30 nomes levam uns 40 s), porque o registro.br é um
serviço público. Rode uma onda por vez, nunca em paralelo nem em laço. Se a
pasta vizinha não existir (a skill foi copiada sem a `busca-marca`), consulte
`https://registro.br/v2/ajax/avail/raw/<nome>.com.br` um nome por vez, com a
mesma pausa, e leia o campo `status`.

Como ler o `status`:

- **0**: livre.
- **1**: livre, mas outra pessoa também pediu (tickets concorrentes). Proponha
  avisando do risco.
- **2**: registrado.
- **3**: indisponível (reservado ou proibido).
- **5 a 7**: em processo de liberação. Não está livre agora; não proponha como
  livre.
- **8**: o registro.br limitou as consultas. O script espera e tenta de novo
  sozinho; se ainda sair "não consultado (limite)", espere um minuto e
  consulte só esses nomes. Nunca conte como livre.
- **Erro ou status desconhecido**: diga qual foi e não conclua nada sobre o
  nome.

## 4. O filtro

Livre não basta. Passe cada nome livre por estes testes antes de propor:

- **Teste do telefone**: dá para dizer o nome em voz alta e a outra pessoa
  digitar certo de primeira? Letra dobrada ("xiuu"), k no lugar de c
  ("tranka") e grafia em dúvida ("esvai" ou "isvai") falham.
- **Leitura junta**: escrita sem espaço, a expressão ainda se lê?
  "derelance" se perde; "viusumiu" se lê.
- **Distintividade**: palavra comum que descreve o serviço ("sumir",
  "senhasegura") é fraca como marca. O INPI recusa o sinal só descritivo (art.
  124, VI, da Lei 9.279/96). Palavra que só sugere ("Selar") costuma passar.
- **Tamanho**: quanto mais curto, melhor. Acima de 12 letras, precisa de um
  bom motivo.
- **Sentido duplo ou ruim** em português, e em espanhol ou inglês se o produto
  vai para fora.
- **Parecido com marca famosa** do mesmo ramo. A busca completa é da
  `busca-marca`; aqui, só aponte o que salta aos olhos.
- **Empresa com o mesmo nome no mesmo ramo**: uma busca na web por finalista
  ("<nome> <ramo>"). No teste da contabilidade, ela achou uma "Egide
  Assessoria Contábil" para um nome cujo domínio estava livre.

## 5. O relatório

Comece pela resposta: quantos nomes consultou, em quantas ondas, e o padrão do
que estava tomado ("os curtos e óbvios estão quase todos registrados: ...").
Depois:

| Domínio | Por que funciona | Risco |
|---|---|---|
| **nome.com.br** | o que o nome conta e por que vende, em uma ou duas frases | o ponto fraco (grafia, distintividade, tom) |

- **Três finalistas** na tabela, do melhor para o pior.
- **"Também livres, mas piores"**: os outros bons livres, um por linha, com o
  motivo de terem ficado de fora.
- **A recomendação**: um nome, com a condição que a decide ("se o foco é
  vender para agências, Selar; se é ser lembrado, Viu Sumiu").
- **O próximo passo**: rodar a `busca-marca` nos finalistas antes de registrar
  o domínio ou investir no nome. Ofereça fazer isso. Lembre também o @ nas
  redes sociais e, se for nome de empresa, a consulta de viabilidade do nome
  na Junta Comercial do estado.
- **Os limites**, em uma linha: a disponibilidade é a da hora da consulta e
  muda a qualquer momento; quem registra é o usuário, no registro.br, com o
  CPF ou o CNPJ.
- **A lista completa da busca**, por último: uma tabela por onda, com o nome
  da família no título ("Onda 2: verbos do serviço, 30 nomes, 9 livres"). Use
  as tabelas do `--markdown` e preencha a Observação dos livres: "finalista",
  "também livre, mas pior" ou o motivo de ter ficado de fora em poucas
  palavras ("difícil de soletrar", "descritivo demais"). Situação sempre por
  extenso: o usuário não sabe o que é "status 0", e um "dominio.com.br 0" solto
  não diz nada a ele.

Ponha a data e a hora da consulta, no fuso do usuário. Não registre domínio nem
compre nada: isso é do usuário.

## Quando algo der errado

- **Muitos "não consultado (limite)" ou erros seguidos no script**: o
  registro.br está limitando os pedidos, em geral porque outra busca roda do
  mesmo IP. Espere um minuto e rode uma onda menor. Nunca trate erro como
  "livre".
- **Tudo tomado em duas ondas**: troque de família. Expressões e inventados
  costumam ter mais domínio livre do que palavras do dicionário.
- **O usuário não gostou de nenhum finalista**: pergunte do que ele não gostou
  (tom, tamanho, sentido) e ajuste o briefing antes da próxima onda, em vez de
  gerar mais do mesmo.
