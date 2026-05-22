# AISearch Global Website

This is a static, SEO-first landing site for `https://aisearch.global`.

## Files
- `index.html` - Main website
- `robots.txt` - Crawl directives
- `sitemap.xml` - Search engine sitemap

## Recommended hosting (Cloudflare Pages)
1. Push this repo to GitHub.
2. In Cloudflare: `Workers & Pages` -> `Create` -> `Pages` -> `Connect to Git`.
3. Select this repo.
4. Build settings:
   - Framework preset: `None`
   - Build command: *(leave empty)*
   - Build output directory: `/`
5. Deploy.
6. Add custom domain: `aisearch.global` and `www.aisearch.global`.
7. In DNS:
   - `CNAME` for `www` to your Cloudflare Pages target.
   - Apex/root (`aisearch.global`) using Cloudflare CNAME flattening to same target.
8. Enable SSL/TLS Full (strict).

## Post-launch SEO setup
- Submit `https://aisearch.global/sitemap.xml` in Google Search Console.
- Add and verify both properties:
  - `https://aisearch.global`
  - `https://www.aisearch.global` (if enabled)
- Set canonical preference to root domain.
- Add Bing Webmaster Tools and submit sitemap.
- Create and upload actual `og-image.jpg` and `logo.png`.
- Set up analytics (GA4 or Plausible) and event tracking for form submits.

## Optional improvements
- Add dedicated pages:
  - `/services/aoe-audit`
  - `/services/schema-implementation`
  - `/insights/` articles
- Add `WebPage`, `BreadcrumbList`, and `Article` schema on those pages.
- Add real case studies/testimonials and author bios for E-E-A-T signals.
