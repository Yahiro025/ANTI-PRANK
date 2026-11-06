package com.caught.companion;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.AdvertiseCallback;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertiseSettings;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.content.Intent;
import android.os.IBinder;
import android.os.ParcelUuid;
import java.util.UUID;

public final class BeaconService extends Service {
    static volatile boolean running = false;
    static volatile String status = "Lookout is off.";
    private static final String STOP = "com.caught.companion.STOP";
    private BluetoothLeAdvertiser advertiser;
    private AdvertiseCallback callback;

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null || STOP.equals(intent.getAction())) { stopSelf(); return START_NOT_STICKY; }
        String code = intent.getStringExtra("code");
        if (code == null || !code.matches("[0-9A-F]{8}")) { status = "Invalid laptop code. Try again."; stopSelf(); return START_NOT_STICKY; }
        if (running) return START_NOT_STICKY;
        running = true;
        status = "Starting lookout…";
        try {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            nm.createNotificationChannel(new NotificationChannel("lookout", "Bluetooth lookout", NotificationManager.IMPORTANCE_LOW));
            PendingIntent open = PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
            PendingIntent stop = PendingIntent.getService(this, 1, new Intent(this, BeaconService.class).setAction(STOP), PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
            Notification notification = new Notification.Builder(this, "lookout")
                .setContentTitle("CAUGHT! lookout is on")
                .setContentText("Your laptop can detect this phone nearby.")
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setContentIntent(open).setOngoing(true)
                .addAction(new Notification.Action.Builder(null, "Stop lookout", stop).build()).build();
            startForeground(41, notification);
            BluetoothManager manager = (BluetoothManager) getSystemService(BLUETOOTH_SERVICE);
            BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
            advertiser = adapter == null ? null : adapter.getBluetoothLeAdvertiser();
            if (advertiser == null) { fail("Bluetooth advertising is unavailable. Check Bluetooth and try again."); return START_NOT_STICKY; }
            ParcelUuid uuid = new ParcelUuid(UUID.fromString(code.toLowerCase() + "-cabe-4aed-9c0d-0123456789ab"));
            callback = new AdvertiseCallback() {
                @Override public void onStartSuccess(AdvertiseSettings settings) { status = "Lookout is on. Keep this notification active while you're away."; }
                @Override public void onStartFailure(int errorCode) { fail("Couldn't start Bluetooth advertising (" + errorCode + "). Try restarting Bluetooth."); }
            };
            advertiser.startAdvertising(new AdvertiseSettings.Builder().setAdvertiseMode(AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY).setConnectable(false).setTxPowerLevel(AdvertiseSettings.ADVERTISE_TX_POWER_MEDIUM).build(),
                new AdvertiseData.Builder().addServiceUuid(uuid).setIncludeDeviceName(false).build(), callback);
        } catch (RuntimeException error) { fail("Couldn't start the lookout. Check Bluetooth permissions and try again."); }
        return START_NOT_STICKY;
    }
    private void fail(String message) { status = message; running = false; stopSelf(); }
    @Override public void onDestroy() {
        if (advertiser != null && callback != null) { try { advertiser.stopAdvertising(callback); } catch (RuntimeException ignored) {} }
        if (running) status = "Lookout is off.";
        running = false; advertiser = null; callback = null;
        stopForeground(true);
        super.onDestroy();
    }
    @Override public IBinder onBind(Intent intent) { return null; }
}
