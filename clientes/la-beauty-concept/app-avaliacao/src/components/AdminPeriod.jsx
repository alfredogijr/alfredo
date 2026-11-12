import { CalendarDays } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { monthLabel } from "@/lib/period";

export default function AdminPeriod({ period, setPeriod, months }) {
  const value = period.type === "month" ? period.value : period.type;

  function onSelect(v) {
    if (v === "all") setPeriod({ type: "all" });
    else if (v === "custom") setPeriod({ type: "custom", from: period.from || "", to: period.to || "" });
    else setPeriod({ type: "month", value: v });
  }

  return (
    <div className="flex flex-col sm:flex-row sm:items-end gap-3">
      <div className="space-y-1.5">
        <label className="text-xs text-muted-foreground">Período</label>
        <Select value={value} onValueChange={onSelect}>
          <SelectTrigger className="h-11 w-full sm:w-64 bg-secondary border-border rounded-md" aria-label="Período">
            <div className="flex items-center gap-2"><CalendarDays className="w-4 h-4 text-accent" /><SelectValue /></div>
          </SelectTrigger>
          <SelectContent>
            {months.map((m, i) => (
              <SelectItem key={m} value={m}>{i === 0 ? `Este mês (${monthLabel(m)})` : monthLabel(m)}</SelectItem>
            ))}
            <SelectItem value="all">Todo o período</SelectItem>
            <SelectItem value="custom">Escolher datas</SelectItem>
          </SelectContent>
        </Select>
      </div>
      {period.type === "custom" && (
        <div className="flex items-end gap-2">
          <div className="space-y-1.5">
            <label htmlFor="de" className="text-xs text-muted-foreground">De</label>
            <Input id="de" type="date" value={period.from} onChange={(e) => setPeriod({ ...period, from: e.target.value })} className="h-11 bg-secondary border-border rounded-md" />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="ate" className="text-xs text-muted-foreground">Até</label>
            <Input id="ate" type="date" value={period.to} onChange={(e) => setPeriod({ ...period, to: e.target.value })} className="h-11 bg-secondary border-border rounded-md" />
          </div>
        </div>
      )}
    </div>
  );
}
