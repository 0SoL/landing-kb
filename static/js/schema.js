'use strict';

// JSON-LD injection helper — used server-side via apps/seo/jsonld.py
// This client-side file can be used to augment or override structured data dynamically.

// Example: inject organization schema on pages that don't already have one
(function () {
  const hasSchema = document.querySelector('script[type="application/ld+json"]');
  if (hasSchema) return; // server already injected one

  const org = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'РЖД-Инфра Казахстан',
    areaServed: 'Kazakhstan',
  };

  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.textContent = JSON.stringify(org);
  document.head.appendChild(script);
})();
