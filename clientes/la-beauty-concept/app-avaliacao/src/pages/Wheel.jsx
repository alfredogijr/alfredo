import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import FlowLayout from "../components/FlowLayout";
import PrizeWheel from "../components/PrizeWheel";
import PrizeReveal from "../components/PrizeReveal";
import { base44 } from "@/api/base44Client";
import { COUPON_PREFIX } from "@/lib/la";

function generateCode() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let code = COUPON_PREFIX;
  for (let i = 0; i < 6; i++) {
    code += chars[Math.floor(Math.random() * chars.length)];
  }
  return code;
}

export default function Wheel() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [revealPrize, setRevealPrize] = useState(null);
  const [pendingCouponId, setPendingCouponId] = useState(null);

  useEffect(() => {
    const surveyId = sessionStorage.getItem("survey_id");
    const reg = sessionStorage.getItem("survey_registration");
    if (!surveyId || !reg) {
      navigate("/cadastro");
    } else {
      setReady(true);
    }
  }, [navigate]);

  async function handleFinish(prize) {
    const reg = JSON.parse(sessionStorage.getItem("survey_registration"));
    const surveyId = sessionStorage.getItem("survey_id");

    const coupon = await base44.entities.Coupon.create({
      customer_name: reg.customer_name,
      whatsapp: reg.whatsapp,
      prize_name: prize.name,
      prize_emoji: prize.emoji,
      code: generateCode(),
      survey_id: surveyId,
    });

    sessionStorage.setItem("coupon_id", coupon.id);
    sessionStorage.setItem("coupon_data", JSON.stringify(coupon));
    setPendingCouponId(coupon.id);
    setRevealPrize(prize);
  }

  function handleContinue() {
    navigate("/cupom");
  }

  if (!ready) return null;

  return (
    <>
      {revealPrize && (
        <PrizeReveal prize={revealPrize} onContinue={handleContinue} />
      )}
      <FlowLayout step={3} totalSteps={4}>
        <div className="text-center mb-6">
          <motion.h2
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl text-foreground"
          >
            Gire a roleta
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-sm text-muted-foreground mt-2"
          >
            O prêmio vale para o seu próximo horário.
          </motion.p>
        </div>
        <PrizeWheel onFinish={handleFinish} />
      </FlowLayout>
    </>
  );
}