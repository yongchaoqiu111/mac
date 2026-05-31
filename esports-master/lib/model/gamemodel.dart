import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:esports/model/api.dart';

GameModel games(context) => Provider.of<GameModel>(context, listen: false);

class GameModel with ChangeNotifier {
  
  // SharedPreferences instance
  SharedPreferences prefs;

  // Shared preferences key
  String gamesKey = "GAMES";

  // List of selected games
  List<String> list = [];

  // Switch the game on or off
  toggleGame(String game){
    if(list.contains(game)){
      list.remove(game);
    } else {
      list.add(game);
    }
    if(prefs != null)
      prefs.setStringList(gamesKey, list);
    notifyListeners();
  }

  // Initialize the SharedPreferences instance, and retrieve the saved list of games
  init() async {
    prefs = await SharedPreferences.getInstance();
    list = prefs.getStringList(gamesKey) ?? List<String>.of(API.games);
    notifyListeners();
  }
}