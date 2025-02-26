function generateParagraphs(jsonData) {
  const paragraphs = [];
  let currentParagraph = "";
  let lastStyle = null;
  let lastY = null; // 直前の line_bbox の y0 を保持

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

    // line_bbox の第二要素（y0）が同一の場合、スペースの場合、タブ(置換後|)の場合paragraphの終了判定を行わない
    if (lastY !== line.line_bbox[1] || /[ |]$/.test(currentParagraph)==false) {
      // paragraphの終了判定
      // 1.最後の文字が文末文字(.!?)  → 新しい paragraph
      // 3.前の行と style が異なる    → 新しい paragraph
      if (/[.?!]$/.test(currentParagraph) || lastStyle !== currentLineStyle) {
        paragraphs.push(currentParagraph);
        currentParagraph = "";
      }
    }
    // block 内で連続した line の line_bbox[1] が同じなら、既に内容がある場合に "|" を挟む
    if (line.line_bbox && lastY === line.line_bbox[1] && currentParagraph) {
      currentParagraph += "|";
    }
    // line 内の各 span の text を連結
    const lineText = line.spans.map(span => span.text).join("").replace(/\t/g, "|");
    currentParagraph += lineText;
    if (currentParagraph.includes("staff, warily trying to defend against any attackers.")) {
      debugger;
    }
    // 現在行の最終 span の style を更新
    lastStyle = getStyle(line.spans[line.spans.length - 1]);
    // 現在の line の y0 を更新
    if (line.line_bbox) {
      lastY = line.line_bbox[1];
    }
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