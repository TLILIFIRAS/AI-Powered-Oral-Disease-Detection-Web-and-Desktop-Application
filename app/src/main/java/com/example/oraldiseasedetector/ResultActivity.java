package com.example.oraldiseasedetector;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;
import java.util.List;

public class ResultActivity extends AppCompatActivity {
    private ImageView resultImageView;
    private TextView resultsTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        resultImageView = findViewById(R.id.resultImageView);
        resultsTextView = findViewById(R.id.resultsTextView);

        String imagePath = getIntent().getStringExtra("imagePath");
        // TODO: Display processed image and detection results
    }
} 