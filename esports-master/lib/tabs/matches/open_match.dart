import 'package:esports/model/api.dart';
import 'package:esports/model/matchmodel.dart';
import 'package:esports/tabs/tournaments/open_roster.dart';
import 'package:esports/tabs/tournaments/open_tournament.dart';
import 'package:esports/utils.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
  
  
  // Takes a match [id], opens a bottom sheet displaying the data of the match
openMatch(BuildContext context, int id) async {
    match(context).fetch(id);
    showModalBottomSheet(
      context: context,
      elevation: 4,
      isScrollControlled: true,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16.0))),
      builder: (BuildContext context){
        return MatchSheet(id);
      }
    );
  }

class MatchSheet extends StatelessWidget {
  const MatchSheet(this.id, {Key key}) : super(key: key);

  final int id;
  
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.all(16),
      child: Consumer<MatchModel>(
        builder: (context, _match, child) { 
          return _match.current != null && _match.current.id == id ? Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            GestureDetector(
              behavior: HitTestBehavior.translucent,
              onTap: (){
                  Navigator.pop(context);
                  openTournament(context, _match.current.tournamentId);
                },
            child: Row(children: <Widget>[
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(_match.current.videogame.name, style: TextStyle(fontSize: 26),),
                    SizedBox(height: 4,),
                    Text(_match.current.league.name,
                      softWrap: false, 
                      maxLines: 1,
                      overflow: TextOverflow.fade,
                      style: TextStyle(fontSize: 14),),
                  ],
                )),
              Expanded(
                child: Column(
                  children: <Widget>[
                  Text(_match.current.serie.name ?? _match.current.serie.fullName ?? "", 
                    softWrap: false,
                    maxLines: 1,
                    overflow: TextOverflow.fade,
                    style: TextStyle(fontSize: 14),),
                  SizedBox(height: 4,),
                  Text(_match.current.tournament.name, style: TextStyle(fontSize: 14),),
                ],),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: <Widget>[
                    Text(API.localTime(_match.current.beginAt), 
                      style: TextStyle(fontSize: 26)),
                    Text(API.localDate(_match.current.beginAt), 
                      style: TextStyle(fontSize: 18)),
                  ],),
              ),
            ],)),
            SizedBox(height: 13,),
            Divider(),
            SizedBox(height: 13,),
            if(_match.current.opponents.length == 2) Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
              Expanded(
                child: GestureDetector(
                  onTap: () => downloadRoster(context, _match.current.tournamentId, _match.current.opponents[0].opponent.id),
                  child: Column(
                    children: <Widget>[
                      Text(_match.current.opponents[0].opponent.name, 
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 18)),
                      SizedBox(height: 8),
                      image(_match.current.opponents[0].opponent.imageUrl, 80),
                    ],
                  ),
                ),
              ),
              Text("VS", 
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 20)),
              Expanded(
                child: GestureDetector(
                  onTap: () => downloadRoster(context, _match.current.tournamentId, _match.current.opponents[1].opponent.id),
                  child: Column(
                    children: <Widget>[
                      Text(_match.current.opponents[1].opponent.name, 
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 18)),
                      SizedBox(height: 8),
                      image(_match.current.opponents[1].opponent.imageUrl, 80),
                    ],
                  ),
                ),
              ),
            ],),
            SizedBox(height: 13,),
            Divider(),
            SizedBox(height: 13,),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: <Widget>[
                for(var game in _match.current.games)
                  Card(child: Container(
                    width: 116,
                    height: 58,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: <Widget>[
                      Text("${str(context, "game")} ${game.position}"),
                      Text(game.finished  
                        ? _match.current.opponents.firstWhere((o) => o.opponent.id == game.winner.id).opponent.name
                        : game.beginAt != null ? API.localTime(game.beginAt) : "N/A")
                    ],),
                  ),)
                ],
              ),
            ),
            SizedBox(height: 16,),
            if(_match.current.liveUrl != null)
              Container(
                child: OutlineButton(
                  borderSide: BorderSide(color: Theme.of(context).accentColor),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(8.0))),
                  child: Text(_match.current.liveUrl.replaceFirst("https://", "")),
                  onPressed: () => _launch(_match.current.liveUrl),
                ),
              )
          ],
        ) : loadingCircle;
        },
      ),
    );
  }
}

  // Launch a URL
  _launch(String url) async {
    if (await canLaunch(url)) {
      await launch(url);
    } else {
      throw 'Could not launch $url';
    }
  }