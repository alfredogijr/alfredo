import { Star } from "lucide-react";
import { PROFESSIONALS } from "@/lib/la";

export default function AdminRanking({ responses, onPick, active }) {
  const rows = PROFESSIONALS.map((name) => {
    const mine = responses.filter((r) => r.professional_name === name);
    const avg = mine.length ? mine.reduce((s, r) => s + (r.professional_rating || 0), 0) / mine.length : null;
    const low = mine.filter((r) => (r.professional_rating || 0) <= 3).length;
    return { name, count: mine.length, avg, low };
  }).sort((a, b) => (b.avg ?? -1) - (a.avg ?? -1) || b.count - a.count);

  return (
    <section className="mt-10">
      <h2 className="text-2xl text-foreground mb-1">Atendimento por profissional</h2>
      <p className="text-sm text-muted-foreground mb-4">Toque num nome para ver só as avaliações dele ou dela.</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-foreground/60 text-left text-xs text-muted-foreground">
              <th className="py-2 pr-4 font-medium">Profissional</th>
              <th className="py-2 pr-4 font-medium">Média</th>
              <th className="py-2 pr-4 font-medium text-right">Avaliações</th>
              <th className="py-2 font-medium text-right">Notas até 3</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name} className={`border-b border-border ${active === r.name ? "bg-secondary" : ""}`}>
                <td className="py-3 pr-4">
                  <button onClick={() => onPick(active === r.name ? "all" : r.name)} className="font-medium text-foreground hover:underline underline-offset-4 text-left">
                    {r.name}
                  </button>
                </td>
                <td className="py-3 pr-4">
                  {r.avg === null ? (
                    <span className="text-muted-foreground">Sem avaliações</span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 tabular-nums">
                      <Star className="w-4 h-4 fill-accent text-accent" strokeWidth={1.5} />
                      {r.avg.toFixed(1).replace(".", ",")}
                    </span>
                  )}
                </td>
                <td className="py-3 pr-4 text-right tabular-nums">{r.count}</td>
                <td className={`py-3 text-right tabular-nums ${r.low ? "text-destructive" : "text-muted-foreground"}`}>{r.low}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
