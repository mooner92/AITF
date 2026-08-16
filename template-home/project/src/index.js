// 내 최애 전문가 AI — 시작점
// 여기서부터 AI와 함께 만들어 나가면 됩니다.

import fs from "fs";

const files = fs.readdirSync("data").filter((f) => f.endsWith(".md"));

console.log("내 자료 폴더에 있는 파일:");
if (files.length === 0) {
  console.log("  (아직 없어요 — data 폴더에 .md 파일을 만들어 보세요)");
} else {
  files.forEach((f) => console.log("  -", f));
}
