import { Star } from "lucide-react";
import { useState } from "react";

const WORDS = ["", "Ruim", "Regular", "Bom", "Muito bom", "Excelente"];

export default function StarRating({ value, onChange, label, size = "md" }) {
  const [hover, setHover] = useState(0);
  const shown = hover || value;
  const dim = size === "lg" ? "w-11 h-11" : "w-9 h-9";

  return (
    <div className="space-y-3">
      {label && <p className="text-base text-foreground/90">{label}</p>}
      <div className="flex items-center gap-1.5" role="radiogroup" aria-label={label}>
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            role="radio"
            aria-checked={value === star}
            aria-label={`${star} de 5`}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            onClick={() => onChange(star)}
            className="p-0.5 rounded-sm transition-transform active:scale-90"
          >
            <Star
              className={`${dim} transition-colors duration-150 ${
                star <= shown ? "fill-accent text-accent" : "text-muted-foreground/35"
              }`}
              strokeWidth={1.5}
            />
          </button>
        ))}
        <span className="ml-2 text-sm text-muted-foreground min-w-[5rem]">{WORDS[shown]}</span>
      </div>
    </div>
  );
}
