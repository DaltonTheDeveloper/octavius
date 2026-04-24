"use client";
import { motion } from "framer-motion";
import { Chrome, Terminal, Folder, Gamepad2, Globe, Bot } from "lucide-react";

/**
 * Animated mechanical arms emerging from a central core. Each arm is tipped
 * with an icon representing one capability domain. SVG-based, no images.
 */
export default function Arms() {
  const arms = [
    { angle: -150, length: 220, Icon: Gamepad2,  label: "UE5",     color: "#a855f7" },
    { angle: -110, length: 180, Icon: Chrome,    label: "Chrome",  color: "#22d3ee" },
    { angle:  -70, length: 240, Icon: Terminal,  label: "Shell",   color: "#fb923c" },
    { angle:  -30, length: 190, Icon: Folder,    label: "Files",   color: "#a855f7" },
    { angle:   30, length: 210, Icon: Globe,     label: "Network", color: "#22d3ee" },
    { angle:   80, length: 200, Icon: Bot,       label: "Custom",  color: "#fb923c" },
  ];

  return (
    <div className="relative w-full h-[520px] flex items-center justify-center">
      {/* central core */}
      <motion.div
        initial={{ scale: 0.6, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="absolute z-20"
      >
        <div className="relative h-32 w-32 rounded-full bg-gradient-to-br from-plasma-500 via-plasma-600 to-rust-600 ring-2 ring-plasma-300/40 shadow-[0_0_80px_rgba(168,85,247,0.6)]">
          <div className="absolute inset-2 rounded-full bg-ink-950/70 backdrop-blur grid place-items-center">
            <span className="font-mono text-xs tracking-[0.3em] text-plasma-300">CORE</span>
          </div>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
            className="absolute -inset-3 rounded-full border border-dashed border-plasma-400/30"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
            className="absolute -inset-7 rounded-full border border-dashed border-rust-400/20"
          />
        </div>
      </motion.div>

      {/* arms */}
      {arms.map((arm, i) => {
        const rad = (arm.angle * Math.PI) / 180;
        const tipX = Math.cos(rad) * arm.length;
        const tipY = Math.sin(rad) * arm.length;
        const Icon = arm.Icon;
        return (
          <motion.div
            key={arm.label}
            className="absolute z-10"
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 + i * 0.12, duration: 0.5 }}
            style={{ width: 0, height: 0 }}
          >
            {/* arm line */}
            <svg
              className="absolute"
              width={Math.abs(tipX) + 80}
              height={Math.abs(tipY) + 80}
              style={{
                left: tipX < 0 ? tipX - 40 : -40,
                top: tipY < 0 ? tipY - 40 : -40,
                overflow: "visible",
                pointerEvents: "none",
              }}
            >
              <defs>
                <linearGradient id={`g-${i}`} x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor={arm.color} stopOpacity="0.9" />
                  <stop offset="100%" stopColor={arm.color} stopOpacity="0.2" />
                </linearGradient>
              </defs>
              <motion.path
                d={`M ${tipX < 0 ? -tipX + 40 : 40} ${tipY < 0 ? -tipY + 40 : 40}
                    Q ${tipX < 0 ? -tipX / 2 + 40 : tipX / 2 + 40} ${(tipY < 0 ? -tipY + 40 : tipY + 40) - 40},
                      ${tipX < 0 ? 40 : tipX + 40} ${tipY < 0 ? 40 : tipY + 40}`}
                stroke={`url(#g-${i})`}
                strokeWidth="3"
                fill="none"
                strokeLinecap="round"
                animate={{ pathLength: [0.95, 1, 0.95] }}
                transition={{ duration: 4 + i * 0.5, repeat: Infinity, ease: "easeInOut" }}
              />
              {/* segment joints */}
              {[0.33, 0.66].map((t) => (
                <circle
                  key={t}
                  cx={(tipX < 0 ? -tipX + 40 : 40) + ((tipX < 0 ? 40 : tipX + 40) - (tipX < 0 ? -tipX + 40 : 40)) * t}
                  cy={(tipY < 0 ? -tipY + 40 : 40) + ((tipY < 0 ? 40 : tipY + 40) - (tipY < 0 ? -tipY + 40 : 40)) * t - 20 * (1 - Math.abs(2 * t - 1))}
                  r="3"
                  fill={arm.color}
                  opacity="0.9"
                />
              ))}
            </svg>

            {/* tip with icon */}
            <motion.div
              className="absolute"
              style={{ left: tipX, top: tipY }}
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 4 + i * 0.4, repeat: Infinity, ease: "easeInOut" }}
            >
              <div
                className="relative -translate-x-1/2 -translate-y-1/2 h-14 w-14 rounded-2xl grid place-items-center backdrop-blur border ring-1"
                style={{
                  background: `linear-gradient(135deg, ${arm.color}22, transparent)`,
                  borderColor: `${arm.color}66`,
                  boxShadow: `0 0 24px ${arm.color}44`,
                }}
              >
                <Icon size={22} style={{ color: arm.color }} />
                <div
                  className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] tracking-widest font-mono"
                  style={{ color: arm.color }}
                >
                  {arm.label.toUpperCase()}
                </div>
              </div>
            </motion.div>
          </motion.div>
        );
      })}

      {/* scanning line */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none rounded-3xl">
        <div className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-plasma-400/60 to-transparent animate-scan" />
      </div>
    </div>
  );
}
