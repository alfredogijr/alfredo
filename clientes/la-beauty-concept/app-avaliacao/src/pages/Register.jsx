import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import FlowLayout from "../components/FlowLayout";
import { User, Phone, Calendar, CreditCard } from "lucide-react";
import { base44 } from "@/api/base44Client";

function formatCPF(val) {
  const digits = val.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

function validateCPF(cpf) {
  const clean = cpf.replace(/\D/g, "");
  if (clean.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(clean)) return false;

  let sum = 0;
  for (let i = 0; i < 9; i++) sum += parseInt(clean[i]) * (10 - i);
  let d1 = (sum * 10) % 11;
  if (d1 === 10) d1 = 0;
  if (d1 !== parseInt(clean[9])) return false;

  sum = 0;
  for (let i = 0; i < 10; i++) sum += parseInt(clean[i]) * (11 - i);
  let d2 = (sum * 10) % 11;
  if (d2 === 10) d2 = 0;
  if (d2 !== parseInt(clean[10])) return false;

  return true;
}

const CPF_LOCK_ENABLED = false; // Temporariamente desativado para testes — reativar quando lançar para clientes

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [whatsapp, setWhatsapp] = useState("");
  const [cpf, setCpf] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [checking, setChecking] = useState(false);
  const [blocked, setBlocked] = useState(false);

  function formatPhone(val) {
    const digits = val.replace(/\D/g, "").slice(0, 11);
    if (digits.length <= 2) return `(${digits}`;
    if (digits.length <= 7) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim() || !whatsapp.trim() || !cpf.trim() || !birthDate) return;
    if (!validateCPF(cpf)) return;

    const cleanCpf = cpf.replace(/\D/g, "");

    if (CPF_LOCK_ENABLED) {
      setChecking(true);
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
      const existing = await base44.entities.SurveyResponse.filter({
        cpf: cleanCpf,
        created_date: { $gte: thirtyDaysAgo },
      });
      setChecking(false);

      if (existing.length > 0) {
        setBlocked(true);
        return;
      }
    }

    const data = {
      customer_name: name.trim(),
      whatsapp: whatsapp.trim(),
      cpf: cleanCpf,
      birth_date: birthDate,
    };
    sessionStorage.setItem("survey_registration", JSON.stringify(data));
    navigate("/pesquisa");
  }

  const cpfValid = validateCPF(cpf);
  const isValid =
    name.trim().length >= 2 &&
    whatsapp.replace(/\D/g, "").length >= 10 &&
    cpfValid &&
    birthDate;

  if (blocked) {
    return (
      <FlowLayout step={1} totalSteps={4}>
        <div className="text-center space-y-5">
          <h2 className="text-3xl text-foreground">
            Você já participou.
          </h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Este CPF já participou nos últimos 30 dias.
            <br />
            Você poderá participar novamente após esse período.
          </p>
          <Button
            onClick={() => navigate("/")}
            className="w-full h-12 bg-primary text-primary-foreground font-semibold rounded-md"
          >
            Voltar ao início
          </Button>
        </div>
      </FlowLayout>
    );
  }

  return (
    <FlowLayout step={1} totalSteps={4}>
      <div className="text-center mb-8">
        <h2 className="text-3xl text-foreground">Seus dados</h2>
        <p className="text-sm text-muted-foreground mt-2">Para o cupom sair no seu nome e chegar no seu WhatsApp.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="space-y-2">
          <Label className="text-sm text-foreground/85 flex items-center gap-2">
            <User className="w-4 h-4 text-accent" /> Nome completo
          </Label>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Seu nome"
            autoComplete="name"
            className="h-12 bg-secondary border-border rounded-md text-base text-foreground placeholder:text-muted-foreground/50"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-sm text-foreground/85 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-accent" /> CPF
          </Label>
          <Input
            value={cpf}
            onChange={(e) => setCpf(formatCPF(e.target.value))}
            placeholder="000.000.000-00"
            inputMode="numeric"
            className="h-12 bg-secondary border-border rounded-md text-base text-foreground placeholder:text-muted-foreground/50"
          />
          {cpf.length > 0 && !cpfValid && (
            <p className="text-xs text-destructive">Confira o CPF, ele parece incompleto ou inválido.</p>
          )}
        </div>

        <div className="space-y-2">
          <Label className="text-sm text-foreground/85 flex items-center gap-2">
            <Phone className="w-4 h-4 text-accent" /> WhatsApp
          </Label>
          <Input
            value={whatsapp}
            onChange={(e) => setWhatsapp(formatPhone(e.target.value))}
            placeholder="(21) 99999-9999"
            autoComplete="tel"
            type="tel"
            inputMode="numeric"
            className="h-12 bg-secondary border-border rounded-md text-base text-foreground placeholder:text-muted-foreground/50"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-sm text-foreground/85 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-accent" /> Data de nascimento
          </Label>
          <Input
            type="date"
            autoComplete="bday"
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            className="h-12 bg-secondary border-border rounded-md text-base text-foreground placeholder:text-muted-foreground/50"
          />
        </div>

        <p className="text-xs text-muted-foreground leading-relaxed">
          Usamos seus dados só para emitir o cupom e falar com você sobre o salão. O CPF evita que o mesmo cupom seja gerado duas vezes.
        </p>

        <Button
          type="submit"
          disabled={!isValid || checking}
          className="w-full h-14 mt-4 bg-primary text-primary-foreground font-semibold text-base rounded-md hover:bg-primary/90 disabled:opacity-40 transition-colors"
        >
          {checking ? "Verificando..." : "Continuar"}
        </Button>
      </form>
    </FlowLayout>
  );
}