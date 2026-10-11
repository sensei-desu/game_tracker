(() => {
  const $ = (selector) => document.querySelector(selector);
  const themes = window.NEXUS_THEMES || {};
  const themeSelect = $('#themeSelect');
  const form = $('#searchForm');
  const queryInput = $('#gameQuery');
  const notice = $('#notice');
  const results = $('#results');
  const searchButton = $('#searchButton');
  const apiStatus = $('#apiStatus');
  const historySection = $('#searchHistory');
  const historyList = $('#historyList');
  const HISTORY_KEY = 'nexusGameSearchHistory';
  const MAX_HISTORY = 8;
  const symbols = {'Jujutsu Kaisen — Cursed Energy':'呪','Psyduck.exe':'???','Gamer\'s Library':'▤'};
  let activeTheme = 'Midnight Pro';
  // Fixed production backend; users cannot change this from the frontend.
  const backendUrl = 'https://game-tracker-19sp.onrender.com';

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
  function readSearchHistory() {
    try {
      const value = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
      return Array.isArray(value) ? value.filter(item => typeof item === 'string') : [];
    } catch { return []; }
  }
  function saveSearchHistory(items) {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, MAX_HISTORY))); } catch { /* Storage may be disabled. */ }
    renderSearchHistory();
  }
  function renderSearchHistory() {
    const items = readSearchHistory();
    historyList.replaceChildren();
    historySection.hidden = items.length === 0;
    items.forEach(game => {
      const row = el('div', 'history-item');
      const replay = el('button', 'history-replay');
      replay.type = 'button';
      replay.append(el('span', 'history-game-icon', '🎮'), el('span', 'history-game-name', game), el('span', 'history-open', '↗'));
      replay.addEventListener('click', () => {
        queryInput.value = game;
        form.requestSubmit();
      });
      const remove = el('button', 'history-remove', '×');
      remove.type = 'button';
      remove.setAttribute('aria-label', `Remove ${game} from search history`);
      remove.title = 'Remove from history';
      remove.addEventListener('click', () => saveSearchHistory(readSearchHistory().filter(item => item !== game)));
      row.append(replay, remove);
      historyList.append(row);
    });
  }
  $('#clearHistory').addEventListener('click', () => saveSearchHistory([]));
  renderSearchHistory();

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const query = queryInput.value.trim();
    if (!query) { showNotice('Enter a game title to start searching.', 'error'); return; }
    clearNotice();
    results.replaceChildren();
    searchButton.disabled = true;
    searchButton.textContent = 'Searching…';
    apiStatus.textContent = 'Fetching game data…';
    try {
      const data = await requestJson(`${backendUrl}/api/game/${encodeURIComponent(query)}`);
      renderResult(data, query);
      const selectedTitle = (data.igdb && data.igdb.name) || (data.itad_game && data.itad_game.title) || query;
      const updated = [selectedTitle, ...readSearchHistory().filter(item => item.toLowerCase() !== selectedTitle.toLowerCase())];
      saveSearchHistory(updated);
      apiStatus.textContent = 'API reachable';
      apiStatus.style.color = 'var(--accent)';
      $('#results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      showNotice(`Search failed: ${error.message}. Verify the backend URL and its environment API keys.`, 'error');
      apiStatus.textContent = 'API error';
    } finally {
      searchButton.disabled = false;
      searchButton.innerHTML = 'Find a game <b>↗</b>';
    }
  });
  apiStatus.textContent = 'Backend configured';

  // Chawchaa chat: requests go through FastAPI; the Ollama key stays server-side.
  const matrixPanel = $('#matrixPanel');
  const matrixMessages = $('#matrixMessages');
  const matrixForm = $('#matrixForm');
  const matrixInput = $('#matrixInput');
  const matrixSend = $('#matrixSend');
  function addMatrixMessage(text, who='assistant') {
    const bubble = el('div', `matrix-message ${who}`);
    if (who === 'assistant') bubble.append(el('span','matrix-speaker','CHAWCHAA AI'));
    bubble.append(el('p','',text));
    matrixMessages.append(bubble);
    matrixMessages.scrollTop = matrixMessages.scrollHeight;
    return bubble;
  }
  $('#matrixToggle').addEventListener('click', () => {
    matrixPanel.hidden = !matrixPanel.hidden;
    if (!matrixPanel.hidden) matrixInput.focus();
  });
  $('#matrixClose').addEventListener('click', () => { matrixPanel.hidden = true; });
  document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {
    matrixInput.value = button.dataset.prompt;
    matrixInput.focus();
  }));
  matrixForm.addEventListener('submit', async event => {
    event.preventDefault();
    const message = matrixInput.value.trim();
    if (!message || matrixSend.disabled) return;
    addMatrixMessage(message, 'user');
    matrixInput.value = '';
    matrixSend.disabled = true;
    const waiting = addMatrixMessage('Connecting to the gaming network…', 'assistant');
    waiting.classList.add('matrix-waiting');
    try {
      const data = await requestJson(`${backendUrl}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      waiting.remove();
      addMatrixMessage(data.answer || 'No answer was returned.');
    } catch (error) {
      waiting.remove();
      addMatrixMessage(`Chawchaa connection failed: ${error.message}. Please try again in a moment.`);
    } finally {
      matrixSend.disabled = false;
      matrixInput.focus();
    }
  });
})();

  // Nexus community reviews
  const reviewForm = $('#websiteReviewForm');

  if (reviewForm) {
    const starButtons = [...document.querySelectorAll('.rating-star')];
    const ratingInput = $('#reviewRating');
    const catEmoji = $('#reviewCatEmoji');
    const catCaption = $('#reviewCatCaption');
    const catStage = document.querySelector('.review-cat-stage');
    const reviewName = $('#reviewName');
    const reviewFeedback = $('#reviewFeedback');
    const reviewStatus = $('#reviewStatus');
    const submitReview = $('#submitReview');
    const reviewList = $('#reviewList');
    const reviewAverage = $('#reviewAverage');
    const reviewCount = $('#reviewCount');

    const catReactions = {
      1: { emoji: '😭', caption: 'ONE STAR?! This cat is CRYING.' },
      2: { emoji: '😿', caption: 'Two stars… the cat is disappointed.' },
      3: { emoji: '🙀', caption: 'Three stars? The cat is confused.' },
      4: { emoji: '😸', caption: 'Four stars! Kitty approves.' },
      5: { emoji: '😻', caption: 'FIVE STARS! MAXIMUM HAPPINESS! 🐾' }
    };

    function showCatReaction(rating) {
      const reaction = catReactions[rating];
      if (!reaction) {
        catEmoji.textContent = '😺';
        catCaption.textContent = 'Choose your rating, gamer.';
        return;
      }

      catEmoji.textContent = reaction.emoji;
      catCaption.textContent = reaction.caption;
      catStage.classList.remove('is-reacting');
      void catStage.offsetWidth;
      catStage.classList.add('is-reacting');
    }

    function paintStars(rating) {
      starButtons.forEach(button => {
        const value = Number(button.dataset.rating);
        button.classList.toggle('is-active', value <= rating);
        button.setAttribute('aria-pressed', String(value === rating));
      });
    }

    starButtons.forEach(button => {
      const rating = Number(button.dataset.rating);

      button.addEventListener('mouseenter', () => {
        starButtons.forEach(star => {
          star.classList.toggle(
            'is-preview',
            Number(star.dataset.rating) <= rating
          );
        });
        showCatReaction(rating);
      });

      button.addEventListener('focus', () => showCatReaction(rating));

      button.addEventListener('click', () => {
        ratingInput.value = String(rating);
        paintStars(rating);
        showCatReaction(rating);
      });

      button.addEventListener('mouseleave', () => {
        starButtons.forEach(star => star.classList.remove('is-preview'));
      });
    });

    $('#starPicker').addEventListener('mouseleave', () => {
      const selected = Number(ratingInput.value);
      paintStars(selected);
      showCatReaction(selected);
    });

    function getBrowserId() {
      const key = 'nexusReviewBrowserId';
      let id = localStorage.getItem(key);

      if (!id) {
        if (crypto.randomUUID) {
          id = crypto.randomUUID();
        } else {
          id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0;
            return (c === 'x' ? r : (r & 3 | 8)).toString(16);
          });
        }
        localStorage.setItem(key, id);
      }

      return id;
    }

    function setReviewStatus(message, isError = false) {
      reviewStatus.textContent = message;
      reviewStatus.classList.toggle('is-error', isError);
    }

    function renderReviews(reviews) {
      reviewList.replaceChildren();

      if (!reviews.length) {
        reviewList.append(el('p', 'review-muted',
          'No approved reviews yet. Be the first to leave one!'));
        return;
      }

      reviews.forEach(review => {
        const card = el('article', 'review-item');
        const top = el('div', 'review-item-top');
        top.append(
          el('span', 'review-item-name', review.display_name || 'Anonymous'),
          el('span', 'review-item-stars',
            '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating))
        );

        const meta = el('div', 'review-item-top');
        meta.append(
          el('span', 'review-item-category',
            review.category || 'Overall experience')
        );

        if (review.created_at) {
          const date = new Date(review.created_at);
          if (!Number.isNaN(date.getTime())) {
            meta.append(el('span', 'review-item-date',
              date.toLocaleDateString()));
          }
        }

        card.append(top, meta);

        if (review.feedback) {
          card.append(el('p', 'review-item-feedback', review.feedback));
        }

        reviewList.append(card);
      });
    }

    async function loadReviews() {
      try {
        const [reviewData, stats] = await Promise.all([
          requestJson(`${backendUrl}/api/reviews?limit=10`),
          requestJson(`${backendUrl}/api/reviews/stats`)
        ]);

        const reviews = Array.isArray(reviewData.reviews)
          ? reviewData.reviews : [];

        reviewAverage.textContent =
          Number(stats.count) > 0
            ? Number(stats.average_rating).toFixed(1)
            : '—';

        reviewCount.textContent =
          `${stats.count} approved review${Number(stats.count) === 1 ? '' : 's'}`;

        renderReviews(reviews);
      } catch (error) {
        reviewAverage.textContent = '—';
        reviewCount.textContent = 'Community reviews are temporarily unavailable.';
        reviewList.replaceChildren(
          el('p', 'review-muted',
            `Could not load reviews: ${error.message}`)
        );
      }
    }

    reviewForm.addEventListener('submit', async event => {
      event.preventDefault();

      const rating = Number(ratingInput.value);
      const feedback = reviewFeedback.value.trim();

      if (rating < 1 || rating > 5) {
        setReviewStatus('Choose a star rating first!', true);
        return;
      }

      if (!feedback) {
        setReviewStatus('Please write a little feedback before submitting.', true);
        reviewFeedback.focus();
        return;
      }

      submitReview.disabled = true;
      submitReview.textContent = 'Submitting…';
      setReviewStatus('');

      try {
        const result = await requestJson(`${backendUrl}/api/reviews`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            browser_id: getBrowserId(),
            display_name: reviewName.value.trim() || 'Anonymous',
            rating,
            category: 'Overall experience',
            feedback
          })
        });

        setReviewStatus(result.message || 'Thanks for reviewing Nexus!');

        reviewForm.reset();
        ratingInput.value = '0';
        paintStars(0);
        showCatReaction(5);
        await loadReviews();
      } catch (error) {
        setReviewStatus(error.message, true);
      } finally {
        submitReview.disabled = false;
        submitReview.textContent = 'Submit review ↗';
      }
    });

    loadReviews();
  }

