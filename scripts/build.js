
const fs = require("node:fs");
const path = require("node:path");

const outputDir = path.join(__dirname, "..", "dist");
const source = path.join(__dirname, "..", "src", "index.js");

fs.mkdirSync(outputDir, { recursive: true });
fs.copyFileSync(source, path.join(outputDir, "index.js"));

console.log("빌드 성공!");
