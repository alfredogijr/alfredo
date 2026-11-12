import { Star, Download } from "lucide-react";
import { PROFESSIONALS } from "@/lib/la";

// Weighted score: everyone starts with WEIGHT imaginary ratings of PRIOR stars, so the score only climbs
// with volume. A single 5-star review (4.17) does not outrank forty reviews averaging 4.8 (4.71).
const WEIGHT = 5;
const PRIOR = 4;
const fmt = (v) => (v === null || v === undefined ? "—" : v.toFixed(2).replace(".", ","));

export function buildRanking(responses, prevResponses) {
  const stat = (list, name) => {
    const mine = list.filter((r) => r.professional_name === name && r.professional_rating);
    const sum = mine.reduce((s, r) => s + r.professional_rating, 0);
    return { mine, count: mine.length, avg: mine.length ? sum / mine.length : null, sum };
  };

  return PROFESSIONALS.map((name) => {
    const now = stat(responses, name);
    const before = prevResponses ? stat(prevResponses, name) : null;
    const weighted = now.count ? (WEIGHT * PRIOR + now.sum) / (WEIGHT + now.count) : null;
    return {
      name,
      count: now.count,
      avg: now.avg,
      weighted,
      five: now.count ? Math.round((now.mine.filter((r) => r.professional_rating === 5).length / now.count) * 100) : null,
      low: now.mine.filter((r) => r.professional_rating <= 3).length,
      delta: before && before.avg !== null && now.avg !== null ? now.avg - before.avg : null,
    };
  }).sort((a, b) => (b.weighted ?? -1) - (a.weighted ?? -1) || b.count - a.count);
}

function exportCSV(rows, periodLabel) {
  const head = ["Posição", "Profissional", "Avaliações", "Média simples", "Nota ponderada", "% 5 estrelas", "Notas até 3", "Variação da média"];
  const lines = rows.map((r, i) => [
    r.weighted === null ? "" : i + 1, r.name, r.count,
    r.avg === null ? "" : r.avg.toFixed(2).replace(".", ","),
    r.weighted === null ? "" : r.weighted.toFixed(2).replace(".", ","),
    r.five === null ? "" : r.five + "%", r.low,
    r.delta === null ? "" : r.delta.toFixed(2).replace(".", ","),
  ].join(";"));
  const blob = new Blob(["﻿" + [head.join(";"), ...lines].join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `ranking-la-beauty-concept-${periodLabel.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}

export default function AdminRanking({ responses, prevResponses, periodLabel, onPick, active }) {
  const rows = buildRanking(responses, prevResponses);
  let pos = 0;

  return (
    <section className="mt-10">
      <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
        <div>
          <h2 className="text-2xl text-foreground">Ranking da equipe, {periodLabel.toLowerCase()}</h2>
          <p className="text-sm text-muted-foreground mt-1 max-w-2xl">
            Ordenado pela nota ponderada: cada profissional começa com 5 avaliações imaginárias de nota 4, e a nota sobe conforme as avaliações reais chegam. Assim, uma única nota 5 não passa na frente de quem tem muitas avaliações altas.
          </p>
        </div>
        <button onClick={() => exportCSV(rows, periodLabel)} className="inline-flex items-center gap-2 h-10 px-4 rounded-md border border-border text-sm hover:bg-secondary">
          <Download className="w-4 h-4" /> Exportar ranking
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm min-w-[720px]">
          <thead>
            <tr className="border-b border-foreground/60 text-left text-xs text-muted-foreground">
              <th className="py-2 pr-3 font-medium w-10">#</th>
              <th className="py-2 pr-4 font-medium">Profissional</th>
              <th className="py-2 pr-4 font-medium text-right">Nota ponderada</th>
              <th className="py-2 pr-4 font-medium text-right">Média simples</th>
              <th className="py-2 pr-4 font-medium text-right">Avaliações</th>
              <th className="py-2 pr-4 font-medium text-right">5 estrelas</th>
              <th className="py-2 pr-4 font-medium text-right">Notas até 3</th>
              <th className="py-2 font-medium text-right">Vs anterior</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              if (r.weighted !== null) pos += 1;
              return (
                <tr key={r.name} className={`border-b border-border ${active === r.name ? "bg-secondary" : ""}`}>
                  <td className="py-3 pr-3 tabular-nums text-muted-foreground">{r.weighted === null ? "" : pos}</td>
                  <td className="py-3 pr-4">
                    <button onClick={() => onPick(active === r.name ? "all" : r.name)} className="font-medium text-foreground hover:underline underline-offset-4 text-left">
                      {r.name}
                    </button>
                  </td>
                  <td className="py-3 pr-4 text-right tabular-nums">
                    {r.weighted === null ? <span className="text-muted-foreground">Sem avaliações</span> : (
                      <span className="inline-flex items-center gap-1.5 font-semibold"><Star className="w-4 h-4 fill-accent text-accent" strokeWidth={1.5} />{fmt(r.weighted)}</span>
                    )}
                  </td>
                  <td className="py-3 pr-4 text-right tabular-nums text-foreground/80">{fmt(r.avg)}</td>
                  <td className="py-3 pr-4 text-right tabular-nums">{r.count}</td>
                  <td className="py-3 pr-4 text-right tabular-nums text-foreground/80">{r.five === null ? "—" : `${r.five}%`}</td>
                  <td className={`py-3 pr-4 text-right tabular-nums ${r.low ? "text-destructive" : "text-muted-foreground"}`}>{r.low}</td>
                  <td className="py-3 text-right tabular-nums">
                    {r.delta === null ? <span className="text-muted-foreground">—</span> : Math.abs(r.delta) < 0.05 ? <span className="text-muted-foreground">=</span> : (
                      <span className={r.delta > 0 ? "text-accent" : "text-destructive"}>{r.delta > 0 ? "▲" : "▼"} {Math.abs(r.delta).toFixed(1).replace(".", ",")}</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
