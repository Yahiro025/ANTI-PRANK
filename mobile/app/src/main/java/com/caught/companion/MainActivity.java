package com.caught.companion;

import android.Manifest;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final int CREAM = Color.rgb(255, 244, 222), INK = Color.rgb(37, 28, 25), RED = Color.rgb(185, 45, 36);
    private final Handler handler = new Handler(Looper.getMainLooper());
    private EditText code;
    private TextView status;
    private Button start, stop;
    private boolean requestedNotifications;
    private final Runnable refresh = new Runnable() {
        public void run() { refreshStatus(); handler.postDelayed(this, 800); }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(INK);
        getWindow().setNavigationBarColor(INK);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(CREAM);
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(26), dp(24), dp(26), dp(30));
        scroll.addView(page);
        TextView brand = text("CAUGHT!", 20, true, RED);
        page.addView(brand);
        TextView title = text("Your phone is the lookout.", 34, true, INK);
        title.setLineSpacing(dp(2), 1f);
        add(page, title, 22);
        add(page, text("Take your phone with you. Your laptop will watch for it to move away.", 16, false, INK), 12);
        add(page, text("1. On your laptop, select PHONE WATCH.\n2. Enter the eight-character code below.\n3. Start the lookout, then keep your phone nearby until the laptop finds it.", 15, false, INK), 26);
        TextView label = text("LAPTOP CODE", 13, true, INK);
        add(page, label, 26);
        code = new EditText(this);
        code.setSingleLine(true);
        code.setTextSize(24);
        code.setTypeface(Typeface.MONOSPACE, Typeface.BOLD);
        code.setTextColor(INK);
        code.setHintTextColor(Color.rgb(113, 93, 80));
        code.setHint("e.g. A12B34CD");
        code.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        code.setFilters(new InputFilter[]{new InputFilter.AllCaps(), new InputFilter.LengthFilter(8)});
        code.setPadding(dp(16), dp(12), dp(16), dp(12));
        code.setBackground(box(Color.WHITE, 2, INK));
        LinearLayout.LayoutParams codeParams = new LinearLayout.LayoutParams(-1, dp(60));
        codeParams.topMargin = dp(9);
        page.addView(code, codeParams);
        status = text("Lookout is off.", 15, true, INK);
        status.setPadding(dp(16), dp(15), dp(16), dp(15));
        status.setBackground(box(Color.rgb(245, 225, 199), 0, INK));
        add(page, status, 22);
        start = button("START LOOKOUT", RED, CREAM);
        start.setOnClickListener(v -> requestStart());
        add(page, start, 20);
        stop = button("STOP LOOKOUT", INK, CREAM);
        stop.setOnClickListener(v -> { stopService(new Intent(this, BeaconService.class)); refreshStatus(); });
        add(page, stop, 10);
        add(page, text("Bluetooth gives an approximate signal, not an exact distance. A visible notification stays on while the lookout runs. This is a prank demo, not a lock or security system.", 13, false, INK), 26);
        setContentView(scroll);
    }

    private void requestStart() {
        String value = code.getText().toString().trim().toUpperCase(Locale.ROOT);
        if (!value.matches("[0-9A-F]{8}")) {
            code.setError("Enter the eight characters shown on your laptop.");
            code.requestFocus(); return;
        }
        ArrayList<String> permissions = new ArrayList<>();
        if (Build.VERSION.SDK_INT >= 31) {
            if (checkSelfPermission(Manifest.permission.BLUETOOTH_ADVERTISE) != PackageManager.PERMISSION_GRANTED) permissions.add(Manifest.permission.BLUETOOTH_ADVERTISE);
            if (checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) permissions.add(Manifest.permission.BLUETOOTH_CONNECT);
        }
        if (Build.VERSION.SDK_INT >= 33 && !requestedNotifications && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS);
            requestedNotifications = true;
        }
        if (!permissions.isEmpty()) { requestPermissions(permissions.toArray(new String[0]), 10); return; }
        BluetoothManager manager = (BluetoothManager) getSystemService(BLUETOOTH_SERVICE);
        BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
        if (adapter == null) { showStatus("This phone doesn't support Bluetooth."); return; }
        if (!adapter.isEnabled()) { showStatus("Turn Bluetooth on, then tap START LOOKOUT again."); return; }
        if (!adapter.isMultipleAdvertisementSupported()) { showStatus("This phone doesn't support Bluetooth advertising."); return; }
        Intent intent = new Intent(this, BeaconService.class).putExtra("code", value);
        try { startForegroundService(intent); showStatus("Starting lookout…"); }
        catch (RuntimeException error) { showStatus("Couldn't start the lookout. Try again with the app open."); }
    }

    @Override public void onRequestPermissionsResult(int request, String[] names, int[] results) {
        super.onRequestPermissionsResult(request, names, results);
        if (request != 10) return;
        boolean bluetoothGranted = Build.VERSION.SDK_INT < 31 ||
            (checkSelfPermission(Manifest.permission.BLUETOOTH_ADVERTISE) == PackageManager.PERMISSION_GRANTED && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED);
        if (bluetoothGranted) requestStart(); else showStatus("Allow Nearby devices to start the lookout.");
    }

    @Override protected void onResume() { super.onResume(); handler.post(refresh); }
    @Override protected void onPause() { handler.removeCallbacks(refresh); super.onPause(); }
    private void refreshStatus() {
        if (status == null) return;
        status.setText(BeaconService.status);
        boolean running = BeaconService.running;
        start.setEnabled(!running); code.setEnabled(!running); stop.setEnabled(running);
        start.setAlpha(running ? .5f : 1f); stop.setAlpha(running ? 1f : .5f);
    }
    private void showStatus(String message) { BeaconService.status = message; status.setText(message); }
    private int dp(int value) { return (int) (value * getResources().getDisplayMetrics().density + .5f); }
    private TextView text(String value, int size, boolean bold, int color) { TextView t = new TextView(this); t.setText(value); t.setTextSize(size); t.setTextColor(color); t.setLineSpacing(dp(2), 1.08f); if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD); return t; }
    private Button button(String value, int background, int color) { Button b = new Button(this); b.setText(value); b.setTextColor(color); b.setTextSize(15); b.setTypeface(Typeface.DEFAULT, Typeface.BOLD); b.setAllCaps(false); b.setMinHeight(dp(52)); b.setBackground(box(background, 0, color)); return b; }
    private GradientDrawable box(int fill, int stroke, int line) { GradientDrawable d = new GradientDrawable(); d.setColor(fill); d.setCornerRadius(dp(10)); if (stroke > 0) d.setStroke(dp(stroke), line); return d; }
    private void add(LinearLayout parent, View view, int margin) { LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2); p.topMargin = dp(margin); parent.addView(view, p); }
}
