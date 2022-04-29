import os
import shutil
from os import makedirs, path
from pathlib import Path
from typing import Any, Dict, List

import frontmatter

from .settings import stg, wr_stg
from .utils import ddir, stg

YML = stg(None, "dev.yml")

DOCS = ddir(YML, "docs")
RULES = ddir(YML, "rules")
IDF = Path(f'./{ddir(YML, "docs/input")}')
MD_VARS_YML = ddir(YML, "md_vars")
RMVC = ddir(MD_VARS_YML, "global")

DGD = []
DGF = []

GEN = {
    "docs": [DGD, DGF],
}

class Constants:
    pass

def dd(od: Dict[str, List[str]], *dicts: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    for d in dicts:
        for a, v in d.items():
            od[a] = [*(od.get(a, []) or []), *v]
    return od

def rules_fn(rules: Dict[Any, Any]) -> Dict[str, List[str]]:
    return dd({"": ddir(rules, "del", [])}, ddir(rules, "repl"))

def repl(s: str, repl_dict: Dict[str, List[str]]) -> str:
    op = s
    for k, v in repl_dict.items():
        for i in v:
            op = op.replace(i, k)
    return op

def inmd(p: str, type: str):
    """
    "If Not `path.isdir`, Make Directories"

    Args:
        p (str): [description]
    """

    pd = path.dirname(p)
    if not path.isdir(pd):
        GEN[type][0].append(pd)
        makedirs(pd)
    return p

def del_gen():
    try:
        for _, v in stg("generated", "docs/_meta.yml").items():
            for i in v["folders"]:
                if path.isdir(i):
                    shutil.rmtree(i)
            for i in v["files"]:
                if path.isfile(i):
                    os.remove(i)
    except TypeError:
        shutil.copy("docs/_meta.yml.bak", "docs/_meta.yml")
        del_gen()

def main(rmv: Dict[Any, Any]={}):
    docs_pdir = DOCS["op"]
    rmv_r = ddir(rmv, "rules")
    rmv_mv = ddir(rmv, "md_vars")
    MVC = dict(RMVC, **ddir(rmv_mv, "global"))

    del_gen()

    for rip in list(IDF.rglob("*.ymd")):
        out = path.join(
            docs_pdir,
            *rip.parts[1:-1],
            f"{rip.stem}.md"
        )
        print(out)
        GEN["docs"][1].append(out)

        rf = frontmatter.load(rip)
        md = repl(rf.content, dd(rules_fn(RULES), rules_fn(rmv_r)))

        d = dict(
            MVC,
            **ddir(
                MD_VARS_YML,
                f"local/{rip.stem}"
            ),
            **ddir(
                rmv_mv,
                f"local/{rip.stem}"
            )
        )
        for k, v in d.items():
            md = md.replace(f"${{{k}}}", v)

        if title:=rf.get("title"):
            if link:=rf.get("link"):
                md = """<h1 align="center" style="font-weight: bold">
    <a target="_blank" href="{}">{}</a>
</h1>\n\n{}\n""".format(link, title, md)
            else:
                md = """<h1 align="center" style="font-weight: bold">
    {}
</h1>\n\n{}\n""".format(title, md)

        with open(inmd(out, "docs"), "w") as f:
            f.write(md)

    shutil.copy("docs/_meta.yml", "docs/_meta.yml.bak")
    for k, v in GEN.items():
        for key, i in zip(["folders", "files"], v):
            wr_stg(f"generated/{k}/{key}", list(set(i)), "docs/_meta.yml")