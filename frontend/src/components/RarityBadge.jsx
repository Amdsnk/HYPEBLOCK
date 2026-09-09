import { TIER_STYLES } from "@/config";

export default function RarityBadge({ tier, size = "sm" }) {
  const s = TIER_STYLES[tier] || TIER_STYLES.Common;
  const pad = size === "lg" ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-[11px]";
  return (
    <span
      data-testid={`tier-badge-${tier?.toLowerCase()}`}
      className={`inline-flex items-center gap-1.5 rounded-md border ${s.border} ${s.bg} ${s.text} ${s.glow} ${pad} font-mono2 font-bold uppercase tracking-wider`}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: s.dot, boxShadow: `0 0 8px ${s.dot}` }} />
      {tier}
    </span>
  );
}
