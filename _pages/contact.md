---
layout: page
title: contact
permalink: /contact/
nav: true
nav_order: 2
description: Get in touch for research, clinical, teaching, or collaboration inquiries.
---

{% include language-toggle.liquid en_url="/contact/" fr_url="/fr/contact/" %}

<div class="post">
  <article>
    <p>
      For research, supervision, teaching, or clinical collaboration inquiries, please use the form
      below. This helps keep the site free of a publicly listed email address, which reduces spam and
      phishing attempts.
    </p>

    <form action="https://formspree.io/f/mzdndzop" method="POST" class="contact-form">
      <div class="form-group mb-3">
        <label for="name">Name</label>
        <input type="text" class="form-control" id="name" name="name" required>
      </div>

      <div class="form-group mb-3">
        <label for="email">Your email</label>
        <input type="email" class="form-control" id="email" name="_replyto" required>
      </div>

      <div class="form-group mb-3">
        <label for="subject">Subject</label>
        <input type="text" class="form-control" id="subject" name="subject">
      </div>

      <div class="form-group mb-3">
        <label for="message">Message</label>
        <textarea class="form-control" id="message" name="message" rows="6" required></textarea>
      </div>

      <input type="hidden" name="_next" value="{{ site.url }}{{ '/contact/success/' | relative_url }}">
      <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">

      <button type="submit" class="btn btn-primary">Send message</button>
    </form>

  </article>
</div>
