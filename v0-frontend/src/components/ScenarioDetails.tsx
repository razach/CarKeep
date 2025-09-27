"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatCurrency } from "@/lib/formatters"

interface ScenarioDetailsProps {
  scenario: {
    description: string
    vehicle_name: string
    msrp: number
    financing_type: 'loan' | 'lease'
    monthly_payment: number
    trade_in_value?: number
    loan_term?: number
    principal_balance?: number
    down_payment?: number
    incentives?: number
    state?: string
  }
  showTitle?: boolean
}

export default function ScenarioDetails({ scenario, showTitle = true }: ScenarioDetailsProps) {
  return (
    <Card>
      {showTitle && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{scenario.vehicle_name}</CardTitle>
            <Badge variant={scenario.financing_type === 'lease' ? 'secondary' : 'default'}>
              {scenario.financing_type === 'lease' ? 'Lease' : 'Loan'}
            </Badge>
          </div>
          <CardDescription>{scenario.description}</CardDescription>
        </CardHeader>
      )}
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">MSRP</p>
            <p className="text-2xl font-bold">{formatCurrency(scenario.msrp)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">Monthly Payment</p>
            <p className="text-2xl font-bold">{formatCurrency(scenario.monthly_payment)}</p>
          </div>
          {scenario.trade_in_value && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Trade-in Value</p>
              <p className="text-2xl font-bold">{formatCurrency(scenario.trade_in_value)}</p>
            </div>
          )}
          {scenario.down_payment && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Down Payment</p>
              <p className="text-lg font-semibold">{formatCurrency(scenario.down_payment)}</p>
            </div>
          )}
          {scenario.principal_balance && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Principal Balance</p>
              <p className="text-lg font-semibold">{formatCurrency(scenario.principal_balance)}</p>
            </div>
          )}
          {scenario.loan_term && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Loan Term</p>
              <p className="text-lg font-semibold">{scenario.loan_term} months</p>
            </div>
          )}
          {scenario.incentives && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Incentives</p>
              <p className="text-lg font-semibold text-green-600">{formatCurrency(scenario.incentives)}</p>
            </div>
          )}
          {scenario.state && (
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">State Tax Scenario</p>
              <p className="text-lg font-semibold">{scenario.state}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}