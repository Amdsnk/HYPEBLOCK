import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { ExternalLink, Menu, X, Wallet } from "lucide-react";
import { LINKS, CREATOR_WALLET } from "@/config";

const NAV = [
  { label: "Showcase", to: "/#showcase" },
  { label: "The Gremlins", to: "/gremlins" },
  { label: "Trait Lab", to: "/trait-lab" },
  { label: "Roadmap", to: "/#roadmap" },
  { label: "FAQ", to: "/#faq" },
  { label: "Waitlist", to: "/#waitlist" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const nav = useNavigate();

  const go = (to) => {
    setOpen(false);
    if (to.startsWith("/#")) {
      const id = to.slice(2);
      if (window.location.pathname !== "/") {
        nav("/");
        setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }), 120);
      } else {
        document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
      }
    } else {
      nav(to);
      window.scrollTo(0, 0);
    }
  };

  return (
    <header className="fixed top-0 left-0 z-50 w-full backdrop-blur-xl bg-[#08090D]/85 border-b border-[#252A3E]">
      <div className="mx-auto max-w-[1400px] px-4 sm:px-6 h-16 flex items-center justify-between">
        <button data-testid="logo-home-btn" onClick={() => go("/")} className="flex items-center gap-2 group">
          <span className="inline-block h-7 w-7 rounded-[6px] bg-[#FF0055] rotate-[-4deg] shadow-[0_0_16px_rgba(255,0,85,0.6)] group-hover:rotate-3 transition-transform" />
          <span className="font-display text-lg sm:text-xl font-extrabold tracking-tight text-white neon-pink-text">HYPEBLOCK</span>
        </button>

        <nav className="hidden lg:flex items-center gap-7">
          {NAV.map((n) => (
            <button
              key={n.label}
              data-testid={`nav-${n.label.toLowerCase().replace(/\s+/g, "-")}`}
              onClick={() => go(n.to)}
              className="font-head text-sm font-semibold text-slate-300 hover:text-[#00E5FF] transition-colors uppercase tracking-wide"
            >
              {n.label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <span className="hidden md:inline-flex items-center gap-1.5 font-mono2 text-[11px] text-slate-400 border border-[#252A3E] rounded-full px-3 py-1.5">
            <Wallet size={13} className="text-[#CCFF00]" />
            {CREATOR_WALLET.slice(0, 5)}…{CREATOR_WALLET.slice(-4)}
          </span>
          <a
            data-testid="nav-view-rarible-btn"
            href={LINKS.rarible}
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 bg-[#FF0055] hover:bg-[#ff2e73] text-white font-head font-bold text-sm px-4 py-2 rounded-full transition-colors shadow-[0_0_20px_rgba(255,0,85,0.4)]"
          >
            View on Rarible <ExternalLink size={15} />
          </a>
          <button data-testid="mobile-menu-btn" className="lg:hidden text-white p-2" onClick={() => setOpen(!open)}>
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {open && (
        <div className="lg:hidden border-t border-[#252A3E] bg-[#0F111A] px-4 py-4 flex flex-col gap-1">
          {NAV.map((n) => (
            <button
              key={n.label}
              data-testid={`mobile-nav-${n.label.toLowerCase().replace(/\s+/g, "-")}`}
              onClick={() => go(n.to)}
              className="text-left font-head font-semibold text-slate-200 py-2.5 uppercase text-sm"
            >
              {n.label}
            </button>
          ))}
          <a href={LINKS.rarible} target="_blank" rel="noreferrer" className="mt-2 inline-flex items-center justify-center gap-1.5 bg-[#FF0055] text-white font-bold text-sm px-4 py-2.5 rounded-full">
            View on Rarible <ExternalLink size={15} />
          </a>
        </div>
      )}
    </header>
  );
}
