import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Zhuchka Keyboards')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton(
              onPressed: () => Navigator.of(context).pushNamed('/health'),
              child: const Text('Health'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pushNamed('/inventory'),
              child: const Text('Inventory Levels'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pushNamed('/login'),
              child: const Text('Sign up'),
            ),
          ],
        ),
      ),
    );
  }
}
