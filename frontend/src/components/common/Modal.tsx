import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  useTheme,
  Slide,
  SlideProps,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  children: React.ReactNode;
  actions?: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  fullScreen?: boolean;
  disableBackdropClick?: boolean;
  disableEscapeKeyDown?: boolean;
  showCloseButton?: boolean;
  customPaperProps?: React.ComponentProps<typeof Dialog>['PaperProps'];
}

const Transition = React.forwardRef(function Transition(
  props: SlideProps,
  ref: React.Ref<unknown>
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  children,
  actions,
  maxWidth = 'sm',
  fullWidth = true,
  fullScreen = false,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
  showCloseButton = true,
  customPaperProps,
}) => {
  const theme = useTheme();

  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (disableBackdropClick) {
      event.stopPropagation();
    } else {
      onClose();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      fullScreen={fullScreen}
      TransitionComponent={Transition}
      onBackdropClick={handleBackdropClick}
      disableEscapeKeyDown={disableEscapeKeyDown}
      PaperProps={{
        sx: {
          borderRadius: theme.shape.borderRadius,
          ...(fullScreen
            ? {}
            : {
                maxHeight: '90vh',
                margin: theme.spacing(2),
              }),
        },
        ...customPaperProps,
      }}
    >
      {title && (
        <DialogTitle
          sx={{
            m: 0,
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          {typeof title === 'string' ? (
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          ) : (
            title
          )}
          {showCloseButton && (
            <IconButton
              aria-label="close"
              onClick={onClose}
              sx={{
                color: theme.palette.grey[500],
                '&:hover': {
                  color: theme.palette.grey[700],
                },
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </DialogTitle>
      )}

      <DialogContent
        sx={{
          p: 3,
          '&.MuiDialogContent-root': {
            paddingTop: title ? 3 : 4,
          },
        }}
      >
        {children}
      </DialogContent>

      {actions && (
        <DialogActions
          sx={{
            p: 2,
            borderTop: `1px solid ${theme.palette.divider}`,
          }}
        >
          {actions}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default Modal; 