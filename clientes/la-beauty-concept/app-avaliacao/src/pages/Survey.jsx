import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Textarea } from "@/components/ui/textarea";
import FlowLayout from "../components/FlowLayout";
import StarRating from "../components/StarRating";
import RadioChoice from "../components/RadioChoice";
import ProfessionalPicker from "../components/ProfessionalPicker";
import { base44 } from "@/api/base44Client";
import { SERVICES, firstName } from "@/lib/la";

const RECOMMEND = ["10, com certeza", "7 a 9, muito provável", "4 a 6, talvez", "0 a 3, pouco provável"];

function Block({ n, title, children }) {
  return (
    <section className="border-t border-border pt-6">
      <p className="text-xs text-muted-foreground mb-1">{n}</p>
      <h3 className="text-xl text-foreground mb-4">{title}</h3>
      {children}
    </section>
  );
}

export default function Survey() {
  const navigate = useNavigate();
  const [professional, setProfessional] = useState("");
  const [professionalRating, setProfessionalRating] = useState(0);
  const [services, setServices] = useState([]);
  const [experience, setExperience] = useState(0);
  const [recommend, setRecommend] = useState("");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionStorage.getItem("survey_registration")) navigate("/cadastro");
  }, [navigate]);

  const ready = professional && professionalRating >= 1 && services.length > 0 && experience >= 1 && recommend;

  async function handleSubmit() {
    if (!ready || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      const reg = JSON.parse(sessionStorage.getItem("survey_registration"));
      const survey = await base44.entities.SurveyResponse.create({
        ...reg,
        professional_name: professional,
        professional_rating: professionalRating,
        services_done: services.join(", "),
        experience_rating: experience,
        recommend_score: recommend,
        comment: comment.trim() || undefined,
      });
      sessionStorage.setItem("survey_id", survey.id);
      navigate("/roleta");
    } catch (e) {
      setError("Não conseguimos enviar agora. Confira sua internet e toque em enviar de novo.");
      setSubmitting(false);
    }
  }

  return (
    <FlowLayout step={2} totalSteps={4}>
      <div className="mb-8">
        <h2 className="text-3xl text-foreground">Sua avaliação</h2>
        <p className="text-sm text-muted-foreground mt-2">Começando por quem cuidou de você hoje.</p>
      </div>

      <div className="space-y-8">
        <Block n="1 de 5" title="Quem te atendeu hoje?">
          <ProfessionalPicker
            value={professional}
            onChange={(name) => {
              setProfessional(name);
              setProfessionalRating(0);
            }}
          />
        </Block>

        <AnimatePresence initial={false}>
          {professional && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
              <Block n="2 de 5" title={`Que nota você dá para o atendimento de ${firstName(professional)}?`}>
                <StarRating size="lg" value={professionalRating} onChange={setProfessionalRating} />
              </Block>
            </motion.div>
          )}
        </AnimatePresence>

        <Block n="3 de 5" title="O que você fez hoje?">
          <RadioChoice label="" options={SERVICES} value={services} onChange={setServices} multi />
        </Block>

        <Block n="4 de 5" title="E a experiência no salão, de modo geral?">
          <StarRating value={experience} onChange={setExperience} />
        </Block>

        <Block n="5 de 5" title="Qual a chance de você indicar o LA para uma amiga?">
          <RadioChoice label="" options={RECOMMEND} value={recommend} onChange={setRecommend} />
        </Block>

        <section className="border-t border-border pt-6 space-y-3">
          <label htmlFor="comentario" className="block text-base text-foreground/90">
            Quer deixar um recado? <span className="text-muted-foreground text-sm">(opcional)</span>
          </label>
          <Textarea
            id="comentario"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Um elogio, uma sugestão..."
            rows={3}
            className="bg-secondary border-border rounded-md text-base text-foreground placeholder:text-muted-foreground/50 resize-none"
          />
        </section>

        {error && <p className="text-sm text-destructive" role="alert">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={!ready || submitting}
          className="w-full min-h-[56px] bg-primary text-primary-foreground font-semibold text-base rounded-md hover:bg-primary/90 disabled:opacity-40 transition-colors"
        >
          {submitting ? "Enviando..." : "Enviar e girar a roleta"}
        </button>
        {!ready && <p className="text-xs text-muted-foreground text-center -mt-4">Responda as 5 perguntas para liberar a roleta.</p>}
      </div>
    </FlowLayout>
  );
}
