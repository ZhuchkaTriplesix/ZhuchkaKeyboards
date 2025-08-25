import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/screens/home_page.dart';
import 'package:zhuchka_flutter/screens/health_page.dart';
import 'package:zhuchka_flutter/screens/inventory_page.dart';
import 'package:zhuchka_flutter/screens/login_page.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class _FakeApi extends ApiClient {
  @override
  Future<Map<String, dynamic>> getHealth() async => {'status': 'ok'};
  @override
  Future<dynamic> getInventoryLevels() async => const [];
  @override
  Future<Map<String, dynamic>> signUp({
    required String email,
    required String password,
    String? fullName,
    String? phoneNumber,
  }) async => {'ok': true};
}

void main() {
  testWidgets('Home buttons navigate to respective screens', (tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [Provider<ApiClient>.value(value: _FakeApi())],
        child: MaterialApp(
          routes: {
            '/': (_) => const HomePage(),
            '/health': (_) => const HealthPage(),
            '/inventory': (_) => const InventoryPage(),
            '/login': (_) => const LoginPage(),
          },
        ),
      ),
    );

    // Health
    await tester.tap(find.text('Health'));
    await tester.pumpAndSettle();
    expect(find.text('Health'), findsOneWidget);

    // Back
    await tester.pageBack();
    await tester.pumpAndSettle();

    // Inventory
    await tester.tap(find.text('Inventory Levels'));
    await tester.pumpAndSettle();
    expect(find.text('Inventory Levels'), findsOneWidget);

    // Back
    await tester.pageBack();
    await tester.pumpAndSettle();

    // Sign up
    await tester.tap(find.text('Sign up'));
    await tester.pumpAndSettle();
    expect(find.text('Sign up'), findsOneWidget);
  });
}
