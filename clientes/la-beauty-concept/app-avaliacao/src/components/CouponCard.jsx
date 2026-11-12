import { useRef, useState } from "react";
import { Download } from "lucide-react";
import html2canvas from "html2canvas";
import { LOGO_LIGHT, COUPON_DAYS, PRIZES } from "@/lib/la";

export default function CouponCard({ coupon, onDownloaded }) {
  const couponRef = useRef(null);
  const [busy, setBusy] = useState(false);

  const issueDate = new Date(coupon.created_date || Date.now());
  const expiryDate = new Date(issueDate);
  expiryDate.setDate(expiryDate.getDate() + COUPON_DAYS);
  const tone = (PRIZES.find((p) => p.name === coupon.prize_name) || {}).color || "#c89b62";

  async function handleDownload() {
    if (!couponRef.current || busy) return;
    setBusy(true);
    const canvas = await html2canvas(couponRef.current, { backgroundColor: "#121110", scale: 2, useCORS: true });
    const link = document.createElement("a");
    link.download = `cupom-la-beauty-concept-${coupon.code}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
    setBusy(false);
    setTimeout(() => onDownloaded && onDownloaded(), 1200);
  }

  return (
    <div className="flex flex-col items-center gap-6 w-full max-w-sm mx-auto">
      <div ref={couponRef} className="w-full rounded-md overflow-hidden border border-border" style={{ background: "#121110", borderTop: `6px solid ${tone}` }}>
        <div className="px-6 pt-7 pb-5 text-center border-b border-dashed" style={{ borderColor: "#3a3633" }}>
          <img src={LOGO_LIGHT} alt="LA Beauty Concept" crossOrigin="anonymous" className="h-16 w-auto object-contain mx-auto" />
        </div>

        <div className="px-6 py-6 text-center space-y-4" style={{ color: "#f3efe8" }}>
          <p className="text-sm" style={{ color: "#a89f95" }}>Cupom de prêmio</p>
          <div className="text-5xl" aria-hidden="true">{coupon.prize_emoji}</div>
          <p className="text-2xl leading-tight" style={{ fontFamily: "'Libre Bodoni', Georgia, serif" }}>{coupon.prize_name}</p>

          <div className="pt-2 space-y-1 text-sm" style={{ color: "#cfc7bd" }}>
            <p>{coupon.customer_name}</p>
            <p>Válido até <strong style={{ color: "#f3efe8" }}>{expiryDate.toLocaleDateString("pt-BR")}</strong></p>
          </div>

          <div className="mt-2 rounded-md px-4 py-3" style={{ background: "#1e1c1a" }}>
            <p className="text-xs mb-1" style={{ color: "#a89f95" }}>Código</p>
            <p className="text-2xl font-bold tracking-wider" style={{ color: tone }}>{coupon.code}</p>
          </div>

          <p className="text-xs leading-snug" style={{ color: "#a89f95" }}>
            Apresente este cupom na recepção do salão no seu próximo atendimento. Estrada do Tindiba, 332, Loja D, Pechincha.
          </p>
        </div>
      </div>

      <button
        onClick={handleDownload}
        disabled={busy}
        className="w-full min-h-[56px] flex items-center justify-center gap-2 bg-primary text-primary-foreground font-semibold rounded-md hover:bg-primary/90 transition-colors disabled:opacity-60"
      >
        <Download className="w-5 h-5" />
        {busy ? "Gerando imagem..." : "Baixar meu cupom"}
      </button>
    </div>
  );
}
