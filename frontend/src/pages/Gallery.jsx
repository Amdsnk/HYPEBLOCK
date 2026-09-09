import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { SlidersHorizontal, Search, X, ChevronLeft, ChevronRight } from "lucide-react";
import { API, TIER_STYLES } from "@/config";
import NftCard from "@/components/NftCard";

const FILTER_CATS = ["Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory"];
const SORTS = [
  { v: "rank_asc", l: "Rank (Rarest first)" },
  { v: "id_asc", l: "ID: #001 → #096" },
  { v: "id_desc", l: "ID: #096 → #001" },
  { v: "price_desc", l: "Price: High → Low" },
  { v: "price_asc", l: "Price: Low → High" },
];
const LIMIT = 24;

export default function Gallery() {
  const [traits, setTraits] = useState({});
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [tier, setTier] = useState("");
  const [sort, setSort] = useState("rank_asc");
  const [filters, setFilters] = useState({});
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    axios.get(`${API}/traits`).then((r) => setTraits(r.data.counts || {})).catch(() => {});
  }, []);

  const fetchNfts = useCallback(async () => {
    setLoading(true);
    const params = { sort, page, limit: LIMIT };
    if (tier) params.tier = tier;
    if (search) params.search = search;
    Object.entries(filters).forEach(([k, v]) => { if (v) params[k.toLowerCase()] = v; });
    try {
      const r = await axios.get(`${API}/nfts`, { params });
      setItems(r.data.items);
      setTotal(r.data.total);
    } catch (e) { /* noop */ }
    setLoading(false);
  }, [sort, page, tier, search, filters]);

  useEffect(() => { fetchNfts(); }, [fetchNfts]);
  useEffect(() => { setPage(1); }, [tier, search, filters, sort]);

  const setFilter = (cat, val) => setFilters((f) => ({ ...f, [cat]: f[cat] === val ? "" : val }));
  const clearAll = () => { setFilters({}); setTier(""); setSearch(""); };
  const totalPages = Math.max(1, Math.ceil(total / LIMIT));
  const activeCount = Object.values(filters).filter(Boolean).length + (tier ? 1 : 0);

  const FilterPanel = (
    <div className="space-y-6 hb-scroll">
      <div>
        <p className="font-mono2 text-[11px] uppercase tracking-[0.2em] text-slate-500 mb-2">Rarity Tier</p>
        <div className="flex flex-wrap gap-2">
          {["Common", "Rare", "Epic", "Legendary", "Mythic"].map((t) => {
            const s = TIER_STYLES[t];
            const active = tier === t;
            return (
              <button key={t} data-testid={`rarity-filter-${t.toLowerCase()}`} onClick={() => setTier(active ? "" : t)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-mono2 font-bold uppercase transition-all ${active ? `${s.border} ${s.bg} ${s.text}` : "border-[#252A3E] text-slate-400 hover:border-slate-500"}`}>
                {t}
              </button>
            );
          })}
        </div>
      </div>
      {FILTER_CATS.map((cat) => {
        const opts = Object.keys(traits[cat] || {}).sort();
        if (!opts.length) return null;
        return (
          <div key={cat}>
            <p className="font-mono2 text-[11px] uppercase tracking-[0.2em] text-slate-500 mb-2">{cat}</p>
            <div className="flex flex-wrap gap-1.5">
              {opts.map((o) => {
                const active = filters[cat] === o;
                return (
                  <button key={o} data-testid={`filter-${cat.toLowerCase()}-${o.toLowerCase().replace(/\s+/g, "-")}`}
                    onClick={() => setFilter(cat, o)}
                    className={`px-2.5 py-1 rounded-md border text-[11px] transition-all ${active ? "border-[#FF0055] bg-[#FF0055]/10 text-[#FF0055]" : "border-[#252A3E] text-slate-400 hover:border-slate-500"}`}>
                    {o} <span className="text-slate-600">{traits[cat][o]}</span>
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="pt-16">
      <div className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="flex items-end justify-between flex-wrap gap-4">
          <div>
            <p className="font-mono2 text-xs uppercase tracking-[0.25em] text-[#CCFF00]">The Collection</p>
            <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl font-black uppercase text-white mt-2">The Gremlins</h1>
          </div>
          <p className="font-mono2 text-sm text-slate-400"><span className="text-[#00E5FF] font-bold">{total}</span> results</p>
        </div>

        {/* Toolbar */}
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input data-testid="nft-search-input" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Search ID (#42) or name…"
              className="w-full h-11 rounded-xl bg-[#161926] border border-[#252A3E] pl-9 pr-3 text-white placeholder:text-slate-500 focus:border-[#00E5FF] outline-none" />
          </div>
          <select data-testid="sort-select" value={sort} onChange={(e) => setSort(e.target.value)}
            className="h-11 rounded-xl bg-[#161926] border border-[#252A3E] px-3 text-sm text-white outline-none focus:border-[#00E5FF]">
            {SORTS.map((s) => <option key={s.v} value={s.v}>{s.l}</option>)}
          </select>
          <button data-testid="toggle-filters-btn" onClick={() => setShowFilters(!showFilters)}
            className="lg:hidden h-11 px-4 rounded-xl border border-[#252A3E] text-white inline-flex items-center gap-2 font-head font-bold text-sm">
            <SlidersHorizontal size={16} /> Filters {activeCount > 0 && <span className="bg-[#FF0055] text-white rounded-full px-1.5 text-[11px]">{activeCount}</span>}
          </button>
          {activeCount > 0 && (
            <button data-testid="clear-filters-btn" onClick={clearAll} className="h-11 px-3 rounded-xl text-slate-400 hover:text-white inline-flex items-center gap-1 text-sm">
              <X size={15} /> Clear
            </button>
          )}
        </div>

        <div className="mt-8 grid lg:grid-cols-[260px_1fr] gap-8">
          {/* Sidebar desktop */}
          <aside className="hidden lg:block sticky top-24 self-start max-h-[calc(100vh-120px)] overflow-y-auto pr-2 hb-scroll">
            {FilterPanel}
          </aside>

          {/* Mobile filter drawer */}
          {showFilters && (
            <div className="lg:hidden fixed inset-0 z-50 bg-black/70" onClick={() => setShowFilters(false)}>
              <div className="absolute right-0 top-0 h-full w-[85%] max-w-sm bg-[#0F111A] border-l border-[#252A3E] p-5 overflow-y-auto hb-scroll" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-4">
                  <p className="font-display font-extrabold text-white">Filters</p>
                  <button onClick={() => setShowFilters(false)} className="text-slate-400"><X size={22} /></button>
                </div>
                {FilterPanel}
              </div>
            </div>
          )}

          {/* Grid */}
          <div>
            {loading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="aspect-square rounded-2xl bg-[#161926] animate-pulse" />
                ))}
              </div>
            ) : items.length === 0 ? (
              <div className="py-24 text-center text-slate-500 font-mono2">No gremlins match — try clearing the filters.</div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                {items.map((n) => <NftCard key={n.token_id} nft={n} />)}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-10 flex items-center justify-center gap-3">
                <button data-testid="page-prev" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="h-10 w-10 grid place-items-center rounded-lg border border-[#252A3E] text-white disabled:opacity-40 hover:border-[#00E5FF]/60">
                  <ChevronLeft size={18} />
                </button>
                <span className="font-mono2 text-sm text-slate-300">Page {page} / {totalPages}</span>
                <button data-testid="page-next" disabled={page >= totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="h-10 w-10 grid place-items-center rounded-lg border border-[#252A3E] text-white disabled:opacity-40 hover:border-[#00E5FF]/60">
                  <ChevronRight size={18} />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
