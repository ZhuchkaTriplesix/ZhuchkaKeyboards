import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class HealthPage extends StatefulWidget {
  const HealthPage({super.key});

  @override
  State<HealthPage> createState() => _HealthPageState();
}

class _HealthPageState extends State<HealthPage> {
  ApiClient? _api;
  String _status = 'Checking...';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _api ??= context.read<ApiClient>();
    _load();
  }

  Future<void> _load() async {
    try {
      final res = await _api!.getHealth();
      if (!mounted) return;
      setState(() => _status = res.toString());
    } catch (e) {
      if (!mounted) return;
      setState(() => _status = 'Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Health')),
      body: Center(child: Text(_status)),
    );
  }
}
