import 'package:cached_network_image/cached_network_image.dart';
import 'package:esports/localizations.dart';
import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

// i18n String getter
  String str(BuildContext context, String key) => EsportsLocalizations.of(context).get(key);

  // Sized square image fetched from the web
  Widget image(String url, double size) => url != null 
    ? SizedBox(width: size, height: size, child: CachedNetworkImage(imageUrl: url,
      progressIndicatorBuilder: (context, _, __) => Shimmer.fromColors(
        baseColor: Colors.transparent,
        highlightColor: Colors.white12,
        child: Container(
          margin: EdgeInsets.all(2),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.all(Radius.circular(16))),)
      ),),) 
    : SizedBox(width: size, height: size);

  // Loading animation
  Widget get loadingCircle => Container(
    width: double.maxFinite,
    height: 140,
    alignment: Alignment.center,
    child: CircularProgressIndicator(strokeWidth: 1,),);

  // Placeholder widget when there is no data to be shown
  Widget nothingBox(String label) => SizedBox( 
    width: double.maxFinite,
    height: 140, 
    child: Center(
      child: Text(
        label, 
        style: TextStyle(
          fontSize: 20,
          color: Colors.grey)),),);
// Commonly used widgets and functions in the app
class Utils {

  
}