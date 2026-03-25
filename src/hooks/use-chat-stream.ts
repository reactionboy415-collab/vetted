import { useState, useCallback, useEffect } from "react";

export type MessageRole = "user" | "ai";

export interface Source {
  title: string;
  url: string;
  domain: string;
}

export interface Product {
  name: string;
  imageUrls: string[];
  price: { currency: string; amount: number } | null;
  purchaseUrl: string | null;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources?: Source[];
  products?: Product[];
}

interface RawProduct {
  name?: string;
  nameFromApi?: string;
  imageUrls?: string[];
  affiliatePages?: Array<{
    url?: string;
    price?: { currency: string; amount: number } | null;
    rank?: number;
  }>;
}

interface StatusLogEntry {
  kind?: string;
  statusMessage?: string;
  statusData?: {
    kind?: string;
    data?:
      | Array<{ title?: string; url?: string; domain?: string }>
      | { text?: string };
  };
}

const STORAGE_KEY = "shopsense_chat_v1";
const MAX_STORED = 40;

function loadFromStorage(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as ChatMessage[];
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch {}
  return [];
}

function extractSources(statusLog: StatusLogEntry[]): Source[] {
  const sourceMap = new Map<string, Source>();
  for (const entry of statusLog) {
    const data = entry?.statusData?.data;
    if (Array.isArray(data)) {
      for (const d of data) {
        if (d?.url && d?.title && !sourceMap.has(d.url)) {
          let domain = d.domain ?? "";
          if (!domain) {
            try {
              domain = new URL(d.url).hostname.replace(/^www\./, "");
            } catch {
              domain = d.url;
            }
          }
          sourceMap.set(d.url, { title: d.title, url: d.url, domain });
        }
      }
    }
  }
  return Array.from(sourceMap.values()).slice(0, 15);
}

function extractProducts(rawProducts: RawProduct[]): Product[] {
  return rawProducts
    .filter((p) => p.name || p.nameFromApi)
    .map((p) => {
      const pages = (p.affiliatePages ?? [])
        .slice()
        .sort((a, b) => (a.rank ?? 99) - (b.rank ?? 99));
      const priceEntry = pages.find((pp) => pp.price?.amount);
      return {
        name: p.name || p.nameFromApi || "Product",
        imageUrls: (p.imageUrls ?? []).filter(Boolean).slice(0, 4),
        price: priceEntry?.price ?? null,
        purchaseUrl: pages[0]?.url ?? null,
      };
    });
}

export function useChatStream() {
  const [messages, setMessages] = useState<ChatMessage[]>(loadFromStorage);
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusText, setStatusText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  // Persist to localStorage whenever messages change
  useEffect(() => {
    try {
      if (messages.length > 0) {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify(messages.slice(-MAX_STORED))
        );
      }
    } catch {}
  }, [messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setStatusText("");
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }, []);

  const askQuestion = useCallback(
    async (query: string) => {
      if (!query.trim() || isStreaming) return;

      const userMessageId = crypto.randomUUID();
      const aiMessageId = crypto.randomUUID();
      const sessionId = `anonymous:${crypto.randomUUID()}`;
      const queryId = crypto.randomUUID().replace(/-/g, "").slice(0, 16);

      // Build conversation context from recent history (last 3 Q&A pairs)
      const recentMessages = messages.slice(-6).filter((m) => m.content.trim());
      const conversationContext =
        recentMessages.length > 0
          ? recentMessages
              .map(
                (m) =>
                  `${m.role === "user" ? "User" : "Assistant"}: ${m.content.slice(0, 300)}`
              )
              .join("\n") + "\n\nCurrent question: " + query
          : `I want to know if I should buy ${query}. Analyze reviews, pros, cons, and value for money.`;

      setMessages((prev) => [
        ...prev,
        { id: userMessageId, role: "user", content: query },
        { id: aiMessageId, role: "ai", content: "" },
      ]);

      setIsStreaming(true);
      setStatusText("Initializing analysis…");
      setError(null);

      try {
        const payload = {
          queries: {
            researchProductComparison: {
              [queryId]: {
                localization: "IN",
                context: conversationContext,
              },
            },
          },
        };

        const response = await fetch("https://api.vetted.ai/queries", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-session-id": sessionId,
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze)",
            Origin: "https://vetted.ai",
            Referer: "https://vetted.ai/",
            Accept: "application/x-ndjson, application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(
            `Request failed: ${response.status} ${response.statusText}`
          );
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("Response body is not readable");

        const decoder = new TextDecoder();
        let buffer = "";
        let latestSummary = "";
        let latestSources: Source[] = [];
        let latestProducts: Product[] = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;
            try {
              const obj = JSON.parse(trimmed);
              const queryResult =
                obj?.responses?.researchProductComparison?.[queryId];
              if (!queryResult) continue;

              const statusLog: StatusLogEntry[] = queryResult.statusLog ?? [];

              for (let i = statusLog.length - 1; i >= 0; i--) {
                const msg = statusLog[i]?.statusMessage;
                if (msg && typeof msg === "string" && msg.length < 120) {
                  setStatusText(msg);
                  break;
                }
              }

              const sources = extractSources(statusLog);
              if (sources.length > 0) latestSources = sources;

              for (const entry of statusLog) {
                const d = entry?.statusData?.data;
                if (
                  d &&
                  !Array.isArray(d) &&
                  typeof d.text === "string" &&
                  d.text.length > 50
                ) {
                  latestSummary = d.text;
                }
              }

              const finalSummary: string | undefined =
                queryResult?.data?.summary;
              if (typeof finalSummary === "string" && finalSummary.length > 50) {
                latestSummary = finalSummary;
              }

              const rawProducts: RawProduct[] =
                queryResult?.data?.products ?? [];
              if (rawProducts.length > 0)
                latestProducts = extractProducts(rawProducts);
            } catch {}
          }
        }

        // Process any remaining buffer
        if (buffer.trim()) {
          try {
            const obj = JSON.parse(buffer.trim());
            const queryResult =
              obj?.responses?.researchProductComparison?.[queryId];
            if (queryResult) {
              const finalSummary: string | undefined =
                queryResult?.data?.summary;
              if (
                typeof finalSummary === "string" &&
                finalSummary.length > 50
              ) {
                latestSummary = finalSummary;
              }
              const rawProducts: RawProduct[] =
                queryResult?.data?.products ?? [];
              if (rawProducts.length > 0)
                latestProducts = extractProducts(rawProducts);
              const statusLog: StatusLogEntry[] = queryResult.statusLog ?? [];
              const sources = extractSources(statusLog);
              if (sources.length > 0) latestSources = sources;
            }
          } catch {}
        }

        setStatusText("");

        if (!latestSummary.trim()) {
          latestSummary =
            "Analysis complete, but no summary was returned. Please try a different query.";
        }

        // Reveal word-by-word for natural streaming feel
        const words = latestSummary.split(" ");
        let displayed = "";
        for (let i = 0; i < words.length; i++) {
          displayed += (i === 0 ? "" : " ") + words[i];
          const snapshot = displayed;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId
                ? {
                    ...msg,
                    content: snapshot,
                    sources: latestSources,
                    products: latestProducts,
                  }
                : msg
            )
          );
          if (i % 10 === 9) {
            await new Promise((r) => setTimeout(r, 16));
          }
        }

        // Final flush with complete data
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiMessageId
              ? {
                  ...msg,
                  content: latestSummary,
                  sources: latestSources,
                  products: latestProducts,
                }
              : msg
          )
        );
      } catch (err) {
        console.error("API error:", err);
        const errMsg =
          err instanceof Error ? err.message : "An unknown error occurred.";
        setError(errMsg);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiMessageId && !msg.content
              ? {
                  ...msg,
                  content:
                    "Sorry, I encountered an error. Please try again.",
                }
              : msg
          )
        );
      } finally {
        setIsStreaming(false);
        setStatusText("");
      }
    },
    [isStreaming, messages]
  );

  return { messages, isStreaming, statusText, error, askQuestion, clearChat };
}
