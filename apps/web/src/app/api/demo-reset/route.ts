import { proxyApiPost } from "@/lib/api-proxy";

export async function POST() {
  return proxyApiPost("/v1/demo/reset?customerId=demo-customer", {
    service: "Demo reset service",
  });
}
