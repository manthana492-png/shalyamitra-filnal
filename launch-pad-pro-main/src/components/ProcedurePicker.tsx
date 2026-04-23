/**
 * ProcedurePicker — Domain-aware smart search component.
 *
 * Shows a searchable list of procedures filtered by domain (ayurveda / modern).
 * Supports:
 *  - Fuzzy search across label + category
 *  - Category grouping for Modern domain
 *  - "Custom / Other" free-text entry
 *  - Keyboard navigation (↑ ↓ Enter)
 */

import { useState, useRef, useEffect, useMemo } from "react";
import { Search, ChevronDown, X } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  getProceduresByDomain,
  type ProcedureEntry,
} from "@/lib/procedures";

type Domain = "ayurveda" | "modern";

interface ProcedurePickerProps {
  domain: Domain;
  value: string;
  onChange: (value: string) => void;
}

export function ProcedurePicker({ domain, value, onChange }: ProcedurePickerProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [activeIdx, setActiveIdx] = useState(0);
  const [customText, setCustomText] = useState("");
  const [isCustom, setIsCustom] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const procedures = getProceduresByDomain(domain);

  // Filter by search query
  const filtered = useMemo(() => {
    if (!query.trim()) return procedures;
    const q = query.toLowerCase();
    return procedures.filter(
      (p) =>
        p.label.toLowerCase().includes(q) ||
        (p.category?.toLowerCase().includes(q) ?? false),
    );
  }, [query, procedures]);

  // Group by category for modern domain
  const grouped = useMemo(() => {
    if (domain === "ayurveda") {
      return { "": filtered };
    }
    const map: Record<string, ProcedureEntry[]> = {};
    for (const p of filtered) {
      const cat = p.category ?? "Other";
      if (!map[cat]) map[cat] = [];
      map[cat].push(p);
    }
    return map;
  }, [filtered, domain]);

  const flatFiltered = filtered;

  // Selected label display
  const selectedLabel = isCustom
    ? customText || "Custom / Other Procedure"
    : procedures.find((p) => p.label === value)?.label || value || "Select procedure…";

  // When domain changes, reset
  useEffect(() => {
    setQuery("");
    setActiveIdx(0);
    setIsCustom(false);
  }, [domain]);

  const handleSelect = (proc: ProcedureEntry) => {
    if (proc.custom) {
      setIsCustom(true);
      setOpen(false);
      setQuery("");
      onChange("Custom / Other Procedure");
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setIsCustom(false);
      onChange(proc.label);
      setOpen(false);
      setQuery("");
    }
    setActiveIdx(0);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open) {
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        setOpen(true);
        e.preventDefault();
      }
      return;
    }
    if (e.key === "ArrowDown") {
      setActiveIdx((i) => Math.min(i + 1, flatFiltered.length - 1));
      e.preventDefault();
    } else if (e.key === "ArrowUp") {
      setActiveIdx((i) => Math.max(i - 1, 0));
      e.preventDefault();
    } else if (e.key === "Enter") {
      if (flatFiltered[activeIdx]) handleSelect(flatFiltered[activeIdx]);
      e.preventDefault();
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  // Scroll active item into view
  useEffect(() => {
    if (!listRef.current) return;
    const el = listRef.current.querySelector(`[data-idx="${activeIdx}"]`);
    el?.scrollIntoView({ block: "nearest" });
  }, [activeIdx]);

  return (
    <div className={cn("relative w-full", open && "z-[70]")}>
      {/* Trigger */}
      <button
        type="button"
        onClick={() => { setOpen((o) => !o); }}
        onKeyDown={handleKeyDown}
        className={cn(
          "w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-md border text-sm transition-colors text-left",
          "bg-surface-2/50 border-border hover:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50",
          open && "border-primary/60 ring-1 ring-primary/40",
        )}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className={cn("flex-1 truncate", !value && "text-muted-foreground")}>
          {selectedLabel}
        </span>
        <ChevronDown className={cn("h-4 w-4 text-muted-foreground shrink-0 transition-transform", open && "rotate-180")} />
      </button>

      {/* Custom text input (when "Custom / Other" chosen) */}
      {isCustom && (
        <div className="mt-2 flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            placeholder="Describe the procedure…"
            value={customText}
            onChange={(e) => {
              setCustomText(e.target.value);
              onChange(e.target.value || "Custom / Other Procedure");
            }}
            className="flex-1 px-3 py-2 text-sm rounded-md border border-primary/40 bg-surface-2/50 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary/50"
          />
          <button
            type="button"
            onClick={() => { setIsCustom(false); onChange(""); setCustomText(""); }}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Dropdown */}
      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border border-primary/30 bg-surface-1 shadow-2xl overflow-hidden">
          {/* Search box */}
          <div className="sticky top-0 border-b border-primary/20 bg-surface-1 px-3 py-2 flex items-center gap-2">
            <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
            <input
              type="text"
              autoFocus
              placeholder="Search procedures…"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setActiveIdx(0); }}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
            />
            {query && (
              <button type="button" onClick={() => setQuery("")}>
                <X className="h-3.5 w-3.5 text-muted-foreground hover:text-foreground" />
              </button>
            )}
          </div>

          {/* Results */}
          <div
            ref={listRef}
            className="max-h-72 overflow-y-auto overscroll-contain"
            role="listbox"
          >
            {flatFiltered.length === 0 && (
              <div className="px-4 py-6 text-center text-sm text-muted-foreground">
                No procedures match "{query}"
              </div>
            )}

            {domain === "modern"
              ? // Grouped by category
                Object.entries(grouped).map(([cat, items]) => (
                  <div key={cat}>
                    {cat && (
                      <div className="px-3 pt-3 pb-1 text-[10px] uppercase tracking-[0.2em] text-primary/50 font-semibold">
                        {cat}
                      </div>
                    )}
                    {items.map((proc) => {
                      const idx = flatFiltered.indexOf(proc);
                      const isActive = idx === activeIdx;
                      const isSelected = proc.label === value;
                      return (
                        <button
                          key={proc.id}
                          type="button"
                          role="option"
                          aria-selected={isSelected}
                          data-idx={idx}
                          onClick={() => handleSelect(proc)}
                          onMouseEnter={() => setActiveIdx(idx)}
                          className={cn(
                            "w-full text-left px-4 py-2 text-sm transition-colors flex items-center gap-2",
                            isActive && "bg-primary/10 text-foreground",
                            isSelected && "text-primary font-medium",
                            !isActive && !isSelected && "text-foreground/80 hover:bg-surface-2",
                            proc.custom && "italic text-primary/70",
                          )}
                        >
                          {isSelected && (
                            <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                          )}
                          <span className="flex-1 truncate">{proc.label}</span>
                        </button>
                      );
                    })}
                  </div>
                ))
              : // Flat list for Ayurveda
                flatFiltered.map((proc, idx) => {
                  const isActive = idx === activeIdx;
                  const isSelected = proc.label === value;
                  return (
                    <button
                      key={proc.id}
                      type="button"
                      role="option"
                      aria-selected={isSelected}
                      data-idx={idx}
                      onClick={() => handleSelect(proc)}
                      onMouseEnter={() => setActiveIdx(idx)}
                      className={cn(
                        "w-full text-left px-4 py-2 text-sm transition-colors flex items-center gap-2",
                        isActive && "bg-primary/10 text-foreground",
                        isSelected && "text-primary font-medium",
                        !isActive && !isSelected && "text-foreground/80 hover:bg-surface-2",
                        proc.custom && "italic text-primary/70",
                      )}
                    >
                      {isSelected && (
                        <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                      )}
                      <span className="flex-1 truncate">{proc.label}</span>
                    </button>
                  );
                })}
          </div>

          {/* Count footer */}
          <div className="border-t border-primary/15 px-3 py-1.5 text-mono text-[10px] text-muted-foreground">
            {filtered.length} of {procedures.length} procedures
          </div>
        </div>
      )}
    </div>
  );
}
