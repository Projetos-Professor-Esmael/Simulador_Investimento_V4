"""Gera news.json (notícias + imagens + indicadores oficiais do BCB). Sem API paga.
Cada item: título, link original, fonte, data, imagem (se houver), categoria, ativos
possivelmente afetados e quantas fontes cobriram o fato."""
import json, os, sys, re, html, datetime as dt, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

UA = {"User-Agent": "Mozilla/5.0 (compatible; mesa-decisao-bot)"}
FEEDS = {
    "Agência Brasil": "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml",
    "g1 Economia": "https://g1.globo.com/rss/g1/economia/",
    "InfoMoney": "https://www.infomoney.com.br/feed/",
    "Google Notícias": "https://news.google.com/rss/search?q=Ibovespa+OR+Selic+OR+d%C3%B3lar+OR+Copom+when:2d&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Banco Central": "https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias",
}
SGS = {"selic": 432, "cdi": 4389, "ipca12": 13522, "dolar": 1}
STOP = set("de da do das dos a o e em para por com que um uma no na os as ao à se mais após diz vai".split())
CATS = [("Juros e inflação", r"selic|juros|copom|infla|ipca|\bcdi\b|tesouro|banco central"),
        ("Governo e fiscal", r"fiscal|governo|c[âa]mara|senado|lula|haddad|imposto|tribut|or[çc]amento|congresso|\bpl\b|\bpt\b"),
        ("Câmbio", r"d[óo]lar|c[âa]mbio|\beuro\b|moeda"),
        ("Empresas", r"petrobras|\bvale\b|ita[úu]|bradesco|a[çc][ãa]o|a[çc][õo]es|ibovespa|\bb3\b|dividendo|lucro|balan[çc]o|empresa|banco|cvm")]
ASSETS = [("acoes", r"a[çc][ãa]o|a[çc][õo]es|ibovespa|\bb3\b|dividendo|lucro|balan[çc]o|petrobras|\bvale\b|ita[úu]|bradesco|cvm|d[óo]lar"),
          ("selic", r"selic|copom|juros|\bcdi\b"),
          ("ipca", r"infla|ipca|fiscal|d[ée]ficit|gasto|juros futuros|tesouro")]

def tokens(t): return {w for w in re.findall(r"\w+", t.lower()) if w not in STOP and len(w) > 2}
def classify(t):
    low = t.lower()
    cat = next((c for c, rx in CATS if re.search(rx, low)), "Geral")
    return cat, [k for k, rx in ASSETS if re.search(rx, low)]
def parse_date(s):
    try: return parsedate_to_datetime(s).astimezone(dt.timezone.utc)
    except Exception:
        try: return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception: return None
def img_of(it):
    for e in it.iter():
        tag = e.tag.split("}")[-1]
        if tag in ("content", "thumbnail") and e.get("url") and not e.get("type", "").startswith("video"): return e.get("url")
        if tag == "enclosure" and e.get("type", "").startswith("image"): return e.get("url")
    blob = (it.findtext("description") or "") + "".join((e.text or "") for e in it if e.tag.endswith("encoded"))
    m = re.search(r'<img[^>]+src=["\']([^"\']+)', html.unescape(blob))
    return m.group(1) if m else ""
def og_image(link):
    if "news.google.com" in link: return ""
    try:
        h = urllib.request.urlopen(urllib.request.Request(link, headers=UA), timeout=8).read(250000).decode("utf-8", "ignore")
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', h) or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', h)
        return html.unescape(m.group(1)) if m else ""
    except Exception: return ""
def fetch(name, url):
    out = []
    try:
        root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read())
        for it in root.iter("item"):
            t = (it.findtext("title") or "").strip(); l = (it.findtext("link") or "").strip(); d = parse_date(it.findtext("pubDate") or "")
            src = (it.findtext("source") or name).strip()
            if name == "Google Notícias": t = re.sub(r"\s+-\s+[^-]+$", "", t)
            if t and l.startswith("http") and d:
                out.append({"title": t, "link": l, "source": src, "published": d.isoformat(), "image": img_of(it)})
    except Exception as e:
        print("falha em", name, e)
    print(f"{name}: {len(out)} itens")
    return out
def gnews(key):
    out = []
    try:
        q = urllib.parse.urlencode({"q": "Ibovespa OR Selic OR Copom OR dólar", "lang": "pt", "country": "br", "max": 10, "apikey": key})
        for a in json.load(urllib.request.urlopen("https://gnews.io/api/v4/search?" + q, timeout=25))["articles"]:
            d = parse_date(a["publishedAt"])
            if d: out.append({"title": a["title"], "link": a["url"], "source": a["source"]["name"], "published": d.isoformat(), "image": a.get("image") or ""})
    except Exception as e: print("falha em GNews", e)
    print(f"GNews: {len(out)} itens")
    return out
def sgs(n):
    try:
        u = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{n}/dados/ultimos/1?formato=json"
        j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))[0]
        return {"v": float(j["valor"]), "d": j["data"]}
    except Exception as e:
        print("falha SGS", n, e); return None

def main():
    items = [i for n, u in FEEDS.items() for i in fetch(n, u)]
    if os.environ.get("GNEWS_KEY"): items += gnews(os.environ["GNEWS_KEY"])
    cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)
    items = sorted([i for i in items if dt.datetime.fromisoformat(i["published"]) > cut], key=lambda i: i["published"], reverse=True)
    groups = []
    for i in items:
        tk = tokens(i["title"])
        for g in groups:
            if len(tk & g["tk"]) / max(1, len(tk | g["tk"])) > 0.45 and i["source"] not in g["srcs"]:
                g["srcs"].add(i["source"]); g["item"]["image"] = g["item"]["image"] or i["image"]; break
        else: groups.append({"item": dict(i), "tk": tk, "srcs": {i["source"]}})
    res = []
    for g in groups:
        i = g["item"]; i["sources"] = len(g["srcs"]); i["category"], i["assets"] = classify(i["title"]); res.append(i)
    res.sort(key=lambda i: (i["sources"] > 1, i["published"]), reverse=True)
    res = res[:60]
    for i in [x for x in res if not x["image"]][:20]: i["image"] = og_image(i["link"])
    for i in res:
        if not i["image"].startswith("https://"): i["image"] = ""
    ind = {k: v for k, v in ((k, sgs(n)) for k, n in SGS.items()) if v}
    if not res: sys.exit("Nenhuma notícia coletada: veja as mensagens de falha acima.")
    json.dump({"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "indicators": ind, "items": res},
              open("news.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(res), "itens;", sum(1 for i in res if i["image"]), "com imagem")

if __name__ == "__main__": main()
