#!/usr/bin/env python3
"""Synchronize public ORCID works into the website's BibTeX bibliography.

Existing citation keys and al-folio-only fields are preserved. Standard citation
metadata is refreshed from Crossref when possible and otherwise from ORCID.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ORCID_ID = "0000-0002-1054-2837"
ORCID_API = "https://pub.orcid.org/v3.0"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "jeffreymccrossin.github.io ORCID sync (mailto:jeffrey.mccrossin@umontreal.ca)"


def fetch_json(url: str, accept: str = "application/json") -> dict:
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def clean_doi(value: str) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I).lower()


def value_at(obj: dict | None, *keys: str) -> str:
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
    return str(current or "").strip()


def split_bib_entries(text: str) -> tuple[str, list[str]]:
    starts = [match.start() for match in re.finditer(r"(?m)^@\w+\s*\{", text)]
    if not starts:
        return text, []
    prefix = text[: starts[0]]
    entries: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        entries.append(text[start:end].strip())
    return prefix, entries


def parse_entry(entry: str) -> tuple[str, str, dict[str, str]]:
    header = re.match(r"@(\w+)\s*\{\s*([^,]+),", entry)
    if not header:
        raise ValueError(f"Could not parse BibTeX entry: {entry[:80]}")
    entry_type, key = header.group(1).lower(), header.group(2).strip()
    body = entry[header.end() :]
    fields: dict[str, str] = {}
    position = 0
    field_pattern = re.compile(r"([A-Za-z][\w-]*)\s*=\s*\{")
    while match := field_pattern.search(body, position):
        depth = 1
        cursor = match.end()
        while cursor < len(body) and depth:
            if body[cursor] == "{" and (cursor == 0 or body[cursor - 1] != "\\"):
                depth += 1
            elif body[cursor] == "}" and (cursor == 0 or body[cursor - 1] != "\\"):
                depth -= 1
            cursor += 1
        if depth:
            raise ValueError(f"Unclosed field in BibTeX entry {key}")
        fields[match.group(1).lower()] = body[match.end() : cursor - 1].strip()
        position = cursor
    return entry_type, key, fields


def format_entry(entry_type: str, key: str, fields: dict[str, str]) -> str:
    preferred = ["author", "title", "journal", "booktitle", "publisher", "volume", "number", "pages", "year", "doi", "url", "note"]
    names = [name for name in preferred if fields.get(name)]
    names.extend(sorted(name for name, value in fields.items() if value and name not in names))
    lines = [f"@{entry_type}{{{key},"]
    for index, name in enumerate(names):
        comma = "," if index < len(names) - 1 else ""
        lines.append(f"  {name} = {{{fields[name]}}}{comma}")
    lines.append("}")
    return "\n".join(lines)


def orcid_doi(work: dict) -> str:
    for external_id in (work.get("external-ids") or {}).get("external-id") or []:
        if external_id.get("external-id-type", "").lower() == "doi":
            return clean_doi(external_id.get("external-id-value", ""))
    return ""


def author_from_orcid(contributor: dict) -> str:
    name = value_at(contributor, "credit-name", "value")
    pieces = name.split()
    return f"{pieces[-1]}, {' '.join(pieces[:-1])}" if len(pieces) > 1 else name


def metadata_from_orcid(work: dict) -> tuple[str, dict[str, str]]:
    work_type = work.get("type", "")
    entry_type = "article"
    if work_type in {"book", "edited-book"}:
        entry_type = "book"
    elif work_type in {"book-chapter", "conference-paper"}:
        entry_type = "inproceedings"

    fields: dict[str, str] = {
        "title": value_at(work, "title", "title", "value"),
        "year": value_at(work, "publication-date", "year", "value"),
        "journal": value_at(work, "journal-title", "value"),
        "doi": orcid_doi(work),
        "url": value_at(work, "url", "value"),
    }
    contributors = ((work.get("contributors") or {}).get("contributor") or [])
    authors = [author_from_orcid(item) for item in contributors if value_at(item, "credit-name", "value")]
    if authors:
        fields["author"] = " and ".join(authors)
    if work_type == "preprint":
        fields["note"] = "Preprint"
        if fields.get("doi", "").startswith("10.31235/osf.io/"):
            fields["journal"] = "SocArXiv"
    return entry_type, {key: value for key, value in fields.items() if value}


def metadata_from_crossref(doi: str) -> tuple[str, dict[str, str]] | None:
    try:
        payload = fetch_json(f"{CROSSREF_API}/{urllib.parse.quote(doi, safe='')}")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None
    message = payload.get("message", {})
    crossref_type = message.get("type", "")
    entry_type = {"book": "book", "book-chapter": "inproceedings", "proceedings-article": "inproceedings"}.get(crossref_type, "article")
    authors = []
    for author in message.get("author", []):
        family, given = author.get("family", "").strip(), author.get("given", "").strip()
        name = f"{family}, {given}" if family and given else family or given or author.get("name", "")
        if name:
            authors.append(name)
    date_parts = (message.get("published") or message.get("published-online") or message.get("issued") or {}).get("date-parts", [[]])
    title = (message.get("title") or [""])[0]
    container = (message.get("container-title") or [""])[0]
    fields = {
        "author": " and ".join(authors),
        "title": title,
        "journal": container if entry_type == "article" else "",
        "booktitle": container if entry_type == "inproceedings" else "",
        "publisher": message.get("publisher", "") if entry_type == "book" else "",
        "volume": str(message.get("volume", "")),
        "number": str(message.get("issue", "")),
        "pages": str(message.get("page") or message.get("article-number") or "").replace("-", "--"),
        "year": str(date_parts[0][0]) if date_parts and date_parts[0] else "",
        "doi": clean_doi(message.get("DOI", doi)),
        "url": message.get("URL", f"https://doi.org/{doi}"),
    }
    return entry_type, {key: value for key, value in fields.items() if value}


def citation_key(fields: dict[str, str], used: set[str]) -> str:
    first_author = fields.get("author", "McCrossin").split(" and ")[0].split(",")[0]
    base = normalize(first_author) + fields.get("year", "") + normalize(fields.get("title", ""))[:20]
    base = base or "orcidwork"
    candidate, suffix = base, 2
    while candidate in used:
        candidate, suffix = f"{base}{suffix}", suffix + 1
    return candidate


def synchronize(bib_path: Path, orcid_id: str) -> tuple[int, int]:
    original = bib_path.read_text(encoding="utf-8")
    prefix, raw_entries = split_bib_entries(original)
    parsed = [parse_entry(entry) for entry in raw_entries]
    original_parsed = [(entry_type, key, dict(fields)) for entry_type, key, fields in parsed]
    by_doi = {clean_doi(fields.get("doi", "")): index for index, (_, _, fields) in enumerate(parsed) if fields.get("doi")}
    by_title = {normalize(fields.get("title", "")): index for index, (_, _, fields) in enumerate(parsed) if fields.get("title")}
    used_keys = {key for _, key, _ in parsed}

    summary = fetch_json(f"{ORCID_API}/{orcid_id}/works", "application/vnd.orcid+json")
    groups = summary.get("group", [])
    if len(groups) < 5:
        raise RuntimeError(f"ORCID returned only {len(groups)} work groups; refusing to rewrite bibliography")

    updated = added = 0
    for group in groups:
        summaries = group.get("work-summary", [])
        if not summaries:
            continue
        preferred = max(summaries, key=lambda item: item.get("display-index", 0))
        work = fetch_json(f"{ORCID_API}{preferred['path']}", "application/vnd.orcid+json")
        orcid_type, orcid_fields = metadata_from_orcid(work)
        if not orcid_fields.get("title"):
            continue
        doi = orcid_fields.get("doi", "")
        crossref = metadata_from_crossref(doi) if doi else None
        entry_type, incoming = crossref or (orcid_type, orcid_fields)
        if normalize(incoming.get("title", "")) != normalize(orcid_fields["title"]):
            entry_type, incoming = orcid_type, orcid_fields
        if work.get("type") == "preprint":
            incoming["note"] = "Preprint"
            if doi.startswith("10.31235/osf.io/"):
                incoming.setdefault("journal", "SocArXiv")
        incoming.setdefault("url", f"https://doi.org/{doi}" if doi else "")

        index = by_doi.get(doi) if doi else None
        if index is None:
            index = by_title.get(normalize(orcid_fields["title"]))
        if index is None:
            wanted = normalize(orcid_fields["title"])
            candidates = [
                (difflib.SequenceMatcher(None, wanted, normalize(fields.get("title", ""))).ratio(), candidate_index)
                for candidate_index, (_, _, fields) in enumerate(parsed)
            ]
            score, candidate_index = max(candidates, default=(0.0, 0))
            if score >= 0.78:
                index = candidate_index
        if index is not None:
            old_type, key, old_fields = parsed[index]
            merged = dict(old_fields)
            stale_submission = merged.get("note", "").lower() == "manuscript under review" and work.get("type") == "journal-article" and bool(doi)
            if stale_submission:
                for name in ("journal", "volume", "number", "pages", "year", "doi", "url"):
                    if incoming.get(name):
                        merged[name] = incoming[name]
                merged.pop("note", None)
            elif doi and not merged.get("doi"):
                merged["doi"] = doi
                merged.setdefault("url", f"https://doi.org/{doi}")
            new_value = (entry_type if stale_submission else old_type, key, merged)
            if new_value != parsed[index]:
                parsed[index] = new_value
                updated += 1
        else:
            key = citation_key(incoming, used_keys)
            used_keys.add(key)
            parsed.append((entry_type, key, incoming))
            added += 1

    rendered_entries = []
    for index, entry in enumerate(parsed):
        if index < len(original_parsed) and entry == original_parsed[index]:
            rendered_entries.append(raw_entries[index])
        else:
            rendered_entries.append(format_entry(*entry))
    rendered = prefix.rstrip() + "\n" if prefix.strip() else ""
    rendered += "\n\n".join(rendered_entries) + "\n"
    bib_path.write_text(rendered, encoding="utf-8")
    return updated, added


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", type=Path, default=Path("_bibliography/papers.bib"))
    parser.add_argument("--orcid", default=ORCID_ID)
    args = parser.parse_args()
    try:
        updated, added = synchronize(args.bib, args.orcid)
    except Exception as error:  # Fail closed so a partial API response is never committed.
        print(f"ORCID synchronization failed: {error}", file=sys.stderr)
        traceback.print_exc()
        return 1
    print(f"ORCID synchronization complete: {updated} updated, {added} added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
