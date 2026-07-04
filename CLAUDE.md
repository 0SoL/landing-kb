# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Corporate website for a Kazakhstani railway infrastructure company (design, construction, reconstruction of railway tracks for industrial enterprises, ports, logistics terminals).

**Stack:** Django 5.x + Jinja2 templates + Vanilla JS · PostgreSQL (SQLite for local) · django-unfold admin · Gunicorn + Nginx on VPS

## Development Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Database
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata initial_data.json

# Run (uses config/settings/local.py)
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver

# Static files (production)
python manage.py collectstatic
```

Settings module: `config/settings/base.py` + `local.py` / `production.py`. Always pass `DJANGO_SETTINGS_MODULE` explicitly or set it in `.env`.

## Architecture

### App Responsibilities

| App | Purpose |
|-----|---------|
| `apps/core` | Homepage, About, Contacts, FAQ. Contains `CompanyStats` (singleton), `FAQItem`, `ContactInquiry` models |
| `apps/projects` | Portfolio. `Project` + `ProjectImage`. Featured projects pulled by `is_featured=True` |
| `apps/services` | `ServiceCategory` → `Service`. Stages stored as `JSONField` list of `{title, description}` |
| `apps/equipment` | `EquipmentCategory` → `Equipment`. Specs in `JSONField` dict |
| `apps/articles` | Unified content: news, investor articles, technical pieces, director's book — differentiated by `ArticleCategory.slug` |
| `apps/seo` | Sitemap generation, robots.txt view, JSON-LD helper utilities |

### Template Layer

`templates/base.html` is the root layout. All pages extend it. Reusable partials live in `templates/components/`:
- `seo_head.html` — all meta tags + JSON-LD injection point
- `header.html`, `footer.html`, `breadcrumbs.html`, `cta_block.html`

Per-app templates mirror the app structure: `templates/projects/`, `templates/services/`, etc.

### Static Files

```
static/css/base.css          # CSS custom properties, reset, typography
static/css/components.css    # Shared UI components
static/css/pages/            # Per-page styles
static/js/main.js            # Header scroll, mobile menu, counter animation
static/js/schema.js          # JSON-LD injection helpers
```

No inline styles — all styling via CSS custom properties defined in `base.css`.

### View → Template Contract

Every view must pass `meta_title` and `meta_description` to context. All DB queries belong in views, not templates. Templates only handle display logic.

### Contact Form Flow

`ContactInquiry` form → saves to DB → `django.core.mail.send_mail` (synchronous, no Celery). Recipient configured via `INQUIRY_RECIPIENT_EMAIL` env var.

## URL Structure

```
/                           → core: homepage
/uslugi/                    → services: list
/uslugi/<slug>/             → services: detail
/proekty/                   → projects: list (JS filter by client_type, no page reload)
/proekty/<slug>/            → projects: detail
/tekhnika/                  → equipment: list grouped by category
/o-kompanii/                → core: about
/faq/                       → core: FAQ (use <details>/<summary> for crawler-friendly accordion)
/kontakty/                  → core: contacts + inquiry form
/novosti/                   → articles: news list
/novosti/<slug>/            → articles: news detail
/investoram/                → articles: investor category list
/tekhnicheskaya-informatsiya/ → articles: technical category list
/direktoru-kniga/           → articles: director's book section
/sitemap.xml
/robots.txt
```

## Design System

```css
/* CSS Custom Properties — defined in base.css */
--color-primary: #1A1A1A;   /* steel near-black */
--color-accent: #C8922A;    /* amber/gold industrial highlight */
--color-bg: #F5F2EE;        /* warm off-white concrete */
--color-surface: #FFFFFF;
--color-muted: #6B6B6B;

/* Typography */
/* Display: Bebas Neue or DM Serif Display */
/* Body: Geologica or Golos Text (Cyrillic support required) */
/* Numbers/stats: JetBrains Mono */
```

Layout is wide-screen editorial: full-bleed hero sections, asymmetric grids, big numbers as visual anchors. Motion: subtle fade + translateY entrance animations, counter animations for stats only.

## SEO Requirements (Critical)

### JSON-LD — Required on Every Page

Inject via `seo_head.html`. Schema types by page:
- **Homepage:** `Organization` with `areaServed: "Kazakhstan"`, `serviceType`
- **Project detail:** `Project` with `provider: Organization`
- **Service detail:** `Service` with `provider`, `areaServed`, `serviceType`
- **Article:** `Article` with `author`, `datePublished`, `publisher`
- **FAQ:** `FAQPage` with `mainEntity` list — highest-priority AI SEO asset

### robots.txt

Allow all AI crawlers explicitly: `GPTBot`, `Google-Extended`, `PerplexityBot`, `anthropic-ai`.

### Sitemap Priorities

Homepage: 1.0 · Projects/Services: 0.9 · Articles: 0.7

### Semantic HTML Rules

- One `<h1>` per page, keyword-rich
- Use `<article>`, `<section>`, `<nav>`, `<main>`, `<aside>` semantically
- All images: descriptive `alt` attributes + WebP format + `loading="lazy"`
- Dates: `<time datetime="YYYY-MM-DD">`
- FAQ accordion: `<details>`/`<summary>` (crawler-friendly, no JS required to read)

### Performance Targets

Lighthouse score > 90. CSS in `<head>`, JS deferred. `font-display: swap`. WebP images only — add Pillow conversion in model `save()` override or via signal.

## Django Admin (django-unfold)

Admin pattern for all models:
- `list_display` includes publish/featured status
- `list_editable` for `is_published`, `is_featured`, `order`
- `prepopulated_fields = {'slug': ('title',)}`
- SEO fieldset collapsed by default
- `ContactInquiry`: read-only list + bulk "Mark as processed" action

## Definition of Done (Per Page)

- [ ] Renders on 375px mobile and 1440px desktop
- [ ] Has `<h1>`, `<title>`, `<meta description>` in context
- [ ] Has correct JSON-LD structured data
- [ ] All images have `alt` attributes
- [ ] Lighthouse < 3s on 4G
- [ ] Admin can CRUD the content
- [ ] Contact form saves to DB + sends email
- [ ] URL registered in `sitemap.xml`

## What This Project Does NOT Include

No SPA framework · No custom CMS · No payments · No user accounts · No WebSockets · No Celery · No complex REST API
