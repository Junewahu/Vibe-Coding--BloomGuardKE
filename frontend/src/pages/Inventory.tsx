import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  InputAdornment,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { theme as customTheme } from '../utils/theme';

// Placeholder data - replace with actual API calls
const mockInventory = [
  {
    id: 1,
    name: 'Paracetamol 500mg',
    category: 'medication',
    quantity: 1000,
    unit: 'tablets',
    expiryDate: '2024-12-31',
    status: 'good',
    supplier: 'MediSupplies Ltd',
    reorderLevel: 200,
  },
  {
    id: 2,
    name: 'Bandages 5cm',
    category: 'supplies',
    quantity: 50,
    unit: 'rolls',
    expiryDate: '2025-06-30',
    status: 'low',
    supplier: 'HealthCare Supplies',
    reorderLevel: 20,
  },
  // Add more mock inventory items as needed
];

const categories = [
  { value: 'medication', label: 'Medication' },
  { value: 'supplies', label: 'Medical Supplies' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'vaccines', label: 'Vaccines' },
];

const Inventory: React.FC = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [inventoryDialogOpen, setInventoryDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<typeof mockInventory[0] | null>(null);

  const handleAddItem = () => {
    setSelectedItem(null);
    setInventoryDialogOpen(true);
  };

  const handleEditItem = (item: typeof mockInventory[0]) => {
    setSelectedItem(item);
    setInventoryDialogOpen(true);
  };

  const handleDialogClose = () => {
    setInventoryDialogOpen(false);
    setSelectedItem(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return customTheme.colors.babyBlue;
      case 'low':
        return customTheme.colors.lavender;
      case 'critical':
        return customTheme.colors.candyPink;
      default:
        return customTheme.colors.babyBlue;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
        return <CheckCircle fontSize="small" />;
      case 'low':
        return <Warning fontSize="small" />;
      case 'critical':
        return <Error fontSize="small" />;
      default:
        return <CheckCircle fontSize="small" />;
    }
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
          {t('inventory.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddItem}
          sx={{
            backgroundColor: customTheme.colors.babyBlue,
            color: customTheme.colors.deepNavy,
            '&:hover': {
              backgroundColor: customTheme.colors.skyBlue,
            },
            borderRadius: customTheme.borderRadius.md,
          }}
        >
          {t('inventory.addItem')}
        </Button>
      </Box>

      {/* Search and Filter Section */}
      <Paper
        sx={{
          p: 2,
          mb: 3,
          borderRadius: customTheme.borderRadius.lg,
          boxShadow: customTheme.shadows.soft,
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder={t('inventory.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: customTheme.borderRadius.md,
                },
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>{t('inventory.category')}</InputLabel>
              <Select
                value={selectedCategory}
                label={t('inventory.category')}
                onChange={(e) => setSelectedCategory(e.target.value)}
                sx={{
                  borderRadius: customTheme.borderRadius.md,
                }}
              >
                <MenuItem value="all">{t('inventory.allCategories')}</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Inventory Table */}
      <TableContainer
        component={Paper}
        sx={{
          borderRadius: customTheme.borderRadius.lg,
          boxShadow: customTheme.shadows.soft,
        }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('inventory.name')}</TableCell>
              <TableCell>{t('inventory.category')}</TableCell>
              <TableCell>{t('inventory.quantity')}</TableCell>
              <TableCell>{t('inventory.expiryDate')}</TableCell>
              <TableCell>{t('inventory.status')}</TableCell>
              <TableCell>{t('inventory.supplier')}</TableCell>
              <TableCell>{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockInventory.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.name}</TableCell>
                <TableCell>{t(`inventory.categories.${item.category}`)}</TableCell>
                <TableCell>
                  {item.quantity} {item.unit}
                </TableCell>
                <TableCell>{item.expiryDate}</TableCell>
                <TableCell>
                  <Chip
                    icon={getStatusIcon(item.status)}
                    label={t(`inventory.status.${item.status}`)}
                    size="small"
                    sx={{
                      backgroundColor: getStatusColor(item.status),
                      color: customTheme.colors.deepNavy,
                    }}
                  />
                </TableCell>
                <TableCell>{item.supplier}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleEditItem(item)}
                    sx={{ color: customTheme.colors.deepNavy }}
                  >
                    <Edit fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    sx={{ color: customTheme.colors.deepNavy }}
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Inventory Item Dialog */}
      <Dialog
        open={inventoryDialogOpen}
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: customTheme.borderRadius.lg,
            boxShadow: customTheme.shadows.medium,
          },
        }}
      >
        <DialogTitle sx={{ color: customTheme.colors.deepNavy }}>
          {selectedItem
            ? t('inventory.editItem')
            : t('inventory.addItem')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label={t('inventory.name')}
              fullWidth
              defaultValue={selectedItem?.name}
            />
            <FormControl fullWidth>
              <InputLabel>{t('inventory.category')}</InputLabel>
              <Select
                label={t('inventory.category')}
                defaultValue={selectedItem?.category || ''}
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label={t('inventory.quantity')}
                  type="number"
                  fullWidth
                  defaultValue={selectedItem?.quantity}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label={t('inventory.unit')}
                  fullWidth
                  defaultValue={selectedItem?.unit}
                />
              </Grid>
            </Grid>
            <TextField
              label={t('inventory.expiryDate')}
              type="date"
              fullWidth
              defaultValue={selectedItem?.expiryDate}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label={t('inventory.supplier')}
              fullWidth
              defaultValue={selectedItem?.supplier}
            />
            <TextField
              label={t('inventory.reorderLevel')}
              type="number"
              fullWidth
              defaultValue={selectedItem?.reorderLevel}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleDialogClose}
            sx={{ color: customTheme.colors.deepNavy }}
          >
            {t('common.cancel')}
          </Button>
          <Button
            variant="contained"
            sx={{
              backgroundColor: customTheme.colors.babyBlue,
              color: customTheme.colors.deepNavy,
              '&:hover': {
                backgroundColor: customTheme.colors.skyBlue,
              },
            }}
          >
            {selectedItem ? t('common.save') : t('inventory.add')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Inventory; 