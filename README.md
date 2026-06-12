# PLUM ♥ SANNAMY — Othello

A two-phone Othello/Reversi game for Mr. Plum and Sannamy. 8-bit NES style,
real-time sync, no accounts, no app store — just one HTML file.

## How it works

- The whole game is **one file**: `index.html`. There is no server to run.
- Both phones open the same web page. Each phone keeps a WebSocket connection
  to a free public MQTT message broker (EMQX, with HiveMQ as automatic backup).
  Every move is published on a private room channel and shows up on the other
  phone in roughly 100–300 ms — effectively instant for a board game.
- The current board is *retained* on the broker, so if a phone loses signal,
  goes to sleep, or reloads the page, it gets the latest board back the moment
  it reconnects. You can play a slow game over a whole day.
- First time the page opens it asks "WHO ARE YOU?" — pick Mr. Plum on his
  phone and Sannamy on hers. The choice is remembered (use SWITCH PLAYER in
  the footer if you ever pick wrong). Mr. Plum (plum discs) always moves first.

## Putting it online (one-time, ~5 minutes)

Any static host works. Easiest free option — **GitHub Pages**:

1. Create a repository on github.com (it can be private? No — Pages on a free
   account needs a **public** repo, which is fine: the page is harmless).
2. Upload `index.html` (drag & drop in the GitHub web UI works).
3. In the repo: Settings → Pages → Source: "Deploy from a branch" →
   branch `main`, folder `/ (root)` → Save.
4. After a minute your game is at `https://<your-username>.github.io/<repo>/`.

Open that URL on both phones. In Chrome, use **⋮ → Add to Home Screen** to get
a proper icon — it then launches full-screen like a real app.

**Quick test at home instead:** on a computer on the same Wi-Fi, run
`python3 -m http.server 8765` in this folder, then open
`http://<computer-ip>:8765` on both phones.

## Privacy / the room code

There is no login. The "key" to your game is the room code at the top of the
script in `index.html`:

```js
const ROOM = 'psm-othello-x7k2q9d4';
```

It travels over a public broker, so in theory anyone who guessed that exact
random string could watch or interfere — for a couples' Othello game this is
plenty private. Change it to any string you like (it must be identical for
both phones, so just edit the file before uploading).

## Notes

- Sound effects start after the first tap (browsers require a user gesture).
- The phone vibrates briefly when it becomes your turn.
- If a player has no legal move, the game passes automatically and shows
  "... PASSED — NO MOVES!".
- NEW GAME (with a confirm box) resets the board for both phones.
- The LINK indicator in the footer shows the connection: green LINK OK,
  blinking yellow LINK... while reconnecting, red NO LINK.
