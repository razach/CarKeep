"use client"

import { useEffect, useState } from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { StateSelect, StateOption } from "@/components/StateSelect"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "@/components/ui/dialog"
import { useApi } from "@/hooks/use-api"

interface StateTaxConfig {
  property_tax_rate: number
  pptra_relief: number
  relief_cap: number
  state_name: string
}

export default function StateTaxesPage() {
  const { get, post, put, delete: deleteApi } = useApi()
  const [taxConfigs, setTaxConfigs] = useState<Record<string, StateTaxConfig>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editState, setEditState] = useState<string | null>(null)
  const [form, setForm] = useState({
    state_code: "",
    state_name: "",
    property_tax_rate: "",
    pptra_relief: "",
    relief_cap: ""
  })
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
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchConfigs()
  }, [])

  async function fetchConfigs() {
    setLoading(true)
    setError(null)
    try {
      const data = await get("/state-taxes")
      setTaxConfigs(data)
    } catch (e: any) {
      setError("Failed to load state tax configs")
    } finally {
      setLoading(false)
    }
  }

  function openAddDialog() {
    setEditState(null)
    setForm({ state_code: "", state_name: "", property_tax_rate: "", pptra_relief: "", relief_cap: "" })
    setDialogOpen(true)
  }

  function openEditDialog(code: string, config: StateTaxConfig) {
    setEditState(code)
    setForm({
      state_code: code,
      state_name: config.state_name,
      property_tax_rate: (config.property_tax_rate * 100).toString(),
      pptra_relief: (config.pptra_relief * 100).toString(),
      relief_cap: config.relief_cap.toString()
    })
    setDialogOpen(true)
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload = {
        state_name: form.state_name,
        property_tax_rate: parseFloat(form.property_tax_rate),
        pptra_relief: parseFloat(form.pptra_relief),
        relief_cap: parseFloat(form.relief_cap)
      }
      if (editState) {
        await put(`/state-taxes/${form.state_code}`, payload)
      } else {
        await post("/state-taxes", { ...payload, state_code: form.state_code })
      }
      setDialogOpen(false)
      fetchConfigs()
    } catch (e: any) {
      setError("Failed to save state tax config")
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(code: string) {
    if (!window.confirm("Delete this state tax config?")) return
    setSaving(true)
    setError(null)
    try {
      await deleteApi(`/state-taxes/${code}`)
      fetchConfigs()
    } catch (e: any) {
      setError("Failed to delete state tax config")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-10">
      <div className="flex items-center gap-4 mb-8">
        <Link href="/">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">State Tax Settings</h1>
          <p className="text-muted-foreground">Manage property tax rates and relief for each state.</p>
        </div>
        <div className="flex-1 flex justify-end">
          <Button onClick={openAddDialog}>Add State</Button>
        </div>
      </div>
      <Card>
        <CardContent>
          {loading ? (
            <div>Loading...</div>
          ) : error ? (
            <div className="text-red-500">{error}</div>
          ) : (
            <div className="space-y-4">
              {Object.entries(taxConfigs).map(([code, config]) => (
                <div key={code} className="flex items-center gap-4 border-b pb-2">
                  <div className="flex-1">
                    <div className="font-semibold">{config.state_name} <span className="text-xs text-muted-foreground">({code})</span></div>
                    <div className="text-sm text-muted-foreground">
                      Property Tax Rate: {(config.property_tax_rate * 100).toFixed(2)}% | PPTRA Relief: {(config.pptra_relief * 100).toFixed(2)}% | Relief Cap: ${config.relief_cap.toLocaleString()}
                    </div>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => openEditDialog(code, config)}>Edit</Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(code)} disabled={saving || ["VA","TX","CA"].includes(code)}>Delete</Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editState ? "Edit State Tax Config" : "Add State Tax Config"}</DialogTitle>
            <DialogDescription>Enter property tax and relief details for the state.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSave} className="space-y-4">
            {!editState && (
              <div>
                <Label htmlFor="state_code">State</Label>
                <p className="text-xs text-muted-foreground mb-1">Select the U.S. state for these tax settings</p>
                <StateSelect
                  value={form.state_code}
                  onChange={code => {
                    setForm(f => ({ ...f, state_code: code, state_name: stateOptions.find(opt => opt.code === code)?.name || "" }))
                  }}
                  options={stateOptions}
                />
              </div>
            )}
            <div>
              <Label htmlFor="state_name">State Name</Label>
              <p className="text-xs text-muted-foreground mb-1">Full name of the state</p>
              <Input id="state_name" value={form.state_name} onChange={e => setForm(f => ({ ...f, state_name: e.target.value }))} required />
            </div>
            <div>
              <Label htmlFor="property_tax_rate">Property Tax Rate (%)</Label>
              <p className="text-xs text-muted-foreground mb-1">Annual vehicle property tax rate (as a percent of value)</p>
              <Input id="property_tax_rate" type="number" step="0.01" value={form.property_tax_rate} onChange={e => setForm(f => ({ ...f, property_tax_rate: e.target.value }))} required />
            </div>
            <div>
              <Label htmlFor="pptra_relief">PPTRA Relief (%)</Label>
              <p className="text-xs text-muted-foreground mb-1">Personal Property Tax Relief Act (PPTRA) percentage, if applicable</p>
              <Input id="pptra_relief" type="number" step="0.01" value={form.pptra_relief} onChange={e => setForm(f => ({ ...f, pptra_relief: e.target.value }))} required />
            </div>
            <div>
              <Label htmlFor="relief_cap">Relief Cap ($)</Label>
              <p className="text-xs text-muted-foreground mb-1">Maximum dollar amount eligible for PPTRA relief</p>
              <Input id="relief_cap" type="number" step="100" value={form.relief_cap} onChange={e => setForm(f => ({ ...f, relief_cap: e.target.value }))} required />
            </div>
            {error && <div className="text-red-500 text-sm">{error}</div>}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} disabled={saving}>Cancel</Button>
              <Button type="submit" disabled={saving}>{saving ? "Saving..." : "Save"}</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
