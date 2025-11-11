'use client'

import { ChakraProvider } from '@chakra-ui/react'
import { theme } from '../theme' // We use ../theme because we are inside the app folder

export function Providers({ children }: { children: React.ReactNode }) {
  return <ChakraProvider theme={theme}>{children}</ChakraProvider>
}