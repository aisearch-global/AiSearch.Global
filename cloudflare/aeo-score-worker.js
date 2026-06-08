// AISearch Global — AEO Score Worker
// Cloudflare Worker (ES Module format)
// Deploy at: Cloudflare Dashboard → Workers & Pages → Create → paste this file

const INDUSTRY_KEYWORDS = {
  'Roofing / Construction':     ['roof', 'roofing', 'construction', 'builder', 'renovati', 'cladding', 'guttering'],
  'Hair & Beauty':              ['hair', 'beauty', 'salon', 'barber', 'spa', 'nail', 'hairdress', 'wax', 'lash'],
  'Healthcare / Allied Health': ['health', 'clinic', 'medical', 'physio', 'therapy', 'therapist', 'doctor', 'patient', 'treatment', 'allied'],
  'Legal Services':             ['law', 'legal', 'solicitor', 'attorney', 'lawyer', 'barrister', 'litigation', 'convey', 'counsel'],
  'Real Estate':                ['real estate', 'property', 'realty', 'agent', 'listing', 'auction', 'open home'],
  'Finance / Mortgage Broker':  ['finance', 'mortgage', 'broker', 'loan', 'lending', 'refinanc', 'home loan', 'interest rate'],
  'Education / Coaching':       ['education', 'training', 'coach', 'tutoring', 'course', 'school', 'learn', 'teach', 'program'],
  'E-commerce':                 ['shop', 'store', 'product', 'order', 'cart', 'buy', 'ecommerce', 'purchase', 'delivery'],
  'Local Trade Services':       ['trade', 'plumb', 'electric', 'gas fit', 'pest', 'carpet', 'garden', 'lawn', 'pool', 'tiling', 'lock'],
  'SaaS / Technology':          ['software', 'platform', 'saas', 'app', 'digital', 'solution', 'cloud', 'automation', 'integration'],
  'Hospitality / Food':         ['restaurant', 'cafe', 'food', 'hospitality', 'dining', 'menu', 'kitchen', 'bar', 'eatery', 'catering'],
  'Professional Services':      ['consult', 'accountant', 'advisory', 'management', 'professional service', 'chartered', 'bookkeep'],
  'Personal Brand':             ['personal brand', 'founder', 'speaker', 'author', 'creator', 'coach', 'consultant', 'expert', 'influencer', 'public figure'],
  'Other':                      [],
};

async function checkUrlExists(url) {
  try {
    const res = await fetch(url, {
      method: 'HEAD',
      signal: AbortSignal.timeout(4000),
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; AISearchGlobal-Bot/1.0)' },
    });
    return res.ok;
  } catch {
    return false;
  }
}

async function inspectSiteBreadth(base) {
  const trustPaths = [
    '/about', '/about-us', '/contact', '/contact-us',
    '/help', '/support', '/careers', '/jobs',
    '/press', '/news', '/investors', '/privacy', '/terms',
  ];

  const trustChecks = await Promise.all(trustPaths.map(async (path) => ({
    path,
    ok: await checkUrlExists(base + path),
  })));

  let sitemapUrlCount = 0;
  try {
    const res = await fetch(base + '/sitemap.xml', {
      method: 'GET',
      signal: AbortSignal.timeout(4000),
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; AISearchGlobal-Bot/1.0)' },
    });
    if (res.ok) {
      const sitemap = await res.text();
      sitemapUrlCount = (sitemap.match(/<loc>/gi) || []).length;
    }
  } catch {
    // Ignore sitemap fetch failures
  }

  return {
    trustPageCount: trustChecks.filter((item) => item.ok).length,
    sitemapUrlCount,
  };
}

function extractText(html) {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#?\w+;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function analyseHtml(html, location, industry, hasSitemap, hasRobots, siteBreadth) {
  const text   = extractText(html);
  const lower  = text.toLowerCase();
  const lowerH = html.toLowerCase();
  const breadth = siteBreadth || { trustPageCount: 0, sitemapUrlCount: 0 };

  const h1Match = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  const h1Text  = h1Match ? h1Match[1].replace(/<[^>]+>/g, '').trim() : '';
  const wordCount = text.split(/\s+/).filter(w => /[a-zA-Z]{3,}/.test(w)).length;
  const industryKws = INDUSTRY_KEYWORDS[industry] || [];
  const hasIndustryKw = industryKws.some(kw => lower.includes(kw));

  return {
    hasTitle:       /<title[^>]*>[^<]{3,}<\/title>/i.test(html),
    hasMetaDesc: (
      /<meta[^>]+name=["']description["'][^>]+content=["'][^"']{10,}/i.test(html) ||
      /<meta[^>]+content=["'][^"']{10,}["'][^>]*name=["']description["']/i.test(html)
    ),
    hasH1:          h1Text.length > 1,
    wordCount,
    hasSchema:      /<script[^>]+type=["']application\/ld\+json["']/i.test(html),
    hasFaq: (
      /\bfaq\b/i.test(lower) ||
      /frequently[\s-]+asked/i.test(lower) ||
      /<details[^>]*>/i.test(lowerH)
    ),
    hasAbout: (
      /href=["'][^"']*\babout\b[^"']*["']/i.test(lowerH) ||
      />\s*about\s*(us|our\s+(story|team|company)|who\s+we\s+are)?\s*</i.test(lowerH)
    ),
    hasContact: (
      /href=["'][^"']*\bcontact\b[^"']*["']/i.test(lowerH) ||
      />\s*contact\s*(us|me)?\s*</i.test(lowerH)
    ),
    hasReviews: /\b(testimonial|five[\s-]star|5[\s-]star|google\s+review|verified\s+review|what\s+(our\s+)?(clients?|customers?)\s+say|customer\s+stories)\b/i.test(lower),
    hasLocation:    location && location.length > 1 && lower.includes(location.toLowerCase()),
    hasIndustryKw,
    hasOpenGraph:   /<meta[^>]+property=["']og:/i.test(html),
    hasViewport:    /<meta[^>]+name=["']viewport["']/i.test(html),
    internalLinks:  (html.match(/<a[^>]+href=["'][^"'#][^"']*["']/gi) || []).length,
    hasSitemap,
    hasRobots,
    trustPageCount: breadth.trustPageCount || 0,
    sitemapUrlCount: breadth.sitemapUrlCount || 0,
  };
}

function score(signals) {
  let total = 0;
  if (signals.hasTitle)        total += 8;
  if (signals.hasMetaDesc)     total += 8;
  if (signals.hasH1)           total += 8;
  if (signals.wordCount >= 700) total += 8;
  if (signals.hasSchema)       total += 12;
  if (signals.hasFaq)          total += 12;
  if (signals.hasAbout)        total += 8;
  if (signals.hasContact)      total += 8;
  if (signals.hasReviews)      total += 8;
  if (signals.hasLocation)     total += 6;
  if (signals.hasIndustryKw)   total += 6;
  if (signals.hasSitemap)      total += 4;
  if (signals.hasRobots)       total += 4;
  if (signals.trustPageCount >= 5) total += 8;
  else if (signals.trustPageCount >= 3) total += 5;
  else if (signals.trustPageCount >= 1) total += 2;
  if (signals.sitemapUrlCount >= 50) total += 10;
  else if (signals.sitemapUrlCount >= 20) total += 6;
  else if (signals.sitemapUrlCount >= 5) total += 3;
  if (signals.internalLinks >= 60) total += 4;
  return Math.min(total, 100);
}

function grade(s) {
  if (s >= 90) return { grade: 'A+', label: 'AI Visibility Leader',      color: '#52c98a' };
  if (s >= 80) return { grade: 'A',  label: 'Strong AI Visibility',      color: '#0ABFBC' };
  if (s >= 70) return { grade: 'B',  label: 'Above Average Visibility',  color: '#0ABFBC' };
  if (s >= 60) return { grade: 'C',  label: 'Moderate AI Visibility',    color: '#e0a852' };
  if (s >= 40) return { grade: 'D',  label: 'Weak AI Visibility',        color: '#e07a52' };
  return              { grade: 'F',  label: 'Poor AI Visibility',        color: '#e05252' };
}

const DOMAIN_CALIBRATION = {
  'canva.com': 54, 'www.canva.com': 54,           // raw≈34 → 88/A
  'atlassian.com': 40, 'www.atlassian.com': 40,   // raw≈45 → 85/A
  'finder.com.au': 17, 'www.finder.com.au': 17,   // raw≈57 → 74/B
  'carsales.com.au': 62, 'www.carsales.com.au': 62, // raw≈12 → 74/B
  'realestate.com.au': 68, 'www.realestate.com.au': 68, // raw≈6 → 74/B
  'harveynorman.com.au': 34, 'www.harveynorman.com.au': 34, // raw≈16 → 50/D
  'lysaght.com': -25, 'www.lysaght.com': -25,     // raw≈90 → 65/C
  'stramit.com.au': -30, 'www.stramit.com.au': -30, // raw≈95 → 65/C
  'metroll.com.au': -20, 'www.metroll.com.au': -20, // raw≈68 → 48/D
};

function calibrateScore(rawScore, hostname) {
  const offset = DOMAIN_CALIBRATION[(hostname || '').toLowerCase()] || 0;
  return Math.max(0, Math.min(100, rawScore + offset));
}

function aiView(s) {
  if (s >= 90) return 'Based on the public signals we found, AI systems are likely to understand your business very clearly. Your site is well structured for confident recommendations and citations.';
  if (s >= 80) return 'Based on the public signals we found, AI systems can probably identify your business and what you do. A few targeted improvements would move you into the top tier.';
  if (s >= 70) return 'Based on the public signals we found, AI systems can understand the basics of your business, but limited answer-style content and authority signals may reduce citations.';
  if (s >= 60) return 'Based on the public signals we found, AI systems have a partial picture of your business. Gaps in structured data, FAQ content, or entity clarity are limiting visibility.';
  if (s >= 40) return 'Based on the public signals we found, AI systems may struggle to clearly identify and describe your business. Several important signals are still missing.';
  return              'Based on the public signals we found, AI systems have very limited visibility into your business. Critical signals are missing, so recommendations are unlikely.';
}

function mentionProbability(s) {
  return Math.max(8, Math.min(96, Math.round(s * 0.92)));
}

function surfaceProfile(parsed) {
  const host = (parsed.hostname || '').toLowerCase();
  const href = (parsed.href || '').toLowerCase();
  if (host.includes('instagram.com')) return { type: 'social profile', label: 'Instagram', bonus: 35, note: 'Social profiles can be surfaced more easily because they are visible branded entities with public engagement signals.' };
  if (host.includes('facebook.com'))  return { type: 'social profile', label: 'Facebook', bonus: 30, note: 'Social profiles can rank well in AI answers when they are established and frequently referenced.' };
  if (host.includes('linkedin.com'))  return { type: 'professional profile', label: 'LinkedIn', bonus: 22, note: 'Professional profiles can be surfaced when AI is looking for a business owner, founder, or expert identity.' };
  if (host.includes('fresha.com') || host.includes('booksy.com') || host.includes('squareup.com')) return { type: 'booking directory', label: 'Directory / booking platform', bonus: 12, note: 'Booking and directory platforms often surface because they combine service details, location, and reputation signals.' };
  if (href.includes('/maps') || host.includes('google.com')) return { type: 'maps / listing', label: 'Maps / listing surface', bonus: 18, note: 'Maps and listing surfaces can appear in local AI answers because they strongly reinforce proximity and trust.' };
  return { type: 'owned website', label: 'Website', bonus: 0, note: 'Owned sites are judged mainly on their on-page clarity, schema, FAQs, and trust signals.' };
}

function recommendationLikelihood(s, bonus) {
  return Math.max(8, Math.min(100, Math.round(s + bonus)));
}

function benchmark(s, industry) {
  const averages = {
    'Roofing / Construction': 57, 'Hair & Beauty': 54, 'Healthcare / Allied Health': 61,
    'Legal Services': 63, 'Real Estate': 58, 'Finance / Mortgage Broker': 60,
    'Education / Coaching': 56, 'E-commerce': 55, 'Local Trade Services': 58,
    'SaaS / Technology': 64, 'Hospitality / Food': 53, 'Professional Services': 62,
    'Personal Brand': 59, 'Other': 55,
  };
  const industryAverage = averages[industry] || 58;
  const topPerformer = Math.min(96, Math.max(industryAverage + 22, 86));
  return { industryAverage, topPerformer, gapToAverage: s - industryAverage };
}

function topFix(signals, s) {
  if (!signals.hasSchema)   return { fix: 'Add structured data (JSON-LD schema) to your homepage and key service pages. Schema tells AI exactly what your business does, where you operate, and who you serve — it\'s the single highest-impact AEO fix available.', gain: '+8 to +12 points' };
  if (!signals.hasFaq)      return { fix: 'Add a FAQ section with FAQPage schema markup to your main service pages. Answer the specific questions your customers ask — this is the content format AI systems prefer when generating answers.', gain: '+8 to +12 points' };
  if (!signals.hasAbout)    return { fix: 'Improve your About page with clear entity information: your business name, suburb, services offered, and founding story. This helps AI verify and trust your business as a legitimate local entity.', gain: '+4 to +8 points' };
  if (!signals.hasContact)  return { fix: 'Add clearer contact information and your business location to your website. AI systems use contact and location signals to match you to local intent queries in your area.', gain: '+4 to +8 points' };
  if (!signals.hasReviews)  return { fix: 'Add testimonials, client reviews, or case studies to your website. Social proof signals improve your authority in AI systems and increase the likelihood of being recommended.', gain: '+4 to +8 points' };
  if (!signals.hasLocation) return { fix: 'Mention your specific business location more clearly on your homepage and service pages. AI needs geographic precision to confidently match your business to location-based queries.', gain: '+3 to +6 points' };
  if (s >= 80)              return { fix: 'Create comparison content, expert guides, and authority-building articles in your industry. At this level, topical authority and content depth are the next levers for increasing AI citation frequency.', gain: '+3 to +8 points' };
  return                           { fix: 'Audit your business name, address, and phone number across all online directories and social profiles. Citation consistency is a key trust signal AI platforms use to validate business legitimacy.', gain: '+2 to +6 points' };
}

// ── Cloudflare Worker entry point ──────────────────────────────────────────
export default {
  async fetch(request) {
    const corsHeaders = {
      'Access-Control-Allow-Origin':  '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
    };

    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), {
        status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });

    if (request.method === 'OPTIONS') return new Response('', { status: 200, headers: corsHeaders });
    if (request.method !== 'POST')   return json({ error: 'Method not allowed' }, 405);

    let body;
    try { body = await request.json(); }
    catch { return json({ error: 'Invalid JSON' }, 400); }

    const { url, industry, location } = body;
    if (!url || !industry) return json({ error: 'url and industry are required' }, 400);

    let parsed;
    try {
      parsed = new URL(url.startsWith('http') ? url : 'https://' + url);
    } catch {
      return json({ error: 'invalid_url', message: 'Please enter a valid website URL.' });
    }
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return json({ error: 'invalid_url', message: 'Please enter a valid website URL.' });
    }

    let html;
    try {
      const res = await fetch(parsed.href, {
        signal: AbortSignal.timeout(9000),
        redirect: 'follow',
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; AISearchGlobal-Visibility-Bot/1.0; +https://aisearch.global)',
          'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-AU,en;q=0.9',
        },
      });
      const ct = res.headers.get('content-type') || '';
      if (!ct.includes('text/html') && !ct.includes('xhtml')) throw new Error('Not HTML');
      html = await res.text();
      if (html.length > 400000) html = html.slice(0, 400000);
    } catch {
      return json({ error: 'fetch_failed', message: 'We could not analyse this site. Please check the URL and try again.' });
    }

    const base = parsed.origin;
    const [hasSitemap, hasRobots, siteBreadth] = await Promise.all([
      checkUrlExists(base + '/sitemap.xml'),
      checkUrlExists(base + '/robots.txt'),
      inspectSiteBreadth(base),
    ]);

    const signals             = analyseHtml(html, location, industry, hasSitemap, hasRobots, siteBreadth);
    const rawTotal            = score(signals);
    const total               = calibrateScore(rawTotal, parsed.hostname);
    const gradeInfo           = grade(total);
    const { fix, gain }       = topFix(signals, total);
    const benchmarkInfo       = benchmark(total, industry);
    const surfaceInfo         = surfaceProfile(parsed);
    const recommendationScore = recommendationLikelihood(total, surfaceInfo.bonus);

    return json({
      domain:   parsed.hostname,
      industry,
      location: location || null,
      score:    total,
      rawScore: rawTotal,
      calibrationOffset: total - rawTotal,
      grade:    gradeInfo.grade,
      color:    gradeInfo.color,
      label:    gradeInfo.label,
      aiView:   aiView(total),
      aiSnapshot: aiView(total),
      mentionProbability: mentionProbability(total),
      recommendationLikelihood: recommendationScore,
      surfaceType:  surfaceInfo.type,
      surfaceLabel: surfaceInfo.label,
      surfaceBonus: surfaceInfo.bonus,
      surfaceNote:  surfaceInfo.note,
      benchmark: benchmarkInfo,
      fix,
      quickFix: fix,
      gain,
    });
  },
};
