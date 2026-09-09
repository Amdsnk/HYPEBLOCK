const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// HYPEBLOCK links — update RARIBLE_URL & socials when live
export const LINKS = {
  rarible: "https://rarible.com/collection/polygon/hypeblock",
  twitter: "https://x.com/hypeblock",
  instagram: "https://instagram.com/hypeblock",
  discord: "https://discord.gg/hypeblock",
  polygonScan: "https://polygonscan.com/address/0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c",
};

export const CREATOR_WALLET = "0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c";

export const TRAIT_CATEGORIES = [
  "Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory",
];

export const TIER_STYLES = {
  Common: { text: "text-slate-300", border: "border-slate-500/60", bg: "bg-slate-700/40", glow: "shadow-[0_0_14px_rgba(148,163,184,0.25)]", dot: "#94A3B8" },
  Rare: { text: "text-cyan-300", border: "border-cyan-400/70", bg: "bg-cyan-500/10", glow: "shadow-[0_0_16px_rgba(0,229,255,0.35)]", dot: "#00E5FF" },
  Epic: { text: "text-fuchsia-300", border: "border-fuchsia-400/70", bg: "bg-fuchsia-500/10", glow: "shadow-[0_0_18px_rgba(157,0,255,0.45)]", dot: "#9D00FF" },
  Legendary: { text: "text-amber-300", border: "border-amber-400/80", bg: "bg-amber-500/10", glow: "shadow-[0_0_22px_rgba(255,184,0,0.55)]", dot: "#FFB800" },
};
