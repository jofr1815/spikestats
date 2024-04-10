from sys import argv
from glom import glom
import pandas as pd
import argparse


class Set:
    def __init__(self, setname, season, wonSet, wonMatch, teamName, opponent):
        self.setname = setname
        self.teamName = teamName
        self.opponent = opponent
        self.season = season
        self.wonSet = wonSet
        self.wonMatch = wonMatch
        self.serveErr = 0
        self.setErr = 0
        self.attackErr = 0
        self.freeballErr = 0
        self.ace = 0
        self.kill = 0
        self.stuffBlock = 0
        self.unforcedErrs = 0
        self.earnedPts = 0

    def export(self):
        return(f"\n{self.setname},{self.teamName},{self.opponent},{self.season},{self.wonSet},{self.wonMatch},{self.unforcedErrs},{self.earnedPts},{self.serveErr},{self.setErr},{self.attackErr},{self.freeballErr},{self.ace},{self.kill},{self.stuffBlock}")

colNames = "setname,teamName,opponent,season,wonSet,wonMatch,unforcedErrs,earnedPts,serveErr,setErr,attackErr,freeballErr,ace,kill,stuffBlock"

def fixSeasonName(season):
    if "CU" in season:
        season = season.split(" ")[-1]
    return season

def processSets(df, cuPerspect = True):

    init_length = len(df)

    if cuPerspect == True:
        df = df.loc[
        (df["team"] == "CU")]
    else:
        df = df.loc[
            (df["team"]!= "CU")
        ]

    sets = dict()
    df = df.loc[
        (((df["evaluation_code"] == "=") & (df["skill"].isin(["Serve", "Set", "Attack", "Freeball"]))) |
        ((df["evaluation_code"] == "#") & (df["skill"].isin(["Serve", "Attack", "Block"]))))
        ]
    
    filtered_len = len(df)
    print(f"Filtered out {filtered_len} plays from a total of {init_length} ({100*filtered_len/init_length:.2f}%)")

    for i in range(len(df)):
        currRow = df.iloc[i]
        if currRow["match_set"] not in sets:
            sets[currRow["match_set"]] = Set(currRow["match_set"], fixSeasonName(currRow["season"]), currRow["won_set"], currRow["won_match"], currRow["team"], currRow["opponent"])
        if currRow["evaluation_code"] == "=":
            sets[currRow["match_set"]].unforcedErrs += 1
            match currRow["skill"]:
                case "Serve":
                    sets[currRow["match_set"]].serveErr += 1
                case "Set":
                    sets[currRow["match_set"]].setErr += 1
                case "Attack":
                    sets[currRow["match_set"]].attackErr += 1
                case "Freeball":
                    sets[currRow["match_set"]].freeballErr += 1

        elif currRow["evaluation_code"] == "#":
            sets[currRow["match_set"]].earnedPts += 1
            match currRow["skill"]:
                case "Serve":
                    sets[currRow["match_set"]].ace += 1
                case "Attack":
                    sets[currRow["match_set"]].kill += 1
                case "Block":
                    sets[currRow["match_set"]].stuffBlock += 1

    print(f"Collected {len(sets)} total sets")

    if cuPerspect == True:
        f = open(f"{argv[1][:-4]}_processed.csv", "+w")
    else:
        f = open(f"{argv[1][:-4]}_opp.csv", "+w")
    f.write(colNames)
    for i in sets:
        f.write(sets[i].export())
    f.write("\n")

df = pd.read_csv(argv[1], low_memory=False)
processSets(df, True)
processSets(df, False)