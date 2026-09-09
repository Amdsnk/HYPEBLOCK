import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ExternalLink, ArrowRight, Sparkles, Flame, Shield, Crown, Gem,
} from "lucide-react";
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion";
import { API, LINKS, TIER_STYLES } from "@/config";
import NftCard from "@/components/NftCard";
import RarityBadge from "@/components/RarityBadge";
import WaitlistForm from "@/components/WaitlistForm";

const TICKER = [
  "96 ORIGINAL PFP", "POLYGON / MATIC", "ERC-721 SINGLE", "FREE LAZY MINT",
  "5 RARITY TIERS", "8 TRAIT CATEGORIES", "RARIBLE VERIFIED", "ROYALTY 5–10%",
];

const TIER_INFO = [
  { tier: "Common", pct: "52%", pcs: 50, price: "8–15 POL", icon: Shield, desc: "Everyday street gremlins." },
  { tier: "Rare", pct: "25%", pcs: 24, price: "20–40 POL", icon: Sparkles, desc: "Rare traits — diamond chains & horns." },
  { tier: "Epic", pct: "13.5%", pcs: 13, price: "60–120 POL", icon: Flame, desc: "Laser / flame eyes, crown energy." },
  { tier: "Legendary", pct: "6.25%", pcs: 6, price: "200+ POL", icon: Crown, desc: "Gold & diamond skins, flaming halo." },
  { tier: "Mythic", pct: "3.1%", pcs: 3, price: "Auction", icon: Gem, desc: "The 1-of-1 crown-jewel kings & queens." },
];

const FAQS = [
  { q: "What is HYPEBLOCK Graffiti Gremlins?", a: "A collection of 96 original 'graffiti gremlin' PFP mascots — bold, edgy, streetwear, neon spray-paint style. Every gremlin is a unique 1-of-1 artwork, with traits & rarity like top PFP collections, but 100% original mascots (gremlins, not apes)." },
  { q: "How big is the collection and where is it listed?", a: "96 unique items total (HYPEBLOCK #001–#096). Listed on Rarible on the Polygon network as ERC-721 (Single / 1-of-1) with free lazy minting — the buyer pays gas at purchase." },
  { q: "Why Polygon?", a: "Polygon is cheap and fast. With lazy minting the creator cost is ~0 and buyers only pay a tiny gas fee at purchase. Perfect for an art-only drop." },
  { q: "How are Rarity Score & Tier calculated?", a: "The rarity score is based on how scarce each trait is across the 96 items (the rarer a trait, the higher the score). Tiers: Common, Rare, Epic, Legendary, and 3 Mythic 1-of-1 crown jewels." },
  { q: "How do I join the Gremlin Gang waitlist?", a: "Drop your email (and optional wallet) in the Waitlist form. The waitlist hears about drops and Mythic auctions first." },
];

export default function Home() {
  const [stats, setStats] = useState(null);
  const [featured, setFeatured] = useState([]);
  const [hero, setHero] = useState(null);

  useEffect(() => {
    axios.get(`${API}/stats`).then((r) => setStats(r.data)).catch(() => {});
    axios.get(`${API}/nfts`, { params: { sort: "rank_asc", limit: 10 } }).then((r) => {
      setHero(r.data.items[0]);
      setFeatured(r.data.items.slice(1, 9));
    }).catch(() => {});
  }, []);

  return (
    <div className="pt-16">
      {/* HERO */}
      <section id="showcase" className="relative overflow-hidden hb-noise">
        <div className="absolute inset-0 hb-grid opacity-40 pointer-events-none" />
        <div className="relative mx-auto max-w-[1400px] px-6 pt-16 pb-14 grid lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7">
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              <span className="inline-flex items-center gap-2 font-mono2 text-[11px] uppercase tracking-[0.25em] text-[#00E5FF] border border-[#00E5FF]/30 rounded-full px-3 py-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[#00E5FF] animate-pulse" /> 96 PFP · Polygon / Rarible
              </span>
              <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[0.95] uppercase text-white mt-5">
                Graffiti Gremlin <span className="text-[#FF0055] neon-pink-text">Collective</span>
              </h1>
              <p className="mt-5 text-slate-300 text-base sm:text-lg max-w-xl leading-relaxed">
                96 original street gremlin mascots. Bold, edgy, neon spray-paint. Rowdy, gang, hype —
                underground PFP for lovers of offbeat art.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a data-testid="hero-rarible-btn" href={LINKS.rarible} target="_blank" rel="noreferrer"
                  className="inline-flex items-center gap-2 bg-[#FF0055] hover:bg-[#ff2e73] text-white font-head font-bold px-6 py-3.5 rounded-full transition-colors shadow-[0_0_28px_rgba(255,0,85,0.45)]">
                  View on Rarible <ExternalLink size={17} />
                </a>
                <Link data-testid="hero-gallery-btn" to="/gremlins"
                  className="inline-flex items-center gap-2 border border-[#252A3E] hover:border-[#00E5FF]/60 text-white font-head font-bold px-6 py-3.5 rounded-full transition-colors">
                  Explore the Gremlins <ArrowRight size={17} />
                </Link>
              </div>

              {stats && (
                <div className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-xl">
                  {[
                    { k: "Supply", v: stats.total_supply },
                    { k: "Network", v: stats.network },
                    { k: "Tiers", v: "5" },
                    { k: "Traits", v: "8" },
                  ].map((x) => (
                    <div key={x.k} className="rounded-xl border border-[#252A3E] bg-[#0F111A]/70 p-3">
                      <p className="font-mono2 text-[10px] uppercase tracking-[0.2em] text-slate-500">{x.k}</p>
                      <p className="font-display font-extrabold text-white text-lg mt-1">{x.v}</p>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </div>

          <div className="lg:col-span-5">
            {hero && (
              <motion.div initial={{ opacity: 0, scale: 0.94 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6 }}
                className="relative floaty">
                <div className="absolute -inset-3 rounded-[28px] bg-gradient-to-br from-[#FF0055]/30 via-[#9D00FF]/20 to-[#00E5FF]/30 blur-2xl" />
                <Link to={`/gremlin/${hero.token_id}`} data-testid="hero-featured-nft" className="relative block rounded-[24px] overflow-hidden border border-[#252A3E]">
                  <img src={hero.image} alt={hero.title} className="w-full aspect-square object-cover" />
                  <div className="absolute top-3 left-3 flex items-center gap-2">
                    <RarityBadge tier={hero.tier} size="lg" />
                    <span className="font-mono2 text-[11px] bg-black/70 text-white px-2 py-1 rounded-md border border-white/10">RANK #{hero.rank}</span>
                  </div>
                  <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/85 to-transparent">
                    <p className="font-mono2 text-xs text-slate-300">{hero.title}</p>
                    <p className="font-display font-extrabold text-white text-xl">{hero.name}</p>
                  </div>
                </Link>
              </motion.div>
            )}
          </div>
        </div>

        {/* Ticker */}
        <div className="border-y border-[#252A3E] bg-[#0B0C12] overflow-hidden">
          <div className="ticker-track flex whitespace-nowrap py-3">
            {[...TICKER, ...TICKER].map((t, i) => (
              <span key={i} className="mx-8 font-mono2 text-xs uppercase tracking-[0.2em] text-slate-400 inline-flex items-center gap-3">
                <span className="h-1 w-1 rounded-full bg-[#FF0055]" /> {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURED SHOWCASE */}
      <section className="mx-auto max-w-[1400px] px-6 py-20">
        <div className="flex items-end justify-between flex-wrap gap-4">
          <div>
            <p className="font-mono2 text-xs uppercase tracking-[0.25em] text-[#CCFF00]">Rarity Ranking</p>
            <h2 className="font-display text-2xl sm:text-3xl lg:text-4xl font-extrabold uppercase text-white mt-2">Top Gremlins</h2>
          </div>
          <Link to="/gremlins" data-testid="see-all-gremlins" className="inline-flex items-center gap-2 text-[#00E5FF] font-head font-bold hover:gap-3 transition-all">
            See all Gremlins <ArrowRight size={17} />
          </Link>
        </div>
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          {featured.map((n) => <NftCard key={n.token_id} nft={n} />)}
        </div>
      </section>

      {/* RARITY TIERS */}
      <section className="mx-auto max-w-[1400px] px-6 pb-8">
        <p className="font-mono2 text-xs uppercase tracking-[0.25em] text-[#CCFF00]">Distribution</p>
        <h2 className="font-display text-2xl sm:text-3xl lg:text-4xl font-extrabold uppercase text-white mt-2">5 Rarity Tiers</h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {TIER_INFO.map(({ tier, pct, pcs, price, icon: Icon, desc }) => {
            const s = TIER_STYLES[tier];
            return (
              <div key={tier} className={`tilt-card rounded-2xl border ${s.border} bg-[#0F111A] p-5 ${s.glow}`}>
                <div className="flex items-center justify-between">
                  <Icon className={s.text} size={22} />
                  <span className={`font-display font-black text-2xl ${s.text}`}>{pct}</span>
                </div>
                <RarityBadge tier={tier} />
                <p className="mt-3 text-sm text-slate-400">{desc}</p>
                <div className="mt-4 pt-3 border-t border-[#252A3E] flex items-center justify-between font-mono2 text-xs">
                  <span className="text-slate-500">{pcs} pcs</span>
                  <span className="text-[#CCFF00]">{price}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ROADMAP */}
      <section id="roadmap" className="mx-auto max-w-[1400px] px-6 py-20">
        <p className="font-mono2 text-xs uppercase tracking-[0.25em] text-[#CCFF00]">The Plan</p>
        <h2 className="font-display text-2xl sm:text-3xl lg:text-4xl font-extrabold uppercase text-white mt-2">Roadmap</h2>
        <div className="mt-10 relative border-l-2 border-[#252A3E] ml-3 space-y-10">
          {[
            { p: "PHASE 1", t: "Tagging the Block", d: "96 unique original gremlin PFPs live, Rarible store on Polygon, lazy mint ready." },
            { p: "PHASE 2", t: "Gremlin Gang Invasion", d: "Waitlist + drip release ~20–30/week, underground Discord gang opens." },
            { p: "PHASE 3", t: "Merch Drip & Spray Cans", d: "Free wallpaper pack, sticker bombs, holder Discord role, mini-comic lore." },
            { p: "PHASE 4", t: "Underground Vault", d: "Community vault, secondary royalty sharing, artist collabs." },
          ].map((ph, i) => (
            <motion.div key={ph.p} initial={{ opacity: 0, x: -12 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }}
              className="relative pl-8">
              <span className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-[#FF0055] shadow-[0_0_14px_rgba(255,0,85,0.7)]" />
              <p className="font-mono2 text-xs text-[#00E5FF] tracking-[0.2em]">{ph.p}</p>
              <h3 className="font-display font-extrabold text-white text-xl mt-1">{ph.t}</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-xl">{ph.d}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* WAITLIST */}
      <section id="waitlist" className="mx-auto max-w-[1400px] px-6 py-10">
        <WaitlistForm />
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-[900px] px-6 py-20">
        <p className="font-mono2 text-xs uppercase tracking-[0.25em] text-[#CCFF00] text-center">Questions</p>
        <h2 className="font-display text-2xl sm:text-3xl lg:text-4xl font-extrabold uppercase text-white mt-2 text-center">FAQ</h2>
        <Accordion type="single" collapsible className="mt-8">
          {FAQS.map((f, i) => (
            <AccordionItem key={i} value={`item-${i}`} data-testid={`faq-item-${i}`} className="border-[#252A3E]">
              <AccordionTrigger className="font-head font-bold text-white text-left hover:text-[#00E5FF] hover:no-underline">
                {f.q}
              </AccordionTrigger>
              <AccordionContent className="text-slate-400 text-sm leading-relaxed">{f.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </section>
    </div>
  );
}
