#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa um script JS suspeito de ser o "decisor" de um cloaker: o codigo que
decide, no navegador, se o visitante ve a fachada ou a oferta real.

A analise deste script e ESTATICA: ele so le o texto do alvo. A excecao e
--webcrack: o webcrack avalia o decodificador de strings do alvo dentro de um
sandbox proprio (isolated-vm) para desfazer a ofuscacao. O que sai:
  - strings em claro (com escapes \\xNN / \\uNNNN e base64 decodificados)
  - o que o script le do navegador (fingerprint)
  - para onde ele fala (fetch, XHR, sendBeacon, WebSocket)
  - como ele entregaria outra pagina (redirect, troca de DOM, document.write)
  - estado que ele guarda (cookies, storage) e truques anti-analise
  - assinaturas de cloakers conhecidos, URLs, caminhos e portas
  - um veredito: DECISOR PROVAVEL / SUSPEITO / SEM INDICIOS

Se o codigo estiver ofuscado (obfuscator.io e parecidos), --webcrack tenta
desofuscar antes com o `webcrack` (github.com/j4k0xb/webcrack) e analisa o
resultado junto. So usa o que ja esta instalado; --npx deixa baixar via npx e
so deve ser passado quando o usuario autorizou instalar.

Limite conhecido: ofuscacao em VM (bytecode proprio) nao e desfeita por
desofuscador nenhum daqui. Nesse caso o relatorio traz so o que esta em claro
e avisa — nao presuma que "nao achei" significa "nao tem".

Uso:
  python analisar_script_decisor.py script.js
  python analisar_script_decisor.py script.js --out pasta/        # grava relatorio .md
  python analisar_script_decisor.py script.js --webcrack --out pasta/
  python analisar_script_decisor.py script.js --webcrack --npx --out pasta/
"""
import argparse
import base64
import os
import re
import shutil
import subprocess
import sys

SINAIS = {
    "fingerprint": [
        r"userAgent\b", r"userAgentData", r"getHighEntropyValues", r"\bwebdriver\b",
        r"maxTouchPoints", r"getBattery", r"chargingTime", r"dischargingTime",
        r"DeviceMotionEvent", r"rotationRate", r"DeviceOrientationEvent",
        r"UNMASKED_RENDERER_WEBGL", r"WEBGL_debug_renderer_info", r"getContext",
        r"hardwareConcurrency", r"deviceMemory", r"\bplugins\b", r"\blanguages?\b",
        r"timeZone", r"getTimezoneOffset", r"devicePixelRatio", r"colorDepth",
        r"\bscreen\b", r"\bplatform\b", r"\breferrer\b", r"ontouchstart",
    ],
    "rede": [
        r"\bfetch\b", r"XMLHttpRequest", r"sendBeacon", r"WebSocket", r"EventSource",
        r"credentials", r"no-store", r"referrerPolicy",
    ],
    "entrega": [
        r"location\.(replace|assign|href)", r"\b(replace|assign)\b", r"http-equiv",
        r"document\.(write|open)", r"\binnerHTML\b", r"\bouterHTML\b",
        r"pushState", r"replaceState", r"createElement", r"insertAdjacentHTML",
    ],
    "ocultacao": [
        r"opacity['\"\]\s]*=\s*['\"]0", r"visibility", r"display['\"\]\s]*[:=]\s*['\"]?none",
    ],
    "estado": [r"\bcookie\b", r"localStorage", r"sessionStorage", r"indexedDB"],
    "anti_analise": [
        r"\bdebugger\b", r"\beval\b", r"(?-i:\bFunction\()", r"toString\(\)",
        r"devtools", r"outerWidth", r"outerHeight", r"(?-i:new Proxy\b)", r"__nightmare",
        r"_phantom", r"callPhantom", r"\$cdc_", r"HeadlessChrome", r"\bselenium\b",
        r"\bpuppeteer\b", r"\bplaywright\b",
    ],
    "assinatura_cloaker": [
        r"cloack?er", r"isHideQueryParamsEnabled", r"TheWhiteRabbit", r"Cloakup",
        r"Adspect", r"Keitaro", r"\bBinom\b", r"HideClick", r"antispy", r"proxy-check",
        r"\ballowed\b", r"\bdenied\b", r"\bfunnel\b", r"pr[e3]s[e3]ll", r"sw[a4]p",
        r"white[_-]?page", r"black[_-]?page", r"safe[_-]?page", r"money[_-]?page",
    ],
}

RE_STRING = re.compile(r"""(["'`])((?:\\.|(?!\1)[^\\\n]){3,400})\1""")
RE_URL = re.compile(r"""(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?::\d+)?(?:/[^\s"'`<>\\)]*)?""")
RE_PATH = re.compile(r"""^/[A-Za-z0-9_\-./]{3,}$""")
RE_B64 = re.compile(r"^[A-Za-z0-9+/_-]{16,}={0,2}$")
PORTAS_CONHECIDAS = {"80", "443", "2052", "2053", "2082", "2083", "2086", "2087",
                     "2095", "2096", "8080", "8443", "8880"}
# so conta porta em lista curta de numeros ([443, 2053, ...]); numero solto e ruido
RE_LISTA_NUM = re.compile(r"\[\s*(\d{2,5}(?:\s*,\s*\d{2,5}){1,11})\s*\]")


def desescapar(s):
    s = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), s)
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    return s.replace("\\/", "/")


def tentar_b64(s):
    if not RE_B64.match(s):
        return None
    try:
        raw = base64.b64decode(s.replace("-", "+").replace("_", "/") + "=" * (-len(s) % 4))
        txt = raw.decode("utf-8")
    except Exception:
        return None
    imprimivel = sum(c.isprintable() for c in txt)
    return txt if txt and imprimivel / len(txt) > 0.95 else None


def extrair_strings(code):
    vistas, saida = set(), []
    for m in RE_STRING.finditer(code):
        s = desescapar(m.group(2))
        if s in vistas:
            continue
        vistas.add(s)
        saida.append(s)
        dec = tentar_b64(s)
        if dec and dec not in vistas:
            vistas.add(dec)
            saida.append(dec)
    return saida


def analisar(code):
    strings = extrair_strings(code)
    alvo = desescapar(code) + "\n" + "\n".join(strings)
    achados = {}
    for cat, padroes in SINAIS.items():
        hits = sorted({m.group(0) for p in padroes for m in re.finditer(p, alvo, re.I)})
        if hits:
            achados[cat] = hits
    urls = sorted(set(RE_URL.findall(alvo)))
    caminhos = sorted({s for s in strings if RE_PATH.match(s)})
    portas = set()
    for lista in RE_LISTA_NUM.findall(code):
        nums = re.split(r"\s*,\s*", lista)
        if all(n in PORTAS_CONHECIDAS for n in nums):
            portas.update(nums)
    portas = sorted(portas, key=int)
    vm = bool(re.search(r"\bvm[x_]?[0-9a-f_]{4,}", code, re.I)) or (
        len(code) > 50000 and len(strings) < len(code) / 400
    )
    return {"strings": strings, "achados": achados, "urls": urls,
            "caminhos": caminhos, "portas": portas, "vm": vm}


def veredito(r):
    a = r["achados"]
    n_fp = len(a.get("fingerprint", []))
    fala_ou_entrega = bool(a.get("rede")) or bool(a.get("entrega"))
    if a.get("assinatura_cloaker") and fala_ou_entrega and n_fp >= 3:
        return "DECISOR PROVAVEL"
    if n_fp >= 5 and a.get("rede") and (a.get("entrega") or a.get("ocultacao")):
        return "DECISOR PROVAVEL"
    if n_fp >= 3 or a.get("assinatura_cloaker") or a.get("anti_analise"):
        return "SUSPEITO"
    return "SEM INDICIOS"


def rodar_webcrack(arquivo, out_dir, permitir_npx):
    exe = shutil.which("webcrack")
    cmd = [exe] if exe else None
    if not cmd and permitir_npx and shutil.which("npx"):
        cmd = [shutil.which("npx"), "--yes", "webcrack"]
    if not cmd:
        return None, "webcrack nao instalado (rode com --npx se o usuario autorizou instalar)"
    destino = os.path.join(out_dir, "webcrack-" + os.path.splitext(os.path.basename(arquivo))[0])
    try:
        p = subprocess.run(cmd + [arquivo, "-o", destino, "-f"],
                           capture_output=True, text=True, timeout=300)
    except Exception as e:
        return None, f"webcrack falhou: {e}"
    saida = os.path.join(destino, "deobfuscated.js")
    if p.returncode != 0 or not os.path.exists(saida):
        return None, f"webcrack saiu com codigo {p.returncode}: {(p.stderr or '').strip()[:300]}"
    return saida, "comando: " + " ".join(cmd + [arquivo, "-o", destino, "-f"])


def montar_relatorio(arquivo, r, v, nota_webcrack):
    L = [f"# Analise de script decisor: {os.path.basename(arquivo)}", "",
         f"- Veredito estatico: **{v}**",
         f"- Tamanho analisado: {r['tamanho']} bytes | strings em claro: {len(r['strings'])}"]
    if nota_webcrack:
        L.append(f"- Desofuscacao: {nota_webcrack}")
    if r["vm"]:
        L.append("- AVISO: parece ofuscado em VM. O que segue e so o que esta em claro; "
                 "a logica de decisao NAO foi verificada.")
    L.append("")
    nomes = {"fingerprint": "Le do navegador", "rede": "Fala com a rede",
             "entrega": "Pode entregar outra pagina", "ocultacao": "Esconde a pagina",
             "estado": "Guarda estado", "anti_analise": "Anti-analise",
             "assinatura_cloaker": "Assinaturas de cloaker"}
    for cat, titulo in nomes.items():
        if cat in r["achados"]:
            L.append(f"## {titulo}")
            L.append(", ".join(f"`{h}`" for h in r["achados"][cat]))
            L.append("")
    L.append("## URLs e dominios em claro")
    L.append("\n".join(f"- {u}" for u in r["urls"]) or "nenhum")
    L.append("")
    if r["caminhos"]:
        L.append("## Caminhos em claro")
        L.append("\n".join(f"- {c}" for c in r["caminhos"][:60]))
        L.append("")
    if r["portas"]:
        L.append("## Portas citadas")
        L.append(", ".join(r["portas"]))
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo")
    ap.add_argument("--out", help="pasta onde gravar o relatorio .md e a saida do webcrack")
    ap.add_argument("--webcrack", action="store_true", help="tentar desofuscar com webcrack antes")
    ap.add_argument("--npx", action="store_true", help="permite baixar o webcrack via npx (instala)")
    args = ap.parse_args()

    if not os.path.isfile(args.arquivo):
        print(f"arquivo nao encontrado: {args.arquivo}")
        sys.exit(2)
    code = open(args.arquivo, encoding="utf-8", errors="ignore").read()

    nota, sufixo = "", ""
    if args.webcrack:
        out_dir = args.out or os.path.dirname(os.path.abspath(args.arquivo))
        os.makedirs(out_dir, exist_ok=True)
        limpo, nota = rodar_webcrack(args.arquivo, out_dir, args.npx)
        if limpo:
            code += "\n" + open(limpo, encoding="utf-8", errors="ignore").read()
            nota = f"feita ({limpo}); {nota}"
            sufixo = "-webcrack"

    r = analisar(code)
    r["tamanho"] = os.path.getsize(args.arquivo)
    v = veredito(r)
    rel = montar_relatorio(args.arquivo, r, v, nota)
    print(rel)

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        destino = os.path.join(args.out, "decisor-" + os.path.basename(args.arquivo) + sufixo + ".md")
        with open(destino, "w", encoding="utf-8") as f:
            f.write(rel + "\n## Strings em claro\n" + "\n".join(f"- {s}" for s in r["strings"][:500]) + "\n")
        print(f"\nrelatorio gravado em {destino}")


if __name__ == "__main__":
    main()
