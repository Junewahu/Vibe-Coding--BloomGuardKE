import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  IconButton,
  Divider,
  useTheme,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  PhotoCamera as PhotoCameraIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    address: '',
    bio: '',
  });
  const [formErrors, setFormErrors] = useState({
    name: '',
    email: '',
    phone: '',
  });

  const validateForm = () => {
    let isValid = true;
    const errors = {
      name: '',
      email: '',
      phone: '',
    };

    if (!formData.name) {
      errors.name = 'Name is required';
      isValid = false;
    }

    if (!formData.email) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
      isValid = false;
    }

    if (formData.phone && !/^\+?[\d\s-]{10,}$/.test(formData.phone)) {
      errors.phone = 'Phone number is invalid';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    setFormErrors((prev) => ({
      ...prev,
      [name]: '',
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        // TODO: Implement profile update
        setIsEditing(false);
      } catch (err) {
        // Handle error
      }
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      phone: '',
      address: '',
      bio: '',
    });
    setFormErrors({
      name: '',
      email: '',
      phone: '',
    });
    setIsEditing(false);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Profile Settings
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Box sx={{ position: 'relative', mr: 3 }}>
            <Avatar
              src={user?.avatar}
              alt={user?.name}
              sx={{ width: 100, height: 100 }}
            />
            {isEditing && (
              <IconButton
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  right: 0,
                  backgroundColor: 'background.paper',
                  '&:hover': { backgroundColor: 'background.paper' },
                }}
              >
                <PhotoCameraIcon />
              </IconButton>
            )}
          </Box>
          <Box>
            <Typography variant="h5">{user?.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.email}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                error={!!formErrors.name}
                helperText={formErrors.name}
                disabled={!isEditing}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={!!formErrors.email}
                helperText={formErrors.email}
                disabled={!isEditing}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone Number"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                error={!!formErrors.phone}
                helperText={formErrors.phone}
                disabled={!isEditing}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Bio"
                name="bio"
                multiline
                rows={4}
                value={formData.bio}
                onChange={handleChange}
                disabled={!isEditing}
              />
            </Grid>
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            {isEditing ? (
              <>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={handleCancel}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={<SaveIcon />}
                >
                  Save Changes
                </Button>
              </>
            ) : (
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={() => setIsEditing(true)}
              >
                Edit Profile
              </Button>
            )}
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Security Settings
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Button variant="outlined" color="primary">
              Change Password
            </Button>
          </Grid>
          <Grid item xs={12}>
            <Button variant="outlined" color="error">
              Delete Account
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Profile; 