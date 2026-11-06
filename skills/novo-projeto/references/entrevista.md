# A entrevista

Quatro rodadas curtas, nesta ordem. A ordem não é arbitrária: a rodada 2 depende
de saber o que o produto é, e a 4 depende de saber o que já foi decidido nas
outras três.

Conduza em **português do Brasil**, uma rodada por vez, esperando a resposta
antes de seguir. Chegue com palpite pronto — "pelo nome e pelo que você falou,
imagino que seja X, rodando em Y; confere?" custa um "sim" e economiza um
parágrafo digitado. Onde as respostas forem enumeráveis, use `AskUserQuestion`
com uma recomendação marcada; onde a resposta for uma explicação, texto livre.

**O que você já sabe e não deve perguntar** (padrões da casa — confirme só se
algo na conversa contradisser):

- Tudo em português do Brasil: documentos, commits, interface, mensagem de erro.
- O usuário testa e aprova cada bloco manualmente; não se empilha bloco sem
  checkpoint.
- Commits em pt-BR, `tipo: resumo` ou `Bloco N (área): resumo`, corpo com o que
  mudou e por quê, nunca `--amend`.
- Quem decide produto é o usuário; a resposta certa é uma recomendação, não um
  cardápio.
- O que só ele pode fazer (painel de terceiro, credencial, loja) vira passo a
  passo numerado e curto.

---

## Rodada 1 — o que é

O material daqui vira o "O que é" do CLAUDE.md e as seções 1 e 2 do PRD.

1. **Em duas frases: o que este projeto faz, e para quem?** Peça o problema
   concreto, não a categoria. "ferramenta de gestão" não diz nada; "a escala do
   mês vive numa planilha desatualizada e todo mês alguém aparece no plantão
   errado" diz tudo, e é dessa frase que sai toda decisão de escopo depois.
2. **Quem usa, e o que cada um faz lá?** Duas ou três personas bastam. Se houver
   papéis com poderes diferentes (quem administra, quem opera no dia a dia, quem
   só consulta), isso é modelo de autorização e precisa aparecer no PRD.
3. **O que ele deliberadamente NÃO vai fazer, e por quê?** A pergunta mais
   valiosa da entrevista. Todo projeto tem um vizinho óbvio que ele não é, e
   quem não escreve isso reimplementa o vizinho aos poucos. Se não vier resposta
   pronta, ofereça a sua ("imagino que não seja um app de delivery, porque…") e
   deixe corrigir.
4. **É produto comercial, ferramenta interna ou experimento?** Muda o peso do
   PRD: produto comercial ganha planos, preço e critério de aceite por fase;
   experimento ganha um PRD de uma página e mais nada.
5. **Existe repositório irmão ou sistema do qual ele depende?** Se sim, qual é o
   contrato entre os dois e o que quebra quando um muda sozinho. O caso
   perigoso é o que não quebra no mesmo commit: um lado muda, o outro só falha
   depois, na mão de quem está usando.

## Rodada 2 — stack e ambiente

Vira a seção "Comandos" e parte da "Arquitetura" do CLAUDE.md, mais o
`.gitignore` e a escolha dos arquivos de `rules/`.

1. **Em que ambiente isto vai ser desenvolvido?** Pergunta de opções, e ela vem
   cedo porque decide quais armadilhas entram nos documentos:
   - **Windows + Docker Desktop** — o caso com mais pegadinhas próprias
     (evento de filesystem não atravessa bind mount, container que não recria ao
     mudar `.env`, dependência instalada dentro do container). Elas viram seção
     no `workflow.md`.
   - **Windows, sem Docker** — caminho com `\`, PowerShell, fim de linha.
   - **Outro** (macOS, Linux, WSL, remoto): peça para descrever em uma linha e
     escreva o que for verdade dali. **Não copie as armadilhas do Windows para um
     ambiente que não é Windows** — aviso que não se aplica ensina a ignorar
     avisos, e a partir daí os que se aplicam também passam batido.
2. **Linguagem, framework e banco.** Havendo dúvida, recomende com base no que
   já roda na máquina (o que os outros projetos usam) e siga — escolha de stack
   não é para ficar em aberto no fim da entrevista.
3. **Como se roda em dev?** O comando literal. Docker Compose, `npm start`,
   `uv run`, o que for.
4. **Como se valida um bloco?** Teste, build, os dois. Este é o comando que vai
   parar no ciclo de trabalho do `workflow.md`, então precisa ser o comando de
   verdade — "roda os testes" não serve, `cd backend && uv run pytest` serve.
5. **Serviços de terceiro** (pagamento, e-mail, IA, storage, push): quais, e o
   que acontece quando cada um está mal configurado. A resposta dessa segunda
   metade vira armadilha documentada, e é o que evita a falha silenciosa.
6. **Onde vai rodar em produção?** Servidor próprio, PaaS, loja de aplicativos,
   nada ainda. "Nada ainda" é resposta legítima e vira bloco no TASKS.md.
7. **Em que áreas o código se divide, e em que pasta mora cada uma?** A primeira
   metade decide quais arquivos entram em `rules/` — um por área com regras
   próprias, nunca um por pasta. A segunda vira o `paths:` de cada um, que é o
   que faz a regra só carregar quando se mexe naquela área. Chegue com o palpite
   do layout padrão do stack (`stacks.md`): "backend em `backend/`, frontend em
   `frontend/`, confere?". Área sem pasta (operar um painel, um runbook) não é
   regra com `paths:` — é candidata a skill de projeto, e só nasce quando houver
   um procedimento de verdade para escrever.

## Rodada 3 — regras e riscos

Vira `rules/*.md`, a seção "Armadilhas" do CLAUDE.md e as primeiras entradas do
MEMORY.md.

1. **Que convenções já são inegociáveis para você aqui?** Nomenclatura, idioma
   da interface, estilo, o que nunca pode ser feito. Ele costuma ter opinião
   formada; capture com o motivo junto.
2. **O que já te mordeu em projeto parecido?** Versão travada, incompatibilidade
   de Windows, comportamento de API de terceiro. Cada resposta é uma entrada de
   MEMORY.md que economiza uma tarde.
3. **O que é segredo aqui, e onde ele mora?** Chave, token, credencial. A regra
   de que segredo não vai para o log nem para o repositório é padrão da casa,
   mas *quais* segredos existem é específico do projeto.
4. **Que decisão você já tomou e não quer rediscutir?** Vai para o MEMORY.md
   como decisão datada. É o que impede o Claude de propor, três semanas depois,
   exatamente o que já foi descartado.

## Rodada 4 — o plano

Vira o TASKS.md e a seção de fases do PRD.

1. **Qual é a primeira versão que já serve para alguma coisa?** Não é o produto
   completo; é o menor recorte que se pode olhar e julgar.
2. **Que blocos separam o zero disso?** Ajude a quebrar: um bloco é uma tela,
   um grupo de endpoints, uma integração — algo que se implementa, se valida e
   se testa numa sessão. Bloco que não cabe numa sessão é dois blocos.
3. **Como se sabe que um bloco está pronto?** Critério verificável por bloco.
   Sem isso, TASKS.md vira lista de desejos.
4. **O que depende só de você** (arte, conta em serviço de terceiro, documento,
   credencial)? Entra como pendência nominal — nos dois projetos existentes, é
   sempre isso que vira caminho crítico e sempre aparece tarde demais.

---

## Versão curta

Quando o usuário cortar a entrevista, pergunte só estas quatro e escreva o que
der:

1. O que faz e para quem, em duas frases.
2. Stack, comando para rodar e comando para validar.
3. O que deliberadamente não faz.
4. Quais são os três primeiros blocos.

Com isso saem CLAUDE.md, workflow.md, TASKS.md e um MEMORY.md com as decisões
que acabaram de ser tomadas. O PRD sai em versão de uma página, com as lacunas
registradas como tarefa — **nunca** como cabeçalho vazio. Diga, em uma linha, o
que ficou de fora e onde está anotado.
