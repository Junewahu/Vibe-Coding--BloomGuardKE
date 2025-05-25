import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Button,
  ButtonGroup,
} from '@mui/material';
import { customTheme } from '../utils/theme';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <ButtonGroup
      variant="contained"
      size="small"
      sx={{
        '& .MuiButton-root': {
          backgroundColor: customTheme.colors.babyBlue,
          color: customTheme.colors.deepNavy,
          '&:hover': {
            backgroundColor: customTheme.colors.skyBlue,
          },
          '&.Mui-selected': {
            backgroundColor: customTheme.colors.deepNavy,
            color: customTheme.colors.white,
            '&:hover': {
              backgroundColor: customTheme.colors.deepNavy,
            },
          },
        },
      }}
    >
      <Button
        onClick={() => changeLanguage('en')}
        className={i18n.language === 'en' ? 'Mui-selected' : ''}
      >
        EN
      </Button>
      <Button
        onClick={() => changeLanguage('sw')}
        className={i18n.language === 'sw' ? 'Mui-selected' : ''}
      >
        SW
      </Button>
    </ButtonGroup>
  );
};

export default LanguageSwitcher; 