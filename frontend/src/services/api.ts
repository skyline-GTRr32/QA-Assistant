// frontend/src/services/api.ts

import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api', // Your backend API base URL
});

/**
 * Sends the website URL and design document to the backend for analysis.
 * The backend will process this and return a PDF file as a blob.
 */
export const analyzeWebsite = async (url: string, file: File) => {
  // We use FormData to send a file and text together
  const formData = new FormData();
  formData.append('url', url);
  formData.append('file', file);

  try {
    const response = await apiClient.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob', // This is crucial to handle the PDF file response
    });
    return response; // Return the full response so we can access the data blob
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Try to read the error message from the blob response
      const errorText = await error.response.data.text();
      const errorJson = JSON.parse(errorText);
      throw new Error(errorJson.detail || 'An unknown error occurred during analysis.');
    }
    throw error;
  }
};