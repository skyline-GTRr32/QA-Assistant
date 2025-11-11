'use client'

import { Box } from '@chakra-ui/react'
import { HeroSection } from '@/components/HeroSection'
import { FeaturesSection } from '@/components/FeaturesSection'
import { TestSection } from '@/components/TestSection'
import { Footer } from '@/components/Footer'

export default function Home() {
  return (
    <Box as="main" bgGradient="linear(to-b, #fafafa, #f9fafb)" overflow="hidden">
      <HeroSection />
      <FeaturesSection />
      <TestSection />
      <Footer />
    </Box>
  )
}