import { useState, useRef, useEffect } from "react";
import { ArrowUp, Square } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (query: string) => void;
  isStreaming: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, isStreaming, placeholder }: ChatInputProps) {
  const [query, setQuery] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`;
  }, [query]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (query.trim() && !isStreaming) {
      onSend(query.trim());
      setQuery("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSubmit = query.trim().length > 0 && !isStreaming;

  return (
    <div className="relative w-full max-w-3xl mx-auto">
      {/* Glow ring */}
      <div
        className={cn(
          "absolute -inset-px rounded-2xl pointer-events-none transition-opacity duration-300",
          canSubmit ? "opacity-100" : "opacity-0",
        )}
        style={{
          background:
            "linear-gradient(135deg, hsl(28 90% 55% / 0.3), hsl(195 75% 52% / 0.15))",
          borderRadius: "inherit",
          filter: "blur(8px)",
        }}
      />

      <form
        onSubmit={handleSubmit}
        className="relative flex items-end gap-2 bg-card border border-border rounded-2xl p-2 shadow-lg transition-all duration-200 focus-within:border-primary/40"
      >
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? "Ask about any product, deal, or shopping question…"}
          disabled={isStreaming}
          rows={1}
          className="w-full min-h-[52px] max-h-[180px] py-3.5 pl-4 pr-2 bg-transparent text-sm text-foreground placeholder:text-muted-foreground/60 resize-none outline-none overflow-y-auto leading-relaxed"
        />

        <button
          type="submit"
          disabled={!canSubmit}
          className={cn(
            "flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200",
            canSubmit
              ? "bg-primary text-primary-foreground shadow-md shadow-primary/25 hover:brightness-110 active:scale-95"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          )}
        >
          {isStreaming ? (
            <Square className="w-3.5 h-3.5 fill-current" />
          ) : (
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          )}
        </button>
      </form>

      <p className="text-center text-[11px] text-muted-foreground/50 mt-2.5">
        ShopSense AI · Verify important purchasing decisions independently
      </p>
    </div>
  );
}
