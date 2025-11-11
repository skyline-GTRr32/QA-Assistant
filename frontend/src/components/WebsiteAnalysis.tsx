'use client'

import { useState } from 'react'
import {
  Box,
  Button,
  VStack,
  Text,
  useToast,
  Input,
  FormControl,
  FormLabel,
} from '@chakra-ui/react'
import { analyzeWebsite } from '@/services/api'

export const WebsiteAnalysis = () => {
  const [url, setUrl] = useState('')
  // State is now for a File object, not a string
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false)
  const toast = useToast()

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === 'application/pdf' || file.type === 'text/plain') {
        setSelectedFile(file);
      } else {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a PDF or TXT file.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  const handleAnalyze = async () => {
    // Updated validation to check for a selected file
    if (!url.trim() || !selectedFile) {
      toast({
        title: 'Please provide both a URL and a design document',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      setIsLoading(true)
      toast({
        title: 'Analysis Started',
        description: 'This may take a minute. Your report will download automatically.',
        status: 'info',
        duration: 10000,
        isClosable: true,
      });

      // The API call now sends the file object
      const response = await analyzeWebsite(url, selectedFile);

      // --- PDF Download Logic ---
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      // Extract filename from response headers or set a default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'QA_Report.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch.length === 2)
          filename = filenameMatch[1];
      }
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      // --- End of Download Logic ---

      toast({
        title: 'Analysis Complete!',
        description: 'Your PDF report has been downloaded.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      toast({
        title: 'Error Analyzing Website',
        description: error instanceof Error ? error.message : 'An unknown error occurred.',
        status: 'error',
        duration: 9000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <VStack spacing={6} align="stretch">
      <Box borderWidth="1px" borderRadius="lg" p={6} boxShadow="sm">
        <VStack spacing={5} align="stretch">
          <FormControl isRequired>
            <FormLabel fontWeight="bold">Website URL to analyze:</FormLabel>
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
            />
          </FormControl>

          <FormControl isRequired>
            <FormLabel fontWeight="bold">Design Documentation (PDF or TXT):</FormLabel>
            <Input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.txt"
              p={1.5} // Add padding to the file input
            />
             {selectedFile && <Text fontSize="sm" mt={2} color="gray.600">Selected: {selectedFile.name}</Text>}
          </FormControl>

          <Button
            colorScheme="blue"
            onClick={handleAnalyze}
            isLoading={isLoading}
            loadingText="Analyzing..."
            mt={4}
            size="lg"
          >
            Analyze Website & Download Report
          </Button>
        </VStack>
      </Box>

      {/* The old report display is removed, as the result is now a PDF download */}
    </VStack>
  )
}