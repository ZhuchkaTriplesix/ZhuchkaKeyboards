import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zhuchka_flutter/screens/inventory_page.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class _FakeApi extends ApiClient {
  @override
  Future<dynamic> getInventoryLevels() async {
    return [
      {'name': 'Keyboard X', 'quantity': 5, 'updated_at': '2024-01-01T12:00:00Z'},
      {'name': 'Keyboard Y', 'quantity': 3, 'updated_at': '2024-01-02T15:30:00Z'},
    ];
  }
}

void main() {
  testWidgets('InventoryPage renders list items from API', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: InventoryPage(api: _FakeApi()),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Keyboard X'), findsOneWidget);
    expect(find.text('Keyboard Y'), findsOneWidget);
  });
}
