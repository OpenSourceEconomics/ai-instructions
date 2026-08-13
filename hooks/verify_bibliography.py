#!/usr/bin/env python3
"""Verify BibTeX entries against CrossRef so citations cannot drift from reality.

The failure this targets is not a malformed file — it is a citation that looks
authoritative and is wrong: a DOI copied from the wrong line of a reference list,
a year silently off by one, a title belonging to a different paper. Those survive
every formatter and every human proofread, and they propagate, because the next
author trusts the reference list they were inherited from.

Two layers, deliberately separated:

- Structural checks run offline and always: duplicate keys, and entries missing
  the author/title/year needed to identify a work at all.
- Metadata verification runs with `--online` and only for entries that already
  carry a DOI. It asks CrossRef what that DOI actually points to and compares the
  title, year, and first author against what the entry claims.

Entries without a DOI are reported but never fail the run by default: in a real
economics bibliography the large majority have none, so demanding one would make
the check unusable. Pass `--require-doi` where a bibliography is curated enough
to hold that line.

Network trouble is a warning, never an error — a flaky runner must not be able to
manufacture a citation failure, and only a definite contradiction should.
"""

import argparse
import contextlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

CROSSREF = "https://api.crossref.org/works/"
HTTP_NOT_FOUND = 404
"""CrossRef's answer for a DOI it has never registered."""

TITLE_SIMILARITY_FLOOR = 0.75
"""Below this ratio a DOI's title is treated as a different work."""

YEAR_SLACK = 1
"""Online-first and print years legitimately differ by one."""

IDENTIFYING_FIELDS = ("title", "year")
ALIASES = {
    "year": ("year", "date"),
    "journal": ("journal", "journaltitle"),
    "author": ("author", "editor"),
}
"""biblatex spellings that satisfy the same requirement as the BibTeX original.

`date` outnumbers `year` by roughly seven to one in a Zotero-exported library, so
treating them as distinct fields would bury real findings under false ones.
"""

VENUE_BY_TYPE = {
    "article": "journal",
    "incollection": "booktitle",
    "inproceedings": "booktitle",
    "techreport": "institution",
    "phdthesis": "school",
    "mastersthesis": "school",
    "book": "publisher",
}
SKIPPED_TYPES = frozenset({"comment", "string", "preamble"})


@dataclass(frozen=True)
class Entry:
    """One parsed BibTeX record."""

    key: str
    """Citation key, as written."""
    entry_type: str
    """Lowercased entry type, e.g. `article`."""
    fields: dict[str, str]
    """Lowercased field name to raw value."""
    path: Path
    """File the entry was read from."""
    line: int
    """1-indexed line where the entry starts."""


@dataclass
class Report:
    """Accumulated findings across all files."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, entry: Entry, message: str) -> None:
        """Record a finding that must fail the run."""
        self.errors.append(f"{entry.path}:{entry.line}: [{entry.key}] {message}")

    def warn(self, entry: Entry, message: str) -> None:
        """Record a finding worth reporting that must not fail the run."""
        self.warnings.append(f"{entry.path}:{entry.line}: [{entry.key}] {message}")


def parse_bibtex(text: str, path: Path) -> list[Entry]:
    """Parse `text` into entries, tracking brace depth so nested values survive."""
    entries: list[Entry] = []
    for match in re.finditer(r"@(\w+)\s*\{", text):
        entry_type = match.group(1).lower()
        if entry_type in SKIPPED_TYPES:
            continue
        body = _read_balanced(text, match.end() - 1)
        if body is None:
            continue
        key, _, rest = body.partition(",")
        entries.append(
            Entry(
                key=key.strip(),
                entry_type=entry_type,
                fields=_parse_fields(rest),
                path=path,
                line=text.count("\n", 0, match.start()) + 1,
            )
        )
    return entries


def _read_balanced(text: str, start: int) -> str | None:
    """Return the text inside the braces opening at `start`, or None if unclosed."""
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    return None


def _parse_fields(text: str) -> dict[str, str]:
    """Split an entry body into a mapping of lowercased field names to values."""
    fields: dict[str, str] = {}
    index = 0
    while index < len(text):
        match = re.compile(r"(\w+)\s*=\s*").search(text, index)
        if match is None:
            break
        name = match.group(1).lower()
        value, index = _read_value(text, match.end())
        if name not in fields:
            fields[name] = value
    return fields


def _read_value(text: str, start: int) -> tuple[str, int]:
    """Read one field value beginning at `start`; return it with the next index."""
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text):
        return "", start
    if text[start] == "{":
        inner = _read_balanced(text, start)
        if inner is not None:
            return inner.strip(), start + len(inner) + 2
    if text[start] == '"':
        end = text.find('"', start + 1)
        if end != -1:
            return text[start + 1 : end].strip(), end + 1
    end = text.find(",", start)
    end = len(text) if end == -1 else end
    return text[start:end].strip(), end


def get_field(entry: Entry, name: str) -> str:
    """Return `name` from `entry`, accepting any recognized biblatex alias."""
    for candidate in ALIASES.get(name, (name,)):
        value = entry.fields.get(candidate, "").strip()
        if value:
            return value
    return ""


def normalize(value: str) -> str:
    """Reduce a LaTeX-flavored string to comparable lowercase words."""
    value = re.sub(r"\\[a-zA-Z]+\s*", " ", value)
    value = re.sub(r"[{}\\$]", "", value)
    value = re.sub(r"[^\w\s]", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def first_surname(authors: str) -> str:
    """Return the normalized surname of the first author in a BibTeX author list."""
    first = re.split(r"\s+and\s+", authors.strip(), maxsplit=1)[0]
    surname = first.split(",")[0] if "," in first else first.split()[-1:] or [""]
    return normalize(surname if isinstance(surname, str) else surname[0])


def check_structure(entries: list[Entry], report: Report, *, require_doi: bool) -> None:
    """Apply the offline checks that need no network access."""
    seen: dict[str, Entry] = {}
    for entry in entries:
        if entry.key in seen:
            report.error(
                entry,
                f"duplicate citation key, first defined at {seen[entry.key].path}",
            )
        else:
            seen[entry.key] = entry

        for name in IDENTIFYING_FIELDS:
            if not get_field(entry, name):
                report.error(entry, f"missing required field `{name}`")
        if not get_field(entry, "author"):
            report.error(entry, "missing both `author` and `editor`")

        venue = VENUE_BY_TYPE.get(entry.entry_type)
        if venue and not get_field(entry, venue):
            report.warn(entry, f"`@{entry.entry_type}` without `{venue}`")

        if not entry.fields.get("doi"):
            message = "no DOI, so the citation cannot be verified automatically"
            if require_doi and not entry.fields.get("url"):
                report.error(entry, message)
            else:
                report.warn(entry, message)


def fetch_crossref(doi: str, mailto: str | None, timeout: float) -> dict | None:
    """Return CrossRef's record for `doi`, None if unknown, raising on network error."""
    url = CROSSREF + urllib.parse.quote(doi, safe="")
    agent = "verify_bibliography/1.0"
    if mailto:
        agent += f" (mailto:{mailto})"
    request = urllib.request.Request(url, headers={"User-Agent": agent})  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return json.loads(response.read()).get("message")
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            return None
        raise


def compare_metadata(entry: Entry, record: dict, report: Report) -> None:
    """Compare a CrossRef record against what the entry claims."""
    titles = record.get("title") or []
    claimed_title = get_field(entry, "title")
    if titles and claimed_title and not _titles_agree(claimed_title, titles[0]):
        report.error(
            entry,
            f"DOI {entry.fields['doi']} is a different work: "
            f"entry says {claimed_title!r}, CrossRef says {titles[0]!r}",
        )

    actual_year = _crossref_year(record)
    claimed_year = re.search(r"\d{4}", get_field(entry, "year"))
    if actual_year and claimed_year:
        difference = abs(int(claimed_year.group()) - actual_year)
        if difference > YEAR_SLACK:
            report.error(
                entry,
                f"year {claimed_year.group()} contradicts CrossRef's {actual_year}",
            )

    authors = record.get("author") or []
    claimed_author = get_field(entry, "author")
    if authors and claimed_author:
        actual_surname = normalize(authors[0].get("family", ""))
        claimed_surname = first_surname(claimed_author)
        if actual_surname and claimed_surname and actual_surname != claimed_surname:
            report.warn(
                entry,
                f"first author {claimed_surname!r} does not match "
                f"CrossRef's {actual_surname!r}",
            )


def _titles_agree(claimed: str, actual: str) -> bool:
    """Judge whether two titles denote the same work.

    Registries routinely store a work under its main title alone while the
    bibliography carries the full `Main Title: Subtitle`. Containment therefore
    counts as agreement — otherwise every subtitled work reports as a mismatch,
    which is the single largest source of false positives on a real library.
    """
    left, right = normalize(claimed), normalize(actual)
    if not left or not right:
        return True
    if left in right or right in left:
        return True
    return SequenceMatcher(None, left, right).ratio() >= TITLE_SIMILARITY_FLOOR


def _crossref_year(record: dict) -> int | None:
    """Extract a publication year, preferring the print date over the online one."""
    for key in ("published-print", "issued", "published-online", "created"):
        parts = (record.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def check_online(
    entries: list[Entry], report: Report, options: argparse.Namespace
) -> None:
    """Verify every entry that carries a DOI against CrossRef."""
    cache = _load_cache(options.cache)
    checked = 0
    for entry in entries:
        doi = entry.fields.get("doi", "").strip()
        if not doi:
            continue
        doi = re.sub(r"^(https?://(dx\.)?doi\.org/)", "", doi, flags=re.IGNORECASE)
        if doi in cache:
            record = cache[doi]
        else:
            try:
                record = fetch_crossref(doi, options.mailto, options.timeout)
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                report.warn(entry, f"could not reach CrossRef for {doi}: {error}")
                continue
            except json.JSONDecodeError:
                report.warn(entry, f"CrossRef returned unreadable JSON for {doi}")
                continue
            cache[doi] = record
            checked += 1
            time.sleep(options.delay)
        if record is None:
            report.error(entry, f"DOI {doi} is not registered with CrossRef")
        else:
            compare_metadata(entry, record, report)
    _save_cache(options.cache, cache)
    print(f"Verified {checked} DOI(s) against CrossRef ({len(cache)} cached).")


def _load_cache(path: Path | None) -> dict:
    """Read the DOI metadata cache, tolerating absence or corruption."""
    if path is None or not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(path: Path | None, cache: dict) -> None:
    """Persist the DOI metadata cache; a failed write must not fail the check."""
    if path is None:
        return
    with contextlib.suppress(OSError):
        path.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line interface."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("files", nargs="+", type=Path, help="`.bib` files to check")
    parser.add_argument(
        "--online", action="store_true", help="verify DOIs against CrossRef"
    )
    parser.add_argument("--mailto", help="contact address for CrossRef's polite pool")
    parser.add_argument(
        "--require-doi",
        action="store_true",
        help="treat an entry with neither DOI nor URL as an error",
    )
    parser.add_argument("--cache", type=Path, help="path to a DOI metadata cache")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--delay", type=float, default=0.1, help="seconds between CrossRef requests"
    )
    parser.add_argument(
        "--warnings-as-errors", action="store_true", help="also fail on warnings"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Check every requested bibliography; return 1 if anything failed."""
    options = build_parser().parse_args(argv)
    report = Report()

    entries: list[Entry] = []
    for path in options.files:
        try:
            entries.extend(parse_bibtex(path.read_text(encoding="utf-8"), path))
        except (OSError, UnicodeDecodeError) as error:
            report.errors.append(f"{path}: could not read: {error}")

    check_structure(entries, report, require_doi=options.require_doi)
    if options.online:
        check_online(entries, report, options)

    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}")
    print(
        f"\n{len(entries)} entries checked; "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )

    if report.errors:
        return 1
    return 1 if options.warnings_as_errors and report.warnings else 0


if __name__ == "__main__":
    sys.exit(main())
