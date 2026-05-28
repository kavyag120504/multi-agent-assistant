import { NextResponse } from 'next/server';

export async function POST(req) {
  try {
    const { message } = await req.json();

    const groqReq = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'llama3-8b-8192',
        messages: [{ role: 'user', content: message }]
      })
    });

    const data = await groqReq.json();
    const reply = data.choices?.[0]?.message?.content || "Hello! I am KAVI. (Running in fallback mode)";

    return NextResponse.json({
      response: reply,
      intent: "general",
      confidence: 100,
      agents: []
    });
  } catch (error) {
    return NextResponse.json({
      response: "Hello! The chat is currently in fallback mode.",
      intent: "general",
      confidence: 100,
      agents: []
    });
  }
}
