import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Star } from "lucide-react";

export default function GoogleRedirectOverlay() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setProgress((p) => Math.min(p + 2, 100)), 60);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/95 px-6"
      role="status"
    >
      <div className="text-center max-w-xs w-full">
        <div className="flex justify-center gap-1 mb-6" aria-hidden="true">
          {[0, 1, 2, 3, 4].map((i) => <Star key={i} className="w-7 h-7 fill-accent text-accent" strokeWidth={1.5} />)}
        </div>
        <h2 className="text-3xl text-foreground mb-3">Obrigada!</h2>
        <p className="text-sm text-muted-foreground mb-8 leading-relaxed">
          Agora vamos te levar para deixar sua avaliação no Google. Ela ajuda muito o salão.
        </p>
        <div className="w-full bg-secondary h-1 overflow-hidden mb-3">
          <div style={{ transform: `scaleX(${progress / 100})`, transformOrigin: "left" }} className="h-full bg-accent transition-transform duration-100" />
        </div>
        <p className="text-xs text-muted-foreground">Abrindo o Google...</p>
      </div>
    </motion.div>
  );
}
