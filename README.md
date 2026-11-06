# Skills da Vaula

Skills do Claude Code feitas na Vaula Tecnologia, num plugin só (`vaula`).

| Skill | Para que serve |
|---|---|
| `novo-projeto` | Cria a estrutura de trabalho de um repositório: CLAUDE.md, AGENTS.md, README, `.claude/` com PRD, TASKS, MEMORY, regras por área e o medidor de orçamento dos documentos. |
| `manter-docs` | Compacta e reorganiza esses documentos quando passam do orçamento, sem perder conteúdo (vai para `.claude/historico/`), e migra projetos antigos para a forma atual. Usa os arquivos da `novo-projeto`. |
| `busca-marca` | Busca preliminar de marca no INPI (pePI) e de domínio `.br` no registro.br, com leitura do risco de conflito. Não substitui advogado de marcas. |

## Instalar em outra máquina

O repositório é privado: a máquina precisa de acesso à org Vaula-Tecnologia no
GitHub (por exemplo, `gh auth login`).

```text
/plugin marketplace add Vaula-Tecnologia/skills
/plugin install vaula@vaula
```

As skills aparecem como `vaula:novo-projeto`, `vaula:manter-docs` e
`vaula:busca-marca`. Para atualizar depois: `/plugin marketplace update vaula`.

Sem o sistema de plugins, também dá para copiar cada pasta de `skills/` para
`~/.claude/skills/`. Nesse caso, copie `novo-projeto` junto com `manter-docs`,
que lê os arquivos dela pela pasta vizinha.

## Estrutura

```text
.claude-plugin/
  marketplace.json   o repositório é o marketplace "vaula"...
  plugin.json        ...e também o plugin "vaula", na raiz
skills/
  <nome>/SKILL.md    uma pasta por skill, com scripts/, references/ e assets/ quando precisa
```

## Mudanças

Mude a skill aqui, abra PR e suba a `version` do `plugin.json` quando a mudança
for para as outras máquinas. Skill nova: uma pasta em `skills/` e uma linha na
tabela acima.

Só entram skills feitas aqui. As instaladas de terceiros (Blender, Three.js,
Vercel, OpenSpec, Maestri e outras) ficam com os donos delas. As skills de
projeto (as do `infra-aeternis`, a `langfuse` do Átrio) moram no repositório
de cada projeto.
