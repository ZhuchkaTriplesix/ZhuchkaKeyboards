import 'package:flutter/material.dart';
import 'package:zhuchka_flutter/config/app_config.dart';
import 'package:zhuchka_flutter/screens/health_page.dart';
import 'package:zhuchka_flutter/screens/inventory_page.dart';
import 'package:zhuchka_flutter/screens/login_page.dart';
import 'package:zhuchka_flutter/screens/home_page.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.load();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Zhuchka Keyboards',
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        useMaterial3: true,
      ),
      routes: {
        '/': (context) => const HomePage(),
        '/health': (context) => const HealthPage(),
        '/inventory': (context) => const InventoryPage(),
        '/login': (context) => const LoginPage(),
      },
    );
  }
}
