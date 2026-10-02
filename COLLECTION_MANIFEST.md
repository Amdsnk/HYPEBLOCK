# HYPEBLOCK — Genesis Collection Manifest

## Canon

HYPEBLOCK Genesis is a grim character collectible universe. The existing visual language, named characters, trait hierarchy, rarity tiers and level/batch mechanics are canon and should be evolved rather than replaced.

The current dataset contains **296 Genesis tokens**. Supply must not be increased merely to create volume. New tokens should enter Genesis only when they add a genuinely new character, trait expression, narrative role, or exceptional 1/1 artwork.

## Non-negotiable asset rules

1. One token ID = one canonical artwork identity.
2. Exact duplicate images are prohibited, regardless of filename.
3. A recolor/crop/overlay of another token is not considered final unique artwork.
4. Uploaded original artwork takes precedence over procedural placeholder art.
5. Every final artwork must agree with its metadata traits.
6. Token IDs and final metadata should be frozen before minting.
7. SHA-256 hashes of final artwork should be recorded before publishing metadata/IPFS assets.

Run `python backend/audit_collection.py` before every collection release.

## Trait architecture

Core marketplace traits remain compatible with the current app:

- Gender / archetype
- Skin
- Eyes
- Headwear
- Mouth
- Outfit
- Background
- Accessory

The collection can grow richer without breaking these filters by adding optional lore traits to metadata:

- Faction
- Origin
- Temperament
- Mutation
- Aura
- Relic
- Marking
- Environment
- Era
- Signature Ability

These extra traits should be curated, not randomly attached for artificial rarity.

## Rarity hierarchy

Keep the established hierarchy:

- Common
- Rare
- Epic
- Legendary
- Mythic

Mythic should be reserved for crown-jewel characters and intentional 1/1 or near-1/1 trait combinations. Rarity should derive from actual trait distribution plus curated exceptional status; it must not be presented as a promise of financial value.

## Artwork states

Each token should eventually have one of these explicit states:

- `canonical` — final original artwork, approved for mint
- `candidate` — unique artwork under metadata/trait review
- `placeholder` — deterministic web preview only; not mint-ready

The existing `/api/render/{token_id}` fallback is useful for complete website coverage, but placeholder renders are not canonical mint assets.

## Recommended release model

Keep Genesis finite at 296 while artwork reconciliation is underway. Use batch unlocks for storytelling and discovery rather than creating artificial scarcity. Future expansion should be a separately named collection/season so Genesis provenance stays understandable.

## Mint-readiness gate

A release is mint-ready only when:

- no duplicate token IDs or names exist;
- no duplicate core trait signatures exist unless intentionally documented;
- no exact duplicate binary artwork exists;
- every released token has canonical artwork;
- artwork and metadata have been manually spot-checked;
- metadata image URIs are immutable/content-addressed;
- contract/network/royalty settings are reviewed separately;
- collection claims avoid guaranteed resale, appreciation, or investment-return language.
