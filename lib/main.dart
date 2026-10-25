import 'package:flutter/material.dart';
import 'frontend/citizen.dart';
import 'frontend/admin.dart';
import 'frontend/login.dart';
import 'frontend/signup.dart';
import 'frontend/auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final bool loggedIn = await AuthService.isLoggedIn();
  final bool adminStatus = await AuthService.isAdmin();

  String startRoute = '/login';
  if (loggedIn) {
    startRoute = adminStatus ? '/admin' : '/citizen';
  }
  runApp(MyApp(initialRoute: startRoute));
}

class MyApp extends StatefulWidget {
  final String initialRoute; 
  
  const MyApp({super.key, required this.initialRoute});

  @override
  State<MyApp> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyApp> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'RoadSense',
      initialRoute: widget.initialRoute,
      routes: {
        "/login": (context) => MyLogin(),
        "/signup": (context) => const MyRegister(),
        "/citizen": (context) => const MyCitizen(),
        "/admin": (context) => const Myadministrator(),
      }
    );
  }
}