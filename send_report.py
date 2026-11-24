"""Envia por e-mail o relatório diário de mercado (indicadores do BCB + manchetes de news.json).
Credenciais vêm dos Secrets do GitHub: SMTP_USER, SMTP_PASS, MAIL_TO (lista separada por vírgula).
Opcionais: SMTP_HOST (padrão smtp.gmail.com), SMTP_PORT (padrão 465)."""
import json, os, smtplib, ssl, datetime as dt
from email.message import EmailMessage
from html import escape

d = json.load(open("news.json", encoding="utf-8"))
ind, items = d.get("indicators", {}), d.get("items", [])[:10]
names = {"selic": "Selic meta (% a.a.)", "cdi": "CDI (% a.a.)", "ipca12": "IPCA 12m (%)", "dolar": "Dólar venda (R$)"}
hoje = dt.date.today().strftime("%d/%m/%Y")
txt, htm = [f"Relatório diário de mercado, {hoje}", ""], [f"<h2>Relatório diário de mercado, {hoje}</h2><ul>"]
for k, n in names.items():
    if k in ind:
        txt.append(f"{n}: {ind[k]['v']} ({ind[k]['d']})"); htm.append(f"<li>{n}: <b>{ind[k]['v']}</b> ({ind[k]['d']})</li>")
htm.append("</ul><h3>Manchetes</h3><ul>"); txt += ["", "Manchetes:"]
for i in items:
    sel = f" [{i['sources']} fontes]" if i.get("sources", 1) > 1 else ""
    txt.append(f"- {i['title']} ({i['source']}){sel}\n  {i['link']}")
    htm.append(f"<li><a href=\"{escape(i['link'])}\">{escape(i['title'])}</a> ({escape(i['source'])}){sel}</li>")
htm.append("</ul><p style='color:#666;font-size:12px'>Material educacional, não é recomendação de investimento. Confira sempre na fonte original.</p>")
user, pwd = os.environ["SMTP_USER"], os.environ["SMTP_PASS"]
msg = EmailMessage()
msg["Subject"], msg["From"], msg["To"] = f"Relatório diário de mercado {hoje}", user, os.environ["MAIL_TO"]
msg.set_content("\n".join(txt)); msg.add_alternative("".join(htm), subtype="html")
with smtplib.SMTP_SSL(os.environ.get("SMTP_HOST", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", "465")), context=ssl.create_default_context()) as s:
    s.login(user, pwd); s.send_message(msg)
print("E-mail enviado para", os.environ["MAIL_TO"])
