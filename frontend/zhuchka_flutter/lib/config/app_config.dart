import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'constants.dart';

class AppConfig {
  static String apiBaseUrl = Constants.defaultApiBaseUrl;

  static Future<void> load() async {
    try {
      await dotenv.load(fileName: 'assets/env');
      final value = dotenv.env['API_BASE_URL'];
      if (value != null && value.isNotEmpty) {
        apiBaseUrl = value;
      }
    } catch (_) {
      // Fallback to default if env not found or failed to load
      apiBaseUrl = Constants.defaultApiBaseUrl;
    }
  }
}
