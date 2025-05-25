# BloomGuard - Pediatric HealthTech Platform

A modern, accessible, and engaging UI for BloomGuard, a pediatric healthtech platform targeting private clinics and caregivers in Kenya.

## Design Philosophy

BloomGuard's UI is designed to be:
- **Playful yet Professional**: Warm, inviting interface that maintains medical credibility
- **Accessible**: High contrast, clear typography, and responsive design
- **Multilingual**: Support for English and Swahili with easy language switching
- **Mobile-First**: Optimized for both mobile and web platforms
- **Offline-Capable**: Progressive Web App with offline functionality

## Color Palette

- Baby Blue: `#BDE0FE`
- Candy Pink: `#FFAFCC`
- Lavender: `#CDB4DB`
- Sky Blue: `#A2D2FF`
- Deep Navy: `#22223B` (Text)
- White: `#FFFFFF` (Background)

## Key Features

### 1. Modular Components
- `BloomCard`: Reusable card component with status indicators and animations
- `BloomLayout`: Responsive layout with navigation and theme switching
- Custom form components with validation
- Status indicators and microinteractions

### 2. Responsive Design
- Mobile-first approach
- Adaptive layouts for different screen sizes
- Touch-friendly interface elements

### 3. Internationalization
- English and Swahili language support
- Easy language switching
- Culturally appropriate content

### 4. Accessibility
- WCAG 2.1 compliant
- High contrast text
- Screen reader support
- Keyboard navigation

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Junewahu/Vibe-Coding--BloomGuardKE.git
cd Vibe-Coding--BloomGuardKE
```

2. Install dependencies:
```bash
cd frontend
npm install
```

3. Start the development server:
```bash
npm start
```

### Building for Production

```bash
npm run build
```

## Component Structure

```
src/
├── components/
│   ├── common/
│   │   ├── BloomCard.tsx
│   │   └── BloomButton.tsx
│   ├── layout/
│   │   └── BloomLayout.tsx
│   └── forms/
│       └── PatientForm.tsx
├── theme/
│   └── theme.ts
├── i18n/
│   └── config.ts
└── pages/
    ├── Dashboard.tsx
    ├── PatientList.tsx
    └── PatientProfile.tsx
```

## Development Guidelines

### Code Style
- Use TypeScript for type safety
- Follow ESLint and Prettier configurations
- Write meaningful component documentation

### Component Development
- Create reusable, modular components
- Implement proper error handling
- Add loading states and fallbacks
- Include accessibility attributes

### Testing
- Write unit tests for components
- Test responsive behavior
- Verify accessibility compliance

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Material-UI for the component library
- i18next for internationalization
- React community for best practices and patterns 