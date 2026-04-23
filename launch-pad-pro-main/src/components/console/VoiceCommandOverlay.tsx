/**
 * VoiceCommandOverlay — Full-screen glassmorphic help overlay.
 * Shows categorised voice commands. Auto-dismisses after 10 seconds.
 */

import { useDirector } from "@/lib/director";
import { useEffect } from "react";
import { X, Camera, Microscope, Activity, BookOpen, Wrench, Volume2 } from "lucide-react";

const COMMAND_GROUPS = [
  {
    icon: Camera,
    label: "Cameras",
    commands: [
      "expand surgical camera",
      "show all cameras",
      "show monitor",
      "show overhead",
    ],
  },
  {
    icon: Microscope,
    label: "Anatomy",
    commands: [
      "mark arteries",
      "mark veins",
      "mark nerves",
      "mark marma points",
      "mark everything",
      "remove overlays",
    ],
  },
  {
    icon: Activity,
    label: "Vitals & Drugs",
    commands: [
      "show pharmacokinetics",
      "show drug doses",
    ],
  },
  {
    icon: BookOpen,
    label: "Knowledge",
    commands: [
      "show risk flags",
      "show shloka",
      "show imaging",
    ],
  },
  {
    icon: Wrench,
    label: "Status",
    commands: [
      "instrument count",
      "retraction timer",
    ],
  },
  {
    icon: Volume2,
    label: "Control",
    commands: [
      "acknowledged",
      "clear / back",
      "mute / unmute",
      "lock layout",
      "end session",
    ],
  },
];

export function VoiceCommandOverlay() {
  const { showVoiceHelp, setShowVoiceHelp } = useDirector();

  useEffect(() => {
    if (showVoiceHelp) {
      const timer = setTimeout(() => setShowVoiceHelp(false), 10000);
      return () => clearTimeout(timer);
    }
  }, [showVoiceHelp, setShowVoiceHelp]);

  if (!showVoiceHelp) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center animate-fade-in"
      style={{ background: "rgba(0, 0, 0, 0.7)", backdropFilter: "blur(12px)" }}
    >
      <div className="max-w-3xl w-[90vw] glass-panel rounded-2xl p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Voice Commands</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Say <span className="text-primary font-medium">"Nael, ..."</span> followed by any command below
            </p>
          </div>
          <button onClick={() => setShowVoiceHelp(false)} className="p-1 hover:bg-surface-3 rounded-md">
            <X className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>

        {/* Command grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {COMMAND_GROUPS.map((group) => (
            <div key={group.label}>
              <div className="flex items-center gap-1.5 mb-2">
                <group.icon className="h-3.5 w-3.5 text-primary" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-primary/70">
                  {group.label}
                </span>
              </div>
              <ul className="space-y-1">
                {group.commands.map((cmd) => (
                  <li key={cmd} className="text-xs text-foreground/80 font-mono">
                    "{cmd}"
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Auto-dismiss hint */}
        <p className="text-[10px] text-muted-foreground text-center mt-5">
          Auto-dismisses in 10 seconds
        </p>
      </div>
    </div>
  );
}

export default VoiceCommandOverlay;
