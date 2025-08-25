import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('getHealth times out and throws ApiException', () async {
    final mock = MockClient((request) async {
      await Future<void>.delayed(const Duration(seconds: 2));
      return http.Response(json.encode({'status': 'ok'}), 200);
    });
    final api = ApiClient(httpClient: mock, requestTimeout: const Duration(milliseconds: 200));
    expect(() => api.getHealth(), throwsA(isA<ApiException>()));
  });

  test('getInventoryLevels returns ApiException on invalid json', () async {
    final mock = MockClient((request) async => http.Response('not-json', 200));
    final api = ApiClient(httpClient: mock);
    expect(() => api.getInventoryLevels(), throwsA(isA<ApiException>()));
  });

  test('signUp returns ApiException on 500', () async {
    final mock = MockClient((request) async => http.Response('boom', 500));
    final api = ApiClient(httpClient: mock);
    expect(
      () => api.signUp(email: 'e@e.com', password: 'x'),
      throwsA(isA<ApiException>()),
    );
  });
}
