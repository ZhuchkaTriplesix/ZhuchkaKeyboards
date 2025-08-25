import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zhuchka_flutter/screens/login_page.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class _FakeApi extends ApiClient {
  Map<String, dynamic>? lastPayload;
  @override
  Future<Map<String, dynamic>> signUp({
    required String email,
    required String password,
    String? fullName,
    String? phoneNumber,
  }) async {
    lastPayload = {
      'email': email,
      'password': password,
      'full_name': fullName,
      'phone_number': phoneNumber,
    };
    return {'ok': true};
  }
}

void main() {
  testWidgets('LoginPage validates and calls signUp', (tester) async {
    final api = _FakeApi();
    await tester.pumpWidget(
      MaterialApp(
        home: LoginPage(api: api),
      ),
    );

    // Fill required fields
    await tester.enterText(find.byType(TextFormField).at(0), 'user@example.com');
    await tester.enterText(find.byType(TextFormField).at(1), 'secret123');
    await tester.tap(find.byType(ElevatedButton));
    await tester.pumpAndSettle();

    // Should have called signUp with provided credentials
    expect(api.lastPayload?['email'], 'user@example.com');
    expect(api.lastPayload?['password'], 'secret123');
  });
}
