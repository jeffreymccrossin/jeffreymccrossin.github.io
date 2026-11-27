---
layout: page
permalink: /fr/teaching/
title: enseignement
lang: fr
nav: false
description: Ressources et ateliers pour les cours enseignés.
---

{% include language-toggle.liquid en_url="/teaching/" fr_url="/fr/teaching/" %}

<div id="teaching-gate" class="card p-4 my-3" style="max-width:480px">
  <h3 class="mt-0">Accès étudiant</h3>
  <p>Entrez le mot de passe du cours pour accéder aux documents de l’atelier PSE1208.</p>
  <form id="teaching-form">
    <div class="form-group mb-3">
      <input type="password" id="teaching-pw" class="form-control" placeholder="Mot de passe du cours" aria-label="Mot de passe du cours" autocomplete="off" required>
    </div>
    <button type="submit" class="btn btn-primary">Accéder</button>
    <div id="teaching-err" class="text-danger mt-2" role="alert"></div>
  </form>
</div>

<div id="teaching-content" hidden>
  <h3>PSE1208 · Introduction à la psychoéducation</h3>
  <p><strong>Atelier du 1<sup>er</sup> décembre 2026 — Concevoir et ajuster une intervention</strong></p>
  <ul>
    <li><a href="https://jeffreymccrossin.github.io/pse1208-atelier-2026-12-01/carte-intervention.html">Carte conceptuelle interactive de l’intervention</a></li>
    <li><a href="https://jeffreymccrossin.github.io/pse1208-atelier-2026-12-01/exemple-fluppy.html">Exemple guidé · Fluppy en maternelle</a></li>
    <li><a href="https://jeffreymccrossin.github.io/pse1208-atelier-2026-12-01/atelier-balado.html">Fiche d’équipe · Étude de cas audio</a></li>
    <li><a href="https://jeffreymccrossin.github.io/pse1208-atelier-2026-12-01/carte-intervention.pdf">Version PDF complète (hors ligne / impression)</a></li>
  </ul>
</div>

<script>
(function () {
  const K = "pse1208_auth_v1";
  const H = "c965848b6f2eb76f98bc54d40928d8d5948f6e5082e12c223718d3584f96a694";
  const gate = document.getElementById("teaching-gate");
  const content = document.getElementById("teaching-content");
  const form = document.getElementById("teaching-form");
  const input = document.getElementById("teaching-pw");
  const err = document.getElementById("teaching-err");

  function unlock() {
    gate.hidden = true;
    content.hidden = false;
  }

  if (sessionStorage.getItem(K) === H) {
    unlock();
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const val = input.value.trim().toLowerCase();
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(val));
    const hex = Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
    if (hex === H) {
      sessionStorage.setItem(K, H);
      unlock();
    } else {
      err.textContent = "Mot de passe incorrect. Veuillez réessayer.";
      input.select();
    }
  });
})();
</script>
