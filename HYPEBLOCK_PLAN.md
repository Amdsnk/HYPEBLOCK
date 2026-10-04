# HYPEBLOCK — Current implementation and release plan

The Genesis manifest is authoritative: 296 token records, eight core trait categories, five rarity tiers, with the existing Grim characters, levels and batches preserved.

## Implemented

React gallery, search/filter/sort/pagination, NFT details, rarity engine, trait lab, lore and perks, waitlist, private admin, metadata and wallpaper exports. FastAPI uses an atomic JSON store; MongoDB and Emergent are not required for the deployed website. The root Dockerfile builds React and serves it through FastAPI, with Railway health checks and persistent storage instructions in `deploy/RAILWAY.md`.

## Audit findings

296 unique IDs, names and core trait signatures. 193 token image files have no exact binary duplicates. 103 tokens still use fallback previews. Distinct metadata, URLs and hashes are not evidence of visually unique final artwork or matching traits. Do not announce all 296 as mint-ready.

## Remaining launch work

1. Curate the 193 image files and supplied originals against their character metadata; review visual duplicates, quality and style consistency.
2. Create and approve final original artwork for missing tokens. Preserve token identity rather than relabeling an unrelated image.
3. Freeze token metadata and pin final images and per-token metadata to immutable content-addressed storage.
4. Confirm network, actual collection/contract, royalties and sale configuration with the creator wallet. Wallet signatures are performed by the owner.
5. Replace unverified social and marketplace links with owned, confirmed URLs.
6. Publish the website, verify volume persistence, then run a small reviewed release before opening the remaining collection.

Prices in the dataset are proposed asking prices, not market valuations or promised returns. Marketing success cannot be guaranteed by the software.
