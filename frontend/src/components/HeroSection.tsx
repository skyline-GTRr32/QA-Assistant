'use client'

import { Box, VStack, Text, Badge, chakra, HStack } from '@chakra-ui/react'
import { motion, useMotionValue, useTransform } from 'framer-motion'
import { useCallback } from 'react'

const MotionBox = motion(chakra.div)

export const HeroSection = () => {
  // Mouse parallax (subtle)
  const mx = useMotionValue(0)
  const my = useMotionValue(0)
  const rotX = useTransform(my, [-50, 50], [6, -6])
  const rotY = useTransform(mx, [-50, 50], [-6, 6])

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    const { innerWidth, innerHeight } = window
    const x = (e.clientX / innerWidth) * 100 - 50
    const y = (e.clientY / innerHeight) * 100 - 50
    mx.set(x)
    my.set(y)
  }, [mx, my])

  return (
    <Box
      as="section"
      minH="100vh"
      position="relative"
      overflow="hidden"
      bg="#050816"
      onMouseMove={onMouseMove}
    >
      {/* Hex / grid overlay via SVG (solid strokes, no color gradients) */}
      <Box aria-hidden position="absolute" inset={0} opacity={0.06}
        bgImage={`url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'%3E%3Cg stroke='%2388a' stroke-width='1' fill='none' opacity='0.9'%3E%3Cpath d='M32 0 L64 16 L64 48 L32 64 L0 48 L0 16 Z'/%3E%3C/g%3E%3C/svg%3E")`}
        bgSize="64px 64px" bgRepeat="repeat"
      />

      {/* Subtle matrix code (falling) */}
      <MotionBox aria-hidden position="absolute" inset={0} color="#3b82f6" fontFamily="mono" fontSize="xs" opacity={0.05}
        animate={{ y: ['-20%', '0%'] }} transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
        whiteSpace="pre" px={6} pt={8}
      >
        {'01010100110110100100 1010011010010110 0101010011 001101\n'.repeat(40)}
      </MotionBox>

      {/* Scanline */}
      <MotionBox aria-hidden position="absolute" left={0} right={0} height="2px" bg="#0ea5e9" opacity={0.12}
        animate={{ top: ['0%', '100%'] }} transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
      />

      {/* Content - tech style */}
      <MotionBox style={{ rotateX: rotX, rotateY: rotY, transformStyle: 'preserve-3d' }}>
      <VStack
        spacing={6}
        align="start"
        position="relative"
        zIndex={1}
        maxW="1200px"
        mx="auto"
        px={{ base: 6, md: 10 }}
        pt={{ base: 24, md: 36 }}
        pb={{ base: 16, md: 24 }}
        color="white"
      >
        <HStack>
          <Box w="8px" h="8px" borderRadius="50%" bg="#06b6d4" boxShadow="0 0 12px #06b6d4, 0 0 24px #06b6d4" />
          <Badge
            fontSize="0.75rem"
            px={3}
            py={1}
            borderRadius="full"
            bg="#0a0f23"
            border="1px solid #0ea5e9"
            color="#e5f2ff"
            fontFamily="mono"
            boxShadow="0 0 12px rgba(14,165,233,0.35)"
          >
            ◉ AI-Powered Analysis
          </Badge>
        </HStack>

        <MotionBox
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Text
            as="h1"
            fontWeight="extrabold"
            lineHeight="1.02"
            letterSpacing="-0.02em"
            fontSize={{ base: '3rem', md: '5.5rem', lg: '7rem' }}
            textShadow="0 0 24px rgba(59,130,246,0.35)"
          >
            Automated QA for Modern Websites
          </Text>
        </MotionBox>

        <MotionBox
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.15 }}
          maxW={{ base: '90%', md: '560px' }}
        >
          <Text
            fontSize={{ base: 'md', md: 'lg' }}
            color="#a1a1aa"
            fontFamily="mono"
          >
            Analyze. Compare. Report. All in 60 seconds.
          </Text>
        </MotionBox>

        {/* Tech stats / metrics */}
        <HStack spacing={4} color="#9ca3af" fontFamily="mono" pt={2}>
          <Text><Box as="span" color="#22c55e">{'<1min'}</Box> | Analysis Time</Text>
          <Text>•</Text>
          <Text><Box as="span" color="#22c55e">AI-Powered</Box> | Smart Detection</Text>
          <Text>•</Text>
          <Text><Box as="span" color="#22c55e">100% Automated</Box> | Zero Setup</Text>
        </HStack>

        {/* CTA */}
        <MotionBox
          whileHover={{ scale: 1.02, boxShadow: '0 0 28px rgba(59,130,246,0.45)' }}
          whileTap={{ scale: 0.99 }}
          mt={4}
        >
          <Box
            as="a"
            href="#try"
            px={6}
            py={3}
            borderRadius="md"
            bg="#0b1226"
            border="1px solid #3b82f6"
            color="white"
            fontFamily="mono"
          >
            → Start Analysis  <Box as="span" color="#9ca3af">Press ⌘K</Box>
          </Box>
        </MotionBox>
      </VStack>
      </MotionBox>

      {/* Floating wireframe elements */}
      <MotionBox aria-hidden position="absolute" right="8%" top="20%" w="220px" h="220px" border="1px solid #3b82f6"
        opacity={0.25} style={{ transformStyle: 'preserve-3d' }}
        animate={{ rotateZ: [0, 360] }} transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      />
      <MotionBox aria-hidden position="absolute" left="6%" bottom="12%" w="180px" h="180px" borderRadius="50%"
        border="1px dashed #06b6d4" opacity={0.25}
        animate={{ rotate: [0, 360] }} transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
      />

      {/* SYSTEM ONLINE indicator */}
      <Box position="absolute" top={3} right={4} fontFamily="mono" fontSize="xs" color="#22c55e">
        ● SYSTEM ONLINE
      </Box>
    </Box>
  )
}

