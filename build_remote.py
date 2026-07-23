#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Z snippet-elementor.html vyrobí SELF-HOSTED verziu (štýl Trustindex):
- widget.js  = celý widget (CSS + skeleton + JS + záložné dáta) — hostuje sa na CDN
- embed-wp.html = 2-riadkový kód do WordPressu, ktorý sa už NIKDY nemení
widget.js si sám stiahne čerstvé reviews-widget.json z rovnakého CDN priečinka."""
import os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(HERE, 'snippet-elementor.html')).read()

css = html.split('<style>')[1].split('</style>')[0]
js = html.split('<script>')[1].split('</script>')[0]
pre = html.split('<style>')[0]
m = re.search(r'<div class="zkr-wrap">(.*)</div>\s*$', pre, re.S)
skeleton = m.group(1).strip()

# IIFE -> funkcia s parametrom jsonUrl; ZKR_JSON_URL sa dosadí z loadera
js_fn = js.replace('(function(){', 'function ZKR_WIDGET(zkrJsonUrl){', 1)
js_fn = js_fn.rstrip()
assert js_fn.endswith('})();'), 'unexpected script tail'
js_fn = js_fn[:-len('})();')] + '}'
js_fn = js_fn.replace("var ZKR_JSON_URL = '';", "var ZKR_JSON_URL = zkrJsonUrl || '';", 1)

widget = ('/* Recenzie widget — Hotel Zlatý Kľúčik (self-hosted replika Trustindexu).\n'
          '   Embed vo WP sa nemení; dáta = reviews-widget.json vedľa tohto súboru.\n'
          '   Zdroj + cron: https://github.com/SlohGPT/zk-reviews-widget */\n'
          '(function(){\n'
          'var CSS=' + json.dumps(css) + ';\n'
          'var SKEL=' + json.dumps(skeleton) + ';\n'
          'var JSON_URL=(function(){var s=document.currentScript;\n'
          "  return (s&&s.src)? s.src.replace(/widget\\.js(\\?.*)?$/,'reviews-widget.json') : '';})();\n"
          + js_fn + '\n'
          'function zkrReady(fn){ if(document.readyState!==\'loading\') fn();\n'
          '  else document.addEventListener(\'DOMContentLoaded\',fn); }\n'
          'zkrReady(function(){\n'
          '  if(!document.querySelector(\'.zkr-wrap\')) return;\n'
          '  if(!document.getElementById(\'zkr-style\')){\n'
          '    var st=document.createElement(\'style\'); st.id=\'zkr-style\'; st.textContent=CSS;\n'
          '    document.head.appendChild(st);\n'
          '    var f=document.createElement(\'link\'); f.rel=\'stylesheet\';\n'
          '    f.href=\'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap\';\n'
          '    document.head.appendChild(f);\n'
          '  }\n'
          '  Array.prototype.forEach.call(document.querySelectorAll(\'.zkr-wrap\'),function(w){\n'
          '    if(!w.firstElementChild) w.innerHTML=SKEL; });\n'
          '  ZKR_WIDGET(JSON_URL);\n'
          '});\n'
          '})();\n')
open(os.path.join(HERE, 'widget.js'), 'w').write(widget)

embed = ('<!-- Recenzie — vlož RAZ do Elementor HTML widgetu; už sa nikdy nemení.\n'
         '     Nové recenzie + čísla chodí samé z GitHubu (cron každý pondelok). -->\n'
         '<div class="zkr-wrap"></div>\n'
         '<script src="https://cdn.jsdelivr.net/gh/SlohGPT/zk-reviews-widget@main/widget.js" defer></script>\n')
open(os.path.join(HERE, 'embed-wp.html'), 'w').write(embed)
print('WROTE widget.js (%d KB) + embed-wp.html' % (len(widget) // 1024))
