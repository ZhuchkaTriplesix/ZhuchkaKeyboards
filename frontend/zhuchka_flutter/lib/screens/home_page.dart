import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final spacing = 16.0;
    return Scaffold(
      appBar: AppBar(title: const Text('Zhuchka Keyboards')),
      body: Center(
        child: Padding(
          padding: EdgeInsets.all(spacing),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              FilledButton(
                onPressed: () => Navigator.of(context).pushNamed('/health'),
                style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
                child: const Text('Health'),
              ),
              SizedBox(height: spacing),
              FilledButton.tonal(
                onPressed: () => Navigator.of(context).pushNamed('/inventory'),
                style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
                child: const Text('Inventory Levels'),
              ),
              SizedBox(height: spacing),
              OutlinedButton(
                onPressed: () => Navigator.of(context).pushNamed('/login'),
                style: OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(48)),
                child: const Text('Sign up'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
