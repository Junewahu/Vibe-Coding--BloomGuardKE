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
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Analytics as AnalyticsIcon,
  Inventory as InventoryIcon,
  LocalShipping as ShippingIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Profile', icon: <PersonIcon />, path: '/profile' },
  { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory' },
  { text: 'Shipping', icon: <ShippingIcon />, path: '/shipping' },
  { text: 'Reports', icon: <AssessmentIcon />, path: '/reports' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      open={open}
      onClose={onClose}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: `1px solid ${theme.palette.divider}`,
        },
      }}
    >
      <Box sx={{ overflow: 'auto', mt: 8 }}>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: location.pathname === item.path
                      ? 'primary.contrastText'
                      : 'text.primary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
      </Box>
    </Drawer>
  );
};

export default Sidebar; 