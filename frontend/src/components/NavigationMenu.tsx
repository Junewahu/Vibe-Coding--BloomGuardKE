import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Box,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard,
  People,
  Event,
  Notifications,
  Settings,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router-dom';
import { theme as customTheme } from '../utils/theme';

interface NavigationMenuProps {
  open: boolean;
  onClose: () => void;
}

const NavigationMenu: React.FC<NavigationMenuProps> = ({ open, onClose }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const menuItems = [
    { path: '/', icon: <Dashboard />, label: t('dashboard.title') },
    { path: '/patients', icon: <People />, label: t('patients.title') },
    { path: '/appointments', icon: <Event />, label: t('appointments.title') },
    { path: '/reminders', icon: <Notifications />, label: t('reminders.title') },
    { path: '/settings', icon: <Settings />, label: t('settings.title') },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: `1px solid ${customTheme.colors.lightGray}`,
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          p: 1,
        }}
      >
        <ListItemButton onClick={onClose}>
          {isMobile ? <ChevronLeft /> : <ChevronRight />}
        </ListItemButton>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: customTheme.colors.babyBlue,
                  '&:hover': {
                    backgroundColor: customTheme.colors.skyBlue,
                  },
                },
                '&:hover': {
                  backgroundColor: customTheme.colors.babyBlue + '40',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path
                    ? customTheme.colors.deepNavy
                    : 'text.secondary',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                sx={{
                  color: location.pathname === item.path
                    ? customTheme.colors.deepNavy
                    : 'text.primary',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default NavigationMenu; 