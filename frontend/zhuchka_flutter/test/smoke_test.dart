import 'package:flutter_test/flutter_test.dart';
import 'package:zhuchka_flutter/config/app_config.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('AppConfig loads with default base URL when env missing', () async {
    await AppConfig.load();
    expect(AppConfig.apiBaseUrl.isNotEmpty, true);
  });
}
