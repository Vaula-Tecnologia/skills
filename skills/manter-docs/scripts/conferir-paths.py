"""Lista as regras de .claude/rules/ cujo `paths:` não casa com arquivo nenhum.

Regra com `paths:` só carrega quando o agente abre um arquivo que casa. Se o
padrão estiver errado (pasta renomeada, layout que mudou no Bloco 1), a regra
nunca carrega, e nada avisa: o agente trabalha sem ela achando que não existe.

Uso:
  python conferir-paths.py <repo>

Compara cada padrão com os arquivos versionados (git ls-files). Sai com 1 se
algum padrão não casar com nada.
"""

import pathlib
import re
import subprocess
import sys


def para_regex(padrao: str) -> re.Pattern:
    i, saida = 0, ""
    while i < len(padrao):
        c = padrao[i]
        if padrao.startswith("**/", i):
            saida, i = saida + "(?:.*/)?", i + 3
        elif padrao.startswith("**", i):
            saida, i = saida + ".*", i + 2
        elif c == "*":
            saida, i = saida + "[^/]*", i + 1
        elif c == "?":
            saida, i = saida + "[^/]", i + 1
        elif c == "{":
            fim = padrao.index("}", i)
            opcoes = padrao[i + 1:fim].split(",")
            saida, i = saida + "(?:" + "|".join(re.escape(o) for o in opcoes) + ")", fim + 1
        else:
            saida, i = saida + re.escape(c), i + 1
    return re.compile(saida + r"\Z")


def padroes(regra: pathlib.Path) -> list[str]:
    linhas = regra.read_text(encoding="utf-8", errors="replace").splitlines()
    if not linhas or linhas[0].strip() != "---":
        return []
    achados, dentro = [], False
    for linha in linhas[1:]:
        if linha.strip() == "---":
            break
        if linha.startswith("paths:"):
            dentro = True
            resto = linha[len("paths:"):].strip()
            if resto.startswith("["):
                achados += [p.strip().strip("\"'") for p in resto.strip("[]").split(",") if p.strip()]
                dentro = False
        elif dentro and linha.strip().startswith("- "):
            achados.append(linha.strip()[2:].strip().strip("\"'"))
        elif dentro and linha.strip() and not linha.startswith(" "):
            dentro = False
    return achados


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    repo = pathlib.Path(sys.argv[1])
    versionados = subprocess.run(
        ["git", "-C", str(repo), "ls-files"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.splitlines()

    mortos = 0
    for regra in sorted((repo / ".claude" / "rules").rglob("*.md")):
        nome = regra.relative_to(repo).as_posix()
        lista = padroes(regra)
        if not lista:
            print(f"{nome}: sem paths: (carrega em toda sessão)")
            continue
        for p in lista:
            casados = sum(1 for f in versionados if para_regex(p).match(f))
            if not casados:
                mortos += 1
            print(f"{nome}: {p} -> {casados} arquivos" + ("  <- NÃO CASA COM NADA" if not casados else ""))
    return 1 if mortos else 0


if __name__ == "__main__":
    sys.exit(main())
