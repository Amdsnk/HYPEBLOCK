import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { FlaskConical, Shuffle, RotateCcw } from "lucide-react";
import { API, TIER_STYLES } from "@/config";
import RarityBadge from "@/components/RarityBadge";

const CATS = ["Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory"];

export default function TraitLab() {
  const [counts, setCounts] = useState({});
  const [sel, setSel] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API}/traits`).then((r) => {
      const c = r.data.counts || {};
      setCounts(c);
      // default: first value in each category
      const init = {};
      CATS.forEach((cat) => {
        const keys = Object.keys(c[cat] || {});
        if (keys.length) init[cat] = keys[0];
      });
      setSel(init);
    });
  }, []);

  useEffect(() => {
    if (Object.keys(sel).length === 0) return;
    setLoading(true);
    const t = setTimeout(() => {
      axios.post(`${API}/trait-lab/estimate`, { traits: sel })
        .then((r) => setResult(r.data))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [sel]);

  const options = useMemo(() => {
    const o = {};
    CATS.forEach((cat) => { o[cat] = Object.keys(counts[cat] || {}).sort(); });
    return o;
  }, [counts]);

  const randomize = () => {
    const next = {};
    CATS.forEach((cat) => {
      const keys = options[cat] || [];
      if (keys.length) next[cat] = keys[Math.floor(Math.random() * keys.length)];
    });
    setSel(next);
  };

  const reset = () => {
    const init = {};
    CATS.forEach((cat) => { const k = options[cat] || []; if (k.length) init[cat] = k[0]; });
    setSel(init);
  };

  const s = result ? TIER_STYLES[result.tier_guess] : TIER_STYLES.Common;

  return (
    <div className="pt-24 pb-20">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="flex items-center gap-2 text-[#CCFF00] font-mono2 text-xs uppercase tracking-[0.25em]">
          <FlaskConical size={15} /> Interactive
        </div>
        <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl font-black uppercase text-white mt-2">Trait Lab</h1>
        <p className="text-slate-400 mt-3 max-w-2xl">
          Mix &amp; match traits and see a live rarity estimate — score, tier and where it would rank in the 200.
          Great for planning which gremlin to hunt.
        </p>

        <div className="mt-8 grid lg:grid-cols-[1.5fr_1fr] gap-8">
          {/* PICKERS */}
          <div className="space-y-5">
            <div className="flex gap-3">
              <button data-testid="trait-lab-randomize" onClick={randomize}
                className="inline-flex items-center gap-2 bg-[#9D00FF] hover:bg-[#b23bff] text-white font-head font-bold px-4 py-2.5 rounded-xl text-sm transition-colors">
                <Shuffle size={15} /> Randomize
              </button>
              <button data-testid="trait-lab-reset" onClick={reset}
                className="inline-flex items-center gap-2 border border-[#252A3E] hover:border-slate-500 text-white font-head font-bold px-4 py-2.5 rounded-xl text-sm transition-colors">
                <RotateCcw size={15} /> Reset
              </button>
            </div>

            {CATS.map((cat) => (
              <div key={cat}>
                <p className="font-mono2 text-[11px] uppercase tracking-[0.2em] text-slate-500 mb-2">{cat}</p>
                <div className="flex flex-wrap gap-2">
                  {(options[cat] || []).map((val) => {
                    const active = sel[cat] === val;
                    const pct = counts[cat]?.[val] ? Math.round((counts[cat][val] / 200) * 100) : 0;
                    return (
                      <button
                        key={val}
                        data-testid={`trait-opt-${cat}-${val}`.replace(/\s+/g, "-")}
                        onClick={() => setSel((p) => ({ ...p, [cat]: val }))}
                        className={`px-3 py-1.5 rounded-lg border text-xs font-mono2 font-bold transition-all ${active
                          ? "border-[#00E5FF] bg-[#00E5FF]/10 text-[#00E5FF]"
                          : "border-[#252A3E] text-slate-300 hover:border-slate-500"}`}
                      >
                        {val} <span className="text-slate-500">· {pct}%</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* RESULT */}
          <div className="lg:sticky lg:top-24 h-fit">
            <div className={`rounded-3xl border ${s.border} bg-[#0F111A] p-6 ${s.glow}`}>
              <p className="font-mono2 text-[11px] uppercase tracking-[0.25em] text-slate-500">Estimated Tier</p>
              <div className="mt-2" data-testid="trait-lab-tier">
                {result ? <RarityBadge tier={result.tier_guess} size="lg" /> : <span className="text-slate-500">—</span>}
              </div>

              <div className="mt-6 grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-[#252A3E] bg-[#0B0C12] p-4">
                  <p className="font-mono2 text-[10px] uppercase tracking-[0.2em] text-slate-500">Rarity Score</p>
                  <p className="font-display font-black text-2xl mt-1" data-testid="trait-lab-score" style={{ color: s.dot }}>
                    {loading ? "…" : result?.score ?? "—"}
                  </p>
                </div>
                <div className="rounded-xl border border-[#252A3E] bg-[#0B0C12] p-4">
                  <p className="font-mono2 text-[10px] uppercase tracking-[0.2em] text-slate-500">Est. Rank</p>
                  <p className="font-display font-black text-2xl mt-1 text-white">
                    {loading ? "…" : result ? `#${result.rank_estimate}` : "—"}
                  </p>
                </div>
              </div>

              {result && (
                <div className="mt-4">
                  <div className="flex items-center justify-between font-mono2 text-xs text-slate-400 mb-1">
                    <span>Rarer than</span>
                    <span className="text-[#CCFF00] font-bold">{result.percentile}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-[#161926] overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${result.percentile}%`, background: s.dot }} />
                  </div>
                </div>
              )}

              <div className="mt-6 space-y-2">
                <p className="font-mono2 text-[11px] uppercase tracking-[0.2em] text-slate-500">Your Combo</p>
                {CATS.map((cat) => (
                  <div key={cat} className="flex items-center justify-between text-sm border-b border-[#161926] py-1.5">
                    <span className="text-slate-400">{cat}</span>
                    <span className="text-white font-head font-bold">
                      {sel[cat] || "—"}
                      {result?.per_trait_pct?.[cat] != null && (
                        <span className="text-[#00E5FF] font-mono2 text-[11px] ml-2">{result.per_trait_pct[cat]}%</span>
                      )}
                    </span>
                  </div>
                ))}
              </div>
              <p className="text-slate-500 text-[11px] mt-4 font-mono2">
                Estimate only — final tier is fixed per token in the collection.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
