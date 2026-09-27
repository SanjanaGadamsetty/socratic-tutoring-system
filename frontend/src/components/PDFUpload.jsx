import { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import { PDFDocument } from 'pdf-lib';
import { uploadPDF } from '../services/api';

const PDFUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pageCount, setPageCount] = useState(null);

  const validatePDF = async (file) => {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdfDoc = await PDFDocument.load(arrayBuffer);
      const numPages = pdfDoc.getPageCount();

      if (numPages > 2) {
        setError(`PDF has ${numPages} pages. Maximum 2 pages allowed.`);
        setFile(null);
        setPageCount(null);
        return false;
      }

      setPageCount(numPages);
      setError('');
      return true;
    } catch (err) {
      setError('Failed to read PDF file. Please ensure it is a valid PDF.');
      setFile(null);
      setPageCount(null);
      return false;
    }
  };

  const handleFileChange = async (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) {
      setFile(null);
      setPageCount(null);
      return;
    }

    if (selectedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file only.');
      setFile(null);
      setPageCount(null);
      return;
    }

    const isValid = await validatePDF(selectedFile);
    if (isValid) {
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file || !title.trim()) {
      setError('Please provide both a file and a title.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await uploadPDF(file, title, description);
      onUploadSuccess(result);

      // Reset form
      setFile(null);
      setTitle('');
      setDescription('');
      setPageCount(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Upload Study Material (PDF)
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Upload your study material (max 2 pages) to start tutoring
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
            required
            placeholder="e.g., Chemistry Chapter 3"
          />

          <TextField
            label="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
            multiline
            rows={2}
            placeholder="Brief description of the content"
          />

          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUpload />}
            fullWidth
          >
            Select PDF File (Max 2 Pages)
            <input
              type="file"
              hidden
              accept=".pdf"
              onChange={handleFileChange}
            />
          </Button>

          {file && pageCount !== null && (
            <Alert severity="success">
              ✓ {file.name} ({pageCount} page{pageCount !== 1 ? 's' : ''})
            </Alert>
          )}

          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || !title.trim() || loading}
            fullWidth
            size="large"
          >
            {loading ? <CircularProgress size={24} /> : 'Upload & Start Session'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PDFUpload;
