import json, urllib.request

url = "https://docs.google.com/spreadsheets/d/1SSsxWmE8Oz35D6MvLheFNUfhWerHNkUGOGtjxLlrTuA/gviz/tq?tqx=out:json&gid=1249626217"

# A complete backup of the raw sheet, so the site can be rebuilt even if the
# Google Sheet ever disappears. Each successful fetch refreshes it; if the sheet
# is unreachable we transparently fall back to the last saved copy. Git history
# keeps every past version as a dated archive.
BACKUP = "sheet_backup.json"
try:
    t = urllib.request.urlopen(url, timeout=30).read().decode()
    j = json.loads(t[t.index("{"):t.rindex("}")+1])
    json.dump(j, open(BACKUP, "w"), separators=(",", ":"))
    print("fetched live sheet; refreshed", BACKUP)
except Exception as e:
    print("live fetch failed (%s) -> falling back to %s" % (e, BACKUP))
    j = json.load(open(BACKUP))
rows = j["table"]["rows"]

def C(c):
    if not c: return ""
    if c.get("f") is not None: return str(c["f"])
    return "" if c.get("v") is None else str(c["v"])

def num(x):
    x=(x or "").strip()
    if x=="" : return 0
    try:
        f=float(x); return int(f) if f==int(f) else f
    except: return x

def yn(x):
    x=(x or "").strip(); return x if x else "No"

MAST={"WB":"Warbird","Dread":"Dreadnought"}
def mast(x):
    return " ".join(MAST.get(w,w) for w in (x or "").split())

CAREER_CODE={"Uni":0,"Tac":1,"Eng":2,"Sci":3}
SPEC_CODE={"":0,"Int":4,"Cmd":5,"Pil":6,"Tmp":7,"MW":8}

def transform(r):
    v=[C(c) for c in r["c"]]
    def g(i): return v[i] if i<len(v) else ""
    boff=[(47,48,49),(50,51,52),(53,54,55),(56,57,58),(59,60,61),(62,63,64)]
    seats=[]; stations=0; abil=0; seatData=[]
    for cnt,car,spc in boff:
        c=g(cnt).strip()
        if c=="" : continue
        career=g(car).strip(); spec=g(spc).strip(); stations+=1
        try: abil+=int(float(c))
        except: pass
        seats.append(f"{c} {career}"+(f"/{spec}" if spec else ""))
        seatData.append([int(float(c)), CAREER_CODE.get(career,0), SPEC_CODE.get(spec,0)])
    tcon,econ,scon,ucon=num(g(73)),num(g(74)),num(g(75)),num(g(76))
    def n(*xs):
        tot=0
        for x in xs:
            try: tot+=int(float(x))
            except: pass
        return tot
    m=[None]*66
    m[0]=0; m[1]=g(2); m[2]=g(3); m[3]=num(g(4)); m[4]=num(g(5))
    m[5]=g(6); m[6]=g(7); m[7]=g(8) or "(None)"; m[8]=g(9) or "(None)"
    m[9]=g(10); m[10]=g(11); m[11]=g(12) or "(None)"; m[12]=mast(g(13))
    m[13]=num(g(16)); m[14]=num(g(17)); m[15]=num(g(18)); m[16]=num(g(19))
    m[17]=num(g(20)); m[18]=num(g(21)); m[19]=num(g(22)); m[20]=num(g(23)); m[21]=num(g(24))
    m[22]=num(g(37)); m[23]=num(g(39)); m[24]=num(g(40)); m[25]=num(g(41)); m[26]=num(g(42))
    m[27]=num(g(43)); m[28]=num(g(44)); m[29]=num(g(45)); m[30]=num(g(46))
    m[31]=num(g(65)); m[32]=num(g(66)); m[33]=num(g(67))
    m[34]=yn(g(68)); m[35]=yn(g(69)); m[36]=num(g(70)); m[37]=num(g(71)); m[38]=yn(g(72))
    m[39]=tcon; m[40]=econ; m[41]=scon; m[42]=ucon; m[43]=n(tcon,econ,scon,ucon)
    m[44]=yn(g(77)); m[45]=yn(g(78)); m[46]=yn(g(79)); m[47]=yn(g(80))
    m[48]=yn(g(81)); m[49]=yn(g(82)); m[50]=yn(g(83)); m[51]=yn(g(84)); m[52]=yn(g(85))
    m[53]=yn(g(86)); m[54]=yn(g(87)); m[55]=yn(g(88))
    m[56]=g(89) or "(None)"; m[57]=g(90) or "(None)"; m[58]=g(91) or "(None)"
    m[59]=g(113).strip(); m[60]=g(115).strip(); m[61]=g(117).strip()
    m[62]=stations; m[63]=abil; m[64]=", ".join(seats); m[65]=seatData
    return m

CAREER_NAME={0:"Uni",1:"Tac",2:"Eng",3:"Sci"}
SPEC_NAME={0:"",4:"Int",5:"Cmd",6:"Pil",7:"Tmp",8:"MW"}

# career display priority for re-sorting split-ship seats: Uni, Tac, Sci, Eng
CAREER_PRI={0:0,1:1,3:2,2:3}
def seats_string(seats):
    order=sorted(range(len(seats)),
                 key=lambda i:(-seats[i][0], CAREER_PRI.get(seats[i][1],9),
                               0 if seats[i][2] else 1, i))
    out=[]
    for i in order:
        rank,car,spc=seats[i]
        out.append(f"{rank} {CAREER_NAME[car]}"+(f"/{SPEC_NAME[spc]}" if spc else ""))
    return ", ".join(out)

def split_science_destroyer(m):
    """Science Destroyers list both rank-4 Tac and Sci seats (combined view).
       Each mode keeps one at rank 4 and demotes the other to rank 3."""
    base=m[65]
    tac_seats=[i for i,s in enumerate(base) if s[1]==1]
    sci_seats=[i for i,s in enumerate(base) if s[1]==3]
    tac_idx=max(tac_seats, key=lambda i:base[i][0]) if tac_seats else None
    sci_idx=max(sci_seats, key=lambda i:base[i][0]) if sci_seats else None
    results=[]
    for mode in ("Science","Tactical"):
        mm=list(m)
        seats=[list(s) for s in base]
        demoted=None
        if mode=="Science" and tac_idx is not None:
            seats[tac_idx][0]-=1; demoted=tac_idx
        elif mode=="Tactical" and sci_idx is not None:
            seats[sci_idx][0]-=1; demoted=sci_idx
        mm[1]=m[1]+(" (Science Mode)" if mode=="Science" else " (Tactical Mode)")
        mm[65]=seats
        def mx(pred):
            r=[s[0] for s in seats if pred(s)]
            return max(r) if r else 0
        mm[13]=mx(lambda s:s[1]==1); mm[14]=mx(lambda s:s[1]==2)
        mm[15]=mx(lambda s:s[1]==3); mm[16]=mx(lambda s:s[1]==0)
        mm[17]=mx(lambda s:s[2]==4); mm[18]=mx(lambda s:s[2]==5)
        mm[19]=mx(lambda s:s[2]==6); mm[20]=mx(lambda s:s[2]==7); mm[21]=mx(lambda s:s[2]==8)
        if mode=="Science":
            mm[35]="No"; mm[48]="Yes"; mm[49]="Yes"; mm[50]="Yes"
        else:
            mm[35]="Yes"; mm[48]="No"; mm[49]="No"; mm[50]="No"
        mm[62]=len(seats); mm[63]=sum(s[0] for s in seats)
        mm[64]=seats_string(seats)
        results.append(mm)
    return results

out=[]
for r in rows:
    v=[C(c) for c in r["c"]]
    if len(v)<=98 or v[98].strip().upper()!="TRUE": continue
    out.append(transform(r))
# split Science Destroyers (Tac/Sci Modes flag at model idx 51) into two entries each
expanded=[]
for m in out:
    if m[51]=="Yes": expanded.extend(split_science_destroyer(m))
    else: expanded.append(m)
out=expanded
out.sort(key=lambda m:m[1].lower())
for i,m in enumerate(out): m[0]=i

# numeric-vs-string per model idx (over displayed attribute idxs)
CAT=[("Release Date",2),("Year",3),
("Original Source",5),("Source",6),("Bundle",7),("Starter Bundle",8),("Faction",9),
("Origin",10),("Family",11),("Mastery Package",12),("Max Tactical Seat",13),
("Max Engineering Seat",14),("Max Science Seat",15),("Max Universal Seat",16),
("Max Intelligence Seat",17),("Max Command Seat",18),("Max Pilot Seat",19),
("Max Temporal Seat",20),("Max Miracle Worker Seat",21),("Total BOff Stations",62),
("Total BOff Abilities",63),("Hull Modifier",22),("Shield Modifier",23),("Turn Rate",24),
("Impulse Modifier",25),("Inertia Rating",26),("Bonus Weapons Power",27),
("Bonus Shield Power",28),("Bonus Engine Power",29),("Bonus Auxilliary Power",30),
("Fore + Aft Weapons",31),("Fore Weapons",32),("Aft Weapons",33),("Equip Dual Cannons",34),
("Exp Weapon Slot",35),("Hangar Bays",36),("Devices",37),("Fleet Grade",38),
("Tactical Consoles",39),("Engineering Consoles",40),("Science Consoles",41),
("Universal Consoles",42),("Total Consoles",43),("CC: Weapon Syst. Eff.",44),
("CC: Shield Freq. Mod.",45),("CC: Strat. Maneuvering",46),("CC: Attract Fire",47),
("Secondary Deflector",48),("Subsytem Targeting",49),("Sensor Analysis",50),
("Tac/Sci Modes",51),("Singularity",52),("Cloak",53),("Flanking",54),("Wingmen",55),
("Trait",56),("Console",58)]

def is_num(idx):
    for m in out:
        val=m[idx]
        if val in ("", None): continue
        if isinstance(val,(int,float)): continue
        s=str(val).strip()
        try: float(s)
        except: return False
    return True

catalog=[{"label":lab,"idx":idx,"numeric":is_num(idx)} for lab,idx in CAT]
# release date (idx 2) is a date string -> chronological sort, not numeric/lexical
for c in catalog:
    if c["idx"]==2: c["numeric"]=False; c["type"]="date"

json.dump({"seed":out,"catalog":catalog}, open("appdata.json","w"), separators=(",",":"))
print("ships:",len(out))
print("numeric attrs:",sum(1 for c in catalog if c["numeric"]),"/",len(catalog))
import os; print("appdata.json bytes:",os.path.getsize("appdata.json"))
print("sample ship:",json.dumps(out[0]))
