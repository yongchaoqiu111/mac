import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;

/// Class representing the REST API
class API {

  /// List of the supported games names
  static const games = [
    "CS:GO", 
    "LoL", 
    "Dota 2", 
    "Rocket League", 
    "Overwatch", 
    "PUBG", 
    "Call of Duty Modern Warfare", 
    "Rainbow 6 Siege",
  ];

  /// Access token
  static String accessToken;

  /// Get the local DateTime corresponding to an ISO-8601 formatted string
  static DateTime localDateTime(String date) => DateTime.parse(date).toLocal();

  /// Get the local date or time as a String
  static String localDate(String date) => localDateTime(date).toString().substring(0, 10);
  static String localTime(String date) => localDateTime(date).toString().substring(11, 16);
  
  /// Get token from the asset file
  static get getToken async => await rootBundle.loadString("assets/apikey.txt");

  /// Initialize the access token
  static Future<Null> initToken() async {
    accessToken = "Bearer ${await getToken}";
  } 

  /// GET request to the API for a single object or a list
  static Future<dynamic> getRequest(String url) async {
    var res;
    try {
      final response =
          await http.get(url, headers: {'Authorization': accessToken});
      if (response.statusCode == 200) {
        res = json.decode(response.body);
      }
    } catch (_) {}
    return res;
  }
}