"""Config loader for judgment-loop.

One config file = one judgment instance: a person's graph (the typed value/framework
nodes) plus the corpus those nodes are mined from. TOML, stdlib-only (tomllib, 3.11+).

Everything the original engine hardcoded — vault layout, frontmatter keys, the body
field labels, the baseline tag, the corpus sources — lives here as config with sensible
defaults, so the same code runs against any content layout. Engines read their own
section off `cfg.raw` and resolve paths via `cfg.resolve(...)`.
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass

# Defaults match the schema the engine grew up on; override per-instance in TOML.
DEFAULT_FM = {
    "id": "id",
    "name": "name",
    "type": "type",
    "applies_to": "applies-to",
    "embodies": "embodies",
}
DEFAULT_BODY = {
    "statement": "Statement",
    "procedure": "Procedure",
    "rules": "Rules that serve it",
    "operationalized": "Operationalized by",
}
DEFAULT_BASELINE_TAG = "baseline"
DEFAULT_GRAPH_DIR = "09 Rules/_judgment"


@dataclass
class GraphCfg:
    dir: str                 # directory of node .md files, relative to root
    fm: dict                 # frontmatter key map (logical name -> actual key)
    body: dict               # body field-label map (logical name -> actual bold label)
    baseline_tag: str        # applies-to tag marking an always-on (floor) lens


@dataclass
class Config:
    root: str                # absolute path relative dirs are resolved against
    graph: GraphCfg
    lens_cap: int
    config_path: str
    raw: dict                # full parsed TOML — engines read their own section

    @property
    def judgment_dir(self) -> str:
        return os.path.join(self.root, self.graph.dir)

    def resolve(self, rel: str) -> str:
        """Resolve a config-relative path against the instance root."""
        return rel if os.path.isabs(rel) else os.path.join(self.root, rel)

    def section(self, name: str) -> dict:
        return self.raw.get(name) or {}


def load(path: str) -> Config:
    """Load and resolve a config. Relative `paths.root` resolves against the config
    file's own directory, so a config can sit next to the content it describes."""
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    cfg_dir = os.path.dirname(os.path.abspath(path))
    root = (raw.get("paths") or {}).get("root", ".")
    if not os.path.isabs(root):
        root = os.path.normpath(os.path.join(cfg_dir, root))

    g = raw.get("graph") or {}
    graph = GraphCfg(
        dir=g.get("dir", DEFAULT_GRAPH_DIR),
        fm={**DEFAULT_FM, **(g.get("frontmatter") or {})},
        body={**DEFAULT_BODY, **(g.get("body") or {})},
        baseline_tag=(g.get("tags") or {}).get("baseline", DEFAULT_BASELINE_TAG),
    )
    lens_cap = int((raw.get("lens") or {}).get("cap", 4))
    return Config(root=root, graph=graph, lens_cap=lens_cap,
                  config_path=os.path.abspath(path), raw=raw)
