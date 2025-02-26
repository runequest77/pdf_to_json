function generateParagraphs(jsonData) {
  const paragraphs = [];
  let currentParagraph = "";
  let lastStyle = null;

  // span の style を文字列に変換（font と size を連結）
  function getStyle(span) {
    const roundedSize = Math.round(span.size * 2) / 2;
    return `${span.font}-${roundedSize}`;
  }

  // JSONの構造は [page, …] の中に zones, blocks, lines, spans があるので全lineをフラットに取得
  const lines = [];
  jsonData.forEach(page => {
    if (page.zones) {
      page.zones.forEach(zone => {
        if (zone.blocks) {
          zone.blocks.forEach(block => {
            if (block.lines) {
              block.lines.forEach(line => {
                lines.push(line);
              });
            }
          });
        }
      });
    }
  });

  // 各 line を走査して paragraph を作成
  lines.forEach(line => {
    if (!line.spans || line.spans.length === 0) {
      return;
    }
    // 現在行の先頭 span の style を取得
    const currentLineStyle = getStyle(line.spans[0]);
    // paragraph に既に内容があり、かつ下記のいずれかの条件を満たす場合、現在の段落をクローズする
    // 1. 前行の最終 span と現在行の先頭 span の style が異なる
    // 2. 現在の paragraph の最後の文字が空白でない
    if (currentParagraph) {
      if (lastStyle !== currentLineStyle || (currentParagraph.slice(-1) !== " " && currentParagraph.slice(-1) !== "|")) {
        paragraphs.push(currentParagraph);
        currentParagraph = "";
      }
    }
    // line 内の各 span の text を連結
    const lineText = line.spans.map(span => span.text).join("").replace(/\t/g, "|");
    currentParagraph += lineText;
    // 現在行の最終 span の style を更新
    lastStyle = getStyle(line.spans[line.spans.length - 1]);
  });

  // ループ終了後、残りの paragraph があれば追加
  if (currentParagraph) {
    paragraphs.push(currentParagraph);
  }

  // HTML <p>タグにラップして返す
  const html = paragraphs.map(para => `<p>${para}</p>`).join("\n");
  return html;
}

// 関数をエクスポート
module.exports = generateParagraphs;