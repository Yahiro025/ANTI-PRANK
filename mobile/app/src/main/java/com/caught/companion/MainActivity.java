package com.caught.companion;

import android.Manifest;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.drawable.RippleDrawable;
import android.view.WindowInsets;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Rect;
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
    static final int CREAM = Color.rgb(255, 244, 222), INK = Color.rgb(37, 28, 25), RED = Color.rgb(185, 45, 36), MUTED = Color.rgb(107, 87, 76), PAPER = Color.rgb(255, 251, 242);
    private final Handler handler = new Handler(Looper.getMainLooper());
    private EditText code;
    private TextView status, stateTitle;
    private LookoutView mascot;
    private Typeface displayFace;
    private Button start, stop;
    private boolean requestedNotifications;
    private final Runnable refresh = new Runnable() {
        public void run() { refreshStatus(); handler.postDelayed(this, 800); }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        displayFace = Typeface.createFromAsset(getAssets(), "bricolage.ttf");
        getWindow().setStatusBarColor(CREAM);
        getWindow().setNavigationBarColor(CREAM);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(CREAM);
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
            scroll.setOnApplyWindowInsetsListener((v, insets) -> {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.ime());
                v.setPadding(bars.left, bars.top, bars.right, bars.bottom);
                View focused = getCurrentFocus();
                if (focused != null && insets.isVisible(WindowInsets.Type.ime())) {
                    v.post(() -> focused.requestRectangleOnScreen(
                        new Rect(0, 0, focused.getWidth(), focused.getHeight() + dp(16)), false));
                }
                return insets;
            });
        }
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(24), dp(20), dp(24), dp(32));
        scroll.addView(page);
        LinearLayout header = new LinearLayout(this);
        header.setGravity(Gravity.CENTER_VERTICAL);
        TextView brand = text("CAUGHT!", 24, true, INK);
        brand.setTypeface(displayFace, Typeface.BOLD);
        boolean largeText = getResources().getConfiguration().fontScale > 1.3f;
        if (largeText) header.setOrientation(LinearLayout.VERTICAL);
        header.addView(brand, largeText ? new LinearLayout.LayoutParams(-1, -2)
                                      : new LinearLayout.LayoutParams(0, -2, 1));
        TextView companion = text("Companion", 13, false, MUTED);
        header.addView(companion);
        page.addView(header);
        mascot = new LookoutView(this);
        mascot.setContentDescription("Little lookout, resting");
        LinearLayout.LayoutParams mascotParams = new LinearLayout.LayoutParams(dp(144), dp(136));
        mascotParams.gravity = Gravity.CENTER_HORIZONTAL;
        mascotParams.topMargin = dp(24);
        page.addView(mascot, mascotParams);
        TextView title = text("Your pocket\nlookout.", 36, true, INK);
        title.setTypeface(displayFace, Typeface.BOLD);
        title.setLineSpacing(0, 1f);
        add(page, title, 8);
        add(page, text("Your phone signals. Your laptop watches.", 16, false, MUTED), 8);
        TextView label = text("Laptop code", 14, true, INK);
        add(page, label, 24);
        code = new EditText(this);
        code.setId(101);
        label.setLabelFor(101);
        code.setSingleLine(true);
        code.setTextSize(24);
        code.setTypeface(Typeface.MONOSPACE, Typeface.BOLD);
        code.setTextColor(INK);
        code.setHintTextColor(MUTED);
        code.setHint("A12B34CD");
        code.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        code.setFilters(new InputFilter[]{new InputFilter.AllCaps(), new InputFilter.LengthFilter(8)});
        code.setPadding(dp(16), dp(16), dp(16), dp(16));
        code.setMinimumHeight(dp(64));
        code.setBackground(box(PAPER, 1, MUTED));
        code.setOnFocusChangeListener((v, focused) -> code.setBackground(box(PAPER, focused ? 2 : 1, focused ? RED : MUTED)));
        add(page, code, 8);
        if (state != null) {
            code.setText(state.getString("laptopCode", ""));
            requestedNotifications = state.getBoolean("requestedNotifications", false);
        }
        add(page, text("Find it under PHONE WATCH on your laptop.", 13, false, MUTED), 8);
        start = button("Start lookout", RED, CREAM);
        start.setOnClickListener(v -> requestStart());
        add(page, start, 20);
        stateTitle = text("Lookout is off", 17, true, INK);
        add(page, stateTitle, 24);
        status = text(BeaconService.status, 14, false, MUTED);
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        add(page, status, 4);
        stop = button("Stop lookout", INK, CREAM);
        stop.setOnClickListener(v -> { stopService(new Intent(this, BeaconService.class)); refreshStatus(); });
        add(page, stop, 12);
        View divider = new View(this);
        divider.setBackgroundColor(Color.rgb(220, 203, 178));
        LinearLayout.LayoutParams line = new LinearLayout.LayoutParams(-1, dp(1));
        line.topMargin = dp(24);
        page.addView(divider, line);
        add(page, text("The coffee-break plan", 18, true, INK), 24);
        add(page, text("1. Connect while your phone is close.\n2. Take your phone with you. The laptop arms.\n3. A key, click or scroll triggers the laptop's reveal.", 15, false, INK), 12);
        add(page, text("Bluetooth estimates proximity, not meters. Allow notifications to see the running lookout. The laptop handles the camera and alarm; this phone does not receive alerts. A prank demo, not a security lock.", 13, false, MUTED), 24);
        setContentView(scroll);
    }

    @Override public void onSaveInstanceState(Bundle state) {
        state.putString("laptopCode", code.getText().toString());
        state.putBoolean("requestedNotifications", requestedNotifications);
        super.onSaveInstanceState(state);
    }

    private void requestStart() {
        code.setError(null);
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
        if (!adapter.isEnabled()) { showStatus("Turn Bluetooth on, then tap Start lookout again."); return; }
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
        String next = BeaconService.status;
        if (!next.contentEquals(status.getText())) status.setText(next);
        boolean running = BeaconService.running;
        start.setEnabled(!running); code.setEnabled(!running); stop.setEnabled(running);
        start.setAlpha(running ? .5f : 1f);
        code.setAlpha(running ? .5f : 1f);
        stop.setVisibility(running ? View.VISIBLE : View.GONE);
        boolean broadcasting = BeaconService.broadcasting;
        String title = broadcasting ? "Phone is broadcasting" : running ? "Starting lookout" : "Lookout is off";
        if (!title.contentEquals(stateTitle.getText())) stateTitle.setText(title);
        mascot.setWatching(broadcasting);
        mascot.setContentDescription(broadcasting ? "Little lookout, watching" : "Little lookout, resting");
    }
    private void showStatus(String message) { BeaconService.status = message; status.setText(message); }
    private int dp(int value) { return (int) (value * getResources().getDisplayMetrics().density + .5f); }
    private TextView text(String value, int size, boolean bold, int color) { TextView t = new TextView(this); t.setText(value); t.setTextSize(size); t.setTextColor(color); t.setLineSpacing(dp(2), 1.08f); if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD); return t; }
    private Button button(String value, int background, int color) { Button b = new Button(this); b.setText(value); b.setTextColor(color); b.setTextSize(16); b.setTypeface(Typeface.DEFAULT, Typeface.BOLD); b.setAllCaps(false); b.setMinHeight(dp(56)); b.setPadding(dp(16), dp(12), dp(16), dp(12)); b.setBackground(new RippleDrawable(ColorStateList.valueOf(Color.argb(45, 255, 244, 222)), box(background, 0, color), null)); return b; }
    private GradientDrawable box(int fill, int stroke, int line) { GradientDrawable d = new GradientDrawable(); d.setColor(fill); d.setCornerRadius(dp(12)); if (stroke > 0) d.setStroke(dp(stroke), line); return d; }
    private void add(LinearLayout parent, View view, int margin) { LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2); p.topMargin = dp(margin); parent.addView(view, p); }
}
