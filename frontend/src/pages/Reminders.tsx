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
  Switch,
  FormControlLabel,
  useTheme,
  Paper,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterListIcon,
  Sync as SyncIcon,
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  NotificationsOff as NotificationsOffIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationSystem';

interface Reminder {
  id: number;
  title: string;
  description: string;
  date: string;
  time: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'completed' | 'overdue';
  patientName?: string;
}

const Reminders: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { showNotification } = useNotification();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedReminder, setSelectedReminder] = useState<Reminder | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // Mock data - replace with actual API calls
  const reminders: Reminder[] = [
    {
      id: 1,
      title: 'Follow-up Appointment',
      description: 'Follow-up with John Doe after surgery',
      date: '2024-02-25',
      time: '10:00 AM',
      priority: 'high',
      status: 'pending',
      patientName: 'John Doe',
    },
    {
      id: 2,
      title: 'Vaccination Due',
      description: 'Vaccination due for Jane Smith',
      date: '2024-02-26',
      time: '02:30 PM',
      priority: 'medium',
      status: 'pending',
      patientName: 'Jane Smith',
    },
    // Add more mock reminders as needed
  ];

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, reminder: Reminder) => {
    setAnchorEl(event.currentTarget);
    setSelectedReminder(reminder);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedReminder(null);
  };

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleAddReminder = () => {
    setOpenDialog(true);
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
  };

  const handleDeleteClick = (reminder: Reminder) => {
    setSelectedReminder(reminder);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedReminder) {
      // Implement delete logic here
      showNotification(t('reminders.deleteSuccess'), 'success');
      setDeleteDialogOpen(false);
      setSelectedReminder(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return theme.palette.primary.main;
      case 'completed':
        return theme.palette.success.main;
      case 'overdue':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
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

  const getNotificationIcon = (method: string) => {
    switch (method) {
      case 'sms':
        return <NotificationsIcon />;
      case 'email':
        return <NotificationsActiveIcon />;
      case 'both':
        return <NotificationsOffIcon />;
      default:
        return <NotificationsIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">{t('reminders.title')}</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/reminders/new')}
        >
          {t('reminders.addReminder')}
        </Button>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <TextField
            fullWidth
            variant="outlined"
            placeholder={t('reminders.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('reminders.title')}</TableCell>
              <TableCell>{t('reminders.description')}</TableCell>
              <TableCell>{t('reminders.date')}</TableCell>
              <TableCell>{t('reminders.time')}</TableCell>
              <TableCell>{t('reminders.priority')}</TableCell>
              <TableCell>{t('reminders.status')}</TableCell>
              <TableCell>{t('reminders.patient')}</TableCell>
              <TableCell>{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reminders.map((reminder: Reminder) => (
              <TableRow key={reminder.id}>
                <TableCell>{reminder.title}</TableCell>
                <TableCell>{reminder.description}</TableCell>
                <TableCell>{reminder.date}</TableCell>
                <TableCell>{reminder.time}</TableCell>
                <TableCell>
                  <Chip
                    label={t(`reminders.priorities.${reminder.priority}`)}
                    size="small"
                    sx={{
                      bgcolor: getPriorityColor(reminder.priority),
                      color: theme.palette.common.white,
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={t(`reminders.statuses.${reminder.status}`)}
                    size="small"
                    sx={{
                      bgcolor: getStatusColor(reminder.status),
                      color: theme.palette.common.white,
                    }}
                  />
                </TableCell>
                <TableCell>{reminder.patientName}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuClick(e, reminder)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteClick(reminder)}
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
        count={reminders.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />

      {/* Reminder Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>{t('reminders.viewDetails')}</MenuItem>
        <MenuItem onClick={handleMenuClose}>{t('reminders.edit')}</MenuItem>
        <MenuItem onClick={handleMenuClose}>{t('reminders.resend')}</MenuItem>
        <MenuItem onClick={handleMenuClose}>{t('reminders.markAsCompleted')}</MenuItem>
      </Menu>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleFilterClose}
      >
        <MenuItem onClick={handleFilterClose}>{t('reminders.filterByStatus')}</MenuItem>
        <MenuItem onClick={handleFilterClose}>{t('reminders.filterByPriority')}</MenuItem>
        <MenuItem onClick={handleFilterClose}>{t('reminders.filterByType')}</MenuItem>
      </Menu>

      {/* Add Reminder Dialog */}
      <Dialog open={openDialog} onClose={handleDialogClose} maxWidth="md" fullWidth>
        <DialogTitle>{t('reminders.addNewReminder')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('reminders.patient')}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('reminders.type')}</InputLabel>
                <Select
                  label={t('reminders.type')}
                  defaultValue=""
                >
                  <MenuItem value="vaccination">{t('reminders.type.vaccination')}</MenuItem>
                  <MenuItem value="checkup">{t('reminders.type.checkup')}</MenuItem>
                  <MenuItem value="medication">{t('reminders.type.medication')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('reminders.dueDate')}
                type="date"
                variant="outlined"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('reminders.priority')}</InputLabel>
                <Select
                  label={t('reminders.priority')}
                  defaultValue=""
                >
                  <MenuItem value="high">{t('reminders.priority.high')}</MenuItem>
                  <MenuItem value="medium">{t('reminders.priority.medium')}</MenuItem>
                  <MenuItem value="low">{t('reminders.priority.low')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>{t('reminders.notificationMethod')}</InputLabel>
                <Select
                  label={t('reminders.notificationMethod')}
                  defaultValue=""
                >
                  <MenuItem value="sms">{t('reminders.notificationMethod.sms')}</MenuItem>
                  <MenuItem value="email">{t('reminders.notificationMethod.email')}</MenuItem>
                  <MenuItem value="both">{t('reminders.notificationMethod.both')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label={t('reminders.recurring')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('reminders.notes')}
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
        <DialogTitle>{t('reminders.deleteConfirm')}</DialogTitle>
        <DialogContent>
          <Typography>
            {selectedReminder?.title} - {selectedReminder?.date} {selectedReminder?.time}
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

export default Reminders; 