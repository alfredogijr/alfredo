// Função serverless (Vercel) — recebe o lead do formulário do site,
// cria Contato + Oportunidade no Grão CRM (Base44) e devolve OK.
// O aviso por WhatsApp fica a cargo de uma automação/agente dentro do
// próprio Grão CRM, disparada quando entra uma nova oportunidade do site.
//
// Variáveis de ambiente necessárias no Vercel (Project → Settings → Environment Variables):
//   BASE44_API_KEY      → chave de API do app Grão CRM (Base44 → Grão CRM → Settings → API Keys)
//   BASE44_APP_ID       → (opcional) id do app. Padrão: Grão CRM
//   BASE44_PIPELINE_ID  → (opcional) id do funil. Padrão: Serviços
//   BASE44_STAGE        → (opcional) etapa. Padrão: contact (Contato)

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "Method not allowed" });
  }

  // body pode vir como objeto (Vercel) ou string
  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  const { nome, email, empresa, whatsapp, desafio } = body || {};

  if (!nome || !email) {
    return res.status(400).json({ ok: false, error: "Informe ao menos nome e e-mail." });
  }

  const APP_ID = process.env.BASE44_APP_ID || "687c60550f7c48fc3bec4a93"; // Grão CRM
  const API_KEY = process.env.BASE44_API_KEY;
  const PIPELINE_ID = process.env.BASE44_PIPELINE_ID || "6882f1bbc60e5c71dca24942"; // Serviços
  const STAGE = process.env.BASE44_STAGE || "contact"; // etapa "Contato"
  const BASE = `https://app.base44.com/api/apps/${APP_ID}/entities`;

  // Sem a chave configurada ainda: não quebra o site (o e-mail já é enviado pelo
  // FormSubmit no front). Apenas sinaliza que falta configurar.
  if (!API_KEY) {
    return res.status(200).json({ ok: false, pending: "BASE44_API_KEY não configurada no Vercel." });
  }

  const headers = { "Content-Type": "application/json", "api_key": API_KEY };

  try {
    // 1) cria o Contato
    const cRes = await fetch(`${BASE}/Contact`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        name: nome,
        email,
        phone: whatsapp || "",
        notes: desafio || "",
        tags: "site,lead",
      }),
    });
    const contact = await cRes.json();
    const contactId = Array.isArray(contact) ? contact[0]?.id : contact?.id;

    // 2) cria a Oportunidade (Deal) no funil escolhido, etapa Contato
    if (contactId) {
      await fetch(`${BASE}/Deal`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          title: `Lead do site — ${nome}${empresa ? " (" + empresa + ")" : ""}`,
          contact_id: contactId,
          pipeline_id: PIPELINE_ID,
          stage: STAGE,
          source: "outro",
          notes: desafio || "",
        }),
      });
    }

    return res.status(200).json({ ok: true });
  } catch (e) {
    // não expõe erro pro visitante; o e-mail via FormSubmit já garante o aviso
    return res.status(200).json({ ok: false, error: String(e) });
  }
}
