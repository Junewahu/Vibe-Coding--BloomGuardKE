import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  FormControl,
  InputLabel,
  Select,
  useTheme,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterListIcon,
  Sync as SyncIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationSystem';

interface Patient {
  id: number;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  phone: string;
  email: string;
  lastVisit: string;
  nextAppointment: string;
  status: 'active' | 'inactive';
}

const Patients: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { showNotification } = useNotification();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // Mock data - replace with actual API calls
  const patients: Patient[] = [
    {
      id: 1,
      name: 'John Doe',
      age: 35,
      gender: 'male',
      phone: '+1234567890',
      email: 'john@example.com',
      lastVisit: '2024-02-15',
      nextAppointment: '2024-03-01',
      status: 'active',
    },
    {
      id: 2,
      name: 'Jane Smith',
      age: 28,
      gender: 'female',
      phone: '+1987654321',
      email: 'jane@example.com',
      lastVisit: '2024-02-14',
      nextAppointment: '2024-02-28',
      status: 'active',
    },
    // Add more mock patients as needed
  ];

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, patient: Patient) => {
    setAnchorEl(event.currentTarget);
    setSelectedPatient(patient);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPatient(null);
  };

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleAddPatient = () => {
    setOpenDialog(true);
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
  };

  const handleDeleteClick = (patient: Patient) => {
    setSelectedPatient(patient);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedPatient) {
      // Implement delete logic here
      showNotification(t('patients.deleteSuccess'), 'success');
      setDeleteDialogOpen(false);
      setSelectedPatient(null);
    }
  };

  const getRiskScoreColor = (riskScore: string) => {
    switch (riskScore.toLowerCase()) {
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      case 'low':
        return theme.palette.success.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">{t('patients.title')}</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<FilterListIcon />}
            onClick={handleFilterClick}
          >
            {t('common.filter')}
          </Button>
          <Button
            variant="outlined"
            startIcon={<SyncIcon />}
          >
            {t('common.sync')}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/patients/new')}
          >
            {t('patients.addPatient')}
          </Button>
        </Box>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder={t('patients.searchPatients')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
            <IconButton>
              <FilterListIcon />
            </IconButton>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('patients.name')}</TableCell>
                <TableCell>{t('patients.age')}</TableCell>
                <TableCell>{t('patients.gender')}</TableCell>
                <TableCell>{t('patients.phone')}</TableCell>
                <TableCell>{t('patients.email')}</TableCell>
                <TableCell>{t('patients.lastVisit')}</TableCell>
                <TableCell>{t('patients.nextAppointment')}</TableCell>
                <TableCell>{t('common.actions')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredPatients
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((patient) => (
                  <TableRow key={patient.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                          {patient.name.charAt(0)}
                        </Avatar>
                        <Typography>{patient.name}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{patient.age}</TableCell>
                    <TableCell>{t(`patients.${patient.gender}`)}</TableCell>
                    <TableCell>{patient.phone}</TableCell>
                    <TableCell>{patient.email}</TableCell>
                    <TableCell>{patient.lastVisit}</TableCell>
                    <TableCell>{patient.nextAppointment}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuClick(e, patient)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(patient)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={patients.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>

      {/* Patient Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>{t('patients.viewDetails')}</MenuItem>
        <MenuItem onClick={handleMenuClose}>{t('patients.edit')}</MenuItem>
        <MenuItem onClick={handleMenuClose}>{t('patients.scheduleVisit')}</MenuItem>
        <MenuItem onClick={handleMenuClose}>{t('patients.viewHistory')}</MenuItem>
      </Menu>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleFilterClose}
      >
        <MenuItem onClick={handleFilterClose}>{t('patients.filterByRisk')}</MenuItem>
        <MenuItem onClick={handleFilterClose}>{t('patients.filterByStatus')}</MenuItem>
        <MenuItem onClick={handleFilterClose}>{t('patients.filterByAge')}</MenuItem>
      </Menu>

      {/* Add Patient Dialog */}
      <Dialog open={openDialog} onClose={handleDialogClose} maxWidth="md" fullWidth>
        <DialogTitle>{t('patients.addNewPatient')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('patients.name')}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('patients.age')}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('patients.gender')}</InputLabel>
                <Select
                  label={t('patients.gender')}
                  defaultValue=""
                >
                  <MenuItem value="male">{t('patients.male')}</MenuItem>
                  <MenuItem value="female">{t('patients.female')}</MenuItem>
                  <MenuItem value="other">{t('patients.other')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('patients.dateOfBirth')}
                type="date"
                variant="outlined"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('patients.address')}
                variant="outlined"
                multiline
                rows={3}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>{t('common.cancel')}</Button>
          <Button variant="contained" onClick={handleDialogClose}>
            {t('common.save')}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>{t('patients.deleteConfirm')}</DialogTitle>
        <DialogContent>
          <Typography>
            {selectedPatient?.name}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            {t('common.cancel')}
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
          >
            {t('common.delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Patients; 