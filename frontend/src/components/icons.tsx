type IconProps = { className?: string };

export function IconLayers({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <path d="M16 4 L29 11 L16 18 L3 11 Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M3 17 L16 24 L29 17" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M3 23 L16 30 L29 23" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    </svg>
  );
}

export function IconBolt({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <path
        d="M18 3 L7 18 H15 L13 29 L26 13 H18 Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconRuler({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <rect x="3" y="12" width="26" height="10" rx="1.5" stroke="currentColor" strokeWidth="2" />
      <path d="M8 12 V17 M13 12 V19 M18 12 V17 M23 12 V19" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

export function IconCoin({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <circle cx="16" cy="16" r="12" stroke="currentColor" strokeWidth="2" />
      <path d="M16 10 V22 M13 12.5 H18.5 A2.5 2.5 0 0 1 18.5 17.5 H13.5 A2.5 2.5 0 0 0 13.5 22.5 H19" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
