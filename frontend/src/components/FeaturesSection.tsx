'use client'

import { Box, VStack, Text, HStack, chakra, Code } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { Brain, Camera, Gauge, Ruler, ListChecks, Zap } from 'lucide-react'

const MotionBox = motion(chakra.div)

const items = [
  { icon: Brain, title: 'AI-Powered Diff', desc: 'LLM-assisted comparison of CSS/HTML vs. design specs.' },
  { icon: Camera, title: 'Auto Screenshots', desc: 'Pinpoint issues with element-level captures.' },
  { icon: Gauge, title: 'Performance Built-In', desc: 'PageSpeed metrics in every run.' },
  { icon: Ruler, title: 'Design Compliance', desc: 'Colors, typography, layout, content verified.' },
  { icon: ListChecks, title: 'Evidence-Based', desc: 'Exact selectors, values, and doc page refs.' },
  { icon: Zap, title: '<60s Reports', desc: 'From URL + doc to downloadable PDF.' },
]

const codeSample = `// QA run (pseudo)
await analyze({
  url: "https://product.io",
  doc: "brand-guide.pdf"
})
// => report.pdf with issues[], screenshots[], metrics{}`

export const FeaturesSection = () => {
  return (
    <Box as="section" id="why" position="relative" bg="#0b1020">
      <VStack maxW="1200px" mx="auto" px={{ base: 6, md: 10 }} py={{ base: 16, md: 24 }} spacing={10} align="stretch">
        <VStack spacing={2} align="start">
          <Text as="h2" fontSize={{ base: '2xl', md: '4xl' }} fontWeight="extrabold" color="white">
            Why engineering teams choose our QA tool
          </Text>
          <Text fontSize={{ base: 'md', md: 'lg' }} color="#9ca3af">
            Built like the tools we love — minimal, fast, developer-first.
          </Text>
        </VStack>

        {/* Two-column: left = compact feature list, right = code/editor */}
        <Box display="grid" gridTemplateColumns={{ base: '1fr', md: '1.2fr 1fr' }} gap={{ base: 8, md: 12 }}>
          {/* Left: Feature rows (no cards) */}
          <VStack spacing={5} align="stretch">
            {items.map((f, idx) => {
              const Icon = f.icon
              return (
                <MotionBox
                  key={f.title}
                  display="flex"
                  alignItems="flex-start"
                  gap={4}
                  px={0}
                  py={2}
                  borderBottom="1px solid rgba(148,163,184,0.15)"
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.05 }}
                >
                  <Box
                    aria-hidden
                    minW="40px"
                    minH="40px"
                    display="grid"
                    placeItems="center"
                    borderRadius="8px"
                    bg="#0a0f23"
                    border="1px solid #1f2a44"
                    color="#e5f2ff"
                    boxShadow="0 0 18px rgba(59,130,246,0.25)"
                  >
                    <Icon aria-hidden size={20} />
                  </Box>
                  <VStack spacing={0} align="start">
                    <Text as="h3" fontSize="lg" fontWeight="bold" color="white">
                      {f.title}
                    </Text>
                    <Text fontSize="md" color="#9ca3af">
                      {f.desc}
                    </Text>
                  </VStack>
                </MotionBox>
              )
            })}

            {/* Inline trust indicators (no cards) */}
            <HStack spacing={4} pt={2} color="#9ca3af" fontFamily="mono">
              <Text><Box as="span" color="#22c55e">99.9%</Box> uptime</Text>
              <Text>•</Text>
              <Text>Export: PDF</Text>
              <Text>•</Text>
              <Text>API-first</Text>
              <Text>•</Text>
              <Text>Local dev friendly</Text>
            </HStack>
          </VStack>

          {/* Right: Minimal code editor aesthetic */}
          <MotionBox
            bg="#0a0f23"
            border="1px solid #1f2a44"
            borderRadius="12px"
            overflow="hidden"
            boxShadow="0 10px 40px rgba(0,0,0,0.35)"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            {/* Editor header */}
            <HStack justify="space-between" px={4} py={2} borderBottom="1px solid #1f2a44">
              <HStack spacing={2}>
                <Box w="10px" h="10px" borderRadius="50%" bg="#ef4444" />
                <Box w="10px" h="10px" borderRadius="50%" bg="#f59e0b" />
                <Box w="10px" h="10px" borderRadius="50%" bg="#22c55e" />
              </HStack>
              <Text fontSize="xs" color="#9ca3af">qa-run.ts</Text>
            </HStack>
            {/* Editor body */}
            <Box display="grid" gridTemplateColumns="40px 1fr">
              <VStack align="end" spacing={0} py={4} px={2} bg="#080c1a" color="#475569" fontFamily="mono" fontSize="xs">
                {Array.from({ length: 10 }).map((_, i) => (
                  <Text key={i}>{i + 1}</Text>
                ))}
              </VStack>
              <Box py={4} px={4} color="#e5f2ff" fontFamily="mono" fontSize="sm">
                <Code whiteSpace="pre" bg="transparent" color="inherit" p={0}>
{codeSample}
                </Code>
                <Box mt={3} color="#22c55e">_ ready: report.pdf</Box>
              </Box>
            </Box>
          </MotionBox>
        </Box>
      </VStack>
    </Box>
  )
}

