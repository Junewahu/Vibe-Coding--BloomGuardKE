import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../../setupTests';
import LanguageSwitcher from '../LanguageSwitcher';
import { changeLanguage } from '../../../i18n';

// Mock the i18n module
jest.mock('../../../i18n', () => ({
  changeLanguage: jest.fn(),
  getLanguageDirection: jest.fn((lang) => (lang === 'ar' ? 'rtl' : 'ltr')),
}));

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders language switcher button', () => {
    renderWithProviders(<LanguageSwitcher />);
    expect(screen.getByLabelText('change language')).toBeInTheDocument();
  });

  it('opens language menu on button click', () => {
    renderWithProviders(<LanguageSwitcher />);
    const button = screen.getByLabelText('change language');
    fireEvent.click(button);
    expect(screen.getByText('English')).toBeInTheDocument();
    expect(screen.getByText('Español')).toBeInTheDocument();
    expect(screen.getByText('Français')).toBeInTheDocument();
    expect(screen.getByText('العربية')).toBeInTheDocument();
  });

  it('changes language when a language option is clicked', async () => {
    renderWithProviders(<LanguageSwitcher />);
    const button = screen.getByLabelText('change language');
    fireEvent.click(button);
    
    const spanishOption = screen.getByText('Español');
    fireEvent.click(spanishOption);

    await waitFor(() => {
      expect(changeLanguage).toHaveBeenCalledWith('es');
    });
  });

  it('applies RTL direction for Arabic language', () => {
    renderWithProviders(<LanguageSwitcher />);
    const button = screen.getByLabelText('change language');
    fireEvent.click(button);
    
    const arabicOption = screen.getByText('العربية').closest('li');
    expect(arabicOption).toHaveStyle({ direction: 'rtl' });
  });

  it('closes menu after language selection', async () => {
    renderWithProviders(<LanguageSwitcher />);
    const button = screen.getByLabelText('change language');
    fireEvent.click(button);
    
    const englishOption = screen.getByText('English');
    fireEvent.click(englishOption);

    await waitFor(() => {
      expect(screen.queryByText('Español')).not.toBeInTheDocument();
    });
  });
}); 