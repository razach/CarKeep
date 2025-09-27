import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import { Suspense } from "react"
import "./globals.css"

import { Geist as V0_Font_Geist, Geist_Mono as V0_Font_Geist_Mono, Source_Serif_4 as V0_Font_Source_Serif_4 } from 'next/font/google'

// Initialize fonts
const geist = V0_Font_Geist({ 
  weight: ["100","200","300","400","500","600","700","800","900"],
  subsets: ["latin"]
})
const geistMono = V0_Font_Geist_Mono({ 
  weight: ["100","200","300","400","500","600","700","800","900"],
  subsets: ["latin"]
})
const sourceSerif = V0_Font_Source_Serif_4({ 
  weight: ["200","300","400","500","600","700","800","900"],
  subsets: ["latin"]
})

export const metadata: Metadata = {
  title: "CarKeep - Vehicle Cost Comparison",
  description: "Compare vehicle costs and make informed financial decisions",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable} antialiased`}>
        <Suspense fallback={null}>{children}</Suspense>
        <Analytics />
      </body>
    </html>
  )
}
