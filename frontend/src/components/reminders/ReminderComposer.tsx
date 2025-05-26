import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  Grid,
  FormControlLabel,
  Switch,
  Slider,
  FormGroup,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  WhatsApp as WhatsAppIcon,
  Sms as SmsIcon,
  Phone as PhoneIcon,
  Language as LanguageIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';

interface ReminderTemplate {
  title: string;
  content: {
    [key: string]: string; // language code -> content
  };
  deliveryChannels: string[];
  scheduling: {
    sendNow: boolean;
    scheduledDate?: string;
  };
  retrySettings: {
    maxRetries: number;
    retryInterval: number;
  };
  reminderType: 'vaccination' | 'checkup' | 'followup' | 'custom';
  priority: 'high' | 'medium' | 'low';
}

interface ReminderComposerProps {
  onSave: (template: ReminderTemplate) => void;
  onSend: (template: ReminderTemplate) => void;
  supportedLanguages: string[];
}

const ReminderComposer: React.FC<ReminderComposerProps> = ({
  onSave,
  onSend,
  supportedLanguages,
}) => {
  const { t } = useTranslation(['reminders', 'common']);
  const theme = useTheme();

  const [template, setTemplate] = useState<ReminderTemplate>({
    title: '',
    content: {},
    deliveryChannels: [],
    scheduling: {
      sendNow: true,
    },
    retrySettings: {
      maxRetries: 3,
      retryInterval: 24,
    },
    reminderType: 'vaccination',
    priority: 'medium',
  });

  const handleContentChange = (language: string, value: string) => {
    setTemplate((prev) => ({
      ...prev,
      content: {
        ...prev.content,
        [language]: value,
      },
    }));
  };

  const toggleDeliveryChannel = (channel: string) => {
    setTemplate((prev) => ({
      ...prev,
      deliveryChannels: prev.deliveryChannels.includes(channel)
        ? prev.deliveryChannels.filter((c) => c !== channel)
        : [...prev.deliveryChannels, channel],
    }));
  };

  return (
    <Card sx={{ p: 3 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          {t('title')}
        </Typography>

        {/* Basic Information */}
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label={t('reminderTitle')}
              value={template.title}
              onChange={(e) =>
                setTemplate((prev) => ({ ...prev, title: e.target.value }))
              }
            />
          </Grid>

          {/* Reminder Type and Priority */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>{t('reminderType')}</InputLabel>
              <Select
                value={template.reminderType}
                onChange={(e) =>
                  setTemplate((prev) => ({
                    ...prev,
                    reminderType: e.target.value as ReminderTemplate['reminderType'],
                  }))
                }
              >
                <MenuItem value="vaccination">{t('vaccination')}</MenuItem>
                <MenuItem value="checkup">{t('checkup')}</MenuItem>
                <MenuItem value="followup">{t('followup')}</MenuItem>
                <MenuItem value="custom">{t('custom')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>{t('priority')}</InputLabel>
              <Select
                value={template.priority}
                onChange={(e) =>
                  setTemplate((prev) => ({
                    ...prev,
                    priority: e.target.value as ReminderTemplate['priority'],
                  }))
                }
              >
                <MenuItem value="high">{t('high')}</MenuItem>
                <MenuItem value="medium">{t('medium')}</MenuItem>
                <MenuItem value="low">{t('low')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Multilingual Content */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('reminderContent')}
          </Typography>
          {supportedLanguages.map((lang) => (
            <TextField
              key={lang}
              fullWidth
              multiline
              rows={4}
              label={`${t('reminderContent')} (${lang})`}
              value={template.content[lang] || ''}
              onChange={(e) => handleContentChange(lang, e.target.value)}
              sx={{ mb: 2 }}
            />
          ))}
        </Box>

        {/* Delivery Channels */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('deliveryChannels')}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              icon={<WhatsAppIcon />}
              label={t('whatsapp')}
              onClick={() => toggleDeliveryChannel('whatsapp')}
              color={
                template.deliveryChannels.includes('whatsapp')
                  ? 'primary'
                  : 'default'
              }
            />
            <Chip
              icon={<SmsIcon />}
              label={t('sms')}
              onClick={() => toggleDeliveryChannel('sms')}
              color={
                template.deliveryChannels.includes('sms')
                  ? 'primary'
                  : 'default'
              }
            />
            <Chip
              icon={<PhoneIcon />}
              label={t('voice')}
              onClick={() => toggleDeliveryChannel('voice')}
              color={
                template.deliveryChannels.includes('voice')
                  ? 'primary'
                  : 'default'
              }
            />
          </Box>
        </Box>

        {/* Scheduling */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('scheduling')}
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={template.scheduling.sendNow}
                onChange={(e) =>
                  setTemplate((prev) => ({
                    ...prev,
                    scheduling: {
                      ...prev.scheduling,
                      sendNow: e.target.checked,
                    },
                  }))
                }
              />
            }
            label={t('sendNow')}
          />
          {!template.scheduling.sendNow && (
            <TextField
              type="datetime-local"
              fullWidth
              value={template.scheduling.scheduledDate}
              onChange={(e) =>
                setTemplate((prev) => ({
                  ...prev,
                  scheduling: {
                    ...prev.scheduling,
                    scheduledDate: e.target.value,
                  },
                }))
              }
              sx={{ mt: 2 }}
            />
          )}
        </Box>

        {/* Retry Settings */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('retrySettings')}
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>{t('maxRetries')}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton
                  onClick={() =>
                    setTemplate((prev) => ({
                      ...prev,
                      retrySettings: {
                        ...prev.retrySettings,
                        maxRetries: Math.max(0, prev.retrySettings.maxRetries - 1),
                      },
                    }))
                  }
                >
                  <RemoveIcon />
                </IconButton>
                <Typography>{template.retrySettings.maxRetries}</Typography>
                <IconButton
                  onClick={() =>
                    setTemplate((prev) => ({
                      ...prev,
                      retrySettings: {
                        ...prev.retrySettings,
                        maxRetries: prev.retrySettings.maxRetries + 1,
                      },
                    }))
                  }
                >
                  <AddIcon />
                </IconButton>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>{t('retryInterval')}</Typography>
              <Slider
                value={template.retrySettings.retryInterval}
                onChange={(_, value) =>
                  setTemplate((prev) => ({
                    ...prev,
                    retrySettings: {
                      ...prev.retrySettings,
                      retryInterval: value as number,
                    },
                  }))
                }
                min={1}
                max={72}
                valueLabelDisplay="auto"
              />
            </Grid>
          </Grid>
        </Box>

        {/* Actions */}
        <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={() => onSave(template)}
          >
            {t('saveTemplate')}
          </Button>
          <Button
            variant="contained"
            onClick={() => onSend(template)}
            disabled={template.deliveryChannels.length === 0}
          >
            {template.scheduling.sendNow
              ? t('sendReminder')
              : t('scheduleReminder')}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ReminderComposer; 