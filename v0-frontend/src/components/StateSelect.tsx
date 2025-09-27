import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export interface StateOption {
  code: string
  name: string
}

export function StateSelect({ value, onChange, options, disabled }: {
  value: string
  onChange: (value: string) => void
  options: StateOption[]
  disabled?: boolean
}) {
  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger>
        <SelectValue placeholder="Select scenario" />
      </SelectTrigger>
      <SelectContent>
        {options.map(opt => (
          <SelectItem key={opt.code} value={opt.code}>
            {opt.name} ({opt.code})
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
