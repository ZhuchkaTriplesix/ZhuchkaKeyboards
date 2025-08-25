import 'package:flutter/widgets.dart';
import 'package:provider/provider.dart';
import 'package:zhuchka_flutter/services/api_client.dart';

List<SingleChildWidget> buildAppProviders() {
  return [
    Provider<ApiClient>(
      create: (_) => ApiClient(),
      dispose: (_, client) => client.close(),
    ),
  ];
}
