/* 대시보드 내장 검색 엔진: 서버·API 키 없이 브라우저에서 동작
 * 글자 n-gram TF-IDF 를 쓰되, ① 조사·어미·흔한 말 제거 ② 코사인 + 질의 커버리지 혼합
 * ③ 문서 풀 / 교육과정 풀 분리 순위로 짧은 과정명이 문서를 덮지 않게 합니다. */
const RagEngine = (() => {
  const TOK = /[0-9a-z]+|[가-힣]+/g;
  // 조사·어미 (긴 것부터)
  const SUFFIX = /(하고싶어요|싶어요|싶습니다|싶은데|싶은|하려면|하려고|할까요|인가요|입니까|있나요|있어요|해야|해요|합니다|하는|하고|하게|하면|해서|이에요|이예요|예요|에요|으로서|으로|에서|에게|이란|까지|부터|이다|이|가|은|는|을|를|의|에|와|과|도|로|요)$/;
  const STOP = new Set(['갖춰야', '해야', '할', '하는', '하고', '있는', '어떻게', '무엇', '뭐', '어때', '알려줘', '알려', '주세요', '알려주세요',
    '대한', '위한', '관련', '무엇인가요', '인가요', '어떤', '있나요', '추천', '필요한', '필요', '좀', '수', '것', '처음', '싶어', '싶어요', '싶은', '싶다',
    '잘', '잘하고', '잘하는', '좋은', '좋아', '가장', '정말', '너무', '제일', '많이', '자주', '그냥', '바로', '먼저', '지금', '요즘', '우리', '저희',
    '나는', '내가', '제가', '저는', '때', '때문', '경우', '정도', '방법', '어디', '언제', '누가', '왜', '입니다', '있다', '없다', '되는', '되어', '됩니다',
    '해주세요', '궁금', '궁금해요', '문의', '질문', '그리고', '그런', '이런', '저런', '모든', '각', '등', '및', '또는', '통해', '위해', '따라']);

  const norm = tok => {
    if (/^[가-힣]{3,}$/.test(tok)) { const t = tok.replace(SUFFIX, ''); return t.length >= 2 ? t : tok; }
    return tok;
  };
  const gramsOf = text => {
    const m = new Map();
    for (const raw of (String(text).toLowerCase().match(TOK) || [])) {
      if (STOP.has(raw)) continue;
      const tok = norm(raw);
      if (STOP.has(tok)) continue;
      const set = new Set([tok]);
      for (const n of [2, 3]) for (let i = 0; i + n <= tok.length; i++) set.add(tok.slice(i, i + n));
      for (const g of set) m.set(g, (m.get(g) || 0) + 1 + 0.5 * (g.length - 1));
    }
    return m;
  };

  function buildCorpus(docs, data) {
    const G = (data.grades || []).map(g => g.name);
    const out = docs.map(d => ({ t: d.t, d: d.d, p: d.p || 0, s: d.s || '', u: d.u || '', pool: 'doc' }));
    for (const c of data.courses || []) {
      const ct = (data.cats || {})[c.cat];
      const cat = ct && typeof ct === 'object' ? (ct.name || c.cat) : (ct || c.cat || '');
      const target = (c.grades || []).map(i => G[i]).filter(Boolean).join(', ') || '전체';
      out.push({ t: `교육과정: ${c.t}\n교육기관: ${c.inst}\n플랫폼: ${c.plat}\n분야: ${cat}\n추천 직급: ${target}`,
                 d: '대시보드 · 교육과정 목록', p: 0, s: `${c.plat} · ${cat}`, u: c.url || '', pool: 'course' });
    }
    return out;
  }

  function buildIndex(corpus) {
    // 섹션 제목도 검색 대상에 포함 (예: '직급 주임', '인사평가 · ...')
    const vecs = corpus.map(c => gramsOf((c.pool === 'doc' ? c.s + '\n' : '') + c.t));
    const df = new Map();
    vecs.forEach(v => v.forEach((_, g) => df.set(g, (df.get(g) || 0) + 1)));
    const N = corpus.length, idf = g => Math.log(1 + N / (df.get(g) || 1));
    const post = new Map(), norms = new Float64Array(N);
    vecs.forEach((v, i) => {
      let s = 0;
      v.forEach((w, g) => {
        const x = w * idf(g); s += x * x;
        if (!post.has(g)) post.set(g, []);
        post.get(g).push([i, x]);
      });
      norms[i] = Math.sqrt(s) || 1;
    });
    const secTok = corpus.map(c => c.pool === 'doc' ? new Set([...gramsOf(c.s).keys()].filter(g => g.length >= 2)) : null);
    return { corpus, post, norms, idf, secTok };
  }

  /* 점수 = 0.5·코사인 + 0.5·커버리지(질문의 중요 단어 중 문서가 담은 비율).
   * 코사인은 짧은 문서에, 커버리지는 긴 문서에 유리하므로 섞어서 편향을 줄입니다. */
  function score(index, query) {
    const q = gramsOf(query);
    let qn = 0, qTotal = 0; const qw = new Map();
    q.forEach((w, g) => { const x = w * index.idf(g); qw.set(g, x); qn += x * x; qTotal += x; });
    qn = Math.sqrt(qn) || 1; qTotal = qTotal || 1;
    const dot = new Map(), cov = new Map();
    qw.forEach((x, g) => {
      for (const [i, y] of index.post.get(g) || []) {
        dot.set(i, (dot.get(i) || 0) + x * y);
        cov.set(i, (cov.get(i) || 0) + x);
      }
    });
    // 질문 단어가 문서의 섹션 제목(예: '직급 주임')과 정확히 겹치면 가산점
    const qWords = [...q.keys()].filter(g => g.length >= 2 && !qw.has(g + '#')).slice(0, 40);
    const out = [];
    dot.forEach((d, i) => {
      let bonus = 0;
      const st = index.secTok[i];
      if (st) { let hit = 0; for (const g of qWords) if (st.has(g) && g.length >= 2) hit++; bonus = Math.min(0.2, hit * 0.04); }
      out.push({ i, score: Math.min(1, 0.5 * d / (qn * index.norms[i]) + 0.5 * cov.get(i) / qTotal + bonus) });
    });
    return out;
  }

  /* 문서 풀과 교육과정 풀을 따로 순위 매긴 뒤 합칩니다. 문서가 근거에 먼저 오르고,
   * 과정은 남는 자리를 채웁니다(과정을 묻는 질문이면 과정 점수가 높아 자연히 앞섭니다). */
  function search(index, query, topK, threshold) {
    const hits = score(index, query).filter(r => r.score >= threshold)
      .map(r => ({ ...index.corpus[r.i], score: r.score }));
    const docs = hits.filter(h => h.pool === 'doc').sort((a, b) => b.score - a.score);
    const courses = hits.filter(h => h.pool === 'course').sort((a, b) => b.score - a.score);
    const top = [];
    let di = 0, ci = 0;
    while (top.length < topK && (di < docs.length || ci < courses.length)) {
      const d = docs[di], c = courses[ci];
      // 문서 점수에 가산점(0.1)을 줘 비슷한 점수면 문서를 우선
      if (d && (!c || d.score + 0.1 >= c.score)) { top.push(d); di++; } else { top.push(c); ci++; }
    }
    return top.sort((a, b) => b.score - a.score);
  }

  // 질문과 가장 겹치는 줄만 골라 답변 근거 문장으로 사용
  function bestLines(text, query, n = 2) {
    const qg = gramsOf(query);
    return String(text).split(/\n+/).map(l => {
      let s = 0; gramsOf(l).forEach((w, g) => { if (qg.has(g)) s += w; });
      return { l: l.trim(), s };
    }).filter(x => x.l).sort((a, b) => b.s - a.s).slice(0, n).map(x => x.l);
  }
  return { buildCorpus, buildIndex, search, bestLines };
})();
if (typeof window !== 'undefined') window.RagEngine = RagEngine;
if (typeof module !== 'undefined') module.exports = RagEngine;
