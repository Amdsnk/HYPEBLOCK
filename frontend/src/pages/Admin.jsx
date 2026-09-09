import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { Lock, Download, Trash2, Check, ArrowLeft, RefreshCw } from "lucide-react";
import { API } from "@/config";

export default function Admin() {
  const [key, setKey] = useState("");
  const [authed, setAuthed] = useState(false);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [q, setQ] = useState("");

  const load = async (k) => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/admin/waitlist`, { params: { key: k } });
      setEntries(r.data.entries);
      setAuthed(true);
    } catch (e) {
      toast.error("Key salah. Coba lagi.");
      setAuthed(false);
    } finally {
      setLoading(false);
    }
  };

  const submit = (e) => { e.preventDefault(); load(key); };

  const markContacted = async (id) => {
    await axios.post(`${API}/admin/waitlist/${id}/contacted`, null, { params: { key } });
    setEntries((es) => es.map((x) => (x.id === id ? { ...x, contacted: true } : x)));
    toast.success("Ditandai contacted");
  };

  const del = async (id) => {
    await axios.delete(`${API}/admin/waitlist/${id}`, { params: { key } });
    setEntries((es) => es.filter((x) => x.id !== id));
    toast.success("Entry dihapus");
  };

  const exportCsv = () => {
    const rows = [["email", "wallet", "created_at", "contacted"], ...entries.map((e) => [e.email, e.wallet || "", e.created_at, e.contacted])];
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "hypeblock-waitlist.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  const filtered = entries.filter((e) => e.email.toLowerCase().includes(q.toLowerCase()) || (e.wallet || "").toLowerCase().includes(q.toLowerCase()));

  if (!authed) {
    return (
      <div className="min-h-screen grid place-items-center bg-[#08090D] hb-noise px-6">
        <form onSubmit={submit} className="w-full max-w-sm rounded-3xl border border-[#252A3E] bg-[#0F111A] p-8">
          <div className="h-12 w-12 grid place-items-center rounded-xl bg-[#FF0055]/15 text-[#FF0055] mb-4">
            <Lock size={22} />
          </div>
          <h1 className="font-display text-2xl font-extrabold text-white uppercase">Admin Access</h1>
          <p className="text-slate-400 text-sm mt-1">Masukin key buat lihat waitlist.</p>
          <input data-testid="admin-key-input" type="password" value={key} onChange={(e) => setKey(e.target.value)}
            placeholder="Admin key" autoFocus
            className="mt-5 w-full h-12 rounded-xl bg-[#161926] border border-[#252A3E] px-4 text-white placeholder:text-slate-500 focus:border-[#FF0055] outline-none" />
          <button data-testid="admin-login-btn" disabled={loading}
            className="mt-3 w-full h-12 rounded-xl bg-[#FF0055] hover:bg-[#ff2e73] text-white font-head font-bold transition-colors disabled:opacity-60">
            {loading ? "…" : "Unlock"}
          </button>
          <Link to="/" className="mt-4 inline-flex items-center gap-1.5 text-slate-500 text-sm hover:text-white"><ArrowLeft size={14} /> Back to site</Link>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#08090D] px-6 py-10">
      <div className="mx-auto max-w-[1100px]">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <Link to="/" className="inline-flex items-center gap-1.5 text-slate-500 text-sm hover:text-white mb-2"><ArrowLeft size={14} /> Back to site</Link>
            <h1 className="font-display text-3xl font-black text-white uppercase">Waitlist Admin</h1>
            <p className="font-mono2 text-sm text-slate-400 mt-1"><span className="text-[#00E5FF] font-bold">{entries.length}</span> total signups</p>
          </div>
          <div className="flex items-center gap-2">
            <button data-testid="admin-refresh-btn" onClick={() => load(key)} className="h-11 px-4 rounded-xl border border-[#252A3E] text-white inline-flex items-center gap-2 font-head font-bold text-sm">
              <RefreshCw size={16} /> Refresh
            </button>
            <button data-testid="admin-export-btn" onClick={exportCsv} className="h-11 px-4 rounded-xl bg-[#CCFF00] text-black inline-flex items-center gap-2 font-head font-bold text-sm">
              <Download size={16} /> Export CSV
            </button>
          </div>
        </div>

        <input data-testid="admin-search-input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search email / wallet…"
          className="mt-6 w-full max-w-md h-11 rounded-xl bg-[#161926] border border-[#252A3E] px-4 text-white placeholder:text-slate-500 focus:border-[#00E5FF] outline-none" />

        <div className="mt-6 rounded-2xl border border-[#252A3E] overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#0F111A] text-slate-400 font-mono2 text-xs uppercase">
              <tr>
                <th className="text-left px-4 py-3">Email</th>
                <th className="text-left px-4 py-3 hidden sm:table-cell">Wallet</th>
                <th className="text-left px-4 py-3 hidden md:table-cell">Date</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody data-testid="admin-waitlist-table">
              {filtered.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-12 text-center text-slate-500 font-mono2">Belum ada signup.</td></tr>
              ) : filtered.map((e) => (
                <tr key={e.id} data-testid={`admin-row-${e.id}`} className="border-t border-[#252A3E] hover:bg-[#0F111A]">
                  <td className="px-4 py-3 text-white">{e.email}</td>
                  <td className="px-4 py-3 text-slate-400 font-mono2 text-xs hidden sm:table-cell">{e.wallet ? `${e.wallet.slice(0, 8)}…` : "—"}</td>
                  <td className="px-4 py-3 text-slate-500 font-mono2 text-xs hidden md:table-cell">{new Date(e.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    {e.contacted
                      ? <span className="text-[#CCFF00] font-mono2 text-xs">Contacted</span>
                      : <span className="text-slate-500 font-mono2 text-xs">New</span>}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      {!e.contacted && (
                        <button data-testid={`mark-contacted-${e.id}`} onClick={() => markContacted(e.id)} title="Mark contacted"
                          className="h-8 w-8 grid place-items-center rounded-lg border border-[#252A3E] text-slate-300 hover:text-[#CCFF00] hover:border-[#CCFF00]/50"><Check size={15} /></button>
                      )}
                      <button data-testid={`delete-${e.id}`} onClick={() => del(e.id)} title="Delete"
                        className="h-8 w-8 grid place-items-center rounded-lg border border-[#252A3E] text-slate-300 hover:text-[#FF0055] hover:border-[#FF0055]/50"><Trash2 size={15} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
