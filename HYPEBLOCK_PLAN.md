# HYPEBLOCK — Master Plan, Architecture & Launch Playbook
_200 Original Graffiti Gremlins · Polygon · Rarible / OpenSea_

This document is the single source of truth for **how HYPEBLOCK is built** and **how to make it succeed** in the NFT market. It covers (1) the product/architecture that is already live, and (2) the concrete, step-by-step go-to-market plan.

---

## 1. What Exists Right Now (Live App)

- **Full-stack showcase site** — React + FastAPI + MongoDB, dark neon street-art theme, all copy in **English**.
- **200-item collection**, deterministic (seeded) with the **original founding trait scheme**:
  - Skin, Eyes, Headwear, Mouth, Outfit, Background, Accessory, Gender (8 categories).
- **5 rarity tiers**:
  | Tier | Count | Share | Price (POL) |
  |------|-------|-------|-------------|
  | Common | 120 | 60% | 8–15 |
  | Rare | 50 | 25% | 20–40 |
  | Epic | 24 | 12% | 60–120 |
  | Legendary | 5 | 2.5% | 200+ |
  | **Mythic (1-of-1)** | **1** | **0.5%** | **Auction** |
- **Mythic "Genesis King"** — the single 1-of-1 crown jewel, always Rarity Rank #1.
- **Rarity engine** — per-trait scarcity → rarity score + rank + per-trait % on each detail page.
- **Waitlist** (email + optional wallet) stored in MongoDB, with an **Admin dashboard** (`/admin`, key `hypeblock2026`): search, CSV export, mark-contacted, delete.
- **Mint Kit export** — `/api/metadata/export` returns all 200 items in the OpenSea/Rarible metadata standard; a one-click "Mint Kit JSON" download lives in the Admin dashboard.

### Key API endpoints (all under `/api`)
- `GET /stats` — supply, tiers, waitlist count, creator wallet.
- `GET /nfts` — filter (tier, gender, all traits), search, sort, paginate.
- `GET /nfts/{token_id}` — one gremlin + per-trait rarity %.
- `GET /nfts/{token_id}/metadata` — single-token OpenSea metadata.
- `GET /metadata/export` — full 200-item metadata array (the Mint Kit).
- `POST /waitlist`, `GET /waitlist/count`, `GET/POST/DELETE /admin/waitlist`.

---

## 2. Technical Architecture

```
                 ┌────────────────────────────────────────────┐
   Buyer / Fan → │  React SPA (Home / Gallery / Detail / Admin) │
                 └───────────────┬────────────────────────────┘
                                 │  REST (/api, via REACT_APP_BACKEND_URL)
                 ┌───────────────▼────────────────────────────┐
                 │  FastAPI  (rarity engine + waitlist + admin) │
                 └───────────────┬────────────────────────────┘
                                 │  Motor (async)
                 ┌───────────────▼────────────────────────────┐
                 │  MongoDB   (nfts, waitlist, meta)            │
                 └─────────────────────────────────────────────┘

        Art  → IPFS (images)         Sale → Rarible (ERC-721 Single, lazy mint) on Polygon
```

- **On-chain layer:** ERC-721 "Single" (each token a true 1-of-1) on **Polygon**, sold via **Rarible lazy mint** (creator pays ~0 gas; buyer mints on purchase). Creator royalty **5–10%**.
- **Off-chain layer:** the showcase site is the marketing hub + rarity explorer + waitlist funnel. It does NOT hold funds and never touches private keys.
- **Storage of art & metadata:** IPFS (Pinata/NFT.Storage). The site references image URLs today; for the on-chain listing the images + JSON must be pinned to IPFS.

---

## 3. Assets & Art Strategy

- **Locked base style** (critical for a cohesive collection): bold graffiti, thick black outline, neon drip, bust portrait, pointy-eared original gremlin (NOT an ape → no copycat risk).
- **5 founding base renders** you supplied are integrated as the visual anchors (green space-buns female, epic zombie devil-horns, toxic-blue snapback, toxic-blue gold-cap, blue neon-hair female). The blue gold-cap "HYPEBLOCK" render is the **Mythic Genesis King**.
- **Current gap:** the 200 items map to a curated library of hero renders (variety by skin/tier/gender), not yet 200 unique 1-per-token images.
- **Path to 200 unique renders:** batch-generate one image per token from each item's stored `prompt` (already produced by the backend), QA, then pin to IPFS and overlay via `backend/gremlin_images.json` (`{ "<token_id>": "ipfs://.../<id>.png" }`). The site auto-uses these when present. _This step needs an image-generation key (Gemini nano-banana via Emergent LLM Key)._

---

## 4. Step-by-Step: Listing on Rarible & OpenSea

**A. Prep the Mint Kit**
1. In `/admin`, click **Mint Kit JSON** → downloads `hypeblock-metadata.json` (all 200 in OpenSea/Rarible standard).
2. Generate/finalize the 200 images (see §3). Keep filenames `001.png … 200.png`.

**B. Pin to IPFS**
3. Create an account on Pinata or NFT.Storage (free tier is fine).
4. Upload the **image folder** → get a folder CID. Images become `ipfs://<CID>/001.png`.
5. Replace each `image` field in the metadata with its `ipfs://<CID>/<id>.png`, then upload the **metadata folder** → get a metadata CID.

**C. Rarible (primary sales channel — Polygon, lazy mint)**
6. Connect MetaMask (wallet `0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c`) to Rarible → switch to **Polygon**.
7. Create a **Collection** (ERC-721). Set name HYPEBLOCK, symbol, logo/banner, royalty 5–10%.
8. For each token: **Create → Single**, upload art (or point to IPFS), paste name + description + attributes from the Mint Kit, choose **"Free minting" (lazy mint)**, set price per the tier table (Mythic = timed auction).
9. **Drip release**: list only Batch 1 (~20) first. Add ~20–30/week to build momentum + FOMO.
10. Update `frontend/src/config.js → LINKS.rarible` to the real collection URL once created (currently points to the creator profile).

**D. OpenSea (secondary discovery)**
11. OpenSea auto-indexes Polygon collections. Once tokens are minted/sold on Rarible they appear on OpenSea; verify the collection, set the same royalty, description, and links.

---

## 5. Go-to-Market Plan (the 80% that actually sells NFTs)

> Honest truth: with zero starting audience, **community + content is the make-or-break**, not the art alone.

**Phase 0 — Foundations (before any sale)**
- Lock socials: X (@hypeblock), Instagram, Discord. Update `config.js → LINKS`.
- Turn on the **waitlist** (already live) — it's the #1 owned-audience asset.
- Write 2 weeks of content in advance.

**Phase 1 — Warm-up (Weeks 1–2, NO selling)**
- Post the making-of: single gremlins, trait teasers, "which one are you?" polls.
- Rules to avoid platform "inauthentic" flags: vary every caption (no copy-paste), links in **replies** not the main post, max 1–2 hashtags, never mass-follow.

**Phase 2 — Reveal & Drop 1 (Week 3)**
- Reveal the collection + rarity system + the Mythic Genesis King as the hero story.
- List Batch 1 (~20) on Rarible. Soft-sell: "for people who love offbeat art, not a get-rich scheme. Link in reply."

**Phase 3 — Drip & Community (Weeks 4–10)**
- ~20–30 new gremlins/week. Open Discord, give holders a role.
- Free soft-utility to boost retention: wallpaper pack, sticker bombs, mini-comic lore.

**Phase 4 — Sustain (Month 3+)**
- Artist collabs, community vault, secondary-royalty perks, feature top holders.

---

## 6. Risks & Mitigations
- **Style drift across 200** → mitigated by a single locked base style + curated hero renders.
- **No audience** → waitlist + daily authentic content + Discord (Phase 1–3).
- **Copycat accusations** → 100% original gremlin mascot, never an ape.
- **Buyer friction** → Polygon + lazy mint keeps buyer cost to a few cents of gas.

---

## 7. What You Need to Provide
- **MetaMask** wallet with a little POL (for collection setup/activity).
- **Real social handles** + the **live Rarible collection URL** (to replace placeholders in `config.js`).
- **Confirm** first batch size (recommended: 20) and whether to AI-generate all 200 unique renders (needs image key).
