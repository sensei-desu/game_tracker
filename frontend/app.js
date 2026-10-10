(() => {
  const $ = (selector) => document.querySelector(selector);
  const themes = window.NEXUS_THEMES || {};
  const themeSelect = $('#themeSelect');
  const form = $('#searchForm');
  const queryInput = $('#gameQuery');
  const notice = $('#notice');
  const results = $('#results');
  const searchButton = $('#searchButton');
  const backendInput = $('#backendUrl');
  const dialog = $('#settingsDialog');
  const apiStatus = $('#apiStatus');
  const symbols = {'Jujutsu Kaisen — Cursed Energy':'呪','Psyduck.exe':'???','Gamer\'s Library':'▤'};
  let activeTheme = 'Midnight Pro';
  let backendUrl = localStorage.getItem('nexusBackendUrl') || 'https://game-tracker-19sp.onrender.com';

  Object.keys(themes).forEach(name => {
    const option = document.createElement('option'); option.value = name; option.textContent = name; themeSelect.append(option);
  });
  function setTheme(name) {
    const t = themes[name]; if (!t) return;
    activeTheme = name;
    document.body.dataset.theme = name;
    document.body.dataset.backdrop = t.backdrop || 'midnight';
    document.body.dataset.cursor = t.cursor || name;
    document.documentElement.style.setProperty('--bg', t.bg);
    document.documentElement.style.setProperty('--panel', t.panel);
    document.documentElement.style.setProperty('--panel2', t.panel2);
    document.documentElement.style.setProperty('--text', t.text);
    document.documentElement.style.setProperty('--muted', t.muted);
    document.documentElement.style.setProperty('--line', t.line);
    document.documentElement.style.setProperty('--accent', t.accent);
    document.documentElement.style.setProperty('--deep', t.deep);
    document.documentElement.style.setProperty('--radius', t.radius);
    document.documentElement.style.setProperty('--font', `'${t.font || 'DM Sans'}',sans-serif`);
    document.documentElement.style.colorScheme = t.mode === 'light' ? 'light' : 'dark';
    $('#themeTitle').textContent = name;
    $('#themeTagline').textContent = t.tagline;
    $('#themeSymbol').textContent = symbols[name] || t.symbol || '✦';
    $('#palette').replaceChildren(...[t.bg,t.panel,t.accent,t.deep,t.text].map(color => {const s=document.createElement('span');s.style.setProperty('--swatch',color);s.title=color;return s;}));
    const art = t.image;
    if (art) {
      document.documentElement.style.setProperty('--theme-art', `url("${art}")`);
      document.body.classList.add('has-art');
    } else {
      document.body.classList.remove('has-art');
      document.documentElement.style.removeProperty('--theme-art');
    }
    themeSelect.value = name;
    localStorage.setItem('nexusTheme', name);
    const u = new URL(location.href); u.searchParams.set('theme',name); history.replaceState({},'',u);
  }
  themeSelect.addEventListener('change', () => setTheme(themeSelect.value));
  const urlTheme = new URLSearchParams(location.search).get('theme');
  setTheme(themes[urlTheme] ? urlTheme : (localStorage.getItem('nexusTheme') && themes[localStorage.getItem('nexusTheme')] ? localStorage.getItem('nexusTheme') : 'Midnight Pro'));

  function showNotice(message, kind='') { notice.textContent=message; notice.className=`notice ${kind}`; notice.hidden=false; }
  function clearNotice() { notice.hidden=true; notice.textContent=''; notice.className='notice'; }
  function money(value,currency='') {
    if (value === null || value === undefined || value === '') return 'Unavailable';
    const n=Number(value); if (!Number.isFinite(n)) return 'Unavailable';
    const c=String(currency||'').toUpperCase();
    const symbols={INR:'₹',USD:'$',EUR:'€',GBP:'£'};
    return symbols[c] ? `${symbols[c]}${n.toLocaleString(undefined,{maximumFractionDigits:2})}` : `${n.toLocaleString(undefined,{maximumFractionDigits:2})} ${c}`.trim();
  }
  function el(tag, cls, text) { const node=document.createElement(tag); if(cls)node.className=cls; if(text!==undefined)node.textContent=text; return node; }
  function safeHttpUrl(value) { try { const u=new URL(value); return ['https:','http:'].includes(u.protocol) ? u.href : ''; } catch { return ''; } }
  function makeMetric(label,value,sub) { const n=el('article','metric');n.append(el('div','metric-label',label),el('div','metric-value',value),el('div','metric-sub',sub));return n; }
  function renderResult(data, query) {
    results.replaceChildren();
    const igdb=data.igdb||{}, prices=data.prices||{}, history=data.history||{}, itad=data.itad_game||{}, deals=prices.deals||[];
    const title=igdb.name||itad.title||query||'Game details';
    const overview=el('section',''); const head=el('div','section-head');const headleft=el('div');headleft.append(el('div','section-index','SEARCH RESULT / GAME OVERVIEW'),el('h2','',title));head.append(headleft);overview.append(head);
    const card=el('article','game-card'); const coverUrl=safeHttpUrl(igdb.cover_url||(itad.assets||{}).banner400||(itad.assets||{}).boxart);
    if(coverUrl){const img=el('img','cover');img.src=coverUrl;img.alt=`${title} cover`;img.loading='lazy';card.append(img);}else{const noCover=el('div','cover');noCover.style.display='grid';noCover.style.placeItems='center';noCover.textContent='🎮';card.append(noCover);}
    const details=el('div','');details.append(el('h3','game-title',title));const chips=el('div','chips');
    if(igdb.first_release_date){const d=new Date(Number(igdb.first_release_date)*1000);if(!Number.isNaN(d.getTime()))chips.append(el('span','chip',`Released ${d.getFullYear()}`));}
    (igdb.genres||[]).slice(0,3).forEach(x=>x.name&&chips.append(el('span','chip',x.name)));
    if(chips.childNodes.length)details.append(chips);
    details.append(el('p','summary',(igdb.summary||'Game description is not available from the metadata provider.').slice(0,850)));
    const platforms=(igdb.platforms||[]).map(p=>p.name).filter(Boolean);if(platforms.length){const pc=el('div','chips');platforms.forEach(p=>pc.append(el('span','chip',p)));details.append(pc);}
    const itadUrl=safeHttpUrl(itad.itad_url);if(itadUrl){const a=el('a','buy','View on IsThereAnyDeal ↗');a.href=itadUrl;a.target='_blank';a.rel='noopener noreferrer';details.append(a);}
    card.append(details);overview.append(card);results.append(overview);
    const low=history.low||{}, best=deals[0], bestPrice=best&&best.price||{};
    const section=el('section','');section.append(el('h2','offers-title','Price intelligence · India region'));
    const metrics=el('div','metric-grid');metrics.append(makeMetric('BEST CURRENT PRICE',best?money(bestPrice.amount,bestPrice.currency):'—',best?.shop?.name||'No deal found'),makeMetric('ALL-TIME LOW',money(low.amount,low.currency),low.amount!==undefined?(low.shop?.name||'Across tracked stores'):'No history available'),makeMetric('STORES COMPARED',String(deals.length),'Live offers returned by provider'));section.append(metrics);
    section.append(el('h3','offers-title','Available offers'));
    if(deals.length){deals.forEach((deal,index)=>{const offer=el('article','offer');offer.append(el('div','offer-icon',index===0?'🏆':'🛒'));const info=el('div','');info.append(el('div','offer-name',deal.shop?.name||'Store'));
      const regular=deal.regular||{}, price=deal.price||{}, discount=Number(deal.cut||0);let sub='Current listed price';if(discount>0)sub=`${discount}% off`;if(regular.amount!==undefined&&Number(regular.amount)>Number(price.amount))sub=`Regular ${money(regular.amount,regular.currency||price.currency)} · Save ${discount}%`;info.append(el('div','offer-sub',sub));if(discount>0)info.append(el('span','discount',`-${discount}%`));offer.append(info);
      const priceBox=el('div','offer-price',money(price.amount,price.currency));const buyUrl=safeHttpUrl(deal.url);if(buyUrl){const a=el('a','buy',`Buy at ${deal.shop?.name||'store'} ↗`);a.href=buyUrl;a.target='_blank';a.rel='noopener noreferrer';priceBox.append(document.createElement('br'),a);}else priceBox.append(el('div','offer-sub','Purchase link unavailable'));offer.append(priceBox);section.append(offer);});
      section.append(el('p','summary','Prices and currencies are shown as returned by the provider. Regional availability can vary.'));
    }else section.append(el('p','summary','No price offers were returned for this title. Try another title or check provider regional coverage.'));
    results.append(section);
  }
  async function requestJson(url, options={}) { const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),30000);try{const response=await fetch(url,{...options,signal:controller.signal});let body;try{body=await response.json();}catch{body={};}if(!response.ok)throw new Error(`${body.detail||'Request failed'} (HTTP ${response.status})`);return body;}finally{clearTimeout(timer);} }
  async function testConnection() {
    const url=(backendInput.value||backendUrl).trim().replace(/\/$/,'');const status=$('#settingsStatus');status.textContent='Checking backend…';
    try{const data=await requestJson(`${url}/`);status.textContent=`Connected: ${data.app||'API online'}`;apiStatus.textContent='API reachable';apiStatus.style.color='var(--accent)';return true;}
    catch(e){status.textContent=`Could not connect: ${e.message}. Check the URL and that the backend is deployed.`;return false;}
  }
  form.addEventListener('submit',async event=>{
    event.preventDefault();const query=queryInput.value.trim();if(!query){showNotice('Enter a game title to start searching.','error');return;}
    if(!backendUrl||backendUrl.includes('your-backend.onrender.com')){showNotice('Set your actual FastAPI backend URL using the ⚙ button before searching.');dialog.showModal();backendInput.value=backendUrl.includes('your-backend.onrender.com')?'':backendUrl;return;}
    clearNotice();results.replaceChildren();searchButton.disabled=true;searchButton.textContent='Searching…';apiStatus.textContent='Fetching game data…';
    try{const data=await requestJson(`${backendUrl}/api/game/${encodeURIComponent(query)}`);renderResult(data,query);apiStatus.textContent='API reachable';apiStatus.style.color='var(--accent)';$('#results').scrollIntoView({behavior:'smooth',block:'start'});}
    catch(error){showNotice(`Search failed: ${error.message}. Verify the backend URL and its environment API keys.`, 'error');apiStatus.textContent='API error';}
    finally{searchButton.disabled=false;searchButton.innerHTML='Find a game <b>↗</b>';}
  });
  $('#settingsButton').addEventListener('click',()=>{backendInput.value=backendUrl.includes('your-backend.onrender.com')?'':backendUrl;$('#settingsStatus').textContent='';dialog.showModal();});
  $('#testApi').addEventListener('click',testConnection);
  $('#saveApi').addEventListener('click',()=>{const val=backendInput.value.trim().replace(/\/$/,'');if(!val){$('#settingsStatus').textContent='Enter a backend URL first.';return;}backendUrl=val;localStorage.setItem('nexusBackendUrl',backendUrl);apiStatus.textContent='URL saved · not tested';});
  if(backendUrl&&!backendUrl.includes('your-backend.onrender.com')){apiStatus.textContent='Backend URL configured';}
})();
