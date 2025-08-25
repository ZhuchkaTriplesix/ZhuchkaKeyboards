import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/config/app_config.dart';
import 'package:zhuchka_flutter/di/providers.dart';
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
    return MultiProvider(
      providers: buildAppProviders(),
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Zhuchka Keyboards',
        theme: ThemeData(
          useMaterial3: true,
          colorSchemeSeed: Colors.indigo,
          appBarTheme: const AppBarTheme(
            centerTitle: true,
          ),
          pageTransitionsTheme: const PageTransitionsTheme(builders: {
            TargetPlatform.android: ZoomPageTransitionsBuilder(),
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.windows: ZoomPageTransitionsBuilder(),
            TargetPlatform.linux: ZoomPageTransitionsBuilder(),
            TargetPlatform.macOS: CupertinoPageTransitionsBuilder(),
          }),
        ),
        routes: {
          '/': (context) => const HomePage(),
          '/health': (context) => const HealthPage(),
          '/inventory': (context) => const InventoryPage(),
          '/login': (context) => const LoginPage(),
        },
      ),
    );
  }
}
