export type CurrencyCode = "INR" | "USD" | "EGP";

interface CurrencyInfo {
  code: CurrencyCode;
  symbol: string;
  label: string;
  /** Approximate mid-market rate: 1 INR -> this currency (Aug 2026). */
  rateFromInr: number;
}

export const CURRENCIES: Record<CurrencyCode, CurrencyInfo> = {
  INR: { code: "INR", symbol: "₹", label: "Indian Rupee", rateFromInr: 1 },
  USD: { code: "USD", symbol: "$", label: "US Dollar", rateFromInr: 0.01044 },
  EGP: { code: "EGP", symbol: "E£", label: "Egyptian Pound", rateFromInr: 0.531 },
};

/** The backend always returns a price in INR; convert + format for display. */
export function formatPrice(priceInr: number, currency: CurrencyCode): string {
  const { symbol, rateFromInr } = CURRENCIES[currency];
  const value = priceInr * rateFromInr;

  if (currency === "INR") {
    if (value >= 1e7) return `${symbol} ${(value / 1e7).toFixed(2)} Cr`;
    if (value >= 1e5) return `${symbol} ${(value / 1e5).toFixed(2)} Lac`;
    return `${symbol} ${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  }

  // USD / EGP: use compact "K" / "M" notation for large numbers.
  if (value >= 1e6) return `${symbol} ${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `${symbol} ${(value / 1e3).toFixed(1)}K`;
  return `${symbol} ${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}
