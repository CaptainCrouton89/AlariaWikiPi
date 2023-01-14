import templateBuilder
import os

WIKI = "wiki"
WIKI_DATA = "wikidata"

from config import WikmdConfig

cfg = WikmdConfig()

if __name__ == '__main__':
    wiki_files = set()
    all_states = set()
    all_races = set()
    all_subraces = set()

    with open(os.path.join(WIKI_DATA, "states.txt")) as f:
        for line in f.readlines():
            all_states.add(line.strip())

    with open(os.path.join(WIKI_DATA, "races.txt")) as f:
        for line in f.readlines():
            all_races.add(line.strip())

    with open(os.path.join(WIKI_DATA, "subraces.txt")) as f:
        for line in f.readlines():
            all_subraces.add(line.strip())

    for filename in os.listdir(cfg.wiki_directory):
        path = os.path.join(cfg.wiki_directory, filename)
        if (".DS_Store" in path) or ("img" in path) or (".git" in path): continue
        wiki_files.add(filename.replace(".md", ""))
    
    for state in all_states:
        if state not in wiki_files:
            print("making state", state)
            templateBuilder.build(f"wiki/{state}.md", "wikitemplates/stateTemplate.md")
    for race in all_races:
        if race not in wiki_files:
            print("making race", race)
            templateBuilder.build(f"wiki/{race}.md", "wikitemplates/raceTemplate.md")
    for subrace in all_subraces:
        if subrace not in wiki_files:
            print("making subrace", subrace)
            templateBuilder.build(f"wiki/{subrace}.md", "wikitemplates/subraceTemplate.md")