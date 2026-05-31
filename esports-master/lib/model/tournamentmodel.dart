import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:esports/model/model.dart';
import 'package:esports/model/api.dart';
import 'package:provider/provider.dart';

// Models getters
TournamentModel tournament(context) => Provider.of<TournamentModel>(context, listen: false);
OngoingTournamentModel ongoingTournaments(context) => Provider.of<OngoingTournamentModel>(context, listen: false);
UpcomingTournamentModel upcomingTournaments(context) => Provider.of<UpcomingTournamentModel>(context, listen: false);

class TournamentModel with ChangeNotifier {

  // API URL for a specific match
  static tournamentUrl(id) => "https://api.pandascore.co/tournaments/$id/";

  // Currently consulted tournament
  Tournament current;

  // Get current tournaments from the  API
  static Future getTournaments(String url) async {
    Iterable l = await API.getRequest(url);
    return (l ?? []).map((i) => Tournament.fromJson(i)).toList();
  }

  // Get specific tournament from the API
  Future fetch(int id) async {
    current = Tournament.fromJson(await API.getRequest(tournamentUrl(id)));
    notifyListeners();
  }

  final controller = ScrollController();
}

class OngoingTournamentModel with ChangeNotifier {

  // API URL for ongoing tournaments
  static final ongoingTournaments =
      "https://api.pandascore.co/tournaments/running";

  // Ongoing tournaments
  List<Tournament> list = [];

  // Get current tournaments from the  API
  Future fetch() async {
    list.clear();
    await TournamentModel.getTournaments(ongoingTournaments).then((_list) => list = _list);
    notifyListeners();
  }
}

class UpcomingTournamentModel with ChangeNotifier {

  // API URL for upcoming tournaments
  static final upcomingTournaments =
      "https://api.pandascore.co/tournaments/upcoming";

  // Upcoming tournaments
  List<Tournament> list = [];

  // Get current tournaments from the  API
  Future fetch() async {
    list.clear();
    await TournamentModel.getTournaments(upcomingTournaments).then((_list) => list = _list);
    notifyListeners();
  }
}