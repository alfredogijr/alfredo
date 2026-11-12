import { motion } from "framer-motion";
import { LOGO_LIGHT } from "@/lib/la";

export default function FlowLayout({ children, step, totalSteps }) {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-start px-5 py-8">
      <img src={LOGO_LIGHT} alt="LA Beauty Concept" className="h-14 w-auto object-contain mb-8" />

      {totalSteps && (
        <div className="w-full max-w-md mb-10">
          <div className="h-px bg-border overflow-hidden">
            <motion.div
              className="h-full bg-accent"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: step / totalSteps }}
              style={{ transformOrigin: "left" }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Passo {step} de {totalSteps}
          </p>
        </div>
      )}

      <motion.div
        key={step}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-md"
      >
        {children}
      </motion.div>
    </div>
  );
}
