const path = require('path');

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@types': path.resolve(__dirname, 'src/types'),
      '@context': path.resolve(__dirname, 'src/context'),
      '@constants': path.resolve(__dirname, 'src/constants'),
    },
  },
  jest: {
    configure: {
      moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '^@components/(.*)$': '<rootDir>/src/components/$1',
        '^@pages/(.*)$': '<rootDir>/src/pages/$1',
        '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
        '^@utils/(.*)$': '<rootDir>/src/utils/$1',
        '^@services/(.*)$': '<rootDir>/src/services/$1',
        '^@assets/(.*)$': '<rootDir>/src/assets/$1',
        '^@styles/(.*)$': '<rootDir>/src/styles/$1',
        '^@types/(.*)$': '<rootDir>/src/types/$1',
        '^@context/(.*)$': '<rootDir>/src/context/$1',
        '^@constants/(.*)$': '<rootDir>/src/constants/$1',
      },
    },
  },
}; 