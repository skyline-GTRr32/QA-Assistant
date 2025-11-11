'use client'

import { useRef, useState } from 'react'
import {
  Box,
  VStack,
  Text,
  Input,
  Icon,
  HStack,
  Button,
  chakra,
  Progress,
  useToast,
} from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { Globe, UploadCloud, Sparkles, Download } from 'lucide-react'
import Confetti from 'react-confetti'
import { analyzeWebsite } from '@/services/api'

const MotionBox = motion(chakra.div)

type ProgressStep = 'idle' | 'scraping' | 'analyzing' | 'capturing' | 'generating' | 'complete'

export const TestSection = () => {
  const toast = useToast()
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [url, setUrl] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisStep, setAnalysisStep] = useState<ProgressStep>('idle')
  const [percent, setPercent] = useState(0)
  const [reportReady, setReportReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const resetProgress = () => {
    setAnalysisStep('idle')
    setPercent(0)
    setReportReady(false)
    setError(null)
  }

  const handleFilePick = (f: File) => {
    if (!f) return
    if (!['application/pdf', 'text/plain'].includes(f.type) && !f.name.endsWith('.pdf') && !f.name.endsWith('.txt')) {
      toast({ title: 'Invalid file type', description: 'Please upload a PDF or TXT file.', status: 'error' })
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      toast({ title: 'File too large', description: 'Max size is 10MB.', status: 'error' })
      return
    }
    setFile(f)
  }

  const simulateProgress = async () => {
    const steps: Array<{ s: ProgressStep; p: number; t: number }> = [
      { s: 'scraping', p: 20, t: 700 },
      { s: 'analyzing', p: 45, t: 900 },
      { s: 'capturing', p: 70, t: 800 },
      { s: 'generating', p: 90, t: 900 },
    ]
    for (const step of steps) {
      setAnalysisStep(step.s)
      await new Promise((r) => setTimeout(r, step.t))
      setPercent(step.p)
    }
  }

  const handleAnalyze = async () => {
    resetProgress()
    if (!url.trim() || !file) {
      toast({ title: 'Missing inputs', description: 'Provide both a URL and a document.', status: 'warning' })
      return
    }
    try {
      setIsAnalyzing(true)
      const progress = simulateProgress()

      const response = await analyzeWebsite(url, file)

      // Finish progress
      setAnalysisStep('complete')
      setPercent(100)

      // Trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      const cd = response.headers['content-disposition']
      let filename = 'QA_Report.pdf'
      if (cd) {
        const m = cd.match(/filename="(.+)"/)
        if (m && m[1]) filename = m[1]
      }
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(downloadUrl)

      setReportReady(true)
      await progress
    } catch (e: any) {
      setError(e?.message || 'An unknown error occurred')
      toast({ title: 'Analysis failed', description: e?.message || 'Unknown error', status: 'error' })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <Box as="section" id="try" position="relative" bgGradient="linear(to-b, #fafafa, #f9fafb)" pt={{ base: 12, md: 20 }} pb={{ base: 16, md: 24 }}>
      {/* Wave divider top */}
      <Box
        aria-hidden
        position="absolute"
        top="-1px"
        left={0}
        right={0}
        h="80px"
        bgImage="url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 1440 80%22><path fill=%22%23ffffff%22 d=%22M0,64L80,53.3C160,43,320,21,480,26.7C640,32,800,64,960,74.7C1120,85,1280,75,1360,69.3L1440,64L1440,0L1360,0C1280,0,1120,0,960,0C800,0,640,0,480,0C320,0,160,0,80,0L0,0Z%22/></svg>')"
        bgRepeat="no-repeat"
        bgPos="top"
        bgSize="cover"
      />

      <VStack maxW="960px" mx="auto" px={{ base: 6, md: 10 }} spacing={8} align="stretch">
        <VStack spacing={2} textAlign="center">
          <Text as="h2" fontSize={{ base: '2xl', md: '4xl' }} fontWeight="extrabold" color="#111827">
            Try It Now
          </Text>
          <Text fontSize={{ base: 'md', md: 'lg' }} color="#6b7280">
            Upload your design document and website URL - see the magic happen
          </Text>
        </VStack>

        {/* Step 1: URL Input (glass effect) */}
        <MotionBox
          bg="rgba(255,255,255,0.65)"
          border="1px solid rgba(17,24,39,0.08)"
          style={{ backdropFilter: 'blur(12px)' }}
          borderRadius="18px"
          px={4}
          py={3}
          whileFocus={{ boxShadow: '0 0 0 6px rgba(37,99,235,0.12)' }}
        >
          <HStack gap={3}>
            <Icon as={Globe} color="#2563eb" aria-label="Website URL" />
            <Input
              aria-label="Website URL"
              placeholder="https://your-website.com"
              variant="unstyled"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              _focus={{ outline: 'none' }}
            />
          </HStack>
          <Box mt={2} h="2px" bgGradient="linear(to-r, #9333ea, #ec4899, #2563eb)" />
        </MotionBox>

        {/* Connector line */}
        <Box mx="auto" w="2px" h="24px" bgGradient="linear(to-b, #9333ea, #ec4899, #2563eb)" opacity={0.5} />

        {/* Step 2: Drag & Drop */}
        <MotionBox
          role="button"
          aria-label="Upload design document"
          tabIndex={0}
          onKeyDown={(e: any) => {
            if (e.key === 'Enter') fileInputRef.current?.click()
          }}
          onClick={() => fileInputRef.current?.click()}
          bg="rgba(255,255,255,0.65)"
          border="2px dashed transparent"
          borderRadius="18px"
          px={{ base: 4, md: 6 }}
          py={{ base: 8, md: 10 }}
          textAlign="center"
          style={{ backdropFilter: 'blur(12px)' }}
          whileHover={{ scale: 1.01, boxShadow: '0 18px 40px rgba(147,51,234,0.12)' }}
          transition={{ type: 'spring', stiffness: 120, damping: 16 }}
          position="relative"
          _before={{
            content: '""',
            position: 'absolute',
            inset: 0,
            borderRadius: '18px',
            padding: '2px',
            background: 'linear-gradient(45deg,#9333ea,#ec4899,#2563eb)',
            WebkitMask:
              'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            maskComposite: 'exclude',
          }}
        >
          <Icon as={UploadCloud} aria-hidden boxSize={10} color="#9333ea" />
          <Text fontWeight="bold" mt={2} color="#111827">
            Drop your design document here
          </Text>
          <Text fontSize="sm" color="#6b7280">
            or click to browse (PDF, TXT - max 10MB)
          </Text>
          {file && (
            <Box
              mt={4}
              display="inline-block"
              px={3}
              py={1}
              borderRadius="9999px"
              bgGradient="linear(to-r, #2563eb, #9333ea)"
              color="white"
            >
              {file.name}
            </Box>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            style={{ display: 'none' }}
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) handleFilePick(f)
            }}
          />
        </MotionBox>

        {/* Step 3: Analyze Button */}
        <Box textAlign="center">
          <Button
            onClick={handleAnalyze}
            isDisabled={!url.trim() || !file || isAnalyzing}
            size="lg"
            px={8}
            py={6}
            borderRadius="9999px"
            bgGradient="linear(to-r, #2563eb, #9333ea)"
            _hover={{
              transform: 'translateY(-2px) scale(1.01)',
              boxShadow: '0 20px 50px rgba(37,99,235,0.25)',
              bgGradient: 'linear(to-r, #3b82f6, #ec4899)',
            }}
            leftIcon={<Icon as={Sparkles} />}
            color="white"
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze Website'}
          </Button>
        </Box>

        {/* Progress / Loading */}
        {isAnalyzing && (
          <VStack spacing={3} pt={2}>
            <Text color="#6b7280" fontSize="sm">
              {analysisStep === 'scraping' && 'Scraping website...'}
              {analysisStep === 'analyzing' && 'Analyzing design...'}
              {analysisStep === 'capturing' && 'Capturing screenshots...'}
              {analysisStep === 'generating' && 'Generating report...'}
            </Text>
            <Progress colorScheme="blue" bg="#e5e7eb" w="100%" borderRadius="full" value={percent} />
          </VStack>
        )}

        {/* Results */}
        {reportReady && !isAnalyzing && (
          <VStack spacing={4} pt={2} textAlign="center">
            <Confetti numberOfPieces={200} recycle={false} />
            <Text fontSize={{ base: 'lg', md: 'xl' }} fontWeight="bold" color="#111827">
              Analysis Complete! 🎉
            </Text>
            <Text color="#6b7280">Your PDF report has been downloaded.</Text>
          </VStack>
        )}

        {error && (
          <Box color="red.500" textAlign="center">
            {error}
          </Box>
        )}
      </VStack>
    </Box>
  )
}

