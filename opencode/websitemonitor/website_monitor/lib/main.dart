import 'dart:async';
import 'dart:io';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:file_selector/file_selector.dart';
import 'package:url_launcher/url_launcher.dart';

class PieChartPainter extends CustomPainter {
  final double? progress;
  final Color fillColor;
  final Color backgroundColor;

  PieChartPainter({
    this.progress,
    required this.fillColor,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // Background circle
    final bgPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius, bgPaint);

    if (progress != null) {
      // Filled pie slice
      final fillPaint = Paint()
        ..color = fillColor
        ..style = PaintingStyle.fill;
      final sweepAngle = 2 * math.pi * progress!;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        -math.pi / 2,
        sweepAngle,
        true,
        fillPaint,
      );
    }
  }

  @override
  bool shouldRepaint(PieChartPainter oldDelegate) =>
      oldDelegate.progress != progress;
}

void main() {
  runApp(const WebsiteMonitorApp());
}

class WebsiteMonitorApp extends StatelessWidget {
  const WebsiteMonitorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Website Monitor',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const MonitorPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});

  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  final _urlController = TextEditingController(text: 'https://www.microsoft.com');
  final _focusNode = FocusNode();
  Timer? _tickTimer;
  double _intervalMinutes = 0.25;
  int _interval = 300;
  int _countdown = 0;
  bool _loading = false;
  bool _autoRefresh = false;
  String? _status;
  int? _statusCode;
  int? _responseTimeMs;
  String? _error;
  DateTime? _lastChecked;
  bool _confirmedUp = false;

  Future<void> _saveUrlToFile() async {
    final result = await getSaveLocation(
      suggestedName: 'website_monitor_url.txt',
      acceptedTypeGroups: [
        XTypeGroup(label: 'Text files', extensions: ['txt']),
      ],
    );
    if (result == null) return;
    final file = File(result.path);
    file.writeAsString(_urlController.text.trim());
  }

  Future<void> _loadUrlFromFile() async {
    final result = await openFile(
      acceptedTypeGroups: [
        XTypeGroup(label: 'Text files', extensions: ['txt']),
      ],
    );
    if (result == null) return;
    final url = await result.readAsString();
    if (url.trim().isNotEmpty && mounted) {
      setState(() {
        _urlController.text = url.trim();
        _status = null;
        _statusCode = null;
        _responseTimeMs = null;
        _error = null;
        _lastChecked = null;
        _confirmedUp = false;
      });
    }
  }

  Future<void> _checkWebsite() async {
    String url = _urlController.text.trim();
    if (url.isEmpty) {
      if (mounted) setState(() => _error = 'Please enter a URL');
      return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://$url';
      _urlController.text = url;
    }

    setState(() {
      _loading = true;
      _statusCode = null;
      _responseTimeMs = null;
      _error = null;
    });

    final stopwatch = Stopwatch()..start();
    try {
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      final request = await client.getUrl(Uri.parse(url));
      final response = await request.close();

      await response.drain<void>();
      stopwatch.stop();

      if (!mounted) return;
      setState(() {
        _lastChecked = DateTime.now();
        _statusCode = response.statusCode;
        _responseTimeMs = stopwatch.elapsedMilliseconds;
        _status = response.statusCode < 400 ? 'UP' : 'DOWN';
        if (_status == 'UP') _confirmedUp = true;
      });
      if (_status == 'DOWN') _stopAutoRefresh();
    } catch (e) {
      stopwatch.stop();
      if (!mounted) return;
      setState(() {
        _lastChecked = DateTime.now();
        _responseTimeMs = stopwatch.elapsedMilliseconds;
        _error = 'Failed to reach $url';
        _status = 'DOWN';
      });
      _stopAutoRefresh();
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _stopAutoRefresh() {
    _tickTimer?.cancel();
    _tickTimer = null;
    _confirmedUp = false;
    if (mounted) setState(() => _autoRefresh = false);
  }

  void _toggleAutoRefresh() {
    if (_autoRefresh) {
      _stopAutoRefresh();
    } else if (!_loading) {
      if (_urlController.text.trim().isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Enter a website URL first')),
        );
        return;
      }
      _interval = (_intervalMinutes * 60).round();
      _countdown = _interval;
      _checkWebsite();
      _tickTimer = Timer.periodic(const Duration(seconds: 1), (_) {
        if (!mounted) return;
        setState(() {
          if (_countdown > 0) _countdown--;
          if (_countdown == 0) {
            _countdown = _interval;
            if (!_loading) _checkWebsite();
          }
        });
      });
      setState(() => _autoRefresh = true);
    }
  }

  @override
  void dispose() {
    _tickTimer?.cancel();
    _urlController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(_confirmedUp
            ? 'Website Monitor ${_urlController.text}'
            : 'Website Monitor'),
        backgroundColor: theme.colorScheme.inversePrimary,
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.menu),
            tooltip: 'Menu',
            onSelected: (v) {
              if (v == 'save') _saveUrlToFile();
              if (v == 'load') _loadUrlFromFile();
            },
            itemBuilder: (_) => [
              const PopupMenuItem(value: 'save', child: Text('Save URL...')),
              const PopupMenuItem(value: 'load', child: Text('Load URL...')),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.info_outline),
            tooltip: 'About',
            onPressed: () => showAboutDialog(
              context: context,
              applicationName: 'Website Monitor',
              applicationVersion: '1.0.0',
              applicationIcon: const Icon(Icons.monitor_heart, size: 48),
              children: [
                const Text(
                  'A simple app to check if a website is up or down by sending HTTP requests.',
                ),
              ],
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: _urlController,
              focusNode: _focusNode,
              enabled: !_autoRefresh,
              decoration: InputDecoration(
                labelText: 'Website URL',
                prefixIcon: const Icon(Icons.language),
                border: const OutlineInputBorder(),
                suffixIcon: _urlController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _urlController.clear();
                          setState(() {
                            _status = null;
                            _statusCode = null;
                            _responseTimeMs = null;
                            _error = null;
                            _lastChecked = null;
                            _confirmedUp = false;
                          });
                        },
                      )
                    : null,
              ),
              keyboardType: TextInputType.url,
              textInputAction: TextInputAction.go,
              onSubmitted: (_) {
                if (!_autoRefresh) _toggleAutoRefresh();
              },
            ),
            const SizedBox(height: 12),
            AnimatedSize(
              duration: const Duration(milliseconds: 300),
              child: AnimatedOpacity(
                duration: const Duration(milliseconds: 300),
                opacity: !_autoRefresh ? 1.0 : 0.0,
                child: !_autoRefresh
                    ? Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Check interval'),
                              const SizedBox(height: 12),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children: [15, 30, 45, 60, 75, 90, 105, 120]
                                    .map((s) => ChoiceChip(
                                          label: Text(s < 60
                                              ? '${s}s'
                                              : s == 60
                                                  ? '1m'
                                                  : '1m${s - 60}s'),
                                          selected: (_intervalMinutes * 60).round() == s,
                                          onSelected: (_) => setState(
                                              () => _intervalMinutes = s / 60),
                                        ))
                                    .toList(),
                              ),
                            ],
                          ),
                        ),
                      )
                    : const SizedBox.shrink(),
              ),
            ),
            const SizedBox(height: 12),
            Center(
              child: SizedBox(
                width: 320,
                height: 56,
                child: FilledButton.icon(
                  onPressed: _autoRefresh ? _stopAutoRefresh : _toggleAutoRefresh,
                  icon: Icon(
                    _autoRefresh ? Icons.stop : Icons.play_arrow,
                    size: 28,
                  ),
                  label: Text(
                    _autoRefresh
                        ? 'Stop'
                        : 'Check website is up',
                    style: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
            ),
            AnimatedSize(
              duration: const Duration(milliseconds: 300),
              child: _autoRefresh
                  ? Column(
                      children: [
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 52,
                              height: 52,
                              child: TweenAnimationBuilder<double>(
                                tween: Tween(
                                  begin: 0,
                                  end: _countdown / _interval,
                                ),
                                duration: const Duration(milliseconds: 300),
                                builder: (context, value, _) => CustomPaint(
                                  size: const Size(52, 52),
                                  painter: PieChartPainter(
                                    progress: value,
                                    fillColor: theme.colorScheme.primary,
                                    backgroundColor:
                                        theme.colorScheme.surfaceContainerHighest,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            AnimatedSwitcher(
                              duration: const Duration(milliseconds: 200),
                              child: Text(
                                'Next check in ${_countdown ~/ 60}:${(_countdown % 60).toString().padLeft(2, '0')}',
                                key: ValueKey(_countdown),
                                style: theme.textTheme.bodyLarge,
                              ),
                            ),
                          ],
                        ),
                      ],
                    )
                  : const SizedBox.shrink(),
            ),
            const SizedBox(height: 24),
            AnimatedSize(
              duration: const Duration(milliseconds: 300),
              child: AnimatedOpacity(
                duration: const Duration(milliseconds: 300),
                opacity: _status != null || _error != null ? 1.0 : 0.0,
                child: _status != null || _error != null
                    ? Card(
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            children: [
                              Icon(
                                _status == 'UP'
                                    ? Icons.check_circle
                                    : Icons.error,
                                size: 64,
                                color: _status == 'UP'
                                    ? Colors.green
                                    : Colors.red,
                              ),
                              const SizedBox(height: 12),
                              Text(
                                _error ?? _status!,
                                style: theme.textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: _status == 'UP'
                                      ? Colors.green
                                      : Colors.red,
                                ),
                              ),
                              if (_statusCode != null) ...[
                                const SizedBox(height: 8),
                                Text('Status: $_statusCode'),
                              ],
                              if (_responseTimeMs != null) ...[
                                const SizedBox(height: 4),
                                Text('Response time: ${_responseTimeMs}ms'),
                              ],
                              if (_lastChecked != null) ...[
                                const SizedBox(height: 4),
                                Text(
                                  'Checked at ${_lastChecked!.hour.toString().padLeft(2, '0')}:${_lastChecked!.minute.toString().padLeft(2, '0')}:${_lastChecked!.second.toString().padLeft(2, '0')}',
                                  style: theme.textTheme.bodySmall,
                                ),
                              ],
                              if (_status == 'UP') ...[
                                const SizedBox(height: 16),
                                FilledButton.icon(
                                  onPressed: () =>
                                      launchUrl(Uri.parse(_urlController.text)),
                                  icon: const Icon(Icons.open_in_new),
                                  label: Text(
                                      'Open ${Uri.parse(_urlController.text).host} in Browser'),
                                ),
                              ],
                            ],
                          ),
                        ),
                      )
                    : const SizedBox.shrink(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
