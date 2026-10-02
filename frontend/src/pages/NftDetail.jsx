import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { ArrowLeft, ExternalLink, Copy, ChevronLeft, ChevronRight } from "lucide-react";
import { API, LINKS, CREATOR_WALLET, TIER_STYLES, COLLECTION_TOTAL } from "@/config";
import RarityBadge from "@/components/RarityBadge";

export default function NftDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [nft, setNft] = useState(null);
  const [loading, setLoading] = useState(true);
  const tokenId = parseInt(id, 10);

  useEffect(() => {
    setLoading(true);
    axios.get(`${API}/nfts/${id}`)
      .then((r) => setNft(r.data))
      .catch(() => setNft(null))
      .finally(() => setLoading(false));
    window.scrollTo(0, 0);
  }, [id]);

  const copy = (text) => { navigator.clipboard.writeText(text); toast.success("Copied to clipboard"); };

  if (loading) return <div className="pt-32 text-center text-slate-500 font-mono2">Loading gremlin…</div>;
  if (!nft) return (
    <div className="pt-32 text-center">
      <p className="text-slate-400 font-mono2">Gremlin not found.</p>
      <Link to="/gremlins" className="text-[#00E5FF] mt-3 inline-block">← Back to gallery</Link>
    </div>
  );

  const s = TIER_STYLES[nft.tier];
  const traitOrder = ["Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory"];

  return (
    <div className="pt-24 pb-16">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="flex items-center justify-between">
          <button data-testid="back-btn" onClick={() => nav(-1)} className="inline-flex items-center gap-2 text-slate-400 hover:text-white font-head font-semibold">
            <ArrowLeft size={18} /> Back
          </button>
          <div className="flex items-center gap-2">
            <button data-testid="prev-nft" disabled={tokenId <= 1} onClick={() => nav(`/gremlin/${tokenId - 1}`)}
              className="h-9 w-9 grid place-items-center rounded-lg border border-[#252A3E] text-white disabled:opacity-40"><ChevronLeft size={17} /></button>
            <button data-testid="next-nft" disabled={tokenId >= COLLECTION_TOTAL} onClick={() => nav(`/gremlin/${tokenId + 1}`)}
              className="h-9 w-9 grid place-items-center rounded-lg border border-[#252A3E] text-white disabled:opacity-40"><ChevronRight size={17} /></button>
          </div>
        </div>

        <div className="mt-6 grid lg:grid-cols-2 gap-10">
          {/* Image */}
          <div className="relative">
            <div className={`absolute -inset-3 rounded-[28px] blur-2xl opacity-60`} style={{ background: s.dot + "33" }} />
            <div className="relative rounded-[24px] overflow-hidden border border-[#252A3E]">
              <img data-testid="nft-detail-image" src={nft.image} alt={nft.title} className="w-full aspect-square object-cover" />
            </div>
          </div>

          <p className="lg:col-span-2 text-sm text-slate-400">{nft.artwork_state === "canonical" ? "Artwork approved. Marketplace availability is announced separately." : nft.artwork_state === "candidate" ? "Artwork under review. This character is not yet approved for mint." : "Concept preview. Final artwork is still in production."}</p>
          {/* Info */}
          <div>
            <div className="flex items-center gap-3">
              <RarityBadge tier={nft.tier} size="lg" />
              <span className="font-mono2 text-sm text-slate-400">{nft.title}</span>
            </div>
            <h1 data-testid="nft-detail-name" className="font-display text-3xl sm:text-4xl font-black uppercase text-white mt-3">{nft.name}</h1>
            <p className="text-slate-400 mt-2 text-sm max-w-md">{nft.description}</p>

            <div className="mt-6 grid grid-cols-3 gap-3">
              <div className="rounded-xl border border-[#252A3E] bg-[#0F111A] p-4">
                <p className="font-mono2 text-[10px] uppercase tracking-[0.2em] text-slate-500">Rank</p>
                <p className="font-display font-black text-white text-xl mt-1">#{nft.rank}</p>
              </div>
              <div className="rounded-xl border border-[#252A3E] bg-[#0F111A] p-4">
                <p className="font-mono2 text-[10px] uppercase tracking-[0.2em] text-slate-500">Score</p>
                <p className="font-display font-black text-xl mt-1" style={{ color: s.dot }}>{nft.rarity_score}</p>
              </div>
              <div className="rounded-xl border border-[#252A3E] bg-[#0F111A] p-4">
                <p className="font-mono2 text-[10px] uppercase tracking-[0.2em] text-slate-500">Price</p>
                <p className="text-xs text-slate-400">Proposed asking price</p><p className="font-display font-black text-[#CCFF00] text-xl mt-1">{nft.price_pol === 0 ? "Auction" : <>{nft.price_pol}<span className="text-xs"> POL</span></>}</p>
              </div>
            </div>

            <a data-testid="buy-rarible-btn" href={LINKS.rarible} target="_blank" rel="noreferrer"
              className="mt-6 w-full inline-flex items-center justify-center gap-2 bg-[#FF0055] hover:bg-[#ff2e73] text-white font-head font-bold px-6 py-3.5 rounded-xl transition-colors shadow-[0_0_24px_rgba(255,0,85,0.4)]">
              View creator on Rarible <ExternalLink size={17} />
            </a>

            {/* Traits */}
            <p className="font-mono2 text-xs uppercase tracking-[0.25em] text-[#CCFF00] mt-8">Traits</p>
            <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {traitOrder.map((cat) => (
                <div key={cat} data-testid={`trait-${cat.toLowerCase()}`} className="rounded-xl border border-[#252A3E] bg-[#161926] p-3">
                  <p className="font-mono2 text-[10px] uppercase tracking-[0.15em] text-slate-500">{cat}</p>
                  <p className="font-head font-bold text-white text-sm mt-1 truncate">{nft.traits[cat]}</p>
                  {nft.trait_rarity_pct?.[cat] != null && (
                    <p className="font-mono2 text-[11px] text-[#00E5FF] mt-0.5">{nft.trait_rarity_pct[cat]}% have this</p>
                  )}
                </div>
              ))}
            </div>

            {/* Contract */}
            <div className="mt-8 rounded-xl border border-[#252A3E] bg-[#0F111A] p-4 font-mono2 text-xs space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-slate-500">Token ID</span>
                <span className="text-slate-300">#{nft.token_id}</span>
              </div>
              <div className="flex items-center justify-between gap-2">
                <span className="text-slate-500">Standard</span>
                <span className="text-slate-300">ERC-721 · Polygon</span>
              </div>
              <div className="flex items-center justify-between gap-2">
                <span className="text-slate-500">Creator</span>
                <button data-testid="copy-wallet-btn" onClick={() => copy(CREATOR_WALLET)} className="text-slate-300 inline-flex items-center gap-1.5 hover:text-[#00E5FF]">
                  {CREATOR_WALLET.slice(0, 6)}…{CREATOR_WALLET.slice(-4)} <Copy size={12} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
