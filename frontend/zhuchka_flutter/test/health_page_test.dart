import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/screens/health_page.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class _FakeApi extends ApiClient {
  _FakeApi(this._health);
  final Map<String, dynamic> _health;
  @override
  Future<Map<String, dynamic>> getHealth() async => _health;
}

void main() {
  testWidgets('HealthPage displays health JSON', (tester) async {
    final api = _FakeApi({'status': 'ok'});
    await tester.pumpWidget(
      MultiProvider(
        providers: [Provider<ApiClient>.value(value: api)],
        child: const MaterialApp(
          home: HealthPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.textContaining('ok'), findsOneWidget);
  });
}
