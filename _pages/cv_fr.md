---
layout: page
lang: fr
permalink: /fr/cv/
title: CV
nav: false
description: Téléchargez le CV le plus récent ou communiquez pour en savoir plus.
---

<div class="post">
  <header class="post-header">
    <h1 class="post-title">{{ page.title }}</h1>
    {% if page.description %}
      <p class="post-description">{{ page.description }}</p>
    {% endif %}
    {% include language-toggle.liquid en_url="/cv/" fr_url="/fr/cv/" %}
  </header>

  <article>
    <div class="cv-html-link">
      <p>
        Vous préférez une version navigateur plutôt qu'un PDF? Ouvrez le
        <a href="{{ '/assets/html/Jeffrey_McCrossin_CV_2026_fr.html' | relative_url }}">CV HTML en français</a>
        ou téléchargez le <a href="{{ '/assets/html/cv_full_toc_fr.pdf' | relative_url }}">PDF (FR)</a>.
        Les deux versions comprennent une table des matières.
        Pour toute demande directe, utilisez le <a href="{{ '/fr/contact/' | relative_url }}">formulaire de contact</a>.
      </p>
    </div>
  </article>
</div>
