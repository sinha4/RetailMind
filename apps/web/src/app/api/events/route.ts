import { NextResponse } from "next/server";

import { parseRequestJson, proxyApiPost } from "@/lib/api-proxy";

export async function POST(request: Request) {
  const payload = await parseRequestJson(request);
  if (payload instanceof NextResponse) return payload;
  return proxyApiPost("/v1/events", {
    body: payload,
    service: "Event service",
  });
}
