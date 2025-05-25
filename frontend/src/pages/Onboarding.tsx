import React, { useState } from 'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Paper,
  useTheme,
  FormControlLabel,
  Switch,
  Chip,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Phone as PhoneIcon,
  WhatsApp as WhatsAppIcon,
  Sms as SmsIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import BloomLayout from '@components/layout/BloomLayout';
import BloomCard from '@components/common/BloomCard';

interface ClinicInfo {
  name: string;
  address: string;
  phone: string;
  email: string;
  nhifNumber: string;
}

interface StaffMember {
  id: string;
  name: string;
  role: 'doctor' | 'nurse' | 'receptionist' | 'admin' | 'chw';
  email: string;
  phone: string;
}

interface Integration {
  id: string;
  name: string;
  enabled: boolean;
  type: 'sms' | 'whatsapp' | 'voice' | 'ussd';
}

const mockIntegrations: Integration[] = [
  {
    id: '1',
    name: 'SMS Gateway',
    enabled: true,
    type: 'sms',
  },
  {
    id: '2',
    name: 'WhatsApp Business API',
    enabled: true,
    type: 'whatsapp',
  },
  {
    id: '3',
    name: 'Voice Calls',
    enabled: false,
    type: 'voice',
  },
  {
    id: '4',
    name: 'USSD Service',
    enabled: false,
    type: 'ussd',
  },
];

const Onboarding: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [activeStep, setActiveStep] = useState(0);
  const [clinicInfo, setClinicInfo] = useState<ClinicInfo>({
    name: '',
    address: '',
    phone: '',
    email: '',
    nhifNumber: '',
  });
  const [staffMembers, setStaffMembers] = useState<StaffMember[]>([]);
  const [integrations] = useState<Integration[]>(mockIntegrations);

  const steps = [
    t('Clinic Information'),
    t('Staff Setup'),
    t('Integrations'),
    t('Theme & Preferences'),
  ];

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleClinicInfoChange = (field: keyof ClinicInfo) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setClinicInfo({
      ...clinicInfo,
      [field]: event.target.value,
    });
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <BloomCard>
            <Typography variant="h6" gutterBottom>
              {t('Clinic Information')}
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('Clinic Name')}
                  value={clinicInfo.name}
                  onChange={handleClinicInfoChange('name')}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('NHIF Number')}
                  value={clinicInfo.nhifNumber}
                  onChange={handleClinicInfoChange('nhifNumber')}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('Address')}
                  value={clinicInfo.address}
                  onChange={handleClinicInfoChange('address')}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('Phone')}
                  value={clinicInfo.phone}
                  onChange={handleClinicInfoChange('phone')}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('Email')}
                  type="email"
                  value={clinicInfo.email}
                  onChange={handleClinicInfoChange('email')}
                />
              </Grid>
            </Grid>
          </BloomCard>
        );

      case 1:
        return (
          <BloomCard>
            <Typography variant="h6" gutterBottom>
              {t('Staff Setup')}
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Button
                variant="outlined"
                startIcon={<PersonIcon />}
                sx={{ borderRadius: '2rem' }}
              >
                {t('Add Staff Member')}
              </Button>
            </Box>
            <Grid container spacing={2}>
              {staffMembers.map((staff) => (
                <Grid item xs={12} key={staff.id}>
                  <Paper
                    sx={{
                      p: 2,
                      borderRadius: '1rem',
                      backgroundColor: theme.palette.grey[50],
                    }}
                  >
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} sm={4}>
                        <Typography variant="subtitle1">{staff.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {t(staff.role)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">{staff.email}</Typography>
                        <Typography variant="body2">{staff.phone}</Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button size="small">{t('Edit')}</Button>
                          <Button size="small" color="error">
                            {t('Remove')}
                          </Button>
                        </Box>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </BloomCard>
        );

      case 2:
        return (
          <BloomCard>
            <Typography variant="h6" gutterBottom>
              {t('Integrations')}
            </Typography>
            <Grid container spacing={2}>
              {integrations.map((integration) => (
                <Grid item xs={12} sm={6} key={integration.id}>
                  <Paper
                    sx={{
                      p: 2,
                      borderRadius: '1rem',
                      backgroundColor: theme.palette.grey[50],
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Box>
                        <Typography variant="subtitle1">{integration.name}</Typography>
                        <Chip
                          size="small"
                          icon={
                            integration.type === 'sms' ? (
                              <SmsIcon />
                            ) : integration.type === 'whatsapp' ? (
                              <WhatsAppIcon />
                            ) : (
                              <PhoneIcon />
                            )
                          }
                          label={t(integration.type)}
                        />
                      </Box>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={integration.enabled}
                            color="primary"
                          />
                        }
                        label={t('Enabled')}
                      />
                    </Box>
                    <Button
                      fullWidth
                      variant="outlined"
                      size="small"
                      sx={{ borderRadius: '1rem' }}
                    >
                      {t('Configure')}
                    </Button>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </BloomCard>
        );

      case 3:
        return (
          <BloomCard>
            <Typography variant="h6" gutterBottom>
              {t('Theme & Preferences')}
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('Color Scheme')}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.primary.main,
                      cursor: 'pointer',
                    }}
                  />
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.secondary.main,
                      cursor: 'pointer',
                    }}
                  />
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.accent.main,
                      cursor: 'pointer',
                    }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('Language')}
                </Typography>
                <FormControl fullWidth>
                  <Select
                    value="en"
                    label={t('Language')}
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="sw">Kiswahili</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('Notifications')}
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label={t('Email Notifications')}
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label={t('SMS Notifications')}
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label={t('WhatsApp Notifications')}
                />
              </Grid>
            </Grid>
          </BloomCard>
        );

      default:
        return null;
    }
  };

  return (
    <BloomLayout title={t('Clinic Setup')}>
      <Box sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ borderRadius: '2rem' }}
          >
            {t('Back')}
          </Button>
          <Button
            variant="contained"
            onClick={handleNext}
            sx={{ borderRadius: '2rem' }}
          >
            {activeStep === steps.length - 1 ? t('Finish') : t('Next')}
          </Button>
        </Box>
      </Box>
    </BloomLayout>
  );
};

export default Onboarding; 