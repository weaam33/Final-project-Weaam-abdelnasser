export default function BlueprintIllustration() {
  return (
    <svg
      viewBox="0 0 520 420"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="blueprint-svg"
      role="img"
      aria-label="Architectural line drawing of a house with a floor plan grid"
    >
      {/* ground line */}
      <line x1="20" y1="360" x2="500" y2="360" stroke="var(--line)" strokeWidth="1.5" />

      {/* floor plan grid, faint, behind the house */}
      <g stroke="var(--line)" strokeWidth="1">
        {Array.from({ length: 9 }).map((_, i) => (
          <line key={`v${i}`} x1={60 + i * 50} y1="140" x2={60 + i * 50} y2="360" />
        ))}
        {Array.from({ length: 5 }).map((_, i) => (
          <line key={`h${i}`} x1="60" y1={140 + i * 55} x2="460" y2={140 + i * 55} />
        ))}
      </g>

      {/* roof */}
      <path
        d="M90 190 L260 70 L430 190"
        stroke="var(--primary)"
        strokeWidth="2.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {/* house body */}
      <rect
        x="110"
        y="190"
        width="300"
        height="170"
        stroke="var(--primary)"
        strokeWidth="2.5"
      />
      {/* chimney */}
      <rect x="330" y="105" width="18" height="55" stroke="var(--primary)" strokeWidth="2" />

      {/* door */}
      <rect
        x="238"
        y="280"
        width="44"
        height="80"
        stroke="var(--accent)"
        strokeWidth="2.5"
      />
      <circle cx="272" cy="322" r="2.2" fill="var(--accent)" />

      {/* windows */}
      <g stroke="var(--primary)" strokeWidth="2">
        <rect x="140" y="230" width="50" height="40" />
        <line x1="165" y1="230" x2="165" y2="270" />
        <line x1="140" y1="250" x2="190" y2="250" />

        <rect x="330" y="230" width="50" height="40" />
        <line x1="355" y1="230" x2="355" y2="270" />
        <line x1="330" y1="250" x2="380" y2="250" />
      </g>

      {/* dimension markers, architectural touch */}
      <g stroke="var(--ink-muted)" strokeWidth="1">
        <line x1="110" y1="378" x2="410" y2="378" />
        <line x1="110" y1="372" x2="110" y2="384" />
        <line x1="410" y1="372" x2="410" y2="384" />
      </g>
      <text
        x="260"
        y="398"
        textAnchor="middle"
        fontFamily="var(--font-mono)"
        fontSize="12"
        fill="var(--ink-muted)"
      >
        carpet area
      </text>

      {/* small tree, single accent of organic shape against the geometry */}
      <g>
        <line x1="460" y1="360" x2="460" y2="320" stroke="var(--primary)" strokeWidth="2" />
        <circle cx="460" cy="300" r="22" stroke="var(--primary)" strokeWidth="2" />
      </g>
    </svg>
  );
}
