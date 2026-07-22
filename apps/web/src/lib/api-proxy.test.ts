import { afterEach, describe, expect, it, vi } from "vitest";

import { parseRequestJson, proxyApiPost } from "@/lib/api-proxy";

afterEach(() => vi.unstubAllGlobals());

describe("API proxy boundary", () => {
  it("returns a specific 400 for malformed request JSON", async () => {
    const request = new Request("http://localhost/api/test", {
      method: "POST",
      body: "{broken",
      headers: { "Content-Type": "application/json" },
    });

    const response = await parseRequestJson(request);
    expect(response).toBeInstanceOf(Response);
    expect((response as Response).status).toBe(400);
    await expect((response as Response).json()).resolves.toMatchObject({
      code: "INVALID_JSON",
    });
  });

  it("preserves upstream status, detail, and request ID", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Customer not found" }), {
          status: 404,
          headers: {
            "Content-Type": "application/json",
            "x-request-id": "request-123",
          },
        }),
      ),
    );

    const response = await proxyApiPost("/v1/test", {
      service: "Test service",
    });
    expect(response.status).toBe(404);
    expect(response.headers.get("x-request-id")).toBe("request-123");
    await expect(response.json()).resolves.toEqual({
      detail: "Customer not found",
    });
  });

  it("distinguishes connection failures from invalid upstream JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("connection refused")),
    );
    const unavailable = await proxyApiPost("/v1/test", {
      service: "Test service",
    });
    expect(unavailable.status).toBe(503);
    await expect(unavailable.json()).resolves.toMatchObject({
      code: "UPSTREAM_UNAVAILABLE",
    });

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("not-json", { status: 200 })),
    );
    const invalid = await proxyApiPost("/v1/test", { service: "Test service" });
    expect(invalid.status).toBe(502);
    await expect(invalid.json()).resolves.toMatchObject({
      code: "UPSTREAM_INVALID_RESPONSE",
    });
  });

  it("returns a gateway timeout when the upstream aborts", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new DOMException("timed out", "TimeoutError")),
    );
    const response = await proxyApiPost("/v1/test", {
      service: "Test service",
      timeoutMs: 1,
    });
    expect(response.status).toBe(504);
    await expect(response.json()).resolves.toMatchObject({
      code: "UPSTREAM_TIMEOUT",
    });
  });
});
