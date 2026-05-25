const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8005";
export interface Option {
  label: string;
  value: string;
}

export interface CTA {
  label: string;
  url: string;
}

export interface ChatResponse {
  session_id: string;
  step: string;
  message: string;
  options: Option[];
  cta: CTA | null;
  user_branch: "new_user" | "returning_user" | null;
}

export async function sendChat(payload: {
  session_id: string | null;
  current_step: string | null;
  selected_option: string | null;
  user_branch: "new_user" | "returning_user" | null;
  message?: string | null;
}): Promise<ChatResponse> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
