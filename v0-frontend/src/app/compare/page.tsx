"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, TrendingUp, TrendingDown, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { formatCurrency } from "@/lib/formatters"
import { useApi } from "@/hooks/use-api"

interface ComparisonData {
  [scenarioName: string]: {
    description: string
    results: {
      cost_difference: {
        columns: string[]
        data: string[][]
      }
      monthly_payment: {
        columns: string[]
        data: string[][]
      }
      summary: {
        columns: string[]
        data: string[][]
      }
    }
  }
}

// Helper function to extract total cost difference from the cost_difference data
const extractTotalCostDifference = (costDifferenceData: { data: string[][] }): number => {
  const totalRow = costDifferenceData.data.find(row => row[0] === "TOTAL COST DIFFERENCE")
  if (totalRow && totalRow[1]) {
    // Remove $ and commas, then parse
    const numericValue = totalRow[1].replace(/[$,]/g, '')
    return parseFloat(numericValue) || 0
  }
  return 0
}

// Helper function to extract monthly payment difference
const extractMonthlyPaymentDifference = (monthlyPaymentData: { data: string[][] }): number => {
  const totalRow = monthlyPaymentData.data.find(row => row[0] === "TOTAL MONTHLY")
  if (totalRow && totalRow[1] && totalRow[2]) {
    // Get new vehicle payment and current vehicle payment
    const newVehiclePayment = parseFloat(totalRow[1].replace(/[$,]/g, '')) || 0
    const currentVehiclePayment = parseFloat(totalRow[2].replace(/[$,]/g, '')) || 0
    return newVehiclePayment - currentVehiclePayment
  }
  return 0
}

export default function ComparePage() {
  const [data, setData] = useState<ComparisonData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { get } = useApi()

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        console.log("[v0] Starting to fetch comparison results...")
        const response = await get("/comparison-results")
        console.log("[v0] Successfully loaded comparison data")
        setData(response)
        setError(null)
      } catch (err) {
        console.error("[v0] Failed to load comparison:", err)
        setError(err instanceof Error ? err.message : "Failed to load comparison data")
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchComparison()
  }, []) // Empty dependency array - only run once on mount

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-3 text-muted-foreground">Loading comparison...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <Card className="max-w-lg mx-auto">
            <CardHeader>
              <CardTitle className="text-destructive">Comparison Error</CardTitle>
            </CardHeader>
            <CardContent>
              <Alert className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-sm">{error || "Unable to load comparison data"}</AlertDescription>
              </Alert>
              <Link href="/">
                <Button variant="outline">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Scenarios
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const scenarios = Object.entries(data)

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Vehicle Cost Comparison</h1>
            <p className="text-muted-foreground">Compare all scenarios against keeping your current vehicle</p>
          </div>
        </div>

        {/* Comparison Cards */}
        <div className="grid gap-6">
          {scenarios.map(([scenarioName, scenario]) => {
            const costDifference = extractTotalCostDifference(scenario.results.cost_difference)
            const monthlyPaymentDifference = extractMonthlyPaymentDifference(scenario.results.monthly_payment)
            
            return (
              <Card key={scenarioName} className="overflow-hidden">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">{scenario.description}</CardTitle>
                      <CardDescription className="mt-1">3-year cost comparison</CardDescription>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge
                        variant={costDifference > 0 ? "destructive" : "default"}
                        className="text-sm px-3 py-1"
                      >
                        {costDifference > 0 ? (
                          <TrendingUp className="h-4 w-4 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 mr-1" />
                        )}
                        {costDifference > 0 ? "+" : ""}
                        {formatCurrency(costDifference)}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
              <CardContent>
                {/* Summary Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        {scenario.results.summary.columns.map((column, index) => (
                          <th
                            key={index}
                            className={`text-left p-3 font-medium ${
                              index === 0 ? "w-1/3" : "text-right"
                            }`}
                          >
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {scenario.results.summary.data.map((row, rowIndex) => {
                        const isTotal = row[0] === "NET OUT-OF-POCKET"
                        const isSubtotal = row[0] === "SUBTOTAL"
                        
                        return (
                          <tr
                            key={rowIndex}
                            className={`border-b border-gray-100 ${
                              isTotal
                                ? "bg-primary/5 font-semibold"
                                : isSubtotal
                                ? "bg-gray-50 font-medium"
                                : ""
                            }`}
                          >
                            {row.map((cell, cellIndex) => (
                              <td
                                key={cellIndex}
                                className={`p-3 ${
                                  cellIndex === 0 ? "font-medium" : "text-right font-mono"
                                }`}
                              >
                                {cell}
                              </td>
                            ))}
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Monthly Payment Comparison */}
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium mb-2">Monthly Payment Impact</h4>
                  <p className="text-sm text-muted-foreground">
                    Monthly payment difference: <span className="font-mono font-medium">
                      {formatCurrency(monthlyPaymentDifference)}
                    </span>
                  </p>
                </div>
              </CardContent>
            </Card>
            )
          })}
        </div>

        {/* Summary */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Comparison Summary</CardTitle>
            <CardDescription>
              Analysis based on 3-year ownership costs including depreciation, taxes, and opportunity cost
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-green-600">
                  {scenarios.filter(([_, s]) => extractTotalCostDifference(s.results.cost_difference) < 0).length}
                </p>
                <p className="text-sm text-muted-foreground">Cheaper than current</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600">
                  {scenarios.filter(([_, s]) => extractTotalCostDifference(s.results.cost_difference) > 0).length}
                </p>
                <p className="text-sm text-muted-foreground">More expensive</p>
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {scenarios.length}
                </p>
                <p className="text-sm text-muted-foreground">Total scenarios</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}