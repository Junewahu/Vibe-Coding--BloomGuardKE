import React from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography,
  useTheme,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Language as LanguageIcon } from '@mui/icons-material';
import i18n from '../../i18n';

const rtlLanguages = ['ar', 'he', 'fa'];

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' },
];

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = async (languageCode: string) => {
    await i18n.changeLanguage(languageCode);
    document.dir = rtlLanguages.includes(languageCode) ? 'rtl' : 'ltr';
    document.documentElement.lang = languageCode;
    handleClose();
  };

  const currentLanguage = languages.find((lang) => lang.code === i18n.language) || languages[0];

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          color: theme.palette.text.primary,
          '&:hover': {
            backgroundColor: theme.palette.action.hover,
          },
        }}
        aria-label="change language"
      >
        <LanguageIcon />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 180,
          },
        }}
      >
        {languages.map((language) => (
          <MenuItem
            key={language.code}
            onClick={() => handleLanguageChange(language.code)}
            selected={i18n.language === language.code}
            sx={{
              direction: rtlLanguages.includes(language.code) ? 'rtl' : 'ltr',
            }}
          >
            <ListItemIcon>
              <Typography variant="h6">{language.flag}</Typography>
            </ListItemIcon>
            <ListItemText
              primary={language.name}
              primaryTypographyProps={{
                sx: {
                  fontWeight: i18n.language === language.code ? 600 : 400,
                },
              }}
            />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default LanguageSwitcher; 