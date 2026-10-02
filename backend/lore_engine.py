"""Deterministic HYPEBLOCK lore enrichment.

Adds narrative depth without changing the existing core traits or rarity tier.
Values are deterministic from token identity so metadata stays stable.
"""
from __future__ import annotations
import hashlib

FACTIONS=("Neon Graves","Gutter Saints","Static Syndicate","Toxic Choir","Chrome Vandals","Riot Kin","Void Runners","Acid Court")
ORIGINS=("Block Zero","Underrail","Dead Mall","Acid District","Signal Alley","Chrome Yard","The Spill","Night Market")
TEMPERAMENTS=("Defiant","Mischievous","Unhinged","Cold","Restless","Cunning","Reckless","Watchful")
MUTATIONS=("None","Static Veins","Acid Blood","Ghost Signal","Chrome Bone","Void Scar","Neon Fever","Grime Bloom")
AURAS=("Low Voltage","Toxic Mist","Hot Static","Cold Neon","Riot Glow","Dead Air","Acid Halo","Black Signal")
RELICS=("None","Broken Pager","Subway Token","Burned Cassette","Chrome Tooth","Tagged Key","Bootleg Chip","Lucky Bolt")
ERAS=("Genesis Night","Afterglow","Blackout","Spill Era")
ABILITIES=("Signal Jam","Street Luck","Acid Rush","Ghost Step","Crowd Riot","Static Bite","Neon Sight","Grime Shield")

def _pick(token_id,name,label,values):
    raw=f"hypeblock:{token_id}:{name}:{label}".encode()
    n=int(hashlib.sha256(raw).hexdigest()[:16],16)
    return values[n%len(values)]

def lore_for(item):
    tid=item["token_id"]; name=item["name"]
    return {
      "Faction":_pick(tid,name,"faction",FACTIONS),
      "Origin":_pick(tid,name,"origin",ORIGINS),
      "Temperament":_pick(tid,name,"temperament",TEMPERAMENTS),
      "Mutation":_pick(tid,name,"mutation",MUTATIONS),
      "Aura":_pick(tid,name,"aura",AURAS),
      "Relic":_pick(tid,name,"relic",RELICS),
      "Era":_pick(tid,name,"era",ERAS),
      "Signature Ability":_pick(tid,name,"ability",ABILITIES),
    }

def short_lore(item):
    x=lore_for(item)
    return f"{item['name']} came out of {x['Origin']} with the {x['Faction']}. {x['Temperament']} by nature, carrying {x['Relic']} through the {x['Era']}. Signature: {x['Signature Ability']}."
