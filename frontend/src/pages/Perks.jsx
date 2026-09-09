import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import { Download, Package, Sparkles, ShieldCheck, Wallet, Hash, Bot, ExternalLink, Crown, Image as ImageIcon, Gift } from "lucide-react";
import { API, LINKS } from "@/config";
import RarityBadge from "@/components/RarityBadge";

const DISCORD_STEPS = [
  { icon: ExternalLink, title: "Join the Discord", desc: "Hit the button below to enter the HYPEBLOCK Gremlin Gang server." },
  { icon: Wallet, title: "Connect your wallet", desc: "In the #verify channel, connect the Polygon wallet holding your gremlin(s)." },
  { icon: Bot, title: "Verify with Collab.Land", desc: "Our Collab.Land bot reads your wallet and confirms you own a HYPEBLOCK NFT." },
  { icon: ShieldCheck, title: "Get your Holder role", desc: "The bot auto-grants the Holder role — unlocking holder-only channels & drops." },
];

const PERKS = [
  { icon: ImageIcon, title: "Wallpaper Pack", desc: "High-res gremlin wallpapers for desktop & phone — free for everyone, refreshed as the collection grows." },
  { icon: Hash, title: "Holder-only channels", desc: "Private Discord channels for alpha, giveaways and direct line to the artist." },
  { icon: Crown, title: "Mythic auction access", desc: "Holders get early bidding windows on the 1-of-1 Mythic crown jewels." },
  { icon: Gift, title: "Airdrops & allowlists", desc: "Priority allowlist spots and surprise airdrops for future HYPEBLOCK drops." },
];

export default function Perks() {
  const [walls, setWalls] = useState([]);

  useEffect(() => {
    axios.get(`${API}/wallpapers`, { params: { limit: 12 } })
      .then((r) => setWalls(r.data.items || []))
      .catch(() => {});
  }, []);

  const downloadOne = async (nft) => {
    try {
      const res = await axios.get(nft.image, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `HYPEBLOCK_${String(nft.token_id).padStart(3, "0")}_${nft.name.replace(/\s+/g, "_")}.jpg`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast.success(`Downloaded ${nft.name}`);
    } catch {
      toast.error("Download failed — try again");
    }
  };

  return (
    <div className="pt-16 bg-[#08090D] min-h-screen">
      {/* HERO */}
      <section className="relative overflow-hidden hb-noise border-b border-[#252A3E]">
        <div className="absolute inset-0 hb-grid opacity-30 pointer-events-none" />
        <div className="relative mx-auto max-w-[1400px] px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-flex items-center gap-2 font-mono2 text-[11px] uppercase tracking-[0.25em] text-[#CCFF00] border border-[#CCFF00]/30 rounded-full px-3 py-1.5">
              <Sparkles size={13} /> Gremlin Gang Perks
            </span>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight uppercase text-white mt-5 leading-[0.95]">
              Holder <span className="text-[#FF0055] neon-pink-text">Perks</span>
            </h1>
            <p className="mt-5 text-slate-300 text-base sm:text-lg max-w-2xl leading-relaxed">
              Rep the block. Grab the free wallpaper pack, then verify your gremlin on Discord to unlock
              holder-only channels, Mythic auction access and future airdrops.
            </p>
          </motion.div>
        </div>
      </section>

      {/* WALLPAPER PACK */}
      <section className="mx-auto max-w-[1400px] px-6 py-16">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <span className="inline-flex items-center gap-2 font-mono2 text-[11px] uppercase tracking-[0.25em] text-[#00E5FF]">
              <ImageIcon size={14} /> Free Download
            </span>
            <h2 className="font-display text-3xl sm:text-4xl font-black uppercase text-white mt-2 leading-none">Wallpaper Pack</h2>
            <p className="text-slate-400 text-sm mt-2 max-w-xl">The rarest gremlins in full resolution. Download individually or grab the whole pack as a ZIP.</p>
          </div>
          <a
            data-testid="download-pack-btn"
            href={`${API}/wallpapers/pack?limit=12`}
            className="inline-flex items-center gap-2 self-start bg-[#FF0055] hover:bg-[#ff2e73] text-white font-head font-bold px-6 py-3.5 rounded-full transition-colors shadow-[0_0_28px_rgba(255,0,85,0.45)]"
          >
            <Package size={18} /> Download Pack (ZIP)
          </a>
        </div>

        {walls.length === 0 ? (
          <p data-testid="wallpapers-empty" className="text-slate-500 font-mono2 text-sm">Loading wallpapers…</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
            {walls.map((nft, i) => (
              <motion.div
                key={nft.token_id}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.35, delay: (i % 4) * 0.05 }}
                data-testid={`wallpaper-${nft.token_id}`}
                className="group rounded-2xl overflow-hidden bg-[#161926] border border-[#252A3E] hover:border-[#00E5FF]/50 transition-colors"
              >
                <div className="relative aspect-square overflow-hidden">
                  <img src={nft.image} alt={nft.name} loading="lazy" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  <span className="absolute top-2 left-2"><RarityBadge tier={nft.tier} /></span>
                </div>
                <div className="p-3 flex items-center justify-between gap-2">
                  <div className="min-w-0">
                    <p className="font-mono2 text-[10px] text-slate-500">{nft.title}</p>
                    <p className="font-head font-bold text-white text-sm truncate">{nft.name}</p>
                  </div>
                  <button
                    data-testid={`wallpaper-download-${nft.token_id}`}
                    onClick={() => downloadOne(nft)}
                    className="shrink-0 h-9 w-9 grid place-items-center rounded-full bg-[#00E5FF]/10 border border-[#00E5FF]/40 text-[#00E5FF] hover:bg-[#00E5FF]/20 transition-colors"
                    title="Download"
                  >
                    <Download size={16} />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </section>

      {/* DISCORD ROLE CLAIM */}
      <section className="border-t border-[#252A3E] hb-noise">
        <div className="mx-auto max-w-[1400px] px-6 py-16">
          <div className="grid lg:grid-cols-12 gap-10 items-start">
            <div className="lg:col-span-5">
              <span className="inline-flex items-center gap-2 font-mono2 text-[11px] uppercase tracking-[0.25em] text-[#7289da]">
                <Bot size={14} /> Discord Access
              </span>
              <h2 className="font-display text-3xl sm:text-4xl font-black uppercase text-white mt-2 leading-none">Claim your Holder role</h2>
              <p className="text-slate-400 text-sm mt-3 leading-relaxed">
                Owning a HYPEBLOCK gremlin gets you a verified <span className="text-white font-semibold">Holder</span> role
                in our Discord. It takes under a minute — no gas, no signing anything risky.
              </p>
              <a
                data-testid="join-discord-btn"
                href={LINKS.discord}
                target="_blank"
                rel="noreferrer"
                className="mt-6 inline-flex items-center gap-2 bg-[#5865F2] hover:bg-[#6b77f5] text-white font-head font-bold px-6 py-3.5 rounded-full transition-colors shadow-[0_0_28px_rgba(88,101,242,0.45)]"
              >
                Join Discord & Verify <ExternalLink size={16} />
              </a>
            </div>

            <div className="lg:col-span-7 grid sm:grid-cols-2 gap-4">
              {DISCORD_STEPS.map((step, i) => (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.35, delay: i * 0.06 }}
                  data-testid={`discord-step-${i + 1}`}
                  className="relative rounded-2xl border border-[#252A3E] bg-[#0F111A] p-5"
                >
                  <span className="absolute top-4 right-4 font-display font-black text-3xl text-white/5">{i + 1}</span>
                  <div className="h-10 w-10 grid place-items-center rounded-xl bg-[#00E5FF]/10 border border-[#00E5FF]/30 text-[#00E5FF]">
                    <step.icon size={18} />
                  </div>
                  <h3 className="font-head font-bold text-white mt-3">{step.title}</h3>
                  <p className="text-slate-400 text-sm mt-1 leading-relaxed">{step.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* PERKS GRID */}
      <section className="border-t border-[#252A3E]">
        <div className="mx-auto max-w-[1400px] px-6 py-16">
          <h2 className="font-display text-2xl sm:text-3xl font-black uppercase text-white mb-8">What holders get</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {PERKS.map((p, i) => (
              <motion.div
                key={p.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.35, delay: i * 0.06 }}
                data-testid={`perk-${i + 1}`}
                className="rounded-2xl border border-[#252A3E] bg-[#161926] p-5 hover:border-[#CCFF00]/40 transition-colors"
              >
                <div className="h-11 w-11 grid place-items-center rounded-xl bg-[#CCFF00]/10 border border-[#CCFF00]/30 text-[#CCFF00]">
                  <p.icon size={20} />
                </div>
                <h3 className="font-head font-bold text-white mt-4">{p.title}</h3>
                <p className="text-slate-400 text-sm mt-1 leading-relaxed">{p.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
