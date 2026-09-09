import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { Sparkles, ChevronLeft, ChevronRight, ArrowRight } from "lucide-react";
import { API, TIER_STYLES, priceLabel } from "@/config";
import RarityBadge from "@/components/RarityBadge";

export default function RaritySpotlight() {
  const [items, setItems] = useState([]);
  const [active, setActive] = useState(0);

  useEffect(() => {
    axios.get(`${API}/nfts`, { params: { sort: "rank_asc", limit: 12 } })
      .then((r) => {
        const list = r.data.items || [];
        setItems(list);
        if (list.length) {
          const week = Math.floor(Date.now() / (7 * 86400000));
          setActive(week % list.length);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (items.length < 2) return;
    const t = setInterval(() => setActive((i) => (i + 1) % items.length), 5000);
    return () => clearInterval(t);
  }, [items.length]);

  if (!items.length) return null;
  const nft = items[active];
  const s = TIER_STYLES[nft.tier] || TIER_STYLES.Common;
  const go = (d) => setActive((i) => (i + d + items.length) % items.length);

  return (
    <section id="spotlight" data-testid="rarity-spotlight" className="relative py-20 hb-noise">
      <div className="absolute inset-0 hb-grid opacity-20 pointer-events-none" />
      <div className="relative mx-auto max-w-[1400px] px-6">
        <div className="flex items-end justify-between mb-8">
          <div>
            <span className="inline-flex items-center gap-2 font-mono2 text-[11px] uppercase tracking-[0.25em] text-[#CCFF00]">
              <Sparkles size={14} /> Rarity Spotlight
            </span>
            <h2 className="font-display text-3xl sm:text-4xl font-black uppercase text-white mt-2 leading-none">
              Rarest <span className="text-[#00E5FF]">This Week</span>
            </h2>
          </div>
          <Link to="/gremlins" data-testid="spotlight-viewall"
            className="hidden sm:inline-flex items-center gap-1.5 font-head text-sm font-bold text-slate-300 hover:text-[#00E5FF] transition-colors uppercase">
            View all <ArrowRight size={15} />
          </Link>
        </div>

        <div className="grid lg:grid-cols-12 gap-6 items-stretch">
          {/* Featured */}
          <div className="lg:col-span-8 relative rounded-3xl overflow-hidden border border-[#252A3E] bg-[#0F111A]">
            <AnimatePresence mode="wait">
              <motion.div
                key={nft.token_id}
                initial={{ opacity: 0, scale: 1.02 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
                className="grid sm:grid-cols-2"
              >
                <Link to={`/gremlin/${nft.token_id}`} data-testid="spotlight-featured-img"
                  className="relative aspect-square block overflow-hidden group">
                  <img src={nft.image} alt={nft.name} className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-700" />
                  <span className="absolute top-3 left-3"><RarityBadge tier={nft.tier} /></span>
                  <span className="absolute top-3 right-3 font-mono2 text-[10px] bg-black/70 text-[#CCFF00] px-2 py-1 rounded-md border border-white/10">
                    RANK #{nft.rank}
                  </span>
                </Link>
                <div className="p-6 sm:p-8 flex flex-col justify-center">
                  <p className="font-mono2 text-[11px] text-slate-500">{nft.title}</p>
                  <h3 className="font-display text-2xl sm:text-3xl font-black text-white mt-1 leading-none">{nft.name}</h3>
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <div className="rounded-xl border border-[#252A3E] p-3">
                      <p className="font-mono2 text-[10px] uppercase tracking-widest text-slate-500">Rarity Score</p>
                      <p className="font-display font-extrabold text-lg mt-0.5" style={{ color: s.dot }}>{nft.rarity_score}</p>
                    </div>
                    <div className="rounded-xl border border-[#252A3E] p-3">
                      <p className="font-mono2 text-[10px] uppercase tracking-widest text-slate-500">Price</p>
                      <p className="font-display font-extrabold text-lg text-[#CCFF00] mt-0.5">{priceLabel(nft)}</p>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {Object.entries(nft.traits || {}).slice(0, 4).map(([k, v]) => (
                      <span key={k} className="font-mono2 text-[10px] text-slate-300 border border-[#252A3E] rounded-full px-2.5 py-1">
                        {k}: <span className="text-white">{v}</span>
                      </span>
                    ))}
                  </div>
                  <Link to={`/gremlin/${nft.token_id}`} data-testid="spotlight-cta"
                    className="mt-6 inline-flex items-center gap-2 self-start bg-[#00E5FF] hover:bg-[#33ecff] text-black font-head font-bold px-5 py-3 rounded-full transition-colors">
                    Inspect Gremlin <ArrowRight size={16} />
                  </Link>
                </div>
              </motion.div>
            </AnimatePresence>
            <button data-testid="spotlight-prev" onClick={() => go(-1)}
              className="absolute left-3 top-1/2 -translate-y-1/2 h-9 w-9 grid place-items-center rounded-full bg-black/60 border border-white/10 text-white hover:bg-black/80 transition-colors">
              <ChevronLeft size={18} />
            </button>
            <button data-testid="spotlight-next" onClick={() => go(1)}
              className="absolute right-3 top-1/2 -translate-y-1/2 h-9 w-9 grid place-items-center rounded-full bg-black/60 border border-white/10 text-white hover:bg-black/80 transition-colors">
              <ChevronRight size={18} />
            </button>
          </div>

          {/* Thumbnails */}
          <div className="lg:col-span-4 grid grid-cols-4 lg:grid-cols-3 gap-3 content-start">
            {items.map((it, i) => (
              <button
                key={it.token_id}
                data-testid={`spotlight-thumb-${it.token_id}`}
                onClick={() => setActive(i)}
                className={`relative aspect-square rounded-xl overflow-hidden border transition-all ${i === active ? "border-[#00E5FF] ring-2 ring-[#00E5FF]/40" : "border-[#252A3E] opacity-70 hover:opacity-100"}`}
              >
                <img src={it.image} alt={it.name} loading="lazy" className="h-full w-full object-cover" />
                <span className="absolute bottom-1 left-1 font-mono2 text-[9px] bg-black/70 text-white px-1.5 py-0.5 rounded">#{it.rank}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
