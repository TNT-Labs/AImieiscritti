---
layout: default
title: Cerca
permalink: /cerca/
---
<section class="wrap search-page">
  <h1 class="page-title">Cerca</h1>
  <input type="search" id="search-input" class="search-input"
         data-endpoint="{{ '/search.json' | relative_url }}"
         placeholder="Cerca tra gli articoli…" autocomplete="off" aria-label="Cerca tra gli articoli">
  <div id="search-results" class="card-grid search-results" aria-live="polite"></div>
</section>
<script src="{{ '/assets/js/search.js' | relative_url }}" defer></script>
