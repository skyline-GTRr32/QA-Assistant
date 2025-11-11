'use client'

import { ChakraProvider } from '@chakra-ui/react'
import { theme } from '../src/theme' // Ensure this path correctly points to your theme file

export function Providers({ children }: { children: React.ReactNode }) {
  return <ChakraProvider theme={theme}>{children}</ChakraProvider>
}