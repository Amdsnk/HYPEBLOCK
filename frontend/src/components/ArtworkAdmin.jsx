import { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { API } from "@/config";

export default function ArtworkAdmin({ adminKey }) {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [traitsMatch, setTraitsMatch] = useState(false);
  const [directionChecked, setDirectionChecked] = useState(false);
  const [original, setOriginal] = useState(false);
  const [busy, setBusy] = useState(false);
  const [cid, setCid] = useState("");
  const [release, setRelease] = useState([]);
  const config = { headers: { "X-Admin-Key": adminKey } };
  const load = async () => {
    const r = await axios.get(`${API}/admin/artwork`, config);
    setItems(r.data.items);
  };
  useEffect(() => { load().catch(() => toast.error("Could not load artwork")); }, [adminKey]); // eslint-disable-line react-hooks/exhaustive-deps
  const error = (e) => toast.error(e.response?.data?.detail || "Artwork action failed");
  const update = (item) => {
    setItems((all) => all.map((x) => x.token_id === item.token_id ? item : x));
    setSelected(item); setTraitsMatch(false); setOriginal(false); setDirectionChecked(false);
    setRelease((ids) => ids.filter((id) => id !== item.token_id));
  };
  const upload = async (file) => {
    if (!file || !selected) return;
    setBusy(true);
    try {
      const r = await axios.put(`${API}/admin/artwork/${selected.token_id}`, file, {
        headers: { "X-Admin-Key": adminKey, "Content-Type": file.type || "application/octet-stream" },
      });
      update(r.data); toast.success("Artwork uploaded for review");
    } catch (e) { error(e); } finally { setBusy(false); }
  };
  const review = async (approved) => {
    setBusy(true);
    try {
      const r = await axios.post(`${API}/admin/artwork/${selected.token_id}/review`, {
        sha256: selected.sha256, approved, traits_match: traitsMatch, original_artwork: original, art_direction_checked: directionChecked,
      }, config);
      update(r.data); toast.success(approved ? "Artwork approved" : "Approval removed");
    } catch (e) { error(e); } finally { setBusy(false); }
  };
  const exportRelease = async (imagesOnly = false) => {
    setBusy(true);
    try {
      const r = await axios.post(`${API}/admin/release/${imagesOnly ? "images" : "export"}`, { token_ids: release, image_folder_cid: cid }, { ...config, responseType: "blob" });
      const url = URL.createObjectURL(r.data); const a = document.createElement("a");
      a.href = url; a.download = imagesOnly ? "hypeblock-approved-images.zip" : "hypeblock-release.zip"; a.click(); URL.revokeObjectURL(url);
      toast.success("Release pack downloaded");
    } catch (e) {
      if (e.response?.data instanceof Blob) {
        try { toast.error(JSON.parse(await e.response.data.text()).detail); } catch { error(e); }
      } else error(e);
    } finally { setBusy(false); }
  };
  const visible = items.filter((x) => (filter === "all" || x.artwork_state === filter) && `${x.token_id} ${x.name}`.toLowerCase().includes(search.toLowerCase()));
  const button = "rounded-xl px-4 py-3 bg-[#00E5FF] text-black font-bold disabled:opacity-40";
  return <section className="mt-12 border-t border-[#252A3E] pt-8 text-white">
    <h2 className="font-display text-3xl font-black uppercase">Genesis Artwork Studio</h2>
    <p className="text-slate-400 mt-2">Review each character against its traits. Only approved artwork can enter a release pack.</p>
    <div className="grid sm:grid-cols-3 gap-3 mt-5">
      {["canonical", "candidate", "placeholder"].map((state) => <button key={state} onClick={() => { setFilter(state); setPage(1); }} className="rounded-2xl border border-[#252A3E] p-5 text-left bg-[#0F111A]">
        <strong className="text-3xl text-[#CCFF00]">{items.filter((x) => x.artwork_state === state).length}</strong>
        <p className="capitalize mt-1">{state === "canonical" ? "Approved" : state === "candidate" ? "Needs review" : "Needs final art"}</p>
      </button>)}
    </div>
    <div className="flex gap-3 mt-5 flex-wrap">
      <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder="Find ID or character" className="rounded-xl bg-[#161926] border border-[#252A3E] px-4 py-3" />
      <button onClick={() => { setFilter("all"); setPage(1); }} className="px-4 text-slate-300">All characters</button>
    </div>
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mt-5">
      {visible.slice((page - 1) * 12, page * 12).map((item) => <button key={item.token_id} onClick={() => { setSelected(item); setTraitsMatch(false); setOriginal(false); setDirectionChecked(false); }} className="rounded-2xl bg-[#161926] border border-[#252A3E] overflow-hidden text-left">
        <img src={`${API.replace(/\/api$/, "")}${item.image}`} alt={item.name} className="w-full aspect-square object-cover" loading="lazy" />
        <div className="p-3"><p className="font-bold">#{item.token_id} {item.name}</p><p className="text-xs text-slate-400 mt-1">{item.tier} · {item.artwork_state}</p></div>
      </button>)}
    </div>
    <div className="flex items-center justify-between mt-4">
      <button disabled={page === 1} onClick={() => setPage((p) => p - 1)} className="p-3 disabled:opacity-30">Previous</button>
      <span className="text-slate-400">{page} / {Math.max(1, Math.ceil(visible.length / 12))}</span>
      <button disabled={page * 12 >= visible.length} onClick={() => setPage((p) => p + 1)} className="p-3 disabled:opacity-30">Next</button>
    </div>
    {selected && <div className="mt-6 rounded-2xl border border-[#00E5FF]/40 bg-[#0F111A] p-5 grid md:grid-cols-2 gap-6">
      <img src={`${API.replace(/\/api$/, "")}${selected.image}`} alt={selected.name} className="w-full rounded-xl aspect-square object-cover" />
      <div><h3 className="text-2xl font-bold">#{selected.token_id} {selected.name}</h3>
        {selected.review_notes?.map((note) => <p key={note} className="mt-3 rounded-lg bg-amber-500/10 border border-amber-500/30 p-3 text-amber-200 text-sm">{note}</p>)}
        <dl className="grid grid-cols-2 gap-2 my-4">{Object.entries(selected.traits).map(([k,v]) => <div key={k} className="bg-[#161926] rounded-lg p-2"><dt className="text-xs text-slate-400">{k}</dt><dd>{v}</dd></div>)}</dl>
        <label className="block text-sm text-slate-400">Replace with final artwork (PNG/JPEG/WebP, up to 8 MB)
          <input disabled={busy} type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => upload(e.target.files[0])} className="block mt-2 w-full" />
        </label>
        <label className="flex gap-2 mt-5"><input type="checkbox" checked={traitsMatch} onChange={(e) => setTraitsMatch(e.target.checked)} />I checked that the image matches every trait above.</label>
        <label className="flex gap-2 mt-3"><input type="checkbox" checked={original} onChange={(e) => setOriginal(e.target.checked)} />This is final original art, not a recolor, crop, or placeholder.</label>
        <label className="flex gap-2 mt-3"><input type="checkbox" checked={directionChecked} onChange={(e) => setDirectionChecked(e.target.checked)} />Exactly two eyes; readable HYPEBLOCK branding and detailed traits; intact skin and ears without wounds, scars, blood or skin stitches; males follow the original compact cartoon Grim proportions.</label>
        <div className="flex flex-wrap gap-2 mt-4">
          <button className={button} disabled={busy || !selected.sha256 || !traitsMatch || !original || !directionChecked} onClick={() => review(true)}>Approve artwork</button>
          {selected.artwork_state === "canonical" && <button className="px-4 border border-[#252A3E] rounded-xl" disabled={busy} onClick={() => review(false)}>Remove approval</button>}
        </div>
      </div>
    </div>}
    <div className="mt-8 rounded-2xl border border-[#252A3E] bg-[#0F111A] p-5">
      <h3 className="text-xl font-bold">Release pack</h3><p className="text-slate-400 text-sm mt-2">Choose approved characters, enter the actual IPFS image folder CID, and export images, per-token metadata and a hash manifest. Exporting does not mint NFTs.</p>
      <div className="flex flex-wrap gap-2 mt-4">{items.filter((x) => x.artwork_state === "canonical").map((item) => <label key={item.token_id} className="p-2 rounded-lg bg-[#161926] flex gap-2"><input type="checkbox" checked={release.includes(item.token_id)} onChange={(e) => setRelease((ids) => e.target.checked ? [...ids,item.token_id] : ids.filter((id) => id !== item.token_id))} />#{item.token_id}</label>)}</div>
      <button className={`${button} mt-4`} disabled={busy || !release.length} onClick={() => exportRelease(true)}>1. Download approved images</button>
      <p className="mt-3 text-sm text-slate-400">2. Upload the images folder to your IPFS provider, then paste its CID below.</p>
      <input value={cid} onChange={(e) => setCid(e.target.value)} placeholder="IPFS image folder CID" className="w-full mt-4 rounded-xl bg-[#161926] border border-[#252A3E] px-4 py-3" />
      <button className={`${button} mt-3`} disabled={busy || !cid || !release.length} onClick={() => exportRelease(false)}>Export {release.length} approved characters</button>
    </div>
  </section>;
}
