import React from 'react';
import {
  Button as MuiButton,
  ButtonProps as MuiButtonProps,
  CircularProgress,
  useTheme,
} from '@mui/material';

export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'small' | 'medium' | 'large';
  isLoading?: boolean;
  loadingText?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  loadingText,
  disabled,
  startIcon,
  endIcon,
  ...props
}) => {
  const theme = useTheme();

  const getVariantProps = () => {
    switch (variant) {
      case 'primary':
        return {
          variant: 'contained' as const,
          color: 'primary' as const,
        };
      case 'secondary':
        return {
          variant: 'contained' as const,
          color: 'secondary' as const,
        };
      case 'outline':
        return {
          variant: 'outlined' as const,
          color: 'primary' as const,
        };
      case 'text':
        return {
          variant: 'text' as const,
          color: 'primary' as const,
        };
      default:
        return {
          variant: 'contained' as const,
          color: 'primary' as const,
        };
    }
  };

  const getSizeProps = () => {
    switch (size) {
      case 'small':
        return {
          padding: '6px 16px',
          fontSize: '0.875rem',
        };
      case 'large':
        return {
          padding: '12px 24px',
          fontSize: '1.125rem',
        };
      default:
        return {
          padding: '8px 20px',
          fontSize: '1rem',
        };
    }
  };

  return (
    <MuiButton
      {...getVariantProps()}
      {...props}
      disabled={disabled || isLoading}
      startIcon={
        isLoading ? (
          <CircularProgress
            size={size === 'small' ? 16 : size === 'large' ? 24 : 20}
            color="inherit"
          />
        ) : (
          startIcon
        )
      }
      endIcon={isLoading ? undefined : endIcon}
      sx={{
        ...getSizeProps(),
        minWidth: size === 'small' ? 80 : size === 'large' ? 120 : 100,
        borderRadius: theme.shape.borderRadius,
        textTransform: 'none',
        fontWeight: 500,
        ...props.sx,
      }}
    >
      {isLoading && loadingText ? loadingText : children}
    </MuiButton>
  );
};

export default Button; 