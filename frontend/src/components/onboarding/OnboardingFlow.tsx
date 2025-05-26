import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
} from '@mui/material';
import {
  Business,
  People,
  Settings,
  CheckCircle,
  WhatsApp,
  Sms,
  Phone,
  Payment,
} from '@mui/icons-material';
import theme from '../../theme';
import { StaffMemberForm } from './StaffMemberForm';

interface OnboardingStep {
  label: string;
  icon: React.ReactNode;
}

interface ClinicInfo {
  name: string;
  address: string;
  phone: string;
  email: string;
  nhifNumber?: string;
}

interface StaffMember {
  name: string;
  role: string;
  email: string;
  phone: string;
}

interface ApiConfig {
  whatsapp: boolean;
  sms: boolean;
  voice: boolean;
  nhif: boolean;
  apiKeys: {
    [key: string]: string;
  };
}

interface OnboardingFlowProps {
  onComplete: (data: {
    clinicInfo: ClinicInfo;
    staff: StaffMember[];
    apiConfig: ApiConfig;
  }) => void;
}

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const { t } = useTranslation();
  const [activeStep, setActiveStep] = useState(0);
  const [clinicInfo, setClinicInfo] = useState<ClinicInfo>({
    name: '',
    address: '',
    phone: '',
    email: '',
  });
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [apiConfig, setApiConfig] = useState<ApiConfig>({
    whatsapp: true,
    sms: false,
    voice: false,
    nhif: false,
    apiKeys: {},
  });
  const [isStaffFormOpen, setIsStaffFormOpen] = useState(false);

  const steps: OnboardingStep[] = [
    { label: t('onboarding.clinicInfo'), icon: <Business /> },
    { label: t('onboarding.staffSetup'), icon: <People /> },
    { label: t('onboarding.apiConfig'), icon: <Settings /> },
    { label: t('onboarding.complete'), icon: <CheckCircle /> },
  ];

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      onComplete({ clinicInfo, staff, apiConfig });
    } else {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleClinicInfoChange = (field: keyof ClinicInfo, value: string) => {
    setClinicInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleStaffAdd = (member: StaffMember) => {
    setStaff(prev => [...prev, member]);
  };

  const handleApiToggle = (service: keyof Omit<ApiConfig, 'apiKeys'>) => {
    setApiConfig(prev => ({
      ...prev,
      [service]: !prev[service],
    }));
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Stack spacing={3}>
            <TextField
              label={t('onboarding.clinicName')}
              value={clinicInfo.name}
              onChange={e => handleClinicInfoChange('name', e.target.value)}
              fullWidth
            />
            <TextField
              label={t('onboarding.address')}
              value={clinicInfo.address}
              onChange={e => handleClinicInfoChange('address', e.target.value)}
              fullWidth
            />
            <TextField
              label={t('onboarding.phone')}
              value={clinicInfo.phone}
              onChange={e => handleClinicInfoChange('phone', e.target.value)}
              fullWidth
            />
            <TextField
              label={t('onboarding.email')}
              value={clinicInfo.email}
              onChange={e => handleClinicInfoChange('email', e.target.value)}
              fullWidth
            />
            <TextField
              label={t('onboarding.nhifNumber')}
              value={clinicInfo.nhifNumber}
              onChange={e => handleClinicInfoChange('nhifNumber', e.target.value)}
              fullWidth
            />
          </Stack>
        );

      case 1:
        return (
          <Stack spacing={3}>
            {staff.map((member, index) => (
              <Card key={index} sx={{ p: 2 }}>
                <Stack spacing={2}>
                  <Typography variant="subtitle1">{member.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t(`roles.${member.role}`)}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Typography variant="body2" color="text.secondary">
                      {member.email}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      •
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {member.phone}
                    </Typography>
                  </Stack>
                </Stack>
              </Card>
            ))}
            <Button
              variant="outlined"
              startIcon={<People />}
              onClick={() => setIsStaffFormOpen(true)}
            >
              {t('onboarding.addStaff')}
            </Button>
            <StaffMemberForm
              open={isStaffFormOpen}
              onClose={() => setIsStaffFormOpen(false)}
              onSubmit={handleStaffAdd}
            />
          </Stack>
        );

      case 2:
        return (
          <Stack spacing={3}>
            <Typography variant="h6" gutterBottom>
              {t('onboarding.communicationChannels')}
            </Typography>
            <Stack direction="row" spacing={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={apiConfig.whatsapp}
                    onChange={() => handleApiToggle('whatsapp')}
                  />
                }
                label={
                  <Stack direction="row" spacing={1} alignItems="center">
                    <WhatsApp />
                    <Typography>WhatsApp</Typography>
                  </Stack>
                }
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={apiConfig.sms}
                    onChange={() => handleApiToggle('sms')}
                  />
                }
                label={
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Sms />
                    <Typography>SMS</Typography>
                  </Stack>
                }
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={apiConfig.voice}
                    onChange={() => handleApiToggle('voice')}
                  />
                }
                label={
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Phone />
                    <Typography>Voice</Typography>
                  </Stack>
                }
              />
            </Stack>

            <Typography variant="h6" gutterBottom>
              {t('onboarding.integrations')}
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={apiConfig.nhif}
                  onChange={() => handleApiToggle('nhif')}
                />
              }
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <Payment />
                  <Typography>NHIF Integration</Typography>
                </Stack>
              }
            />

            {Object.entries(apiConfig.apiKeys).map(([service, key]) => (
              <TextField
                key={service}
                label={t(`onboarding.apiKey.${service}`)}
                value={key}
                onChange={e =>
                  setApiConfig(prev => ({
                    ...prev,
                    apiKeys: { ...prev.apiKeys, [service]: e.target.value },
                  }))
                }
                fullWidth
              />
            ))}
          </Stack>
        );

      case 3:
        return (
          <Stack spacing={3} alignItems="center">
            <CheckCircle color="success" sx={{ fontSize: 64 }} />
            <Typography variant="h5" align="center">
              {t('onboarding.setupComplete')}
            </Typography>
            <Typography color="text.secondary" align="center">
              {t('onboarding.setupCompleteMessage')}
            </Typography>
          </Stack>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Card sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((step, index) => (
            <Step key={index}>
              <StepLabel icon={step.icon}>{step.label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mt: 4 }}>{renderStepContent()}</Box>

        <Stack direction="row" spacing={2} justifyContent="flex-end" sx={{ mt: 4 }}>
          {activeStep > 0 && (
            <Button onClick={handleBack}>
              {t('common.back')}
            </Button>
          )}
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={
              (activeStep === 0 && !clinicInfo.name) ||
              (activeStep === 1 && staff.length === 0)
            }
          >
            {activeStep === steps.length - 1
              ? t('common.finish')
              : t('common.next')}
          </Button>
        </Stack>
      </Card>
    </Box>
  );
}; 