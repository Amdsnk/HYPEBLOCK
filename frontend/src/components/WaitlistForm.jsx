import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Zap } from "lucide-react";
import { API } from "@/config";

export default function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [wallet, setWallet] = useState("");
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(null);

  const loadCount = async () => {
    try {
      const r = await axios.get(`${API}/waitlist/count`);
      setCount(r.data.count);
    } catch (e) { /* noop */ }
  };
  useEffect(() => { loadCount(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    try {
      const r = await axios.post(`${API}/waitlist`, { email, wallet: wallet || null });
      setCount(r.data.count);
      loadCount();
      setEmail(""); setWallet("");
      toast.success("You're in the gang! 🔥", { description: "We'll ping you on the next drop." });
    } catch (err) {
      const msg = err?.response?.data?.detail || "Sign-up failed. Try again.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-3xl border border-[#252A3E] bg-[#0F111A] p-6 sm:p-10 relative overflow-hidden">
      <div className="absolute -top-20 -right-20 h-52 w-52 rounded-full bg-[#FF0055]/20 blur-3xl" />
      <div className="relative">
        <div className="flex items-center gap-2 text-[#CCFF00] font-mono2 text-xs uppercase tracking-[0.25em]">
          <Zap size={14} /> Underground Waitlist
        </div>
        <h3 className="font-display text-2xl sm:text-3xl font-extrabold text-white mt-3 uppercase">
          Join the Gremlin Gang
        </h3>
        <p className="text-slate-400 mt-2 text-sm max-w-lg">
          Staggered drip release ~20–30/week. Sign up to hear about drops first — no spam, just hype.
        </p>

        <form onSubmit={submit} className="mt-6 grid gap-3 sm:grid-cols-[1.4fr_1fr_auto]">
          <input
            data-testid="waitlist-email-input"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email@lo.com"
            className="h-12 rounded-xl bg-[#161926] border border-[#252A3E] px-4 text-white placeholder:text-slate-500 focus:border-[#FF0055] outline-none transition-colors"
          />
          <input
            data-testid="waitlist-wallet-input"
            type="text"
            value={wallet}
            onChange={(e) => setWallet(e.target.value)}
            placeholder="0x… wallet (optional)"
            className="h-12 rounded-xl bg-[#161926] border border-[#252A3E] px-4 text-white placeholder:text-slate-500 focus:border-[#00E5FF] outline-none transition-colors font-mono2 text-sm"
          />
          <button
            data-testid="waitlist-submit-btn"
            disabled={loading}
            className="h-12 px-6 rounded-xl bg-[#FF0055] hover:bg-[#ff2e73] disabled:opacity-60 text-white font-head font-bold transition-colors shadow-[0_0_20px_rgba(255,0,85,0.4)] whitespace-nowrap"
          >
            {loading ? "…" : "Join Gang"}
          </button>
        </form>

        {count !== null && (
          <p data-testid="waitlist-count" className="mt-4 font-mono2 text-xs text-slate-400">
            <span className="text-[#00E5FF] font-bold">{count}</span> gremlins already in the waitlist
          </p>
        )}
      </div>
    </div>
  );
}
