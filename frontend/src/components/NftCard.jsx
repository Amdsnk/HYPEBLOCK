import { Link } from "react-router-dom";
import { Lock } from "lucide-react";
import { TIER_STYLES, priceLabel } from "@/config";
import RarityBadge from "@/components/RarityBadge";

function countdown(iso) {
  if (!iso) return null;
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return "unlocking…";
  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function NftCard({ nft }) {
  const s = TIER_STYLES[nft.tier] || TIER_STYLES.Common;
  const locked = nft.released === false;
  return (
    <Link
      to={`/gremlin/${nft.token_id}`}
      data-testid={`nft-card-${nft.token_id}`}
      className={`tilt-card group block rounded-2xl overflow-hidden bg-[#161926] border border-[#252A3E] hover:border-[color:var(--tw)] hover:${s.glow}`}
      style={{ "--tw": s.dot }}
    >
      <div className="relative aspect-square overflow-hidden">
        <img
          src={nft.image}
          alt={nft.title}
          loading="lazy"
          className={`h-full w-full object-cover transition-transform duration-500 group-hover:scale-105 ${locked ? "blur-[6px] scale-105 opacity-60" : ""}`}
        />
        {nft.artwork_state === "placeholder" && <span className="absolute bottom-2 right-2 rounded-md bg-black/80 px-2 py-1 text-[10px] text-slate-200">Concept preview</span>}
        {locked && (
          <div className="absolute inset-0 grid place-items-center bg-black/45">
            <div className="text-center">
              <div className="mx-auto h-9 w-9 grid place-items-center rounded-full bg-black/70 border border-white/20 text-white mb-2">
                <Lock size={16} />
              </div>
              <p className="font-display font-black text-white text-sm uppercase tracking-wide">Coming Soon</p>
              {nft.unlock_date && (
                <p className="font-mono2 text-[11px] text-[#CCFF00] mt-0.5">Unlocks in {countdown(nft.unlock_date)}</p>
              )}
            </div>
          </div>
        )}
        <div className="absolute top-2 left-2">
          <RarityBadge tier={nft.tier} />
        </div>
        <div className="absolute top-2 right-2 font-mono2 text-[10px] bg-black/70 text-slate-200 px-2 py-1 rounded-md border border-white/10">
          RANK #{nft.rank}
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-center justify-between">
          <p className="font-mono2 text-[11px] text-slate-500">{nft.title}</p>
          <p className="font-mono2 text-[11px]" style={{ color: s.dot }}>{nft.rarity_score}</p>
        </div>
        <p className="font-head font-bold text-white text-[15px] leading-tight mt-0.5 truncate">{nft.name}</p>
        <div className="mt-2 flex items-center justify-between">
          <span className="text-[11px] text-slate-400 font-mono2">{nft.traits?.Skin}</span>
          <span className="text-[13px] font-bold text-[#CCFF00] font-mono2">{locked ? "Soon" : priceLabel(nft)}</span>
        </div>
      </div>
    </Link>
  );
}
