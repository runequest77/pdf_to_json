const fs = require('fs');
const path = require('path');
const generateParagraphs = require('./generateParagraphs');

// input_structure.json を読み込む
const inputFilePath = path.join(__dirname, 'input_structure.json');
const jsonData = JSON.parse(fs.readFileSync(inputFilePath, 'utf8'));

// generateParagraphs 関数を呼び出して HTML を生成
const htmlOutput = generateParagraphs(jsonData);

// HTML をファイルに書き出す
const outputFilePath = path.join(__dirname, 'output.html');
const htmlContent = `
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>PDF to HTML</title>
<style>
.page { margin-bottom: 20px; padding: 10px; border: 1px solid #000; }
.nblock { margin: 10px 0; padding: 5px; border: 1px solid #555; }
p { margin: 5px 0; }
span { border: 1px solid #ccc; }
</style>
</head>
<body>
${htmlOutput}
</body>
</html>
`;

fs.writeFileSync(outputFilePath, htmlContent, 'utf8');

console.log(`HTML output has been written to ${outputFilePath}`);