import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Paper,
  Button,
  useTheme,
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  Image as ImageIcon,
  EmojiEmotions as EmojiIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import BloomLayout from '@components/layout/BloomLayout';

interface Message {
  id: string;
  type: 'text' | 'reminder' | 'milestone';
  content: string;
  timestamp: string;
  sender: 'system' | 'caregiver';
  status?: 'sent' | 'delivered' | 'read';
}

interface Reminder {
  id: string;
  title: string;
  date: string;
  type: 'vaccination' | 'checkup' | 'milestone';
  status: 'pending' | 'confirmed' | 'rescheduled';
}

const mockMessages: Message[] = [
  {
    id: '1',
    type: 'reminder',
    content: 'Upcoming vaccination appointment for John on February 20th at 10:00 AM',
    timestamp: '2024-02-15T10:00:00',
    sender: 'system',
  },
  {
    id: '2',
    type: 'text',
    content: 'Thank you for the reminder. I will be there.',
    timestamp: '2024-02-15T10:05:00',
    sender: 'caregiver',
    status: 'read',
  },
  {
    id: '3',
    type: 'milestone',
    content: '🎉 John has reached a new milestone: First Steps!',
    timestamp: '2024-02-16T15:30:00',
    sender: 'system',
  },
];

const mockReminders: Reminder[] = [
  {
    id: '1',
    title: 'BCG Vaccination',
    date: '2024-02-20T10:00:00',
    type: 'vaccination',
    status: 'confirmed',
  },
  {
    id: '2',
    title: '6-Month Checkup',
    date: '2024-03-15T14:30:00',
    type: 'checkup',
    status: 'pending',
  },
];

const CaregiverChat: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [messages] = useState<Message[]>(mockMessages);
  const [reminders] = useState<Reminder[]>(mockReminders);
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      // Handle sending message
      setNewMessage('');
    }
  };

  const handleVoiceNote = () => {
    // Handle voice note recording
  };

  const renderMessage = (message: Message) => {
    const isSystem = message.sender === 'system';

    return (
      <Box
        key={message.id}
        sx={{
          display: 'flex',
          justifyContent: isSystem ? 'flex-start' : 'flex-end',
          mb: 2,
        }}
      >
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '70%',
            borderRadius: '1rem',
            backgroundColor: isSystem ? theme.palette.background.paper : theme.palette.primary.main,
            color: isSystem ? theme.palette.text.primary : theme.palette.common.white,
          }}
        >
          {message.type === 'reminder' && (
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <ScheduleIcon sx={{ mr: 1 }} />
              <Typography variant="subtitle2">{t('Reminder')}</Typography>
            </Box>
          )}
          {message.type === 'milestone' && (
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircleIcon sx={{ mr: 1 }} />
              <Typography variant="subtitle2">{t('Milestone')}</Typography>
            </Box>
          )}
          <Typography variant="body1">{message.content}</Typography>
          <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </Typography>
        </Paper>
      </Box>
    );
  };

  return (
    <BloomLayout title={t('Chat with Caregiver')}>
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box
          sx={{
            p: 2,
            borderBottom: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar
              sx={{
                width: 40,
                height: 40,
                mr: 2,
                backgroundColor: theme.palette.primary.main,
              }}
            >
              M
            </Avatar>
            <Box>
              <Typography variant="subtitle1">Mary Doe</Typography>
              <Typography variant="caption" color="text.secondary">
                {t('Mother of John')}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Messages */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 2,
            backgroundColor: theme.palette.grey[50],
          }}
        >
          {messages.map(renderMessage)}
        </Box>

        {/* Input */}
        <Box
          sx={{
            p: 2,
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton onClick={handleVoiceNote}>
              <MicIcon />
            </IconButton>
            <TextField
              fullWidth
              variant="outlined"
              placeholder={t('Type a message...')}
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '2rem',
                },
              }}
            />
            <IconButton>
              <EmojiIcon />
            </IconButton>
            <IconButton>
              <ImageIcon />
            </IconButton>
            <IconButton
              onClick={handleSendMessage}
              sx={{
                backgroundColor: theme.palette.primary.main,
                color: theme.palette.common.white,
                '&:hover': {
                  backgroundColor: theme.palette.primary.dark,
                },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Box>
    </BloomLayout>
  );
};

export default CaregiverChat; 