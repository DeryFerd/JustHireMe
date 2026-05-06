import { cleanId, json, redis, redisConfigured, redisPipeline, send } from "./_counter.js";

const TOTAL_KEY = "justhireme:downloads:total";
const UNIQUE_PREFIX = "justhireme:downloads:visitor:";

export default async function handler(request, response) {
  try {
    const configured = redisConfigured();
    const baseline = Number.parseInt(process.env.DOWNLOAD_COUNT_BASELINE || "0", 10);

    if (request.method === "GET") {
      const total = configured ? await redis(["GET", TOTAL_KEY]) : null;
      return send(response, json({
        configured,
        total: Number.parseInt(total || `${baseline}`, 10),
      }));
    }

    if (request.method !== "POST") {
      return send(response, json({ error: "Method not allowed" }, 405));
    }

    const body = typeof request.body === "object" && request.body ? request.body : {};
    const visitorId = cleanId(body.visitorId);

    if (!visitorId) {
      return send(response, json({ error: "Missing visitorId" }, 400));
    }

    if (!configured) {
      return send(response, json({ configured: false, counted: false, total: baseline }));
    }

    const visitorKey = `${UNIQUE_PREFIX}${visitorId}`;
    const [wasNew] = await redisPipeline([
      ["SET", visitorKey, "1", "NX"],
      ["SET", TOTAL_KEY, baseline, "NX"],
    ]);

    const total = wasNew
      ? await redis(["INCR", TOTAL_KEY])
      : await redis(["GET", TOTAL_KEY]);

    return send(response, json({
      configured: true,
      counted: Boolean(wasNew),
      total: Number.parseInt(total || `${baseline}`, 10),
    }));
  } catch (error) {
    return send(response, json({
      error: "Download counter unavailable",
      total: Number.parseInt(process.env.DOWNLOAD_COUNT_BASELINE || "0", 10),
    }, 500));
  }
}
