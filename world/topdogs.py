from evennia.utils import evtable
from evennia.utils import dbref_to_obj

def scorelist():

    from typeclasses.objects import Bones
    bones = Bones.objects.all()
    scores = {}
    for bone in bones:
        if bone.db.buried:
            scores.update({bone.locks.get("control"): scores.get(bone.locks.get("control"),0)+bone.db.value})


    players=[]
    bones=[]


    l = list(scores.items())
    l.sort(reverse=True)

    for k,v in l[:10]:
        import re
        from evennia import ObjectDB
        match = re.search(r"control:pid\((#\d*)\)",k)
        players.append(dbref_to_obj(match[1],ObjectDB).key)
        bones.append(v)

    heading = "|/$pad($alt(Top Dogs,|401|132|540|054)|n,106,c,!)|/"
    table = evtable.EvTable("|401Player|n","|401Score|n", table=[players,bones], border="cells")
    table.reformat_column(0,width=60)
    table.reformat_column(1,width=10)
    return heading + str(table)

