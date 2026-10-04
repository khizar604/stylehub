import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: IPInputScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class IPInputScreen extends StatefulWidget {
  @override
  _IPInputScreenState createState() => _IPInputScreenState();
}

class _IPInputScreenState extends State<IPInputScreen> {
  final TextEditingController _ipController = TextEditingController();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    // Pre-fill with the last IP for convenience
    _ipController.text = '192.168.1.28:8000';
  }

  @override
  void dispose() {
    _ipController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('WebView Setup')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Enter the IP address and port of your local server:',
                style: TextStyle(fontSize: 16),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _ipController,
                decoration: InputDecoration(
                  labelText: 'IP Address:Port',
                  hintText: 'Example: 192.168.1.28:8000',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.computer),
                ),
                keyboardType: TextInputType.url,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an IP address';
                  }
                  // Basic validation for IP:port format
                  final RegExp ipPortRegex = RegExp(
                    r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?$',
                  );
                  if (!ipPortRegex.hasMatch(value)) {
                    return 'Invalid IP address format';
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  if (_formKey.currentState!.validate()) {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder:
                            (context) => WebViewExample(
                              ipAddress: 'http://${_ipController.text}',
                            ),
                      ),
                    );
                  }
                },
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12.0),
                  child: Text('Connect', style: TextStyle(fontSize: 18)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class WebViewExample extends StatefulWidget {
  final String ipAddress;

  const WebViewExample({Key? key, required this.ipAddress}) : super(key: key);

  @override
  _WebViewExampleState createState() => _WebViewExampleState();
}

class _WebViewExampleState extends State<WebViewExample> {
  late final WebViewController _controller;
  double _progress = 0;

  @override
  void initState() {
    super.initState();
    _controller =
        WebViewController()
          ..setJavaScriptMode(JavaScriptMode.unrestricted)
          ..setBackgroundColor(Colors.white)
          ..setNavigationDelegate(
            NavigationDelegate(
              onPageStarted: (url) {
                debugPrint('Page started loading: $url');
              },
              onPageFinished: (url) {
                debugPrint('Page finished loading: $url');
              },
              onProgress: (progress) {
                setState(() {
                  _progress = progress / 100;
                });
              },
              onWebResourceError: (WebResourceError error) {
                debugPrint('Web resource error:');
                debugPrint('  Error code: ${error.errorCode}');
                debugPrint('  Description: ${error.description}');
                debugPrint('  Error Type: ${error.errorType}');
                // Show an error message if needed
              },
            ),
          )
          ..loadRequest(Uri.parse(widget.ipAddress));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flutter WebView'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () => _controller.reload(),
          ),
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () {
              // Go back to the IP input screen
              Navigator.of(context).pop();
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_progress < 1) LinearProgressIndicator(value: _progress),
        ],
      ),
    );
  }
}
