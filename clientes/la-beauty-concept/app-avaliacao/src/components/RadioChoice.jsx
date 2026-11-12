import { Check } from "lucide-react";

export default function RadioChoice({ label, options, value, onChange, multi = false }) {
  const isSelected = (opt) => (multi ? (value || []).includes(opt) : value === opt);

  function handleClick(opt) {
    if (multi) {
      const arr = value || [];
      onChange(arr.includes(opt) ? arr.filter((o) => o !== opt) : [...arr, opt]);
    } else {
      onChange(opt);
    }
  }

  return (
    <div className="space-y-3">
      <p className="text-base text-foreground/90">{label}</p>
      {multi && <p className="text-xs text-muted-foreground -mt-2">Pode marcar mais de um</p>}
      <div className="space-y-2">
        {options.map((opt) => {
          const selected = isSelected(opt);
          return (
            <button
              key={opt}
              type="button"
              aria-pressed={selected}
              onClick={() => handleClick(opt)}
              className={`w-full flex items-center gap-3 px-4 min-h-[52px] rounded-md border text-left text-sm transition-colors ${
                selected
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-secondary text-foreground/85 hover:border-foreground/40"
              }`}
            >
              <span
                className={`w-5 h-5 ${multi ? "rounded-sm" : "rounded-full"} border flex items-center justify-center shrink-0 ${
                  selected ? "border-primary-foreground bg-primary-foreground" : "border-muted-foreground/50"
                }`}
              >
                {selected && <Check className="w-3 h-3 text-primary" strokeWidth={3} />}
              </span>
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}
