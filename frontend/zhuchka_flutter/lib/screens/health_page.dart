import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/services/api_client.dart';
import 'package:zhuchka_flutter/widgets/error_retry.dart';

class HealthPage extends StatefulWidget {
  const HealthPage({super.key});

  @override
  State<HealthPage> createState() => _HealthPageState();
}

class _HealthPageState extends State<HealthPage> {
  ApiClient? _api;
  String? _error;
  String? _content;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _api ??= context.read<ApiClient>();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _error = null;
      _content = null;
    });
    try {
      final res = await _api!.getHealth();
      if (!mounted) return;
      setState(() => _content = res.toString());
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final child = _error != null
        ? ErrorRetry(message: _error!, onRetry: _load)
        : _content == null
            ? const CircularProgressIndicator()
            : Text(_content!);
    return Scaffold(
      appBar: AppBar(title: const Text('Health')),
      body: Center(child: child),
    );
  }
}
