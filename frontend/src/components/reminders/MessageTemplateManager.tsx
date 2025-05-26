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
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  WhatsApp as WhatsAppIcon,
  Sms as SmsIcon,
  Phone as PhoneIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { communicationService, MessageTemplate } from '../../services/communicationService';
import { useNotification } from '../NotificationSystem';

const MessageTemplateManager: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { showNotification } = useNotification();
  const [templates, setTemplates] = useState<MessageTemplate[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<MessageTemplate | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    content: '',
    type: 'whatsapp' as const,
    language: 'en',
    variables: [] as string[],
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    const loadedTemplates = await communicationService.getTemplates();
    setTemplates(loadedTemplates);
  };

  const handleOpenDialog = (template?: MessageTemplate) => {
    if (template) {
      setSelectedTemplate(template);
      setFormData({
        name: template.name,
        content: template.content,
        type: template.type,
        language: template.language,
        variables: template.variables,
      });
    } else {
      setSelectedTemplate(null);
      setFormData({
        name: '',
        content: '',
        type: 'whatsapp',
        language: 'en',
        variables: [],
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedTemplate(null);
  };

  const handleSubmit = async () => {
    try {
      if (selectedTemplate) {
        // Update existing template
        const updated = await communicationService.createTemplate({
          ...formData,
          id: selectedTemplate.id,
        });
        if (updated) {
          showNotification(t('templates.updateSuccess'), 'success');
          loadTemplates();
        }
      } else {
        // Create new template
        const created = await communicationService.createTemplate(formData);
        if (created) {
          showNotification(t('templates.createSuccess'), 'success');
          loadTemplates();
        }
      }
      handleCloseDialog();
    } catch (error) {
      showNotification(t('templates.error'), 'error');
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
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5">{t('templates.title')}</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('templates.addNew')}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {templates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">{template.name}</Typography>
                  <Box>
                    <IconButton onClick={() => handleOpenDialog(template)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {getChannelIcon(template.type)}
                  <Chip
                    label={t(`channels.${template.type}`)}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                  <Chip
                    label={template.language}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {template.content}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {template.variables.map((variable) => (
                    <Chip
                      key={variable}
                      label={variable}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTemplate ? t('templates.edit') : t('templates.create')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('templates.name')}
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>{t('templates.type')}</InputLabel>
                  <Select
                    value={formData.type}
                    label={t('templates.type')}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                  >
                    <MenuItem value="whatsapp">WhatsApp</MenuItem>
                    <MenuItem value="sms">SMS</MenuItem>
                    <MenuItem value="voice">Voice</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>{t('templates.language')}</InputLabel>
                  <Select
                    value={formData.language}
                    label={t('templates.language')}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="sw">Swahili</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label={t('templates.content')}
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  helperText={t('templates.variablesHelp')}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{t('common.cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedTemplate ? t('common.update') : t('common.create')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MessageTemplateManager; 