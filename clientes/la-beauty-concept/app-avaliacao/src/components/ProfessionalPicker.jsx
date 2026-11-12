import { Check } from "lucide-react";
import { PROFESSIONALS } from "@/lib/la";

function initials(name) {
  const parts = name.split(" ");
  return (parts[0][0] + (parts[parts.length - 1][0] || "")).toUpperCase();
}

export default function ProfessionalPicker({ value, onChange }) {
  return (
    <div className="grid grid-cols-2 gap-2" role="radiogroup" aria-label="Quem te atendeu hoje?">
      {PROFESSIONALS.map((name) => {
        const selected = value === name;
        return (
          <button
            key={name}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(name)}
            className={`relative flex items-center gap-3 px-3 min-h-[64px] rounded-md border text-left transition-colors ${
              selected
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border bg-secondary text-foreground hover:border-foreground/40"
            }`}
          >
            <span
              className={`w-9 h-9 shrink-0 rounded-full flex items-center justify-center text-xs font-semibold ${
                selected ? "bg-primary-foreground text-primary" : "bg-muted text-foreground/80"
              }`}
            >
              {selected ? <Check className="w-4 h-4" strokeWidth={3} /> : initials(name)}
            </span>
            <span className="text-sm font-medium leading-tight">{name}</span>
          </button>
        );
      })}
    </div>
  );
}
