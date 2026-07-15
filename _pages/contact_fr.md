---
layout: page
title: contact
permalink: /fr/contact/
lang: fr
nav: false
description: Communiquez pour des demandes de recherche, de supervision, d'enseignement ou de collaboration clinique.
---

{% include language-toggle.liquid en_url="/contact/" fr_url="/fr/contact/" %}

<div class="post">
  <article>
    <p>
      Pour toute demande de recherche, de supervision, d'enseignement ou de collaboration clinique,
      veuillez utiliser le formulaire ci-dessous.
    </p>

    <form action="https://formspree.io/f/mzdndzop" method="POST" class="contact-form">
      <div class="form-group mb-3">
        <label for="name">Nom</label>
        <input type="text" class="form-control" id="name" name="name" required>
      </div>

      <div class="form-group mb-3">
        <label for="email">Votre courriel</label>
        <input type="email" class="form-control" id="email" name="_replyto" required>
      </div>

      <div class="form-group mb-3">
        <label for="subject">Sujet</label>
        <input type="text" class="form-control" id="subject" name="subject">
      </div>

      <div class="form-group mb-3">
        <label for="message">Message</label>
        <textarea class="form-control" id="message" name="message" rows="6" required></textarea>
      </div>

      <input type="hidden" name="_next" value="{{ site.url }}{{ '/fr/contact/success/' | relative_url }}">
      <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">

      <button type="submit" class="btn btn-primary">Envoyer</button>
    </form>

  </article>
</div>
