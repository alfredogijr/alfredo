import { Star } from "lucide-react";

function Stars({ count }) {
  return (
    <span className="inline-flex gap-0.5" aria-label={`${count || 0} de 5`}>
      {[1, 2, 3, 4, 5].map((s) => (
        <Star key={s} className={`w-3.5 h-3.5 ${s <= count ? "fill-accent text-accent" : "text-muted-foreground/30"}`} strokeWidth={1.5} />
      ))}
    </span>
  );
}

export default function AdminResponseRow({ response: r, coupon, onToggleRedeemed }) {
  return (
    <div className={`bg-card rounded-md p-4 space-y-3 border ${r.professional_rating <= 3 ? "border-destructive/50" : "border-border"}`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-foreground">{r.customer_name}</p>
          <p className="text-xs text-muted-foreground">{r.whatsapp}</p>
        </div>
        <p className="text-xs text-muted-foreground whitespace-nowrap">{new Date(r.created_date).toLocaleDateString("pt-BR")}</p>
      </div>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
        <span className="text-foreground">
          Atendida por <strong>{r.professional_name || "não informado"}</strong>
        </span>
        <Stars count={r.professional_rating} />
        <span className="text-xs text-muted-foreground inline-flex items-center gap-2">Salão <Stars count={r.experience_rating} /></span>
      </div>

      {r.services_done && <p className="text-xs text-muted-foreground"><span className="text-foreground/70">Fez: </span>{r.services_done}</p>}
      {r.recommend_score && <p className="text-xs text-muted-foreground"><span className="text-foreground/70">Indicaria: </span>{r.recommend_score}</p>}
      {r.comment && <p className="text-sm text-foreground/85 bg-muted rounded-sm p-3">“{r.comment}”</p>}

      {coupon && (
        <div className="flex flex-wrap items-center gap-3 text-sm bg-secondary rounded-sm px-3 py-2">
          <span aria-hidden="true">{coupon.prize_emoji}</span>
          <span className="text-foreground/85">{coupon.prize_name}</span>
          <span className="font-bold tracking-wider text-accent">{coupon.code}</span>
          <button
            onClick={() => onToggleRedeemed(coupon)}
            className={`ml-auto min-h-[36px] px-3 rounded-sm text-xs font-semibold border transition-colors ${
              coupon.redeemed ? "border-border text-muted-foreground" : "border-primary bg-primary text-primary-foreground"
            }`}
          >
            {coupon.redeemed ? "Resgatado, desfazer" : "Marcar como resgatado"}
          </button>
        </div>
      )}
    </div>
  );
}
