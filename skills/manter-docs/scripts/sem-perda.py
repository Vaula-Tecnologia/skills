"""Confere que uma compactação de documentos não perdeu texto.

Cada linha não trivial dos documentos como estavam em <ref> tem de aparecer,
com os espaços normalizados, em algum documento de agora: CLAUDE.md, AGENTS.md
ou qualquer .md sob .claude/ (histórico incluído). Mover é permitido e é o
esperado; reescrever sem deixar o original no histórico aparece aqui como perda.

A comparação ignora quebra de linha, recuo e marcador de lista/título/citação
no começo da linha, então texto movido e reformatado ainda casa. Negrito,
crase e pontuação contam: mover é copiar literal.

Uso:
  python sem-perda.py <repo> <ref> [arquivo ...]

Sem arquivos, confere CLAUDE.md, .claude/TASKS.md, .claude/MEMORY.md e todo
.claude/rules/**/*.md que existiam em <ref>. Sai com 1 se houver linha perdida,
listando cada uma como arquivo:linha.
"""

import pathlib
import re
import subprocess
import sys

MARCADOR = re.compile(r"^\s*(?:#+\s+|>\s?|[-*+]\s+|\d+[.)]\s+|\[[ xX~]\]\s+)+")
MINIMO = 12  # linha mais curta que isso ("---", "## Decisões") não prova nada


def normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", MARCADOR.sub("", texto)).strip()


def git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    ).stdout


def arquivos_padrao(repo: pathlib.Path, ref: str) -> list[str]:
    todos = git(repo, "ls-tree", "-r", "--name-only", ref).splitlines()
    fixos = {"CLAUDE.md", ".claude/TASKS.md", ".claude/MEMORY.md"}
    return [a for a in todos if a in fixos or (a.startswith(".claude/rules/") and a.endswith(".md"))]


def corpus_atual(repo: pathlib.Path) -> str:
    caminhos = [repo / "CLAUDE.md", repo / "AGENTS.md", *sorted((repo / ".claude").rglob("*.md"))]
    partes = []
    for c in caminhos:
        if c.is_file():
            for linha in c.read_text(encoding="utf-8", errors="replace").splitlines():
                partes.append(MARCADOR.sub("", linha))
    return re.sub(r"\s+", " ", " ".join(partes))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    repo, ref = pathlib.Path(sys.argv[1]), sys.argv[2]
    alvos = sys.argv[3:] or arquivos_padrao(repo, ref)
    corpus = corpus_atual(repo)

    perdidas = 0
    conferidas = 0
    for alvo in alvos:
        antigo = git(repo, "show", f"{ref}:{alvo}")
        for n, linha in enumerate(antigo.splitlines(), 1):
            agulha = normalizar(linha)
            if len(agulha) < MINIMO:
                continue
            conferidas += 1
            if agulha not in corpus:
                perdidas += 1
                print(f"{alvo}:{n}: {linha.strip()[:160]}")

    print(f"\n{conferidas} linhas conferidas, {perdidas} sem destino.")
    return 1 if perdidas else 0


if __name__ == "__main__":
    sys.exit(main())
