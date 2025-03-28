import axios from 'axios';
import {
  SegmentationResponse,
  AddDramaticTextRequest,
  AddTextResponse,
  ComposeRequest,
  ComposeResponse,
  MultiLayerTextRequest,
} from '../types/api';

// Create an Axios instance with common configuration
const apiClient = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
  // Increase timeout for image processing operations
  timeout: 300000, // 5 minutes
});

// Generic error handler for API calls
const handleApiError = (error: any) => {
  console.error('API Error:', error);
  
  if (error.code === 'ECONNABORTED') {
    throw new Error('The request took too long to process. Please try a smaller image or try again later.');
  }
  
  if (error.response) {
    throw new Error(error.response.data?.detail || 'Server error. Please try again.');
  } else if (error.request) {
    throw new Error('No response from server. Please check your connection and try again.');
  } else {
    throw new Error('Failed to make request. Please try again.');
  }
};

// API function to upload and segment an image
export const segmentImage = async (file: File): Promise<SegmentationResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    console.log('Sending segmentation request for file:', file.name);
    
    const response = await apiClient.post<SegmentationResponse>('/api/segment', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Segment image response:', response.data);
    console.log('Foreground URL:', response.data.foreground);
    console.log('Background URL:', response.data.background);
    console.log('Mask URL:', response.data.mask);
    
    return response.data;
  } catch (error) {
    console.error('Segmentation error details:', error);
    return handleApiError(error);
  }
};

// API function to add dramatic text
export const addDramaticText = async (request: AddDramaticTextRequest): Promise<AddTextResponse> => {
  try {
    const response = await apiClient.post<AddTextResponse>('/api/add-dramatic-text', request);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// API function to compose the final image
export const composeFinalImage = async (request: ComposeRequest): Promise<ComposeResponse> => {
  try {
    const response = await apiClient.post<ComposeResponse>('/api/compose', request);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// API function to add multiple text layers
export const addMultipleTextLayers = async (request: MultiLayerTextRequest): Promise<AddTextResponse> => {
  try {
    const response = await apiClient.post<AddTextResponse>('/api/add-multiple-text-layers', request);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}; 