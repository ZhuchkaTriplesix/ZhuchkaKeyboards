# Zhuchka Flutter Frontend

Flutter frontend for ZhuchkaKeyboards Gateway.

## Prerequisites
- Flutter SDK (stable channel)
- Dart SDK (bundled with Flutter)

## Quick start
```bash
# Install Flutter if not installed: https://docs.flutter.dev/get-started/install

# From repo root
cd frontend/zhuchka_flutter

# If platform folders (android/ios/web/windows) are missing, scaffold them:
flutter create .

# Install dependencies
flutter pub get

# Lint & tests
flutter analyze
flutter test

# Run the app (choose your preferred platform)
flutter run -d chrome
# or
flutter run -d windows
# or
flutter run -d android
# or
flutter run -d ios
```

## Config
The API base URL is loaded from an asset env file.

- File: `assets/env`
- Example content:
```
API_BASE_URL=http://localhost:8001
```
Make sure your backend Gateway is running and accessible from the device/emulator.

## Architecture notes
- State/DI: `provider` is used for dependency injection. `ApiClient` is provided at the app root and consumed in screens via `context.read<ApiClient>()`.
- Env: `flutter_dotenv` loads `assets/env` during startup.
- UI: Material 3 (FilledButton/OutlinedButton), centered AppBar titles, SafeArea on main screen.

## iOS 120Hz (ProMotion)
Flutter uses the highest refresh rate available on Android by default. For iOS devices with ProMotion (e.g. 120 Hz), add this key to `ios/Runner/Info.plist` after you generate the iOS project with `flutter create .`:
```xml
<key>CADisableMinimumFrameDurationOnPhone</key>
<true/>
```
Then rebuild the iOS app.

## Testing
- Unit tests and widget tests are under `test/`
```bash
flutter test
```
- Example tests: `api_client_test.dart`, `health_page_test.dart`, `inventory_page_test.dart`, `login_page_test.dart`, `home_navigation_test.dart`.

## CI
- GitHub Actions workflow: `.github/workflows/flutter.yml`
  - Runs `flutter pub get`, `flutter analyze`, `flutter test --coverage`
  - Uploads `coverage/lcov.info` as an artifact

## Troubleshooting
- If iOS/Android folders are missing, run `flutter create .` in this directory.
- If the app cannot reach the backend, check `assets/env` and your gateway URL/IP.
- On web, ensure CORS is configured on the backend if using a non-localhost origin.
