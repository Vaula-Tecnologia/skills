---
name: manter-docs
description: Compacta e reorganiza os documentos de trabalho de um repositório (CLAUDE.md, .claude/TASKS.md, MEMORY.md, rules/) quando passam do orçamento — movendo para .claude/historico/ em vez de apagar, pondo paths nas regras por área, separando o que entra em toda sessão do que só entra quando preciso — e migra projetos antigos do /novo-projeto para a forma atual, com o medidor de orçamento instalado. Use quando o hook medir-docs.sh avisar que um documento passou do orçamento, quando o usuário rodar /manter-docs, pedir para "compactar o TASKS/MEMORY", "limpar as tarefas concluídas", "o CLAUDE.md está grande demais", "o agente está se perdendo no projeto", "migrar a documentação para o padrão novo", ou quando um projeto com .claude/ cresceu e o agente começou a errar mais.
---

# Manter os documentos de trabalho

Os documentos do `/novo-projeto` valem pelo que o projeto aprendeu — e é
justamente isso que os faz crescer até ninguém mais lê-los. Esta skill devolve
cada documento ao tamanho em que ele é lido inteiro, **sem perder nada**: o que
sai dos documentos ativos vai para `.claude/historico/`, literal, onde o `grep`
ainda o encontra.

A forma de destino está descrita em
`<pasta desta skill>/../novo-projeto/references/documentos.md` (a novo-projeto
mora ao lado desta, em `~/.claude/skills/` ou no plugin) — leia a seção "O que
entra em contexto, e quando" e as de CLAUDE.md, rules, TASKS e MEMORY antes de
começar. Esta skill não repete aquela forma; ela diz como chegar nela a partir
de um projeto que já tem história.

## Os princípios que não se negociam

- **Mover, nunca apagar.** Toda linha que sai de um documento ativo existe
  depois em outro lugar de `.claude/` — no histórico, literal, ou na regra para
  onde foi. O `scripts/sem-perda.py` confere isso no fim; linha que ele acusar
  ou volta, ou entra no relatório com o motivo (era cópia de outra, era o
  cabeçalho antigo reescrito).
- **O conteúdo é do projeto, não seu.** Compactar não é editar opinião: decisão
  continua dizendo o que dizia. Resumir uma entrada é escrever a conclusão dela
  e mover o texto inteiro para o histórico — nunca reescrever o raciocínio.
- **Documentação não muda comportamento de produção**, mas o processo em volta
  pode: confira antes se algum CI, script ou build lê `.claude/` ou `CLAUDE.md`
  (`grep -rn "\.claude\|CLAUDE.md"` nos arquivos de CI, Dockerfiles e scripts).
  Em projeto com regra de testes seletivos, mudança em `.claude/` não deve
  disparar a suíte inteira; se dispara, diga.
- **Não atropelar outro agente.** Projeto ativo costuma ter outra sessão
  escrevendo no TASKS e no MEMORY agora mesmo.

## Passo 0 — terreno

1. `git status` e `git log -5 --format='%h %ci %s'` no repositório.
   - Mudança não commitada em CLAUDE.md, `.claude/` → pare e diga: é trabalho de
     outra sessão em andamento.
   - Commit em `.claude/` na última hora → há agente ativo. Trabalhe num
     **worktree** em branch própria (`git worktree add <pasta-irmã> -b
     docs/compacta-AAAA-MM-DD`), para não mexer na árvore de quem está
     trabalhando, e deixe o merge para o fim, combinado com o usuário.
2. Guarde a base: `git rev-parse HEAD`. É contra ela que o `sem-perda.py` confere.
3. Projeto em produção: o que você vai mexer é só documentação, mas leia o passo
   de CI acima antes de afirmar isso ao usuário.

## Passo 1 — medir

Rode o medidor do projeto (`sh .claude/hooks/medir-docs.sh`) ou, se ele ainda
não existir, o da skill:
`CLAUDE_PROJECT_DIR=<repo> sh <pasta desta skill>/../novo-projeto/assets/medir-docs.sh`.

Anote o **antes** para o relatório: linhas e KB de cada documento e o total que
entra em toda sessão (CLAUDE.md + regras sem `paths:`; tokens ≈ bytes ÷ 4).
Rode também `python scripts/conferir-paths.py <repo>` para ver quais regras já
têm `paths:`.

## Passo 2 — ler e classificar, antes de mover qualquer coisa

Leia cada documento inteiro (com `offset`/`limit` quando passar de 2.000
linhas) e decida o destino de cada pedaço pela tabela da seção "Tamanho dos
documentos" do `documentos.md`. Os casos que mais aparecem:

**TASKS.md**
- Bloco **aprovado** pelo usuário (diz "aprovado", ou foi aprovado em bloco
  posterior) → `historico/TASKS-AAAA-MM.md` pelo mês da aprovação (sem data de
  aprovação, o da conclusão), literal; em "Concluídos" fica uma linha.
- Bloco ✅ "aguardando aprovação" → **fica**: ainda é trabalho aberto.
- Dentro de bloco aberto, item `[x]` com narrativa de mais de três linhas → a
  narrativa vai literal para o histórico; fica a linha `[x]` com data e ponteiro.
- Seção de estado ("Onde paramos", "O que já está pronto") → vira o "Onde
  paramos" do CLAUDE.md (até 12 linhas); o texto antigo vai para o histórico.
- Cabeçalho que aponta para `git show <hash>:...` → o conteúdo daquele hash vai
  para `historico/` (`git show <hash>:.claude/TASKS.md >
  .claude/historico/TASKS-ate-AAAA-MM-DD.md`) e o ponteiro passa a ser o
  arquivo. Arquivo morto que só se abre sabendo o hash não é consultado.

**MEMORY.md**
- Reorganizar **por tema** (se ainda for cronológico), movendo as entradas
  inteiras, sem reescrever.
- Decisão superada (marcada como tal, ou contradita por decisão posterior) →
  `historico/MEMORY-superadas.md`, com o que a substituiu.
- Entrada de mais de ~8 linhas → texto inteiro em `historico/MEMORY-AAAA-MM.md`
  (mês da entrada); no MEMORY fica o título-conclusão, duas a cinco linhas do
  porquê e o ponteiro.
- Armadilha que só vale numa área → `rules/<área>.md`, junto da regra que ela
  explica. Armadilha sobre um terceiro operado por API → a skill de projeto
  daquele tema.

**CLAUDE.md** (orçamento 200 linhas)
- Parágrafo de estado → "Onde paramos (data)", reescrito, até 12 linhas.
- Ponto de arquitetura com mais de três linhas → `rules/dominios/<tema>.md` com
  `paths:` nos arquivos que o implementam; no CLAUDE.md fica uma linha e o link.
- Armadilha de uma área só → regra da área.

**rules/**
- Regra de área → ganha `paths:` com as pastas da área (confira com
  `git ls-files` que os padrões casam).
- Regra de tema sem pasta (operar Coolify, Cloudflare, um painel) → skill de
  projeto em `.claude/skills/<tema>/SKILL.md`, com `description` dizendo quando
  usar, **entre aspas duplas** (YAML sem aspas quebra com `: ` no meio, e a
  skill não carrega). As armadilhas do tema vão para
  `references/armadilhas.md` dela, e o SKILL.md manda procurar o sintoma lá
  antes de agir. Antes, confira se já não existe skill global do mesmo tema
  (`~/.claude/skills/`): o que for genérico já está lá; o que fica no projeto é
  só o que é deste projeto. **Repositório de operação** (infra, painéis) é quase
  todo assim: o agente opera por API, sem abrir arquivo do tema, e regra com
  `paths:` nunca carregaria. No infra-aeternis, sete temas viraram skill.
- Regra que **muda de lugar** e é linkada de fora (runbook, comentário de
  script, outro documento) → no caminho antigo fica um ponteiro de cinco
  linhas, com `paths:` nos arquivos do tema, dizendo para onde foi. O link
  antigo continua levando a algum lugar, e abrir um arquivo do tema lembra o
  agente de carregar a skill. Procure os links antes: `grep -rn
  "rules/<arquivo>" .` no repo inteiro, não só em `.claude/`.
- O que precisa ser sabido antes de abrir qualquer arquivo (produção, segredo,
  deploy, repositório irmão, quem pode autorizar o quê) → fica sem `paths:`,
  no `workflow.md`. Na dúvida entre "área" e "antes de tudo", pergunte: se o
  agente não souber disso e abrir o arquivo errado, o estrago acontece antes de
  a regra carregar? Se sim, fica sempre carregada.
- `workflow.md` sem as seções "Tamanho dos documentos" e "Duas memórias" →
  ganha as duas (texto no `documentos.md`); o ciclo troca "ler o TASKS.md" por
  "ler o Onde paramos e o bloco que vai atacar".

**Contradições.** Ao classificar, anote todo par de instruções que se
contradizem (regra que ainda manda o que uma decisão posterior superou, dois
números diferentes para a mesma coisa). Resolva pela decisão datada mais
recente; se não houver data que decida, pergunte ao usuário. Elas entram no
relatório — são os pontos em que o agente vinha escolhendo ao acaso.

**Memória automática.** Liste `~/.claude/projects/<pasta-do-projeto>/memory/`
(a pasta é o caminho do repo com `:`, `\` e `/` trocados por `-`, ex.
`D--Dev-atrio`). Fato do projeto que está lá (infra, API, armadilha do código)
é candidato a vir para o MEMORY ou para a regra da área. **Proponha; não apague
arquivo da memória automática sem o ok do usuário** — ela é dele.

Em **migração** (projeto que nunca passou por esta skill), mostre o plano ao
usuário em até 15 linhas antes de mover: o que vira histórico, quais regras
ganham `paths:`, o que vira skill de projeto, as contradições achadas. Em
**compactação de rotina** (o hook avisou e o projeto já está na forma nova),
siga direto.

## Passo 3 — mover

Ordem que evita perda: **primeiro escreva o destino, depois tire da origem.**

1. Crie os arquivos de `historico/` com o texto literal. Copiar trechos de um
   arquivo grande para outro é trabalho de **script em arquivo**, que lê a base
   por `git show <base>:<arquivo>` e nunca redigita texto que precisa ficar
   literal; você só escreve os resumos e as notas. Nada de heredoc, `python -`
   ou `python -c` multilinha: travam ou corrompem acento neste Windows. Antes
   de recortar por entrada, liste as linhas que não caem em entrada nenhuma: no
   infra-aeternis, um `printf '\n'` tinha virado quebra de linha de verdade no
   meio de duas armadilhas, e o recorte ingênuo perderia 16 linhas. Mapeie
   cada entrada para um destino e faça o script **afirmar** que todas têm um.
2. Crie as regras de domínio, as skills de projeto e os `paths:`.
3. Reescreva os documentos ativos.
4. Instale o medidor, se faltar: copie `<pasta desta skill>/../novo-projeto/assets/medir-docs.sh`
   para `.claude/hooks/` e crie (ou complete, sem apagar o que houver) o
   `.claude/settings.json` com o hook `SessionStart` do `documentos.md`.
   Confira que o JSON é válido, e que o `.gitattributes` tem `*.sh text
   eol=lf` (`git check-attr eol -- .claude/hooks/medir-docs.sh` tem de dizer
   `lf`): com `autocrlf=true` o script sai do checkout com CRLF e quebra.

**Quando o orçamento não fecha.** Trabalho aberto de verdade não se esconde no
histórico para o medidor calar. Bloco que parece velho (o próprio documento
mostra que o assunto andou depois) não se fecha sem evidência: vira um item
"reconferir contra o estado ao vivo", no topo do TASKS, citando a evidência. O
medidor continua avisando até alguém reconferir, e é para isso que ele existe.

## Passo 4 — conferir

Nada disto é opcional, e o resultado de cada um vai para o relatório:

- `python scripts/sem-perda.py <repo> <base>` → zero linhas sem destino, ou cada
  uma justificada.
- `python scripts/conferir-paths.py <repo>` → nenhum padrão que não casa com nada.
- `sh .claude/hooks/medir-docs.sh` → saída vazia, ou o aviso que sobrou
  explicado no relatório.
- Frontmatter YAML de toda skill e regra criada válido (`yaml.safe_load` no
  bloco entre os `---`).
- Links relativos em CLAUDE.md e `.claude/` apontando para arquivos que existem.
- Releia o CLAUDE.md novo do começo ao fim como se fosse a primeira sessão: dá
  para saber o que é o projeto, onde paramos e o que fazer agora sem abrir mais
  nada? Se não, falta alguma coisa no lugar errado.

## Passo 5 — commit e relatório

Commit próprio, só de documentação: `docs: compacta CLAUDE, TASKS, MEMORY e
rules` com o antes e o depois no corpo, mensagem escrita em arquivo e passada
com `git commit -F`. Sem push e sem merge no branch principal sem o usuário
dizer — se trabalhou em worktree, diga como integrar e se o branch principal
andou enquanto isso.

Se o branch principal ganhou commits em `.claude/` durante o trabalho, não faça
merge às cegas: veja o que entrou (`git diff <base>..main -- CLAUDE.md
.claude/`), ponha cada acréscimo no lugar certo da forma nova e rode o
`sem-perda.py` de novo contra o novo topo do principal.

Relatório curto:

- tabela antes → depois (linhas, KB e o total que entra em toda sessão);
- o que foi para onde, em uma linha por destino;
- contradições encontradas e como ficaram;
- linhas que o `sem-perda.py` acusou e o motivo de cada uma;
- propostas para a memória automática;
- o que falta o usuário fazer (merge, push, aprovar).

## Arquivos

- `scripts/sem-perda.py` — confere que toda linha da base existe em algum documento de agora.
- `scripts/conferir-paths.py` — lista regras cujo `paths:` não casa com arquivo versionado.
- O medidor e a forma dos documentos moram na skill `novo-projeto`
  (`assets/medir-docs.sh`, `references/documentos.md`): uma fonte só.
