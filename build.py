#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the Trustindex-replica widget (tabs + summary + carousel) from reviews.json + meta.json.
Outputs: snippet-elementor.html (paste into Elementor HTML widget), preview.html, reviews-widget.json."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, 'reviews.json')))
meta = json.load(open(os.path.join(HERE, 'meta.json')))

def order(rows, cap):
    # CHRONOLOGICKY (najnovšie prvé) — dáta sú už zoradené podľa dátumu; relatívne dátumy
    # ("pred 2 dňami") sa prepočítavajú naživo pri každom načítaní stránky.
    return rows[:cap]

sel = {
    'all': order(data, 36),
    'google': order([r for r in data if r['source'] == 'google'], 30),
    'booking': order([r for r in data if r['source'] == 'booking'], 36),
    'tripadvisor': order([r for r in data if r['source'] == 'tripadvisor'], 10),
}
keep = ['name', 'location', 'avatar', 'rating', 'time', 'text', 'text_sk', 'source', 'images']
allids = {}
flat = []
for r in sel['all'] + sel['google'] + sel['booking'] + sel['tripadvisor']:
    k = (r['source'], r.get('name'), r.get('time'))
    if k not in allids:
        allids[k] = len(flat)
        flat.append({x: r.get(x) for x in keep})
IDX = {tab: [allids[(r['source'], r.get('name'), r.get('time'))] for r in rows] for tab, rows in sel.items()}
DATA = json.dumps(flat, ensure_ascii=False)
TABS = json.dumps(IDX, ensure_ascii=False)
META = json.dumps(meta, ensure_ascii=False)
print("cards:", len(flat), "| per tab:", {k: len(v) for k, v in IDX.items()})

COMPONENT = r'''<!-- ============================================================================ -->
<!-- RECENZIE — natívna replika Trustindexu (taby + súhrn + carousel) · zkr- -->
<!-- Dáta + čísla platform sú vložené nižšie. Obnova: refresh.py (viď README). -->
<!-- ============================================================================ -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">

<div class="zkr-wrap">
  <div class="zkr-headcard">
    <div class="zkr-tabs" role="tablist"></div>
    <div class="zkr-sum">
      <div class="zkr-sumL"></div>
      <a class="zkr-write" target="_blank" rel="noopener nofollow"></a>
    </div>
  </div>
  <div class="zkr-slider">
    <div class="zkr-viewport"><div class="zkr-track"></div></div>
    <button type="button" class="zkr-nav zkr-prev" aria-label="&#8249;"></button>
    <button type="button" class="zkr-nav zkr-next" aria-label="&#8250;"></button>
  </div>
</div>

<style>
  .zkr-wrap{ --zkr-vis:3; --zkr-i:0; position:relative; max-width:1140px; margin:0 auto;
    font-family:'Poppins',-apple-system,'Segoe UI',sans-serif; color:#fff; -webkit-font-smoothing:antialiased; }
  .zkr-wrap *{ box-sizing:border-box; margin:0; }
  /* armor: nech tému nič nepreštylizuje (obrázky, tlačidlá, odkazy) */
  .zkr-wrap img{ transform:none !important; filter:none !important; box-shadow:none !important;
    border:none !important; padding:0 !important; }
  .zkr-wrap button{ text-transform:none !important; letter-spacing:normal !important; }
  /* ---------- header card ---------- */
  .zkr-headcard{ background:#1a1a1a; border-radius:16px; margin-bottom:18px; overflow:hidden; }
  .zkr-tabs{ display:flex; gap:6px; padding:0 10px; border-bottom:1px solid #303030;
    overflow-x:auto; scrollbar-width:none; -webkit-overflow-scrolling:touch; }
  .zkr-tabs::-webkit-scrollbar{ display:none; }
  /* tab buttons — armored against theme button:hover/:focus styles (pink bleed) */
  .zkr-tab{ appearance:none; -webkit-appearance:none; background:transparent !important; border:none !important;
    border-bottom:2px solid transparent !important; border-radius:0 !important; box-shadow:none !important;
    text-shadow:none !important; outline:none; color:#fff !important; font-family:inherit; cursor:pointer;
    display:flex; align-items:center; gap:9px; padding:17px 14px 15px; font-size:16.5px; font-weight:500;
    white-space:nowrap; opacity:.92; flex:none; transition:opacity .2s ease; }
  .zkr-tab:hover,.zkr-tab:focus,.zkr-tab:active{ background:transparent !important; color:#fff !important;
    box-shadow:none !important; outline:none; opacity:1; }
  .zkr-tab:focus-visible{ outline:2px solid rgba(255,255,255,.35); outline-offset:-2px; }
  .zkr-tab.on{ border-bottom-color:#fff !important; font-weight:600; opacity:1; }
  .zkr-tab svg{ width:21px; height:21px; display:block; }
  .zkr-tab[data-k="tripadvisor"] svg{ width:24px; height:24px; }
  .zkr-plogo svg{ width:100%; height:100%; display:block; }
  .zkr-plogo.zkr-plogo-ta{ width:26px; height:26px; }
  .zkr-sum{ display:flex; align-items:center; justify-content:space-between; gap:14px; padding:15px 20px; }
  .zkr-sumL{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; min-width:0; }
  /* desktop: skupiny sú "priehľadné" (display:contents) = jeden riadok ako doteraz;
     na mobile sa z nich stanú 2 pevné riadky (titul / hviezdy+čísla) */
  .zkr-sumT,.zkr-sumS{ display:contents; }
  .zkr-sumL .zkr-plogo{ width:23px; height:23px; }
  .zkr-sumL .zkr-pname{ font-size:18px; font-weight:700; }
  .zkr-sumL .zkr-grade{ font-size:18px; font-weight:700; }
  .zkr-sumL .zkr-score{ font-size:18px; font-weight:700; }
  .zkr-sumL .zkr-sep{ color:#5a5a5a; font-size:17px; padding:0 2px; }
  .zkr-sumL .zkr-count{ font-size:17.5px; font-weight:600; white-space:nowrap; }
  .zkr-write{ flex:none; color:#fff !important; text-decoration:none !important; font-size:15.5px; font-weight:600;
    border:1.6px solid #fff !important; border-radius:10px; padding:11px 20px; background:transparent !important;
    box-shadow:none !important; transition:background .2s ease; }
  .zkr-write:visited,.zkr-write:focus,.zkr-write:active{ color:#fff !important; text-decoration:none !important; outline:none; }
  .zkr-write:hover{ background:rgba(255,255,255,.14) !important; color:#fff !important; }
  /* ---------- stars ---------- */
  .zkr-strow{ display:inline-flex; align-items:center; gap:2px; }
  .zkr-st{ position:relative; display:inline-block; }
  .zkr-st>svg{ display:block; width:100%; height:100%; }
  .zkr-stf{ position:absolute; left:0; top:0; height:100%; overflow:hidden; }
  .zkr-seal{ display:inline-block; margin-left:7px; }
  .zkr-seal svg{ display:block; }
  /* ---------- cards ---------- */
  .zkr-slider{ position:relative; }
  .zkr-viewport{ overflow:hidden; margin:0 -8px; }
  .zkr-track{ display:flex; flex-wrap:nowrap; align-items:stretch; will-change:transform;
    transform:translateX(calc(var(--zkr-i) * -100% / var(--zkr-vis))); transition:transform .35s ease-out; }
  .zkr-track.zkr-nt{ transition:none; }
  .zkr-item{ flex:0 0 auto; width:calc(100% / var(--zkr-vis)); padding:0 8px; }
  .zkr-inner{ background:#191919; border-radius:12px; padding:18px 18px 14px; height:100%;
    display:flex; flex-direction:column; position:relative; }
  .zkr-src{ position:absolute; top:16px; right:16px; }
  .zkr-src svg{ display:block; }
  .zkr-head{ display:flex; align-items:center; }
  .zkr-av{ width:40px; height:40px; border-radius:50%; margin-right:13px; flex:none; overflow:hidden;
    display:flex; align-items:center; justify-content:center; font-weight:600; font-size:16px; color:#fff; }
  .zkr-av img{ width:100%; height:100%; object-fit:cover; object-position:top; }
  .zkr-meta{ min-width:0; }
  .zkr-name{ font-weight:600; font-size:15px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; padding-right:26px; }
  .zkr-date{ font-size:13px; color:#8a8a8a; margin-top:1px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .zkr-rating{ margin-top:11px; display:flex; align-items:center; }
  .zkr-body{ display:flex; gap:12px; margin-top:10px; align-items:flex-start; }
  .zkr-text{ flex:1; min-width:0; font-size:14.5px; line-height:21px; height:84px;
    display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:4; overflow:hidden; word-break:break-word; }
  .zkr-text.zkr-exp{ -webkit-line-clamp:unset; height:auto; }
  .zkr-text.zkr-noTxt{ color:#d8d8d8; }
  .zkr-thumb{ flex:none; position:relative; width:96px; height:96px; border-radius:10px; overflow:hidden;
    cursor:pointer; transition:transform .2s ease; }
  .zkr-thumb:hover{ transform:scale(1.04); }
  .zkr-thumb img{ width:100%; height:100%; object-fit:cover; display:block; }
  .zkr-thumb .zkr-tmore{ position:absolute; inset:0; background:rgba(0,0,0,.45); color:#fff;
    display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:700;
    text-shadow:0 1px 8px rgba(0,0,0,.6); letter-spacing:.02em; }
  .zkr-thumbs-m{ display:none; }
  .zkr-thumbs-m img{ cursor:pointer; }
  /* ---------- lightbox ---------- */
  .zkr-lb{ position:fixed; inset:0; z-index:2147483000; display:flex; align-items:center; justify-content:center;
    background:rgba(8,8,8,.93); -webkit-backdrop-filter:blur(12px); backdrop-filter:blur(12px);
    opacity:0; transition:opacity .28s ease; font-family:'Poppins',sans-serif; }
  .zkr-lb.zkr-on{ opacity:1; }
  .zkr-lb-stage{ position:relative; max-width:90vw; max-height:84vh; display:flex; align-items:center; justify-content:center; }
  .zkr-lb-img{ max-width:90vw; max-height:78vh; border-radius:14px; box-shadow:0 30px 90px rgba(0,0,0,.75);
    transform:scale(.88) translateY(12px); opacity:0;
    transition:transform .38s cubic-bezier(.2,.85,.25,1), opacity .3s ease; }
  .zkr-lb.zkr-on .zkr-lb-img{ transform:scale(1) translateY(0); opacity:1; }
  .zkr-lb-img.zkr-lb-sw{ transform:scale(.97); opacity:0; transition:transform .16s ease-in, opacity .16s ease-in; }
  .zkr-lb-cap{ position:absolute; left:0; right:0; bottom:-44px; display:flex; align-items:center;
    justify-content:center; gap:12px; color:#fff; font-size:14px; }
  .zkr-lb-cap .zkr-lb-nm{ font-weight:600; }
  .zkr-lb-cap .zkr-lb-ct{ color:#9a9a9a; }
  .zkr-lb-x{ position:fixed; top:18px; right:18px; width:40px; height:40px; border:none !important; border-radius:50% !important;
    background:rgba(255,255,255,.12) !important; box-shadow:none !important; outline:none; appearance:none; -webkit-appearance:none;
    cursor:pointer; transition:background .2s ease, transform .2s ease; }
  .zkr-lb-x:hover,.zkr-lb-x:focus{ background:rgba(255,255,255,.24) !important; transform:rotate(90deg); outline:none; }
  .zkr-lb-x::before,.zkr-lb-x::after{ content:''; position:absolute; top:50%; left:50%; width:17px; height:2px;
    background:#fff; border-radius:2px; }
  .zkr-lb-x::before{ transform:translate(-50%,-50%) rotate(45deg); }
  .zkr-lb-x::after{ transform:translate(-50%,-50%) rotate(-45deg); }
  .zkr-lb-a{ position:fixed; top:50%; margin-top:-24px; width:48px; height:48px; border:none !important; border-radius:50% !important;
    background:rgba(255,255,255,.12) !important; box-shadow:none !important; outline:none; appearance:none; -webkit-appearance:none;
    cursor:pointer; transition:background .2s ease; }
  .zkr-lb-a:hover,.zkr-lb-a:focus{ background:rgba(255,255,255,.24) !important; outline:none; }
  .zkr-lb-a::before{ content:''; position:absolute; top:50%; left:50%; width:12px; height:12px;
    border-left:2.4px solid #fff; border-bottom:2.4px solid #fff; }
  .zkr-lb-prev{ left:20px; } .zkr-lb-prev::before{ transform:translate(-30%,-50%) rotate(45deg); }
  .zkr-lb-next{ right:20px; } .zkr-lb-next::before{ transform:translate(-70%,-50%) rotate(-135deg); }
  .zkr-lb-a[hidden]{ display:none; }
  @media(max-width:600px){ .zkr-lb-a{ width:40px; height:40px; margin-top:-20px; } .zkr-lb-prev{ left:8px; } .zkr-lb-next{ right:8px; }
    .zkr-lb-img{ max-width:94vw; border-radius:10px; } }
  .zkr-links{ margin-top:7px; display:flex; gap:14px; align-items:center; min-height:19px; }
  .zkr-more,.zkr-orig{ font-size:13.5px; color:#fff; opacity:.5; cursor:pointer; }
  .zkr-more{ visibility:hidden; }
  .zkr-more.on{ visibility:visible; }
  .zkr-more:hover,.zkr-orig:hover{ opacity:1; text-decoration:underline; }
  /* ---------- nav ---------- */
  .zkr-nav{ position:absolute; top:50%; margin-top:-16px; width:32px; height:32px; border-radius:50% !important;
    background:#f2f2f2 !important; border:none !important; cursor:pointer; z-index:3; padding:0;
    box-shadow:0 2px 10px rgba(0,0,0,.5) !important; outline:none; appearance:none; -webkit-appearance:none;
    transform:none !important; transition:background .2s ease, opacity .2s ease; }
  .zkr-nav:hover,.zkr-nav:focus,.zkr-nav:active{ background:#dfdfdf !important; outline:none; transform:none !important; }
  .zkr-nav::before{ content:''; position:absolute; top:50%; left:50%; width:9px; height:9px;
    border-left:2.2px solid #1c1c1c; border-bottom:2.2px solid #1c1c1c; }
  .zkr-prev{ left:-8px; }  .zkr-prev::before{ transform:translate(-30%,-50%) rotate(45deg); }
  .zkr-next{ right:-8px; } .zkr-next::before{ transform:translate(-70%,-50%) rotate(-135deg); }
  .zkr-nav.zkr-off{ opacity:0; pointer-events:none; }
  /* ---------- tablet ---------- */
  @media(max-width:1024px){ .zkr-wrap{ --zkr-vis:2; } }
  /* ---------- mobile (vlastný, krajší než Trustindex) ---------- */
  @media(max-width:600px){
    .zkr-wrap{ --zkr-vis:1; }
    .zkr-tab{ font-size:15px; padding:14px 11px 12px; }
    .zkr-sum{ flex-direction:column; align-items:center; text-align:center; gap:12px; padding:16px 14px; }
    /* 2 pevné riadky ako na Tripadvisor tabe: [logo · názov · Vynikajúce] / [hviezdy · 4,7 | N recenzií] */
    .zkr-sumL{ flex-direction:column; align-items:center; gap:8px; }
    .zkr-sumT,.zkr-sumS{ display:flex; align-items:center; justify-content:center; gap:9px; flex-wrap:wrap; }
    .zkr-write{ padding:10px 22px; }
    .zkr-body{ flex-direction:column; gap:0; }
    .zkr-thumb{ display:none; }
    .zkr-thumbs-m{ display:flex; gap:8px; margin-top:11px; }
    .zkr-thumbs-m img{ width:64px; height:64px; border-radius:9px; object-fit:cover; display:block; }
    .zkr-text{ font-size:14.5px; height:auto; max-height:105px; -webkit-line-clamp:5; }
    .zkr-text.zkr-exp{ max-height:none; }
    .zkr-track{ align-items:flex-start; }
    .zkr-inner{ height:auto; }
    .zkr-nav{ width:30px; height:30px; margin-top:-15px;
      transition:background .2s ease, opacity .2s ease, top .3s ease; }
    .zkr-prev{ left:2px; } .zkr-next{ right:2px; }
  }
</style>

<script>
(function(){
  // Voliteľné: URL na reviews-widget.json pre auto-aktualizáciu bez úprav Elementora.
  var ZKR_JSON_URL = '';
  var DATA = __DATA__;
  var TABS = __TABS__;
  var META = __META__;

  // ---------- i18n (SK / EN / DE — podľa GTranslate /en/ /de/ prefixu) ----------
  var L10N = {
    sk:{ all:'Všetky recenzie', write:'Napísať recenziu', more:'Čítaj viac', less:'Skryť',
         orig:'Zobraziť originál', trans:'Zobraziť preklad',
         reviews:'recenzií', onlyRating:'Tento používateľ zanechal iba hodnotenie.',
         verified:'Overená recenzia', g1:'Vynikajúce', g2:'Veľmi dobré', g3:'Dobré',
         today:'dnes', yest:'včera',
         d:function(n){return 'pred '+n+' dňami';}, w1:'pred týždňom', w:function(n){return 'pred '+n+' týždňami';},
         m1:'pred mesiacom', m:function(n){return 'pred '+n+' mesiacmi';}, y1:'pred rokom', y:function(n){return 'pred '+n+' rokmi';} },
    en:{ all:'All reviews', write:'Write a review', more:'Read more', less:'Hide',
         reviews:'reviews', onlyRating:'This user only left a rating.',
         verified:'Verified review', g1:'Excellent', g2:'Very good', g3:'Good',
         today:'today', yest:'yesterday',
         d:function(n){return n+' days ago';}, w1:'a week ago', w:function(n){return n+' weeks ago';},
         m1:'a month ago', m:function(n){return n+' months ago';}, y1:'a year ago', y:function(n){return n+' years ago';} },
    de:{ all:'Alle Bewertungen', write:'Bewertung schreiben', more:'Mehr lesen', less:'Ausblenden',
         reviews:'Bewertungen', onlyRating:'Dieser Gast hat nur eine Bewertung hinterlassen.',
         verified:'Verifizierte Bewertung', g1:'Hervorragend', g2:'Sehr gut', g3:'Gut',
         today:'heute', yest:'gestern',
         d:function(n){return 'vor '+n+' Tagen';}, w1:'vor einer Woche', w:function(n){return 'vor '+n+' Wochen';},
         m1:'vor einem Monat', m:function(n){return 'vor '+n+' Monaten';}, y1:'vor einem Jahr', y:function(n){return 'vor '+n+' Jahren';} }
  };
  var lang = /^\/en(\/|$)/.test(location.pathname)?'en':(/^\/de(\/|$)/.test(location.pathname)?'de':
             (/^en/.test(document.documentElement.lang||'')?'en':(/^de/.test(document.documentElement.lang||'')?'de':'sk')));
  var T = L10N[lang];
  function relDate(iso){
    if(!iso) return '';
    var then=new Date(iso).getTime(); if(isNaN(then)) return '';
    var d=Math.floor((Date.now()-then)/86400000);
    if(d<=0) return T.today; if(d===1) return T.yest;
    if(d<7) return T.d(d);
    if(d<11) return T.w1; if(d<31) return T.w(Math.round(d/7));
    if(d<46) return T.m1; if(d<330) return T.m(Math.max(2,Math.round(d/30)));
    if(d<550) return T.y1; return T.y(Math.floor(d/365));
  }
  function nfmt(n){ return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,' '); }
  function score(n){ var s=(Math.round(n*10)/10).toFixed(1); return lang==='en'?s:s.replace('.',','); }
  function grade(r5){ return r5>=4.5?T.g1:(r5>=4?T.g2:T.g3); }

  // ---------- SVG ----------
  var GOOG='<svg viewBox="0 0 48 48"><path fill="#4285F4" d="M45.1 24.5c0-1.6-.1-2.7-.4-3.9H24v7.1h12.1c-.2 1.8-1.6 4.6-4.5 6.4l6.9 5.3c4.1-3.8 6.6-9.4 6.6-14.9z"/><path fill="#34A853" d="M24 46c5.9 0 10.9-2 14.5-5.3l-6.9-5.3c-1.9 1.3-4.4 2.2-7.6 2.2-5.8 0-10.7-3.9-12.5-9.2l-7.1 5.5C7.6 41 15.2 46 24 46z"/><path fill="#FBBC05" d="M11.5 28.4c-.5-1.4-.7-2.9-.7-4.4s.3-3 .7-4.4l-7.1-5.5C2.9 17 2 20.4 2 24s.9 7 2.4 9.9z"/><path fill="#EA4335" d="M24 10.4c3.2 0 5.4 1.4 6.7 2.6l5.9-5.8C33 3.9 29 2 24 2 15.2 2 7.6 7 4.4 14.1l7.1 5.5C13.3 14.3 18.2 10.4 24 10.4z"/></svg>';
  var TALOGO='<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="#34E0A1"/><circle cx="15.5" cy="26" r="6.6" fill="none" stroke="#000" stroke-width="2.1"/><circle cx="32.5" cy="26" r="6.6" fill="none" stroke="#000" stroke-width="2.1"/><circle cx="15.5" cy="26" r="2.5" fill="#000"/><circle cx="32.5" cy="26" r="2.5" fill="#000"/><path d="M8 20c2.5-4.5 8-7.5 16-7.5S37.5 15.5 40 20" fill="none" stroke="#000" stroke-width="2.1"/><path d="M21 13l3-3.4L27 13" fill="none" stroke="#000" stroke-width="2.1"/></svg>';
  var BOOK='<svg viewBox="0 0 48 48"><rect width="48" height="48" rx="9" fill="#003580"/><text x="24" y="34" font-family="Poppins,Arial" font-size="28" font-weight="700" fill="#fff" text-anchor="middle">B.</text></svg>';
  var LOGO={google:GOOG,tripadvisor:TALOGO,booking:BOOK};
  var SEAL='<svg width="15" height="15" viewBox="0 0 24 24"><path fill="#3d8bfd" d="M12 .9l2.6 2.5 3.5-.7.7 3.5 3.3 1.4-1.3 3.3 2 3-3 2-.1 3.6-3.6.1-2 3-3.3-1.4-3.3 1.4-2-3-3.6-.1-.1-3.6-3-2 2-3L.7 7.6 4 6.2l.7-3.5 3.5.7z"/><path fill="#fff" d="M10.5 15.6L7.2 12.3l1.4-1.4 1.9 1.9 4.6-4.6 1.4 1.4z"/></svg>';
  var STAR_P='M12 1.7l3.1 6.3 7 1-5 4.9 1.2 6.9L12 17.6l-6.3 3.2 1.2-6.9-5-4.9 7-1z';
  function starSvg(src,on){
    if(src==='tripadvisor')
      return '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.3" fill="'+(on?'#00aa6c':'none')+'" stroke="#00aa6c" stroke-width="2.2"/></svg>';
    if(src==='booking')
      return '<svg viewBox="0 0 24 24"><rect x="1" y="1" width="22" height="22" rx="4.5" fill="'+(on?'#2b5fb3':'#3a3a3a')+'"/>'+
             '<path fill="#fff" opacity="'+(on?'1':'.35')+'" transform="translate(4.4 4.4) scale(0.63)" d="'+STAR_P+'"/></svg>';
    return '<svg viewBox="0 0 24 24"><path fill="'+(on?'#f6bb06':'#4a4a4a')+'" d="'+STAR_P+'"/></svg>';
  }
  function starsHtml(src,rating,size){
    var r=Math.max(0,Math.min(5,+rating||0)), h='<span class="zkr-strow">';
    for(var i=0;i<5;i++){
      var f=Math.max(0,Math.min(1,r-i));
      if(f>0.92) f=1; if(f<0.08) f=0;
      h+='<span class="zkr-st" style="width:'+size+'px;height:'+size+'px">'+starSvg(src,false)+
         (f>0?'<span class="zkr-stf" style="width:'+(f*100)+'%"><span style="display:block;width:'+size+'px;height:'+size+'px">'+starSvg(src,true)+'</span></span>':'')+'</span>';
    }
    return h+'</span>';
  }
  function seal(){ return '<span class="zkr-seal" title="'+T.verified+'">'+SEAL+'</span>'; }

  // ---------- lightbox (plná fotka, plynulý zoom, šípky/swipe/Esc) ----------
  function hiRes(u){ return u.indexOf('googleusercontent')>-1 ? u.split('=')[0]+'=s1600' : u; }
  var LB=null;
  function lbBuild(){
    if(LB) return LB;
    var o=el('div','zkr-lb'), st=el('div','zkr-lb-stage'), img=el('img','zkr-lb-img');
    img.referrerPolicy='no-referrer'; img.alt='';
    var cap=el('div','zkr-lb-cap'); cap.innerHTML='<span class="zkr-lb-nm"></span><span class="zkr-lb-ct"></span>';
    var x=el('button','zkr-lb-x'), pv=el('button','zkr-lb-a zkr-lb-prev'), nx=el('button','zkr-lb-a zkr-lb-next');
    x.type=pv.type=nx.type='button';
    st.appendChild(img); st.appendChild(cap);
    o.appendChild(st); o.appendChild(x); o.appendChild(pv); o.appendChild(nx);
    o.style.display='none'; document.body.appendChild(o);
    LB={o:o,img:img,nm:cap.querySelector('.zkr-lb-nm'),ct:cap.querySelector('.zkr-lb-ct'),pv:pv,nx:nx,imgs:[],i:0,open:false};
    function show(i,anim){
      LB.i=(i+LB.imgs.length)%LB.imgs.length;
      var lo=LB.imgs[LB.i];
      function set(){
        LB.img.src=lo;
        var h=new Image(); h.referrerPolicy='no-referrer';
        h.onload=function(){ if(LB.imgs[LB.i]===lo) LB.img.src=h.src; }; h.src=hiRes(lo);
        LB.ct.textContent=(LB.i+1)+' / '+LB.imgs.length;
        if(LB.imgs.length>1){ var n=new Image(); n.referrerPolicy='no-referrer'; n.src=hiRes(LB.imgs[(LB.i+1)%LB.imgs.length]); }
      }
      if(anim){ LB.img.classList.add('zkr-lb-sw'); setTimeout(function(){ set(); LB.img.classList.remove('zkr-lb-sw'); },170); }
      else set();
    }
    function close(){ LB.open=false; LB.o.classList.remove('zkr-on');
      document.documentElement.style.overflow='';
      setTimeout(function(){ if(!LB.open) LB.o.style.display='none'; },300); }
    LB.show=show; LB.close=close;
    x.addEventListener('click',close);
    o.addEventListener('click',function(e){ if(e.target===o||e.target===st) close(); });
    pv.addEventListener('click',function(){ show(LB.i-1,true); });
    nx.addEventListener('click',function(){ show(LB.i+1,true); });
    document.addEventListener('keydown',function(e){ if(!LB.open)return;
      if(e.key==='Escape') close(); else if(e.key==='ArrowRight') show(LB.i+1,true);
      else if(e.key==='ArrowLeft') show(LB.i-1,true); });
    var tx0=null;
    o.addEventListener('touchstart',function(e){ tx0=e.touches[0].clientX; },{passive:true});
    o.addEventListener('touchend',function(e){ if(tx0==null)return; var dx=e.changedTouches[0].clientX-tx0;
      if(Math.abs(dx)>40&&LB.imgs.length>1) show(LB.i+(dx<0?1:-1),true); tx0=null; },{passive:true});
    return LB;
  }
  function lbOpen(r,idx){
    var lb=lbBuild(); lb.imgs=(r.images||[]); if(!lb.imgs.length) return;
    lb.nm.textContent=r.name||''; lb.open=true;
    var many=lb.imgs.length>1; lb.pv.hidden=!many; lb.nx.hidden=!many;
    lb.o.style.display='flex'; void lb.o.offsetWidth;
    lb.o.classList.add('zkr-on'); document.documentElement.style.overflow='hidden';
    lb.show(idx||0,false);
  }

  // ---------- cards ----------
  function el(t,c){ var e=document.createElement(t); if(c)e.className=c; return e; }
  var AVC=['#7b5ea7','#2f6f9f','#1a8f79','#b1493f','#c1662a','#3a4a5a','#2a8f57','#8a6d3b'];
  function avatar(r){
    var a=el('div','zkr-av');
    function ini(){ var n=(r.name||'?').trim(); a.textContent=n.charAt(0).toUpperCase();
      a.style.background=AVC[(n.charCodeAt(0)||63)%AVC.length]; }
    if(r.avatar){ var im=el('img'); im.loading='lazy'; im.referrerPolicy='no-referrer'; im.alt=r.name||'';
      im.onerror=function(){ a.innerHTML=''; ini(); }; im.src=r.avatar; a.appendChild(im); }
    else ini();
    return a;
  }
  function badgeSize(src){ return src==='booking'?25:(src==='tripadvisor'?24:21); } /* Booking > TA > Google (zámer) */
  function card(r){
    var it=el('div','zkr-item'), inner=el('div','zkr-inner');
    var src=el('div','zkr-src'); src.innerHTML=(LOGO[r.source]||'').replace('<svg','<svg width="'+badgeSize(r.source)+'" height="'+badgeSize(r.source)+'"'); inner.appendChild(src);
    var h=el('div','zkr-head'); h.appendChild(avatar(r));
    var m=el('div','zkr-meta');
    var nm=el('div','zkr-name'); nm.textContent=r.name||'Hosť'; m.appendChild(nm);
    var dt=el('div','zkr-date'); dt.textContent=relDate(r.time)+(r.location?(' · '+r.location):''); m.appendChild(dt);
    h.appendChild(m); inner.appendChild(h);
    var rt=el('div','zkr-rating'); rt.innerHTML=starsHtml(r.source,r.rating,17)+seal(); inner.appendChild(rt);
    var body=el('div','zkr-body');
    var tx=el('div','zkr-text');
    var skTxt=(lang==='sk'&&r.text_sk)?r.text_sk:null, showingSk=!!skTxt;
    if(r.text){ tx.textContent=skTxt||r.text; } else { tx.textContent=T.onlyRating; tx.classList.add('zkr-noTxt'); }
    body.appendChild(tx);
    if(r.images&&r.images.length){
      var th=el('div','zkr-thumb'); var im=el('img'); im.loading='lazy'; im.referrerPolicy='no-referrer'; im.src=r.images[0]; th.appendChild(im);
      if(r.images.length>1){ var mo=el('div','zkr-tmore'); mo.textContent='+'+(r.images.length-1); th.appendChild(mo); }
      th.addEventListener('click',function(){ lbOpen(r,0); });
      body.appendChild(th);
      var tm=el('div','zkr-thumbs-m');
      r.images.slice(0,4).forEach(function(u,ix){ var i2=el('img'); i2.loading='lazy'; i2.referrerPolicy='no-referrer'; i2.src=u;
        i2.addEventListener('click',function(){ lbOpen(r,ix); }); tm.appendChild(i2); });
      inner.appendChild(body); inner.appendChild(tm);
    } else inner.appendChild(body);
    var links=el('div','zkr-links');
    var more=el('span','zkr-more'); more.textContent=T.more;
    more.addEventListener('click',function(){ var o=tx.classList.toggle('zkr-exp'); more.textContent=o?T.less:T.more; });
    links.appendChild(more);
    if(skTxt){
      var og=el('span','zkr-orig'); og.textContent=T.orig;
      og.addEventListener('click',function(){ showingSk=!showingSk;
        tx.textContent=showingSk?skTxt:r.text; og.textContent=showingSk?T.orig:T.trans;
        it._fit&&it._fit(); });
      links.appendChild(og);
    }
    inner.appendChild(links);
    it._fit=function(){ more.classList.toggle('on', !!r.text && (tx.classList.contains('zkr-exp') || tx.scrollHeight-tx.clientHeight>4)); };
    it.appendChild(inner);
    return it;
  }

  // ---------- widget ----------
  function initWidget(wrap){
    if(wrap.dataset.zkrOn) return; wrap.dataset.zkrOn='1';
    var tabsEl=wrap.querySelector('.zkr-tabs'), sumL=wrap.querySelector('.zkr-sumL'),
        writeB=wrap.querySelector('.zkr-write'), track=wrap.querySelector('.zkr-track'),
        vp=wrap.querySelector('.zkr-viewport'), prev=wrap.querySelector('.zkr-prev'), next=wrap.querySelector('.zkr-next');
    var TABDEF=[ {k:'all',label:T.all,logo:''},
      {k:'google',label:'Google',logo:GOOG}, {k:'tripadvisor',label:'Tripadvisor',logo:TALOGO},
      {k:'booking',label:'Booking',logo:BOOK} ];
    var cur='all', index=0, vis=3, timer=null, animating=false, N=0;

    TABDEF.forEach(function(t){
      var b=el('button','zkr-tab'+(t.k==='all'?' on':'')); b.type='button'; b.setAttribute('role','tab');
      b.innerHTML=(t.logo?t.logo:'')+'<span>'+t.label+'</span>'; b.dataset.k=t.k;
      b.addEventListener('click',function(){ if(cur===t.k)return; cur=t.k;
        tabsEl.querySelectorAll('.zkr-tab').forEach(function(x){ x.classList.toggle('on',x.dataset.k===cur); });
        summary(); rebuild(); play(); });
      tabsEl.appendChild(b);
    });

    function summary(){
      var h='';
      if(cur==='all'){
        var m=META.total;
        h='<span class="zkr-sumT"><span class="zkr-grade">'+grade(m.rating)+'</span></span>'+
          '<span class="zkr-sumS">'+starsHtml('google',m.rating,21)+
          '<span class="zkr-score">'+score(m.rating)+'</span><span class="zkr-sep">|</span>'+
          '<span class="zkr-count">'+nfmt(m.count)+' '+T.reviews+'</span></span>';
        writeB.href=META.google.write;
      } else {
        var m2=META[cur], r5=cur==='booking'?m2.rating/2:m2.rating,
            sc=cur==='booking'?score(m2.rating):score(m2.rating);
        h='<span class="zkr-sumT"><span class="zkr-plogo'+(cur==='tripadvisor'?' zkr-plogo-ta':'')+'">'+LOGO[cur]+'</span><span class="zkr-pname">'+
          (cur==='google'?'Google':cur==='booking'?'Booking':'Tripadvisor')+'</span>'+
          '<span class="zkr-grade">'+grade(r5)+'</span></span>'+
          '<span class="zkr-sumS">'+starsHtml(cur,r5,21)+
          '<span class="zkr-score">'+sc+'</span><span class="zkr-sep">|</span>'+
          '<span class="zkr-count">'+nfmt(m2.count)+' '+T.reviews+'</span></span>';
        writeB.href=m2.write;
      }
      sumL.innerHTML=h; writeB.textContent=T.write;
    }
    function visCount(){ var w=window.innerWidth; return w<=600?1:(w<=1024?2:3); }
    function maxIndex(){ return Math.max(0,N-vis); }
    // mobil (1 karta): šípky centrovať na AKTUÁLNU kartu, nie na 50 % tracku
    // (track je vysoký ako najvyššia karta zo všetkých → pri krátkej recenzii šípka "utekala" dole)
    function navPos(){ var t=0;
      if(vis===1){ var it=track.children[index], inner=it&&it.querySelector('.zkr-inner');
        if(inner) t=inner.offsetHeight/2; }
      prev.style.top=t?t+'px':''; next.style.top=t?t+'px':'';
    }
    function apply(anim){ if(anim) track.classList.remove('zkr-nt'); else track.classList.add('zkr-nt');
      wrap.style.setProperty('--zkr-i',index); if(!anim) void track.offsetWidth;
      prev.classList.toggle('zkr-off',index<=0);
      next.classList.toggle('zkr-off',index>=maxIndex());
      navPos();
    }
    function rebuild(){
      var ids=TABS[cur]||[]; N=ids.length; index=0;
      track.innerHTML='';
      ids.forEach(function(i){ track.appendChild(card(DATA[i])); });
      vis=visCount(); wrap.style.setProperty('--zkr-vis',vis);
      apply(false);
      Array.prototype.forEach.call(track.children,function(c){ c._fit&&c._fit(); });
    }
    function go(dir){ if(animating)return; var nx=index+dir; if(nx<0||nx>maxIndex())return;
      animating=true; index=nx; apply(true); setTimeout(function(){ animating=false; },380); }
    next.addEventListener('click',function(){ go(1); });
    prev.addEventListener('click',function(){ go(-1); });
    // "Čítaj viac"/"Skryť" mení výšku karty → prepočítať pozíciu šípok
    track.addEventListener('click',function(){ setTimeout(navPos,0); });
    function play(){ stop(); timer=setInterval(function(){
      if(index>=maxIndex()){ stop(); return; } go(1); },6000); }
    function stop(){ if(timer){ clearInterval(timer); timer=null; } }
    wrap.addEventListener('mouseenter',stop); wrap.addEventListener('mouseleave',play);
    var x0=null;
    vp.addEventListener('touchstart',function(e){ x0=e.touches[0].clientX; stop(); },{passive:true});
    vp.addEventListener('touchend',function(e){ if(x0==null)return; var dx=e.changedTouches[0].clientX-x0;
      if(Math.abs(dx)>40) go(dx<0?1:-1); x0=null; },{passive:true});
    var rt; window.addEventListener('resize',function(){ clearTimeout(rt); rt=setTimeout(function(){
      var nv=visCount(); if(nv!==vis){ vis=nv; wrap.style.setProperty('--zkr-vis',vis);
        if(index>maxIndex()) index=maxIndex(); apply(false); }
      Array.prototype.forEach.call(track.children,function(c){ c._fit&&c._fit(); }); navPos(); },150); });
    summary(); rebuild();
    if(document.fonts&&document.fonts.ready){ document.fonts.ready.then(function(){
      Array.prototype.forEach.call(track.children,function(c){ c._fit&&c._fit(); }); navPos(); }); }
    play();
  }
  function start(){ Array.prototype.forEach.call(document.querySelectorAll('.zkr-wrap'),initWidget); }
  function boot(){
    if(ZKR_JSON_URL){
      fetch(ZKR_JSON_URL,{cache:'no-store'}).then(function(r){ return r.json(); })
        .then(function(d){ if(d&&Array.isArray(d.reviews)&&d.reviews.length){ DATA=d.reviews; TABS=d.tabs||TABS; META=d.meta||META; } })
        .catch(function(){}).then(start);
    } else start();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else boot();
})();
</script>
<!-- ===== KONIEC RECENZIE ===== -->'''

component = COMPONENT.replace('__DATA__', DATA).replace('__TABS__', TABS).replace('__META__', META)
open(os.path.join(HERE, 'snippet-elementor.html'), 'w').write(component)
json.dump({'meta': meta, 'tabs': IDX, 'reviews': flat},
          open(os.path.join(HERE, 'reviews-widget.json'), 'w'), ensure_ascii=False)

preview = ('<!doctype html><html lang="sk"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<title>Recenzie – náhľad</title>'
 '<style>body{background:#080808;margin:0;padding:56px 16px 90px;font-family:"Poppins",sans-serif;}'
 '.zk-eyebrow{color:#b9b9b9;letter-spacing:.35em;font-size:13px;text-align:center;text-transform:uppercase;}'
 '.zk-h{color:#fff;text-align:center;font-family:"Lora",Georgia,serif;font-weight:400;font-size:clamp(30px,6vw,52px);margin:14px 0 10px;}'
 '.zk-sub{color:#cfcfcf;text-align:center;font-size:17px;margin:0 0 40px;}</style></head>'
 '<body><div class="zk-eyebrow">RECENZIE</div><div class="zk-h">Naši hostia napísali</div>'
 '<div class="zk-sub">Vyskúšajte naše služby a podeľte sa o svoje zážitky aj vy.</div>'
 + component + '</body></html>')
open(os.path.join(HERE, 'preview.html'), 'w').write(preview)
print("WROTE snippet-elementor.html + preview.html + reviews-widget.json")
