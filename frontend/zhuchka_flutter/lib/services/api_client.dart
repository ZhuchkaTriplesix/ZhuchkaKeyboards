import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

class ApiClient {
  ApiClient({http.Client? httpClient}) : _httpClient = httpClient ?? http.Client();

  final http.Client _httpClient;

  Uri _uri(String path, [Map<String, String>? query]) {
    final base = AppConfig.apiBaseUrl.endsWith('/')
        ? AppConfig.apiBaseUrl.substring(0, AppConfig.apiBaseUrl.length - 1)
        : AppConfig.apiBaseUrl;
    return Uri.parse('$base$path').replace(queryParameters: query);
  }

  Future<Map<String, dynamic>> getHealth() async {
    final res = await _httpClient.get(_uri('/api/health'));
    _ensureOk(res);
    return json.decode(res.body) as Map<String, dynamic>;
  }

  Future<dynamic> getInventoryLevels() async {
    final res = await _httpClient.get(_uri('/api/inventory/levels'));
    _ensureOk(res);
    return json.decode(res.body);
  }

  Future<Map<String, dynamic>> signUp({
    required String email,
    required String password,
    String? fullName,
    String? phoneNumber,
  }) async {
    final payload = <String, dynamic>{
      'email': email,
      'password': password,
      if (fullName != null && fullName.isNotEmpty) 'full_name': fullName,
      if (phoneNumber != null && phoneNumber.isNotEmpty) 'phone_number': phoneNumber,
    };
    final res = await _httpClient.post(
      _uri('/api/user/sign-up'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(payload),
    );
    _ensureOk(res, allow201: true);
    return json.decode(res.body) as Map<String, dynamic>;
  }

  void _ensureOk(http.Response res, {bool allow201 = false}) {
    final ok = res.statusCode >= 200 && res.statusCode < 300;
    if (!ok || (!allow201 && res.statusCode == 201)) {
      throw ApiException('HTTP ${res.statusCode}: ${res.body}');
    }
  }

  void close() => _httpClient.close();
}

class ApiException implements Exception {
  ApiException(this.message);
  final String message;

  @override
  String toString() => 'ApiException: $message';
}
