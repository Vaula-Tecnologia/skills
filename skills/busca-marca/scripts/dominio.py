"""Disponibilidade de domínios .br no registro.br.

Uso:
    python dominio.py selar viusumiu esvai           (.com.br por padrão)
    python dominio.py sigilo --sufixo seg.br
    python dominio.py sigilo.dev.br                  (nome com ponto = domínio completo)
    python dominio.py sigilo --sugestoes             (mostra as categorias .br em que o nome está livre)

Usa a consulta pública do site (registro.br/v2/ajax/avail/raw/<domínio>), com
pausa entre pedidos. A disponibilidade é a do momento: alguém pode registrar
logo depois.
"""

import argparse
import json
import sys
import time
import urllib.request

URL = "https://registro.br/v2/ajax/avail/raw/{}"
PAUSA = 1.2

# 0 e 2 conferidos na prática (2026-11-06); 5 apareceu num nome em liberação.
# Os textos de 1, 3, 4, 6 e 7 são o entendimento atual dos estados do
# registro.br: na dúvida, abra o domínio no site. Status desconhecido sai com
# o número cru.
STATUS = {
    0: "DISPONÍVEL",
    1: "disponível, com tickets concorrentes",
    2: "registrado",
    3: "indisponível (reservado ou proibido)",
    4: "consulta inválida",
    5: "aguardando processo de liberação",
    6: "disponível no processo de liberação em andamento",
    7: "disponível no processo de liberação, com tickets concorrentes",
}


def consultar(fqdn: str) -> dict:
    pedido = urllib.request.Request(URL.format(fqdn), headers={"User-Agent": "Mozilla/5.0 busca-marca/1.0"})
    with urllib.request.urlopen(pedido, timeout=20) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Disponibilidade de domínios no registro.br.")
    parser.add_argument("nomes", nargs="+")
    parser.add_argument("--sufixo", default="com.br")
    parser.add_argument("--sugestoes", action="store_true", help="lista outras categorias .br livres para o nome")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    resultados = []
    for nome in args.nomes:
        fqdn = nome.lower() if "." in nome else f"{nome.lower()}.{args.sufixo}"
        try:
            dados = consultar(fqdn)
            status = dados.get("status")
            item = {
                "dominio": fqdn,
                "status": status,
                "situacao": STATUS.get(status, f"status {status} (conferir no registro.br)"),
                "expira": dados.get("expires-at", ""),
                "sugestoes": dados.get("suggestions", []),
            }
        except Exception as erro:  # rede, limite de consultas, resposta inesperada
            item = {"dominio": fqdn, "status": None, "situacao": f"erro: {erro}", "expira": "", "sugestoes": []}
        resultados.append(item)
        time.sleep(PAUSA)

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return
    for r in resultados:
        linha = f"{r['dominio']:<32} {r['situacao']}"
        if r["expira"]:
            linha += f" (expira {r['expira'][:10]})"
        print(linha)
        if args.sugestoes and r["sugestoes"]:
            print(f"    livre também em: {', '.join(r['sugestoes'])}")


if __name__ == "__main__":
    main()
