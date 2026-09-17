---
name: File-backed hosting storage
description: Durable hosting constraint for HYPEBLOCK data and artwork.
---

HYPEBLOCK is intended to run on traditional hosting without MongoDB or third-party asset storage. Mutable records use an atomic JSON file, while NFT artwork must remain in the hosting filesystem and be served by the app.

**Why:** The target hosting environment may provide only a writable filesystem, and remote asset URLs can disappear or become inaccessible.

**How to apply:** Keep the JSON data file and asset directories on persistent storage, back them up with the host, and set `HYPEBLOCK_DATA_FILE` when the application directory is not persistent.