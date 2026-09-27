import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { QuestionAnswer } from '@mui/icons-material';
import { getProblems, startProblemSession } from '../services/api';

const ProblemSelector = ({ studentId, onSessionStart }) => {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [startingSession, setStartingSession] = useState(null);

  useEffect(() => {
    loadProblems();
  }, []);

  const loadProblems = async () => {
    try {
      const data = await getProblems();
      setProblems(data.problems || []);
    } catch (err) {
      setError('Failed to load problems. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = async (problemId) => {
    setStartingSession(problemId);
    setError(''); // Clear previous errors
    try {
      const session = await startProblemSession(problemId, studentId);
      onSessionStart(session, 'problem');
    } catch (err) {
      console.error('Session start error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to start session. Please try again.';
      setError(errorMsg);
    } finally {
      setStartingSession(null);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Select a Problem to Practice
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Choose a problem and start your Socratic tutoring session
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {problems.map((problem) => (
          <Grid item xs={12} sm={6} md={4} key={problem.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <QuestionAnswer color="primary" />
                  <Chip
                    label={problem.difficulty_level || 'Medium'}
                    color={getDifficultyColor(problem.difficulty_level)}
                    size="small"
                  />
                </Box>

                <Typography variant="h6" gutterBottom>
                  {problem.title}
                </Typography>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Topic: {problem.topic || 'General'}
                </Typography>

                <Typography variant="body2" sx={{ mb: 2, minHeight: 60 }}>
                  {problem.problem_text.length > 100
                    ? problem.problem_text.substring(0, 100) + '...'
                    : problem.problem_text}
                </Typography>

                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => handleStartSession(problem.id)}
                  disabled={startingSession === problem.id}
                >
                  {startingSession === problem.id ? (
                    <CircularProgress size={24} />
                  ) : (
                    'Start Session'
                  )}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {problems.length === 0 && (
          <Grid item xs={12}>
            <Alert severity="info">
              No problems available. Please create some problems first using the API.
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ProblemSelector;
