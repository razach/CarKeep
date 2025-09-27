"use client"

import { useState } from "react"

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "https://carkeep.onrender.com") + "/api"

interface ApiError extends Error {
  status?: number
}

export const useApi = () => {
  const [loading, setLoading] = useState(false)

  const request = async (endpoint: string, options: RequestInit = {}) => {
    setLoading(true)
    try {
      const fullUrl = `${API_BASE_URL}${endpoint}`
      console.log("[v0] Making API request to:", fullUrl)

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout

      const response = await fetch(fullUrl, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      })

      clearTimeout(timeoutId)

      console.log("[v0] API response status:", response.status)
      console.log("[v0] API response ok:", response.ok)
      console.log("[v0] API response headers:", Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        let errorText = "Unknown error"
        try {
          errorText = await response.text()
        } catch (e) {
          console.log("[v0] Could not read error response text")
        }
        console.log("[v0] API error response:", errorText)
        const error: ApiError = new Error(`API Error (${response.status}): ${response.statusText}`)
        error.status = response.status
        throw error
      }

      const data = await response.json()
      console.log("[v0] API response data keys:", Object.keys(data))
      return data
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === "AbortError") {
          console.error("[v0] API request timed out after 10 seconds")
          throw new Error("Request timed out - the API server may be down or slow to respond")
        } else if (error.message.includes("Failed to fetch") || error.message.includes("Load failed")) {
          console.error("[v0] Network error - likely CORS, DNS, or server unavailable")
          throw new Error("Cannot connect to CarKeep API - server may be down or unreachable")
        }
      }
      console.error("[v0] API request failed:", error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const get = (endpoint: string) => request(endpoint)

  const post = (endpoint: string, data: any) =>
    request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    })

  const put = (endpoint: string, data: any) =>
    request(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    })

  const del = (endpoint: string) =>
    request(endpoint, {
      method: "DELETE",
    })

  return { get, post, put, delete: del, loading }
}
