"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Edit, Trash2, BarChart3, GitCompare, TrendingUp, TrendingDown } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useApi } from "@/hooks/use-api"
import { formatCurrency } from "@/lib/formatters"
import ScenarioDetails from "@/components/ScenarioDetails"
import CostBreakdownTable from "@/components/CostBreakdownTable"
import { 
  transformScenarioData, 
  type APIScenarioResponse, 
  type FlatScenarioData 
} from "@/lib/dataTransforms"

interface ScenarioData extends FlatScenarioData {}

export default function ScenarioDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { get, delete: deleteScenario } = useApi()
  const [scenario, setScenario] = useState<ScenarioData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  const scenarioName = params.scenarioName as string

  useEffect(() => {
    if (scenarioName) {
      loadScenario()
    }
  }, [scenarioName])

  const loadScenario = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load both scenario config and results
      const [scenariosResponse, resultsResponse] = await Promise.all([
        get('/scenarios'),
        get(`/scenario/${scenarioName}`)
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
      
      const transformedData = transformScenarioData(combinedData)
      setScenario(transformedData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${scenario?.vehicle_name}"? This action cannot be undone.`)) {
      return
    }

    try {
      setDeleting(true)
      await deleteScenario(`/scenarios/${scenarioName}`)
      router.push('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scenario')
    } finally {
      setDeleting(false)
    }
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
          <div className="h-64 bg-muted animate-pulse rounded-lg" />
        </div>
      </div>
    )
  }

  if (error || !scenario) {
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
          <AlertDescription>
            {error || 'Scenario not found'}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{scenario.vehicle_name}</h1>
            <p className="text-muted-foreground">{scenario.description}</p>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Link href={`/compare/${scenarioName}`}>
            <Button variant="default" size="sm">
              <GitCompare className="h-4 w-4 mr-2" />
              Compare vs Baseline
            </Button>
          </Link>
          <Button variant="outline" size="sm" disabled>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button 
            variant="destructive" 
            size="sm" 
            onClick={handleDelete}
            disabled={deleting}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>

      {/* Scenario Details */}
      <div className="space-y-6">
        <ScenarioDetails scenario={scenario} showTitle={false} />

        {/* Quick Summary Card */}
        {scenario.results?.cost_difference && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                <CardTitle>Quick Analysis Summary</CardTitle>
              </div>
              <CardDescription>
                Key metrics compared to keeping your current vehicle
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {(() => {
                  // Extract total cost difference
                  const totalRow = scenario.results.cost_difference.data.find(row => row[0] === "TOTAL COST DIFFERENCE")
                  const totalCost = totalRow ? parseFloat(totalRow[1].replace(/[$,]/g, '')) : 0
                  
                  // Extract monthly payment difference
                  const monthlyRow = scenario.results.monthly_payment?.data.find(row => row[0] === "TOTAL MONTHLY")
                  let monthlyDiff = 0
                  if (monthlyRow && monthlyRow[1] && monthlyRow[2]) {
                    const newPayment = parseFloat(monthlyRow[1].replace(/[$,]/g, ''))
                    const currentPayment = parseFloat(monthlyRow[2].replace(/[$,]/g, ''))
                    monthlyDiff = newPayment - currentPayment
                  }

                  return (
                    <>
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-muted-foreground">Total Cost Impact (3 years)</p>
                        <div className="flex items-center gap-2">
                          <p className={`text-2xl font-bold ${totalCost > 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {totalCost > 0 ? '+' : ''}{formatCurrency(Math.abs(totalCost))}
                          </p>
                          <Badge variant={totalCost > 0 ? "destructive" : "secondary"} className="flex items-center gap-1">
                            {totalCost > 0 ? (
                              <TrendingUp className="h-3 w-3" />
                            ) : (
                              <TrendingDown className="h-3 w-3" />
                            )}
                            {totalCost > 0 ? 'More Expensive' : 'Less Expensive'}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-muted-foreground">Monthly Payment Impact</p>
                        <div className="flex items-center gap-2">
                          <p className={`text-2xl font-bold ${monthlyDiff > 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {monthlyDiff > 0 ? '+' : ''}{formatCurrency(Math.abs(monthlyDiff))}
                          </p>
                          <Badge variant={monthlyDiff > 0 ? "destructive" : "secondary"}>
                            {monthlyDiff > 0 ? 'Higher' : 'Lower'}
                          </Badge>
                        </div>
                      </div>
                    </>
                  )
                })()}
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-3">
                  Want to see the detailed breakdown?
                </p>
                <Link href={`/compare/${scenarioName}`}>
                  <Button className="w-full">
                    <GitCompare className="h-4 w-4 mr-2" />
                    View Detailed Cost Analysis
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}

        {!scenario.results && (
          <Card>
            <CardContent className="py-8">
              <div className="text-center text-muted-foreground">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Cost analysis not available for this scenario.</p>
                <div className="mt-4">
                  <Link href={`/compare/${scenarioName}`}>
                    <Button variant="outline">
                      <GitCompare className="h-4 w-4 mr-2" />
                      Try Detailed Comparison
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}