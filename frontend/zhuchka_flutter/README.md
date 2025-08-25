# Zhuchka Flutter Frontend

Flutter frontend for ZhuchkaKeyboards Gateway.

## Prerequisites
- Flutter SDK (stable channel)
- Dart SDK (bundled with Flutter)

## First run
```bash
# Install Flutter if not installed: https://docs.flutter.dev/get-started/install

# From repo root
cd frontend/zhuchka_flutter

# If platform folders (android/ios/web etc.) are missing, scaffold them:
flutter create .

# Install dependencies
flutter pub get

# Run analyzer and tests
flutter analyze
flutter test

# Run the app (choose your preferred platform)
flutter run -d chrome
# or
flutter run -d windows
```

## Config
The API base URL is loaded from an asset env file.

- File: `assets/env`
- Example content:
```
API_BASE_URL=http://localhost:8001
```

Make sure your backend Gateway is running and accessible from the device/emulator.
