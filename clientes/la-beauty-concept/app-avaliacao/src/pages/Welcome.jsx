import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { LOGO_LIGHT, PHOTOS, PRIZES } from "@/lib/la";

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="flex-1 flex flex-col items-center px-6 max-w-sm mx-auto w-full py-10">
        <motion.img
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          src={LOGO_LIGHT}
          alt="LA Beauty Concept"
          className="h-24 w-auto object-contain mb-10"
        />

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="grid grid-cols-3 gap-1.5 w-full mb-10"
        >
          {PHOTOS.map((p) => (
            <figure key={p.label} className="m-0">
              <img src={p.image} alt="" className="w-full aspect-[3/4] object-cover rounded-sm" />
              <figcaption className="text-xs text-muted-foreground mt-1.5">{p.label}</figcaption>
            </figure>
          ))}
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="text-[2.4rem] leading-[1.05] text-center text-foreground mb-4"
        >
          Conta pra gente como foi hoje.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-base text-muted-foreground text-center mb-8"
        >
          Avalie quem te atendeu e gire a roleta. Tem {PRIZES.length} prêmios para o seu próximo horário.
        </motion.p>

        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          onClick={() => navigate("/cadastro")}
          className="w-full min-h-[56px] px-8 bg-primary text-primary-foreground font-semibold text-base rounded-md flex items-center justify-center gap-2 hover:bg-primary/90 transition-colors"
        >
          Começar
          <ArrowRight className="w-5 h-5" />
        </motion.button>

        <p className="text-xs text-muted-foreground mt-4">Leva menos de 1 minuto</p>
      </div>
    </div>
  );
}
