"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Plus, Car, DollarSign, TrendingUp, TrendingDown, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { formatCurrency } from "@/lib/formatters"
import { useApi } from "@/hooks/use-api"

interface Vehicle {
  name: string
  current_value: number
  msrp: number
  values_3yr: number[]
}

interface Financing {
  monthly_payment: number
  loan_term?: number
  lease_terms?: number
  principal_balance?: number
}

interface Scenario {
  description: string
  scenario: {
    type: "lease" | "loan"
    vehicle: Vehicle
    financing: Financing
  }
  trade_in?: {
    trade_in_value: number
    loan_balance: number
  }
}

interface BaselineData {
  description: string
  state: string
  vehicle: Vehicle
  current_loan: {
    monthly_payment: number
    principal_balance: number
  }
}

interface ScenariosData {
  baseline: BaselineData
  scenarios: Record<string, Scenario>
}

export default function ScenariosOverview() {
  const [data, setData] = useState<ScenariosData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { get } = useApi()

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        console.log("[v0] Starting to fetch scenarios...")
        const response = await get("/scenarios")
        console.log("[v0] Successfully loaded scenarios data")
        setData(response)
        setError(null)
      } catch (err) {
        console.error("[v0] Failed to load scenarios:", err)
        setError(err instanceof Error ? err.message : "Failed to load scenarios")
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchScenarios()
  }, []) // Empty dependency array - only run once on mount

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-3 text-muted-foreground">Loading scenarios...</span>
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
              <CardTitle className="text-destructive">API Connection Error</CardTitle>
            </CardHeader>
            <CardContent>
              <Alert className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-sm">{error || "Unable to connect to CarKeep API"}</AlertDescription>
              </Alert>

              <div className="space-y-4 text-sm">
                <div>
                  <p className="font-medium text-muted-foreground mb-2">Possible causes:</p>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                    <li>CarKeep API server is down or restarting</li>
                    <li>Network connectivity issues</li>
                    <li>API endpoint has changed</li>
                  </ul>
                </div>

                <div>
                  <p className="font-medium text-muted-foreground mb-2">Troubleshooting:</p>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                    <li>
                      Check if <code className="bg-muted px-1 rounded">carkeep.onrender.com</code> is accessible
                    </li>
                    <li>Verify the API server is running</li>
                    <li>Check browser console for detailed error messages</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <Button onClick={() => window.location.reload()} className="flex-1">
                  Retry Connection
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.open("https://carkeep.onrender.com", "_blank")}
                  className="flex-1"
                >
                  Test API Server
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const scenarioEntries = Object.entries(data.scenarios)
  const totalScenarios = scenarioEntries.length

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">CarKeep</h1>
              <p className="text-muted-foreground mt-1">Vehicle cost comparison and financial analysis</p>
            </div>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Add Scenario
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Scenarios</CardTitle>
              <Car className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalScenarios}</div>
              <p className="text-xs text-muted-foreground">Plus 1 baseline scenario</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Vehicle</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.baseline.vehicle.name}</div>
              <p className="text-xs text-muted-foreground">
                {formatCurrency(data.baseline.vehicle.current_value)} value
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Payment</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(data.baseline.current_loan.monthly_payment)}</div>
              <p className="text-xs text-muted-foreground">Monthly payment</p>
            </CardContent>
          </Card>
        </div>

        {/* Baseline Card */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-foreground">Current Vehicle (Baseline)</h2>
          <Card className="border-primary/20 bg-primary/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Car className="h-5 w-5" />
                    {data.baseline.vehicle.name}
                  </CardTitle>
                  <CardDescription className="mt-1">{data.baseline.description}</CardDescription>
                </div>
                <Badge variant="outline" className="bg-primary/10">
                  Baseline
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Current Value</p>
                  <p className="text-lg font-semibold">{formatCurrency(data.baseline.vehicle.current_value)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Monthly Payment</p>
                  <p className="text-lg font-semibold">{formatCurrency(data.baseline.current_loan.monthly_payment)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Loan Balance</p>
                  <p className="text-lg font-semibold">
                    {formatCurrency(data.baseline.current_loan.principal_balance)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Scenarios Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-foreground">Alternative Scenarios</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarioEntries.map(([scenarioName, scenario]) => (
              <Card key={scenarioName} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{scenario.scenario.vehicle.name}</CardTitle>
                    <Badge variant={scenario.scenario.type === "lease" ? "default" : "secondary"}>
                      {scenario.scenario.type === "lease" ? "Lease" : "Loan"}
                    </Badge>
                  </div>
                  <CardDescription className="text-balance">{scenario.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">MSRP</span>
                      <span className="font-medium">{formatCurrency(scenario.scenario.vehicle.msrp)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Monthly Payment</span>
                      <span className="font-medium">{formatCurrency(scenario.scenario.financing.monthly_payment)}</span>
                    </div>
                    {scenario.trade_in && (
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Trade-in Value</span>
                        <span className="font-medium">{formatCurrency(scenario.trade_in.trade_in_value)}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      View Details
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      Compare
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Analyze and compare your scenarios</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button variant="outline">
                <TrendingUp className="h-4 w-4 mr-2" />
                View Cost Analysis
              </Button>
              <Button variant="outline">
                <TrendingDown className="h-4 w-4 mr-2" />
                Compare All Scenarios
              </Button>
              <Button variant="outline">
                <DollarSign className="h-4 w-4 mr-2" />
                Manage State Taxes
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
