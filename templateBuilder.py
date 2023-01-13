import json
import os
import re

WIKI = "wiki"

from config import WikmdConfig

cfg = WikmdConfig()

def build(filename, template):
    with open(filename, "w") as f:
        with open(template) as t:
            f.write(t.read())

def repair(filename, template):
    pass

if __name__ == '__main__':
    for filename in os.listdir(cfg.wiki_directory):
        path = os.path.join(cfg.wiki_directory, filename)
        if (".DS_Store" in path) or ("img" in path) or (".git" in path): continue
        # build(path, "wikitemplates/stateTemplate.md")
    name = "state_ex"
    build(f"wiki/{name}.md", "wikitemplates/stateTemplate.md")