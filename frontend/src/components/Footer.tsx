'use client'

import { Box, VStack, Text, HStack, Link } from '@chakra-ui/react'

export const Footer = () => {
  return (
    <Box as="footer" bg="#111827" color="#9ca3af" py={{ base: 12, md: 16 }}>
      <VStack spacing={3} textAlign="center" maxW="960px" mx="auto" px={{ base: 6, md: 10 }}>
        <Text as="h3" fontSize="lg" color="white" fontWeight="bold">
          QA Assistant
        </Text>
        <Text>AI-powered website quality assurance</Text>
        <HStack spacing={3}>
          <Link href="#" _hover={{ color: 'blue.300', textDecoration: 'underline' }}>Privacy Policy</Link>
          <Text>·</Text>
          <Link href="#" _hover={{ color: 'blue.300', textDecoration: 'underline' }}>Terms of Service</Link>
          <Text>·</Text>
          <Link href="#" _hover={{ color: 'blue.300', textDecoration: 'underline' }}>Contact</Link>
        </HStack>
        <Text fontSize="sm">© 2025 • Built with ❤️ and AI</Text>
      </VStack>
    </Box>
  )
}

