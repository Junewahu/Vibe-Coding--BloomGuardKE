import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  WhatsApp as WhatsAppIcon,
  Sms as SmsIcon,
  Phone as PhoneIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { communicationService, MessageTemplate } from '../../services/communicationService';
import { useNotification } from '../NotificationSystem';

interface MessageSenderProps {
  patientPhone: string;
  patientName: string;
  onMessageSent?: (messageId: string) => void;
}

const MessageSender: React.FC<MessageSenderProps> = ({
  patientPhone,
  patientName,
  onMessageSent,
}) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { showNotification } = useNotification();
  const [templates, setTemplates] = useState<MessageTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<MessageTemplate | null>(null);
  const [loading, setLoading] = useState(false);
  const [variables, setVariables] = useState<Record<string, string>>({});

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    if (selectedTemplate) {
      const initialVariables: Record<string, string> = {};
      selectedTemplate.variables.forEach((variable) => {
        if (variable === 'patientName') {
          initialVariables[variable] = patientName;
        } else {
          initialVariables[variable] = '';
        }
      });
      setVariables(initialVariables);
    }
  }, [selectedTemplate, patientName]);

  const loadTemplates = async () => {
    const loadedTemplates = await communicationService.getTemplates();
    setTemplates(loadedTemplates);
  };

  const handleTemplateChange = (templateId: string) => {
    const template = templates.find((t) => t.id === templateId);
    setSelectedTemplate(template || null);
  };

  const handleVariableChange = (variable: string, value: string) => {
    setVariables((prev) => ({
      ...prev,
      [variable]: value,
    }));
  };

  const handleSend = async () => {
    if (!selectedTemplate) return;

    setLoading(true);
    try {
      const result = await communicationService.sendMessage({
        recipient: patientPhone,
        templateId: selectedTemplate.id,
        variables,
        channel: selectedTemplate.type,
        language: selectedTemplate.language,
      });

      if (result.success && result.messageId) {
        showNotification(t('messages.sendSuccess'), 'success');
        onMessageSent?.(result.messageId);
      } else {
        showNotification(result.error || t('messages.sendError'), 'error');
      }
    } catch (error) {
      showNotification(t('messages.sendError'), 'error');
    } finally {
      setLoading(false);
    }
  };

  const getChannelIcon = (type: string) => {
    switch (type) {
      case 'whatsapp':
        return <WhatsAppIcon />;
      case 'sms':
        return <SmsIcon />;
      case 'voice':
        return <PhoneIcon />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {t('messages.sendTitle')}
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>{t('messages.selectTemplate')}</InputLabel>
              <Select
                value={selectedTemplate?.id || ''}
                label={t('messages.selectTemplate')}
                onChange={(e) => handleTemplateChange(e.target.value)}
              >
                {templates.map((template) => (
                  <MenuItem key={template.id} value={template.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {getChannelIcon(template.type)}
                      <Typography sx={{ ml: 1 }}>{template.name}</Typography>
                      <Chip
                        label={template.language}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {selectedTemplate && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('messages.templateContent')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedTemplate.content}
                </Typography>
              </Grid>

              {selectedTemplate.variables.map((variable) => (
                <Grid item xs={12} key={variable}>
                  <TextField
                    fullWidth
                    label={t(`variables.${variable}`)}
                    value={variables[variable] || ''}
                    onChange={(e) => handleVariableChange(variable, e.target.value)}
                    disabled={variable === 'patientName'}
                  />
                </Grid>
              ))}

              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                  onClick={handleSend}
                  disabled={loading}
                >
                  {t('messages.send')}
                </Button>
              </Grid>
            </>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default MessageSender; 