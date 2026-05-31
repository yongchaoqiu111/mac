import 'package:esports/model/api.dart';
import 'package:esports/model/tournamentmodel.dart';
import 'package:esports/tabs/matches/open_match.dart';
import 'package:esports/tabs/tournaments/open_roster.dart';
import 'package:esports/utils.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

/// Takes a tournament [id], opens a bottom sheet displaying the data of the tournament
openTournament(BuildContext context, int id) async {
    tournament(context).fetch(id);
    showModalBottomSheet(
      context: context,
      elevation: 4,
      isScrollControlled: true,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16.0))),
      builder: (BuildContext context){
        return TournamentSheet(id);
      }
    );
  }

class TournamentSheet extends StatelessWidget {
  const TournamentSheet(this.id, {Key key}) : super(key: key);
  
  final int id;

  @override
  Widget build(BuildContext context) {
    return Consumer<TournamentModel>(
      builder: (context, model, child) {
        if(model.current == null) return Center(child: CircularProgressIndicator());
        var dateTime = API.localDateTime(model.current.beginAt);
        return Container(
        margin: EdgeInsets.all(16),
        child: model.current != null && model.current.id == id ? Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Flexible(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: <Widget>[
                    image(model.current.league.imageUrl, 72),
                    SizedBox(width: 8,),
                    Flexible(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: <Widget>[
                          Text(model.current.videogame.name,
                            textAlign: TextAlign.start,
                            style: TextStyle(fontSize: 20),),
                          SizedBox(height: 4,),
                          Text(model.current.league.name, 
                            style: TextStyle(fontSize: 14),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,),
                        ],
                      ),
                    ),
                  ],),
                ),
                Column(
                  children: <Widget>[
                    Text(dateTime.year.toString(), 
                      style: TextStyle(fontSize: 22)),
                    Text("${dateTime.month}/${dateTime.day}", 
                      style: TextStyle(fontSize: 18)),
                  ],
                ),
              ],
            ),
            SizedBox(height: 16,),
            Wrap(
              alignment: WrapAlignment.center,
              //mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                  Text(model.current.serie.name ?? model.current.serie.fullName ?? "", style: TextStyle(fontSize: 18),),
                  Text(" – "),
                  Text(model.current.name, style: TextStyle(fontSize: 18),),
              ],
            ),
            SizedBox(height: 4,),
            if(model.current.prizepool != null) 
              ...[Text(model.current.prizepool, style: TextStyle(fontSize: 14),),
              SizedBox(height: 4,)],
            Divider(),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: <Widget>[
                  for(var roster in tournament(context).current.expectedRoster)
                    FlatButton(
                      key: ValueKey(
                        "roster${tournament(context).current.expectedRoster.indexOf(roster)}"),
                      onPressed: () => openRoster(context, roster),
                      padding: EdgeInsets.symmetric(horizontal: 8),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: <Widget>[
                          image(roster.team.imageUrl, 50),
                          Text(roster.team.name ?? "")
                        ],
                      ),
                    ),
                ],
              ),
            ),
            Divider(),
            SizedBox(height: 4),
            Flexible(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * .49),
                child: ListView(
                  shrinkWrap: true,
                  children: <Widget>[
                      for(var match in model.current.matches)
                        GestureDetector(
                          onTap: () => openMatch(context, match.id),
                          child: Card(
                            child: Container(
                              margin: EdgeInsets.all(8),
                              width: MediaQuery.of(context).size.width * .7,
                              child: Wrap(
                                alignment: WrapAlignment.spaceBetween,
                                runAlignment: WrapAlignment.center,
                                crossAxisAlignment: WrapCrossAlignment.center,
                                children: <Widget>[
                                  Text(match.name, style: TextStyle(fontSize: 16)),
                                  if(match.beginAt != null) 
                                    Text("${API.localDate(match.beginAt)} – ${API.localTime(match.beginAt)}",
                                      style: TextStyle(fontSize: 16)),
                                 ],
                              ),
                            ),),
                        )    
                    ],
                ),
              ),
            )
          ]
        ) : loadingCircle
      );
      },
    );
  }
}