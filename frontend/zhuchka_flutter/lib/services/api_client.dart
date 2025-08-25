import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

class ApiClient {
  ApiClient({http.Client? httpClient, Duration? requestTimeout})
      : _httpClient = httpClient ?? http.Client(),
        _timeout = requestTimeout ?? const Duration(seconds: 10);

  final http.Client _httpClient;
  final Duration _timeout;

  Uri _uri(String path, [Map<String, String>? query]) {
    final base = AppConfig.apiBaseUrl.endsWith('/')
        ? AppConfig.apiBaseUrl.substring(0, AppConfig.apiBaseUrl.length - 1)
        : AppConfig.apiBaseUrl;
    return Uri.parse('$base$path').replace(queryParameters: query);
  }

  Future<Map<String, dynamic>> getHealth() async {
    try {
      final res = await _httpClient.get(_uri('/api/health')).timeout(_timeout);
      _ensureOk(res);
      return json.decode(res.body) as Map<String, dynamic>;
    } on SocketException catch (e) {
      throw ApiException('Network error: ${e.message}');
    } on HttpException catch (e) {
      throw ApiException('HTTP error: ${e.message}');
    } on FormatException catch (e) {
      throw ApiException('Invalid JSON: ${e.message}');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(e.toString());
    }
  }

  Future<dynamic> getInventoryLevels() async {
    try {
      final res = await _httpClient.get(_uri('/api/inventory/levels')).timeout(_timeout);
      _ensureOk(res);
      return json.decode(res.body);
    } on SocketException catch (e) {
      throw ApiException('Network error: ${e.message}');
    } on HttpException catch (e) {
      throw ApiException('HTTP error: ${e.message}');
    } on FormatException catch (e) {
      throw ApiException('Invalid JSON: ${e.message}');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(e.toString());
    }
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
    try {
      final res = await _httpClient
          .post(
            _uri('/api/user/sign-up'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(payload),
          )
          .timeout(_timeout);
      _ensureOk(res, allow201: true);
      return json.decode(res.body) as Map<String, dynamic>;
    } on SocketException catch (e) {
      throw ApiException('Network error: ${e.message}');
    } on HttpException catch (e) {
      throw ApiException('HTTP error: ${e.message}');
    } on FormatException catch (e) {
      throw ApiException('Invalid JSON: ${e.message}');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(e.toString());
    }
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
