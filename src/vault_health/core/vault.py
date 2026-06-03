"""Vault scanner — walks directory tree, parses frontmatter, builds link graph."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VaultFile:
    """Represents a single markdown file in the vault."""
    path: str
    relative_path: str
    content: str
    wikilinks: list[str] = field(default_factory=list)
    inbound_links: list[str] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)
    frontmatter: dict[str, str] = field(default_factory=dict)
    word_count: int = 0
    line_count: int = 0
    mtime: float = 0.0  # modification timestamp


@dataclass
class Vault:
    """The entire vault: collection of files + link graph."""
    root: str
    files: dict[str, VaultFile] = field(default_factory=dict)
    total_files: int = 0
    total_wikilinks: int = 0
    broken_links: int = 0


WIKILINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)
SKIP_PATTERNS = [
    '.git', '__pycache__', 'node_modules', '.obsidian',
    '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg',
    '*.pdf', '*.zip', '*.exe', '*.db', '*.bak',
]


def _should_skip(rel_path: str) -> bool:
    for pat in SKIP_PATTERNS:
        if fnmatch.fnmatch(rel_path, pat):
            return True
        if '/' + pat.replace('*', '') in rel_path:
            return True
    return False


def _parse_frontmatter(content: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    meta: dict[str, str] = {}
    for line in m.group(1).split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip().lower()] = val.strip().strip('"').strip("'")
    return meta


def _normalise_link(link: str) -> str:
    """Normalise a wikilink for comparison."""
    # Remove file extension
    link = re.sub(r'\.md$', '', link, flags=re.IGNORECASE)
    # Normalise whitespace
    link = re.sub(r'\s+', ' ', link).strip()
    return link.lower()


def scan(root: str, max_files: int | None = None) -> Vault:
    """Scan a vault directory and build the link graph.

    Args:
        root: Path to vault directory
        max_files: Optional limit for testing (speeds up dev)
    """
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Vault path does not exist: {root_path}")

    vault = Vault(root=str(root_path))

    # Phase 1: collect all markdown files
    collected = 0
    for file_path in root_path.rglob('*.md'):
        rel = str(file_path.relative_to(root_path))
        if _should_skip(rel):
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        rel_normalised = rel.replace('\\', '/')

        vf = VaultFile(
            path=str(file_path),
            relative_path=rel_normalised,
            content=content,
            frontmatter=_parse_frontmatter(content),
            word_count=len(content.split()),
            line_count=content.count('\n') + 1,
            mtime=file_path.stat().st_mtime,
        )

        # Extract wikilinks
        for m in WIKILINK_RE.finditer(content):
            link = m.group(1).strip()
            if link not in vf.wikilinks:
                vf.wikilinks.append(link)

        vault.files[rel_normalised] = vf
        collected += 1
        if max_files and collected >= max_files:
            break

    vault.total_files = len(vault.files)

    # Phase 2: build O(1) lookup maps
    # Map: stem.lower() -> list of relative paths
    stem_map: dict[str, list[str]] = {}
    # Map: alias.lower() -> list of relative paths
    alias_map: dict[str, list[str]] = {}
    # Map: stem without spaces/dashes -> list of relative paths (fuzzy)
    fuzzy_map: dict[str, list[str]] = {}

    for rel_path, vf in vault.files.items():
        stem = Path(rel_path).stem
        stem_lower = stem.lower()
        stem_map.setdefault(stem_lower, []).append(rel_path)

        # Fuzzy key: remove spaces and hyphens for approximate matching
        fuzzy_key = re.sub(r'[\s\-_]', '', stem_lower)
        fuzzy_map.setdefault(fuzzy_key, []).append(rel_path)

        # Collect aliases from frontmatter
        aliases_raw = vf.frontmatter.get('aliases', '')
        if aliases_raw:
            for alias_line in aliases_raw.split('\n'):
                alias = alias_line.strip().strip('-').strip('"').strip("'").strip()
                if alias:
                    alias_lower = alias.lower()
                    alias_map.setdefault(alias_lower, []).append(rel_path)

    # Phase 3: resolve wikilinks using O(1) lookup
    for rel_path, vf in vault.files.items():
        for link in vf.wikilinks:
            link_normalised = _normalise_link(link)

            # 1. Direct stem match
            if link_normalised in stem_map:
                for tgt in stem_map[link_normalised]:
                    tgt_vf = vault.files.get(tgt)
                    if tgt_vf and rel_path not in tgt_vf.inbound_links:
                        tgt_vf.inbound_links.append(rel_path)
                continue

            # 2. Alias match
            if link_normalised in alias_map:
                for tgt in alias_map[link_normalised]:
                    tgt_vf = vault.files.get(tgt)
                    if tgt_vf and rel_path not in tgt_vf.inbound_links:
                        tgt_vf.inbound_links.append(rel_path)
                continue

            # 3. Fuzzy match (without spaces/dashes)
            fuzzy_key = re.sub(r'[\s\-_]', '', link_normalised)
            if fuzzy_key in fuzzy_map:
                for tgt in fuzzy_map[fuzzy_key]:
                    tgt_vf = vault.files.get(tgt)
                    if tgt_vf and rel_path not in tgt_vf.inbound_links:
                        tgt_vf.inbound_links.append(rel_path)
                continue

            # 4. Substring fuzzy match (link is substring of stem, or vice versa)
            matched = False
            for stem_lower, tgts in stem_map.items():
                if link_normalised in stem_lower or stem_lower in link_normalised:
                    for tgt in tgts:
                        tgt_vf = vault.files.get(tgt)
                        if tgt_vf and rel_path not in tgt_vf.inbound_links:
                            tgt_vf.inbound_links.append(rel_path)
                    matched = True
                    break

            if not matched:
                # Check aliases with substring
                for alias_lower, tgts in alias_map.items():
                    if link_normalised in alias_lower or alias_lower in link_normalised:
                        for tgt in tgts:
                            tgt_vf = vault.files.get(tgt)
                            if tgt_vf and rel_path not in tgt_vf.inbound_links:
                                tgt_vf.inbound_links.append(rel_path)
                        matched = True
                        break

            if not matched:
                vault.broken_links += 1
                vf.broken_links.append(link)

    vault.total_wikilinks = sum(len(vf.wikilinks) for vf in vault.files.values())

    return vault
