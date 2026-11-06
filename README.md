# Skills da Vaula

Skills do [Claude Code](https://code.claude.com) feitas na Vaula Tecnologia,
num plugin só (`vaula`). As skills estão em português.

| Skill | Para que serve |
|---|---|
| `novo-projeto` | Cria a estrutura de trabalho de um repositório: CLAUDE.md, AGENTS.md, README, `.claude/` com PRD, TASKS, MEMORY, regras por área e o medidor de orçamento dos documentos. |
| `manter-docs` | Compacta e reorganiza esses documentos quando passam do orçamento, sem perder conteúdo (vai para `.claude/historico/`), e migra projetos antigos para a forma atual. Usa os arquivos da `novo-projeto`. |
| `busca-marca` | Busca preliminar de marca no INPI (base pePI) e de domínio `.br` no registro.br, com leitura do risco de conflito. Não substitui o parecer de um advogado de marcas. |

## Instalar

No Claude Code:

```text
/plugin marketplace add Vaula-Tecnologia/skills
/plugin install vaula@vaula
```

As skills aparecem como `vaula:novo-projeto`, `vaula:manter-docs` e
`vaula:busca-marca`, e o Claude as usa sozinho quando o pedido combina. Para
atualizar: `/plugin marketplace update vaula`.

Sem o sistema de plugins, também dá para copiar cada pasta de `skills/` para
`~/.claude/skills/`. Nesse caso, copie a `novo-projeto` junto com a
`manter-docs`, que lê os arquivos dela pela pasta vizinha.

### Requisitos

- `busca-marca`: Python 3.10 ou mais novo, só a biblioteca padrão. Consulta
  serviços públicos (pePI do INPI e registro.br) com pausa entre pedidos; não
  rode em laço.
- `novo-projeto` e `manter-docs`: `git` e `sh` (no Windows, o Git Bash serve).

## Estrutura

```text
.claude-plugin/
  marketplace.json   o repositório é o marketplace "vaula"...
  plugin.json        ...e também o plugin "vaula", na raiz
skills/
  <nome>/SKILL.md    uma pasta por skill, com scripts/, references/ e assets/ quando precisa
```

## Contribuir

Issues e pull requests são bem-vindos. Mudou uma skill: abra o PR e suba a
`version` do `plugin.json`, para quem já instalou receber a atualização. Skill
nova: uma pasta em `skills/` e uma linha na tabela acima. Rode
`claude plugin validate .` antes de abrir o PR.

## Licença

[MIT](LICENSE) © Vaula Tecnologia LTDA.
