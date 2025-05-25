import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      // Navigation
      Dashboard: 'Dashboard',
      Patients: 'Patients',
      Calendar: 'Calendar',
      Notifications: 'Notifications',
      Settings: 'Settings',
      'Dark Mode': 'Dark Mode',

      // Common
      'Add New': 'Add New',
      'Save Changes': 'Save Changes',
      Cancel: 'Cancel',
      Delete: 'Delete',
      Edit: 'Edit',
      Search: 'Search',
      'No Results': 'No Results Found',
      Loading: 'Loading...',

      // Patient Management
      'Patient Profile': 'Patient Profile',
      'Add Patient': 'Add Patient',
      'Edit Patient': 'Edit Patient',
      'Patient List': 'Patient List',
      'Patient Details': 'Patient Details',
      'Medical History': 'Medical History',
      'Visit History': 'Visit History',
      'Upcoming Appointments': 'Upcoming Appointments',
      'Past Appointments': 'Past Appointments',

      // Status
      Active: 'Active',
      Inactive: 'Inactive',
      Pending: 'Pending',
      Completed: 'Completed',
      Cancelled: 'Cancelled',
      'Missed Appointment': 'Missed Appointment',

      // Messages
      'Changes Saved': 'Changes saved successfully',
      'Error Saving': 'Error saving changes',
      'Confirm Delete': 'Are you sure you want to delete this item?',
      'Delete Success': 'Item deleted successfully',
      'Delete Error': 'Error deleting item',
    },
  },
  sw: {
    translation: {
      // Navigation
      Dashboard: 'Dashibodi',
      Patients: 'Wagonjwa',
      Calendar: 'Kalenda',
      Notifications: 'Arifa',
      Settings: 'Mipangilio',
      'Dark Mode': 'Hali ya Giza',

      // Common
      'Add New': 'Ongeza Mpya',
      'Save Changes': 'Hifadhi Mabadiliko',
      Cancel: 'Ghairi',
      Delete: 'Futa',
      Edit: 'Hariri',
      Search: 'Tafuta',
      'No Results': 'Hakuna Matokeo',
      Loading: 'Inapakia...',

      // Patient Management
      'Patient Profile': 'Wasifu wa Mgonjwa',
      'Add Patient': 'Ongeza Mgonjwa',
      'Edit Patient': 'Hariri Mgonjwa',
      'Patient List': 'Orodha ya Wagonjwa',
      'Patient Details': 'Maelezo ya Mgonjwa',
      'Medical History': 'Historia ya Matibabu',
      'Visit History': 'Historia ya Ziara',
      'Upcoming Appointments': 'Mikutano ijayo',
      'Past Appointments': 'Mikutano ya zamani',

      // Status
      Active: 'Inatumika',
      Inactive: 'Haifanyi kazi',
      Pending: 'Inasubiri',
      Completed: 'Imekamilika',
      Cancelled: 'Imefutwa',
      'Missed Appointment': 'Mkutano Ulioahiriwa',

      // Messages
      'Changes Saved': 'Mabadiliko yamehifadhiwa',
      'Error Saving': 'Hitilafu katika kuhifadhi mabadiliko',
      'Confirm Delete': 'Una uhakika unataka kufuta hiki?',
      'Delete Success': 'Kifaa kimefutwa',
      'Delete Error': 'Hitilafu katika kufuta kifaa',
    },
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
  });

export default i18n; 