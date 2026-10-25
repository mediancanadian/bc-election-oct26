// The Median Canadian, week 3: B.C. election explorer.
// Reads S (site.json: ridings, history, polls, places), T (story.json + the slides' own headlines and lines), TOPO and DETAIL (maps) and REFS.
// The page is built around one choice: your riding. Every chapter's picture highlights it and one sentence places it.
(function () {
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const css = n => getComputedStyle(document.documentElement).getPropertyValue('--' + n).trim();
const PN = {CON: 'Conservative', NDP: 'NDP', GRN: 'Green', CENTRE: 'CentreBC', ONEBC: 'OneBC', OTH: 'Other', IND: 'Independent', UNAF: 'Unaffiliated',
  LBN: 'Libertarian', COMM: 'Communist', CHP: 'Christian Heritage', FPBC: 'Freedom', LIB: 'BC Liberal'};
const SHORT = {CON: 'Con.', NDP: 'NDP', GRN: 'Green'}, PLURAL = {CON: 'Conservatives', NDP: 'NDP', GRN: 'Greens'};
const FN = {LPC: 'Liberal', CPC: 'Conservative', NDP: 'NDP', GPC: 'Green'}, FNP = {LPC: 'Liberals', CPC: 'Conservatives', NDP: 'NDP', GPC: 'Greens'};
const pc = p => css(p) || css('OTH');
const fc = p => ({LPC: css('LPC'), CPC: css('CON'), NDP: css('NDP'), GPC: css('GRN')})[p] || css('OTH');
const R = S.ridings, codes = Object.keys(R), N = codes.length, MAJ = T.majority;
const fmt = d3.format(',');
const f1 = v => v == null || isNaN(v) ? 'n/a' : (Math.round((Math.abs(v) + 1e-9) * 10) / 10 * (v < 0 ? -1 : 1)).toFixed(1);   // round half up
const sgn = v => (v > 0 ? '+' : v < 0 ? '−' : '') + f1(Math.abs(v));
const rr2 = v => (v < 0 ? '−' : '') + Math.abs(v).toFixed(2);
const WORD = ['None', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'];
const word = n => WORD[n] || String(n);
const and = a => a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
const money = v => v >= 1e6 ? '$' + (v / 1e6).toFixed(2) + 'M' : '$' + fmt(Math.round(v / 1000)) + 'k';
const MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const drange = s => { const [a, b] = s.split(' to ').map(x => x.split('-').map(Number));
  return a[1] === b[1] ? `${MON[a[1] - 1]} ${a[2]} to ${b[2]}, ${b[0]}` : `${MON[a[1] - 1]} ${a[2]} to ${MON[b[1] - 1]} ${b[2]}, ${b[0]}`; };
const apd = s => { const [yy, mm, dd] = s.split('-').map(Number); return `${MON[mm - 1]} ${dd}, ${yy}`; };
const ref = id => { const i = REFS.findIndex(r => r.id === id) + 1; return i ? `<sup class="c"><a href="#ref-${i}">[${i}]</a></sup>` : ''; };
const tip = $('#tip');
function showTip(e, h) { tip.innerHTML = h; tip.style.display = 'block'; const x = Math.min(e.clientX + 14, innerWidth - 270); tip.style.left = Math.max(4, x) + 'px'; tip.style.top = (e.clientY + 14) + 'px'; }
function hideTip() { tip.style.display = 'none'; }
addEventListener('scroll', hideTip, {passive: true});
const stamp = t => { const m = String(t).match(/(\d+)\/(\d+)\/(\d+) (\d+):(\d+):\d+ (AM|PM)/); if (!m) return t;
  return `${MON[+m[2] - 1]} ${+m[1]}, ${m[3]}, ${+m[4]}:${m[5]} ${m[6] === 'AM' ? 'a.m.' : 'p.m.'} Pacific`; };
const ASOF = 'as of ' + stamp(T.meta.source_time);   // the 2026 results are dated by when Elections BC posted them
// whole percentages, rounded half up, as on the slides
const pct0 = v => v == null || isNaN(v) ? 'n/a' : Math.floor(v + 0.5) + '%';
const lc1 = s => /^([A-Z]{2}|Conservative|Green|Liberal|NDP|B\.C\.)/.test(s) ? s : s.charAt(0).toLowerCase() + s.slice(1);
const art = s => (/^[aeiou]/i.test(s) ? 'an ' : 'a ') + s;
const aParty = p => p === 'NDP' ? 'an NDP' : art(PN[p] || p);
const electedTxt = r => r.flip ? `elected ${aParty(r.win24)} MLA in 2024 and ${aParty(r.lead)} MLA in 2026` : `elected ${aParty(r.lead)} MLA in 2024 and again in 2026`;
const plural = (n, a, b) => `${n} ${n === 1 ? a : b}`;
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
// where a value sits among the ridings: "higher than in 6 in 10 ridings" (one rule for every chapter)
const rankIn = (vals, v, hi, lo) => { const below = vals.filter(x => x < v).length / vals.length, above = vals.filter(x => x > v).length / vals.length;
  if (Math.abs(below - above) < .2) return 'close to the middle of all ridings';
  return below >= .5 ? `${hi} than in ${Math.floor(below * 10)} in 10 ridings` : `${lo} than in ${Math.floor(above * 10)} in 10 ridings`; };
// ridings where the Greens finished in the top two in 2026 or held the seat in 2024: the sentences there describe that race
const grnRace = c => R[c].c26.slice(0, 2).some(x => x[1] === 'GRN') || R[c].win24 === 'GRN';
const top2Txt = c => and(R[c].c26.slice(0, 2).map(x => 'the ' + (PLURAL[x[1]] || PN[x[1]] || x[0])));
const chg = (r, k) => (r.s26[k] || 0) - (r.s24[k] || 0);
const regName = n => n.replace('Capital Region (Victoria)', 'Victoria area (Capital Region)');

// kickers, headlines and lines: the slides' own words, in the slides' order (data/slide_text.json, keyed by chapter)
const KEYS = Array.isArray(T.order) && T.order.length ? T.order : ['result', 'majority', 'how', 'where', 'who', 'middle', 'why', 'promises'];
const over = o => Array.isArray(o) ? Object.fromEntries(o.map((v, i) => [KEYS[i], v])) : (o || {});
const HEAD = over(T.headlines), LINE = over(T.lines), KICK = over(T.kickers);
for (const k of KEYS) { const h = $('#h-' + k); if (h) h.textContent = HEAD[k] || ''; const l = $('#l-' + k); if (l) l.textContent = LINE[k] || '';
  const kk = k === 'result' ? null : document.querySelector(`#${k} > .kick`); if (kk && KICK[k]) kk.textContent = KICK[k]; }
$('#l-result').innerHTML = esc(LINE.result || '') + ref('ebchist') + ref('ebc26');   // first majority since 1928: Electoral History of BC

// responsive chart frame: each SVG is drawn at the real width of its box, so text keeps its size on a phone
const DRAW = [];
const cw = sel => { const p = document.querySelector(sel).parentNode, cs = getComputedStyle(p);
  return Math.max(260, Math.floor(p.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight))); };
function frame(sel, h) { const svg = d3.select(sel), w = cw(sel);
  svg.attr('viewBox', `0 0 ${w} ${h}`).attr('width', w).attr('height', h); svg.selectAll('*').remove(); return {svg, w, h}; }
function draw(fn) { DRAW.push(fn); fn(); }
let rz, lastW = innerWidth; addEventListener('resize', () => { if (innerWidth === lastW) return; lastW = innerWidth; clearTimeout(rz); rz = setTimeout(() => DRAW.forEach(f => f()), 150); });
const txt = (g, x, y, s, o = {}) => g.append('text').attr('x', x).attr('y', y).attr('font-size', o.size || 12).attr('font-weight', o.weight || 400)
  .attr('fill', o.fill || css('text')).attr('text-anchor', o.anchor || 'start').text(s);
const halo = t => t.attr('paint-order', 'stroke').attr('stroke', css('card')).attr('stroke-width', 3).attr('stroke-linejoin', 'round');
const axis = (g, a) => g.call(a).attr('color', css('muted')).attr('font-size', 12);
// taps and hovers go to the nearest dot, so small dots are easy to hit on a phone
function nearest(svg, pts, onPick, onMiss, hover, maxD = 26) {
  const best = e => { const [mx, my] = d3.pointer(e); const b = d3.least(pts, p => (p.x - mx) ** 2 + (p.y - my) ** 2); return b && Math.hypot(b.x - mx, b.y - my) <= maxD ? b : null; };
  svg.on('click', e => { const b = best(e); if (b) onPick(b, e); else if (onMiss) onMiss(e); })
    .on('mousemove', e => { const b = best(e); if (b && hover) { showTip(e, hover(b)); svg.style('cursor', 'pointer'); } else { hideTip(); svg.style('cursor', onMiss ? 'pointer' : 'default'); } })
    .on('mouseleave', hideTip);
}

// ---------------------------------------------------------------- your riding: the thread through the page
let you = null;
const ON_YOU = [];
const youName = () => you ? R[you].name : '';
const leadTxt = c => `${PN[R[c].lead]}, elected by ${fmt(R[c].margin)} votes`;
const newTxt = c => R[c].flip ? `changed party (${PN[R[c].win24]} in 2024)` : `same party as 2024`;
function setYou(c, o = {}) {
  you = c && R[c] ? c : null;
  try { if (you) localStorage.setItem('bc26-riding', you); else localStorage.removeItem('bc26-riding'); } catch (e) { /* storage blocked */ }
  try { history.replaceState(null, '', you ? '#' + you : location.pathname + location.search); } catch (e) { /* not allowed here */ }
  if (you && o.zoom !== false) { const z = zoneOf(you); if (zoom !== z) setZoom(z); }
  ON_YOU.forEach(f => f());
  if (o.scrollTo) $(o.scrollTo).scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start'});
}
function youBar() {
  const bar = $('#youbar');
  if (!you) { bar.hidden = true; return; }
  $('#ybdot').style.background = pc(R[you].lead);
  $('#ybwho').innerHTML = `<b>${esc(R[you].name)}</b><span>${PN[R[you].lead]} by ${fmt(R[you].margin)} votes · ${R[you].flip ? 'changed party' : 'same party as 2024'}</span>`;
  bar.hidden = finderVisible;
}
let finderVisible = true;
if ('IntersectionObserver' in window) new IntersectionObserver(es => { finderVisible = es[0].isIntersecting; youBar(); }, {threshold: 0}).observe($('#finder'));
$('#ybchange').onclick = () => { $('#finder').scrollIntoView({behavior: 'smooth', block: 'center'}); setTimeout(() => $('#find').focus(), 400); };
$('#ybclear').onclick = () => setYou(null);
ON_YOU.push(youBar);

// ---------------------------------------------------------------- hero: the result and the finder
const P = S.province, lead = p => T.seats[p] || 0;
const under = v => codes.filter(c => R[c].margin < v).length;
const NX = T.next, FINAL = NX.final_count.replace(/\s*\(planned\)/, '');
$('#score').innerHTML = ['CON', 'NDP', 'GRN'].map(p => `<div style="border-top-color:${pc(p)}"><span class="pn">${PN[p]}</span><b>${lead(p)}</b><span>seats</span><span>${f1(T.share[p])}% of votes${ref('ebc26')}</span></div>`).join('');
// the strip: Conservative leads from safest to closest, so the block on the line is the riding that decides the majority
const STRIP = [...codes.filter(c => R[c].lead === 'CON').sort((a, b) => R[b].margin - R[a].margin), ...codes.filter(c => R[c].lead === 'GRN'),
  ...codes.filter(c => R[c].lead === 'NDP').sort((a, b) => R[a].margin - R[b].margin)];
function drawStrip() {
  $('#seatbar').innerHTML = STRIP.map(c => `<i class="${c === you ? 'me' : ''}" style="background:${pc(R[c].lead)}" title="${esc(R[c].name)}"></i>`).join('') + `<em style="left:calc(${100 * MAJ / N}% - 1.5px)"></em>`;
  $('#seatbar').setAttribute('aria-label', `Seats: Conservative ${lead('CON')}, Green ${lead('GRN')}, NDP ${lead('NDP')}. ${MAJ} make a majority.`);
}
drawStrip(); ON_YOU.push(drawStrip);
$('#seatnote').innerHTML = `Results ${ASOF}. Each block is a riding, coloured by the party elected. The line marks ${MAJ} seats, a majority.${ref('ebc26')}`;
$('#jump').innerHTML = KEYS.filter(k => k !== 'result' && document.getElementById(k)).map(k => `<a href="#${k}">${esc(KICK[k] || k)}</a>`).join('');

// finder: riding names, plus every municipality and designated place (2021 Census) with the ridings its people live in
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[-–'’.]/g, ' ').replace(/\s+/g, ' ').trim();
const RN = codes.map(c => ({c, n: norm(R[c].name)}));
const PL = (S.places || []).map(([name, kind, rs, pop]) => ({name, kind, rs, pop, n: norm(name)}));
const dupName = new Set(PL.map(p => p.n).filter((n, i, a) => a.indexOf(n) !== i));
const placeLabel = p => dupName.has(p.n) || p.kind !== 'community' ? `${p.name} (${p.kind})` : p.name;
function search(q) {
  const s = norm(q); if (s.length < 2) return [];
  const hitsR = RN.filter(r => r.n.includes(s) || r.c.toLowerCase() === s).map(r => ({type: 'r', c: r.c, score: r.n === s ? 0 : r.n.startsWith(s) ? 1 : 2}));
  const hitsP = PL.filter(p => p.n.startsWith(s) || p.n.includes(' ' + s)).map(p => ({type: 'p', p, score: p.n === s ? 0.5 : p.n.startsWith(s) ? 1.5 : 2.5}));
  return [...hitsR, ...hitsP].sort((a, b) => a.score - b.score || (a.type === 'p' && b.type === 'p' ? b.p.pop - a.p.pop : 0)).slice(0, 8);
}
const ridingBtn = (c, extra = '') => `<button class="hit" data-pick="${c}"><span><span class="dot" style="background:${pc(R[c].lead)}"></span>${esc(R[c].name)}${extra}</span><small>${PN[R[c].lead]} +${fmt(R[c].margin)}</small></button>`;
function showHits(list, head = '') {
  $('#hits').innerHTML = head + list.map(h => h.type === 'r' ? ridingBtn(h.c) :
    `<button class="hit" data-place="${PL.indexOf(h.p)}"><span>${esc(placeLabel(h.p))}</span><small>${h.p.rs.length === 1 ? R[h.p.rs[0][0]].name : h.p.rs.length + ' ridings'}</small></button>`).join('');
  $$('#hits [data-pick]').forEach(b => b.onclick = () => { setYou(b.dataset.pick); $('#hits').innerHTML = ''; $('#find').value = ''; });
  $$('#hits [data-place]').forEach(b => b.onclick = () => { const p = PL[+b.dataset.place];
    if (p.rs.length === 1) { setYou(p.rs[0][0]); $('#hits').innerHTML = ''; $('#find').value = ''; return; }
    $('#hits').innerHTML = `<div class="note">${esc(placeLabel(p))}: ${p.rs.length} ridings, by share of its people (2021 Census). Pick yours.</div>` + p.rs.map(([c, sh]) => ridingBtn(c, ` <small>· ${f1(sh)}%</small>`)).join('');
    $$('#hits [data-pick]').forEach(x => x.onclick = () => { setYou(x.dataset.pick); $('#hits').innerHTML = ''; $('#find').value = ''; }); });
}
$('#find').addEventListener('input', e => { const q = e.target.value; const h = search(q);
  showHits(h, q.trim().length >= 2 && !h.length ? '<div class="note">No riding or place by that name. Try a city, town or riding.</div>' : ''); });
$('#find').addEventListener('keydown', e => { if (e.key === 'Enter') { const b = $('#hits button'); if (b) { e.preventDefault(); b.click(); } } else if (e.key === 'Escape') { $('#hits').innerHTML = ''; } });
$$('.try').forEach(b => b.onclick = () => { $('#find').value = b.dataset.q; $('#find').dispatchEvent(new Event('input')); });
$('#tomap').onclick = () => $('#where').scrollIntoView({behavior: 'smooth'});
function drawMine() {
  if (!you) { $('#mine').innerHTML = ''; $('#findhelp').hidden = false; return; }
  const r = R[you];
  $('#findhelp').hidden = true;
  $('#mine').innerHTML = `<div class="mine" style="border-left-color:${pc(r.lead)}"><span class="note">Your riding</span><b>${esc(r.name)}</b><span>${leadTxt(you)}, ${newTxt(you)}.${ref('ebc26')}</span>
    <div class="row"><button id="mineMap">See it on the map</button><button id="mineClear">Choose another</button></div></div>`;
  $('#mineMap').onclick = () => $('#where').scrollIntoView({behavior: 'smooth'});
  $('#mineClear').onclick = () => { setYou(null); $('#find').focus(); };
}
ON_YOU.push(drawMine);

// one sentence per chapter about your riding
const YOU = {};
const pickPrompt = '<span>Find your riding at the top, and this chapter will show where it fits. <button class="link" data-findyou>Find your riding</button></span>';
function renderYou() {
  KEYS.slice(1).forEach(k => { const el = $('#you-' + k); if (!el) return;
    if (!you) { el.classList.add('none'); el.innerHTML = pickPrompt; return; }
    el.classList.remove('none'); el.innerHTML = `<div>${YOU[k] ? YOU[k](you) : ''}</div>`; });
  $$('[data-findyou]').forEach(b => b.onclick = () => { $('#finder').scrollIntoView({behavior: 'smooth', block: 'center'}); setTimeout(() => $('#find').focus(), 400); });
}
ON_YOU.push(renderYou);

// ---------------------------------------------------------------- how: the Conservatives replaced the BC Liberals
const FAM = S.families;
const HC = () => ({CON: css('CON'), SC: '#1596a8', COAL: '#a1887f', LIB: css('LPC'), BCLIB: css('LIB'), LEFT: css('NDP'), GRN: css('GRN'), REF: '#7f8c8d', OTH: css('OTH')});
const H28 = S.history.filter(h => h.year < 2026 && (h.share.CON || 0) >= T.share.CON).pop();
const RS = T.rise;
let howView = 'recent', howYear = 2026;
const RECENT = T.rise_long.map(d => d.year);
$$('[data-hv]').forEach(b => b.onclick = () => { howView = b.dataset.hv; $$('[data-hv]').forEach(x => x.classList.toggle('on', x === b)); if (howView === 'recent' && !RECENT.includes(howYear)) howYear = 2026; drawHow(); });
const famName = (k, y) => k === 'LEFT' ? (y < 1961 ? 'CCF' : 'NDP') : FAM[k];
function yearCard(year) {
  const d = S.history.find(h => h.year === year); if (!d) return; const H = HC();
  const rows = Object.entries(d.share).filter(([k, v]) => v > 1).sort((a, b) => b[1] - a[1]).slice(0, 4);
  const gov = d.initial ? `Conservative majority: ${d.won.CON} of ${d.seats} seats.${ref('ebc26')}` : d.gov ? `Government after the vote: ${d.gov}${d.premier ? `; premier ${d.premier.replace(/\s*\(.*?\)/g, '')}` : ''}.${ref('ebchist')}` : '';
  $('#ycard').innerHTML = `<b class="y">${d.year}${d.initial ? ', ' + ASOF : ''}</b><div class="note">${gov}</div><div class="ybars">` +
    rows.map(([k, v]) => `<div class="ybar"><div class="yl"><span><span class="dot" style="background:${H[k]}"></span>${famName(k, d.year)}</span><span><b>${f1(v)}%</b> · ${plural(d.won[k] || 0, 'seat', 'seats')}</span></div><span class="tr"><i style="width:${Math.min(100, v / 70 * 100)}%;background:${H[k]}"></i></span></div>`).join('') + '</div>' +
    (you && RYEAR(you)[year] ? `<p class="note" style="margin:10px 0 0"><b style="color:var(--text)">${esc(R[you].name)}</b>: ${RYEAR(you)[year]}</p>` : '');
}
// your riding's own vote: 2020 (votes moved onto the 2026 riding), 2024 and 2026
const RV = c => { const r = R[c]; return [[2020, (r.s20.LIB || 0) + (r.s20.CON || 0), r.s20.NDP], [2024, r.s24.CON, r.s24.NDP], [2026, r.s26.CON, r.s26.NDP]]; };
const RYEAR = c => { const r = R[c];
  return {2020: `BC Liberal ${f1(r.s20.LIB)}%, Conservative ${f1(r.s20.CON)}%, NDP ${f1(r.s20.NDP)}% (the 2020 votes moved onto this riding).${ref('ebc20')}`,
    2024: `Conservative ${f1(r.s24.CON)}%, NDP ${f1(r.s24.NDP)}%${r.s24.GRN ? `, Green ${f1(r.s24.GRN)}%` : ''}.${ref('ebc24')}`,
    2026: `${r.c26.slice(0, 3).map(([n, p, v, sh]) => `${p === 'OTH' || !PN[p] ? n : PN[p]} ${f1(sh)}%`).join(', ')}, ${ASOF}.${ref('ebc26')}`}; };
const STACK = ['CON', 'COAL', 'SC', 'BCLIB', 'REF', 'LIB'];
// keep labels in one column apart: each label at least gap pixels from its neighbour
function spread(items, gap, lo, hi) {
  items.sort((a, b) => a.y - b.y);
  for (let i = 1; i < items.length; i++) if (items[i].y - items[i - 1].y < gap) items[i].y = items[i - 1].y + gap;
  const over = items.length ? items[items.length - 1].y - hi : 0; if (over > 0) items.forEach(it => { it.y -= over; });
  for (let i = items.length - 2; i >= 0; i--) if (items[i + 1].y - items[i].y < gap) items[i].y = items[i + 1].y - gap;
  if (items.length && items[0].y < lo) { const d = lo - items[0].y; items.forEach(it => { it.y += d; }); }
  return items;
}
function drawHow() {
  const H = HC(), recent = howView === 'recent';
  const D = recent ? T.rise_long.map(d => ({year: d.year, initial: !!d.initial, share: {CON: d.CON, BCLIB: d.BCLIB}, left: d.NDP}))
    : S.history.map(d => ({year: d.year, initial: !!d.initial, share: d.share, left: d.share.LEFT || 0}));
  const keys = recent ? ['CON', 'BCLIB'] : STACK;
  const w1 = cw('#howchart'), nar = w1 < 460, {svg, w, h} = frame('#howchart', 300), m = {l: 40, r: recent ? (nar ? 96 : 140) : 44, t: 30, b: 28};
  const x = d3.scaleLinear([D[0].year, D[D.length - 1].year], [m.l, w - m.r]), y = d3.scaleLinear([0, recent ? 70 : 100], [h - m.b, m.t]);
  const tv = recent ? (w < 600 ? [2001, 2009, 2017, 2026] : D.map(d => d.year)) : null;
  axis(svg.append('g').attr('transform', `translate(0,${h - m.b})`), d3.axisBottom(x).tickValues(tv).ticks(w < 500 ? 5 : 10).tickFormat(d3.format('d')));
  axis(svg.append('g').attr('transform', `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickFormat(v => v + '%'));
  const last = D[D.length - 1];
  if (recent) {   // one line per party, a dot per election: BC Liberal to 2020, Conservative and NDP throughout
    const LN = [['BCLIB', D.filter(d => d.share.BCLIB > 0).map(d => [d.year, d.share.BCLIB]), 3], ['LEFT', D.map(d => [d.year, d.left]), 3], ['CON', D.map(d => [d.year, d.share.CON]), 4]];
    LN.forEach(([k, pts, lw]) => { svg.append('path').datum(pts).attr('fill', 'none').attr('stroke', H[k]).attr('stroke-width', lw).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round').attr('d', d3.line(d => x(d[0]), d => y(d[1])));
      svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', d => x(d[0])).attr('cy', d => y(d[1])).attr('r', 4).attr('fill', H[k]).attr('stroke', css('card')).attr('stroke-width', 1.5); });
    const lib = LN[0][1];
    halo(txt(svg, x(2006), y(lib[1][1]) - 12, 'BC Liberal', {anchor: 'middle', size: 13, weight: 800, fill: H.BCLIB}));
    const ends = spread([{y: y(last.share.CON) + 4, t: `${f1(last.share.CON)}%`, n: nar ? 'Con.' : 'Conservative', col: H.CON}, {y: y(last.left) + 4, t: `${f1(last.left)}%`, n: 'NDP', col: H.LEFT}], 16, m.t, h - m.b);
    ends.forEach(l => { const t = halo(svg.append('text').attr('x', x(last.year) + 9).attr('y', l.y).attr('font-size', 12).attr('fill', l.col));
      t.append('tspan').attr('font-weight', 800).text(l.t); t.append('tspan').attr('font-weight', 700).attr('dx', 5).text(l.n); });
  } else {   // every election since 1928: the main parties other than the CCF and NDP stacked, the CCF and NDP as a line
    const stack = d3.stack().keys(keys).value((d, k) => d.share[k] || 0)(D);
    svg.append('g').selectAll('path').data(stack).join('path').attr('fill', s => H[s.key]).attr('fill-opacity', .9)
      .attr('d', d3.area().x(d => x(d.data.year)).y0(d => y(d[0])).y1(d => y(d[1])));
    const ld = D.filter(d => d.left > 0.5);
    halo(svg.append('path').datum(ld).attr('fill', 'none').attr('stroke-linejoin', 'round').attr('d', d3.line(d => x(d.year), d => y(d.left)))).attr('stroke', H.LEFT).attr('stroke-width', 3).attr('paint-order', null);
    svg.append('g').selectAll('circle').data(ld).join('circle').attr('cx', d => x(d.year)).attr('cy', d => y(d.left)).attr('r', 3).attr('fill', H.LEFT).attr('stroke', css('card')).attr('stroke-width', 1.5);
    const topv = d => keys.reduce((s2, k) => s2 + (d.share[k] || 0), 0);
    txt(svg, w - m.r + 6, y(topv(last)) + 4, f1(topv(last)), {size: 12, weight: 800, fill: H.CON});
    txt(svg, w - m.r + 6, y(last.left) + 4, f1(last.left), {size: 12, weight: 800, fill: H.LEFT});
  }
  // your riding: its own Conservative (2020: BC Liberal and Conservative) and NDP vote, dashed
  $('#howkey').innerHTML = recent && you ? `Dashed lines: ${esc(R[you].name)}, the BC Liberal and Conservative vote together (dark) and the NDP vote (orange).${ref('ebc20')}${ref('ebc24')}${ref('ebc26')}` : '';
  if (recent && you) { const rv = RV(you), yc = css('you');
    [[1, yc, true], [2, H.LEFT, false]].forEach(([i, col, solid]) => { const pts = rv.filter(d => d[i] > 0), ln = d3.line(d => x(d[0]), d => y(d[i]));
      svg.append('path').datum(pts).attr('fill', 'none').attr('stroke', css('card')).attr('stroke-width', 6).attr('d', ln);
      svg.append('path').datum(pts).attr('fill', 'none').attr('stroke', col).attr('stroke-width', 2.5).attr('stroke-dasharray', '6 4').attr('d', ln);
      svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', d => x(d[0])).attr('cy', d => y(d[i])).attr('r', 5)
        .attr('fill', solid ? col : css('card')).attr('stroke', solid ? css('card') : col).attr('stroke-width', solid ? 1.5 : 2.5); });
    const p0 = rv[0], hiR = p0[1] >= p0[2];
    halo(txt(svg, x(2020) - 9, y(hiR ? p0[1] : p0[2]) - 6, R[you].name, {anchor: 'end', size: 12, weight: 800})); }
  // the chosen election
  const xs = x(howYear);
  svg.append('line').attr('x1', xs).attr('x2', xs).attr('y1', m.t).attr('y2', h - m.b).attr('stroke', css('you')).attr('stroke-width', 2.5).attr('pointer-events', 'none');
  const yrs = D.map(d => d.year), lo = i => i ? (yrs[i] + yrs[i - 1]) / 2 : yrs[0], hi = i => i < yrs.length - 1 ? (yrs[i] + yrs[i + 1]) / 2 : yrs[i];
  svg.append('g').selectAll('rect').data(D).join('rect').attr('x', (d, i) => x(lo(i))).attr('width', (d, i) => Math.max(4, x(hi(i)) - x(lo(i)))).attr('y', m.t).attr('height', h - m.t - m.b)
    .attr('fill', 'transparent').style('cursor', 'pointer')
    .on('mousemove', (e, d) => showTip(e, `<b>${d.year}${d.initial ? ' (' + ASOF + ')' : ''}</b><br>` + keys.filter(k => (d.share[k] || 0) > 0.5).map(k => `${FAM[k]} ${f1(d.share[k])}%`).concat(d.left > 0.5 ? [`${d.year < 1961 ? 'CCF' : 'NDP'} ${f1(d.left)}%`] : []).join('<br>')))
    .on('mouseleave', hideTip).on('click', (e, d) => { howYear = d.year; drawHow(); });
  $('#years').innerHTML = (recent ? RECENT : S.history.map(d => d.year)).map(yy => `<button class="${yy === howYear ? 'on' : ''}" data-y="${yy}" aria-pressed="${yy === howYear}">${yy}</button>`).join('');
  $$('#years [data-y]').forEach(b => b.onclick = () => { howYear = +b.dataset.y; drawHow(); });
  yearCard(howYear);
}
draw(drawHow); ON_YOU.push(drawHow);
$('#say-how').innerHTML = `${RS.lib_ridings_2020_con_lead === RS.lib_ridings_2020 ? 'All' : RS.lib_ridings_2020_con_lead + ' of the'} ${RS.lib_ridings_2020} ridings the BC Liberals would have held in 2020 elected Conservatives in 2026, and so did ${RS.ndp_ridings_2020_con_lead} of the ${RS.ndp_ridings_2020} the NDP would have held.${ref('ebc20')}${ref('ebc26')}`;
const LM = S.history.filter(h => h.year < 2026 && (h.won.CON || 0) > h.seats / 2).pop();   // the last Conservative majority
$('#more-how').innerHTML = `<p>The Conservative vote by riding in 2024 closely follows the 2020 BC Liberal and Conservative vote (correlation ${RS.corr_right2020_con2024}, where 1 is a perfect match).${ref('ebc20')} The 2020 votes were moved onto the 2026 ridings by voting area to compare like with like. The Conservatives' ${f1(T.share.CON)}% in 2026 is the party's best result since ${H28.year}${H28.year === LM.year ? `, when it last had a majority: ${LM.won.CON} of ${LM.seats} seats` : `; its ${T.seats.CON} of ${N} seats are its first majority since ${LM.year}, when it had ${LM.won.CON} of ${LM.seats}`}. From 1941 to 1952 it was a partner in a coalition government with the Liberals.${ref('ebchist')}${ref('ebc26')}</p>
<p class="note">The chart shows each party's share of the vote at each B.C. election. From 2001 to 2026 each party is a line: the BC Liberal Party (BC United) to 2020, the Conservatives and the NDP. Over every election since 1928, a band stacks the main parties other than the CCF and NDP, and before 1991 it includes the Liberal Party. 2026 shows the results ${ASOF}.${ref('ebchist')}${ref('ebc26')}</p>`;
YOU.how = c => { const r = R[c], s20 = r.nw20 === 'LIB' ? 'BC Liberal' : PN[r.nw20], c20 = r.nw20 === 'LIB' ? css('LIB') : pc(r.nw20);
  const chip = (y, col, a, b) => `<div style="border-top-color:${col}"><b>${y}</b><span>${a}</span><small>${b}</small></div>`;
  const m24 = r.c24 && r.c24.length > 1 ? r.c24[0][2] - r.c24[1][2] : null;
  return `<b>${esc(r.name)}</b> ${electedTxt(r)}.${ref('ebc24')}${ref('ebc26')}
    <div class="strip">${chip('2020', c20, s20, 'estimated')}${chip('2024', pc(r.win24), PN[r.win24], m24 == null ? 'elected' : `by ${fmt(m24)} votes`)}${chip('2026', pc(r.lead), PN[r.lead], `by ${fmt(r.margin)} votes`)}</div>
    <div class="note" style="margin-top:6px">2020: the 2020 votes moved onto this riding's 2026 boundaries.${ref('ebc20')}</div>`; };

// ---------------------------------------------------------------- where: the map
const feats = topojson.feature(TOPO, TOPO.objects.districts).features;
const svgm = d3.select('#map'), MW = 640, MH = 560;
const meshBC = topojson.mesh(TOPO, TOPO.objects.districts, (a, b) => a !== b);
const DZ = Object.fromEntries(Object.entries(DETAIL).map(([z, t]) => [z, {feats: topojson.feature(t, t.objects.districts).features,
  water: topojson.feature(t, t.objects.water).features, mask: topojson.feature(t, t.objects.mask), mesh: topojson.mesh(t, t.objects.districts, (a, b) => a !== b)}]));
const gMask = svgm.append('g').attr('class', 'maskg'), gLand = svgm.append('g').attr('class', 'land'), gBord = svgm.append('path').attr('class', 'borders'),
  gWater = svgm.append('g').attr('class', 'water'), gSel = svgm.append('path').attr('class', 'selline');
const layer = $('#layer');
const PT = ['Active core', 'Transit suburb', 'Car suburb', 'Exurban and rural'], ptc = t => css('pt' + (PT.indexOf(t) + 1));
const CHIPS = [['flip', 'Changed party since 2024'], ['lead', 'Party elected, 2026'], ['tp', 'Swing'], ['ptype', 'Type of place'], ['fed', 'Federal vote, 2025']];
const MORE = [['nw20', '2020 provincial result on these ridings'], ['CON', 'Conservative share, 2026 provincial election'], ['NDP', 'NDP share, 2026 provincial election'], ['GRN', 'Green share, 2026 provincial election'],
  ['fedLPC', 'Liberal share, 2025 federal election']].concat(S.census.map(c => ['c:' + c.k, c.label + ' (2021 Census)']));
const LAYERS = CHIPS.concat(MORE);
let layerKey = 'flip', zoom = 'metro', ptHi = null;
function drawChips() {
  $('#layers').innerHTML = CHIPS.map(([k, l]) => `<button data-layer="${k}" class="${k === layerKey ? 'on' : ''}" aria-pressed="${k === layerKey}">${l}</button>`).join('');
  $$('[data-layer]').forEach(b => b.onclick = () => { layerKey = b.dataset.layer; layer.value = ''; if (layerKey !== 'ptype') ptHi = null; drawChips(); drawMap(); drawPT(); });
}
layer.innerHTML = '<option value="">More measures</option>' + MORE.map(([k, l]) => `<option value="${k}">${l}</option>`).join('');
layer.onchange = () => { if (!layer.value) return; layerKey = layer.value; ptHi = null; drawChips(); drawMap(); drawPT(); };
const BOX = {metro: [[-123.28, 49.0], [-122.45, 49.43]], vic: [[-123.75, 48.3], [-123.25, 48.75]], okan: [[-120.0, 49.4], [-119.1, 50.45]]};
const zoneOf = c => R[c].region === 'Metro Vancouver' ? 'metro' : R[c].region.startsWith('Capital') ? 'vic' : R[c].region === 'Okanagan' ? 'okan' : 'bc';
function val(c, k) {
  const r = R[c];
  if (k === 'tp') return r.tp; if (['CON', 'NDP', 'GRN'].includes(k)) return r.s26[k]; if (k === 'fedLPC') return r.fed.LPC;
  if (k.startsWith('c:')) return r.census[k.slice(2)]; return null;
}
function unit(k) { if (k.startsWith('c:')) return S.census.find(x => x.k === k.slice(2)).unit; return k === 'tp' ? 'pts' : '%'; }
function fmtv(k, v) { const u = unit(k); return v == null ? 'n/a' : u === '$' ? money(v) : u === '%' ? f1(v) + '%' : u === 'pts' ? sgn(v) : u === 'yrs' ? f1(v) + ' years' : fmt(Math.round(v)) + ' per km²'; }
const muted = p => d3.interpolateRgb(css('land'), pc(p))(.42) + '';
function colorFn(k) {
  const soft = css('land');
  if (k === 'flip') return c => R[c].flip ? pc(R[c].lead) : muted(R[c].lead);
  if (k === 'lead') return c => d3.color(pc(R[c].lead)).copy({opacity: R[c].flip ? 1 : .45}) + '';
  if (k === 'ptype') return c => ptHi && R[c].ptype !== ptHi ? soft : ptc(R[c].ptype);
  if (k === 'nw20') return c => ({LIB: css('LIB'), NDP: css('NDP'), GRN: css('GRN'), CON: css('CON')})[R[c].nw20] || soft;
  if (k === 'fed') return c => fc(R[c].fedwin);
  const vs = codes.map(c => val(c, k)).filter(v => v != null);
  if (k === 'tp') { const m = d3.max(vs.map(Math.abs)); return c => { const v = val(c, k); if (v == null) return soft; return d3.interpolateRgb(soft, v >= 0 ? pc('CON') : pc('NDP'))(Math.min(1, Math.abs(v) / m * 1.6)); }; }
  const base = ['CON', 'NDP', 'GRN'].includes(k) ? pc(k) : k === 'fedLPC' ? css('LPC') : css('text');
  const q = d3.scaleQuantile(vs, d3.range(5)), ramp = d3.range(5).map(i => d3.interpolateRgb(soft, base)(.18 + i * .2));
  return c => val(c, k) == null ? soft : ramp[q(val(c, k))];
}
function legend(k) {
  const L = items => `<div class="legend">${items.map(([c, t, o]) => `<span><i style="background:${c};${o ? 'opacity:' + o : ''}"></i>${t}</span>`).join('')}</div>`;
  if (k === 'flip') return L([[pc('CON'), 'Switched to Conservative'], [pc('NDP'), 'Switched to NDP']])
    + L(['CON', 'NDP', 'GRN'].map(p => [muted(p), `${PN[p]} both years`]))
    + `<div class="note">Party elected provincially in 2026 against the party elected in 2024. Suburbs: Metro Vancouver ridings outside the City of Vancouver.${ref('ebc26')}${ref('ebc24')}</div>`;
  if (k === 'lead') return L(['CON', 'NDP', 'GRN'].map(p => [pc(p), PN[p]])) + `<div class="note">Solid: changed party since 2024. Faded: same party as 2024.${ref('ebc26')}${ref('ebc24')}</div>`;
  if (k === 'ptype') return L(PT.map(t => [ptc(t), t])) + `<div class="note">How people get to work and how densely they live (2021 Census).${ref('suburbs')}${ref('bcstats')}</div>`;
  if (k === 'nw20') return L([[css('LIB'), 'BC Liberal'], [css('NDP'), 'NDP'], [css('GRN'), 'Green']]) + `<div class="note">Most votes in the 2020 B.C. election, with the 2020 votes moved onto the 2026 ridings.${ref('ebc20')}</div>`;
  if (k === 'fed') return L(Object.keys(FN).map(p => [fc(p), FN[p]])) + `<div class="note">Most votes in the April 28, 2025 federal election, with the federal results moved onto the provincial ridings poll by poll.${ref('ecan25')}</div>`;
  if (k === 'tp') return L([[pc('NDP'), 'Moved toward the NDP'], [pc('CON'), 'Moved toward the Conservatives']]) + `<div class="note">Change in the Conservative share of the Conservative and NDP vote, 2024 to 2026.${ref('ebc26')}${ref('ebc24')}</div>`;
  const vs = codes.map(c => val(c, k)).filter(v => v != null).sort(d3.ascending);
  return `<div class="legend"><span>Lightest: lowest fifth of ridings (under ${fmtv(k, d3.quantile(vs, .2))})</span><span>Darkest: highest fifth (over ${fmtv(k, d3.quantile(vs, .8))})</span></div><div class="note">${k.startsWith('c:') ? ref('bcstats') : k === 'fedLPC' ? ref('ecan25') : ref('ebc26')}</div>`;
}
function drawMap() {
  const fs = zoom === 'bc' ? {type: 'FeatureCollection', features: feats} : {type: 'MultiPoint', coordinates: [BOX[zoom][0], BOX[zoom][1], [BOX[zoom][0][0], BOX[zoom][1][1]], [BOX[zoom][1][0], BOX[zoom][0][1]]]};
  // province: B.C. Albers-style projection; zoomed views: centred on the view, so north is straight up and the 49th parallel runs level
  const base = zoom === 'bc' ? d3.geoConicEqualArea().parallels([50, 58.5]).rotate([126, 0])
    : d3.geoConicEqualArea().parallels([48.5, 50.5]).rotate([-(BOX[zoom][0][0] + BOX[zoom][1][0]) / 2, 0]);
  const proj = base.fitExtent([[6, 6], [MW - 6, MH - 6]], fs);
  // Metro Vancouver: the frame's bottom edge sits on the 49th parallel, the border, so no United States shows below it
  if (zoom === 'metro') { const yb = proj([(BOX.metro[0][0] + BOX.metro[1][0]) / 2, 49])[1], t = proj.translate(); proj.translate([t[0], t[1] + MH - yb]); }
  const path = d3.geoPath(proj), k = layerKey, col = colorFn(k), lab = (LAYERS.find(l => l[0] === k) || [])[1];
  const det = zoom === 'bc' ? null : DZ[zoom], F = det ? det.feats : feats;
  gMask.selectAll('path').data(det ? [det.mask] : []).join('path').attr('d', path);
  gBord.attr('d', path(det ? det.mesh : meshBC));
  gWater.selectAll('path').data(det ? det.water : []).join('path').attr('d', path);
  const sf = F.find(d => d.properties.ed_code === you); gSel.attr('d', sf ? path(sf) : null);
  gLand.selectAll('path').data(F, d => d.properties.ed_code).join('path').attr('d', path)
    .attr('fill', d => col(d.properties.ed_code))
    .on('click', (e, d) => setYou(d.properties.ed_code, {zoom: false}))
    .on('mousemove', (e, d) => { const c = d.properties.ed_code, r = R[c];
      showTip(e, `<b>${esc(r.name)}</b><br>${k === 'fed' || k === 'fedLPC' ? 'Provincial, 2026: ' : ''}${leadTxt(c)}` + (r.flip ? `<br>Changed party (${PN[r.win24]} in 2024)` : '') +
        (k.startsWith('c:') || ['tp', 'CON', 'NDP', 'GRN', 'fedLPC'].includes(k) ? `<br>${lab}: ${fmtv(k, val(c, k))}` : k === 'ptype' ? `<br>${r.ptype}` : k === 'fed' ? `<br>Federal, 2025: most votes for the ${FNP[r.fedwin]}` : k === 'nw20' ? `<br>Most votes in the 2020 provincial election: ${r.nw20 === 'LIB' ? 'BC Liberal' : PN[r.nw20]}` : '')); })
    .on('mouseleave', hideTip);
  $('#maplegend').innerHTML = legend(k);
}
function setZoom(z) { zoom = z; $$('[data-z]').forEach(x => { x.classList.toggle('on', x.dataset.z === z); x.setAttribute('aria-pressed', String(x.dataset.z === z)); }); }
$$('[data-z]').forEach(b => b.onclick = () => { setZoom(b.dataset.z); drawMap(); });
const share = (r, p) => (r.c26.find(x => x[1] === p) || [0, 0, 0, 0])[3];
function drawPanel() {
  if (!you) { $('#panel').innerHTML = `<h3>Tap a riding</h3><p class="note">Its card shows the 2026 and 2024 provincial results, the swing and the 2025 federal vote. Use the buttons under the map to zoom in on Metro Vancouver, Victoria or the Okanagan.</p>`; return; }
  const r = R[you], top3 = r.c26.slice(0, 3);
  const g = r.fedwin === 'LPC' ? 'Liberal' : r.fedwin === 'CPC' ? 'Conservative' : r.fedwin === 'NDP' ? 'NDP' : 'Green';
  $('#panel').innerHTML = `<h3>${esc(r.name)}</h3><div class="note">${regName(r.region)} · ${r.ptype}</div>
  <div class="big" style="color:${pc(r.lead)}">${leadTxt(you)}</div>` +
  top3.map(([n, p, v, s]) => `<div class="cbar"><span><span class="dot" style="background:${pc(p)}"></span>${esc(n)} (${PN[p] || p})</span><b>${f1(s)}%</b><span class="tr"><i style="width:${s}%;background:${pc(p)}"></i></span></div>`).join('') +
  `<div class="facts"><div><small>2024 provincial election</small><b>${PN[r.win24]} elected</b></div>
  ${grnRace(you) ? `<div><small>Green share, 2024 to 2026</small><b>${sgn(chg(r, 'GRN'))} points</b></div>` : `<div><small>Provincial swing, 2024 to 2026</small><b>${r.tp == null ? 'not measured' : sgn(r.tp) + ' to ' + (r.tp >= 0 ? 'Con.' : 'NDP')}</b></div>`}
  <div><small>2025 federal vote</small><b>${g} ${f1(r.fed[r.fedwin])}%</b></div>
  <div><small>Ballot boxes counted</small><b>${r.boxes[0]} of ${r.boxes[1]}</b></div></div>
  <p class="note" style="margin:8px 0 0">Provincial results ${ASOF}${ref('ebc26')} and 2024${ref('ebc24')}; federal results, 2025${ref('ecan25')}.${r.tp == null ? ' No NDP candidate ran in 2026.' : ''}</p>`;
}
ON_YOU.push(() => { drawMap(); drawPanel(); });
drawChips(); draw(drawMap); drawPanel();
const swCon = T.switched.filter(s => s.to === 'CON'), swNdp = T.switched.filter(s => s.to === 'NDP'), swOut = T.switched.filter(s => s.region !== 'Metro Vancouver');
const areaList = Object.entries(T.switched_metro_areas).map(([a, n]) => `${a}${n > 1 ? ' (' + n + ')' : ''}`);
const tpAll = codes.filter(c => R[c].tp != null).map(c => R[c].tp).sort(d3.ascending);
const toNDP = codes.filter(c => R[c].tp != null && R[c].tp < 0 && !grnRace(c)).length;   // ridings that moved toward the NDP, Green races left out
const ptName = t => art(t === 'Exurban and rural' ? 'exurban and rural riding' : t.toLowerCase());
const moved = (r, k, nm) => `${nm} ${chg(r, k) >= 0 ? 'rose' : 'fell'} ${f1(Math.abs(chg(r, k)))}`;
YOU.where = c => { const r = R[c], who = `<b>${esc(r.name)}</b>, ${ptName(r.ptype)},`, refs = `${ref('ebc26')}${ref('ebc24')}`;
  if (r.tp == null) return `${who} had no NDP candidate in 2026, so its swing is not measured.${ref('ebc26')}`;
  if (grnRace(c)) return `In <b>${esc(r.name)}</b>, ${ptName(r.ptype)}, ${top2Txt(c)} took the top two places in 2026. The ${moved(r, 'GRN', 'Green share')} points from 2024, the ${moved(r, 'NDP', "NDP's")} and the ${moved(r, 'CON', "Conservatives'")}.${refs}`;
  if (r.tp < 0) return `${who} swung ${f1(-r.tp)} points toward the NDP, one of ${word(toNDP).toLowerCase()} ridings that moved that way.${refs}`;
  return `${who} swung ${f1(r.tp)} points toward the Conservatives, ${rankIn(tpAll, r.tp, 'a bigger swing', 'a smaller swing')}.${refs}`; };
const swConOut = swOut.filter(s => s.to === 'CON'), swNdpOut = swOut.filter(s => s.to === 'NDP'), SY = T.surrey;
$('#say-where').innerHTML = `${SY.con26 === SY.n ? 'All ' + SY.n : SY.con26 + ' of ' + SY.n} Surrey ridings elected Conservatives, up from ${SY.con24} in 2024. Outside Metro Vancouver, ${word(swConOut.length).toLowerCase()} more ridings switched to the Conservatives${swNdpOut.length ? `, and ${and(swNdpOut.map(s => s.name))} to the NDP` : ''}.${ref('ebc26')}${ref('ebc24')}`;
$('#more-where').innerHTML = `<p>${T.n_switched} ridings changed party, ${T.n_switched_metro} of them in Metro Vancouver: ${and(areaList)}. Elsewhere, ${and(swConOut.map(s => s.name))} changed to the Conservatives${swNdpOut.length ? `, and ${and(swNdpOut.map(s => s.name))} to the NDP` : ''}.${ref('ebc26')}${ref('ebc24')}</p>
<p>Ridings are grouped by how densely people live and how they get to work, following the commuting method of the Canadian Suburbs project led by David Gordon at Queen's University: exurban and rural ridings have under 150 people per km²; of the rest, active cores are where many walk or cycle to work, transit suburbs have above-average transit use, and car suburbs are where most drive.${ref('suburbs')}${ref('bcstats')} The project tests walking and cycling first, but only for census tracts inside metropolitan areas; for whole ridings the density test comes first, so a large rural riding with a walkable town counts as rural. Of the ${T.n_switched} ridings that changed party, ${T.suburb_switched} are transit or car suburbs. In the dot chart, solid, ringed dots changed party and the dark line marks each type's average. Peace River North, with no NDP candidate in 2026, is left out.${ref('ebc26')}</p>
<p><b>By region.</b> Each region's share of the vote in 2024 and 2026, and its ridings.</p>`;

// place types: every riding as a dot along the swing, one row per type of place
function dodge(pts, d) {   // simple beeswarm: each dot takes the nearest free spot above or below the axis
  const placed = [];
  for (const p of pts) { let off = 0;
    for (let k = 0; k < 600; k++) { const o = k === 0 ? 0 : (k % 2 ? 1 : -1) * Math.ceil(k / 2);
      if (placed.every(q => Math.abs(q.x - p.x) >= d || (q.x - p.x) ** 2 + (q.dy - o) ** 2 >= d * d)) { off = o; break; } }
    p.dy = off; placed.push(p); }
  return d3.max(pts, p => Math.abs(p.dy)) || 0;
}
function drawPT() {
  const w0 = cw('#ptchart'), r = w0 < 500 ? 4.5 : 5.5, all = codes.filter(c => R[c].tp != null), ext = d3.extent(all, c => R[c].tp);
  const x = d3.scaleLinear().domain([Math.min(0, ext[0]), ext[1]]).nice().range([16, w0 - 20]);
  const rows = T.place_types.map(d => { const pts = all.filter(c => R[c].ptype === d.type).map(c => ({c, x: x(R[c].tp)})).sort((a, b) => a.x - b.x); return {d, pts, spread: dodge(pts, 2 * r + 1)}; });
  let yy = 2; rows.forEach(o => { o.y0 = yy; o.cy = yy + 40 + o.spread + r; o.h = 48 + 2 * (o.spread + r); yy += o.h; });
  const {svg, w, h} = frame('#ptchart', yy + 42);
  svg.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 36).attr('y2', yy).attr('stroke', css('muted')).attr('stroke-dasharray', '3 4');
  const P2 = [];
  rows.forEach(({d, pts, y0, cy, h: rh}) => {
    const g = svg.append('g');
    g.append('rect').attr('x', 0).attr('y', y0).attr('width', w).attr('height', rh - 4).attr('rx', 8).attr('fill', ptHi === d.type ? css('hi') : 'transparent');
    txt(g, 6, y0 + 16, d.type, {size: 13, weight: 800});
    txt(g, 6, y0 + 32, w < 360 ? `${d.n} ridings · ${d.switched} changed · average ${sgn(d.swing)}` : `${d.n} ridings · ${d.switched} changed party · average ${sgn(d.swing)} points`, {size: 12, fill: css('muted')});
    g.append('line').attr('x1', x(d.swing)).attr('x2', x(d.swing)).attr('y1', y0 + 38).attr('y2', y0 + rh - 6).attr('stroke', css('text')).attr('stroke-width', 2.5);
    g.selectAll('circle').data(pts).join('circle').attr('cx', p => p.x).attr('cy', p => cy + p.dy).attr('r', r)
      .attr('fill', ptc(d.type)).attr('fill-opacity', p => R[p.c].flip ? 1 : .5).attr('stroke', p => R[p.c].flip ? css('text') : 'none').attr('stroke-width', 1.6);
    pts.forEach(p => P2.push({x: p.x, y: cy + p.dy, c: p.c, row: d.type, y0, y1: y0 + rh}));
  });
  const me = P2.find(p => p.c === you);
  if (me) { svg.append('circle').attr('cx', me.x).attr('cy', me.y).attr('r', r + 5).attr('fill', 'none').attr('stroke', css('you')).attr('stroke-width', 3);
    halo(txt(svg, Math.min(w - 4, Math.max(4, me.x)), me.y - r - 9, R[me.c].name, {anchor: me.x > w * .7 ? 'end' : me.x < w * .3 ? 'start' : 'middle', size: 12, weight: 800})); }
  axis(svg.append('g').attr('transform', `translate(0,${yy + 2})`), d3.axisBottom(x).ticks(w < 500 ? 5 : 8).tickFormat(v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v)));
  txt(svg, w - 4, h - 4, w < 520 ? 'Swing to the Conservatives (points)' : 'Swing toward the Conservatives, 2024 to 2026 (points)', {anchor: 'end', size: 12, fill: css('muted')});
  nearest(svg, P2, p => setYou(p.c), e => { const [, my] = d3.pointer(e); const row = rows.find(o => my >= o.y0 && my <= o.y0 + o.h); if (!row) return;
      ptHi = ptHi === row.d.type ? null : row.d.type; layerKey = 'ptype'; layer.value = ''; drawChips(); drawMap(); drawPT(); },
    p => `<b>${esc(R[p.c].name)}</b><br>Swing ${sgn(R[p.c].tp)} points${R[p.c].flip ? `<br>Changed party: ${PN[R[p.c].win24]} to ${PN[R[p.c].lead]}` : ''}`, 16);
}
draw(drawPT); ON_YOU.push(drawPT);
const ptr = T.suburb_swing / T.core_rural_swing, ptn = Math.round(ptr);
$('#ptnote').innerHTML = `Across B.C., transit and car suburbs swung ${f1(T.suburb_swing)} points toward the Conservatives on average, ${Math.abs(ptr - ptn) < .15 && ptn >= 2 ? (ptn === 2 ? 'about twice' : `about ${word(ptn).toLowerCase()} times`) : 'against'} the ${f1(T.core_rural_swing)} in active cores and exurban and rural ridings. Tap a row to show that type on the map.${ref('suburbs')}${ref('bcstats')}${ref('ebc26')}${ref('ebc24')}`;
// regions: 2024 and 2026 shares as dots on one line (inside More about this)
const RG = S.regions;
let reg = 'Metro Vancouver';
function dumbbell(p, a, b) { const W = 136, sx = v => 6 + Math.min(v, 70) / 70 * (W - 12), c = pc(p);
  return `<svg width="${W}" height="18" viewBox="0 0 ${W} 18" aria-hidden="true"><line x1="${sx(0)}" x2="${sx(70)}" y1="9" y2="9" stroke="${css('line')}" stroke-width="2"/><line x1="${sx(a)}" x2="${sx(b)}" y1="9" y2="9" stroke="${c}" stroke-width="2.5"/><circle cx="${sx(a)}" cy="9" r="4.5" fill="${css('card')}" stroke="${c}" stroke-width="2"/><circle cx="${sx(b)}" cy="9" r="5.5" fill="${c}"/></svg>`; }
function drawReg() {
  $('#regbtn').innerHTML = RG.map(r => `<button class="${r.region === reg ? 'on' : ''}" data-r="${r.region}">${regName(r.region)}</button>`).join('');
  $$('[data-r]').forEach(b => b.onclick = () => { reg = b.dataset.r; drawReg(); });
  const r = RG.find(x => x.region === reg), rc = codes.filter(c => R[c].region === reg);
  const seats = (p, k) => rc.filter(c => R[c][k] === p).length;
  const rows = ['CON', 'NDP', 'GRN'].map(p => `<tr><td><span class="dot" style="background:${pc(p)}"></span>${PN[p]}</td>
    <td>${dumbbell(p, r[p + '24'], r[p + '26'])}<div>${f1(r[p + '24'])}% → <b>${f1(r[p + '26'])}%</b></div></td><td class="n">${seats(p, 'win24')} → <b>${seats(p, 'lead')}</b></td></tr>`).join('');
  const ch = rc.filter(c => R[c].flip).map(c => `${R[c].name} (${PN[R[c].win24]} to ${PN[R[c].lead]})`);
  $('#regchart').innerHTML = `<table><tr><th>Party</th><th>Share of the vote, ○ 2024 → ● 2026</th><th class="n">Seats, 2024 → 2026</th></tr>${rows}</table>
   <p class="note">${r.ridings} ridings. The line under each share runs from 0 to 70%. Changed party: ${ch.length ? ch.join(', ') : 'none'}.${ref('ebc26')}${ref('ebc24')}</p>`;
}
drawReg();

// ---------------------------------------------------------------- by household income: the slide's four groups, every riding a dot
const IG = T.income_groups, QW = ['lowest', 'second', 'third', 'highest'];
function drawInc() {
  const w0 = cw('#incchart'), nar = w0 < 520, rr = nar ? 4.2 : 5.2, H = nar ? 360 : 400, m = {l: 36, r: 6, t: 12, b: 60};
  const all = codes.filter(c => R[c].incq != null && R[c].tp != null), ext = d3.extent(all, c => R[c].tp);
  const {svg, w, h} = frame('#incchart', H);
  const x = d3.scaleBand().domain([0, 1, 2, 3]).range([m.l, w - m.r]).paddingInner(.16).paddingOuter(.04), bw = x.bandwidth();
  const y = d3.scaleLinear().domain([Math.floor(Math.min(0, ext[0]) / 5) * 5, Math.ceil(ext[1] / 5) * 5]).range([h - m.b, m.t]);
  y.ticks(6).forEach(v => svg.append('line').attr('x1', m.l).attr('x2', w - m.r).attr('y1', y(v)).attr('y2', y(v)).attr('stroke', v === 0 ? css('muted') : css('line')).attr('stroke-width', v === 0 ? 1.5 : 1));
  axis(svg.append('g').attr('transform', `translate(${m.l},0)`), d3.axisLeft(y).ticks(6).tickSize(0).tickPadding(6).tickFormat(v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v))).call(g => g.select('.domain').remove());
  const P = [];
  IG.forEach((g, i) => { const x0 = x(i), cx = x0 + bw / 2, ya = y(g.swing), y0 = y(0);
    svg.append('rect').attr('x', x0).attr('width', bw).attr('y', Math.min(ya, y0)).attr('height', Math.abs(y0 - ya)).attr('rx', 4).attr('fill', css('CON')).attr('fill-opacity', .2);
    svg.append('line').attr('x1', x0).attr('x2', x0 + bw).attr('y1', ya).attr('y2', ya).attr('stroke', css('CON')).attr('stroke-width', 3);
    const pts = all.filter(c => R[c].incq === i).map(c => ({c, x: y(R[c].tp)})).sort((a, b) => a.x - b.x);
    dodge(pts, 2 * rr + 1);   // ridings spread sideways within their column so none overlap
    pts.forEach(p => { p.cx = Math.max(x0 + rr, Math.min(x0 + bw - rr, cx + p.dy)); p.cy = p.x; P.push({x: p.cx, y: p.cy, c: p.c}); });
    svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', p => p.cx).attr('cy', p => p.cy).attr('r', rr)
      .attr('fill', css('text')).attr('fill-opacity', .45).attr('stroke', css('card')).attr('stroke-width', 1);
    txt(svg, cx, h - m.b + 21, sgn(g.swing), {anchor: 'middle', size: nar ? 15 : 17, weight: 800, fill: css('CON')});
    txt(svg, cx, h - m.b + 38, money(g.income), {anchor: 'middle', size: 13, weight: 700});
    txt(svg, cx, h - m.b + 54, nar ? QW[i] : QW[i] + ' income', {anchor: 'middle', size: 11, fill: css('muted')});
  });
  const me = P.find(p => p.c === you);
  if (me) { svg.append('circle').attr('cx', me.x).attr('cy', me.y).attr('r', rr + 5).attr('fill', 'none').attr('stroke', css('you')).attr('stroke-width', 3);
    svg.append('circle').attr('cx', me.x).attr('cy', me.y).attr('r', rr).attr('fill', css('you'));
    halo(txt(svg, Math.min(w - 4, Math.max(m.l + 2, me.x)), Math.max(14, me.y - rr - 9), R[me.c].name, {anchor: me.x > w * .7 ? 'end' : me.x < w * .3 ? 'start' : 'middle', size: 12, weight: 800})); }
  nearest(svg, P, p => setYou(p.c), null, p => `<b>${esc(R[p.c].name)}</b><br>Median household income ${money(R[p.c].census.hh_income_median)}<br>Swing ${sgn(R[p.c].tp)} points<br>Elected in 2026: ${PN[R[p.c].lead]}`, 16);
}
draw(drawInc); ON_YOU.push(drawInc);
const incRefs = `${ref('bcstats')}${ref('ebc26')}${ref('ebc24')}`;
$('#incsub').innerHTML = `Four groups of ${IG[0].n} ridings, ranked by median household income. Bars: each group's average swing; dots: its ridings.`;
$('#incnote').innerHTML = `Swing: change in the Conservative share of the Conservative and NDP vote, 2024 to 2026, in points. Under each group: its average swing and its typical riding's median household income (2021 Census). Peace River North, with no NDP candidate in 2026, is left out. These describe places and say nothing about how any one person voted.${incRefs}`;
YOU.who = c => { const r = R[c], inc = r.census.hh_income_median;
  if (r.incq == null) return `<b>${esc(r.name)}</b> had no NDP candidate in 2026, so it has no swing and is left out of the income groups. Its median household income is ${money(inc)} (2021 Census).${ref('bcstats')}`;
  const g = IG[r.incq], own = grnRace(c) ? `There, ${top2Txt(c)} took the top two places in 2026.`
    : r.tp < 0 ? `It swung ${f1(-r.tp)} points toward the NDP.` : `It swung ${f1(r.tp)} points toward the Conservatives.`;
  return `<b>${esc(r.name)}</b> has a median household income of ${money(inc)} (2021 Census), in the ${QW[r.incq]} of the four income groups, whose ridings swung ${f1(g.swing)} points toward the Conservatives on average. ${own}${incRefs}`; };
const ratio = IG[3].swing / IG[0].swing, rn = Math.round(ratio);
$('#say-who').innerHTML = `Ridings in the highest income group swung ${f1(IG[3].swing)} points toward the Conservatives on average, ${Math.abs(ratio - rn) < .15 && rn >= 2 ? (rn === 2 ? 'about twice' : `about ${word(rn).toLowerCase()} times`) : 'against'} the ${f1(IG[0].swing)} points of the lowest group. Across all ${d3.sum(IG, g => g.n)} ridings, the higher a riding's income, the bigger its swing tended to be (correlation ${T.income_r}, where 1 is a perfect match).${incRefs}`;

// ---------------------------------------------------------------- who lives there: compare your riding
const WP = T.who_pooled, sm = WP.switched, sn = WP.stayed_ndp, sc = WP.stayed_con;
const GRP = c => R[c].flip ? (R[c].lead === 'CON' ? 'switched' : null) : R[c].lead === 'NDP' ? 'stayed_ndp' : R[c].lead === 'CON' ? 'stayed_con' : null;
const GL = {switched: 'Switched to Conservative', stayed_ndp: 'Stayed NDP', stayed_con: 'Stayed Conservative'};
const GC = () => ({switched: css('CON'), stayed_ndp: css('NDP'), stayed_con: d3.interpolateRgb(css('soft'), css('CON'))(.45)});
const CARD = [['own', 'pct_hh_owner', 'own their home'], ['vismin', 'pct_vm_total', 'visible minorities'],
  ['drive', 'pct_commute_car', 'go to work by car'], ['income', 'hh_income_median', 'median household income']];
function drawCmp() {
  const G = GC();
  const card = (title, sub, col, get, me) => `<div class="pcard${me ? ' me' : ''}" style="border-top-color:${col}"><div class="ph"><b>${esc(title)}</b><span>${sub}</span></div>` +
    CARD.map(([k, ck, label]) => { const v = get(k, ck); return `<div class="pr"><div class="bigv">${k === 'income' ? money(v) : pct0(v)}</div><div class="pl">${label}</div></div>`; }).join('') + '</div>';
  const grp = g => card(GL[g], `${WP[g].n} ridings`, G[g], (k) => WP[g][k], false);
  $('#cmpchart').innerHTML = you
    ? card(R[you].name, 'Your riding', pc(R[you].lead), (k, ck) => R[you].census[ck], true) + grp('switched') + grp('stayed_ndp')
    : grp('switched') + grp('stayed_ndp') + grp('stayed_con');
}
draw(drawCmp); ON_YOU.push(drawCmp);
$('#cmpnote').innerHTML = `Of the three groups, ridings that stayed Conservative have the most homeowners and car commuters: ${pct0(sc.own)} and ${pct0(sc.drive)}. Each card counts every household, commuter or resident in its group's ridings together.${ref('bcstats')}${ref('ebc26')}`;
// scatter: any other census measure against the swing (income has its own chart above)
const XCH = [['pct_hh_owner', 'Home owners'], ['pct_commute_car', 'Go to work by car'], ['pct_vm_total', 'Visible minority'], ['pct_bachelor_plus_25_64', 'University degree'], ['median_age', 'Median age'], ['hh_income_median', 'Income']];
let xk = 'pct_hh_owner';
function pearson(a, b) { const ma = d3.mean(a), mb = d3.mean(b); let s = 0, sa = 0, sb = 0; a.forEach((v, i) => { s += (v - ma) * (b[i] - mb); sa += (v - ma) ** 2; sb += (b[i] - mb) ** 2; }); return s / Math.sqrt(sa * sb); }
function drawXChips() {
  $('#xchips').innerHTML = XCH.map(([k, l]) => `<button data-x="${k}" class="${k === xk ? 'on' : ''}" aria-pressed="${k === xk}">${l}</button>`).join('');
  $$('[data-x]').forEach(b => b.onclick = () => { xk = b.dataset.x; $('#xvar').value = ''; drawXChips(); drawWho(); });
}
$('#xvar').innerHTML = '<option value="">More measures</option>' + S.census.filter(c => !XCH.some(x => x[0] === c.k)).map(c => `<option value="${c.k}">${c.label}</option>`).join('');
$('#xvar').onchange = () => { if (!$('#xvar').value) return; xk = $('#xvar').value; drawXChips(); drawWho(); };
function drawWho() {
  const cm = S.census.find(c => c.k === xk), {svg, w, h} = frame('#scatter', 360), m = {l: 46, r: 14, t: 24, b: 40};
  const pts = codes.map(c => ({c, vx: R[c].census[xk], vy: R[c].tp})).filter(d => d.vx != null && d.vy != null);
  const x = d3.scaleLinear().domain(d3.extent(pts, d => d.vx)).nice().range([m.l, w - m.r]), y = d3.scaleLinear().domain(d3.extent(pts, d => d.vy)).nice().range([h - m.b, m.t]);
  axis(svg.append('g').attr('transform', `translate(0,${h - m.b})`), d3.axisBottom(x).ticks(w < 500 ? 4 : 6).tickFormat(v => cm.unit === '$' ? '$' + d3.format('~s')(v) : cm.unit === '' ? d3.format('~s')(v) : v));
  axis(svg.append('g').attr('transform', `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickFormat(v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v)));
  if (y.domain()[0] < 0 && y.domain()[1] > 0) svg.append('line').attr('x1', m.l).attr('x2', w - m.r).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', css('muted'));
  txt(svg, w - m.r, h - 6, cm.label + (cm.unit === '%' ? ' (%)' : ''), {anchor: 'end', size: 12, fill: css('muted')});
  txt(svg, 0, 12, 'Swing toward the Conservatives (points)', {size: 12, fill: css('muted')});
  pts.forEach(p => { p.x = x(p.vx); p.y = y(p.vy); });
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', d => d.x).attr('cy', d => d.y).attr('r', w < 500 ? 5 : 6)
    .attr('fill', d => pc(R[d.c].lead)).attr('fill-opacity', .75).attr('stroke', css('card'));
  const me = pts.find(p => p.c === you);
  if (me) { svg.append('circle').attr('cx', me.x).attr('cy', me.y).attr('r', 11).attr('fill', 'none').attr('stroke', css('you')).attr('stroke-width', 3);
    halo(txt(svg, me.x > w * .6 ? me.x - 14 : me.x + 14, me.y + 4, R[me.c].name, {anchor: me.x > w * .6 ? 'end' : 'start', size: 12, weight: 800})); }
  nearest(svg, pts, p => setYou(p.c), null, p => `<b>${esc(R[p.c].name)}</b><br>${cm.label}: ${fmtv('c:' + xk, p.vx)}<br>Swing ${sgn(p.vy)} points`, 18);
  const rr = pearson(pts.map(d => d.vx), pts.map(d => d.vy));
  $('#scstat').innerHTML = `Across ${pts.length} ridings the link is ${Math.abs(rr) < .2 ? 'little or none' : Math.abs(rr) < .4 ? 'weak' : Math.abs(rr) < .6 ? 'moderate' : 'strong'} (r = ${rr2(rr)})${Math.abs(rr) >= .2 ? `: ridings higher on this measure swung ${rr > 0 ? 'more' : 'less'} toward the Conservatives` : ''}. Dots are coloured by the party elected in 2026.${ref('bcstats')}${ref('ebc26')}`;
  const s = pts.slice().sort((a, b) => a.vx - b.vx), q = i => s.slice(Math.floor(i * s.length / 4), Math.floor((i + 1) * s.length / 4));
  $('#quart').innerHTML = `<table><tr><th>Ridings by ${lc1(cm.label)}</th><th class="n">Middle value</th><th class="n">Average swing (points)</th></tr>` +
    [0, 1, 2, 3].map(i => `<tr><td>${['Lowest quarter', 'Second quarter', 'Third quarter', 'Highest quarter'][i]}</td><td class="n">${fmtv('c:' + xk, d3.median(q(i), d => d.vx))}</td><td class="n">${sgn(d3.mean(q(i), d => d.vy))}</td></tr>`).join('') + '</table>';
}
drawXChips(); draw(drawWho); ON_YOU.push(drawWho);
// income x education groups (inside More about this)
const IE = T.income_education, base92 = codes.filter(c => c !== 'PCN');
const mi = d3.median(base92, c => R[c].census.hh_income_median), me = d3.median(base92, c => R[c].census.pct_bachelor_plus_25_64);
const ieOf = c => [R[c].census.hh_income_median >= mi ? 'Higher income' : 'Lower income', R[c].census.pct_bachelor_plus_25_64 >= me ? 'more degrees' : 'fewer degrees'];
let ieSel = null;
function drawIE() {
  const order = [['Higher income', 'fewer degrees'], ['Higher income', 'more degrees'], ['Lower income', 'fewer degrees'], ['Lower income', 'more degrees']];
  const mx = d3.max(IE, d => d.swing);
  $('#iegrid').innerHTML = order.map(([a, b]) => { const d = IE.find(x => x.income === a && x.education === b); const on = ieSel && ieSel[0] === a && ieSel[1] === b;
    return `<button class="cell${on ? ' on' : ''}" data-ie="${a}|${b}" aria-pressed="${!!on}" style="background:${d3.interpolateRgb(css('card'), css('CON'))(d.swing / mx * .3)}"><small>${a}, ${b}</small><b>${sgn(d.swing)}</b><small>points toward the Conservatives · ${d.n} ridings · ${d.switched} changed party</small></button>`; }).join('');
  $$('[data-ie]').forEach(el => el.onclick = () => { ieSel = el.dataset.ie.split('|'); drawIE(); });
  $('#ielist').innerHTML = ieSel ? `<b>${ieSel[0]}, ${ieSel[1]}:</b> ` + base92.filter(c => { const g = ieOf(c); return g[0] === ieSel[0] && g[1] === ieSel[1]; }).sort((a, b) => R[b].tp - R[a].tp)
    .map(c => `<button class="link" data-sel="${c}">${esc(R[c].name)}</button> (${sgn(R[c].tp)})`).join(', ') : '';
  $$('#ielist [data-sel]').forEach(a => a.onclick = () => setYou(a.dataset.sel, {scrollTo: '#where'}));
}
drawIE();
const rentTop = codes.slice().sort((a, b) => R[b].census.pct_hh_renter - R[a].census.pct_hh_renter).slice(0, Math.round(N / 4));
const rentNDP = rentTop.filter(c => R[c].lead === 'NDP').length;
const rq = codes.filter(c => R[c].tp != null), rrent = pearson(rq.map(c => R[c].census.pct_hh_renter), rq.map(c => R[c].tp));
const vm = `${f1(sm.vismin)}% of residents are visible minorities`;
const grnBoth = codes.filter(c => R[c].win24 === 'GRN' && R[c].lead === 'GRN').length;
$('#more-who').innerHTML = `<p><b>The income groups.</b> Ridings are ranked by median household income (2020 incomes, 2021 Census) and cut into four groups of ${IG[0].n}, with Peace River North (no NDP candidate in 2026) left out. Each group's swing is the average, over its ridings, of the change in the Conservative share of the Conservative and NDP vote, 2024 to 2026; the income under each group is its typical (middle) riding's median. Across the ${d3.sum(IG, g => g.n)} ridings the correlation between income and swing is ${T.income_r}.${incRefs}</p>
<p><b>The census cards.</b> Across the ${sm.n} ridings that switched to the Conservatives, ${f1(sm.own)}% of households own their home and ${f1(sm.drive)}% of commuters go to work by car, against ${f1(sn.own)}% and ${f1(sn.drive)}% in the ${sn.n} ridings that stayed NDP, and ${f1(sc.own)}% and ${f1(sc.drive)}% in the ${sc.n} that stayed Conservative. ${vm}, against ${f1(sn.vismin)}% in ridings that stayed NDP and ${f1(sc.vismin)}% in ridings that stayed Conservative. In the typical riding that switched, the median household income is ${money(sm.income)}, against ${money(sn.income)} in ridings that stayed NDP and ${money(sc.income)} in ridings that stayed Conservative. ${and(swNdp.map(s => s.name))}, which moved to the NDP, and the ${word(grnBoth).toLowerCase()} ridings that elected Greens both years are left out.${ref('bcstats')}${ref('ebc26')}${ref('ebc24')}</p>
<p class="note">The group cards count every household, commuter or resident in each group's ridings together; income is the typical (middle) riding's median. The cards round shares to whole percentages. These describe places as a whole and do not show how any one person voted. Income measures have the strongest links with the swing among the census measures here; links to immigration and visible minority share weaken by about a third, and to education by half, once income, age, renting and Metro Vancouver are held equal. Renter-heavy ridings swung about as much as others (r = ${rr2(rrent)}), and NDP candidates were elected in ${rentNDP} of the ${rentTop.length} ridings with the most renters.${ref('bcstats')}${ref('ebc26')}</p>
<p><b>Income and education together.</b> Splitting ridings at the middle value of household income and of university degrees gives four groups, an approach used in research on how income and education shape party support.${ref('kr')} Ridings higher on both moved most toward the Conservatives; ridings lower on both moved least. Tap a group to list its ridings.</p>`;

// ---------------------------------------------------------------- the middle ground: one small alluvial per federal group, B.C. 2024 to B.C. 2026
const MD = T.middle, MF = T.middle_flows;
const AG = [{k: 'right', label: 'Conservative federally', keys: ['CPC']}, {k: 'mid', label: 'Liberal federally', keys: ['LPC']}, {k: 'left', label: 'NDP or Green federally', keys: ['NDP', 'GPC']}];
AG.forEach(g => { g.n = d3.sum(g.keys, k => MD[k].n); g.fl = {}; g.keys.forEach(k => Object.entries(MF[k] || {}).forEach(([pair, n]) => { g.fl[pair] = (g.fl[pair] || 0) + n; })); });
const fedSwing = f => { const cs = codes.filter(c => R[c].fedwin === f && R[c].tp != null); return {n: cs.length, v: d3.mean(cs, c => R[c].tp), names: cs.map(c => R[c].name)}; };
const FS = Object.fromEntries(['LPC', 'CPC', 'NDP', 'GPC'].map(f => [f, fedSwing(f)]));
const ridingsIn = (g, a, b) => codes.filter(c => g.keys.includes(R[c].fedwin) && R[c].win24 === a && R[c].lead === b).sort((x, z) => R[x].name.localeCompare(R[z].name));
const groupOf = c => AG.find(g => g.keys.includes(R[c].fedwin));
let midSel = 'mid', midBand = 'NDP>CON', midOpen = false;   // the band listed below the chart, as 'NDP>CON'; it opens on the story's band
// the slide's chart: the provincial vote in one group of ridings, each line the party it measures (story.json middle_pooled)
const MP = T.middle_pooled, MPK = {right: 'CPC', mid: 'LPC', left: 'NDP_GPC'};
const GNAME = {right: 'Conservative federally', mid: 'Liberal federally', left: 'NDP or Green federally'}, GSHORT = {right: 'Conservative', mid: 'Liberal', left: 'NDP or Green'};
const conGain = c => (R[c].s26.CON || 0) - (R[c].s24.CON || 0);
const grpIn = g => codes.filter(c => g.keys.includes(R[c].fedwin)).sort((a, b) => conGain(b) - conGain(a) || R[a].name.localeCompare(R[b].name));
let grpOpen = false;
function setMid(k) { midSel = k; midBand = null; midOpen = false; grpOpen = false; drawGrp(); drawMid(); }
const groupChips = sel => { $(sel).innerHTML = ['mid', 'right', 'left'].map(k => `<button data-gk="${k}" class="${k === midSel ? 'on' : ''}" aria-pressed="${k === midSel}">${GSHORT[k]}</button>`).join('');
  $$(sel + ' [data-gk]').forEach(b => b.onclick = () => { if (b.dataset.gk !== midSel) setMid(b.dataset.gk); }); };
const GP = [['NDP', 'NDP', 5], ['CON', 'Conservative', 5], ['GRN', 'Green', 2]];   // party, name, line width
function drawGrp() {
  groupChips('#grpbtn');
  const g = AG.find(x => x.k === midSel), m = MP[MPK[g.k]], mine = you && g.keys.includes(R[you].fedwin) ? R[you] : null;
  $('#grptitle').textContent = `Provincial vote in ridings that voted ${GSHORT[g.k]} federally`;
  $('#grpsub').innerHTML = `Share of all valid votes in the ${m.n} ridings where the ${g.k === 'right' ? 'Conservatives' : g.k === 'mid' ? 'Liberals' : 'NDP or the Greens'} came first in the April 28, 2025 federal election (federal results estimated on provincial ridings)${ref('ecan25')}`;
  const w0 = cw('#grpchart'), narrow = w0 < 460, H = 300, top = 40, bot = H - 22;
  const mineV = mine ? [['NDP', mine.s24.NDP, mine.s26.NDP], ['CON', mine.s24.CON, mine.s26.CON]].filter(([p, a, b2]) => a && b2) : [];
  const vals = GP.flatMap(([p]) => [m.y2024[p], m.y2026[p]]).concat(mineV.flatMap(([, a, b2]) => [a, b2]));
  const lo = Math.max(0, Math.floor((d3.min(vals) - 3) / 5) * 5), hi = Math.ceil((d3.max(vals) + 3) / 5) * 5;
  const {svg, w} = frame('#grpchart', H), y = d3.scaleLinear([lo, hi], [bot, top]);
  const xL = narrow ? 60 : 90, xR = narrow ? Math.max(xL + 100, w - 150) : Math.min(w - 170, xL + 340), fs = narrow ? 13 : 14;
  [xL, xR].forEach((x, i) => { svg.append('line').attr('x1', x).attr('x2', x).attr('y1', top - 10).attr('y2', bot + 6).attr('stroke', css('line')).attr('stroke-width', 1.5);
    txt(svg, x, 18, i ? 'Provincial 2026' : 'Provincial 2024', {anchor: 'middle', size: 12, weight: 800, fill: css('muted')}); });
  const L = [], Rt = [], LINES = [];
  GP.slice().reverse().forEach(([p, name, lw]) => { const a = m.y2024[p], b2 = m.y2026[p], col = pc(p);
    svg.append('line').attr('x1', xL).attr('x2', xR).attr('y1', y(a)).attr('y2', y(b2)).attr('stroke', col).attr('stroke-width', lw).attr('stroke-linecap', 'round');
    [[xL, a], [xR, b2]].forEach(([x, v]) => svg.append('circle').attr('cx', x).attr('cy', y(v)).attr('r', lw > 2 ? 6 : 3.5).attr('fill', col));
    L.push({y: y(a) + 4, t: `${f1(a)}%`, col, big: lw > 2}); Rt.push({y: y(b2) + 4, t: `${f1(b2)}%`, n: name, col, big: lw > 2});
    LINES.push({a, b: b2, tip: `<b>${name}</b>, ${GNAME[g.k]} (${m.n} ridings)<br>${f1(a)}% in 2024, ${f1(b2)}% in 2026 (${sgn(b2 - a)} points)`}); });
  spread(L, 16, top, bot + 4).forEach(l => halo(txt(svg, xL - 10, l.y, l.t, {anchor: 'end', size: l.big ? fs : 12, weight: 800, fill: l.col})));
  spread(Rt, 17, top, bot + 4).forEach(l => { const t = halo(svg.append('text').attr('x', xR + 10).attr('y', l.y).attr('font-size', l.big ? fs : 12).attr('fill', l.col));
    t.append('tspan').attr('font-weight', 800).text(l.t); t.append('tspan').attr('font-weight', 700).attr('dx', 6).text(l.n); });
  if (mineV.length) {   // your riding: its own NDP and Conservative shares as thin dashed lines
    mineV.forEach(([p, a, b2]) => { svg.append('line').attr('x1', xL).attr('x2', xR).attr('y1', y(a)).attr('y2', y(b2)).attr('stroke', pc(p)).attr('stroke-width', 2).attr('stroke-dasharray', '6 4');
      [[xL, a], [xR, b2]].forEach(([x, v]) => svg.append('circle').attr('cx', x).attr('cy', y(v)).attr('r', 3.5).attr('fill', css('card')).attr('stroke', pc(p)).attr('stroke-width', 2));
      LINES.push({a, b: b2, tip: `<b>${esc(mine.name)}</b>, ${PN[p]}<br>${f1(a)}% in 2024, ${f1(b2)}% in 2026 (${sgn(b2 - a)} points)`}); });
    const hiLine = mineV.reduce((q, r2) => (r2[1] + r2[2] > q[1] + q[2] ? r2 : q)), mx = (xL + xR) / 2, my = (y(hiLine[1]) + y(hiLine[2])) / 2;
    const t = halo(txt(svg, mx, my - 10, mine.name, {anchor: 'middle', size: 12, weight: 800}));
    const boxes = [...svg.node().querySelectorAll('text')].filter(n => n !== t.node()).map(n => n.getBBox());
    const clash = bb => boxes.some(o => bb.x < o.x + o.width && o.x < bb.x + bb.width && bb.y < o.y + o.height && o.y < bb.y + bb.height);
    let bb = t.node().getBBox();
    if (bb.x < 2) t.attr('x', mx + (2 - bb.x)); else if (bb.x + bb.width > w - 2) t.attr('x', mx - (bb.x + bb.width - w + 2));
    for (const dy of [0, -16, 28, -32, 44]) { t.attr('y', my - 10 + dy); bb = t.node().getBBox(); if (!clash(bb)) break; }
  }
  const at = (q, t) => y(q.a) + (y(q.b) - y(q.a)) * t;
  const pick = e => { const [mx, my] = d3.pointer(e), t = Math.max(0, Math.min(1, (mx - xL) / (xR - xL))), best = d3.least(LINES, q => Math.abs(my - at(q, t)));
    return best && Math.abs(my - at(best, t)) <= 22 ? best : null; };
  svg.on('click', e => { const q = pick(e); if (q) showTip(e, q.tip); else hideTip(); })
    .on('mousemove', e => { const q = pick(e); if (q) { showTip(e, q.tip); svg.style('cursor', 'pointer'); } else { hideTip(); svg.style('cursor', 'default'); } })
    .on('mouseleave', hideTip);
  const seat = (sx, yr) => `${and([[sx.CON, 'Conservative'], [sx.NDP, 'NDP'], [sx.GRN, 'Green']].filter(([n]) => n).map(([n, p]) => `${n} ${p}`))} ${sx.CON + sx.NDP + sx.GRN === 1 ? 'MLA' : 'MLAs'} in ${yr}`;
  $('#grpseats').innerHTML = `Provincially, these ${m.n} ridings elected ${seat(m.seats24, 2024)}, and ${seat(m.seats26, 2026)}.${ref('ebc24')}${ref('ebc26')}`
    + (mine ? `<br><span style="color:var(--text);font-weight:700">${mineV.length === 1 ? 'Dashed line' : 'Dashed lines'}: ${esc(mine.name)}, your riding.</span>` : you ? `<br>${esc(R[you].name)}, your riding, voted ${GSHORT[groupOf(you).k]} federally; pick that group to see its lines.` : '')
    + (g.k === 'right' ? ' Peace River North had no NDP candidate in 2026; its votes are counted.' : '');
  const all = grpIn(g), list = you && all.includes(you) ? [you, ...all.filter(c => c !== you)] : all, few = w0 >= 700 ? 12 : 6, cut = grpOpen || list.length <= few + 2 ? list.length : few;
  const chip = c => `<button class="rchip${c === you ? ' on' : ''}" data-sel="${c}"><span class="dot" style="background:${pc(R[c].lead)}"></span>${esc(R[c].name)}<small>Con. ${sgn(conGain(c))}</small></button>`;
  $('#grplist').innerHTML = `<p style="margin:10px 0 0"><b>The ${m.n} ridings</b>, by the change in the Conservative share of the provincial vote, 2024 to 2026 (points). The dot is the party elected in 2026; tap a riding to make it yours.</p>
    <div class="rlist">${list.slice(0, cut).map(chip).join('')}${cut < list.length ? `<button class="rmore" id="grpmore">${list.length - cut} more</button>` : ''}</div>`;
  if ($('#grpmore')) $('#grpmore').onclick = () => { grpOpen = true; drawGrp(); };
  $$('#grplist [data-sel]').forEach(x => x.onclick = () => setYou(x.dataset.sel));
}
function drawMid() {
  const w0 = cw('#midchart'), order = ['NDP', 'CON', 'GRN'], nodeW = 12, gapN = 4, k = w0 < 500 ? 3.4 : 4.4;
  const lx = Math.max(82, Math.min(170, w0 * .22)), rx = w0 - lx - nodeW, x0 = lx + nodeW, x1 = rx, xm = (x0 + x1) / 2;
  const side = (g, s) => Object.fromEntries(order.map(p => [p, d3.sum(Object.entries(g.fl).filter(([pr]) => pr.split('>')[s] === p), ([, n]) => n)]));
  const hh = t => d3.sum(order, p => t[p] ? t[p] * k + gapN : 0) - gapN;
  let y = 30;
  const blocks = AG.map(g => { const L = side(g, 0), Rr = side(g, 1), b = {g, L, Rr, y0: y, top: y + 48}; b.y1 = b.top + Math.max(hh(L), hh(Rr)) + 14; y = b.y1 + 8; return b; });
  const {svg, w} = frame('#midchart', y);
  const defs = svg.append('defs'), grad = (a, b) => { const id = `mg-${a}-${b}`; if (!defs.select('#' + id).size()) {
    const lg = defs.append('linearGradient').attr('id', id).attr('gradientUnits', 'userSpaceOnUse').attr('x1', x0).attr('x2', x1).attr('y1', 0).attr('y2', 0);
    lg.append('stop').attr('offset', '12%').attr('stop-color', pc(a)); lg.append('stop').attr('offset', '88%').attr('stop-color', pc(b)); } return `url(#${id})`; };
  txt(svg, lx + nodeW / 2, 16, 'Provincial 2024', {anchor: 'middle', size: 12, weight: 800, fill: css('muted')});
  txt(svg, rx + nodeW / 2, 16, 'Provincial 2026', {anchor: 'middle', size: 12, weight: 800, fill: css('muted')});
  blocks.forEach(b => {
    const g = b.g, on = g.k === midSel, gg = svg.append('g').style('cursor', 'pointer').on('click', () => { if (g.k !== midSel) setMid(g.k); });
    gg.append('rect').attr('x', 0).attr('y', b.y0 - 4).attr('width', w).attr('height', b.y1 - b.y0 + 4).attr('rx', 10).attr('fill', on ? css('soft') : 'transparent');
    if (on) gg.append('rect').attr('x', 0).attr('y', b.y0 - 4).attr('width', 4).attr('height', b.y1 - b.y0 + 4).attr('rx', 2).attr('fill', css('text'));
    txt(gg, 10, b.y0 + 16, `${g.label}: ${g.n} ridings`, {size: 13, weight: 800, fill: on ? css('text') : css('muted')});
    const swl = g.keys.length === 1 ? (w < 360 ? `Provincial swing ${sgn(FS[g.keys[0]].v)} points` : `Average provincial swing toward the Conservatives ${sgn(FS[g.keys[0]].v)} points`) : (w < 360 ? `Provincial swing ${sgn(FS.NDP.v)}, ${FS.NDP.n} NDP ridings` : `Average provincial swing ${sgn(FS.NDP.v)} points in the ${FS.NDP.n} ridings that voted NDP federally`);
    txt(gg, 10, b.y0 + 33, swl, {size: 12, fill: css('muted')});
    const ly = {}, ry = {}; let yl = b.top, yr = b.top;
    order.forEach(p => [[b.L, lx, ly, 0], [b.Rr, rx, ry, 1]].forEach(([t, nx, pos, s]) => { if (!t[p]) return; const y0 = s ? yr : yl, hgt = t[p] * k; pos[p] = y0;
      gg.append('rect').attr('x', nx).attr('y', y0).attr('width', nodeW).attr('height', Math.max(1.5, hgt)).attr('fill', pc(p));
      if (t[p] >= 3) txt(gg, s ? nx + nodeW + 6 : nx - 6, y0 + hgt / 2 + 4, `${SHORT[p]} ${t[p]}`, {anchor: s ? 'start' : 'end', size: 12, weight: 800, fill: pc(p)});
      if (s) yr += hgt + gapN; else yl += hgt + gapN; }));
    const lo = {...ly}, ro = {...ry}, labels = [];
    order.forEach(a => order.forEach(c2 => { const n = g.fl[`${a}>${c2}`] || 0; if (!n) return;
      const t = n * k, y0 = lo[a], y1 = ro[c2]; lo[a] += t; ro[c2] += t; const swd = a !== c2, list = ridingsIn(g, a, c2), key = `${a}>${c2}`, sel = on && midBand === key;
      gg.append('path').attr('d', `M${x0},${y0}C${xm},${y0} ${xm},${y1} ${x1},${y1}L${x1},${y1 + t}C${xm},${y1 + t} ${xm},${y0 + t} ${x0},${y0 + t}Z`)
        .attr('fill', swd ? grad(a, c2) : pc(a)).attr('fill-opacity', sel ? 1 : on ? (swd ? .9 : .4) : (swd ? .55 : .18))
        .attr('stroke', sel ? css('text') : 'transparent').attr('stroke-width', sel ? 1.5 : t < 10 ? 8 : 0)   // a wider hit area for thin bands
        .on('click', e => { e.stopPropagation(); const ch = g.k !== midSel; midSel = g.k; midBand = midBand === key && on ? null : key; midOpen = false; if (ch) { grpOpen = false; drawGrp(); } drawMid(); })
        .on('mousemove', e => showTip(e, `<b>${g.label}</b><br>${swd ? `Provincially ${PN[a]} in 2024, ${PN[c2]} in 2026` : `Provincially ${PN[a]} in 2024 and 2026`}: ${n} ${n === 1 ? 'riding' : 'ridings'}${list.length <= 8 ? '<br>' + list.map(c => R[c].name).join(', ') : ''}`)).on('mouseleave', hideTip);
      const mine = you && list.includes(you) ? (() => { const i = list.indexOf(you); return (y0 + y1) / 2 + (i + .5) * k; })() : null;
      if (swd && on) { let ly2 = (y0 + y1) / 2 + t / 2 + 4; if (mine != null && Math.abs(mine - (ly2 - 4)) < 11) ly2 = mine + 17;
        labels.push([xm, ly2, n >= 3 ? `${n} switched` : and(list.map(c => R[c].name))]); }
      if (mine != null) labels.push(['you', xm, mine, R[you].name, (y0 + y1) / 2]);
    }));
    labels.forEach(l => { if (l[0] === 'you') { gg.append('circle').attr('cx', l[1]).attr('cy', l[2]).attr('r', 6).attr('fill', css('you')).attr('stroke', css('card')).attr('stroke-width', 2).style('pointer-events', 'none');
        halo(txt(gg, l[1], Math.min(l[2] - 10, l[4] - 5), l[3], {anchor: 'middle', size: 12, weight: 800})).style('pointer-events', 'none'); }
      else halo(txt(gg, l[0], l[1], l[2], {anchor: 'middle', size: 12, weight: 800})).style('pointer-events', 'none'); });
  });
  groupChips('#midbtn');
  const G = AG.find(g => g.k === midSel), chip = c => `<button class="rchip${c === you ? ' on' : ''}" data-sel="${c}"><span class="dot" style="background:${pc(R[c].lead)}"></span>${esc(R[c].name)}</button>`;
  if (midBand && ridingsIn(G, ...midBand.split('>')).length) { const [a, c2] = midBand.split('>'), all = ridingsIn(G, a, c2);
    const list = you && all.includes(you) ? [you, ...all.filter(c => c !== you)] : all, few = w0 >= 700 ? 12 : 6, cut = midOpen || list.length <= few + 2 ? list.length : few;
    $('#midlist').innerHTML = `<p style="margin:10px 0 0"><b>${G.label}, ${a === c2 ? `${PN[a]} provincially in 2024 and 2026` : `${PN[a]} provincially in 2024, ${PN[c2]} in 2026`}:</b> ${plural(list.length, 'riding', 'ridings')}</p><div class="rlist">${list.slice(0, cut).map(chip).join('')}${cut < list.length ? `<button class="rmore" id="midmore">${list.length - cut} more</button>` : ''}</div>`;
    if ($('#midmore')) $('#midmore').onclick = () => { midOpen = true; drawMid(); }; }
  else $('#midlist').innerHTML = `<p style="margin:10px 0 0">${G.label}: ${plural(G.n, 'riding', 'ridings')}. Tap a band to list them.</p>`;
  $$('#midlist [data-sel]').forEach(a => a.onclick = () => setYou(a.dataset.sel));
}
draw(drawGrp); draw(drawMid); ON_YOU.push(() => { if (you) { midSel = groupOf(you).k; midBand = `${R[you].win24}>${R[you].lead}`; midOpen = false; grpOpen = false; } drawGrp(); drawMid(); if ($('#flowsvg').closest('details').open) drawFed(); });
YOU.middle = c => { const r = R[c], fp = r.fedwin, refs = `${ref('ecan25')}${ref('ebc24')}${ref('ebc26')}`;
  const fv = Object.entries(r.fed).sort((a, b) => b[1] - a[1]), even = fv[0][1] - fv[1][1] <= 0.5 + 1e-9;   // margins of 0.5 point or less: too close to call
  const fed = even ? `<b>${esc(r.name)}</b> was about even between the ${FNP[fv[0][0]]} and the ${FNP[fv[1][0]]} in the April 28, 2025 federal election (${f1(fv[0][1])}% and ${f1(fv[1][1])}%, estimated); it is grouped with the ridings that voted ${GSHORT[groupOf(c).k]} federally.`
    : `<b>${esc(r.name)}</b> gave the ${FNP[fp]} the most votes in the April 28, 2025 federal election (${f1(r.fed[fp])}%).`;
  const con = `the Conservative share there went from ${f1(r.s24.CON)}% in 2024 to ${f1(r.s26.CON)}% in 2026`;
  return r.s26.NDP ? `${fed} Provincially, ${con}, and the NDP's from ${f1(r.s24.NDP)}% to ${f1(r.s26.NDP)}%.${refs}` : `${fed} Provincially, ${con}; there was no NDP candidate in 2026.${refs}`; };
$('#say-middle').innerHTML = `In ridings that voted Liberal federally, the Conservative share of the provincial vote rose ${f1(MP.LPC.y2026.CON - MP.LPC.y2024.CON)} points and the NDP's fell ${f1(MP.LPC.y2024.NDP - MP.LPC.y2026.NDP)}. In ridings that voted Conservative federally, the Conservative share rose ${f1(MP.CPC.y2026.CON - MP.CPC.y2024.CON)} points and the NDP's fell ${f1(MP.CPC.y2024.NDP - MP.CPC.y2026.NDP)}.${ref('ecan25')}${ref('ebc24')}${ref('ebc26')}`;
const gpc = FS.GPC;
$('#more-middle').innerHTML = `<p><b>The vote chart.</b> Each line is one party's share of all valid votes cast in the provincial election in one group of ridings, 2024 and 2026: ${MP.LPC.n} ridings that voted Liberal federally, ${MP.CPC.n} that voted Conservative federally and ${MP.NDP_GPC.n} that voted NDP or Green federally. Votes are added up across each group's ridings. The dashed lines are your riding's own shares. Peace River North, which voted Conservative federally, had no NDP candidate in 2026; its votes are counted.${ref('ebc24')}${ref('ebc26')}</p>
<p>Each riding is grouped by the party with the most votes there in the April 28, 2025 federal election, with the federal results moved onto the provincial ridings poll by poll.${ref('ecan25')} In the ${MD.LPC.n} ridings that voted Liberal federally, ${MD.LPC.y2024.NDP} elected NDP MLAs in the 2024 provincial election and ${MD.LPC.y2026.CON} elected Conservatives in 2026. Of the ${T.n_switched} ridings that changed party, ${MD.LPC.switched} are in this group.${ref('ebc24')}${ref('ebc26')} Each band runs from the party elected provincially in 2024 (left) to the party elected provincially in 2026 (right); bands that change colour are ridings that changed party. Swing is the change, between the 2024 and 2026 provincial elections, in the Conservative share of the Conservative and NDP vote; ${gpc.n === 1 ? `the one riding that voted Green federally, ${gpc.names[0]}, swung ${sgn(gpc.v)} points, too few to compare, and ` : ''}Peace River North, with no NDP candidate in 2026, has no swing.</p>
<p><b>How each federal party's voters voted provincially, estimated.</b> Estimates from riding totals suggest the NDP's share of 2025 federal Liberal voters fell from about ${Math.round(T.flows.ndp24.LPC[0])}% in the 2024 provincial election to about ${Math.round(T.flows.ndp26.LPC[0])}% in 2026, while the Conservative share rose to about ${Math.round(T.flows.con26.LPC[0])}% (from ${Math.round(T.flows.con24.LPC[0])}%) and the Green share to about ${Math.round(T.flows.grn26.LPC[0])}% (from ${Math.round(T.flows.grn24.LPC[0])}%). These are estimates from an ecological regression, with 90% ranges from resampling the ridings; they describe broad patterns across ridings and cannot show how any one person voted. Federal and provincial turnout differ, so shares need not add to 100.${ref('goodman')}${ref('ecan25')}${ref('ebc26')}${ref('ebc24')}</p>`;
const FL = T.flows, cap = v => Math.max(0, Math.min(100, v));
const FROWS = [['LPC', 'Federal Liberal voters → provincial vote'], ['CPC', 'Federal Conservative voters → provincial vote'], ['NDP', 'Federal NDP voters → provincial vote']], FPARTY = [['ndp', 'NDP'], ['con', 'CON'], ['grn', 'GRN']];
function drawFlows() {
  const panelH = 26 + 3 * 24 + 8, {svg, w, h} = frame('#flowsvg', FROWS.length * panelH + 30), x = d3.scaleLinear([0, 100], [82, w - 84]);
  FROWS.forEach(([f, label], i) => {
    const y0 = 2 + i * panelH;
    txt(svg, 0, y0 + 15, label, {size: 13, weight: 800});
    FPARTY.forEach(([kk, p], j) => {
      const y = y0 + 36 + j * 24, a = FL[kk + '24'][f].map(cap), b = FL[kk + '26'][f].map(cap);
      txt(svg, 0, y + 4, SHORT[p], {size: 12, weight: 700, fill: pc(p)});
      svg.append('line').attr('x1', x(0)).attr('x2', x(100)).attr('y1', y).attr('y2', y).attr('stroke', css('line')).attr('stroke-width', 2);
      svg.append('line').attr('x1', x(b[1])).attr('x2', x(b[2])).attr('y1', y).attr('y2', y).attr('stroke', pc(p)).attr('stroke-width', 8).attr('stroke-opacity', .3).attr('stroke-linecap', 'round');
      svg.append('line').attr('x1', x(a[0])).attr('x2', x(b[0])).attr('y1', y).attr('y2', y).attr('stroke', css('muted')).attr('stroke-width', 1.5);
      svg.append('circle').attr('cx', x(a[0])).attr('cy', y).attr('r', 4.5).attr('fill', css('card')).attr('stroke', pc(p)).attr('stroke-width', 2);
      svg.append('circle').attr('cx', x(b[0])).attr('cy', y).attr('r', 5.5).attr('fill', pc(p));
      txt(svg, w - 78, y + 4, `${Math.round(a[0])}% → ${Math.round(b[0])}%`, {size: 12, weight: 700});
    });
  });
  axis(svg.append('g').attr('transform', `translate(0,${h - 24})`), d3.axisBottom(x).tickValues([0, 25, 50, 75, 100]).tickFormat(v => v + '%'));
  $('#flownote').innerHTML = `<div class="note">○ 2024 provincial election, ● 2026 provincial election, estimated; the shaded line is the 2026 estimate's 90% range.${ref('goodman')}</div>`;
}
function drawFed() {
  const {svg, w, h} = frame('#fedsc', 340), m = {l: 46, r: 14, t: 24, b: 40};
  const pts = codes.filter(c => c !== 'PCN').map(c => ({c, vx: R[c].fed.LPC, vy: R[c].ndp_swing}));
  const x = d3.scaleLinear().domain(d3.extent(pts, d => d.vx)).nice().range([m.l, w - m.r]), y = d3.scaleLinear().domain(d3.extent(pts, d => d.vy)).nice().range([h - m.b, m.t]);
  axis(svg.append('g').attr('transform', `translate(0,${h - m.b})`), d3.axisBottom(x).ticks(w < 500 ? 4 : 6));
  axis(svg.append('g').attr('transform', `translate(${m.l},0)`), d3.axisLeft(y).ticks(5));
  txt(svg, w - m.r, h - 6, 'Liberal share, April 28, 2025 federal election (%)', {anchor: 'end', size: 12, fill: css('muted')});
  txt(svg, 0, 12, 'Provincial NDP share, change 2024 to 2026 (points)', {size: 12, fill: css('muted')});
  pts.forEach(p => { p.x = x(p.vx); p.y = y(p.vy); });
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', d => d.x).attr('cy', d => d.y).attr('r', 5).attr('fill', d => fc(R[d.c].fedwin)).attr('fill-opacity', .8);
  const me = pts.find(p => p.c === you);
  if (me) { svg.append('circle').attr('cx', me.x).attr('cy', me.y).attr('r', 10).attr('fill', 'none').attr('stroke', css('you')).attr('stroke-width', 3);
    halo(txt(svg, me.x > w * .6 ? me.x - 13 : me.x + 13, me.y + 4, R[me.c].name, {anchor: me.x > w * .6 ? 'end' : 'start', size: 12, weight: 800})); }
  nearest(svg, pts, p => setYou(p.c), null, p => `<b>${esc(R[p.c].name)}</b><br>Liberal ${f1(p.vx)}%, NDP change ${sgn(p.vy)}`, 16);
  $('#fedlegend').innerHTML = `<div class="legend">${Object.keys(FN).map(k => `<span><i style="background:${fc(k)}"></i>${FN[k]} federally</span>`).join('')}</div><div class="note">Each dot is a riding. The provincial NDP fell most where the federal Liberals were strongest. Peace River North, with no NDP candidate in 2026, is left out.${ref('ecan25')}${ref('ebc26')}${ref('ebc24')}</div>`;
}
// charts inside a closed block are drawn when it opens, at its real width
$$('details.more').forEach(d => d.addEventListener('toggle', () => { if (d.open) { if (d.querySelector('#flowsvg')) { drawFlows(); drawFed(); } if (d.querySelector('#idxchart')) drawIdx(); } }));
DRAW.push(() => { if ($('#flowsvg').closest('details').open) { drawFlows(); drawFed(); } });

// ---------------------------------------------------------------- why: the worries, with the party rated best (the same calls as the slides)
const WY = T.why, iss = WY.issues, top = iss.slice().sort((a, b) => b.pct - a.pct);
const vals = d => Object.entries(d.best).sort((a, b) => b[1] - a[1]).map(([p, v]) => `${SHORT[p]} ${v}%`).join(', ');
const call = d => d.lead === 'even' ? 'About even' : `Rated best: ${PLURAL[d.lead]}`;
let openWorry = null;
function drawWorries() {
  $('#whychart').innerHTML = top.map((d, i) => { const even = d.lead === 'even', col = even ? '' : pc(d.lead), open = openWorry === i;
    return `<li><button data-w="${i}" aria-expanded="${open}"><span class="rank">${i + 1}</span><span><b>${d.issue}</b><div class="pct"><span>${d.pct}%</span>named it</div>
    <span class="chip"${col ? ` style="border-color:${col}"` : ''}><i style="background:${even ? `linear-gradient(90deg,${pc('CON')} 50%,${pc('NDP')} 50%)` : col}"></i>${call(d)}${even ? '' : ` (${vals(d)})`}</span>
    ${open ? `<div class="det">${WY.issues_source.pollster}, ${drange(WY.issues_source.field)}: ${d.pct}% of B.C. adults put ${d.issue.toLowerCase()} among their top three issues.${ref('ar')} ${WY.best_source.pollster}, ${drange(WY.best_source.field)}, a weighted sample of ${fmt(WY.best_source.n)}: party best on ${d.issue.toLowerCase()}, ${vals(d)}, a gap of ${d.gap} ${d.gap === 1 ? 'point' : 'points'}. ${even ? 'That is too small to call in a poll this size.' : 'The gap is larger than the margin of error a random sample of this size would have.'}${ref('irg')}</div>` : ''}</span></button></li>`; }).join('');
  $$('[data-w]').forEach(b => b.onclick = () => { const i = +b.dataset.w; openWorry = openWorry === i ? null : i; drawWorries(); });
}
drawWorries();
$('#tfc').innerHTML = `In ${WY.time_for_change.pollster}'s final campaign poll (${drange(WY.time_for_change.field)}), ${WY.time_for_change.pct}% said it was time for a change of government; ${WY.time_for_change.reelect}% said the NDP government deserved re-election.${ref('ipsos')}`;
const pp = new Set(['CON', 'NDP']);
let pollRange = 'all';
function drawPolls() {
  $('#pollbtn').innerHTML = ['CON', 'NDP', 'GRN'].map(p => `<button class="${pp.has(p) ? 'on' : ''}" data-p="${p}" aria-pressed="${pp.has(p)}"><span class="sw" style="background:${pc(p)}"></span>${PN[p]}</button>`).join('');
  $$('[data-p]').forEach(b => b.onclick = () => { pp.has(b.dataset.p) ? pp.delete(b.dataset.p) : pp.add(b.dataset.p); drawPolls(); });
  $('#pollrange').innerHTML = [['all', 'Since January 2025'], ['camp', 'The campaign']].map(([k, l]) => `<button data-pr="${k}" class="${k === pollRange ? 'on' : ''}" aria-pressed="${k === pollRange}">${l}</button>`).join('');
  $$('[data-pr]').forEach(b => b.onclick = () => { pollRange = b.dataset.pr; drawPolls(); });
  const camp = pollRange === 'camp', pd = d => new Date(d + 'T12:00:00'), x0 = camp ? '2026-09-15' : '2025-01-01', x1 = camp ? '2026-10-28' : '2026-11-01';
  const {svg, w, h} = frame('#polls', 300), m = {l: 40, r: 50, t: 22, b: 28};
  const x = d3.scaleTime([pd(x0), pd(x1)], [m.l, w - m.r]), polls = S.polls.filter(q => pd(q.end) >= pd(x0));
  const vs = [...pp].flatMap(p => polls.filter(q => q[p] != null).map(q => q[p]).concat([T.share[p]]));
  const y = d3.scaleLinear(vs.length ? [Math.max(0, Math.floor((d3.min(vs) - 4) / 10) * 10), Math.ceil((d3.max(vs) + 4) / 10) * 10] : [0, 60], [h - m.b, m.t]);
  const tv = (camp ? (w < 600 ? ['2026-09-22', '2026-10-24'] : w < 900 ? ['2026-09-22', '2026-10-08', '2026-10-24'] : ['2026-09-22', '2026-10-01', '2026-10-08', '2026-10-15', '2026-10-24'])
    : w < 600 ? ['2025-01-01', '2026-01-01', '2026-07-01'] : ['2025-01-01', '2025-04-01', '2025-07-01', '2025-10-01', '2026-01-01', '2026-04-01', '2026-07-01', '2026-10-01']).map(pd);
  const xa = axis(svg.append('g').attr('transform', `translate(0,${h - m.b})`), d3.axisBottom(x).tickValues(tv).tickFormat(d => camp ? `${MON[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}` : d.getMonth() === 0 ? `January ${d.getFullYear()}` : MON[d.getMonth()]));
  if (!camp) xa.select('.tick:first-of-type text').attr('text-anchor', 'start').attr('dx', '-4');   // month names in full; the first label starts at the axis
  axis(svg.append('g').attr('transform', `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickFormat(v => v + '%'));
  const xc = x(pd('2026-09-22'));
  svg.append('line').attr('x1', xc).attr('x2', xc).attr('y1', m.t).attr('y2', h - m.b).attr('stroke', css('muted')).attr('stroke-dasharray', '4 4');
  txt(svg, camp ? xc + 4 : xc - 4, 14, w < 420 ? 'Election called' : 'Election called, September 22, 2026', {anchor: camp ? 'start' : 'end', size: 12, fill: css('muted')});
  const all = [], about = q => `<b>${q.d.pollster}</b>, field work ending ${apd(q.d.end)}<br>${PN[q.p]} ${f1(q.d[q.p])}%${q.d.mode ? ` · ${q.d.mode}` : ''}${q.d.opened ? '' : '<br>(its own release could not be opened)'}`;
  pp.forEach(p => {
    const pts = polls.filter(q => q[p] != null);
    svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', d => x(pd(d.end))).attr('cy', d => y(d[p])).attr('r', camp ? 5 : 4).attr('fill', pc(p)).attr('fill-opacity', d => d.opened ? .85 : .3);
    pts.forEach(d => all.push({x: x(pd(d.end)), y: y(d[p]), d, p}));
    const cnt = T.share[p], xe = x(pd('2026-10-24'));
    svg.append('rect').attr('x', xe - 7).attr('y', y(cnt) - 2).attr('width', 14).attr('height', 4).attr('fill', pc(p));
    txt(svg, xe + 10, y(cnt) + 4, f1(cnt), {size: 12, weight: 700, fill: pc(p)});
  });
  nearest(svg, all, (q, e) => showTip(e, about(q)), null, about, 14);
}
draw(drawPolls);
const FP = S.final_polls, avg = d3.mean(FP, d => d.CON), avgN = d3.mean(FP, d => d.NDP);
YOU.why = c => { const r = R[c], con = share(r, 'CON'), ndp = share(r, 'NDP');
  const first = r.lead === 'GRN' ? `gave the Greens ${f1(share(r, 'GRN'))}%, the Conservatives ${f1(con)}% and the NDP ${f1(ndp)}% in 2026; across B.C. it was ${f1(T.share.GRN)}%, ${f1(T.share.CON)}% and ${f1(T.share.NDP)}%`
    : ndp ? `gave the Conservatives ${f1(con)}% and the NDP ${f1(ndp)}% in 2026; across B.C. it was ${f1(T.share.CON)}% and ${f1(T.share.NDP)}%`
    : `gave the Conservatives ${f1(con)}% in 2026, with no NDP candidate on the ballot; across B.C. the Conservatives had ${f1(T.share.CON)}%`;
  return `<b>${esc(r.name)}</b> ${first}. Polls ask British Columbians as a whole, so no poll speaks for one riding.${ref('ebc26')}`; };
$('#say-why').innerHTML = `Cost of living topped the list, and more people rated the Conservatives best on it. On health care and housing the two parties were about even. The final polls put the Conservatives first, with a smaller share than they received.${ref('ar')}${ref('irg')}${ref('polls')}`;
$('#more-why').innerHTML = `<p>${top[0].issue} was the top worry of British Columbians in the ${WY.issues_source.pollster}'s final campaign poll of B.C. adults, ahead of ${and(top.slice(1).map(d => d.issue.toLowerCase()))}; people could pick up to three.${ref('ar')} "About even" means the gap is smaller than the margin of error a probability sample of this size would have on the gap (about ${d3.max(iss, d => d.moe)} points, 19 times out of 20). The pollster notes that a margin of error cannot be calculated for its online panel.${ref('irg')}</p>
<p>The last campaign poll from each of ${FP.length} pollsters averaged ${f1(avg)}% for the Conservatives and ${f1(avgN)}% for the NDP. The results ${ASOF} have ${f1(T.share.CON)}% and ${f1(T.share.NDP)}%${avg < T.share.CON && avg - avgN < T.share.CON - T.share.NDP ? ', so the polls put the Conservatives first but understated both their share and their margin over the NDP' : ''}.${ref('polls')}${ref('ebc26')} In the chart each dot is a poll; faded dots are polls whose own release could not be opened. The marks at the right edge are the results ${ASOF}; the dashed line marks September 22, 2026, when the election was called.${ref('ebcdates')}</p>`;
$('#polltbl').innerHTML = `<table><tr><th>Final poll, field work ended</th><th class="n">Conservative</th><th class="n">NDP</th><th class="n">Green</th></tr>${FP.slice().sort((a, b) => b.CON - a.CON).map(d =>
  `<tr><td>${d.url ? `<a href="${d.url}" rel="noopener">${d.full_name}</a>` : d.full_name}<div class="note">${apd(d.field_end)}</div></td><td class="n">${f1(d.CON)}%</td><td class="n">${f1(d.NDP)}%</td><td class="n">${d.GRN == null ? '' : f1(d.GRN) + '%'}</td></tr>`).join('')}
  <tr><td><b>Results</b>${ref('ebc26')}<div class="note">${ASOF.replace('as of ', 'As of ')}</div></td><td class="n"><b>${f1(T.share.CON)}%</b></td><td class="n"><b>${f1(T.share.NDP)}%</b></td><td class="n"><b>${f1(T.share.GRN)}%</b></td></tr></table>`;

// ---------------------------------------------------------------- the majority: seats, and a swingometer
// model: a uniform shift of s points of each riding's Conservative and NDP vote from the Conservatives to the NDP (s < 0: the other way);
// other candidates keep their votes; Peace River North, with no NDP candidate, keeps its leader
const VT = Object.fromEntries(codes.map(c => { const v = p => d3.sum(R[c].c26.filter(x => x[1] === p), x => x[2]);
  const others = R[c].c26.filter(x => x[1] !== 'CON' && x[1] !== 'NDP'); const ob = d3.greatest(others, x => x[2]);
  return [c, {CON: v('CON'), NDP: v('NDP'), ob: ob ? ob[2] : 0, op: ob ? ob[1] : null}]; }));
function leaderAt(c, s) {
  const v = VT[c]; if (!v.NDP || !v.CON) return R[c].lead;
  const t2 = v.CON + v.NDP, con = v.CON - s * t2 / 100, ndp = v.NDP + s * t2 / 100;
  if (v.ob > con && v.ob > ndp) return v.op;
  return con >= ndp ? 'CON' : 'NDP';
}
const seatsAt = s => { const n = {CON: 0, NDP: 0, GRN: 0, OTH: 0}; codes.forEach(c => { const p = leaderAt(c, s); n[p in n ? p : 'OTH']++; }); return n; };
// where the Conservative majority ends, and where an NDP majority begins
const scan = d3.range(0, 1001).map(i => i / 50);
const conEnds = scan.find(s => seatsAt(s).CON < MAJ), ndpStarts = scan.find(s => seatsAt(s).NDP >= MAJ);
function flipAt(c) {   // smallest shift, either way, at which the riding changes hands
  const L = R[c].lead; const up = scan.find(s => leaderAt(c, s) !== L), dn = scan.find(s => leaderAt(c, -s) !== L);
  return {up, dn};
}
let swingS = 0, SEATS = [];
// both seat charts share one layout: seats fill from the left (NDP) to the right (Conservative), and within a party the closest races sit nearest the middle
function seatLayout(Rm) {
  const nR = Rm < 95 ? 4 : Rm < 160 ? 5 : 7, r0 = Rm * .5, radii = d3.range(nR).map(i => r0 + i * (Rm - r0) / (nR - 1));
  const per = radii.map(r => Math.round(N * r / d3.sum(radii)));
  for (let i = nR - 1; d3.sum(per) !== N; i = (i - 1 + nR) % nR) per[i] += Math.sign(N - d3.sum(per));
  const posn = []; radii.forEach((r, i) => d3.range(per[i]).forEach(j => posn.push({r, a: Math.PI * (1 - j / (per[i] - 1)), row: i})));
  posn.sort((p, q) => q.a - p.a || p.row - q.row);
  return {posn, r0, dotR: Math.min((Rm - r0) / (nR - 1) * .44, Math.PI * r0 / (per[0] - 1) * .44)};
}
const mg24 = c => { const x = R[c].c24; return x && x.length > 1 ? x[0][2] - x[1][2] : 1e9; };   // 2024 margin in votes
const mgAt = (c, s) => { const v = VT[c]; if (!v.NDP || !v.CON) return R[c].margin; const t2 = v.CON + v.NDP; return Math.abs((v.CON - s * t2 / 100) - (v.NDP + s * t2 / 100)); };
const SH24 = T.rise.years.find(y => y.year === 2024);
function shareAt(s) {
  if (s === 0) return {CON: T.share.CON, NDP: T.share.NDP, GRN: T.share.GRN};
  const t = {CON: 0, NDP: 0, GRN: 0}, all = d3.sum(codes, c => d3.sum(R[c].c26, x => x[2]));
  codes.forEach(c => { const v = VT[c], t2 = v.CON + v.NDP, d = v.NDP && v.CON ? s * t2 / 100 : 0; t.CON += v.CON - d; t.NDP += v.NDP + d; t.GRN += d3.sum(R[c].c26.filter(x => x[1] === 'GRN'), x => x[2]); });
  return {CON: 100 * t.CON / all, NDP: 100 * t.NDP / all, GRN: 100 * t.GRN / all};
}
function drawVS() {
  const s = swingS, n26 = seatsAt(s), sh26 = shareAt(s);
  const w0 = cw('#vschart'), Rm = Math.max(56, Math.min(w0 / 4 - 8, 210)), cy = 14 + Rm, big = Rm >= 120;
  const {svg, w} = frame('#vschart', cy + (big ? 82 : 66)), L = seatLayout(Rm), ord = ['NDP', 'GRN', 'OTHX', 'CON'];
  const panels = [
    {yr: 2024, label: '2024', cx: w / 4, owner: c => R[c].win24, mg: mg24, seats: T.seats24, sh: {CON: SH24.CON, NDP: SH24.NDP}},
    {yr: 2026, label: '2026', cx: 3 * w / 4, owner: c => leaderAt(c, s), mg: c => mgAt(c, s), seats: n26, sh: sh26}];
  SEATS = [];
  panels.forEach(P => {
    const grp = c => { const p = P.owner(c); return ord.includes(p) ? p : 'OTHX'; };
    const list = ord.flatMap(p => codes.filter(c => grp(c) === p).sort((a, b) => p === 'CON' ? P.mg(a) - P.mg(b) : P.mg(b) - P.mg(a)));
    const pts = L.posn.map((q, i) => ({c: list[i], yr: P.yr, x: P.cx + q.r * Math.cos(q.a), y: cy - q.r * Math.sin(q.a)}));
    const g = svg.append('g');
    g.selectAll('circle').data(pts).join('circle').attr('cx', d => d.x).attr('cy', d => d.y).attr('r', L.dotR).attr('fill', d => pc(P.owner(d.c)))
      .attr('stroke', d => P.yr === 2026 && P.owner(d.c) !== R[d.c].win24 ? css('text') : 'none').attr('stroke-width', Math.max(1.2, L.dotR * .3));
    const me = pts.find(d => d.c === you);
    if (me) g.append('circle').attr('cx', me.x).attr('cy', me.y).attr('r', L.dotR + 4).attr('fill', 'none').attr('stroke', css('you')).attr('stroke-width', 2.5);
    g.append('line').attr('x1', P.cx).attr('x2', P.cx).attr('y1', cy - Rm - L.dotR - 7).attr('y2', cy - L.r0 + L.dotR + 2)
      .attr('stroke', css('text')).attr('stroke-width', 1.5).attr('stroke-dasharray', '4 3');
    txt(g, P.cx, cy - (big ? 6 : 3), P.label, {anchor: 'middle', size: big ? 34 : 19, weight: 800});   // the year inside the arc, as on the slide
    const st = g.append('text').attr('x', P.cx).attr('y', cy + (big ? 24 : 18)).attr('text-anchor', 'middle').attr('font-size', big ? 16 : 12).attr('font-weight', 800);
    st.append('tspan').attr('fill', pc('NDP')).text(`NDP ${P.seats.NDP}`); st.append('tspan').attr('fill', css('muted')).text(' · '); st.append('tspan').attr('fill', pc('CON')).text(`Con. ${P.seats.CON}`);
    st.append('tspan').attr('fill', css('muted')).attr('font-weight', 700).text(' seats');
    const t = g.append('text').attr('x', P.cx).attr('y', cy + (big ? 48 : 37)).attr('text-anchor', 'middle').attr('font-size', big ? 15 : 12).attr('font-weight', 800);
    t.append('tspan').attr('fill', pc('NDP')).text(`NDP ${f1(P.sh.NDP)}%`); t.append('tspan').attr('fill', css('muted')).text(' · '); t.append('tspan').attr('fill', pc('CON')).text(`Con. ${f1(P.sh.CON)}%`);
    txt(g, P.cx, cy + (big ? 68 : 54), P.yr === 2026 && s !== 0 ? 'of the vote, with the slider' : 'of the vote', {anchor: 'middle', size: big ? 12 : 11, fill: css('muted')});
    pts.forEach(d => SEATS.push(d));
  });
  nearest(svg, SEATS, d => setYou(d.c), null, d => { const r = R[d.c];
    if (d.yr === 2024) return `<b>${esc(r.name)}</b><br>2024: ${PN[r.win24]}, by ${fmt(mg24(d.c))} votes`;
    return `<b>${esc(r.name)}</b><br>` + (s === 0 ? `2026: ${leadTxt(d.c)}${r.flip ? `<br>Changed party (${PN[r.win24]} in 2024)` : ''}` : `${PN[leaderAt(d.c, s)]} at this setting (${PN[r.lead]} elected)`); }, Math.max(12, L.dotR * 2.4));
  const st = n26.CON >= MAJ ? `Conservative majority: ${n26.CON} seats` : n26.NDP >= MAJ ? `NDP majority: ${n26.NDP} seats` : `No party has a majority: Conservative ${n26.CON}, NDP ${n26.NDP}`;
  $('#swingout').innerHTML = (s === 0 ? `Results ${ASOF}. ` : `${f1(Math.abs(s))} points toward the ${s > 0 ? 'NDP' : 'Conservatives'}. `) + st + '.';
  $('#readout').innerHTML = ['CON', 'NDP', 'GRN'].map(p => `<div style="border-top-color:${pc(p)}"><b>${n26[p]}</b><span>${PN[p]}${s ? ` (${sgn(n26[p] - lead(p)).replace('.0', '')})` : ''}</span></div>`).join('');
  $('#vsnote').innerHTML = `Each dot is a riding, coloured by the party elected. In 2026, ringed dots ${s === 0 ? 'changed party since 2024' : 'differ from 2024 at this setting'}. Majority: ${MAJ} seats${s === 0 && n26.CON >= MAJ ? `, with ${n26.CON - MAJ} to spare` : ''}; the dotted line marks it. The final count, planned for ${FINAL}, can change the closest ridings.${ref('ebc24')}${ref('ebc26')}${ref('ebcdates')}`;
  drawScale();
  if ($('#you-majority') && you) $('#you-majority').innerHTML = `<div>${YOU.majority(you)}</div>`;
}
function drawScale() {
  const {svg, w} = frame('#swingscale', 66), x = d3.scaleLinear([-10, 10], [12, w - 12]);
  svg.append('line').attr('x1', x(-10)).attr('x2', x(10)).attr('y1', 8).attr('y2', 8).attr('stroke', css('line')).attr('stroke-width', 2);
  [-10, -5, 0, 5, 10].forEach(v => { svg.append('line').attr('x1', x(v)).attr('x2', x(v)).attr('y1', 4).attr('y2', 12).attr('stroke', css('muted'));
    txt(svg, x(v), 26, v === 0 ? 'Results' : String(Math.abs(v)), {anchor: v === -10 ? 'start' : v === 10 ? 'end' : 'middle', size: 11, fill: css('muted')}); });
  const mark = (v, label, row) => { if (v == null || v > 10) return; const an = x(v) > w * .62 ? 'end' : 'start';
    svg.append('line').attr('x1', x(v)).attr('x2', x(v)).attr('y1', 0).attr('y2', row - 10).attr('stroke', css('NDP')).attr('stroke-width', 2.5);
    txt(svg, x(v) + (an === 'end' ? 3 : -3), row, label, {anchor: an, size: 12, weight: 800, fill: css('NDP')}); };
  mark(conEnds, `Conservative majority ends at ${f1(conEnds)}`, 44);
  if (ndpStarts != null) mark(ndpStarts, `NDP majority from ${f1(ndpStarts)}`, 62);
  svg.append('circle').attr('cx', x(swingS)).attr('cy', 8).attr('r', 6).attr('fill', css('text')).attr('stroke', css('card')).attr('stroke-width', 2);
}
$('#swing').addEventListener('input', e => { swingS = +e.target.value; drawVS(); });
$('#swingreset').onclick = () => { swingS = 0; $('#swing').value = 0; drawVS(); };
draw(drawVS); ON_YOU.push(drawVS);
YOU.majority = c => { const r = R[c], f = flipAt(c), at = swingS === 0 ? '' : ` At this setting it is ${PN[leaderAt(c, swingS)]}.`;
  if (r.tp == null) return `<b>${esc(r.name)}</b> had no NDP candidate in 2026, so the slider leaves it ${PN[r.lead]}.`;
  const toN = f.up, toC = f.dn, other = r.lead === 'CON' ? 'NDP' : 'Conservatives';
  const need = r.lead === 'CON' ? toN : r.lead === 'NDP' ? toC : Math.min(toN ?? 99, toC ?? 99);
  return need != null && need <= 20 ? `<b>${esc(r.name)}</b> changes hands at a shift of ${f1(need)} points toward the ${r.lead === 'GRN' ? (toN != null && toN <= (toC ?? 99) ? 'NDP' : 'Conservatives') : other}.${at}${ref('ebc26')}`
    : `<b>${esc(r.name)}</b> stays ${PN[r.lead]} even with a shift of 20 points.${at}${ref('ebc26')}`; };
const VS = T.votes_seats, TP = T.tipping, WT = T.votes_where_trailing;
const gap24 = SH24.NDP - SH24.CON, gap26 = T.share.CON - T.share.NDP, net = T.seats.CON - T.seats24.CON;
$('#say-majority').innerHTML = `The Conservative share rose ${f1(T.share.CON - SH24.CON)} points and the NDP's fell ${f1(SH24.NDP - T.share.NDP)}. Each riding elects the candidate who finishes first, so ${net} seats moved, net, from the NDP to the Conservatives.${ref('ebc24')}${ref('ebc26')}`;
$('#more-majority').innerHTML = `<p><b>Votes and seats.</b> In 2024, ${f1(SH24.NDP)}% of the vote gave the NDP ${T.seats24.NDP} seats, the smallest possible majority, and ${f1(SH24.CON)}% gave the Conservatives ${T.seats24.CON}: a ${f1(gap24)}-point NDP margin. In 2026, ${f1(VS.CON.votes)}% gives the Conservatives ${T.seats.CON} of ${N} seats (${f1(VS.CON.seats)}%) and ${f1(VS.NDP.votes)}% gives the NDP ${T.seats.NDP}: a ${f1(gap26)}-point Conservative margin.${ref('ebc24')}${ref('ebc26')}</p>
<p><b>The slider.</b> It moves the same share of each riding's Conservative and NDP vote from one party to the other, starting from the results ${ASOF}, and leaves other candidates' votes as they are. Real elections never swing evenly, so read it as a measure of how far the vote is from changing the result. One point on the slider is one point of swing, the same measure as the swing on the map. The Conservative majority ends at a shift of about ${f1(conEnds)} points toward the NDP${ndpStarts != null ? `, and an NDP majority begins at about ${f1(ndpStarts)}` : ''}. Peace River North, with no NDP candidate in 2026, stays ${PN[R.PCN ? R.PCN.lead : 'CON']}.${ref('ebc26')}</p>
<p><b>How safe is the majority?</b> The Conservatives could see their ${TP.seats_to_lose - 1} closest ridings change hands and still hold ${MAJ} seats. Ending the majority would take ${fmt(TP.voters)} voters switching to the second-place candidate across their ${TP.seats_to_lose} closest ridings, from the closest up to ${TP.tipping_riding}, the ${MAJ}th seat. That is ${TP.pct_of_votes}% of the votes counted.${ref('ebc26')}</p>
<p>Most NDP votes went to candidates who finished second or lower: ${f1(WT.NDP)}%, against ${f1(WT.CON)}% of Conservative votes. For the Greens it is ${f1(WT.GRN)}%.${ref('ebc26')}</p>
<p><b>Over time.</b> Pick a measure to compare 2026 with every B.C. election since 1928.</p>`;
const IX = [['lsq', 'Disproportionality (Gallagher index)', "How far seat shares sit from vote shares: the square root of half the sum of squared gaps between each party's vote and seat percentages. 0 means seats match votes exactly.", 'gallagher'],
  ['env', 'Effective number of parties, votes', 'One divided by the sum of squared vote shares: the number of equal-sized parties that would give the same spread of votes.', 'laakso'],
  ['ens', 'Effective number of parties, seats', 'The same measure for seats.', 'laakso'],
  ['volatility', 'Volatility (Pedersen index)', "Half the sum of every party's change in vote share since the election before: the share of the vote that moved between parties.", 'pedersen']];
$('#idxsel').innerHTML = IX.map(([k, l]) => `<option value="${k}">${l}</option>`).join('');
function drawIdx() {
  const k = $('#idxsel').value, it = IX.find(i => i[0] === k), D = T.indices.filter(d => d[k] != null);
  const {svg, w, h} = frame('#idxchart', 240), m = {l: 40, r: 14, t: 16, b: 28};
  const x = d3.scaleLinear([1928, 2026], [m.l, w - m.r]), y = d3.scaleLinear([0, d3.max(D, d => d[k]) * 1.1], [h - m.b, m.t]);
  axis(svg.append('g').attr('transform', `translate(0,${h - m.b})`), d3.axisBottom(x).tickFormat(d3.format('d')).ticks(w < 500 ? 5 : 10));
  axis(svg.append('g').attr('transform', `translate(${m.l},0)`), d3.axisLeft(y).ticks(5));
  svg.append('path').datum(D).attr('fill', 'none').attr('stroke', css('text')).attr('stroke-width', 2).attr('d', d3.line(d => x(d.year), d => y(d[k])));
  const pts = D.map(d => ({d, x: x(d.year), y: y(d[k])}));
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', p => p.x).attr('cy', p => p.y).attr('r', p => p.d.year === 2026 ? 6 : 4).attr('fill', p => p.d.year === 2026 ? css('CON') : css('text'));
  nearest(svg, pts, () => {}, null, p => `<b>${p.d.year}${p.d.year === 2026 ? ' (' + ASOF + ')' : ''}</b><br>${it[1]}: ${f1(p.d[k])}`, 14);
  const last = D[D.length - 1], prev = D[D.length - 2];
  $('#idxdef').innerHTML = `${it[2]} ${last.year} (${ASOF}): ${f1(last[k])}; ${prev.year}: ${f1(prev[k])}.${ref(it[3])}${ref('ebchist')}${ref('ebc26')}`;
}
$('#idxsel').onchange = drawIdx; DRAW.push(() => { if ($('#idxchart').closest('details').open) drawIdx(); });

// ---------------------------------------------------------------- what comes next: promises and the final count
const PLAT = T.platform;
let pf = 'all', openP = null;
const PROM = T.promises.flatMap(w => w.items.map((p, i) => ({...p, worry: w.worry, id: w.worry + i}))).filter(p => !/^No target/.test(p.short));
const issuePct = w => { const d = iss.find(x => x.issue.toLowerCase() === w.toLowerCase()); return d ? d.pct : null; };
const pageTxt = p => /^\d/.test(p.page) ? `Platform ${/,| to /.test(p.page) ? 'pages' : 'page'} ${p.page}` : "The party's plan page";
function drawPromises() {
  $('#pfilter').innerHTML = [['all', 'All'], ...T.promises.map(w => [w.worry, `${w.worry} · ${issuePct(w.worry)}%`])].map(([k, l]) => `<button data-pf="${k}" class="${k === pf ? 'on' : ''}" aria-pressed="${k === pf}">${l}</button>`).join('');
  $$('[data-pf]').forEach(b => b.onclick = () => { pf = b.dataset.pf; drawPromises(); });
  $('#pgrid').innerHTML = PROM.filter(p => pf === 'all' || p.worry === pf).map(p => { const open = openP === p.id;
    return `<button class="promise" data-pid="${esc(p.id)}" aria-expanded="${open}"><span class="wt">${p.worry}</span><b>${esc(p.short.replace(/\s*\(party plan page\)$/, ''))}</b><span class="pg">${pageTxt(p)}</span>
      ${open ? `<span class="det">${esc(p.detail)} <a href="${p.url}" rel="noopener" onclick="event.stopPropagation()">Open the source</a></span>` : ''}</button>`; }).join('');
  $$('[data-pid]').forEach(b => b.onclick = () => { openP = openP === b.dataset.pid ? null : b.dataset.pid; drawPromises(); });
}
drawPromises();
let watchN = 400;
function drawWatch() {
  const list = codes.filter(c => R[c].margin <= watchN).sort((a, b) => R[a].margin - R[b].margin);
  $('#watchlab').textContent = `Show margins of ${fmt(watchN)} votes or fewer: ${list.length} ${list.length === 1 ? 'riding' : 'ridings'}`;
  $('#watch').innerHTML = list.map(c => { const r = R[c];
    return `<button class="wrow${c === you ? ' me' : ''}" data-sel="${c}"><span><span class="dot" style="background:${pc(r.lead)}"></span><b>${esc(r.name)}</b>${r.flip ? '<span class="new">new</span>' : ''}</span><small>${PN[r.lead]} by ${fmt(r.margin)}</small><span class="tr"><i style="width:${100 * r.margin / watchN}%;background:${pc(r.lead)}"></i></span></button>`; }).join('') || '<div class="note">No riding is that close.</div>';
  if (you && R[you].margin > watchN) { const r = R[you], k = codes.filter(x => R[x].margin < r.margin).length;
    $('#watch').innerHTML += `<div class="pin">Your riding</div><div class="wrow me"><span><span class="dot" style="background:${pc(r.lead)}"></span><b>${esc(r.name)}</b>${r.flip ? '<span class="new">new</span>' : ''}</span><small>${PN[r.lead]} by ${fmt(r.margin)}</small><span class="note" style="grid-column:1/-1;font-size:13px">${k} ${k === 1 ? 'riding is' : 'ridings are'} closer.</span></div>`; }
  $$('#watch [data-sel]').forEach(b => b.onclick = () => setYou(b.dataset.sel));
}
$('#watchn').addEventListener('input', e => { watchN = +e.target.value; drawWatch(); });
drawWatch(); ON_YOU.push(drawWatch);
const LT = S.late2024;
$('#watchnote').innerHTML = `The final count, planned for ${FINAL}, adds vote-by-mail, assisted telephone voting, out-of-district and other ballots. In the 2024 B.C. election those ballots leaned NDP, so the closest Conservative margins are the most likely to change.${ref('ebcdates')}${ref('ebc24')}`;
YOU.promises = c => { const r = R[c], k = codes.filter(x => x !== c && R[x].margin < r.margin).length;
  return `<b>${esc(r.name)}</b> elected ${aParty(r.lead)} MLA by ${fmt(r.margin)} votes. ${k === 0 ? 'No riding is closer.' : `${k} of the other ${N - 1} ridings ${k === 1 ? 'is' : 'are'} closer.`}${ref('ebc26')}`; };
$('#say-promises').innerHTML = `Each card is a promise from the Conservative platform on one of the three top worries before the vote.${ref('platform')}${ref('ar')} Return Day, when the results become official, is ${NX.return_day}.${ref('ebcdates')}`;
$('#more-promises').innerHTML = `<p>${and(T.promises.map(w => w.worry.toLowerCase())).replace(/^./, s => s.toUpperCase())} were British Columbians' top three worries.${ref('ar')} The cards quote or summarize the Conservative platform, with its page.${ref('platform')} On housing, the platform sets no number of homes and no target for rents or prices; its timeline is for approvals.${ref('platform')} The platform, "${PLAT.title}", is the version posted on the party's website on October 19, 2026. It adds $${PLAT.new_spending_full_year_billion} billion a year in new spending at full cost and $${PLAT.tax_relief_four_years_billion} billion in tax relief over four years, and projects a deficit of $${PLAT.deficit_2029_30_billion} billion in 2029/30.${ref('platform')}</p>
<ul><li>Final count: ${NX.final_count}.${ref('ebcdates')}${ref('ebcnight')}</li>
<li>In the 2024 B.C. election, the kinds of ballots left to the 2026 final count (vote-by-mail, assisted telephone and absentee ballots on Final Voting Day) gave the Conservatives ${f1(LT.con_two_party_late)}% of the Conservative and NDP vote, against ${f1(LT.con_two_party_rest)}% in all other ballots.${ref('ebc24')}</li>
<li>Return Day, when the results become official: ${NX.return_day}.${ref('ebcdates')}</li>
<li>Swearing-in of the premier and cabinet: ${NX.swearing_in} as of October 25, 2026.</li>
<li>Lorne Doerkson, the Conservatives' interim leader, is expected to become premier. The party's board says he will remain leader and that it will seek to amend the party's rules.${ref('cpcboard')}${ref('cpcconst')}</li></ul>
<p class="note">Results ${ASOF}, as posted by Elections BC: ${fmt(T.meta.boxes)} of ${fmt(T.meta.boxes_total)} ballot boxes counted. ${word(T.n_within_150)} ridings have margins of 150 votes or fewer.${ref('ebc26')}</p>`;

// ---------------------------------------------------------------- methods and references
const H28y = H28.year;
$('#methodtext').innerHTML = `<p><b>Results.</b> 2026 numbers are Elections BC's results ${ASOF}, read from its official results files for all ${N} electoral districts (ridings).${ref('ebc26')} 2024 numbers are the certified final results.${ref('ebc24')} "Changed party" compares the party elected in each riding in 2026 with the party elected there in 2024. The final count adds vote-by-mail, assisted telephone voting, out-of-district and other ballots.${ref('ebcnight')}</p>
<p><b>Find your riding.</b> Places are the municipalities and designated places of the 2021 Census; each lists the ridings its people live in, from census block populations allocated to the 2023 ridings.${ref('statcan')}${ref('bcdc')} Your choice stays in this browser only.</p>
<p><b>2020 on the 2026 ridings.</b> Elections BC's 2020 results by voting area were moved onto the 2023 boundaries, which both the 2024 and 2026 elections use, weighted by 2024 registered voters.${ref('ebc20')}</p>
<p><b>Swing.</b> The Conservative share of the Conservative and NDP vote in 2026 minus the same share in 2024. It reduces the effect of 2024 independents and of Green candidates entering or leaving a riding. Peace River North had no NDP candidate in 2026 and is left out of swing measures.</p>
<p><b>Census and place types.</b> 2021 Census profiles for the ${N} ridings published by BC Stats on the 2023 boundaries.${ref('bcstats')}${ref('statcan')} Place types follow the commuting method of the Canadian Suburbs project, applied in this order: exurban and rural ridings have under 150 people per km²; of the rest, active cores have walking and cycling to work at least 1.5 times the provincial rate, transit suburbs have above-average transit use, and the rest are car suburbs. The project applies the method to census tracts within metropolitan areas and tests walking and cycling first; here it is applied to whole ridings with provincial averages, density first, a simplification.${ref('suburbs')} The profile cards count every household, commuter or resident in each group's ridings together, each over its own census universe, and round the shares to whole percentages. Links between census measures and votes are correlations across ridings. They describe places as a whole and do not show how any one person voted.</p>
<p><b>Federal vote.</b> Elections Canada's results for the April 28, 2025 federal election, poll by poll, allocated to provincial ridings by the share of each polling division's 2021 population inside each riding (dissemination blocks). Advance and special ballots, which have no polling division, are spread within each federal riding by its election-day pattern. Totals match Elections Canada's B.C. totals.${ref('ecan25')}${ref('bcdc')} The estimates of how each federal party's voters voted provincially regress each provincial party's riding shares on the federal shares (non-negative least squares) and resample the ridings 400 times; the ranges run from the 5th to the 95th percentile.${ref('goodman')}</p>
<p><b>History and measures.</b> Province-wide shares and seats from Elections BC's Electoral History of British Columbia and Statements of Votes, 1928 to 2024. The ${H28y} Conservative share counts that party's own candidates (${f1(H28.share.CON)}%).${ref('ebchist')} Disproportionality, the effective number of parties and volatility use party families (Conservative, Social Credit, Coalition, Liberal, BC Liberal, CCF and NDP, Green, Reform, others).${ref('gallagher')}${ref('laakso')}${ref('pedersen')}</p>
<p><b>Polls.</b> Each poll is taken from the pollster's own release where it could be opened; the final-poll average uses the last campaign poll from each pollster, fixed before polls closed. A party is shown as rated best only when its gap over the other is larger than the 95% margin of error that a probability sample of the same size would have on the gap between two shares; the pollster notes that a margin of error cannot be calculated for its online panel.${ref('polls')}${ref('ar')}${ref('irg')}${ref('ipsos')}</p>
<p><b>Promises.</b> Quoted or summarized from the Conservative platform, with page numbers.${ref('platform')} The pledge not to raise taxes comes from the party's plan page and its September 27, 2026 release.</p>
<p><b>Map.</b> Official 2023 electoral district boundaries, clipped to land with lakes over 50 km² removed, simplified without gaps for the province view.${ref('bcdc')} The Metro Vancouver, Victoria area and Okanagan views use the full-resolution boundaries, lightly smoothed, with B.C. waters out to the international boundary, lakes over 1 km² and rivers over 50 hectares from the BC Freshwater Atlas drawn as water; areas outside B.C. are left blank.</p>
<p>The full methodology, every script and a table of every published number are in the project's repository: <a href="https://github.com/mediancanadian/bc-election-oct26">github.com/mediancanadian/bc-election-oct26</a>.</p>`;
$('#refs').innerHTML = REFS.map((r, i) => `<li id="ref-${i + 1}">${r.title}.${r.url ? ` <a href="${r.url}" rel="noopener">${r.url.replace(/^https?:\/\//, '')}</a>` : ''}</li>`).join('');
// a reference link opens its closed block first
document.addEventListener('click', e => { const a = e.target.closest('a[href^="#ref-"]'); if (!a) return; const li = $(a.getAttribute('href')); if (!li) return; const d = li.closest('details'); if (d && !d.open) d.open = true; });

// ---------------------------------------------------------------- start: your riding from the link or from this browser
addEventListener('hashchange', () => { const h = (location.hash || '').slice(1).toUpperCase(); if (R[h] && h !== you) setYou(h); });
let start = null;
const hc = (location.hash || '').slice(1).toUpperCase();
if (R[hc]) start = hc; else { try { const v = localStorage.getItem('bc26-riding'); if (v && R[v]) start = v; } catch (e) { /* storage blocked */ } }
setYou(start, {zoom: !!start});
})();
