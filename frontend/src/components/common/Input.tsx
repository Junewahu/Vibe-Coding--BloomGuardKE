import React, { forwardRef } from 'react';
import {
  TextField,
  TextFieldProps,
  InputAdornment,
  IconButton,
  useTheme,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

export interface InputProps extends Omit<TextFieldProps, 'variant'> {
  variant?: 'outlined' | 'filled' | 'standard';
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url';
  showPasswordToggle?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLDivElement, InputProps>(
  (
    {
      variant = 'outlined',
      type = 'text',
      showPasswordToggle = false,
      startIcon,
      endIcon,
      ...props
    },
    ref
  ) => {
    const theme = useTheme();
    const [showPassword, setShowPassword] = React.useState(false);

    const handleTogglePassword = () => {
      setShowPassword(!showPassword);
    };

    const getInputProps = () => {
      const inputProps: any = {};

      if (startIcon) {
        inputProps.startAdornment = (
          <InputAdornment position="start">{startIcon}</InputAdornment>
        );
      }

      if (endIcon || (type === 'password' && showPasswordToggle)) {
        inputProps.endAdornment = (
          <InputAdornment position="end">
            {type === 'password' && showPasswordToggle ? (
              <IconButton
                aria-label="toggle password visibility"
                onClick={handleTogglePassword}
                edge="end"
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            ) : (
              endIcon
            )}
          </InputAdornment>
        );
      }

      return inputProps;
    };

    return (
      <TextField
        ref={ref}
        variant={variant}
        type={type === 'password' && showPassword ? 'text' : type}
        InputProps={getInputProps()}
        fullWidth
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: theme.shape.borderRadius,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.primary.main,
            },
          },
          '& .MuiInputLabel-root': {
            '&.Mui-focused': {
              color: theme.palette.primary.main,
            },
          },
          ...props.sx,
        }}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';

export default Input; 