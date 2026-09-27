import axios from 'axios';

// Use environment variable in production, fallback to localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session APIs
export const startProblemSession = async (problemId, studentId) => {
  const response = await api.post('/sessions/start', {
    problem_id: problemId,
    student_id: studentId,
  });
  // Transform response to match frontend expectations
  const data = response.data;
  return {
    ...data,
    id: data.session_id,
  };
};

export const startPDFSession = async (pdfId, studentId) => {
  const response = await api.post('/sessions/start', {
    pdf_document_id: pdfId,
    student_id: studentId,
  });
  // Transform response to match frontend expectations
  const data = response.data;
  return {
    ...data,
    id: data.session_id,
  };
};

export const submitTurn = async (sessionId, studentResponse) => {
  const response = await api.post(`/sessions/${sessionId}/turn`, {
    student_answer: studentResponse,
  });
  return response.data;
};

export const getTranscript = async (sessionId) => {
  const response = await api.get(`/sessions/${sessionId}/transcript`);
  return response.data;
};

// Problem APIs
export const getProblems = async () => {
  const response = await api.get('/problems');
  const data = response.data;
  // Transform problems to match frontend expectations
  if (data.problems) {
    data.problems = data.problems.map(problem => ({
      ...problem,
      difficulty_level: problem.difficulty,
    }));
  }
  return data;
};

export const createProblem = async (problemData) => {
  const response = await api.post('/problems', problemData);
  return response.data;
};

// PDF APIs
export const uploadPDF = async (file, title, description) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  if (description) {
    formData.append('description', description);
  }

  const response = await axios.post(`${API_BASE_URL}/pdfs/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getPDFDocuments = async () => {
  const response = await api.get('/pdfs');
  return response.data;
};

export default api;
