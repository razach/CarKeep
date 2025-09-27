"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Car, DollarSign, TrendingUp, TrendingDown, AlertCircle, Edit3, Pencil } from "lucide-react"
import { StateSelect, StateOption } from "@/components/StateSelect"
const stateOptions: StateOption[] = [
  { code: "AL", name: "Alabama" }, { code: "AK", name: "Alaska" }, { code: "AZ", name: "Arizona" },
  { code: "AR", name: "Arkansas" }, { code: "CA", name: "California" }, { code: "CO", name: "Colorado" },
  { code: "CT", name: "Connecticut" }, { code: "DE", name: "Delaware" }, { code: "FL", name: "Florida" },
  { code: "GA", name: "Georgia" }, { code: "HI", name: "Hawaii" }, { code: "ID", name: "Idaho" },
  { code: "IL", name: "Illinois" }, { code: "IN", name: "Indiana" }, { code: "IA", name: "Iowa" },
  { code: "KS", name: "Kansas" }, { code: "KY", name: "Kentucky" }, { code: "LA", name: "Louisiana" },
  { code: "ME", name: "Maine" }, { code: "MD", name: "Maryland" }, { code: "MA", name: "Massachusetts" },
  { code: "MI", name: "Michigan" }, { code: "MN", name: "Minnesota" }, { code: "MS", name: "Mississippi" },
  { code: "MO", name: "Missouri" }, { code: "MT", name: "Montana" }, { code: "NE", name: "Nebraska" },
  { code: "NV", name: "Nevada" }, { code: "NH", name: "New Hampshire" }, { code: "NJ", name: "New Jersey" },
  { code: "NM", name: "New Mexico" }, { code: "NY", name: "New York" }, { code: "NC", name: "North Carolina" },
  { code: "ND", name: "North Dakota" }, { code: "OH", name: "Ohio" }, { code: "OK", name: "Oklahoma" },
  { code: "OR", name: "Oregon" }, { code: "PA", name: "Pennsylvania" }, { code: "RI", name: "Rhode Island" },
  { code: "SC", name: "South Carolina" }, { code: "SD", name: "South Dakota" }, { code: "TN", name: "Tennessee" },
  { code: "TX", name: "Texas" }, { code: "UT", name: "Utah" }, { code: "VT", name: "Vermont" },
  { code: "VA", name: "Virginia" }, { code: "WA", name: "Washington" }, { code: "WV", name: "West Virginia" },
  { code: "WI", name: "Wisconsin" }, { code: "WY", name: "Wyoming" }
]
import { Alert, AlertDescription } from "@/components/ui/alert"
import { formatCurrency } from "@/lib/formatters"
import { useApi } from "@/hooks/use-api"

interface Vehicle {
  name: string
  current_value: number
  msrp: number
  values_3yr: number[]
  impairment?: number
  impairment_affects_taxes?: boolean
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
    incentives?: number
  }
}

interface BaselineData {
  description: string
  state: string
  vehicle: Vehicle
  current_loan: {
    monthly_payment: number
    principal_balance: number
    interest_rate?: number
    extra_payment?: number
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
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editLoading, setEditLoading] = useState(false)
  const [editScenarioDialogOpen, setEditScenarioDialogOpen] = useState(false)
  const [editingScenario, setEditingScenario] = useState<string | null>(null)
  const { get, put } = useApi()
  // Dynamically loaded state tax scenarios (from /state-taxes)
  const [stateTaxOptions, setStateTaxOptions] = useState<StateOption[]>([])

  // Form state for editing baseline
  const [baselineForm, setBaselineForm] = useState({
    vehicle_name: "",
    current_value: "",
    monthly_payment: "",
    principal_balance: "",
    impairment: "",
    interest_rate: "",
    state: ""
  })

  // Initialize form with current baseline data
  useEffect(() => {
    if (data?.baseline) {
      setBaselineForm({
        vehicle_name: data.baseline.vehicle.name || '',
        current_value: data.baseline.vehicle.current_value?.toString() || '',
        monthly_payment: data.baseline.current_loan.monthly_payment?.toString() || '',
        principal_balance: data.baseline.current_loan.principal_balance?.toString() || '',
        impairment: data.baseline.vehicle.impairment?.toString() || '0',
        interest_rate: ((data.baseline.current_loan.interest_rate || 0) * 100)?.toString() || '',
        state: data.baseline.state || ''
      })
    }
  }, [data])

  // Form state for editing scenarios
  const [scenarioForm, setScenarioForm] = useState({
    description: "",
    vehicle_name: "",
    msrp: "",
    financing_type: "loan" as "lease" | "loan",
    monthly_payment: "",
    loan_term: "",
    lease_terms: "",
    principal_balance: "",
    trade_in_value: "",
    loan_balance: "",
    incentives: "",
    state: ""
  })

  // Initialize scenario form when editing
  const initializeScenarioForm = (scenarioKey: string, scenario: Scenario) => {
    setScenarioForm({
      description: scenario.description,
      vehicle_name: scenario.scenario.vehicle.name,
      msrp: scenario.scenario.vehicle.msrp?.toString() || '',
      financing_type: scenario.scenario.type,
      monthly_payment: scenario.scenario.financing.monthly_payment?.toString() || '',
      loan_term: scenario.scenario.financing.loan_term?.toString() || '',
      lease_terms: scenario.scenario.financing.lease_terms?.toString() || '',
      principal_balance: scenario.scenario.financing.principal_balance?.toString() || '',
      trade_in_value: scenario.trade_in?.trade_in_value?.toString() || '',
      loan_balance: scenario.trade_in?.loan_balance?.toString() || '',
      incentives: scenario.trade_in?.incentives?.toString() || '0',
      state: (scenario as any).state || ''
    })
    setEditingScenario(scenarioKey)
    setEditScenarioDialogOpen(true)
  }

  const handleScenarioSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingScenario) return
    
    setEditLoading(true)

    try {
      const updatedScenario = {
        description: scenarioForm.description,
        vehicle_name: scenarioForm.vehicle_name,
        msrp: parseFloat(scenarioForm.msrp),
        financing_type: scenarioForm.financing_type,
        state: scenarioForm.state || undefined,
        monthly_payment: parseFloat(scenarioForm.monthly_payment),
        loan_term: scenarioForm.loan_term ? parseInt(scenarioForm.loan_term) : undefined,
        lease_terms: scenarioForm.lease_terms ? parseInt(scenarioForm.lease_terms) : undefined,
        principal_balance: scenarioForm.principal_balance ? parseFloat(scenarioForm.principal_balance) : undefined,
        trade_in_value: scenarioForm.trade_in_value ? parseFloat(scenarioForm.trade_in_value) : undefined,
        loan_balance: scenarioForm.loan_balance ? parseFloat(scenarioForm.loan_balance) : undefined,
        incentives: scenarioForm.incentives ? parseFloat(scenarioForm.incentives) : 0
      }

      await put(`/scenario/${editingScenario}`, updatedScenario)
      
      // Refresh the data
      const response = await get("/scenarios")
      setData(response)
      setEditScenarioDialogOpen(false)
      setEditingScenario(null)
    } catch (err) {
      console.error("Failed to update scenario:", err)
    } finally {
      setEditLoading(false)
    }
  }

  const handleBaselineSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setEditLoading(true)

    try {
      const updatedBaseline = {
        // Required fields per API validation
        vehicle_name: baselineForm.vehicle_name,
        current_value: parseFloat(baselineForm.current_value),
        description: `${baselineForm.vehicle_name} - Keep current car (baseline)`,
  state: baselineForm.state || data?.baseline.state || 'VA',
        
        // Optional fields
        monthly_payment: parseFloat(baselineForm.monthly_payment),
        principal_balance: parseFloat(baselineForm.principal_balance),
        impairment: parseFloat(baselineForm.impairment) || 0,
        interest_rate: parseFloat(baselineForm.interest_rate) || 0,
        extra_payment: data?.baseline.current_loan.extra_payment || 0,
        msrp: data?.baseline.vehicle.msrp || 0,
        impairment_affects_taxes: false
      }

      await put('/baseline', updatedBaseline)
      
      // Refresh the data
      const response = await get("/scenarios")
      setData(response)
      setEditDialogOpen(false)
    } catch (err) {
      console.error("Failed to update baseline:", err)
      // Handle error - maybe show a toast or alert
    } finally {
      setEditLoading(false)
    }
  }

  const handleEditScenario = (scenarioName: string, scenario: any) => {
    console.log("[v0] Editing scenario:", scenarioName)
    initializeScenarioForm(scenarioName, scenario)
    setEditingScenario(scenarioName)
    setEditScenarioDialogOpen(true)
  }

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        console.log("[v0] Starting to fetch scenarios...")
        const [scenariosRes, stateTaxes] = await Promise.all([
          get("/scenarios"),
          // Load configured state tax scenarios; if it fails we'll fall back to the static 50-state list
          get("/state-taxes").catch(() => ({} as Record<string, any>))
        ])
        console.log("[v0] Successfully loaded scenarios data")
        setData(scenariosRes)
        // Map state tax configs into options: [{ code, name }]
        if (stateTaxes && typeof stateTaxes === 'object') {
          const options: StateOption[] = Object.entries(stateTaxes).map(([code, cfg]: any) => ({
            code,
            name: cfg?.state_name || code
          }))
          // Only set if we have at least one configured state
          if (options.length) setStateTaxOptions(options)
        }
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
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="bg-primary/10">
                    Baseline
                  </Badge>
                  <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Edit3 className="h-4 w-4" />
                        Edit
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Edit Baseline Vehicle</DialogTitle>
                        <DialogDescription>
                          Update your current vehicle information and loan details.
                        </DialogDescription>
                      </DialogHeader>
                      <form onSubmit={handleBaselineSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="vehicle_name">Vehicle Name</Label>
                            <p className="text-xs text-muted-foreground mb-1">e.g., Acura RDX, Tesla Model Y</p>
                            <Input
                              id="vehicle_name"
                              value={baselineForm.vehicle_name}
                              onChange={(e) => setBaselineForm(prev => ({ ...prev, vehicle_name: e.target.value }))}
                              placeholder="e.g., Acura RDX"
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="state">State Tax Scenario</Label>
                            <div className="text-xs text-muted-foreground mb-1 space-y-1">
                              <p>Select the state scenario to use for this vehicle.</p>
                              <p>This determines which tax rates and relief rules apply.</p>
                              <p><Link href="/state-taxes" className="text-primary hover:underline" onClick={(e) => { e.preventDefault(); if (confirm('You have unsaved changes. Navigating away will discard them. Continue to State Tax Settings?')) { window.location.href = '/state-taxes'; } }}>Configured in State Tax Settings</Link></p>
                            </div>
                            <StateSelect
                              value={baselineForm.state}
                              onChange={code => setBaselineForm(prev => ({ ...prev, state: code }))}
                              options={stateTaxOptions.length ? stateTaxOptions : stateOptions}
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="monthly_payment">Monthly Payment ($)</Label>
                            <p className="text-xs text-muted-foreground mb-1">Your current monthly loan or lease payment</p>
                            <Input
                              id="monthly_payment"
                              type="number"
                              step="0.01"
                              value={baselineForm.monthly_payment}
                              onChange={(e) => setBaselineForm(prev => ({ ...prev, monthly_payment: e.target.value }))}
                              placeholder="564.10"
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="principal_balance">Loan Balance ($)</Label>
                            <p className="text-xs text-muted-foreground mb-1">Remaining principal on your current auto loan</p>
                            <Input
                              id="principal_balance"
                              type="number"
                              step="0.01"
                              value={baselineForm.principal_balance}
                              onChange={(e) => setBaselineForm(prev => ({ ...prev, principal_balance: e.target.value }))}
                              placeholder="9909.95"
                              required
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="interest_rate">Interest Rate (%)</Label>
                            <p className="text-xs text-muted-foreground mb-1">Annual interest rate (APR) for your loan</p>
                            <Input
                              id="interest_rate"
                              type="number"
                              step="0.01"
                              value={baselineForm.interest_rate}
                              onChange={(e) => setBaselineForm(prev => ({ ...prev, interest_rate: e.target.value }))}
                              placeholder="5.50"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="impairment">Impairment/Damage ($)</Label>
                            <p className="text-xs text-muted-foreground mb-1">Estimated cost of any major damage or impairment</p>
                            <Input
                              id="impairment"
                              type="number"
                              step="100"
                              value={baselineForm.impairment}
                              onChange={(e) => setBaselineForm(prev => ({ ...prev, impairment: e.target.value }))}
                              placeholder="3000"
                            />
                          </div>
                        </div>
                        <div className="flex justify-end gap-2 pt-4">
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => setEditDialogOpen(false)}
                            disabled={editLoading}
                          >
                            Cancel
                          </Button>
                          <Button type="submit" disabled={editLoading}>
                            {editLoading ? 'Saving...' : 'Save Changes'}
                          </Button>
                        </div>
                      </form>
                    </DialogContent>
                  </Dialog>

                  {/* Scenario Edit Dialog */}
                  <Dialog open={editScenarioDialogOpen} onOpenChange={setEditScenarioDialogOpen}>
                    <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Edit Scenario</DialogTitle>
                        <DialogDescription>
                          Modify the details of this vehicle scenario
                        </DialogDescription>
                      </DialogHeader>
                      <form onSubmit={handleScenarioSubmit}>
                        <div className="grid gap-4 py-4">
                          <div className="space-y-2">
                            <Label htmlFor="scenario_description">Description</Label>
                            <Input
                              id="scenario_description"
                              value={scenarioForm.description}
                              onChange={(e) => setScenarioForm(prev => ({ ...prev, description: e.target.value }))}
                              placeholder="Enter scenario description"
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="vehicle_name">Vehicle Name</Label>
                              <Input
                                id="vehicle_name"
                                value={scenarioForm.vehicle_name}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, vehicle_name: e.target.value }))}
                                placeholder="2024 Honda Accord"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="state">State Tax Scenario</Label>
                              <div className="text-xs text-muted-foreground mb-1 space-y-1">
                                <p>Select the state scenario to use for this vehicle.</p>
                                <p>This determines which tax rates and relief rules apply.</p>
                                <p><Link href="/state-taxes" className="text-primary hover:underline" onClick={(e) => { e.preventDefault(); if (confirm('You have unsaved changes. Navigating away will discard them. Continue to State Tax Settings?')) { window.location.href = '/state-taxes'; } }}>Configured in State Tax Settings</Link></p>
                              </div>
                              <StateSelect
                                value={scenarioForm.state}
                                onChange={code => setScenarioForm(prev => ({ ...prev, state: code }))}
                                options={stateTaxOptions.length ? stateTaxOptions : stateOptions}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="msrp">MSRP ($)</Label>
            <p className="text-xs text-muted-foreground mb-1">Manufacturer's Suggested Retail Price</p>
                              <Input
                                id="msrp"
                                type="number"
                                step="100"
                                value={scenarioForm.msrp}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, msrp: e.target.value }))}
                                placeholder="35000"
                              />
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="financing_type">Financing Type</Label>
            <p className="text-xs text-muted-foreground mb-1">Choose 'Lease' or 'Loan' for this scenario</p>
            <p className="text-xs text-muted-foreground mb-1">Expected monthly payment for this vehicle</p>
                              <Select 
                                value={scenarioForm.financing_type} 
                                onValueChange={(value) => setScenarioForm(prev => ({ ...prev, financing_type: value as "lease" | "loan" }))}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select financing type" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="lease">Lease</SelectItem>
                                  <SelectItem value="loan">Loan</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="monthly_payment">Monthly Payment ($)</Label>
                              <Input
                                id="monthly_payment"
                                type="number"
                                step="10"
                                value={scenarioForm.monthly_payment}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, monthly_payment: e.target.value }))}
                                placeholder="450"
                              />
                            </div>
                          </div>
                          {scenarioForm.financing_type === 'loan' && (
                            <div className="space-y-2">
                              <Label htmlFor="loan_term">Loan Term (months)</Label>
            <p className="text-xs text-muted-foreground mb-1">Total number of months for the loan</p>
                              <Input
                                id="loan_term"
                                type="number"
                                value={scenarioForm.loan_term}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, loan_term: e.target.value }))}
                                placeholder="60"
                              />
                            </div>
                          )}
                          {scenarioForm.financing_type === 'lease' && (
                            <div className="space-y-2">
                              <Label htmlFor="lease_terms">Lease Terms (months)</Label>
            <p className="text-xs text-muted-foreground mb-1">Total number of months for the lease</p>
            <p className="text-xs text-muted-foreground mb-1">Remaining principal if trading in a financed vehicle</p>
                              <Input
                                id="lease_terms"
                                type="number"
                                value={scenarioForm.lease_terms}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, lease_terms: e.target.value }))}
                                placeholder="36"
                              />
                            </div>
                          )}
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="trade_in_value">Trade-in Value ($)</Label>
            <p className="text-xs text-muted-foreground mb-1">Estimated value of your trade-in vehicle</p>
                              <Input
                                id="trade_in_value"
                                type="number"
                                step="100"
                                value={scenarioForm.trade_in_value}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, trade_in_value: e.target.value }))}
                                placeholder="18000"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="loan_balance">Current Loan Balance ($)</Label>
            <p className="text-xs text-muted-foreground mb-1">Outstanding loan balance on trade-in</p>
                              <Input
                                id="loan_balance"
                                type="number"
                                step="100"
                                value={scenarioForm.loan_balance}
                                onChange={(e) => setScenarioForm(prev => ({ ...prev, loan_balance: e.target.value }))}
                                placeholder="15000"
                              />
                            </div>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="incentives">Incentives/Rebates ($)</Label>
            <p className="text-xs text-muted-foreground mb-1">Any cash incentives, rebates, or discounts</p>
                            <Input
                              id="incentives"
                              type="number"
                              step="100"
                              value={scenarioForm.incentives}
                              onChange={(e) => setScenarioForm(prev => ({ ...prev, incentives: e.target.value }))}
                              placeholder="2000"
                            />
                          </div>
                        </div>
                        <div className="flex justify-end gap-2 pt-4">
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => setEditScenarioDialogOpen(false)}
                            disabled={editLoading}
                          >
                            Cancel
                          </Button>
                          <Button type="submit" disabled={editLoading}>
                            {editLoading ? 'Saving...' : 'Save Changes'}
                          </Button>
                        </div>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
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
            <Button className="flex items-center gap-2" onClick={() => {
              setScenarioForm({
                description: "",
                vehicle_name: "",
                msrp: "",
                financing_type: "loan",
                monthly_payment: "",
                loan_term: "",
                lease_terms: "",
                principal_balance: "",
                trade_in_value: "",
                loan_balance: "",
                incentives: "",
                state: ""
              });
              setEditingScenario(null);
              setEditScenarioDialogOpen(true);
            }}>
              <Plus className="h-4 w-4" />
              Add Scenario
            </Button>
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
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleEditScenario(scenarioName, scenario)}
                      className="bg-transparent"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Link href={`/scenario/${scenarioName}`}>
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        View Details
                      </Button>
                    </Link>
                    <Link href={`/compare/${scenarioName}`}>
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        Compare
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
