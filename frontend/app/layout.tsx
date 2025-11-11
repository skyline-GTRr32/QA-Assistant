import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers' // Import the new client component
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Website QA Agent',
  description: 'Analyze and compare websites with design documents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}