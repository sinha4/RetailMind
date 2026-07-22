import { NextResponse } from "next/server";

const DEFAULT_TIMEOUT_MS = 12_000;

const apiUrl = process.env.API_URL ?? "http://localhost:8000";

interface ProxyOptions {
  body?: unknown;
  service: string;
  timeoutMs?: number;
}

function errorResponse(detail: string, code: string, status: number) {
  return NextResponse.json({ detail, code }, { status });
}

export async function parseRequestJson(
  request: Request,
): Promise<unknown | NextResponse> {
  try {
    return await request.json();
  } catch {
    return errorResponse(
      "Request body must be valid JSON.",
      "INVALID_JSON",
      400,
    );
  }
}

export async function proxyApiPost(path: string, options: ProxyOptions) {
  let response: Response;
  try {
    response = await fetch(`${apiUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
      cache: "no-store",
      signal: AbortSignal.timeout(options.timeoutMs ?? DEFAULT_TIMEOUT_MS),
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "TimeoutError") {
      return errorResponse(
        `${options.service} timed out. Please try again.`,
        "UPSTREAM_TIMEOUT",
        504,
      );
    }
    return errorResponse(
      `${options.service} is unavailable. Make sure the API is running.`,
      "UPSTREAM_UNAVAILABLE",
      503,
    );
  }

  const requestId = response.headers.get("x-request-id");
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    return errorResponse(
      `${options.service} returned an invalid response.`,
      "UPSTREAM_INVALID_RESPONSE",
      502,
    );
  }

  return NextResponse.json(body, {
    status: response.status,
    headers: requestId ? { "x-request-id": requestId } : undefined,
  });
}
