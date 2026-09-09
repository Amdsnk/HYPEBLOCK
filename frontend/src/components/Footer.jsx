import { Twitter, Instagram, MessageCircle, ExternalLink } from "lucide-react";
import { LINKS, CREATOR_WALLET } from "@/config";

export default function Footer() {
  return (
    <footer className="border-t border-[#252A3E] bg-[#0B0C12] mt-24">
      <div className="mx-auto max-w-[1400px] px-6 py-12 grid gap-8 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-6 w-6 rounded-[5px] bg-[#FF0055] rotate-[-4deg]" />
            <span className="font-display text-lg font-extrabold text-white">HYPEBLOCK</span>
          </div>
          <p className="mt-3 text-sm text-slate-400 max-w-xs leading-relaxed">
            96 original graffiti gremlin PFPs. Underground collective. Polygon · ERC-721 · Free lazy mint.
          </p>
        </div>
        <div className="font-mono2 text-xs text-slate-500 space-y-2">
          <p className="text-slate-400 uppercase tracking-[0.2em]">Contract</p>
          <p className="break-all">Creator: {CREATOR_WALLET}</p>
          <p>Network: Polygon (MATIC) · Royalty 5–10%</p>
        </div>
        <div className="flex md:justify-end items-start gap-3">
          {[
            { icon: Twitter, url: LINKS.twitter, id: "x" },
            { icon: Instagram, url: LINKS.instagram, id: "ig" },
            { icon: MessageCircle, url: LINKS.discord, id: "discord" },
          ].map(({ icon: Icon, url, id }) => (
            <a
              key={id}
              data-testid={`footer-social-${id}`}
              href={url}
              target="_blank"
              rel="noreferrer"
              className="h-11 w-11 grid place-items-center rounded-xl border border-[#252A3E] text-slate-300 hover:text-[#00E5FF] hover:border-[#00E5FF]/60 transition-colors"
            >
              <Icon size={18} />
            </a>
          ))}
          <a
            data-testid="footer-rarible"
            href={LINKS.rarible}
            target="_blank"
            rel="noreferrer"
            className="h-11 px-4 grid place-items-center rounded-xl bg-[#FF0055] text-white font-bold text-sm gap-1.5 flex items-center"
          >
            Rarible <ExternalLink size={14} />
          </a>
        </div>
      </div>
      <div className="border-t border-[#252A3E] py-5 text-center text-xs text-slate-600 font-mono2">
        © 2026 HYPEBLOCK Graffiti Gremlin Collective — Art-only showcase.
      </div>
    </footer>
  );
}
