"""Generate a printable SVG cross-section without plotting dependencies."""

from html import escape

from .models import CalculationResult


def cross_section_svg(result: CalculationResult) -> str:
    total = max(result.unrestricted_wk, 0.1)
    scale = 700 / total
    left = result.left_allowance * scale
    road = result.travelled_width * scale
    right = result.right_allowance * scale
    wk = result.calculated_wk * scale
    return f"""
    <div style="font-family:system-ui;color:#17212b">
      <svg viewBox="0 0 780 230" role="img" aria-label="Road cross-section" style="width:100%;background:#f8fafc;border-radius:12px">
        <rect x="40" y="75" width="{left:.2f}" height="70" fill="#dbeafe"/>
        <rect x="{40 + left:.2f}" y="75" width="{road:.2f}" height="70" fill="#475569"/>
        <rect x="{40 + left + road:.2f}" y="75" width="{right:.2f}" height="70" fill="#dbeafe"/>
        <path d="M40 65v90 M740 65v90" stroke="#111827" stroke-width="5"/>
        <path d="M{40 + left:.2f} 75v70 M{40 + left + road:.2f} 75v70" stroke="#f8fafc" stroke-width="3" stroke-dasharray="10 8"/>
        <path d="M40 180h{wk:.2f} m-8 -5v10z M{40 + wk:.2f} 180l-8 -5v10z" stroke="#dc2626" stroke-width="2" fill="#dc2626"/>
        <text x="390" y="205" text-anchor="middle" font-size="16" fill="#b91c1c">Wk = {result.calculated_wk:.2f} m</text>
        <text x="{40 + left / 2:.2f}" y="115" text-anchor="middle" font-size="13">Left {result.left_allowance:.2f} m</text>
        <text x="{40 + left + road / 2:.2f}" y="115" text-anchor="middle" font-size="15" fill="white">Travelled way {result.travelled_width:.2f} m</text>
        <text x="{40 + left + road + right / 2:.2f}" y="115" text-anchor="middle" font-size="13">Right {result.right_allowance:.2f} m</text>
      </svg>
      <p style="font-size:.8rem">Diagrammatic only — dimensions govern. {escape(result.rule_applied)}</p>
    </div>"""
