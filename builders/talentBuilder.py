
import os
import re

rgx = r'(?!#### .*)(\*.*?)(?=\n<br>)'

rgx2 = r'(?!#### )(\w.*)(?=\n\*)'

talents = open("../AlariaWiki/Noncombat Talents.md").read()

if __name__ == '__main__':

    talentText = re.findall(rgx, talents, flags=re.MULTILINE | re.DOTALL)
    talentNames = re.findall(rgx2, talents)
    print(talentNames)
    print(len(talentText))
    
    for name, text in zip(talentNames, talentText):
        with open(f"../AlariaWiki/talents/{name}.md", "w+") as f:
            f.write(text)
