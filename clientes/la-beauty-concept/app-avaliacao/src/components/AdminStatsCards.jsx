export default function AdminStatsCards({ responses, coupons }) {
  const n = responses.length;
  const avg = (key) => (n ? (responses.reduce((s, r) => s + (r[key] || 0), 0) / n).toFixed(1).replace(".", ",") : "—");
  const redeemed = coupons.filter((c) => c.redeemed).length;

  const stats = [
    { label: "Avaliações", value: n },
    { label: "Nota do atendimento", value: avg("professional_rating") },
    { label: "Nota do salão", value: avg("experience_rating") },
    { label: "Cupons resgatados", value: `${redeemed} de ${coupons.length}` },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 border-y border-border divide-x divide-border">
      {stats.map((s) => (
        <div key={s.label} className="p-4">
          <p className="text-3xl text-foreground tabular-nums" style={{ fontFamily: "var(--font-heading)" }}>{s.value}</p>
          <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
