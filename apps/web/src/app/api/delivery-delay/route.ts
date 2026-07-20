import { NextResponse } from "next/server";

const apiUrl =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export async function POST(request: Request) {
  try {
    const payload: unknown = await request.json();
    const response = await fetch(`${apiUrl}/v1/orders/delivery-delay`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });
    const body: unknown = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json(
      { detail: "Post-purchase service is unavailable" },
      { status: 503 },
    );
  }
}
