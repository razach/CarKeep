"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, TrendingUp, TrendingDown, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useApi } from "@/hooks/use-api"
import { formatCurrency } from "@/lib/formatters"
import ScenarioDetails from "@/components/ScenarioDetails"
import CostBreakdownTable from "@/components/CostBreakdownTable"
import {
  transformScenarioData,
  transformBaselineData,
  type APIScenarioResponse,
  type APIBaselineResponse,
  type FlatScenarioData,
  type FlatBaselineData
} from "@/lib/dataTransforms"

interface ScenarioData extends FlatScenarioData {}

interface BaselineData extends FlatBaselineData {}

export default function SingleScenarioComparePage() {
  const params = useParams()
  const { get } = useApi()
  const [scenario, setScenario] = useState<ScenarioData | null>(null)
  const [baseline, setBaseline] = useState<BaselineData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const scenarioName = params.scenarioName as string

  useEffect(() => {
    if (scenarioName) {
      loadData()
    }
  }, [scenarioName])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load scenario config, results, and baseline data
      const [scenariosResponse, resultsResponse, apiBaselineData] = await Promise.all([
        get('/scenarios'),
        get(`/scenario/${scenarioName}`),
        get('/baseline') as Promise<APIBaselineResponse>
      ])
      
      const scenarioConfig = scenariosResponse?.scenarios?.[scenarioName]
      if (!scenarioConfig) {
        throw new Error('Scenario not found')
      }
      
      // Combine config with results
      const combinedData: APIScenarioResponse = {
        description: scenarioConfig.description || resultsResponse.description,
        scenario: scenarioConfig.scenario,
        trade_in: scenarioConfig.trade_in,
        cost_overrides: scenarioConfig.cost_overrides,
        state: scenarioConfig.state,
        results: resultsResponse.results
      }
      
      const transformedScenario = transformScenarioData(combinedData)
      const transformedBaseline = transformBaselineData(apiBaselineData)
      
      setScenario(transformedScenario)
      setBaseline(transformedBaseline)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load comparison data')
    } finally {
      setLoading(false)
    }
  }

  // Helper function to extract total cost difference
  const extractTotalCostDifference = (costDifferenceData?: { data: string[][] }): number => {
    if (!costDifferenceData) return 0
    const totalRow = costDifferenceData.data.find(row => row[0] === "TOTAL COST DIFFERENCE")
    if (totalRow && totalRow[1]) {
      const numericValue = totalRow[1].replace(/[$,]/g, '')
      return parseFloat(numericValue) || 0
    }
    return 0
  }

  // Helper function to extract monthly payment difference
  const extractMonthlyPaymentDifference = (monthlyPaymentData?: { data: string[][] }): number => {
    if (!monthlyPaymentData) return 0
    const totalRow = monthlyPaymentData.data.find(row => row[0] === "TOTAL MONTHLY")
    if (totalRow && totalRow[1] && totalRow[2]) {
      const newVehiclePayment = parseFloat(totalRow[1].replace(/[$,]/g, '')) || 0
      const currentVehiclePayment = parseFloat(totalRow[2].replace(/[$,]/g, '')) || 0
      return newVehiclePayment - currentVehiclePayment
    }
    return 0
  }

  if (loading) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center gap-4 mb-6">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
        </div>
        <div className="space-y-4">
          <div className="h-32 bg-muted animate-pulse rounded-lg" />
          <div className="grid md:grid-cols-2 gap-6">
            <div className="h-64 bg-muted animate-pulse rounded-lg" />
            <div className="h-64 bg-muted animate-pulse rounded-lg" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !scenario || !baseline) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center gap-4 mb-6">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || 'Failed to load comparison data'}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  const totalCostDifference = extractTotalCostDifference(scenario.results?.cost_difference)
  const monthlyPaymentDifference = extractMonthlyPaymentDifference(scenario.results?.monthly_payment)

  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Scenario Comparison</h1>
            <p className="text-muted-foreground">
              {scenario.vehicle_name} vs {baseline.vehicle_name}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <Link href="/compare">
            <Button variant="default" size="sm">
              Compare All Scenarios
            </Button>
          </Link>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Total Cost Difference</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${totalCostDifference > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {totalCostDifference > 0 ? '+' : ''}{formatCurrency(Math.abs(totalCostDifference))}
              </span>
              {totalCostDifference !== 0 && (
                <Badge variant={totalCostDifference > 0 ? "destructive" : "secondary"} className="flex items-center gap-1">
                  {totalCostDifference > 0 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {totalCostDifference > 0 ? 'More' : 'Less'}
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Monthly Payment Difference</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${monthlyPaymentDifference > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {monthlyPaymentDifference > 0 ? '+' : ''}{formatCurrency(Math.abs(monthlyPaymentDifference))}
              </span>
              {monthlyPaymentDifference !== 0 && (
                <Badge variant={monthlyPaymentDifference > 0 ? "destructive" : "secondary"}>
                  {monthlyPaymentDifference > 0 ? 'Higher' : 'Lower'}
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Financing Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge variant={scenario.financing_type === 'lease' ? 'secondary' : 'default'} className="text-base">
                {scenario.financing_type === 'lease' ? 'Lease' : 'Loan'}
              </Badge>
              <span className="text-sm text-muted-foreground">
                vs Baseline Loan
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Vehicle Comparison */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            New Vehicle
            <Badge variant="outline">{scenario.financing_type}</Badge>
          </h2>
          <ScenarioDetails scenario={scenario} showTitle={false} />
        </div>

        <div>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            Current Vehicle (Baseline)
            <Badge variant="outline">Loan</Badge>
          </h2>
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Current Value</p>
                  <p className="text-2xl font-bold">{formatCurrency(baseline.current_value)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Monthly Payment</p>
                  <p className="text-2xl font-bold">{formatCurrency(baseline.monthly_payment)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Loan Balance</p>
                  <p className="text-lg font-semibold">{formatCurrency(baseline.loan_balance)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Interest Rate</p>
                  <p className="text-lg font-semibold">{baseline.interest_rate}%</p>
                </div>
                {baseline.impairment_cost > 0 && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Impairment Cost</p>
                    <p className="text-lg font-semibold text-red-600">{formatCurrency(baseline.impairment_cost)}</p>
                  </div>
                )}
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">State Tax Scenario</p>
                  <p className="text-lg font-semibold">{baseline.state}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Detailed Analysis Tables */}
      {scenario.results && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Detailed Cost Analysis</h2>

          {scenario.results.summary && (
            <CostBreakdownTable 
              title="Summary" 
              data={scenario.results.summary} 
            />
          )}

          {scenario.results.cost_difference && (
            <CostBreakdownTable 
              title="Cost Difference Breakdown" 
              data={scenario.results.cost_difference} 
              highlightTotal={true}
            />
          )}

          {scenario.results.monthly_payment && (
            <CostBreakdownTable 
              title="Monthly Payment Comparison" 
              data={scenario.results.monthly_payment} 
            />
          )}
        </div>
      )}

      {!scenario.results && (
        <Card>
          <CardContent className="py-8">
            <div className="text-center text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">Analysis data not available</p>
              <p className="text-sm mt-2">Cost comparison analysis could not be generated for this scenario.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}