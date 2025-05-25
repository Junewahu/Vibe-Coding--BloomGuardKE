import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Download,
  Refresh,
  CalendarMonth,
  TrendingUp,
  People,
  LocalHospital,
  Inventory,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { theme as customTheme } from '../utils/theme';

// Placeholder data - replace with actual API calls
const mockReportData = {
  patientStats: {
    total: 1500,
    newThisMonth: 120,
    active: 980,
    inactive: 520,
  },
  appointmentStats: {
    total: 2500,
    completed: 2100,
    cancelled: 200,
    noShow: 200,
  },
  inventoryStats: {
    totalItems: 500,
    lowStock: 25,
    expiringSoon: 15,
    outOfStock: 5,
  },
  revenueStats: {
    total: 1500000,
    thisMonth: 150000,
    lastMonth: 140000,
    growth: 7.14,
  },
};

const timeRanges = [
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'quarter', label: 'This Quarter' },
  { value: 'year', label: 'This Year' },
];

const Reports: React.FC = () => {
  const { t } = useTranslation();
  const [selectedTimeRange, setSelectedTimeRange] = useState('month');

  const handleTimeRangeChange = (event: any) => {
    setSelectedTimeRange(event.target.value);
  };

  const handleRefresh = () => {
    // Implement refresh logic
  };

  const handleDownload = () => {
    // Implement download logic
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography
          variant="h4"
          sx={{
            color: customTheme.colors.deepNavy,
            fontFamily: customTheme.typography.fontFamily.secondary,
            fontWeight: customTheme.typography.fontWeight.bold,
          }}
        >
          {t('reports.title')}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>{t('reports.timeRange')}</InputLabel>
            <Select
              value={selectedTimeRange}
              label={t('reports.timeRange')}
              onChange={handleTimeRangeChange}
              sx={{
                borderRadius: customTheme.borderRadius.md,
              }}
            >
              {timeRanges.map((range) => (
                <MenuItem key={range.value} value={range.value}>
                  {range.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Tooltip title={t('reports.refresh')}>
            <IconButton
              onClick={handleRefresh}
              sx={{ color: customTheme.colors.deepNavy }}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleDownload}
            sx={{
              backgroundColor: customTheme.colors.babyBlue,
              color: customTheme.colors.deepNavy,
              '&:hover': {
                backgroundColor: customTheme.colors.skyBlue,
              },
              borderRadius: customTheme.borderRadius.md,
            }}
          >
            {t('reports.download')}
          </Button>
        </Box>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <People
                  sx={{
                    color: customTheme.colors.babyBlue,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('reports.totalPatients')}
                </Typography>
              </Box>
              <Typography variant="h4" sx={{ color: customTheme.colors.deepNavy }}>
                {mockReportData.patientStats.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('reports.newThisMonth')}: {mockReportData.patientStats.newThisMonth}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CalendarMonth
                  sx={{
                    color: customTheme.colors.lavender,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('reports.totalAppointments')}
                </Typography>
              </Box>
              <Typography variant="h4" sx={{ color: customTheme.colors.deepNavy }}>
                {mockReportData.appointmentStats.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('reports.completed')}: {mockReportData.appointmentStats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Inventory
                  sx={{
                    color: customTheme.colors.candyPink,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('reports.inventoryStatus')}
                </Typography>
              </Box>
              <Typography variant="h4" sx={{ color: customTheme.colors.deepNavy }}>
                {mockReportData.inventoryStats.totalItems}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('reports.lowStock')}: {mockReportData.inventoryStats.lowStock}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp
                  sx={{
                    color: customTheme.colors.skyBlue,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('reports.revenue')}
                </Typography>
              </Box>
              <Typography variant="h4" sx={{ color: customTheme.colors.deepNavy }}>
                ${mockReportData.revenueStats.thisMonth.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('reports.growth')}: {mockReportData.revenueStats.growth}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Reports */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 2,
                color: customTheme.colors.deepNavy,
                fontFamily: customTheme.typography.fontFamily.secondary,
              }}
            >
              {t('reports.patientDemographics')}
            </Typography>
            {/* Add Patient Demographics Chart Component Here */}
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: customTheme.colors.babyBlue + '20',
                borderRadius: customTheme.borderRadius.md,
              }}
            >
              <Typography color="text.secondary">
                {t('reports.chartPlaceholder')}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 2,
                color: customTheme.colors.deepNavy,
                fontFamily: customTheme.typography.fontFamily.secondary,
              }}
            >
              {t('reports.appointmentTrends')}
            </Typography>
            {/* Add Appointment Trends Chart Component Here */}
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: customTheme.colors.babyBlue + '20',
                borderRadius: customTheme.borderRadius.md,
              }}
            >
              <Typography color="text.secondary">
                {t('reports.chartPlaceholder')}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 2,
                color: customTheme.colors.deepNavy,
                fontFamily: customTheme.typography.fontFamily.secondary,
              }}
            >
              {t('reports.inventoryStatus')}
            </Typography>
            {/* Add Inventory Status Chart Component Here */}
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: customTheme.colors.babyBlue + '20',
                borderRadius: customTheme.borderRadius.md,
              }}
            >
              <Typography color="text.secondary">
                {t('reports.chartPlaceholder')}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 2,
                color: customTheme.colors.deepNavy,
                fontFamily: customTheme.typography.fontFamily.secondary,
              }}
            >
              {t('reports.revenueAnalysis')}
            </Typography>
            {/* Add Revenue Analysis Chart Component Here */}
            <Box
              sx={{
                height: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: customTheme.colors.babyBlue + '20',
                borderRadius: customTheme.borderRadius.md,
              }}
            >
              <Typography color="text.secondary">
                {t('reports.chartPlaceholder')}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Reports; 