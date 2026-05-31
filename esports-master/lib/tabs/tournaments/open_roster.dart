import 'package:esports/model/model.dart';
import 'package:esports/model/tournamentmodel.dart';
import 'package:esports/utils.dart';
import 'package:flutter/material.dart';

Future<void> downloadRoster(
  BuildContext context, 
  int tournamentId, 
  int rosterId) async {
    await tournament(context).fetch(tournamentId);
    var roster = tournament(context).current.expectedRoster.firstWhere(
      (element) => element.team.id == rosterId);
    if(roster != null) openRoster(context, roster);
}

// Takes an ExpectedRoster, opens a bottom sheet displaying the roster data
openRoster(BuildContext context, ExpectedRoster roster) async {
    showModalBottomSheet(
      context: context,
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16.0))),
      builder: (context) {
        return RosterSheet(roster);
      }
    );
  }

class RosterSheet extends StatelessWidget {
  const RosterSheet(this.roster, {Key key}) : super(key: key);

  final ExpectedRoster roster;
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
        image(roster.team.imageUrl, 80),
        SizedBox(height: 4),
        Text(roster.team.name ?? "", style: TextStyle(fontSize: 24)),
        SizedBox(height: 26, child: Divider()),
        roster.players.isEmpty ? Text(str(context, "noroster")) : SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(children: <Widget>[
            for(var player in roster.players)
              ...[
                Column(
                  children: <Widget>[
                    image(player.imageUrl, 100),
                    SizedBox(height: 4,),
                    if(player.role != null) Text(player.role),
                    Text(player.name, style: TextStyle(fontSize: 20)),
                    if(player.firstName != null) Text("${player.firstName} ${player.lastName}"),
                    if(player.hometown != null) Text(player.hometown, style: TextStyle(fontSize: 16)),
                  ],
                ),
                SizedBox(width: 16,)
              ]
          ]),
        )
      ],),
    );
  }
}