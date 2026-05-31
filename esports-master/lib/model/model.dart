

/// Contains the model classes representing the json objects from the API
/// Base generated with https://javiercbk.github.io/json_to_dart/
class Match {
  String beginAt;
  bool detailedStats;
  bool draw;
  String endAt;
  bool forfeit;
  List<Games> games;
  int id;
  League league;
  int leagueId;
  Live live;
  String liveUrl;
  String matchType;
  String modifiedAt;
  String name;
  int numberOfGames;
  List<Opponents> opponents;
  List<Results> results;
  String scheduledAt;
  Serie serie;
  int serieId;
  String slug;
  String status;
  MatchTournament tournament;
  int tournamentId;
  Videogame videogame;
  Map<String, dynamic> videogameVersion;
  Opponent winner;
  int winnerId;

  Match(
      {this.beginAt,
      this.detailedStats,
      this.draw,
      this.endAt,
      this.forfeit,
      this.games,
      this.id,
      this.league,
      this.leagueId,
      this.live,
      this.liveUrl,
      this.matchType,
      this.modifiedAt,
      this.name,
      this.numberOfGames,
      this.opponents,
      this.results,
      this.scheduledAt,
      this.serie,
      this.serieId,
      this.slug,
      this.status,
      this.tournament,
      this.tournamentId,
      this.videogame,
      this.videogameVersion,
      this.winner,
      this.winnerId});

  Match.fromJson(Map<String, dynamic> json) {
    beginAt = json['begin_at'];
    detailedStats = json['detailed_stats'];
    draw = json['draw'];
    endAt = json['end_at'];
    forfeit = json['forfeit'];
    if (json['games'] != null) {
      games = List<Games>();
      json['games'].forEach((v) {
        games.add(Games.fromJson(v));
      });
    }
    id = json['id'];
    league = json['league'] != null ? League.fromJson(json['league']) : null;
    leagueId = json['league_id'];
    live = json['live'] != null ? Live.fromJson(json['live']) : null;
    liveUrl = json['live_url'];
    matchType = json['match_type'];
    modifiedAt = json['modified_at'];
    name = json['name'];
    numberOfGames = json['number_of_games'];
    if (json['opponents'] != null) {
      opponents = List<Opponents>();
      json['opponents'].forEach((v) {
        opponents.add(Opponents.fromJson(v));
      });
    }
    if (json['results'] != null) {
      results = List<Results>();
      json['results'].forEach((v) {
        results.add(Results.fromJson(v));
      });
    }
    scheduledAt = json['scheduled_at'];
    serie = json['serie'] != null ? Serie.fromJson(json['serie']) : null;
    serieId = json['serie_id'];
    slug = json['slug'];
    status = json['status'];
    tournament = json['tournament'] != null
        ? MatchTournament.fromJson(json['tournament'])
        : null;
    tournamentId = json['tournament_id'];
    videogame = json['videogame'] != null
        ? Videogame.fromJson(json['videogame'])
        : null;
    videogameVersion = json['videogame_version'];
    winner = json["winner"] != null ? Opponent.fromJson(json["winner"]) : null;
    winnerId = json['winner_id'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['begin_at'] = this.beginAt;
    data['detailed_stats'] = this.detailedStats;
    data['draw'] = this.draw;
    data['end_at'] = this.endAt;
    data['forfeit'] = this.forfeit;
    if (this.games != null) {
      data['games'] = this.games.map((v) => v.toJson()).toList();
    }
    data['id'] = this.id;
    if (this.league != null) {
      data['league'] = this.league.toJson();
    }
    data['league_id'] = this.leagueId;
    if (this.live != null) {
      data['live'] = this.live.toJson();
    }
    data['live_url'] = this.liveUrl;
    data['match_type'] = this.matchType;
    data['modified_at'] = this.modifiedAt;
    data['name'] = this.name;
    data['number_of_games'] = this.numberOfGames;
    if (this.opponents != null) {
      data['opponents'] = this.opponents.map((v) => v.toJson()).toList();
    }
    if (this.results != null) {
      data['results'] = this.results.map((v) => v.toJson()).toList();
    }
    data['scheduled_at'] = this.scheduledAt;
    if (this.serie != null) {
      data['serie'] = this.serie.toJson();
    }
    data['serie_id'] = this.serieId;
    data['slug'] = this.slug;
    data['status'] = this.status;
    if (this.tournament != null) {
      data['tournament'] = this.tournament.toJson();
    }
    data['tournament_id'] = this.tournamentId;
    if (this.videogame != null) {
      data['videogame'] = this.videogame.toJson();
    }
    data['videogame_version'] = this.videogameVersion;
    data['winner'] = this.winner;
    data['winner_id'] = this.winnerId;
    return data;
  }
}

class Games {
  String beginAt;
  bool detailedStats;
  String endAt;
  bool finished;
  bool forfeit;
  int id;
  int length;
  int matchId;
  int position;
  String status;
  String videoUrl;
  Winner winner;
  String winnerType;

  Games(
      {this.beginAt,
      this.detailedStats,
      this.endAt,
      this.finished,
      this.forfeit,
      this.id,
      this.length,
      this.matchId,
      this.position,
      this.status,
      this.videoUrl,
      this.winner,
      this.winnerType});

  Games.fromJson(Map<String, dynamic> json) {
    beginAt = json['begin_at'];
    detailedStats = json['detailed_stats'];
    endAt = json['end_at'];
    finished = json['finished'];
    forfeit = json['forfeit'];
    id = json['id'];
    length = json['length'];
    matchId = json['match_id'];
    position = json['position'];
    status = json['status'];
    videoUrl = json['video_url'];
    winner = json['winner'] != null ? Winner.fromJson(json['winner']) : null;
    winnerType = json['winner_type'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['begin_at'] = this.beginAt;
    data['detailed_stats'] = this.detailedStats;
    data['end_at'] = this.endAt;
    data['finished'] = this.finished;
    data['forfeit'] = this.forfeit;
    data['id'] = this.id;
    data['length'] = this.length;
    data['match_id'] = this.matchId;
    data['position'] = this.position;
    data['status'] = this.status;
    data['video_url'] = this.videoUrl;
    if (this.winner != null) {
      data['winner'] = this.winner.toJson();
    }
    data['winner_type'] = this.winnerType;
    return data;
  }
}

class Winner {
  int id;
  String type;

  Winner({this.id, this.type});

  Winner.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    type = json['type'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['id'] = this.id;
    data['type'] = this.type;
    return data;
  }
}

class League {
  int id;
  String imageUrl;
  bool liveSupported;
  String modifiedAt;
  String name;
  String slug;
  String url;

  League(
      {this.id,
      this.imageUrl,
      this.liveSupported,
      this.modifiedAt,
      this.name,
      this.slug,
      this.url});

  League.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    imageUrl = json['image_url'];
    liveSupported = json['live_supported'];
    modifiedAt = json['modified_at'];
    name = json['name'];
    slug = json['slug'];
    url = json['url'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['id'] = this.id;
    data['image_url'] = this.imageUrl;
    data['live_supported'] = this.liveSupported;
    data['modified_at'] = this.modifiedAt;
    data['name'] = this.name;
    data['slug'] = this.slug;
    data['url'] = this.url;
    return data;
  }
}

class Live {
  String opensAt;
  bool supported;
  String url;

  Live({this.opensAt, this.supported, this.url});

  Live.fromJson(Map<String, dynamic> json) {
    opensAt = json['opens_at'];
    supported = json['supported'];
    url = json['url'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['opens_at'] = this.opensAt;
    data['supported'] = this.supported;
    data['url'] = this.url;
    return data;
  }
}

class Opponents {
  Opponent opponent;
  String type;

  Opponents({this.opponent, this.type});

  Opponents.fromJson(Map<String, dynamic> json) {
    opponent =
        json['opponent'] != null ? Opponent.fromJson(json['opponent']) : null;
    type = json['type'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    if (this.opponent != null) {
      data['opponent'] = this.opponent.toJson();
    }
    data['type'] = this.type;
    return data;
  }
}

class Opponent {
  String acronym;
  int id;
  String imageUrl;
  String name;
  String slug;

  Opponent({this.acronym, this.id, this.imageUrl, this.name, this.slug});

  Opponent.fromJson(Map<String, dynamic> json) {
    acronym = json['acronym'];
    id = json['id'];
    imageUrl = json['image_url'];
    name = json['name'];
    slug = json['slug'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['acronym'] = this.acronym;
    data['id'] = this.id;
    data['image_url'] = this.imageUrl;
    data['name'] = this.name;
    data['slug'] = this.slug;
    return data;
  }
}

class Results {
  int score;
  int teamId;

  Results({this.score, this.teamId});

  Results.fromJson(Map<String, dynamic> json) {
    score = json['score'];
    teamId = json['team_id'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['score'] = this.score;
    data['team_id'] = this.teamId;
    return data;
  }
}

class Serie {
  String beginAt;
  String description;
  String endAt;
  String fullName;
  int id;
  int leagueId;
  String modifiedAt;
  String name;
  String prizepool;
  String season;
  String slug;
  int winnerId;
  String winnerType;
  int year;

  Serie(
      {this.beginAt,
      this.description,
      this.endAt,
      this.fullName,
      this.id,
      this.leagueId,
      this.modifiedAt,
      this.name,
      this.prizepool,
      this.season,
      this.slug,
      this.winnerId,
      this.winnerType,
      this.year});

  Serie.fromJson(Map<String, dynamic> json) {
    beginAt = json['begin_at'];
    description = json['description'];
    endAt = json['end_at'];
    fullName = json['full_name'];
    id = json['id'];
    leagueId = json['league_id'];
    modifiedAt = json['modified_at'];
    name = json['name'];
    prizepool = json['prizepool'];
    season = json['season'];
    slug = json['slug'];
    winnerId = json['winner_id'];
    winnerType = json['winner_type'];
    year = json['year'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['begin_at'] = this.beginAt;
    data['description'] = this.description;
    data['end_at'] = this.endAt;
    data['full_name'] = this.fullName;
    data['id'] = this.id;
    data['league_id'] = this.leagueId;
    data['modified_at'] = this.modifiedAt;
    data['name'] = this.name;
    data['prizepool'] = this.prizepool;
    data['season'] = this.season;
    data['slug'] = this.slug;
    data['winner_id'] = this.winnerId;
    data['winner_type'] = this.winnerType;
    data['year'] = this.year;
    return data;
  }
}

class MatchTournament {
  String beginAt;
  String endAt;
  int id;
  int leagueId;
  String modifiedAt;
  String name;
  String prizepool;
  int serieId;
  String slug;
  int winnerId;
  String winnerType;

  MatchTournament(
      {this.beginAt,
      this.endAt,
      this.id,
      this.leagueId,
      this.modifiedAt,
      this.name,
      this.prizepool,
      this.serieId,
      this.slug,
      this.winnerId,
      this.winnerType});

  MatchTournament.fromJson(Map<String, dynamic> json) {
    beginAt = json['begin_at'];
    endAt = json['end_at'];
    id = json['id'];
    leagueId = json['league_id'];
    modifiedAt = json['modified_at'];
    name = json['name'];
    prizepool = json['prizepool'];
    serieId = json['serie_id'];
    slug = json['slug'];
    winnerId = json['winner_id'];
    winnerType = json['winner_type'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['begin_at'] = this.beginAt;
    data['end_at'] = this.endAt;
    data['id'] = this.id;
    data['league_id'] = this.leagueId;
    data['modified_at'] = this.modifiedAt;
    data['name'] = this.name;
    data['prizepool'] = this.prizepool;
    data['serie_id'] = this.serieId;
    data['slug'] = this.slug;
    data['winner_id'] = this.winnerId;
    data['winner_type'] = this.winnerType;
    return data;
  }
}

class Videogame {
  int id;
  String name;
  String slug;

  Videogame({this.id, this.name, this.slug});

  Videogame.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    name = json['name'];
    slug = json['slug'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['id'] = this.id;
    data['name'] = this.name;
    data['slug'] = this.slug;
    return data;
  }
}

class Tournament {
  String beginAt;
  String endAt;
  List<ExpectedRoster> expectedRoster;
  int id;
  League league;
  int leagueId;
  List<Matches> matches;
  String modifiedAt;
  String name;
  String prizepool;
  Serie serie;
  int serieId;
  String slug;
  List<Teams> teams;
  Videogame videogame;
  int winnerId;
  String winnerType;

  Tournament(
      {this.beginAt,
      this.endAt,
      this.id,
      this.league,
      this.leagueId,
      this.matches,
      this.modifiedAt,
      this.name,
      this.prizepool,
      this.serie,
      this.serieId,
      this.slug,
      this.teams,
      this.videogame,
      this.winnerId,
      this.winnerType});

  Tournament.fromJson(Map<String, dynamic> json) {
    beginAt = json['begin_at'];
    endAt = json['end_at'];
    if (json['expected_roster'] != null) {
      expectedRoster = new List<ExpectedRoster>();
      json['expected_roster'].forEach((v) {
        expectedRoster.add(new ExpectedRoster.fromJson(v));
      });
    }
    id = json['id'];
    league = json['league'] != null ? League.fromJson(json['league']) : null;
    leagueId = json['league_id'];
    if (json['matches'] != null) {
      matches = List<Matches>();
      json['matches'].forEach((v) {
        matches.add(Matches.fromJson(v));
      });
    }
    modifiedAt = json['modified_at'];
    name = json['name'];
    prizepool = json['prizepool'];
    serie = json['serie'] != null ? Serie.fromJson(json['serie']) : null;
    serieId = json['serie_id'];
    slug = json['slug'];
    if (json['teams'] != null) {
      teams = List<Teams>();
      json['teams'].forEach((v) {
        teams.add(Teams.fromJson(v));
      });
    }
    videogame = json['videogame'] != null
        ? Videogame.fromJson(json['videogame'])
        : null;
    winnerId = json['winner_id'];
    winnerType = json['winner_type'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['begin_at'] = this.beginAt;
    data['end_at'] = this.endAt;
    if (this.expectedRoster != null) {
      data['expected_roster'] =
          this.expectedRoster.map((v) => v.toJson()).toList();
    }
    data['id'] = this.id;
    if (this.league != null) {
      data['league'] = this.league.toJson();
    }
    data['league_id'] = this.leagueId;
    if (this.matches != null) {
      data['matches'] = this.matches.map((v) => v.toJson()).toList();
    }
    data['modified_at'] = this.modifiedAt;
    data['name'] = this.name;
    data['prizepool'] = this.prizepool;
    if (this.serie != null) {
      data['serie'] = this.serie.toJson();
    }
    data['serie_id'] = this.serieId;
    data['slug'] = this.slug;
    if (this.teams != null) {
      data['teams'] = this.teams.map((v) => v.toJson()).toList();
    }
    if (this.videogame != null) {
      data['videogame'] = this.videogame.toJson();
    }
    data['winner_id'] = this.winnerId;
    data['winner_type'] = this.winnerType;
    return data;
  }
}

class ExpectedRoster {
  List<Players> players;
  Team team;

  ExpectedRoster({this.players, this.team});

  ExpectedRoster.fromJson(Map<String, dynamic> json) {
    if (json['players'] != null) {
      players = new List<Players>();
      json['players'].forEach((v) {
        players.add(new Players.fromJson(v));
      });
    }
    team = json['team'] != null ? new Team.fromJson(json['team']) : null;
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    if (this.players != null) {
      data['players'] = this.players.map((v) => v.toJson()).toList();
    }
    if (this.team != null) {
      data['team'] = this.team.toJson();
    }
    return data;
  }
}
class Players {
  String firstName;
  String hometown;
  int id;
  String imageUrl;
  String lastName;
  String name;
  String role;
  String slug;

  Players(
      {this.firstName,
      this.hometown,
      this.id,
      this.imageUrl,
      this.lastName,
      this.name,
      this.role,
      this.slug});

  Players.fromJson(Map<String, dynamic> json) {
    firstName = json['first_name'];
    hometown = json['hometown'];
    id = json['id'];
    imageUrl = json['image_url'];
    lastName = json['last_name'];
    name = json['name'];
    role = json['role'];
    slug = json['slug'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['first_name'] = this.firstName;
    data['hometown'] = this.hometown;
    data['id'] = this.id;
    data['image_url'] = this.imageUrl;
    data['last_name'] = this.lastName;
    data['name'] = this.name;
    data['role'] = this.role;
    data['slug'] = this.slug;
    return data;
  }
}

class Team {
  String acronym;
  int id;
  String imageUrl;
  String name;
  String slug;

  Team({this.acronym, this.id, this.imageUrl, this.name, this.slug});

  Team.fromJson(Map<String, dynamic> json) {
    acronym = json['acronym'];
    id = json['id'];
    imageUrl = json['image_url'];
    name = json['name'];
    slug = json['slug'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['acronym'] = this.acronym;
    data['id'] = this.id;
    data['image_url'] = this.imageUrl;
    data['name'] = this.name;
    data['slug'] = this.slug;
    return data;
  }
}

class Matches {
  String beginAt;
  bool detailedStats;
  bool draw;
  String endAt;
  bool forfeit;
  int id;
  Live live;
  String liveUrl;
  String matchType;
  String modifiedAt;
  String name;
  int numberOfGames;
  String scheduledAt;
  String slug;
  String status;
  int tournamentId;
  int winnerId;

  Matches(
      {this.beginAt,
      this.detailedStats,
      this.draw,
      this.endAt,
      this.forfeit,
      this.id,
      this.live,
      this.liveUrl,
      this.matchType,
      this.modifiedAt,
      this.name,
      this.numberOfGames,
      this.scheduledAt,
      this.slug,
      this.status,
      this.tournamentId,
      this.winnerId});

  Matches.fromJson(Map<String, dynamic> json) {
    beginAt = json['begin_at'];
    detailedStats = json['detailed_stats'];
    draw = json['draw'];
    endAt = json['end_at'];
    forfeit = json['forfeit'];
    id = json['id'];
    live = json['live'] != null ? Live.fromJson(json['live']) : null;
    liveUrl = json['live_url'];
    matchType = json['match_type'];
    modifiedAt = json['modified_at'];
    name = json['name'];
    numberOfGames = json['number_of_games'];
    scheduledAt = json['scheduled_at'];
    slug = json['slug'];
    status = json['status'];
    tournamentId = json['tournament_id'];
    winnerId = json['winner_id'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['begin_at'] = this.beginAt;
    data['detailed_stats'] = this.detailedStats;
    data['draw'] = this.draw;
    data['end_at'] = this.endAt;
    data['forfeit'] = this.forfeit;
    data['id'] = this.id;
    if (this.live != null) {
      data['live'] = this.live.toJson();
    }
    data['live_url'] = this.liveUrl;
    data['match_type'] = this.matchType;
    data['modified_at'] = this.modifiedAt;
    data['name'] = this.name;
    data['number_of_games'] = this.numberOfGames;
    data['scheduled_at'] = this.scheduledAt;
    data['slug'] = this.slug;
    data['status'] = this.status;
    data['tournament_id'] = this.tournamentId;
    data['winner_id'] = this.winnerId;
    return data;
  }
}

class Teams {
  String acronym;
  int id;
  String imageUrl;
  String name;
  String slug;

  Teams({this.acronym, this.id, this.imageUrl, this.name, this.slug});

  Teams.fromJson(Map<String, dynamic> json) {
    acronym = json['acronym'];
    id = json['id'];
    imageUrl = json['image_url'];
    name = json['name'];
    slug = json['slug'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = Map<String, dynamic>();
    data['acronym'] = this.acronym;
    data['id'] = this.id;
    data['image_url'] = this.imageUrl;
    data['name'] = this.name;
    data['slug'] = this.slug;
    return data;
  }
}
