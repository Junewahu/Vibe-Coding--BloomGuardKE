# Settings Service

The Settings Service is responsible for managing application settings, including user preferences, clinic information, and system configurations. It provides a centralized way to handle settings with caching and API integration.

## Features

- Singleton pattern for global access
- In-memory caching with timeout
- API integration with error handling
- Type-safe settings management
- Form validation support

## Usage

```typescript
import { settingsService } from './services/settingsService';

// Get all settings
const settings = await settingsService.getSettings();

// Update specific settings
await settingsService.updateSettings({
  clinicName: 'New Clinic Name',
  notifications: {
    email: true,
    sms: false,
  },
});

// Reset settings to defaults
await settingsService.resetSettings();

// Clear cache manually
settingsService.clearCache();
```

## API Methods

### `getSettings()`

Fetches all settings from the API or cache. Returns a Promise that resolves to a Settings object.

```typescript
const settings = await settingsService.getSettings();
```

### `updateSettings(settings: Partial<Settings>)`

Updates specific settings via the API. Returns a Promise that resolves to the updated Settings object.

```typescript
await settingsService.updateSettings({
  clinicName: 'New Name',
});
```

### `resetSettings()`

Resets all settings to their default values. Returns a Promise that resolves to the default Settings object.

```typescript
await settingsService.resetSettings();
```

### `clearCache()`

Clears the in-memory cache of settings.

```typescript
settingsService.clearCache();
```

## Caching

The service implements a simple in-memory cache with a 5-minute timeout. This helps reduce API calls while ensuring data freshness.

- Cache is automatically invalidated after 5 minutes
- Cache is updated after successful API calls
- Cache can be manually cleared using `clearCache()`

## Error Handling

The service includes built-in error handling for API calls:

- Network errors are caught and rethrown
- 401 errors trigger automatic logout
- All errors are logged to console

## Types

The service uses TypeScript interfaces for type safety. See `types/settings.ts` for complete type definitions.

## Testing

Tests are located in `__tests__/settingsService.test.ts`. Run tests using:

```bash
npm test
```

## Dependencies

- axios: For API calls
- yup: For form validation
- react-query: For data fetching and caching (optional)

## Contributing

1. Follow the TypeScript style guide
2. Add tests for new features
3. Update documentation
4. Submit a pull request

## License

MIT 