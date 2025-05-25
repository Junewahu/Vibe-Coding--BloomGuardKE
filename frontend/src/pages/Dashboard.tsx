import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  useTheme,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  Inventory,
  LocalShipping,
  Assessment,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// Mock data for demonstration
const analyticsData = {
  totalOrders: 156,
  pendingOrders: 23,
  totalRevenue: 45678,
  averageOrderValue: 292.8,
};

const recentOrders = [
  { id: 1, customer: 'John Doe', amount: 299.99, status: 'Delivered' },
  { id: 2, customer: 'Jane Smith', amount: 199.99, status: 'Processing' },
  { id: 3, customer: 'Bob Johnson', amount: 499.99, status: 'Shipped' },
];

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuth();

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back, {user?.name}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your store today.
        </Typography>
      </Box>

      {/* Analytics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              bgcolor: theme.palette.primary.main,
              color: theme.palette.primary.contrastText,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6" component="h2">
                Total Orders
              </Typography>
              <Inventory />
            </Box>
            <Typography variant="h3" component="div" sx={{ mt: 2 }}>
              {analyticsData.totalOrders}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              +12% from last month
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              bgcolor: theme.palette.secondary.main,
              color: theme.palette.secondary.contrastText,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6" component="h2">
                Pending Orders
              </Typography>
              <LocalShipping />
            </Box>
            <Typography variant="h3" component="div" sx={{ mt: 2 }}>
              {analyticsData.pendingOrders}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              {Math.round((analyticsData.pendingOrders / analyticsData.totalOrders) * 100)}% of total
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              bgcolor: theme.palette.success.main,
              color: theme.palette.success.contrastText,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6" component="h2">
                Total Revenue
              </Typography>
              <TrendingUp />
            </Box>
            <Typography variant="h3" component="div" sx={{ mt: 2 }}>
              ${analyticsData.totalRevenue.toLocaleString()}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              +8% from last month
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              bgcolor: theme.palette.info.main,
              color: theme.palette.info.contrastText,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6" component="h2">
                Avg. Order Value
              </Typography>
              <Assessment />
            </Box>
            <Typography variant="h3" component="div" sx={{ mt: 2 }}>
              ${analyticsData.averageOrderValue}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              +5% from last month
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Orders */}
      <Card>
        <CardHeader
          title="Recent Orders"
          action={
            <IconButton>
              <RefreshIcon />
            </IconButton>
          }
        />
        <Divider />
        <CardContent>
          <Box sx={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Order ID</th>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Customer</th>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Amount</th>
                  <th style={{ textAlign: 'left', padding: '8px' }}>Status</th>
                  <th style={{ textAlign: 'right', padding: '8px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentOrders.map((order) => (
                  <tr key={order.id}>
                    <td style={{ padding: '8px' }}>#{order.id}</td>
                    <td style={{ padding: '8px' }}>{order.customer}</td>
                    <td style={{ padding: '8px' }}>${order.amount}</td>
                    <td style={{ padding: '8px' }}>
                      <Typography
                        variant="body2"
                        sx={{
                          color:
                            order.status === 'Delivered'
                              ? 'success.main'
                              : order.status === 'Processing'
                              ? 'warning.main'
                              : 'info.main',
                        }}
                      >
                        {order.status}
                      </Typography>
                    </td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>
                      <IconButton size="small">
                        <MoreVertIcon />
                      </IconButton>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Button variant="contained" startIcon={<Inventory />}>
              New Order
            </Button>
          </Grid>
          <Grid item>
            <Button variant="outlined" startIcon={<LocalShipping />}>
              Track Shipment
            </Button>
          </Grid>
          <Grid item>
            <Button variant="outlined" startIcon={<Assessment />}>
              Generate Report
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard; 