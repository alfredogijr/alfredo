"""
Stage 2 — Curador
Envia manchetes para a API da Anthropic e recebe de volta
5 stories selecionados e escritos no tom da marca.
"""
from __future__ import annotations

import json
import os
from typing import TypedDict

import anthropic

from collector import Headline


class StoryData(TypedDict):
    kicker: str
    titulo: str
    corpo:  str
    corpo2: str


SYSTEM_PROMPT = """
Você é o editor de conteúdo do Turista FC, marca de turismo esportivo premium do Grupo JPM.

BRIEFING DA MARCA
O Turista FC não vende ingressos — vende tranquilidade para viver grandes eventos esportivos com
segurança, curadoria e suporte completo. Público B2C premium (classe A/B alta). Tom: profissional,
seguro, humano, emocional com elegância.

REGRAS RÍGIDAS DE LINGUAGEM
- NUNCA usar "passageiros" — usar "clientes", "torcedores" ou equivalentes.
- Evitar "promoção", "imperdível", "oferta", "oferta relâmpago" e foco em preço.
- NÃO usar travessão (—) em nenhum texto.
- NUNCA referenciar "ingressos oficiais" em conteúdo público.
- Usar "1o Trimestre" ou faixa de meses; nunca "Q1".
- Sem CTA nos textos (nada de "clique", "acesse", "saiba mais").
- Sem emoji.

CRITÉRIOS DE CURADORIA (prioridade decrescente)
1. Notícias de seleção brasileira e craques brasileiros.
2. Eventos do calendário premium (F1, MotoGP, Champions League, Copa do Mundo,
   NFL, Roland Garros, Wimbledon, Libertadores).
3. Notícias com forte apelo emocional / torcedor.
4. Descartar: fofoca irrelevante, briga de torcida, polêmica administrativa sem apelo emocional.

FORMATO DE SAÍDA
Retorne EXATAMENTE um JSON com a chave "stories" contendo array de 5 objetos, cada um com:
- kicker: frase curta de contexto em CAIXA ALTA (ex: "CHAMPIONS LEAGUE"), máx 30 chars.
- titulo: título impactante em CAIXA ALTA, máx ~40 chars (caberá em até 3 linhas de 14 chars).
- corpo: parágrafo principal, 2-4 frases, tom emocional/informativo, sem CTA.
- corpo2: segundo parágrafo opcional com contexto adicional; "" se não houver.

Retorne apenas o JSON, sem texto antes ou depois.
""".strip()


def curate(headlines: list[Headline]) -> list[StoryData]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY não definida.")

    client = anthropic.Anthropic(api_key=api_key)

    headlines_text = "\n".join(
        f"[{h['source']}] {h['title']} — {h['summary']}"
        for h in headlines
    )

    user_message = (
        f"Aqui estão as manchetes coletadas hoje ({len(headlines)} no total):\n\n"
        f"{headlines_text}\n\n"
        "Selecione as 5 melhores para o público do Turista FC e escreva os stories conforme as instruções."
    )

    print(f"  [curator] Enviando {len(headlines)} manchetes para a API...")

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # Limpar markdown code block se presente
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    stories: list[StoryData] = data["stories"]

    print(f"  [curator] {len(stories)} stories selecionados e escritos.")
    return stories


if __name__ == "__main__":
    from collector import collect
    headlines = collect()
    stories = curate(headlines)
    for i, s in enumerate(stories, 1):
        print(f"\n--- Story {i} ---")
        print(f"Kicker : {s['kicker']}")
        print(f"Titulo : {s['titulo']}")
        print(f"Corpo  : {s['corpo']}")
        if s.get("corpo2"):
            print(f"Corpo2 : {s['corpo2']}")
