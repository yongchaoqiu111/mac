
import 'package:flutter_driver/flutter_driver.dart';
//import 'package:flutter_test/flutter_test.dart' as f_test;
import 'package:screenshots/screenshots.dart';
import 'package:test/test.dart';
import 'dart:io';

void main() {
  group('eSports', () {

    FlutterDriver driver;

    final config = Config();

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

    test('screenshot', () async {
      // Matches tab
      await screenshot(driver, config, 'matches');

      await driver.tap(find.byValueKey("gamesButton"));
      await screenshot(driver, config, 'gamesButton');
      await driver.tap(find.byValueKey("gamesButton"));

      // Match sheet
      await driver.tap(find.byValueKey("todayMatch0"));
      await screenshot(driver, config, 'match');
      await pressSystemBack();

      // Tournaments tab
      await driver.tap(find.byValueKey("tournamentsTab"));
      await screenshot(driver, config, 'tournaments');

      // Tournament sheet
      await driver.tap(find.byValueKey("ongoingTournament0"));
      await screenshot(driver, config, 'tournament');

      // Roster sheet
      await driver.tap(find.byValueKey("roster0"));
      await screenshot(driver, config, 'roster');

      //expect(await driver.getText(find.text(str(context, "today"))), "0");
    }, timeout: Timeout(Duration(minutes: 1)));
  });
}

Future<void> pressSystemBack() async {
  await Process.run(
    'adb', 
    <String>['shell', 'input', 'keyevent', 'KEYCODE_BACK'], 
    runInShell: true,
  );
}