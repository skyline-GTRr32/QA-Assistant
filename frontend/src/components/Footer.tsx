'use client'

import { Box, VStack, Text } from '@chakra-ui/react'

export const Footer = () => {
  return (
    <Box as="footer" bg="#111827" color="#9ca3af" py={{ base: 12, md: 16 }}>
      <VStack spacing={3} textAlign="center" maxW="960px" mx="auto" px={{ base: 6, md: 10 }}>
        <Text as="h3" fontSize="lg" color="white" fontWeight="bold">
          QA Assistant
        </Text>
        <Text>AI-powered website quality assurance</Text>
        <Text fontSize="sm">Made by Umar Umais</Text>
        <Text fontSize="sm">© 2025 • Built with ❤️ and AI</Text>
      </VStack>
    </Box>
  )
}

