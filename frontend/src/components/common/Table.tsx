import React, { useState } from 'react';
import {
  Table as MuiTable,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  Box,
  Typography,
  useTheme,
  Paper,
} from '@mui/material';

export interface Column<T> {
  id: keyof T;
  label: string;
  minWidth?: number;
  align?: 'left' | 'right' | 'center';
  format?: (value: any) => string | number;
  sortable?: boolean;
}

export interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  selectable?: boolean;
  onRowClick?: (row: T) => void;
  onSelectionChange?: (selectedRows: T[]) => void;
  defaultSort?: {
    column: keyof T;
    direction: 'asc' | 'desc';
  };
  pagination?: {
    pageSize?: number;
    pageSizeOptions?: number[];
  };
}

function Table<T extends { id: string | number }>({
  columns,
  data,
  selectable = false,
  onRowClick,
  onSelectionChange,
  defaultSort,
  pagination = {
    pageSize: 10,
    pageSizeOptions: [5, 10, 25, 50],
  },
}: TableProps<T>) {
  const theme = useTheme();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(pagination.pageSize || 10);
  const [selected, setSelected] = useState<T[]>([]);
  const [orderBy, setOrderBy] = useState<keyof T | undefined>(
    defaultSort?.column
  );
  const [order, setOrder] = useState<'asc' | 'desc'>(
    defaultSort?.direction || 'asc'
  );

  const handleSort = (column: keyof T) => {
    const isAsc = orderBy === column && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(column);
  };

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = data.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
      );
      setSelected(newSelected);
      onSelectionChange?.(newSelected);
      return;
    }
    setSelected([]);
    onSelectionChange?.([]);
  };

  const handleClick = (row: T) => {
    if (selectable) {
      const selectedIndex = selected.findIndex((item) => item.id === row.id);
      let newSelected: T[] = [];

      if (selectedIndex === -1) {
        newSelected = [...selected, row];
      } else {
        newSelected = selected.filter((item) => item.id !== row.id);
      }

      setSelected(newSelected);
      onSelectionChange?.(newSelected);
    }
    onRowClick?.(row);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const isSelected = (row: T) =>
    selected.findIndex((item) => item.id === row.id) !== -1;

  const sortedData = React.useMemo(() => {
    if (!orderBy) return data;

    return [...data].sort((a, b) => {
      const aValue = a[orderBy];
      const bValue = b[orderBy];

      if (aValue === bValue) return 0;
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      const comparison = aValue < bValue ? -1 : 1;
      return order === 'asc' ? comparison : -comparison;
    });
  }, [data, order, orderBy]);

  const paginatedData = sortedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Paper
      sx={{
        width: '100%',
        overflow: 'hidden',
        borderRadius: theme.shape.borderRadius,
      }}
    >
      <TableContainer>
        <MuiTable stickyHeader>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={
                      selected.length > 0 &&
                      selected.length < paginatedData.length
                    }
                    checked={
                      paginatedData.length > 0 &&
                      selected.length === paginatedData.length
                    }
                    onChange={handleSelectAllClick}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={String(column.id)}
                  align={column.align || 'left'}
                  style={{ minWidth: column.minWidth }}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={() => handleSort(column.id)}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (selectable ? 1 : 0)}
                  align="center"
                >
                  <Typography variant="body2" color="text.secondary">
                    No data available
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row) => {
                const isItemSelected = isSelected(row);

                return (
                  <TableRow
                    hover
                    role="checkbox"
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={row.id}
                    selected={isItemSelected}
                    onClick={() => handleClick(row)}
                    sx={{
                      cursor: onRowClick ? 'pointer' : 'default',
                      '&:last-child td, &:last-child th': { border: 0 },
                    }}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox checked={isItemSelected} />
                      </TableCell>
                    )}
                    {columns.map((column) => {
                      const value = row[column.id];
                      return (
                        <TableCell key={String(column.id)} align={column.align}>
                          {column.format ? column.format(value) : value}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </MuiTable>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={pagination.pageSizeOptions}
        component="div"
        count={data.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}

export default Table; 