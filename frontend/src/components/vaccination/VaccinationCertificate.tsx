import React from 'react';
import { useTranslation } from 'react-i18next';
import { QRCodeSVG } from 'qrcode.react';
import { Box, Card, Typography, Button, Stack } from '@mui/material';
import { Download, Share, Verified } from '@mui/icons-material';
import { theme } from '../../theme';

interface VaccinationCertificateProps {
  patientName: string;
  dateOfBirth: string;
  vaccinations: Array<{
    name: string;
    date: string;
    batchNumber: string;
    administeredBy: string;
  }>;
  certificateId: string;
  issueDate: string;
  issuingFacility: string;
}

export const VaccinationCertificate: React.FC<VaccinationCertificateProps> = ({
  patientName,
  dateOfBirth,
  vaccinations,
  certificateId,
  issueDate,
  issuingFacility,
}) => {
  const { t, i18n } = useTranslation();

  const handleDownload = () => {
    // Implement PDF generation and download
  };

  const handleShare = () => {
    // Implement sharing functionality
  };

  return (
    <Card
      sx={{
        p: 3,
        maxWidth: 800,
        mx: 'auto',
        bgcolor: theme.palette.background.paper,
        borderRadius: 2,
        boxShadow: 3,
      }}
    >
      <Stack spacing={3}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Typography variant="h4" color="primary" gutterBottom>
            {t('vaccination.certificate.title')}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {t('vaccination.certificate.subtitle')}
          </Typography>
        </Box>

        {/* Patient Info */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Box>
            <Typography variant="h6">{patientName}</Typography>
            <Typography color="text.secondary">
              {t('vaccination.certificate.dob')}: {dateOfBirth}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="body2" color="text.secondary">
              {t('vaccination.certificate.id')}: {certificateId}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('vaccination.certificate.issueDate')}: {issueDate}
            </Typography>
          </Box>
        </Box>

        {/* Vaccination Records */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('vaccination.certificate.records')}
          </Typography>
          {vaccinations.map((vaccination, index) => (
            <Box
              key={index}
              sx={{
                p: 2,
                mb: 1,
                bgcolor: theme.palette.background.default,
                borderRadius: 1,
              }}
            >
              <Typography variant="subtitle1">{vaccination.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {t('vaccination.certificate.date')}: {vaccination.date}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('vaccination.certificate.batch')}: {vaccination.batchNumber}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('vaccination.certificate.administeredBy')}: {vaccination.administeredBy}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* QR Code */}
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <QRCodeSVG
            value={`https://bloomguard.ke/verify/${certificateId}`}
            size={200}
            level="H"
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {t('vaccination.certificate.scanToVerify')}
          </Typography>
        </Box>

        {/* Footer */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {t('vaccination.certificate.issuingFacility')}: {issuingFacility}
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 2 }}>
            <Button
              variant="contained"
              startIcon={<Download />}
              onClick={handleDownload}
            >
              {t('common.download')}
            </Button>
            <Button
              variant="outlined"
              startIcon={<Share />}
              onClick={handleShare}
            >
              {t('common.share')}
            </Button>
          </Stack>
        </Box>
      </Stack>
    </Card>
  );
}; 