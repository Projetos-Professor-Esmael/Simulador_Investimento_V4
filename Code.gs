// Envio automático de e-mail: Google Apps Script (grátis). Implante como Web App.
// O corpo do e-mail é montado AQUI (indicadores e manchetes do seu news.json), nunca vem da página,
// para ninguém usar sua conta para enviar texto arbitrário.
const NEWS_URL = "https://SEU-USUARIO.github.io/SEU-REPOSITORIO/news.json";  // troque pelo seu endereço
const MAX_POR_DIA = 60;   // teto global (conta gmail.com permite cerca de 100 destinatários por dia)

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    const email = String(d.email || "").trim().toLowerCase();
    if (d.website) return ok();                                                   // isca anti-robô
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 120) return ok();
    const cache = CacheService.getScriptCache();
    if (cache.get("e:" + email)) return ok();                                     // 1 envio por e-mail a cada 6 h
    const lock = LockService.getScriptLock(); lock.waitLock(5000);
    const props = PropertiesService.getScriptProperties();
    const dia = Utilities.formatDate(new Date(), "America/Sao_Paulo", "yyyyMMdd");
    const n = Number(props.getProperty("n_" + dia) || 0);
    if (n >= MAX_POR_DIA) { lock.releaseLock(); return ok(); }
    props.setProperty("n_" + dia, String(n + 1)); lock.releaseLock();
    cache.put("e:" + email, "1", 21600);
    const j = JSON.parse(UrlFetchApp.fetch(NEWS_URL).getContentText());
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const nm = { selic: "Selic meta (% a.a.)", cdi: "CDI (% a.a.)", ipca12: "IPCA 12m (%)", dolar: "Dólar venda (R$)" };
    const ind = j.indicators || {}, it = (j.items || []).slice(0, 8);
    let txt = "Relatório de mercado de " + dia + "\n\n", htm = "<h2>Relatório de mercado</h2><ul>";
    Object.keys(nm).forEach(k => { if (ind[k]) { txt += nm[k] + ": " + ind[k].v + " (" + ind[k].d + ")\n"; htm += "<li>" + nm[k] + ": <b>" + ind[k].v + "</b> (" + ind[k].d + ")</li>"; } });
    htm += "</ul><h3>Manchetes</h3><ul>"; txt += "\nManchetes:\n";
    it.forEach(i => { txt += "- " + i.title + " (" + i.source + ")\n  " + i.link + "\n"; htm += '<li><a href="' + esc(i.link) + '">' + esc(i.title) + "</a> (" + esc(i.source) + ")</li>"; });
    const rod = "Você recebeu isto porque este endereço foi digitado no simulador. Se não foi você, ignore: não enviaremos mais nada. Material educacional, não é recomendação de investimento.";
    MailApp.sendEmail({ to: email, subject: "Relatório de mercado " + dia, body: txt + "\n" + rod, htmlBody: htm + "</ul><p style='color:#666;font-size:12px'>" + rod + "</p>", name: "Mesa de Decisão" });
  } catch (err) { console.error(err); }
  return ok();
}
function ok() { return ContentService.createTextOutput("ok"); }
function teste() { doPost({ postData: { contents: JSON.stringify({ email: Session.getActiveUser().getEmail() }) } }); }  // rode 1 vez para autorizar
