package com.caught.companion;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.View;
import static com.caught.companion.MainActivity.*;

/** Flat, original geometry shared with the desktop's Little lookout. */
public final class LookoutView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private boolean watching;
    private static final int FEET = Color.rgb(138, 30, 23), CHEEK = Color.rgb(201, 69, 59);
    public LookoutView(Context context) { super(context); }
    public void setWatching(boolean value) {
        if (watching != value) { watching = value; invalidate(); }
    }
    private void oval(Canvas c, float l, float t, float r, float b, int color) {
        paint.setColor(color); c.drawOval(l, t, r, b, paint);
    }
    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float size = Math.min(getWidth(), getHeight());
        canvas.save();
        canvas.translate((getWidth() - size) / 2, 0);
        canvas.scale(size / 100, size / 100);
        oval(canvas, 27, 82, 45, 94, FEET);
        oval(canvas, 55, 82, 73, 94, FEET);
        oval(canvas, 14, 10, 86, 86, RED);
        oval(canvas, 27, 22, 73, 68, CREAM);
        int gaze = watching ? 0 : 7;
        oval(canvas, 40+gaze, 35, 60+gaze, 55, INK);
        oval(canvas, 46+gaze, 38, 51+gaze, 43, PAPER);
        oval(canvas, 23, 63, 33, 69, CHEEK);
        oval(canvas, 67, 63, 77, 69, CHEEK);
        canvas.restore();
    }
}
