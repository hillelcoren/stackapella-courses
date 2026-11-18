"""Where each part starts a new line (a breath, "br"), in template beats, and how the breath is made.
Rule 1 (docs/arrangements-voicings-plan.md): before a new line every part rests at least half a beat and half a
second (a beat after a line of 8 seconds or more), taken from the line's last note (kept to half a beat), or by
starting an off-beat pickup later. At 60 a beat is a second. Fauré writes no rests in his long lines; the breaths
follow Racine's commas where there is one, and otherwise the places a choir breathes, never inside a word."""
BR = {
    'S': [32, 40, 48, 56, 62, 76, 82, 92, 98, 108, 116, 130, 146, 188, 196, 204, 211, 220, 227, 244, 259, 268],
    'A': [24, 32, 40, 46, 56, 62, 76, 82, 92, 98, 108, 116, 128, 134, 144, 150, 180, 189, 197, 204, 211, 219, 227, 244, 259, 268],
    'T': [8, 16, 23, 32, 40, 46, 56, 62, 76, 82, 92, 98, 110, 118, 126, 131, 142, 147, 164, 172, 179, 190, 198, 204, 211, 219, 227, 244, 259, 268],
    'B': [0, 8, 16, 23, 31, 40, 46, 56, 62, 76, 82, 92, 98, 110, 118, 124, 131, 140, 147, 156, 158, 164, 172, 179, 186, 191, 198, 204, 211, 219, 227, 244, 259, 268],
}

# Breaths made by starting the new line later, so that the four parts still sing its first syllable together:
# (part, breath beat): beats the line's first note starts later (its end stays).
DELAY = {
    ('B', 31): 1.0,   # the bass's "nous" (a half note on beat 3) starts on beat 4 with the others: a beat's breath after "cieux"
    ('S', 56): 0.5,   # "Di-vin" (bar 27): with the alto, tenor and bass, who need a beat's breath after their "yeux"
}
