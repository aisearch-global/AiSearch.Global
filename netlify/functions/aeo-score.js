// AI Visibility Assessment™ — backend analyser
// Uses Node 18 global fetch (no npm dependencies needed)

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

function analyseHtml(html, location, industry, hasSitemap, hasRobots) {
  const text   = extractText(html);
  const lower  = text.toLowerCase();
  const lowerH = html.toLowerCase();

  // H1: strip any inner tags to get actual text
  const h1Match = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  const h1Text  = h1Match ? h1Match[1].replace(/<[^>]+>/g, '').trim() : '';

  // Word count: only words 3+ letters (avoids nav noise)
  const wordCount = text.split(/\s+/).filter(w => /[a-zA-Z]{3,}/.test(w)).length;

  // Industry keyword check
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

function aiView(s) {
  if (s >= 90) return 'AI search engines have a strong, clear understanding of your business. Your site is structured to be cited confidently in AI-generated answers.';
  if (s >= 80) return 'AI can clearly identify your business and what you do. Your site has solid foundations — a few targeted improvements will push you into the top tier.';
  if (s >= 70) return 'AI can understand your business basics, but your site has limited answer-style content and authority signals that reduce your citation rate.';
  if (s >= 60) return 'AI has a partial picture of your business. Gaps in structured data, FAQ content, or entity clarity are reducing the likelihood of AI recommendations.';
  if (s >= 40) return 'AI struggles to clearly identify and describe your business. Multiple important signals are missing, making citations in AI-generated answers unlikely.';
  return              'AI search engines have very limited visibility into your business. Critical signals are missing across several key areas — citations from platforms like ChatGPT or Perplexity are unlikely.';
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

exports.handler = async function (event) {
  const cors = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: cors, body: '' };
  }
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  let body;
  try { body = JSON.parse(event.body || '{}'); } catch {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const { url, industry, location } = body;
  if (!url || !industry) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'url and industry are required' }) };
  }

  // Validate URL
  let parsed;
  try {
    parsed = new URL(url.startsWith('http') ? url : 'https://' + url);
  } catch {
    return { statusCode: 200, headers: cors, body: JSON.stringify({ error: 'invalid_url', message: 'Please enter a valid website URL.' }) };
  }
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return { statusCode: 200, headers: cors, body: JSON.stringify({ error: 'invalid_url', message: 'Please enter a valid website URL.' }) };
  }

  // Fetch page HTML
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
    if (!ct.includes('text/html') && !ct.includes('xhtml')) {
      throw new Error('Not an HTML page');
    }

    html = await res.text();
    // Cap at 400 KB to stay within memory limits
    if (html.length > 400000) html = html.slice(0, 400000);
  } catch {
    return {
      statusCode: 200,
      headers: cors,
      body: JSON.stringify({ error: 'fetch_failed', message: 'We could not analyse this site. Please check the URL and try again.' }),
    };
  }

  // Parallel checks for sitemap + robots.txt
  const base = parsed.origin;
  const [hasSitemap, hasRobots] = await Promise.all([
    checkUrlExists(base + '/sitemap.xml'),
    checkUrlExists(base + '/robots.txt'),
  ]);

  const signals   = analyseHtml(html, location, industry, hasSitemap, hasRobots);
  const total     = score(signals);
  const gradeInfo = grade(total);
  const { fix, gain } = topFix(signals, total);

  return {
    statusCode: 200,
    headers: cors,
    body: JSON.stringify({
      domain:   parsed.hostname,
      industry,
      location: location || null,
      score:    total,
      grade:    gradeInfo.grade,
      color:    gradeInfo.color,
      label:    gradeInfo.label,
      aiView:   aiView(total),
      fix,
      gain,
    }),
  };
};
