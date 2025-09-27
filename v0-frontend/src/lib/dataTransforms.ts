// Data transformation utilities for converting API responses to component-friendly formats

export interface APIScenarioResponse {
  description: string
  scenario: {
    vehicle: {
      name: string
      msrp: number
      current_value?: number
      values_3yr?: number[]
    }
    financing: {
      monthly_payment: number
      loan_term?: number
      principal_balance?: number
      down_payment?: number
    }
    type: 'loan' | 'lease'
  }
  trade_in?: {
    trade_in_value?: number
  }
  cost_overrides?: {
    incentives?: number
  }
  state?: string
  results?: {
    cost_difference?: {
      columns: string[]
      data: string[][]
    }
    monthly_payment?: {
      columns: string[]
      data: string[][]
    }
    summary?: {
      columns: string[]
      data: string[][]
    }
  }
}

export interface FlatScenarioData {
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
  results?: {
    cost_difference?: {
      columns: string[]
      data: string[][]
    }
    monthly_payment?: {
      columns: string[]
      data: string[][]
    }
    summary?: {
      columns: string[]
      data: string[][]
    }
  }
}

/**
 * Transform API scenario response to flat structure expected by components
 */
export function transformScenarioData(apiData: APIScenarioResponse): FlatScenarioData {
  return {
    description: apiData.description,
    vehicle_name: apiData.scenario.vehicle.name,
    msrp: apiData.scenario.vehicle.msrp,
    financing_type: apiData.scenario.type,
    monthly_payment: apiData.scenario.financing.monthly_payment,
    trade_in_value: apiData.trade_in?.trade_in_value,
    loan_term: apiData.scenario.financing.loan_term,
    principal_balance: apiData.scenario.financing.principal_balance,
    down_payment: apiData.scenario.financing.down_payment,
    incentives: apiData.cost_overrides?.incentives,
    state: apiData.state,
    results: apiData.results
  }
}

/**
 * Transform API baseline response to expected format
 */
export interface APIBaselineResponse {
  baseline: {
    vehicle: {
      name: string
      current_value: number
      impairment: number
    }
    current_loan: {
      monthly_payment: number
      principal_balance: number
      interest_rate: number
    }
    state: string
  }
}

export interface FlatBaselineData {
  vehicle_name: string
  current_value: number
  monthly_payment: number
  loan_balance: number
  interest_rate: number
  impairment_cost: number
  state: string
}

export function transformBaselineData(apiData: APIBaselineResponse): FlatBaselineData {
  return {
    vehicle_name: apiData.baseline.vehicle.name,
    current_value: apiData.baseline.vehicle.current_value,
    monthly_payment: apiData.baseline.current_loan.monthly_payment,
    loan_balance: apiData.baseline.current_loan.principal_balance,
    interest_rate: apiData.baseline.current_loan.interest_rate,
    impairment_cost: apiData.baseline.vehicle.impairment,
    state: apiData.baseline.state
  }
}