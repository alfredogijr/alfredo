// Period filters for the admin: a month, the whole history or a custom range.
const MONTHS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];

export function monthKey(date) {
  const d = new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function monthLabel(key) {
  const [y, m] = key.split("-");
  return `${MONTHS[Number(m) - 1]} de ${y}`;
}

// Months that have data, plus the current one, newest first
export function availableMonths(records) {
  const keys = new Set([monthKey(Date.now())]);
  records.forEach((r) => r.created_date && keys.add(monthKey(r.created_date)));
  return [...keys].sort().reverse();
}

// Returns { start, end } (end exclusive) for the chosen period, or null for the whole history
export function periodRange(period) {
  if (period.type === "month") {
    const [y, m] = period.value.split("-").map(Number);
    return { start: new Date(y, m - 1, 1), end: new Date(y, m, 1) };
  }
  if (period.type === "custom" && period.from && period.to) {
    const start = new Date(period.from + "T00:00:00");
    const end = new Date(period.to + "T00:00:00");
    end.setDate(end.getDate() + 1);
    return { start, end };
  }
  return null;
}

// The period of the same length right before, for comparison
export function previousRange(range, period) {
  if (!range) return null;
  if (period.type === "month") {
    const s = new Date(range.start);
    return { start: new Date(s.getFullYear(), s.getMonth() - 1, 1), end: s };
  }
  const len = range.end - range.start;
  return { start: new Date(range.start.getTime() - len), end: range.start };
}

export function inRange(record, range) {
  if (!range) return true;
  const d = new Date(record.created_date);
  return d >= range.start && d < range.end;
}

export function describePeriod(period) {
  if (period.type === "month") return monthLabel(period.value);
  if (period.type === "custom" && period.from && period.to) {
    const f = (s) => s.split("-").reverse().join("/");
    return `${f(period.from)} a ${f(period.to)}`;
  }
  return "Todo o período";
}
