import React from 'react';
import { Snackbar, Alert, AlertColor, Box } from '@mui/material';
import { createContext, useContext, useState, useCallback } from 'react';

interface NotificationContextType {
  showNotification: (message: string, severity?: AlertColor) => void;
  hideNotification: () => void;
}

const NotificationContext = createContext<NotificationContextType>({
  showNotification: () => {},
  hideNotification: () => {},
});

export const useNotification = () => useContext(NotificationContext);

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState<AlertColor>('info');

  const showNotification = useCallback((message: string, severity: AlertColor = 'info') => {
    setMessage(message);
    setSeverity(severity);
    setOpen(true);
  }, []);

  const hideNotification = useCallback(() => {
    setOpen(false);
  }, []);

  return (
    <NotificationContext.Provider value={{ showNotification, hideNotification }}>
      {children}
      <Box
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 2000,
        }}
      >
        <Snackbar
          open={open}
          autoHideDuration={6000}
          onClose={hideNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={hideNotification}
            severity={severity}
            variant="filled"
            sx={{
              width: '100%',
              boxShadow: 3,
              '& .MuiAlert-icon': {
                fontSize: 24,
              },
            }}
          >
            {message}
          </Alert>
        </Snackbar>
      </Box>
    </NotificationContext.Provider>
  );
};

// Toast notification component for quick notifications
export const Toast: React.FC<{
  message: string;
  severity?: AlertColor;
  onClose: () => void;
}> = ({ message, severity = 'info', onClose }) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 2000,
      }}
    >
      <Snackbar
        open={true}
        autoHideDuration={3000}
        onClose={onClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={onClose}
          severity={severity}
          variant="filled"
          sx={{
            width: '100%',
            boxShadow: 3,
            '& .MuiAlert-icon': {
              fontSize: 24,
            },
          }}
        >
          {message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

// Global notification component for important messages
export const GlobalNotification: React.FC<{
  message: string;
  severity?: AlertColor;
  onClose: () => void;
}> = ({ message, severity = 'info', onClose }) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 24,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 2000,
        width: '100%',
        maxWidth: 600,
        px: 2,
      }}
    >
      <Alert
        onClose={onClose}
        severity={severity}
        variant="filled"
        sx={{
          width: '100%',
          boxShadow: 3,
          '& .MuiAlert-icon': {
            fontSize: 24,
          },
        }}
      >
        {message}
      </Alert>
    </Box>
  );
};

export default NotificationProvider; 