"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown } from "lucide-react"
import { formatCurrency } from "@/lib/formatters"

interface CostBreakdownTableProps {
  title: string
  data: {
    columns: string[]
    data: string[][]
  }
  highlightTotal?: boolean
}

export default function CostBreakdownTable({ title, data, highlightTotal = false }: CostBreakdownTableProps) {
  if (!data || !data.data || data.data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No data available</p>
        </CardContent>
      </Card>
    )
  }

  // Extract total difference for highlighting (if it's a cost difference table)
  const totalRow = data.data.find(row => 
    row[0]?.includes('TOTAL') || row[0]?.includes('Total')
  )
  
  let totalDifference = 0
  if (totalRow && totalRow[1]) {
    const numericValue = totalRow[1].replace(/[$,]/g, '')
    totalDifference = parseFloat(numericValue) || 0
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          {highlightTotal && totalRow && (
            <Badge 
              variant={totalDifference > 0 ? "destructive" : "secondary"}
              className="flex items-center gap-1"
            >
              {totalDifference > 0 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {totalDifference > 0 ? 'More Expensive' : 'Less Expensive'}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                {data.columns.map((column, index) => (
                  <th key={index} className="text-left py-2 px-3 font-medium">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.data.map((row, rowIndex) => {
                const isTotal = row[0]?.includes('TOTAL') || row[0]?.includes('Total')
                return (
                  <tr 
                    key={rowIndex} 
                    className={`border-b last:border-b-0 ${
                      isTotal ? 'bg-muted/50 font-semibold' : ''
                    }`}
                  >
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex} className="py-2 px-3">
                        {cell}
                      </td>
                    ))}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}