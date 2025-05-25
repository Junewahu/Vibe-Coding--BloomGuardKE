import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  useTheme,
  IconButton,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Language as LanguageIcon,
  QrCode as QrCodeIcon,
  Verified as VerifiedIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import BloomLayout from '@components/layout/BloomLayout';
import BloomCard from '@components/common/BloomCard';

interface Vaccination {
  id: string;
  name: string;
  date: string;
  batchNumber: string;
  administeredBy: string;
  facility: string;
  verified: boolean;
}

const mockVaccinations: Vaccination[] = [
  {
    id: '1',
    name: 'BCG',
    date: '2024-01-15',
    batchNumber: 'BCG-2024-001',
    administeredBy: 'Dr. Jane Smith',
    facility: 'BloomGuard Clinic, Nairobi',
    verified: true,
  },
  {
    id: '2',
    name: 'Polio',
    date: '2024-02-01',
    batchNumber: 'POL-2024-002',
    administeredBy: 'Dr. John Doe',
    facility: 'BloomGuard Clinic, Nairobi',
    verified: true,
  },
];

const VaccinationCertificate: React.FC = () => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const [vaccinations] = useState<Vaccination[]>(mockVaccinations);
  const [language, setLanguage] = useState<'en' | 'sw'>('en');

  const handleLanguageChange = () => {
    setLanguage(language === 'en' ? 'sw' : 'en');
  };

  const handleDownload = () => {
    // Handle certificate download
  };

  return (
    <BloomLayout title={t('Vaccination Certificate')}>
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Certificate */}
          <Grid item xs={12} md={8}>
            <Paper
              elevation={3}
              sx={{
                p: 4,
                borderRadius: '2xl',
                backgroundColor: theme.palette.background.paper,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Header */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
                <Box>
                  <Typography variant="h4" gutterBottom>
                    {t('Vaccination Certificate')}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    {t('BloomGuard Health System')}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <IconButton onClick={handleLanguageChange}>
                    <LanguageIcon />
                  </IconButton>
                  <IconButton onClick={handleDownload}>
                    <DownloadIcon />
                  </IconButton>
                </Box>
              </Box>

              {/* Patient Info */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  {t('Patient Information')}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('Name')}
                    </Typography>
                    <Typography variant="body1">John Doe</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('Date of Birth')}
                    </Typography>
                    <Typography variant="body1">January 1, 2022</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('ID Number')}
                    </Typography>
                    <Typography variant="body1">BG-2022-001</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('Facility')}
                    </Typography>
                    <Typography variant="body1">BloomGuard Clinic, Nairobi</Typography>
                  </Grid>
                </Grid>
              </Box>

              {/* Vaccination History */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  {t('Vaccination History')}
                </Typography>
                {vaccinations.map((vaccination) => (
                  <Box
                    key={vaccination.id}
                    sx={{
                      p: 2,
                      mb: 2,
                      borderRadius: '1rem',
                      backgroundColor: theme.palette.grey[50],
                    }}
                  >
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle1">{vaccination.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(vaccination.date).toLocaleDateString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <VerifiedIcon
                            sx={{
                              color: vaccination.verified
                                ? theme.palette.status.success
                                : theme.palette.status.error,
                            }}
                          />
                          <Typography variant="body2">
                            {vaccination.verified
                              ? t('Verified')
                              : t('Pending Verification')}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">
                          {t('Batch Number')}: {vaccination.batchNumber}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {t('Administered by')}: {vaccination.administeredBy}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                ))}
              </Box>

              {/* QR Code */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  mt: 4,
                }}
              >
                <Box
                  sx={{
                    p: 2,
                    borderRadius: '1rem',
                    backgroundColor: theme.palette.common.white,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  }}
                >
                  <QrCodeIcon sx={{ fontSize: 200, color: theme.palette.primary.main }} />
                </Box>
              </Box>
            </Paper>
          </Grid>

          {/* Verification Info */}
          <Grid item xs={12} md={4}>
            <BloomCard title={t('Certificate Verification')}>
              <Typography variant="body1" paragraph>
                {t(
                  'This digital certificate is issued by BloomGuard Health System and can be verified using the QR code.'
                )}
              </Typography>
              <Button
                fullWidth
                variant="contained"
                startIcon={<VerifiedIcon />}
                sx={{ borderRadius: '2rem' }}
              >
                {t('Verify Certificate')}
              </Button>
            </BloomCard>

            <BloomCard title={t('Download Options')} sx={{ mt: 3 }}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<DownloadIcon />}
                sx={{ mb: 2, borderRadius: '2rem' }}
              >
                {t('Download PDF')}
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<DownloadIcon />}
                sx={{ borderRadius: '2rem' }}
              >
                {t('Download Image')}
              </Button>
            </BloomCard>
          </Grid>
        </Grid>
      </Box>
    </BloomLayout>
  );
};

export default VaccinationCertificate; 