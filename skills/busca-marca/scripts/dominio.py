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

Registrado com a data de expiração já passada (em Brasília) sai como
"registrado, expirado": está no prazo de renovação, pode ser liberado depois,
e nunca conta como livre. No --json, o campo "expirado" diz isso.
"""

import argparse
import json
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone

URL = "https://registro.br/v2/ajax/avail/raw/{}"
# Brasília não tem horário de verão desde 2019: UTC-3 fixo é o mesmo que
# America/Sao_Paulo, e serve no Windows sem o pacote tzdata.
UTC_MENOS_3 = timezone(timedelta(hours=-3), "UTC-3")
OBS_EXPIRADO = "expirou em {}; em prazo de renovação, pode ser liberado depois"
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


def fuso_de_brasilia():
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo("America/Sao_Paulo")
    except Exception:  # Windows sem tzdata: ZoneInfoNotFoundError
        return UTC_MENOS_3


def hoje_em_brasilia() -> date:
    return datetime.now(fuso_de_brasilia()).date()


def data_de_expiracao(expira: str | None) -> date | None:
    """A data (em Brasília) do expires-at do registro.br, ou None se não houver."""
    if not expira:
        return None
    texto = expira.strip().replace("Z", "+00:00")
    try:
        quando = datetime.fromisoformat(texto)
    except ValueError:
        try:
            return date.fromisoformat(texto[:10])
        except ValueError:
            return None
    if quando.tzinfo is None:
        return quando.date()
    return quando.astimezone(fuso_de_brasilia()).date()


def esta_expirado(expira: str | None, hoje: date | None = None) -> bool:
    """Verdadeiro quando a data de expiração já passou (antes de hoje, em Brasília).

    Domínio registrado e expirado ainda tem dono: está no prazo de renovação e
    só pode entrar em liberação depois. Nunca é livre.
    """
    vence = data_de_expiracao(expira)
    if vence is None:
        return False
    return vence < (hoje or hoje_em_brasilia())


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


def montar_item(fqdn: str, dados: dict, hoje: date | None = None) -> dict:
    status = dados.get("status")
    expira = dados.get("expires-at", "")
    expirado = status == 2 and esta_expirado(expira, hoje)
    situacao = STATUS.get(status, f"status {status} (conferir no registro.br)")
    if expirado:
        situacao = "registrado, expirado (em prazo de renovação; pode ser liberado depois)"
    return {
        "dominio": fqdn,
        "status": status,
        "situacao": situacao,
        "expira": expira,
        "expirado": expirado,
        "sugestoes": dados.get("suggestions", []),
    }


def linha_da_tabela(r: dict) -> tuple[str, str]:
    """Situação e Observação da tabela --markdown."""
    vence = data_de_expiracao(r["expira"])
    if r["expirado"]:
        return "registrado, expirado", OBS_EXPIRADO.format(vence.isoformat())
    situacao = SITUACAO_CURTA.get(r["status"], r["situacao"])
    if r["status"] in (0, 1):
        situacao = f"**{situacao}**"
    return situacao, f"expira em {vence.isoformat()}" if vence else ""


def linha_de_texto(r: dict) -> str:
    vence = data_de_expiracao(r["expira"])
    linha = f"{r['dominio']:<32} "
    if r["expirado"]:
        return linha + f"registrado, expirado ({OBS_EXPIRADO.format(vence.isoformat())})"
    linha += r["situacao"]
    if vence:
        linha += f" (expira {vence.isoformat()})"
    return linha


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
            item = montar_item(fqdn, dados)
        except Exception as erro:  # rede, resposta inesperada
            item = {
                "dominio": fqdn,
                "status": None,
                "situacao": f"erro: {erro}",
                "expira": "",
                "expirado": False,
                "sugestoes": [],
            }
        resultados.append(item)
        time.sleep(PAUSA)

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return
    if args.markdown:
        print("| Domínio | Situação | Observação |")
        print("|---|---|---|")
        for r in resultados:
            situacao, observacao = linha_da_tabela(r)
            print(f"| {r['dominio']} | {situacao} | {observacao} |")
        return
    for r in resultados:
        print(linha_de_texto(r))
        if args.sugestoes and r["sugestoes"]:
            print(f"    livre também em: {', '.join(r['sugestoes'])}")


if __name__ == "__main__":
    main()
