#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Acha (e opcionalmente remove) botoes/links de checkout OCULTOS ou herdados do
original que sobraram no HTML clonado. O reveal por timer do original
(.esconder, display:none, hidden, setTimeout) esconde o botao mas ele continua
no codigo — e reaparece se algum script/CSS for importado junto.

Uso:
  python limpar_ocultos.py index.html                 # so lista
  python limpar_ocultos.py index.html --allow-id oferta   # ignora o botao NOSSO (dentro de #oferta)
  python limpar_ocultos.py index.html --remove [--out limpo.html]

Sai com codigo 1 se sobrou algo (use como gate antes do deploy).
"""
import argparse
import re
import sys
from html.parser import HTMLParser

CHECKOUT_DOMAINS = [
    "payt.com", "hotmart", "kiwify", "eduzz", "monetizze", "braip", "perfectpay",
    "yampi", "cartpanda", "ticto", "pay.", "checkout.", "pagar.me", "appmax",
    "greenn", "doppus", "lastlink", "stripe.com", "mercadopago", "paypal",
]
CTA_TEXT = re.compile(r"\b(comprar|quero|garantir|garanta|adquirir|acessar|assinar|checkout|finalizar)\b", re.I)
HIDDEN_STYLE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?![.\d])", re.I)
HIDDEN_CLASS_NAMES = {"esconder", "hidden", "d-none", "oculto", "hide", "invisible", "is-hidden"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def css_hidden_classes(html):
    """Classes que o proprio <style> da pagina define como display:none."""
    found = set(HIDDEN_CLASS_NAMES)
    for style in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I):
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", style):
            if HIDDEN_STYLE.search(body):
                found.update(re.findall(r"\.([A-Za-z0-9_-]+)", sel))
    return found


class Scanner(HTMLParser):
    def __init__(self, html, hidden_classes, allow_ids):
        super().__init__(convert_charrefs=False)
        self.html = html
        self.hidden_classes = hidden_classes
        self.allow_ids = set(allow_ids)
        self.line_starts = [0]
        for m in re.finditer("\n", html):
            self.line_starts.append(m.end())
        self.stack = []   # (tag, hidden, allowed)
        self.cur = None   # elemento <a>/<button> aberto: dict
        self.hits = []

    def off(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        hidden = (
            "hidden" in a
            or a.get("aria-hidden") == "true"
            or bool(HIDDEN_STYLE.search(a.get("style") or ""))
            or bool(classes & self.hidden_classes)
        )
        allowed = a.get("id") in self.allow_ids
        self.stack.append((tag, hidden, allowed))
        if tag in ("a", "button") and self.cur is None:
            href = (a.get("href") or a.get("data-href") or a.get("formaction") or "").lower()
            self.cur = {
                "tag": tag, "start": self.off(), "line": self.getpos()[0],
                "href": href, "id": a.get("id"), "text": "",
                "hidden_chain": any(h for _, h, _ in self.stack),
                "allowed": any(al for _, _, al in self.stack),
                "depth": len(self.stack),
            }

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"] += data

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.cur is not None and tag == self.cur["tag"] and len(self.stack) == self.cur["depth"]:
            end = self.html.find(">", self.off()) + 1
            c = self.cur
            self.cur = None
            is_checkout = any(d in c["href"] for d in CHECKOUT_DOMAINS)
            looks_cta = bool(CTA_TEXT.search(c["text"])) or (c["id"] or "").lower().startswith("btn")
            if (is_checkout or looks_cta) and not c["allowed"]:
                motivo = []
                if c["hidden_chain"]:
                    motivo.append("OCULTO")
                if is_checkout:
                    motivo.append("link de checkout")
                if looks_cta and not is_checkout:
                    motivo.append("texto/id de CTA")
                self.hits.append({**c, "end": end, "motivo": ", ".join(motivo)})
        while self.stack:
            if self.stack.pop()[0] == tag:
                break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--allow-id", action="append", default=[],
                    help="id do container do botao NOSSO (ex: oferta); tudo dentro dele e ignorado")
    ap.add_argument("--remove", action="store_true", help="remove os elementos encontrados")
    ap.add_argument("--out", help="arquivo de saida do --remove (padrao: sobrescreve)")
    args = ap.parse_args()

    html = open(args.arquivo, encoding="utf-8", errors="ignore").read()
    sc = Scanner(html, css_hidden_classes(html), args.allow_id)
    sc.feed(html)

    # Remove so os mais externos (evita sobreposicao)
    hits = sorted(sc.hits, key=lambda h: h["start"])
    print(f"=== BOTOES/LINKS DE CHECKOUT SOBRANDO ({len(hits)}) ===")
    for h in hits:
        txt = re.sub(r"\s+", " ", h["text"]).strip()[:50]
        print(f"  linha {h['line']:>5} <{h['tag']}> [{h['motivo']}] href={h['href'][:70] or '-'} texto='{txt}'")

    inline = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)[^;]{0,80}(?:style\.display|classList\.(?:remove|add))", html)
    if inline:
        print("\n=== JS QUE REVELA ELEMENTOS DO ORIGINAL (revise e remova) ===")
        for i in sorted(set(inline)):
            print(f"  - #{i}")

    if args.remove and hits:
        out, last = [], 0
        for h in hits:
            if h["start"] < last:
                continue
            out.append(html[last:h["start"]])
            last = h["end"]
        out.append(html[last:])
        dest = args.out or args.arquivo
        open(dest, "w", encoding="utf-8").write("".join(out))
        print(f"\nRemovidos {len(hits)} elemento(s) -> {dest}. Rode de novo pra confirmar 0.")
        sys.exit(0)

    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
