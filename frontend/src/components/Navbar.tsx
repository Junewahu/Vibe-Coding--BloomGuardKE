import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Menu,
  MenuItem,
  Badge,
  Avatar,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface NavbarProps {
  onMenuClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationsAnchorEl, setNotificationsAnchorEl] = useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationsMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsMenuClose = () => {
    setNotificationsAnchorEl(null);
  };

  const handleProfileClick = () => {
    handleMenuClose();
    navigate('/profile');
  };

  const handleSettingsClick = () => {
    handleMenuClose();
    navigate('/settings');
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    navigate('/login');
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: 'background.paper',
        color: 'text.primary',
        boxShadow: theme.shadows[1],
        zIndex: theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, fontWeight: 600 }}
        >
          BloomGuard
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton
            color="inherit"
            onClick={handleNotificationsMenuOpen}
          >
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton
            edge="end"
            color="inherit"
            onClick={handleProfileMenuOpen}
          >
            {user?.avatar ? (
              <Avatar
                src={user.avatar}
                alt={user.name}
                sx={{ width: 32, height: 32 }}
              />
            ) : (
              <AccountCircle />
            )}
          </IconButton>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem onClick={handleProfileClick}>Profile</MenuItem>
          <MenuItem onClick={handleSettingsClick}>Settings</MenuItem>
          <MenuItem onClick={handleLogout}>Logout</MenuItem>
        </Menu>

        <Menu
          anchorEl={notificationsAnchorEl}
          open={Boolean(notificationsAnchorEl)}
          onClose={handleNotificationsMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem onClick={handleNotificationsMenuClose}>
            <Typography variant="body2">New message from John</Typography>
          </MenuItem>
          <MenuItem onClick={handleNotificationsMenuClose}>
            <Typography variant="body2">System update available</Typography>
          </MenuItem>
          <MenuItem onClick={handleNotificationsMenuClose}>
            <Typography variant="body2">New feature released</Typography>
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 