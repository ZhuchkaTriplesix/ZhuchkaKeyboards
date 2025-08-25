import 'package:flutter/material.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class HealthPage extends StatefulWidget {
  const HealthPage({super.key, this.api});

  final ApiClient? api;

  @override
  State<HealthPage> createState() => _HealthPageState();
}

class _HealthPageState extends State<HealthPage> {
  late final ApiClient _api;
  late final bool _ownsClient;
  String _status = 'Checking...';

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ApiClient();
    _ownsClient = widget.api == null;
    _load();
  }

  Future<void> _load() async {
    try {
      final res = await _api.getHealth();
      if (!mounted) return;
      setState(() => _status = res.toString());
    } catch (e) {
      if (!mounted) return;
      setState(() => _status = 'Error: $e');
    }
  }

  @override
  void dispose() {
    if (_ownsClient) {
      _api.close();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Health')),
      body: Center(child: Text(_status)),
    );
  }
}
