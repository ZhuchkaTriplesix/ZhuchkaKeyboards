import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:zhuchka_flutter/config/app_config.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    await AppConfig.load();
  });

  test('getHealth returns parsed JSON on 200', () async {
    final mock = MockClient((request) async {
      expect(request.url.path, '/api/health');
      return http.Response(json.encode({'status': 'ok'}), 200, headers: {'content-type': 'application/json'});
    });
    final api = ApiClient(httpClient: mock);
    final res = await api.getHealth();
    expect(res['status'], 'ok');
  });

  test('getInventoryLevels returns list when API returns array', () async {
    final mock = MockClient((request) async {
      expect(request.url.path, '/api/inventory/levels');
      return http.Response(json.encode([
        {'name': 'kbd', 'quantity': 10}
      ]), 200);
    });
    final api = ApiClient(httpClient: mock);
    final res = await api.getInventoryLevels();
    expect(res, isA<List<dynamic>>());
  });

  test('signUp accepts optional fields and returns JSON on 201', () async {
    final mock = MockClient((request) async {
      expect(request.url.path, '/api/user/sign-up');
      final body = json.decode(request.body) as Map<String, dynamic>;
      expect(body['full_name'], 'John');
      expect(body['phone_number'], '123');
      return http.Response(json.encode({'result': 'ok'}), 201);
    });
    final api = ApiClient(httpClient: mock);
    final res = await api.signUp(email: 'a@b.c', password: 'secret', fullName: 'John', phoneNumber: '123');
    expect(res['result'], 'ok');
  });

  test('throws ApiException on non-2xx', () async {
    final mock = MockClient((request) async => http.Response('boom', 500));
    final api = ApiClient(httpClient: mock);
    expect(() => api.getHealth(), throwsA(isA<ApiException>()));
  });
}
