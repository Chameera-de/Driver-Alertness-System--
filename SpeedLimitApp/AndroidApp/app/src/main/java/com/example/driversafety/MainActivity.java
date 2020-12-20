package com.example.driversafety;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.AnimationDrawable;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Build;
import android.os.Handler;
import android.provider.Settings;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.animation.Animation;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.koushikdutta.async.future.FutureCallback;
import com.koushikdutta.ion.Ion;

import org.json.JSONException;
import org.json.JSONObject;
import org.w3c.dom.Text;

import java.util.Locale;


public class MainActivity extends AppCompatActivity {
    private Button b;
    private TextView t,uSpd,sugSpd,road, speedMsg;
    private LocationManager locationManager;
    private LocationListener listener;
    public String response;
    public RequestQueue queue;
    private TextToSpeech t1;
    private ImageView iV;

    private AnimationDrawable animationDrawableFAST;
    private AnimationDrawable animationDrawableSLOW;
    private FrameLayout frameLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        frameLayout = findViewById(R.id.frameID);
        animationDrawableFAST = (AnimationDrawable) frameLayout.getBackground();
        animationDrawableFAST.setEnterFadeDuration(5000);
        animationDrawableFAST.setExitFadeDuration(2000);

        animationDrawableSLOW = (AnimationDrawable) frameLayout.getBackground();
        animationDrawableSLOW.setEnterFadeDuration(5000);
        animationDrawableSLOW.setExitFadeDuration(2000);
        fCall();
        iV = findViewById(R.id.iV);
        t = (TextView) findViewById(R.id.textView);
        speedMsg = (TextView) findViewById(R.id.txt1);
        road = (TextView) findViewById(R.id.road);
        uSpd = (TextView) findViewById(R.id.yourSpeed);
        sugSpd = (TextView) findViewById(R.id.suggestedSpeed);
        b = (Button) findViewById(R.id.button);
        queue = Volley.newRequestQueue(this);
        locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);

        t1=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if(status != TextToSpeech.ERROR) {
                    t1.setLanguage(Locale.UK);
                }
                if (status == TextToSpeech.SUCCESS) {
                    t1.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                        @Override
                        public void onDone(String utteranceId) {
                            Toast.makeText(MainActivity.this, "Spoke", Toast.LENGTH_SHORT).show();
                        }

                        @Override
                        public void onError(String utteranceId) {
                        }

                        @Override
                        public void onStart(String utteranceId) {
                        }
                    });
                } else {
                    Log.e("MainActivity", "Initilization Failed!");
                }
            }
        });



        listener = new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                t.setText("\n " + location.getLongitude() + " " + location.getLatitude());

            }

            @Override
            public void onStatusChanged(String s, int i, Bundle bundle) {

            }

            @Override
            public void onProviderEnabled(String s) {

            }

            @Override
            public void onProviderDisabled(String s) {

                Intent i = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                startActivity(i);
            }
        };

        configure_button();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        switch (requestCode){
            case 10:
                configure_button();
                break;
            default:
                break;
        }
    }

    void configure_button(){

        // first check for permissions
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                requestPermissions(new String[]{Manifest.permission.ACCESS_COARSE_LOCATION,Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.INTERNET}
                        ,10);
            }
            return;
        }
        // this code won't execute IF permissions are not allowed, because in the line above there is return statement.
        b.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //noinspection MissingPermission
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 5000, 0, listener);

            }
        });
    }

    void fCall(){
        final String requestUrl = "http://192.168.43.23/server.php";



        Ion.with(getApplicationContext()).load(requestUrl).asString().setCallback(new FutureCallback<String>() {
            @Override
            public void onCompleted(Exception e, String result) {
              //  Toast.makeText(MainActivity.this, result, Toast.LENGTH_SHORT).show();
                try {

                    JSONObject jsonObject = new JSONObject(result);
                    String uSpeed = jsonObject.getString("uSpeed");
                    String sLimit = jsonObject.getString("speedLimit");
                    String mRoad = jsonObject.getString("road");
                    uSpd.setText(uSpeed );
                    sugSpd.setText("Speed Limit:" + jsonObject.getString("speedLimit") + "km/h");
                    road.setText("The road you are on:" + mRoad);

                    if(Integer.parseInt(uSpeed) > Integer.parseInt(sLimit))
                    {
                        t1.speak("Please slow down. The speed limit for this place is" + jsonObject.getString("speedLimit") + "kilometers per hour", TextToSpeech.QUEUE_FLUSH, null);
                        speedMsg.setText("Too fast. Slow down!");
                        iV.setImageResource(R.drawable.down);
                       frameLayout.setBackgroundColor(Color.RED);
                        //animationDrawableFAST.start();
                    }
                    else{

                        speedMsg.setText("Everything's fine!");
                        iV.setImageResource(R.drawable.tick);
                        frameLayout.setBackgroundColor(Color.GREEN);
                    }

                } catch (JSONException e1) {
                    e1.printStackTrace();
                }

            }
        });
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
               fCall();
            }
        }, 9000);
    }

}
