import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

class InventoryPage extends StatefulWidget {
  const InventoryPage({super.key});

  @override
  State<InventoryPage> createState() => _InventoryPageState();
}

class _InventoryPageState extends State<InventoryPage> {
  ApiClient? _api;
  List<dynamic>? _items;
  String? _error;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _api ??= context.read<ApiClient>();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _error = null;
      _items = null;
    });
    try {
      final res = await _api!.getInventoryLevels();
      if (!mounted) return;
      setState(() => _items = (res is Map && res['data'] != null) ? (res['data'] as List<dynamic>) : (res as List<dynamic>?));
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Inventory Levels')),
      body: _error != null
          ? Center(child: Text(_error!))
          : _items == null
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.separated(
                    itemCount: _items!.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, index) {
                      final item = _items![index] as Map<String, dynamic>;
                      final name = item['product_name'] ?? item['name'] ?? 'Unnamed';
                      final qty = item['quantity'] ?? item['qty'] ?? 0;
                      final updated = item['updated_at'] ?? item['date'] ?? '';
                      return ListTile(
                        title: Text(name.toString()),
                        subtitle: Text('Updated: ${_formatDate(updated)}'),
                        trailing: Text('$qty'),
                      );
                    },
                  ),
                ),
    );
  }

  String _formatDate(dynamic value) {
    try {
      if (value is String && value.isNotEmpty) {
        final dt = DateTime.tryParse(value);
        if (dt != null) {
          return DateFormat.yMd().add_Hms().format(dt);
        }
      }
      return value?.toString() ?? '';
    } catch (_) {
      return value?.toString() ?? '';
    }
  }
}
