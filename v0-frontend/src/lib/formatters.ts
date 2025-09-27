export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format a decimal as percentage
 */
export const formatPercentage = (decimal: number): string => {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  }).format(decimal)
}

/**
 * Format large numbers with K/M suffixes
 */
export const formatCompactNumber = (num: number): string => {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    compactDisplay: "short",
  }).format(num)
}

/**
 * Format a number with commas for readability
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat("en-US").format(num)
}
