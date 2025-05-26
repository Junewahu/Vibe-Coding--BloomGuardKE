import React, { useState } from 'react';
import {
  Box,
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
  Tabs,
  Tab,
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
import MessageTemplateManager from '../components/reminders/MessageTemplateManager';
import MessageSender from '../components/reminders/MessageSender';

interface Reminder {
  id: number;
  title: string;
  description: string;
  date: string;
  time: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'completed' | 'overdue';
  patientName?: string;
  patientPhone?: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reminder-tabpanel-${index}`}
      aria-labelledby={`reminder-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
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
  const [tabValue, setTabValue] = useState(0);

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
      patientPhone: '+254712345678',
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
      patientPhone: '+254712345679',
    },
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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">{t('reminders.title')}</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddReminder}
        >
          {t('reminders.addReminder')}
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label={t('reminders.activeReminders')} />
          <Tab label={t('reminders.templates')} />
          <Tab label={t('reminders.sentMessages')} />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder={t('reminders.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={handleFilterClick}>
                    <FilterListIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('reminders.title')}</TableCell>
                <TableCell>{t('reminders.patient')}</TableCell>
                <TableCell>{t('reminders.date')}</TableCell>
                <TableCell>{t('reminders.time')}</TableCell>
                <TableCell>{t('reminders.priority')}</TableCell>
                <TableCell>{t('reminders.status')}</TableCell>
                <TableCell>{t('reminders.actions')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reminders
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((reminder) => (
                  <TableRow key={reminder.id}>
                    <TableCell>{reminder.title}</TableCell>
                    <TableCell>{reminder.patientName}</TableCell>
                    <TableCell>{reminder.date}</TableCell>
                    <TableCell>{reminder.time}</TableCell>
                    <TableCell>
                      <Chip
                        label={t(`priority.${reminder.priority}`)}
                        size="small"
                        sx={{
                          backgroundColor: getPriorityColor(reminder.priority),
                          color: theme.palette.common.white,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={t(`status.${reminder.status}`)}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(reminder.status),
                          color: theme.palette.common.white,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuClick(e, reminder)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={reminders.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <MessageTemplateManager />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {reminders.map((reminder) => (
            <Grid item xs={12} md={6} key={reminder.id}>
              <MessageSender
                patientPhone={reminder.patientPhone || ''}
                patientName={reminder.patientName || ''}
              />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>
          <EditIcon sx={{ mr: 1 }} />
          {t('common.edit')}
        </MenuItem>
        <MenuItem onClick={() => handleDeleteClick(selectedReminder!)}>
          <DeleteIcon sx={{ mr: 1 }} />
          {t('common.delete')}
        </MenuItem>
      </Menu>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>{t('reminders.deleteConfirm')}</DialogTitle>
        <DialogContent>
          <Typography>
            {t('reminders.deleteConfirmMessage')}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            {t('common.cancel')}
          </Button>
          <Button onClick={handleDeleteConfirm} color="error">
            {t('common.delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Reminders; 