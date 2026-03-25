import { useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, RotateCcw } from "lucide-react";
import { useChatStream } from "@/hooks/use-chat-stream";
import { HeroSection } from "@/components/hero-section";
import { ChatInput } from "@/components/chat-input";
import { ChatBubble } from "@/components/chat-bubble";

const EXAMPLE_QUERIES = [
  "Should I buy the PS5 in 2025?",
  "Best noise-cancelling headphones under ₹10,000",
  "iPhone 15 vs Samsung Galaxy S24",
  "Are refurbished MacBooks worth it?",
  "Best budget mechanical keyboard for coding",
  "Is the Apple Watch Ultra worth the price?",
];

export default function Home() {
  const { messages, isStreaming, statusText, error, askQuestion, clearChat } =
    useChatStream();

  // Separate refs: one for scroll container, one for the sentinel
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef(true);

  const hasMessages = messages.length > 0;

  // Track whether the user is near the bottom of the scroll container
  const handleScroll = useCallback(() => {
    const el = chatScrollRef.current;
    if (!el) return;
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    isNearBottomRef.current = distFromBottom < 120;
  }, []);

  // Auto-scroll to bottom only when: (a) new user message sent, or (b) streaming
  // and user is already near the bottom (follow behaviour)
  useEffect(() => {
    const el = chatScrollRef.current;
    if (!el) return;

    const lastMsg = messages[messages.length - 1];
    const justSentUserMsg = lastMsg?.role === "user";

    if (justSentUserMsg || (isStreaming && isNearBottomRef.current)) {
      // Instant scroll when user sends; smooth follow while streaming
      el.scrollTop = el.scrollHeight;
    }
  }, [messages, isStreaming]);

  return (
    /*
     * h-screen + overflow-hidden on root is the critical fix.
     * Without an explicit height, flex children using overflow-y-auto
     * have no upper bound and never create an actual scroll region.
     */
    <div className="h-screen bg-background text-foreground flex flex-col relative overflow-hidden">
      {/* Ambient background glows */}
      <div className="ambient-glow-left" />
      <div className="ambient-glow-right" />

      {/* ── Header ── */}
      <header className="relative z-10 flex-shrink-0 w-full px-6 py-4 flex items-center justify-between border-b border-border/30">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-primary/15 border border-primary/25 flex items-center justify-center">
            <span className="font-display text-sm font-bold text-primary">S</span>
          </div>
          <span className="font-display font-bold text-[17px] tracking-tight">
            ShopSense<span className="text-primary">.ai</span>
          </span>
        </div>

        <AnimatePresence>
          {hasMessages && (
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              onClick={clearChat}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary hover:bg-muted border border-border text-xs font-medium text-muted-foreground hover:text-foreground transition-all duration-200"
            >
              <RotateCcw className="w-3 h-3" />
              New Chat
            </motion.button>
          )}
        </AnimatePresence>
      </header>

      {/* ── Main content area ── */}
      {/*
       * flex-1 min-h-0 = take remaining height but allow shrinking below content size.
       * Without min-h-0, flex children can't scroll internally.
       */}
      <main className="relative z-10 flex-1 min-h-0 w-full max-w-4xl mx-auto px-4 sm:px-6 flex flex-col">
        <AnimatePresence mode="wait">
          {!hasMessages ? (
            /* ── Hero / Landing ── */
            <motion.div
              key="hero"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.3 }}
              className="flex-1 min-h-0 overflow-y-auto flex flex-col justify-center pb-8"
            >
              <HeroSection />
              <div className="w-full mt-6 pb-6">
                <ChatInput onSend={askQuestion} isStreaming={isStreaming} />
                <div className="mt-8 flex flex-wrap justify-center gap-2">
                  {EXAMPLE_QUERIES.map((query, i) => (
                    <motion.button
                      key={i}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 + i * 0.055, duration: 0.3 }}
                      onClick={() => askQuestion(query)}
                      className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-secondary border border-border hover:border-primary/30 hover:bg-muted text-[12px] text-muted-foreground hover:text-foreground transition-all duration-200 group"
                    >
                      <Search className="w-3 h-3 text-muted-foreground/50 group-hover:text-primary transition-colors" />
                      {query}
                    </motion.button>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            /* ── Chat View ── */
            <motion.div
              key="chat"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.25 }}
              ref={chatScrollRef}
              onScroll={handleScroll}
              /*
               * overflow-y-auto + min-h-0 = the scroll container.
               * The padding-bottom creates space so content isn't hidden
               * behind the fixed floating input bar (≈188px tall).
               */
              className="flex-1 min-h-0 overflow-y-auto"
            >
              <div className="pt-5 pb-52 px-0.5">
                {messages.map((msg, index) => {
                  const isLast = index === messages.length - 1;
                  return (
                    <ChatBubble
                      key={msg.id}
                      message={msg}
                      isStreamingLast={
                        isLast && isStreaming && msg.role === "ai"
                      }
                    />
                  );
                })}

                {/* Live status indicator */}
                <AnimatePresence>
                  {isStreaming && statusText && (
                    <motion.div
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center gap-2.5 px-1 mb-4 ml-11"
                    >
                      <div className="flex gap-1">
                        {[0, 120, 240].map((d) => (
                          <span
                            key={d}
                            className="w-1 h-1 rounded-full bg-primary/60 animate-bounce"
                            style={{ animationDelay: `${d}ms` }}
                          />
                        ))}
                      </div>
                      <span className="text-[11px] text-muted-foreground italic">
                        {statusText}
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {error && (
                  <div className="max-w-3xl mx-auto w-full p-3.5 mb-6 bg-destructive/10 border border-destructive/20 rounded-xl text-destructive-foreground/80 text-center text-xs">
                    {error}
                  </div>
                )}

                {/* Invisible sentinel at the end */}
                <div ref={sentinelRef} className="h-px" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ── Floating input (chat mode only) ── */}
      <AnimatePresence>
        {hasMessages && (
          <motion.div
            initial={{ opacity: 0, y: 64 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 64 }}
            transition={{ type: "spring", damping: 28, stiffness: 320 }}
            className="absolute bottom-0 left-0 right-0 z-20 px-4 pb-5 pt-16 bg-gradient-to-t from-background via-background/96 to-transparent pointer-events-none"
          >
            <div className="pointer-events-auto max-w-4xl mx-auto">
              <ChatInput onSend={askQuestion} isStreaming={isStreaming} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
