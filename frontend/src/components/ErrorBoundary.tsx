import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Container,
  useTheme,
} from '@mui/material';
import { Error as ErrorIcon, Refresh as RefreshIcon } from '@mui/icons-material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <ErrorDisplay
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onReset={this.handleReset}
        />
      );
    }

    return this.props.children;
  }
}

interface ErrorDisplayProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  onReset: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, errorInfo, onReset }) => {
  const theme = useTheme();

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
            width: '100%',
            maxWidth: 600,
            textAlign: 'center',
          }}
        >
          <ErrorIcon
            sx={{
              fontSize: 64,
              color: theme.palette.error.main,
              mb: 2,
            }}
          />
          <Typography variant="h4" gutterBottom>
            Oops! Something went wrong
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            We apologize for the inconvenience. An error has occurred in the application.
          </Typography>
          {process.env.NODE_ENV === 'development' && (
            <Box
              sx={{
                mt: 3,
                p: 2,
                backgroundColor: theme.palette.background.default,
                borderRadius: 1,
                textAlign: 'left',
                overflow: 'auto',
                maxHeight: 200,
              }}
            >
              <Typography variant="subtitle2" color="error" gutterBottom>
                {error?.toString()}
              </Typography>
              <Typography
                variant="caption"
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {errorInfo?.componentStack}
              </Typography>
            </Box>
          )}
          <Box sx={{ mt: 4 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<RefreshIcon />}
              onClick={onReset}
              sx={{ mr: 2 }}
            >
              Try Again
            </Button>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default ErrorBoundary; 