# BloomGuard Frontend

This is the frontend application for BloomGuard, a healthcare management system.

## Features

- CHW Field Tracker for managing community health worker activities
- Patient management and tracking
- Caregiver engagement monitoring
- Incentives and adherence tracking

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/bloomguard.git
cd bloomguard/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory and add your environment variables:
```env
REACT_APP_API_URL=http://localhost:3000/api
```

## Development

To start the development server:

```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Building for Production

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Testing

To run tests:

```bash
npm test
```

## Project Structure

```
src/
  ├── components/     # React components
  ├── contexts/      # React contexts
  ├── hooks/         # Custom React hooks
  ├── routes/        # Route components
  ├── services/      # API services
  ├── stores/        # State management
  ├── types/         # TypeScript types
  ├── App.tsx        # Main App component
  └── index.tsx      # Entry point
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 