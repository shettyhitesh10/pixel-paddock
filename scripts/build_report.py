"""Generate the user's retro HTML progress output from recorded work and sourced data."""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    data = json.loads((ROOT / 'dist/data/content.json').read_text())
    progress = json.loads((ROOT / 'dist/data/progress.json').read_text())
    esc = lambda value: html.escape(str(value))
    font = base64.b64encode((ROOT / 'dist/assets/paddock-pixel.woff').read_bytes()).decode()
    metrics = ''.join(f'<div class="metric"><strong>{len(data.get(k, []))}</strong><span>{k}</span></div>' for k in ['drivers', 'teams', 'principals', 'news', 'comments'])
    tasks = ''.join(f'<tr><td><span class="status {esc(t["status"])}">{esc(t["status"])}</span></td><td>{esc(t["task"])}</td><td>{esc(t["evidence"])}</td></tr>' for t in progress['tasks'])
    items = lambda key: ''.join(f'<li>{esc(x)}</li>' for x in progress.get(key, []))
    history = ''.join(f'<li><time>{esc(x["date"])}</time> — {esc(x["text"])}</li>' for x in progress.get('history', []))
    css = '''@font-face{font-family:PaddockPixel;src:url("data:font/woff;base64,FONT") format("woff")}*{box-sizing:border-box}:root{color-scheme:dark}body{margin:0;background:#081020;color:#dfebff;font:15px/1.9 PaddockPixel,monospace;background-image:linear-gradient(#14264a 1px,transparent 1px),linear-gradient(90deg,#14264a 1px,transparent 1px);background-size:16px 16px}main{max-width:1120px;margin:auto;padding:40px 24px}a{color:#ffce43;text-decoration:none}a:hover{color:#fff0b0}a:focus-visible{outline:3px solid #ffce43;outline-offset:5px}.brand{font-size:20px}.eyebrow{font-size:10px;color:#82ade8;margin-top:35px}h1{font-size:34px;line-height:1.6;color:#ffce43;margin:17px 0;text-shadow:3px 3px #020719;font-weight:400}h2{font-size:19px;color:#ffce43;margin:0 0 18px;font-weight:400}p{font-size:12px;color:#a0b9de;max-width:900px}.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:28px 0}.metric,.panel{background:#132b50;border:3px solid;border-color:#5c8ece #030a19 #030a19 #5c8ece;box-shadow:3px 3px #020617}.metric{padding:20px 16px}.metric strong{display:block;font-size:28px;font-weight:400;color:#ffce43}.metric span{font-size:9px}.panel{padding:25px;margin:22px 0}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:10px}th,td{padding:14px 10px;border-bottom:2px solid #07182e;text-align:left;vertical-align:top}th{font-weight:400;color:#7b9ecd;font-size:8px}td:first-child{width:100px}td:last-child{color:#9db7db}.status{font-size:8px;padding:5px 7px;background:#264675;color:#9fc5f4}.status.complete{color:#74efb8}.status.pending{color:#ffce43}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.grid .panel{margin:0}li{font-size:11px;color:#9db7db;margin:12px 0}ul{padding-left:18px}time{color:#9ac4fa}footer{font-size:7px;color:#7697c6;margin-top:35px}@media(max-width:650px){main{padding:28px 14px}.metrics{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.panel{padding:18px 14px}h1{font-size:25px}td{min-width:130px;font-size:9px}h2{font-size:17px}}'''.replace('FONT',font)
    markup = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pixel Paddock · Build save file</title><style>{css}</style></head><body><main><a class="brand" href="index.html">PIXEL PADDOCK</a><div class="eyebrow">BUILD SAVE FILE · RELEASE 04</div><h1>The paddock, rebuilt.</h1><p>Completed work, checks and remaining tasks for the retro Formula 1 project.</p><p>Report updated: <time>{esc(progress['updatedAt'])}</time><br>Racing snapshot: <time>{esc(data.get('meta',{}).get('updatedAt','Unknown'))}</time></p><div class="metrics">{metrics}</div><section class="panel"><h2>Release checklist</h2><div class="table-wrap"><table><thead><tr><th>STATE</th><th>WORK</th><th>EVIDENCE</th></tr></thead><tbody>{tasks}</tbody></table></div></section><div class="grid"><section class="panel"><h2>Validation</h2><ul>{items('validation')}</ul></section><section class="panel"><h2>Delivery limits</h2><ul>{items('limitations')}</ul></section></div><section class="panel"><h2>Next lap</h2><p>{esc(progress['nextStep'])}</p><p>{esc(progress['schedule'])}</p></section><section class="panel"><h2>Build history</h2><ul>{history}</ul></section><a href="index.html">← Enter the paddock</a><footer>ORIGINAL FAN PROJECT · SOURCE LINKS IN THE DASHBOARD · ALL TIMES UTC</footer></main></body></html>'''
    (ROOT / 'dist/progress.html').write_text(markup)
    print(json.dumps({'report':str(ROOT / 'dist/progress.html'), 'updatedAt':progress['updatedAt']}))


if __name__ == '__main__':
    build()
