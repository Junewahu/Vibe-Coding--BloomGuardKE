import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';

interface StaffMember {
  name: string;
  role: string;
  email: string;
  phone: string;
}

interface StaffMemberFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (member: StaffMember) => void;
}

const ROLES = [
  'admin',
  'doctor',
  'nurse',
  'receptionist',
  'pharmacist',
  'lab_technician',
  'chw',
];

export const StaffMemberForm: React.FC<StaffMemberFormProps> = ({
  open,
  onClose,
  onSubmit,
}) => {
  const { t } = useTranslation();
  const [member, setMember] = useState<StaffMember>({
    name: '',
    role: '',
    email: '',
    phone: '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof StaffMember, value: string) => {
    setMember(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleSubmit = () => {
    // Basic validation
    if (!member.name || !member.role || !member.email || !member.phone) {
      setError(t('onboarding.staffForm.validation.required'));
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(member.email)) {
      setError(t('onboarding.staffForm.validation.invalidEmail'));
      return;
    }

    // Phone validation (basic)
    const phoneRegex = /^\+?[\d\s-]{10,}$/;
    if (!phoneRegex.test(member.phone)) {
      setError(t('onboarding.staffForm.validation.invalidPhone'));
      return;
    }

    onSubmit(member);
    setMember({ name: '', role: '', email: '', phone: '' });
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{t('onboarding.staffForm.title')}</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 2 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <TextField
            label={t('onboarding.staffForm.name')}
            value={member.name}
            onChange={e => handleChange('name', e.target.value)}
            fullWidth
            required
          />

          <FormControl fullWidth required>
            <InputLabel>{t('onboarding.staffForm.role')}</InputLabel>
            <Select
              value={member.role}
              label={t('onboarding.staffForm.role')}
              onChange={e => handleChange('role', e.target.value)}
            >
              {ROLES.map(role => (
                <MenuItem key={role} value={role}>
                  {t(`roles.${role}`)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label={t('onboarding.staffForm.email')}
            type="email"
            value={member.email}
            onChange={e => handleChange('email', e.target.value)}
            fullWidth
            required
          />

          <TextField
            label={t('onboarding.staffForm.phone')}
            value={member.phone}
            onChange={e => handleChange('phone', e.target.value)}
            fullWidth
            required
            placeholder="+254..."
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('common.cancel')}</Button>
        <Button onClick={handleSubmit} variant="contained">
          {t('common.add')}
        </Button>
      </DialogActions>
    </Dialog>
  );
}; 