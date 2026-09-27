import { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material';
import { Send, Person, School } from '@mui/icons-material';
import { submitTurn, getTranscript } from '../services/api';

const ChatInterface = ({ sessionId, sessionType, onEndSession }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadTranscript();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadTranscript = async () => {
    try {
      const transcript = await getTranscript(sessionId);
      setMessages(transcript.turns || []);
    } catch (err) {
      console.error('Failed to load transcript:', err);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        speaker: 'student',
        message: userMessage,
        timestamp: new Date().toISOString(),
      },
    ]);

    setLoading(true);

    try {
      const response = await submitTurn(sessionId, userMessage);

      // Add tutor response
      setMessages((prev) => [
        ...prev,
        {
          speaker: 'tutor',
          message: response.tutor_question || response.tutor_response,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error('Failed to send message:', err);
      setMessages((prev) => [
        ...prev,
        {
          speaker: 'tutor',
          message: 'Sorry, there was an error. Please try again.',
          timestamp: new Date().toISOString(),
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6">Socratic Tutoring Session</Typography>
            <Chip
              label={sessionType === 'problem' ? 'Problem-Based' : 'PDF-Based'}
              color="primary"
              size="small"
              sx={{ mt: 1 }}
            />
          </Box>
          <Button variant="outlined" color="error" onClick={onEndSession}>
            End Session
          </Button>
        </Box>
      </Paper>

      {/* Messages */}
      <Paper
        sx={{
          flex: 1,
          p: 2,
          overflow: 'auto',
          mb: 2,
          backgroundColor: '#FFFEF7',
        }}
      >
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
            <School sx={{ fontSize: 48, mb: 2 }} />
            <Typography>
              Start by asking a question or sharing your thoughts!
            </Typography>
          </Box>
        )}

        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: msg.speaker === 'student' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Box
              sx={{
                maxWidth: '70%',
                display: 'flex',
                flexDirection: msg.speaker === 'student' ? 'row-reverse' : 'row',
                gap: 1,
              }}
            >
              {/* Avatar */}
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  backgroundColor: msg.speaker === 'student' ? '#FDB813' : '#FFC107',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#000000',
                }}
              >
                {msg.speaker === 'student' ? <Person /> : <School />}
              </Box>

              {/* Message bubble */}
              <Box>
                <Paper
                  sx={{
                    p: 2,
                    backgroundColor: msg.speaker === 'student' ? '#FFF9E6' : 'white',
                    borderRadius: 2,
                    border: '1px solid #FDB813',
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 'bold',
                      color: '#000000',
                    }}
                  >
                    {msg.speaker === 'student' ? 'You' : 'Tutor'}
                  </Typography>
                  <Typography sx={{ mt: 0.5, color: '#000000' }}>{msg.message}</Typography>
                </Paper>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, ml: 1 }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Typography>
              </Box>
            </Box>
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                backgroundColor: '#FFC107',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#000000',
              }}
            >
              <School />
            </Box>
            <Paper sx={{ p: 2, backgroundColor: 'white' }}>
              <CircularProgress size={20} />
              <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>
                Tutor is thinking...
              </Typography>
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Input */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Type your response or question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <Button
            variant="contained"
            endIcon={<Send />}
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
