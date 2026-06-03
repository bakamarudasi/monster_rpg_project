// ワールドマップとミニマップで共有するユーティリティ。
// 地方名から色相(0..359)を決めるハッシュ。両画面で同じ式を使うことで
// 地図とミニマップの地方カラーを一致させる（片方だけ変えると色がズレるため集約）。
function regionHue(name) {
  let h = 0;
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) % 360;
  return h;
}
