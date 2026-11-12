import { Download, FileSpreadsheet, FileText, Contact } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import * as XLSX from "xlsx";

function buildFullRows(responses, couponMap) {
  return responses.map((r) => {
    const c = couponMap[r.id];
    return {
      Nome: r.customer_name || "",
      WhatsApp: r.whatsapp || "",
      CPF: r.cpf || "",
      "Data de Nascimento": r.birth_date || "",
      Cadastro: r.created_date ? new Date(r.created_date).toLocaleString("pt-BR") : "",
      Profissional: r.professional_name || "",
      "Nota do Profissional": r.professional_rating ?? "",
      "Nota do Salão": r.experience_rating ?? "",
      "Serviços": r.services_done || "",
      "Indicaria": r.recommend_score || "",
      Comentário: r.comment || "",
      "Prêmio": c?.prize_name || "",
      "Código Cupom": c?.code || "",
      "Cupom Resgatado": c ? (c.redeemed ? "Sim" : "Não") : "",
    };
  });
}

function buildContactRows(responses) {
  return responses.map((r) => ({
    Nome: r.customer_name || "",
    WhatsApp: r.whatsapp || "",
    "Data de Nascimento": r.birth_date || "",
    CPF: r.cpf || "",
    Cadastro: r.created_date ? new Date(r.created_date).toLocaleDateString("pt-BR") : "",
  }));
}

function downloadCSV(rows, filename) {
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const escape = (v) => {
    const s = String(v ?? "");
    return /[",\n;]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const csv = [
    headers.join(";"),
    ...rows.map((row) => headers.map((h) => escape(row[h])).join(";")),
  ].join("\n");
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function downloadXLSX(rows, filename) {
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Respostas");
  XLSX.writeFile(wb, filename);
}

export default function AdminExportMenu({ responses, couponMap }) {
  const disabled = !responses.length;

  function exportFullCSV() {
    downloadCSV(buildFullRows(responses, couponMap), "la-beauty-concept-completo.csv");
  }
  function exportContactsCSV() {
    downloadCSV(buildContactRows(responses), "la-beauty-concept-contatos.csv");
  }
  function exportFullXLSX() {
    downloadXLSX(buildFullRows(responses, couponMap), "la-beauty-concept-completo.xlsx");
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          disabled={disabled}
          className="h-11 gap-2 font-body font-medium rounded-md border-border"
        >
          <Download className="w-4 h-4" />
          Exportar
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuItem onClick={exportFullCSV} className="gap-2 cursor-pointer">
          <FileText className="w-4 h-4 text-primary" />
          <div className="flex flex-col">
            <span className="text-sm font-body">CSV completo</span>
            <span className="text-[10px] text-muted-foreground">Todos os dados + cupons</span>
          </div>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportContactsCSV} className="gap-2 cursor-pointer">
          <Contact className="w-4 h-4 text-accent" />
          <div className="flex flex-col">
            <span className="text-sm font-body">CSV contatos</span>
            <span className="text-[10px] text-muted-foreground">Nome, WhatsApp, aniversário</span>
          </div>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportFullXLSX} className="gap-2 cursor-pointer">
          <FileSpreadsheet className="w-4 h-4 text-accent" />
          <div className="flex flex-col">
            <span className="text-sm font-body">Excel completo</span>
            <span className="text-[10px] text-muted-foreground">Planilha .xlsx</span>
          </div>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}