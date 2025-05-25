import React, { Component, ErrorInfo } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  useTheme,
} from '@mui/material';
import { Error as ErrorIcon, Refresh as RefreshIcon } from '@mui/icons-material';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: Props) {
    if (
      this.props.resetOnPropsChange &&
      prevProps.children !== this.props.children
    ) {
      this.setState({
        hasError: false,
        error: null,
      });
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorFallback
          error={this.state.error}
          onReset={this.handleReset}
        />
      );
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error | null;
  onReset: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, onReset }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        p: 3,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 600,
          width: '100%',
          textAlign: 'center',
          borderRadius: theme.shape.borderRadius,
        }}
      >
        <ErrorIcon
          color="error"
          sx={{ fontSize: 64, mb: 2 }}
        />
        <Typography variant="h5" component="h1" gutterBottom>
          Oops! Something went wrong
        </Typography>
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mb: 3 }}
        >
          {error?.message || 'An unexpected error occurred'}
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={onReset}
          sx={{
            borderRadius: theme.shape.borderRadius,
          }}
        >
          Try Again
        </Button>
      </Paper>
    </Box>
  );
};

export default ErrorBoundary; 