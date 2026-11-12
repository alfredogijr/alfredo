import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FlowLayout from "../components/FlowLayout";
import CouponCard from "../components/CouponCard";
import GoogleRedirectOverlay from "../components/GoogleRedirectOverlay";
import { GOOGLE_REVIEW_URL, WHATSAPP_URL, INSTAGRAM_URL } from "@/lib/la";

export default function CouponPage() {
  const navigate = useNavigate();
  const [coupon, setCoupon] = useState(null);
  const [redirecting, setRedirecting] = useState(false);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    // The coupon is kept from the moment it was created: clients never read other people's coupons
    const saved = sessionStorage.getItem("coupon_data");
    if (!saved) {
      navigate("/");
      return;
    }
    setCoupon(JSON.parse(saved));
  }, [navigate]);

  function handleDownloaded() {
    sessionStorage.removeItem("survey_registration");
    sessionStorage.removeItem("survey_id");
    sessionStorage.removeItem("coupon_id");
    if (GOOGLE_REVIEW_URL) {
      setRedirecting(true);
      setTimeout(() => { window.location.href = GOOGLE_REVIEW_URL; }, 3000);
    } else {
      setFinished(true);
    }
  }

  if (!coupon) return null;

  return (
    <FlowLayout step={4} totalSteps={4}>
      <div className="text-center mb-6">
        <h2 className="text-3xl text-foreground">Seu prêmio está garantido.</h2>
        <p className="text-sm text-muted-foreground mt-2">Baixe o cupom e mostre na recepção no próximo horário.</p>
      </div>

      <CouponCard coupon={coupon} onDownloaded={handleDownloaded} />

      {finished && (
        <div className="mt-8 border-t border-border pt-6 text-center space-y-3">
          <p className="text-base text-foreground">Cupom salvo. Obrigada por avaliar!</p>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener" className="flex items-center justify-center w-full min-h-[52px] rounded-md border border-foreground/40 text-foreground font-semibold hover:bg-secondary transition-colors">
            Agendar o próximo horário
          </a>
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener" className="block text-sm text-muted-foreground underline underline-offset-4">
            Seguir o LA no Instagram
          </a>
        </div>
      )}

      {redirecting && <GoogleRedirectOverlay />}
    </FlowLayout>
  );
}
