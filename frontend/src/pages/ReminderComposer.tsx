import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  useTheme,
  Grid,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Send as SendIcon,
  Language as LanguageIcon,
  Schedule as ScheduleIcon,
  Phone as PhoneIcon,
  WhatsApp as WhatsAppIcon,
  Sms as SmsIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import BloomLayout from '@components/layout/BloomLayout';
import BloomCard from '@components/common/BloomCard';

interface Template {
  id: string;
  name: string;
  content: {
    en: string;
    sw: string;
  };
  type: 'vaccination' | 'checkup' | 'milestone';
  channels: ('sms' | 'whatsapp' | 'voice')[];
  daysBefore: number;
  retryEnabled: boolean;
  retryCount: number;
  retryInterval: number;
}

const mockTemplates: Template[] = [
  {
    id: '1',
    name: 'Vaccination Reminder',
    content: {
      en: 'Dear {caregiver}, this is a reminder for {child}\'s {vaccine} vaccination on {date}. Please confirm your attendance.',
      sw: 'Mpendwa {caregiver}, hii ni kumbusho kwa {child} kwa chanjo ya {vaccine} tarehe {date}. Tafadhali thibitisha uwepo wako.',
    },
    type: 'vaccination',
    channels: ['sms', 'whatsapp'],
    daysBefore: 3,
    retryEnabled: true,
    retryCount: 3,
    retryInterval: 24,
  },
];

const ReminderComposer: React.FC = () => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const [templates] = useState<Template[]>(mockTemplates);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [previewLanguage, setPreviewLanguage] = useState<'en' | 'sw'>('en');

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
  };

  const renderChannelIcon = (channel: string) => {
    switch (channel) {
      case 'sms':
        return <SmsIcon />;
      case 'whatsapp':
        return <WhatsAppIcon />;
      case 'voice':
        return <PhoneIcon />;
      default:
        return null;
    }
  };

  return (
    <BloomLayout title={t('Reminder Composer')}>
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Template List */}
          <Grid item xs={12} md={4}>
            <BloomCard title={t('Templates')}>
              <List>
                {templates.map((template) => (
                  <ListItem
                    key={template.id}
                    button
                    selected={selectedTemplate?.id === template.id}
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <ListItemText
                      primary={template.name}
                      secondary={`${template.daysBefore} ${t('days before')}`}
                    />
                  </ListItem>
                ))}
              </List>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AddIcon />}
                sx={{ mt: 2, borderRadius: '2rem' }}
              >
                {t('New Template')}
              </Button>
            </BloomCard>
          </Grid>

          {/* Template Editor */}
          <Grid item xs={12} md={8}>
            {selectedTemplate ? (
              <BloomCard>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    {selectedTemplate.name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    {selectedTemplate.channels.map((channel) => (
                      <Chip
                        key={channel}
                        icon={renderChannelIcon(channel)}
                        label={t(channel)}
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>

                {/* Content Editor */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1">{t('Message Content')}</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        startIcon={<LanguageIcon />}
                        onClick={() => setPreviewLanguage('en')}
                        variant={previewLanguage === 'en' ? 'contained' : 'outlined'}
                      >
                        EN
                      </Button>
                      <Button
                        size="small"
                        startIcon={<LanguageIcon />}
                        onClick={() => setPreviewLanguage('sw')}
                        variant={previewLanguage === 'sw' ? 'contained' : 'outlined'}
                      >
                        SW
                      </Button>
                    </Box>
                  </Box>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={selectedTemplate.content[previewLanguage]}
                    variant="outlined"
                  />
                </Box>

                {/* Delivery Settings */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {t('Delivery Settings')}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>{t('Days Before')}</InputLabel>
                        <Select
                          value={selectedTemplate.daysBefore}
                          label={t('Days Before')}
                        >
                          <MenuItem value={1}>1 {t('day')}</MenuItem>
                          <MenuItem value={2}>2 {t('days')}</MenuItem>
                          <MenuItem value={3}>3 {t('days')}</MenuItem>
                          <MenuItem value={7}>7 {t('days')}</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>{t('Type')}</InputLabel>
                        <Select value={selectedTemplate.type} label={t('Type')}>
                          <MenuItem value="vaccination">{t('Vaccination')}</MenuItem>
                          <MenuItem value="checkup">{t('Check-up')}</MenuItem>
                          <MenuItem value="milestone">{t('Milestone')}</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Box>

                {/* Retry Settings */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {t('Retry Settings')}
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={selectedTemplate.retryEnabled}
                        color="primary"
                      />
                    }
                    label={t('Enable Retry')}
                  />
                  {selectedTemplate.retryEnabled && (
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          type="number"
                          label={t('Retry Count')}
                          value={selectedTemplate.retryCount}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          type="number"
                          label={t('Retry Interval (hours)')}
                          value={selectedTemplate.retryInterval}
                        />
                      </Grid>
                    </Grid>
                  )}
                </Box>

                {/* Actions */}
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<ScheduleIcon />}
                    sx={{ borderRadius: '2rem' }}
                  >
                    {t('Schedule')}
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<SendIcon />}
                    sx={{ borderRadius: '2rem' }}
                  >
                    {t('Send Now')}
                  </Button>
                </Box>
              </BloomCard>
            ) : (
              <BloomCard>
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    py: 4,
                  }}
                >
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    {t('Select a Template')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('Choose a template from the list to start editing')}
                  </Typography>
                </Box>
              </BloomCard>
            )}
          </Grid>
        </Grid>
      </Box>
    </BloomLayout>
  );
};

export default ReminderComposer; 