import { Link } from "react-router-dom";
import { TIER_STYLES } from "@/config";
import RarityBadge from "@/components/RarityBadge";

export default function NftCard({ nft }) {
  const s = TIER_STYLES[nft.tier] || TIER_STYLES.Common;
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
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
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
          <span className="text-[13px] font-bold text-[#CCFF00] font-mono2">{nft.price_pol} POL</span>
        </div>
      </div>
    </Link>
  );
}
