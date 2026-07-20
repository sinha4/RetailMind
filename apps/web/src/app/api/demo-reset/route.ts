import { NextResponse } from "next/server";

const apiUrl =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export async function POST() {
  try {
    const response = await fetch(
      `${apiUrl}/v1/demo/reset?customerId=demo-customer`,
      { method: "POST", cache: "no-store" },
    );
    const body: unknown = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json(
      { detail: "Demo reset service is unavailable" },
      { status: 503 },
    );
  }
}
