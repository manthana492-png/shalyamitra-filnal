/**
 * AnimatedNumber — smooth counter transition component.
 *
 * Spec: "Data value change: 200ms counter animation
 * (old → new, values never jump, they transition)"
 *
 * Uses requestAnimationFrame for 60fps interpolation.
 * Zero dependencies.
 */

import { useEffect, useRef, useState } from "react";

type AnimatedNumberProps = {
  value: number;
  duration?: number;    // ms, default 200
  decimals?: number;    // decimal places, default 0
  className?: string;
};

export function AnimatedNumber({
  value,
  duration = 200,
  decimals = 0,
  className,
}: AnimatedNumberProps) {
  const [display, setDisplay] = useState(value);
  const prevRef = useRef(value);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const from = prevRef.current;
    const to = value;
    prevRef.current = value;

    if (from === to) return;

    const startTime = performance.now();
    const diff = to - from;

    const step = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic for smooth deceleration
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = from + diff * eased;

      setDisplay(current);

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(step);
      } else {
        setDisplay(to);
      }
    };

    rafRef.current = requestAnimationFrame(step);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [value, duration]);

  const formatted = decimals > 0
    ? display.toFixed(decimals)
    : Math.round(display).toString();

  return <span className={className}>{formatted}</span>;
}

export default AnimatedNumber;
