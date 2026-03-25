import { motion } from "framer-motion";

const stats = [
  { value: "Millions", label: "Reviews Analyzed" },
  { value: "Real-time", label: "Intelligence" },
  { value: "Unbiased", label: "AI Verdict" },
];

export function HeroSection() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.7 }}
      className="w-full max-w-3xl mx-auto pt-16 pb-6 text-center"
    >
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/20 bg-primary/8 mb-8"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
        <span className="text-[11px] font-semibold tracking-widest uppercase text-primary/90">
          AI Shopping Analyst
        </span>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="font-display text-5xl md:text-[4.25rem] font-bold leading-[1.08] tracking-tight mb-6"
      >
        The Intelligence
        <br />
        <span className="text-primary">Behind Every</span>
        <br />
        Purchase
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="text-base md:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed mb-10"
      >
        Ask about any product, brand, or deal. ShopSense analyzes thousands of
        expert reviews and surfaces exactly what matters.
      </motion.p>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="flex items-center justify-center gap-8 md:gap-12"
      >
        {stats.map((stat, i) => (
          <div key={i} className="text-center">
            <div className="font-display text-lg font-bold text-foreground">{stat.value}</div>
            <div className="text-[11px] text-muted-foreground tracking-wide mt-0.5">{stat.label}</div>
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
}
