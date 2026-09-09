# HYPEBLOCK — Graffiti Gremlins (PRD)

## Original Problem Statement
Koleksi 200 PFP maskot "graffiti gremlin" original (Bold, edgy, streetwear, spray-paint neon). Format PFP + trait + rarity, maskot 100% original. Situs showcase (React + FastAPI + MongoDB) + listing di Rarible (Polygon, ERC-721 Single, lazy mint). Rarity 4 tier. Waitlist email capture + admin.

## User Choices
- Generate art untuk gremlin (AI) — semua 200 dipetakan ke library art original.
- Generate 200 metadata otomatis dengan distribusi rarity persis (Common 120 / Rare 50 / Epic 24 / Legendary 6).
- Waitlist disimpan di MongoDB + halaman admin lihat daftar.
- Creator wallet: 0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c (Polygon, ERC-721 Single, lazy mint).

## Architecture
- Backend: FastAPI + MongoDB (Motor). Deterministic collection generator (seed=42) auto-seeds 200 NFTs on startup (idempotent). Endpoints: /api/stats, /api/nfts (filter/search/sort/paginate), /api/nfts/{token_id}, /api/traits, /api/waitlist (POST), /api/waitlist/count, /api/admin/waitlist (GET/POST contacted/DELETE, static key).
- Frontend: React (react-router, framer-motion, sonner, shadcn/ui, tailwind). Pages: Home, Gallery (/gremlins), NftDetail (/gremlin/:id), Admin (/admin). Dark neon street-art theme.
- Art: 20 original AI-generated graffiti-gremlin artworks (Gemini nano-banana), mapped to 200 items by skin + tier + gender.

## Implemented (2026-06)
- 200-item collection with exact rarity distribution, rarity score + rank, per-trait rarity %, prices per tier.
- Hero + stats ticker, Top Gremlins ranking, rarity tiers, roadmap, FAQ, waitlist form.
- Gallery: tier + 8 trait-category filters, search (id/name), 6 sort modes, pagination, mobile filter drawer.
- NFT detail: image, tier/rank/score/price, trait matrix w/ rarity %, contract info, prev/next, Rarible buy link.
- Admin waitlist: static-key gate (hypeblock2026), search, CSV export, mark contacted, delete.
- Tested: backend 15/15 pytest pass; frontend all core flows pass.

## Notes / Mocked
- Rarible & social links in `src/config.js` are PLACEHOLDERS — update `LINKS` when the Rarible collection & socials are live.
- Art is a curated library of 20 original gremlins mapped across 200 items (not 200 unique renders yet).
- Admin is a simple static-key gate (no user accounts).

## Backlog
- P1: Generate full 200 unique gremlin renders (batch, one per token).
- P1: Interactive "Trait Lab" remix previewer with live rarity estimate.
- P2: Real IPFS pinning + on-chain metadata export JSON download.
- P2: Drip-release scheduler / "coming soon" locked states per batch.
