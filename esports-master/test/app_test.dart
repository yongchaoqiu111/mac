// Imports the Flutter Driver API.
import 'package:esports/localizations.dart';
import 'package:flutter_driver/flutter_driver.dart';
import 'package:test/test.dart';

void main() {
  group('Esports App', () {

    FlutterDriver driver;
    // Connect to the Flutter driver before running any tests.
    setUpAll(() async {
      driver = await FlutterDriver.connect();
    });

    // Close the connection to the driver after the tests have completed.
    tearDownAll(() async {
      if (driver != null) {
        driver.close();
      }
    });

    // Verifies the status of Flutter Driver extension
    test('check flutter driver health', () async {
      Health health = await driver.checkHealth();
      print(health.status);
    });
  });
}