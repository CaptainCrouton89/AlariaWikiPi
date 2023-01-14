from importlib.machinery import all_suffixes
import json
import os
import re

TAGS = "./tagLookup.json"
WIKI = "wiki"
LINK_TEXT = "Links: "
TAGS_TEXT = "Tags: "
WIKI_DATA = "wikidata"

LINK_PATTERN = "\[([\w\s\d]*)\]"

EOW = [",", ";", "!", ".", " ", "\n", "\t", "—"]

from config import WikmdConfig

cfg = WikmdConfig()

with open(TAGS) as f:
    tagLookUp = json.load(f)


def get_links(tagList):
    links = []
    for tag in tagList:
        links.append(f"[{tagLookUp[tag]}]({tagLookUp[tag]})")
    return ", ".join(links)

def auto_tag(filename):
    with open(filename) as f:
        fin = f.read()
    tags = re.finditer(TAGS_TEXT, fin)
    tagString = ""
    end_of_tags = 0
    for tag in tags:
        end_of_tags = tag.end()
        for char in fin[tag.end():]:
            if char != "\n":
                end_of_tags += 1
                tagString += char
            else: break
    if tagString == "": return # skip file if no tags

    tags = tagString.split(", ")
    
    links = re.finditer(LINK_TEXT, fin)
    linkString = ""
    start_of_links = 0
    end_of_links = 0
    for link in links:
        start_of_links = link.end()
        end_of_links = link.end()
        for char in fin[link.end():]:
            if char != "\n":
                end_of_links += 1
                linkString += char
            else: break
    if end_of_links == 0:
        fin = fin[:end_of_tags] + "\n\n" + LINK_TEXT + get_links(tags) + fin[end_of_tags:]
    else:
        fin = fin[:start_of_links] + get_links(tags) + fin[end_of_links:]    
    with open(filename, "w") as f:
        f.write(fin)

def auto_link(filename):
    with open(filename) as f:
        fin = f.read()
    doc_length = len(fin)
    links = re.finditer(LINK_PATTERN, fin)
    padding = 0
    for link in links:
        index = link.end() + padding
        if index == doc_length + padding:
            url = fin[link.start()+padding+1:index-1]
            fin = fin[:index] + "(" + url + ")" + fin[index:]
            padding += len(url) + 2
            break
        if fin[index] == '(': 
            continue
        else:
            url = fin[link.start()+padding+1:index-1]
            fin = fin[:index] + "(" + url + ")" + fin[index:]
            padding += len(url) + 2
                
    with open(filename, "w") as f:
        f.write(fin)

def get_md_file_paths(directory):
    md_paths = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            md_paths.append(os.path.join(root, name))
            print(name)
    return md_paths

def total_auto_link(filename, all_files):
    linkables = set()
    # data = ["states", "races", "subraces"]
    # for doc in data:
    #     with open(os.path.join(WIKI_DATA, f"{doc}.txt")) as f:
    #         for line in f.readlines():
    #             linkables.add(line.strip())

    # for root, dirs, files in os.walk(cfg.wiki_directory):



    for mdfile in all_files:
        # path = os.path.join(cfg.wiki_directory, mdfile)
        if (".DS_Store" in mdfile) or ("img" in mdfile) or (".git" in mdfile): continue
        linkables.add(mdfile.replace(".md", ""))

    with open(filename) as f:
        fin = f.read()

    flexnames_to_file = {}
    with open(os.path.join(WIKI_DATA, "autolink.json")) as f:
        file_to_flexnames = json.load(f)
    for md_file, flexnames in file_to_flexnames.items():
        for flexname in flexnames:
            flexnames_to_file[flexname] = md_file

    for linkable in linkables:
        padding = 0
        links = re.finditer(linkable, fin, re.IGNORECASE)
        for link in links:
            index = link.end() + padding
            try:
                if (fin[index] not in EOW):
                    continue
                if (fin[link.start()-1] not in EOW):
                    continue
                else:
                    url = fin[link.start()+padding:index]
                    insertion = f"[{url}]({linkable})"
                    fin = fin[:index-len(url)] + insertion + fin[index:]
                    padding += len(url) + 4
            except:
                pass

    for flexname in flexnames_to_file.keys():
        padding = 0
        links = re.finditer(flexname, fin, re.IGNORECASE)
        for link in links:
            index = link.end() + padding
            # start_index = link.start() + padding
            try:
                # if (fin[start_index-1] != " " or fin[start_index-1] != "\n"): continue
                if (fin[index] not in EOW):
                    continue
                if (fin[link.start()-1] not in EOW):
                    continue
                else:
                    match = fin[link.start()+padding:index]
                    match_length = len(match)
                    insertion = f"[{match}]({flexnames_to_file[flexname.lower()]})"
                    # print("insertion:", insertion)
                    fin = fin[:index-match_length] + insertion + fin[index:]
                    padding += len(insertion) - match_length
            except:
                pass

    with open(filename, "w") as f:
        f.write(fin)

def full_site_auto_link(all_files):
    for path in get_md_file_paths(cfg.wiki_directory):
        # path = os.path.join(cfg.wiki_directory, mdfile)
        if (".DS_Store" in path) or ("img" in path) or (".git" in path): continue
        auto_link(path)
        total_auto_link(path, all_files)                            

def main():
    # for filename in os.listdir(cfg.wiki_directory):
    #     path = os.path.join(cfg.wiki_directory, filename)
    #     if (".DS_Store" in path) or ("img" in path) or (".git" in path): continue
    #     pass
    total_auto_link("wiki/ztest.md")
    auto_link("wiki/ztest.md")

if __name__ == '__main__':
    main()