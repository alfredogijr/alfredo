function mean(list, key) {
  return list.length ? list.reduce((s, r) => s + (r[key] || 0), 0) / list.length : null;
}
const fmt = (v) => (v === null ? "—" : v.toFixed(1).replace(".", ","));

function Delta({ now, before, suffix = "" }) {
  if (now === null || before === null || before === undefined) return null;
  const d = now - before;
  if (Math.abs(d) < 0.05) return <span className="text-xs text-muted-foreground">igual ao período anterior</span>;
  const up = d > 0;
  return (
    <span className={`text-xs ${up ? "text-accent" : "text-destructive"}`}>
      {up ? "▲" : "▼"} {Math.abs(d).toFixed(suffix ? 0 : 1).replace(".", ",")}{suffix} vs período anterior
    </span>
  );
}

export default function AdminStatsCards({ responses, coupons, prevResponses }) {
  const n = responses.length;
  const redeemed = coupons.filter((c) => c.redeemed).length;
  const prev = prevResponses;

  const stats = [
    { label: "Avaliações", value: String(n), delta: prev && <Delta now={n} before={prev.length} suffix="" /> },
    { label: "Nota do atendimento", value: fmt(mean(responses, "professional_rating")), delta: prev && <Delta now={mean(responses, "professional_rating")} before={mean(prev, "professional_rating")} /> },
    { label: "Nota do salão", value: fmt(mean(responses, "experience_rating")), delta: prev && <Delta now={mean(responses, "experience_rating")} before={mean(prev, "experience_rating")} /> },
    { label: "Cupons resgatados", value: `${redeemed} de ${coupons.length}` },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 border-y border-border divide-x divide-border">
      {stats.map((s) => (
        <div key={s.label} className="p-4 space-y-1">
          <p className="text-3xl text-foreground tabular-nums" style={{ fontFamily: "var(--font-heading)" }}>{s.value}</p>
          <p className="text-xs text-muted-foreground">{s.label}</p>
          {s.delta}
        </div>
      ))}
    </div>
  );
}
