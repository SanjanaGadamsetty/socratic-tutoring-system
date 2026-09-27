import { createTheme } from '@mui/material/styles';

// Yellow and White Theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#FDB813', // Vibrant yellow
      light: '#FFD54F',
      dark: '#F9A825',
      contrastText: '#000000',
    },
    secondary: {
      main: '#FFC107', // Amber yellow
      light: '#FFD54F',
      dark: '#FFA000',
      contrastText: '#000000',
    },
    background: {
      default: '#FFFEF7', // Off-white/cream
      paper: '#FFFFFF',
    },
    text: {
      primary: '#000000',
      secondary: '#424242',
    },
    warning: {
      main: '#FF9800',
    },
    success: {
      main: '#FDB813',
      contrastText: '#000000',
    },
    error: {
      main: '#D32F2F',
      contrastText: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { color: '#000000' },
    h2: { color: '#000000' },
    h3: { color: '#000000' },
    h4: { color: '#000000' },
    h5: { color: '#000000' },
    h6: { color: '#000000' },
    body1: { color: '#000000' },
    body2: { color: '#424242' },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FDB813',
          color: '#000000',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        contained: {
          backgroundColor: '#FDB813',
          color: '#000000',
          '&:hover': {
            backgroundColor: '#F9A825',
          },
        },
        outlined: {
          borderColor: '#FDB813',
          color: '#000000',
          '&:hover': {
            borderColor: '#F9A825',
            backgroundColor: 'rgba(253, 184, 19, 0.04)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFF9E6',
          color: '#000000',
          borderColor: '#FDB813',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '&:hover fieldset': {
              borderColor: '#FDB813',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#FDB813',
            },
          },
        },
      },
    },
  },
});

export default theme;
