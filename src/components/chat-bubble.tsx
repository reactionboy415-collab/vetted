import { motion } from "framer-motion";
import { User, ExternalLink, ShoppingBag, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessage, Source, Product } from "@/hooks/use-chat-stream";

interface ChatBubbleProps {
  message: ChatMessage;
  isStreamingLast?: boolean;
}

/* ─── Inline markdown parser ─── */
function parseInline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={i} className="font-semibold text-foreground">
              {part.slice(2, -2)}
            </strong>
          );
        }
        if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
          return <em key={i}>{part.slice(1, -1)}</em>;
        }
        return part;
      })}
    </>
  );
}

function MarkdownRenderer({ text }: { text: string }) {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      i++;
      continue;
    }

    if (trimmed.startsWith("### ")) {
      elements.push(
        <h3
          key={i}
          className="font-display text-[13px] font-semibold uppercase tracking-widest text-primary mt-5 mb-2 first:mt-0"
        >
          {parseInline(trimmed.slice(4))}
        </h3>
      );
      i++;
      continue;
    }

    if (trimmed.startsWith("## ")) {
      elements.push(
        <h2
          key={i}
          className="font-display text-base font-semibold text-foreground mt-5 mb-2 first:mt-0"
        >
          {parseInline(trimmed.slice(3))}
        </h2>
      );
      i++;
      continue;
    }

    if (/^[\*\-]\s/.test(trimmed)) {
      const listItems: React.ReactNode[] = [];
      while (i < lines.length) {
        const t = lines[i].trim();
        if (/^[\*\-]\s/.test(t)) {
          const content = t.replace(/^[\*\-]\s+/, "");
          listItems.push(
            <li key={i} className="flex gap-2 items-start">
              <span className="mt-2 w-1 h-1 rounded-full bg-primary flex-shrink-0" />
              <span>{parseInline(content)}</span>
            </li>
          );
          i++;
        } else if (!t) {
          i++;
          break;
        } else {
          break;
        }
      }
      elements.push(
        <ul key={`ul-${i}`} className="space-y-1.5 my-2">
          {listItems}
        </ul>
      );
      continue;
    }

    elements.push(
      <p key={i} className="text-sm leading-relaxed text-foreground/85">
        {parseInline(trimmed)}
      </p>
    );
    i++;
  }

  return <div className="space-y-2.5">{elements}</div>;
}

/* ─── Product Cards ─── */
function ProductCards({ products }: { products: Product[] }) {
  if (!products.length) return null;

  const formatPrice = (price: Product["price"]) => {
    if (!price) return null;
    const amount = price.amount / 100;
    if (price.currency === "INR") return `₹${amount.toLocaleString("en-IN")}`;
    return `${price.currency} ${amount.toLocaleString()}`;
  };

  return (
    <div className="mt-5 pt-4 border-t border-border/50">
      <div className="flex items-center gap-2 mb-3">
        <ShoppingBag className="w-3.5 h-3.5 text-primary" />
        <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Products Found
        </span>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-thin">
        {products.map((product, i) => (
          <div
            key={i}
            className="flex-shrink-0 w-48 bg-card border border-border rounded-xl overflow-hidden group"
          >
            {product.imageUrls[0] && (
              <div className="w-full h-28 bg-muted overflow-hidden">
                <img
                  src={product.imageUrls[0]}
                  alt={product.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              </div>
            )}
            <div className="p-3">
              <p className="text-[12px] font-semibold text-foreground line-clamp-2 leading-tight mb-1">
                {product.name}
              </p>
              {product.price && (
                <p className="text-[11px] font-bold text-primary mb-2">
                  {formatPrice(product.price)}
                </p>
              )}
              {product.purchaseUrl && (
                <a
                  href={product.purchaseUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-[11px] font-medium text-primary/80 hover:text-primary transition-colors"
                >
                  View Product
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Source Cards ─── */
function SourceCards({ sources }: { sources: Source[] }) {
  if (!sources.length) return null;

  const displayed = sources.slice(0, 9);

  return (
    <div className="mt-4 pt-4 border-t border-border/50">
      <div className="flex items-center gap-2 mb-3">
        <BookOpen className="w-3.5 h-3.5 text-muted-foreground" />
        <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Sources ({sources.length})
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {displayed.map((source, i) => (
          <a
            key={i}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            title={source.title}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-muted hover:bg-muted/80 border border-border/60 hover:border-primary/30 transition-all duration-200 group max-w-[200px]"
          >
            <img
              src={`https://www.google.com/s2/favicons?domain=${source.domain}&sz=16`}
              alt=""
              className="w-3.5 h-3.5 flex-shrink-0 rounded-sm"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
            <span className="text-[11px] text-muted-foreground group-hover:text-foreground transition-colors truncate">
              {source.domain}
            </span>
          </a>
        ))}
        {sources.length > 9 && (
          <div className="flex items-center px-2.5 py-1.5 text-[11px] text-muted-foreground">
            +{sources.length - 9} more
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Main ChatBubble ─── */
export function ChatBubble({ message, isStreamingLast }: ChatBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.25, 0.1, 0.25, 1] }}
      className={cn("flex w-full gap-3 max-w-4xl mx-auto mb-6", isUser ? "justify-end" : "justify-start")}
    >
      {!isUser && (
        <div className="flex-shrink-0 mt-0.5">
          <div className="w-8 h-8 rounded-xl bg-primary/15 border border-primary/25 flex items-center justify-center">
            <span className="font-display text-xs font-bold text-primary">S</span>
          </div>
        </div>
      )}

      <div className={cn("relative", isUser ? "max-w-[82%]" : "max-w-[92%] flex-1")}>
        {isUser ? (
          <div className="px-5 py-3.5 rounded-2xl rounded-tr-sm bg-secondary border border-white/5 text-sm text-foreground/90 leading-relaxed">
            {message.content}
          </div>
        ) : (
          <div>
            {message.content ? (
              <div className="text-sm">
                <MarkdownRenderer text={message.content} />
                {isStreamingLast && (
                  <span className="inline-block w-[2px] h-4 ml-1 bg-primary cursor-blink align-middle rounded-full" />
                )}
              </div>
            ) : (
              <div className="flex gap-1.5 items-center h-8">
                {[0, 150, 300].map((delay) => (
                  <span
                    key={delay}
                    className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
            )}

            {message.content && !isStreamingLast && (
              <>
                {message.products && message.products.length > 0 && (
                  <ProductCards products={message.products} />
                )}
                {message.sources && message.sources.length > 0 && (
                  <SourceCards sources={message.sources} />
                )}
              </>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 mt-0.5">
          <div className="w-8 h-8 rounded-xl bg-secondary border border-white/8 flex items-center justify-center">
            <User className="w-4 h-4 text-muted-foreground" />
          </div>
        </div>
      )}
    </motion.div>
  );
}
