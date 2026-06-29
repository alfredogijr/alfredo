// Função serverless (Vercel) — recebe o lead do formulário do site e cria
// Contato + Oportunidade no Grão CRM (Base44), usando o SDK oficial.
// O aviso por WhatsApp fica a cargo de uma automação/agente dentro do
// próprio Grão CRM, disparada quando entra uma nova oportunidade do site.
//
// Variáveis de ambiente no Vercel (Project → Settings → Environment Variables):
//   BASE44_API_KEY      → chave de API do app Grão CRM  (OBRIGATÓRIA — nunca no código)
//   BASE44_APP_ID       → (opcional) id do app.  Padrão: Grão CRM
//   BASE44_PIPELINE_ID  → (opcional) id do funil. Padrão: Serviços
//   BASE44_STAGE        → (opcional) etapa.       Padrão: contact (Contato)

import { createClient } from "@base44/sdk";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "Method not allowed" });
  }

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  const { nome, email, empresa, whatsapp, desafio } = body || {};

  if (!nome || !email) {
    return res.status(400).json({ ok: false, error: "Informe ao menos nome e e-mail." });
  }

  const API_KEY = process.env.BASE44_API_KEY;
  // Sem a chave ainda: não quebra o site (o e-mail já sai pelo FormSubmit no front).
  if (!API_KEY) {
    return res.status(200).json({ ok: false, pending: "BASE44_API_KEY não configurada no Vercel." });
  }

  const APP_ID = process.env.BASE44_APP_ID || "687c60550f7c48fc3bec4a93"; // Grão CRM
  const PIPELINE_ID = process.env.BASE44_PIPELINE_ID || "6882f1bbc60e5c71dca24942"; // Serviços
  const STAGE = process.env.BASE44_STAGE || "contact"; // etapa "Contato"

  try {
    const base44 = createClient({ appId: APP_ID, headers: { api_key: API_KEY } });

    // 1) Contato
    const contact = await base44.entities.Contact.create({
      name: nome,
      email,
      phone: whatsapp || "",
      notes: desafio || "",
      tags: "site,lead",
    });

    // 2) Oportunidade no funil escolhido, etapa Contato
    if (contact && contact.id) {
      await base44.entities.Deal.create({
        title: `Lead do site — ${nome}${empresa ? " (" + empresa + ")" : ""}`,
        contact_id: contact.id,
        pipeline_id: PIPELINE_ID,
        stage: STAGE,
        source: "outro",
        notes: desafio || "",
      });
    }

    return res.status(200).json({ ok: true, id: contact && contact.id });
  } catch (e) {
    // não expõe erro ao visitante; o e-mail via FormSubmit já garante o aviso
    return res.status(200).json({ ok: false, error: String((e && e.message) || e) });
  }
}
