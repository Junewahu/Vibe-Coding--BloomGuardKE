import React from 'react';
import {
  Card as MuiCard,
  CardProps as MuiCardProps,
  CardHeader,
  CardContent,
  CardActions,
  Typography,
  Box,
  useTheme,
} from '@mui/material';

export interface CardProps extends Omit<MuiCardProps, 'variant'> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'elevation' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
}

const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  headerAction,
  footer,
  variant = 'elevation',
  padding = 'medium',
  ...props
}) => {
  const theme = useTheme();

  const getPadding = () => {
    switch (padding) {
      case 'none':
        return 0;
      case 'small':
        return theme.spacing(2);
      case 'large':
        return theme.spacing(4);
      default:
        return theme.spacing(3);
    }
  };

  return (
    <MuiCard
      variant={variant}
      sx={{
        borderRadius: theme.shape.borderRadius,
        overflow: 'hidden',
        ...props.sx,
      }}
      {...props}
    >
      {(title || subtitle || headerAction) && (
        <CardHeader
          title={
            typeof title === 'string' ? (
              <Typography variant="h6" component="div">
                {title}
              </Typography>
            ) : (
              title
            )
          }
          subheader={subtitle}
          action={headerAction}
          sx={{
            padding: getPadding(),
            '& .MuiCardHeader-content': {
              overflow: 'hidden',
            },
            '& .MuiCardHeader-title': {
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            },
          }}
        />
      )}

      <CardContent
        sx={{
          padding: getPadding(),
          '&:last-child': {
            paddingBottom: getPadding(),
          },
        }}
      >
        {children}
      </CardContent>

      {footer && (
        <CardActions
          sx={{
            padding: getPadding(),
            justifyContent: 'flex-end',
            borderTop: `1px solid ${theme.palette.divider}`,
          }}
        >
          {footer}
        </CardActions>
      )}
    </MuiCard>
  );
};

export default Card; 