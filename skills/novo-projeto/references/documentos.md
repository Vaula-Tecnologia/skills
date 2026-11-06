# Os documentos, um por um

Estrutura, tom e o erro que estraga cada arquivo. Escreva na ordem do SKILL.md
(PRD → CLAUDE → rules → TASKS → MEMORY → medidor → resto): cada um usa o anterior.

Vale para todos:

- **Português do Brasil**, sempre.
- **Datas absolutas** (`2026-08-13`), nunca "hoje", "ontem" ou "na semana
  passada" — o documento é lido meses depois.
- **Motivo junto da regra.** Uma linha que diz o que quebra vale por dez que
  mandam obedecer. Se você não conseguir escrever o motivo, desconfie da regra.
- **Nada de seção vazia nem `TODO`.** Falta vira tarefa no TASKS.md.
- **Cada documento tem orçamento**, e o número mora no `medir-docs.sh`. O
  orçamento não é meta de tamanho: é o ponto em que o documento para de ser
  lido inteiro ou começa a diluir o resto. Projeto novo nasce bem abaixo dele.
- **Estado se reescreve, registro se acrescenta.** O que descreve o presente
  ("Onde paramos", domínios) é reescrito; o que registra o passado vai para o
  histórico. Documento ativo que só recebe acréscimo é histórico disfarçado.
- Poucos negritos, e só onde a frase é a que não pode ser pulada. Documento
  todo em negrito não tem ênfase nenhuma.
- Evite `SEMPRE`/`NUNCA` em caixa alta como muleta. Onde couber, explique;
  guarde o imperativo duro para o que realmente não tem exceção (segredo,
  isolamento entre clientes, dado que não volta).

## O que entra em contexto, e quando

É isto que decide onde cada informação mora — não o assunto dela:

| Onde | Quando entra no contexto | O que vai lá |
|---|---|---|
| `CLAUDE.md` | toda sessão, inteiro | o que vale em qualquer tarefa: o que é, onde paramos, comandos, mapa |
| `rules/workflow.md` (sem `paths:`) | toda sessão, inteiro | processo, e o que precisa ser sabido **antes** de abrir qualquer arquivo: produção, segredo, deploy, repositório irmão |
| `rules/<área>.md` (com `paths:`) | quando o agente lê ou edita um arquivo da área | convenções e armadilhas daquela área |
| `rules/dominios/<tema>.md` (com `paths:`) | quando o agente lê ou edita um arquivo do tema | como um tema que cruza arquivos funciona hoje |
| `skills/<tema>/SKILL.md` | quando o assunto aparece (a descrição fica sempre visível) | procedimento sem pasta própria: operar API de terceiro, runbook |
| `TASKS.md`, `MEMORY.md`, `PRD.md` | quando o agente abre | trabalho aberto, decisões vigentes, requisitos |
| `historico/` | só por `grep` | o que já foi: blocos aprovados, decisões superadas, investigação |

Regra de `paths:` carrega quando o agente usa Read, Edit ou Write num arquivo
que casa (ou `cat`/`head` num arquivo só) — **não** com Grep nem Glob. Por isso o
que tem de estar na cabeça antes de qualquer leitura não pode depender de
`paths:`: vai para o `workflow.md` ou para o CLAUDE.md.

---

## `.claude/PRD.md`

O que o produto é, para quem, e como se sabe que ficou pronto. É o documento que
se consulta **antes de qualquer funcionalidade nova**, e o único que fala de
requisito em vez de código.

```markdown
# PRD — <Projeto>

> Requisitos e critérios de aceite. Status por tarefa fica no TASKS.md;
> decisões e armadilhas, no MEMORY.md — não duplicar.

## 1. Contexto e problema
## 2. Usuários e personas
## 3. Escopo  (o que é, e o que deliberadamente não é)
## 4. Arquitetura pretendida
## 5. Modelo de dados (essência)
## 6. Requisitos funcionais
## 7. Requisitos não funcionais
## 8. Fases e critérios de aceite
```

- Produto comercial ganha uma seção de **planos e preço** dentro do escopo, com
  a regra de o que cada plano libera. Ferramenta interna e experimento pulam
  essa seção — e se o PRD inteiro couber em uma página, que caiba.
- O modelo de dados é a **essência**: entidades, o que cada uma guarda e como se
  relacionam. Não é DDL, e vai ficar desatualizado se for.
- Critério de aceite é frase verificável ("o bot responde em até 5s a uma
  pergunta sobre o cardápio"), não adjetivo ("rápido").
- Seção 3 é a mais importante e a que se esquece de escrever: o escopo negativo
  com o motivo ao lado.

## `CLAUDE.md`

O guia operacional do repositório — o arquivo que entra em contexto em toda
sessão. Ele responde: o que é isto, onde paramos, como rodo, como as peças se
ligam, o que não posso fazer, onde piso em falso. **Orçamento: 200 linhas** —
a documentação do Claude Code pede isso porque arquivo maior reduz a aderência
às regras que ele mesmo contém.

```markdown
# CLAUDE.md

Guia para o Claude Code (claude.ai/code) trabalhar neste repositório.

## O que é
## Onde paramos (2026-08-13)
## Documentos do projeto (ler antes de trabalhar)
## Comandos
## Arquitetura
## Convenções essenciais
## Armadilhas deste projeto
## Ciclo de trabalho
```

**"O que é"** — dois a três parágrafos: o produto e o stack. Se houver
repositório irmão, ele é citado aqui com o caminho absoluto e o que os liga.

**"Onde paramos (data)"** — até 12 linhas: versão no ar, o que acabou de ser
feito, o que está esperando o usuário, qual é o próximo bloco. É o passe de
bastão entre sessões, e mora aqui porque o CLAUDE.md é o único documento que
toda sessão lê sem pedir. **Reescrito** ao fechar cada bloco, com a data no
título — nunca acrescentado embaixo do anterior; o anterior está no git. Não
existe outra cópia dele (nem no TASKS.md): duas cópias de estado divergem, e a
que não foi atualizada é lida com a mesma confiança.

**"Documentos do projeto"** — uma linha por arquivo de `.claude/`, com link
relativo e o que se vai buscar lá. Não repita o conteúdo: o valor é o roteiro.
Inclua a linha do `historico/` quando ele existir: "antes de reabrir assunto que
pareça resolvido, `grep -rn <termo> .claude/`".

**"Comandos"** — os comandos literais, em blocos `sh`, com comentário ao lado do
que cada um faz. Se algum tiver pegadinha de diretório, de ambiente ou de
sistema operacional, ela vem em negrito logo abaixo — é o tipo de coisa que
custa meia hora quando não está escrita.

**"Arquitetura"** — o fluxo principal em bloco ASCII e os **pontos que atravessam
vários arquivos**: aquilo que ninguém descobre lendo um arquivo só. Cada ponto
tem **até três linhas**: o que é e onde está o detalhe. Quando um ponto precisa
de mais, o detalhe vira `rules/dominios/<tema>.md` (ver abaixo) e aqui fica a
linha com o link. Foi por não ter esse teto que a lista do maitre-virtual chegou
a 440 linhas carregadas em toda sessão, inclusive nas que não tocavam em nada
daquilo.

**"Convenções essenciais"** — o resumo inegociável, cinco a dez linhas, com o
detalhe delegado a `.claude/rules/`. Não copie as regras inteiras para cá: duas
cópias divergem, e a de cima é a que vai ficar velha.

**"Armadilhas"** — só as que valem em qualquer área do código. A armadilha de uma
área mora na regra da área, que carrega quando se mexe ali — é lá que ela evita
o erro, no momento em que ele seria cometido. Cada uma diz o **sintoma** antes da
causa, porque é pelo sintoma que ela vai ser procurada.

**"Ciclo de trabalho"** — três a cinco linhas, apontando para
`.claude/rules/workflow.md`.

## `.claude/rules/workflow.md`

O processo. É o arquivo mais estável do repositório e o que mais evita atrito.
**Sem `paths:`**: entra em toda sessão, e por isso divide com as outras regras
sem `paths:` um orçamento de 250 linhas. Nasce com os padrões da casa já
preenchidos, adaptados ao stack:

```markdown
# Regras de processo (como trabalhar neste repo)

## Ciclo de trabalho
## Commits
## Depuração de problemas reportados
## Interação
## Tamanho dos documentos
## Duas memórias
## Ambiente / gotchas operacionais
```

- **Ciclo**: ler o "Onde paramos" do CLAUDE.md e, no TASKS.md, só o bloco que vai
  atacar → implementar → validar com o comando real do projeto → atualizar
  TASKS.md e MEMORY.md, reescrever o "Onde paramos" → `sh
  .claude/hooks/medir-docs.sh` (saída vazia é o certo) → commit → **parar para
  o teste manual**. O checkpoint é regra, não sugestão: não empilhar blocos.
  "Ler o TASKS.md inteiro" não entra: em projeto que cresceu, o Read para em
  2.000 linhas ou em ~25 mil tokens, o que vier primeiro (o TASKS do atrio, com
  918 linhas, foi cortado na 778), e o agente segue achando que viu tudo.
- **Commits**: pt-BR, `tipo: resumo` ou `Bloco N (área): resumo`, corpo com
  bullets do que mudou e por quê, nunca `--amend`, trailers do harness no fim.
  Se ainda não houver remote, diga isso e diga o que muda quando houver.
- **Depuração**: investigar antes de corrigir — olhar o dado, o log e o código
  rodando de verdade no ambiente real. Bug de comportamento vira teste que
  reproduz o caso. Relatar sempre como causa raiz → correção → como testar.
- **Interação**: responder em pt-BR; quem decide produto é o usuário, e ele quer
  recomendação, não lista de opções; o que só ele pode fazer (painel de terceiro,
  credencial, loja) vira passo a passo numerado e curto.
- **Tamanho dos documentos** — a receita curta, para qualquer agente aplicar sem
  depender de skill:

  ```markdown
  ## Tamanho dos documentos

  Os orçamentos moram em `.claude/hooks/medir-docs.sh`, que roda no começo de
  toda sessão e fica calado enquanto está tudo dentro. Quando ele avisar, compactar
  antes do próximo bloco (skill `manter-docs`, ou à mão por esta tabela).
  Compactar é **mover**, nunca apagar:

  | Quando | Sai de | Vai para |
  |---|---|---|
  | bloco aprovado no teste manual | TASKS.md | `historico/TASKS-AAAA-MM.md` (mês da aprovação), texto literal; no TASKS fica uma linha em "Concluídos" |
  | decisão superada | MEMORY.md | `historico/MEMORY-superadas.md`, com a data e o que a substituiu; no MEMORY fica a decisão nova |
  | entrada com investigação longa | MEMORY.md | o texto inteiro em `historico/MEMORY-AAAA-MM.md`; no MEMORY fica a conclusão e o ponteiro |
  | armadilha de uma área só | MEMORY.md ou CLAUDE.md | `rules/<área>.md` |
  | ponto de arquitetura com mais de 3 linhas | CLAUDE.md | `rules/dominios/<tema>.md` |

  Compactação vai em commit próprio (`docs: compacta TASKS e MEMORY`), separado
  de código. Se outro agente tiver mudança não commitada nesses arquivos, não
  compactar — avisar o usuário: os dois trabalhos se atropelam no merge.
  ```

- **Duas memórias** — a fronteira entre o MEMORY.md do repositório e a memória
  automática do Claude Code (`~/.claude/projects/<pasta>/memory/`):

  ```markdown
  ## Duas memórias

  Fato do projeto — infra, API, comportamento do código, armadilha, decisão —
  vai para `.claude/MEMORY.md` (ou para a regra da área): é versionado, chega a
  qualquer máquina e a qualquer agente. A memória automática do Claude Code
  guarda só o que é do usuário e vale além deste repositório: preferência, jeito
  de trabalhar, correção de comportamento. Fato de projeto na memória automática
  some na próxima máquina e não aparece para quem lê o repositório.
  ```

- **Ambiente**: o que o usuário respondeu na rodada 2 e o que isso implica no
  stack escolhido (ver `stacks.md`). Seção opcional — se o ambiente não tiver
  pegadinha conhecida, ela não entra.

## `.claude/rules/<área>.md`

Um arquivo por área com regras próprias, decidido na rodada 2 — não um por
pasta. **Abre com `paths:`** apontando para as pastas da área:

```markdown
---
paths:
  - "backend/**"
---

# Backend
```

O `paths:` é o que faz a regra aparecer quando se mexe naquele código e sumir
quando não — o que ao mesmo tempo poupa contexto e põe a armadilha na frente do
agente na hora certa. Globs aceitam `**` e chaves (`"src/**/*.{ts,tsx}"`). Em
projeto novo as pastas ainda não existem: use o layout que o stack vai criar
(`stacks.md`) e registre no Bloco 1 a tarefa de conferir que os `paths:` batem
com as pastas criadas — regra cujo `paths:` não casa com nada nunca carrega, e
nada avisa.

Cada regra com o motivo, e as armadilhas da área junto das regras que elas
explicam. Em projeto novo esses arquivos são curtos e honestos: as convenções
que a entrevista produziu, mais as do stack. Eles engordam sozinhos — toda vez
que um bloco descobre uma regra ou uma armadilha da área, ela entra aqui. O
orçamento de cada um é 300 linhas.

Termine cada arquivo de área com um "antes de fechar um bloco": a checagem que
vale para aquela área (o comando de build, o que olhar na tela, o que atualizar).

**Não nasce na criação, mas a skill deve saber que existem:**

- `rules/dominios/<tema>.md` — como um tema que atravessa vários arquivos
  funciona **hoje**: fluxo, estados, invariantes, onde mora cada peça. Leva
  `paths:` com os arquivos que implementam o tema, então aparece quando se mexe
  neles. É reescrito quando o comportamento muda, nunca acrescentado — o que ele
  descreve é o presente. Nasce quando um ponto da "Arquitetura" do CLAUDE.md
  passa de três linhas. É o "spec" que vale ter: estado atual por domínio, e não
  um segundo sistema de planejamento ao lado dos blocos.
- `.claude/skills/<tema>/SKILL.md` — para assunto sem pasta: operar a API de um
  painel, um runbook de deploy, a rotina de um terceiro. `paths:` não serve
  porque não há arquivo para casar; a skill carrega quando o assunto aparece,
  pela descrição. Frontmatter com `name` e uma `description` que diga **quando**
  usar ("Carregar ANTES de qualquer `bash bin/cool.sh`..."), **entre aspas
  duplas**: YAML sem aspas quebra quando o valor tem `: ` no meio, e skill com
  frontmatter inválido simplesmente não carrega. Como a skill depende de o
  agente lembrar de chamá-la, o ciclo do `workflow.md` diz "carregar a skill do
  tema antes de operar" e lista os nomes.

## `.claude/TASKS.md`

**Só o que está aberto.** Bloco aprovado sai daqui, então o arquivo fica do
tamanho do trabalho em andamento, não do tamanho da história do projeto.
Orçamento: 300 linhas.

```markdown
# TASKS — <Projeto>

Só o que está aberto. **Onde paramos** fica no CLAUDE.md. Bloco aprovado no
teste manual sai daqui para `.claude/historico/TASKS-AAAA-MM.md` (texto literal)
e deixa uma linha em "Concluídos". Tarefa descoberta no meio do caminho entra
aqui, não some.

Um bloco = implementar → validar (`<comando real>`) → atualizar este arquivo,
o MEMORY.md e o "Onde paramos" → commit → **teste manual antes do próximo**.
Não empilhar blocos.

---

## Bloco 1 — <o primeiro passo real>
Aceite: <critério verificável>
- [ ] …

## Pendências que não são código
(dependem de decisão, arte ou acesso)
- [ ] …

## Concluídos
- Bloco 0 — andaime do repositório (<data de hoje>): CLAUDE, AGENTS, README,
  .gitignore e `.claude/` criados por `/novo-projeto`; decisões da entrevista
  no MEMORY.
```

- Dentro de um bloco aberto, item feito vira `[x]` com a data e uma linha do que
  foi feito — é o progresso do bloco. Quando o bloco é **aprovado** (teste
  manual), ele inteiro vai para o histórico, literal, e em "Concluídos" fica uma
  linha: `- Bloco N — título (data) → historico/TASKS-AAAA-MM.md`.
- Bloco feito e ainda não aprovado fica aqui, com ✅ e "aguardando aprovação":
  enquanto o usuário não testou, ele ainda é trabalho aberto.
- "Concluídos" fica no fim: quem abre o arquivo precisa ver primeiro o que falta.
  Quando passar de ~30 linhas, as mais antigas viram uma só ("Blocos 0 a 20: ver
  `historico/`").
- Blocos seguintes saem da rodada 4, cada um com critério de aceite.
- A lista de pendências que não são código (arte, conta em serviço, credencial)
  fica separada e visível — é ela que costuma virar caminho crítico.

## `.claude/MEMORY.md`

Memória de longo prazo: **decisões vigentes com o motivo** e fatos que não dá
para deduzir lendo o código. É o documento que distingue um repositório em que
o Claude trabalha bem de um em que ele repete os mesmos erros — e por isso não
pode crescer até ninguém o ler. Orçamento: 400 linhas.

```markdown
# MEMORY — <Projeto>

> Decisões **vigentes** com o motivo, e fatos que não dá para deduzir do código.
> Organizado por tema: entrada nova entra na seção do tema, com data.
> Decisão superada sai para `historico/MEMORY-superadas.md`; investigação longa
> fica no histórico e aqui fica a conclusão. Armadilha de uma área só mora na
> regra da área. Antes de reabrir assunto que pareça resolvido:
> `grep -rn "<termo>" .claude/`.
> Não duplicar o PRD.md (requisitos) nem o TASKS.md (status).

## <Tema>

- **<data> — <a decisão em uma frase que já diz o porquê>.** <O contexto: o que
  se considerou, o que foi descartado e o que quebra se alguém fizer diferente.>
```

**Não nasce vazio.** A entrevista produziu decisões — o escopo negativo, a
escolha do stack, o que ficou fora de propósito, o que já foi descartado — e são
exatamente essas que ninguém escreve depois, porque na hora pareciam óbvias. Três
a seis entradas é um começo saudável, nos temas que elas mesmas pedem (costuma
ser "Escopo" e "Stack"). Tema novo nasce quando a primeira entrada dele aparece.

**Por tema, não por data.** Em ordem cronológica, quem quer saber "o que se
decidiu sobre cobrança" lê o arquivo todo; por tema, lê uma seção. O
maitre-virtual chegou a essa forma sozinho, depois de passar de mil linhas. Com
o tempo, as decisões que se repetem viram uma seção "Princípios" no topo —
quando houver, não antes.

**Entrada curta, histórico longo.** O título é a conclusão numa frase; o
parágrafo, até umas seis linhas, diz o que se perde fazendo diferente. A
investigação — medições, tentativas, o caminho até a conclusão — vale ouro e
mora no `historico/` (ou na mensagem do commit), com o ponteiro aqui.

**Decisão superada sai daqui.** Antes ficava marcada no lugar, e o resultado era
a decisão velha e a nova lado a lado no mesmo arquivo — a documentação do
Claude Code avisa que, diante de duas instruções contraditórias, ele pode seguir
qualquer uma. Ela vai para `historico/MEMORY-superadas.md`, com a data e o que a
substituiu; aqui fica só a vigente.

## `.claude/hooks/medir-docs.sh` e `.claude/settings.json`

O medidor é cópia literal de `assets/medir-docs.sh` — não adapte os limites por
projeto na criação; se um projeto precisar de outro número, a mudança é no
script dele, com o motivo no commit.

O `settings.json` (versionado, ao contrário do `settings.local.json`) liga o
medidor no começo da sessão:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear",
        "hooks": [
          {
            "type": "command",
            "command": "sh \"$CLAUDE_PROJECT_DIR/.claude/hooks/medir-docs.sh\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

A saída de um hook `SessionStart` entra no contexto do agente, e por isso o
script fica calado quando está tudo dentro do orçamento. No Windows o comando
roda no Git Bash; `$CLAUDE_PROJECT_DIR` chega como `D:\...` e o `sh` aceita.
O script sempre sai com 0: medidor nunca impede uma sessão de começar.

**`.gitattributes` com `*.sh text eol=lf` desde o primeiro commit.** Nesta
máquina o git está com `core.autocrlf=true`: sem a linha, o checkout grava o
medidor com CRLF e o `sh` quebra em toda sessão com `$'\r': command not found` —
ruído que entra no contexto do agente no lugar do aviso. A mesma linha salva
qualquer script que vá rodar em container Linux.

## `.claude/historico/`

Não nasce na criação (pasta vazia não vai para o git, e não haveria o que
guardar). Aparece no primeiro bloco aprovado. É arquivo morto **legível**:
ninguém o lê inteiro, mas `grep -rn` o encontra — diferente do `git show
<hash>:arquivo`, que só serve para quem já sabe o hash. Nomes por mês
(`TASKS-2026-10.md`, `MEMORY-2026-10.md`) e um `MEMORY-superadas.md`. Texto
movido entra literal, sem reescrever: é o que permite conferir depois que a
compactação não perdeu nada.

## `README.md`

Para gente, não para o Claude. O que é, como rodar, como validar. Curto. Se
houver ambiguidade de público, o README fala com quem chega ao repositório pela
primeira vez; o CLAUDE.md fala com quem vai mexer no código hoje.

## `AGENTS.md`

Ponteiro, não cópia. Outras ferramentas procuram por este nome:

```markdown
# AGENTS.md

As regras de trabalho deste repositório estão no [CLAUDE.md](CLAUDE.md) e em
[.claude/rules/](.claude/rules/). Este arquivo existe porque algumas ferramentas
procuram por este nome — o conteúdo é o mesmo, e mora lá.
```

## `.gitignore`

Do stack escolhido (ver `stacks.md`), mais o que a entrevista revelou: arquivo de
credencial, `.env`, artefato de build, pasta de dados local. **Nada de segredo
versionado** — se algum arquivo de credencial já existir na pasta, cite-o
explicitamente no relatório final.

## `.claude/settings.local.json`

Permissões locais. Nasce enxuto: só o que a rodada 2 mostrou que vai ser rodado
toda hora (o comando de teste, o de build, `git add`/`git commit`, o medidor).
Permissão demais concedida cedo é a que ninguém revisa depois.

```json
{
  "permissions": {
    "allow": [
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(sh .claude/hooks/medir-docs.sh)"
    ]
  }
}
```
