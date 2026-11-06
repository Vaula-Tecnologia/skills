"""Disponibilidade de domínios .br no registro.br.

Uso:
    python dominio.py selar viusumiu esvai           (.com.br por padrão)
    python dominio.py sigilo --sufixo seg.br
    python dominio.py sigilo.dev.br                  (nome com ponto = domínio completo)
    python dominio.py sigilo --sugestoes             (mostra as categorias .br em que o nome está livre)
    python dominio.py selar esvai --markdown         (tabela Domínio | Situação | Observação)

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
# Status 8 é o limite de consultas do registro.br: espera e tenta de novo.
ESPERAS_DO_LIMITE = (20, 40, 60)

# 0, 2, 5 e 8 conferidos na prática (2026-11-06; o 8 apareceu com vários
# agentes consultando do mesmo IP). Os textos de 1, 3, 4, 6 e 7 são o
# entendimento atual dos estados do registro.br: na dúvida, abra o domínio no
# site. Status desconhecido sai com o número cru.
STATUS = {
    0: "DISPONÍVEL",
    1: "disponível, com tickets concorrentes",
    2: "registrado",
    3: "indisponível (reservado ou proibido)",
    4: "consulta inválida",
    5: "aguardando processo de liberação",
    6: "disponível no processo de liberação em andamento",
    7: "disponível no processo de liberação, com tickets concorrentes",
    8: "limite de consultas do registro.br: não consultado",
}

# A mesma situação, para a tabela que o usuário lê.
SITUACAO_CURTA = {
    0: "livre",
    1: "livre, com concorrência",
    2: "registrado",
    3: "reservado",
    4: "nome inválido",
    5: "em liberação",
    6: "em liberação (livre)",
    7: "em liberação (com concorrência)",
    8: "não consultado (limite)",
}


def consultar(fqdn: str) -> dict:
    pedido = urllib.request.Request(URL.format(fqdn), headers={"User-Agent": "Mozilla/5.0 busca-marca/1.0"})
    with urllib.request.urlopen(pedido, timeout=20) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def consultar_com_espera(fqdn: str) -> dict:
    dados = consultar(fqdn)
    for espera in ESPERAS_DO_LIMITE:
        if dados.get("status") != 8:
            break
        print(f"  registro.br pediu calma em {fqdn}; esperando {espera} s", file=sys.stderr)
        time.sleep(espera)
        dados = consultar(fqdn)
    return dados


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Disponibilidade de domínios no registro.br.")
    parser.add_argument("nomes", nargs="+")
    parser.add_argument("--sufixo", default="com.br")
    parser.add_argument("--sugestoes", action="store_true", help="lista outras categorias .br livres para o nome")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true", help="tabela com a situação por extenso")
    args = parser.parse_args()

    resultados = []
    for nome in args.nomes:
        fqdn = nome.lower() if "." in nome else f"{nome.lower()}.{args.sufixo}"
        try:
            dados = consultar_com_espera(fqdn)
            status = dados.get("status")
            item = {
                "dominio": fqdn,
                "status": status,
                "situacao": STATUS.get(status, f"status {status} (conferir no registro.br)"),
                "expira": dados.get("expires-at", ""),
                "sugestoes": dados.get("suggestions", []),
            }
        except Exception as erro:  # rede, resposta inesperada
            item = {"dominio": fqdn, "status": None, "situacao": f"erro: {erro}", "expira": "", "sugestoes": []}
        resultados.append(item)
        time.sleep(PAUSA)

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return
    if args.markdown:
        print("| Domínio | Situação | Observação |")
        print("|---|---|---|")
        for r in resultados:
            situacao = SITUACAO_CURTA.get(r["status"], r["situacao"])
            if r["status"] in (0, 1):
                situacao = f"**{situacao}**"
            observacao = f"expira em {r['expira'][:10]}" if r["expira"] else ""
            print(f"| {r['dominio']} | {situacao} | {observacao} |")
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
