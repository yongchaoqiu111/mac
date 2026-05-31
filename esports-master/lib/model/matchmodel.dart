
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:esports/model/model.dart';
import 'package:esports/model/api.dart';
import 'package:provider/provider.dart';

// Models getters
MatchModel match(context) => Provider.of<MatchModel>(context, listen: false);
LiveMatchModel liveMatches(context) => Provider.of<LiveMatchModel>(context, listen: false);
TodayMatchModel todayMatches(context) => Provider.of<TodayMatchModel>(context, listen: false);

class MatchModel with ChangeNotifier {

  // API URL for a specific match
  static matchUrl(id) => "https://api.pandascore.co/matches/$id/";

  // Current consulted match
  Match current;

  // Get a list of matches from the API
  static Future<List<Match>> getMatches(String url) async {
    Iterable l = await API.getRequest(url);
    return (l ?? []).map((i) => Match.fromJson(i)).toList();
  }

  // Fetch specific match from the API
  Future fetch(int id) async {
    current = Match.fromJson(await API.getRequest(matchUrl(id)));
    notifyListeners();
  }

  final controller = ScrollController();
}
class LiveMatchModel with ChangeNotifier {
  // API URL for live matches
  static final liveMatchesUrl = "https://api.pandascore.co/matches/running";

  // Live matches
  List<Match> list = [];

  // Is a request currently running
  bool fetching = true;

  // Get live matches from the API
  Future fetch() async {
    list.clear();
    fetching = true;
    notifyListeners();
    list = await MatchModel.getMatches(liveMatchesUrl);
    fetching = false;
    notifyListeners();
  }
}

class TodayMatchModel with ChangeNotifier {

  // Today matches
  List<Match> list = [];

  // Is showing past games of the day
  bool past = false;

  /// Current date and time
  static DateTime get _now => DateTime.now().toUtc();

  /// Get today's date in the API format
  static get _pastRange => "${_now.subtract(Duration(days: 1)).toIso8601String()},${_now.toIso8601String()}";

  /// Get today's date in the API format
  static get _comingRange => "${_now.toIso8601String()},${_now.add(Duration(days: 1)).toIso8601String()}";

  // API URL for today matches
  get todayMatchesUrl => 
    "https://api.pandascore.co/matches/${past ? "past" : "upcoming"}"
    "?sort=begin_at&range[begin_at]=${past ? _pastRange : _comingRange}";

  void toggleMode() {
    past = !past;
    fetch();
  }

  // Get today matches from the API
  Future fetch() async {
    list.clear();
    notifyListeners();
    list = (await MatchModel.getMatches(todayMatchesUrl))..removeWhere((match) => match.opponents.length < 2);
    if(past) list = list.reversed.toList();
    notifyListeners();
  }
}
