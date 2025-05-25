import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

const Layout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isSidebarOpen, setIsSidebarOpen] = useState(!isMobile);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      <Navbar onMenuClick={toggleSidebar} />
      <Box sx={{ display: 'flex', flex: 1 }}>
        <Sidebar open={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - ${isSidebarOpen ? 240 : 0}px)` },
            ml: { sm: isSidebarOpen ? '240px' : 0 },
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
          }}
        >
          <Outlet />
        </Box>
      </Box>
      <Footer />
    </Box>
  );
};

export default Layout; 