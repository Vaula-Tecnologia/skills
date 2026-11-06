---
name: novo-projeto
description: Cria do zero a estrutura de trabalho de um repositório — pasta, CLAUDE.md, AGENTS.md, README.md, .gitignore e a pasta .claude/ com PRD.md, TASKS.md, MEMORY.md, rules/ com paths por área, settings e o medidor de orçamento dos documentos — e faz o primeiro commit. Use sempre que o usuário rodar /novo-projeto, disser que vai começar um projeto novo, pedir para "criar a pasta do projeto", "montar o CLAUDE.md", "preparar a documentação de um repo novo", "fazer o scaffold", "iniciar um repositório" ou "padronizar a documentação de agente" — e também quando um projeto que já tem código ainda não tem CLAUDE.md nem .claude/ e precisa ganhar os dois. Projeto que já tem CLAUDE.md e .claude/ é caso da skill manter-docs, não desta.
---

# Novo projeto

Monta o **andaime de trabalho** de um repositório: os documentos que fazem o
Claude Code trabalhar bem nele desde a primeira sessão. É a estrutura que um
repositório costuma levar meses para ganhar, arrancado a arrancado — aqui ela
nasce pronta.

## O que sai daqui

```
<destino>/
├── CLAUDE.md              guia do repositório: o que é, onde paramos, comandos, arquitetura, armadilhas
├── AGENTS.md              ponteiro para o CLAUDE.md (outros agentes e ferramentas leem este nome)
├── README.md              leia-me humano: o que é e como rodar
├── .gitignore             do stack escolhido
└── .claude/
    ├── PRD.md             requisitos: problema, personas, escopo, modelo de dados, critérios de aceite
    ├── TASKS.md           só o que está aberto, por bloco
    ├── MEMORY.md          decisões vigentes COM o motivo, por tema
    ├── settings.json      hook que roda o medidor no começo da sessão (versionado)
    ├── settings.local.json permissões locais
    ├── hooks/
    │   └── medir-docs.sh  o medidor: calado dentro do orçamento, avisa fora dele
    └── rules/
        ├── workflow.md    processo, commits, ambiente — sem `paths:`, entra em toda sessão
        └── <área>.md      uma por área, com `paths:` — só entra quando se mexe na área
```

E o que **nasce depois**, quando houver conteúdo (nunca vazio na criação):
`.claude/historico/` (arquivo morto: blocos aprovados, decisões superadas,
investigação longa — consultado por `grep`), `.claude/rules/dominios/<tema>.md`
(como um tema que cruza vários arquivos funciona hoje, com `paths:` nos arquivos
que o implementam) e `.claude/skills/<tema>/SKILL.md` (procedimento sem pasta
própria: operar uma API de terceiro, um runbook de deploy).

O que **não** sai daqui: código. Este comando não roda `create-expo-app`, `npm
create vite`, `uv init` nem instala dependência — quem faz isso é o Bloco 1 do
TASKS.md, na sessão seguinte, já com as regras escritas para guiá-lo. A separação
é de propósito: o andaime funciona para qualquer stack e não quebra por causa de
rede, npm ou versão de CLI.

## A regra que governa tudo

Esses documentos valem pelo **porquê**, não pelo cabeçalho. "Use tokens de cor"
é uma linha que ninguém obedece sob pressão; "cor cravada no JSX não troca com o
tema, e foi assim que o app apareceu com tarja preta no aparelho" é uma linha que
se lembra. Ao escrever qualquer arquivo daqui, a pergunta é sempre: *o que
quebra se alguém fizer diferente?* Se não houver resposta, a linha provavelmente
não precisa existir.

Disso sai o corolário mais importante deste comando: **seção sem conteúdo não é
escrita**. Nada de `## Arquitetura` seguido de `TODO: preencher`. Um documento
com esqueleto vazio ensina, na primeira leitura, que aquelas seções são
decorativas — e a partir daí ninguém as preenche nem as lê. Documento curto e
verdadeiro vence documento completo e oco, sempre. O que faltar entra como
tarefa no TASKS.md, que é o lugar onde falta é informação útil.

## A segunda regra: documento que só cresce deixa de ser lido

O andaime anterior acertava no conteúdo e errava no envelhecimento: toda regra
dele fazia os documentos crescerem e nenhuma os fazia encolher. Medido em
2026-10-13, nos projetos que nasceram dele:

- no maitre-virtual, CLAUDE.md com 638 linhas e `rules/` com 69 KB entravam
  inteiros em toda sessão — uns 32 mil tokens antes da primeira pergunta. A
  documentação do Claude Code pede menos de 200 linhas por CLAUDE.md porque
  arquivo longo **reduz a aderência** às próprias regras;
- no infra-aeternis, o TASKS.md chegou a 4.241 linhas, e o Read lê no máximo
  2.000 linhas ou ~25 mil tokens por chamada (o do atrio, com 918, foi cortado
  na 778): o passo "ler o TASKS.md" lia um pedaço e seguia achando que tinha
  visto tudo. Mais da metade eram blocos já fechados;
- os dois foram compactados à mão uma vez, sem gatilho nem receita, com o
  arquivo morto num `git show <hash>` que ninguém consulta — e cresceram de novo
  em seis semanas;
- nenhum dos 62 arquivos de `rules/` usava `paths:`, então a regra de frontend
  ocupava contexto até em sessão que só mexia em migration.

Daí saem quatro decisões, que valem para tudo o que este comando escreve:

1. **O que entra em toda sessão é pouco**: CLAUDE.md e `workflow.md`. Regra de
   área leva `paths:` e só carrega quando o agente abre um arquivo daquela área —
   que é exatamente quando a armadilha dela precisa aparecer.
2. **Tudo tem para onde ir quando envelhece.** Bloco aprovado, decisão superada,
   investigação longa: saem dos documentos ativos para `.claude/historico/`,
   **movidos, não apagados**, e continuam achados por `grep`.
3. **Estado se reescreve; registro se acrescenta.** "Onde paramos" e os
   documentos de domínio são reescritos a cada bloco. Só o histórico cresce por
   acréscimo, e ele não é lido inteiro por ninguém.
4. **Orçamento medido por máquina.** Cada documento tem um limite, e o
   `.claude/hooks/medir-docs.sh` roda no começo de toda sessão: calado dentro do
   orçamento, aviso dentro do contexto do agente fora dele. Instrução em
   CLAUDE.md é contexto, não garantia — o hook é o que não depende de lembrar.

A compactação em si — e a migração de projeto antigo para esta forma — é da
skill `manter-docs`. Este comando só faz os documentos nascerem já com lugar para
envelhecer.

## Passo 0 — destino, nome e terreno

O nome vem do argumento (`/novo-projeto orcamento-familiar`). Sem argumento,
pergunte antes de qualquer outra coisa.

**O destino é a pasta em que o comando foi chamado**: o projeto nasce em
`<diretório atual>/<nome>`. Não há caminho padrão e não se move nada para outro
lugar — quem escolhe onde o projeto mora é o usuário, escolhendo de onde chama.
Confirme o caminho completo antes de criar qualquer coisa, para não haver dúvida
de onde a pasta apareceu.

Três situações, e vale checar qual é antes de seguir:

- **Pasta nova**: caminho livre, siga para o Passo 1.
- **`<diretório atual>/<nome>` já existe e não está vazia**: pare e pergunte. Dois
  desfechos legítimos, e a escolha é do usuário: (a) o projeto já tem código e
  quer ganhar a documentação, ou (b) foi engano no nome. Nunca sobrescreva
  arquivo existente sem dizer qual e por quê.
- **O comando foi chamado de dentro de um projeto que já existe** (o diretório
  atual tem `.git`, `package.json`, `pyproject.toml` ou coisa do gênero) e não
  veio nome no argumento: o pedido quase certamente é documentar **esta** pasta,
  não criar uma subpasta dentro dela. Confirme em uma linha antes de escrever.
- **A pasta já tem `CLAUDE.md` e `.claude/` com TASKS/MEMORY**: não é caso deste
  comando. Reescrever o andaime por cima apagaria o que o projeto aprendeu; o
  que esse projeto precisa é a skill `manter-docs`, que migra para a forma
  atual movendo em vez de reescrever. Diga isso e pergunte.

**Onde já houver código, leia antes de perguntar**: `package.json`/
`pyproject.toml`, a árvore de pastas, o README, os scripts, o histórico do git.
Metade da entrevista se responde lendo, e perguntar o que está escrito na tela
gasta a paciência do usuário para as perguntas que importam. Diga o que você
deduziu e peça só a confirmação e as lacunas.

## Passo 1 — a entrevista

Leia `references/entrevista.md` e conduza-a **inteira antes de escrever qualquer
arquivo**. São quatro rodadas curtas; a ordem importa porque cada rodada usa a
resposta da anterior.

Como conduzir, em resumo (o detalhe está no arquivo):

- Em **português do Brasil**, uma rodada por vez, com o que você já deduziu
  preenchido — corrigir um palpite é mais rápido do que redigir do zero.
- Use `AskUserQuestion` quando as respostas forem enumeráveis (stack, tipo de
  projeto, áreas do código) e texto livre quando a resposta for uma explicação.
  Recomende uma opção em vez de oferecer um cardápio neutro.
- Persiga o **motivo** e o **escopo negativo**. "O que este projeto
  deliberadamente não vai fazer, e por quê" é a pergunta que mais rende: é dela
  que saem as melhores linhas do CLAUDE.md e as primeiras entradas do MEMORY.md.
- Se o usuário cortar a entrevista ("só cria logo"), reduza às quatro essenciais da
  seção "Versão curta" do `entrevista.md`, escreva o que der e registre o resto
  como pendência no TASKS.md — nunca preencha com invenção plausível.

## Passo 2 — escrever os documentos

Leia `references/documentos.md`: ele tem, arquivo por arquivo, a estrutura, o
tom e os erros que estragam cada um. Leia `references/stacks.md` para os padrões
do stack escolhido: comandos, `.gitignore`, quais arquivos de `rules/` criar e as
armadilhas já conhecidas daquele terreno.

Ordem de escrita — cada arquivo alimenta o próximo:

1. **`.claude/PRD.md`** — o que o produto é e para quem. Sai direto das rodadas 1 e 4.
2. **`CLAUDE.md`** — o guia operacional. Resume o PRD em dois parágrafos e aponta para ele; o "Onde paramos" nasce dizendo que o andaime está pronto e o Bloco 1 é o próximo.
3. **`.claude/rules/workflow.md`** e as regras por área — o processo e as convenções. Cada regra de área com o `paths:` das pastas que a rodada 2 definiu.
4. **`.claude/TASKS.md`** — os blocos até a primeira versão utilizável, com o Bloco 0 (este andaime) já em "Concluídos", com a data de hoje.
5. **`.claude/MEMORY.md`** — semeado com as decisões que a entrevista produziu, cada uma com data e motivo, agrupadas por tema. **MEMORY.md não nasce vazio**: se a entrevista rendeu escopo negativo, escolha de stack ou restrição conhecida, isso são entradas, e são justamente as que ninguém lembra de escrever depois.
6. **`.claude/hooks/medir-docs.sh`** — cópia literal de `assets/medir-docs.sh` — e **`.claude/settings.json`** com o hook que o roda (modelo no `documentos.md`).
7. **`README.md`**, **`AGENTS.md`**, **`.gitignore`**, **`.gitattributes`** (no mínimo `*.sh text eol=lf`, senão o medidor sai do checkout com CRLF e quebra), **`.claude/settings.local.json`**.

Datas sempre absolutas (`2026-08-13`), nunca "hoje" ou "semana passada" — use a
data do ambiente. Todo texto em português do Brasil.

Antes do commit, rode `sh .claude/hooks/medir-docs.sh` na pasta nova: andaime
recém-criado que já nasce acima do orçamento está escrevendo demais, e a hora de
cortar é agora. Saída vazia é o resultado certo.

## Passo 3 — git

```sh
git init -b main   # só se ainda não houver repositório
git add -A
git commit         # mensagem em pt-BR, com os trailers do harness
```

**Projeto que já tem repositório não leva `git init`**, e o `git add -A` ali
arrastaria junto todo trabalho não commitado que já estava na pasta. Nesse caso,
adicione **apenas os arquivos criados agora**, nominalmente, e diga no relatório
o que ficou de fora.

Mensagem no formato da casa: primeira linha `chore: estrutura inicial do projeto`
e corpo com bullets do que foi criado e das decisões que a entrevista fixou.
Se o `git init` falhar (git ausente, pasta dentro de outro repo), diga e siga —
os documentos já valem sem o commit.

## Passo 4 — fechar

Relate em cinco linhas, não mais:

- onde ficou o projeto e o que foi criado;
- as **decisões** que ficaram gravadas (é o que o usuário vai querer conferir);
- o que ficou **em aberto** por falta de resposta, e onde está anotado;
- o próximo passo concreto (quase sempre: abrir o Claude Code na pasta nova e
  atacar o Bloco 1 do TASKS.md).

Não abra o projeto, não instale nada, não comece o Bloco 1 na mesma sessão a
menos que o usuário peça. O andaime é o entregável.

## Arquivos de referência

- `references/entrevista.md` — as quatro rodadas, com o motivo de cada pergunta e a versão curta.
- `references/documentos.md` — estrutura, tom e armadilhas de cada arquivo gerado.
- `references/stacks.md` — padrões por stack: comandos, `.gitignore`, arquivos de `rules/` com seus `paths:`, armadilhas conhecidas.
- `assets/medir-docs.sh` — o medidor de orçamento, copiado sem alteração para `.claude/hooks/` de cada projeto. Os limites moram nele.
