import { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  TextField,
  Button,
  AppBar,
  Toolbar,
} from '@mui/material';
import { School } from '@mui/icons-material';
import ProblemSelector from './components/ProblemSelector';
import PDFUpload from './components/PDFUpload';
import ChatInterface from './components/ChatInterface';
import { startPDFSession } from './services/api';

function App() {
  const [studentId, setStudentId] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [activeSession, setActiveSession] = useState(null);
  const [sessionType, setSessionType] = useState(null);

  const handleLogin = () => {
    if (studentId.trim()) {
      setIsLoggedIn(true);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  const handleSessionStart = (session, type) => {
    setActiveSession(session);
    setSessionType(type);
  };

  const handlePDFUploadSuccess = async (uploadResult) => {
    try {
      const pdfId = uploadResult.pdf_id || uploadResult.document_id;
      const session = await startPDFSession(pdfId, studentId);
      handleSessionStart(session, 'pdf');
    } catch (err) {
      console.error('Failed to start PDF session:', err);
      alert('Failed to start tutoring session. Please try again.');
    }
  };

  const handleEndSession = () => {
    setActiveSession(null);
    setSessionType(null);
  };

  // Login screen
  if (!isLoggedIn) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#FFFEF7',
        }}
      >
        <Paper sx={{ p: 4, maxWidth: 400, width: '100%' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <School sx={{ fontSize: 60, color: 'primary.main' }} />
            <Typography variant="h4" gutterBottom>
              Socratic Tutor
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Multi-Agent AI Tutoring System
            </Typography>
          </Box>

          <TextField
            fullWidth
            label="Enter Your Student ID"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., student123"
            sx={{ mb: 2 }}
          />

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleLogin}
            disabled={!studentId.trim()}
          >
            Start Learning
          </Button>
        </Paper>
      </Box>
    );
  }

  // Active session screen
  if (activeSession) {
    return (
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static">
          <Toolbar>
            <School sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Socratic Tutor - {studentId}
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg" sx={{ flex: 1, py: 3, display: 'flex', flexDirection: 'column' }}>
          <ChatInterface
            sessionId={activeSession.id}
            sessionType={sessionType}
            onEndSession={handleEndSession}
          />
        </Container>
      </Box>
    );
  }

  // Session selection screen
  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <School sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Socratic Tutor - {studentId}
          </Typography>
          <Button color="inherit" onClick={() => setIsLoggedIn(false)}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            centered
          >
            <Tab label="Practice Problems" />
            <Tab label="Upload Study Material" />
          </Tabs>
        </Paper>

        <Box sx={{ mt: 3 }}>
          {tabValue === 0 && (
            <ProblemSelector
              studentId={studentId}
              onSessionStart={handleSessionStart}
            />
          )}

          {tabValue === 1 && (
            <Box sx={{ maxWidth: 600, mx: 'auto' }}>
              <PDFUpload onUploadSuccess={handlePDFUploadSuccess} />
            </Box>
          )}
        </Box>
      </Container>
    </Box>
  );
}

export default App;
