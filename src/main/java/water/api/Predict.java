package water.api;

import water.*;
import water.fvec.*;
import water.util.Log;
import water.util.RString;

public class Predict extends Request2 {
  static final int API_WEAVER = 1; // This file has auto-gen'd doc & json fields
  static public DocGen.FieldDoc[] DOC_FIELDS; // Initialized from Auto-Gen code.

  @API(help = "Model", required = true, filter = Default.class)
  public Iced model; // Type to Model when retired OldModel

  @API(help = "Data frame", required = true, filter = Default.class)
  public Frame data;

  @API(help = "Prediction", filter = Default.class)
  public Key prediction = Key.make("__Prediction_" + Key.make());

  public static String link(Key k, String content) {
    RString rs = new RString("<a href='Predict.query?model=%$key'>%content</a>");
    rs.replace("key", k.toString());
    rs.replace("content", content);
    return rs.toString();
  }

  @Override protected Response serve() {
    try {
      if( model == null )
        throw new IllegalArgumentException("Model is missing");
      Frame fr;
      if( model instanceof Model )
           fr = ((   Model)model).score(data);
      else fr = ((OldModel)model).score(data);
      UKV.put(prediction, fr);
      return Inspect2.redirect(this, prediction.toString());
    } catch( Throwable t ) {
      Log.err(t);
      return Response.error(t.getMessage());
    }
  }
}
