#!/bin/sh
# Mede os documentos de trabalho do repositório contra o orçamento de cada um.
#
# Roda sozinho no começo de cada sessão (hook SessionStart em
# .claude/settings.json) e à mão ao fechar um bloco. Dentro do orçamento não
# imprime nada: aviso que aparece sempre vira paisagem. Fora dele, diz o que
# passou e o que fazer, e a saída do hook entra no contexto do agente.
#
# Por que existe: instrução escrita em CLAUDE.md é contexto, não garantia. Sem
# um medidor, compactar depende de alguém lembrar, e os documentos crescem até
# o agente não conseguir mais lê-los inteiros (o Read para em 2000 linhas) e
# até o que entra em toda sessão diluir as regras que importam.
#
# Os limites moram aqui e em nenhum outro lugar. Quem muda um, muda aqui.

LIM_CLAUDE=200    # CLAUDE.md: entra inteiro em toda sessão
LIM_SEMPRE=250    # soma das rules/ sem `paths:`: também entram em toda sessão
LIM_REGRA=300     # cada rule com `paths:` (área ou domínio)
LIM_TASKS=300     # TASKS.md: só o que está aberto
LIM_MEMORY=400    # MEMORY.md: decisões vigentes, por tema
BYTES_LINHA=90    # teto em bytes = linhas x isto; pega linha comprida demais

raiz=${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
cd "$raiz" 2>/dev/null || exit 0

avisos=""

medir() { # rótulo linhas bytes limite
  teto=$(( $4 * BYTES_LINHA ))
  if [ "$2" -gt "$4" ] || [ "$3" -gt "$teto" ]; then
    avisos="$avisos
- $1: $2 linhas, $(( $3 / 1024 )) KB (limite: $4 linhas, $(( teto / 1024 )) KB)"
  fi
}

arquivo() { # caminho limite
  [ -f "$1" ] || return 0
  medir "$1" "$(( $(wc -l < "$1") ))" "$(( $(wc -c < "$1") ))" "$2"
}

tem_paths() { # a regra abre com frontmatter que declara paths:
  awk '{ sub(/\r$/, "") }
       NR == 1 { if ($0 != "---") exit; next }
       $0 == "---" { exit }
       /^paths:/ { achou = 1; exit }
       END { exit !achou }' "$1"
}

arquivo CLAUDE.md "$LIM_CLAUDE"
arquivo .claude/TASKS.md "$LIM_TASKS"
arquivo .claude/MEMORY.md "$LIM_MEMORY"

sempre_l=0
sempre_b=0
for r in .claude/rules/*.md .claude/rules/*/*.md; do
  [ -f "$r" ] || continue
  if tem_paths "$r"; then
    arquivo "$r" "$LIM_REGRA"
  else
    sempre_l=$(( sempre_l + $(wc -l < "$r") ))
    sempre_b=$(( sempre_b + $(wc -c < "$r") ))
  fi
done
medir ".claude/rules/ sem paths: (carregadas em toda sessão)" "$sempre_l" "$sempre_b" "$LIM_SEMPRE"

if [ -n "$avisos" ]; then
  printf '%s\n' \
    "Documentos de trabalho acima do orçamento (.claude/hooks/medir-docs.sh):$avisos" \
    "" \
    "Antes do próximo bloco, compactar: skill manter-docs, ou a seção \"Tamanho dos documentos\" de .claude/rules/workflow.md. Compactar é mover para .claude/historico/, não apagar. Se outro agente tiver mudança não commitada nesses arquivos (git status), avise o usuário em vez de compactar."
fi
exit 0
