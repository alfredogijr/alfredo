import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { useAuth } from "@/lib/AuthContext";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Cake, User } from "lucide-react";
import AdminStatsCards from "../components/AdminStatsCards";
import AdminRanking from "../components/AdminRanking";
import AdminResponseRow from "../components/AdminResponseRow";
import AdminExportMenu from "../components/AdminExportMenu";
import AdminPeriod from "../components/AdminPeriod";
import { availableMonths, monthKey, periodRange, previousRange, inRange, describePeriod } from "@/lib/period";
import { LOGO_LIGHT, PROFESSIONALS } from "@/lib/la";

const MONTHS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];

function Gate({ title, text, action }) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="max-w-sm w-full text-center space-y-5">
        <img src={LOGO_LIGHT} alt="LA Beauty Concept" className="h-16 mx-auto" />
        <h1 className="text-3xl text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">{text}</p>
        {action}
      </div>
    </div>
  );
}

export default function Admin() {
  const { user, isAuthenticated, isLoadingAuth, navigateToLogin, logout } = useAuth();
  const [responses, setResponses] = useState([]);
  const [coupons, setCoupons] = useState([]);
  const [search, setSearch] = useState("");
  const [birthMonth, setBirthMonth] = useState("all");
  const [pro, setPro] = useState("all");
  const [period, setPeriod] = useState({ type: "month", value: monthKey(Date.now()) });
  const [loading, setLoading] = useState(true);

  const isAdmin = isAuthenticated && user?.role === "admin";

  useEffect(() => {
    if (!isAdmin) return;
    async function load() {
      const [r, c] = await Promise.all([
        base44.entities.SurveyResponse.list("-created_date", 1000),
        base44.entities.Coupon.list("-created_date", 1000),
      ]);
      setResponses(r);
      setCoupons(c);
      setLoading(false);
    }
    load();
  }, [isAdmin]);

  if (isLoadingAuth) return null;
  if (!isAuthenticated) {
    return (
      <Gate
        title="Painel do salão"
        text="Entre com a conta autorizada para ver as avaliações e os cupons."
        action={<button onClick={navigateToLogin} className="w-full min-h-[52px] bg-primary text-primary-foreground font-semibold rounded-md">Entrar</button>}
      />
    );
  }
  if (!isAdmin) {
    return (
      <Gate
        title="Acesso restrito"
        text="Esta conta não tem permissão para o painel. Peça acesso ao responsável pelo salão."
        action={<button onClick={() => logout()} className="text-sm underline underline-offset-4 text-muted-foreground">Sair</button>}
      />
    );
  }

  async function toggleRedeemed(coupon) {
    const updated = await base44.entities.Coupon.update(coupon.id, { redeemed: !coupon.redeemed });
    setCoupons((cs) => cs.map((c) => (c.id === coupon.id ? { ...c, ...updated, redeemed: !coupon.redeemed } : c)));
  }

  const range = periodRange(period);
  const prevRange = previousRange(range, period);
  const periodResponses = responses.filter((r) => inRange(r, range));
  const prevResponses = prevRange ? responses.filter((r) => inRange(r, prevRange)) : null;
  const periodCoupons = coupons.filter((c) => inRange(c, range));
  const periodLabel = describePeriod(period);

  const couponMap = {};
  coupons.forEach((c) => { couponMap[c.survey_id] = c; });

  const q = search.trim().toLowerCase();
  const filtered = periodResponses.filter((r) => {
    const c = couponMap[r.id];
    const matchesSearch = !q
      || r.customer_name?.toLowerCase().includes(q)
      || r.whatsapp?.replace(/\D/g, "").includes(q.replace(/\D/g, "") || "§")
      || c?.code?.toLowerCase().includes(q);
    const matchesMonth = birthMonth === "all" || r.birth_date?.slice(5, 7) === String(birthMonth).padStart(2, "0");
    const matchesPro = pro === "all" || r.professional_name === pro;
    return matchesSearch && matchesMonth && matchesPro;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-border border-t-foreground rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        <header className="flex items-end justify-between gap-4 mb-8 border-b border-border pb-6">
          <div className="flex items-center gap-4">
            <img src={LOGO_LIGHT} alt="LA Beauty Concept" className="h-14 w-auto" />
            <div>
              <h1 className="text-3xl text-foreground">Avaliações e prêmios</h1>
              <p className="text-sm text-muted-foreground">Painel do salão</p>
            </div>
          </div>
          <button onClick={() => logout()} className="text-sm text-muted-foreground underline underline-offset-4">Sair</button>
        </header>

        <div className="mb-6">
          <AdminPeriod period={period} setPeriod={setPeriod} months={availableMonths(responses)} />
        </div>

        <AdminStatsCards responses={periodResponses} coupons={periodCoupons} prevResponses={prevResponses} />
        <AdminRanking responses={periodResponses} prevResponses={prevResponses} periodLabel={periodLabel} onPick={setPro} active={pro} />

        <div className="flex flex-col md:flex-row gap-3 mt-10 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Nome, WhatsApp ou código do cupom" aria-label="Buscar" className="pl-10 h-11 bg-secondary border-border rounded-md" />
          </div>
          <Select value={pro} onValueChange={setPro}>
            <SelectTrigger className="h-11 w-full md:w-56 bg-secondary border-border rounded-md" aria-label="Profissional">
              <div className="flex items-center gap-2"><User className="w-4 h-4 text-accent" /><SelectValue placeholder="Profissional" /></div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toda a equipe</SelectItem>
              {PROFESSIONALS.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={birthMonth} onValueChange={setBirthMonth}>
            <SelectTrigger className="h-11 w-full md:w-48 bg-secondary border-border rounded-md" aria-label="Mês de aniversário">
              <div className="flex items-center gap-2"><Cake className="w-4 h-4 text-accent" /><SelectValue placeholder="Aniversário" /></div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os meses</SelectItem>
              {MONTHS.map((m, i) => <SelectItem key={m} value={String(i + 1)}>{m}</SelectItem>)}
            </SelectContent>
          </Select>
          <AdminExportMenu responses={filtered} couponMap={couponMap} />
        </div>

        <h2 className="text-2xl text-foreground mt-2 mb-1">Avaliações</h2>
        <p className="text-xs text-muted-foreground mb-3">{filtered.length} resultado{filtered.length !== 1 ? "s" : ""} em {periodLabel.toLowerCase()}{pro !== "all" ? `, de ${pro}` : ""}</p>
        <div className="space-y-3">
          {filtered.map((r) => (
            <AdminResponseRow key={r.id} response={r} coupon={couponMap[r.id]} onToggleRedeemed={toggleRedeemed} />
          ))}
          {filtered.length === 0 && <div className="text-center py-12 text-muted-foreground">Nenhuma avaliação encontrada.</div>}
        </div>
      </div>
    </div>
  );
}
