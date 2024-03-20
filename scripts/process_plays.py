from sys import argv
import pandas as pd


df = pd.read_csv(argv[1], low_memory=False)
init_length = len(df)

df = df.loc[
    (df["team"] == "CU") &
    ((df["evaluation_code"] == "=") |
    ((df["evaluation_code"] == "#") & (df["skill"].isin(["Serve", "Attack", "Block"]))))
]

filtered_len = len(df)

print(f"Filtered out {filtered_len} plays from a total of {init_length} ({100*filtered_len/init_length:.2f}%)")

sets = dict()

class Set:
    def __init__(self, setname, season, wonSet, wonMatch, opponent):
        self.setname = setname
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
        return(f"\n{self.setname},{self.opponent},{self.season},{self.wonSet},{self.wonMatch},{self.unforcedErrs},{self.earnedPts},{self.serveErr},{self.setErr},{self.attackErr},{self.freeballErr},{self.ace},{self.kill},{self.stuffBlock}")

colNames = "setname,opponent,season,wonSet,wonMatch,unforcedErrs,earnedPts,serveErr,setErr,attackErr,freeballErr,ace,kill,stuffBlock"

def fixSeasonName(season):
    if "CU" in season:
        season = season.split(" ")[-1]
    return season

for i in range(len(df)):
    currRow = df.iloc[i]
    if currRow["match_set"] not in sets:
        sets[currRow["match_set"]] = Set(currRow["match_set"], fixSeasonName(currRow["season"]), currRow["won_set"], currRow["won_match"], currRow["opp_team_mw"])
    if currRow["evaluation_code"] == "=":
        match currRow["skill"]:
            case "Serve":
                sets[currRow["match_set"]].serveErr += 1
                sets[currRow["match_set"]].unforcedErrs += 1
            case "Set":
                sets[currRow["match_set"]].setErr += 1
                sets[currRow["match_set"]].unforcedErrs += 1
            case "Attack":
                sets[currRow["match_set"]].attackErr += 1
                sets[currRow["match_set"]].unforcedErrs += 1
            case "Freeball":
                sets[currRow["match_set"]].freeballErr += 1
                sets[currRow["match_set"]].unforcedErrs += 1

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

with open(f"{argv[1][:-4]}_processed.csv", "w") as f:
    f.write(colNames)
    for set in sets:
        f.write(sets[set].export())
    f.write("\n")